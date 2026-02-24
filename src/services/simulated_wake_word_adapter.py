"""Simulated WakeWord adapter for unit tests.

Provides a minimal implementation of :class:`~src.services.wake_word_service.IWakeWordAdapter` that allows
control over the callbacks and can be easily mocked.
"""

from typing import Callable, Optional
from ..interfaces.wake_word import IWakeWordAdapter
import logging

logger = logging.getLogger(__name__)


class SimulatedWakeWordAdapter(IWakeWordAdapter):
    """A lightweight, deterministic adapter used in tests.

    The real adapter would stream audio from a microphone and run the
    detection algorithm.  The simulated version simply records calls and
    allows the test to trigger the ``on_detect`` callback manually.
    """

    def __init__(self) -> None:
        self._on_detect: Optional[Callable[[], None]] = None
        self._on_audio: Optional[Callable[[bytes], None]] = None
        self.start_called = False
        self.stop_called = False

    def start(self, device_index, on_detect, on_audio) -> bool:
        self.start_called = True
        self._on_detect = on_detect
        self._on_audio = on_audio
        logger.debug("SimulatedWakeWordAdapter start called with device %s", device_index)
        return True

    def stop(self) -> None:
        self.stop_called = True
        logger.debug("SimulatedWakeWordAdapter stopped")

    def get_audio_devices(self) -> list:
        return [(0, "Simulated Microphone")]

    # Helper for tests to manually trigger callbacks
    def trigger_detect(self) -> None:
        if self._on_detect:
            self._on_detect()

    def trigger_audio(self, data: bytes) -> None:
        if self._on_audio:
            self._on_audio(data)
