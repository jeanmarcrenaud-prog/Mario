from typing import Optional, List
from ..utils.logger import logger

class TTSService:
    """Service de synthèse vocale de base."""
    
    def __init__(self, voice_name: str = "fr_FR-siwis-medium"):
        self.voice_name = voice_name
        self.is_available = self._check_tts_availability()
        logger.info(f"TTSService initialisé - Voix: {voice_name}")
    
    def _check_tts_availability(self) -> bool:
        """Vérifie si le TTS est disponible."""
        try:
            # Pour le moment, juste un test basique
            return True
        except Exception as e:
            logger.warning(f"TTS non disponible: {e}")
            return False
    
    def speak(self, text: str, speed: float = 1.0) -> bool:
        """
        Synthétise et lit le texte.
        Retourne True si réussi, False sinon.
        """
        try:
            if not text.strip():
                logger.warning("Texte vide fourni au TTS")
                return False
            
            if not self.is_available:
                logger.warning("TTS non disponible, message ignoré")
                return False
            
            # Pour le moment, juste un log
            logger.info(f"🗣️ TTS: {text}")
            
            # Ici viendra l'intégration avec votre TTS existant
            # self._actual_speak(text, speed)
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur TTS: {e}")
            return False
    
    def test_synthesis(self, text: str = "Bonjour, ceci est un test.") -> bool:
        """Teste la synthèse vocale."""
        logger.info("🧪 Test de synthèse vocale...")
        success = self.speak(text)
        if success:
            logger.info("✅ Test TTS réussi")
        else:
            logger.error("❌ Test TTS échoué")
        return success

    def get_available_voices(self) -> List[str]:
        """Retourne la liste des voix disponibles."""
        try:
            import os
            from ..config.config import config
            
            voices = []
            if os.path.exists(config.VOICES_FOLDER):
                for d in os.listdir(config.VOICES_FOLDER):
                    sub = os.path.join(config.VOICES_FOLDER, d)
                    if os.path.isdir(sub) and any(f.endswith(".onnx") for f in os.listdir(sub)):
                        voices.append(d)
            return voices or [config.DEFAULT_VOICE]
        except Exception as e:
            logger.error(f"Erreur récupération voix: {e}")
            return ["fr_FR-siwis-medium"]
