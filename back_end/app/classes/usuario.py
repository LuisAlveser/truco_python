from carta import Naipe, Carta


class Usuario:
    def __init__(self, nome, email, senha):
        self._mao = []
        self._nome = nome
        self._email = email
        self._senha = senha
        self._pontuacao = 0

    @property
    def pontuacao(self):
        return self._pontuacao

    def incrementa_pontuacao(self, ponto):
        self._pontuacao += ponto

    def recebeCartas(self, Carta: list):
        self._mao = []
        self._mao.extend(Carta)

    def jogarcarta(self, id_carta):
        for carta in self._mao:
            if (carta.id_carta == id_carta):
                self._mao.remove(carta)
                print(f" Carta jogada pelo usuario :{carta}")
                return carta
        return None
