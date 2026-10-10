from enum import Enum


class Naipe(Enum):
    ESPADAS = 0
    BASTOS = 1
    OROS = 2
    COPAS = 3


class Carta:
    def __init__(
        self,
            id_carta, naipe: Naipe, valor, imagem_frente, imagem_costa):
        self._id_carta = id_carta
        self._naipe = naipe
        self._valor = valor
        self._imagem_frente = imagem_frente
        self._imagem_costa = imagem_costa

    @property
    def id_carta(self):
        return self._id_carta

    @property
    def naipe(self):
        return self._naipe

    @property
    def valor(self):
        return self._valor

    def __repr__(self):
        return f"Carta({self._valor} de {self._naipe.name})"
