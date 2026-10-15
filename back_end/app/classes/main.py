
from .usuario import Usuario
from .bot import Bot
from .partida import Partida

from .partida import TrucoOpcao, EnvidoOpcao


def rodar_jogo():
    # 1. Cria instâncias dos jogadores com estados iniciais básicos
    usuario = Usuario(nome="Jogador")
    bot = Bot(nome="Bot Gaudério")

    usuario.maoVez = True
    bot.maoVez = False

    # Garante que as pontuações comecem zeradas

    # 3. Cria a instância da Partida passados os jogadores
    partida = Partida(jogador=usuario, bot=bot)

    # 4. Inicia o loop de testes no terminal
    partida.inicio_partida()


if __name__ == "__main__":
    rodar_jogo()
