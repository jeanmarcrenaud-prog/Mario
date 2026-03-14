# ─────────────────────────────────────────────────────────────────────
# exceptions.py
# Exceptions custom pour Mario Assistant Vocal
# ─────────────────────────────────────────────────────────────────────

class MarioException(Exception):
    """Exception base pour Mario"""
    pass


class SpeechRecognitionError(MarioException):
    """Erreur de reconnaissance vocale"""
    pass


class TextToSpeechError(MarioException):
    """Erreur de synthèse vocale"""
    pass


class HardwareError(MarioException):
    """Erreur matérielle (micro, haut-parleur, etc.)"""
    pass


class WakeWordError(MarioException):
    """Erreur de détection mot-clé"""
    pass


class AudioBufferError(MarioException):
    """Erreur de buffer audio (taux, format)"""
    pass


class LLMConnectionError(MarioException):
    """Erreur de connexion LLM"""
    pass


class ConversationNotFoundError(MarioException):
    """Conversation non trouvée"""
    pass


class IntentNotFoundError(MarioException):
    """Intent non reconnu"""
    pass


# ─────────────────────────────────────────────────────────────────────
# Fin
# ─────────────────────────────────────────────────────────────────────
