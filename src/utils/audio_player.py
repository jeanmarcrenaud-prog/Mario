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
    """Gère la lecture audio et les sons système de manière centralisée.

    Cette classe encapsule l'accès à PyAudio pour éviter les conflits entre threads
    et garantir la bonne fermeture des ressources.
    """

    def __init__(self):
        self._pyaudio_instance = None
        self._lock = threading.Lock()
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
    # Lecture audio
    # ---------------------------------------------------------------------
    def play_audio(self, audio_data: np.ndarray, samplerate: Optional[int] = None):
        """Lit un buffer audio numpy en arrière-plan.

        Args:
            audio_data (np.ndarray): Données audio au format PCM 16 bits.
            samplerate (int, optional): Fréquence d’échantillonnage. Si None, utilise config.SAMPLERATE.
        """
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
                        if stream:
                            stream.write(audio_data.tobytes())
                        else:
                            logger.warning("Impossible de jouer l'audio : flux non disponible.")
            except Exception as e:
                logger.error(f"Erreur lecture audio : {e}")

        threading.Thread(target=_play_thread, daemon=True).start()

    # ---------------------------------------------------------------------
    # Génération de sons simples
    # ---------------------------------------------------------------------
    def play_beep(self, frequency: int = 1200, duration: float = 0.25, volume: float = 0.3):
        """Joue un bip sonore simple.

        Args:
            frequency (int): Fréquence en Hz.
            duration (float): Durée en secondes.
            volume (float): Volume de 0.0 à 1.0.
        """
        try:
            samplerate = 44100
            t = np.linspace(0, duration, int(samplerate * duration), False)
            beep = volume * np.sin(2 * math.pi * frequency * t)
            audio_data = (beep * 32767).astype(np.int16)

            with self._lock:
                with self._safe_stream(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=samplerate,
                    output=True,
                ) as stream:
                    if stream:
                        stream.write(audio_data.tobytes())
                        time.sleep(0.05)
        except Exception as e:
            logger.warning(f"Impossible de jouer le bip: {e}")
