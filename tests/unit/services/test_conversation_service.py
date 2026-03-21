"""
Tests unitaires pour ConversationService.
"""

from src.services.conversation_service import ConversationService


class TestConversationService:
    """Tests pour ConversationService."""
    
    def test_service_init(self):
        """Test l'initialisation de ConversationService."""
        service = ConversationService()
        assert service is not None
    
    def test_add_message(self):
        """Test l'ajout d'un message."""
        service = ConversationService()
        service.add_message("user", "Hello")
        assert len(service.conversation_state.messages) == 1
