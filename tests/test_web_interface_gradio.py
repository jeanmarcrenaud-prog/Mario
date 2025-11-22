"""
Tests unitaires pour l'interface web Gradio
"""

import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Ajouter le chemin src pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.views.web_interface_gradio import GradioWebInterface

class TestWebInterfaceGradio(unittest.TestCase):
    """Tests pour l'interface web Gradio"""

    def setUp(self):
        """Initialisation avant chaque test"""
        # Créer un mock pour l'assistant controller
        self.mock_assistant = MagicMock()
        
        # Configurer les mocks nécessaires
        self.mock_assistant.settings.web_port = 7860
        self.mock_assistant.settings.llm_model = "qwen3-coder:latest"
        self.mock_assistant.settings.voice_name = "fr_FR-siwis-medium"
        
        # Mocks pour les services
        self.mock_assistant.wake_word_service.get_audio_devices.return_value = [(0, "Microphone test")]
        self.mock_assistant.tts_service.get_available_voices.return_value = ["fr_FR-siwis-medium"]
        self.mock_assistant.llm_service.get_available_models.return_value = ["qwen3-coder:latest"]
        self.mock_assistant.system_monitor.get_system_stats.return_value = {
            "cpu_percent": 25.0,
            "memory_percent": 60.0
        }
        
        self.interface = GradioWebInterface(self.mock_assistant)

    def test_initialization(self):
        """Test d'initialisation de l'interface"""
        self.assertIsNotNone(self.interface)
        self.assertEqual(self.interface.assistant, self.mock_assistant)
        self.assertIsNone(self.interface.demo)
        self.assertEqual(self.interface.chat_history, [])

    @patch('src.views.web_interface_gradio.gr')
    def test_create_interface(self, mock_gr):
        """Test de création de l'interface"""
        # Configurer les mocks Gradio
        mock_blocks = MagicMock()
        mock_gr.Blocks.return_value.__enter__.return_value = mock_blocks
        
        # Mock pour les composants Gradio
        mock_blocks.Markdown = MagicMock()
        mock_blocks.Row = MagicMock()
        mock_blocks.Column = MagicMock()
        mock_blocks.Tabs = MagicMock()
        mock_blocks.Tab = MagicMock()
        mock_blocks.Group = MagicMock()
        mock_blocks.Accordion = MagicMock()
        mock_blocks.State = MagicMock()
        mock_blocks.Textbox = MagicMock()
        mock_blocks.Button = MagicMock()
        mock_blocks.Dropdown = MagicMock()
        mock_blocks.Slider = MagicMock()
        mock_blocks.Chatbot = MagicMock()
        mock_blocks.File = MagicMock()
        mock_blocks.Dataframe = MagicMock()
        mock_blocks.Number = MagicMock()
        
        # Appeler la méthode
        interface = self.interface.create_interface()
        
        # Vérifier que l'interface a été créée
        self.assertIsNotNone(interface)
        mock_gr.Blocks.assert_called_once()

    def test_get_microphone_choices(self):
        """Test de récupération des microphones"""
        # Configurer le mock
        self.mock_assistant.wake_word_service.get_audio_devices.return_value = [
            (0, "Microphone 1"),
            (1, "Microphone 2")
        ]
        
        choices = self.interface._get_microphone_choices()
        expected = ["0: Microphone 1", "1: Microphone 2"]
        self.assertEqual(choices, expected)

    def test_get_microphone_choices_error(self):
        """Test de récupération des microphones avec erreur"""
        # Configurer le mock pour lever une exception
        self.mock_assistant.wake_word_service.get_audio_devices.side_effect = Exception("Erreur")
        
        choices = self.interface._get_microphone_choices()
        expected = ["0: Microphone par défaut"]
        self.assertEqual(choices, expected)

    def test_get_voice_choices(self):
        """Test de récupération des voix"""
        # Configurer le mock
        self.mock_assistant.tts_service.get_available_voices.return_value = [
            "fr_FR-siwis-medium",
            "fr_FR-gilles-low"
        ]
        
        choices = self.interface._get_voice_choices()
        expected = ["fr_FR-siwis-medium", "fr_FR-gilles-low"]
        self.assertEqual(choices, expected)

    def test_get_voice_choices_error(self):
        """Test de récupération des voix avec erreur"""
        # Configurer le mock pour lever une exception
        self.mock_assistant.tts_service.get_available_voices.side_effect = Exception("Erreur")
        
        choices = self.interface._get_voice_choices()
        expected = ["fr_FR-siwis-medium"]
        self.assertEqual(choices, expected)

    def test_get_model_choices(self):
        """Test de récupération des modèles"""
        # Configurer le mock
        self.mock_assistant.llm_service.get_available_models.return_value = [
            "qwen3-coder:latest",
            "llama3.2:latest",
            "gemma2:latest"
        ]
        
        choices = self.interface._get_model_choices()
        # Devrait filtrer et retourner les modèles pertinents
        self.assertIn("qwen3-coder:latest", choices)
        self.assertIn("llama3.2:latest", choices)
        self.assertIn("gemma2:latest", choices)

    def test_get_model_choices_error(self):
        """Test de récupération des modèles avec erreur"""
        # Configurer le mock pour lever une exception
        self.mock_assistant.llm_service.get_available_models.side_effect = Exception("Erreur")
        
        choices = self.interface._get_model_choices()
        # Devrait retourner les modèles par défaut
        self.assertIn("qwen3-coder:latest", choices)

    def test_get_default_model(self):
        """Test du modèle par défaut"""
        default_model = self.interface._get_default_model()
        self.assertEqual(default_model, "qwen3-coder:latest")

    def test_get_chat_history(self):
        """Test de récupération de l'historique du chat"""
        # Configurer le mock pour l'historique
        mock_history = [
            {"role": "user", "content": "Bonjour"},
            {"role": "assistant", "content": "Salut!"}
        ]
        self.mock_assistant.get_conversation_history.return_value = mock_history
        
        history = self.interface._get_chat_history()
        expected = [
            {"role": "user", "content": "Bonjour"},
            {"role": "assistant", "content": "Salut!"}
        ]
        self.assertEqual(history, expected)

    def test_get_chat_history_error(self):
        """Test de récupération de l'historique avec erreur"""
        # Configurer le mock pour lever une exception
        self.mock_assistant.get_conversation_history.side_effect = Exception("Erreur")
        
        history = self.interface._get_chat_history()
        self.assertEqual(history, [])

    def test_get_system_stats_text(self):
        """Test de récupération des stats système"""
        # Configurer le mock
        self.mock_assistant.system_monitor.get_system_stats.return_value = {
            "cpu_percent": 25.5,
            "memory_percent": 60.3,
            "gpu_memory_used": 1024
        }
        
        stats_text = self.interface._get_system_stats_text()
        self.assertIn("CPU: 25.5%", stats_text)
        self.assertIn("Mémoire: 60.3%", stats_text)
        self.assertIn("GPU: 1024MB", stats_text)

    def test_get_system_stats_text_no_gpu(self):
        """Test de récupération des stats système sans GPU"""
        # Configurer le mock
        self.mock_assistant.system_monitor.get_system_stats.return_value = {
            "cpu_percent": 25.5,
            "memory_percent": 60.3
        }
        
        stats_text = self.interface._get_system_stats_text()
        self.assertIn("CPU: 25.5%", stats_text)
        self.assertIn("Mémoire: 60.3%", stats_text)
        self.assertNotIn("GPU:", stats_text)

    def test_get_system_stats_text_error(self):
        """Test de récupération des stats avec erreur"""
        # Configurer le mock pour lever une exception
        self.mock_assistant.system_monitor.get_system_stats.side_effect = Exception("Erreur")
        
        stats_text = self.interface._get_system_stats_text()
        self.assertEqual(stats_text, "❌ Erreur stats")

    def test_refresh_chat(self):
        """Test de rafraîchissement du chat"""
        # Configurer le mock
        mock_history = [{"role": "user", "content": "Test"}]
        self.interface._get_chat_history = MagicMock(return_value=mock_history)
        
        result = self.interface._refresh_chat()
        self.assertEqual(result, mock_history)

    def test_refresh_chat_error(self):
        """Test de rafraîchissement du chat avec erreur"""
        # Configurer le mock pour lever une exception
        self.interface._get_chat_history = MagicMock(side_effect=Exception("Erreur"))
        
        result = self.interface._refresh_chat()
        self.assertEqual(result, [])

    @patch('src.views.web_interface_gradio.gr')
    def test_launch(self, mock_gr):
        """Test du lancement de l'interface"""
        # Configurer les mocks
        mock_demo = MagicMock()
        self.interface.demo = mock_demo
        
        # Appeler la méthode
        self.interface.launch(server_port=7860)
        
        # Vérifier que launch a été appelé
        mock_demo.launch.assert_called_once_with(server_port=7860)

    def test_get_default_microphone(self):
        """Test de récupération du microphone par défaut"""
        # Cas normal
        self.interface._get_microphone_choices = MagicMock(return_value=["0: Microphone 1", "1: Microphone 2"])
        default_mic = self.interface._get_default_microphone()
        self.assertEqual(default_mic, "0: Microphone 1")
        
        # Cas vide
        self.interface._get_microphone_choices = MagicMock(return_value=[])
        default_mic = self.interface._get_default_microphone()
        self.assertEqual(default_mic, "0: Microphone par défaut")

    def test_get_default_voice(self):
        """Test de récupération de la voix par défaut"""
        default_voice = self.interface._get_default_voice()
        self.assertEqual(default_voice, "fr_FR-siwis-medium")

    def test_get_default_local_models(self):
        """Test de récupération des modèles locaux par défaut"""
        models = self.interface._get_default_local_models()
        # Vérifier que qwen3-coder est présent (votre modèle par défaut)
        self.assertIn("qwen3-coder:latest", models)
        # Vérifier qu'il y a au moins un modèle
        self.assertGreater(len(models), 0)
        # OU vérifier que la liste contient les modèles attendus (ajuster selon l'implémentation réelle)
        expected_models = ["qwen3-coder:latest"]  # Ajuster selon votre implémentation
        for model in expected_models:
            if model in models:
                self.assertIn(model, models)

if __name__ == '__main__':
    # Exécuter les tests avec plus de verbosité
    unittest.main(verbosity=2)
