import os
from dataclasses import dataclass
from typing import Optional
import logging

@dataclass
class Config:
    # Chemins
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    VOICES_FOLDER: str = os.path.join(BASE_DIR, "voices")
    CONVERSATION_HISTORY_FOLDER: str = os.path.join(BASE_DIR, "conversations")
    LOG_FOLDER: str = os.path.join(BASE_DIR, "logs")
    PORCUPINE_LIB_PATH: str = os.path.join(BASE_DIR, "porcupine_libs")
    
    # Fichiers de configuration
    VAD_THRESHOLD_FILE: str = os.path.join(BASE_DIR, "vad_threshold.json")
    
    # Modèles
    # Chemins pour les fichiers Piper
    PIPER_VOICE_ONNX: str = os.path.join(VOICES_FOLDER, "fr_FR-siwis-medium", "fr_FR-siwis-medium.onnx")
    PIPER_VOICE_JSON: str = os.path.join(VOICES_FOLDER, "fr_FR-siwis-medium", "fr_FR-siwis-medium.onnx.json")
    WHISPER_MODEL_NAME: str = "large"
    WAKE_WORD_MODEL: str = "small"
    DEFAULT_PIPER_VOICE: str = "fr_FR-siwis-medium"
    
    # Porcupine
    PORCUPINE_ACCESS_KEY: str = os.getenv("PORCUPINE_ACCESS_KEY", "")
    PORCUPINE_MODEL_PATH: str = os.path.join(PORCUPINE_LIB_PATH, "porcupine_params_fr.pv")
    PORCUPINE_LIBRARY_PATH: str = os.path.join(PORCUPINE_LIB_PATH, "pv_porcupine.dll")
    PORCUPINE_KEYWORD_PATH: str = os.path.join(PORCUPINE_LIB_PATH, "mario_fr_windows_v3_0_0.ppn")
    PORCUPINE_SENSITIVITY: float = 0.9
    
    # Audio
    SAMPLERATE: int = 22050
    VAD_AGGRESSIVENESS: int = 3
    FRAME_DURATION_MS: int = 30
    VAD_CALIBRATION_TIME: int = 5
    VAD_THRESHOLD_MULTIPLIER: float = 1.2
    
    # Performance
    MAX_THREADS: int = 4
    OLLAMA_TIMEOUT: int = 600
    MAX_RETRIES: int = 3
    BATCH_SIZE: int = 4
    
    # Interface
    INTERFACE_PORT: int = 7860
    MAX_DEBUG_LINES: int = 1000
    
    # Logging
    LOG_LEVEL: int = logging.INFO
    
    def __post_init__(self):
        # Création des dossiers nécessaires
        for folder in [self.VOICES_FOLDER, self.CONVERSATION_HISTORY_FOLDER, 
                      self.LOG_FOLDER, self.PORCUPINE_LIB_PATH]:
            os.makedirs(folder, exist_ok=True)
        
        # Vérification des fichiers nécessaires
        self._validate_config()
    
    def _validate_config(self):
        """Valide la configuration"""
        if not self.PORCUPINE_ACCESS_KEY:
            logging.warning("PORCUPINE_ACCESS_KEY non configuré")
        
        # Vérifier que les fichiers existent
        required_files = [
            self.PORCUPINE_MODEL_PATH,
            self.PORCUPINE_LIBRARY_PATH,
            self.PORCUPINE_KEYWORD_PATH,
            self.PIPER_VOICE_ONNX,
            self.PIPER_VOICE_JSON
        ]
        
        for file_path in required_files:
            if not os.path.exists(file_path):
                logging.warning(f"Fichier requis manquant : {file_path}")

config = Config()
