# src/interfaces/microphone_status.py
from abc import ABC, abstractmethod

class IMicrophoneStatus(ABC):
    @abstractmethod
    def is_microphone_available(self) -> bool:
        pass
