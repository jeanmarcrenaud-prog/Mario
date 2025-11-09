import numpy as np
import pyaudio
from typing import Optional
from ..core.text_to_speech import TextToSpeech  # Votre classe existante
from ..utils.logger import logger

class AudioOutputAdapter:
    def __init__(self):
        self.tts_engine = TextToSpeech()
        self.current_voice = None
    
    def load_voice(self, voice_name: str) -> bool:
        """Charge une voix."""
        try:
            success = self.tts_engine.load_voice(voice_name)
            if success:
                self.current_voice = voice_name
            return success
        except Exception as e:
            logger.error(f"Erreur chargement voix {voice_name}: {e}")
            return False
    
    def say(self, text: str, speed: float = 1.0) -> bool:
        """Synthétise et lit le texte."""
        try:
            return self.tts_engine.say(text, speed)
        except Exception as e:
            logger.error(f"Erreur synthèse vocale: {e}")
            return False
    
    def synthesize(self, text: str, speed: float = 1.0) -> Optional[np.ndarray]:
        """Synthétise le texte en audio (sans jouer)."""
        try:
            return self.tts_engine.synthesize(text, speed)
        except Exception as e:
            logger.error(f"Erreur synthèse: {e}")
            return None
    
    def test_synthesis(self, text: str = "Bonjour, ceci est un test.") -> bool:
        """Teste la synthèse vocale."""
        try:
            return self.tts_engine.test_synthesis(text)
        except Exception as e:
            logger.error(f"Erreur test synthèse: {e}")
            return False
    
    def get_available_voices(self) -> list:
        """Retourne la liste des voix disponibles."""
        try:
            from ..config import config
            import os
            voices = []
            if os.path.exists(config.VOICES_FOLDER):
                for d in os.listdir(config.VOICES_FOLDER):
                    sub = os.path.join(config.VOICES_FOLDER, d)
                    if os.path.isdir(sub) and any(f.endswith(".onnx") for f in os.listdir(sub)):
                        voices.append(d)
            return voices or [config.DEFAULT_PIPER_VOICE]
        except Exception as e:
            logger.error(f"Erreur récupération voix: {e}")
            return []
