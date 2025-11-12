"""
Test pour le service de reconnaissance vocale
==========================================
"""

import pytest
from unittest.mock import MagicMock, patch
from src.core.speech_recognition_service import SpeechRecognitionService

@pytest.fixture
def mock_recognizer():
    mock_recognizer = MagicMock()
    return mock_recognizer

def test_speech_recognition_initialization(mock_recognizer):
    """Test l'initialisation du service de reconnaissance vocale."""
    with patch('speech_recognition.Recognizer', return_value=mock_recognizer):
        service = SpeechRecognitionService()
        assert service.recognizer == mock_recognizer

@patch.object(SpeechRecognitionService, 'listen')
def test_listen(mock_listen, mock_recognizer):
    """Test la capture et la reconnaissance de l'audio."""
    with patch('speech_recognition.Recognizer', return_value=mock_recognizer):
        service = SpeechRecognitionService()
        mock_listen.return_value = "Test audio"
        result = service.listen()
        assert result == "Test audio"

@patch.object(SpeechRecognitionService, 'stop')
def test_stop(mock_stop, mock_recognizer):
    """Test l'arrêt du service de reconnaissance vocale."""
    with patch('speech_recognition.Recognizer', return_value=mock_recognizer):
        service = SpeechRecognitionService()
        service.stop()
        mock_stop.assert_called_once()
