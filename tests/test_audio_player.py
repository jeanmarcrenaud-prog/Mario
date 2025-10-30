import sys
import pathlib
import pytest
import time
import threading
import numpy as np
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from src.utils.audio_player import AudioPlayer

@pytest.fixture
def mock_pyaudio(monkeypatch):
    mock_instance = MagicMock()
    mock_stream = MagicMock()

    # Use MagicMock for open instead of a regular function
    mock_instance.open = MagicMock(return_value=mock_stream)
    monkeypatch.setattr("pyaudio.PyAudio", lambda: mock_instance)
    return mock_instance, mock_stream

def test_play_beep_sets_is_playing(mock_pyaudio):
    mock_instance, mock_stream = mock_pyaudio
    player = AudioPlayer()
    assert not player.is_playing, "L'état doit être inactif au démarrage"
    player.play_beep(frequency=1000, duration=0.05)
    time.sleep(0.2)
    assert not player.is_playing, "L'état doit repasser à inactif après le bip"

def test_play_audio_thread(mock_pyaudio):
    mock_instance, mock_stream = mock_pyaudio
    player = AudioPlayer()
    data = np.zeros(1000, dtype=np.int16)

    player.play_audio(data)
    time.sleep(0.2)
    mock_instance.open.assert_called()

def test_play_audio(mock_pyaudio):
    mock_instance, mock_stream = mock_pyaudio
    player = AudioPlayer()
    assert not player.is_playing, "L'état doit être inactif au démarrage"

    player.play_beep()
    time.sleep(0.1)
    mock_instance.open.assert_called()
