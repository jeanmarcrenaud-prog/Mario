import numpy as np
import pyaudio
import collections
import threading
from typing import Optional, Callable
from pvrecorder import PvRecorder
from ..config.config import ConfigManager
from ..utils.logger import logger

class AudioInputAdapter:
    def __init__(self, config: ConfigManager):
        self.config = config
        self.is_listening = False
        self.recorder = None
        self.listening_thread = None
        self.wake_word_callback: Optional[Callable] = None
        self.audio_callback: Optional[Callable] = None
        self.sample_rate = 16000
    
    def set_wake_word_callback(self, callback: Callable):
        """Définit le callback pour la détection du mot-clé."""
        self.wake_word_callback = callback
    
    def set_audio_callback(self, callback: Callable):
        """Définit le callback pour l'audio capturé."""
        self.audio_callback = callback
    
    def start_listening(self, device_index: int = 0):
        """Démarre l'écoute audio."""
        if self.is_listening:
            logger.warning("L'écoute est déjà en cours")
            return
        
        try:
            self.recorder = PvRecorder(
                device_index=device_index, 
                frame_length=512  # Ajuster selon vos besoins
            )
            self.recorder.start()
            self.is_listening = True
            
            self.listening_thread = threading.Thread(
                target=self._listening_loop, 
                daemon=True
            )
            self.listening_thread.start()
            
            logger.info(f"Écoute démarrée sur périphérique {device_index}")
            
        except Exception as e:
            logger.error(f"Erreur démarrage écoute: {e}")
    
    def stop_listening(self):
        """Arrête l'écoute audio."""
        self.is_listening = False
        
        if self.recorder:
            try:
                self.recorder.stop()
                self.recorder.delete()
            except Exception as e:
                logger.warning(f"Erreur arrêt recorder: {e}")
        
        if self.listening_thread and self.listening_thread.is_alive():
            self.listening_thread.join(timeout=2.0)
        
        logger.info("Écoute arrêtée")
    
    def _listening_loop(self):
        """Boucle principale d'écoute."""
        try:
            while self.is_listening:
                try:
                    pcm = self.recorder.read()
                    # Ici, vous pouvez intégrer votre logique de détection de mot-clé
                    # Pour l'instant, on transmet directement l'audio
                    if self.audio_callback:
                        audio_data = np.array(pcm, dtype=np.int16)
                        self.audio_callback(audio_data)
                        
                except Exception as e:
                    if self.is_listening:  # Ne log pas si on est en train d'arrêter
                        logger.error(f"Erreur lecture audio: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"Erreur boucle écoute: {e}")
        finally:
            logger.info("Boucle d'écoute terminée")
    
    def get_audio_devices(self) -> list:
        """Retourne la liste des périphériques audio disponibles."""
        try:
            devices = PvRecorder.get_audio_devices()
            return [(idx, device) for idx, device in enumerate(devices)]
        except Exception as e:
            logger.error(f"Erreur récupération périphériques: {e}")
            return []
