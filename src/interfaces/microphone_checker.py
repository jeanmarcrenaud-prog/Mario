# interfaces/microphone_checker.py
from abc import ABC, abstractmethod

class MicrophoneChecker(ABC):
    @abstractmethod
    def is_microphone_available(self) -> bool:
        pass
