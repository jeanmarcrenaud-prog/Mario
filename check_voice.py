import os
import numpy as np
import pyaudio
from piper import PiperVoice

# Chemins vers les fichiers de la voix
model_path = os.path.join("voices", "fr_FR-siwis-medium", "fr_FR-siwis-medium.onnx")
config_path = os.path.join("voices", "fr_FR-siwis-medium", "fr_FR-siwis-medium.onnx.json")

# Vérifiez que les fichiers existent
if not os.path.exists(model_path):
    raise FileNotFoundError(f"Fichier .onnx introuvable : {model_path}")
if not os.path.exists(config_path):
    raise FileNotFoundError(f"Fichier .json introuvable : {config_path}")

# Initialise PiperVoice
try:
    voice = PiperVoice.load(model_path, config_path=config_path, use_cuda=False)
except Exception as e:
    raise RuntimeError(f"Erreur lors de l'initialisation de PiperVoice : {e}")

# Synthétise un texte
text = "Bonjour, ceci est un test."
audio_data = voice.synthesize(text)

# Convertit les objets AudioChunk en tableau NumPy
audio_chunks = list(audio_data)
if len(audio_chunks) == 0:
    raise ValueError("Aucune donnée audio générée.")

# Utilise audio_float_array pour obtenir les données audio
audio_samples = np.concatenate([chunk.audio_float_array for chunk in audio_chunks])

# Joue l'audio
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paFloat32, channels=1, rate=22050, output=True)
stream.write(audio_samples.astype(np.float32).tobytes())
stream.stop_stream()
stream.close()
p.terminate()
