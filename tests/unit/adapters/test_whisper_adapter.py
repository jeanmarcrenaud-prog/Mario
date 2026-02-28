import pytest
import numpy as np
import sys
from types import SimpleNamespace

# Import adapter
from src.adapters.speech_recognition_whisper_adapter import WhisperSpeechRecognitionAdapter

@pytest.fixture
def mock_whisper(monkeypatch):
    # Mock whisper to provide a model with predictable transcribe output
    dummy_model = SimpleNamespace(transcribe=lambda audio, language="fr", fp16=False: {"text": "transcribed_15"})
    monkeypatch.setitem(sys.modules, "whisper", SimpleNamespace(load_model=lambda name: dummy_model))
    # Mock torch.cuda.is_available
    monkeypatch.setitem(sys.modules, "torch", SimpleNamespace(cuda=SimpleNamespace(is_available=lambda: False)))

@pytest.fixture
def silence_logger(monkeypatch):
    class DummyLogger:
        def info(self, *args, **kwargs):
            pass
        def error(self, *args, **kwargs):
            pass
    monkeypatch.setattr("src.adapters.speech_recognition_whisper_adapter.logger", DummyLogger())


def test_whisper_adapter_success(mock_whisper, silence_logger):
    adapter = WhisperSpeechRecognitionAdapter("tiny")
    assert adapter.model is not None
    audio = np.array([1,2,3,4,5], dtype=np.int16)
    text = adapter.transcribe_array(audio)
    assert text == "transcribed_15"
    text_file = adapter.transcribe_file("dummy.wav")
    assert text_file == "transcribed_15"
