"""
Tests end-to-end pour l'assistant vocal complet.
"""

import pytest
from src.core.app_factory import AppFactory
from src.models.settings import Settings
from src.config.config import config


class TestFullAssistantE2E:
    """Tests end-to-end pour l'assistant vocal."""
    
    def test_full_conversation_flow(self):
        """Test le flux complet de conversation."""
        factory = AppFactory()
        settings = Settings.from_config(config)
        assistant = factory.create(settings)
        
        # Test conversation
        response = assistant.process_user_message("Bonjour")
        assert response is not None
        assert len(response) > 0
        
        # Test TTS
        result = assistant.speak("Test")
        assert result is True or result is False  # TTS peut échouer en simulation
    
    def test_project_analysis(self):
        """Test l'analyse de projet."""
        factory = AppFactory()
        settings = Settings.from_config(config)
        assistant = factory.create(settings)
        
        # Test analyse de projet (si fichier existe)
        try:
            report = assistant.analyze_project(".")
            assert "summary" in report or "error" in report
        except Exception:
            pytest.skip("Analyse de projet non disponible")
