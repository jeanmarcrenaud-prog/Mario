import numpy as np
import wave
import subprocess
import os
import tempfile
import uuid
import torch
import time
from typing import Optional, Dict, Any
from ..config import config
from ..utils.logger import logger

class TextToSpeech:
    def __init__(self, default_voice: Optional[str] = None):
        self.use_python_lib = True
        self.current_voice: Optional[Dict[str, Any]] = None
        self.audio_cache: Dict[str, np.ndarray] = {}
        self.max_cache_size = 100

        # Tentative d'import de la bibliothèque Piper
        try:
            from piper import PiperVoice
            self.PiperVoice = PiperVoice
            logger.info("[OK] Bibliothèque Piper Python disponible")
        except ImportError:
            logger.warning("[ATTENTION] Piper Python library non disponible, fallback sur CLI")
            self.use_python_lib = False

        # Charge la voix par défaut si spécifiée
        if default_voice:
            self.load_voice(default_voice)

    def load_voice(self, voice_name: str) -> bool:
        """Charge une voix Piper avec vérification."""
        if self.current_voice and self.current_voice.get("voice_name") == voice_name:
            logger.debug("Voix '%s' déjà chargée", voice_name)
            return True

        model_path = os.path.join(config.VOICES_FOLDER, voice_name, f"{voice_name}.onnx")
        config_path = os.path.join(config.VOICES_FOLDER, voice_name, f"{voice_name}.onnx.json")
        
        if not os.path.exists(model_path):
            logger.error("[ERREUR] Modèle voix non trouvé: %s", model_path)
            return False

        start_time = time.time()
        
        if self.use_python_lib:
            try:
                use_cuda = torch.cuda.is_available()
                voice_obj = self.PiperVoice.load(
                    model_path, 
                    config_path=config_path,
                    use_cuda=use_cuda
                )
                
                self.current_voice = {
                    "type": "py",
                    "voice": voice_obj,
                    "model_path": model_path,
                    "config_path": config_path,
                    "voice_name": voice_name,
                    "sample_rate": getattr(voice_obj.config, 'sample_rate', 22050)
                }
                
                load_time = time.time() - start_time
                logger.info("[OK] Voix '%s' chargée en %.2fs (CUDA: %s)", voice_name, load_time, use_cuda)
                return True
                
            except Exception as e:
                logger.error("[ERREUR] Erreur chargement voix Python: %s", e)
                self.use_python_lib = False

        # Fallback sur CLI
        self.current_voice = {
            "type": "cli",
            "model_path": model_path,
            "voice_name": voice_name,
            "sample_rate": 22050
        }
        logger.info("[OUTIL] Voix '%s' prête pour CLI", voice_name)
        return True

    def synthesize(self, text: str, speed: float = 1.0, cache_key: Optional[str] = None) -> Optional[np.ndarray]:
        """Synthétise un texte en audio avec cache."""
        if not self.current_voice or not text.strip():
            return None

        if cache_key and cache_key in self.audio_cache:
            logger.debug("[CACHE] Audio récupéré du cache: %s", cache_key)
            return self.audio_cache[cache_key]

        start_time = time.time()
        
        try:
            if self.current_voice["type"] == "py" and self.use_python_lib:
                audio_data = self._synthesize_python_simple(text)
            else:
                audio_data = self._synthesize_cli(text, speed)
            
            if audio_data is not None:
                # Ajuster la vitesse si nécessaire
                if speed != 1.0:
                    audio_data = self._adjust_speed(audio_data, speed, 22050)
                
                synthesis_time = time.time() - start_time
                logger.info("[AUDIO] Synthèse audio en %.2fs - %d caractères", synthesis_time, len(text))
                
                if cache_key and len(self.audio_cache) < self.max_cache_size:
                    self.audio_cache[cache_key] = audio_data
                
                return audio_data
            else:
                return None
                
        except Exception as e:
            logger.error("[ERREUR] Erreur de synthèse: %s", e)
            return None

    def _synthesize_python_simple(self, text: str) -> Optional[np.ndarray]:
        """
        Méthode simple et fiable utilisant un fichier temporaire.
        Cette approche évite les problèmes avec les générateurs et AudioChunk.
        """
        try:
            voice_obj = self.current_voice["voice"]
            temp_wav_path = os.path.join(tempfile.gettempdir(), f"piper_temp_{uuid.uuid4()}.wav")
            
            logger.debug("[AUDIO] Synthèse via fichier temporaire: %s", temp_wav_path)
            
            # Utiliser la méthode fichier - toujours fiable
            with wave.open(temp_wav_path, "wb") as wav_file:
                # Définir les paramètres audio
                sample_rate = getattr(voice_obj.config, 'sample_rate', 22050)
                wav_file.setnchannels(1)    # Mono
                wav_file.setsampwidth(2)    # 16-bit
                wav_file.setframerate(sample_rate)
                
                # Synthétiser directement dans le fichier
                voice_obj.synthesize(text, wav_file)
            
            # Lire le fichier généré
            with wave.open(temp_wav_path, "rb") as wav_file:
                frames = wav_file.readframes(wav_file.getnframes())
                audio_data = np.frombuffer(frames, dtype=np.int16)
                
                # Conversion mono si stéréo (normalement déjà mono)
                if wav_file.getnchannels() == 2:
                    audio_data = audio_data.reshape(-1, 2).mean(axis=1).astype(np.int16)
                    logger.debug("[AUDIO] Conversion stéréo -> mono effectuée")
            
            # Nettoyer le fichier temporaire
            os.unlink(temp_wav_path)
            logger.debug("[AUDIO] Fichier temporaire nettoyé")
            
            return audio_data
            
        except Exception as e:
            logger.error("[ERREUR] Synthèse Python simple échouée: %s", e)
            # Fallback vers CLI
            return self._synthesize_cli(text, 1.0)

    def _synthesize_cli(self, text: str, speed: float) -> Optional[np.ndarray]:
        """Synthèse avec la CLI Piper - méthode alternative."""
        temp_wav_path = os.path.join(tempfile.gettempdir(), f"piper_temp_{uuid.uuid4()}.wav")
        
        try:
            cmd = [
                "piper", 
                "--model", self.current_voice["model_path"],
                "--output_file", temp_wav_path,
            ]
            
            # Ajouter le paramètre de vitesse seulement si différent de 1.0
            if speed != 1.0:
                cmd.extend(["--length_scale", str(1.0 / speed)])
            
            logger.debug("[CLI] Commande Piper: %s", " ".join(cmd))
            
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=text, timeout=30)
            
            if process.returncode != 0:
                logger.error("[ERREUR] Erreur CLI Piper: %s", stderr)
                return None
            
            # Vérifier que le fichier a été créé
            if not os.path.exists(temp_wav_path):
                logger.error("[ERREUR] Fichier de sortie non créé: %s", temp_wav_path)
                return None
            
            # Lire le fichier WAV généré
            with wave.open(temp_wav_path, "rb") as wav_file:
                frames = wav_file.readframes(wav_file.getnframes())
                audio_data = np.frombuffer(frames, dtype=np.int16)
                
                # Conversion mono si stéréo
                if wav_file.getnchannels() == 2:
                    audio_data = audio_data.reshape(-1, 2).mean(axis=1).astype(np.int16)
                
                logger.debug("[CLI] Audio généré: %d échantillons, %d Hz", 
                           len(audio_data), wav_file.getframerate())
                
                return audio_data
                
        except subprocess.TimeoutExpired:
            logger.error("[TIMEOUT] Timeout CLI Piper")
            return None
        except FileNotFoundError:
            logger.error("[ERREUR] Commande Piper non trouvée")
            return None
        except Exception as e:
            logger.error("[ERREUR] Erreur synthèse CLI: %s", e)
            return None
        finally:
            # Nettoyer le fichier temporaire
            if os.path.exists(temp_wav_path):
                try:
                    os.unlink(temp_wav_path)
                except Exception as e:
                    logger.warning("[ATTENTION] Impossible de supprimer le fichier temporaire: %s", e)

    def _adjust_speed(self, audio_data: np.ndarray, speed: float, sample_rate: int) -> np.ndarray:
        """Ajuste la vitesse de l'audio manuellement (optionnel)."""
        if speed == 1.0:
            return audio_data  # Pas d'ajustement nécessaire
            
        try:
            import librosa
            
            # Convertir en float pour le traitement
            audio_float = audio_data.astype(np.float32) / 32768.0
            
            # Ajuster la vitesse avec librosa
            adjusted_audio = librosa.effects.time_stretch(audio_float, rate=speed)
            
            # Reconvertir en int16
            adjusted_audio = (adjusted_audio * 32768.0).astype(np.int16)
            
            logger.debug("[AUDIO] Vitesse ajustée: %.2fx", speed)
            return adjusted_audio
            
        except ImportError:
            logger.warning("[ATTENTION] Librosa non disponible, vitesse non ajustée")
            return audio_data
        except Exception as e:
            logger.warning("[ATTENTION] Erreur ajustement vitesse: %s", e)
            return audio_data

    def say(self, text: str, speed: float = 1.0):
        """Méthode utilitaire pour synthétiser et jouer l'audio."""
        audio_data = self.synthesize(text, speed)
        if audio_data is not None:
            try:
                import pyaudio
            except ImportError:
                logger.error("[ERREUR] pyaudio non installé. Installez-le avec `pip install pyaudio`.")
                return False            
            # Lecture audio avec pyaudio
            p = pyaudio.PyAudio()
            stream = p.open(format=pyaudio.paInt16,
                            channels=1,
                            rate=self.current_voice.get("sample_rate", 22050),
                            output=True)
            stream.write(audio_data.astype(np.int16).tobytes())
            # Bip court de fin
            self._play_end_beep(p)
            stream.stop_stream()
            stream.close()
            p.terminate()
            # Ici vous ajouterez la lecture audio (pyaudio, etc.)
            logger.info("[AUDIO] Texte synthétisé: '%s'", text[:50] + "..." if len(text) > 50 else text)
            return True
        else:
            logger.error("[ERREUR] Impossible de synthétiser le texte")
            return False

    def get_voice_info(self) -> Dict[str, Any]:
        """Retourne les informations sur la voix actuelle."""
        if not self.current_voice:
            return {}
        
        return {
            "name": self.current_voice.get("voice_name"),
            "type": self.current_voice.get("type"),
            "sample_rate": self.current_voice.get("sample_rate", 22050),
            "using_python_lib": self.use_python_lib
        }

    def test_synthesis(self, text: str = "Bonjour, ceci est un test.") -> bool:
        """Teste la synthèse vocale."""
        logger.info("[TEST] Test de synthèse vocale...")
        audio_data = self.synthesize(text)
        
        if audio_data is not None:
            logger.info("[TEST] ✅ Synthèse vocale fonctionnelle (%d échantillons)", len(audio_data))
            return True
        else:
            logger.error("[TEST] ❌ Synthèse vocale échouée")
            return False

    def cleanup(self):
        """Nettoie les ressources."""
        self.audio_cache.clear()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("[NETTOYAGE] Cache TTS nettoyé")

# Exemple d'utilisation
if __name__ == "__main__":
    # Test simple de la classe
    tts = TextToSpeech("fr_FR-siwis-medium")
    if tts.test_synthesis():
        print("✅ Text-to-Speech fonctionne correctement!")
    else:
        print("❌ Text-to-Speech a échoué")
