# tests/test_speech_recognition.py
import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from src.core.speech_recognition import SpeechRecognizer

@patch('src.core.speech_recognition.whisper.load_model')
def test_transcribe(mock_load_model):
    """Test la transcription audio."""
    # Configuration du mock
    mock_model = MagicMock()
    mock_model.transcribe.return_value = {"text": "bonjour test", "segments": [{"avg_logprob": -0.5}]}
    mock_load_model.return_value = mock_model
    
    # Instanciation et chargement du modèle
    recognizer = SpeechRecognizer()
    recognizer.model = mock_model  # Simuler un modèle chargé
    recognizer.is_loaded = True
    
    # Création de données audio fictives
    fake_audio = np.random.random(16000).astype(np.float32)  # 1 seconde à 16kHz
    
    # Appel de la méthode correcte : transcribe() pas transcribe_audio()
    result = recognizer.transcribe(fake_audio, language="fr")
    
    # Vérifications
    assert result["text"] == "bonjour test"
    assert result["language"] == "fr"
    assert result["has_speech"] == True
    mock_model.transcribe.assert_called_once()

def test_is_ready():
    """Test la vérification de disponibilité."""
    recognizer = SpeechRecognizer()
    
    # Test quand le modèle n'est pas chargé
    assert recognizer.is_ready() == False
    
    # Test quand le modèle est chargé
    recognizer.is_loaded = True
    recognizer.model = MagicMock()
    assert recognizer.is_ready() == True

@patch('src.core.speech_recognition.whisper.load_model')
def test_load_model_success(mock_load_model):
    """Test le chargement réussi du modèle."""
    mock_model = MagicMock()
    mock_load_model.return_value = mock_model
    
    recognizer = SpeechRecognizer()
    result = recognizer.load_model("base")
    
    assert result == True
    assert recognizer.is_loaded == True
    assert recognizer.model == mock_model

@patch('src.core.speech_recognition.whisper.load_model')
def test_load_model_failure(mock_load_model):
    """Test l'échec du chargement du modèle."""
    mock_load_model.side_effect = Exception("Load error")
    
    recognizer = SpeechRecognizer()
    result = recognizer.load_model("base")
    
    assert result == False
    assert recognizer.is_loaded == False

def test_transcribe_without_model():
    """Test la transcription sans modèle chargé."""
    recognizer = SpeechRecognizer()
    recognizer.is_loaded = False
    
    fake_audio = np.random.random(16000).astype(np.float32)
    result = recognizer.transcribe(fake_audio)
    
    assert result["text"] == ""
    assert "error" in result
