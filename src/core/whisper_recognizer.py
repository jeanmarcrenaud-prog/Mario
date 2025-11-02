# src/core/whisper_recognizer.py
from .recognizer_base import SpeechRecognizerBase

class WhisperRecognizer(SpeechRecognizerBase):
    def __init__(self, model="small"):
        # initialiser votre modèle Whisper ici
        self.model = model

    def transcribe(self, audio_path: str) -> str:
        # Appeler Whisper
        return "texte transcrit"
