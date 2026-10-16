# 🃏 Truco Gaúcho / Espanhol — Web Edition

Um jogo completo de **Truco Gaúcho (Espanhol)** jogado contra um **Bot (IA em Python)** em tempo real via **WebSockets**, desenvolvido com uma arquitetura moderna e escalável utilizando **FastAPI** no backend e **Next.js** no frontend.

---

## 🛠️ Tecnologias Utilizadas

### **Frontend**
- **Next.js 14/15** (App Router, React, TypeScript)
- **Tailwind CSS** (Estilização e layout responsivo)
- **Framer Motion** (Animações de cartas e interações de mesa)
- **Lucide React** (Ícones da interface)

### **Backend**
- **Python 3.11+**
- **FastAPI** (WebSockets em tempo real e API RESTful)
- **Pydantic** (Validação de tipos e esquemas de dados)
- **Pytest** (Suíte de testes unitários para a engine de regras)
- **SQLAlchemy / SQLModel** + **PostgreSQL** (Persistência de estatísticas)

### **DevOps & Deploy**
- **Docker & Docker Compose** (Containerização do ambiente)
- **Vercel** (Hospedagem do Frontend Next.js)
- **Render / Fly.io / Railway** (Hospedagem do Backend FastAPI)

---

## 🎲 Regras do Jogo & Funcionalidades

O jogo segue as regras tradicionais do **Truco Gaúcho/Espanhol**:

- **Baralho Espanhol (40 cartas):** Sem 8s, 9s ou Coringas.
- **Manilhas Fixas (Ordem de Força):**
  1. 🗡️ **1 de Espadas** (*Espadão*)
  2. 🏑 **1 de Bastos** (*Bastião*)
  3. 🗡️ **7 de Espadas**
  4. 🏆 **7 de Ouros** (*Sete Belo*)
  5. 🍷/🏆 **1s de Copas e Ouros** (*Guembés*)
- **Gritos e Cantos Implementados:**
  - **Truco, Retruco e Vale 4**
  - **Envido, Real Envido e Falta Envido** (Com cálculo automático de pontuação de cartas do mesmo naipe + 20)
  - **Flor, Contra-Flor e Contra-Flor e o Resto**

---

## 🤖 Inteligência do Bot (IA)

O Bot do jogo é construído em Python puro e integrado diretamente ao fluxo da partida:

- **Análise de Mão:** Avalia a força das cartas para tomar decisões de ataque ou defesa.
- **Cálculo de Envido:** Toma decisões estatísticas para pedir ou aceitar Envido com base em sua pontuação atual e blefes aleatórios.
- **Respostas de Flor:** Canta e responde automaticamente a combinações de 3 cartas do mesmo naipe.
- **Simulação de Humano:** Delay de resposta configurável via WebSocket para simular o tempo de pensamento.

---

## 📐 Arquitetura do Sistema

```text
┌─────────────────────────────────────────────────────────┐
│                    Next.js (Frontend)                   │
│  - Tabuleiro interativo    │
│  - Gerenciamento de estado de voz, placar e turnos      │
└───────────────────────────┬─────────────────────────────┘
                            │
                            │ WebSockets (Eventos JSON)
                            ▼
┌─────────────────────────────────────────────────────────┐
│                    FastAPI (Backend)                    │
│  ├── Engine de Regras (Pure Python & Máquina de Estado) │
│  ├── Módulo do Bot (Tomada de Decisão & Heurística)     │
│  └── Connection Manager (Comunicação em Tempo Real)     │
└───────────────────────────┬─────────────────────────────┘
           
