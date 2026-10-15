from enum import Enum
from .usuario import Usuario
from .bot import Bot
from .regras import Regras
from .baralho import Baralho


class TrucoOpcao(Enum):
    QUERO = 0
    CORRER = 1
    RETRUCO = 2
    VALE_QUATRO = 3


class EnvidoOpcao(Enum):
    QUERO = 0
    NAO_QUERO = 1
    REAL_ENVIDO = 2


class Partida:
    def __init__(self, jogador: Usuario, bot: Bot):
        self._jogador = jogador
        self._bot = bot
        self.rodadas = 0
        self.vitorias_jogador = 0
        self.vitorias_bot = 0
        self.historico_rodadas = []
        self.regras = Regras(self._jogador, self._bot)

        self.baralho = Baralho()
        self.valor_da_mao_atual = 1
        self.envido_ja_cantado = False
        self.envido_permitido = True
        self.flor_ja_cantada = False
        self.mao_inicial = self._jogador.maoVez
        self.PONTUACAO_MAXIMA = 24
        self.partida_encerrada = False

        # Garante o estado inicial da mão (Jogador começa como mão se não definido)
        if not hasattr(self._jogador, "_maoVez") or not hasattr(self._bot, "_maoVez"):
            self._jogador._maoVez = True
            self._bot._maoVez = False

    def vencedor_mao(self):
        if len(self.historico_rodadas) < 2:
            return None

        primeira, segunda = self.historico_rodadas[:2]
        if primeira == segunda and primeira != 2:
            return primeira
        if primeira == 2 and segunda != 2:
            return segunda
        if primeira != 2 and segunda == 2:
            return primeira
        if len(self.historico_rodadas) < 3:
            return None

        terceira = self.historico_rodadas[2]
        if terceira != 2:
            return terceira
        if primeira != 2:
            return primeira
        if segunda != 2:
            return segunda
        return 0 if self.mao_inicial else 1

    def fase_preliminar(self):
        """Gerencia os cantos de Flor e Envido antes das jogadas das cartas"""
        print("\n--- FASE PRELIMINAR (FLOR E ENVIDO) ---")

        # 1. FLOR (Checagem automática)
        tem_flor_jogador = self.regras.verifica_flor(self._jogador._mao)
        tem_flor_bot = self.regras.verifica_flor(self._bot._mao)

        if tem_flor_jogador and tem_flor_bot:
            print("🌸 Ambos os jogadores possuem Flor! (+3 tentos para cada um)")
            self._jogador._pontuacao += 3
            self._bot._pontuacao += 3
            self.envido_permitido = False
            return
        elif tem_flor_jogador:
            print(f"🌸 {self._jogador.nome} canta: 'Flor na mesa!' (+3 tentos)")
            self._jogador._pontuacao += 3
            self.envido_permitido = False
            return
        elif tem_flor_bot:
            print("🤖 Bot canta: 'Flor na mesa!' (+3 tentos para o Bot)")
            self._bot._pontuacao += 3
            self.envido_permitido = False
            return

        # 2. ENVIDO (Se ninguém teve Flor)
        if self.envido_permitido and not self.envido_ja_cantado:
            quer_envido = input(
                f"\n{self._jogador.nome}, deseja cantar ENVIDO? (s/n): ").strip().lower()
            if quer_envido == 's':
                self.gerenciar_pedido_envido(self._jogador)
            else:
                # O Bot decide se canta Envido por conta própria
                pontos_envido_bot = self.regras.verifica_valor_envido(
                    self._bot._mao)
                if pontos_envido_bot >= 28:
                    self.gerenciar_pedido_envido(self._bot)

    def gerenciar_pedido_truco(self, quem_pediu):
        oponente = self._bot if quem_pediu == self._jogador else self._jogador
        print(f"\n{quem_pediu.nome} gritou TRUCO!")

        if oponente == self._bot:
            resposta = TrucoOpcao.QUERO
        else:
            escolha = input(
                f"{oponente.nome}, aceita o truco? (q = Quero / c = Correr): "
            ).strip().lower()
            resposta = (
                TrucoOpcao.QUERO if escolha == "q" else TrucoOpcao.CORRER
            )

        if resposta == TrucoOpcao.QUERO:
            if self.valor_da_mao_atual == 1:
                self.valor_da_mao_atual = 2
                print(f"{oponente.nome} aceitou! A mão agora vale 2 tentos.")
            elif self.valor_da_mao_atual == 2:
                self.valor_da_mao_atual = 3
                print(
                    f"{oponente.nome} aceitou o Retruco! A mão agora vale 3 tentos.")
            elif self.valor_da_mao_atual == 3:
                self.valor_da_mao_atual = 4
                print(
                    f"{oponente.nome} aceitou o Vale Quatro! A mão agora vale 4 tentos.")
            return self.valor_da_mao_atual

        elif resposta == TrucoOpcao.CORRER:
            print(f"{oponente.nome} correu do truco!")
            quem_pediu._pontuacao += self.valor_da_mao_atual
            return -1

    def gerenciar_pedido_envido(self, quem_pediu):
        self.envido_ja_cantado = True
        oponente = self._bot if quem_pediu == self._jogador else self._jogador
        print(f"\n{quem_pediu.nome} cantou ENVIDO!")

        if oponente == self._bot:
            pontos_bot_temp = self.regras.verifica_valor_envido(self._bot._mao)
            resposta = EnvidoOpcao.QUERO if pontos_bot_temp >= 27 else EnvidoOpcao.NAO_QUERO
            print(
                f"Bot respondeu: {'QUERO' if resposta == EnvidoOpcao.QUERO else 'NAO QUERO'}")
        else:
            resp_user = input(
                f"{self._jogador.nome}, aceita o Envido? (q = Quero / n = Não Quero): ").strip().lower()
            resposta = EnvidoOpcao.QUERO if resp_user == 'q' else EnvidoOpcao.NAO_QUERO

        if resposta == EnvidoOpcao.QUERO:
            print("Envido aceito!")
            pontos_j = self.regras.verifica_valor_envido(self._jogador._mao)
            pontos_b = self.regras.verifica_valor_envido(self._bot._mao)

            print(
                f"Pontuacao de Envido -> {self._jogador.nome}: {pontos_j} | Bot: {pontos_b}")

            vencedor = self.regras.comparacao_pontos_envido(pontos_j, pontos_b)

            if vencedor == 0:
                print(f"{self._jogador.nome} ganhou o Envido!")
                self._jogador._pontuacao += 2
            else:
                print("Bot ganhou o Envido!")
                self._bot._pontuacao += 2
        elif resposta == EnvidoOpcao.NAO_QUERO:
            print(f"{oponente.nome} correu do Envido.")
            quem_pediu._pontuacao += 1

    def inicio_partida(self):
        while True:
            # 1. PREPARAÇÃO DA MÃO
            self.baralho = Baralho()
            cartas = self.baralho.distribuir_cartas()

            cartas_jogador = cartas[0:3]
            cartas_bot = cartas[3:6]

            self.historico_rodadas.clear()
            self.vitorias_jogador = 0
            self.vitorias_bot = 0
            self.envido_permitido = True
            self.envido_ja_cantado = False
            self.flor_ja_cantada = False
            self.mao_inicial = self._jogador.maoVez

            self._jogador.recebeCartas(cartas_jogador)
            self._bot.recebeCartas(cartas_bot)

            # Placar atualizado na tela
            print(f"\n==================================================")
            print(
                f"🎮 PLACAR DA PARTIDA: {self._jogador.nome} [{self._jogador._pontuacao}] x [{self._bot._pontuacao}] Bot")
            print(f"==================================================")

            # 2. FASE PRELIMINAR (FLOR / ENVIDO)
            self.fase_preliminar()

            # 3. RODADAS DE CARTAS (MELHOR DE 3)
            for self.rodadas in range(3):
                print(f"\n======== {self.rodadas + 1}ª RODADA ========")

                carta_usuario = None
                carta_bot = None

                # ORDEM DE JOGADA DE ACORDO COM A VEZ
                if self._jogador._maoVez:
                    # VEZ DO USUÁRIO PRIMEIRO
                    print(f"\n👋 Suas cartas, {self._jogador.nome}:")
                    for c in self._jogador._mao:
                        print(f"   [ID: {c.id_carta}] -> {c}")

                    id_escolhido = int(
                        input("\nDigite o ID da carta que deseja jogar: "))
                    carta_usuario = self._jogador.jogarcarta(id_escolhido)

                    # VEZ DO BOT DEPOIS
                    id_bot = self._bot._mao[0].id_carta
                    carta_bot = self._bot.jogarcarta(id_bot)
                    print(f"🤖 Carta jogada pelo Bot: {carta_bot}")
                else:
                    # VEZ DO BOT PRIMEIRO
                    id_bot = self._bot._mao[0].id_carta
                    carta_bot = self._bot.jogarcarta(id_bot)

                    print(f"\n🤖 O Bot já jogou: {carta_bot}")
                    print(f"👋 Suas cartas, {self._jogador.nome}:")
                    for c in self._jogador._mao:
                        print(f"   [ID: {c.id_carta}] -> {c}")

                    id_escolhido = int(
                        input("\nDigite o ID da carta que deseja jogar: "))
                    carta_usuario = self._jogador.jogarcarta(id_escolhido)

                # AVALIAÇÃO DA RODADA
                resultado = self.regras.verifica_carta_mais_forte_da_rodada(
                    carta_usuario, carta_bot)
                self.historico_rodadas.append(resultado)

                if resultado == 0:
                    print(f"👉 Vencedor da rodada: {self._jogador.nome}")
                    self._jogador._maoVez = True
                    self._bot._maoVez = False
                    self.vitorias_jogador += 1
                elif resultado == 1:
                    print("👉 Vencedor da rodada: Bot")
                    self._jogador._maoVez = False
                    self._bot._maoVez = True
                    self.vitorias_bot += 1
                else:
                    print("👉 A rodada empatou.")

                self.envido_permitido = False

                vencedor_mao = self.vencedor_mao()
                if vencedor_mao == 0:
                    print(
                        f"\n🎉 {self._jogador.nome} ganhou a mão (+{self.valor_da_mao_atual} tento)!")
                    self._jogador._pontuacao += self.valor_da_mao_atual
                    break
                elif vencedor_mao == 1:
                    print(
                        f"\n🤖 Bot ganhou a mão (+{self.valor_da_mao_atual} tento)!")
                    self._bot._pontuacao += self.valor_da_mao_atual
                    break

            # 4. FINAL DA MÃO E PREPARAÇÃO DA PRÓXIMA
            self.rodadas = 0
            self.regras.trocaMaoJogadores()

            if self._jogador._pontuacao >= self.PONTUACAO_MAXIMA or self._bot._pontuacao >= self.PONTUACAO_MAXIMA:
                self.partida_encerrada = True
                print("\n🏆 ==========================================")
                print("🏆          PARTIDA FINALIZADA!          🏆")
                print(
                    f"   Placar Final: {self._jogador.nome} {self._jogador._pontuacao} x {self._bot._pontuacao} Bot")
                print("============================================\n")
                break
