"""
Tests complets pour les services
"""
import pytest
from unittest.mock import MagicMock, Mock, patch


class TestWhisperService:
    """Tests complets pour le service Whisper."""
    
    def test_whisper_service_import(self):
        """Test d'import de WhisperService."""
        from src.core.services.whisper_service import WhisperService
        
        assert WhisperService is not None
    
    def test_whisper_service_init(self):
        """Test d'initialisation de WhisperService."""
        from src.core.services.whisper_service import WhisperService
        
        service = WhisperService()
        
        assert service is not None
    
    def test_transcribe_audio(self):
        """Test de transcription audio."""
        from src.core.services.whisper_service import WhisperService
        
        with patch('whisper.transcribe') as mock_transcribe:
            mock_transcribe.return_value = {
                "text": "Bonjour, ceci est un test",
                "language": "fr"
            }
            
            service = WhisperService()
            result = service.transcribe_audio("test.mp3")
            
            assert result["text"] == "Bonjour, ceci est un test"
    
    def test_load_model(self):
        """Test de chargement du modèle."""
        from src.core.services.whisper_service import WhisperService
        
        with patch('whisper.load_model') as mock_load:
            mock_model = Mock()
            mock_load.return_value = mock_model
            
            service = WhisperService()
            
            assert mock_load.called


class TestTTSService:
    """Tests complets pour le service TTS."""
    
    def test_tts_service_import(self):
        """Test d'import de TTSService."""
        from src.core.services.tts_service import TTSService
        
        assert TTSService is not None
    
    def test_tts_service_init(self):
        """Test d'initialisation de TTSService."""
        from src.core.services.tts_service import TTSService
        
        service = TTSService()
        
        assert service is not None
    
    def test_speak_text(self):
        """Test de synthèse vocale."""
        from src.core.services.tts_service import TTSService
        
        service = TTSService()
        service._text_to_speech = "mock_tts_instance"
        
        result = service.speak_text("Bonjour")
        
        assert result is not None
    
    def test_get_available_voices(self):
        """Test de récupération des voix disponibles."""
        from src.core.services.tts_service import TTSService
        
        service = TTSService()
        service._text_to_speech = "mock_tts_instance"
        
        voices = service.get_available_voices()
        
        assert voices is not None


class TestWakeWordService:
    """Tests complets pour le service de mot déclencheur."""
    
    def test_wake_word_service_import(self):
        """Test d'import de WakeWordService."""
        from src.core.services.wake_word_service import WakeWordService
        
        assert WakeWordService is not None
    
    def test_wake_word_service_init(self):
        """Test d'initialisation de WakeWordService."""
        from src.core.services.wake_word_service import WakeWordService
        
        with patch('pynoise.net.porcupine.Porcupine') as mock_porcupine:
            mock_porc = Mock()
            mock_porc.enable.return_value = mock_porc
            mock_porc.process.return_value = -1
            
            service = WakeWordService()
            
            assert service is not None
    
    def test_process_audio(self):
        """Test de traitement de l'audio."""
        from src.core.services.wake_word_service import WakeWordService
        
        with patch('pynoise.net.porcupine.Porcupine') as mock_porcupine:
            mock_porc = Mock()
            mock_porc.enable.return_value = mock_porc
            mock_porc.process.return_value = -1
            
            service = WakeWordService()
            
            result = service.process_audio(b"test_audio")
            
            assert result is not None
    
    def test_is_speaking(self):
        """Test de vérification de la parole."""
        from src.core.services.wake_word_service import WakeWordService
        
        with patch('pynoise.net.porcupine.Porcupine') as mock_porcupine:
            mock_porc = Mock()
            mock_porc.enable.return_value = mock_porc
            mock_porc.process.return_value = -1
            
            service = WakeWordService()
            
            speaking = service.is_speaking()
            
            assert speaking is not None


class TestSpeechRecognitionService:
    """Tests complets pour le service de reconnaissance vocale."""
    
    def test_speech_recognition_service_import(self):
        """Test d'import de SpeechRecognitionService."""
        from src.core.services.speech_recognition_service import SpeechRecognitionService
        
        assert SpeechRecognitionService is not None
    
    def test_speech_recognition_service_init(self):
        """Test d'initialisation de SpeechRecognitionService."""
        from src.core.services.speech_recognition_service import SpeechRecognitionService
        
        service = SpeechRecognitionService()
        
        assert service is not None
    
    def test_listen(self):
        """Test de lecture de l'audio."""
        from src.core.services.speech_recognition_service import SpeechRecognitionService
        
        with patch('pyaudio.PyAudio') as mock_pyaudio:
            mock_pa = Mock()
            mock_stream = Mock()
            mock_stream.read.return_value = b"test_audio_bytes"
            
            mock_pyaudio.open.return_value = mock_stream
            mock_pyaudio.init.return_value = None
            mock_pyaudio.terminate.return_value = None
            
            service = SpeechRecognitionService()
            
            result = service.listen()
            
            assert result is not None


class TestLLMService:
    """Tests complets pour le service LLM."""
    
    def test_llm_service_import(self):
        """Test d'import de LLMService."""
        from src.core.services.llm_service import LLMService
        
        assert LLMService is not None
    
    def test_llm_service_init(self):
        """Test d'initialisation de LLMService."""
        from src.core.services.llm_service import LLMService
        
        service = LLMService()
        
        assert service is not None
    
    def test_generate(self):
        """Test de génération."""
        from src.core.services.llm_service import LLMService
        
        service = LLMService()
        with patch.object(service, '_client') as mock_client:
            mock_response = Mock()
            mock_response.response = "Réponse LLM"
            mock_client.generate.return_value = mock_response
            
            result = service.generate(
                model="qwen3-coder",
                prompt="Test prompt",
                context=[]
            )
            
            assert result == "Réponse LLM"
    
    def test_stream_generate(self):
        """Test de génération stream."""
        from src.core.services.llm_service import LLMService
        
        service = LLMService()
        with patch.object(service, '_client') as mock_client:
            mock_generator = Mock()
            mock_generator.__iter__ = Mock(return_value=iter([
                {"response": "Partie 1"},
                {"response": "Partie 2"}
            ]))
            mock_client.generate.return_value = mock_generator
            
            gen = service.generate(
                model="qwen3-coder",
                prompt="Test",
                context=[],
                stream=True
            )
            
            assert hasattr(gen, "__iter__")


class TestSystemMonitor:
    """Tests complets pour le moniteur système."""
    
    @pytest.fixture
    def mock_psutil(self):
        """Mock psutil."""
        psutil = Mock()
        
        # Mock CPU
        psutil.cpu_percent.return_value = 25.0
        psutil.cpu_count.return_value = 8
        
        # Mock memory
        mem = Mock()
        mem.percent = 50.0
        psutil.virtual_memory = lambda: mem
        
        return psutil
    
    def test_system_monitor_import(self):
        """Test d'import de SystemMonitor."""
        from src.core.services.system_monitor import SystemMonitor
        
        assert SystemMonitor is not None
    
    def test_system_monitor_init(self, mock_psutil):
        """Test d'initialisation de SystemMonitor."""
        from src.core.services.system_monitor import SystemMonitor
        
        monitor = SystemMonitor(mock_psutil)
        
        assert monitor is not None
    
    def test_get_cpu_info(self, mock_psutil):
        """Test de récupération info CPU."""
        from src.core.services.system_monitor import SystemMonitor
        
        monitor = SystemMonitor(mock_psutil)
        
        cpu_info = monitor.get_cpu_info()
        
        assert cpu_info is not None
    
    def test_get_memory_info(self, mock_psutil):
        """Test de récupération info mémoire."""
        from src.core.services.system_monitor import SystemMonitor
        
        monitor = SystemMonitor(mock_psutil)
        
        memory_info = monitor.get_memory_info()
        
        assert memory_info is not None


class TestAudioPipeline:
    """Tests complets pour la pipeline audio."""
    
    def test_audio_pipeline_import(self):
        """Test d'import de AudioPipeline."""
        from src.core.services.audio_pipeline import AudioPipeline
        
        assert AudioPipeline is not None
    
    def test_audio_pipeline_init(self):
        """Test d'initialisation de AudioPipeline."""
        from src.core.services.audio_pipeline import AudioPipeline
        
        pipeline = AudioPipeline()
        
        assert pipeline is not None
    
    def test_process_audio(self):
        """Test de traitement audio."""
        from src.core.services.audio_pipeline import AudioPipeline
        
        pipeline = AudioPipeline()
        
        with patch.object(pipeline, '_resampler') as mock_resampler:
            with patch.object(pipeline, '_silence_detector') as mock_silence:
                with patch.object(pipeline, '_gain_compressor') as mock_gain:
                    mock_resampler.sample_rate = 16000
                    mock_silence.is_silent.return_value = False
                    mock_gain.compressed_audio = b"compressed_audio"
                    
                    result = pipeline.process_audio(b"input_audio")
                    
                    assert result is not None


class TestConversationHandler:
    """Tests complets pour le gestionnaire de conversation."""
    
    def test_conversation_handler_import(self):
        """Test d'import de ConversationHandler."""
        from src.core.services.conversation_handler import ConversationHandler
        
        assert ConversationHandler is not None
    
    def test_conversation_handler_init(self):
        """Test d'initialisation de ConversationHandler."""
        from src.core.services.conversation_handler import ConversationHandler
        
        handler = ConversationHandler()
        
        assert handler is not None
    
    def test_process_prompt(self):
        """Test de traitement de prompt."""
        from src.core.services.conversation_handler import ConversationHandler
        
        handler = ConversationHandler()
        handler._intent_router = Mock()
        handler._prompt_manager = Mock()
        handler._tts_service = Mock()
        handler._text_to_speech = Mock()
        
        with patch.object(handler, '_conversation_state') as mock_state:
            result = handler.process_prompt("Test prompt")
            
            assert result is not None
    
    def test_clear_conversation(self):
        """Test de nettoyage de conversation."""
        from src.core.services.conversation_handler import ConversationHandler
        
        handler = ConversationHandler()
        
        result = handler.clear_conversation()
        
        assert result is True


class TestPromptManager:
    """Tests complets pour le gestionnaire de prompts."""
    
    def test_prompt_manager_import(self):
        """Test d'import de PromptManager."""
        from src.core.services.prompt_manager import PromptManager
        
        assert PromptManager is not None
    
    def test_prompt_manager_init(self):
        """Test d'initialisation de PromptManager."""
        from src.core.services.prompt_manager import PromptManager
        
        manager = PromptManager()
        
        assert manager is not None
    
    def test_generate_prompt_text(self):
        """Test de génération de texte de prompt."""
        from src.core.services.prompt_manager import PromptManager
        
        manager = PromptManager()
        
        result = manager.generate_prompt_text(
            role="developer",
            content="Test content",
            custom_variables={}
        )
        
        assert result is not None
    
    def test_create_system_personality_prompt(self):
        """Test de création de prompt de personnalité système."""
        from src.core.services.prompt_manager import PromptManager
        
        manager = PromptManager()
        
        result = manager.create_system_personality_prompt("mario", "fr_FR")
        
        assert result is not None
    
    def test_create_system_instructions(self):
        """Test de création d'instructions système."""
        from src.core.services.prompt_manager import PromptManager
        
        manager = PromptManager()
        
        result = manager.create_system_instructions("mario", "fr_FR")
        
        assert result is not None


class TestGradioWebInterface:
    """Tests complets pour l'interface Gradio."""
    
    def test_gradio_web_interface_import(self):
        """Test d'import de GradioWebInterface."""
        from src.views.web_interface_gradio import GradioWebInterface
        
        assert GradioWebInterface is not None
    
    def test_gradio_web_interface_init(self):
        """Test d'initialisation de GradioWebInterface."""
        from src.views.web_interface_gradio import GradioWebInterface
        
        with patch('gradio.Blocks') as mock_blocks:
            interface = GradioWebInterface(mock_blocks)
            
            assert interface is not None
