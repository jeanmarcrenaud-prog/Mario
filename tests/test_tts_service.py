"""
Tests unitaires pour le service de synthèse vocale (TTS)
"""

import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Ajouter le chemin src pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.tts_service import TTSService

class TestTTSService(unittest.TestCase):
    """Tests pour TTSService"""

    def setUp(self):
        """Initialisation avant chaque test"""
        with patch('src.core.tts_service.logger'):
            self.tts_service = TTSService()
            # Initialize audio_cache for cache-related tests
            self.tts_service.audio_cache = {}

    def test_initialization(self):
        """Test d'initialisation du service TTS"""
        self.assertIsNotNone(self.tts_service)
        self.assertEqual(self.tts_service.voice_name, "fr_FR-siwis-medium")
        self.assertTrue(self.tts_service.is_available)

    def test_speak_success(self):
        """Test de synthèse vocale réussie"""
        with patch('src.core.tts_service.logger') as mock_logger:
            result = self.tts_service.speak("Bonjour")
            
            self.assertTrue(result)
            mock_logger.info.assert_called_with("🗣️ TTS: Bonjour")

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
        # Simuler une exception
        with patch('src.core.tts_service.logger') as mock_logger:
            mock_logger.info.side_effect = Exception("Erreur de log")
            
            result = self.tts_service.speak("Bonjour")
            
            self.assertFalse(result)
            mock_logger.error.assert_called_once()

    def test_test_synthesis_success(self):
        """Test de synthèse de test réussie"""
        with patch.object(self.tts_service, 'speak', return_value=True):
            with patch('src.core.tts_service.logger') as mock_logger:
                result = self.tts_service.test_synthesis()
                
                self.assertTrue(result)
                mock_logger.info.assert_called_with("✅ Test TTS réussi")

    def test_test_synthesis_failure(self):
        """Test de synthèse de test échouée"""
        with patch.object(self.tts_service, 'speak', return_value=False):
            with patch('src.core.tts_service.logger') as mock_logger:
                result = self.tts_service.test_synthesis()
                
                self.assertFalse(result)
                mock_logger.error.assert_called_once_with("❌ Test TTS échoué")

    def test_test_synthesis_with_custom_text(self):
        """Test de synthèse de test avec texte personnalisé"""
        test_text = "Test personnalisé"
        
        with patch.object(self.tts_service, 'speak') as mock_speak:
            mock_speak.return_value = True
            
            result = self.tts_service.test_synthesis(test_text)
            
            mock_speak.assert_called_once_with(test_text)

    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('src.config.config.config')  # Mock config at the source
    def test_get_available_voices_success(self, mock_config, mock_listdir, mock_exists):
        """Test de récupération des voix disponibles"""
        mock_exists.return_value = True
        mock_config.VOICES_FOLDER = "/voices"
        mock_config.DEFAULT_VOICE = "fr_FR-siwis-medium"
        
        # First call to listdir returns the voice directories
        # Second and third calls return files in each voice directory
        mock_listdir.side_effect = [
            ["voice1", "voice2"],  # First call: directories in VOICES_FOLDER
            [".onnx"],             # Second call: files in voice1 directory
            [".onnx"]              # Third call: files in voice2 directory
        ]
        
        with patch('os.path.isdir', return_value=True):
            voices = self.tts_service.get_available_voices()
            
            self.assertIn("voice1", voices)
            self.assertIn("voice2", voices)

    @patch('os.path.exists')
    @patch('src.config.config.config')  # Mock config at the source
    def test_get_available_voices_no_folder(self, mock_config, mock_exists):
        """Test de récupération des voix avec dossier inexistant"""
        mock_exists.return_value = False
        mock_config.VOICES_FOLDER = "/nonexistent"
        mock_config.DEFAULT_VOICE = "fr_FR-siwis-medium"
        
        voices = self.tts_service.get_available_voices()
        
        self.assertEqual(voices, ["fr_FR-siwis-medium"])

    @patch('os.path.exists')
    @patch('os.listdir')
    @patch('src.config.config.config')  # Mock config at the source
    def test_get_available_voices_exception(self, mock_config, mock_listdir, mock_exists):
        """Test de récupération des voix avec exception"""
        mock_exists.return_value = True
        mock_listdir.side_effect = Exception("Erreur d'accès")
        mock_config.VOICES_FOLDER = "/voices"
        mock_config.DEFAULT_VOICE = "fr_FR-siwis-medium"
        
        with patch('src.core.tts_service.logger') as mock_logger:
            voices = self.tts_service.get_available_voices()
            
            self.assertEqual(voices, ["fr_FR-siwis-medium"])
            mock_logger.error.assert_called_once()

    def test_unload_voice_with_engine(self):
        """Test de déchargement de voix avec moteur"""
        # Simuler un moteur TTS
        mock_engine = MagicMock()
        mock_engine.cleanup = MagicMock()
        self.tts_service.tts_engine = mock_engine
        
        with patch('src.core.tts_service.logger') as mock_logger:
            result = self.tts_service.unload_voice()
            
            self.assertTrue(result)
            mock_engine.cleanup.assert_called_once()
            mock_logger.info.assert_called_with("🗑️ Voix déchargée")

    def test_unload_voice_with_current_voice(self):
        """Test de déchargement de voix avec voix courante"""
        # Simuler une voix courante
        self.tts_service.current_voice = "test_voice"
        
        with patch('src.core.tts_service.logger') as mock_logger:
            result = self.tts_service.unload_voice()
            
            self.assertTrue(result)
            self.assertIsNone(self.tts_service.current_voice)
            mock_logger.info.assert_called_with("🗑️ Voix déchargée")

    def test_unload_voice_nothing_to_unload(self):
        """Test de déchargement de voix sans rien à décharger"""
        # S'assurer qu'il n'y a rien à décharger
        if hasattr(self.tts_service, 'tts_engine'):
            delattr(self.tts_service, 'tts_engine')
        if hasattr(self.tts_service, 'current_voice'):
            delattr(self.tts_service, 'current_voice')
        
        result = self.tts_service.unload_voice()
        self.assertFalse(result)

    def test_unload_voice_with_exception(self):
        """Test de déchargement de voix avec exception"""
        # Simuler un moteur TTS qui lève une exception
        mock_engine = MagicMock()
        mock_engine.cleanup.side_effect = Exception("Erreur de nettoyage")
        self.tts_service.tts_engine = mock_engine
        
        with patch('src.core.tts_service.logger') as mock_logger:
            result = self.tts_service.unload_voice()
            
            self.assertFalse(result)
            mock_logger.error.assert_called_once()

    def test_optimize_voice_cache_with_cache(self):
        """Test d'optimisation du cache voix avec cache"""
        # Simuler un cache avec plus de 50 entrées pour déclencher l'optimisation
        self.tts_service.audio_cache = {}
        for i in range(60):
            self.tts_service.audio_cache[f"key{i}"] = f"value{i}"
        
        result = self.tts_service.optimize_voice_cache()
        self.assertTrue(result)
        # After optimization, cache should be reduced (implementation depends on your logic)