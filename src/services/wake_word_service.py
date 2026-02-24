from typing import Callable, Optional
from abc import ABC, abstractmethod
import logging
import sys

logger = logging.getLogger(__name__)

def _get_simulated_adapter_class():
    if 'src.core.wake_word_service' in sys.modules:
        return sys.modules['src.core.wake_word_service'].SimulatedWakeWordAdapter
    from .simulated_wake_word_adapter import SimulatedWakeWordAdapter
    return SimulatedWakeWordAdapter

class IWakeWordAdapter(ABC):
    """Interface for WakeWord adapters."""

    @abstractmethod
    def start(self, device_index, on_detect, on_audio) -> bool:
        ...

    @abstractmethod
    def stop(self) -> None:
        ...

    @abstractmethod
    def get_audio_devices(self) -> list:
        ...

class IWakeWordService(ABC):
    """Interface for WakeWord services."""

    @abstractmethod
    def set_wake_word_callback(self, callback: Callable[[], None]) -> None:
        ...

    @abstractmethod
    def set_audio_callback(self, callback: Callable[[bytes], None]) -> None:
        ...

    @abstractmethod
    def start_detection(self, device_index: int = 0) -> None:
        ...

    @abstractmethod
    def stop_detection(self) -> None:
        ...

    @abstractmethod
    def get_audio_devices(self) -> list:
        ...

class WakeWordService(IWakeWordService):
    """Concrete implementation used only for tests.
    It holds an adapter instance and forwards calls.
    """

    def __init__(self, adapter: IWakeWordAdapter):
        self.wake_word_adapter = adapter
        self.wake_word_callback: Optional[Callable[[], None]] = None
        self.audio_callback: Optional[Callable[[bytes], None]] = None

    def set_wake_word_callback(self, callback: Callable[[], None]) -> None:
        self.wake_word_callback = callback

    def set_audio_callback(self, callback: Callable[[bytes], None]) -> None:
        self.audio_callback = callback

    def start_detection(self, device_index: int = 0) -> None:
        if self.wake_word_callback is None or self.audio_callback is None:
            logger.warning("Callbacks not set before start_detection")
            return
        self.wake_word_adapter.start(device_index, self.wake_word_callback, self.audio_callback)

    def stop_detection(self) -> None:
        self.wake_word_adapter.stop()

    def get_audio_devices(self):
        return self.wake_word_adapter.get_audio_devices()

    @staticmethod
    def create_with_vosk() -> "WakeWordService":
        """Factory method to instantiate WakeWordService with the Vosk adapter.

        This method mirrors the real application factory used in the root
        composition. It loads the Vosk model from the path defined in
        :mod:`src.config` and passes a default microphone checker.
        """
        from ..config import config
        from ..adapters.vosk_wake_word_adapter import VoskWakeWordAdapter
        from ..interfaces.microphone_checker import Microphone_Checker as MicrophoneChecker
        mic_checker = MicrophoneChecker()
        adapter = VoskWakeWordAdapter(config.VOSK_MODEL_PATH, microphone_checker=mic_checker)
        return WakeWordService(adapter)

    @staticmethod
    def create_with_simulation() -> "WakeWordService":
        """Factory method to instantiate WakeWordService with the simulated adapter."""
        adapter = _get_simulated_adapter_class()()
        return WakeWordService(adapter)

# End of file