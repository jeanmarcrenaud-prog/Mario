import unittest
import tempfile
import os
from unittest.mock import MagicMock, patch
import numpy as np
from src.core.speech_recognition_service import SpeechRecognitionService

class TestSpeechRecognitionService(unittest.TestCase):

    def setUp(self):
        self.speech_recognition_service = SpeechRecognitionService(model_name="base")

    def test_initialization(self):
        # Vérifie que le service s'initialise correctement
        self.assertIsNotNone(self.speech_recognition_service)
        self.assertEqual(self.speech_recognition_service.model_name, "base")

    @patch('src.core.speech_recognition_service.whisper')
    def test_load_model(self, mock_whisper):
        # Mock de whisper.load_model
        mock_model = MagicMock()
        mock_whisper.load_model.return_value = mock_model

        # Appel de la méthode de chargement du modèle
        result = self.speech_recognition_service._load_model()

        # Vérification du résultat
        self.assertTrue(result)
        self.assertIsNotNone(self.speech_recognition_service.model)

    @patch('src.core.speech_recognition_service.whisper')
    def test_transcribe(self, mock_whisper):
        # Mock de whisper.load_model et model.transcribe
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {"text": "test transcription"}
        mock_whisper.load_model.return_value = mock_model
        self.speech_recognition_service.model = mock_model

        # Appel de la méthode de transcription
        audio_data = np.zeros(16000, dtype=np.int16)
        result = self.speech_recognition_service.transcribe(audio_data)

        # Vérification du résultat
        self.assertEqual(result, "test transcription")
        mock_model.transcribe.assert_called_once()

    @patch('src.core.speech_recognition_service.whisper')
    def test_transcribe_failure(self, mock_whisper):
        # Mock de whisper.load_model et model.transcribe pour simuler une erreur
        mock_model = MagicMock()
        mock_model.transcribe.side_effect = Exception("Erreur de transcription")
        mock_whisper.load_model.return_value = mock_model
        self.speech_recognition_service.model = mock_model

        # Appel de la méthode de transcription
        audio_data = np.zeros(16000, dtype=np.int16)
        result = self.speech_recognition_service.transcribe(audio_data)

        # Vérification du résultat
        self.assertEqual(result, "")

    @patch('src.core.speech_recognition_service.whisper')
    def test_transcribe_file(self, mock_whisper):
        # Mock de whisper.load_model et model.transcribe
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {"text": "test transcription from file"}
        mock_whisper.load_model.return_value = mock_model
        self.speech_recognition_service.model = mock_model

        # Appel de la méthode de transcription de fichier
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            np.save(temp_file, np.zeros(16000, dtype=np.int16))
            temp_file_path = temp_file.name

        result = self.speech_recognition_service.transcribe_file(temp_file_path)

        # Vérification du résultat
        self.assertEqual(result, "test transcription from file")
        mock_model.transcribe.assert_called_once_with(temp_file_path, language="fr", fp16=False)

        # Nettoyage
        os.unlink(temp_file_path)

    def test_get_available_models(self):
        # Vérifie que la liste des modèles disponibles est correcte
        models = self.speech_recognition_service.get_available_models()
        self.assertEqual(models, ["tiny", "base", "small", "medium", "large"])

if __name__ == '__main__':
    unittest.main()
