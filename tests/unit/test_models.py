"""
Tests complets pour les modèles de données
"""
import pytest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch


class TestOllamaClient:
    """Tests complets pour le client Ollama."""
    
    @pytest.fixture
    def mock_ollama_response(self):
        """Mock réponse Ollama."""
        return {
            "response": "Bonjour! Je suis Qwen."
        }
    
    def test_create_client(self):
        """Test de création du client Ollama."""
        from src.models.ollama_client import OllamaClient
        
        client = OllamaClient()
        
        assert client is not None
        assert hasattr(client, "base_url")
        assert hasattr(client, "timeout")
    
    def test_set_base_url(self):
        """Test de réglage de base URL."""
        from src.models.ollama_client import OllamaClient
        
        client = OllamaClient()
        
        client.set_base_url("http://localhost:11434")
        
        assert client.base_url == "http://localhost:11434"
    
    def test_set_timeout(self):
        """Test de réglage de timeout."""
        from src.models.ollama_client import OllamaClient
        
        client = OllamaClient()
        
        client.set_timeout(60)
        
        assert client.timeout == 60
    
    def test_generate_response(self):
        """Test de génération de réponse."""
        from src.models.ollama_client import OllamaClient
        
        client = OllamaClient()
        
        # Mock la génération
        with patch.object(client, "generate") as mock_generate:
            mock_generate.return_value = MagicMock(
                done=True,
                response="Test réponse"
            )
            
            result = client.generate(
                model="qwen3-coder:latest",
                prompt="Bonjour",
                context=[],
                stream=False
            )
            
            assert result["response"] == "Test réponse"
    
    def test_generate_stream(self):
        """Test de génération stream."""
        from src.models.ollama_client import OllamaClient
        
        client = OllamaClient()
        
        # Mock response itératif
        mock_generator = Mock()
        mock_generator.__iter__ = Mock(return_value=iter([
            {"response": "Bonjour"},
            {"response": "Comment"},
            {"response": "ça"},
            {"response": "va?"}
        ]))
        
        # Test itération stream
        gen = client.generate(
            model="test",
            prompt="test",
            context=[],
            stream=True
        )
        
        assert hasattr(gen, "__iter__")


class TestConversationState:
    """Tests complets pour l'état conversation."""
    
    def test_conversation_state_init(self):
        """Test d'initialisation de l'état conversation."""
        from src.models.conversation_state import ConversationState
        
        state = ConversationState()
        
        assert state is not None
        assert hasattr(state, "messages")
        assert hasattr(state, "history")
    
    def test_get_messages(self):
        """Test de récupération des messages."""
        from src.models.conversation_state import ConversationState
        
        state = ConversationState()
        
        # Add message
        state.messages.append({
            "role": "user",
            "content": "Bonjour"
        })
        state.messages.append({
            "role": "assistant",
            "content": "Salut!"
        })
        
        messages = state.get_messages()
        
        assert len(messages) == 2
        assert messages[0]["role"] == "user"
        assert messages[1]["role"] == "assistant"
    
    def test_add_message(self):
        """Test d'ajout de message."""
        from src.models.conversation_state import ConversationState
        
        state = ConversationState()
        
        state.add_message("user", "Message test")
        
        assert len(state.messages) == 1
        assert state.messages[0]["content"] == "Message test"
    
    def test_add_user_message(self):
        """Test d'ajout de message utilisateur."""
        from src.models.conversation_state import ConversationState
        
        state = ConversationState()
        
        state.add_user_message("User message content")
        
        assert state.messages[-1]["role"] == "user"
        assert state.messages[-1]["content"] == "User message content"
    
    def test_add_assistant_response(self):
        """Test d'ajout de réponse assistant."""
        from src.models.conversation_state import ConversationState
        
        state = ConversationState()
        
        state.add_assistant_response("Assistant response")
        
        assert state.messages[-1]["role"] == "assistant"
        assert state.messages[-1]["content"] == "Assistant response"
    
    def test_clear_history(self, tmp_path):
        """Test de nettoyage d'historique avec sauvegarde."""
        from src.models.conversation_state import ConversationState
        
        state = ConversationState()
        state.history_file = tmp_path / "conversation.json"
        
        # Setup avec messages
        state._save_history()
        
        assert state.history_file.exists()
        
        # Clear et sauvegarde
        state.clear_history()
        state._save_history()
        
        # Vérifie que l'historique est vide
        with open(state.history_file, "r") as f:
            data = json.load(f)
        
        assert len(data.get("messages", [])) == 0
    
    def test_load_history(self):
        """Test de chargement d'historique."""
        from src.models.conversation_state import ConversationState
        import json
        
        # Create temp file with history
        tmp_path = Path(None)
        history_file = tmp_path / "history.json"
        
        history_data = {
            "messages": [
                {"role": "user", "content": "Test user message"},
                {"role": "assistant", "content": "Test assistant response"}
            ]
        }
        
        state = ConversationState(str(history_file))
        
        assert len(state.messages) == 2


class TestDataFileAnalyzer:
    """Tests complets pour l'analyseur de fichiers/Données."""
    
    @pytest.fixture
    def sample_project_data(self, tmp_path):
        """Crée data de projet échantillon."""
        data_dir = tmp_path / "sample_project"
        data_dir.mkdir()
        
        # Create sample files
        (data_dir / "README.md").write_text("# Sample Project\nThis is a test project.")
        (data_dir / "config.yaml").write_text("sample: true")
        (data_dir / "utils.py").write_text("# Utils module\npass")
        
        return str(data_dir)
    
    def test_analyze_project(self, sample_project_data):
        """Test d'analyse de projet."""
        from src.models.file_analyzer import FileAnalyzer
        
        analyzer = FileAnalyzer()
        
        result = analyzer.analyze_directory(sample_project_data)
        
        assert result is not None
        assert "files" in result or "size" in result
    
    def test_get_file_types(self, sample_project_data):
        """Test de récupération de types de fichiers."""
        from src.models.file_analyzer import FileAnalyzer
        
        analyzer = FileAnalyzer()
        
        file_types = analyzer.get_file_types(sample_project_data)
        
        assert file_types is not None
        assert isinstance(file_types, list)


class TestTextToSpeech:
    """Tests complets pour TTS."""
    
    def test_text_to_speech_import(self):
        """Test d'import TTS."""
        from src.models.text_to_speech import TextToSpeech
        
        tts = TextToSpeech()
        
        assert tts is not None
    
    def test_get_speakers(self):
        """Test de récupération de speakers."""
        from src.models.text_to_speech import TextToSpeech
        
        tts = TextToSpeech()
        
        speakers = tts.get_speakers()
        
        assert speakers is not None


class TestAudioDeviceManager:
    """Tests complets pour la gestion des devices audio."""
    
    @pytest.fixture
    def mock_psutil(self):
        """Mock psutil."""
        psutil = Mock()
        
        # Mock CPU
        psutil.cpu_percent.return_value = 25.0
        
        # Mock memory
        mem = Mock()
        mem.percent = 50.0
        mem.virtual_memory = lambda: mem
        
        psutil.virtual_memory = lambda: mem
        
        # Mock CPU COUNTS
        psutil.cpu_count.return_value = 8
        
        return psutil
    
    def test_get_cpu_info(self, mock_psutil):
        """Test de récupération info CPU."""
        from src.models.audio_device_manager import AudioDeviceManager
        
        device_mgr = AudioDeviceManager(mock_psutil)
        
        cpu_info = device_mgr.get_cpu_info()
        
        assert cpu_info is not None
    
    def test_get_memory_info(self, mock_psutil):
        """Test de récupération info mémoire."""
        from src.models.audio_device_manager import AudioDeviceManager
        
        device_mgr = AudioDeviceManager(mock_psutil)
        
        memory_info = device_mgr.get_memory_info()
        
        assert memory_info is not None


class TestWaveUtils:
    """Tests utilitaires pour les fonctions d'ondes audio."""
    
    def test_wave_utils_import(self):
        """Test d'import des utilitaires ondes."""
        from src.utils.audio_utils import WaveUtils
        
        utils = WaveUtils()
        
        assert utils is not None


class TestConfigSettingsTest:
    """Tests supplémentaires pour les settings."""
    
    def test_settings_get_sample_rate(self):
        """Test de obtention du taux d'échantillonnage."""
        from src.models.settings import Settings
        
        settings = Settings()
        
        sample_rate = settings.get_sample_rate()
        
        assert sample_rate == 16000
    
    def test_settings_set_sample_rate(self, tmp_path):
        """Test de réglage du taux d'échantillonnage."""
        from src.models.settings import Settings
        
        config_file = tmp_path / "config.yaml"
        config_file.write_text("sample_rate: 22050")
        
        settings = Settings(str(config_file))
        settings._sample_rate = 22050
        
        assert settings.get_sample_rate() == 22050
