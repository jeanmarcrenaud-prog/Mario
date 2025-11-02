# src/factory.py
from src.core.whisper_recognizer import WhisperRecognizer
# Possible d'importer d'autres implémentations futures

class RecognizerFactory:
    @staticmethod
    def create(config):
        if config["type"] == "whisper":
            return WhisperRecognizer(model=config.get("model", "small"))
        # Ajouter d'autres backends ici
        raise ValueError("Recognizer inconnu")
