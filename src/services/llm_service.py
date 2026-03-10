from typing import List, Dict, Optional, Generator, Protocol
import logging

logger = logging.getLogger(__name__)


class ILLMAdapter(Protocol):
    """Interface pour les adaptateurs LLM."""
    
    def chat(self, messages: List[Dict[str, str]], temperature: float) -> str: ...
    
    def test_connection(self) -> bool: ...


class SimulatedLLMAdapter:
    """Adaptateur LLM simulé pour les tests."""
    
    def __init__(self, fake_responses: Optional[Dict[str, str]] = None):
        self.fake_responses = fake_responses or {}
    
    def chat(self, messages: List[Dict[str, str]], temperature: float) -> str:
        if len(messages) >= 1 and 'content' in messages[-1]:
            content = messages[-1]['content'].lower()
            
            # Mots-clés spécifiques pour les tests (ordre important!)
            if "analyse ce code" in content or "analyse du code" in content or "analyse projet" in content or "analyse du projet" in content:
                return "Analyse du projet simulée"
            if "test" in content and "[erreur]" not in content:
                return "Test réussi"
            if "recommandation" in content:
                return "[Optimisation des performances]\n[Amélioration de la documentation]\n[Refactorisation du code]"
            
            # Vérifier les réponses personnalisées
            for key, response in self.fake_responses.items():
                if key.lower() in content:
                    return response
            
        return "Ceci est une réponse simulée."
    
    def test_connection(self) -> bool:
        return True
    
    def generate_response(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        return self.chat(messages, temperature)
    
    def generate_analysis(self, code_text: str) -> str:
        system_prompt = "Tu es un expert en développement logiciel."
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Analyse ce code:\n{code_text}"}
        ]
        return self.chat(messages, 0.7)
    
    def generate_recommendations(self, project_path: str) -> List[str]:
        messages = [
            {"role": "system", "content": "Donnez des recommandations."},
            {"role": "user", "content": f"Projet: {project_path}"}
        ]
        response = self.chat(messages, 0.7)
        return [response]
    
    def get_available_models(self) -> List[str]:
        return ["qwen3-coder", "llama2", "mistral"]


class OllamaLLMAdapter:
    """Adaptateur LLM pour Ollama."""
    
    def __init__(self, model_name: str = "qwen3-coder", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.is_available = False
        self._check_availability()
    
    def _check_availability(self):
        try:
            import requests
            response = requests.get(f"{self.base_url}/api/tags")
            self.is_available = response.status_code == 200
        except Exception as e:
            logger.debug(f"Ollama non disponible: {e}")
            self.is_available = False
    
    def chat(self, messages: List[Dict[str, str]], temperature: float) -> str:
        try:
            import requests
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model_name,
                    "messages": messages,
                    "temperature": temperature
                }
            )
            response.raise_for_status()
            return response.json()['message']['content']
        except Exception as e:
            logger.error(f"Erreur Ollama: {e}")
            return f"[ERREUR OLLAMA] {str(e)}"
    
    def test_connection(self) -> bool:
        try:
            import requests
            response = requests.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Test connexion Ollama échoué: {e}")
            return False


class LLMService:
    """Service de génération de réponses LLM."""
    
    def __init__(self, adapter=None):
        self._adapter = adapter
    
    def generate_response(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """Génère une réponse basée sur l'historique de conversation."""
        try:
            if self._adapter:
                return self._adapter.chat(messages, temperature)
            return "[ERREUR] Adaptateur LLM non initialisé"
        except Exception as e:
            logger.error(f"Erreur génération LLM: {e}")
            return "[ERREUR]"
    
    def generate_response_stream(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> Generator[str, None, None]:
        """Génère une réponse en streaming."""
        exc = None
        try:
            if self._adapter and hasattr(self._adapter, 'chat_stream'):
                yield from self._adapter.chat_stream(messages, temperature)
                return
        except Exception as e:
            logger.error(f"Erreur streaming LLM: {e}")
            exc = e
        
        if exc:
            yield f"[ERREUR] {str(exc)}"
        else:
            yield "[ERREUR] Adaptateur non compatible avec le streaming"
    
    def generate_analysis(self, code_text: str) -> str:
        """Génère une analyse de code."""
        system_prompt = "Tu es un expert en développement logiciel. Analysez le code fourni."
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Analyse du projet et du code:\n{code_text}"}
        ]
        return self.generate_response(messages)
    
    def generate_recommendations(self, project_path: str) -> List[str]:
        """Génère des recommandations pour un projet."""
        system_prompt = "Tu es un expert en développement logiciel. Donnez des recommandations concrètes."
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Projet: {project_path} - Recommandations:"}
        ]
        response = self.generate_response(messages)
        if "\n" in response:
            return [line.strip() for line in response.split("\n") if line.strip()]
        return [response]
    
    def test_connection(self) -> bool:
        """Teste la connexion au service LLM."""
        try:
            if self._adapter:
                return self._adapter.test_connection()
            return False
        except Exception as e:
            logger.error(f"Test LLM échoué: {e}")
            return False
    
    @classmethod
    def create_with_simulation(cls, custom_responses: Optional[Dict[str, str]] = None):
        """Crée un service avec adapter simulé."""
        from src.services.llm_service import SimulatedLLMAdapter
        
        adapter = SimulatedLLMAdapter(fake_responses=custom_responses)
        instance = cls(adapter=adapter)
        return instance
    
    @property
    def llm_adapter(self):
        """Expose l'adaptateur pour les tests."""
        return self._adapter
    
    def get_available_models(self) -> List[str]:
        """Retourne la liste des modèles disponibles."""
        if self._adapter and hasattr(self._adapter, 'get_available_models'):
            return self._adapter.get_available_models()
        return []
    
    def test_service(self) -> bool:
        """Teste le service LLM."""
        try:
            if self._adapter and hasattr(self._adapter, 'test_connection'):
                return self._adapter.test_connection()
            return True
        except Exception as e:
            logger.error(f"Test de service échoué: {e}")
            return False
