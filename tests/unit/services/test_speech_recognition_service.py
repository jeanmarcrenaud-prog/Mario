"""
Tests unitaires pour SpeechRecognitionService.
"""

import numpy as np
from src.services.speech_recognition_service import SpeechRecognitionService
from src.adapters.speech_recognition_whisper_adapter import WhisperSpeechRecognitionAdapter
from src.adapters.speech_recognition_simulated_adapter import SimulatedSpeechRecognitionAdapter


class TestSpeechRecognitionService:
    """Tests pour SpeechRecognitionService."""
    
    def test_service_init_with_whisper(self):
        """Test l'initialisation avec Whisper adapter."""
        adapter = WhisperSpeechRecognitionAdapter(model_size="base")
        service = SpeechRecognitionService(adapter)
        assert service is not None
        assert service.is_available
        
    def test_service_init_with_simulation(self):
        """Test l'initialisation avec simulation adapter."""
        adapter = SimulatedSpeechRecognitionAdapter()
        service = SpeechRecognitionService(adapter)
        assert service is not None
        assert service.is_available
    
    def test_transcribe_returns_string(self, mocker):
        """Test que transcribe retourne une chaîne."""
        adapter = mocker.Mock()
        adapter.transcribe_array.return_value = "Test transcription"
        service = SpeechRecognitionService(adapter)
        
        result = service.transcribe(np.zeros(16000, dtype=np.int16))
        assert isinstance(result, str)
