import logging
import threading
from typing import List, Dict, Optional
import gradio as gr
from ..config import config
from ..core.llm_client import LLMClient
from ..core.text_to_speech import TextToSpeech
from ..core.speech_recognition import SpeechRecognizer
from ..core.wake_word_detector import WakeWordDetector
from ..utils.audio_player import AudioPlayer
from ..utils.logger import logger
from pathlib import Path
import re

class InterfaceHelpers:
    """Classe helper pour les opérations communes de l'interface."""
    def __init__(self):
        pass

    def format_file_size(self, size: int) -> str:
        """Formate la taille d'un fichier en une chaîne lisible."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    def truncate_text(self, text: str, max_length: int) -> str:
        """Tronque un texte à une longueur donnée."""
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."

    def sanitize_filename(self, filename: str) -> str:
        """Nettoie un nom de fichier pour enlever les caractères non autorisés."""
        sanitized = re.sub(r'[\\/*?:"<>|]', "_", filename)
        return sanitized
        
    def get_theme(self):
        """Retourne le thème Gradio."""
        return gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="cyan",
            neutral_hue="gray",
        ).set(
            button_primary_background_fill="*primary_500",
            button_primary_background_fill_hover="*primary_400",
            block_title_text_weight="600",
        )

    def get_microphones(self) -> List[str]:
        """Retourne la liste des microphones disponibles."""
        try:
            from pvrecorder import PvRecorder
            devices = PvRecorder.get_available_devices()
            return [f"{i}: {name}" for i, name in enumerate(devices)]
        except Exception as e:
            logger.error(f"Erreur détection microphones: {e}")
            return ["0: Microphone par défaut"]

    def get_default_microphone(self) -> str:
        """Retourne le microphone par défaut."""
        mics = self.get_microphones()
        return mics[0] if mics else "0: Microphone par défaut"

    def get_piper_voices(self) -> List[str]:
        """Retourne la liste des voix Piper disponibles."""
        import os
        voices = []
        if os.path.exists(config.VOICES_FOLDER):
            for d in os.listdir(config.VOICES_FOLDER):
                sub = os.path.join(config.VOICES_FOLDER, d)
                if os.path.isdir(sub) and any(f.endswith(".onnx") for f in os.listdir(sub)):
                    voices.append(d)
        return voices or [config.DEFAULT_PIPER_VOICE]

    def get_ollama_models(self) -> List[str]:
        """Retourne la liste des modèles Ollama disponibles."""
        try:
            import subprocess
            result = subprocess.run(
                ["ollama", "list"], capture_output=True, text=True, timeout=10
            )
            lines = result.stdout.strip().splitlines()[1:]
            return [line.split()[0] for line in lines if line.strip()]
        except Exception as e:
            logger.error(f"Erreur détection modèles Ollama: {e}")
            return []

    def get_default_ollama_model(self) -> Optional[str]:
        """Retourne le modèle Ollama par défaut."""
        models = self.get_ollama_models()
        return models[0] if models else None

    def transcribe_audio(self, speech_recognizer: SpeechRecognizer, audio_data) -> str:
        """Transcrit l'audio en texte."""
        try:
            result = speech_recognizer.transcribe(audio_data, "fr")
            if isinstance(result, dict):
                text = result.get("text", "").strip()
            else:
                text = str(result).strip()
            return text if text else ""
        except Exception as e:
            logger.error(f"Erreur transcription: {e}")
            return ""

    def generate_llm_response(self, llm_client: LLMClient, model: str, messages: List[Dict]) -> str:
        """Génère une réponse LLM."""
        try:
            llm_client.set_model(model)
            response = ""
            for token in llm_client.chat_stream(messages):
                response += token
            return response
        except Exception as e:
            logger.error(f"Erreur génération LLM: {e}")
            return f"[ERREUR] Impossible de générer une réponse: {str(e)}"

    def play_tts_response(self, tts: TextToSpeech, voice: str, text: str, speed: float, audio_player: AudioPlayer):
        """Joue une réponse TTS."""
        try:
            tts.load_voice(voice)
            audio_data = tts.synthesize(text, speed)
            if audio_data is not None:
                audio_player.play_audio(audio_data)
        except Exception as e:
            logger.error(f"Erreur TTS: {e}")

    def is_analysis_command(self, text: str) -> bool:
        """Détecte si le texte est une commande d'analyse."""
        text_lower = text.lower()
        return "analyse" in text_lower and ("fichiers" in text_lower or "arborescence" in text_lower)

    def extract_path_from_command(self, text: str) -> Optional[Path]:
        """Extrait un chemin d'une commande vocale."""
        patterns = [
            r"dans\s+(.+)",
            r"du\s+(.+)", 
            r"sur\s+(.+)",
            r"chemin\s+(.+)",
            r"répertoire\s+(.+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                path = match.group(1).strip()
                path = re.sub(r'[.,;!?]$', '', path)
                path_obj = Path(path)
                if path_obj.exists():
                    return path_obj
        return None

    def auto_start_listening(self, interface, mic_label, whisper_model, piper_voice, ollama_model, speed):
        """Démarrage automatique de l'écoute."""
        try:
            interface.default_mic_index = (
                int(mic_label.split(":")[0]) if ":" in mic_label else int(mic_label)
            )
            
            interface.tts.load_voice(piper_voice)
            interface.llm_client.set_model(ollama_model)
            interface.current_ollama_model = ollama_model
            interface.current_piper_voice = piper_voice
            interface.current_speed = speed
            
            interface._setup_audio_callbacks()
            interface._start_listening_internal(interface.default_mic_index)
            interface.is_running = True
            
            return "[MICRO] Écoute active - Dites 'Mario' pour activer l'assistant"
        except Exception as e:
            logger.error(f"Erreur démarrage automatique: {e}")
            return f"[ERREUR] Erreur: {str(e)}"

    def start_listening_internal(self, wake_detector: WakeWordDetector, mic_index: int):
        """Démarrage interne de l'écoute."""
        wake_detector.start_listening(mic_index)

    def stop_listening(self, wake_detector: WakeWordDetector) -> str:
        """Arrêt de l'écoute."""
        wake_detector.stop_listening()
        return "Écoute arrêtée"

    def restart_listening(self, interface, mic_label, whisper_model, piper_voice, ollama_model, speed):
        """Redémarrage de l'écoute."""
        try:
            interface._stop_listening()
            mic_index = int(mic_label.split(":")[0]) if ":" in mic_label else int(mic_label)
            
            interface.tts.load_voice(piper_voice)
            interface.llm_client.set_model(ollama_model)
            interface.current_ollama_model = ollama_model
            interface.current_piper_voice = piper_voice
            interface.current_speed = speed
            
            interface._setup_audio_callbacks()
            interface._start_listening_internal(mic_index)
            interface.is_running = True
            
            return "[MICRO] Écoute redémarrée"
        except Exception as e:
            logger.error(f"Erreur redémarrage: {e}")
            return f"[ERREUR] Erreur: {str(e)}"
