import threading
from typing import Optional
from ..core.wake_word_service import WakeWordService
from ..core.speech_recognition_service import SpeechRecognitionService
from ..core.conversation_service import ConversationService
from ..core.tts_service import TTSService
from ..core.intent_router import IntentRouter
from ..models.user_profile import UserProfile
from ..models.settings import Settings
from ..adapters.audio_input_microphone import AudioInputAdapter
from ..adapters.audio_output_speaker import AudioOutputAdapter
from ..adapters.cloud_openai_api import OpenAIAPIAdapter
from ..utils.logger import logger

class AssistantController:
    def __init__(self, config):
        self.config = config
        self.is_running = False
        
        # Initialiser les adapters
        self.audio_input = AudioInputAdapter(config)
        self.audio_output = AudioOutputAdapter()
        self.llm_adapter = OpenAIAPIAdapter(config)
        
        # Initialiser les services
        self.wake_word_service = WakeWordService(self.audio_input)
        self.speech_recognition_service = SpeechRecognitionService(self.audio_input)
        self.conversation_service = ConversationService(self.llm_adapter)
        self.tts_service = TTSService(self.audio_output)
        self.intent_router = IntentRouter()
        
        # Modèles de données
        self.user_profile = UserProfile()
        self.settings = Settings()
        
        # Setup des callbacks
        self._setup_callbacks()
    
    def _setup_callbacks(self):
        """Configure les callbacks entre services."""
        self.wake_word_service.set_wake_word_callback(self._on_wake_word_detected)
        self.wake_word_service.set_audio_callback(self._on_audio_received)
    
    def start(self):
        """Démarre l'assistant."""
        if self.is_running:
            logger.warning("L'assistant est déjà démarré")
            return
        
        try:
            self.is_running = True
            
            # Charger les paramètres
            self._load_settings()
            
            # Démarrer les services
            self.wake_word_service.start_detection(self.settings.microphone_index)
            
            # Annoncer le démarrage
            self.tts_service.speak("Assistant vocal démarré")
            
            logger.info("Assistant démarré avec succès")
            
        except Exception as e:
            logger.error(f"Erreur démarrage assistant: {e}")
            self.is_running = False
    
    def stop(self):
        """Arrête l'assistant."""
        self.is_running = False
        self.wake_word_service.stop_detection()
        logger.info("Assistant arrêté")
    
    def process_text_input(self, text: str, model: str = None):
        """Traite une entrée texte."""
        try:
            # Router l'intention
            intent, params = self.intent_router.route_intent(text)
            
            if intent == "file_analysis":
                self._handle_file_analysis(params)
            elif intent == "system_command":
                self._handle_system_command(params)
            else:
                self._handle_conversation(params, model)
                
        except Exception as e:
            logger.error(f"Erreur traitement texte: {e}")
            self.tts_service.speak(f"Erreur: {str(e)}")
    
    def _on_wake_word_detected(self):
        """Callback quand le mot-clé est détecté."""
        logger.info("Mot-clé détecté, prêt à recevoir la commande")
        self.tts_service.speak("Je vous écoute")
    
    def _on_audio_received(self, audio_data):
        """Callback quand l'audio est reçu."""
        try:
            # Transcrire l'audio
            text = self.speech_recognition_service.transcribe(audio_data)
            if text:
                logger.info(f"Texte transcrit: {text}")
                self.process_text_input(text)
            else:
                logger.warning("Aucun texte transcrit")
                
        except Exception as e:
            logger.error(f"Erreur traitement audio: {e}")
    
    def _handle_conversation(self, params: dict, model: str = None):
        """Gère une conversation normale."""
        text = params.get("text", "")
        if not text:
            return
        
        # Ajouter au chat
        self.conversation_service.add_message("user", text)
        
        # Générer la réponse
        response = self.conversation_service.generate_response(text, model)
        
        # Parler la réponse
        self.tts_service.speak(response)
    
    def _handle_file_analysis(self, params: dict):
        """Gère une commande d'analyse de fichiers."""
        # À implémenter selon vos besoins
        path = params.get("path", ".")
        text = params.get("text", "")
        
        self.tts_service.speak(f"Analyse des fichiers dans {path}")
        # Ici vous pouvez appeler votre service d'analyse de fichiers
    
    def _handle_system_command(self, params: dict):
        """Gère une commande système."""
        command = params.get("command", "")
        if "quit" in command or "exit" in command or "stop" in command:
            self.stop()
            self.tts_service.speak("Arrêt de l'assistant")
    
    def _load_settings(self):
        """Charge les paramètres de l'utilisateur."""
        # Charger depuis fichier de config ou base de données
        pass
    
    def get_conversation_history(self):
        """Retourne l'historique de conversation."""
        return self.conversation_service.get_history()
    
    def clear_conversation(self):
        """Efface l'historique de conversation."""
        self.conversation_service.clear_history()
