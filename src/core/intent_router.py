# src/core/intent_router.py

from ..utils.logger import logger

class IntentRouter:
    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    def route_intent(self, text: str):
        # Routage basique, exemple : utilise un LLM pour l’intention
        if self.llm_client:
            response = self.llm_client.ask(text)
        else:
            response = "Aucun client LLM défini"
        logger.info(f"Intent détecté — texte: {text}, réponse: {response}")
        return {"response": response}
