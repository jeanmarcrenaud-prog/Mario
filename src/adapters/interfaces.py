from abc import ABC, abstractmethod

class IAudioInput(ABC):
    @abstractmethod
    def record(self) -> bytes:
        """Retourne des données audio (bytes)"""
        pass

class IAudioOutput(ABC):
    @abstractmethod
    def say(self, text: str, speed: float = 1.0) -> bool:
        """Joue le texte à une certaine vitesse, retourne True si OK"""
        pass
