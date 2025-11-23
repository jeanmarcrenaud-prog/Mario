import threading
import time
from typing import Callable, Optional
import os
import numpy as np
from ..utils.logger import logger
from ..config.config import config

class WakeWordService:
    """Service de détection du mot-clé avec Porcupine."""
    
    def __init__(self):
        self.is_active = False
        self.wake_word_callback: Optional[Callable] = None
        self.audio_callback: Optional[Callable] = None
        self.detection_thread: Optional[threading.Thread] = None
        self.porcupine = None
        self.recorder = None
        logger.info("WakeWordService initialisé")
    
    def set_wake_word_callback(self, callback: Callable):
        """Définit le callback pour la détection du mot-clé."""
        self.wake_word_callback = callback
        logger.debug("Callback wake word défini")
    
    def set_audio_callback(self, callback: Callable):
        """Définit le callback pour l'audio capturé."""
        self.audio_callback = callback
        logger.debug("Callback audio défini")
    
    def initialize_porcupine(self) -> bool:
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
                sensitivities=[0.7]  # Sensibilité moyenne
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
    
    def start_detection(self, device_index: int = 0):
        """Démarre la détection du mot-clé."""
        if self.is_active:
            logger.warning("La détection est déjà active")
            return
        
        self.is_active = True
        logger.info(f"Démarrage détection wake word sur device {device_index}")
        
        # Essayer d'initialiser Porcupine
        if self.initialize_porcupine():
            self._start_porcupine_detection(device_index)
        else:
            logger.info("Utilisation détection simulée")
            self._simulate_detection()
    
    def stop_detection(self):
        """Arrête la détection du mot-clé."""
        self.is_active = False
        logger.info("Détection wake word arrêtée")
        
        # Nettoyer les ressources Porcupine
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
    
    def _start_porcupine_detection(self, device_index: int):
        """Démarre la détection avec Porcupine."""
        try:
            from pvrecorder import PvRecorder
            
            def detection_loop():
                try:
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
                            if self.wake_word_callback:
                                self.wake_word_callback()
                            
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
                                if self.audio_callback:
                                    # Convertir en numpy array
                                    audio_data = np.array(audio_buffer, dtype=np.int16)
                                    self.audio_callback(audio_data)
                                
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
                                    if self.audio_callback:
                                        audio_data = np.array(audio_buffer, dtype=np.int16)
                                        self.audio_callback(audio_data)
                                    
                                    capture_audio = False
                                    audio_buffer = []
                                    capture_frames = 0
                                    
                except Exception as e:
                    logger.error(f"Erreur boucle détection: {e}")
                finally:
                    logger.info("⏹️ Boucle détection Porcupine terminée")
            
            self.detection_thread = threading.Thread(target=detection_loop, daemon=True)
            self.detection_thread.start()
            
        except Exception as e:
            logger.error(f"Erreur démarrage détection Porcupine: {e}")
            logger.info("Retour à la simulation")
            self._simulate_detection()
    
    def _simulate_detection(self):
        """Simule la détection (fallback)."""
        def detection_loop():
            logger.info("🔍 Détection simulée démarrée")
            counter = 0
            while self.is_active:
                time.sleep(2)  # Simulation
                counter += 1
                if counter % 3 == 0:  # Toutes les 6 secondes
                    logger.debug("🔍 Simulation détection mot-clé")
                    if self.wake_word_callback:
                        self.wake_word_callback()
            
            logger.info("⏹️ Détection simulée terminée")
        
        self.detection_thread = threading.Thread(target=detection_loop, daemon=True)
        self.detection_thread.start()
    
    def get_audio_devices(self) -> list:
        """Retourne la liste des périphériques audio disponibles."""
        try:
            from pvrecorder import PvRecorder
            devices = PvRecorder.get_available_devices()  # ✅ Correct method
            return [(i, device) for i, device in enumerate(devices)]
        except Exception as e:
            logger.error(f"Erreur récupération périphériques: {e}")
            return [(0, "Microphone par défaut")]
