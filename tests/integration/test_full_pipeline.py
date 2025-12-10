# tests/integration/test_full_pipeline.py
import pytest
import numpy as np
from src.core.app_factory import create_assistant

class TestFullPipeline:
    """Tests du pipeline complet de l'assistant"""

    def test_assistant_creation_with_vosk(self):
        """Test de création de l'assistant avec Vosk"""
        assistant = create_assistant()
        
        assert assistant is not None
        assert hasattr(assistant, 'wake_word_service')
        assert hasattr(assistant, 'tts_service')
        assert hasattr(assistant, 'speech_recognition_service')
        assert hasattr(assistant, 'llm_service')

    def test_service_interactions(self):
        """Test des interactions entre services"""
        assistant = create_assistant()
        
        # Simuler un message utilisateur
        test_message = "Bonjour, comment allez-vous ?"
        
        # Traiter le message
        response = assistant.process_user_message(test_message)
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert response != "[ERREUR] Impossible de traiter votre message"

    def test_audio_pipeline(self):
        """Test du pipeline audio complet"""
        assistant = create_assistant()
        
        # Créer un audio de test
        test_audio = np.zeros(16000, dtype=np.int16)  # 1 seconde
        
        # Simuler la transcription
        transcribed = assistant.speech_recognition_service.transcribe(test_audio)
        
        # Vérifier que la transcription fonctionne (même simulée)
        assert isinstance(transcribed, str)
