import numpy as np
import torch
import whisper
import time
from typing import Optional, Dict, Any
from ..config import config
from ..utils.logger import logger

class SpeechRecognizer:
    def __init__(self):
        self.model = None
        self.fallback_model = None
        self.is_loaded = False
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.use_fp16 = torch.cuda.is_available()
        logger.info("Utilisation de %s pour Whisper (FP16: %s)", self.device, self.use_fp16)

    def load_model(self, model_name: str = config.WHISPER_MODEL_NAME) -> bool:
        """Charge le modèle Whisper avec optimisation GPU."""
        if self.is_loaded and self.model is not None:
            logger.info("Modèle Whisper déjà chargé: %s", model_name)
            return True

        try:
            logger.info("Chargement du modèle Whisper '%s' sur %s", model_name, self.device)
            
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.backends.cudnn.benchmark = True
            
            start_time = time.time()
            self.model = whisper.load_model(model_name, device=self.device)
            load_time = time.time() - start_time
            
            self.is_loaded = True
            logger.info("Modèle Whisper chargé avec succès en %.2fs", load_time)
            
            self._preload_fallback_model()
            
            return True
            
        except Exception as e:
            logger.error("Erreur de chargement du modèle Whisper: %s", e)
            return False

    def _preload_fallback_model(self):
        """Précharge un modèle plus léger pour fallback."""
        try:
            if self.fallback_model is None:
                logger.info("[CHARGEMENT] Préchargement du modèle small pour fallback...")
                self.fallback_model = whisper.load_model("small", device=self.device)
        except Exception as e:
            logger.warning("Impossible de précharger le modèle de fallback: %s", e)

    def is_ready(self) -> bool:
        """Vérifie si le modèle est prêt."""
        ready = self.is_loaded and self.model is not None
        if not ready:
            logger.warning("SpeechRecognizer non prêt")
        return ready

    def transcribe(self, audio_data: np.ndarray, language: str = "fr") -> Dict[str, Any]:
        """Transcrit un bloc audio en texte avec métadonnées."""
        if not self.is_ready():
            logger.error("Modèle Whisper non chargé")
            return {"text": "", "confidence": 0.0, "error": "Modèle non chargé"}

        try:
            logger.debug("Transcription en cours...")
            start_time = time.time()
            
            audio_data = self._preprocess_audio(audio_data)
            
            with torch.no_grad():
                result = self.model.transcribe(
                    audio_data,
                    language=language,
                    fp16=self.use_fp16,
                    temperature=0.0,
                    best_of=1,
                    no_speech_threshold=0.6
                )

            transcription_time = time.time() - start_time
            text = result.get("text", "").strip()
            confidence = self._calculate_confidence(result)
            
            logger.debug("Transcription terminée en %.2fs: '%s...'", transcription_time, text[:60])
            
            return {
                "text": text,
                "confidence": confidence,
                "language": language,
                "processing_time": transcription_time,
                "has_speech": len(text) > 0
            }

        except torch.cuda.OutOfMemoryError:
            logger.warning("Mémoire GPU insuffisante, utilisation du modèle small")
            return self._fallback_transcribe(audio_data, language)
        except Exception as e:
            logger.error("Erreur de transcription: %s", e)
            return {"text": "", "confidence": 0.0, "error": str(e)}

    def _preprocess_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """Prétraite l'audio pour Whisper."""
        if len(audio_data.shape) > 1:
            audio_data = np.mean(audio_data, axis=1)
        
        audio_data = audio_data.astype(np.float32)
        if np.max(np.abs(audio_data)) > 0:
            audio_data = audio_data / np.max(np.abs(audio_data))
        
        return audio_data

    def _calculate_confidence(self, result: Dict) -> float:
        """Calcule la confiance de la transcription."""
        try:
            segments = result.get("segments", [])
            if not segments:
                return 0.0
            
            confidences = [seg.get("avg_logprob", 0) for seg in segments]
            return float(np.mean(confidences)) if confidences else 0.0
        except:
            return 0.0

    def _fallback_transcribe(self, audio_data: np.ndarray, language: str) -> Dict[str, Any]:
        """Fallback sur un modèle plus léger."""
        try:
            if self.fallback_model is None:
                self._preload_fallback_model()
            
            if self.fallback_model is None:
                return {"text": "", "confidence": 0.0, "error": "Modèle fallback non disponible"}
            
            start_time = time.time()
            with torch.no_grad():
                result = self.fallback_model.transcribe(
                    audio_data, 
                    language=language, 
                    fp16=self.use_fp16
                )
            
            transcription_time = time.time() - start_time
            text = result.get("text", "").strip()
            
            logger.info("Fallback transcription en %.2fs", transcription_time)
            
            return {
                "text": text,
                "confidence": 0.5,
                "language": language,
                "processing_time": transcription_time,
                "has_speech": len(text) > 0,
                "fallback_used": True
            }
            
        except Exception as e:
            logger.error("Fallback transcription échouée: %s", e)
            return {"text": "", "confidence": 0.0, "error": str(e)}

    def cleanup(self):
        """Nettoie la mémoire GPU."""
        self.model = None
        self.fallback_model = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("Mémoire Whisper nettoyée")
