# tests/e2e/test_full_assistant.py
import pytest
from src.core.app_factory import create_assistant

class TestFullAssistantE2E:
    """Tests de bout en bout de l'assistant complet"""

    def test_assistant_lifecycle(self):
        """Test du cycle de vie complet de l'assistant"""
        # Création
        assistant = create_assistant()
        assert assistant is not None
        
        # Test des services
        assert assistant.tts_service.test_synthesis()
        assert assistant.llm_service.test_service()
        
        # Test de conversation
        response = assistant.process_user_message("Bonjour")
        assert isinstance(response, str)
        assert len(response) > 0

    def test_conversation_flow(self):
        """Test d'un flux de conversation complet"""
        assistant = create_assistant()
        
        # Premier message
        response1 = assistant.process_user_message("Bonjour")
        assert "Bonjour" in response1 or len(response1) > 0
        
        # Deuxième message
        response2 = assistant.process_user_message("Comment allez-vous ?")
        assert isinstance(response2, str)
        assert len(response2) > 0
        
        # Vérifier l'historique
        history = assistant.get_conversation_history()
        assert len(history) >= 4  # 2 messages utilisateur + 2 réponses

    def test_clear_conversation(self):
        """Test d'effacement de la conversation"""
        assistant = create_assistant()
        
        # Ajouter quelques messages
        assistant.process_user_message("Message 1")
        assistant.process_user_message("Message 2")
        
        history_before = assistant.get_conversation_history()
        assert len(history_before) > 0
        
        # Effacer
        assistant.clear_conversation()
        
        history_after = assistant.get_conversation_history()
        assert len(history_after) == 0
