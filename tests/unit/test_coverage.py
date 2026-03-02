import pytest
from unittest.mock import MagicMock, patch, mock_open
import os
import sys


class TestConversationService:
    """Tests pour ConversationService."""

    def test_conversation_service_init(self):
        """Test d'initialisation du service de conversation."""
        from src.services.conversation_service import ConversationService
        
        service = ConversationService()
        assert service is not None


class TestPromptManager:
    """Tests pour PromptManager."""

    def test_prompt_manager_init(self):
        """Test d'initialisation du gestionnaire de prompts."""
        from src.core.prompt_manager import PromptManager
        
        manager = PromptManager()
        assert manager is not None


class TestWakeWordService:
    """Tests pour WakeWordService."""

    def test_wake_word_service_import(self):
        """Test d'import de WakeWordService."""
        from src.services.wake_word_service import WakeWordService
        assert WakeWordService is not None


class TestSpeechRecognitionService:
    """Tests pour SpeechRecognitionService."""

    def test_speech_recognition_service_import(self):
        """Test d'import de SpeechRecognitionService."""
        from src.services.speech_recognition_service import SpeechRecognitionService
        assert SpeechRecognitionService is not None


class TestTTSService:
    """Tests pour TTSService."""

    def test_create_with_piper(self):
        """Test de création du service TTS avec Piper."""
        from src.services.tts_service import TTSService
        
        with patch('src.services.tts_service.PiperTTSAdapter'):
            service = TTSService.create_with_piper("test-voice")
            assert service is not None


class TestMicrophoneChecker:
    """Tests pour MicrophoneChecker."""

    def test_microphone_checker_init(self):
        """Test d'initialisation de MicrophoneChecker."""
        from src.interfaces.microphone_checker import MicrophoneChecker
        
        with patch('src.interfaces.microphone_checker.pyaudio.PyAudio'):
            checker = MicrophoneChecker()
            assert checker is not None


class TestAudioController:
    """Tests pour AudioController."""

    def test_audio_controller_init(self):
        """Test d'initialisation de AudioController."""
        from src.services.audio_controller import AudioController
        
        with patch('src.services.audio_controller.pyaudio.PyAudio'):
            controller = AudioController()
            assert controller is not None


class TestSimulatedAdapters:
    """Tests pour les adaptateurs simulés."""

    def test_simulated_speech_recognition_import(self):
        """Test d'import de la reconnaissance vocale simulée."""
        from src.services import simulated_speech_recognition
        assert simulated_speech_recognition is not None

    def test_simulated_wake_word(self):
        """Test du wake-word simulé."""
        from src.services.simulated_wake_word_adapter import SimulatedWakeWordAdapter
        
        adapter = SimulatedWakeWordAdapter()
        assert adapter is not None


class TestProjectAnalyzer:
    """Tests pour ProjectAnalyzerService."""

    def test_project_analyzer_import(self):
        """Test d'import de ProjectAnalyzerService."""
        from src.services.project_analyzer_service import ProjectAnalyzerService
        assert ProjectAnalyzerService is not None


class TestConversationState:
    """Tests pour ConversationState."""

    def test_conversation_state_init(self):
        """Test d'initialisation de ConversationState."""
        from src.models.conversation_state import ConversationState
        
        state = ConversationState()
        assert state is not None


class TestLogger:
    """Tests pour le logger."""

    def test_logger_import(self):
        """Test d'import du logger."""
        from src.utils.logger import logger
        
        assert logger is not None


class TestDummyAdapters:
    """Tests pour les adaptateurs dummy."""

    def test_dummy_audio_input(self):
        """Test de l'adaptateur audio input dummy."""
        from src.adapters.dummy_audio_input import DummyAudioInput
        
        adapter = DummyAudioInput()
        assert adapter is not None

    def test_dummy_audio_output(self):
        """Test de l'adaptateur audio output dummy."""
        from src.adapters.dummy_audio_output import DummyAudioOutput
        
        adapter = DummyAudioOutput()
        assert adapter is not None


class TestInterfaces:
    """Tests pour les interfaces."""

    def test_interfaces_import(self):
        """Test d'import des interfaces."""
        from src.interfaces import speech_recognition
        from src.interfaces import wake_word
        assert speech_recognition is not None
        assert wake_word is not None


class TestAudioPipelineCoverage:
    """Tests pour améliorer la couverture de AudioPipeline."""

    def test_audio_pipeline_init(self):
        """Test d'initialisation du pipeline audio."""
        from src.core.audio_pipeline import AudioPipeline
        
        mock_settings = MagicMock()
        mock_settings.chunk_size = 1024
        mock_settings.audio_buffer_size = 3
        mock_settings.enable_low_latency = False
        
        mock_wake = MagicMock()
        mock_speech = MagicMock()
        mock_tts = MagicMock()
        
        pipeline = AudioPipeline(mock_wake, mock_speech, mock_tts, mock_settings)
        
        assert pipeline is not None
        assert pipeline._is_running is False

    def test_audio_pipeline_start_stop(self):
        """Test start/stop du pipeline audio."""
        from src.core.audio_pipeline import AudioPipeline
        
        mock_settings = MagicMock()
        mock_settings.chunk_size = 1024
        mock_settings.audio_buffer_size = 3
        mock_settings.enable_low_latency = False
        
        mock_wake = MagicMock()
        mock_speech = MagicMock()
        mock_tts = MagicMock()
        
        pipeline = AudioPipeline(mock_wake, mock_speech, mock_tts, mock_settings)
        
        pipeline._is_running = True
        pipeline.stop()
        
        assert pipeline._is_running is False

    def test_audio_pipeline_set_callbacks(self):
        """Test de configuration des callbacks."""
        from src.core.audio_pipeline import AudioPipeline
        
        mock_settings = MagicMock()
        mock_settings.chunk_size = 1024
        mock_settings.audio_buffer_size = 3
        mock_settings.enable_low_latency = False
        
        mock_wake = MagicMock()
        mock_speech = MagicMock()
        mock_tts = MagicMock()
        
        pipeline = AudioPipeline(mock_wake, mock_speech, mock_tts, mock_settings)
        
        def dummy_transcription(text):
            pass
        
        def dummy_wake_word():
            pass
        
        pipeline.set_transcription_callback(dummy_transcription)
        pipeline.set_wake_word_callback(dummy_wake_word)
        
        assert pipeline._on_transcription_ready is not None
        assert pipeline._on_wake_word_detected is not None


class TestLLMServiceCoverage:
    """Tests pour améliorer la couverture de LLMService."""

    def test_llm_service_with_ollama_unavailable(self):
        """Test LLMService quand Ollama n'est pas disponible."""
        from src.services.llm_service import LLMService
        
        with patch('src.services.llm_service.OllamaLLMAdapter') as mock_adapter:
            mock_instance = MagicMock()
            mock_instance.is_available = False
            mock_adapter.return_value = mock_instance
            
            service = LLMService.create_with_ollama("test-model")
            
            assert service is not None

    def test_simulated_adapter_custom_responses(self):
        """Test de l'adaptateur simulé avec réponses personnalisées."""
        from src.services.llm_service import SimulatedLLMAdapter
        
        responses = {"hello": "Hi there!"}
        adapter = SimulatedLLMAdapter(fake_responses=responses)
        
        result = adapter.generate_response([{"role": "user", "content": "hello"}])
        
        assert result == "Hi there!"

    def test_ollama_adapter_generation_error(self):
        """Test de gestion d'erreur dans OllamaAdapter."""
        from src.services.llm_service import OllamaLLMAdapter
        
        with patch('src.services.llm_service.requests.post') as mock_post:
            mock_post.side_effect = Exception("Network error")
            
            adapter = OllamaLLMAdapter.__new__(OllamaLLMAdapter)
            adapter.model_name = "test"
            adapter.base_url = "http://localhost:11434"
            adapter.is_available = True
            
            with pytest.raises(Exception):
                adapter.generate_response([{"role": "user", "content": "test"}])


class TestSystemMonitorCoverage:
    """Tests pour améliorer la couverture de SystemMonitor."""

    def test_system_monitor_init(self):
        """Test d'initialisation du moniteur système."""
        from src.utils.system_monitor import SystemMonitor
        
        with patch('src.utils.system_monitor.psutil.cpu_percent', return_value=50):
            monitor = SystemMonitor()
            assert monitor is not None

    def test_get_cpu_usage(self):
        """Test de récupération de l'utilisation CPU."""
        from src.utils.system_monitor import SystemMonitor
        
        with patch('src.utils.system_monitor.psutil.cpu_percent', return_value=50):
            monitor = SystemMonitor()
            usage = monitor.get_cpu_usage()
            assert usage == 50

    def test_get_memory_usage(self):
        """Test de récupération de l'utilisation mémoire."""
        from src.utils.system_monitor import SystemMonitor
        
        with patch('src.utils.system_monitor.psutil.virtual_memory') as mock_mem:
            mock_mem.return_value = MagicMock(percent=60)
            
            monitor = SystemMonitor()
            usage = monitor.get_memory_usage()
            assert usage == 60

    def test_get_disk_usage(self):
        """Test de récupération de l'utilisation disque."""
        from src.utils.system_monitor import SystemMonitor
        
        with patch('src.utils.system_monitor.psutil.disk_usage') as mock_disk:
            mock_disk.return_value = MagicMock(percent=70)
            
            monitor = SystemMonitor()
            usage = monitor.get_disk_usage("/")
            assert usage == 70

    def test_get_uptime(self):
        """Test de récupération de l'uptime."""
        from src.utils.system_monitor import SystemMonitor
        
        with patch('src.utils.system_monitor.psutil.boot_time'):
            monitor = SystemMonitor()
            uptime = monitor.get_uptime()
            assert isinstance(uptime, dict)


class TestErrorGuardCoverage:
    """Tests pour améliorer la couverture de ErrorGuard."""

    def test_error_handler_handle(self):
        """Test de la méthode handle d'ErrorHandler."""
        from src.utils.error_guard import ErrorHandler
        
        handler = ErrorHandler("Test")
        handler.handle(ValueError("test"), "context")
        
        assert handler.error_count == 1

    def test_safe_run_with_exception(self):
        """Test de safe_run avec exception."""
        from src.utils.error_guard import safe_run
        
        @safe_run("Test", return_on_error="error")
        def fail():
            raise ValueError("fail")
        
        result = fail()
        assert result == "error"


class TestConfigCoverage:
    """Tests pour améliorer la couverture de config."""

    def test_config_import(self):
        """Test d'import de config."""
        from src.config import config
        
        assert config is not None

    def test_settings_import(self):
        """Test d'import de Settings."""
        from src.models.settings import Settings
        
        settings = Settings()
        assert settings is not None
