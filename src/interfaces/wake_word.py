from abc import ABC, abstractmethod
from typing import Callable, List

class IWakeWordAdapter(ABC):
    """Interface pour les adaptateurs de détection de mot-clé."""
    
    @abstractmethod
    def start(self, device_index: int, on_detect: Callable, on_audio: Callable) -> bool:
        """Démarre la détection avec les callbacks fournis."""
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """Arrête la détection."""
        pass
    
    @abstractmethod
    def get_audio_devices(self) -> List[str]:
        """Retourne la liste des périphériques audio disponibles."""
        pass
