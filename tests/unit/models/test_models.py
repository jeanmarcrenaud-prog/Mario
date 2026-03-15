"""
Tests unitaires pour les modèles de données.
"""

import pytest
from src.models.settings import Settings
from src.models.config_manager import ConfigManager
from src.models.conversation_state import ConversationState
from src.models.file_analyzer import FileAnalyzer
from src.models.ollama_client import OllamaClient
from src.models.audio_device_manager import AudioDeviceManager
from src.models.text_to_speech import TextToSpeech


class TestSettings:
    """Tests pour Settings."""
    
    def test_settings_from_config(self):
        """Test la création de Settings depuis config."""
        settings = Settings.from_config(None)
        assert settings is not None
        assert hasattr(settings, 'voice_name')
        assert hasattr(settings, 'llm_model')


class TestConfigManager:
    """Tests pour ConfigManager."""
    
    def test_config_manager_init(self):
        """Test l'initialisation de ConfigManager."""
        manager = ConfigManager()
        assert manager is not None


class TestConversationState:
    """Tests pour ConversationState."""
    
    def test_conversation_state_init(self):
        """Test l'initialisation de ConversationState."""
        state = ConversationState()
        assert state is not None
        assert hasattr(state, 'messages')


class TestFileAnalyzer:
    """Tests pour FileAnalyzer."""
    
    def test_file_analyzer_init(self):
        """Test l'initialisation de FileAnalyzer."""
        analyzer = FileAnalyzer()
        assert analyzer is not None


class TestOllamaClient:
    """Tests pour OllamaClient."""
    
    def test_ollama_client_init(self):
        """Test l'initialisation de OllamaClient."""
        client = OllamaClient()
        assert client is not None


class TestAudioDeviceManager:
    """Tests pour AudioDeviceManager."""
    
    def test_audio_device_manager_init(self):
        """Test l'initialisation de AudioDeviceManager."""
        manager = AudioDeviceManager()
        assert manager is not None


class TestTextToSpeech:
    """Tests pour TextToSpeech."""
    
    def test_text_to_speech_init(self):
        """Test l'initialisation de TextToSpeech."""
        tts = TextToSpeech()
        assert tts is not None
