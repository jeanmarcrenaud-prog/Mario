# src/services/simulated_speech_recognition.py
from typing import Any, List

class SimpleSimulationSpeechAdapter:
    """Adapter minimal pour les tests de reconnaissance vocale."""
    def transcribe_array(self, audio_data: Any, language: str = "fr") -> str:
        return ""
    def transcribe_file(self, file_path: str, language: str = "fr") -> str:
        return ""
    def unload_model(self) -> None:
        pass
    def get_available_models(self) -> List[str]:
        return []

# Provide a factory for SpeechRecognitionService
