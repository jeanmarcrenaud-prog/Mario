import sys
import atexit
import threading
import time
import socket
import yaml
import signal
from typing import Dict, Optional, Any
import re
from src.config.config import ConfigManager, config
from src.utils.logger import logger, safe_run
from src.utils.system_monitor import SystemMonitor
from src.models.settings import Settings
from src.views.web_interface_gradio import GradioWebInterface
from src.service.conversation_service import ConversationService
from src.service.tts_service import TTSService
from src.services.wake_word_service import WakeWordService
from src.service.speech_recognition_service import SpeechRecognitionService
from src.service.llm_service import LLMService
from src.service.project_analyzer_service import ProjectAnalyzerService
from src.core.performance_optimizer import PerformanceOptimizer
from src.core.prompt_manager import PromptManager

class AssistantVocal:
    def __init__(
        self,
        settings: Settings,
        conversation_service: ConversationService,
        prompt_manager: PromptManager,
        tts_service: TTSService,
        wake_word_service: WakeWordService,
        speech_recognition_service: SpeechRecognitionService,
        llm_service: LLMService,
        project_analyzer_service: ProjectAnalyzerService,
        system_monitor: SystemMonitor,
        performance_optimizer: PerformanceOptimizer
    ):
        """
        Constructeur avec injection de dépendances explicite.
        Toutes les dépendances sont passées en paramètres.
        """
        self._is_running = False
        self.settings = settings
        self.conversation_service = conversation_service
        self.prompt_manager = prompt_manager
        self.tts_service = tts_service
        self.wake_word_service = wake_word_service
        self.speech_recognition_service = speech_recognition_service
        self.llm_service = llm_service
        self.project_analyzer_service = project_analyzer_service
        self.system_monitor = system_monitor
        self.performance_optimizer = performance_optimizer
        self.web_interface: Optional[GradioWebInterface] = None
        self.console_view = None
        
        # Paramètres pour la gestion d'erreurs
        self.max_retry_attempts = 3
        self.transcription_timeout = 10.0  # secondes
        self.audio_processing_timeout = 30.0  # secondes
        
        self._setup_cleanup()
        logger.info("🔧 AssistantVocal initialisé avec injection de dépendances")

    def _setup_console_view(self):
        """Configure la console view."""
        try:
            from src.views.console_view import ConsoleView
            self.console_view = ConsoleView(self)
            logger.info("✅ ConsoleView initialisé")
        except Exception as e:
            logger.warning(f"⚠️ ConsoleView non disponible: {e}")
            self.console_view = None

    def _setup_cleanup(self):
        """Configure le nettoyage à la fermeture."""
        atexit.register(self._cleanup)

    def _cleanup(self):
        """Nettoie les ressources à la fermeture."""
        if not self._is_running:
            return
            
        logger.info("🧹 Nettoyage des ressources...")
        self._is_running = False
        self.wake_word_service.stop_detection()
        self.performance_optimizer.stop_monitoring()

    def _is_french_text(self, text: str) -> bool:
        """Vérifie si le texte est en français."""
        if not text or not text.strip():
            return False
            
        # Expressions régulières pour détecter le français
        french_patterns = [
            r'\b(le|la|les|un|une|des|du|de|à|et|ou|mais|si|que|qui|quoi|où|quand|comment)\b',
            r'\b(je|tu|il|elle|nous|vous|ils|elles)\b',
            r'\b(suis|es|est|sommes|êtes|sont|ai|as|a|avons|avez|ont)\b',
            r'\b(de|dans|sur|sous|entre|avant|après|pendant|pour|par|avec|sans)\b'
        ]
        
        french_word_count = 0
        total_words = len(text.split())
        
        if total_words == 0:
            return False
            
        for pattern in french_patterns:
            matches = re.findall(pattern, text.lower())
            french_word_count += len(matches)
        
        # Si plus de 10% des mots sont des mots français courants
        return (french_word_count / total_words) > 0.1

    def _on_wake_word_detected(self):
        """Callback quand le mot-clé est détecté."""
        logger.info("🎯 Mot-clé détecté ! Prêt à recevoir la commande")
        self.speak_response("Je vous écoute")
    
    def _on_audio_received(self, audio_data):
        """Callback quand l'audio est reçu - avec gestion d'erreurs améliorée."""
        logger.info(f"🎤 Audio reçu ({len(audio_data)} échantillons)")
        
        try:
            # Timeout pour le traitement
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("Timeout lors du traitement audio")

            # --- Gestion multiplateforme du timeout ---
            use_signal_timeout = hasattr(signal, "SIGALRM")

            if use_signal_timeout:
                # Linux / macOS
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(int(self.audio_processing_timeout))
            else:
                # Windows → SIGALRM n'existe pas
                logger.debug("⛔ SIGALRM non disponible sur cette plateforme → timeouts désactivés")
            # -------------------------------------------

            try:
                # Tentatives de retry en cas d'erreur
                for attempt in range(self.max_retry_attempts):
                    try:
                        # Timeout spécifique pour la transcription
                        if use_signal_timeout:
                            signal.alarm(int(self.transcription_timeout))

                        text = self.speech_recognition_service.transcribe(audio_data, "fr")

                        if use_signal_timeout:
                            signal.alarm(0)  # Désactiver

                        if text and text.strip():
                            logger.info(f"📝 Texte transcrit: {text}")

                            if not self._is_french_text(text):
                                logger.warning(f"⚠️ Texte transcrit ne semble pas être en français: {text}")
                                if attempt < self.max_retry_attempts - 1:
                                    logger.info(f"🔄 Tentative {attempt + 1}/{self.max_retry_attempts} de retranscription")
                                    continue

                            response = self.process_user_message(text)
                            self.speak_response(response)
                            return

                        else:
                            logger.warning("🔇 Aucun texte transcrit")
                            if attempt < self.max_retry_attempts - 1:
                                logger.info(f"🔄 Tentative {attempt + 1}/{self.max_retry_attempts} de retranscription")
                                time.sleep(0.5)
                                continue
                            else:
                                break

                    except TimeoutError:
                        logger.error(f"⏰ Timeout transcription (tentative {attempt + 1})")
                        if attempt < self.max_retry_attempts - 1:
                            logger.info(f"🔄 Tentative {attempt + 1}/{self.max_retry_attempts} après timeout")
                            continue
                        else:
                            raise

                    except Exception as e:
                        logger.error(f"❌ Erreur transcription (tentative {attempt + 1}): {e}")
                        if attempt < self.max_retry_attempts - 1:
                            logger.info(f"🔄 Tentative {attempt + 1}/{self.max_retry_attempts} après erreur")
                            time.sleep(1)
                            continue
                        else:
                            raise

                logger.error("💥 Toutes les tentatives de transcription ont échoué")
                self.speak_response("Désolé, je n'ai pas réussi à comprendre votre message. Pouvez-vous répéter ?")

            except TimeoutError:
                logger.error("⏰ Timeout global lors du traitement audio")
                self.speak_response("Désolé, le traitement de votre message a pris trop de temps.")

            except Exception as e:
                logger.error(f"❌ Erreur traitement audio: {e}")
                self.speak_response("Désolé, je n'ai pas compris votre message.")

            finally:
                if use_signal_timeout:
                    signal.alarm(0)  # Toujours désactiver le timeout
                
        except Exception as e:
            logger.error(f"❌ Erreur fatale dans _on_audio_received: {e}")
            self.speak_response("Désolé, une erreur inattendue s'est produite.")

    def optimize_performance(self, aggressive: bool = False) -> bool:
        """Optimise les performances de l'assistant."""
        try:
            logger.info(f"⚡ Optimisation des performances {'agressive' if aggressive else 'normale'}")
            
            memory_success = self.performance_optimizer.optimize_memory(aggressive=aggressive)
            models_success = self.performance_optimizer.optimize_models()
            
            # Optimisations spécifiques aux services
            services = [
                (self.speech_recognition_service, 'optimize_model_cache'),
                (self.tts_service, 'optimize_voice_cache')
            ]
            
            for service, method_name in services:
                if hasattr(service, method_name):
                    getattr(service, method_name)()
            
            success = memory_success or models_success
            logger.info("✅ Optimisation terminée" if success else "✅ Pas d'optimisations nécessaires")
            return success
            
        except Exception as e:
            logger.error(f"❌ Erreur optimisation: {e}")
            return False

    def get_optimization_profile(self) -> Dict:
        """Retourne le profil d'optimisation."""
        return self.performance_optimizer.get_optimization_profile()

    def set_optimization_profile(self, profile: Dict):
        """Définit le profil d'optimisation."""
        self.performance_optimizer.set_optimization_profile(profile)

    def set_performance_thresholds(self, **thresholds):
        """Définit les seuils de performance."""
        self.performance_optimizer.set_thresholds(**thresholds)
    
    def get_performance_status(self) -> Dict:
        """Retourne le statut de performance."""
        return self.performance_optimizer.get_resource_usage()

    def use_custom_prompt(self, prompt_id: str, input_text: str, custom_vars: Dict = None) -> str:
        """
        Utilise un prompt personnalisé.
        """
        try:
            prompt = self.prompt_manager.get_prompt(prompt_id)
            if not prompt:
                return "[ERREUR] Prompt non trouvé"
            
            prompt_text = self.prompt_manager.generate_prompt_text(
                prompt["template"], 
                input_text, 
                custom_vars
            )
            
            messages = [{"role": "user", "content": prompt_text}]
            if prompt.get("system_message"):
                messages.insert(0, {"role": "system", "content": prompt["system_message"]})
            
            response = self.llm_service.generate_response(
                messages, 
                temperature=prompt.get("temperature", 0.7)
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Erreur utilisation prompt: {e}")
            return f"[ERREUR] {str(e)}"

    # Méthodes d'adaptation pour ConsoleView
    def add_user_message(self, user_input: str):
        self.conversation_service.add_message("user", user_input)

    def generate_response(self) -> str:
        messages = self.conversation_service.get_history()
        response = self.llm_service.generate_response(messages)
        self.conversation_service.add_message("assistant", response)
        return response

    def play_tts_response(self, text: str):
        self.speak_response(text)

    def get_history(self):
        return self.conversation_service.get_history()

    def process_user_message(self, message: str) -> str:
        """Traite un message utilisateur et retourne la réponse."""
        try:
            logger.info(f"💬 Traitement du message: {message}")
            
            self.conversation_service.add_message("user", message)
            messages = self.conversation_service.get_history()
            response = self.llm_service.generate_response(messages)
            self.conversation_service.add_message("assistant", response)
            
            logger.info(f"✅ Réponse générée: {response[:100]}...")
            return response
            
        except Exception as e:
            logger.error(f"❌ Erreur traitement message: {e}")
            error_response = "[ERREUR] Impossible de traiter votre message"
            self.conversation_service.add_message("assistant", error_response)
            return error_response

    def get_conversation_history(self):
        return self.conversation_service.get_history()

    def clear_conversation(self):
        self.conversation_service.clear_history()
        logger.info("Conversation effacée")

    def analyze_project(self, project_path: str) -> Dict:
        """Analyse un projet complet."""
        try:
            logger.info(f"🔍 Analyse du projet: {project_path}")
            report = self.project_analyzer_service.analyze_project(project_path)
            
            summary = report.get("summary", "Analyse terminée")
            self.speak_response(f"Analyse du projet terminée. {summary}")
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse projet: {e}")
            error_msg = f"Erreur analyse projet: {str(e)}"
            self.speak_response(error_msg)
            return {"error": error_msg}

    def speak_response(self, text: str) -> bool:
        """Parle une réponse avec le TTS."""
        if not text or not text.strip():
            logger.warning("Texte vide pour la synthèse vocale")
            return False
            
        try:
            if self.console_view:
                self.console_view.display_message(f"Assistant: {text}")
            else:
                logger.info(f"🤖 Assistant: {text}")
        except Exception:
            logger.info(f"🤖 Assistant: {text}")
        
        try:
            success = self.tts_service.say(text, self.settings.speech_speed)
            logger.info("✅ Synthèse vocale réussie" if success else "❌ Échec de la synthèse vocale")
            return success
        except Exception as e:
            logger.error(f"❌ Erreur dans speak_response: {e}")
            return False

    def start_console_interface(self):
        """Démarre l'interface console."""
        try:
            logger.info("🖥️  Démarrage interface console...")
            
            # Initialiser la console view si ce n'est pas déjà fait
            if self.console_view is None:
                self._setup_console_view()
            
            if self.console_view:
                # Démarrer la boucle console dans un thread séparé
                console_thread = threading.Thread(target=self.console_view.loop, daemon=True)
                console_thread.start()
                logger.info("✅ Interface console démarrée")
                return True
            else:
                logger.warning("⚠️ Interface console non disponible")
                return False
                
        except Exception as e:
            logger.error(f"Erreur démarrage interface console: {e}")
            return False

    def start_web_interface(self):
        """Démarre l'interface web Gradio."""
        try:
            logger.info("🌐 Démarrage interface web...")
            self.web_interface = GradioWebInterface(self)
            
            def launch_interface():
                try:
                    local_ip = socket.gethostbyname(socket.gethostname())
                    logger.info(f"🌐 Interface web disponible sur: http://localhost:{self.settings.web_port}")
                    logger.info(f"🌐 Accès réseau: http://{local_ip}:{self.settings.web_port}")
                    
                    self.web_interface.launch(
                        server_name="0.0.0.0",
                        server_port=self.settings.web_port,
                        share=False,
                        inbrowser=True,
                        prevent_thread_lock=True
                    )
                except Exception as e:
                    logger.error(f"Erreur lancement interface: {e}")
            
            interface_thread = threading.Thread(target=launch_interface, daemon=True)
            interface_thread.start()
            
            logger.info("✅ Interface web démarrée")
            return True
            
        except Exception as e:
            logger.error(f"Erreur démarrage interface web: {e}")
            return False

    @safe_run("AssistantVocal")
    def run(self):
        """Démarre l'assistant vocal."""
        logger.info("🚀 Démarrage de l'assistant vocal")
        
        try:
            system_info = self.system_monitor.get_system_info_text()
            logger.info("📊 Informations système:")
            for line in system_info.split('\n'):
                if line.strip():
                    logger.info(line)
        except Exception as e:
            logger.warning(f"Impossible d'afficher les infos système: {e}")
        
        logger.info(f"Configuration: Voix={self.settings.voice_name}, Modèle={self.settings.llm_model}")
        
        # Test du service LLM
        logger.info("🧪 Test du service LLM...")
        if self.llm_service.test_service():
            logger.info("✅ Service LLM fonctionnel")
            test_messages = [{"role": "user", "content": "Bonjour, comment allez-vous ?"}]
            test_response = self.llm_service.generate_response(test_messages)
            logger.info(f"📝 Test réponse LLM: {test_response[:100]}...")
        else:
            logger.warning("⚠️ Service LLM non disponible")
        
        # Configuration des callbacks
        self.wake_word_service.set_wake_word_callback(self._on_wake_word_detected)
        self.wake_word_service.set_audio_callback(self._on_audio_received)
        
        try:
            # Démarrage des interfaces
            logger.info("🌐 Démarrage interface web...")
            if not self.start_web_interface():
                logger.warning("⚠️ Impossible de démarrer l'interface web")
            
            logger.info("🔍 Démarrage détection wake word...")
            self.wake_word_service.start_detection(self.settings.microphone_index)
            
            # Tests
            logger.info("🧪 Test de conversation...")
            test_response = self.process_user_message("Bonjour, comment allez-vous ?")
            logger.info(f"📝 Test réponse: {test_response}")
            
            logger.info("🧪 Test TTS...")
            tts_success = self.tts_service.test_synthesis()
            if tts_success:
                logger.info("✅ Service TTS fonctionnel")
                self.speak_response("Mario est opérationnel")
            else:
                logger.warning("⚠️ Service TTS non disponible")
            
            # Interface console
            logger.info("🖥️  Démarrage interface console...")
            self.start_console_interface()
            
            # Boucle principale
            self._is_running = True
            while self._is_running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("🛑 Arrêt manuel par l'utilisateur")
        except Exception as e:
            logger.critical(f"💥 Erreur fatale dans run(): {e}")
            import traceback
            logger.error(traceback.format_exc())
        finally:
            self._cleanup()
            logger.info("⏹️ Assistant arrêté proprement")
