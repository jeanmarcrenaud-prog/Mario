import pytest
from unittest.mock import MagicMock

# Import the factory functions
from src.core.app_factory import create_assistant, create_assistant_with_simulation

# Helper fixture to mock dependencies
@pytest.fixture
def mock_dependencies(monkeypatch):
    # Create a DummySettings class with a from_config classmethod
    class DummySettings:
        voice_name = "dummy_voice"
        llm_model = "dummy_model"

        @classmethod
        def from_config(cls, cfg):
            return cls()

    # Patch Settings and config
    monkeypatch.setattr("src.core.app_factory.Settings", DummySettings)
    monkeypatch.setattr("src.core.app_factory.config", {}, raising=False)

    # Mock MicrophoneChecker to always return True
    mic_mock = MagicMock()
    mic_mock.is_microphone_available.return_value = True
    monkeypatch.setattr("src.core.app_factory.MicrophoneChecker", lambda: mic_mock)

    # Mock TTSService factory
    tts_mock = MagicMock(name="TTSServiceMock")
    monkeypatch.setattr("src.core.app_factory.TTSService", type("TTSServiceMockClass", (), {
        "create_with_piper": staticmethod(lambda *args, **kwargs: tts_mock)
    }))

    # Mock WakeWordService factory
    wake_mock = MagicMock(name="WakeWordServiceMock")
    monkeypatch.setattr("src.core.app_factory.WakeWordService", type("WakeWordServiceMockClass", (), {
        "create_with_vosk": staticmethod(lambda *args, **kwargs: wake_mock)
    }))

    # Mock SpeechRecognitionService factory
    sr_mock = MagicMock(name="SpeechRecognitionServiceMock")
    monkeypatch.setattr("src.core.app_factory.create_speech_recognition_service_prod", lambda *a, **k: sr_mock)

    # Mock LLMService factory
    llm_mock = MagicMock(name="LLMServiceMock")
    monkeypatch.setattr("src.core.app_factory.LLMService", type("LLMServiceMockClass", (), {
        "create_with_ollama": staticmethod(lambda *args, **kwargs: llm_mock)
    }))

    # Mock ProjectAnalyzerService
    pa_mock = MagicMock(name="ProjectAnalyzerServiceMock")
    monkeypatch.setattr("src.core.app_factory.ProjectAnalyzerService", lambda *args, **kwargs: pa_mock)

    # Mock SystemMonitor and PerformanceOptimizer
    sm_mock = MagicMock(name="SystemMonitorMock")
    po_mock = MagicMock(name="PerformanceOptimizerMock")
    po_mock.start_monitoring = MagicMock()
    monkeypatch.setattr("src.core.app_factory.SystemMonitor", lambda: sm_mock)
    monkeypatch.setattr("src.core.app_factory.PerformanceOptimizer", lambda: po_mock)

    # Mock logger
    monkeypatch.setattr("src.core.app_factory.logger", MagicMock())

    return {
        "tts": tts_mock,
        "wake": wake_mock,
        "sr": sr_mock,
        "llm": llm_mock,
        "pa": pa_mock,
        "sm": sm_mock,
        "po": po_mock
    }


def test_create_assistant_happy_path(mock_dependencies):
    assistant = create_assistant()
    from src.main import AssistantVocal
    assert isinstance(assistant, AssistantVocal)

    assert assistant.tts_service is mock_dependencies["tts"]
    assert assistant.wake_word_service is mock_dependencies["wake"]
    assert assistant.speech_recognition_service is mock_dependencies["sr"]
    assert assistant.llm_service is mock_dependencies["llm"]
    assert assistant.project_analyzer_service is mock_dependencies["pa"]
    assert assistant.system_monitor is mock_dependencies["sm"]
    assert assistant.performance_optimizer is mock_dependencies["po"]

    mock_dependencies["po"].start_monitoring.assert_called_once()


def test_create_assistant_without_microphone(monkeypatch):
    # monkeypatch MicrophoneChecker to return False
    mac_mock = MagicMock()
    mac_mock.is_microphone_available.return_value = False
    monkeypatch.setattr("src.core.app_factory.MicrophoneChecker", lambda: mac_mock)

    # monkeypatch Settings to avoid error
    class Dummy:
        @classmethod
        def from_config(cls, cfg):
            return Dummy()
    monkeypatch.setattr("src.core.app_factory.Settings", Dummy)
    monkeypatch.setattr("src.core.app_factory.config", {}, raising=False)

    # Should raise RuntimeError
    with pytest.raises(RuntimeError) as excinfo:
        create_assistant()
    assert "Microphone non disponible" in str(excinfo.value)

