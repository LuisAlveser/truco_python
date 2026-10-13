from carta import Naipe, Carta
from usuario import Usuario
from bot import Bot


class Regras:
    def __init__(self, jogador1: Usuario, bot: Bot):
        self._jogador1 = jogador1
        self._bot = bot

        self._hierarquia = {
            (7, Naipe.ESPADAS): 14,  # Sete de Espadas (Manilha Máxima)
            (7, Naipe.OROS): 13,     # Sete de Oros
            (1, Naipe.ESPADAS): 12,  # Ás de Espadas (Espadilha)
            (1, Naipe.BASTOS): 11,   # Ás de Bastos (Bastão)

            # Os 3 (todos iguais)
            (3, Naipe.ESPADAS): 10, (3, Naipe.BASTOS): 10, (3, Naipe.OROS): 10, (3, Naipe.COPAS): 10,
            # Os 2 (todos iguais)
            (2, Naipe.ESPADAS): 9,  (2, Naipe.BASTOS): 9,  (2, Naipe.OROS): 9,  (2, Naipe.COPAS): 9,

            # Os Ases restantes (falsos/brutos)
            (1, Naipe.OROS): 8,     (1, Naipe.COPAS): 8,

            # Os Reis (12)
            (12, Naipe.ESPADAS): 7, (12, Naipe.BASTOS): 7, (12, Naipe.OROS): 7, (12, Naipe.COPAS): 7,
            # Os Cavalos (11)
            (11, Naipe.ESPADAS): 6, (11, Naipe.BASTOS): 6, (11, Naipe.OROS): 6, (11, Naipe.COPAS): 6,
            # As Sotas (10)
            (10, Naipe.ESPADAS): 5, (10, Naipe.BASTOS): 5, (10, Naipe.OROS): 5, (10, Naipe.COPAS): 5,

            # Os 7 restantes (falsos)
            (7, Naipe.BASTOS): 4,   (7, Naipe.COPAS): 4,

            # Os 6
            (6, Naipe.ESPADAS): 3,  (6, Naipe.BASTOS): 3,  (6, Naipe.OROS): 3,  (6, Naipe.COPAS): 3,
            # Os 5
            (5, Naipe.ESPADAS): 2,  (5, Naipe.BASTOS): 2,  (5, Naipe.OROS): 2,  (5, Naipe.COPAS): 2,
            # Os 4 (as mais fracas)
            (4, Naipe.ESPADAS): 1,  (4, Naipe.BASTOS): 1,  (4, Naipe.OROS): 1,
        }

    def verifica_valor_envido(self, Carta: list):
        resultado = 20

        v = [0 if c.valor in [10, 11, 12] else c.valor for c in Carta]

    # Caso 1: Carta 0 e Carta 1 têm o mesmo naipe
        if Carta[0].naipe == Carta[1].naipe:
            return resultado + v[0] + v[1]

    # Caso 2: Carta 1 e Carta 2 têm o mesmo naipe
        elif Carta[1].naipe == Carta[2].naipe:
            return resultado + v[1] + v[2]

    # Caso 3: Carta 0 e Carta 2 têm o mesmo naipe (O caso da sua mão atual!)
        elif Carta[0].naipe == Carta[2].naipe:
            return resultado + v[0] + v[2]

    # Caso 4: Nenhuma carta tem o mesmo naipe (Vale a maior carta individual)
        else:
            return max(v[0], v[1], v[2])

    # função que verifica se o usuario tem tres cartas do mesmo naipe

    def verifica_flor(self, Carta: list):
        if Carta[0].naipe == Carta[1].naipe == Carta[2].naipe:
            return True
        else:
            return False

    def trocaMaoJogadores(self):
        self._bot._maoVez = not self._bot._maoVez
        self._jogador1._maoVez = not self._bot._maoVez

    def obter_peso(self, carta):

        return self._hierarquia.get((carta.valor, carta.naipe), 0)

    def verifica_carta_mais_forte_da_rodada(self, jogador_carta: Carta, bot_carta: Carta):
        peso_jogador = self.obter_peso(jogador_carta)
        peso_bot = self.obter_peso(bot_carta)
        if peso_jogador > peso_bot:
            return 0
        else:
            return 1

    def comparacao_pontos_envido(self, pontos_jogador, pontos_bot):
        if pontos_jogador > pontos_bot:
            return 0

        elif pontos_jogador == pontos_bot:
            if self._jogador1.maoVez:
                return 0
            else:
                return 1
        else:
            return 1
