from carta import Naipe, Carta


class Bot:
    def __init__(self, nome):
        self._mao = []
        self._nome = nome
        self._maoVez = False
        self._pontuacao = 0

    @property
    def pontuacao(self):
        return self._pontuacao

    @property
    def maoVez(self):
        return self._maoVez

    @property
    def nome(self):
        return self._nome

    @maoVez.setter
    def maoVez(self, estado: bool):
        self._maoVez = estado

    @pontuacao.setter
    def incrementa_pontuacao(self, ponto):
        self._pontuacao += ponto

    def recebeCartas(self, Carta: list):
        self._mao = []
        self._mao.extend(Carta)

    def jogarcarta(self, id_carta):
        for carta in self._mao:
            if (carta.id_carta == id_carta):
                self._mao.remove(carta)
                print(f" Carta jogada pelo bot :{carta}")
                return carta
        return None
