from carta import Naipe, Carta
from usuario import Usuario

import random


class Baralho:
    def __init__(self):
        self._cartas = []
        self._gerar_baralho()

    def __str__(self):
        return str(self._cartas)

    def _gerar_baralho(self):
        id_atual = 1

        valores = [1, 2, 3, 4, 5, 6, 7, 10, 11, 12]

        for naipe in Naipe:
            for valor in valores:
                imagem_frente = f"{valor}_{naipe.name.lower()}.png"
                imagem_costa = f"{valor}_costas_da_carta.png"
                nova_carta = Carta(
                    id_atual, naipe, valor, imagem_frente, imagem_costa)
                self._cartas.append(nova_carta)
                id_atual += 1

    def distribuir_cartas(self):
        cartas_jogadores = []
        for _ in range(6):
            carta_sorteada = random.choice(self._cartas)
            self._cartas.remove(carta_sorteada)
            cartas_jogadores.append(carta_sorteada)
            print(cartas_jogadores)
        return cartas_jogadores


if __name__ == "__main__":
    print("--- Testando a criação do Baralho ---")

    meu_baralho = Baralho()

    print(f"Total de cartas geradas: {len(meu_baralho._cartas)}")
    print(meu_baralho)

    print("\n--- Testando a distribuição de 6 cartas ---")
    cartas_na_mesa = meu_baralho.distribuir_cartas()
    cartas_jogador = []
    for i in range(3):
        cartas_jogador.append(cartas_na_mesa[i])

    print(f"Cartas dos jogadores,{cartas_na_mesa}")
    usuario = Usuario("luis", "erci@gmiaj", "ddasfsdfd")
    usuario.recebeCartas(cartas_jogador)
    usuario.jogarcarta(cartas_jogador[0].id_carta)

    print(
        f"\nTotal de cartas restantes no baralho: {len(meu_baralho._cartas)}")
