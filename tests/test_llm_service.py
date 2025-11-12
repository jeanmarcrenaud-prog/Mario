import unittest
from unittest.mock import MagicMock, patch
from src.core.llm_service import LLMService

class TestLLMService(unittest.TestCase):

    @patch('src.core.llm_service.LLMAdapter')
    def setUp(self, mock_adapter):
        mock_adapter_instance = MagicMock()
        mock_adapter.return_value = mock_adapter_instance
        self.llm_service = LLMService(base_url="http://test-url")

    def test_initialization(self):
        self.assertIsNotNone(self.llm_service.llm_adapter)
        self.assertEqual(self.llm_service.current_model, "qwen3-coder:latest")

    @patch('src.core.llm_service.LLMAdapter')
    def test_set_model(self, mock_adapter):
        mock_adapter_instance = MagicMock()
        mock_adapter.return_value = mock_adapter_instance
        self.llm_service = LLMService(base_url="http://test-url")

        self.llm_service.set_model("test-model")
        mock_adapter_instance.set_model.assert_called_once_with("test-model")
        self.assertEqual(self.llm_service.current_model, "test-model")

    @patch('src.core.llm_service.LLMAdapter')
    def test_get_available_models(self, mock_adapter):
        mock_adapter_instance = MagicMock()
        mock_adapter_instance.get_available_models.return_value = ["model1", "model2"]
        mock_adapter.return_value = mock_adapter_instance
        self.llm_service = LLMService(base_url="http://test-url")

        models = self.llm_service.get_available_models()
        self.assertEqual(models, ["model1", "model2"])

    @patch('src.core.llm_service.LLMAdapter')
    def test_generate_response(self, mock_adapter):
        mock_adapter_instance = MagicMock()
        mock_adapter_instance.chat.return_value = {"response": "test response"}
        mock_adapter.return_value = mock_adapter_instance
        self.llm_service = LLMService(base_url="http://test-url")

        response = self.llm_service.generate_response("test message")
        self.assertEqual(response, {"response": "test response"})

    @patch('src.core.llm_service.LLMAdapter')
    def test_generate_response_stream(self, mock_adapter):
        mock_adapter_instance = MagicMock()
        mock_adapter_instance.chat_stream.return_value = (chunk for chunk in ["chunk1", "chunk2"])
        mock_adapter.return_value = mock_adapter_instance
        self.llm_service = LLMService(base_url="http://test-url")

        response = self.llm_service.generate_response_stream([{"role": "user", "content": "test message"}])
        self.assertEqual(list(response), ["chunk1", "chunk2"])
        
if __name__ == '__main__':
    unittest.main()
