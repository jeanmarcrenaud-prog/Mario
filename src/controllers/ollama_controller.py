# src/controller/ollama_controller.py
from src.model.ollama_client import OllamaClient
from src.utils.logger import logger

class OllamaController:
    def __init__(self, ollama_client: OllamaClient):
        self.ollama_client = ollama_client

    def send_to_ollama(self, text):
        """Envoie du texte à Ollama et retourne la réponse."""
        try:
            response = self.ollama_client.generate(text)
            return response
        except Exception as e:
            logger.error(f"Erreur dans OllamaController : {e}")
            return f"Erreur : {e}"
