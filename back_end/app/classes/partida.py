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
        self.PONTUACAO_MAXIMA = 24
        self.partida_encerrada = False

        if not hasattr(self._jogador, "_maoVez") or not hasattr(self._bot, "_maoVez"):
            self._jogador._maoVez = True
            self._bot._maoVez = False

    def fase_preliminar(self):
        """Gerencia os cantos de Flor e Envido antes das jogadas das cartas"""
        print("\n--- FASE PRELIMINAR (FLOR E ENVIDO) ---")

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

        if self.envido_permitido and not self.envido_ja_cantado:
            quer_envido = input(
                f"\n{self._jogador.nome}, deseja cantar ENVIDO? (s/n): ").strip().lower()
            if quer_envido == 's':
                self.gerenciar_pedido_envido(self._jogador)
            else:

                pontos_envido_bot = self.regras.verifica_valor_envido(
                    self._bot._mao)
                if pontos_envido_bot >= 28:
                    self.gerenciar_pedido_envido(self._bot)

    def gerenciar_pedido_truco(self, quem_pediu):
        oponente = self._bot if quem_pediu == self._jogador else self._jogador
        print(f"\n📢 {quem_pediu.nome} gritou TRUCO!")

        resposta = oponente.decidir_truco()

        if resposta == TrucoOpcao.QUERO:
            if self.valor_da_mao_atual == 1:
                self.valor_da_mao_atual = 2
                print(f"✅ {oponente.nome} aceitou! A mão agora vale 2 tentos.")
            elif self.valor_da_mao_atual == 2:
                self.valor_da_mao_atual = 3
                print(
                    f"✅ {oponente.nome} aceitou o Retruco! A mão agora vale 3 tentos.")
            elif self.valor_da_mao_atual == 3:
                self.valor_da_mao_atual = 4
                print(
                    f"✅ {oponente.nome} aceitou o Vale Quatro! A mão agora vale 4 tentos.")
            return self.valor_da_mao_atual

        elif resposta == TrucoOpcao.CORRER:
            print(f"🏃 {oponente.nome} correu do truco!")
            quem_pediu._pontuacao += self.valor_da_mao_atual
            return -1

    def gerenciar_pedido_envido(self, quem_pediu):
        self.envido_ja_cantado = True
        oponente = self._bot if quem_pediu == self._jogador else self._jogador
        print(f"\n📢 {quem_pediu.nome} cantou ENVIDO!")

        if oponente == self._bot:
            pontos_bot_temp = self.regras.verifica_valor_envido(self._bot._mao)
            resposta = EnvidoOpcao.QUERO if pontos_bot_temp >= 27 else EnvidoOpcao.NAO_QUERO
            print(
                f"🤖 Bot respondeu: {'QUERO' if resposta == EnvidoOpcao.QUERO else 'NÃO QUERO'}")
        else:
            resp_user = input(
                f"{self._jogador.nome}, aceita o Envido? (q = Quero / n = Não Quero): ").strip().lower()
            resposta = EnvidoOpcao.QUERO if resp_user == 'q' else EnvidoOpcao.NAO_QUERO

        if resposta == EnvidoOpcao.QUERO:
            print("✅ Envido aceito!")
            pontos_j = self.regras.verifica_valor_envido(self._jogador._mao)
            pontos_b = self.regras.verifica_valor_envido(self._bot._mao)

            print(
                f"📊 Pontuação de Envido -> {self._jogador.nome}: {pontos_j} | Bot: {pontos_b}")

            vencedor = self.regras.comparacao_pontos_envido(pontos_j, pontos_b)

            if vencedor == 0:
                print(f"🏆 {self._jogador.nome} ganhou o Envido!")
                self._jogador._pontuacao += 2
            else:
                print("🏆 Bot ganhou o Envido!")
                self._bot._pontuacao += 2
        elif resposta == EnvidoOpcao.NAO_QUERO:
            print(f"❌ {oponente.nome} correu do Envido.")
            quem_pediu._pontuacao += 1

    def inicio_partida(self):
        while True:

            self.baralho = Baralho()
            cartas = self.baralho.distribuir_cartas()

            cartas_jogador = cartas[0:3]
            cartas_bot = cartas[3:6]

            self.historico_rodadas.clear()
            self.vitorias_jogador = 0
            self.vitorias_bot = 0
            self.envido_permitido = True
            self.envido_ja_cantado = False

            self._jogador.recebeCartas(cartas_jogador)
            self._bot.recebeCartas(cartas_bot)

            print(f"\n==================================================")
            print(
                f"🎮 PLACAR DA PARTIDA: {self._jogador.nome} [{self._jogador._pontuacao}] x [{self._bot._pontuacao}] Bot")
            print(f"==================================================")

            self.fase_preliminar()

            for self.rodadas in range(3):
                print(f"\n======== {self.rodadas + 1}ª RODADA ========")

                carta_usuario = None
                carta_bot = None

                if self._jogador._maoVez:

                    print(f"\n👋 Suas cartas, {self._jogador.nome}:")
                    for c in self._jogador._mao:
                        print(f"   [ID: {c.id_carta}] -> {c}")

                    id_escolhido = int(
                        input("\nDigite o ID da carta que deseja jogar: "))
                    carta_usuario = self._jogador.jogarcarta(id_escolhido)

                    id_bot = self._bot._mao[0].id_carta
                    carta_bot = self._bot.jogarcarta(id_bot)
                    print(f"🤖 Carta jogada pelo Bot: {carta_bot}")
                else:

                    id_bot = self._bot._mao[0].id_carta
                    carta_bot = self._bot.jogarcarta(id_bot)

                    print(f"\n🤖 O Bot já jogou: {carta_bot}")
                    print(f"👋 Suas cartas, {self._jogador.nome}:")
                    for c in self._jogador._mao:
                        print(f"   [ID: {c.id_carta}] -> {c}")

                    id_escolhido = int(
                        input("\nDigite o ID da carta que deseja jogar: "))
                    carta_usuario = self._jogador.jogarcarta(id_escolhido)

                resultado = self.regras.verifica_carta_mais_forte_da_rodada(
                    carta_usuario, carta_bot)
                self.historico_rodadas.append(resultado)

                if resultado == 0:
                    print(f"👉 Vencedor da rodada: {self._jogador.nome}")
                    self._jogador._maoVez = True
                    self._bot._maoVez = False
                    self.vitorias_jogador += 1
                else:
                    print("👉 Vencedor da rodada: Bot")
                    self._jogador._maoVez = False
                    self._bot._maoVez = True
                    self.vitorias_bot += 1

                self.envido_permitido = False

                if self.vitorias_jogador == 2:
                    print(
                        f"\n🎉 {self._jogador.nome} ganhou a mão (+{self.valor_da_mao_atual} tento)!")
                    self._jogador._pontuacao += self.valor_da_mao_atual
                    break
                elif self.vitorias_bot == 2:
                    print(
                        f"\n🤖 Bot ganhou a mão (+{self.valor_da_mao_atual} tento)!")
                    self._bot._pontuacao += self.valor_da_mao_atual
                    break

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
