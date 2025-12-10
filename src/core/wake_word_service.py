import threading
import time
from typing import Callable, Optional
import os
import numpy as np
from abc import ABC, abstractmethod
from ..utils.logger import logger
from ..config.config import config
from ..services.microphone_checker import MicrophoneChecker
from ..adapters.vosk_wake_word_adapter import VoskWakeWordAdapter

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

class PorcupineWakeWordAdapter(IWakeWordAdapter):
    """Adaptateur concret pour Porcupine."""
    
    def __init__(self):
        self.mic_checker = MicrophoneChecker()
        self.porcupine = None
        self.recorder = None
        self.is_active = False
        self.detection_thread: Optional[threading.Thread] = None
        self._on_detect: Optional[Callable] = None
        self._on_audio: Optional[Callable] = None
        logger.info("PorcupineWakeWordAdapter initialisé")
    
    def start(self, device_index: int, on_detect: Callable, on_audio: Callable) -> bool:
        if not self.mic_checker.is_microphone_available():
            logger.error("❌ Aucun microphone détecté.")
            return False
        """Démarre la détection avec Porcupine."""
        try:
            if not self._initialize_porcupine():
                return False
            
            self._on_detect = on_detect
            self._on_audio = on_audio
            self.is_active = True
            
            self._start_detection_loop(device_index)
            logger.info("✅ Détection Porcupine démarrée")
            return True
            
        except Exception as e:
            logger.error(f"Erreur démarrage Porcupine: {e}")
            return False
    
    def stop(self) -> None:
        """Arrête la détection."""
        self.is_active = False
        logger.info("Détection Porcupine arrêtée")
        
        # Nettoyer les ressources
        if self.recorder:
            try:
                self.recorder.stop()
                self.recorder.delete()
            except Exception as e:
                logger.debug(f"Erreur nettoyage recorder: {e}")
        
        if self.porcupine:
            try:
                self.porcupine.delete()
            except Exception as e:
                logger.debug(f"Erreur nettoyage porcupine: {e}")
    
    def get_audio_devices(self) -> list:
        """Retourne la liste des périphériques audio disponibles."""
        try:
            from pvrecorder import PvRecorder
            devices = PvRecorder.get_available_devices()
            return [(i, device) for i, device in enumerate(devices)]
        except Exception as e:
            logger.error(f"Erreur récupération périphériques: {e}")
            return [(0, "Microphone par défaut")]
    
    def _initialize_porcupine(self) -> bool:
        """Initialise le détecteur Porcupine."""
        try:
            from pvporcupine import Porcupine
            from pvrecorder import PvRecorder
            
            # Vérifier les fichiers nécessaires
            model_path = getattr(config, 'PORCUPINE_MODEL_PATH', None)
            keyword_path = getattr(config, 'PORCUPINE_KEYWORD_PATH', None)
            library_path = getattr(config, 'PORCUPINE_LIBRARY_PATH', None)
            access_key = getattr(config, 'PORCUPINE_ACCESS_KEY', '')
            
            # Vérifier que les chemins sont absolus ou les convertir
            if model_path and not os.path.isabs(model_path):
                model_path = os.path.join(config.BASE_DIR, model_path)
            if keyword_path and not os.path.isabs(keyword_path):
                keyword_path = os.path.join(config.BASE_DIR, keyword_path)
            if library_path and not os.path.isabs(library_path):
                library_path = os.path.join(config.BASE_DIR, library_path)
            
            required_files = [f for f in [model_path, keyword_path, library_path] if f]
            
            for file_path in required_files:
                if file_path and not os.path.exists(file_path):
                    logger.warning(f"Fichier Porcupine manquant: {file_path}")
                    return False
            
            if not access_key:
                logger.warning("Clé d'accès Porcupine manquante")
                return False
            
            # Initialiser Porcupine avec les chemins absolus
            self.porcupine = Porcupine(
                access_key=access_key,
                model_path=model_path,
                keyword_paths=[keyword_path],
                library_path=library_path,
                sensitivities=[0.9]  # Sensibilité moyenne
            )
            
            logger.info("✅ Porcupine initialisé avec succès")
            logger.info(f"   Frame length: {self.porcupine.frame_length}")
            logger.info(f"   Sample rate: {self.porcupine.sample_rate}Hz")
            return True
            
        except ImportError as e:
            logger.warning(f"Porcupine non installé: {e}")
            return False
        except Exception as e:
            logger.error(f"Erreur initialisation Porcupine: {e}")
            return False
    
    def _start_detection_loop(self, device_index: int):
        """Démarre la boucle de détection."""
        def detection_loop():
            try:
                from pvrecorder import PvRecorder
                
                # Initialiser le recorder
                self.recorder = PvRecorder(
                    device_index=device_index,
                    frame_length=self.porcupine.frame_length
                )
                self.recorder.start()
                logger.info("🎙️ Détection Porcupine démarrée")
                logger.info(f"   Device: {device_index}")
                logger.info(f"   Frame length: {self.porcupine.frame_length}")
                
                # Buffer pour capturer l'audio après détection
                audio_buffer = []
                capture_audio = False
                capture_frames = 0
                max_capture_frames = 100  # ~3 secondes à 16kHz
                
                while self.is_active:
                    pcm = self.recorder.read()
                    
                    # Détection du mot-clé
                    keyword_index = self.porcupine.process(pcm)
                    
                    if keyword_index >= 0:
                        logger.info("🎯 Mot-clé Porcupine détecté!")
                        if self._on_detect:
                            self._on_detect()
                        
                        # Commencer à capturer l'audio pour la transcription
                        capture_audio = True
                        audio_buffer = list(pcm)  # Commencer avec ce frame
                        capture_frames = 0
                        
                    elif capture_audio:
                        # Continuer à capturer l'audio
                        audio_buffer.extend(pcm)
                        capture_frames += 1
                        
                        # Arrêter la capture après le silence ou timeout
                        if capture_frames >= max_capture_frames:
                            logger.info("🎤 Audio capturé pour transcription (timeout)")
                            if self._on_audio:
                                # Convertir en numpy array
                                audio_data = np.array(audio_buffer, dtype=np.int16)
                                self._on_audio(audio_data)
                            
                            capture_audio = False
                            audio_buffer = []
                            capture_frames = 0
                            
                        # Détecter le silence (simplifié)
                        elif len(audio_buffer) > 16000 and capture_frames > 20:  # Après 0.5s
                            # Vérifier si les derniers frames sont silencieux
                            recent_audio = np.array(audio_buffer[-1600:], dtype=np.int16)
                            energy = np.sqrt(np.mean(recent_audio.astype(np.float32) ** 2))
                            if energy < 100:  # Seuil de silence
                                logger.info("🎤 Audio capturé pour transcription (silence détecté)")
                                if self._on_audio:
                                    audio_data = np.array(audio_buffer, dtype=np.int16)
                                    self._on_audio(audio_data)
                                
                                capture_audio = False
                                audio_buffer = []
                                capture_frames = 0
                                
            except Exception as e:
                logger.error(f"Erreur boucle détection: {e}")
            finally:
                logger.info("⏹️ Boucle détection Porcupine terminée")
        
        self.detection_thread = threading.Thread(target=detection_loop, daemon=True)
        self.detection_thread.start()

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
        logger.info("WakeWordService initialisé avec adaptateur")
    
    @classmethod
    def create_with_porcupine(cls):
        mic_checker = MicrophoneChecker()
        """Factory method pour créer un WakeWordService avec Porcupine."""
        adapter = PorcupineWakeWordAdapter()
        return cls(adapter)
    
    @classmethod
    def create_with_simulation(cls):
        """Factory method pour créer un WakeWordService avec simulation."""
        adapter = SimulatedWakeWordAdapter()
        return cls(adapter)

    @classmethod
    def create_with_vosk(cls, model_path: str):
        """Factory method pour creer un WakeWordService avec Vosk."""
        adapter = VoskWakeWordAdapter(model_path)
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
        if hasattr(self, '_is_started') and self._is_started:
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
            self.wake_word_adapter.stop()  # Nettoyer l'adaptateur actuel
            simulated_adapter = SimulatedWakeWordAdapter()
            self.wake_word_adapter = simulated_adapter
            self.wake_word_adapter.start(device_index, on_detect_wrapper, on_audio_wrapper)

        self._is_started = True
    
    def stop_detection(self):
        """Arrête la détection du mot-clé."""
        self.wake_word_adapter.stop()
    
    def get_audio_devices(self) -> list:
        """Retourne la liste des périphériques audio disponibles."""
        return self.wake_word_adapter.get_audio_devices()
