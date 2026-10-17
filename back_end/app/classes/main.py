
from .usuario import Usuario
from .bot import Bot
from .partida import Partida

from .partida import TrucoOpcao, EnvidoOpcao


def rodar_jogo():

    usuario = Usuario(nome="Luis")
    bot = Bot(nome="Bot Gaudério")

    usuario.maoVez = True
    bot.maoVez = False

    partida = Partida(jogador=usuario, bot=bot)

    partida.inicio_partida()


if __name__ == "__main__":
    rodar_jogo()
