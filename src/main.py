import sys
import atexit
import threading
import time
import socket
import pyaudio
import yaml
from typing import Dict
from src.config.config import ConfigManager, config
from src.utils.logger import logger, safe_run
from src.utils.system_monitor import SystemMonitor
from src.core.conversation_service import ConversationService
from src.core.tts_service import TTSService
from src.core.wake_word_service import WakeWordService
from src.models.settings import Settings
from src.ui.web_interface_gradio import GradioWebInterface
from src.core.speech_recognition_service import SpeechRecognitionService
from src.core.llm_service import LLMService
from src.core.project_analyzer_service import ProjectAnalyzerService
from src.core.performance_optimizer import PerformanceOptimizer
from src.core.prompt_manager import PromptManager

class AssistantVocal:
    def __init__(self):
        self._is_running = False
        self.settings = Settings.from_config(config)
        self.conversation_service = ConversationService()
        self.prompt_manager = PromptManager()
        self.tts_service = TTSService(self.settings.voice_name)
        self.wake_word_service = WakeWordService()
        self.speech_recognition_service = SpeechRecognitionService("base")
        self.llm_service = LLMService()
        self.project_analyzer_service = ProjectAnalyzerService(self.llm_service)
        self.system_monitor = SystemMonitor()
        self.web_interface = None
        self.performance_optimizer = PerformanceOptimizer()  # Ajout
        self.performance_optimizer.start_monitoring()  # Démarrage auto
        
        # Initialisation d'une console view basique
        self.console_view = self._create_console_view()
        
        self._setup_cleanup()
        logger.info("🔧 Initialisation de l'assistant vocal terminée")

    def _create_console_view(self):
        """Crée une console view basique ou utilise ConsoleView si disponible."""
        try:
            from src.views.console_view import ConsoleView
            console = ConsoleView()
            # Vérifier si les méthodes nécessaires existent
            if hasattr(console, 'display_message') and hasattr(console, 'get_user_input'):
                logger.info("✅ ConsoleView initialisé")
                return console
            else:
                logger.warning("⚠️ ConsoleView incomplet, utilisation de la version basique")
        except Exception as e:
            logger.warning(f"⚠️ ConsoleView non disponible: {e}")
        
        # Console view basique
        class BasicConsoleView:
            def display_message(self, message):
                logger.info(f"🤖 {message}")
            
            def get_user_input(self, prompt):
                try:
                    return input(prompt)
                except:
                    return None
                    
        return BasicConsoleView()

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
        self.wake_word_service.stop_detection()
        self.performance_optimizer.stop_monitoring()

    # ===============================================================
    # 🔹 Callbacks pour les services
    # ===============================================================
    def _on_wake_word_detected(self):
        """Callback quand le mot-clé est détecté."""
        logger.info("🎯 Mot-clé détecté ! Prêt à recevoir la commande")
        self.speak_response("Je vous écoute")
    
    def _on_audio_received(self, audio_data):
        """Callback quand l'audio est reçu."""
        logger.info(f"🎤 Audio reçu ({len(audio_data)} échantillons)")
        
        # Transcrire l'audio avec Whisper
        try:
            text = self.speech_recognition_service.transcribe(audio_data, "fr")
            
            if text and text.strip():
                logger.info(f"📝 Texte transcrit: {text}")
                
                # Traiter le texte transcrit
                response = self.process_user_message(text)
                self.speak_response(response)
            else:
                logger.warning("🔇 Aucun texte transcrit")
                
        except Exception as e:
            logger.error(f"❌ Erreur traitement audio: {e}")
            self.speak_response("Désolé, je n'ai pas compris votre message.")

    def optimize_performance(self, aggressive: bool = False) -> bool:
        """Optimise les performances de l'assistant."""
        try:
            logger.info(f"⚡ Optimisation des performances {'agressive' if aggressive else 'normale'}")
            
            # Optimiser la mémoire
            memory_success = self.performance_optimizer.optimize_memory(aggressive=aggressive)
            
            # Optimiser les modèles
            models_success = self.performance_optimizer.optimize_models()
            
            # Optimiser les caches spécifiques
            if hasattr(self.speech_recognition_service, 'optimize_model_cache'):
                self.speech_recognition_service.optimize_model_cache()
            
            if hasattr(self.tts_service, 'optimize_voice_cache'):
                self.tts_service.optimize_voice_cache()
            
            success = memory_success or models_success
            if success:
                logger.info("✅ Optimisation terminée")
            else:
                logger.info("✅ Pas d'optimisations nécessaires")
            
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
        
        Args:
            prompt_id (str): ID du prompt
            input_text (str): Texte d'entrée
            custom_vars (Dict): Variables personnalisées
            
        Returns:
            str: Réponse générée
        """
        try:
            # Récupérer le prompt
            prompt = self.prompt_manager.get_prompt(prompt_id)
            if not prompt:
                return "[ERREUR] Prompt non trouvé"
            
            # Générer le texte du prompt
            prompt_text = self.prompt_manager.generate_prompt_text(
                prompt["template"], 
                input_text, 
                custom_vars
            )
            
            # Générer la réponse avec l'IA
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
    
    # ===============================================================
    # 🔹 Gestion de la conversation
    # ===============================================================
    def process_user_message(self, message: str) -> str:
        """Traite un message utilisateur et retourne la réponse."""
        try:
            logger.info(f"💬 Traitement du message: {message}")
            
            # Ajouter le message utilisateur à la conversation
            self.conversation_service.add_message("user", message)
            
            # Récupérer l'historique complet
            messages = self.conversation_service.get_history()
            
            # Générer la réponse avec le LLM
            response = self.llm_service.generate_response(messages)
            
            # Ajouter la réponse à la conversation
            self.conversation_service.add_message("assistant", response)
            
            logger.info(f"✅ Réponse générée: {response[:100]}...")
            return response
            
        except Exception as e:
            logger.error(f"❌ Erreur traitement message: {e}")
            error_response = "[ERREUR] Impossible de traiter votre message"
            self.conversation_service.add_message("assistant", error_response)
            return error_response

    def get_conversation_history(self):
        """Retourne l'historique de conversation."""
        return self.conversation_service.get_history()

    def clear_conversation(self):
        """Efface l'historique de conversation."""
        self.conversation_service.clear_history()
        logger.info("Conversation effacée")
        if self.console_view:
            try:
                self.console_view.display_message("Conversation effacée")
            except:
                logger.info("Conversation effacée")

    def analyze_project(self, project_path: str) -> Dict:
        """Analyse un projet complet."""
        try:
            logger.info(f"🔍 Analyse du projet: {project_path}")
            report = self.project_analyzer_service.analyze_project(project_path)
            
            # Résumer pour la réponse vocale
            summary = report.get("summary", "Analyse terminée")
            self.speak_response(f"Analyse du projet terminée. {summary}")
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse projet: {e}")
            error_msg = f"Erreur analyse projet: {str(e)}"
            self.speak_response(error_msg)
            return {"error": error_msg}

    # ===============================================================
    # 🔹 Gestion TTS
    # ===============================================================
    def speak_response(self, text: str) -> bool:
        """Parle une réponse avec le TTS."""
        # Afficher dans la console si disponible
        if self.console_view:
            try:
                self.console_view.display_message(f"🤖 Assistant: {text}")
            except Exception as e:
                logger.info(f"🤖 Assistant: {text}")  # Fallback
        else:
            logger.info(f"🤖 Assistant: {text}")
        return self.tts_service.speak(text, self.settings.speech_speed)

    # ===============================================================
    # 🔹 Interface console
    # ===============================================================
    def start_console_interface(self):
        """Démarre l'interface console."""
        try:
            logger.info("🖥️  Démarrage interface console...")
            if self.console_view:
                try:
                    self.console_view.display_message("=== Assistant Vocal Mario ===")
                    self.console_view.display_message("Tapez 'quit' pour quitter")
                    self.console_view.display_message("Tapez 'help' pour la liste des commandes")
                except:
                    logger.info("=== Assistant Vocal Mario ===")
                    logger.info("Tapez 'quit' pour quitter")
                    logger.info("Tapez 'help' pour la liste des commandes")
            
            while self._is_running:
                try:
                    if self.console_view:
                        try:
                            user_input = self.console_view.get_user_input("Vous> ")
                        except:
                            user_input = input("Vous> ")
                    else:
                        user_input = input("Vous> ")
                    
                    if not user_input or user_input.lower() in ['quit', 'exit', 'q']:
                        break
                    elif user_input.lower() == 'help':
                        self._show_help()
                    elif user_input.lower() == 'clear':
                        self.clear_conversation()
                    elif user_input.lower() == 'status':
                        self._show_status()
                    else:
                        # Traiter le message utilisateur
                        response = self.process_user_message(user_input)
                        self.speak_response(response)
                        
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    logger.error(f"Erreur interface console: {e}")
                    if self.console_view:
                        try:
                            self.console_view.display_message(f"[ERREUR] {e}")
                        except:
                            logger.error(f"[ERREUR] {e}")
                    
        except Exception as e:
            logger.error(f"Erreur démarrage interface console: {e}")

    def _show_help(self):
        """Affiche l'aide de la console."""
        help_text = """
Commandes disponibles:
  help    - Affiche cette aide
  clear   - Efface l'historique de conversation
  status  - Affiche le statut de l'assistant
  quit    - Quitte l'application
        """
        if self.console_view:
            try:
                self.console_view.display_message(help_text)
            except:
                for line in help_text.strip().split('\n'):
                    logger.info(line)
        else:
            for line in help_text.strip().split('\n'):
                logger.info(line)

    def _show_status(self):
        """Affiche le statut de l'assistant."""
        try:
            status = self.get_performance_status()
            status_text = f"""
Statut de l'assistant:
  CPU: {status.get('cpu_percent', 'N/A')}%
  Mémoire: {status.get('memory_percent', 'N/A')}%
  Disque: {status.get('disk_percent', 'N/A')}%
            """
            if self.console_view:
                try:
                    self.console_view.display_message(status_text)
                except:
                    for line in status_text.strip().split('\n'):
                        logger.info(line)
            else:
                for line in status_text.strip().split('\n'):
                    logger.info(line)
        except Exception as e:
            error_msg = f"[ERREUR] Impossible d'obtenir le statut: {e}"
            if self.console_view:
                try:
                    self.console_view.display_message(error_msg)
                except:
                    logger.error(error_msg)
            else:
                logger.error(error_msg)

    # ===============================================================
    # 🔹 Interface web
    # ===============================================================
    def start_web_interface(self):
        """Démarre l'interface web Gradio."""
        try:
            logger.info("🌐 Démarrage interface web...")
            self.web_interface = GradioWebInterface(self)
            
            # Créer l'interface
            demo = self.web_interface.create_interface()
        
            # Lancer dans un thread séparé
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

    # ===============================================================
    # 🔹 Lancement principal
    # ===============================================================
    @safe_run("AssistantVocal")
    def run(self):
        """Démarre l'assistant vocal."""
        logger.info("🚀 Démarrage de l'assistant vocal")
        
        # Afficher les informations système
        try:
            system_info = self.system_monitor.get_system_info_text()
            logger.info("📊 Informations système:")
            for line in system_info.split('\n'):
                if line.strip():
                    logger.info(line)
        except Exception as e:
            logger.warning(f"Impossible d'afficher les infos système: {e}")
        
        logger.info(f"Configuration: Voix={self.settings.voice_name}, Modèle={self.settings.llm_model}")
        
        # Tester le service LLM
        logger.info("🧪 Test du service LLM...")
        if self.llm_service.test_service():
            logger.info("✅ Service LLM fonctionnel")
            
            # Test avec un message
            test_messages = [{"role": "user", "content": "Bonjour, comment allez-vous ?"}]
            test_response = self.llm_service.generate_response(test_messages)
            logger.info(f"📝 Test réponse LLM: {test_response[:100]}...")
        else:
            logger.warning("⚠️ Service LLM non disponible")
        
        # Configurer les callbacks du wake word
        self.wake_word_service.set_wake_word_callback(self._on_wake_word_detected)
        self.wake_word_service.set_audio_callback(self._on_audio_received)
        
        try:
            # Démarrer l'interface web
            logger.info("🌐 Démarrage interface web...")
            if self.start_web_interface():
                logger.info("✅ Interface web démarrée avec succès")
            else:
                logger.warning("⚠️ Impossible de démarrer l'interface web")
            
            # Démarrer la détection du mot-clé
            logger.info("🔍 Démarrage détection wake word...")
            self.wake_word_service.start_detection(self.settings.microphone_index)
            
            # Test de conversation
            logger.info("🧪 Test de conversation...")
            test_response = self.process_user_message("Bonjour, comment allez-vous ?")
            logger.info(f"📝 Test réponse: {test_response}")
            
            # Test TTS
            logger.info("🧪 Test TTS...")
            tts_success = self.tts_service.test_synthesis()
            if tts_success:
                logger.info("✅ Service TTS fonctionnel")
                self.speak_response("Le service TTS est opérationnel")
            else:
                logger.warning("⚠️ Service TTS non disponible")
            
            # Démarrer l'interface console dans un thread séparé
            logger.info("🖥️  Démarrage interface console...")
            console_thread = threading.Thread(target=self.start_console_interface, daemon=True)
            console_thread.start()
            
            # Boucle principale
            self._is_running = True
            while self._is_running:
                time.sleep(1)
                # Les services continuent de fonctionner en arrière-plan
                
        except KeyboardInterrupt:
            logger.info("🛑 Arrêt manuel par l'utilisateur")
        except Exception as e:
            logger.critical(f"💥 Erreur fatale dans run(): {e}")
            import traceback
            logger.error(traceback.format_exc())
        finally:
            self._cleanup()
            logger.info("⏹️ Assistant arrêté proprement")
            
if __name__ == "__main__":
    assistant = AssistantVocal()
    assistant.run()
