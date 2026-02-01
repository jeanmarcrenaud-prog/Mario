# src/interfaces/microphone_checker.py
"""
MicrophoneChecker – utilitaire de vérification de l’entrée audio.

Fonctionnalités
---------------
* Vérifie que le périphérique d’entrée existe.
* Retourne la liste des périphériques disponibles.
* Permet de tester la capture audio en temps réel.
"""

import logging
import pyaudio

logger = logging.getLogger(__name__)

class MicrophoneChecker:
    """
    Vérifie la disponibilité et la qualité d’un microphone.
    """

    def __init__(self, index: int = 0, sample_rate: int = 16000, chunk_size: int = 1024):
        """
        Parameters
        ----------
        index : int
            Index du périphérique d’entrée (0 par défaut).
        sample_rate : int
            Fréquence d’échantillonnage (ex. 16000 Hz).
        chunk_size : int
            Taille du chunk audio (en échantillons).
        """
        self.index = index
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.pyaudio_instance = pyaudio.PyAudio()

    # ------------------------------------------------------------------
    # 1️⃣  Liste des périphériques
    # ------------------------------------------------------------------
    def list_devices(self) -> list[dict]:
        """Retourne la liste des périphériques d’entrée audio."""
        devices = []
        for i in range(self.pyaudio_instance.get_device_count()):
            info = self.pyaudio_instance.get_device_info_by_index(i)
            if info.get("maxInputChannels", 0) > 0:
                devices.append(
                    {
                        "index": i,
                        "name": info.get("name"),
                        "max_input_channels": info.get("maxInputChannels"),
                        "default_sample_rate": info.get("defaultSampleRate"),
                    }
                )
        return devices

    # ------------------------------------------------------------------
    # 2️⃣  Vérification d’un périphérique
    # ------------------------------------------------------------------
    def is_device_available(self) -> bool:
        """Vérifie que le périphérique d’entrée existe et est utilisable."""
        try:
            stream = self.pyaudio_instance.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                input_device_index=self.index,
                frames_per_buffer=self.chunk_size,
            )
            stream.close()
            return True
        except Exception as e:
            logger.warning(f"Microphone non disponible (index={self.index}): {e}")
            return False

    # ------------------------------------------------------------------
    # 3️⃣  Test de capture en temps réel
    # ------------------------------------------------------------------
    def test_capture(self, duration: float = 3.0) -> bool:
        """
        Capture un court clip audio pour vérifier la qualité.

        Parameters
        ----------
        duration : float
            Durée en secondes.

        Returns
        -------
        bool
            True si la capture a réussi, False sinon.
        """
        try:
            stream = self.pyaudio_instance.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                input_device_index=self.index,
                frames_per_buffer=self.chunk_size,
            )
            frames = []
            for _ in range(int(self.sample_rate / self.chunk_size * duration)):
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                frames.append(data)
            stream.stop_stream()
            stream.close()
            # Si on a bien reçu des frames, on considère que le test a réussi
            return len(frames) > 0
        except Exception as e:
            logger.error(f"Erreur lors du test de capture : {e}")
            return False

    # ------------------------------------------------------------------
    # 4️⃣  Nettoyage
    # ------------------------------------------------------------------
    def close(self):
        """Ferme l’instance PyAudio."""
        self.pyaudio_instance.terminate()

    # ------------------------------------------------------------------
    # 5️⃣  Contexte (facultatif)
    # ------------------------------------------------------------------
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
