from typing import List, Dict, Generator
import openai
from ..config.config import ConfigManager
from ..utils.logger import logger

class OpenAIAPIAdapter:
    def __init__(self, config: ConfigManager):
        self.config = config
        self.client = None
        self.current_model = "gpt-3.5-turbo"
        
        # Initialiser le client OpenAI
        if config.OPENAI_API_KEY:
            self.client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
    
    def set_model(self, model: str):
        """Définit le modèle à utiliser."""
        self.current_model = model
    
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Génère une réponse complète."""
        if not self.client:
            logger.error("Client OpenAI non initialisé")
            return "[ERREUR] Service LLM non disponible"
        
        try:
            response = self.client.chat.completions.create(
                model=self.current_model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"Erreur appel OpenAI: {e}")
            return f"[ERREUR] {str(e)}"
    
    def chat_stream(self, messages: List[Dict[str, str]]) -> Generator[str, None, None]:
        """Génère une réponse en streaming."""
        if not self.client:
            yield "[ERREUR] Service LLM non disponible"
            return
        
        try:
            stream = self.client.chat.completions.create(
                model=self.current_model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"Erreur stream OpenAI: {e}")
            yield f"[ERREUR] {str(e)}"
    
    def get_available_models(self) -> list:
        """Retourne la liste des modèles disponibles."""
        try:
            if not self.client:
                return []
            
            models = self.client.models.list()
            return [model.id for model in models.data 
                   if model.id.startswith(('gpt-', 'text-'))]
        except Exception as e:
            logger.error(f"Erreur récupération modèles: {e}")
            return []
