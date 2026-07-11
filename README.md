<div align="center">

  # Assistente Desktop V1
  *Assistente de IA via terminal com voz e abertura de aplicativos*

  [![Python](https://img.shields.io/badge/Python-3.10+-3776ab?style=flat-square)](https://python.org)
  [![OpenRouter](https://img.shields.io/badge/LLM-OpenRouter-7c3aed?style=flat-square)](https://openrouter.ai)
  [![Edge TTS](https://img.shields.io/badge/TTS-edge--tts-blue?style=flat-square)](https://github.com/rany2/edge-tts)
  [![Licença](https://img.shields.io/badge/licença-MIT-blue?style=flat-square)](LICENSE)

  [Funcionalidades](#funcionalidades) • [Primeiros passos](#primeiros-passos) • [Comandos](#comandos)

</div>

---

> [!NOTE]
> Esta é a V1 — simples e funcional. Para a versão com dashboard web, voz ativa e memória persistente, veja a [V2](https://github.com/RainMT-dv/Assistente-Desktop-V2).

Assistente de texto e voz via terminal. Conversa com uma LLM via OpenRouter, detecta emoções na resposta e sintetiza a fala com Edge TTS — tudo sem custo de API de voz.

## Funcionalidades

- **Chat via terminal** com histórico de conversa
- **Sistema de emoções** — a IA responde com tags `[Feliz]`, `[Triste]`, `[Raiva]`...
- **Síntese de voz** com `edge-tts` (gratuito, sem API extra)
- **Abertura de apps por comando** — `/abrir chrome`, `/abrir discord`...
- Personalidade informal em Português Brasileiro

## Primeiros passos

### Requisitos

- Python 3.10+ — marque "Add to PATH" na instalação
- API Key do OpenRouter (gratuita) — [openrouter.ai](https://openrouter.ai)
- Conexão com internet

### Instalação

**1. Clone o repositório**

```bash
git clone https://github.com/RainMT-dv/Assistente-Desktop-V1.git
cd Assistente-Desktop-V1
```

**2. Instale as dependências**

Dê dois cliques em `SETUP.bat` — ele cria o ambiente virtual e instala tudo automaticamente.

**3. Configure sua API Key**

Edite `config/settings.json` e substitua o placeholder pela sua chave do OpenRouter:

```json
"openrouter_api_key": "sk-or-v1-..."
```

**4. Configure os apps (opcional)**

Edite `config/apps.json` com os caminhos dos executáveis na sua máquina:

```json
{
  "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
  "discord": "C:\\Users\\SEU_USUARIO\\AppData\\Local\\Discord\\Update.exe --processStart Discord.exe"
}
```

## Como executar

Dê dois cliques em `RUN.bat` ou rode no terminal:

```bash
venv\Scripts\activate
python main.py
```

## Comandos

| Comando | Descrição |
|---|---|
| `/abrir <app>` | Abre um aplicativo configurado |
| `/apps` | Lista os apps disponíveis |
| `/emocoes` | Lista as emoções disponíveis |
| `/testarvoz` | Testa todas as emoções em áudio |
| `/limpar` | Limpa o histórico de conversa |
| `/ajuda` | Mostra a lista de comandos |
| `/sair` | Encerra o programa |

## Estrutura

```
├── config/
│   ├── settings.json          # Configurações (API key, modelo, TTS)
│   ├── apps.json              # Caminhos dos apps
│   ├── brain.json             # Estado emocional da IA
│   ├── emotion_profiles.json  # Perfis de voz por emoção
│   └── slang_dictionary.json  # Gírias e expressões
├── core/
│   ├── chat_manager.py        # Comunicação com a LLM
│   ├── tts_engine.py          # Síntese de voz
│   ├── emotion_parser.py      # Parser de tags de emoção
│   └── app_launcher.py        # Abertura de aplicativos
├── main.py
├── SETUP.bat
└── RUN.bat
```

## Contribuindo

Sinta-se à vontade para modificar e melhorar! Crie um fork e publique as suas mudanças.
