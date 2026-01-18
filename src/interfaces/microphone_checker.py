# interfaces/microphone_checker.py
from abc import ABC, abstractmethod
import pyaudio
import logging

logger = logging.getLogger(__name__)


class IMicrophoneChecker(ABC):
    @abstractmethod
    def is_microphone_available(self, device_index: int = None) -> bool:
        pass


class MicrophoneChecker(IMicrophoneChecker):
    """Implémentation par défaut du vérificateur de microphone."""
    
    def is_microphone_available(self, device_index: int = None) -> bool:
        """Vérifie si un microphone est disponible.
        
        Args:
            device_index: Index du périphérique audio (None pour le défaut)
            
        Returns:
            True si le microphone est disponible, False sinon
        """
        try:
            p = pyaudio.PyAudio()
            
            # Si aucun index spécifié, vérifier le microphone par défaut
            if device_index is None:
                device_index = p.get_default_input_device_info()['index']
            
            # Vérifier que le périphérique existe et a des canaux d'entrée
            device_info = p.get_device_info_by_index(device_index)
            is_available = device_info.get('maxInputChannels', 0) > 0
            
            p.terminate()
            return is_available
            
        except Exception as e:
            logger.warning(f"Erreur lors de la vérification du microphone: {e}")
            return False
