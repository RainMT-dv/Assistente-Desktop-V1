"""Text-to-Speech engine using Edge-TTS with emotional profiles."""

import asyncio
import json
import os
from pathlib import Path
from typing import Dict, List, Optional

import edge_tts


class TTSEngine:
    """TTS engine with emotional profile support using Edge-TTS."""

    def __init__(self, config_path: str = "config/settings.json", emotion_profiles_path: str = "config/emotion_profiles.json"):
        """
        Initialize the TTS engine.

        Args:
            config_path: Path to settings.json
            emotion_profiles_path: Path to emotion_profiles.json
        """
        self.config_path = config_path
        self.emotion_profiles_path = emotion_profiles_path
        self.config = {}
        self.emotion_profiles = {}
        self.voice = "pt-BR-FranciscaNeural"
        self.engine = "edge-tts"
        self.output_dir = "audio_output"
        self._file_counter = 0

        self._load_configs()
        self._ensure_output_dir()

    def _load_configs(self) -> None:
        """Load configuration files."""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)

            with open(self.emotion_profiles_path, "r", encoding="utf-8") as f:
                self.emotion_profiles = json.load(f)

            self.voice = self.config.get("tts", {}).get("voice", "pt-BR-FranciscaNeural")
            self.engine = self.config.get("tts", {}).get("engine", "edge-tts")
            self.output_dir = self.config.get("paths", {}).get("audio_output_dir", "audio_output")

            print(f"[INFO] TTS Engine carregado: voice={self.voice}, engine={self.engine}")
        except FileNotFoundError as e:
            print(f"[ERRO] Arquivo de configuração não encontrado: {e}")
            raise
        except json.JSONDecodeError as e:
            print(f"[ERRO] JSON inválido: {e}")
            raise

    def _ensure_output_dir(self) -> None:
        """Create audio output directory if it doesn't exist."""
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        print(f"[INFO] Diretório de áudio: {os.path.abspath(self.output_dir)}")

    def _generate_filename(self, emotion: str) -> str:
        """Generate unique filename for audio output."""
        self._file_counter += 1
        return f"tts_{self._file_counter:04d}_{emotion}.mp3"

    def _get_edge_tts_config(self, emotion: str) -> Dict:
        """Get edge_tts config for an emotion (rate, pitch, volume)."""
        profile = self.emotion_profiles.get(emotion, self.emotion_profiles.get("Neutra", {}))
        return profile.get("edge_tts", {"rate": "+0%", "pitch": "+0Hz", "volume": "+0%"})

    async def generate_audio(self, text: str, emotion: str = "Neutra", output_path: Optional[str] = None) -> str:
        """
        Generate audio file from text with emotional profile.

        Args:
            text: Text to synthesize
            emotion: Emotion name (must exist in emotion_profiles.json)
            output_path: Custom output path (auto-generated if None)

        Returns:
            Path to generated audio file
        """
        if self.engine == "azure":
            raise NotImplementedError("Azure TTS ainda não implementado. Use 'edge-tts'.")

        # Get edge_tts config for this emotion
        edge_config = self._get_edge_tts_config(emotion)

        # Generate output path if not provided
        if output_path is None:
            filename = self._generate_filename(emotion)
            output_path = os.path.join(self.output_dir, filename)

        try:
            communicate = edge_tts.Communicate(
                text=text,
                voice=self.voice,
                rate=edge_config.get("rate", "+0%"),
                pitch=edge_config.get("pitch", "+0Hz"),
                volume=edge_config.get("volume", "+0%"),
            )
            await communicate.save(output_path)
            print(f"[INFO] Áudio gerado: {output_path}")
            return output_path
        except Exception as e:
            print(f"[ERRO] Falha ao gerar áudio: {e}")
            raise

    async def list_voices(self, language: str = "pt-BR") -> List[Dict]:
        """
        List available voices for a language.

        Args:
            language: Language code (e.g., "pt-BR", "en-US")

        Returns:
            List of voice dictionaries with name, gender, etc.
        """
        try:
            voices = await edge_tts.list_voices()
            filtered = [v for v in voices if language.lower() in v.get("Locale", "").lower()]
            return filtered
        except Exception as e:
            print(f"[ERRO] Falha ao listar vozes: {e}")
            return []

    async def test_all_emotions(self, output_dir: Optional[str] = None) -> List[str]:
        """
        Generate test audio for each emotion profile.

        Args:
            output_dir: Directory for test files (uses default if None)

        Returns:
            List of generated file paths
        """
        test_text = "Olá! Este é um teste de emoção na minha voz."
        output_dir = output_dir or self.output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        generated = []
        for emotion in self.emotion_profiles.keys():
            filename = f"test_{emotion}.mp3"
            output_path = os.path.join(output_dir, filename)
            try:
                await self.generate_audio(test_text, emotion, output_path)
                generated.append(output_path)
            except Exception as e:
                print(f"[AVISO] Falha ao gerar teste para {emotion}: {e}")

        print(f"[INFO] {len(generated)} arquivos de teste gerados em {output_dir}")
        return generated


if __name__ == "__main__":
    async def main():
        engine = TTSEngine()
        print("\n[INFO] Testando TTS Engine...")

        # Test single generation
        path = await engine.generate_audio("Olá! Tudo bem por aí?", "Feliz")
        print(f"[INFO] Gerado: {path}")

        # List voices
        print("\n[INFO] Vozes pt-BR disponíveis:")
        voices = await engine.list_voices("pt-BR")
        for v in voices[:5]:
            print(f"  - {v.get('ShortName')}: {v.get('Gender')}")

    asyncio.run(main())
