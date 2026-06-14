"""Core modules for the desktop assistant."""

from .emotion_parser import EmotionParser, parse_emotion_tag, validate_emotion
from .tts_engine import TTSEngine
from .chat_manager import ChatManager
from .app_launcher import AppLauncher

__all__ = [
    "EmotionParser",
    "parse_emotion_tag",
    "validate_emotion",
    "TTSEngine",
    "ChatManager",
    "AppLauncher",
]
