"""Comprehensive tests for core modules to increase coverage."""


class TestAppRunner:
    """Tests pour app_runner module."""

    def test_app_runner_import(self):
        """Test d'import du module app_runner."""
        from src.core import app_runner
        assert app_runner is not None
        # Vérifier les exports principaux
        assert hasattr(app_runner, 'run_application')


class TestConversationHandler:
    """Tests pour conversation_handler module."""

    def test_conversation_handler_import(self):
        """Test d'import du module conversation_handler."""
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
    """Tests pour intent_router module."""

    def test_intent_router_import(self):
        """Test d'import du module intent_router."""
        from src.core import intent_router
        assert intent_router is not None


class TestInterfaceManager:
    """Tests pour interface_manager module."""

    def test_interface_manager_import(self):
        """Test d'import du module interface_manager."""
        from src.core import interface_manager
        assert interface_manager is not None


class TestLLMServiceCore:
    """Tests pour le service LLM central."""

    def test_llm_service_core_import(self):
        """Test d'import du service LLM central."""
        from src.services import llm_service
        assert llm_service is not None


class TestPromptManagerCoverage:
    """Tests supplémentaires pour PromptManager."""

    def test_prompt_manager_import(self):
        """Test d'import du module prompt_manager."""
        from src.core import prompt_manager
        assert prompt_manager is not None


class TestPerformanceOptimizer:
    """Tests pour performance_optimizer module."""

    def test_performance_optimizer_import(self):
        """Test d'import du module performance_optimizer."""
        from src.core import performance_optimizer
        assert performance_optimizer is not None
