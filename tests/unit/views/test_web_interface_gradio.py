import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Ajouter le chemin src pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.views.web_interface_gradio import GradioWebInterface

class TestWebInterfaceGradio(unittest.TestCase):

    def setUp(self):
        """Initialisation avant chaque test"""
        self.mock_assistant = MagicMock()
        self.interface = GradioWebInterface(self.mock_assistant)

    def test_initialization(self):
        """Test d'initialisation de l'interface"""
        self.assertIsNotNone(self.interface.assistant)
        self.assertIsNone(self.interface.demo)

    # Tests pour les méthodes de gestion audio
    def test_get_microphone_choices(self):
        """Test de récupération des microphones"""
        # Configurer le mock
        with patch.object(self.interface.audio_controller, 'get_microphones', return_value=["0: Microphone 1", "1: Microphone 2"]):
            choices = self.interface._get_microphone_choices()
            self.assertIsInstance(choices, list)

    def test_get_microphone_choices_error(self):
        """Test de récupération des microphones avec erreur"""
        # Configurer le mock pour lever une exception
        with patch.object(self.interface.audio_controller, 'get_microphones', side_effect=Exception("Erreur")):
            # L'exception doit être gérée par la méthode, donc on s'attend à avoir une valeur de retour par défaut
            try:
                choices = self.interface._get_microphone_choices()
                # Si l'exception est correctement gérée, on doit avoir une liste de retour
                self.assertIsInstance(choices, list)
            except Exception:
                # Si l'exception n'est pas gérée, le test échoue
                self.fail("L'exception n'a pas été gérée correctement")

    def test_get_default_microphone(self):
        """Test de récupération du microphone par défaut"""
        with patch.object(self.interface.audio_controller, 'get_default_microphone', return_value="0: Microphone 1"):
            default_mic = self.interface._get_default_microphone()
            self.assertIsInstance(default_mic, str)

    # Tests pour les méthodes de gestion des voix
    def test_get_voice_choices(self):
        """Test de récupération des voix"""
        # Configurer le mock
        self.mock_assistant.tts_service = MagicMock()
        self.mock_assistant.tts_service.get_available_voices.return_value = ["voice1", "voice2"]

        choices = self.interface._get_voice_choices()
        self.assertEqual(choices, ["voice1", "voice2"])

    def test_get_voice_choices_error(self):
        """Test de récupération des voix avec erreur"""
        # Configurer le mock pour lever une exception
        self.mock_assistant.tts_service = MagicMock()
        self.mock_assistant.tts_service.get_available_voices.side_effect = Exception("Erreur")

        choices = self.interface._get_voice_choices()
        self.assertEqual(choices, ["fr_FR-siwis-medium"])

    def test_get_default_voice(self):
        """Test de récupération de la voix par défaut"""
        default_voice = self.interface._get_default_voice()
        self.assertEqual(default_voice, "fr_FR-siwis-medium")

    # Tests pour les méthodes de gestion des modèles
    def test_get_model_choices(self):
        """Test de récupération des modèles"""
        # Configurer le mock
        self.mock_assistant.llm_service = MagicMock()
        self.mock_assistant.llm_service.get_available_models.return_value = ["model1", "model2"]

        choices = self.interface._get_model_choices()
        self.assertIsInstance(choices, list)

    def test_get_default_model(self):
        """Test de récupération du modèle par défaut"""
        default_model = self.interface._get_default_model()
        self.assertEqual(default_model, "qwen3-coder:latest")

    # Tests pour les méthodes de gestion des prompts
    def test_get_saved_prompts(self):
        """Test de récupération des prompts sauvegardés"""
        prompts = self.interface._get_saved_prompts()
        self.assertIsInstance(prompts, list)
        self.assertGreater(len(prompts), 0)

    @patch('src.views.web_interface_gradio.gr')
    def test_launch(self, mock_gr):
        """Test du lancement de l'interface"""
        # Configurer les mocks
        mock_demo = MagicMock()
        self.interface.demo = mock_demo

        # Appeler la méthode
        self.interface.launch(server_port=7860)

        # Vérifier que launch a été appelé (les paramètres exacts peuvent varier)
        mock_demo.launch.assert_called()

if __name__ == '__main__':
    unittest.main()
