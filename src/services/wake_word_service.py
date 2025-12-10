import threading
import time
from typing import Callable, Optional
import os
import numpy as np
from abc import ABC, abstractmethod
from src.utils.logger import logger
from src.config.config import config
from src.interfaces.microphone_checker import MicrophoneChecker
from src.adapters.vosk_wake_word_adapter import VoskWakeWordAdapter

class IWakeWordAdapter(ABC):
    """Interface pour les adaptateurs de détection de mot-clé."""
    
    @abstractmethod
    def start(self, device_index: int, on_detect: Callable, on_audio: Callable) -> bool:
        """Démarre la détection avec les callbacks fournis."""
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """Arrête la détection."""
        pass
    
    @abstractmethod
    def get_audio_devices(self) -> list:
        """Retourne la liste des périphériques audio disponibles."""
        pass

class SimulatedWakeWordAdapter(IWakeWordAdapter):
    """Adaptateur simulé pour le développement."""
    
    def __init__(self):
        self.is_active = False
        self.detection_thread: Optional[threading.Thread] = None
        self._on_detect: Optional[Callable] = None
        self._on_audio: Optional[Callable] = None
        logger.info("SimulatedWakeWordAdapter initialisé")
    
    def start(self, device_index: int, on_detect: Callable, on_audio: Callable) -> bool:
        """Démarre la détection simulée."""
        self._on_detect = on_detect
        self._on_audio = on_audio
        self.is_active = True
        
        def detection_loop():
            logger.info("🔍 Détection simulée démarrée")
            counter = 0
            while self.is_active:
                time.sleep(2)  # Simulation
                counter += 1
                if counter % 3 == 0:  # Toutes les 6 secondes
                    logger.debug("🔍 Simulation détection mot-clé")
                    if self._on_detect:
                        self._on_detect()
            
            logger.info("⏹️ Détection simulée terminée")
        
        self.detection_thread = threading.Thread(target=detection_loop, daemon=True)
        self.detection_thread.start()
        return True
    
    def stop(self) -> None:
        """Arrête la détection simulée."""
        self.is_active = False
        logger.info("Détection simulée arrêtée")
    
    def get_audio_devices(self) -> list:
        """Retourne la liste des périphériques audio disponibles."""
        return [(0, "Microphone par défaut"), (1, "Microphone USB")]

class WakeWordService:
    """Service de détection du mot-clé avec injection de dépendance."""
    
    def __init__(self, wake_word_adapter: IWakeWordAdapter):
        self.wake_word_adapter = wake_word_adapter
        self.wake_word_callback: Optional[Callable] = None
        self.audio_callback: Optional[Callable] = None
        self._is_started = False
        logger.info("WakeWordService initialisé avec adaptateur")
    
    @classmethod
    def create_with_vosk(cls, model_path: str = None):
        """Factory method pour créer un WakeWordService avec Vosk."""
        if model_path is None:
            model_path = getattr(config, 'VOSK_MODEL_PATH', './models/vosk-model-small-fr')
        
        adapter = VoskWakeWordAdapter(model_path)
        return cls(adapter)
    
    @classmethod
    def create_with_simulation(cls):
        """Factory method pour créer un WakeWordService avec simulation."""
        adapter = SimulatedWakeWordAdapter()
        return cls(adapter)
    
    def set_wake_word_callback(self, callback: Callable):
        """Définit le callback pour la détection du mot-clé."""
        self.wake_word_callback = callback
        logger.debug("Callback wake word défini")
    
    def set_audio_callback(self, callback: Callable):
        """Définit le callback pour l'audio capturé."""
        self.audio_callback = callback
        logger.debug("Callback audio défini")
    
    def start_detection(self, device_index: int = 0):
        """Démarre la détection du mot-clé."""
        if self._is_started:
            logger.warning("La détection est déjà démarrée.")
            return

        logger.info(f"Démarrage détection wake word sur device {device_index}")
        
        def on_detect_wrapper():
            if self.wake_word_callback:
                self.wake_word_callback()
        
        def on_audio_wrapper(audio_data):
            if self.audio_callback:
                self.audio_callback(audio_data)
        
        success = self.wake_word_adapter.start(device_index, on_detect_wrapper, on_audio_wrapper)
        
        if not success:
            logger.warning("Échec du démarrage de la détection, tentative avec simulation")
            self.wake_word_adapter.stop()
            simulated_adapter = SimulatedWakeWordAdapter()
            self.wake_word_adapter = simulated_adapter
            self.wake_word_adapter.start(device_index, on_detect_wrapper, on_audio_wrapper)

        self._is_started = True
    
    def stop_detection(self):
        """Arrête la détection du mot-clé."""
        self.wake_word_adapter.stop()
        self._is_started = False
    
    def get_audio_devices(self) -> list:
        """Retourne la liste des périphériques audio disponibles."""
        return self.wake_word_adapter.get_audio_devices()
