#!/usr/bin/env python3

import sys

from asyncio import Lock
from dataclasses import dataclass
from random import randint

from discord import (Client, Forbidden, Intents, Interaction, Member,
                     Status, TextChannel, Webhook)
from discord.app_commands import CommandTree

@dataclass(slots=True)
class Score:
    member: Member
    score: int = 0
    guessed: bool = False
    multiplier: int = 1

class KClient(Client):
    def __init__(
        self, *,
        intents: Intents | None = None,
        sync: bool = False,
        **options # pyright: ignore[reportMissingParameterType, reportUnknownParameterType]
    ) -> None:
        super().__init__(
            intents=Intents.default() if intents is None else intents,
            **options)  # pyright: ignore[reportUnknownArgumentType]
        self._sync: bool = sync
        self._tree: CommandTree = CommandTree(self)

        self._channel: TextChannel | None = None
        self._capacity: int | None = None
        self._members: list[Score] = []
        self._send_lock: Lock = Lock()
        self._webhook: Webhook

        @self._tree.command()
        async def join(interaction: Interaction):  # pyright: ignore[reportUnusedFunction]
            if self._capacity is None:
                self._capacity = randint(2, min(10, max(2, len([
                    member for member in interaction.guild.members
                    if not member.bot and
                    member.status != Status.invisible and
                    member.status != Status.offline]))))
                
            if any(x.member == interaction.user for x in self._members):
                _ = await interaction.response.send_message("Você já está no jogo.", ephemeral=True)
                return

            if len(self._members) == self._capacity:
                _ = await interaction.response.send_message("Espere o jogo acabar.")
                return
            
            self._members.append(Score(interaction.user))

            if len(self._members) == self._capacity:
                try:
                    self._webhook = next(wh for wh in await interaction.guild.webhooks())
                except (Forbidden, StopIteration):
                    self._channel = await interaction.guild.create_text_channel(name="game")
                    self._webhook = await self._channel.create_webhook(name=self.user.name)
                else:
                    self._channel = self._webhook.channel
                _ = await self._channel.send("Que os jogos começem!")
            else:
                _ = await interaction.response.send_message(f"{len(self._members)}/{self._capacity} pessoas", ephemeral=True)

        @self._tree.command()
        async def guess(interaction: Interaction, id: int, guess: Member):  # pyright: ignore[reportUnusedFunction]
            if self._channel is None:
                _ = await interaction.response.send_message("Um jogo não foi criado ainda!")
                return

            id -= 1 # traduzir pra index
            if id < 0 or id >= len(self._members):
                _ = await interaction.response.send_message(f"O id é entre 1 e {self._capacity}.", ephemeral=True)
                return
            info = self._members[id]
            if info.member == interaction.user:
                _ = await interaction.response.send_message(f"É você mesmo(a)...", ephemeral=True)
                return
            if info.member == guess:
                if info.guessed:
                    _ = await interaction.response.send_message("Esse usuário já foi adivinhado.", ephemeral=True)
                    return
                info.guessed = True
                info.score += info.multiplier
                info.multiplier += 1
                if all(x.guessed for x in self._members):
                    self._members.sort(key=lambda info: info.score,
                                       reverse=True)
                    highest = [info.member for info in self._members
                               if info.score == self._members[0].score]
                    _ = await interaction.response.send_message(
                        f"Vencedores: {', '.join(highest)} com {self._members[0].score} pontos")
                    self._capacity = None
                    self._members.clear()
                else:
                    _ = await interaction.response.send_message("Acertou!", ephemeral=True)
            else:
                info.score -= info.multiplier
                info.multiplier = 1
                _ = await interaction.response.send_message("Errou!", ephemeral=True)

        @self._tree.command()
        async def send(interaction: Interaction, text: str):  # pyright: ignore[reportUnusedFunction]
            if self._channel is None:
                _ = await interaction.response.send_message("Um jogo não foi criado ainda!")
                return
            try:
                index = next(i + 1 for i, info in enumerate(self._members) if info.member == interaction.user)
            except StopIteration:
                _ = await interaction.response.send_message("Você não está na partida.", ephemeral=True)
            else:
                # Possibilidade de condição de corrida.
                async with self._send_lock:
                    _ = await self._webhook.send(text, username=str(index),
                                                 wait=True)

    async def on_ready(self):
        if self._sync:
            _ = await self._tree.sync()
            self._sync = False

if __name__ == "__main__":
    intents = Intents.default()
    intents.members = intents.presences = intents.webhooks = True
    client = KClient(
        intents=intents,
        sync=any(arg == "-s" or arg == "--sync" for arg in sys.argv))
    with open("token.txt") as token_file:
        token = token_file.read().strip()
    client.run(token)