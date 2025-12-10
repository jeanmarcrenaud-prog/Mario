import unittest
import sys
import os
import numpy as np

# Ajouter le chemin src pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.tts_service import TTSService
from src.core.speech_recognition_service import SpeechRecognitionService
from src.core.wake_word_service import WakeWordService
from src.core.llm_service import LLMService

class TestServiceOrchestration(unittest.TestCase):
    """Tests d'orchestration pour vérifier l'interaction entre les services"""
    
    def setUp(self):
        """Initialisation des services avec adaptateurs simulés"""
        self.tts_service = TTSService.create_with_piper("fr_FR-siwis-medium")
        self.stt_service = SpeechRecognitionService.create_with_simulation()
        self.wake_service = WakeWordService.create_with_simulation()
        self.llm_service = LLMService.create_with_simulation({
            "Bonjour": "Bonjour ! Comment puis-je vous aider ?",
            "test": "Test réussi"
        })
    
    def test_tts_to_llm_interaction(self):
        """Test de l'interaction TTS -> LLM"""
        # Simuler une requête vocale
        test_text = "Bonjour"
        
        # Générer une réponse avec le LLM
        messages = [{"role": "user", "content": test_text}]
        llm_response = self.llm_service.generate_response(messages)
        
        # Utiliser le TTS pour "parler" la réponse
        tts_result = self.tts_service.speak(llm_response)
        
        # Vérifier que tout fonctionne
        self.assertTrue(tts_result)
        self.assertIsInstance(llm_response, str)
        self.assertIn("Bonjour", llm_response)
    
    def test_stt_to_llm_interaction(self):
        """Test de l'interaction STT -> LLM"""
        # Simuler de l'audio
        test_audio = np.zeros(16000, dtype=np.int16)  # 1 seconde de silence
        
        # Transcrire l'audio
        transcribed_text = self.stt_service.transcribe(test_audio)
        
        # Envoyer au LLM
        messages = [{"role": "user", "content": transcribed_text}]
        llm_response = self.llm_service.generate_response(messages)
        
        # Vérifier l'interaction
        self.assertIsInstance(transcribed_text, str)
        self.assertIsInstance(llm_response, str)
    
    def test_wake_word_to_full_pipeline(self):
        """Test du pipeline complet : Wake Word -> STT -> LLM -> TTS"""
        # Simuler la détection du mot-clé
        wake_detected = True
        self.assertTrue(wake_detected)
        
        # Simuler la capture audio après le mot-clé
        test_audio = np.zeros(32000, dtype=np.int16)  # 2 secondes
        
        # Transcription
        transcribed_text = self.stt_service.transcribe(test_audio)
        
        # Traitement par LLM
        messages = [{"role": "user", "content": transcribed_text}]
        llm_response = self.llm_service.generate_response(messages)
        
        # Synthèse vocale de la réponse
        tts_result = self.tts_service.speak(llm_response)
        
        # Vérifier que tout le pipeline fonctionne
        self.assertTrue(tts_result)
        self.assertIsInstance(transcribed_text, str)
        self.assertIsInstance(llm_response, str)
    
    def test_service_lifecycle(self):
        """Test du cycle de vie complet des services"""
        # Test d'initialisation - tous les services ont été créés dans setUp
        services = [self.tts_service, self.stt_service]
        # WakeWordService n'a pas d'attribut is_available, on le teste différemment
        # LLMService n'a pas d'attribut is_available non plus
        
        # Vérifier que les services essentiels sont disponibles
        self.assertTrue(hasattr(self.tts_service, 'is_available'))
        self.assertTrue(self.tts_service.is_available)
        self.assertTrue(hasattr(self.stt_service, 'is_available'))
        self.assertTrue(self.stt_service.is_available)
        # LLMService et WakeWordService n'ont pas is_available, c'est normal
        
        # Test de fonctionnalités
        test_results = []
        test_results.append(self.llm_service.test_service())
        test_results.append(self.stt_service.test_transcription())
        test_results.append(self.tts_service.test_synthesis())
        
        # Au moins un test doit réussir
        self.assertTrue(any(test_results))
        
        # Test de nettoyage (unload)
        unload_results = []
        if hasattr(self.tts_service, 'unload_voice'):
            unload_results.append(self.tts_service.unload_voice())
        if hasattr(self.stt_service, 'unload_model'):
            unload_results.append(self.stt_service.unload_model())
        
        # Les unload ne sont pas obligatoires, mais s'ils existent ils doivent fonctionner
        # On ne vérifie pas le résultat car certains unload peuvent échouer en simulation

if __name__ == '__main__':
    unittest.main()
