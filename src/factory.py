# src/factory.py
from src.adapters.speech_recognition_whisper_adapter import WhisperSpeechRecognitionAdapter

class RecognizerFactory:
    @staticmethod
    def create(config):
        if config["type"] == "whisper":
            return WhisperSpeechRecognitionAdapter(model=config.get("model", "small"))
        elif config["type"] == "simulation":
            from src.adapters.speech_recognition_simulated_adapter import SimulatedSpeechRecognitionAdapter
            return SimulatedSpeechRecognitionAdapter()
        raise ValueError(f"Recognizer inconnu: {config['type']}")
