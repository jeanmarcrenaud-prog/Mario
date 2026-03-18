import pytest
from src.services.llm_service import LLMService

# -- Helper fixture -------------------------------------------
@pytest.fixture
def simulated_service():
    """Return an LLMService instance backed by the simulated adapter."""
    return LLMService.create_with_simulation()

# -- Tests -------------------------------------------

def test_create_with_simulation(simulated_service):
    assert simulated_service is not None
    assert simulated_service.service_type == "simulation"
    assert simulated_service.llm_adapter is not None
    # Simulated adapter should report available models
    assert len(simulated_service.get_available_models()) == 3


def test_set_and_get_model(simulated_service):
    # Set a fake model name
    success = simulated_service.set_model("fake-model-123")
    assert success is True
    # The adapter should keep the model name
    assert getattr(simulated_service.llm_adapter, "model_name", None) == "fake-model-123"


def test_generate_response_keywords(simulated_service):
    # Test specific triggers that the simulated adapter understands
    messages = [
        {"role": "user", "content": "Analyse ce code"}
    ]
    resp = simulated_service.generate_response(messages)
    assert resp == "Analyse du projet simulée"

    messages = [{"role": "user", "content": "Test [erreur]"}]
    resp = simulated_service.generate_response(messages)
    # Should not return "Test réussi" because of the error tag
    assert resp != "Test réussi"

    messages = [{"role": "user", "content": "Test de code"}]
    resp = simulated_service.generate_response(messages)
    assert resp == "Test réussi"


def test_generate_recommendations(simulated_service):
    project_path = "/path/to/project"
    recs = simulated_service.generate_recommendations(project_path)
    # Simulated adapter returns a single string with newlines
    assert isinstance(recs, list)
    assert all(isinstance(r, str) for r in recs)
    assert len(recs) > 0


def test_get_service_info(simulated_service):
    info = simulated_service.get_service_info()
    assert info["service_type"] == "simulation"
    assert info["adapter"] == "SimulatedLLMAdapter"
    assert info["available"] is True
    assert info["connection"] is True
    assert info["models"] == 3


def test_test_service(simulated_service):
    assert simulated_service.test_service() is True
    assert simulated_service.test_connection() is True

# -------------------------------------------
