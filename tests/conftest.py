# tests/conftest.py
import sys
import os
import pytest
import numpy as np
from unittest.mock import Mock, MagicMock

# Ajouter src au path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

@pytest.fixture
def sample_audio():
    """Fixture pour audio de test (1 seconde de silence)"""
    return np.zeros(16000, dtype=np.int16)

@pytest.fixture
def sample_audio_2sec():
    """Fixture pour audio de test (2 secondes)"""
    return np.zeros(32000, dtype=np.int16)

@pytest.fixture
def mock_assistant():
    """Fixture pour un assistant mocké"""
    from unittest.mock import MagicMock
    assistant = MagicMock()
    assistant.settings = Mock()
    assistant.settings.microphone_index = 1
    assistant.settings.voice_name = "fr_FR-siwis-medium"
    assistant.settings.llm_model = "qwen3-coder:latest"
    return assistant

@pytest.fixture
def mock_assistant_init():
    """Fixture assistant mocké avec initialisation complète"""
    from unittest.mock import Mock, MagicMock
    assistant = MagicMock()
    assistant.settings = Mock()
    assistant.settings.microphone_index = 1
    assistant.settings.voice_name = "fr_FR-siwis-medium"
    assistant.settings.llm_model = "qwen3-coder:latest"
    assistant.settings.web_port = 7860
    assistant.settings.sample_rate = 16000
    assistant.display_message = Mock(return_value=True)
    assistant.process_audio = Mock(return_value={"text": "test"})
    return assistant

@pytest.fixture
def conversation_history():
    """Fixture pour un historique de conversation"""
    return [
        {"role": "user", "content": "Bonjour"},
        {"role": "assistant", "content": "Bonjour ! Comment puis-je vous aider ?"}
    ]

@pytest.fixture
def dummy_microphone():
    """Fixture pour microphone faux"""
    from unittest.mock import MagicMock, Mock
    mic = Mock()
    mic.start = Mock(return_value=Mock())
    mic.stop = Mock(return_value=Mock())
    mic.close = Mock(return_value=Mock())
    mic.is_microphone_available = Mock(return_value=True)
    return mic

@pytest.fixture
def mock_ollama_client():
    """Mock OllamaClient avec tous les attrs/methods"""
    from unittest.mock import Mock, PropertyMock
    client = Mock()
    client.base_url = "http://localhost:11434"
    
    # Créer un timeout mutable qui peut être changé par set_timeout
    class MutableTimeout:
        def __init__(self, initial):
            self._value = initial
        @property
        def value(self):
            return self._value
        @value.setter
        def value(self, v):
            self._value = v
    
    timeout_obj = MutableTimeout(120)
    
    # Mock set_timeout pour mettre à jour le timeout
    def mock_set_timeout(timeout):
        timeout_obj.value = timeout
    
    client.set_base_url = Mock(return_value=None)
    client.set_timeout = Mock(side_effect=mock_set_timeout, return_value=None)
    
    # Propriété timeout qui retourne la valeur mutable
    type(client).timeout = PropertyMock(side_effect=lambda: timeout_obj.value)
    
    client.generate = Mock(return_value={"response": "test"})
    client.chat = Mock(return_value={"message": {"content": "response"}})
    client.list = Mock(return_value={"models": []})
    client.show = Mock(return_value={"modelformat": {"name": "llama2"}})
    return client

@pytest.fixture
def mock_conversation_state():
    """Mock ConversationState avec history et méthodes"""
    from unittest.mock import Mock
    state = Mock()
    state.messages = []
    state.history = []
    state.add_message = Mock()
    state.get_messages = Mock(return_value=state.messages)
    state.add_user_message = Mock(side_effect=lambda content: state.add_message("user", content))
    state.add_assistant_response = Mock(side_effect=lambda content: state.add_message("assistant", content))
    state.clear_history = Mock(side_effect=lambda: state.history.clear())
    state.history_file = None
    state._save_history = Mock()
    state.delete_last_n_messages = Mock(side_effect=lambda n: state.messages.pop())
    return state

@pytest.fixture
def mock_file_analyzer():
    """Mock FileAnalyzer pour analyse de fichier"""
    from unittest.mock import Mock
    analyzer = Mock()
    analyzer.analyze_directory = Mock(return_value={"files": []})
    analyzer.get_file_types = Mock(return_value=[".py", ".md"])
    analyzer.analyze_file = Mock(return_value="Analyse terminée")
    analyzer._get_content = Mock(return_value="")
    return analyzer

@pytest.fixture
def mock_text_to_speech():
    """Mock TextToSpeech"""
    from unittest.mock import Mock
    tts = Mock()
    tts.get_speakers = Mock(return_value=["speaker_1", "speaker_2"])
    tts.speak = Mock(return_value=True)
    tts.get_available_voices = Mock(return_value=["fr_FR", "en_US"])
    return tts

@pytest.fixture
def mock_audio_device_manager():
    """Mock AudioDeviceManager"""
    from unittest.mock import Mock
    device_mgr = Mock()
    device_mgr.get_cpu_info = Mock(return_value=Mock(cpu_percent=25.0))
    device_mgr.get_memory_info = Mock(return_value=Mock(percent=50.0, virtual=8192))
    device_mgr.get_disk_info = Mock(return_value=Mock(usage=50.0))
    device_mgr.get_total_cpu = Mock(return_value=8)
    return device_mgr

@pytest.fixture
def mock_wave_utils():
    """Mock WaveUtils"""
    from unittest.mock import Mock
    utils = Mock()
    utils.wave_read = Mock(return_value=Mock(data=b"test"))
    utils.wave_write = Mock(return_value=True)
    utils.get_wave_info = Mock(return_value={"channels": 1, "rate": 16000})
    return utils

@pytest.fixture
def mock_settings():
    """Mock Settings"""
    from unittest.mock import Mock
    settings = Mock()
    settings.chunk_size = 1024
    settings.audio_buffer_size = 3
    settings.enable_low_latency = False
    settings.voice_name = ["fr_FR-siwis-medium"]
    settings.llm_model = ["qwen3-coder"]
    settings.get_sample_rate = Mock(return_value=16000)
    settings.invalid_voice_names = ["invalid", "bad"]
    settings.invalid_llm_models = ["invalid-model"]
    settings.microphone_index = 1
    settings.get_microphone_index = Mock(return_value=1)
    return settings

@pytest.fixture
def mock_config_manager():
    """Mock ConfigManager avec tous les attributs"""
    from unittest.mock import Mock
    cfg = Mock()
    cfg.default_microphone_index = 1
    cfg.default_voice = "fr_FR-siwis-medium"
    cfg.default_model = "qwen3-coder:latest"
    cfg.web_port = 7860
    cfg.sample_rate = 16000
    cfg.voice_name = "fr_FR-siwis-medium"
    cfg.llm_model = "qwen3-coder:latest"
    cfg.performance = Mock()
    cfg.performance.auto_optimize = True
    cfg.performance.alert_thresholds = Mock()
    cfg.performance.alert_thresholds.cpu_max = 80.0
    cfg.performance.alert_thresholds.memory_max = 85.0
    cfg.performance.alert_thresholds.disk_max = 90.0
    cfg.log_level = "INFO"
    cfg.save = Mock()
    cfg._parse_settings = Mock(return_value=Mock())
    cfg.get_cpu_percent = Mock(return_value=25.0)
    cfg.get_memory_percent = Mock(return_value=50.0)
    return cfg

@pytest.fixture
def config_manager_tmp(tmp_path):
    """ConfigManager pour tests de configuration"""
    from src.config.config import ConfigManager
    config_file = tmp_path / "config_test.yaml"
    content = """
default_microphone_index: 1
default_voice: "fr_FR-siwis-medium"
default_model: "qwen3-coder:latest"
web_port: 7860
sample_rate: 16000
performance:
  auto_optimize: true
  alert_thresholds:
    cpu_max: 80.0
    memory_max: 85.0
log_level: INFO
"""
    config_file.write_text(content)
    cfg = ConfigManager(str(config_file))
    return cfg

# ========== FIXTURES VIEWS ==========

@pytest.fixture
def mock_console_view():
    """Mock ConsoleView"""
    from unittest.mock import Mock
    view = Mock()
    view.assistant = Mock()
    view.display_message = Mock(return_value=True)
    view.display_error = Mock(return_value=None)
    view.reset = Mock(return_value=None)
    return view

@pytest.fixture
def mock_welcome_screen():
    """Mock show_welcome_screen"""
    from unittest.mock import Mock, patch
    console = Mock()
    console.print = Mock(return_value=None)
    console.run = Mock(return_value=None)
    return console

@pytest.fixture
def mock_analysis_manager():
    """Mock AnalysisManager"""
    from unittest.mock import Mock
    manager = Mock()
    manager.analyze_file = Mock(return_value="Analyse terminée")
    manager.analyze_directory = Mock(return_value={"files": []})
    manager.get_stats = Mock(return_value={"lines": 0, "files": 0})
    return manager

@pytest.fixture
def mock_epaper_view():
    """Mock EpaperView"""
    from unittest.mock import Mock
    view = Mock()
    view.assistant = Mock()
    view.update = Mock(return_value=True)
    view.display_text = Mock(return_value=None)
    return view

@pytest.fixture
def mock_interface_helpers():
    """Mock InterfaceHelpers"""
    from unittest.mock import Mock
    helpers = Mock()
    helpers.format_message = Mock(return_value="Formatted")
    helpers.format_prompt = Mock(return_value="FormattedPrompt")
    helpers.format_analysis = Mock(return_value="FormattedAnalysis")
    return helpers

# ========== FIXTURES SERVICES ==========

@pytest.fixture
def mock_audio_pipeline():
    """Mock AudioPipeline"""
    from unittest.mock import Mock
    pipeline = Mock()
    pipeline.process_audio = Mock(return_value={"text": "test"})
    pipeline.transcribe = Mock(return_value={"text": "test"})
    return pipeline

@pytest.fixture
def mock_tts_service():
    """Mock TTSService"""
    from unittest.mock import Mock
    service = Mock()
    service.speak = Mock(return_value=True)
    service.get_available_voices = Mock(return_value=["fr_FR", "en_US"])
    return service

@pytest.fixture
def mock_wake_word_service():
    """Mock WakeWordService"""
    from unittest.mock import Mock
    service = Mock()
    service.detect_wake_word = Mock(return_value=True)
    service.is_speaking = Mock(return_value=False)
    return service

@pytest.fixture
def mock_speech_recognition_service():
    """Mock SpeechRecognitionService"""
    from unittest.mock import Mock
    service = Mock()
    service.transcribe = Mock(return_value={"text": "test"})
    service.listen = Mock(return_value=b"test_audio")
    return service

@pytest.fixture
def mock_llm_service():
    """Mock LLMService"""
    from unittest.mock import Mock
    service = Mock()
    service.generate_response = Mock(return_value="Réponse")
    service.generate_analysis = Mock(return_value="Analyse")
    service.generate_recommendations = Mock(return_value=["Recommandation"])
    service.test_service = Mock(return_value=True)
    service.get_available_models = Mock(return_value=["model1", "model2"])
    return service

@pytest.fixture
def mock_system_monitor():
    """Mock SystemMonitor"""
    from unittest.mock import Mock
    monitor = Mock()
    monitor.get_cpu_percent = Mock(return_value=25.0)
    monitor.get_memory_percent = Mock(return_value=50.0)
    monitor.get_disk_percent = Mock(return_value=70.0)
    monitor.get_cpu_info = Mock(return_value={"cpu_freq": 3000, "cpu_times": {}})
    monitor.get_memory_info = Mock(return_value=Mock(virtual=8192, percent=50.0))
    return monitor

@pytest.fixture
def mock_audio_pipeline_components():
    """Mock composants AudioPipeline"""
    from unittest.mock import Mock
    whisper = Mock()
    whisper.transcribe.return_value = {"text": "test"}
    
    wake = Mock()
    wake.detect_wake_word.return_value = True
    
    speech = Mock()
    speech.transcribe.return_value = {"text": "test"}
    
    tts = Mock()
    tts.speak.return_value = True
    
    settings = Mock()
    settings.sample_rate = 16000
    
    return whisper, wake, speech, tts, settings

@pytest.fixture
def mock_conversation_handler():
    """Mock ConversationHandler"""
    from unittest.mock import Mock
    handler = Mock()
    handler.process_prompt = Mock(return_value="Processed prompt")
    handler.clear_conversation = Mock(return_value=True)
    handler.add_message = Mock(return_value=None)
    return handler

@pytest.fixture
def mock_prompt_manager():
    """Mock PromptManager"""
    from unittest.mock import Mock
    manager = Mock()
    manager.generate_prompt_text = Mock(return_value="Prompt text")
    manager.create_system_personality_prompt = Mock(return_value="System prompt")
    manager.create_system_instructions = Mock(return_value="System instructions")
    return manager

@pytest.fixture
def mock_gradio_web_interface():
    """Mock GradioWebInterface"""
    from unittest.mock import Mock
    interface = Mock()
    interface.launch = Mock(return_value=Mock(share=False))
    interface.show = Mock(return_value=None)
    return interface

@pytest.fixture
def mock_project_analyzer_service():
    """Mock ProjectAnalyzerService"""
    from unittest.mock import Mock
    service = Mock()
    service.analyze = Mock(return_value={"complexity": "low", "status": "healthy"})
    service.get_issues = Mock(return_value=[])
    service.get_recommendations = Mock(return_value=[])
    return service

@pytest.fixture
def mock_dummy_audio_input():
    """Mock DummyAudioInput"""
    from unittest.mock import Mock
    input = Mock()
    input.start = Mock(return_value=Mock())
    input.stop = Mock(return_value=Mock())
    input.close = Mock(return_value=Mock())
    input.get_stream = Mock(return_value=Mock())
    return input

@pytest.fixture
def mock_dummy_audio_output():
    """Mock DummyAudioOutput"""
    from unittest.mock import Mock
    output = Mock()
    output.speak = Mock(return_value=True)
    output.stop = Mock(return_value=True)
    output.close = Mock(return_value=True)
    return output

@pytest.fixture
def mock_vosk_adapter():
    """Mock VoskWakeWordAdapter"""
    from unittest.mock import Mock
    adapter = Mock()
    adapter.is_available = True
    adapter.load_model = Mock(return_value=True)
    adapter.detect_wake_word = Mock(return_value=True)
    adapter.is_speaking = Mock(return_value=False)
    return adapter

@pytest.fixture
def mock_whisper_adapter():
    """Mock WhisperAdapter"""
    from unittest.mock import Mock
    adapter = Mock()
    adapter.transcribe = Mock(return_value={"text": "test text"})
    return adapter
# Fin des fixtures
