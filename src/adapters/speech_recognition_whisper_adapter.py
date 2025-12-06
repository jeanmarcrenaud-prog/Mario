from __future__ import annotations
import numpy as np
from typing import Any
from ..interfaces.speech_recognition import ISpeechRecognitionAdapter
from ..utils.logger import logger


class WhisperSpeechRecognitionAdapter(ISpeechRecognitionAdapter):
    """Adaptateur concret pour Whisper."""

    def __init__(self, model_name: str = "base"):
        self.model_name = model_name
        self.model = None
        self.load_model()
        logger.info(f"WhisperSpeechRecognitionAdapter initialisé - Modèle: {model_name}")

    def load_model(self) -> None:
        """Charge le modèle Whisper."""
        try:
            import whisper
            logger.info(f"🔄 Chargement du modèle Whisper '{self.model_name}'...")
            self.model = whisper.load_model(self.model_name)
            logger.info("✅ Modèle Whisper chargé avec succès")
        except Exception as e:
            logger.error(f"❌ Erreur chargement modèle Whisper: {e}")

    def unload_model(self) -> None:
        """Décharge le modèle Whisper de la mémoire GPU."""
        try:
            import torch
            if self.model and torch.cuda.is_available():
                del self.model
                self.model = None
                torch.cuda.empty_cache()
                logger.info("🗑️ Modèle Whisper déchargé")
            elif self.model:
                del self.model
                self.model = None
                logger.info("🗑️ Modèle Whisper déchargé (CPU)")
        except Exception as e:
            logger.error(f"Erreur déchargement modèle Whisper: {e}")

    def transcribe_array(self, audio: Any, **kwargs: Any) -> str:
        """Transcrit un tableau numpy d'audio en texte."""
        try:
            if self.model is None:
                return ""

            import whisper
            # Convertir int16 en float32
            if audio.dtype == np.int16:
                audio_float = audio.astype(np.float32) / 32768.0
            else:
                audio_float = audio.astype(np.float32)

            language = kwargs.get("language", "fr")
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

    def transcribe_file(self, path: str, **kwargs: Any) -> str:
        """Transcrit un fichier audio en texte."""
        try:
            if self.model is None:
                return ""

            import whisper
            language = kwargs.get("language", "fr")
            logger.info(f"📝 Transcription du fichier: {path}")

            result = self.model.transcribe(
                path,
                language=language,
                fp16=False
            )

            text = result.get("text", "").strip()
            logger.info(f"✅ Transcription fichier réussie: {text}")

            return text

        except Exception as e:
            logger.error(f"❌ Erreur transcription fichier: {e}")
            return ""

    def get_available_models(self) -> list[str]:
        """Retourne la liste des modèles Whisper disponibles."""
        return ["tiny", "base", "small", "medium", "large"]
