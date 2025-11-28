import numpy as np
import tempfile
import os
from typing import Optional
from abc import ABC, abstractmethod
from ..utils.logger import logger

class ISpeechRecognitionAdapter(ABC):
    """Interface pour les adaptateurs de reconnaissance vocale."""
    
    @abstractmethod
    def transcribe_array(self, audio_data: np.ndarray, language: str = "fr") -> str:
        """Transcrit un tableau numpy d'audio en texte."""
        pass
    
    @abstractmethod
    def transcribe_file(self, file_path: str, language: str = "fr") -> str:
        """Transcrit un fichier audio en texte."""
        pass
    
    @abstractmethod
    def unload(self) -> bool:
        """Décharge le modèle de la mémoire."""
        pass
    
    @abstractmethod
    def optimize_cache(self) -> bool:
        """Optimise le cache du modèle."""
        pass

class WhisperSpeechRecognitionAdapter(ISpeechRecognitionAdapter):
    """Adaptateur concret pour Whisper."""
    
    def __init__(self, model_name: str = "base"):
        self.model_name = model_name
        self.model = None
        self._load_model()
        logger.info(f"WhisperSpeechRecognitionAdapter initialisé - Modèle: {model_name}")
    
    def _load_model(self) -> bool:
        """Charge le modèle Whisper."""
        try:
            import whisper
            logger.info(f"🔄 Chargement du modèle Whisper '{self.model_name}'...")
            self.model = whisper.load_model(self.model_name)
            logger.info("✅ Modèle Whisper chargé avec succès")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur chargement modèle Whisper: {e}")
            return False
    
    def transcribe_array(self, audio_data: np.ndarray, language: str = "fr") -> str:
        """Transcrit un tableau numpy d'audio en texte."""
        try:
            if self.model is None:
                return ""
            
            import whisper
            # Convertir int16 en float32
            if audio_data.dtype == np.int16:
                audio_float = audio_data.astype(np.float32) / 32768.0
            else:
                audio_float = audio_data.astype(np.float32)
            
            logger.info(f"📝 Transcription de {len(audio_float)} échantillons...")
            
            # Transcrire avec Whisper
            result = self.model.transcribe(
                audio_float,
                language=language,
                fp16=False  # Désactiver FP16 pour compatibilité
            )
            
            text = result.get("text", "").strip()
            logger.info(f"✅ Transcription réussie: {text}")
            
            return text
            
        except Exception as e:
            logger.error(f"❌ Erreur transcription: {e}")
            return ""
    
    def transcribe_file(self, file_path: str, language: str = "fr") -> str:
        """Transcrit un fichier audio en texte."""
        try:
            if self.model is None:
                return ""
            
            import whisper
            logger.info(f"📝 Transcription du fichier: {file_path}")
            
            result = self.model.transcribe(
                file_path,
                language=language,
                fp16=False
            )
            
            text = result.get("text", "").strip()
            logger.info(f"✅ Transcription fichier réussie: {text}")
            
            return text
            
        except Exception as e:
            logger.error(f"❌ Erreur transcription fichier: {e}")
            return ""
    
    def unload(self) -> bool:
        """Décharge le modèle Whisper de la mémoire GPU."""
        try:
            import torch
            if self.model and torch.cuda.is_available():
                del self.model
                self.model = None
                torch.cuda.empty_cache()
                logger.info("🗑️ Modèle Whisper déchargé")
                return True
            elif self.model:
                del self.model
                self.model = None
                logger.info("🗑️ Modèle Whisper déchargé (CPU)")
                return True
        except Exception as e:
            logger.error(f"Erreur déchargement modèle Whisper: {e}")
        return False
    
    def optimize_cache(self) -> bool:
        """Optimise le cache du modèle."""
        try:
            if hasattr(self.model, 'cache_clear'):
                self.model.cache_clear()
                logger.info("🧹 Cache modèle Whisper nettoyé")
            return True
        except Exception as e:
            logger.debug(f"Erreur optimisation cache Whisper: {e}")
            return False

class SimulatedSpeechRecognitionAdapter(ISpeechRecognitionAdapter):
    """Adaptateur simulé pour le développement et les tests."""
    
    def __init__(self, fake_result: str = "Bonjour, comment allez-vous ?"):
        self.fake_result = fake_result
        logger.info("SimulatedSpeechRecognitionAdapter initialisé")
    
    def transcribe_array(self, audio_data: np.ndarray, language: str = "fr") -> str:
        """Transcrit un tableau numpy d'audio en texte simulé."""
        logger.warning("🔍 Utilisation transcription simulée")
        # Pour les tests, on peut renvoyer un texte basé sur la longueur de l'audio
        duration_ms = len(audio_data) // 16  # Approximation en ms (16kHz)
        return f"[SIMULÉ {duration_ms}ms] {self.fake_result}"
    
    def transcribe_file(self, file_path: str, language: str = "fr") -> str:
        """Transcrit un fichier audio en texte simulé."""
        logger.warning("🔍 Utilisation transcription fichier simulée")
        try:
            # Simuler la lecture du fichier
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            return f"[SIMULÉ FICHIER {file_size}b] {self.fake_result}"
        except:
            return f"[SIMULÉ] {self.fake_result}"
    
    def unload(self) -> bool:
        """Décharge le modèle simulé."""
        logger.info("🗑️ Modèle simulé déchargé")
        return True
    
    def optimize_cache(self) -> bool:
        """Optimise le cache simulé."""
        logger.info("🧹 Cache simulé optimisé")
        return True

class SpeechRecognitionService:
    """Service de reconnaissance vocale avec injection de dépendance."""
    
    def __init__(self, speech_recognition_adapter: ISpeechRecognitionAdapter):
        self.speech_recognition_adapter = speech_recognition_adapter
        self.is_available = True
        logger.info("SpeechRecognitionService initialisé avec adaptateur")
    
    @classmethod
    def create_with_whisper(cls, model_name: str = "base"):
        """Factory method pour créer un service avec Whisper."""
        adapter = WhisperSpeechRecognitionAdapter(model_name)
        return cls(adapter)
    
    @classmethod
    def create_with_simulation(cls, fake_result: str = "Bonjour, comment allez-vous ?"):
        """Factory method pour créer un service avec simulation."""
        adapter = SimulatedSpeechRecognitionAdapter(fake_result)
        return cls(adapter)
    
    def transcribe(self, audio_data: np.ndarray, language: str = "fr") -> str:
        """
        Transcrit l'audio en texte.
        
        Args:
            audio_data: Données audio numpy array (16kHz, int16)
            language: Langue de transcription (par défaut: fr)
            
        Returns:
            Texte transcrit
        """
        try:
            return self.speech_recognition_adapter.transcribe_array(audio_data, language)
        except Exception as e:
            logger.error(f"❌ Erreur transcription: {e}")
            return ""
    
    def transcribe_file(self, file_path: str, language: str = "fr") -> str:
        """
        Transcrit un fichier audio.
        
        Args:
            file_path: Chemin du fichier audio
            language: Langue de transcription
            
        Returns:
            Texte transcrit
        """
        try:
            return self.speech_recognition_adapter.transcribe_file(file_path, language)
        except Exception as e:
            logger.error(f"❌ Erreur transcription fichier: {e}")
            return ""
    
    def unload_model(self):
        """Décharge le modèle de la mémoire."""
        try:
            return self.speech_recognition_adapter.unload()
        except Exception as e:
            logger.error(f"Erreur déchargement modèle: {e}")
            return False
    
    def optimize_model_cache(self):
        """Optimise le cache du modèle."""
        try:
            return self.speech_recognition_adapter.optimize_cache()
        except Exception as e:
            logger.debug(f"Erreur optimisation cache: {e}")
            return False
    
    def get_available_models(self) -> list:
        """Retourne la liste des modèles disponibles."""
        # Cette méthode pourrait être déplacée dans l'adaptateur si nécessaire
        return ["tiny", "base", "small", "medium", "large"]
    
    def test_transcription(self) -> bool:
        """Teste la transcription."""
        try:
            # Créer un court échantillon de test
            test_audio = np.zeros(16000, dtype=np.int16)  # 1 seconde de silence
            result = self.transcribe(test_audio)
            logger.info("✅ Test transcription réussi")
            return True
        except Exception as e:
            logger.error(f"❌ Test transcription échoué: {e}")
            return False
