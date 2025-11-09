# src/controller/tts_controller.py
from src.model.text_to_speech import TextToSpeech
from src.utils.logger import logger

class TTSBotController:
    def __init__(self, tts: TextToSpeech):
        self.tts = tts

    def say(self, text, voice=None):
        """Utilise TextToSpeech pour synthétiser un texte."""
        try:
            audio_path = self.tts.synthesize(text, voice)
            return audio_path
        except Exception as e:
            logger.error(f"Erreur dans TTSBotController : {e}")
            return None
