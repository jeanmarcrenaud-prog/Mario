# interfaces/microphone_checker.py
from abc import ABC, abstractmethod

class IMicrophoneChecker(ABC):
    @abstractmethod
    def is_microphone_available(self) -> bool:
        pass
