from typing import List, Dict, Optional, Generator, Protocol, Any
import logging

logger = logging.getLogger(__name__)


class ILLMAdapter(Protocol):
    """Interface pour les adaptateurs LLM."""
    
    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str: ...
    
    def test_connection(self) -> bool: ...
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        **kwargs
    ) -> str: ...

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

    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Génère une réponse pour ProjectAnalyzerService."""
        return self.chat(messages, kwargs.get('temperature', 0.7))

    def test_connection(self) -> bool:
        return True

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
    
    def set_model(self, model_name: str) -> bool:
        """Change le modèle simulé."""
        return True  # Simulation ignore les changements


class LMStudioLLMAdapter:
    """Adaptateur LLM pour LM Studio."""

    def __init__(self, model_name: str = "qwen/qwen3.5-9b", base_url: str = "http://localhost:1234", timeout: int = 30):
        self.model_name = model_name
        self.base_url = base_url
        self.timeout = timeout
        self.is_available = False
        self._check_availability()

    def _check_availability(self):
        try:
            import requests
            # LM Studio API v1
            response = requests.get(f"{self.base_url}/v1/models", timeout=self.timeout)
            self.is_available = response.status_code == 200
        except Exception as e:
            logger.debug(f"LM Studio non disponible: {e}")
            self.is_available = False

    def chat(self, messages: List[Dict[str, str]], temperature: float, max_tokens: int = 2048) -> str:
        try:
            import requests            
            # Debug: log le format des messages
            logger.debug(f"LM Studio - Messages envoyés: {messages}")           
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    "model": self.model_name,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": False
                },
                headers={"Content-Type": "application/json"},
                timeout=self.timeout
            )           
            # Debug: log la réponse complète
            logger.debug(f"LM Studio - Status code: {response.status_code}")
            logger.debug(f"LM Studio - Response body: {response.text[:500]}")            
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"Erreur LM Studio: {e}")
            return f"[ERREUR LM STUDIO] {str(e)}"

    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Génère une réponse pour ProjectAnalyzerService."""
        return self.chat(messages, kwargs.get('temperature', 0.7))

    def test_connection(self) -> bool:
        try:
            import requests
            logger.debug(f"Test connexion LM Studio à {self.base_url}/v1/models")
            response = requests.get(f"{self.base_url}/v1/models", timeout=self.timeout)
            logger.debug(f"LM Studio - Status code: {response.status_code}")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Test connexion LM Studio échoué: {e}")
            return False
    
    def get_available_models(self) -> List[str]:
        """Retourne la liste des modèles LM Studio disponibles."""
        try:
            import requests
            logger.debug(f"Récupération modèles LM Studio depuis {self.base_url}/v1/models")
            response = requests.get(f"{self.base_url}/v1/models", timeout=self.timeout)
            logger.debug(f"LM Studio - Status code: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                logger.debug(f"LM Studio - Models data: {data}")
                if isinstance(data, dict):
                    models = data.get("data", [])
                elif isinstance(data, list):
                    models = data
                else:
                    models = []
                return [m.get("id") or m.get("name") for m in models]
            return []
        except Exception as e:
            logger.debug(f"Erreur récupération modèles LM Studio: {e}")
            return []

    def set_model(self, model_name: str) -> bool:
        try:
            self.model_name = model_name
            return True
        except Exception as e:
            logger.error(f"Erreur changement modèle LM Studio: {e}")
            return False


class OllamaLLMAdapter:
    """Adaptateur LLM pour Ollama."""

    def __init__(self, model_name: str = "qwen/qwen3.5-9b", base_url: str = "http://localhost:11434", timeout: int = 30):
        self.model_name = model_name
        self.base_url = base_url
        self.timeout = timeout
        self.is_available = False
        self._check_availability()

    def _check_availability(self):
        try:
            import requests
            response = requests.get(f"{self.base_url}/api/tags", timeout=self.timeout)
            self.is_available = response.status_code == 200
        except Exception as e:
            logger.debug(f"Ollama non disponible: {e}")
            self.is_available = False

    def chat(self, messages: List[Dict[str, str]], temperature: float, max_tokens: int = 2048) -> str:
        try:
            import requests
            # Format compatible avec ollama_client.py qui utilise /api/generate
            prompt = self._format_messages_for_ollama(messages)
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()['response']
        except Exception as e:
            logger.error(f"Erreur Ollama: {e}")
            return f"[ERREUR OLLAMA] {str(e)}"

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

    def generate_response(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Génère une réponse pour ProjectAnalyzerService."""
        return self.chat(messages, kwargs.get('temperature', 0.7))

    def test_connection(self) -> bool:
        try:
            import requests
            response = requests.get(f"{self.base_url}/api/tags", timeout=self.timeout)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Test connexion Ollama échoué: {e}")
            return False

    def refresh_models(self):
        if hasattr(self.get_available_models, "cache_clear"):
            self.get_available_models.cache_clear()

        return self.get_available_models()
    
    def get_available_models(self) -> List[str]:
        """Retourne la liste des modèles Ollama disponibles."""
        try:
            import requests
            response = requests.get(f"{self.base_url}/api/tags", timeout=self.timeout)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [model['name'] for model in models]
            return []
        except Exception as e:
            logger.debug(f"Erreur récupération modèles Ollama: {e}")
            return []
    
    def set_model(self, model_name: str) -> bool:
        """Change le modèle actif."""
        try:
            self.model_name = model_name
            return True
        except Exception as e:
            logger.error(f"Erreur changement modèle Ollama: {e}")
            return False


class LLMService:
    """Service de génération de réponses LLM avec support Ollama et LM Studio."""

    def __init__(self, adapter=None):
        self._adapter = adapter
        self.service_type = self._detect_service_type()

    def _detect_service_type(self) -> str:
        if self._adapter is None:
            return "none"
        name = self._adapter.__class__.__name__.lower()
        if "ollama" in name:
            return "ollama"
        if "lmstudio" in name:
            return "lm_studio"
        if "simulated" in name:
            return "simulation"
        return "unknown"

    @classmethod
    def detect_and_create(cls, preferred_model: Optional[str] = None):
        """Détecte automatiquement le service LLM disponible et utilise celui déjà chargé."""
        logger.info("🔎 Détection automatique du service LLM...")
        services = [
            ("ollama", "http://localhost:11434"),
            ("lm_studio", "http://localhost:1234")
        ]        
        for service_type, url in services:
            try:
                if service_type == "lm_studio":
                    adapter = LMStudioLLMAdapter(
                        model_name=preferred_model or "",
                        base_url=url
                    )
                elif service_type == "ollama":
                    adapter = OllamaLLMAdapter(
                        model_name=preferred_model or "",
                        base_url=url
                    )
                else:
                    continue
                if adapter.test_connection():
                    models = adapter.get_available_models()
                    if models:
                        logger.info(
                            f"✅ Service détecté : {service_type} | modèles: {len(models)}"
                        )
                        if preferred_model is None:
                            adapter.set_model(models[0])
                        return cls(adapter)
            except Exception as e:
                logger.debug(f"Service {service_type} non disponible : {e}")
        logger.warning("⚠ Aucun service LLM détecté -> mode simulation")
        return cls.create_with_simulation()

    def refresh_models(self):
        if self._adapter and hasattr(self._adapter, "refresh_models"):
            return self._adapter.refresh_models()
        if self._adapter and hasattr(self._adapter, "get_available_models"):
            return self._adapter.get_available_models()
        return []

    # ------------------------------------------------
    # INFO SERVICE
    # ------------------------------------------------

    def get_service_info(self) -> Dict[str, Any]:
        return {
            "service_type": self.service_type,            
            "adapter": self._adapter.__class__.__name__,
            "model": getattr(self._adapter, "model_name", None),
            "available": self._adapter is not None,
            "connection": self.test_connection(),
            "models": len(self.get_available_models())
        }
    
    def set_model(self, model_name: str) -> bool:
        try:
            if self._adapter and hasattr(self._adapter, "set_model"):
                success = self._adapter.set_model(model_name)
                if success:
                    logger.info(f"🤖 Modèle changé -> {model_name}")
                return success
            return False
        except Exception as e:
            logger.error(f"Erreur changement modèle: {e}")
            return False
    
    def generate_response(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """Génère une réponse basée sur l'historique de conversation."""
        try:
            if self._adapter:
                return self._adapter.chat(messages, temperature)
            return "[ERREUR] Adaptateur LLM non initialisé"
        except Exception as e:
            logger.error(f"Erreur génération LLM: {e}")
            return "[ERREUR]"
    
    def generate_response_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7
    ) -> Generator[str, None, None]:

        if self._adapter and hasattr(self._adapter, "chat_stream"):
            yield from self._adapter.chat_stream(messages, temperature)
            return
        response = self.generate_response(messages, temperature)
        for i in range(0, len(response), 4):
            yield response[i:i+4]
    
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
    
    # ------------------------------------------------
    # TEST
    # ------------------------------------------------

    def test_connection(self) -> bool:
        try:
            if self._adapter:
                return self._adapter.test_connection()
        except Exception as e:
            logger.error(f"Test connexion échoué: {e}")
        return False
    
    # ------------------------------------------------
    # SIMULATION
    # ------------------------------------------------

    @classmethod
    def create_with_simulation(cls):
        adapter = SimulatedLLMAdapter()
        return cls(adapter)
    
    @classmethod
    def create_with_ollama(cls, model_name: str = "qwen3-coder", base_url: str = "http://localhost:11434"):
        """Crée un service avec adapter Ollama."""        
        adapter = OllamaLLMAdapter(model_name=model_name, base_url=base_url)
        instance = cls(adapter=adapter)
        return instance
    
    @property
    def llm_adapter(self):
        """Expose l'adaptateur pour les tests."""
        return self._adapter
    
    # ------------------------------------------------
    # MODELES
    # ------------------------------------------------

    def get_available_models(self) -> List[str]:
        try:
            if self._adapter and hasattr(self._adapter, "get_available_models"):
                return self._adapter.get_available_models()
        except Exception as e:
            logger.error(f"Erreur récupération modèles: {e}")
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
