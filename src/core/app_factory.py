"""
Factory pour la création de l'assistant vocal avec injection de dépendances.
Cette composition root sépare clairement l'assemblage des objets de la logique métier.
"""

from typing import Optional
from ..config.config import config
from ..models.settings import Settings
from ..utils.logger import logger
from ..utils.system_monitor import SystemMonitor

# Services principaux
from .conversation_service import ConversationService
from .tts_service import TTSService
from .wake_word_service import WakeWordService
from .speech_recognition_service import SpeechRecognitionService
from ..adapters.speech_recognition_whisper_adapter import WhisperSpeechRecognitionAdapter
from ..adapters.speech_recognition_simulated_adapter import SimulatedSpeechRecognitionAdapter
from .llm_service import LLMService
from .project_analyzer_service import ProjectAnalyzerService
from .performance_optimizer import PerformanceOptimizer
from .prompt_manager import PromptManager
from ..services.microphone_checker import MicrophoneChecker
# Vues
from ..views.web_interface_gradio import GradioWebInterface

# Modèle principal
from .main import AssistantVocal

def create_assistant() -> AssistantVocal:
    """
    Factory method pour créer un AssistantVocal complètement configuré.
    Cette fonction centralise l'assemblage de toutes les dépendances.
    
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
        logger.error("❌ Aucun microphone détecté. Impossible de démarrer le mode vocal.")
        raise RuntimeError("Microphone non disponible") 
        
    # 3. Services avec injection de dépendances
    tts_service = TTSService.create_with_piper(settings.voice_name)
    wake_word_service = WakeWordService.create_with_porcupine()
    speech_recognition_service = SpeechRecognitionService.create_with_whisper("base")
    llm_service = LLMService.create_with_ollama(settings.llm_model)
    
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

def create_assistant_with_simulation() -> AssistantVocal:
    """
    Factory method pour créer un AssistantVocal avec des services simulés.
    Utile pour les tests et le développement hors ligne.
    
    Returns:
        AssistantVocal: Instance avec services simulés
    """
    logger.info("🔧 Démarrage de la composition root (simulation)...")
    
    # 1. Configuration
    settings = Settings.from_config(config)
    
    # 2. Services de base
    conversation_service = ConversationService()
    prompt_manager = PromptManager()
    
    # 3. Services simulés
    tts_service = TTSService.create_with_piper(settings.voice_name)  # TTS réel pour les tests
    wake_word_service = WakeWordService.create_with_simulation()
    speech_recognition_service = SpeechRecognitionService.create_with_simulation()
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
    
    logger.info("✅ Assistant vocal simulé créé")
    return assistant

def create_minimal_assistant() -> AssistantVocal:
    """
    Factory method pour créer un AssistantVocal minimal.
    Utile pour les tests unitaires ou les environnements restreints.
    
    Returns:
        AssistantVocal: Instance minimale
    """
    logger.info("🔧 Démarrage de la composition root (minimal)...")
    
    # 1. Configuration minimale
    settings = Settings.from_config(config)
    
    # 2. Services de base uniquement
    conversation_service = ConversationService()
    prompt_manager = PromptManager()
    
    # 3. Services simulés
    tts_service = TTSService.create_with_simulation()
    wake_word_service = WakeWordService.create_with_simulation()
speech_recognition_service = create_speech_recognition_service_prod()
        llm_service = LLMService.create_with_simulation()
    
    # 4. Services dépendants
    project_analyzer_service = ProjectAnalyzerService(llm_service)
    
    # 5. Services système minimalistes
    system_monitor = SystemMonitor()
    performance_optimizer = PerformanceOptimizer()
    
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
    
    logger.info("✅ Assistant vocal minimal créé")
    return assistant



# Speech Recognition Service Factories

def create_speech_recognition_service_prod(model_name: str = "base") -> SpeechRecognitionService:
    """Factory pour créer un service STT avec Whisper (production)."""
    adapter = WhisperSpeechRecognitionAdapter(model_name=model_name)
    return SpeechRecognitionService(speech_recognition_adapter=adapter)


def create_speech_recognition_service_simulated(fake_result: str = "Bonjour, comment allez-vous ?") -> SpeechRecognitionService:
    """Factory pour créer un service STT avec simulation (développement/tests)."""
    adapter = SimulatedSpeechRecognitionAdapter(fake_result=fake_result)
    return SpeechRecognitionService(speech_recognition_adapter=adapter)
