import pytest
from unittest.mock import patch, MagicMock
import numpy as np
from src.core.wake_word_detector import WakeWordDetector

class TestWakeWordDetector:

    def test_initialize_porcupine_success(self):
        """Test l'initialisation réussie de Porcupine avec clé valide."""
        with patch('src.core.wake_word_detector.os.path.exists', return_value=True):
            with patch.dict('sys.modules', {'pvporcupine': MagicMock()}):
                with patch('pvporcupine.Porcupine') as mock_porcupine:
                    mock_porcupine.return_value = MagicMock()
                    with patch('src.config.config.PORCUPINE_ACCESS_KEY', 'fake_key'):
                        detector = WakeWordDetector()
                        result = detector.initialize_porcupine()
                        assert result is True
                        mock_porcupine.assert_called_once()

    def test_initialize_porcupine_missing_file(self):
        """Échec si fichier Porcupine manquant."""
        with patch('src.core.wake_word_detector.os.path.exists', return_value=False):
            detector = WakeWordDetector()
            result = detector.initialize_porcupine()
            assert result is False

    def test_initialize_porcupine_import_error(self):
        """Échec si pvporcupine n'est pas installé."""
        with patch.dict('sys.modules', {'pvporcupine': None}):
            detector = WakeWordDetector()
            result = detector.initialize_porcupine()
            assert result is False

    def test_set_wake_word_callback(self):
        """Test assignation du callback wake-word."""
        detector = WakeWordDetector()
        callback_mock = MagicMock()
        detector.set_wake_word_callback(callback_mock)
        assert detector.wake_word_callback == callback_mock

    def test_set_audio_callback(self):
        """Test assignation du callback audio."""
        detector = WakeWordDetector()
        callback_mock = MagicMock()
        detector.set_audio_callback(callback_mock)
        assert detector.audio_callback == callback_mock

    def test_calculate_energy(self):
        """Test calcul de l'énergie audio."""
        detector = WakeWordDetector()
        signal = np.array([1, -1, 2, -2], dtype=float)
        energy = detector._calculate_energy(signal)  # méthode privée
        expected_energy = float(np.sqrt(np.mean(signal ** 2)))
        assert energy == expected_energy
