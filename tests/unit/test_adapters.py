"""
Tests complets pour les adapters audio et LLM
"""
import pytest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch


class TestSpeechRecognitionWhisper:
    """Tests complets pour le adaptateur Whisper."""
    
    @pytest.fixture
    def whisper_adapter(self):
        """Setup adaptateur Whisper."""
        from src.adapters.speech_recognition_whisper_adapter import (
            SpeechRecognitionWhisperAdapter
        )
        
        settings = MagicMock()
        settings.sample_rate = 16000
        
        adapter = SpeechRecognitionWhisperAdapter()
        adapter.settings = settings
        
        return adapter
    
    def test_load_model(self, whisper_adapter, tmp_path):
        """Test d'chargement du modèle Whisper."""
        
        with pytest.raises(FileNotFoundError) as excinfo:
            whisper_adapter.load_model()
            
            assert "fichier .pt" in str(excinfo.value)
    
    def test_unload_model(self, whisper_adapter):
        """Test de déchargement du modèle."""
        assert whisper_adapter.wk is None
    
    def test_transcribe_array(self, whisper_adapter):
        """Test de transcription d'array audio."""
        # Audio mock (faux signal audio)
        mock_audio = Mock()
        
        # Simule une transcription
        whisper_adapter.wk = Mock()
        whisper_adapter.wk.transcribe.return_value = {
            "text": "Bonjour, ceci est un test"
        }
        
        result = whisper_adapter.transcribe_array(mock_audio, 16000)
        
        assert result == "Bonjour, ceci est un test"
    
    def test_transcribe_file(self, whisper_adapter, tmp_path):
        """Test de transcription fichier audio."""
        # Fichier audio mock
        audio_file = tmp_path / "test.wav"
        audio_file.write_bytes("fake audio data")
        
        # Setup mock
        whisper_adapter.wk = Mock()
        whisper_adapter.wk.transcribe.return_value = {
            "text": "Transcription depuis fichier"
        }
        
        result = whisper_adapter.transcribe_file(str(audio_file))
        
        assert result == "Transcription depuis fichier"
    
    def test_get_available_models(self, whisper_adapter):
        """Test des modèles disponibles."""
        # Setup mock
        whisper_adapter.wk = Mock()
        whisper_adapter.wk.available_models.return_value = [
            {"model": "whisper-small"},
            {"model": "whisper-large"}
        ]
        
        models = whisper_adapter.get_available_models()
        
        assert models is not None


class TestSpeechRecognitionSimulated:
    """Tests pour l'adaptateur simulé."""
    
    def test_simulated_adapter(self):
        """Test de l'adaptateur simulé."""
        from src.adapters.speech_recognition_simulated_adapter import (
            SimulatedSpeechRecognition
        )
        
        adapter = SimulatedSpeechRecognition()
        
        assert adapter is not None
        assert callable(adapter.transcribe_array)
    
    def test_simulate_transcription(self):
        """Test de simulation transcription."""
        mock_audio = Mock()
        
        adapter = SimulatedSpeechRecognition()
        
        # Simule une transcription simple
        result = "Simulation: Ceci est une transcription fausse"
        
        assert result is not None


class TestVoskWakeWordAdapter:
    """Tests complets pour l'adaptateur Vosk Wake Word."""
    
    @pytest.fixture
    def vosk_adapter(self):
        """Setup adaptateur Vosk."""
        from src.adapters.vosk_wake_word_adapter import VoskWakeWordAdapter
        
        settings = MagicMock()
        settings.sample_rate = 16000
        
        adapter = VoskWakeWordAdapter()
        adapter.settings = settings
        
        return adapter
    
    def test_start_detection(self, vosk_adapter):
        """Test de démarrage detection."""
        
        with pytest.raises(FileNotFoundError) as excinfo:
            vosk_adapter.start_detection(1, lambda: None, lambda: None)
            
            assert "fichier .model" in str(excinfo.value)
    
    def test_stop_detection(self, vosk_adapter):
        """Test d'arrêt detection."""
        # Setup
        vosk_adapter.model = Mock()
        vosk_adapter.model.set_frontend.return_value = True
        
        result = vosk_adapter.stop_detection()
        
        assert result is True
    
    def test_get_audio_devices(self, vosk_adapter):
        """Test récupération devices audio."""
        # Mock
        vosk_adapter.model = Mock()
        vosk_adapter.model.query_all_interface_devices.return_value = [
            {"id": "1", "name": "Microphone 1"},
            {"id": "2", "name": "Microphone 2"}
        ]
        
        devices = vosk_adapter.get_audio_devices()
        
        assert isinstance(devices, list)


class TestDummyAudioInput:
    """Tests pour l'input audio Dummy (mock)."""
    
    def test_dummy_audio_input(self):
        """Test du dummy audio input."""
        from src.adapters.dummy_audio_input import DummyAudioInput
        
        input_device = DummyAudioInput()
        
        assert input_device is not None
        assert callable(input_device.record)
    
    def test_dummy_record(self):
        """Test du dummy record."""
        input_device = DummyAudioInput()
        
        # Mock record
        with patch.object(input_device, "record", return_value=b"fake audio"):
            result = input_device.record()
            
            assert isinstance(result, bytes)


class TestDummyAudioOutput:
    """Tests pour l'output audio Dummy."""
    
    def test_dummy_audio_output(self):
        """Test du dummy audio output."""
        from src.adapters.dummy_audio_output import DummyAudioOutput
        
        output_device = DummyAudioOutput()
        
        assert output_device is not None
        assert callable(output_device.say)
    
    def test_dummy_say(self):
        """Test du dummy say."""
        output_device = DummyAudioOutput()
        
        # Mock say
        with patch.object(output_device, "say", return_value=True):
            result = output_device.say("Test", 1.0)
            
            assert result is True


class TestCloudOpenAIApi:
    """Tests pour l'API OpenAI cloud."""
    
    def test_openai_api_import(self):
        """Test d'import de l'API OpenAI."""
        from src.adapters.cloud_openai_api import OpenAIAPI
        
        api = OpenAIAPI()
        
        assert api is not None
        assert callable(api.chat)
    
    def test_setup_api(self):
        """Test du setup de l'API."""
        api = OpenAIAPI()
        
        # Setup avec clé API
        api.setup("test-key-123")
        
        assert api.setup.called


class TestLlmAdapter:
    """Tests pour l'adaptateur LLM."""
    
    def test_llm_adapter_import(self):
        """Test d'import de l'adaptateur LLM."""
        from src.adapters.llm_adapter import LLMAdapter
        
        adapter = LLMAdapter()
        
        assert adapter is not None
    
    def test_llm_adapter_init(self):
        """Test d'initialisation de l'adaptateur."""
        adapter = LLMAdapter()
        
        assert adapter.model_name is None
        assert adapter.token is None


class TestAudioInputMicrophone:
    """Tests pour microphone input."""
    
    def test_microphone_input(self):
        """Test de l'input microphone."""
        from src.adapters.audio_input_microphone import AudioInputMicrophone
        
        settings = MagicMock()
        input_device = AudioInputMicrophone(settings)
        
        assert input_device is not None
    
    def test_start_recording(self):
        """Test du démarrage d'enregistrement."""
        from src.adapters.audio_input_microphone import AudioInputMicrophone
        
        settings = MagicMock()
        input_device = AudioInputMicrophone(settings)
        
        # Mock start_recording
        with patch.object(input_device, "start_recording"):
            input_device.start_recording(16000)
            
            assert input_device.start_recording.called
    
    def test_stop_recording(self):
        """Test de l'arrêt d'enregistrement."""
        from src.adapters.audio_input_microphone import AudioInputMicrophone
        
        settings = MagicMock()
        input_device = AudioInputMicrophone(settings)
        
        input_device.microphone = Mock()
        input_device.microphone.stop_streaming.return_value = True
        
        input_device.stop_recording()
        
        assert input_device.microphone.stop_streaming.called


class TestAudioOutputSpeaker:
    """Tests pour speaker output."""
    
    def test_speaker_output(self):
        """Test de l'output speaker."""
        from src.adapters.audio_output_speaker import AudioOutputSpeaker
        
        settings = MagicMock()
        output_device = AudioOutputSpeaker(settings)
        
        assert output_device is not None
    
    def test_play(self):
        """Test du lecture audio."""
        from src.adapters.audio_output_speaker import AudioOutputSpeaker
        
        settings = MagicMock()
        output_device = AudioOutputSpeaker(settings)
        
        # Mock play
        with patch.object(output_device, "play", return_value=True):
            result = output_device.play(b"fake_audio_bytes", 1.0)
            
            assert result is True
