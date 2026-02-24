import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import numpy as np

# Ajouter le chemin src pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.services.speech_recognition_service import SpeechRecognitionService, ISpeechRecognitionAdapter

class MockSpeechRecognitionAdapter(ISpeechRecognitionAdapter):
    """Adaptateur mock pour les tests"""
    
    def __init__(self):
        self.transcribe_array_called = False
        self.transcribe_file_called = False
        self.unload_called = False
        self.optimize_cache_called = False
    
    def transcribe_array(self, audio_data, language="fr"):
        self.transcribe_array_called = True
        return "Test transcription"
    
    def transcribe_file(self, file_path, language="fr"):
        self.transcribe_file_called = True
        return "Test file transcription"
    
    def unload(self):
        self.unload_called = True
        return True
    
    def optimize_cache(self):
        self.optimize_cache_called = True
        return True
    
    def get_available_models(self):
        return ["tiny", "base", "small"]

class TestSpeechRecognitionService(unittest.TestCase):

    def setUp(self):
        """Initialisation avant chaque test"""
        self.mock_adapter = MockSpeechRecognitionAdapter()
        self.speech_recognition_service = SpeechRecognitionService(self.mock_adapter)

    def test_initialization(self):
        """Test d'initialisation du service"""
        self.assertIsNotNone(self.speech_recognition_service.speech_recognition_adapter)
        self.assertTrue(self.speech_recognition_service.is_available)

    def test_transcribe(self):
        """Test de transcription audio"""
        audio_data = np.array([1, 2, 3], dtype=np.int16)
        result = self.speech_recognition_service.transcribe(audio_data)
        
        self.assertEqual(result, "Test transcription")
        self.assertTrue(self.mock_adapter.transcribe_array_called)

    def test_transcribe_file(self):
        """Test de transcription de fichier"""
        result = self.speech_recognition_service.transcribe_file("test.wav")
        
        self.assertEqual(result, "Test file transcription")
        self.assertTrue(self.mock_adapter.transcribe_file_called)

    def test_unload_model(self):
        """Test de déchargement du modèle"""
        result = self.speech_recognition_service.unload_model()
        
        self.assertTrue(result)
        self.assertTrue(self.mock_adapter.unload_called)

    def test_optimize_model_cache(self):
        """Test d'optimisation du cache"""
        result = self.speech_recognition_service.optimize_model_cache()
        
        self.assertTrue(result)
        self.assertTrue(self.mock_adapter.optimize_cache_called)

    def test_get_available_models(self):
        """Test de récupération des modèles disponibles"""
        models = self.speech_recognition_service.get_available_models()
        self.assertIsInstance(models, list)
        self.assertIn("base", models)

    def test_transcribe_with_exception(self):
        """Test de transcription avec exception"""
        self.mock_adapter.transcribe_array = MagicMock(side_effect=Exception("Transcription error"))
        
        audio_data = np.array([1, 2, 3], dtype=np.int16)
        result = self.speech_recognition_service.transcribe(audio_data)
        
        self.assertEqual(result, "")

    def test_transcribe_file_with_exception(self):
        """Test de transcription de fichier avec exception"""
        self.mock_adapter.transcribe_file = MagicMock(side_effect=Exception("File transcription error"))
        
        result = self.speech_recognition_service.transcribe_file("test.wav")
        
        self.assertEqual(result, "")

    def test_test_transcription(self):
        """Test de transcription de test"""
        with patch('src.core.speech_recognition_service.logger'):
            result = self.speech_recognition_service.test_transcription()
            self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
