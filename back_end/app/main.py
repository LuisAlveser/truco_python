from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.classes.usuario import Usuario
from app.classes.bot import Bot
from app.classes.partida import Partida
from app.classes.baralho import Baralho
app = FastAPI(title="Truco_Gaúcho_Api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
partidas_ativas = {}


def _placar(partida):
    return {
        "jogador": partida._jogador._pontuacao,
        "bot": partida._bot._pontuacao,
    }


def _serializar_carta(carta):
    return {
        "id": carta.id_carta,
        "nome": str(carta),
        "valor": carta.valor,
        "neipe": carta.naipe.name,
    }


def _vencedor_mao(historico, jogador_comeca):
    if len(historico) < 2:
        return None

    primeira, segunda = historico[:2]
    if primeira == segunda and primeira != 2:
        return primeira
    if primeira == 2 and segunda != 2:
        return segunda
    if primeira != 2 and segunda == 2:
        return primeira
    if len(historico) < 3:
        return None

    terceira = historico[2]
    if terceira != 2:
        return terceira
    return 0 if jogador_comeca else 1


def _iniciar_nova_mao(partida):
    partida.regras.trocaMaoJogadores()
    partida.baralho = Baralho()
    cartas = partida.baralho.distribuir_cartas()
    partida._jogador.recebeCartas(cartas[:3])
    partida._bot.recebeCartas(cartas[3:6])
    partida.historico_rodadas.clear()
    partida.vitorias_jogador = 0
    partida.vitorias_bot = 0
    partida.valor_da_mao_atual = 1
    partida.envido_ja_cantado = False
    partida.envido_permitido = True
    partida.flor_ja_cantada = False
    partida.mao_inicial = partida._jogador.maoVez
    _pontuar_flor_bot(partida)


def _pontuar_flor_bot(partida):
    if partida.regras.verifica_flor(partida._bot._mao):
        partida._bot._pontuacao += 3
        partida.envido_permitido = False


def _jogador_tem_flor(partida):
    return partida.regras.verifica_flor(partida._jogador._mao)


async def _enviar_fim_partida(websocket, partida):
    if (
        partida._jogador._pontuacao < partida.PONTUACAO_MAXIMA
        and partida._bot._pontuacao < partida.PONTUACAO_MAXIMA
    ):
        return False

    partida.partida_encerrada = True
    if partida._jogador._pontuacao == partida._bot._pontuacao:
        vencedor = "empate"
    else:
        vencedor = (
            "jogador"
            if partida._jogador._pontuacao > partida._bot._pontuacao
            else "bot"
        )
    await websocket.send_json({
        "evento": "PARTIDA_ENCERRADA",
        "placar": _placar(partida),
        "vencedor": vencedor,
    })
    return True


@app.websocket("/ws/partida/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()

    usuario = Usuario(nome="Jogador")
    bot = Bot(nome="Bot")
    partida = Partida(jogador=usuario, bot=bot)

    partida.baralho = Baralho()
    cartas = partida.baralho.distribuir_cartas()
    usuario.recebeCartas(cartas[0:3])
    bot.recebeCartas(cartas[3:6])
    partida.mao_inicial = usuario.maoVez
    _pontuar_flor_bot(partida)

    partidas_ativas[room_id] = partida
    await websocket.send_json({
        "evento": "INICIO_MAO",
        "cartas_jogador": [_serializar_carta(c) for c in usuario._mao],
        "cartas_bot": len(bot._mao),
        "placar": _placar(partida),
        "turno_jogador": usuario._maoVez
    })

    try:
        while True:

            dados_recebidos = await websocket.receive_json()
            acao = dados_recebidos.get("acao")

            if partida.partida_encerrada:
                await websocket.send_json({
                    "evento": "ERRO",
                    "mensagem": "A partida já foi encerrada.",
                })
                continue

            if acao == "JOGAR_CARTA":
                carta_id = dados_recebidos.get("carta_id")

                if _jogador_tem_flor(partida) and not partida.flor_ja_cantada:
                    await websocket.send_json({
                        "evento": "ERRO",
                        "mensagem": "Cante sua Flor antes de jogar uma carta.",
                    })
                    continue

                if not bot._mao:
                    await websocket.send_json({
                        "evento": "ERRO",
                        "mensagem": "A mão terminou. Aguarde a próxima."
                    })
                    continue

                carta_usuario = usuario.jogarcarta(carta_id)
                if carta_usuario is None:
                    await websocket.send_json({
                        "evento": "ERRO",
                        "mensagem": "Carta inválida ou já jogada."
                    })
                    continue

                carta_bot = bot.jogarcarta(bot._mao[0].id_carta)
                if carta_bot is None:
                    await websocket.send_json({
                        "evento": "ERRO",
                        "mensagem": "O bot não conseguiu jogar uma carta."
                    })
                    continue

                resultado = partida.regras.verifica_carta_mais_forte_da_rodada(
                    carta_usuario, carta_bot)
                partida.historico_rodadas.append(resultado)
                partida.envido_permitido = False
                if resultado == 0:
                    usuario.maoVez = True
                    bot.maoVez = False
                elif resultado == 1:
                    usuario.maoVez = False
                    bot.maoVez = True

                vencedor_mao = _vencedor_mao(
                    partida.historico_rodadas, partida.mao_inicial
                )
                if vencedor_mao == 0:
                    usuario._pontuacao += partida.valor_da_mao_atual
                elif vencedor_mao == 1:
                    bot._pontuacao += partida.valor_da_mao_atual

                placar = _placar(partida)

                await websocket.send_json({
                    "evento": "FIM_RODADA",
                    "carta_usuario": _serializar_carta(carta_usuario),
                    "carta_bot": _serializar_carta(carta_bot),
                    "vencedor_rodada": (
                        "jogador" if resultado == 0
                        else "bot" if resultado == 1
                        else "empate"
                    ),
                    "vencedor_mao": (
                        "jogador" if vencedor_mao == 0
                        else "bot" if vencedor_mao == 1
                        else None
                    ),
                    "mao_encerrada": vencedor_mao is not None,
                    "placar": placar,
                    "cartas_bot": len(bot._mao),
                    "cartas_restantes_jogador": [
                        _serializar_carta(c) for c in usuario._mao
                    ]
                })
                if vencedor_mao is not None:
                    if await _enviar_fim_partida(websocket, partida):
                        continue
                    else:
                        _iniciar_nova_mao(partida)
                        placar = _placar(partida)
                        if await _enviar_fim_partida(websocket, partida):
                            continue
                        await websocket.send_json({
                            "evento": "INICIO_MAO",
                            "cartas_jogador": [
                                _serializar_carta(c) for c in usuario._mao
                            ],
                            "cartas_bot": len(bot._mao),
                            "placar": placar,
                            "turno_jogador": usuario.maoVez,
                        })

            elif acao == "CANTAR_ENVIDO":
                if (
                    not partida.envido_permitido
                    or partida.envido_ja_cantado
                    or partida.regras.verifica_flor(usuario._mao)
                    or partida.regras.verifica_flor(bot._mao)
                ):
                    await websocket.send_json({
                        "evento": "ERRO",
                        "mensagem": "Envido não pode ser cantado nesta situação.",
                    })
                    continue
                pontos_j = partida.regras.verifica_valor_envido(usuario._mao)
                pontos_b = partida.regras.verifica_valor_envido(bot._mao)
                vencedor = partida.regras.comparacao_pontos_envido(
                    pontos_j, pontos_b
                )
                if pontos_j == pontos_b:
                    vencedor = 0 if partida.mao_inicial else 1
                if vencedor == 0:
                    usuario._pontuacao += 2
                else:
                    bot._pontuacao += 2

                partida.envido_ja_cantado = True
                partida.envido_permitido = False

                await websocket.send_json({
                    "evento": "RESULTADO_ENVIDO",
                    "pontos_jogador": pontos_j,
                    "pontos_bot": pontos_b,
                    "vencedor": "jogador" if vencedor == 0 else "bot",
                    "placar": _placar(partida),
                })
                await _enviar_fim_partida(websocket, partida)

            elif acao == "CANTAR_TRUCO":
                if _jogador_tem_flor(partida) and not partida.flor_ja_cantada:
                    await websocket.send_json({
                        "evento": "ERRO",
                        "mensagem": "Cante sua Flor antes de pedir Truco.",
                    })
                    continue
                if partida.valor_da_mao_atual >= 4:
                    await websocket.send_json({
                        "evento": "ERRO",
                        "mensagem": "A mão já está no valor máximo de 4 tentos.",
                    })
                    continue

                partida.valor_da_mao_atual += 1
                partida.envido_permitido = False

                await websocket.send_json({
                    "evento": "RESULTADO_TRUCO",
                    "valor_mao": partida.valor_da_mao_atual,
                    "aceito": True,
                    "placar": _placar(partida),
                })

            elif acao == "CANTAR_FLOR":
                if partida.flor_ja_cantada or not _jogador_tem_flor(partida):
                    await websocket.send_json({
                        "evento": "ERRO",
                        "mensagem": "Você não pode cantar Flor nesta situação.",
                    })
                    continue

                usuario._pontuacao += 3
                partida.flor_ja_cantada = True
                partida.envido_permitido = False
                await websocket.send_json({
                    "evento": "RESULTADO_CANTAR_FLOR",
                    "pontos_jogador": 3,
                    "placar": _placar(partida),
                })
                await _enviar_fim_partida(websocket, partida)

            else:
                await websocket.send_json({
                    "evento": "ERRO",
                    "mensagem": "Ação desconhecida.",
                })

    except WebSocketDisconnect:
        print(f"Usuário desconectou da sala {room_id}")
        if room_id in partidas_ativas:
            del partidas_ativas[room_id]
