import os
from dataclasses import dataclass
import yaml
from ..utils.logger import logger

@dataclass
class ConfigManager:
    # Chemins
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    VOICES_FOLDER: str = os.path.join(BASE_DIR, "voices")
    CONFIG_FILE: str = os.path.join(BASE_DIR, "config.yaml")
    LOG_FOLDER: str = os.path.join(BASE_DIR, "logs")
    VOSK_MODEL_PATH: str = os.path.join(BASE_DIR, "models", "vosk-model-small-fr")
    
    # API Keys
    OPENAI_API_KEY: str = ""

    # Audio settings
    SAMPLE_RATE: int = 16000
    DEFAULT_MICROPHONE_INDEX: int = 0
    
    # Whisper
    DEFAULT_VOICE: str = "fr_FR-siwis-medium"
    DEFAULT_WHISPER_MODEL: str = "large-v3-turbo"
    
    # Ollama
    DEFAULT_MODEL: str = "qwen3-coder"


    # Porcupine
    PORCUPINE_ACCESS_KEY: str = os.getenv("PORCUPINE_ACCESS_KEY", "")
    PORCUPINE_MODEL_PATH: str = os.path.join(PORCUPINE_LIB_PATH, "common", "porcupine_params_fr.pv")
    PORCUPINE_LIBRARY_PATH: str = os.path.join(PORCUPINE_LIB_PATH, "windows", "amd64", "pv_porcupine.dll")
    PORCUPINE_KEYWORD_PATH: str = os.path.join(PORCUPINE_LIB_PATH, "keywords", "windows", "mario_fr_windows_v3_0_0.ppn")
    PORCUPINE_SENSITIVITY: float = 0.9
    
    # Interface
    WEB_PORT: int = 7860
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    def __post_init__(self):
        """Charge la configuration depuis le fichier YAML."""
        self._load_from_file()
        self._create_directories()
        
    def _load_from_file(self):
        """Charge la configuration depuis le fichier."""
        if not os.path.exists(self.CONFIG_FILE):
            logger.warning(f"Fichier de config non trouvé: {self.CONFIG_FILE}")
            return
        
        try:
            with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f) or {}
            
            # Mettre à jour les attributs avec les valeurs du fichier
            for key, value in config_data.items():
                attr_name = key.upper()
                if hasattr(self, attr_name):
                    setattr(self, attr_name, value)
                    
        except Exception as e:
            logger.error(f"Erreur chargement config: {e}")
    
    def _create_directories(self):
        """Crée les répertoires nécessaires."""
        directories = [
            self.VOICES_FOLDER,
            self.LOG_FOLDER,
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)


# Instance globale
config = ConfigManager()
