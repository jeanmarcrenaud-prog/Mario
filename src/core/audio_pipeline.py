# ────────────────────────────────────────────────────────────────────────
# audio_pipeline.py
# Pipeline audio pour l'assistant vocal Mario
# Gère: wake-word detection, transcription speech-to-text, synthèse TTS
# ────────────────────────────────────────────────────────────────────────

import numpy as np
import queue
import threading
import time
from typing import Callable, Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor, Future
from collections import deque

from src.utils.logger import logger


# Configuration constante pour le pipeline audio
AUDIO_CONFIG = {
    "DEFAULT_CHUNK_SIZE": 2048,
    "LOW_LATENCY_DIVISOR": 2,
    "TRANSCRIBE_WORKERS": 2,
    "TTS_WORKERS": 1,
    "SPEAK_TIMEOUT_SECONDS": 30,
    "AGGRESSIVE_CHUNK_SIZE": 512,
    "MIN_AUDIO_BUFFER": 2,
    "MAX_STATS_SAMPLE_SIZE": 1000,
}


class AudioPipeline:
    """
    Gère le pipeline audio: wake-word detection, transcription speech-to-text, synthèse TTS.

    Architecture threading:
    - Thread principal gère les callbacks du service wake-word
    - ThreadPoolExecutor gère les tâches de transcription (2 workers)
    - Separate ThreadPoolExecutor gère les tâches TTS (1 worker)
    - Les données audio transitent par une queue bornée

    Sécurité threads:
    - Utilise threading.Event pour la gestion d'état (_running_event)
    - Les callbacks sont isolés pour empêcher les bugs consommateurs de crasher le pipeline
    - La queue est vidée à l'arrêt pour éviter les fuites de ressources

    Gestion erreurs:
    - Tous les appels de service externe enveloppés dans try-except
    - Les callbacks utilisateurs protégés avec des handlers d'exceptions individuels
    - Dégradation élégante en cas d'échec de service

    Exemple d'utilisation:
        pipeline = AudioPipeline(
            wake_word_service=MyWakeWord(),
            speech_recognition_service=STTService(),
            tts_service=TTSVoice(),
            settings=config
        )
        pipeline.set_transcription_callback(on_transcribed)
        pipeline.start()

        # ... plus tard ...
        pipeline.stop()
    """

    def __init__(
        self,
        wake_word_service: Any,
        speech_recognition_service: Any,
        tts_service: Any,
        settings: Any,
    ):
        """Initialise le pipeline audio avec validation des dépendances."""
        # Validation des dépendances requises
        if wake_word_service is None:
            raise ValueError("wake_word_service est requis")
        if speech_recognition_service is None:
            raise ValueError("speech_recognition_service est requis")
        if tts_service is None:
            raise ValueError("tts_service est requis")
        if settings is None:
            raise ValueError("settings est requis")

        # Vérification des méthodes requises (duck typing)
        self._validate_services(wake_word_service, speech_recognition_service, tts_service)

        self.wake_word_service = wake_word_service
        self.speech_recognition_service = speech_recognition_service
        self.tts_service = tts_service
        self.settings = settings

        # Flag thread-safe pour l'état du pipeline (remplace _is_running booléen)
        self._running_event: threading.Event = threading.Event()

        # Queue audio bornée pour éviter les fuites mémoire
        self._audio_queue: queue.Queue[np.ndarray] = queue.Queue(
            maxsize=settings.audio_buffer_size or AUDIO_CONFIG["MIN_AUDIO_BUFFER"]
        )

        # Taille du chunk (peut être modifiée par optimize_performance)
        chunk_size = settings.chunk_size // AUDIO_CONFIG["LOW_LATENCY_DIVISOR"] \
            if hasattr(settings, 'enable_low_latency') and settings.enable_low_latency \
            else settings.chunk_size
        self._chunk_size: int = chunk_size

        # Executors asynchrones pour transcription et TTS
        self._transcribe_executor: ThreadPoolExecutor = ThreadPoolExecutor(
            max_workers=AUDIO_CONFIG["TRANSCRIBE_WORKERS"]
        )
        self._tts_executor: ThreadPoolExecutor = ThreadPoolExecutor(
            max_workers=AUDIO_CONFIG["TTS_WORKERS"]
        )

        # Callbacks utilisateur (isolés contre les exceptions)
        self._on_transcription_ready: Optional[Callable[[str], None]] = None
        self._on_wake_word_detected: Optional[Callable[[], None]] = None

        # Statistiques de latence avec deque borné pour éviter fuite mémoire
        self._latency_stats: Dict[str, deque[float]] = {
            "transcription": deque(maxlen=AUDIO_CONFIG["MAX_STATS_SAMPLE_SIZE"]),
            "tts": deque(maxlen=AUDIO_CONFIG["MAX_STATS_SAMPLE_SIZE"]),
            "wake_word": deque(maxlen=AUDIO_CONFIG["MAX_STATS_SAMPLE_SIZE"]),
        }

    def _validate_services(
        self,
        wake_word_service: Any,
        speech_recognition_service: Any,
        tts_service: Any,
    ) -> None:
        """Valide que les services ont les méthodes requises."""
        wake_word_methods = ["set_wake_word_callback", "start_detection"]
        for method in wake_word_methods:
            if not hasattr(wake_word_service, method):
                logger.warning(f"Le service WakeWord n'a pas la méthode: {method}")

    def start(self) -> bool:
        """Démarre le pipeline audio."""
        if self._running_event.is_set():
            logger.warning("Pipeline déjà en cours d'exécution")
            return False

        try:
            self._running_event.set()

            # Appliquer la configuration du chunk_size si modifiée par optimize_performance
            chunk_size = self._chunk_size

            # Configurer les callbacks pour le service wake-word
            self.wake_word_service.set_wake_word_callback(self._on_wake_word_detected_fn)
            self.wake_word_service.set_audio_callback(self._on_audio_received_fn)
            self.wake_word_service.start_detection(self.settings.microphone_index)

            logger.info("AudioPipeline démarré")
            return True

        except Exception as e:
            logger.error(f"Erreur démarrage AudioPipeline: {e}")
            self._running_event.clear()
            return False

    def stop(self) -> bool:
        """Arrête le pipeline audio proprement."""
        if not self._running_event.is_set():
            logger.warning("Pipeline déjà arrêté")
            return False

        try:
            # Marquer comme non en cours d'exécution avant de nettoyer
            self._running_event.clear()

            # Vider la queue audio pour éviter les fuites de ressources
            while not self._audio_queue.empty():
                try:
                    self._audio_queue.get_nowait()
                except queue.Empty:
                    break

            # Arrêter le service wake-word
            if hasattr(self.wake_word_service, 'stop_detection'):
                self.wake_word_service.stop_detection()

            # Fermer les executors proprement
            # Cancel les futures en attente pour éviter blocage
            self._transcribe_executor.shutdown(wait=True, cancel_futures=True)
            self._tts_executor.shutdown(wait=False)  # TTS peut être interrompu

            logger.info("AudioPipeline arrêté")
            return True

        except Exception as e:
            logger.error(f"Erreur arrêt AudioPipeline: {e}")
            return False

    def set_transcription_callback(self, callback: Callable[[str], None]) -> None:
        """Définit le callback appelé quand la transcription est prête."""
        self._on_transcription_ready = callback

    def set_wake_word_callback(self, callback: Callable[[], None]) -> None:
        """Définit le callback appelé quand le wake-word est détecté."""
        self._on_wake_word_detected = callback

    def speak(self, text: str) -> Optional[Future]:
        """
        Synthétise et joue le texte (mode non-blocant).

        Args:
            text: Texte à synthétiser

        Returns:
            Future object qui peut être utilisé pour attendre la fin du TTS,
            ou None si l'échec immédiat (texte vide)

        Note:
            Cette méthode retourne immédiatement. Utiliser .result() sur le
            return value pour attendre si nécessaire.
        """
        if not text or not text.strip():
            logger.warning("Texte vide pour synthèse vocale")
            return None

        try:
            # Soumettre à l'executor sans bloquer - retourne Future immédiatement
            future = self._tts_executor.submit(
                self.tts_service.say, text, self.settings.speech_speed
            )

            # Ajouter callback pour mesurer la latence une fois terminé
            def log_latency(fut: Future) -> None:
                try:
                    start_time = getattr(fut, '_start_time', time.time())
                    latency = time.time() - start_time
                    self._latency_stats["tts"].append(latency)

                    # Log seulement si succès pour réduire bruit
                    if fut.result():  # Vérifier le retour du service TTS
                        logger.debug(f"Latence TTS: {latency:.3f}s")
                except Exception as e:
                    logger.debug(f"Détail latence TTS: {e}")

            future.add_done_callback(log_latency)
            return future

        except Exception as e:
            logger.error(f"Erreur dans speak(): {e}")
            return None

    def _on_wake_word_detected_fn(self) -> None:
        """Callback appelé quand le mot-clé de réveil est détecté."""
        try:
            self._running_event.wait(timeout=0.5)  # Vérifier que le pipeline est actif
            if not self._running_event.is_set():
                return

            logger.info("🎯 Mot d'éveil détecté!")

            # Appeler le callback utilisateur protégé contre les exceptions
            if self._on_wake_word_detected:
                try:
                    self._on_wake_word_detected()
                except Exception as e:
                    logger.error(f"Exception dans wake-word callback: {e}")
                    # Ne pas propager - protéger le pipeline des bugs utilisateurs

        except Exception as e:
            logger.error(f"Erreur dans _on_wake_word_detected_fn: {e}")

    def _on_audio_received_fn(self, audio_data: bytes) -> None:
        """Callback appelé quand des données audio sont reçues du microphone."""
        try:
            start_time = time.time()
            # Réduire la verbosité : log en DEBUG au lieu d'INFO
            logger.debug(f"Données audio reçues ({len(audio_data)} octets)")

            # Convertir les données audio brutes en tableau float32 normalisé
            audio_np = self._convert_audio_to_float(audio_data)

            # Soumettre à l'executor de transcription sans bloquer
            future = self._transcribe_executor.submit(
                self.speech_recognition_service.transcribe, audio_np, "fr"
            )
            future.add_done_callback(lambda f: self._handle_transcription(f, start_time))

        except Exception as e:
            logger.error(f"Erreur dans _on_audio_received_fn: {e}")

    def _convert_audio_to_float(self, audio_data: bytes) -> np.ndarray:
        """
        Convertit des données PCM 16-bit en tableau float32 normalisé.

        Args:
            audio_data: Données audio brutes en format int16

        Returns:
            Tableau numpy float32 avec valeurs entre -1.0 et 1.0
        """
        return np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

    def _handle_transcription(self, future: Future, start_time: float = 0.0) -> None:
        """
        Gère le résultat de la transcription avec isolation des callbacks.

        Args:
            future: Future object retourné par l'executor de transcription
            start_time: Timestamp pour calculer latence (optionnel)
        """
        try:
            # Obtenir le résultat avec timeout pour éviter blocage infini
            text = future.result(timeout=60)

            # Calculer et stocker la latence si timestamp fourni
            if start_time > 0:
                latency = time.time() - start_time
                self._latency_stats["transcription"].append(latency)
                logger.debug(f"Latence transcription: {latency:.3f}s")

        except queue.Empty:
            # Cas rare mais possible si future est annulé avant complétion
            logger.warning("Transcription annulée (queue.Empty)")
            return

        except Exception as e:
            logger.error(f"Erreur de transcription: {e}")
            return

        # Vérifier que le texte n'est pas vide
        if not text or not text.strip():
            # Réduire la verbosité : log en DEBUG au lieu d'WARNING
            logger.debug("Aucun texte transcrit")
            return

        logger.info(f"Texte transcrit: {text}")

        # Appeler le callback utilisateur protégé contre les exceptions
        if self._on_transcription_ready:
            try:
                self._on_transcription_ready(text)
            except Exception as e:
                logger.error(f"Exception dans transcription callback: {e}")
                # Ne pas propager - protéger le pipeline des bugs utilisateurs

    def optimize_performance(self, aggressive: bool = False) -> bool:
        """
        Optimise les performances du pipeline.

        Note:
            Nécessite un redémarrage du pipeline pour prendre effet complet.
            L'optimisation est bloquée si le pipeline est actif.

        Args:
            aggressive: Si True, réduit la taille des buffers (latence plus faible)

        Returns:
            True si l'optimisation réussie, False sinon
        """
        # Empêcher l'optimisation pendant l'exécution (race condition protection)
        if self._running_event.is_set():
            logger.warning("Optimisation des performances requiert un arrêt du pipeline")
            return False

        try:
            # Optimiser les services sous-jacents si les méthodes existent
            if hasattr(self.speech_recognition_service, "optimize_model_cache"):
                self.speech_recognition_service.optimize_model_cache()

            if hasattr(self.tts_service, "optimize_voice_cache"):
                self.tts_service.optimize_voice_cache()

            # Mode agressif pour latence réduite (chunk_size plus petit)
            if aggressive:
                old_chunk = self._chunk_size
                self._chunk_size = AUDIO_CONFIG["AGGRESSIVE_CHUNK_SIZE"]

                logger.info(
                    f"Mode agressif activé: "
                    f"chunk_size {old_chunk} -> {self._chunk_size}"
                )

            return True

        except Exception as e:
            logger.error(f"Erreur lors de l'optimisation des performances: {e}")
            return False

    def get_latency_stats(self) -> Dict[str, float]:
        """
        Retourne les statistiques de latence (moyenne/min/max par métrique).

        Returns:
            Dictionnaire avec clés: <type>_avg, <type>_min, <type>_max
            où type ∈ {transcription, tts, wake_word}
        """
        stats: Dict[str, float] = {}

        for key, values in self._latency_stats.items():
            if values:  # Vérifier que la deque n'est pas vide
                stats[f"{key}_avg"] = sum(values) / len(values)
                stats[f"{key}_min"] = min(values)
                stats[f"{key}_max"] = max(values)

        return stats

    def get_status(self) -> Dict[str, Any]:
        """Retourne l'état actuel du pipeline."""
        return {
            "running": self._running_event.is_set(),
            "chunk_size": self._chunk_size,
            "queue_size": self._audio_queue.qsize() if not self._audio_queue.empty() else 0,
            "transcription_stats": self.get_latency_stats().get("transcription_avg", 0),
            "tts_stats": self.get_latency_stats().get("tts_avg", 0),
        }
