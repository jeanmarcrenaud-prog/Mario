# tests/test_text_to_speech.py - Version simplifiée
import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from src.core.text_to_speech import TextToSpeech

def test_initialization():
    """Test l'initialisation de base."""
    tts = TextToSpeech()
    assert tts.current_voice is None
    assert isinstance(tts.audio_cache, dict)

def test_synthesize_without_voice():
    """Test la synthèse sans voix chargée."""
    tts = TextToSpeech()
    result = tts.synthesize("Hello world")
    assert result is None

def test_synthesize_empty_text():
    """Test la synthèse avec texte vide."""
    tts = TextToSpeech()
    tts.current_voice = {"type": "cli", "model_path": "/path/to/model.onnx"}
    result = tts.synthesize("")
    assert result is None

def test_get_voice_info():
    """Test la récupération des informations de voix."""
    tts = TextToSpeech()
    tts.current_voice = {
        "type": "cli",
        "voice_name": "test_voice", 
        "sample_rate": 22050
    }
    info = tts.get_voice_info()
    assert info["name"] == "test_voice"
    assert info["type"] == "cli"

@patch('src.core.text_to_speech.TextToSpeech.synthesize')
def test_test_synthesis(mock_synthesize):
    """Test la méthode de test de synthèse."""
    # Test réussite
    mock_synthesize.return_value = np.array([1, 2, 3], dtype=np.int16)
    tts = TextToSpeech()
    assert tts.test_synthesis() == True
    
    # Test échec
    mock_synthesize.return_value = None
    assert tts.test_synthesis() == False
