# main.py
from usuario import Usuario
from bot import Bot
from partida import Partida
# Importa os Enums se precisar
from partida import TrucoOpcao, EnvidoOpcao


def rodar_jogo():
    # 1. Cria instâncias dos jogadores com estados iniciais básicos
    # Certifique-se de que o construtor do seu Usuario/Bot aceite esses parâmetros ou defina pontuacao como 0
    usuario = Usuario(nome="Luis", email="luis@email.com", senha="123")
    bot = Bot(nome="Bot Gaudério")

    # 2. Define quem começará a primeira mão como Mão da rodada
    usuario.maoVez = True
    bot.maoVez = False

    # Garante que as pontuações comecem zeradas

    # 3. Cria a instância da Partida passados os jogadores
    partida = Partida(jogador=usuario, bot=bot)

    # 4. Inicia o loop de testes no terminal
    partida.inicio_partida()


if __name__ == "__main__":
    rodar_jogo()
