import pyaudio
import numpy as np
from ..utils.logger import logger

# Constantes globales pour éviter les répétitions
SAMPLE_RATE = 44100
DEFAULT_FREQUENCY = 800
DEFAULT_DURATION = 0.2
DEFAULT_VOLUME = 0.3

def play_beep(frequency: int = DEFAULT_FREQUENCY, duration: float = DEFAULT_DURATION, volume: float = DEFAULT_VOLUME):
    """Joue un bip sonore."""
    try:
        # Génération du bip
        t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
        beep = volume * np.sin(2 * np.pi * frequency * t)
        audio_data = (beep * 32767).astype(np.int16)
        
        # Lecture audio
        p = pyaudio.PyAudio()
        try:
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=SAMPLE_RATE,
                output=True
            )
            stream.write(audio_data.tobytes())
            stream.stop_stream()
            stream.close()
        finally:
            p.terminate()
            
    except Exception as e:
        logger.error(f"Erreur lecture bip: {e}")

def play_confirmation_beep():
    """Joue un bip de confirmation standard."""
    play_beep()

def play_error_beep():
    """Joue un bip d'erreur."""
    play_beep(frequency=400, duration=0.5, volume=0.2)
