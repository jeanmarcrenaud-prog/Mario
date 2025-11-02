# src/core/recognizer_base.py
from abc import ABC, abstractmethod

class SpeechRecognizerBase(ABC):
    @abstractmethod
    def transcribe(self, audio_path: str) -> str:
        pass
