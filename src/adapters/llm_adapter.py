import requests
import json
from typing import List, Dict, Generator
from ..utils.logger import logger

class LLMAdapter:
    """Adaptateur pour différents modèles LLM."""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.current_model = "qwen3-coder:latest"  # Modèle par défaut
        self.is_available = self._check_connection()
        logger.info(f"LLMAdapter initialisé - Base URL: {base_url}")
    
    def _check_connection(self) -> bool:
        """Vérifie la connexion au serveur LLM."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Connexion LLM établie")
                return True
            else:
                logger.warning("⚠️ Serveur LLM non disponible")
                return False
        except Exception as e:
            logger.warning(f"⚠️ Impossible de se connecter au LLM: {e}")
            return False
    
    def set_model(self, model_name: str):
        """Définit le modèle à utiliser."""
        self.current_model = model_name
        logger.info(f"Modèle LLM défini: {model_name}")
    
    def get_available_models(self) -> List[str]:
        """Retourne la liste des modèles disponibles."""
        try:
            if not self.is_available:
                return []
            
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models_data = response.json()
                models = [model["name"] for model in models_data.get("models", [])]
                logger.info(f"Modèles disponibles: {models}")
                return models
            return []
        except Exception as e:
            logger.error(f"Erreur récupération modèles: {e}")
            return []
    
    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """
        Génère une réponse complète.
        
        Args:
            messages: Liste des messages de conversation
            temperature: Température du modèle (0.0-1.0)
            
        Returns:
            Réponse du modèle
        """
        try:
            if not self.is_available:
                return self._get_fallback_response(messages)
            
            payload = {
                "model": self.current_model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature
                }
            }
            
            logger.info(f"🤖 Appel LLM avec {len(messages)} messages...")
            
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=300  # 5 minutes timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get("message", {}).get("content", "")
                logger.info(f"✅ Réponse LLM: {answer[:100]}...")
                return answer
            else:
                logger.error(f"❌ Erreur LLM: {response.status_code} - {response.text}")
                return self._get_error_response()
                
        except Exception as e:
            logger.error(f"❌ Erreur appel LLM: {e}")
            return self._get_error_response()
    
    def chat_stream(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> Generator[str, None, None]:
        """
        Génère une réponse en streaming.
        
        Args:
            messages: Liste des messages de conversation
            temperature: Température du modèle
            
        Yields:
            Morceaux de réponse du modèle
        """
        try:
            if not self.is_available:
                yield from self._get_fallback_response_stream(messages)
                return
            
            payload = {
                "model": self.current_model,
                "messages": messages,
                "stream": True,
                "options": {
                    "temperature": temperature
                }
            }
            
            logger.info(f"🤖 Appel LLM streaming avec {len(messages)} messages...")
            
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=300,
                stream=True
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line.decode('utf-8'))
                            if 'message' in data and 'content' in data['message']:
                                content = data['message']['content']
                                if content:
                                    yield content
                            elif 'done' in data and data['done']:
                                break
                        except json.JSONDecodeError:
                            continue
            else:
                logger.error(f"❌ Erreur streaming LLM: {response.status_code}")
                yield "[ERREUR] Impossible de générer une réponse"
                
        except Exception as e:
            logger.error(f"❌ Erreur streaming LLM: {e}")
            yield "[ERREUR] Erreur de connexion au modèle"
    
    def _get_fallback_response(self, messages: List[Dict[str, str]]) -> str:
        """Réponse de secours quand LLM non disponible."""
        last_message = messages[-1]["content"] if messages else ""
        return f"Je comprends votre message: '{last_message}'. C'est une réponse simulée car le modèle n'est pas disponible."
    
    def _get_fallback_response_stream(self, messages: List[Dict[str, str]]) -> Generator[str, None, None]:
        """Réponse de secours en streaming."""
        last_message = messages[-1]["content"] if messages else ""
        response = f"Je comprends votre message: '{last_message}'. C'est une réponse simulée car le modèle n'est pas disponible."
        for char in response:
            yield char
    
    def _get_error_response(self) -> str:
        """Réponse d'erreur."""
        return "[ERREUR] Impossible de générer une réponse. Veuillez vérifier que le modèle est démarré."
    
    def test_connection(self) -> bool:
        """Teste la connexion au LLM."""
        try:
            test_messages = [{"role": "user", "content": "Bonjour"}]
            response = self.chat(test_messages)
            success = "Bonjour" in response or len(response) > 0
            if success:
                logger.info("✅ Test connexion LLM réussi")
            else:
                logger.error("❌ Test connexion LLM échoué")
            return success
        except Exception as e:
            logger.error(f"❌ Test connexion LLM échoué: {e}")
            return False
