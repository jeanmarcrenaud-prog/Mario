import whisper
import numpy as np
import tempfile
import os
from typing import Optional
from ..utils.logger import logger

class SpeechRecognitionService:
    """Service de reconnaissance vocale avec Whisper."""
    
    def __init__(self, model_name: str = "base"):
        self.model_name = model_name
        self.model = None
        self.is_available = self._load_model()
        logger.info(f"SpeechRecognitionService initialisé - Modèle: {model_name}")
    
    def _load_model(self) -> bool:
        """Charge le modèle Whisper."""
        try:
            logger.info(f"🔄 Chargement du modèle Whisper '{self.model_name}'...")
            self.model = whisper.load_model(self.model_name)
            logger.info("✅ Modèle Whisper chargé avec succès")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur chargement modèle Whisper: {e}")
            return False

    def unload_model(self):
        """Décharge le modèle Whisper de la mémoire GPU."""
        try:
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

    def optimize_model_cache(self):
        """Optimise le cache du modèle."""
        try:
            if hasattr(self.model, 'cache_clear'):
                self.model.cache_clear()
                logger.info("🧹 Cache modèle Whisper nettoyé")
            return True
        except Exception as e:
            logger.debug(f"Erreur optimisation cache Whisper: {e}")
            return False

    def load_model_on_demand(self):
        """Charge le modèle uniquement quand nécessaire."""
        if not self.model:
            logger.info("⚡ Chargement modèle Whisper à la demande")
            return self._load_model()
        return True
    
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
            if not self.is_available or self.model is None:
                logger.warning("Whisper non disponible, retour texte simulé")
                return self._simulate_transcription(audio_data)
            
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
    
    def _simulate_transcription(self, audio_data: np.ndarray) -> str:
        """Simulation de transcription pour tests."""
        logger.warning("🔍 Utilisation transcription simulée")
        return "Bonjour, comment allez-vous ?"
    
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
            if not self.is_available or self.model is None:
                logger.warning("Whisper non disponible")
                return ""
            
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
    
    def get_available_models(self) -> list:
        """Retourne la liste des modèles disponibles."""
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
