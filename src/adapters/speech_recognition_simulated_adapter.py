import numpy as np
from typing import Any, List, Optional
from ..interfaces.speech_recognition import ISpeechRecognitionAdapter
from ..utils.logger import logger


class SimulatedSpeechRecognitionAdapter(ISpeechRecognitionAdapter):
    """Adaptateur de reconnaissance vocale simulé pour les tests."""

    def __init__(self, fake_responses: Optional[dict] = None):
        self.fake_responses = fake_responses or {}
        self.is_available = True
        logger.info("SimulatedSpeechRecognitionAdapter initialisé")

    def transcribe_array(self, audio: np.ndarray, **kwargs: Any) -> str:
        """Transcrit un tableau d'audio numpy."""
        try:
            if self.fake_responses:
                for key, response in self.fake_responses.items():
                    if key.lower() in str(audio):
                        return response
            return "Ceci est une transcription simulée."
        except Exception as e:
            logger.error(f"Erreur transcription simulée: {e}")
            return ""

    def transcribe_file(self, path: str, **kwargs: Any) -> str:
        """Transcrit un fichier audio."""
        try:
            if self.fake_responses:
                for key, response in self.fake_responses.items():
                    if key.lower() in path:
                        return response
            return f"Transcription simulée du fichier: {path}"
        except Exception as e:
            logger.error(f"Erreur transcription fichier simulée: {e}")
            return ""

    def unload_model(self) -> None:
        """Décharge le modèle de la mémoire."""
        logger.info("Modèle déchargé (simulation)")

    def load_model(self) -> None:
        logger.info("Modèle chargé (simulation)")

    def get_available_models(self) -> List[str]:
        """Retourne la liste des modèles disponibles."""
        return ["simulated-base", "simulated-large"]

    def optimize_cache(self) -> bool:
        """Optimise le cache du modèle."""
        logger.info("Cache optimisé (simulation)")
        return True
