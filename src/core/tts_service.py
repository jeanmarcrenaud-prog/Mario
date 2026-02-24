# src/core/tts_service.py
# Re-export TTSService from services for backward compatibility
from ..services.tts_service import TTSService, PiperTTSAdapter, logger

# Allow direct imports
__all__ = ["TTSService", "PiperTTSAdapter", "logger"]
