"""
Tests de performance pour benchmarking.
"""

import pytest
import time
from src.core.app_factory import AppFactory
from src.models.settings import Settings
from src.config.config import ConfigManager, config


class TestPerformanceBenchmark:
    """Tests de benchmarking de performance."""
    
    def test_llm_response_time(self):
        """Test le temps de réponse LLM."""
        factory = AppFactory()
        settings = Settings.from_config(config)
        assistant = factory.create(settings)
        
        start = time.time()
        response = assistant.process_user_message("Test performance")
        elapsed = time.time() - start
        
        assert elapsed < 30  # Moins de 30 secondes
        assert response is not None
    
    def test_tts_response_time(self):
        """Test le temps de réponse TTS."""
        factory = AppFactory()
        settings = Settings.from_config(config)
        assistant = factory.create(settings)
        
        start = time.time()
        assistant.speak("Test performance")
        elapsed = time.time() - start
        
        assert elapsed < 10  # Moins de 10 secondes
