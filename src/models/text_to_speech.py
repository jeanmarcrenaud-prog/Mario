import numpy as np
import wave
import subprocess
import os
import tempfile
import uuid
import torch
import time
import re
from typing import Optional, Dict, Any
from ..config import config
from ..utils.logger import logger

def nettoyer_markdown(text):
    # Supprime le gras markdown : **mot** et __mot__
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)   # bold **
    text = re.sub(r'__(.*?)__', r'\1', text)       # bold __
    # Optionnel : italique
    text = re.sub(r'\*(.*?)\*', r'\1', text)       # italic *
    text = re.sub(r'_(.*?)_', r'\1', text)         # italic _
    return text


class TextToSpeech:

    def __init__(self, default_voice: Optional[str] = None):
        self.use_python_lib = True
        self.current_voice: Optional[Dict[str, Any]] = None
        self.audio_cache: Dict[str, np.ndarray] = {}
        self.max_cache_size = 100

        # Tentative d'import de la bibliothèque Piper
        try:
            import piper
            self.PiperVoice = piper.PiperVoice
            self.piper_module = piper
            logger.info("[OK] Bibliothèque Piper Python disponible")
        except ImportError:
            logger.warning("[ATTENTION] Piper Python library non disponible, fallback sur CLI")
            self.use_python_lib = False
            self.PiperVoice = None
            self.piper_module = None

        # Charge la voix par défaut si spécifiée
        if default_voice:
            self.load_voice(default_voice)

    def load_voice(self, voice_name: str) -> bool:
        """Charge une voix Piper avec vérification."""
        logger.info(f"Tentative de chargement de la voix: {voice_name}")
        
        if self.current_voice and self.current_voice.get("voice_name") == voice_name:
            logger.debug("Voix '%s' déjà chargée", voice_name)
            return True

        model_path = os.path.join(config.VOICES_FOLDER, voice_name, f"{voice_name}.onnx")
        config_path = os.path.join(config.VOICES_FOLDER, voice_name, f"{voice_name}.onnx.json")
        
        logger.info(f"Recherche du modèle dans: {model_path}")
        
        if not os.path.exists(model_path):
            logger.error("[ERREUR] Modèle voix non trouvé: %s", model_path)
            return False

        start_time = time.time()
        
        if self.use_python_lib and self.PiperVoice:
            try:
                use_cuda = torch.cuda.is_available()
                logger.info(f"Chargement avec PiperVoice (CUDA: {use_cuda})")
                
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
        logger.info("Utilisation du fallback CLI")
        self.current_voice = {
            "type": "cli",
            "model_path": model_path,
            "voice_name": voice_name,
            "sample_rate": 22050
        }
        
        try:
            import json
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                if 'audio' in config_data and 'sample_rate' in config_data['audio']:
                    self.current_voice["sample_rate"] = config_data['audio']['sample_rate']
        except Exception as e:
            logger.warning("Impossible de lire le sample_rate depuis le JSON: %s", e)
        
        logger.info("[OUTIL] Voix '%s' prête pour CLI (sample_rate: %d)", 
                   voice_name, self.current_voice["sample_rate"])
        return True

    def synthesize(self, text: str, speed: float = 1.0, cache_key: Optional[str] = None) -> Optional[np.ndarray]:
        """Synthétise un texte en audio avec cache."""
        logger.info(f"Synthétisation du texte: {text}")
        text = nettoyer_markdown(text)
        logger.info(f"Synthétisation: '{text}'")
        
        if not self.current_voice:
            logger.error("❌ Aucune voix chargée - appel à load_voice() manquant?")
            if hasattr(config, 'DEFAULT_PIPER_VOICE'):
                logger.info("Tentative de rechargement de la voix par défaut")
                if not self.load_voice(config.DEFAULT_PIPER_VOICE):
                    logger.error("Échec du rechargement de la voix par défaut")
                    return None
            else:
                return None
        
        if not text.strip():
            logger.warning("Texte vide fourni à la synthèse")
            return None

        if cache_key and cache_key in self.audio_cache:
            logger.debug("[CACHE] Audio récupéré du cache: %s", cache_key)
            return self.audio_cache[cache_key]

        start_time = time.time()
        
        try:
            if self.current_voice["type"] == "py" and self.use_python_lib:
                audio_data = self._synthesize_python_simple(text)
                logger.info("[AUDIO] Méthode _synthesize_python_simple")
            else:
                audio_data = self._synthesize_cli(text, speed)
            
            if audio_data is not None:
                if speed != 1.0:
                    audio_data = self._adjust_speed(audio_data, speed, self.current_voice.get("sample_rate", 22050))
                
                synthesis_time = time.time() - start_time
                logger.info("[AUDIO] Synthèse audio en %.2fs - %d caractères", synthesis_time, len(text))
                
                if cache_key and len(self.audio_cache) < self.max_cache_size:
                    self.audio_cache[cache_key] = audio_data
                
                return audio_data
            else:
                logger.error("Échec de la synthèse audio")
                return None
                
        except Exception as e:
            logger.error("[ERREUR] Erreur de synthèse: %s", e)
            return None

    def _play_end_beep(self, p):
        """Joue un bip de fin avec le bon sample rate."""
        try:
            import pyaudio
            sample_rate = self.current_voice.get("sample_rate", 22050)
            
            stream = p.open(format=pyaudio.paInt16, 
                           channels=1, 
                           rate=int(sample_rate),  # Utiliser le même sample rate
                           output=True)
            
            # Générer un bip simple adapté au sample rate
            duration = 0.1  # 100ms
            t = np.linspace(0, duration, int(sample_rate * duration))
            beep = np.sin(2 * np.pi * 440 * t)  # La 440Hz
            beep_int16 = (beep * 32767).astype(np.int16)
            
            stream.write(beep_int16.tobytes())
            stream.stop_stream()
            stream.close()
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du bip de fin: {e}")

    def debug_audio_playback(self, audio_data: np.ndarray, sample_rate: int):
        """Méthode de debug pour la lecture audio."""
        try:
            import pyaudio
            p = pyaudio.PyAudio()
            
            # Afficher les informations de debug
            logger.info(f"[DEBUG] Audio data: {len(audio_data)} samples, dtype: {audio_data.dtype}")
            logger.info(f"[DEBUG] Sample rate: {sample_rate}")
            
            # Vérifier les valeurs min/max pour détecter les problèmes de volume
            if audio_data.dtype == np.int16:
                max_val = np.max(np.abs(audio_data))
                logger.info(f"[DEBUG] Valeur max (int16): {max_val}/32767")
            elif audio_data.dtype == np.float32:
                max_val = np.max(np.abs(audio_data))
                logger.info(f"[DEBUG] Valeur max (float32): {max_val:.3f}")
            
            # Lecture de test
            stream = p.open(
                format=pyaudio.paInt16 if audio_data.dtype == np.int16 else pyaudio.paFloat32,
                channels=1,
                rate=sample_rate,
                output=True
            )
            
            stream.write(audio_data.tobytes())
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            logger.info("[DEBUG] Lecture debug réussie")
            
        except Exception as e:
            logger.error(f"[DEBUG] Erreur lecture: {e}")


    def _synthesize_python_simple(self, text: str) -> Optional[np.ndarray]:
        """Synthèse avec gestion robuste du sample rate."""
        try:
            voice_obj = self.current_voice["voice"]
            
            # Récupérer le sample rate correct depuis la configuration
            sample_rate = getattr(voice_obj.config, 'sample_rate', 22050)
            logger.info(f"[AUDIO] Sample rate configuré: {sample_rate} Hz")
            
            # Méthode directe avec gestion d'erreur améliorée
            audio_data = voice_obj.synthesize(text)
            audio_chunks = list(audio_data)
            
            if len(audio_chunks) == 0:
                logger.error("[ERREUR] Aucune donnée audio générée")
                return None
            
            # Concaténer les chunks audio
            audio_samples = np.concatenate([chunk.audio_float_array for chunk in audio_chunks])
            
            # Conversion float32 -> int16 avec normalisation
            audio_int16 = (audio_samples * 32767).astype(np.int16)
            
            # Vérifier la qualité audio
            audio_duration = len(audio_int16) / sample_rate
            logger.info(f"[AUDIO] Durée générée: {audio_duration:.2f}s, {len(audio_int16)} échantillons")
            
            return audio_int16
            
        except Exception as e:
            logger.error("[ERREUR] Synthèse Python échouée: %s", e)
            return self._synthesize_cli(text, 1.0)


    def _synthesize_cli(self, text: str, speed: float) -> Optional[np.ndarray]:
        """Synthèse avec la CLI Piper."""
        temp_wav_path = os.path.join(tempfile.gettempdir(), f"piper_temp_{uuid.uuid4()}.wav")
        
        try:
            cmd = [
                "piper", 
                "--model", self.current_voice["model_path"],
                "--output_file", temp_wav_path,
            ]
            
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
            
            if not os.path.exists(temp_wav_path):
                logger.error("[ERREUR] Fichier de sortie non créé: %s", temp_wav_path)
                return None
            
            with wave.open(temp_wav_path, "rb") as wav_file:
                frames = wav_file.readframes(wav_file.getnframes())
                audio_data = np.frombuffer(frames, dtype=np.int16)
                
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
            if os.path.exists(temp_wav_path):
                try:
                    os.unlink(temp_wav_path)
                except Exception as e:
                    logger.warning("[ATTENTION] Impossible de supprimer le fichier temporaire: %s", e)

    def _adjust_speed(self, audio_data: np.ndarray, speed: float, sample_rate: int) -> np.ndarray:
        """Ajuste la vitesse de l'audio."""
        if speed == 1.0:
            return audio_data
            
        try:
            import librosa
            audio_float = audio_data.astype(np.float32) / 32768.0
            adjusted_audio = librosa.effects.time_stretch(audio_float, rate=speed)
            adjusted_audio = (adjusted_audio * 32768.0).astype(np.int16)
            logger.debug("[AUDIO] Vitesse ajustée: %.2fx", speed)
            return adjusted_audio
            
        except ImportError:
            logger.warning("[ATTENTION] Librosa non disponible, vitesse non ajustée")
            return audio_data
        except Exception as e:
            logger.warning("[ATTENTION] Erreur ajustement vitesse: %s", e)
            return audio_data

    def say_direct_method(self, text: str):
        """Utilise EXACTEMENT votre script de test qui fonctionne."""
        try:
            import os
            import numpy as np
            import pyaudio
            from piper import PiperVoice

            # Chemins vers les fichiers de la voix
            model_path = os.path.join("voices", "fr_FR-siwis-medium", "fr_FR-siwis-medium.onnx")
            config_path = os.path.join("voices", "fr_FR-siwis-medium", "fr_FR-siwis-medium.onnx.json")
            logger.info(f"model_path: {model_path} ")
            logger.info(f"config_path: {config_path} ")
            # Initialise PiperVoice
            voice = PiperVoice.load(model_path, config_path=config_path, use_cuda=False)

            # Synthétise le texte - METHODE EXACTE
            audio_data = voice.synthesize(text)

            # Convertit les objets AudioChunk en tableau NumPy
            audio_chunks = list(audio_data)
            if len(audio_chunks) == 0:
                raise ValueError("Aucune donnée audio générée.")

            # Utilise audio_float_array pour obtenir les données audio
            audio_samples = np.concatenate([chunk.audio_float_array for chunk in audio_chunks])

            # Joue l'audio - METHODE EXACTE
            p = pyaudio.PyAudio()
            stream = p.open(format=pyaudio.paFloat32, channels=1, rate=22050, output=True)
            stream.write(audio_samples.astype(np.float32).tobytes())
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            logger.info("✅ Méthode directe réussie")
            return True
            
        except Exception as e:
            logger.error(f"❌ Méthode directe échouée: {e}")
            return False

    def say(self, text: str, speed: float = 1.0):
        """Méthode utilitaire pour synthétiser et jouer l'audio."""
        logger.info(f"Demande de synthèse vocale pour le texte: {text}")
        audio_data = self.synthesize(text, speed)
        if audio_data is not None:
            try:
                import pyaudio
            except ImportError:
                logger.error("[ERREUR] pyaudio non installé. Installez-le avec `pip install pyaudio`.")
                return False
                
            # Utiliser le sample_rate de la voix chargée - CORRECTION IMPORTANTE
            sample_rate = self.current_voice.get("sample_rate", 22050)
            logger.info(f"[AUDIO] Sample rate utilisé: {sample_rate} Hz")
            
            # Vérifier la longueur des données audio
            logger.info(f"[AUDIO] Données audio: {len(audio_data)} échantillons, dtype: {audio_data.dtype}")
            
            # Lecture audio avec pyaudio - CORRECTION COMPLÈTE
            p = pyaudio.PyAudio()
            
            try:
                # Toujours utiliser int16 pour la compatibilité
                if audio_data.dtype != np.int16:
                    if audio_data.dtype == np.float32:
                        # Conversion float32 -> int16
                        audio_data = (audio_data * 32767).astype(np.int16)
                    else:
                        # Conversion vers int16
                        audio_data = audio_data.astype(np.int16)
                
                # Créer le stream avec les paramètres corrects
                stream = p.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=int(sample_rate),  # Assurer que c'est un integer
                    output=True,
                    frames_per_buffer=1024
                )
                
                # Écrire les données audio
                stream.write(audio_data.tobytes())
                
                # Attendre que la lecture soit terminée
                stream.stop_stream()
                stream.close()
                
                logger.info("[AUDIO] Lecture audio terminée avec succès")
                
            except Exception as e:
                logger.error(f"[AUDIO] Erreur lors de la lecture: {e}")
                return False
            finally:
                p.terminate()
            
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
        
        if not self.current_voice:
            logger.error("[TEST] ❌ Aucune voix chargée pour le test")
            return False
            
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

if __name__ == "__main__":
    tts = TextToSpeech("fr_FR-siwis-medium")
    if tts.test_synthesis():
        print("✅ Text-to-Speech fonctionne correctement!")
    else:
        print("❌ Text-to-Speech a échoué")
