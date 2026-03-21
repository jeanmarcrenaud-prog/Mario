"""
Tests for core modules - simplified
"""


class TestInterfaceManager:
    """Tests InterfaceManager."""
    
    def test_interface_manager_import(self):
        """Test d'import de InterfaceManager."""
        from src.core.interface_manager import InterfaceManager
        assert InterfaceManager is not None


class TestPromptManager:
    """Tests PromptManager."""
    
    def test_prompt_manager_import(self):
        """Test d'import de PromptManager."""
        from src.core.prompt_manager import PromptManager
        assert PromptManager is not None
    
    def test_prompt_manager_init(self):
        """Test d'initialisation de PromptManager."""
        from src.core.prompt_manager import PromptManager
        manager = PromptManager()
        assert manager is not None


class TestAudioPlayer:
    """Tests AudioPlayer."""
    
    def test_audio_player_import(self):
        """Test d'import de AudioPlayer."""
        from src.utils.audio_player import AudioPlayer
        assert AudioPlayer is not None
    
    def test_audio_player_init(self):
        """Test initialisation AudioPlayer."""
        from src.utils.audio_player import AudioPlayer
        player = AudioPlayer()
        assert player is not None


class TestExceptions:
    """Tests pour les exceptions."""
    
    def test_exceptions_import(self):
        """Test d'import des exceptions."""
        from src.core.exceptions import SpeechRecognitionError, TextToSpeechError, HardwareError
        assert SpeechRecognitionError is not None
        assert TextToSpeechError is not None
        assert HardwareError is not None


class TestIntentRouterCore:
    """Tests IntentRouter."""
    
    def test_intent_router_import(self):
        """Test d'import de IntentRouter."""
        from src.core.intent_router import IntentRouter
        assert IntentRouter is not None
    
    def test_intent_router_init(self):
        """Test d'initialisation de IntentRouter."""
        from src.core.intent_router import IntentRouter
        router = IntentRouter()
        assert router is not None
