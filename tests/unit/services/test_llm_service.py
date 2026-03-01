import pytest
from src.services.llm_service import LLMService, SimulatedLLMAdapter

class TestLLMService:
    def setup_method(self):
        self.adapter = SimulatedLLMAdapter()
        self.llm_service = LLMService(llm_adapter=self.adapter)

    def test_generate_response(self):
        messages = [{"role": "user", "content": "Bonjour"}]
        response = self.llm_service.generate_response(messages)
        assert len(response) > 0

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
