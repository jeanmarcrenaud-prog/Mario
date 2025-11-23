# test_tts.py
import os
import sys

# Ajouter le chemin du projet au Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from src.utils.logger import logger
from src. models.text_to_speech import TextToSpeech

def test_tts_direct():
    """Test direct de TTS sans toute l'application"""
    print("🧪 Test TTS direct...")
    
    tts = TextToSpeech("fr_FR-siwis-medium")
    
    # Test 1: Synthèse seule
    print("1. Test synthèse...")
    audio_data = tts.synthesize("Bonjour, test audio")
    if audio_data is not None:
        print(f"✅ Synthèse OK: {len(audio_data)} samples")
    else:
        print("❌ Synthèse échouée")
        return False
    
    # Test 2: Lecture audio
    print("2. Test lecture...")
    success = tts.say("Bonjour, ceci est un test de lecture audio")
    if success:
        print("✅ Lecture OK")
    else:
        print("❌ Lecture échouée")
    
    return success

if __name__ == "__main__":
    test_tts_direct()
