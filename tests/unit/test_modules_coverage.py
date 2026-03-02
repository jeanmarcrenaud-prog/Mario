"""Comprehensive tests for models and utils modules."""
import pytest
from unittest.mock import MagicMock, patch
import os


class TestAudioDeviceManager:
    """Tests pour AudioDeviceManager."""

    def test_audio_device_manager_import(self):
        """Test d'import de AudioDeviceManager."""
        from src.models.audio_device_manager import AudioDeviceManager
        assert AudioDeviceManager is not None


class TestFileAnalyzer:
    """Tests pour FileAnalyzer."""

    def test_file_analyzer_import(self):
        """Test d'import de FileAnalyzer."""
        from src.models.file_analyzer import FileAnalyzer
        assert FileAnalyzer is not None


class TestOllamaClient:
    """Tests pour OllamaClient."""

    def test_ollama_client_import(self):
        """Test d'import de OllamaClient."""
        from src.models.ollama_client import OllamaClient
        assert OllamaClient is not None


class TestTextToSpeech:
    """Tests pour TextToSpeech."""

    def test_text_to_speech_import(self):
        """Test d'import de TextToSpeech."""
        from src.models.text_to_speech import TextToSpeech
        assert TextToSpeech is not None


class TestAudioPlayer:
    """Tests pour AudioPlayer."""

    def test_audio_player_import(self):
        """Test d'import de AudioPlayer."""
        from src.utils.audio_player import AudioPlayer
        assert AudioPlayer is not None


class TestConsoleView:
    """Tests pour ConsoleView."""

    def test_console_view_import(self):
        """Test d'import de ConsoleView."""
        from src.views.console_view import ConsoleView
        assert ConsoleView is not None


class TestWelcomeScreen:
    """Tests pour WelcomeScreen."""

    def test_welcome_screen_import(self):
        """Test d'import de WelcomeScreen."""
        from src.views.welcome_screen import show_welcome_screen, show_main_menu
        assert show_welcome_screen is not None
        assert show_main_menu is not None
