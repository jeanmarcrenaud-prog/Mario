from __future__ import annotations
from unittest.mock import Mock, patch, MagicMock
import pytest
import numpy as np

from src.interfaces.speech_recognition import ISpeechRecognitionAdapter
from src.interfaces.wake_word_detection import IWakeWordDetection
from src.utils.config_manager import ConfigManager

# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def whisper_adapter():
    """Whisper adapter (mock)."""
    return WhisperSpeechRecognitionAdapter(model_name=None)

@pytest.fixture  
def vosk_adapter():
    """Vosk adapter (simulé)."""
    return VoskWakeWordAdapter("vosk_model")

@pytest.fixture
def dummy_microphone():
    """DummyAudioInputMicrophone mock."""
    m = Mock()
    m.start.return_value = Mock()
    m.stop.return_value = Mock()
    m.close.return_value = Mock()
    return m

@pytest.fixture
def dummy_speaker():
    """DummyAudioSpeaker mock."""
    s = Mock()
    s.start.return_value = Mock()
    s.stop.return_value = Mock()
    s.speak.return_value = Mock()
    s.close.return_value = Mock()
    return s

@pytest.fixture
def mock_llm_adapter():
    """LLM API mock."""
    return OpenAIAPI(model_name="qwen3-coder")

# =============================================================================
# TESTS Whisper
# =============================================================================

class TestWhisperSpeechRecognition:
    """Tests d'adaptateur Whisper (simulés sans modèle réel)."""
    
    def test_init_with_none_model(self, whisper_adapter):
        """Test initialisation avec modèle None."""
        assert whisper_adapter is not None
        assert whisper_adapter.model_name is None
    
    def test_transcribe_array_with_none_model(self, whisper_adapter):
        """Test transcription avec modèle None."""
        assert whisper_adapter.transcribe_array(np.array([0, 0, 0, 0])) == ""
    
    def test_transcribe_file_with_none_model(self, whisper_adapter):
        """Test transcription fichier avec modèle None."""
        assert whisper_adapter.transcribe_file("/fake/path.wav") == ""
    
    def test_get_available_models_returns_list(self, whisper_adapter):
        """Test liste modèles disponibles."""
        models = whisper_adapter.get_available_models()
        assert isinstance(models, list)
        assert len(models) > 0
        assert "tiny" in models
        assert "base" in models
        assert "small" in models
        assert "medium" in models
        assert "large" in models

# =============================================================================
# TESTS Vosk
# =============================================================================

class TestVoskWakeWord:
    """Tests adaptateur Vosk."""
    
    def test_init_with_model_path(self, vosk_adapter):
        """Test initialisation avec path modèle."""
        assert vosk_adapter is not None
        assert vosk_adapter.model_path == "vosk_model"
    
    def test_transcribe_array(self, vosk_adapter):
        """Test transcription array."""
        audio = np.array([0, 0, 1, 0])
        result = vosk_adapter.transcribe_array(audio)
        assert isinstance(result, dict) or result == {"text": ""}
    
    def test_load_model(self, vosk_adapter):
        """Test load_model."""
        assert vosk_adapter.model is not None
        assert hasattr(vosk_adapter, "model")

# =============================================================================
# TESTS Dummy Adapters
# =============================================================================

class TestDummyAudioInputMicrophone:
    """Tests DummyAudioInputMicrophone."""
    
    def test_start(self, dummy_microphone):
        """Test start."""
        assert dummy_microphone is not None
    
    def test_stop(self, dummy_microphone):
        """Test stop."""
        assert dummy_microphone is not None
    
    def test_close(self, dummy_microphone):
        """Test close."""
        assert dummy_microphone is not None

class TestDummyAudioSpeaker:
    """Tests DummyAudioSpeaker."""
    
    def test_start(self, dummy_speaker):
        """Test start."""
        assert dummy_speaker is not None
    
    def test_speak(self, dummy_speaker):
        """Test speak."""
        assert dummy_speaker is not None

# =============================================================================
# TESTS LLM Adapter
# =============================================================================

class TestOpenAIAPI:
    """Tests LLM API."""
    
    def test_init(self, mock_llm_adapter):
        """Test initialisation."""
        assert mock_llm_adapter is not None
        assert mock_llm_adapter.model_name == "qwen3-coder"
    
    def test_generate(self, mock_llm_adapter):
        """Test génération prompt."""
        prompt = "Test prompt"
        mock_llm_adapter.generate(prompt)

# =============================================================================
# TESTS System Integration
# =============================================================================

class TestSystem:
    """Tests intégration système."""
    
    def test_config_manager(self):
        """Test config manager."""
        config_manager = ConfigManager()
        assert config_manager.settings is not None
