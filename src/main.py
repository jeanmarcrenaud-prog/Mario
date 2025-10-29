import sys
import atexit
import threading
import time
from .config import config
from .utils.file_analyzer import FileAnalyzer
from .utils.logger import logger
from .ui.interface import AssistantInterface
from .utils.system_monitor import get_system_info
from .core.speech_recognition import SpeechRecognizer
from .core.text_to_speech import TextToSpeech

class AssistantVocal:
    def __init__(self):
        self.interface = None
        self.speech_recognizer = None
        self.tts = None
        self._is_running = False
        self._setup_cleanup()

    def _setup_cleanup(self):
        """Configure le nettoyage à la fermeture."""
        atexit.register(self._cleanup)

    def _cleanup(self):
        """Nettoie les ressources."""
        logger.info("Nettoyage des ressources...")
        self._is_running = False
        
        # Nettoyage spécifique des composants
        if self.speech_recognizer:
            try:
                self.speech_recognizer.cleanup()
            except Exception as e:
                logger.error(f"Erreur lors du nettoyage du recognizer: {e}")
        
        if self.tts:
            try:
                self.tts.cleanup()
            except Exception as e:
                logger.error(f"Erreur lors du nettoyage du TTS: {e}")

    def _preload_models(self):
        """Précharge les modèles nécessaires."""
        logger.info("Préchargement des modèles...")

        try:
            # Préchargement de Whisper
            logger.info("Chargement du modèle Whisper...")
            self.speech_recognizer = SpeechRecognizer()
            if not self.speech_recognizer.load_model(config.WHISPER_MODEL_NAME):
                logger.error("Échec du chargement du modèle Whisper")
                return False
            logger.info("Modèle Whisper chargé avec succès")

            # Chargement de Piper
            logger.info("Chargement de la voix Piper...")
            self.tts = TextToSpeech(default_voice=config.DEFAULT_PIPER_VOICE)
            logger.info(f"Voix Piper '{config.DEFAULT_PIPER_VOICE}' prête")
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du préchargement des modèles: {e}")
            return False

    def say(self, text: str):
        """Synthétise et joue un texte."""
        try:
            if self.tts is None:
                logger.error("TTS non initialisé")
                return
                
            audio_data = self.tts.synthesize(text)
            if audio_data is not None:
                # Ici, ajoutez le code pour jouer l'audio (par exemple, avec pyaudio)
                logger.info("Lecture de l'audio synthétisé")
                # Exemple de code pour jouer l'audio :
                self._play_audio(audio_data)
            else:
                logger.error("Échec de la synthèse vocale")
                
        except Exception as e:
            logger.error(f"Erreur lors de la synthèse vocale: {e}")

    def _play_audio(self, audio_data):
        """Méthode pour jouer l'audio (à implémenter selon votre solution)"""
        # Exemple avec pyaudio :
        import pyaudio
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=config.SAMPLERATE, output=True)
        stream.write(audio_data)
        stream.stop_stream()
        stream.close()
        p.terminate()
        pass

    def run(self):
        """Démarre l'assistant."""
        try:
            logger.info("Démarrage de l'assistant vocal")
            logger.info(get_system_info())

            # Préchargement des modèles
            if not self._preload_models():
                logger.error("Échec du préchargement des modèles")
                sys.exit(1)

            # Création de l'interface avec le recognizer préchargé
            logger.info("Création de l'interface...")
            self.interface = AssistantInterface(speech_recognizer=self.speech_recognizer)

            # Création et lancement de l'interface
            app = self.interface.create_interface()
            logger.info("Interface créée, démarrage du serveur...")
            
            import socket
            local_ip = socket.gethostbyname(socket.gethostname())
            logger.info(f"[WEB] Accès local : http://{local_ip}:{config.INERFACE_PORT}")
            
            # Démarrage du serveur dans un thread séparé pour éviter les blocages
            def start_server():
                app.launch(
                    server_name="0.0.0.0",      # 🌍 Permet l’accès depuis le réseau local
                    server_port=config.INTERFACE_PORT,
                    share=False,
                    inbrowser=True
                )
            
            server_thread = threading.Thread(target=start_server, daemon=True)
            server_thread.start()
            
            # Maintien en vie de l'assistant
            self._is_running = True
            while self._is_running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Arrêt par l'utilisateur")
        except Exception as e:
            logger.error(f"Erreur fatale: {e}")
            sys.exit(1)
        finally:
            self._cleanup()

if __name__ == "__main__":
    assistant = AssistantVocal()
    assistant.run()
