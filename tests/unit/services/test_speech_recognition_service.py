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
        adapter = WhisperSpeechRecognitionAdapter(model_name="base")
        service = SpeechRecognitionService(adapter)
        assert service is not None
        assert service.is_available
        
    def test_service_init_with_simulation(self):
        """Test l'initialisation avec simulation adapter."""
        adapter = SimulatedSpeechRecognitionAdapter()
        service = SpeechRecognitionService(adapter)
        assert service is not None
        assert service.is_available
    
    def test_transcribe_returns_string(self, monkeypatch):
        """Test que transcribe retourne une chaîne."""
        from src.adapters.speech_recognition_simulated_adapter import SimulatedSpeechRecognitionAdapter
        
        adapter = SimulatedSpeechRecognitionAdapter()
        service = SpeechRecognitionService(adapter)
        
        # Patch transcribe_array méthode
        monkeypatch.setattr(adapter, 'transcribe_array', lambda audio, **kwargs: "Test transcription")
        
        result = service.transcribe(np.zeros(16000, dtype=np.int16))
        assert isinstance(result, str)
        assert result == "Test transcription"
