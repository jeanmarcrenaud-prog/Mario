# tests/performance/test_benchmark.py
import pytest
import time

class TestPerformanceBenchmark:
    """Tests de performance et benchmarks"""

    def test_conversation_service_performance(self, benchmark):
        """Benchmark du service de conversation"""
        from src.services.conversation_service import ConversationService
        
        service = ConversationService()
        
        def add_messages():
            for i in range(100):
                service.add_message("user", f"Message {i}")
                service.add_message("assistant", f"Réponse {i}")
        
        benchmark(add_messages)
        
        # Vérifier que l'historique est correct
        assert service.get_message_count() == 200

    def test_llm_response_time(self, benchmark):
        """Benchmark du temps de réponse LLM"""
        from src.core.llm_service import LLMService
        
        service = LLMService.create_with_simulation()
        messages = [{"role": "user", "content": "Bonjour"}]
        
        def generate_response():
            return service.generate_response(messages)
        
        result = benchmark(generate_response)
        assert isinstance(result, str)
