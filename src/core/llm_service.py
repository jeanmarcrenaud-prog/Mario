# Minimal LLMService stub for tests
from typing import Dict, List

class LLMService:
    def __init__(self, fake_responses: Dict[str, str] = None):
        self.fake_responses = fake_responses or {}

    @staticmethod
    def create_with_simulation(fake_responses: Dict[str, str] = None):
        return LLMService(fake_responses=fake_responses)

    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        content = messages[-1]["content"] if messages else ""
        for key, resp in self.fake_responses.items():
            if key.lower() in content.lower():
                return resp
        return f"Réponse simulée à: {content[:50]}..."

    def test_service(self) -> bool:
        return True

    def get_available_models(self) -> List[str]:
        return []
