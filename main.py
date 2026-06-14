"""Main entry point for the Desktop Assistant V1."""

import asyncio
import json
import os
import re
import sys
import time as time_module
from pathlib import Path

import pygame

# Colors for terminal output
COLOR_GREEN = "\033[92m"  # AI messages
COLOR_BLUE = "\033[94m"   # User messages
COLOR_YELLOW = "\033[93m" # Warnings
COLOR_RED = "\033[91m"    # Errors
COLOR_RESET = "\033[0m"


def print_header():
    """Print ASCII art header."""
    header = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                 ASSISTENTE DESKTOP V1                        ║
║              Texto → LLM → Emoção → TTS                      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(COLOR_GREEN + header + COLOR_RESET)


def load_config(path: str) -> dict:
    """Load a JSON config file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"{COLOR_RED}[ERRO] Falha ao carregar {path}: {e}{COLOR_RESET}")
        return {}


def remove_emojis(text: str) -> str:
    """Remove emojis do texto para evitar leitura bizarra no TTS."""
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001f926-\U0001f937"
        "\U00010000-\U0010ffff"
        "\u2640-\u2642"
        "\u2600-\u2B55"
        "\u200d"
        "\u23cf"
        "\u23e9"
        "\u231a"
        "\ufe0f"
        "\u3030"
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub("", text).strip()


def play_audio(audio_path: str, cleanup: bool = True):
    """Reproduz áudio via pygame e aguarda terminar."""
    try:
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time_module.sleep(0.05)
    except Exception as e:
        print(f"{COLOR_YELLOW}[ERRO] Falha ao reproduzir áudio: {e}{COLOR_RESET}")
    finally:
        pygame.mixer.music.unload()
        if cleanup:
            try:
                os.remove(audio_path)
            except:
                pass


async def main():
    """Main REPL loop."""
    print_header()

    # Setup paths
    base_dir = Path(__file__).parent
    os.chdir(base_dir)

    config = load_config("config/settings.json")
    brain = load_config("config/brain.json")

    # Check API key
    api_key = config.get("llm", {}).get("openrouter_api_key", "")
    if not api_key or api_key == "COLOQUE_SUA_API_KEY_AQUI":
        print(f"{COLOR_YELLOW}[AVISO] API key da OpenRouter não configurada!{COLOR_RESET}")
        print(f"{COLOR_YELLOW}        Edite config/settings.json e adicione sua chave.{COLOR_RESET}\n")

    # Initialize modules
    try:
        from core import TTSEngine, ChatManager, EmotionParser, AppLauncher

        print("[INFO] Inicializando módulos...")
        tts = TTSEngine("config/settings.json", "config/emotion_profiles.json")
        chat = ChatManager("config/settings.json", "config/brain.json", "config/slang_dictionary.json")
        parser = EmotionParser()
        launcher = AppLauncher("config/apps.json")
        print(f"{COLOR_GREEN}[INFO] Tudo pronto! Vamos conversar?{COLOR_RESET}\n")

        # Inicializa pygame mixer
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        print("[INFO] Sistema de áudio inicializado")
    except Exception as e:
        print(f"{COLOR_RED}[ERRO] Falha ao inicializar: {e}{COLOR_RESET}")
        raise

    # Welcome message (Bug 5: remove "tcheco")
    welcome_text = "[Feliz] Oi! Tô online, bora conversar!"
    print(f"{COLOR_GREEN}{welcome_text}{COLOR_RESET}")

    try:
        emotion, clean_welcome = parser.parse(welcome_text)
        clean_welcome = remove_emojis(clean_welcome)
        welcome_path = await tts.generate_audio(clean_welcome, emotion)
        play_audio(welcome_path)
    except Exception as e:
        print(f"{COLOR_YELLOW}[AVISO] Não consegui gerar áudio de boas-vindas: {e}{COLOR_RESET}")

    print(f"\n{COLOR_YELLOW}Comandos: /apps, /abrir <app>, /emocoes, /testarvoz, /limpar, /ajuda, /sair{COLOR_RESET}\n")

    # Main loop (Bug 8: commands with / prefix)
    while True:
        try:
            # Get user input
            user_input = input(f"{COLOR_BLUE}Você: {COLOR_RESET}").strip()

            if not user_input:
                continue

            # Check for exit commands (text or /sair)
            if user_input.lower() in ("sair", "exit", "quit", "tchau", "bye") or user_input.lower() == "/sair":
                goodbye = "[Triste] Tchau! Até mais!"
                print(f"{COLOR_GREEN}{goodbye}{COLOR_RESET}")
                try:
                    emotion, clean_goodbye = parser.parse(goodbye)
                    clean_goodbye = remove_emojis(clean_goodbye)
                    path = await tts.generate_audio(clean_goodbye, emotion)
                    play_audio(path)
                except:
                    pass
                pygame.mixer.quit()
                break

            # Commands with / prefix
            if user_input.startswith("/"):
                cmd_parts = user_input[1:].split(maxsplit=1)
                cmd = cmd_parts[0].lower() if cmd_parts else ""
                args = cmd_parts[1] if len(cmd_parts) > 1 else ""

                if cmd == "apps":
                    apps = launcher.list_apps()
                    msg = f"[Neutra] Apps disponíveis: {', '.join(apps)}"
                    print(f"{COLOR_GREEN}{msg}{COLOR_RESET}")
                    try:
                        emotion, clean_msg = parser.parse(msg)
                        clean_msg = remove_emojis(clean_msg)
                        path = await tts.generate_audio(clean_msg, emotion)
                        play_audio(path)
                    except:
                        pass
                    continue

                elif cmd == "abrir":
                    if not args:
                        print(f"{COLOR_YELLOW}Uso: /abrir <nome do app>{COLOR_RESET}")
                        continue
                    success, message = launcher.launch(args)
                    print(f"{COLOR_GREEN}{message}{COLOR_RESET}")
                    try:
                        emotion, text = parser.parse(message)
                        text = remove_emojis(text)
                        path = await tts.generate_audio(text, emotion)
                        play_audio(path)
                    except:
                        pass
                    continue

                elif cmd in ("emocoes", "emoções", "emotions"):
                    from core.emotion_parser import EMOTION_ALIASES
                    emocoes = list(EMOTION_ALIASES.keys())
                    msg = f"[Curiosa] Emoções que eu sei: {', '.join(emocoes)}"
                    print(f"{COLOR_GREEN}{msg}{COLOR_RESET}")
                    try:
                        emotion, clean_msg = parser.parse(msg)
                        clean_msg = remove_emojis(clean_msg)
                        path = await tts.generate_audio(clean_msg, emotion)
                        play_audio(path)
                    except:
                        pass
                    continue

                elif cmd == "testarvoz":
                    print(f"{COLOR_YELLOW}[INFO] Gerando áudios de teste...{COLOR_RESET}")
                    try:
                        test_files = await tts.test_all_emotions()
                        for f in test_files:
                            print(f"  Tocando {os.path.basename(f)}...")
                            play_audio(f, cleanup=False)
                            time_module.sleep(0.3)
                    except Exception as e:
                        print(f"{COLOR_RED}[ERRO] {e}{COLOR_RESET}")
                    continue

                elif cmd == "ajuda":
                    print("""
Comandos disponíveis:
  /apps        - Lista apps disponíveis
  /abrir <app> - Abre um aplicativo
  /emocoes     - Lista emoções disponíveis
  /testarvoz   - Testa todas as emoções
  /limpar      - Limpa histórico
  /ajuda       - Mostra esta mensagem
  /sair        - Encerra o programa
""")
                    continue

                elif cmd == "limpar":
                    chat.history = []
                    chat.image_summaries = []
                    print(f"{COLOR_GREEN}[Neutra] Histórico limpo!{COLOR_RESET}")
                    continue

                else:
                    print(f"{COLOR_YELLOW}Comando desconhecido: {cmd}. Digite /ajuda para ver os comandos.{COLOR_RESET}")
                    continue

            # Normal chat flow
            try:
                # Get response from LLM
                raw_response = await chat.chat(user_input)  # Bug 4: raw response

                # Parse emotion
                emotion, clean_text = parser.parse(raw_response)  # Separate tag from text

                # Remove emojis
                clean_text = remove_emojis(clean_text)  # Bug 6: remove emojis

                # Update brain
                chat.update_brain(emotion, 0.7)

                # Display response (Bug 6: use clean_text)
                print(f"{COLOR_GREEN}IA: [{emotion}] {clean_text}{COLOR_RESET}")

                # Generate and play audio (Bug 4: send clean_text to TTS)
                try:
                    audio_path = await tts.generate_audio(clean_text, emotion)
                    play_audio(audio_path)
                except Exception as e:
                    print(f"{COLOR_YELLOW}[AVISO] Erro no TTS: {e}{COLOR_RESET}")

            except Exception as e:
                print(f"{COLOR_RED}[ERRO] Erro na conversa: {e}{COLOR_RESET}")

        except KeyboardInterrupt:
            print(f"\n{COLOR_GREEN}[Neutra] Interrompido. Até logo!{COLOR_RESET}")
            break
        except Exception as e:
            print(f"{COLOR_RED}[ERRO] Erro inesperado: {e}{COLOR_RESET}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"{COLOR_RED}[ERRO FATAL] {e}{COLOR_RESET}")
        sys.exit(1)
