# src/core/wake_word_service.py
# Wrapper for WakeWordService
from ..services.wake_word_service import WakeWordService
# Expose simulated adapter for testing
from ..services.simulated_wake_word_adapter import SimulatedWakeWordAdapter
