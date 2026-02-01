# src/services/wake_word_service.py
"""
Wake‑word detection service.

- Utilise Vosk pour la reconnaissance en temps réel.
- Expose deux callbacks :
    * `wake_word_callback` – appelé dès que le mot‑clé est détecté.
    * `audio_callback`     – appelé avec le chunk audio capturé.
- Le service tourne dans un thread séparé pour ne pas bloquer le reste de l’application.
"""

import queue
import threading
import time
import logging
from typing import Callable, Optional

import pyaudio
from vosk import Model, KaldiRecognizer

logger = logging.getLogger(__name__)

class WakeWordService:
    """
    Wake‑word detection service.

    Parameters
    ----------
    wake_word : str
        Mot‑clé à détecter (ex. "mario").
    model_path : str
        Chemin vers le modèle Vosk (ex. "vosk-model-small-fr-0.22").
    sample_rate : int, default 16000
        Fréquence d’échantillonnage du microphone.
    chunk_size : int, default 4000
        Taille du chunk audio (en échantillons) envoyé au recognizer.
    """

    def __init__(
        self,
        wake_word: str = "mario",
        model_path: str = "vosk-model-small-fr-0.22",
        sample_rate: int = 16000,
        chunk_size: int = 4000,
    ):
        self.wake_word = wake_word.lower()
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size

        # Callbacks – à définir par l’utilisateur
        self._wake_word_callback: Optional[Callable[[], None]] = None
        self._audio_callback: Optional[Callable[[bytes], None]] = None

        # Threading
        self._running = False
        self._thread: Optional[threading.Thread] = None

        # Vosk
        try:
            self.model = Model(model_path)
            self.recognizer = KaldiRecognizer(self.model, self.sample_rate)
        except Exception as e:
            logger.exception(f"Impossible de charger le modèle Vosk ({model_path}): {e}")
            raise

        # PyAudio
        self.pyaudio_instance = pyaudio.PyAudio()
        self.stream = None

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------
    def set_wake_word_callback(self, callback: Callable[[], None]) -> None:
        """Définit la fonction appelée quand le mot‑clé est détecté."""
        self._wake_word_callback = callback

    def set_audio_callback(self, callback: Callable[[bytes], None]) -> None:
        """Définit la fonction appelée avec le chunk audio capturé."""
        self._audio_callback = callback

    # ------------------------------------------------------------------
    # Démarrage / arrêt
    # ------------------------------------------------------------------
    def start_detection(self, microphone_index: int = 0) -> None:
        """Démarre la détection en arrière‑plan."""
        if self._running:
            logger.warning("WakeWordService déjà en cours d’exécution")
            return

        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        logger.info("WakeWordService démarré")

    def stop_detection(self) -> None:
        """Arrête la détection."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.pyaudio_instance.terminate()
        logger.info("WakeWordService arrêté")

    # ------------------------------------------------------------------
    # Boucle principale
    # ------------------------------------------------------------------
    def _run(self) -> None:
        """Boucle de capture audio et de reconnaissance."""
        try:
            self.stream = self.pyaudio_instance.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
            )
        except Exception as e:
            logger.exception(f"Impossible d’ouvrir le microphone: {e}")
            self._running = False
            return

        while self._running:
            try:
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                if self._audio_callback:
                    # On transmet le chunk brut (bytes) au callback
                    self._audio_callback(data)

                if self.recognizer.AcceptWaveform(data):
                    result = self.recognizer.Result()
                    # Le résultat est un JSON; on ne s’intéresse qu’au champ "text"
                    import json

                    text = json.loads(result).get("text", "").lower()
                    if self.wake_word in text:
                        logger.info(f"Mot‑clé détecté : '{self.wake_word}'")
                        if self._wake_word_callback:
                            self._wake_word_callback()
            except Exception as e:
                logger.exception(f"Erreur dans la boucle de détection : {e}")
                time.sleep(0.1)  # éviter un loop trop rapide en cas d’erreur

    # ------------------------------------------------------------------
    # Contexte (facultatif)
    # ------------------------------------------------------------------
    def __enter__(self):
        self.start_detection()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_detection()
