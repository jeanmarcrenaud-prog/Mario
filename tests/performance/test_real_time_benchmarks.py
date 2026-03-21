"""
Tests de benchmarks temps réel.
"""

import time
from src.core.app_factory import AppFactory
from src.models.settings import Settings
from src.config.config import config


class TestRealTimeBenchmarks:
    """Tests de benchmarks temps réel."""
    
    def test_full_cycle_time(self):
        """Test le temps d'un cycle complet."""
        factory = AppFactory()
        settings = Settings.from_config(config)
        assistant = factory.create(settings)
        
        start = time.time()
        
        # Cycle complet: wake word -> transcription -> LLM -> TTS
        assistant.speak("Test cycle")
        response = assistant.process_user_message("Test cycle")
        assistant.speak(response)
        
        elapsed = time.time() - start
        
        assert elapsed < 60  # Moins d'une minute
        print(f"Cycle complet: {elapsed:.2f} secondes")
    
    def test_memory_usage(self):
        """Test l'utilisation mémoire."""
        from src.utils.system_monitor import SystemMonitor
        
        monitor = SystemMonitor()
        initial_memory = monitor.get_memory_usage()
        
        # Exécuter plusieurs cycles
        factory = AppFactory()
        settings = Settings.from_config(config)
        assistant = factory.create(settings)
        
        for _ in range(10):
            assistant.process_user_message("Test memory")
        
        final_memory = monitor.get_memory_usage()
        memory_increase = final_memory - initial_memory
        
        assert memory_increase < 500  # Moins de 500 Mo d'augmentation
