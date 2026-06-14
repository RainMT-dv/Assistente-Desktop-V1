# 🤖 Assistente Pessoal Desktop — V1

A versão inicial do assistente de texto + voz via terminal. Conversa com uma LLM (OpenRouter), detecta emoções na resposta e sintetiza a fala via Edge-TTS.

> **Nota:** Esta é a V1 — versão texto puro via terminal. Para a versão completa com dashboard web, voz ativa, memória persistente e muito mais, veja a [V2](https://github.com/RainMT-dv/Assistente-Pessoal-Desktop-Proativo-e-Multimodal).

---

## ✨ Funcionalidades

- 💬 **Chat via terminal** com histórico de conversa
- 🎭 **Sistema de emoções** — a IA responde com tags `[Feliz]`, `[Triste]`, `[Raiva]`...
- 🔊 **Síntese de voz** com `edge-tts` (gratuito, sem API extra)
- 🚀 **Abertura de apps por comando** — `/abrir chrome`, `/abrir discord`...
- 🎤 Personalidade informal em Português Brasileiro

---

## 🛠️ Pré-requisitos

- **Python 3.10+** — [python.org](https://python.org) (marque "Add to PATH" na instalação)
- **API Key do OpenRouter** (gratuita) — [openrouter.ai](https://openrouter.ai)
- Conexão com internet

---

## 📦 Instalação

### 1. Clone o repositório
```bash
git clone https://github.com/RainMT-dv/Assistente-Pessoal-Desktop-Proativo-e-Multimodal.git
cd Assistente-Pessoal-Desktop-Proativo-e-Multimodal
```

### 2. Instale as dependências
Dê dois cliques em **`SETUP.bat`** — ele cria o ambiente virtual e instala tudo automaticamente.

### 3. Configure sua API Key
Edite `config/settings.json` e substitua `COLOQUE_SUA_API_KEY_AQUI` pela sua chave do OpenRouter:
```json
"openrouter_api_key": "sk-or-v1-..."
```

---

## 🏃 Como executar

Dê dois cliques em **`RUN.bat`** ou rode no terminal:
```bash
venv\Scripts\activate
python main.py
```

---

## 💬 Comandos disponíveis

| Comando | Descrição |
|---|---|
| `/apps` | Lista os apps configurados |
| `/abrir <app>` | Abre um aplicativo |
| `/emocoes` | Lista as emoções disponíveis |
| `/testarvoz` | Testa todas as emoções em áudio |
| `/limpar` | Limpa o histórico de conversa |
| `/ajuda` | Mostra a lista de comandos |
| `/sair` | Encerra o programa |

---

## 📂 Estrutura

```
├── config/
│   ├── settings.json          # Configurações (API key, modelo, TTS)
│   ├── apps.json              # Caminhos dos apps para abrir por voz
│   ├── brain.json             # Estado emocional atual da IA
│   ├── emotion_profiles.json  # Perfis de voz por emoção
│   └── slang_dictionary.json  # Gírias e expressões
├── core/
│   ├── chat_manager.py        # Comunicação com a LLM (OpenRouter)
│   ├── tts_engine.py          # Síntese de voz (edge-tts)
│   ├── emotion_parser.py      # Parser de tags de emoção
│   └── app_launcher.py        # Abertura de aplicativos
├── main.py                    # Ponto de entrada
├── SETUP.bat                  # Instalação automatizada
└── RUN.bat                    # Execução automatizada
```

---

## 🔑 Configurando Apps

Edite `config/apps.json` com os caminhos dos executáveis na **sua** máquina:

```json
{
    "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "discord": "C:\\Users\\SEU_USUARIO\\AppData\\Local\\Discord\\Update.exe --processStart Discord.exe"
}
```

---

## 📄 Licença

MIT — use, modifique e distribua livremente.
