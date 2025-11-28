from typing import Optional, List
from abc import ABC, abstractmethod
from ..utils.logger import logger
from ..config.config import config

class ITTSAdapter(ABC):
    """Interface pour les adaptateurs TTS."""
    
    @abstractmethod
    def say(self, text: str, speed: float = 1.0) -> bool:
        """Synthétise et lit le texte."""
        pass
    
    @abstractmethod
    def unload_voice(self) -> bool:
        """Décharge la voix de la mémoire."""
        pass
    
    @abstractmethod
    def get_available_voices(self) -> List[str]:
        """Retourne la liste des voix disponibles."""
        pass

class PiperTTSAdapter(ITTSAdapter):
    """Adaptateur concret pour Piper TTS."""
    
    def __init__(self, voice_name: str = "fr_FR-siwis-medium"):
        self.voice_name = voice_name
        from src.models.text_to_speech import TextToSpeech
        self._tts_engine = TextToSpeech(voice_name)
        logger.info(f"PiperTTSAdapter initialisé - Voix: {voice_name}")
    
    def say(self, text: str, speed: float = 1.0) -> bool:
        """Synthétise et lit le texte."""
        try:
            self._tts_engine.say(text, speed)
            return True
        except Exception as e:
            logger.error(f"Erreur PiperTTS: {e}")
            return False
    
    def unload_voice(self) -> bool:
        """Décharge la voix de la mémoire."""
        try:
            if hasattr(self._tts_engine, 'cleanup'):
                self._tts_engine.cleanup()
            logger.info("🗑️ Voix déchargée")
            return True
        except Exception as e:
            logger.error(f"Erreur déchargement voix PiperTTS: {e}")
            return False
    
    def get_available_voices(self) -> List[str]:
        """Retourne la liste des voix disponibles."""
        try:
            import os
            voices = []
            if os.path.exists(config.VOICES_FOLDER):
                for d in os.listdir(config.VOICES_FOLDER):
                    sub = os.path.join(config.VOICES_FOLDER, d)
                    if os.path.isdir(sub) and any(f.endswith(".onnx") for f in os.listdir(sub)):
                        voices.append(d)
            return voices or [config.DEFAULT_VOICE]
        except Exception as e:
            logger.error(f"Erreur récupération voix PiperTTS: {e}")
            return ["fr_FR-siwis-medium"]

class TTSService:
    """Service de synthèse vocale avec injection de dépendance."""
    
    def __init__(self, tts_adapter: ITTSAdapter):
        self.tts_adapter = tts_adapter
        self.is_available = True
        logger.info("TTSService initialisé avec adaptateur")
    
    @classmethod
    def create_with_piper(cls, voice_name: str = "fr_FR-siwis-medium"):
        """Factory method pour créer un TTSService avec PiperTTSAdapter."""
        adapter = PiperTTSAdapter(voice_name)
        return cls(adapter)
    
    def say(self, text: str, speed: float = 1.0) -> bool:
        """Alias pour la méthode speak - pour la compatibilité avec le code existant"""
        return self.speak(text, speed)
    
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
            
            logger.info(f"🗣️ TTS: {text}")
            return self.tts_adapter.say(text, speed)
            
        except Exception as e:
            logger.error(f"Erreur TTS: {e}")
            return False

    def unload_voice(self):
        """Décharge la voix de la mémoire."""
        try:
            return self.tts_adapter.unload_voice()
        except Exception as e:
            logger.error(f"Erreur déchargement voix: {e}")
            return False

    def optimize_voice_cache(self):
        """Optimise le cache voix - délégué à l'adaptateur si supporté."""
        try:
            # Si l'adaptateur supporte l'optimisation de cache, l'appeler
            if hasattr(self.tts_adapter, 'optimize_cache'):
                return self.tts_adapter.optimize_cache()
            return False
        except Exception as e:
            logger.debug(f"Erreur optimisation cache TTS: {e}")
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
            return self.tts_adapter.get_available_voices()
        except Exception as e:
            logger.error(f"Erreur récupération voix: {e}")
            return ["fr_FR-siwis-medium"]
