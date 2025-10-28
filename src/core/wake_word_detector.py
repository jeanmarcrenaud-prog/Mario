import os
import numpy as np
import webrtcvad
import pyaudio
import collections
import threading
import time
from typing import Optional, Callable
from pvrecorder import PvRecorder
from ..config import config
from ..utils.logger import logger

class WakeWordDetector:
    def __init__(self):
        self.porcupine = None
        self.vad = webrtcvad.Vad(config.VAD_AGGRESSIVENESS)
        self.is_listening = False
        self.listening_thread = None
        self.wake_word_callback: Optional[Callable] = None
        self.audio_callback: Optional[Callable] = None
        self.recorder = None
        self.energy_threshold = 1000
        
    def initialize_porcupine(self) -> bool:
        """Initialise le détecteur Porcupine avec vérifications."""
        try:
            from pvporcupine import Porcupine
            
            # Vérification des fichiers
            required_files = [
                config.PORCUPINE_MODEL_PATH,
                config.PORCUPINE_KEYWORD_PATH,
                config.PORCUPINE_LIBRARY_PATH
            ]
            
            for file_path in required_files:
                if not os.path.exists(file_path):
                    logger.error("[ERREUR] Fichier Porcupine manquant: %s", file_path)
                    return False
            
            if not config.PORCUPINE_ACCESS_KEY:
                logger.error("[ERREUR] Clé d'accès Porcupine manquante")
                return False
                
            self.porcupine = Porcupine(
                access_key=config.PORCUPINE_ACCESS_KEY,
                library_path=config.PORCUPINE_LIBRARY_PATH,
                model_path=config.PORCUPINE_MODEL_PATH,
                keyword_paths=[config.PORCUPINE_KEYWORD_PATH],
                sensitivities=[config.PORCUPINE_SENSITIVITY]
            )
            
            logger.info("[OK] Porcupine initialisé avec succès")
            return True
            
        except ImportError:
            logger.error("[ERREUR] Bibliothèque Porcupine non installée")
            return False
        except Exception as e:
            logger.error("[ERREUR] Erreur d'initialisation Porcupine: %s", e)
            return False
    
    def set_wake_word_callback(self, callback: Callable):
        """Définit la fonction à appeler lors de la détection du mot-clé."""
        self.wake_word_callback = callback
    
    def set_audio_callback(self, callback: Callable):
        """Définit la fonction à appeler avec l'audio capturé."""
        self.audio_callback = callback
    
    def _play_beep(self, frequency: int = 800, duration: float = 0.2):
        """Joue un bip de confirmation."""
        try:
            import pyaudio
            import numpy as np
            
            sample_rate = 44100
            samples = int(sample_rate * duration)
            t = np.linspace(0, duration, samples, False)
            
            # Bip simple
            beep = 0.3 * np.sin(2 * np.pi * frequency * t)
            audio_data = (beep * 32767).astype(np.int16)
            
            p = pyaudio.PyAudio()
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=sample_rate,
                output=True
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
        return float(np.sqrt(np.mean(audio_data.astype(np.float64)**2)))

    
    def start_listening(self, mic_index: int = 0):
        """Démarre l'écoute du mot-clé dans un thread séparé."""
        if not self.porcupine:
            if not self.initialize_porcupine():
                logger.error("[ERREUR] Impossible d'initialiser Porcupine")
                return
        
        if self.is_listening:
            logger.warning("[ATTENTION] Écoute déjà en cours")
            return
        
        self.listening_thread = threading.Thread(
            target=self._listening_loop,
            args=(mic_index,),
            daemon=True
        )
        self.is_listening = True
        self.listening_thread.start()
        logger.info("[ECOUTE] Écoute démarrée sur microphone %d", mic_index)
    
    def _listening_loop(self, mic_index: int):
        """Boucle principale d'écoute."""
        try:
            # CORRECTION : Supprimer le paramètre frame_rate qui n'existe pas
            self.recorder = PvRecorder(
                device_index=mic_index,
                frame_length=self.porcupine.frame_length
                # frame_rate=16000  <- Ce paramètre n'existe pas dans PvRecorder
            )
            self.recorder.start()
            
            silence_counter = 0
            speech_detected = False
            audio_buffer = collections.deque(maxlen=16000 * 10)  # 10 secondes
            
            logger.info("[AUDIO] Boucle d'écoute active...")
            
            while self.is_listening:
                pcm = self.recorder.read()
                audio_chunk = np.array(pcm, dtype=np.int16)
                audio_buffer.extend(audio_chunk)
                
                # Détection du mot-clé
                keyword_index = self.porcupine.process(pcm)
                if keyword_index >= 0:
                    logger.info("[ALERTE] Mot-clé détecté!")
                    self._play_beep()
                    
                    if self.wake_word_callback:
                        self.wake_word_callback()
                    
                    # Capture audio après détection
                    self._capture_speech(mic_index, audio_buffer)
                    audio_buffer.clear()
                    silence_counter = 0
                    speech_detected = False
                
                # Détection VAD pour monitoring
                if len(audio_chunk) >= 480:  # 30ms à 16kHz
                    is_speech = self.vad.is_speech(
                        audio_chunk[:480].tobytes(), 
                        16000
                    )
                    
                    if is_speech:
                        speech_detected = True
                        silence_counter = 0
                    elif speech_detected:
                        silence_counter += 1
                    
                    # Log périodique de l'activité
                    if silence_counter % 100 == 0 and silence_counter > 0:
                        energy = self._calculate_energy(audio_chunk)
                        logger.debug("[STATS] Activité audio - Énergie: %.1f", energy)
                        
        except Exception as e:
            logger.error("[ERREUR] Erreur dans la boucle d'écoute: %s", e)
        finally:
            if self.recorder:
                self.recorder.stop()
                self.recorder.delete()
            logger.info("[ARRET] Boucle d'écoute arrêtée")
    
    def _capture_speech(self, mic_index: int, initial_buffer: collections.deque):
        """Capture la parole après détection du mot-clé."""
        try:
            if not self.audio_callback:
                return
            
            audio_buffer = collections.deque(initial_buffer, maxlen=16000 * 5)  # 5 secondes
            silence_frames = 0
            max_silence_frames = 50  # ~1.5 secondes de silence
            
            logger.info("[MICRO] Capture de la parole en cours...")
            
            # Capture pendant 5 secondes maximum ou jusqu'à silence prolongé
            for _ in range(500):  # 5 secondes à 100 FPS
                if not self.is_listening:
                    break
                
                pcm = self.recorder.read()
                audio_chunk = np.array(pcm, dtype=np.int16)
                audio_buffer.extend(audio_chunk)
                
                # Détection VAD pour fin de phrase
                if len(audio_chunk) >= 480:
                    is_speech = self.vad.is_speech(
                        audio_chunk[:480].tobytes(), 
                        16000
                    )
                    
                    if is_speech:
                        silence_frames = 0
                    else:
                        silence_frames += 1
                        
                    if silence_frames >= max_silence_frames:
                        logger.info("[SILENCE] Fin de phrase détectée")
                        break
            
            # Conversion et envoi de l'audio
            if len(audio_buffer) > 16000:  # Au moins 1 seconde d'audio
                audio_data = np.array(list(audio_buffer))
                logger.info("[FICHIER] Audio capturé: %d échantillons", len(audio_data))
                self.audio_callback(audio_data)
            else:
                logger.warning("[ATTENTION] Audio capturé trop court")
                
        except Exception as e:
            logger.error("[ERREUR] Erreur lors de la capture: %s", e)
    
    def stop_listening(self):
        """Arrête l'écoute de manière sécurisée."""
        self.is_listening = False
        if self.recorder:
            self.recorder.stop()
        if self.listening_thread and self.listening_thread.is_alive():
            self.listening_thread.join(timeout=2.0)
        logger.info("[ARRET] Détection mot-clé arrêtée")
    
    def get_audio_devices(self) -> list:
        """Retourne la liste des périphériques audio disponibles."""
        try:
            recorder = PvRecorder.get_audio_devices()
            return [(idx, device) for idx, device in enumerate(recorder)]
        except Exception as e:
            logger.error("[ERREUR] Erreur liste périphériques: %s", e)
            return []
    
    def cleanup(self):
        """Nettoie les ressources."""
        self.stop_listening()
        if self.porcupine:
            self.porcupine.delete()
        logger.info("[NETTOYAGE] Ressources wake-word nettoyées")
