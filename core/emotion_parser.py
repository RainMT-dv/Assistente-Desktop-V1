"""Emotion parser module for extracting emotion tags from LLM responses."""

import re
from typing import Tuple

# Emotion aliases mapping to canonical names
EMOTION_ALIASES = {
    "Feliz": ["feliz", "alegre", "contente", "animada", "animado", "excitada", "cheerful", "happy"],
    "Surpresa": ["surpresa", "surpreso", "espantada", "chocada", "surprise", "shocked"],
    "Triste": ["triste", "tristeza", "desanimada", "chateada", "sad"],
    "Raiva": ["raiva", "brava", "bravo", "irritada", "furiosa", "angry", "braba"],
    "Curiosa": ["curiosa", "curioso", "pensativa", "curious"],
    "Séria": ["séria", "sério", "focada", "serious", "determinada"],
    "Assustada": ["assustada", "assustado", "medo", "pânico", "fearful", "scared"],
    "Sussurro": ["sussurro", "sussurrando", "baixinho", "segredo", "whisper"],
    "Neutra": ["neutra", "neutro", "normal", "neutral"],
}

# Build reverse mapping: alias -> canonical
_ALIAS_TO_CANONICAL = {}
for canonical, aliases in EMOTION_ALIASES.items():
    _ALIAS_TO_CANONICAL[canonical.lower()] = canonical
    for alias in aliases:
        _ALIAS_TO_CANONICAL[alias.lower()] = canonical

# Regex to match emotion tag at the START of string: [Emotion]
_EMOTION_TAG_REGEX = re.compile(r'^\[([^\]]+)\]\s*')


class EmotionParser:
    """Parser for extracting emotion tags from text responses."""

    def __init__(self):
        """Initialize the emotion parser."""
        self.valid_emotions = set(EMOTION_ALIASES.keys())

    def parse(self, text: str) -> Tuple[str, str]:
        """
        Parse emotion tag from the beginning of text.

        Args:
            text: Text that may start with [Emotion] tag

        Returns:
            Tuple of (emotion_name, clean_text)
        """
        return parse_emotion_tag(text)

    def validate(self, emotion: str) -> str:
        """
        Validate and normalize an emotion name.

        Args:
            emotion: Raw emotion string

        Returns:
            Canonical emotion name or "Neutra" if unknown
        """
        return validate_emotion(emotion)


def parse_emotion_tag(text: str) -> Tuple[str, str]:
    """
    Extract emotion tag from the beginning of text.

    Args:
        text: Text that may start with [Emotion] tag

    Returns:
        Tuple of (emotion_name, clean_text_without_tag)
    """
    if not text:
        return ("Neutra", "")

    match = _EMOTION_TAG_REGEX.match(text)
    if not match:
        return ("Neutra", text)

    raw_emotion = match.group(1).strip()
    clean_text = text[match.end():].strip()

    emotion = validate_emotion(raw_emotion)
    return (emotion, clean_text)


def validate_emotion(emotion: str) -> str:
    """
    Validate and normalize an emotion name to its canonical form.

    Args:
        emotion: Raw emotion string (e.g., "feliz", "Feliz", "happy")

    Returns:
        Canonical emotion name (e.g., "Feliz") or "Neutra" if unknown
    """
    if not emotion:
        return "Neutra"

    normalized = emotion.strip().lower()
    canonical = _ALIAS_TO_CANONICAL.get(normalized)

    if canonical:
        return canonical

    # Check for case-insensitive exact match with canonical names
    for valid in EMOTION_ALIASES.keys():
        if normalized == valid.lower():
            return valid

    return "Neutra"


if __name__ == "__main__":
    # Simple tests
    test_cases = [
        "[Feliz] E aí tcheco! Bora jogar!",
        "[feliz] Texto com lowercase",
        "[animada] Usando alias",
        "[Raiva] QUE ISSO!",
        "[Desconhecida] Tag invalida",
        "Sem tag nenhuma",
        "",
        "[Sussurro]",
    ]

    print("[INFO] Testando EmotionParser:")
    for test in test_cases:
        emotion, text = parse_emotion_tag(test)
        print(f"  Entrada: {repr(test)}")
        print(f"  Saída: emotion={emotion}, text={repr(text)}\n")
