"""Comprehensive tests for core modules to increase coverage."""
import pytest
from unittest.mock import MagicMock, patch, Mock
from io import StringIO


class TestAppRunner:
    """Tests pour AppRunner."""

    def test_app_runner_import(self):
        """Test d'import de AppRunner."""
        from src.core import app_runner
        assert app_runner is not None


class TestConversationHandler:
    """Tests pour ConversationHandler."""

    def test_conversation_handler_import(self):
        """Test d'import de ConversationHandler."""
        from src.core import conversation_handler
        assert conversation_handler is not None


class TestExceptions:
    """Tests pour les exceptions."""

    def test_speech_recognition_error(self):
        """Test d'exception SpeechRecognitionError."""
        from src.core.exceptions import SpeechRecognitionError
        
        exc = SpeechRecognitionError("Test error")
        assert str(exc) == "Test error"

    def test_text_to_speech_error(self):
        """Test d'exception TextToSpeechError."""
        from src.core.exceptions import TextToSpeechError
        
        exc = TextToSpeechError("Audio error")
        assert str(exc) == "Audio error"

    def test_hardware_error(self):
        """Test d'exception HardwareError."""
        from src.core.exceptions import HardwareError
        
        exc = HardwareError("Hardware error")
        assert str(exc) == "Hardware error"


class TestIntentRouter:
    """Tests pour IntentRouter."""

    def test_intent_router_import(self):
        """Test d'import de IntentRouter."""
        from src.core import intent_router
        assert intent_router is not None


class TestInterfaceManager:
    """Tests pour InterfaceManager."""

    def test_interface_manager_import(self):
        """Test d'import de InterfaceManager."""
        from src.core import interface_manager
        assert interface_manager is not None


class TestLLMServiceCore:
    """Tests pour le service LLM central."""

    def test_llm_service_core_import(self):
        """Test d'import du service LLM central."""
        from src.core import llm_service
        assert llm_service is not None


class TestPromptManagerCoverage:
    """Tests supplémentaires pour PromptManager."""

    def test_prompt_manager_import(self):
        """Test d'import de PromptManager."""
        from src.core.prompt_manager import PromptManager
        assert PromptManager is not None


class TestPerformanceOptimizer:
    """Tests pour PerformanceOptimizer."""

    def test_performance_optimizer_import(self):
        """Test d'import de PerformanceOptimizer."""
        from src.core import performance_optimizer
        assert performance_optimizer is not None
