# src/core/exceptions/__init__.py
from src.core.exceptions.exceptions import (
    MarioException,
    SpeechRecognitionError,
    TextToSpeechError,
    HardwareError,
    WakeWordError,
    AudioBufferError,
    LLMConnectionError,
    ConversationNotFoundError,
    IntentNotFoundError,
)

__all__ = [
    "MarioException",
    "SpeechRecognitionError",
    "TextToSpeechError",
    "HardwareError",
    "WakeWordError",
    "AudioBufferError",
    "LLMConnectionError",
    "ConversationNotFoundError",
    "IntentNotFoundError",
]
