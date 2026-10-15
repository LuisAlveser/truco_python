from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.classes.usuario import Usuario
from app.classes.bot import Bot
from app.classes.partida import Partida
from app.classes.baralho import Baralho
from app.classes.regras import Regras
app = FastAPI(title="Truco_Gaúcho_Api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

partidas_ativas = {}


def _verificar_fim_partida(partida):
    pontos_jogador = partida._jogador._pontuacao
    pontos_bot = partida._bot._pontuacao
    if (
        pontos_jogador < partida.PONTUACAO_MAXIMA
        and pontos_bot < partida.PONTUACAO_MAXIMA
    ):
        return None

    partida.partida_encerrada = True
    if pontos_jogador == pontos_bot:
        return "empate"
    return "jogador" if pontos_jogador > pontos_bot else "bot"


def _preparar_nova_mao(partida, alternar_mao=False):
    if alternar_mao:
        partida.regras.trocaMaoJogadores()

    partida.baralho = Baralho()
    cartas = partida.baralho.distribuir_cartas()
    partida._jogador.recebeCartas(cartas[:3])
    partida._bot.recebeCartas(cartas[3:6])
    partida.vitorias_jogador = 0
    partida.vitorias_bot = 0
    partida.historico_rodadas.clear()
    partida.valor_da_mao_atual = 1
    partida.envido_ja_cantado = False
    partida.envido_permitido = True
    partida.flor_ja_cantada = False
    partida.mao_inicial = partida._jogador.maoVez
    partida.partida_encerrada = False


def _pontuar_flor_bot(partida):
    if partida.regras.verifica_flor(partida._bot._mao):
        partida._bot._pontuacao += 3
        partida.envido_permitido = False


def _flor_jogador_pendente(partida):
    return (
        not partida.flor_ja_cantada
        and partida.regras.verifica_flor(partida._jogador._mao)
    )


@app.websocket("/ws/partida/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()

    usuario = Usuario(nome="Luis")
    bot = Bot(nome="Bot")
    partida = Partida(jogador=usuario, bot=bot)

    partida.baralho = Baralho()
    cartas = partida.baralho.distribuir_cartas()

    usuario.recebeCartas(cartas[0:3])
    bot.recebeCartas(cartas[3:6])
    partida.mao_inicial = usuario.maoVez
    regra = Regras(usuario, bot)

    partidas_ativas[room_id] = partida

    _pontuar_flor_bot(partida)
    vencedor_partida = _verificar_fim_partida(partida)

    await websocket.send_json({
        "evento": "INICIO_MAO",
        "cartas_jogador": [c.to_dict() for c in usuario._mao],
        "cartas_bot": len(bot._mao),
        "placar": {
            "jogador": usuario._pontuacao,
            "bot": bot._pontuacao
        },
        "turno_jogador": usuario._maoVez
    })
    if vencedor_partida:
        await websocket.send_json({
            "evento": "PARTIDA_ENCERRADA",
            "placar": {
                "jogador": usuario._pontuacao,
                "bot": bot._pontuacao
            },
            "vencedor": vencedor_partida
        })

    try:
        while True:
            dados_recebidos = await websocket.receive_json()
            acao = dados_recebidos.get("acao")

            if partida.partida_encerrada:
                await websocket.send_json({
                    "evento": "ERRO",
                    "mensagem": "A partida já foi encerrada."
                })
                continue

            if acao == "JOGAR_CARTA":
                carta_id = dados_recebidos.get("carta_id")
                if partidas_ativas.get(room_id) is not partida:
                    await websocket.send_json({"evento": "ERRO", "mensagem": "Partida não encontrada."})
                    continue

                if _flor_jogador_pendente(partida):
                    await websocket.send_json({
                        "evento": "ERRO",
                        "mensagem": "Cante sua Flor antes de jogar uma carta."
                    })
                    continue

                if not bot._mao:
                    await websocket.send_json({
                        "evento": "ERRO",
                        "mensagem": "O bot não possui cartas para jogar."
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
                        "mensagem": "Não foi possível selecionar a carta do bot."
                    })
                    continue

                resultado = partida.regras.verifica_carta_mais_forte_da_rodada(
                    carta_usuario, carta_bot
                )

                partida.historico_rodadas.append(resultado)
                if resultado == 0:
                    partida.vitorias_jogador += 1
                    vencedor_rodada = "jogador"
                    usuario.maoVez = True
                    bot.maoVez = False
                elif resultado == 1:
                    partida.vitorias_bot += 1
                    vencedor_rodada = "bot"
                    usuario.maoVez = False
                    bot.maoVez = True
                else:
                    vencedor_rodada = "empate"
                partida.envido_permitido = False

                vencedor_mao_numero = partida.vencedor_mao()
                vencedor_mao = (
                    "jogador" if vencedor_mao_numero == 0
                    else "bot" if vencedor_mao_numero == 1
                    else None
                )
                mao_encerrada = vencedor_mao is not None
                if vencedor_mao == "jogador":
                    usuario._pontuacao += partida.valor_da_mao_atual
                elif vencedor_mao == "bot":
                    bot._pontuacao += partida.valor_da_mao_atual

                cartas_restantes_formatadas = [
                    {
                        "id": c.id_carta,
                        "valor": c._valor,
                        "neipe": c._naipe.name,
                        "nome": str(c)
                    } for c in usuario._mao
                ]

                await websocket.send_json({
                    "evento": "FIM_RODADA",
                    "carta_usuario": {
                        "id": carta_usuario.id_carta,
                        "valor": carta_usuario._valor,
                        "neipe": carta_usuario._naipe.name,
                        "nome": str(carta_usuario)
                    },
                    "carta_bot": {
                        "id": carta_bot.id_carta,
                        "valor": carta_bot._valor,
                        "neipe": carta_bot._naipe.name,
                        "nome": str(carta_bot)
                    },
                    "vencedor_rodada": vencedor_rodada,
                    "vencedor_mao": vencedor_mao,
                    "mao_encerrada": mao_encerrada,
                    "placar": {
                        "jogador": usuario._pontuacao,
                        "bot": bot._pontuacao
                    },
                    "cartas_restantes_jogador": cartas_restantes_formatadas
                })
                if mao_encerrada:
                    vencedor_partida = _verificar_fim_partida(partida)
                    if vencedor_partida:
                        await websocket.send_json({
                            "evento": "PARTIDA_ENCERRADA",
                            "placar": {
                                "jogador": usuario._pontuacao,
                                "bot": bot._pontuacao
                            },
                            "vencedor": vencedor_partida
                        })
                    else:
                        _preparar_nova_mao(partida, alternar_mao=True)
                        _pontuar_flor_bot(partida)
                        vencedor_partida = _verificar_fim_partida(partida)
                        if vencedor_partida:
                            await websocket.send_json({
                                "evento": "PARTIDA_ENCERRADA",
                                "placar": {
                                    "jogador": usuario._pontuacao,
                                    "bot": bot._pontuacao
                                },
                                "vencedor": vencedor_partida
                            })
                        else:
                            await websocket.send_json({
                                "evento": "INICIO_MAO",
                                "cartas_jogador": [
                                    c.to_dict() for c in usuario._mao
                                ],
                                "cartas_bot": len(bot._mao),
                                "placar": {
                                    "jogador": usuario._pontuacao,
                                    "bot": bot._pontuacao
                                },
                                "turno_jogador": usuario._maoVez
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
                        "mensagem": "Envido não pode ser cantado nesta situação."
                    })
                    continue
                partida.gerenciar_pedido_envido(usuario)
                partida.envido_permitido = False
                await websocket.send_json({
                    "evento": "RESULTADO_ENVIDO",
                    "pontos_jogador": usuario._pontuacao,
                    "pontos_bot": bot._pontuacao,
                    "placar": {
                        "jogador": usuario._pontuacao,
                        "bot": bot._pontuacao
                    }
                })
                vencedor_partida = _verificar_fim_partida(partida)
                if vencedor_partida:
                    await websocket.send_json({
                        "evento": "PARTIDA_ENCERRADA",
                        "placar": {
                            "jogador": usuario._pontuacao,
                            "bot": bot._pontuacao
                        },
                        "vencedor": vencedor_partida
                    })

            elif acao == "CANTAR_TRUCO":
                if _flor_jogador_pendente(partida):
                    await websocket.send_json({
                        "evento": "ERRO",
                        "mensagem": "Cante sua Flor antes de pedir Truco."
                    })
                    continue
                if partida.valor_da_mao_atual >= 4:
                    await websocket.send_json({
                        "evento": "ERRO",
                        "mensagem": "A mão já está no valor máximo de 4 tentos."
                    })
                    continue
                partida.envido_permitido = False
                ponto_truco = partida.gerenciar_pedido_truco(usuario)
                await websocket.send_json({
                    "evento": "RESULTADO_TRUCO",
                    "valor_mao": partida.valor_da_mao_atual,
                    "pontos_jogador": ponto_truco,
                    "placar": {
                        "jogador": usuario._pontuacao,
                        "bot": bot._pontuacao
                    }
                })
                if ponto_truco == -1:
                    vencedor_partida = _verificar_fim_partida(partida)
                    if vencedor_partida:
                        await websocket.send_json({
                            "evento": "PARTIDA_ENCERRADA",
                            "placar": {
                                "jogador": usuario._pontuacao,
                                "bot": bot._pontuacao
                            },
                            "vencedor": vencedor_partida
                        })
                    else:
                        _preparar_nova_mao(partida, alternar_mao=True)
                        _pontuar_flor_bot(partida)
                        vencedor_partida = _verificar_fim_partida(partida)
                        if vencedor_partida:
                            await websocket.send_json({
                                "evento": "PARTIDA_ENCERRADA",
                                "placar": {
                                    "jogador": usuario._pontuacao,
                                    "bot": bot._pontuacao
                                },
                                "vencedor": vencedor_partida
                            })
                        else:
                            await websocket.send_json({
                                "evento": "INICIO_MAO",
                                "cartas_jogador": [
                                    c.to_dict() for c in usuario._mao
                                ],
                                "cartas_bot": len(bot._mao),
                                "placar": {
                                    "jogador": usuario._pontuacao,
                                    "bot": bot._pontuacao
                                },
                                "turno_jogador": usuario._maoVez
                            })

            elif acao == "CANTAR_FLOR":
                if (
                    partida.flor_ja_cantada
                    or len(usuario._mao) != 3
                    or not regra.verifica_flor(usuario._mao)
                ):
                    await websocket.send_json({
                        "evento": "ERRO",
                        "mensagem": "Você não pode cantar flor nesta situação."
                    })
                    continue

                usuario._pontuacao += 3
                partida.flor_ja_cantada = True
                partida.envido_permitido = False
                await websocket.send_json({
                    "evento": "RESULTADO_CANTAR_FLOR",
                    "pontos_jogador": 3,
                    "resultado_da_flor": True,
                    "placar": {
                        "jogador": usuario._pontuacao,
                        "bot": bot._pontuacao
                    }
                })
                vencedor_partida = _verificar_fim_partida(partida)
                if vencedor_partida:
                    await websocket.send_json({
                        "evento": "PARTIDA_ENCERRADA",
                        "placar": {
                            "jogador": usuario._pontuacao,
                            "bot": bot._pontuacao
                        },
                        "vencedor": vencedor_partida
                    })
            else:
                await websocket.send_json({
                    "evento": "ERRO",
                    "mensagem": "Ação desconhecida."
                })

    except WebSocketDisconnect:
        print(f"Usuário desconectou da sala {room_id}")
        if partidas_ativas.get(room_id) is partida:
            del partidas_ativas[room_id]
