import unittest

from app.classes.bot import Bot
from app.classes.carta import Carta, Naipe
from app.classes.partida import Partida
from app.classes.regras import Regras
from app.classes.usuario import Usuario
from app.main import (
    _flor_jogador_pendente,
    _pontuar_flor_bot,
    _verificar_fim_partida,
)


def carta(valor, naipe):
    return Carta(0, naipe, valor, "", "")


class RegrasTest(unittest.TestCase):
    def setUp(self):
        self.jogador = Usuario("Jogador")
        self.bot = Bot("Bot")
        self.regras = Regras(self.jogador, self.bot)

    def test_empate_nao_deve_ser_vitoria_do_bot(self):
        resultado = self.regras.verifica_carta_mais_forte_da_rodada(
            carta(6, Naipe.COPAS),
            carta(6, Naipe.ESPADAS),
        )
        self.assertEqual(resultado, 2)

    def test_quatro_de_copas_tem_o_mesmo_peso_dos_outros_quatros(self):
        pesos = {
            self.regras.obter_peso(carta(4, naipe))
            for naipe in Naipe
        }
        self.assertEqual(pesos, {1})

    def test_envido_escolhe_o_melhor_par_do_mesmo_naipe(self):
        mao = [
            carta(1, Naipe.COPAS),
            carta(7, Naipe.COPAS),
            carta(6, Naipe.COPAS),
        ]
        self.assertEqual(self.regras.verifica_valor_envido(mao), 33)

    def test_envido_sem_par_vale_a_maior_carta(self):
        mao = [
            carta(1, Naipe.COPAS),
            carta(7, Naipe.ESPADAS),
            carta(6, Naipe.BASTOS),
        ]
        self.assertEqual(self.regras.verifica_valor_envido(mao), 7)


class VencedorMaoTest(unittest.TestCase):
    def setUp(self):
        self.partida = Partida(Usuario("Jogador"), Bot("Bot"))

    def test_duas_primeiras_rodadas_vencidas_pelo_mesmo_jogador(self):
        self.partida.historico_rodadas = [0, 0]
        self.assertEqual(self.partida.vencedor_mao(), 0)

    def test_rodada_empatada_nao_da_vitoria_ao_bot(self):
        self.partida.historico_rodadas = [2, 0]
        self.assertEqual(self.partida.vencedor_mao(), 0)
        self.partida.historico_rodadas = [1, 2]
        self.assertEqual(self.partida.vencedor_mao(), 1)

    def test_terceira_rodada_desempata_e_empate_final_favorece_mao(self):
        self.partida.historico_rodadas = [0, 1, 2]
        self.assertEqual(self.partida.vencedor_mao(), 0)
        self.partida.historico_rodadas = [2, 2, 2]
        self.assertEqual(self.partida.vencedor_mao(), 0)
        self.partida.mao_inicial = False
        self.assertEqual(self.partida.vencedor_mao(), 1)


class FlorWebSocketTest(unittest.TestCase):
    def setUp(self):
        self.partida = Partida(Usuario("Jogador"), Bot("Bot"))

    def test_jogador_precisa_cantar_flor_antes_de_jogar(self):
        self.partida._jogador._mao = [
            carta(1, Naipe.COPAS),
            carta(7, Naipe.COPAS),
            carta(6, Naipe.COPAS),
        ]
        self.assertTrue(_flor_jogador_pendente(self.partida))
        self.partida.flor_ja_cantada = True
        self.assertFalse(_flor_jogador_pendente(self.partida))

    def test_flor_do_bot_pontua_e_partida_encerra_ao_chegar_a_24(self):
        self.partida._bot._mao = [
            carta(1, Naipe.ESPADAS),
            carta(7, Naipe.ESPADAS),
            carta(6, Naipe.ESPADAS),
        ]
        _pontuar_flor_bot(self.partida)
        self.assertEqual(self.partida._bot._pontuacao, 3)
        self.assertFalse(self.partida.envido_permitido)

        self.partida._jogador._pontuacao = 24
        self.assertEqual(_verificar_fim_partida(self.partida), "jogador")
        self.assertTrue(self.partida.partida_encerrada)


if __name__ == "__main__":
    unittest.main()
