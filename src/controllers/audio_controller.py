"""
Contrôleur pour la gestion audio selon le modèle MVC
"""

from ..models.audio_device_manager import AudioDeviceManager
from typing import Dict, List
from ..utils.logger import logger

class AudioController:
    """Contrôleur pour les opérations audio"""
    
    def __init__(self):
        self.audio_model = AudioDeviceManager()
        self.logger = logger
        
    def get_audio_devices(self) -> Dict[str, List[str]]:
        """Retourne les périphériques audio filtrés."""
        return self.audio_model.get_filtered_audio_devices()
    
    def get_microphones(self) -> List[str]:
        """Retourne la liste des microphones."""
        devices = self.get_audio_devices()
        return devices.get("inputs", [])
    
    def get_speakers(self) -> List[str]:
        """Retourne la liste des haut-parleurs."""
        devices = self.get_audio_devices()
        return devices.get("outputs", [])
    
    def get_default_microphone(self) -> str:
        """Retourne le microphone par défaut."""
        mics = self.get_microphones()
        # S'assurer que la valeur existe dans la liste
        default_candidates = ["0: Microphone (Realtek(R) Audio)", "0: Microphone par défaut"]
        
        for candidate in default_candidates:
            if candidate in mics:
                return candidate
        
        return mics[0] if mics else "0: Microphone par défaut"
    
    def get_default_speaker(self) -> str:
        """Retourne le haut-parleur par défaut."""
        speakers = self.get_speakers()
        # S'assurer que la valeur existe dans la liste
        default_candidates = [
            "3: Haut-parleurs (Realtek(R) Audio)", 
            "0: Haut-parleurs par défaut",
            "0: Speakers"
        ]
        
        for candidate in default_candidates:
            if candidate in speakers:
                return candidate
        
        return speakers[0] if speakers else "0: Haut-parleurs par défaut"
    
    def debug_devices(self):
        """Lance le débogage des périphériques."""
        self.audio_model.debug_audio_devices()
