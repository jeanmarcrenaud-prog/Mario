# src/services/microphone_checker.py
from ..interfaces.microphone_checker import IMicrophoneChecker
from pvrecorder import PvRecorder
from ..utils.logger import logger

class MicrophoneChecker(IMicrophoneChecker):
    def is_microphone_available(self) -> bool:
        try:
            devices = PvRecorder.get_available_devices()
            available = len(devices) > 0
            if not available:
                logger.warning("❌ Aucun microphone détecté.")
            else:
                logger.info(f"✅ Microphone disponible: {len(devices)} périphérique(s) trouvé(s)")
            return available
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du microphone : {e}")
            return False
