"""
Tests simplifiés pour les adapters
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestDummyAudioInput:
    """Tests pour dummy_audio_input.py"""
    
    def test_dummy_input_record(self):
        """Test d'enregistrement."""
        from src.adapters.dummy_audio_input import DummyAudioInput
        
        audio_input = DummyAudioInput()
        
        result = audio_input.record()
        
        assert result == b"dummy_audio_data"
        assert isinstance(result, bytes)


class TestDummyAudioOutput:
    """Tests pour dummy_audio_output.py"""
    
    def test_dummy_output_say(self):
        """Test de synthèse vocale."""
        from src.adapters.dummy_audio_output import DummyAudioOutput
        
        audio_output = DummyAudioOutput()
        
        result = audio_output.say("test message")
        
        assert result is True
    
    def test_dummy_output_with_speed(self):
        """Test avec vitesse personnalisée."""
        from src.adapters.dummy_audio_output import DummyAudioOutput
        
        audio_output = DummyAudioOutput()
        
        result = audio_output.say("test", speed=1.5)
        
        assert result is True


class TestIAudioInputInterface:
    """Tests pour l'interface IAudioInput"""
    
    def test_iaudio_input_is_abstract(self):
        """Test que IAudioInput est abstrait."""
        from src.adapters.interfaces import IAudioInput
        
        # Cannot instantiate abstract class
        with pytest.raises(TypeError):
            IAudioInput()


class TestIAudioOutputInterface:
    """Tests pour l'interface IAudioOutput"""
    
    def test_iaudio_output_is_abstract(self):
        """Test que IAudioOutput est abstrait."""
        from src.adapters.interfaces import IAudioOutput
        
        # Cannot instantiate abstract class
        with pytest.raises(TypeError):
            IAudioOutput()
    
    def test_iaudio_output_say_signature(self):
        """Test de la signature de say."""
        from src.adapters.interfaces import IAudioOutput
        
        class MockOutput(IAudioOutput):
            def say(self, text: str, speed: float = 1.0) -> bool:
                return True
        
        output = MockOutput()
        
        assert output.say("test") is True
        assert output.say("test", 1.5) is True


class TestAudioInputMicrophoneAdapter:
    """Tests pour audio_input_microphone.py"""
    
    def test_audio_input_adapter_init(self):
        """Test d'initialisation."""
        from src.adapters.audio_input_microphone import AudioInputAdapter
        from unittest.mock import Mock
        
        config = Mock()
        
        adapter = AudioInputAdapter(config)
        
        assert adapter is not None
        assert adapter.is_listening is False
    
    def test_audio_input_set_callbacks(self):
        """Test de设定 des callbacks."""
        from src.adapters.audio_input_microphone import AudioInputAdapter
        from unittest.mock import Mock
        
        config = Mock()
        
        adapter = AudioInputAdapter(config)
        
        audio_callback = Mock()
        adapter.set_audio_callback(audio_callback)
        
        assert adapter.audio_callback == audio_callback
    
    def test_audio_input_get_devices(self):
        """Test de récupération des appareils."""
        from src.adapters.audio_input_microphone import AudioInputAdapter
        from unittest.mock import Mock, patch
        
        config = Mock()
        
        with patch('src.adapters.audio_input_microphone.PvRecorder') as mock_recorder:
            mock_recorder.get_available_devices.return_value = ["device1", "device2"]
            
            adapter = AudioInputAdapter(config)
            devices = adapter.get_audio_devices()
            
            assert isinstance(devices, list)


class TestAdapterInterfacesModule:
    """Tests pour le module interfaces.py"""
    
    def test_module_imports(self):
        """Test des imports du module."""
        from src.adapters import interfaces
        
        assert hasattr(interfaces, 'IAudioInput')
        assert hasattr(interfaces, 'IAudioOutput')


class TestAdaptersPackage:
    """Tests pour le package adapters"""
    
    def test_package_imports(self):
        """Test des imports du package."""
        from src import adapters
        
        assert adapters is not None


class TestAudioOutputSpeakerAdapter:
    """Tests pour audio_output_speaker.py"""
    
    def test_speaker_adapter_init(self):
        """Test d'initialisation."""
        from src.adapters.audio_output_speaker import AudioOutputAdapter
        from unittest.mock import Mock
        
        config = Mock()
        
        adapter = AudioOutputAdapter(config)
        
        assert adapter is not None


class TestLLMAdapterNew:
    """Tests pour llm_adapter.py"""
    
    def test_llm_adapter_init(self):
        """Test d'initialisation."""
        from src.adapters.llm_adapter import LLMAdapter
        from unittest.mock import Mock
        
        config = Mock()
        
        adapter = LLMAdapter(config)
        
        assert adapter is not None


class TestCloudOpenAIAPI:
    """Tests pour cloud_openai_api.py"""
    
    def test_openai_adapter_init(self):
        """Test d'initialisation."""
        from src.adapters.cloud_openai_api import OpenAIAdapter
        from unittest.mock import Mock
        
        config = Mock()
        
        adapter = OpenAIAdapter(config)
        
        assert adapter is not None


class TestDisplayEpaperAdapter:
    """Tests pour display_epaper.py"""
    
    def test_epaper_adapter_init(self):
        """Test d'initialisation."""
        from src.adapters.display_epaper import EpaperDisplay
        from unittest.mock import Mock
        
        config = Mock()
        
        display = EpaperDisplay(config)
        
        assert display is not None
