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
