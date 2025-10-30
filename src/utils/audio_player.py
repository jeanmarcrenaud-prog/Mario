import pyaudio
import numpy as np
import threading
import time
import math
from contextlib import contextmanager
from typing import Optional
from ..config import config
from ..utils.logger import logger


class AudioPlayer:
    """Gère la lecture audio et les sons système de manière centralisée."""

    def __init__(self):
        self._pyaudio_instance = None
        self._lock = threading.Lock()
        self._is_playing = threading.Event()  # Initialisé à False
        self._initialize_audio()

    # ---------------------------------------------------------------------
    # Initialisation & nettoyage
    # ---------------------------------------------------------------------
    def _initialize_audio(self):
        """Initialise l'instance PyAudio avec gestion d'erreurs."""
        try:
            self._pyaudio_instance = pyaudio.PyAudio()
            logger.debug("AudioPlayer : PyAudio initialisé.")
        except Exception as e:
            logger.error(f"Échec initialisation PyAudio : {e}")
            self._pyaudio_instance = None

    def cleanup(self):
        """Ferme proprement PyAudio."""
        with self._lock:
            if self._pyaudio_instance:
                try:
                    self._pyaudio_instance.terminate()
                    logger.debug("AudioPlayer : PyAudio terminé proprement.")
                except Exception as e:
                    logger.warning(f"Erreur nettoyage audio: {e}")
                finally:
                    self._pyaudio_instance = None

    @contextmanager
    def _safe_stream(self, **kwargs):
        """Context manager pour ouvrir un flux audio en toute sécurité."""
        if not self._pyaudio_instance:
            self._initialize_audio()
        stream = None
        try:
            stream = self._pyaudio_instance.open(**kwargs)
            yield stream
        except Exception as e:
            logger.error(f"Erreur ouverture flux audio : {e}")
            yield None
        finally:
            if stream:
                try:
                    stream.stop_stream()
                    stream.close()
                except Exception as e:
                    logger.warning(f"Erreur fermeture flux audio : {e}")

    # ---------------------------------------------------------------------
    # État
    # ---------------------------------------------------------------------
    @property
    def is_playing(self) -> bool:
        """Retourne True si un son est en cours de lecture."""
        return self._is_playing.is_set()

    # ---------------------------------------------------------------------
    # Lecture audio
    # ---------------------------------------------------------------------
    def play_audio(self, audio_data: np.ndarray, samplerate: Optional[int] = None):
        def _play_thread():
            try:
                with self._lock:
                    rate = samplerate or getattr(config, "SAMPLERATE", 44100)
                    with self._safe_stream(
                        format=pyaudio.paInt16,
                        channels=1,
                        rate=rate,
                        output=True,
                    ) as stream:
                        if not stream:
                            logger.warning("Impossible de jouer l'audio : flux non disponible.")
                            return
                        self._is_playing.set()
                        stream.write(audio_data.tobytes())
                        self._is_playing.clear()
            except Exception as e:
                self._is_playing.clear()
                logger.error(f"Erreur lecture audio : {e}")
        threading.Thread(target=_play_thread, daemon=True).start()


    # ---------------------------------------------------------------------
    # Bip simple
    # ---------------------------------------------------------------------

    def play_beep(self, frequency: int = 1200, duration: float = 0.25, volume: float = 0.3):
        try:
            samplerate = 44100
            t = np.linspace(0, duration, int(samplerate * duration), False)
            beep = volume * np.sin(2 * np.pi * frequency * t)
            audio_data = (beep * 32767).astype(np.int16)
            with self._lock:
                with self._safe_stream(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=samplerate,
                    output=True,
                ) as stream:
                    if not stream:
                        logger.warning("Impossible de jouer le bip : flux non disponible.")
                        return
                    self._is_playing.set()
                    stream.write(audio_data.tobytes())
                    time.sleep(duration)
                    self._is_playing.clear()
        except Exception as e:
            self._is_playing.clear()
            logger.warning(f"Impossible de jouer le bip: {e}")
           
    def play_confirmation_beep(self):
        self.play_beep(frequency=880, duration=0.15, volume=0.4)

    def play_error_beep(self):
        self.play_beep(frequency=220, duration=0.25, volume=0.5)
