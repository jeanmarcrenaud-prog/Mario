# tests/unit/adapters/test_vosk_wake_word_adapter.py
import pytest
from unittest.mock import MagicMock, patch
import numpy as np
from src.adapters.vosk_wake_word_adapter import VoskWakeWordAdapter

class TestVoskWakeWordAdapter:
    @patch('src.adapters.vosk_wake_word_adapter.Model')
    @patch('src.adapters.vosk_wake_word_adapter.pyaudio.PyAudio')
    def test_initialization(self, mock_pyaudio, mock_model):
        adapter = VoskWakeWordAdapter("/fake/model/path")
        assert adapter is not None
