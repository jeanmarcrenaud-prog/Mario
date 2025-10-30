# tests/test_wake_word_detector.py - APPROCHE SIMPLIFIÉE
import pytest
import numpy as np
from unittest.mock import patch, MagicMock, call
from src.core.wake_word_detector import WakeWordDetector

class TestWakeWordDetector:
    
    def test_initialize_porcupine_success(self):
        """Test l'initialisation réussie de Porcupine."""
        # Mock conditionnel PLUS SIMPLE
        with patch('src.core.wake_word_detector.os.path.exists') as mock_exists:
            mock_exists.return_value = True
            
            # Mock l'import de Porcupine en le forçant à être disponible
            with patch.dict('sys.modules', {'pvporcupine': MagicMock()}):
                with patch('pvporcupine.Porcupine') as mock_porcupine:
                    mock_porcupine_instance = MagicMock()
                    mock_porcupine.return_value = mock_porcupine_instance
                    
                    detector = WakeWordDetector()
                    result = detector.initialize_porcupine()
                    
                    assert result == True
                    assert detector.porcupine == mock_porcupine_instance

    def test_initialize_porcupine_missing_file(self):
        """Test l'échec d'initialisation si fichier manquant."""
        with patch('src.core.wake_word_detector.os.path.exists') as mock_exists:
            mock_exists.return_value = False
            
            detector = WakeWordDetector()
            result = detector.initialize_porcupine()
            
            assert result == False
            assert detector.porcupine is None

    def test_initialize_porcupine_import_error(self):
        """Test l'échec d'initialisation si import error."""
        with patch('src.core.wake_word_detector.os.path.exists') as mock_exists:
            mock_exists.return_value = True
            
            # Simuler que pvporcupine n'est pas installé
            with patch.dict('sys.modules', {'pvporcupine': None}):
                detector = WakeWordDetector()
                result = detector.initialize_porcupine()
                
                assert result == False
                assert detector.porcupine is None

    # ... les autres tests restent simples et inchangés ...

    def test_set_callbacks(self):
        """Test la définition des callbacks."""
        detector = WakeWordDetector()
        
        wake_callback = MagicMock()
        audio_callback = MagicMock()
        
        detector.set_wake_word_callback(wake_callback)
        detector.set_audio_callback(audio_callback)
        
        assert detector.wake_word_callback == wake_callback
        assert detector.audio_callback == audio_callback

    def test_calculate_energy(self):
        """Test le calcul d'énergie audio."""
        detector = WakeWordDetector()
        
        audio_data = np.array([1000, -1000, 500, -500], dtype=np.int16)
        energy = detector._calculate_energy(audio_data)
        
        assert isinstance(energy, float)
        assert energy > 0

    # ... tests plus simples pour commencer ...
