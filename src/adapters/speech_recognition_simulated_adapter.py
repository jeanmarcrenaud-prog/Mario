from __future__ import annotations
import os
import numpy as np
from typing import Any
from ..interfaces.speech_recognition import ISpeechRecognitionAdapter
from ..utils.logger import logger


class SimulatedSpeechRecognitionAdapter(ISpeechRecognitionAdapter):
    """Adaptateur simulé pour le développement et les tests."""

    def __init__(self, fake_result: str = "Bonjour, comment allez-vous ?"):
        self.fake_result = fake_result
        logger.info("SimulatedSpeechRecognitionAdapter initialisé")

    def load_model(self) -> None:
        """Charge le modèle simulé (no-op)."""
        logger.info("🔄 Chargement du modèle simulé...")
        logger.info("✅ Modèle simulé chargé")

    def unload_model(self) -> None:
        """Décharge le modèle simulé (no-op)."""
        logger.info("🗑️ Modèle simulé déchargé")

    def transcribe_array(self, audio: Any, **kwargs: Any) -> str:
        """Transcrit un tableau numpy d'audio en texte simulé."""
        logger.warning("🔍 Utilisation transcription simulée")
        # Pour les tests, on peut renvoyer un texte basé sur la longueur de l'audio
        duration_ms = len(audio) // 16  # Approximation en ms (16kHz)
        return f"[SIMULÉ {duration_ms}ms] {self.fake_result}"

    def transcribe_file(self, path: str, **kwargs: Any) -> str:
        """Transcrit un fichier audio en texte simulé."""
        logger.warning("🔍 Utilisation transcription fichier simulée")
        try:
            # Simuler la lecture du fichier
            file_size = os.path.getsize(path) if os.path.exists(path) else 0
            return f"[SIMULÉ FICHIER {file_size}b] {self.fake_result}"
        except Exception:
            return f"[SIMULÉ] {self.fake_result}"

    def get_available_models(self) -> list[str]:
        """Retourne la liste des modèles simulés."""
        return ["simulated-tiny", "simulated-base"]
