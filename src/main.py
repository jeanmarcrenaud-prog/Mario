# ────────────────────────────────────────────────────────────────────────
# main.py
# AssistantVocal – version optimisée pour AMD Ryzen 9 9800X3D + RTX 5080
# ────────────────────────────────────────────────────────────────────────

import sys
import re
import atexit
import time
import torch
from typing import Dict, Optional

from src.config.config import ConfigManager, config
from src.utils.logger import logger, safe_run
from src.utils.system_monitor import SystemMonitor
from src.models.settings import Settings
from src.services.conversation_service import ConversationService
from src.services.tts_service import TTSService
from src.services.wake_word_service import WakeWordService
from src.services.speech_recognition_service import SpeechRecognitionService
from src.services.llm_service import LLMService
from src.services.project_analyzer_service import ProjectAnalyzerService
from src.core.performance_optimizer import PerformanceOptimizer
from src.core.prompt_manager import PromptManager
from src.core.audio_pipeline import AudioPipeline
from src.core.conversation_handler import ConversationHandler
from src.core.interface_manager import InterfaceManager


class AssistantVocal:
    """
    Assistant vocal principal.
    Utilise des modules séparés pour l'audio, la conversation et les interfaces.
    """

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

        self._is_running = False

        self.audio_pipeline = AudioPipeline(
            wake_word_service,
            speech_recognition_service,
            tts_service,
            settings,
        )

        self.conversation_handler = ConversationHandler(
            conversation_service,
            llm_service,
        )

        self.interface_manager = InterfaceManager(self, settings)

        self._setup_callbacks()
        self._setup_cleanup()
        logger.info("AssistantVocal initialisé avec modules séparés")

    def _setup_callbacks(self):
        """Configure les callbacks entre les modules"""
        self.audio_pipeline.set_wake_word_callback(self._on_wake_word)
        self.audio_pipeline.set_transcription_callback(self._on_transcription)

    def _on_wake_word(self):
        """Called when wake-word is detected"""
        logger.info("Wake-word détecté")
        self.speak("Je vous écoute")

    def _on_transcription(self, text: str):
        """Called when transcription is ready"""
        logger.info(f"Transcription: {text}")
        if not self._is_french_text(text):
            logger.warning(f"Texte，可能不是 français: {text}")
        response = self.conversation_handler.process_message(text)
        self.speak(response)

    def _setup_cleanup(self):
        atexit.register(self._cleanup)

    def _cleanup(self):
        if not self._is_running:
            return
        logger.info("Nettoyage des ressources...")
        self._is_running = False
        if hasattr(self, 'audio_pipeline'):
            self.audio_pipeline.stop()
        self.performance_optimizer.stop_monitoring()

    def speak(self, text: str) -> bool:
        """Synthétise et joue le texte"""
        if not text or not text.strip():
            return False
        self.interface_manager.display_message(f"Assistant: {text}")
        return self.audio_pipeline.speak(text)

    def speak_response(self, text: str) -> bool:
        """Alias pour speak"""
        return self.speak(text)

    def process_user_message(self, message: str) -> str:
        """Traite un message utilisateur"""
        return self.conversation_handler.process_message(message)

    def add_user_message(self, user_input: str):
        self.conversation_service.add_message("user", user_input)

    def generate_response(self) -> str:
        return self.conversation_handler.process_message("")

    def play_tts_response(self, text: str):
        self.speak(text)

    def get_history(self):
        return self.conversation_handler.get_history()

    def optimize_performance(self, aggressive: bool = False) -> bool:
        try:
            logger.info(f"Optimisation des performances {'agressive' if aggressive else 'normale'}")
            memory_success = self.performance_optimizer.optimize_memory(aggressive=aggressive)
            models_success = self.performance_optimizer.optimize_models()
            self.audio_pipeline.optimize_performance(aggressive)
            success = memory_success or models_success
            logger.info("Optimisation terminée" if success else "Pas d'optimisations nécessaires")
            return success
        except Exception as e:
            logger.error(f"Erreur optimisation: {e}")
            return False

    def start_console_interface(self) -> bool:
        return self.interface_manager.start_console()

    def start_web_interface(self) -> bool:
        return self.interface_manager.start_web()

    @safe_run("AssistantVocal")
    def run(self):
        logger.info("Démarrage de l'assistant vocal")

        torch.backends.cudnn.benchmark = True
        torch.backends.cudnn.deterministic = False
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.set_num_threads(16)
        torch.set_num_interop_threads(8)

        self.performance_optimizer.start_monitoring()

        try:
            system_info = self.system_monitor.get_system_info_text()
            logger.info("Informations système:")
            for line in system_info.split("\n"):
                if line.strip():
                    logger.info(line)
        except Exception as e:
            logger.warning(f"Impossible d'afficher les infos système: {e}")

        logger.info(f"Configuration: Voix={self.settings.voice_name}, Modèle={self.settings.llm_model}")

        logger.info("Test du service LLM...")
        if self.conversation_handler.test_llm():
            logger.info("Service LLM fonctionnel")
            test_messages = [{"role": "user", "content": "Bonjour, comment allez-vous ?"}]
            test_response = self.llm_service.generate_response(test_messages)
            logger.info(f"Test réponse LLM: {test_response[:100]}...")
        else:
            logger.warning("Service LLM non disponible")

        self.audio_pipeline.start()

        if not self.start_web_interface():
            logger.warning("Impossible de démarrer l'interface web")

        logger.info("Test de conversation...")
        test_response = self.process_user_message("Bonjour, comment allez-vous ?")
        logger.info(f"Test réponse: {test_response}")

        logger.info("Test TTS...")
        if self.tts_service.test_synthesis():
            logger.info("Service TTS fonctionnel")
            self.speak("Mario est opérationnel")
        else:
            logger.warning("Service TTS non disponible")

        self.start_console_interface()

        self._is_running = True
        try:
            while self._is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Arrêt manuel par l'utilisateur")
        except Exception as e:
            logger.critical(f"Erreur fatale dans run(): {e}")
            import traceback
            logger.error(traceback.format_exc())
        finally:
            self._cleanup()
            logger.info("Assistant arrêté proprement")

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

    def use_custom_prompt(self, prompt_id: str, input_text: str, custom_vars: Optional[Dict] = None) -> str:
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
            logger.info(f"Analyse du projet: {project_path}")
            report = self.project_analyzer_service.analyze_project(project_path)
            summary = report.get("summary", "Analyse terminée")
            self.speak(f"Analyse du projet terminée. {summary}")
            return report
        except Exception as e:
            logger.error(f"Erreur analyse projet: {e}")
            error_msg = f"Erreur analyse projet: {str(e)}"
            self.speak(error_msg)
            return {"error": error_msg}

    def clear_conversation(self):
        self.conversation_handler.clear_history()

    def get_conversation_history(self):
        return self.conversation_handler.get_history()


# ────────────────────────────────────────────────────────────────────────
# Fin de main.py
# ────────────────────────────────────────────────────────────────────────
