"use client";
import { Dispatch, SetStateAction } from "react";

interface RegrasProps {
    janela_regras: Dispatch<SetStateAction<boolean>>;
}

export default function TelaRegras({ janela_regras }: RegrasProps) {
    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-fade-in p-4">
            <div className="bg-green-950 border border-green-700/60 rounded-2xl p-6 w-full max-w-lg max-h-[85vh] overflow-y-auto shadow-2xl flex flex-col items-center text-center gap-4 text-white">

                <span className="text-4xl">📜</span>

                <div>
                    <h3 className="text-xl font-bold text-yellow-300">Regras do Truco Gaúcho</h3>
                    <p className="text-xs text-green-300 mt-1">
                        Um resumo rápido para você dominar a partida!
                    </p>
                </div>

                {/* Caixa com o resumo das regras */}
                <div className="text-left text-sm text-green-100 space-y-3 w-full bg-green-900/40 p-4 rounded-xl border border-green-800">
                    <div>
                        <strong className="text-yellow-300">🃏 Dinâmica da Mão:</strong>
                        <p className="text-xs mt-0.5 text-green-200">Cada mão é disputada em melhor de 3 rodadas. Quem vencer 2 rodadas ganha a mão e leva os tentos em jogo.</p>
                    </div>

                    <div>
                        <strong className="text-yellow-300">⚔️ Manilhas Fixas (As Mais Fortes):</strong>
                        <p className="text-xs mt-0.5 text-green-200">
                            1º ♠ Espadão (Ás de Espadas)<br />
                            2º ♣ Bastião (7 de Bastos)<br />
                            3º ♦ Sete de Ouros<br />
                            4º ♥ Sete de Copas
                        </p>
                    </div>

                    <div>
                        <strong className="text-yellow-300">📊 Envido:</strong>
                        <p className="text-xs mt-0.5 text-green-200">Disputa de pontos somando duas cartas do mesmo naipe + 20. Figuras (10, 11, 12) valem 0.</p>
                    </div>

                    <div>
                        <strong className="text-yellow-300">🌸 Flor:</strong>
                        <p className="text-xs mt-0.5 text-green-200">Ocorre quando você tem 3 cartas do mesmo naipe na mão. Vale 3 pontos automáticos.</p>
                    </div>

                    <div>
                        <strong className="text-yellow-300">📢 Truco e Vitória:</strong>
                        <p className="text-xs mt-0.5 text-green-200">O Truco vale 3 tentos (podendo subir para Retruco, Vale 9 e Vale Jogo). Vence a partida quem atingir primeiro 24 pontos.</p>
                    </div>
                </div>

                {/* Botão de Fechar */}
                <div className="flex w-full mt-2">
                    <button
                        onClick={() => janela_regras(false)}
                        className="w-full bg-green-800 hover:bg-green-700 text-green-100 font-semibold py-2 px-4 rounded-xl transition cursor-pointer shadow-md"
                    >
                        Fechar
                    </button>
                </div>
            </div>
        </div>
    );
}