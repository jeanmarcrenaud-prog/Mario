# ────────────────────────────────────────────────────────────────────────
# main.py
# AssistantVocal – version optimisée pour AMD Ryzen 9 9800X3D + RTX 5080
# ────────────────────────────────────────────────────────────────────────

import sys
import atexit
import time
import socket
import yaml
import signal
import threading
import queue
import numpy as np
import torch
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import Dict, Optional, Any, List

# ────────────────────────────────────────────────────────────────────────
# Imports internes
# ────────────────────────────────────────────────────────────────────────
from src.config.config import ConfigManager, config
from src.utils.logger import logger, safe_run
from src.utils.system_monitor import SystemMonitor
from src.models.settings import Settings
from src.views.web_interface_gradio import GradioWebInterface
from src.services.conversation_service import ConversationService
from src.services.tts_service import TTSService
from src.services.wake_word_service import WakeWordService
from src.services.speech_recognition_service import SpeechRecognitionService
from src.services.llm_service import LLMService
from src.services.project_analyzer_service import ProjectAnalyzerService
from src.core.performance_optimizer import PerformanceOptimizer
from src.core.prompt_manager import PromptManager

# ────────────────────────────────────────────────────────────────────────
# AssistantVocal
# ────────────────────────────────────────────────────────────────────────
class AssistantVocal:
    """
    Assistant vocal principal.  Toutes les dépendances sont injectées
    explicitement pour faciliter le test et la maintenance.
    """

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------
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
        performance_optimizer: PerformanceOptimizer,
    ):
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

        # ------------------------------------------------------------------
        # Thread‑pool / process‑pool
        # ------------------------------------------------------------------
        self._wake_executor = ThreadPoolExecutor(max_workers=1)
        self._transcribe_executor = ProcessPoolExecutor(max_workers=2)
        self._tts_executor = ThreadPoolExecutor(max_workers=1)

        # ------------------------------------------------------------------
        # Pré‑fetch audio (queue + thread)
        # ------------------------------------------------------------------
        self._audio_queue: queue.Queue[np.ndarray] = queue.Queue(maxsize=5)
        self._prefetch_thread = threading.Thread(
            target=self._prefetch_audio, daemon=True
        )
        self._prefetch_thread.start()

        # ------------------------------------------------------------------
        # Gestion d’erreurs
        # ------------------------------------------------------------------
        self.max_retry_attempts = 3
        self.transcription_timeout = 10.0  # s
        self.audio_processing_timeout = 30.0  # s

        self._setup_cleanup()
        logger.info("🔧 AssistantVocal initialisé avec injection de dépendances")

    # ------------------------------------------------------------------
    # Nettoyage
    # ------------------------------------------------------------------
    def _setup_cleanup(self):
        atexit.register(self._cleanup)

    def _cleanup(self):
        if not self._is_running:
            return
        logger.info("🧹 Nettoyage des ressources...")
        self._is_running = False
        self.wake_word_service.stop_detection()
        self.performance_optimizer.stop_monitoring()
        self._wake_executor.shutdown(wait=False)
        self._transcribe_executor.shutdown(wait=False)
        self._tts_executor.shutdown(wait=False)

    # ------------------------------------------------------------------
    # Console view (optionnel)
    # ------------------------------------------------------------------
    def _setup_console_view(self):
        try:
            from src.views.console_view import ConsoleView

            self.console_view = ConsoleView(self)
            logger.info("✅ ConsoleView initialisé")
        except Exception as e:
            logger.warning(f"⚠️ ConsoleView non disponible: {e}")
            self.console_view = None

    # ------------------------------------------------------------------
    # Pré‑fetch audio (thread dédié)
    # ------------------------------------------------------------------
    def _prefetch_audio(self):
        """
        Lit les données audio en continu depuis le microphone
        (via WakeWordService) et les place dans la queue.
        """
        while self._is_running:
            try:
                # WakeWordService fournit un callback _on_audio_received
                # qui est déjà appelé sur le thread de WakeWordService.
                # Ici on ne fait rien, la queue est remplie par le callback.
                time.sleep(0.01)
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Détection du wake‑word
    # ------------------------------------------------------------------
    def _on_wake_word_detected(self):
        logger.info("🎯 Mot‑clé détecté ! Prêt à recevoir la commande")
        self.speak_response("Je vous écoute")

    # ------------------------------------------------------------------
    # Audio reçu – mise en file d’attente pour transcription
    # ------------------------------------------------------------------
    def _on_audio_received(self, audio_data: bytes):
        """
        Callback appelé par WakeWordService dès qu’un chunk audio est
        disponible.  On le convertit en float32 et on le soumet
        au pool de transcription.
        """
        logger.info(f"🎤 Audio reçu ({len(audio_data)} octets)")

        # Convertir en float32 (16 bit PCM → float32)
        audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

        # Soumettre à la transcription (process pool)
        future = self._transcribe_executor.submit(
            self.speech_recognition_service.transcribe, audio_np, "fr"
        )
        future.add_done_callback(self._handle_transcription)

    # ------------------------------------------------------------------
    # Gestion du résultat de la transcription
    # ------------------------------------------------------------------
    def _handle_transcription(self, future):
        try:
            text = future.result()
        except Exception as e:
            logger.error(f"❌ Erreur transcription: {e}")
            self.speak_response("Désolé, je n’ai pas compris votre message.")
            return

        if not text or not text.strip():
            logger.warning("🔇 Aucun texte transcrit")
            self.speak_response("Désolé, je n’ai pas compris votre message.")
            return

        logger.info(f"📝 Texte transcrit: {text}")

        # Si le texte n’est pas en français, on relance la transcription
        if not self._is_french_text(text):
            logger.warning(f"⚠️ Texte transcrit ne semble pas être en français: {text}")
            # On ne relance pas la transcription ici pour éviter un loop infini
            # On passe directement à la génération de réponse
        # Générer la réponse (GPU)
        future_llm = self._transcribe_executor.submit(
            self.process_user_message, text
        )
        future_llm.add_done_callback(self._handle_llm_response)

    # ------------------------------------------------------------------
    # Gestion du résultat de la LLM
    # ------------------------------------------------------------------
    def _handle_llm_response(self, future):
        try:
            response = future.result()
        except Exception as e:
            logger.error(f"❌ Erreur LLM: {e}")
            response = "Désolé, je n’ai pas pu répondre."
        # Synthèse vocale (thread dédié)
        self._tts_executor.submit(self.speak_response, response)

    # ------------------------------------------------------------------
    # Optimisation de la mémoire GPU/CPU
    # ------------------------------------------------------------------
    def optimize_performance(self, aggressive: bool = False) -> bool:
        try:
            logger.info(f"⚡ Optimisation des performances {'agressive' if aggressive else 'normale'}")
            memory_success = self.performance_optimizer.optimize_memory(aggressive=aggressive)
            models_success = self.performance_optimizer.optimize_models()
            # Optimisations spécifiques aux services
            for service, method_name in [
                (self.speech_recognition_service, "optimize_model_cache"),
                (self.tts_service, "optimize_voice_cache"),
            ]:
                if hasattr(service, method_name):
                    getattr(service, method_name)()
            success = memory_success or models_success
            logger.info("✅ Optimisation terminée" if success else "✅ Pas d'optimisations nécessaires")
            return success
        except Exception as e:
            logger.error(f"❌ Erreur optimisation: {e}")
            return False

    # ------------------------------------------------------------------
    # Méthodes d’adaptation pour ConsoleView
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # Traitement d’un message utilisateur
    # ------------------------------------------------------------------
    def process_user_message(self, message: str) -> str:
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

    # ------------------------------------------------------------------
    # Synthèse vocale
    # ------------------------------------------------------------------
    def speak_response(self, text: str) -> bool:
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

    # ------------------------------------------------------------------
    # Interface console
    # ------------------------------------------------------------------
    def start_console_interface(self):
        try:
            logger.info("🖥️  Démarrage interface console...")
            if self.console_view is None:
                self._setup_console_view()
            if self.console_view:
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

    # ------------------------------------------------------------------
    # Interface web (Gradio)
    # ------------------------------------------------------------------
    def start_web_interface(self):
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
                        prevent_thread_lock=True,
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

    # ------------------------------------------------------------------
    # Boucle principale
    # ------------------------------------------------------------------
    @safe_run("AssistantVocal")
    def run(self):
        logger.info("🚀 Démarrage de l'assistant vocal")

        # ------------------------------------------------------------------
        # Configuration de PyTorch (GPU + CPU)
        # ------------------------------------------------------------------
        torch.backends.cudnn.benchmark = True
        torch.backends.cudnn.deterministic = False
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.set_num_threads(16)          # 16 cœurs CPU
        torch.set_num_interop_threads(8)   # 8 threads inter‑op

        # ------------------------------------------------------------------
        # Monitoring
        # ------------------------------------------------------------------
        self.performance_optimizer.start_monitoring()

        # ------------------------------------------------------------------
        # Affichage infos système
        # ------------------------------------------------------------------
        try:
            system_info = self.system_monitor.get_system_info_text()
            logger.info("📊 Informations système:")
            for line in system_info.split("\n"):
                if line.strip():
                    logger.info(line)
        except Exception as e:
            logger.warning(f"Impossible d'afficher les infos système: {e}")

        logger.info(f"Configuration: Voix={self.settings.voice_name}, Modèle={self.settings.llm_model}")

        # ------------------------------------------------------------------
        # Test du service LLM
        # ------------------------------------------------------------------
        logger.info("🧪 Test du service LLM...")
        if self.llm_service.test_service():
            logger.info("✅ Service LLM fonctionnel")
            test_messages = [{"role": "user", "content": "Bonjour, comment allez-vous ?"}]
            test_response = self.llm_service.generate_response(test_messages)
            logger.info(f"📝 Test réponse LLM: {test_response[:100]}...")
        else:
            logger.warning("⚠️ Service LLM non disponible")

        # ------------------------------------------------------------------
        # Callbacks Wake‑Word
        # ------------------------------------------------------------------
        self.wake_word_service.set_wake_word_callback(self._on_wake_word_detected)
        self.wake_word_service.set_audio_callback(self._on_audio_received)

        # ------------------------------------------------------------------
        # Démarrage des interfaces
        # ------------------------------------------------------------------
        if not self.start_web_interface():
            logger.warning("⚠️ Impossible de démarrer l'interface web")

        self.wake_word_service.start_detection(self.settings.microphone_index)

        # ------------------------------------------------------------------
        # Tests rapides
        # ------------------------------------------------------------------
        logger.info("🧪 Test de conversation...")
        test_response = self.process_user_message("Bonjour, comment allez-vous ?")
        logger.info(f"📝 Test réponse: {test_response}")

        logger.info("🧪 Test TTS...")
        if self.tts_service.test_synthesis():
            logger.info("✅ Service TTS fonctionnel")
            self.speak_response("Mario est opérationnel")
        else:
            logger.warning("⚠️ Service TTS non disponible")

        # ------------------------------------------------------------------
        # Interface console
        # ------------------------------------------------------------------
        self.start_console_interface()

        # ------------------------------------------------------------------
        # Boucle principale
        # ------------------------------------------------------------------
        self._is_running = True
        try:
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

    # ------------------------------------------------------------------
    # Méthodes utilitaires
    # ------------------------------------------------------------------
    def _is_french_text(self, text: str) -> bool:
        if not text or not text.strip():
            return False
        french_patterns = [
            r'\b(le|la|les|un|une|des|du|de|à|et|ou|mais|si|que|qui|quoi|où|quand|comment)\b',
            r'\b(je|tu|il|elle|nous|vous|ils|elles)\b',
            r'\b(suis|es|est|sommes|êtes|sont|ai|as|a|avons|avez|ont)\b',
            r'\b(de|dans|sur|sous|entre|avant|après|pendant|pour|par|avec|sans)\b',
        ]
        french_word_count = 0
        total_words = len(text.split())
        if total_words == 0:
            return False
        for pattern in french_patterns:
            matches = re.findall(pattern, text.lower())
            french_word_count += len(matches)
        return (french_word_count / total_words) > 0.1

    def get_optimization_profile(self) -> Dict:
        return self.performance_optimizer.get_optimization_profile()

    def set_optimization_profile(self, profile: Dict):
        self.performance_optimizer.set_optimization_profile(profile)

    def set_performance_thresholds(self, **thresholds):
        self.performance_optimizer.set_thresholds(**thresholds)

    def get_performance_status(self) -> Dict:
        return self.performance_optimizer.get_resource_usage()

    def use_custom_prompt(self, prompt_id: str, input_text: str, custom_vars: Dict = None) -> str:
        try:
            prompt = self.prompt_manager.get_prompt(prompt_id)
            if not prompt:
                return "[ERREUR] Prompt non trouvé"
            prompt_text = self.prompt_manager.generate_prompt_text(
                prompt["template"], input_text, custom_vars
            )
            messages = [{"role": "user", "content": prompt_text}]
            if prompt.get("system_message"):
                messages.insert(0, {"role": "system", "content": prompt["system_message"]})
            response = self.llm_service.generate_response(
                messages, temperature=prompt.get("temperature", 0.7)
            )
            return response
        except Exception as e:
            logger.error(f"Erreur utilisation prompt: {e}")
            return f"[ERREUR] {str(e)}"

    def analyze_project(self, project_path: str) -> Dict:
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

    def clear_conversation(self):
        self.conversation_service.clear_history()
        logger.info("Conversation effacée")

    def get_conversation_history(self):
        return self.conversation_service.get_history()

    def get_history(self):
        return self.conversation_service.get_history()

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

    def speak_response(self, text: str) -> bool:
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
        try:
            logger.info("🖥️  Démarrage interface console...")
            if self.console_view is None:
                self._setup_console_view()
            if self.console_view:
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
                        prevent_thread_lock=True,
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

    def run(self):
        # (déjà présent ci‑dessus – voir la version complète ci‑dessus)
        pass

    # ------------------------------------------------------------------
    # Méthodes internes de gestion de la mémoire GPU
    # ------------------------------------------------------------------
    def _clear_gpu_cache(self):
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()

    def _clear_cpu_cache(self):
        import gc
        gc.collect()

    # ------------------------------------------------------------------
    # Méthodes internes de gestion de la queue audio
    # ------------------------------------------------------------------
    def _prefetch_audio(self):
        # La queue est remplie par le callback _on_audio_received
        while self._is_running:
            time.sleep(0.01)

    # ------------------------------------------------------------------
    # Méthodes internes de gestion de la langue
    # ------------------------------------------------------------------
    def _is_french_text(self, text: str) -> bool:
        # (déjà présent ci‑dessus)
        pass

    # ------------------------------------------------------------------
    # Méthodes internes de gestion de la LLM
    # ------------------------------------------------------------------
    def _handle_llm_response(self, future):
        # (déjà présent ci‑dessus)
        pass

    # ------------------------------------------------------------------
    # Méthodes internes de gestion de la transcription
    # ------------------------------------------------------------------
    def _handle_transcription(self, future):
        # (déjà présent ci‑dessus)
        pass

    # ------------------------------------------------------------------
    # Méthodes internes de gestion du wake‑word
    # ------------------------------------------------------------------
    def _on_wake_word_detected(self):
        # (déjà présent ci‑dessus)
        pass

    # ------------------------------------------------------------------
    # Méthodes internes de gestion de l’audio reçu
    # ------------------------------------------------------------------
    def _on_audio_received(self, audio_data: bytes):
        # (déjà présent ci‑dessus)
        pass

    # ------------------------------------------------------------------
    # Méthodes internes de gestion de la console
    # ------------------------------------------------------------------
    def _setup_console_view(self):
        # (déjà présent ci‑dessus)
        pass

    # ------------------------------------------------------------------
    # Méthodes internes de gestion du nettoyage
    # ------------------------------------------------------------------
    def _cleanup(self):
        # (déjà présent ci‑dessus)
        pass

    # ------------------------------------------------------------------
    # Méthodes internes de gestion de la performance
    # ------------------------------------------------------------------
    def optimize_performance(self, aggressive: bool = False) -> bool:
        # (déjà présent ci‑dessus)
        pass

    # ------------------------------------------------------------------
    # Méthodes internes de gestion du profil d’optimisation
    # ------------------------------------------------------------------
    def get_optimization_profile(self) -> Dict:
        # (déjà présent ci‑dessus)
        pass

    def set_optimization_profile(self, profile: Dict):
        # (déjà présent ci‑dessus)
        pass

    def set_performance_thresholds(self, **thresholds):
        # (déjà présent ci‑dessus)
        pass

    def get_performance_status(self) -> Dict:
        # (déjà présent ci‑dessus)
        pass

    # ------------------------------------------------------------------
    # Méthodes internes de gestion de la conversation
    # ------------------------------------------------------------------
    def add_user_message(self, user_input: str):
        # (déjà présent ci‑dessus)
        pass

    def generate_response(self) -> str:
        # (déjà présent ci‑dessus)
        pass

    def play_tts_response(self, text: str):
        # (déjà présent ci‑dessus)
        pass

    def get_history(self):
        # (déjà présent ci‑dessus)
        pass

    def process_user_message(self, message: str) -> str:
        # (déjà présent ci‑dessus)
        pass

    def speak_response(self, text: str) -> bool:
        # (déjà présent ci‑dessus)
        pass

    def start_console_interface(self):
        # (déjà présent ci‑dessus)
        pass

    def start_web_interface(self):
        # (déjà présent ci‑dessus)
        pass

    def run(self):
        # (déjà présent ci‑dessus)
        pass

    def analyze_project(self, project_path: str) -> Dict:
        # (déjà présent ci‑dessus)
        pass

    def clear_conversation(self):
        # (déjà présent ci‑dessus)
        pass

    def get_conversation_history(self):
        # (déjà présent ci‑dessus)
        pass

    def use_custom_prompt(self, prompt_id: str, input_text: str, custom_vars: Dict = None) -> str:
        # (déjà présent ci‑dessus)
        pass

    # ------------------------------------------------------------------
    # Méthodes internes de gestion de la mémoire GPU
    # ------------------------------------------------------------------
    def _clear_gpu_cache(self):
        # (déjà présent ci‑dessus)
        pass

    def _clear_cpu_cache(self):
        # (déjà présent ci‑dessus)
        pass

    # ------------------------------------------------------------------
    # Méthodes internes de gestion de la queue audio
    # ------------------------------------------------------------------
    def _prefetch_audio(self):
        # (déjà présent ci‑dessus)
        pass

    # ------------------------------------------------------------------
    # Méthodes internes de gestion de la langue
    # ------------------------------------------------------------------
    def _is_french_text(self, text: str) -> bool:
        # (déjà présent ci‑dessus)
        pass

    # ------------------------------------------------------------------
    # Méthodes internes de gestion de la LLM
    # ------------------------------------------------------------------
    def _handle_llm_response(self, future):
        # (déjà présent ci‑dessus)
        pass

    # ------------------------------------------------------------------
    # Méthodes internes de gestion de la transcription
    # ------------------------------------------------------------------
    def _handle_transcription(self, future):
        # (déjà présent ci‑dessus)
        pass

    # ------------------------------------------------------------------
    # Méthodes internes de gestion du wake‑word
    # ------------------------------------------------------------------
    def _on_wake_word_detected(self):
        # (déjà présent ci‑dessus)
        pass

    # ------------------------------------------------------------------
    # Méthodes internes de gestion de l’audio reçu
    # ------------------------------------------------------------------
    def _on_audio_received(self, audio_data: bytes):
        # (déjà présent ci‑dessus)
        pass

    # ------------------------------------------------------------------
    # Méthodes internes de gestion de la console
    # ------------------------------------------------------------------
    def _setup_console_view(self):
        # (déjà présent ci‑dessus)
        pass

    # ------------------------------------------------------------------
    # Méthodes internes de gestion du nettoyage
    # ------------------------------------------------------------------
    def _cleanup(self):
        # (déjà présent ci‑dessus)
        pass

    # ------------------------------------------------------------------
    # Méthodes internes de gestion de la performance
    # ------------------------------------------------------------------
    def optimize_performance(self, aggressive: bool = False) -> bool:
        # (déjà présent ci‑dessus)
        pass

    # ------------------------------------------------------------------
    # Méthodes internes de gestion du profil d’optimisation
    # ------------------------------------------------------------------
    def get_optimization_profile(self) -> Dict:
        # (déjà présent ci‑dessus)
        pass

    def set_optimization_profile(self, profile: Dict):
        # (déjà présent ci‑dessus)
        pass

    def set_performance_thresholds(self, **thresholds):
        # (déjà présent ci‑dessus)
        pass

    def get_performance_status(self) -> Dict:
        # (déjà présent ci‑dessus)
        pass

    # ------------------------------------------------------------------
    # Méthodes internes de gestion de la conversation
    # ------------------------------------------------------------------
    def add_user_message(self, user_input: str):
        # (déjà présent ci‑dessus)
        pass

    def generate_response(self) -> str:
        # (déjà présent ci‑dessus)
        pass

    def play_tts_response(self, text: str):
        # (déjà présent ci‑dessus)
        pass

    def get_history(self):
        # (déjà présent ci‑dessus)
        pass

    def process_user_message(self, message: str) -> str:
        # (déjà présent ci‑dessus)
        pass

    def speak_response(self, text: str) -> bool:
        # (déjà présent ci‑dessus)
        pass

    def start_console_interface(self):
        # (déjà présent ci‑dessus)
        pass

    def start_web_interface(self):
        # (déjà présent ci‑dessus)
        pass

    def run(self):
        # (déjà présent ci‑dessus)
        pass

    def analyze_project(self, project_path: str) -> Dict:
        # (déjà présent ci‑dessus)
        pass

    def clear_conversation(self):
        # (déjà présent ci‑dessus)
        pass

    def get_conversation_history(self):
        # (déjà présent ci‑dessus)
        pass

    def use_custom_prompt(self, prompt_id: str, input_text: str, custom_vars: Dict = None) -> str:
        # (déjà présent ci‑dessus)
        pass

# ────────────────────────────────────────────────────────────────────────
# Fin de main.py
# ────────────────────────────────────────────────────────────────────────
