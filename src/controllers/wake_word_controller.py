import os
import numpy as np
import torch
import pyaudio
import collections
import threading
import time
from typing import Optional, Callable
from pvrecorder import PvRecorder
#from ..config import config
from src.model.config_manager import ConfigManager
from ..utils.logger import logger


class WakeWordController:
    def __init__(self):
        self.porcupine = None
        self.vad_model = None
        self.vad_utils = None
        self.is_listening = False
        self.listening_thread = None
        self.wake_word_callback: Optional[Callable] = None
        self.audio_callback: Optional[Callable] = None
        self.recorder = None
        self.energy_threshold = 1000
        self.sample_rate = 16000

    # ------------------------------------------------------------
    # Initialisation Silero-VAD
    # ------------------------------------------------------------
    def initialize_vad(self):
        """Initialise le modèle Silero-VAD (remplacement de WebRTC-VAD)."""
        try:
            self.vad_model, self.vad_utils = torch.hub.load(
                repo_or_dir="snakers4/silero-vad",
                model="silero_vad",
                force_reload=False
            )
            self.vad_model.eval()
            logger.info("[OK] Silero-VAD initialisé avec succès")
            return True
        except Exception as e:
            logger.error("[ERREUR] Impossible d'initialiser Silero-VAD: %s", e)
            return False

    # ------------------------------------------------------------
    # Initialisation Porcupine
    # ------------------------------------------------------------
    def initialize_porcupine(self) -> bool:
        """Initialise le détecteur Porcupine avec vérifications."""
        try:
            from pvporcupine import Porcupine

            required_files = [
                ConfigManager.PORCUPINE_MODEL_PATH,
                ConfigManager.PORCUPINE_KEYWORD_PATH,
                ConfigManager.PORCUPINE_LIBRARY_PATH,
            ]

            for file_path in required_files:
                if not os.path.exists(file_path):
                    logger.error("[ERREUR] Fichier Porcupine manquant: %s", file_path)
                    return False

            if not ConfigManager.PORCUPINE_ACCESS_KEY:
                logger.error("[ERREUR] Clé d'accès Porcupine manquante")
                return False

            self.porcupine = Porcupine(
                access_key=ConfigManager.PORCUPINE_ACCESS_KEY,
                library_path=ConfigManager.PORCUPINE_LIBRARY_PATH,
                model_path=ConfigManager.PORCUPINE_MODEL_PATH,
                keyword_paths=[ConfigManager.PORCUPINE_KEYWORD_PATH],
                sensitivities=[ConfigManager.PORCUPINE_SENSITIVITY],
            )

            logger.info("[OK] Porcupine initialisé avec succès")
            return True

        except ImportError:
            logger.error("[ERREUR] Bibliothèque Porcupine non installée")
            return False
        except Exception as e:
            logger.error("[ERREUR] Erreur d'initialisation Porcupine: %s", e)
            return False

    # ------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------
    def set_wake_word_callback(self, callback: Callable):
        """Définit la fonction à appeler lors de la détection du mot-clé."""
        self.wake_word_callback = callback

    def set_audio_callback(self, callback: Callable):
        """Définit la fonction à appeler avec l'audio capturé."""
        self.audio_callback = callback

    # ------------------------------------------------------------
    # Utilitaires audio
    # ------------------------------------------------------------
    def _play_beep(self, frequency: int = 800, duration: float = 0.2):
        """Joue un bip de confirmation."""
        try:
            sample_rate = 44100
            samples = int(sample_rate * duration)
            t = np.linspace(0, duration, samples, False)
            beep = 0.3 * np.sin(2 * np.pi * frequency * t)
            audio_data = (beep * 32767).astype(np.int16)

            p = pyaudio.PyAudio()
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=sample_rate,
                output=True,
            )
            stream.write(audio_data.tobytes())
            stream.stop_stream()
            stream.close()
            p.terminate()
        except Exception as e:
            logger.warning("[ATTENTION] Impossible de jouer le bip: %s", e)

    def _calculate_energy(self, audio_data: np.ndarray) -> float:
        """Calcule l'énergie du signal audio."""
        if audio_data.size == 0:
            return 0.0
        return float(np.sqrt(np.mean(audio_data.astype(np.float64) ** 2)))

    # ------------------------------------------------------------
    # Gestion d'écoute
    # ------------------------------------------------------------
    def start_listening(self, mic_index: int = 0):
        """Démarre l'écoute du mot-clé dans un thread séparé."""
        if self.is_listening:
            logger.warning("[ATTENTION] L'écoute est déjà en cours")
            return

        if not self.porcupine and not self.initialize_porcupine():
            logger.error("[ERREUR] Impossible d'initialiser Porcupine")
            return

        if not self.vad_model and not self.initialize_vad():
            logger.error("[ERREUR] Impossible d'initialiser Silero-VAD")
            return

        self.is_listening = True
        self.listening_thread = threading.Thread(
            target=self._listening_loop, args=(mic_index,), daemon=True
        )
        self.listening_thread.start()
        logger.info("[ECOUTE] Écoute démarrée sur microphone %d", mic_index)

    def _is_speech_silero(self, audio_chunk: np.ndarray) -> bool:
        """Utilise Silero-VAD pour déterminer si un chunk contient de la parole."""
        try:
            from torch import tensor

            audio_float = audio_chunk.astype(np.float32) / 32768.0
            audio_tensor = tensor(audio_float)
            is_speech = self.vad_model(audio_tensor, self.sample_rate).item() > 0.5
            return bool(is_speech)
        except Exception as e:
            logger.debug("[VAD] Erreur détection parole: %s", e)
            return False

    def _listening_loop(self, mic_index: int):
        """Boucle principale d'écoute."""
        try:
            self.recorder = PvRecorder(
                device_index=mic_index, frame_length=self.porcupine.frame_length
            )
            self.recorder.start()

            audio_buffer = collections.deque(maxlen=self.sample_rate * 10)

            logger.info("[AUDIO] Boucle d'écoute active...")

            while self.is_listening:
                pcm = self.recorder.read()
                audio_chunk = np.array(pcm, dtype=np.int16)
                audio_buffer.extend(audio_chunk)

                # Détection mot-clé
                keyword_index = self.porcupine.process(pcm)
                if keyword_index >= 0:
                    logger.info("[ALERTE] Mot-clé détecté!")
                    self._play_beep()

                    if self.wake_word_callback:
                        self.wake_word_callback()

                    self._capture_speech(mic_index, audio_buffer)
                    audio_buffer.clear()

        except Exception as e:
            logger.error("[ERREUR] Erreur dans la boucle d'écoute: %s", e)
        finally:
            if self.recorder:
                self.recorder.stop()
                self.recorder.delete()
            logger.info("[ARRET] Boucle d'écoute arrêtée")

    # ------------------------------------------------------------
    # Capture audio après détection
    # ------------------------------------------------------------
    def _capture_speech(self, mic_index: int, initial_buffer: collections.deque):
        """Capture la parole après détection du mot-clé."""
        try:
            if not self.audio_callback:
                return

            audio_buffer = collections.deque(initial_buffer, maxlen=self.sample_rate * 5)
            silence_frames = 0
            max_silence_frames = 50

            logger.info("[MICRO] Capture de la parole en cours...")

            for _ in range(500):  # ~5 secondes max
                if not self.is_listening:
                    break

                pcm = self.recorder.read()
                audio_chunk = np.array(pcm, dtype=np.int16)
                audio_buffer.extend(audio_chunk)

                if self._is_speech_silero(audio_chunk):
                    silence_frames = 0
                else:
                    silence_frames += 1

                if silence_frames >= max_silence_frames:
                    logger.info("[SILENCE] Fin de phrase détectée")
                    break

            if len(audio_buffer) > self.sample_rate:
                audio_data = np.array(list(audio_buffer))
                logger.info("[FICHIER] Audio capturé: %d échantillons", len(audio_data))
                self.audio_callback(audio_data)
            else:
                logger.warning("[ATTENTION] Audio capturé trop court")

        except Exception as e:
            logger.error("[ERREUR] Erreur lors de la capture: %s", e)

    # ------------------------------------------------------------
    # Arrêt & nettoyage
    # ------------------------------------------------------------
    def stop_listening(self):
        """Arrête l'écoute proprement."""
        if not self.is_listening:
            return
        self.is_listening = False
        if self.recorder:
            self.recorder.stop()
        if self.listening_thread and self.listening_thread.is_alive():
            self.listening_thread.join(timeout=2.0)
        logger.info("[ARRET] Détection mot-clé arrêtée")

    def get_audio_devices(self) -> list:
        """Retourne la liste des périphériques audio disponibles."""
        try:
            devices = PvRecorder.get_audio_devices()
            return [(idx, device) for idx, device in enumerate(devices)]
        except Exception as e:
            logger.error("[ERREUR] Erreur liste périphériques: %s", e)
            return []

    def cleanup(self):
        """Nettoie toutes les ressources."""
        self.stop_listening()
        if self.porcupine:
            self.porcupine.delete()
        logger.info("[NETTOYAGE] Ressources wake-word nettoyées")
