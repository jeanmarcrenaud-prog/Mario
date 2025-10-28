import pyaudio
import numpy as np
import threading
import time
import math
from ..config import config
from ..utils.logger import logger

class AudioPlayer:
    """Gère la lecture audio de manière centralisée."""
    
    def __init__(self):
        self.pyaudio_instance = pyaudio.PyAudio()
    
    def play_audio(self, audio_data: np.ndarray):
        """Joue des données audio."""
        def play():
            try:
                stream = self.pyaudio_instance.open(
                    format=pyaudio.paInt16, 
                    channels=1, 
                    rate=config.SAMPLERATE, 
                    output=True
                )
                stream.write(audio_data.tobytes())
                stream.stop_stream()
                stream.close()
            except Exception as e:
                logger.error(f"Erreur lecture audio: {e}")
        
        threading.Thread(target=play, daemon=True).start()
    
    def play_beep(self, frequency: int = 1200, duration: float = 0.25, volume: float = 0.3):
        """Joue un bip sonore."""
        try:
            stream = self.pyaudio_instance.open(
                format=pyaudio.paInt16, 
                channels=1, 
                rate=44100, 
                output=True
            )
            t = np.linspace(0, duration, int(44100 * duration), False)
            beep = volume * np.sin(2 * math.pi * frequency * t)
            audio_data = (beep * 32767).astype(np.int16)
            stream.write(audio_data.tobytes())
            time.sleep(0.1)
            stream.stop_stream()
            stream.close()
        except Exception as e:
            logger.warning(f"Impossible de jouer le bip: {e}")
    
    def cleanup(self):
        """Nettoie les ressources audio."""
        try:
            self.pyaudio_instance.terminate()
        except Exception as e:
            logger.warning(f"Erreur nettoyage audio: {e}")
