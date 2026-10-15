"use client";
import { Dispatch, SetStateAction } from "react";

interface Fechar {
    janela: Dispatch<SetStateAction<boolean>>;

}

export default function TelaReiniciar({ janela }: Fechar) {

    const handleReiniciar = () => {
        window.location.reload();
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-fade-in">

            <div className="bg-green-950 border border-green-700/60 rounded-2xl p-6 w-80 shadow-2xl flex flex-col items-center text-center gap-4 text-white">


                <span className="text-4xl">🔄</span>


                <div>
                    <h3 className="text-lg font-bold">Reiniciar Partida</h3>
                    <p className="text-sm text-green-300 mt-1">
                        Tem certeza que deseja reiniciar o jogo? Todo o progresso atual será perdido.
                    </p>
                </div>


                <div className="flex gap-3 w-full mt-2">
                    <button
                        onClick={() => janela(false)}
                        className="flex-1 bg-green-800 hover:bg-green-700 text-green-100 font-semibold py-2 px-4 rounded-xl transition cursor-pointer"
                    >
                        Cancelar
                    </button>

                    <button
                        onClick={handleReiniciar}
                        className="flex-1 bg-red-600 hover:bg-red-500 text-white font-semibold py-2 px-4 rounded-xl transition cursor-pointer shadow-md"
                    >
                        Reiniciar
                    </button>
                </div>
            </div>
        </div>
    );
}