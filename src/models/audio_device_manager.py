"""
Gestionnaire des périphériques audio selon le modèle MVC
"""

import logging
from typing import List, Dict, Tuple
from ..utils.logger import logger

class AudioDeviceManager:
    """Modèle pour la gestion des périphériques audio"""
    
    def __init__(self):
        self.logger = logger
            
    def get_filtered_audio_devices(self) -> Dict[str, List[str]]:
        """
        Version simplifiée - utilise ce qui est détecté
        """
        try:
            # Microphones avec PvRecorder
            from pvrecorder import PvRecorder
            mic_devices = [f"{i}: {name}" for i, name in enumerate(PvRecorder.get_available_devices())]
            
            # Sorties avec PyAudio (filtrage léger)
            import pyaudio
            p = pyaudio.PyAudio()
            speaker_devices = []
            
            for i in range(p.get_device_count()):
                device_info = p.get_device_info_by_index(i)
                if device_info['maxOutputChannels'] > 0:
                    name = device_info['name']
                    # Filtrage très léger
                    name_lower = name.lower()
                    if not any(virtual in name_lower for virtual in ['voicemod', 'virtual audio']):
                        speaker_devices.append(f"{i}: {name}")
            
            p.terminate()
            
            return {
                "inputs": mic_devices[:4],  # Maximum 4 micros
                "outputs": speaker_devices[:4]  # Maximum 4 sorties
            }
            
        except Exception as e:
            self.logger.error(f"Erreur détection audio simplifiée: {e}")
            return {
                "inputs": ["0: Microphone (Realtek(R) Audio)", "1: Microphone secondaire"],
                "outputs": ["3: Haut-parleurs (Realtek(R) Audio)", "1: Casque audio"]
            }

    def _get_pvrecorder_microphones(self) -> List[str]:
        """Récupère les microphones avec PvRecorder (plus fiable)."""
        try:
            from pvrecorder import PvRecorder
            devices = PvRecorder.get_available_devices()
            
            # PvRecorder est déjà fiable, on prend tous les micros détectés
            return [f"{i}: {name}" for i, name in enumerate(devices)]
            
        except Exception as e:
            self.logger.error(f"Erreur PvRecorder: {e}")
            # Fallback vers PyAudio
            raw_inputs, _ = self._get_raw_audio_devices()
            return self._filter_input_devices(raw_inputs)

    def _get_raw_audio_devices(self) -> Tuple[List[Tuple[int, str]], List[Tuple[int, str]]]:
        """Récupère tous les périphériques audio bruts."""
        try:
            import pyaudio
            p = pyaudio.PyAudio()
            
            inputs = []
            outputs = []
            
            for i in range(p.get_device_count()):
                device_info = p.get_device_info_by_index(i)
                name = device_info['name'].strip()
                
                if device_info['maxInputChannels'] > 0:
                    inputs.append((i, name))
                if device_info['maxOutputChannels'] > 0:
                    outputs.append((i, name))
            
            p.terminate()
            return inputs, outputs
            
        except Exception as e:
            self.logger.error(f"Erreur récupération périphériques bruts: {e}")
            return [], []

    def _filter_input_devices(self, devices: List[Tuple[int, str]]) -> List[str]:
        """Filtre les périphériques d'entrée."""
        filtered = []
        seen_names = set()
        
        for idx, name in devices:
            name_lower = name.lower()
            
            # Exclusion des périphériques virtuels et systèmes
            if self._is_virtual_device(name_lower):
                continue
                
            # Inclusion seulement des microphysiques
            if self._is_physical_input_device(name_lower):
                # Éviter les doublons basés sur le nom normalisé
                normalized_name = self._normalize_device_name(name)
                if normalized_name not in seen_names:
                    seen_names.add(normalized_name)
                    filtered.append(f"{idx}: {name}")
        
        return filtered

    def _filter_output_devices(self, devices: List[Tuple[int, str]]) -> List[str]:
        """Filtre les périphériques de sortie."""
        filtered = []
        seen_names = set()
        
        for idx, name in devices:
            name_lower = name.lower()
            
            # Exclusion des périphériques virtuels et systèmes
            if self._is_virtual_device(name_lower):
                continue
                
            # Inclusion seulement des sorties physiques
            if self._is_physical_output_device(name_lower):
                # Éviter les doublons basés sur le nom normalisé
                normalized_name = self._normalize_device_name(name)
                if normalized_name not in seen_names:
                    seen_names.add(normalized_name)
                    filtered.append(f"{idx}: {name}")
        
        return filtered

    def _is_virtual_device(self, name_lower: str) -> bool:
        """Détermine si un périphérique est virtuel."""
        virtual_keywords = [
            'mappeur de sons', 'pilote de capture', 'périphérique audio principal',
            'voicemod', 'virtual audio', 'cable', 'loopback', 'stereo mix', 'mixage stéréo'
        ]
        # Rendre l'exclusion moins agressive
        return any(keyword in name_lower for keyword in virtual_keywords)

    def _is_physical_input_device(self, name_lower: str) -> bool:
        """Détermine si c'est un périphérique d'entrée physique."""
        input_keywords = [
            'microphone', 'mic', 'realtek', 'nvidia', 'hd audio', 'headset',
            'line in', 'input'  # Ajouter des termes plus généraux
        ]
        return any(keyword in name_lower for keyword in input_keywords)

    def _is_physical_output_device(self, name_lower: str) -> bool:
        """Détermine si c'est un périphérique de sortie physique."""
        output_keywords = [
            'haut-parleurs', 'speakers', 'headphones', 'casque', 'realtek', 
            'nvidia', 'hd audio', 'hdmi', 'displayport', 'line out', 'output',
            'primary', 'second', 'analog', 'digital'  # Ajouter des termes plus généraux
        ]
        return any(keyword in name_lower for keyword in output_keywords)

    def _normalize_device_name(self, name: str) -> str:
        """Normalise le nom du périphérique pour éviter les doublons."""
        # Supprimer les variations de parenthèses et espaces
        import re
        normalized = re.sub(r'\([^)]*\)', '', name)  # Supprimer les parenthèses
        normalized = re.sub(r'\s+', ' ', normalized)  # Espaces multiples -> simple
        normalized = normalized.strip().lower()
        return normalized

    def _limit_devices(self, devices: List[str], max_count: int) -> List[str]:
        """Limite le nombre de périphériques affichés."""
        if len(devices) <= max_count:
            return devices
        
        # Prioriser les périphériques avec les index les plus bas (plus probables d'être physiques)
        return sorted(devices, key=lambda x: int(x.split(':')[0]))[:max_count]

    def _get_fallback_devices(self) -> Dict[str, List[str]]:
        """Périphériques de fallback en cas d'erreur."""
        return {
            "inputs": ["0: Microphone par défaut", "1: Microphone secondaire"],
            "outputs": ["0: Haut-parleurs par défaut", "1: Casque audio"]
        }

    def debug_audio_devices(self):
        """Méthode de débogage pour voir tous les périphériques."""
        try:
            import pyaudio
            p = pyaudio.PyAudio()
            
            self.logger.info("=== DÉBOGAGE PÉRIPHÉRIQUES AUDIO ===")
            for i in range(p.get_device_count()):
                device_info = p.get_device_info_by_index(i)
                self.logger.info(f"{i}: {device_info['name']} (In: {device_info['maxInputChannels']}, Out: {device_info['maxOutputChannels']})")
            
            p.terminate()
            
        except Exception as e:
            self.logger.error(f"Erreur débogage audio: {e}")
