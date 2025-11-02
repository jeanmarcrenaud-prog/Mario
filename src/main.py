import sys
import atexit
import threading
import time
import socket
import pyaudio
import yaml
from src.factory import RecognizerFactory

from src.config import config
from src.utils.file_analyzer import FileAnalyzer
from src.utils.logger import logger, safe_run
from src.ui.interface import AssistantInterface
from src.utils.system_monitor import SystemMonitor
from src.core.speech_recognition import SpeechRecognizer
from src.core.text_to_speech import TextToSpeech


class AssistantVocal:
    def __init__(self):
        self.interface = None
        self.speech_recognizer = None
        self.tts = None
        self._is_running = False
        self._setup_cleanup()
        logger.info("🔧 Initialisation de l'assistant vocal terminée")

    def main():
        with open("config.yaml") as f:
            config = yaml.safe_load(f)

        recognizer = RecognizerFactory.create(config["recognizer"])
        text = recognizer.transcribe("exemple.wav")
        print(text)

    # ===============================================================
    # 🔹 Nettoyage des ressources
    # ===============================================================
    def _setup_cleanup(self):
        """Configure le nettoyage à la fermeture."""
        atexit.register(self._cleanup)

    def _cleanup(self):
        """Nettoie les ressources à la fermeture."""
        logger.info("🧹 Nettoyage des ressources...")
        self._is_running = False

        # Nettoyage spécifique des composants
        if self.speech_recognizer:
            try:
                self.speech_recognizer.cleanup()
            except Exception as e:
                logger.error(f"[CLEANUP] Erreur recognizer: {e}")

        if self.tts:
            try:
                self.tts.cleanup()
            except Exception as e:
                logger.error(f"[CLEANUP] Erreur TTS: {e}")

    # ===============================================================
    # 🔹 Préchargement des modèles
    # ===============================================================
    @safe_run("AssistantVocal")
    def _preload_models(self) -> bool:
        """Précharge Whisper et Piper avec gestion des erreurs."""
        logger.info("🔄 Préchargement des modèles...")

        try:
            # Whisper
            self.speech_recognizer = SpeechRecognizer()
            if not self.speech_recognizer.load_model(config.WHISPER_MODEL_NAME):
                logger.error("❌ Échec du chargement du modèle Whisper")
                return False
            logger.info("✅ Modèle Whisper chargé avec succès")

            # Piper - avec vérification simple
            self.tts = TextToSpeech(default_voice=config.DEFAULT_PIPER_VOICE)
            
            # Vérification simple que la voix est chargée (sans get_voice_info)
            if not self.tts.current_voice:
                logger.error("❌ Échec du chargement de la voix Piper")
                return False
                
            logger.info(f"🔊 Voix Piper prête : {config.DEFAULT_PIPER_VOICE}")
            
            # Test de synthèse pour confirmer le fonctionnement
            test_text = "Test de synthèse vocale"
            logger.info(f"[TEST] Test de synthèse: '{test_text}'")
            audio_data = self.tts.synthesize(test_text)
            
            if audio_data is not None:
                logger.info(f"✅ Test de synthèse réussi ({len(audio_data)} échantillons)")
            else:
                logger.warning("⚠️ Test de synthèse a retourné None")

            return True

        except Exception as e:
            logger.error(f"Erreur lors du préchargement des modèles: {e}")
            return False

    # ===============================================================
    # 🔹 Synthèse et lecture audio
    # ===============================================================
    @safe_run("AssistantVocal")
    def say(self, text: str):
        """Synthétise et lit un texte."""
        if not text or not self.tts:
            logger.warning("TTS non prêt ou texte vide")
            return

        logger.info(f"🎤 Synthèse vocale : '{text[:50]}...'")
        audio_data = self.tts.synthesize(text)

        if audio_data is None:
            logger.error("❌ Échec de la synthèse vocale")
            return

        self._play_audio(audio_data)

    @safe_run("AssistantVocal")
    def _play_audio(self, audio_data):
        """Lecture audio sécurisée via PyAudio."""
        try:
            p = pyaudio.PyAudio()
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=config.SAMPLERATE,
                output=True
            )
            stream.write(audio_data)
            stream.stop_stream()
            stream.close()
            p.terminate()
            logger.info("🔊 Lecture de l'audio terminée")
        except Exception as e:
            logger.error(f"[AUDIO] Erreur de lecture : {e}")

    # ===============================================================
    # 🔹 Lancement principal
    # ===============================================================
    @safe_run("AssistantVocal")
    def run(self):
        """Démarre l'assistant vocal et l'interface utilisateur."""
        logger.info("🚀 Démarrage de l'assistant vocal")

        monitor = SystemMonitor()
        logger.info(monitor.get_system_info_text())

        if not self._preload_models():
            logger.error("❌ Impossible de précharger les modèles, arrêt.")
            sys.exit(1)

        try:
            logger.info("🖥️ Création de l'interface Gradio...")
            self.interface = AssistantInterface(
                speech_recognizer=self.speech_recognizer, 
                tts=self.tts  # Passer l'instance TTS partagée
            )
            app = self.interface.create_interface()

            local_ip = socket.gethostbyname(socket.gethostname())
            logger.info(f"🌐 Accès local : http://{local_ip}:{config.INTERFACE_PORT}")

            def start_server():
                try:
                    app.launch(
                        server_name="0.0.0.0",
                        server_port=config.INTERFACE_PORT,
                        share=False,
                        inbrowser=True
                    )
                except Exception as e:
                    logger.error(f"[SERVER] Échec du démarrage de Gradio : {e}")

            server_thread = threading.Thread(target=start_server, daemon=True)
            server_thread.start()
            logger.info("✅ Interface lancée avec succès")

            # Boucle principale
            self._is_running = True
            while self._is_running:
                time.sleep(1)

        except KeyboardInterrupt:
            logger.info("🛑 Arrêt manuel par l'utilisateur")
        except Exception as e:
            logger.critical(f"💥 Erreur fatale dans run(): {e}")
        finally:
            self._cleanup()
            logger.info("⏹️ Assistant arrêté proprement")


if __name__ == "__main__":
    assistant = AssistantVocal()
    assistant.run()
