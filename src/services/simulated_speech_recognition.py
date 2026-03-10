import numpy as np
from typing import List


class SimulatedSpeechRecognitionAdapter:
    """Adaptateur de reconnaissance vocale simulé pour les tests."""
    
    def __init__(self):
        self.is_available = True
    
    def transcribe_array(self, audio_data: np.ndarray, language: str = "fr") -> str:
        """Simule la transcription d'un tableau audio."""
        return "Bonjour, comment puis-je vous aider ?"
    
    def transcribe_file(self, file_path: str, language: str = "fr") -> str:
        """Simule la transcription d'un fichier audio."""
        return "Bonjour, comment puis-je vous aider ?"
    
    def unload_model(self) -> bool:
        """Décharge le modèle (simulation)."""
        return True
    
    def get_available_models(self) -> List[str]:
        """Retourne les modèles disponibles (simulation)."""
        return ["base", "small", "medium"]
    
    def optimize_cache(self) -> bool:
        """Optimise le cache (simulation)."""
        return True
    
    def test_transcription(self) -> bool:
        """Teste la transcription."""
        try:
            test_audio = np.zeros(16000, dtype=np.int16)
            result = self.transcribe_array(test_audio)
            return isinstance(result, str) and len(result) > 0
        except Exception:
            return False
