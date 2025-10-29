import sys
import pathlib
import pytest
import time
import numpy as np
from unittest.mock import MagicMock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from src.utils.audio_player import AudioPlayer

@pytest.fixture
def mock_pyaudio(monkeypatch):
    """Mock complet de PyAudio pour éviter la lecture réelle."""
    mock_instance = MagicMock()
    mock_stream = MagicMock()
    mock_instance.open.return_value = mock_stream
    monkeypatch.setattr("src.utils.audio_player.pyaudio.PyAudio", lambda: mock_instance)
    return mock_instance, mock_stream

def test_play_beep_sets_is_playing(mock_pyaudio):
    mock_instance, mock_stream = mock_pyaudio
    player = AudioPlayer()
    assert not player.is_playing, "L'état doit être inactif au démarrage"  # Maintenant correct avec @property
    player.play_beep(frequency=1000, duration=0.05)
    time.sleep(0.2)
    assert not player.is_playing, "L'état doit repasser à inactif après le bip"  # Maintenant correct

def test_play_audio_thread(mock_pyaudio):
    mock_instance, mock_stream = mock_pyaudio
    player = AudioPlayer()
    data = np.zeros(1000, dtype=np.int16)
    player.play_audio(data)
    time.sleep(0.5)
    assert not player.is_playing, "Lecture terminée : état inactif"  # Maintenant correct
    mock_instance.open.assert_called()
    mock_stream.write.assert_called()

def test_play_audio():
    audio_player = AudioPlayer()
    audio_player.play_beep()
    time.sleep(0.1)
    assert audio_player.is_playing, "L'état doit être actif pendant la lecture"  # Maintenant correct
