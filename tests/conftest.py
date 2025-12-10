# tests/conftest.py
import sys
import os
import pytest
import numpy as np

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
    return MagicMock()

@pytest.fixture
def conversation_history():
    """Fixture pour un historique de conversation"""
    return [
        {"role": "user", "content": "Bonjour"},
        {"role": "assistant", "content": "Bonjour ! Comment puis-je vous aider ?"}
    ]
