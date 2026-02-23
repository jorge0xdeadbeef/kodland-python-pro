# "Quem é?"
Esse projeto é um bot de Discord que implementa um jogo simples:
Pessoas entram em uma sala virtual usando `/join`, cuja sala é criada com uma capacidade entre 2 e 10 pessoas. Após entrarem na sala, o bot cria um canal de texto e cada um é identificado por um número começando em 1. Os participantes usam `/send` para enviar mensagens no canal usando o seu número, e o objetivo de cada participante é advinhar quem está por trás de cada número usando o comando `/guess`. O jogo acaba quando todos os participantes são advinhados.
É mais apropriado jogar em servidores com várias pessoas (por exemplo, uma turma da Kodland) :)
Recursos:
- Uso apropriado de webhooks
- Pontuação com "boost de pontos" por sequência de acertos
- Pessoas anônimas

Recursos que ainda não foram implementados:
- Dicas
- Safeguards em evento da pessoa sair do jogo
- Envio de arquivos
- Jogar em mais de um canal
- Jogar em múltiplos servidores
- Jogar entre servidores

Eu não implementei esses recursos pois esse projeto é algo que precisei fazer e finalizar rápido.

# Instalação
Certifique-se de que tenha `git`, Python e `pip` instalados. Após isso, clone o projeto e instale as dependências:
```sh
git clone https://github.com/jorge0xdeadbeef/kodland-python-pro
cd kodland-python-pro
pip3 install -r requirements.txt
```
Para executar o bot, é necessário [criar uma conta para bot](https://discord.com/developers/applications), extrair a token dele e colocá-lo em um arquivo chamado `token.txt` dentro da pasta do bot. Após isso, para rodar o bot:
```sh
python3 main.py
```
Caso você adicione/remova comandos nele, coloque `-s` após o `main.py`, pois isso vai fazer o Discord sincronizar os comandos.