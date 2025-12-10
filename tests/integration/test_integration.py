import unittest
import sys
import os

# Ajouter le chemin src pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.services.tts_service import TTSService
from src.services.speech_recognition_service import SpeechRecognitionService
from src.services.wake_word_service import WakeWordService
from src.services.llm_service import LLMService

class TestIntegration(unittest.TestCase):
    """Tests d'intégration pour vérifier l'orchestration des services"""
    
    def test_tts_service_with_piper_adapter(self):
        """Test du service TTS avec adaptateur Piper"""
        # Test avec la factory method
        tts_service = TTSService.create_with_piper("fr_FR-siwis-medium")
        self.assertIsInstance(tts_service, TTSService)
        self.assertTrue(hasattr(tts_service, 'tts_adapter'))
    
    def test_speech_recognition_with_whisper_adapter(self):
        """Test du service de reconnaissance vocale avec adaptateur Whisper"""
        # Test avec la factory method
        stt_service = SpeechRecognitionService.create_with_whisper("base")
        self.assertIsInstance(stt_service, SpeechRecognitionService)
        self.assertTrue(hasattr(stt_service, 'speech_recognition_adapter'))
    
    def test_wake_word_with_porcupine_adapter(self):
        """Test du service de détection de mot-clé avec adaptateur Porcupine"""
        # Test avec la factory method
        wake_service = WakeWordService.create_with_porcupine()
        self.assertIsInstance(wake_service, WakeWordService)
        self.assertTrue(hasattr(wake_service, 'wake_word_adapter'))
    
    def test_llm_with_ollama_adapter(self):
        """Test du service LLM avec adaptateur Ollama"""
        # Test avec la factory method (avec fallback automatique)
        llm_service = LLMService.create_with_ollama("qwen3-coder:latest")
        self.assertIsInstance(llm_service, LLMService)
        self.assertTrue(hasattr(llm_service, 'llm_adapter'))
    
    def test_full_pipeline_simulation(self):
        """Test du pipeline complet avec adaptateurs simulés"""
        # Créer des services avec adaptateurs simulés
        tts_service = TTSService.create_with_piper("fr_FR-siwis-medium")
        stt_service = SpeechRecognitionService.create_with_simulation()
        wake_service = WakeWordService.create_with_simulation()
        llm_service = LLMService.create_with_simulation()
        
        # Vérifier que tous les services sont créés correctement
        services = [tts_service, stt_service, wake_service, llm_service]
        for service in services:
            self.assertIsNotNone(service)
        
        # Test basique de fonctionnalité
        test_result = llm_service.test_service()
        self.assertIsInstance(test_result, bool)

if __name__ == '__main__':
    unittest.main()
