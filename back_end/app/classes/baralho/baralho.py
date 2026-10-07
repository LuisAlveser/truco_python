from carta import Carta, Naipe


class Baralho:
    def __init__(self):
        self._cartas = []
        self._gerar_baralho()

    def _gerar_baralho():
        id_atual = 1

        valores = [1, 2, 3, 4, 5, 6, 7, 10, 11, 12]

        for naipe in Naipe:
            for valor in valores:
                nome_imagem = f"{valor}_{naipe.name.lower()}.png"
                costas_carta = f"{valor}_costas_da_carta.png"
                nova_carta = Carta(id_atual, naipe, nome_imagem, costas_carta)
                self._cartas.append(nova_carta)
                id_atual += 1
