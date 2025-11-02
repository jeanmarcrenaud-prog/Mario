# tests/fake_recognizer.py
from core.recognizer_base import SpeechRecognizerBase

class FakeRecognizer(SpeechRecognizerBase):
    def transcribe(self, audio_path: str) -> str:
        return "[FAKE] texte transcrit"
