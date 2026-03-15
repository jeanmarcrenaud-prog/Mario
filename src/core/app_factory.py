"""
Factory pour la création de l'assistant vocal avec injection de dépendances.
Cette composition root sépare clairement l'assemblage des objets de la logique métier.
"""

from typing import Optional, Any
from src.config.config import config
from src.models.settings import Settings
from src.utils.logger import logger
from src.utils.system_monitor import SystemMonitor

# Services principaux
from src.services.conversation_service import ConversationService
from src.services.tts_service import TTSService
from src.services.wake_word_service import WakeWordService
from src.services.speech_recognition_service import SpeechRecognitionService
from src.adapters.speech_recognition_whisper_adapter import WhisperSpeechRecognitionAdapter
from src.services.llm_service import LLMService
from src.services.project_analyzer_service import ProjectAnalyzerService
from src.core.performance_optimizer import PerformanceOptimizer
from src.core.prompt_manager import PromptManager
from src.interfaces.microphone_checker import MicrophoneChecker
# Vues
from src.views.web_interface_gradio import GradioWebInterface

# Modèle principal
from src.main import AssistantVocal


class AppFactory:
    """Factory class pour créer et configurer l'assistant vocal."""
    
    def __init__(self):
        """Initialise l'AppFactory avec les services de base."""
        pass
    
    def create(self, settings: Settings) -> AssistantVocal:
        """
        Crée une instance configurée de l'assistant vocal.
        
        Args:
            settings: Configuration de l'assistant
            
        Returns:
            AssistantVocal: Instance configurée
        """
        logger.info("🔧 Démarrage de la composition root...")
        
        # 1. Services de base
        conversation_service = ConversationService()
        prompt_manager = PromptManager()
        
        # Vérification du microphone
        mic_checker = MicrophoneChecker()
        if not mic_checker.is_microphone_available():
            logger.error("❌ Aucun microphone détecté.")
            raise RuntimeError("Microphone non disponible") 
            
        # 2. Services
        tts_service = TTSService.create_with_piper(settings.voice_name)
        wake_word_service = WakeWordService.create_with_vosk()
        speech_recognition_service = create_speech_recognition_service()
        
        # 3. Détection et création automatique du service LLM
        llm_service = LLMService.detect_and_create()
        
        # 3. Services dépendants
        llm_adapter = llm_service.llm_adapter if llm_service and llm_service.llm_adapter else None
        if not llm_adapter:
            from src.services.llm_service import SimulatedLLMAdapter
            llm_adapter = SimulatedLLMAdapter()
        project_analyzer_service = ProjectAnalyzerService(llm_adapter)
        
        # 4. Services système
        system_monitor = SystemMonitor()
        
        # 5. Rafraîchir les modèles LLM au démarrage
        logger.info("=== Rafraîchissement des modèles LLM au démarrage ===")
        llm_info = system_monitor.refresh_llm_models()
        if llm_info.get("service_type") not in ["error", "none"]:
            logger.info(f"✅ Service LLM actif: {llm_info['service_type']}")
            logger.info(f"🤖 Modèle utilisé: {llm_info['active_model']}")
            logger.info(f"📊 Total modèles: {llm_info['total_models']}")
        else:
            logger.warning("⚠️  Aucun service LLM détecté")
        
        performance_optimizer = PerformanceOptimizer()
        
        # 6. Démarrer le monitoring
        performance_optimizer.start_monitoring()
        
        # 6. Créer l'instance de l'assistant
        assistant = AssistantVocal(
            settings=settings,
            conversation_service=conversation_service,
            prompt_manager=prompt_manager,
            tts_service=tts_service,
            wake_word_service=wake_word_service,
            speech_recognition_service=speech_recognition_service,
            llm_service=llm_service,
            project_analyzer_service=project_analyzer_service,
            system_monitor=system_monitor,
            performance_optimizer=performance_optimizer
        )
        
        logger.info("✅ Assistant vocal créé avec injection de dépendances")
        return assistant


def create_assistant() -> AssistantVocal:
    """
    Factory method pour créer un AssistantVocal complètement configuré.
    
    Returns:
        AssistantVocal: Instance configurée et prête à l'emploi
    """
    logger.info("🔧 Démarrage de la composition root...")
    
    # 1. Configuration
    settings = Settings.from_config(config)
    
    # 2. Services de base
    conversation_service = ConversationService()
    prompt_manager = PromptManager()
    
    # Vérification du microphone
    mic_checker = MicrophoneChecker()
    if not mic_checker.is_microphone_available():
        logger.error("❌ Aucun microphone détecté.")
        raise RuntimeError("Microphone non disponible") 
        
    # 3. Services
    tts_service = TTSService.create_with_piper(settings.voice_name)
    wake_word_service = WakeWordService.create_with_simulation()
    speech_recognition_service = create_speech_recognition_service()
    llm_service = LLMService.create_with_simulation()
    
    # 4. Services dépendants
    project_analyzer_service = ProjectAnalyzerService(llm_service)
    
    # 5. Services système
    system_monitor = SystemMonitor()
    performance_optimizer = PerformanceOptimizer()
    
    # 6. Démarrer le monitoring
    performance_optimizer.start_monitoring()
    
    # 7. Créer l'instance de l'assistant
    assistant = AssistantVocal(
        settings=settings,
        conversation_service=conversation_service,
        prompt_manager=prompt_manager,
        tts_service=tts_service,
        wake_word_service=wake_word_service,
        speech_recognition_service=speech_recognition_service,
        llm_service=llm_service,
        project_analyzer_service=project_analyzer_service,
        system_monitor=system_monitor,
        performance_optimizer=performance_optimizer
    )
    
    logger.info("✅ Assistant vocal créé avec injection de dépendances")
    return assistant

# Speech Recognition Service Factory

def create_speech_recognition_service(model_name: str = "base") -> SpeechRecognitionService:
    """Factory pour créer un service STT avec Whisper."""
    adapter = WhisperSpeechRecognitionAdapter(model_name=model_name)
    return SpeechRecognitionService(speech_recognition_adapter=adapter)


def create_assistant_with_simulation() -> AssistantVocal:
    """
    Factory method pour créer un AssistantVocal avec simulation LLM.
    
    Returns:
        AssistantVocal: Instance configurée avec simulation
    """
    logger.info("🔧 Création de l'assistant avec simulation...")
    
    settings = Settings.from_config(config)
    conversation_service = ConversationService()
    prompt_manager = PromptManager()
    
    mic_checker = MicrophoneChecker()
    if not mic_checker.is_microphone_available():
        logger.error("❌ Aucun microphone détecté.")
        raise RuntimeError("Microphone non disponible")
        
    tts_service = TTSService.create_with_piper(settings.voice_name)
    wake_word_service = WakeWordService.create_with_simulation()
    speech_recognition_service = create_speech_recognition_service()
    
    llm_service = LLMService.detect_and_create()
    if not llm_service:
        from src.services.llm_service import SimulatedLLMAdapter
        llm_adapter = SimulatedLLMAdapter()
    else:
        llm_adapter = llm_service.llm_adapter if llm_service and llm_service.llm_adapter else None
        if not llm_adapter:
            from src.services.llm_service import SimulatedLLMAdapter
            llm_adapter = SimulatedLLMAdapter()
    
    project_analyzer_service = ProjectAnalyzerService(llm_adapter)
    system_monitor = SystemMonitor()
    performance_optimizer = PerformanceOptimizer()
    performance_optimizer.start_monitoring()
    
    assistant = AssistantVocal(
        settings=settings,
        conversation_service=conversation_service,
        prompt_manager=prompt_manager,
        tts_service=tts_service,
        wake_word_service=wake_word_service,
        speech_recognition_service=speech_recognition_service,
        llm_service=llm_service,
        project_analyzer_service=project_analyzer_service,
        system_monitor=system_monitor,
        performance_optimizer=performance_optimizer
    )
    
    logger.info("✅ Assistant avec simulation créé")
    return assistant


def create_minimal_assistant() -> AssistantVocal:
    """
    Factory method pour créer un AssistantVocal minimaliste.
    
    Returns:
        AssistantVocal: Instance minimale configurée
    """
    logger.info("🔧 Création de l'assistant minimal...")
    
    settings = Settings.from_config(config)
    conversation_service = ConversationService()
    prompt_manager = PromptManager()
    
    mic_checker = MicrophoneChecker()
    if not mic_checker.is_microphone_available():
        logger.error("❌ Aucun microphone détecté.")
        raise RuntimeError("Microphone non disponible")
        
    tts_service = TTSService.create_with_piper(settings.voice_name)
    speech_recognition_service = create_speech_recognition_service()
    
    llm_service = LLMService.detect_and_create()
    if not llm_service:
        from src.services.llm_service import SimulatedLLMAdapter
        llm_adapter = SimulatedLLMAdapter()
    else:
        llm_adapter = llm_service.llm_adapter if llm_service and llm_service.llm_adapter else None
        if not llm_adapter:
            from src.services.llm_service import SimulatedLLMAdapter
            llm_adapter = SimulatedLLMAdapter()
    
    project_analyzer_service = ProjectAnalyzerService(llm_adapter)
    system_monitor = SystemMonitor()
    
    assistant = AssistantVocal(
        settings=settings,
        conversation_service=conversation_service,
        prompt_manager=prompt_manager,
        tts_service=tts_service,
        wake_word_service=None,
        speech_recognition_service=speech_recognition_service,
        llm_service=llm_service,
        project_analyzer_service=project_analyzer_service,
        system_monitor=system_monitor,
        performance_optimizer=None
    )
    
    logger.info("✅ Assistant minimal créé")
    return assistant
