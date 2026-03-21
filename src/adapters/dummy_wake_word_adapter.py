"""
Adaptateur de simulation pour la détection de mot-clé.
"""

from typing import Callable, List
import logging

logger = logging.getLogger(__name__)


class DummyWakeWordAdapter:
    """
    Adaptateur de simulation pour la détection de mot-clé.
    
    Simule la détection de mot-clé sans utiliser de modèle réel.
    Utile pour les tests et le développement.
    """
    
    def start(self, device_index: int, on_detect: Callable, on_audio: Callable) -> bool:
        """Simule le démarrage de la détection."""
        logger.info("🎤 Simulation: Détection de mot-clé démarrée (mode simulation)")
        return True
    
    def stop(self) -> None:
        """Simule l'arrêt de la détection."""
        logger.info("🎤 Simulation: Détection de mot-clé arrêtée")
    
    def get_audio_devices(self) -> List[str]:
        """Retourne une liste de périphériques simulés."""
        return ["Microphone (simulation)"]
