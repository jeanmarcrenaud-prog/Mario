# src/core/conversation_handler.py
from typing import List, Dict, Any, Optional, Callable

from src.utils.logger import logger


class ConversationHandler:
    """Gère la conversation: historique, traitement messages, responses LLM"""

    def __init__(
        self,
        conversation_service,
        llm_service,
    ):
        self.conversation_service = conversation_service
        self.llm_service = llm_service
        self._on_response_ready: Optional[Callable[[str], None]] = None

    def set_response_callback(self, callback: Callable[[str], None]):
        """Définit le callback quand une réponse est générée"""
        self._on_response_ready = callback

    def process_message(self, message: str) -> str:
        """Traite un message utilisateur et retourne la réponse"""
        try:
            logger.info(f"Traitement message: {message}")
            self.conversation_service.add_message("user", message)

            messages = self.conversation_service.get_history()
            response = self.llm_service.generate_response(messages)

            self.conversation_service.add_message("assistant", response)
            logger.info(f"Réponse générée: {response[:100]}...")

            if self._on_response_ready:
                self._on_response_ready(response)

            return response
        except Exception as e:
            logger.error(f"Erreur traitement message: {e}")
            error_response = "[ERREUR] Impossible de traiter votre message"
            self.conversation_service.add_message("assistant", error_response)
            return error_response

    def get_history(self) -> List[Dict[str, str]]:
        """Retourne l'historique de conversation"""
        return self.conversation_service.get_history()

    def clear_history(self):
        """Efface l'historique"""
        self.conversation_service.clear_history()
        logger.info("Historique effacé")

    def test_llm(self) -> bool:
        """Teste le service LLM"""
        return self.llm_service.test_service()
