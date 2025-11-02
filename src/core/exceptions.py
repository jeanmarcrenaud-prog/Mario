class SpeechRecognitionError(Exception):
    """Erreur lors de la reconnaissance vocale."""

class TextToSpeechError(Exception):
    """Erreur lors de la synthèse vocale."""

class HardwareError(Exception):
    """Erreur liée au matériel (micro, carte son, etc.)."""
