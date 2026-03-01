# src/core/audio_pipeline.py
import numpy as np
import queue
import threading
import time
from typing import Callable, Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

from src.utils.logger import logger


class AudioPipeline:
    """Gère le pipeline audio: wake-word, transcription, TTS"""

    def __init__(
        self,
        wake_word_service,
        speech_recognition_service,
        tts_service,
        settings,
    ):
        self.wake_word_service = wake_word_service
        self.speech_recognition_service = speech_recognition_service
        self.tts_service = tts_service
        self.settings = settings

        self._is_running = False
        self._audio_queue: queue.Queue[np.ndarray] = queue.Queue(maxsize=settings.audio_buffer_size)
        
        chunk_size = settings.chunk_size // 2 if settings.enable_low_latency else settings.chunk_size
        self._chunk_size = chunk_size
        
        self._transcribe_executor = ThreadPoolExecutor(max_workers=2)
        self._tts_executor = ThreadPoolExecutor(max_workers=1)

        self._on_transcription_ready: Optional[Callable] = None
        self._on_wake_word_detected: Optional[Callable] = None
        
        self._latency_stats = {
            "transcription": [],
            "tts": [],
            "wake_word": [],
        }

    def start(self):
        """Démarre le pipeline audio"""
        self._is_running = True

        self.wake_word_service.set_wake_word_callback(self._on_wake_word_detected_fn)
        self.wake_word_service.set_audio_callback(self._on_audio_received_fn)
        self.wake_word_service.start_detection(self.settings.microphone_index)

        logger.info("AudioPipeline started")

    def stop(self):
        """Arrête le pipeline audio"""
        self._is_running = False
        self.wake_word_service.stop_detection()
        self._transcribe_executor.shutdown(wait=False)
        self._tts_executor.shutdown(wait=False)
        logger.info("AudioPipeline stopped")

    def set_transcription_callback(self, callback: Callable[[str], None]):
        """Définit le callback quand la transcription est prête"""
        self._on_transcription_ready = callback

    def set_wake_word_callback(self, callback: Callable[[], None]):
        """Définit le callback quand le wake-word est détecté"""
        self._on_wake_word_detected = callback

    def speak(self, text: str) -> bool:
        """Synthétise et joue le texte"""
        if not text or not text.strip():
            return False
        try:
            start_time = time.time()
            success = self._tts_executor.submit(
                self.tts_service.say, text, self.settings.speech_speed
            ).result(timeout=30)
            latency = time.time() - start_time
            self._latency_stats["tts"].append(latency)
            logger.debug(f"Latence TTS: {latency:.3f}s")
            return bool(success)
        except Exception as e:
            logger.error(f"Erreur speak: {e}")
            return False

    def _on_wake_word_detected_fn(self):
        logger.info("🎯 Wake-word détecté!")
        if self._on_wake_word_detected:
            self._on_wake_word_detected()

    def _on_audio_received_fn(self, audio_data: bytes):
        """Callback appelé quand des données audio sont reçues"""
        start_time = time.time()
        logger.info(f"Audio reçu ({len(audio_data)} octets)")

        audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

        future = self._transcribe_executor.submit(
            self.speech_recognition_service.transcribe, audio_np, "fr"
        )
        future.add_done_callback(lambda f: self._handle_transcription(f, start_time))

    def _handle_transcription(self, future, start_time: float = 0.0):
        try:
            text = future.result()
            if start_time:
                latency = time.time() - start_time
                self._latency_stats["transcription"].append(latency)
                logger.debug(f"Latence transcription: {latency:.3f}s")
        except Exception as e:
            logger.error(f"Erreur transcription: {e}")
            return

        if not text or not text.strip():
            logger.warning("Aucun texte transcrit")
            return

        logger.info(f"Texte transcrit: {text}")

        if self._on_transcription_ready:
            self._on_transcription_ready(text)

    def optimize_performance(self, aggressive: bool = False) -> bool:
        """Optimise les performances du pipeline"""
        try:
            if hasattr(self.speech_recognition_service, "optimize_model_cache"):
                self.speech_recognition_service.optimize_model_cache()
            if hasattr(self.tts_service, "optimize_voice_cache"):
                self.tts_service.optimize_voice_cache()
            
            if aggressive:
                self._chunk_size = 512
                self._audio_queue = queue.Queue(maxsize=2)
                logger.info("Mode agressif activé: chunk_size=512, buffer=2")
            
            return True
        except Exception as e:
            logger.error(f"Erreur optimisation: {e}")
            return False

    def get_latency_stats(self) -> Dict[str, float]:
        """Retourne les statistiques de latence"""
        stats = {}
        for key, values in self._latency_stats.items():
            if values:
                stats[f"{key}_avg"] = sum(values) / len(values)
                stats[f"{key}_min"] = min(values)
                stats[f"{key}_max"] = max(values)
        return stats
