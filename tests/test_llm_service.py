import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Ajouter le chemin src pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.llm_service import LLMService, ILLMAdapter, SimulatedLLMAdapter

class MockLLMAdapter(ILLMAdapter):
    """Adaptateur mock pour les tests"""
    
    def __init__(self):
        self.generate_response_called = False
        self.last_messages = None
    
    def generate_response(self, messages, **kwargs):
        self.generate_response_called = True
        self.last_messages = messages
        return "Test response"

class TestLLMService(unittest.TestCase):

    def setUp(self):
        """Initialisation avant chaque test"""
        self.mock_adapter = MockLLMAdapter()
        self.llm_service = LLMService(self.mock_adapter)

    def test_initialization(self):
        """Test d'initialisation du service LLM"""
        self.assertIsNotNone(self.llm_service.llm_adapter)
        self.assertIsInstance(self.llm_service, LLMService)

    def test_generate_response(self):
        """Test de génération de réponse"""
        messages = [{"role": "user", "content": "Hello"}]
        response = self.llm_service.generate_response(messages)
        
        self.assertEqual(response, "Test response")
        self.assertTrue(self.mock_adapter.generate_response_called)
        self.assertEqual(self.mock_adapter.last_messages, messages)

    def test_generate_response_with_exception(self):
        """Test de génération de réponse avec exception"""
        self.mock_adapter.generate_response = MagicMock(side_effect=Exception("API Error"))
        
        messages = [{"role": "user", "content": "Hello"}]
        response = self.llm_service.generate_response(messages)
        
        self.assertEqual(response, "[ERREUR] Impossible de générer la réponse")

    def test_test_service_success(self):
        """Test du service de test réussi"""
        self.mock_adapter.generate_response = MagicMock(return_value="Test response")
        
        result = self.llm_service.test_service()
        self.assertTrue(result)

    def test_test_service_with_exception(self):
        """Test du service de test avec exception"""
        self.mock_adapter.generate_response = MagicMock(side_effect=Exception("API Error"))
        
        result = self.llm_service.test_service()
        self.assertFalse(result)

    def test_get_available_models(self):
        """Test de récupération des modèles disponibles"""
        models = self.llm_service.get_available_models()
        self.assertIsInstance(models, list)
        self.assertGreater(len(models), 0)

    def test_simulated_adapter(self):
        """Test de SimulatedLLMAdapter"""
        adapter = SimulatedLLMAdapter()
        
        messages = [{"role": "user", "content": "Test message"}]
        response = adapter.generate_response(messages)
        
        self.assertIsInstance(response, str)
        self.assertNotEqual(response, "")

    def test_simulated_adapter_with_custom_responses(self):
        """Test de SimulatedLLMAdapter avec réponses personnalisées"""
        fake_responses = {"hello": "Bonjour!"}
        adapter = SimulatedLLMAdapter(fake_responses)
        
        messages = [{"role": "user", "content": "Hello world"}]
        response = adapter.generate_response(messages)
        
        self.assertEqual(response, "Bonjour!")

    def test_create_with_simulation(self):
        """Test de la factory method create_with_simulation"""
        fake_responses = {"test": "Test response"}
        service = LLMService.create_with_simulation(fake_responses)
        
        self.assertIsInstance(service, LLMService)
        self.assertIsInstance(service.llm_adapter, SimulatedLLMAdapter)

if __name__ == '__main__':
    unittest.main()
