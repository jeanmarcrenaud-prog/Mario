from typing import List, Dict, Optional, Generator
from ..models.conversation_state import ConversationState
from ..utils.logger import logger

class ConversationService:
    """Service de gestion de la conversation."""
    
    def __init__(self):
        self.conversation_state = ConversationState()
        logger.info("ConversationService initialisé")
    
    def add_message(self, role: str, content: str):
        """Ajoute un message à l'historique de conversation."""
        self.conversation_state.add_message(role, content)
        logger.debug(f"Message ajouté: {role} - {content[:50]}...")
    
    def get_history(self) -> List[Dict[str, str]]:
        """Retourne l'historique de conversation."""
        return self.conversation_state.get_messages()
    
    def get_last_message(self) -> Optional[Dict[str, str]]:
        """Retourne le dernier message."""
        return self.conversation_state.get_last_message()
    
    def clear_history(self):
        """Efface l'historique de conversation."""
        self.conversation_state.clear()
        logger.info("Historique de conversation effacé")
    
    def get_message_count(self) -> int:
        """Retourne le nombre de messages."""
        return self.conversation_state.get_message_count()
    
    def generate_response(self, user_message: str, llm_adapter=None) -> str:
        """
        Génère une réponse à partir du message utilisateur.
        Pour le moment, retourne une réponse simulée.
        """
        try:
            # Ajouter le message utilisateur
            self.add_message("user", user_message)
            
            # Simuler une réponse (à remplacer par l'appel LLM réel)
            if llm_adapter:
                # Ici viendra l'appel à l'LLM
                response = llm_adapter.generate_response(user_message)
            else:
                response = f"Je comprends votre message: '{user_message}'. C'est une réponse simulée."
            
            # Ajouter la réponse
            self.add_message("assistant", response)
            
            logger.info(f"Réponse générée: {response[:50]}...")
            return response
            
        except Exception as e:
            logger.error(f"Erreur génération réponse: {e}")
            error_response = "[ERREUR] Impossible de générer une réponse"
            self.add_message("assistant", error_response)
            return error_response
