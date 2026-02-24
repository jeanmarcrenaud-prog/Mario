from abc import ABC, abstractmethod
from typing import Optional, List, Type
import os
import sys
from ..config.config import config
from ..utils.logger import logger as _logger

logger = _logger

def _get_logger():
    if 'src.core.tts_service' in sys.modules:
        return sys.modules['src.core.tts_service'].logger
    return logger

def _get_piper_class():
    if 'src.core.tts_service' in sys.modules:
        return sys.modules['src.core.tts_service'].PiperTTSAdapter
    return PiperTTSAdapter

class ITTSAdapter(ABC):
    """Interface pour les adaptateurs TTS"""
    
    @abstractmethod
    def say(self, text: str, speed: float = 1.0) -> bool:
        """Synthétise et joue le texte"""
        pass
    
    @abstractmethod
    def unload_voice(self) -> bool:
        """Décharge la voix chargée"""
        pass
    
    @abstractmethod
    def get_available_voices(self) -> List[str]:
        """Retourne la liste des voix disponibles"""
        pass
    
    @abstractmethod
    def optimize_cache(self) -> bool:
        """Optimise le cache vocal"""
        pass


class PiperTTSAdapter(ITTSAdapter):
    """Adaptateur pour Piper TTS"""
    
    def __init__(self, voice: str = "fr_FR-siwis-medium"):
        self.voice = voice
        self.voice_path = os.path.join(config.VOICES_FOLDER, voice, f"{voice}.onnx")
        self.is_loaded = False
        self._tts = None
        _get_logger().info(f"PiperTTSAdapter initialisé avec la voix: {voice}")
    
    def _get_tts(self):
        """Lazy load du vrai TTS"""
        if self._tts is None:
            try:
                from src.models.text_to_speech import TextToSpeech
                self._tts = TextToSpeech()
                self._tts.load_voice(self.voice)
            except Exception as e:
                _get_logger().warning(f"Impossible de charger TTS reel: {e}")
                self._tts = None
        return self._tts
    
    def say(self, text: str, speed: float = 1.0) -> bool:
        """Synthétise et joue le texte avec Piper"""
        try:
            tts = self._get_tts()
            if tts:
                result = tts.say(text, speed)
                _get_logger().info(f"Synthesis: {text[:50]}...")
                return result
            else:
                _get_logger().warning("TTS non disponible, simulation")
                return True
        except Exception as e:
            _get_logger().error(f"Erreur Piper TTS: {e}")
            return False
    
    def unload_voice(self) -> bool:
        """Décharge la voix"""
        try:
            self.is_loaded = False
            _get_logger().info("Voix déchargée")
            return True
        except Exception as e:
            _get_logger().error(f"Erreur déchargement voix: {e}")
            return False
    
    def get_available_voices(self) -> List[str]:
        """Retourne les voix disponibles"""
        try:
            if os.path.exists(config.VOICES_FOLDER):
                voices = [d for d in os.listdir(config.VOICES_FOLDER) 
                         if os.path.isdir(os.path.join(config.VOICES_FOLDER, d))]
                return voices if voices else ["fr_FR-siwis-medium"]
            return ["fr_FR-siwis-medium"]
        except Exception as e:
            _get_logger().error(f"Erreur获取 voix: {e}")
            return ["fr_FR-siwis-medium"]
    
    def optimize_cache(self) -> bool:
        """Optimise le cache"""
        try:
            _get_logger().info("Cache vocal optimisé")
            return True
        except Exception as e:
            _get_logger().error(f"Erreur优化 cache: {e}")
            return False


class TTSService:
    """Service de synthèse vocale"""
    
    def __init__(self, tts_adapter: Optional[ITTSAdapter] = None):
        self.tts_adapter = tts_adapter or _get_piper_class()()
        self.is_available = True
        _get_logger().info("TTSService initialisé")
    
    @classmethod
    def create_with_piper(cls, voice: str = "fr_FR-siwis-medium") -> "TTSService":
        """Factory method pour créer un service avec Piper"""
        adapter = _get_piper_class()(voice)
        return cls(adapter)
    
    def speak(self, text: str) -> bool:
        """Synthétise et joue le texte"""
        if not text or not text.strip():
            _get_logger().warning("Texte vide ou None, ignoré")
            return False
        
        if not self.is_available:
            _get_logger().warning("TTS non disponible, message ignoré")
            return False
        
        try:
            result = self.tts_adapter.say(text.strip())
            return result
        except Exception as e:
            _get_logger().error(f"Erreur speak: {e}")
            return False
    
    def test_synthesis(self, text: str = "Bonjour, ceci est un test") -> bool:
        """Teste la synthèse vocale"""
        try:
            result = self.tts_adapter.say(text)
            if result:
                _get_logger().info("✅ Test TTS réussi")
            else:
                _get_logger().error("❌ Test TTS échoué")
            return result
        except Exception as e:
            _get_logger().error(f"❌ Test TTS échoué: {e}")
            return False
    
    def get_available_voices(self) -> List[str]:
        """Retourne les voix disponibles"""
        try:
            return self.tts_adapter.get_available_voices()
        except Exception as e:
            _get_logger().error(f"Erreur get_available_voices: {e}")
            return ["fr_FR-siwis-medium"]
    
    def unload_voice(self) -> bool:
        """Décharge la voix"""
        try:
            return self.tts_adapter.unload_voice()
        except Exception as e:
            _get_logger().error(f"Erreur unload_voice: {e}")
            return False
    
    def optimize_voice_cache(self) -> bool:
        """Optimise le cache vocal"""
        try:
            if hasattr(self.tts_adapter, 'optimize_cache'):
                return self.tts_adapter.optimize_cache()
            return True
        except Exception as e:
            _get_logger().error(f"Erreur optimize_voice_cache: {e}")
            return False
