import pytest
from src.services.llm_service import LLMService, SimulatedLLMAdapter

# Helper adapter simulating no connectivity
class DummyAdapter:
    def __init__(self, name="dummy"):
        self.model_name = "dummy"
        self._name = name
        self.is_available = False
    def test_connection(self):
        return self.is_available
    def get_available_models(self):
        return []
    def chat(self, messages, temperature):
        raise RuntimeError("No connection")

@pytest.mark.parametrize("adapter", [None, DummyAdapter()])
def test_generate_response_missing_adapter(adapter):
    svc = LLMService(adapter)
    response = svc.generate_response([{"role": "user", "content": "Hi"}])
    if adapter is None:
        assert response == "[ERREUR] Adaptateur LLM non initialisé"
    else:
        # DummyAdapter.chat will raise, should be caught and return [ERREUR]
        assert response == "[ERREUR]"


def test_simulated_llm_get_available_models():
    svc = LLMService.create_with_simulation()
    models = svc.get_available_models()
    assert isinstance(models, list)
    assert set(models) == {"qwen3-coder", "llama2", "mistral"}


def test_simulated_llm_generate_response():
    svc = LLMService.create_with_simulation()
    resp = svc.generate_response([{"role": "user", "content": "Hello"}])
    assert resp == "Ceci est une réponse simulée."
    resp2 = svc.generate_response([{"role": "user", "content": "Analyse ce code"}])
    assert resp2 == "Analyse du projet simulée"


def test_service_create_with_ollama_instantiation():
    svc = LLMService.create_with_ollama("qwen/qwen3.5-9b", "http://localhost:11434")
    assert svc.service_type == "ollama"
    from src.services.llm_service import OllamaLLMAdapter
    assert isinstance(svc.llm_adapter, OllamaLLMAdapter)
    assert svc.llm_adapter.model_name == "qwen/qwen3.5-9b"
    assert svc.llm_adapter.base_url == "http://localhost:11434"


def test_llm_service_get_service_info_simulation():
    svc = LLMService.create_with_simulation()
    info = svc.get_service_info()
    assert info["service_type"] == "simulation"
    assert info["adapter"] == "SimulatedLLMAdapter"
    assert info["model"] is None
    assert info["available"] is True
    assert info["connection"] is True
    assert info["models"] == 3


def test_llm_service_set_model_for_ollama(monkeypatch):
    # Patch _check_availability to avoid network calls
    def fake_check(self):
        self.is_available = True
    monkeypatch.setattr("src.services.llm_service.OllamaLLMAdapter._check_availability", fake_check)
    svc = LLMService.create_with_ollama("qwen/qwen3.5-9b", "http://localhost:11434")
    svc.set_model("new-model")
    assert svc.llm_adapter is not None
    assert svc.llm_adapter.model_name == "new-model"


def test_detect_and_create_fallback(monkeypatch):
    def fake_get(*args, **kwargs):
        raise Exception("Service down")
    monkeypatch.setattr("requests.get", fake_get)
    svc = LLMService.detect_and_create()
    assert svc.service_type == "simulation"
    assert isinstance(svc.llm_adapter, SimulatedLLMAdapter)
