from typing import List, Dict, Generator, Optional
from ..adapters.llm_adapter import LLMAdapter
from ..utils.logger import logger

class LLMService:
    """Service de gestion des modèles LLM."""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.llm_adapter = LLMAdapter(base_url)
        self.current_model = "qwen3-coder:latest"
        logger.info("LLMService initialisé")
    
    def set_model(self, model_name: str):
        """Définit le modèle à utiliser."""
        self.current_model = model_name
        self.llm_adapter.set_model(model_name)
        logger.info(f"Modèle LLM défini: {model_name}")
    
    def get_available_models(self) -> List[str]:
        """Retourne la liste des modèles disponibles."""
        try:
            return self.llm_adapter.get_available_models()
        except Exception as e:
            logger.error(f"Erreur récupération modèles: {e}")
            return ["qwen3-coder"]

    def _get_fallback_response(self, messages: List[Dict[str, str]]) -> str:
        """Réponse de secours quand LLM non disponible."""
        last_message = messages[-1]["content"] if messages else ""
        return f"Je comprends votre message: '{last_message}'. C'est une réponse simulée car le modèle n'est pas disponible."
    
    def generate_response(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """
        Génère une réponse complète.
        
        Args:
            messages: Liste des messages de conversation
            temperature: Température du modèle
            
        Returns:
            Réponse du modèle
        """
        try:
            if not messages:
                return "Aucun message à traiter."
            
            # Ajouter le contexte si nécessaire
            enhanced_messages = self._enhance_messages(messages)
            
            logger.info(f"🤖 Génération réponse avec {len(enhanced_messages)} messages...")
            response = self.llm_adapter.chat(enhanced_messages, temperature)
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Erreur génération réponse: {e}")
            return "[ERREUR] Impossible de générer une réponse"
    
    def generate_response_stream(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> Generator[str, None, None]:
        """
        Génère une réponse en streaming.
        
        Args:
            messages: Liste des messages de conversation
            temperature: Température du modèle
            
        Yields:
            Morceaux de réponse du modèle
        """
        try:
            if not messages:
                yield "Aucun message à traiter."
                return
            
            enhanced_messages = self._enhance_messages(messages)
            
            logger.info(f"🤖 Génération réponse streaming avec {len(enhanced_messages)} messages...")
            yield from self.llm_adapter.chat_stream(enhanced_messages, temperature)
            
        except Exception as e:
            logger.error(f"❌ Erreur génération réponse streaming: {e}")
            yield "[ERREUR] Impossible de générer une réponse"
    
    def _enhance_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Améliore les messages avec du contexte si nécessaire."""
        # Pour le moment, retourne les messages tels quels
        # Vous pouvez ajouter ici du contexte système, des instructions, etc.
        return messages
    
    def is_available(self) -> bool:
        """Vérifie si le service LLM est disponible."""
        return self.llm_adapter.is_available
    
    def test_service(self) -> bool:
        """Teste le service LLM."""
        try:
            logger.info("🧪 Test du service LLM...")
            return self.llm_adapter.test_connection()
        except Exception as e:
            logger.error(f"❌ Test service LLM échoué: {e}")
            return False
