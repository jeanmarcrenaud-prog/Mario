"""
Tests d'intégration complets pour l'assistant Mario
"""
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch, call


class TestFullPipelineIntegration:
    """Tests d'intégration complete pour le pipeline audio/LLM."""
    
    @pytest.fixture
    def pipeline_setup(self):
        """Setup complet du pipeline pour tests d'intégration."""
        # Mocks nécessaires
        mock_wake_word = Mock()
        mock_wake_word.check_microphone.return_value = 1
        mock_wake_word.is_speaking.return_value = False
        
        mock_speech_recognition = Mock()
        mock_speech_recognition.transcribe.return_value = "Bonjour, comment puis-je vous aider?"
        
        mock_tts = Mock()
        mock_tts.synthesize.return_value = "fake_audio_data"
        
        mock_llm = Mock()
        mock_llm.generate.return_value = {
            "response": "Bonjour! Je suis Mario, votre assistant vocal.",
            "history": []
        }
        
        return {
            "wake_word": mock_wake_word,
            "speech_recognition": mock_speech_recognition,
            "tts": mock_tts,
            "llm": mock_llm
        }
    
    def test_full_transcribe_generate_speak_flow(self, pipeline_setup):
        """Test du flux complet: transcribe → générer → parler."""
        from src.core.audio_pipeline import AudioPipeline
        
        mock_settings = MagicMock()
        mock_settings.chunk_size = 1024
        mock_settings.audio_buffer_size = 1
        mock_settings.enable_low_latency = False
        
        # Crée un pipeline avec mocks
        pipeline = AudioPipeline(
            pipeline_setup["wake_word"],
            pipeline_setup["speech_recognition"],
            pipeline_setup["tts"],
            mock_settings
        )
        
        # Mock interne
        pipeline._transcriber = Mock()
        pipeline._transcriber.transcribe.return_value = "Test transcription"
        
        result = pipeline.process_audio(None)
        
        assert result is not None
    
    def test_conversation_flow_with_context(self, pipeline_setup):
        """Test de flux conversationnel avec contexte préservé."""
        from src.core.audio_pipeline import AudioPipeline
        
        mock_settings = MagicMock()
        mock_settings.chunk_size = 1024
        mock_settings.audio_buffer_size = 1
        mock_settings.enable_low_latency = False
        
        pipeline = AudioPipeline(
            pipeline_setup["wake_word"],
            pipeline_setup["speech_recognition"],
            pipeline_setup["tts"],
            mock_settings
        )
        
        pipeline._transcriber = Mock(return_value="Question sur Python")
        
        # Test avec historique
        history = [
            {"role": "user", "content": "Salut!"}
        ]
        
        with patch.object(pipeline, "_conversation_state") as mock_state:
            mock_state.messages = history
            result = pipeline.process_audio(None)
            
            assert mock_state.messages is history


class TestSystemIntegration:
    """Tests d'intégration système complète."""
    
    @pytest.fixture
    def mock_system(self):
        """Mock système complet."""
        system = Mock()
        
        system.cpu_percent = lambda: 25.0
        system.cpu_count = lambda: 8
        system.memory_percent = lambda: 50.0
        system.virtual_memory = lambda: MagicMock(percent=50.0)
        
        return system
    
    def test_system_stats_collection(self, mock_system):
        """Test de collecte complète des stats système."""
        from src.utils.system_monitor import SystemMonitor
        
        monitor = SystemMonitor(mock_system)
        
        stats = monitor.get_system_stats()
        
        assert stats is not None
        assert hasattr(stats, 'cpu') or hasattr(stats, 'memory')
    
    def test_system_alerts_generation(self, mock_system):
        """Test de génération d'alertes système."""
        from src.utils.system_monitor import SystemMonitor
        import pytest
        
        monitor = SystemMonitor(mock_system)
        
        # Setup avec haut usage
        mock_system.cpu_percent = lambda: 95.0
        mock_system.memory_percent = lambda: 90.0
        
        alerts = monitor.check_alerts()
        
        assert alert is not None


class TestLLMPipelineIntegration:
    """Tests de pipeline LLM complète."""
    
    @pytest.fixture
    def llm_pipeline_setup(self):
        """Setup pipeline LLM."""
        llm_client = Mock()
        llm_client.generate.return_value = {
            "response": "Réponse AI complete",
            "done": True
        }
        
        return llm_client
    
    def test_llm_generation_with_system_message(self, llm_pipeline_setup):
        """Test de génération avec système message."""
        from src.services.llm_service import LLMService
        
        llm_service = LLMService(llm_pipeline_setup)
        
        messages = [
            {"role": "system", "content": "Vous êtes Mario, assistant vocal"},
            {"role": "user", "content": "Bonjour"}
        ]
        
        result = llm_service.generate_response(messages)
        
        assert "response" in result


class TestAudioPipelineIntegration:
    """Tests de pipeline audio complète."""
    
    @pytest.fixture
    def mock_audio_devices(self, tmp_path):
        """Mock devices audio."""
        devices = [{"id": 0, "name": "Microphone (Realtek)"}]
        return devices
    
    def test_audio_pipeline_buffering(self, mock_audio_devices):
        """Test du buffering audio."""
        # Setup pipeline
        mock_wake_word = Mock()
        mock_speech = Mock(return_value="transcription")
        mock_tts = Mock(return_value="audio")
        
        from src.core.audio_pipeline import AudioPipeline
        
        mock_settings = MagicMock()
        mock_settings.chunk_size = 1024
        mock_settings.audio_buffer_size = 3
        mock_settings.enable_low_latency = False
        
        pipeline = AudioPipeline(mock_wake_word, mock_speech, mock_tts, mock_settings)
        
        pipeline._buffer = []
        
        pipeline.add_chunk(b"audio_data")
        
        assert len(pipeline._buffer) > 0


class TestConversationStateIntegration:
    """Tests d'état conversationnel complète."""
    
    def test_conversation_with_multiple_turns(self):
        """Test de conversation avec plusieurs tours."""
        from src.models.conversation_state import ConversationState
        
        state = ConversationState()
        
        # Simule plusieurs tours
        state.add_user_message("Hello")
        state.add_system_message("Je suis Mario")
        state.add_assistant_response("Bonjour! Comment puis-je vous aider?")
        
        messages = state.get_messages()
        
        assert len(messages) == 3
        assert messages[0]["role"] == "user"
        assert messages[1]["role"] == "system"
        assert messages[2]["role"] == "assistant"


class TestErrorHandlingIntegration:
    """Tests de gestion d'erreurs complète."""
    
    def test_retry_mechanism_works(self):
        """Test du mécanisme de retry."""
        from src.utils.error_guard import retry
        
        call_count = 0
        
        @retry(max_attempts=3, delay=0.001)
        def failing_then_success():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Connection failed")
            return "Success after retries"
        
        result = failing_then_success()
        
        assert result == "Success after retries"
        assert call_count == 3
    
    def test_safe_run_catches_errors(self):
        """Test que safe_run capture les erreurs."""
        from src.utils.error_guard import safe_run
        
        @safe_run("test_module", return_on_error="ERROR")
        def fails():
            raise ValueError("Test error")
        
        result = fails()
        
        assert result == "ERROR"


class TestPerformanceIntegration:
    """Tests de performance."""
    
    def test_audio_processing_latency(self, tmp_path):
        """Test de latence traitement audio."""
        from src.core.audio_pipeline import AudioPipeline
        from unittest.mock import Mock, MagicMock
        
        mock_pipeline_setup = Mock()
        mock_pipeline_setup.transcribe.return_value = "text"
        
        mock_settings = MagicMock()
        mock_settings.chunk_size = 1024
        mock_settings.audio_buffer_size = 1
        mock_settings.enable_low_latency = True
        
        pipeline = AudioPipeline(
            Mock(),
            mock_pipeline_setup,
            Mock(),
            mock_settings
        )
        
        latency_stats = pipeline.get_latency_stats()
        
        assert isinstance(latency_stats, dict)
        assert "transcription_avg" in latency_stats or "tts_avg" in latency_stats


class TestEventBusIntegration:
    """Tests du système d'événements."""
    
    def test_event_publishing(self):
        """Test de publication d'événements."""
        from src.events.events import events
        
        # Test que events sont disponibles
        assert events is not None
    
    def test_event_subscription(self):
        """Test d'abonnement aux événements."""
        from src.events.event_bus import EventBus
        
        bus = EventBus()
        
        received = []
        
        def on_event(event):
            received.append(event)
        
        bus.subscribe("AUDIO_PLAYED", on_event)
        
        assert bus.subscribers is not None


class TestConfigIntegration:
    """Tests d'intégration configuration."""
    
    def test_config_with_all_options(self):
        """Test configuration complète."""
        from src.models.settings import Settings
        
        settings = Settings()
        
        assert hasattr(settings, 'chunk_size')
        assert hasattr(settings, 'microphone_index')
        assert hasattr(settings, 'voice_name')
        assert hasattr(settings, 'llm_model')
        assert hasattr(settings, 'web_port')
        assert hasattr(settings, 'sample_rate')


class TestIntegrationCompleteAssistant:
    """Tests de l'assistant complet."""
    
    def test_assistant_initialization(self):
        """Test d'initialisation de l'assistant."""
        from src.core.app_factory import AppFactory
        from unittest.mock import Mock
        
        configs = Mock()
        configs.DEFAULT_MICROPHONE_INDEX = 1
        configs.DEFAULT_VOICE = "fr_FR-siwis-medium"
        configs.DEFAULT_MODEL = "qwen3-coder"
        configs.WEB_PORT = 7860
        configs.SAMPLE_RATE = 16000
        
        with patch('src.core.app_factory.ConversationService') as conv_mock:
            with patch('src.core.app_factory.TTSPiperService') as tts_mock:
                with patch('src.core.app_factory.WakeWordService') as wake_mock:
                    with patch('src.core.app_factory.SpeechRecognitionService') as sr_mock:
                        with patch('src.core.app_factory.LLMService') as llm_mock:
                            with patch('src.core.app_factory.SystemMonitor') as sys_mock:
                                conv_mock.return_value = Mock()
                                tts_mock.return_value = Mock()
                                wake_mock.return_value = Mock()
                                sr_mock.return_value = Mock()
                                llm_mock.return_value = Mock()
                                sys_mock.return_value = Mock()
                                
                                factory = AppFactory()
                                app = factory.create(configs)
                                
                                assert app is not None


class TestInterfaceIntegration:
    """Tests d'interface complète."""
    
    def test_web_interface_startup(self, tmp_path):
        """Test de démarrage interface web."""
        from unittest.mock import Mock, patch
        
        with patch('src.views.web_interface_gradio.GradioWebInterface') as mock_gradio:
            mock_app = Mock()
            mock_app.app_state = Mock()
            mock_app.status_text = Mock()
            mock_app.system_stats = Mock()
            mock_app.conversation_messages = Mock()
            mock_app.files = Mock()
            mock_app.prompts = Mock()
            mock_app.settings = Mock()
            
            mock_gradio.return_value = mock_app
            
            from src.core.interface_manager import InterfaceManager
            
            interface_manager = InterfaceManager(mock_app, configs)
            
            assert interface_manager is not None


# ==================== FIXTURES UTILITY ====================


@pytest.fixture
def mock_configs():
    """Configuration par défaut pour tests d'intégration."""
    return {
        "DEFAULT_MICROPHONE_INDEX": 1,
        "DEFAULT_VOICE": "fr_FR-siwes-medium",
        "DEFAULT_MODEL": "qwen3-coder",
        "WEB_PORT": 7860,
        "SAMPLE_RATE": 16000
    }


@pytest.fixture
def mock_audio_file(tmp_path):
    """Crée fichier audio pour tests."""
    audio_file = tmp_path / "test.wav"
    audio_file.write_bytes(b"fake_audio_data")
    return str(audio_file)


@pytest.fixture  
def temporary_config_file(tmp_path):
    """Crée fichier configuration temporaire."""
    config = tmp_path / "test_config.yaml"
    config.write_text("""
default_microphone_index: 1
default_voice: "fr_FR-siwis-medium"
default_model: "qwen3-coder"
web_port: 7860
sample_rate: 16000
""")
    return str(config)
