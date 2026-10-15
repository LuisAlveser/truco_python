import { useEffect, useState, useRef, useCallback } from "react";

export interface Carta {
    id: number;
    nome: string;
    valor: number;
    neipe: string;
}

export interface Placar {
    jogador: number;
    bot: number;
}

export function useTrucoSocket(roomId: string) {
    const [cartasJogador, setCartasJogador] = useState<Carta[]>([]);
    const [cartasBot, setCartasBot] = useState(0);
    const [placar, setPlacar] = useState<Placar>({ jogador: 0, bot: 0 });
    const [partidaEncerrada, setPartidaEncerrada] = useState(false);
    const [turnoJogador, setTurnoJogador] = useState<boolean>(false);
    const [valorMao, setValorMao] = useState<number>(1);
    const [cartaMesaUsuario, setCartaMesaUsuario] = useState<Carta | null>(null);
    const [cartaMesaBot, setCartaMesaBot] = useState<Carta | null>(null);
    const [statusConexao, setStatusConexao] = useState<"conectando" | "conectado" | "desconectado">("conectando");

    const socketRef = useRef<WebSocket | null>(null);

    // Declaração antecipada para o onopen/onmessage
    const enviarAcao = useCallback((dados: object) => {
        if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
            socketRef.current.send(JSON.stringify(dados));
        } else {
            console.error("WebSocket não está conectado.");
        }
    }, []);

    const cantarFlor = useCallback(() => {
        enviarAcao({ acao: "CANTAR_FLOR" });
    }, [enviarAcao]);

    useEffect(() => {
        const ws = new WebSocket(`ws://localhost:8000/ws/partida/${roomId}`);
        socketRef.current = ws;

        ws.onopen = () => {
            console.log("🟢 Conectado ao servidor de Truco");
            setStatusConexao("conectado");
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log("📩 Evento recebido:", data);

            switch (data.evento) {
                case "INICIO_MAO":
                    setPartidaEncerrada(false);
                    if (data.cartas_jogador) {
                        setCartasJogador(data.cartas_jogador);
                    }
                    if (data.cartas_bot !== undefined) setCartasBot(data.cartas_bot);
                    if (data.placar) setPlacar(data.placar);
                    if (data.turno_jogador !== undefined) setTurnoJogador(data.turno_jogador);

                    setValorMao(1);
                    setCartaMesaUsuario(null);
                    setCartaMesaBot(null);
                    break;

                case "FIM_RODADA":
                    setCartaMesaUsuario(data.carta_usuario);
                    setCartaMesaBot(data.carta_bot);
                    setCartasBot((cartas) => Math.max(0, cartas - 1));
                    if (data.cartas_restantes_jogador) {
                        setCartasJogador(data.cartas_restantes_jogador);
                    }
                    if (data.placar) {
                        setPlacar(data.placar);
                    }
                    break;

                case "RESULTADO_TRUCO":
                    if (data.valor_mao && data.valor_mao > 0) {
                        setValorMao(data.valor_mao);
                    }
                    if (data.placar) {
                        setPlacar(data.placar);
                    }
                    break;

                case "RESULTADO_ENVIDO":
                    alert(`Envido! Você: ${data.pontos_jogador} pts | Bot: ${data.pontos_bot} pts`);
                    if (data.placar) {
                        setPlacar(data.placar);
                    }
                    break;

                case "RESULTADO_CANTAR_FLOR":
                    if (data.placar) setPlacar(data.placar);
                    break;

                case "PARTIDA_ENCERRADA":
                    if (data.placar) setPlacar(data.placar);
                    setPartidaEncerrada(true);
                    alert(`Partida encerrada! Vencedor: ${data.vencedor}`);
                    break;

                case "ERRO":
                    alert(`Erro: ${data.mensagem}`);
                    break;

                default:
                    break;
            }
        };

        ws.onerror = (error) => {
            console.error("❌ Erro na conexão WebSocket:", error);
        };

        ws.onclose = (event) => {
            console.log(`🔴 Desconectado do servidor. Código: ${event.code}, Motivo: ${event.reason}`);
            setStatusConexao("desconectado");
        };

        return () => {
            ws.close();
        };
    }, [roomId, cantarFlor]);

    const jogarCarta = (cartaId: number) => {
        enviarAcao({ acao: "JOGAR_CARTA", carta_id: cartaId });
    };

    const cantarTruco = () => {
        enviarAcao({ acao: "CANTAR_TRUCO" });
    };

    const cantarEnvido = () => {
        enviarAcao({ acao: "CANTAR_ENVIDO" });
    };

    return {
        statusConexao,
        partidaEncerrada,
        cartasJogador,
        placar,
        turnoJogador,
        valorMao,
        cartaMesaUsuario,
        cartaMesaBot,
        cartasBot,
        jogarCarta,
        cantarTruco,
        cantarEnvido,
        cantarFlor,
        setCartaMesaBot,
        setCartasJogador,
        setCartaMesaUsuario,
    };
}