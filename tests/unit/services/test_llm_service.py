import pytest
from src.services.llm_service import LLMService, SimulatedLLMAdapter, OllamaLLMAdapter, ILLMAdapter
from unittest.mock import MagicMock, patch

class TestLLMService:
    def setup_method(self):
        self.adapter = SimulatedLLMAdapter()
        self.llm_service = LLMService(adapter=self.adapter)

    def test_generate_response(self):
        messages = [{"role": "user", "content": "Bonjour"}]
        response = self.llm_service.generate_response(messages)
        assert len(response) > 0

    def test_generate_response_with_custom_responses(self):
        adapter = SimulatedLLMAdapter(fake_responses={"hello": "Hello!"})
        service = LLMService(adapter=adapter)
        messages = [{"role": "user", "content": "Hello world"}]
        response = service.generate_response(messages)
        assert response == "Hello!"

    def test_generate_analysis(self):
        prompt = "Quelle est la complexité du projet ?"
        analysis = self.llm_service.generate_analysis(prompt)
        assert "Analyse du projet simulée" in analysis

    def test_generate_recommendations(self):
        analysis = "Le code n'est pas optimisé."
        recommendations = self.llm_service.generate_recommendations(analysis)
        expected_recommendations = [
            "[Optimisation des performances]",
            "[Amélioration de la documentation]",
            "[Refactorisation du code]"
        ]
        assert recommendations == expected_recommendations

    def test_test_service(self):
        result = self.llm_service.test_service()
        assert result is True

    def test_get_available_models(self):
        models = self.llm_service.get_available_models()
        assert isinstance(models, list)
        assert len(models) > 0

    def test_create_with_simulation(self):
        service = LLMService.create_with_simulation()
        assert isinstance(service, LLMService)
        assert isinstance(service.llm_adapter, SimulatedLLMAdapter)

    def test_create_with_simulation_custom_responses(self):
        custom_responses = {"test": "Custom response"}
        service = LLMService.create_with_simulation(custom_responses)
        assert isinstance(service.llm_adapter, SimulatedLLMAdapter)
        assert service.llm_adapter.fake_responses == custom_responses

    def test_generate_response_error_handling(self):
        self.adapter.chat = MagicMock(side_effect=Exception("API Error"))
        messages = [{"role": "user", "content": "Test"}]
        response = self.llm_service.generate_response(messages)
        assert "[ERREUR]" in response


class TestSimulatedLLMAdapter:
    def test_default_response(self):
        adapter = SimulatedLLMAdapter()
        messages = [{"role": "user", "content": "Random text"}]
        response = adapter.generate_response(messages)
        assert isinstance(response, str)
        assert len(response) > 0

    def test_test_keyword_response(self):
        adapter = SimulatedLLMAdapter()
        messages = [{"role": "user", "content": "test"}]
        response = adapter.generate_response(messages)
        assert "Test réussi" in response

    def test_analysis_keyword_response(self):
        adapter = SimulatedLLMAdapter()
        messages = [{"role": "user", "content": "analyse projet"}]
        response = adapter.generate_response(messages)
        assert "Analyse du projet simulée" in response

    def test_recommendations_keyword_response(self):
        adapter = SimulatedLLMAdapter()
        messages = [{"role": "user", "content": "recommandation"}]
        response = adapter.generate_response(messages)
        assert "Optimisation" in response

    def test_generate_analysis(self):
        adapter = SimulatedLLMAdapter()
        analysis = adapter.generate_analysis("Test prompt")
        assert "Analyse du projet simulée" in analysis

    def test_generate_recommendations(self):
        adapter = SimulatedLLMAdapter()
        recommendations = adapter.generate_recommendations("Test analysis")
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0


class TestOllamaLLMAdapter:
    @patch('requests.get')
    def test_check_availability_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"models": [{"name": "llama2"}]}
        mock_get.return_value = mock_response
        
        adapter = OllamaLLMAdapter()
        assert adapter.is_available is True

    @patch('requests.get')
    def test_check_availability_failure(self, mock_get):
        mock_get.side_effect = Exception("Connection error")
        
        adapter = OllamaLLMAdapter()
        assert adapter.is_available is False
