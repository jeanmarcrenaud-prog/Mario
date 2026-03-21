"""
Tests for app_factory module
"""


def test_app_factory_imports():
    """Test que les imports fonctionnent."""
    from src.core.app_factory import (
        create_assistant,
        AssistantVocal,
        ConversationService,
        GradioWebInterface,
        LLMService,
        MicrophoneChecker,
        PerformanceOptimizer,
        ProjectAnalyzerService,
        PromptManager,
        SpeechRecognitionService,
        TTSService,
        WakeWordService,
    )
    
    assert create_assistant is not None
    assert AssistantVocal is not None
    assert ConversationService is not None
    assert GradioWebInterface is not None
    assert LLMService is not None
    assert MicrophoneChecker is not None
    assert PerformanceOptimizer is not None
    assert ProjectAnalyzerService is not None
    assert PromptManager is not None
    assert SpeechRecognitionService is not None
    assert TTSService is not None
    assert WakeWordService is not None


def test_create_assistant_is_callable():
    """Test que create_assistant est callable."""
    from src.core.app_factory import create_assistant
    
    assert callable(create_assistant)
