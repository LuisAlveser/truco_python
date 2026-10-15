"use client";
import { useState, useEffect } from "react";
import { Carta, useTrucoSocket } from "@/app/hoocks/useTrucoSocket";
import Image from "next/image";
import TelaReiniciar from "./componentes/Tela_Reiniciar_Partida";
import Regras from "./componentes/Regras";
export default function MesaTruco() {

  const {
    statusConexao,
    partidaEncerrada,
    cartasJogador,
    placar,
    valorMao,
    cartaMesaUsuario,
    cartaMesaBot,
    cartasBot,
    jogarCarta,
    cantarTruco,
    cantarEnvido,
    cantarFlor,
    setCartasJogador,
    setCartaMesaUsuario,


  } = useTrucoSocket("skjksd");

  const [flor, setflor] = useState<boolean>(false)
  const [janela, setjanela] = useState<boolean>(false)
  const [janela_regras, setjanela_regras] = useState<boolean>(false)

  useEffect(() => {

    const verficaflor = () => {


      const temFlor =
        cartasJogador.length === 3 &&
        cartasJogador[0].neipe === cartasJogador[1].neipe &&
        cartasJogador[0].neipe === cartasJogador[2].neipe;

      setflor(temFlor)

    }

    verficaflor()
  }, [cartasJogador])
  useEffect(() => {
    if (placar.bot >= 24 || placar.jogador >= 24) {
      setjanela(true);
    }
  }, [placar]);

  const jogarCarta_id = (carta: Carta) => {
    jogarCarta(carta.id)
    setCartasJogador(prev => prev.filter(c => c.id !== carta.id));
    setCartaMesaUsuario(carta)


  }
  const regras = () => {
    setjanela_regras(!janela_regras)
  }

  if (statusConexao === "conectando") {
    return (
      <div className="flex h-screen items-center justify-center bg-green-950 text-white font-bold text-lg">
        Conectando à partida... 🃏
      </div>
    );
  }

  return (
    <div className="flex flex-col justify-between h-screen bg-green-900 text-white p-4 select-none">

      {/* 1. TOPO: PLACAR E BOT */}
      <header className="flex justify-between items-center bg-green-950 p-4 rounded-xl shadow-md">
        <div>
          <h2 className="text-lg font-bold">🤖 Bot (Rival)</h2>
          <p className="text-sm text-green-300">Pontuação Geral: {placar.bot}</p>
        </div>
        {/* Cartas do Bot viradas para baixo */}
        <div className="flex gap-2">
          {Array.from({ length: cartasBot }, (_, index) => (
            <Image
              className="transition-transform duration-300 hover:-translate-y-2"
              key={index}

              src={"/cartas/costas_da_carta.png"}
              alt="Descrição da imagem"
              width={50}
              height={50}
            />
          ))}
        </div>
      </header>
      {janela ? <TelaReiniciar janela={setjanela} /> : null}
      {/* 2. CENTRO: A MESA DE JOGO */}
      <main className="flex flex-col items-center justify-center gap-4 my-auto">
        <div className="bg-green-800/80 px-6 py-2 rounded-full border border-green-700 shadow-inner">
          <span className="text-sm font-semibold tracking-wide text-yellow-300">
            Mão atual valendo: {valorMao} {valorMao === 1 ? "tento" : "tentos"}
          </span>
        </div>

        {/* Cartas jogadas na rodada */}
        <div className="flex gap-8 items-center h-32">

          <div className="flex gap-8 items-center h-32">
            {cartaMesaUsuario ?
              <Image

                key={cartaMesaUsuario.id}

                src={
                  cartaMesaUsuario.neipe === "OROS" ? `/cartas/oros/oros_${cartaMesaUsuario.valor}_.png`
                    : cartaMesaUsuario.neipe === "BASTOS"
                      ? `/cartas/bastos/bastos_${cartaMesaUsuario.valor}_.png`
                      : cartaMesaUsuario.neipe === "ESPADAS"
                        ? `/cartas/espadas/espadas_${cartaMesaUsuario.valor}_.png`
                        : cartaMesaUsuario.neipe === "COPAS" ? `/cartas/copas/copas_${cartaMesaUsuario.valor}_.png` : ""
                }
                alt="Descrição da imagem"
                width={80}
                height={100}
              />
              : "Cartas Bot"
            }
            <span>VS</span>
            {cartaMesaBot ?
              <Image

                key={cartaMesaBot.id}

                src={
                  cartaMesaBot.neipe === "OROS" ? `/cartas/oros/oros_${cartaMesaBot.valor}_.png`
                    : cartaMesaBot.neipe === "BASTOS"
                      ? `/cartas/bastos/bastos_${cartaMesaBot.valor}_.png`
                      : cartaMesaBot.neipe === "ESPADAS"
                        ? `/cartas/espadas/espadas_${cartaMesaBot.valor}_.png`
                        : cartaMesaBot.neipe === "COPAS" ? `/cartas/copas/copas_${cartaMesaBot.valor}_.png` : ""
                }
                alt="Descrição da imagem"
                width={80}
                height={100}
              />
              : "Cartas Jogador"}
          </div>
        </div>
      </main>

      {/* 3. INFERIOR: SUAS CARTAS E AÇÕES */}
      <footer className="flex flex-col items-center gap-4 bg-green-950 p-4 rounded-xl shadow-md">
        {/* Botões de Aposta */}
        <div className="flex gap-3">
          <button disabled={partidaEncerrada} onClick={() => cantarTruco()} className=" cursor-pointer bg-yellow-600 hover:bg-yellow-500 text-white font-bold py-1.5 px-4 rounded-lg shadow transition disabled:opacity-50">
            Cantar Truco 📢
          </button>
          <button disabled={partidaEncerrada} onClick={() => cantarEnvido()} className="cursor-pointer bg-blue-600 hover:bg-blue-500 text-white font-bold py-1.5 px-4 rounded-lg shadow transition disabled:opacity-50">
            Cantar Envido 📊
          </button>

          {flor ?
            <button disabled={partidaEncerrada} onClick={() => cantarFlor()} className=" cursor-pointer bg-yellow-600 hover:bg-yellow-500 text-white font-bold py-1.5 px-4 rounded-lg shadow transition disabled:opacity-50">
              Cantar Flor 🌸
            </button>
            : null
          }
          <button disabled={partidaEncerrada} onClick={regras} className="cursor-pointer bg-red-600 hover:bg-blue-500 text-white font-bold py-1.5 px-4 rounded-lg shadow transition disabled:opacity-50">
            Regras
          </button>
        </div>
        {janela_regras ? <Regras janela_regras={setjanela_regras} /> : null}
        {/* Suas Cartas na Mão */}
        <div className="flex gap-4 cursor-pointer    " >
          {cartasJogador.map((carta) => (
            <Image
              className="transition-transform duration-300 hover:-translate-y-2"
              key={carta.id}
              onClick={() => { if (!partidaEncerrada) jogarCarta_id(carta) }}
              src={
                carta.neipe === "OROS" ? `/cartas/oros/oros_${carta.valor}_.png`
                  : carta.neipe === "BASTOS"
                    ? `/cartas/bastos/bastos_${carta.valor}_.png`
                    : carta.neipe === "ESPADAS"
                      ? `/cartas/espadas/espadas_${carta.valor}_.png`
                      : carta.neipe === "COPAS" ? `/cartas/copas/copas_${carta.valor}_.png` : ""
              }
              alt="Descrição da imagem"
              width={100}
              height={150}
            />
          ))}
        </div>
        <p className="text-sm text-green-300">Pontuação Geral: {placar.jogador}</p>
      </footer>

    </div>
  );
}