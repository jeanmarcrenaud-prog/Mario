"""
Tests unitaires pour le service de synthèse vocale (TTS)
"""

import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Ajouter le chemin src pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.tts_service import TTSService, ITTSAdapter, PiperTTSAdapter

class MockTTSAdapter(ITTSAdapter):
    """Adaptateur mock pour les tests"""
    
    def __init__(self):
        self.say_called = False
        self.unload_voice_called = False
    
    def say(self, text: str, speed: float = 1.0) -> bool:
        self.say_called = True
        return True
    
    def unload_voice(self) -> bool:
        self.unload_voice_called = True
        return True
    
    def get_available_voices(self) -> list:
        return ["test-voice"]
    
    def optimize_cache(self) -> bool:
        return True

class TestTTSService(unittest.TestCase):
    """Tests pour TTSService"""

    def setUp(self):
        """Initialisation avant chaque test"""
        self.mock_adapter = MockTTSAdapter()
        self.tts_service = TTSService(self.mock_adapter)

    def test_initialization(self):
        """Test d'initialisation du service TTS"""
        self.assertIsNotNone(self.tts_service.tts_adapter)
        self.assertTrue(self.tts_service.is_available)
        self.assertIsInstance(self.tts_service, TTSService)

    def test_speak_success(self):
        """Test de synthèse vocale réussie"""
        result = self.tts_service.speak("Bonjour")
        
        self.assertTrue(result)
        self.assertTrue(self.mock_adapter.say_called)

    def test_speak_empty_text(self):
        """Test de synthèse vocale avec texte vide"""
        with patch('src.core.tts_service.logger') as mock_logger:
            result = self.tts_service.speak("")
            
            self.assertFalse(result)
            mock_logger.warning.assert_called_once()

    def test_speak_with_whitespace_only(self):
        """Test de synthèse vocale avec espaces uniquement"""
        with patch('src.core.tts_service.logger') as mock_logger:
            result = self.tts_service.speak("   ")
            
            self.assertFalse(result)
            mock_logger.warning.assert_called_once()

    def test_speak_unavailable_service(self):
        """Test de synthèse vocale avec service indisponible"""
        # Simuler un service indisponible
        self.tts_service.is_available = False
        
        with patch('src.core.tts_service.logger') as mock_logger:
            result = self.tts_service.speak("Bonjour")
            
            self.assertFalse(result)
            mock_logger.warning.assert_called_once_with("TTS non disponible, message ignoré")

    def test_speak_with_exception(self):
        """Test de synthèse vocale avec exception"""
        self.mock_adapter.say = MagicMock(side_effect=Exception("TTS Error"))
        
        with patch('src.core.tts_service.logger') as mock_logger:
            result = self.tts_service.speak("Bonjour")
            
            self.assertFalse(result)
            mock_logger.error.assert_called_once()

    def test_test_synthesis_success(self):
        """Test de synthèse de test réussie"""
        with patch('src.core.tts_service.logger') as mock_logger:
            result = self.tts_service.test_synthesis()
            
            self.assertTrue(result)
            mock_logger.info.assert_called_with("✅ Test TTS réussi")

    def test_test_synthesis_failure(self):
        """Test de synthèse de test échouée"""
        self.mock_adapter.say = MagicMock(return_value=False)
        # Recréer le service avec l'adaptateur modifié
        self.tts_service = TTSService(self.mock_adapter)
        
        with patch('src.core.tts_service.logger') as mock_logger:
            result = self.tts_service.test_synthesis()
            
            self.assertFalse(result)
            mock_logger.error.assert_called_once_with("❌ Test TTS échoué")

    def test_test_synthesis_with_custom_text(self):
        """Test de synthèse de test avec texte personnalisé"""
        test_text = "Test personnalisé"
        
        result = self.tts_service.test_synthesis(test_text)
        
        self.assertTrue(result)
        self.assertTrue(self.mock_adapter.say_called)

    def test_get_available_voices_success(self):
        """Test de récupération des voix disponibles"""
        voices = self.tts_service.get_available_voices()
        
        self.assertEqual(voices, ["test-voice"])

    def test_get_available_voices_with_exception(self):
        """Test de récupération des voix avec exception"""
        self.mock_adapter.get_available_voices = MagicMock(side_effect=Exception("Voice error"))
        
        with patch('src.core.tts_service.logger') as mock_logger:
            voices = self.tts_service.get_available_voices()
            
            self.assertEqual(voices, ["fr_FR-siwis-medium"])
            mock_logger.error.assert_called_once()

    def test_unload_voice_success(self):
        """Test de déchargement de voix réussi"""
        result = self.tts_service.unload_voice()
        
        self.assertTrue(result)
        self.assertTrue(self.mock_adapter.unload_voice_called)

    def test_unload_voice_with_exception(self):
        """Test de déchargement de voix avec exception"""
        self.mock_adapter.unload_voice = MagicMock(side_effect=Exception("Unload error"))
        
        with patch('src.core.tts_service.logger') as mock_logger:
            result = self.tts_service.unload_voice()
            
            self.assertFalse(result)
            mock_logger.error.assert_called_once()

    def test_optimize_voice_cache_success(self):
        """Test d'optimisation du cache voix"""
        result = self.tts_service.optimize_voice_cache()
        
        self.assertTrue(result)

    def test_optimize_voice_cache_with_exception(self):
        """Test d'optimisation du cache voix avec exception"""
        # Créer un mock qui n'a pas optimize_cache
        mock_adapter_no_cache = MagicMock()
        del mock_adapter_no_cache.optimize_cache  # Supprimer la méthode
        mock_adapter_no_cache.has_calls = []  # Ajouter un attribut pour le suivi
        
        service = TTSService(mock_adapter_no_cache)
        
        with patch('src.core.tts_service.logger') as mock_logger:
            result = service.optimize_voice_cache()
            
            self.assertFalse(result)

    def test_create_with_piper(self):
        """Test de la factory method create_with_piper"""
        with patch('src.core.tts_service.PiperTTSAdapter') as mock_piper:
            mock_adapter_instance = MagicMock()
            mock_piper.return_value = mock_adapter_instance
            
            service = TTSService.create_with_piper("test-voice")
            
            self.assertIsInstance(service, TTSService)
            mock_piper.assert_called_once_with("test-voice")

if __name__ == '__main__':
    unittest.main()
