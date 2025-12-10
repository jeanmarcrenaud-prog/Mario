import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Ajouter le chemin src pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.services.wake_word_service import IWakeWordService, IWakeWordAdapter

class MockWakeWordAdapter(IWakeWordAdapter):
    """Adaptateur mock pour les tests"""
    
    def __init__(self):
        self.start_called = False
        self.stop_called = False
        self.get_audio_devices_called = False
        self.start_args = None
    
    def start(self, device_index, on_detect, on_audio):
        self.start_called = True
        self.start_args = (device_index, on_detect, on_audio)
        return True
    
    def stop(self):
        self.stop_called = True
    
    def get_audio_devices(self):
        self.get_audio_devices_called = True
        return [(0, "Test Microphone")]

class TestWakeWordService(unittest.TestCase):

    def setUp(self):
        """Initialisation avant chaque test"""
        self.mock_adapter = MockWakeWordAdapter()
        self.wake_word_service = WakeWordService(self.mock_adapter)

    def test_initialization(self):
        """Test d'initialisation du service"""
        self.assertIsNotNone(self.wake_word_service.wake_word_adapter)
        self.assertIsNone(self.wake_word_service.wake_word_callback)
        self.assertIsNone(self.wake_word_service.audio_callback)

    def test_set_wake_word_callback(self):
        """Test de définition du callback wake word"""
        callback = MagicMock()
        self.wake_word_service.set_wake_word_callback(callback)
        self.assertEqual(self.wake_word_service.wake_word_callback, callback)

    def test_set_audio_callback(self):
        """Test de définition du callback audio"""
        callback = MagicMock()
        self.wake_word_service.set_audio_callback(callback)
        self.assertEqual(self.wake_word_service.audio_callback, callback)

    def test_start_detection(self):
        """Test de démarrage de la détection"""
        self.wake_word_service.set_wake_word_callback(MagicMock())
        self.wake_word_service.set_audio_callback(MagicMock())
        
        self.wake_word_service.start_detection(1)
        
        self.assertTrue(self.mock_adapter.start_called)
        self.assertEqual(self.mock_adapter.start_args[0], 1)

    def test_stop_detection(self):
        """Test d'arrêt de la détection"""
        self.wake_word_service.stop_detection()
        self.assertTrue(self.mock_adapter.stop_called)

    def test_get_audio_devices(self):
        """Test de récupération des périphériques audio"""
        devices = self.wake_word_service.get_audio_devices()
        self.assertTrue(self.mock_adapter.get_audio_devices_called)
        self.assertEqual(devices, [(0, "Test Microphone")])

    def test_create_with_porcupine(self):
        """Test de la factory method create_with_porcupine"""
        with patch('src.core.wake_word_service.PorcupineWakeWordAdapter') as mock_porcupine:
            mock_adapter_instance = MagicMock()
            mock_porcupine.return_value = mock_adapter_instance
            
            service = WakeWordService.create_with_porcupine()
            
            self.assertIsInstance(service, WakeWordService)
            mock_porcupine.assert_called_once()

    def test_create_with_simulation(self):
        """Test de la factory method create_with_simulation"""
        with patch('src.core.wake_word_service.SimulatedWakeWordAdapter') as mock_simulated:
            mock_adapter_instance = MagicMock()
            mock_simulated.return_value = mock_adapter_instance
            
            service = WakeWordService.create_with_simulation()
            
            self.assertIsInstance(service, WakeWordService)
            mock_simulated.assert_called_once()

if __name__ == '__main__':
    unittest.main()
