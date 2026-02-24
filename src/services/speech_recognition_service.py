from __future__ import annotations
import numpy as np
from typing import Any
from ..interfaces.speech_recognition import ISpeechRecognitionAdapter
from ..utils.logger import logger


class SpeechRecognitionService:
    """Service de reconnaissance vocale avec injection de dépendance."""

    def __init__(self, speech_recognition_adapter: ISpeechRecognitionAdapter):
        self.speech_recognition_adapter = speech_recognition_adapter
        self.is_available = True
        logger.info("SpeechRecognitionService initialisé avec adaptateur")

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
            return self.speech_recognition_adapter.transcribe_array(audio_data, language=language)
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
            return self.speech_recognition_adapter.transcribe_file(file_path, language=language)
        except Exception as e:
            logger.error(f"❌ Erreur transcription fichier: {e}")
            return ""

    def unload_model(self) -> bool:
        """Décharge le modèle de la mémoire."""
        try:
            # Adapter may expose unload() or unload_model(); try both
            if hasattr(self.speech_recognition_adapter, "unload"):
                self.speech_recognition_adapter.unload()
            else:
                self.speech_recognition_adapter.unload_model()
            return True
        except Exception as e:
            logger.error(f"Erreur déchargement modèle: {e}")
            return False

    def get_available_models(self) -> list[str]:
        """Retourne la liste des modèles disponibles."""
        try:
            return self.speech_recognition_adapter.get_available_models()
        except Exception as e:
            logger.debug(f"Erreur récupération modèles: {e}")
            return []

    def optimize_model_cache(self) -> bool:
        """Optimise le cache du modèle."""
        try:
            # Adapter may expose optimize_cache(); use it
            self.speech_recognition_adapter.optimize_cache()
            return True
        except Exception as e:
            logger.debug(f"Erreur optimisation cache: {e}")
            return False


    def get_available_models(self) -> list[str]:
        """Retourne la liste des modèles disponibles."""
        try:
            return self.speech_recognition_adapter.get_available_models()
        except Exception as e:
            logger.debug(f"Erreur récupération modèles: {e}")
            return []

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

    @classmethod
    def create_with_simulation(cls):
        """Factory method pour une instance de service simulé."""
        from .simulated_speech_recognition import SimpleSimulationSpeechAdapter
        adapter = SimpleSimulationSpeechAdapter()
        return cls(adapter)

    @classmethod
    def create_with_whisper(cls, model_size: str = "base"):
        """Factory method pour une instance de service avec Whisper."""
        from ..adapters.speech_recognition_whisper_adapter import WhisperSpeechRecognitionAdapter
        adapter = WhisperSpeechRecognitionAdapter(model_size)
        return cls(adapter)
