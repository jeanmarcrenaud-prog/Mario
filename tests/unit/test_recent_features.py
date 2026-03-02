import pytest
from unittest.mock import MagicMock, patch, PropertyMock
import sys

class TestGradioWebInterface:
    """Tests pour l'interface Gradio."""

    @patch('src.views.web_interface_gradio.GradioWebInterface.__init__', lambda x: None)
    def test_initialize_components(self):
        """Test de l'initialisation des composants."""
        from src.views.web_interface_gradio import GradioWebInterface
        
        mock_assistant = MagicMock()
        mock_assistant.settings.llm_model = "test-model"
        mock_assistant.settings.voice_name = "test-voice"
        
        interface = object.__new__(GradioWebInterface)
        interface.assistant = mock_assistant
        interface._initialize_components()
        
        assert interface.app_state is None
        assert interface.status_text is None
        assert interface.system_stats is None


class TestAudioPipelineLatency:
    """Tests pour l'optimisation de latence audio."""

    def test_latency_stats_tracking(self):
        """Test du suivi des statistiques de latence."""
        from src.core.audio_pipeline import AudioPipeline
        
        mock_settings = MagicMock()
        mock_settings.chunk_size = 1024
        mock_settings.audio_buffer_size = 3
        mock_settings.enable_low_latency = False
        
        mock_wake = MagicMock()
        mock_speech = MagicMock()
        mock_tts = MagicMock()
        
        with patch.object(AudioPipeline, '__init__', lambda self, w, s, t, st: None):
            pipeline = AudioPipeline(mock_wake, mock_speech, mock_tts, mock_settings)
            pipeline._latency_stats = {"transcription": [], "tts": [], "wake_word": []}
            pipeline._latency_stats["transcription"] = [0.5, 0.6, 0.7]
            pipeline._latency_stats["tts"] = [0.3, 0.4]
            
            result = pipeline.get_latency_stats()
            
            assert "transcription_avg" in result
            assert result["transcription_avg"] == pytest.approx(0.6)
            assert "transcription_min" in result
            assert result["transcription_min"] == 0.5
            assert "transcription_max" in result
            assert result["transcription_max"] == 0.7
            assert "tts_avg" in result
            assert result["tts_avg"] == pytest.approx(0.35)


class TestErrorHandling:
    """Tests pour la gestion d'erreurs."""

    def test_error_handler_class(self):
        """Test de la classe ErrorHandler."""
        from src.utils.error_guard import ErrorHandler
        
        handler = ErrorHandler("Test")
        
        assert handler.module_name == "Test"
        assert handler.error_count == 0
        assert len(handler.get_errors()) == 0
        
        handler.handle(Exception("Test error"), "test_context")
        
        assert handler.error_count == 1
        assert len(handler.get_errors()) == 1
        assert handler.get_errors()[0]["context"] == "test_context"
        
        handler.clear_errors()
        
        assert handler.error_count == 0
        assert len(handler.get_errors()) == 0

    def test_safe_run_decorator(self):
        """Test du décorateur safe_run."""
        from src.utils.error_guard import safe_run
        
        @safe_run("Test", return_on_error=-1)
        def function_that_works():
            return 42
        
        @safe_run("Test", return_on_error=-1)
        def function_that_fails():
            raise ValueError("Test error")
        
        assert function_that_works() == 42
        assert function_that_fails() == -1

    def test_retry_decorator(self):
        """Test du décorateur retry."""
        from src.utils.error_guard import retry
        
        call_count = 0
        
        @retry(max_attempts=3, delay=0.01)
        def function_that_fails_twice():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Fail")
            return "Success"
        
        result = function_that_fails_twice()
        
        assert result == "Success"
        assert call_count == 3

    def test_suppress_errors_decorator(self):
        """Test du décorateur suppress_errors."""
        from src.utils.error_guard import suppress_errors
        
        @suppress_errors(return_value="suppressed")
        def function_that_fails():
            raise ValueError("Error")
        
        result = function_that_fails()
        
        assert result == "suppressed"

    def test_global_error_handler(self):
        """Test du gestionnaire d'erreurs global."""
        from src.utils.error_guard import get_error_handler, _global_error_handler
        
        handler = get_error_handler()
        
        assert handler is _global_error_handler


class TestGPUMonitoring:
    """Tests pour le monitoring GPU."""

    @patch('src.utils.system_monitor.torch.cuda.is_available')
    def test_get_gpu_info_empty_no_cuda(self, mock_cuda):
        """Test get_gpu_info quand CUDA n'est pas disponible."""
        mock_cuda.return_value = False
        
        from src.utils.system_monitor import SystemMonitor
        monitor = SystemMonitor()
        
        with patch('src.utils.system_monitor.SystemMonitor._get_gpu_info_nvidia_smi', return_value=[]):
            result = monitor.get_gpu_info()
            
            assert result == []

    @patch('src.utils.system_monitor.torch.cuda.is_available')
    def test_get_gpu_utilization_nvidia_smi(self, mock_cuda):
        """Test de la récupération de l'utilisation GPU via nvidia-smi."""
        mock_cuda.return_value = False
        
        from src.utils.system_monitor import SystemMonitor
        monitor = SystemMonitor()
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="75\n")
            
            result = monitor._get_gpu_utilization()
            
            assert result == 75.0

    @patch('src.utils.system_monitor.torch.cuda.is_available')
    def test_get_gpu_power_nvidia_smi(self, mock_cuda):
        """Test de la récupération de la puissance GPU via nvidia-smi."""
        mock_cuda.return_value = False
        
        from src.utils.system_monitor import SystemMonitor
        monitor = SystemMonitor()
        
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "150.5"
            mock_run.return_value = mock_result
            
            result = monitor._get_gpu_power()
            
            assert result == 150.5


class TestAudioSettings:
    """Tests pour les settings audio."""

    def test_settings_default_values(self):
        """Test des valeurs par défaut des settings audio."""
        from src.models.settings import Settings
        
        settings = Settings()
        
        assert settings.chunk_size == 1024
        assert settings.audio_buffer_size == 3
        assert settings.enable_low_latency is False

    def test_settings_from_config(self):
        """Test de la création des settings depuis la config."""
        from src.models.settings import Settings
        
        mock_config = MagicMock()
        mock_config.DEFAULT_MICROPHONE_INDEX = 1
        mock_config.DEFAULT_VOICE = "test-voice"
        mock_config.DEFAULT_MODEL = "test-model"
        mock_config.WEB_PORT = 8080
        mock_config.SAMPLE_RATE = 44100
        mock_config.OPENAI_API_KEY = "test-key"
        mock_config.CHUNK_SIZE = 512
        mock_config.AUDIO_BUFFER_SIZE = 2
        mock_config.ENABLE_LOW_LATENCY = True
        
        settings = Settings.from_config(mock_config)
        
        assert settings.microphone_index == 1
        assert settings.voice_name == "test-voice"
        assert settings.chunk_size == 512
        assert settings.audio_buffer_size == 2
        assert settings.enable_low_latency is True
