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

    partidas_ativas[room_id] = partida
    await websocket.send_json({
        "evento": "INICIO_MAO",
        "cartas_jogador": [{"id": c.id_carta, "nome": str(c)} for c in usuario._mao],
        "placar": {
            "jogador": usuario._pontuacao,
            "bot": bot._pontuacao
        },
        "turno_jogador": usuario._maoVez
    })

    try:
        while True:

            dados_recebidos = await websocket.receive_json()
            acao = dados_recebidos.get("acao")

            if acao == "JOGAR_CARTA":
                carta_id = dados_recebidos.get("carta_id")

                carta_usuario = usuario.jogarcarta(carta_id)
                carta_bot = bot.jogarcarta(bot._mao[0].id_carta)

                resultado = partida.regras.verifica_carta_mais_forte_da_rodada(
                    carta_usuario, carta_bot)

                await websocket.send_json({
                    "evento": "FIM_RODADA",
                    "carta_usuario": str(carta_usuario),
                    "carta_bot": str(carta_bot),
                    "vencedor_rodada": "jogador" if resultado == 0 else "bot",
                    "cartas_restantes_jogador": [{"id": c.id_carta, "nome": str(c)} for c in usuario._mao]
                })

            elif acao == "CANTAR_ENVIDO":

                pontos_j = partida.regras.verifica_valor_envido(usuario._mao)
                pontos_b = partida.regras.verifica_valor_envido(bot._mao)

                await websocket.send_json({
                    "evento": "RESULTADO_ENVIDO",
                    "pontos_jogador": pontos_j,
                    "pontos_bot": pontos_b
                })

            elif acao == "CANTAR_TRUCO":

                pontos_j = partida.gerenciar_pedido_truco(usuario)

                await websocket.send_json({
                    "evento": "RESULTADO_TRUCO",
                    "pontos_jogador": pontos_j,

                })

            elif acao == "CANTAR_ENVIDO":
                partida = Partida(usuario, bot)
                pontos_j = partida.gerenciar_pedido_envido(
                    usuario, usuario._mao)
                await websocket.send_json({
                    "evento": "RESULTADO_ENVIDO",
                    "pontos_jogador": pontos_j,
                })

    except WebSocketDisconnect:
        print(f"Usuário desconectou da sala {room_id}")
        if room_id in partidas_ativas:
            del partidas_ativas[room_id]
