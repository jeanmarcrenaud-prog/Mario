"""
Tests unitaires pour le service de conversation
"""

import pytest
from src.services.conversation_service import ConversationService
from unittest.mock import MagicMock

class TestConversationService:
    """Tests pour ConversationService"""

    def test_get_last_message(self):
        """Test de récupération du dernier message"""
        service = ConversationService()
        service.add_message("user", "Bonjour")
        service.add_message("assistant", "Salut !")

        last_message = service.get_last_message()
        assert last_message is not None
        assert last_message["role"] == "assistant"
        assert last_message["content"] == "Salut !"

    def test_get_message_count(self):
        """Test du compteur de messages"""
        service = ConversationService()
        assert service.get_message_count() == 0

        service.add_message("user", "Bonjour")
        assert service.get_message_count() == 1   

    def test_generate_response(self):
        """Test de génération de réponse"""
        service = ConversationService()
        mock_adapter = MagicMock()
        mock_adapter.generate_response.return_value = "Réponse simulée"

        response = service.generate_response("Bonjour", mock_adapter)
        assert response == "Réponse simulée"
        assert service.get_message_count() == 2        
    
    def test_initialization(self):
        """Test d'initialisation du service"""
        service = ConversationService()
        assert service is not None
        assert len(service.get_history()) == 0
    
    def test_add_message(self):
        """Test d'ajout de message"""
        service = ConversationService()
        service.add_message("user", "Bonjour")
        
        history = service.get_history()
        assert len(history) == 1
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Bonjour"
    
    def test_clear_history(self):
        """Test d'effacement de l'historique"""
        service = ConversationService()
        service.add_message("user", "Message 1")
        service.add_message("assistant", "Réponse 1")
        
        assert len(service.get_history()) == 2
        
        service.clear_history()
        assert len(service.get_history()) == 0

if __name__ == "__main__":
    pytest.main([__file__])
