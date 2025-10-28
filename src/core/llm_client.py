import requests
import json
import time
from typing import List, Dict, Optional, Generator
from ..config import config
from ..utils.logger import logger

class LLMClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.current_model: Optional[str] = None
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'AssistantVocal/1.0'
        })
    
    def health_check(self) -> bool:
        """Vérifie si Ollama est accessible."""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error("Ollama non accessible: %s", e)
            return False
    
    def get_available_models(self) -> List[str]:
        """Retourne la liste des modèles disponibles."""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=10)
            response.raise_for_status()
            return [model['name'] for model in response.json().get('models', [])]
        except Exception as e:
            logger.error("Erreur récupération modèles: %s", e)
            return []
    
    def set_model(self, model_name: str) -> bool:
        """Définit le modèle à utiliser avec vérification."""
        if self.current_model == model_name:
            return True
            
        available_models = self.get_available_models()
        if model_name not in available_models:
            logger.error("Modèle '%s' non disponible. Modèles: %s", model_name, available_models)
            return False
        
        self.current_model = model_name
        logger.info("Modèle défini: %s", model_name)
        return True
    
    def chat_stream(self, messages: List[Dict[str, str]]) -> Generator[str, None, None]:
        """Stream la réponse du modèle avec format correct pour Ollama."""
        if not self.current_model:
            logger.error("Aucun modèle sélectionné")
            yield "Erreur: Aucun modèle LLM sélectionné"
            return
        
        # CORRECTION : Format simple pour Ollama
        # Ollama attend un format spécifique - simplifions
        payload = {
            "model": self.current_model,
            "prompt": self._format_messages_for_ollama(messages),
            "stream": True
        }
        
        start_time = time.time()
        full_response = ""
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/generate",  # Utiliser /api/generate au lieu de /api/chat
                json=payload,
                stream=True,
                timeout=config.OLLAMA_TIMEOUT
            )
            
            if response.status_code != 200:
                logger.error("Erreur Ollama (HTTP %d): %s", response.status_code, response.text)
                yield f"Erreur: Ollama a retourné le code {response.status_code}"
                return
                
            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue

                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if data.get("done"):
                    break

                if "response" in data:
                    content = data["response"]
                    full_response += content
                    yield content
                elif "error" in data:
                    logger.error("Erreur Ollama: %s", data['error'])
                    yield f"Erreur: {data['error']}"
                    break
                        
        except requests.exceptions.Timeout:
            logger.error("Timeout lors de la communication avec Ollama")
            yield "Erreur: Délai d'attente dépassé"
        except requests.exceptions.ConnectionError:
            logger.error("Impossible de se connecter à Ollama")
            yield "Erreur: Service Ollama indisponible"
        except Exception as e:
            logger.error("Erreur communication Ollama: %s", e)
            yield "Erreur de communication avec le service LLM"
        finally:
            response_time = time.time() - start_time
            logger.info("Réponse LLM générée en %.2fs - %d caractères", response_time, len(full_response))
    
    def _format_messages_for_ollama(self, messages: List[Dict[str, str]]) -> str:
        """Convertit les messages en prompt simple pour Ollama."""
        formatted = ""
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "system":
                formatted += f"System: {content}\n\n"
            elif role == "user":
                formatted += f"User: {content}\n\n"
            elif role == "assistant":
                formatted += f"Assistant: {content}\n\n"
        formatted += "Assistant:"
        return formatted
    
    def generate_response(self, prompt: str, conversation_history: List[Dict] = None) -> str:
        """Génère une réponse simple sans streaming."""
        if conversation_history is None:
            conversation_history = []
            
        messages = conversation_history + [{"role": "user", "content": prompt}]        
        full_response = ""
        for chunk in self.chat_stream(messages):
            full_response += chunk
            
        return full_response
    
    def cleanup(self):
        """Nettoie les ressources."""
        self.session.close()
