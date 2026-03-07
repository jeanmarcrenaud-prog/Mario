"""
Configuration complète pour pytest avec fixtures et marqueurs
"""
import pytest


def pytest_configure(config):
    """Configuration de pytest."""
    config.addinivalue_line("markers", "slow: mark test as slow")
    config.addinivalue_line("markers", "unit: unit tests")
    config.addinivalue_line("markers", "integration: integration tests")


# ==================== FIXTURES GENERIQUES ====================


@pytest.fixture
def mock_configs():
    """Configuration par défaut pour tous les tests."""
    return {
        "DEFAULT_MICROPHONE_INDEX": 1,
        "DEFAULT_VOICE": "fr_FR-siwes-medium",
        "DEFAULT_MODEL": "qwen3-coder",
        "WEB_PORT": 7860,
        "SAMPLE_RATE": 16000
    }


@pytest.fixture
def mock_audio_file(tmp_path):
    """Crée un fichier audio simple pour les tests."""
    audio_file = tmp_path / "test_audio.wav"
    
    # Créer un signal audio (1 seconde à 440 Hz)
    sample_rate = 16000
    duration = 1.0
    frequency = 440
    
    import numpy as np
    import soundfile as sf
    
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    signal = 0.5 * np.sin(2 * np.pi * frequency * t)
    
    sf.write(str(audio_file), signal, sample_rate)
    
    return str(audio_file)


@pytest.fixture
def mock_llm_response():
    """Mock réponse LLM pour tests."""
    class MockLLMResponse:
        def __init__(self):
            self.response = "Ceci est une réponse de LLM"
            self.history = []
    
    return MockLLMResponse()


@pytest.fixture
def mock_conversation_state():
    """Mock état de conversation pour tests."""
    from collections import defaultdict
    
    return defaultdict(list)


# ==================== MARKERS ====================


def pytest_collection_modifyitems(config, items):
    """Marquage automatique des tests."""
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(pytest.mark.slow)
        if "web" in item.keywords:
            item.add_marker(pytest.mark.integration)
