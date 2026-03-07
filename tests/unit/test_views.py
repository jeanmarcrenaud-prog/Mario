"""
Tests pour les views et l'initialisation
"""
import pytest


class TestConsoleView:
    """Tests complets pour la console view."""
    
    @pytest.fixture
    def mock_assistant(self):
        """Mock assistant pour les tests."""
        assistant = Mock()
        assistant.settings.microphone_index = 1
        assistant.settings.voice_name = "fr_FR-siwis-medium"
        assistant.settings.llm_model = "qwen3-coder"
        
        return assistant
    
    def test_console_view_import(self):
        """Test d'import de ConsoleView."""
        from src.views.console_view import ConsoleView
        
        assert ConsoleView is not None
    
    def test_console_view_init(self, mock_assistant):
        """Test d'initialisation de ConsoleView."""
        from src.views.console_view import ConsoleView
        
        view = ConsoleView(mock_assistant)
        
        assert view is not None
        assert view.assistant is mock_assistant
    
    def test_display_message(self, mock_assistant):
        """Test d'affichage de message."""
        from src.views.console_view import ConsoleView
        
        view = ConsoleView(mock_assistant)
        
        view.display_message("Test message")
        
        # Vérifie que l'affichage a été appelé
        assert view.display_message.called


class TestWelcomeScreen:
    """Tests pour l'écran d'accueil."""
    
    def test_show_welcome_screen(self, tmp_path):
        """Test d'affichage de l'écran d'accueil."""
        from src.views.welcome_screen import show_welcome_screen
        
        # Mock console
        with patch('src.views.welcome_screen.console') as mock_console:
            show_welcome_screen(tmp_path)
            
            assert mock_console.print.called
    
    def test_show_main_menu(self, tmp_path):
        """Test de menu principal."""
        from src.views.welcome_screen import show_main_menu
        
        with patch('src.views.welcome_screen.console') as mock_console:
            show_main_menu(tmp_path)
            
            assert mock_console.print.called


class TestAnalysisManager:
    """Tests complets pour le gestionnaire d'analyse."""
    
    def test_analysis_manager_import(self):
        """Test d'import de AnalysisManager."""
        from src.views.analysis_manager import AnalysisManager
        
        assert AnalysisManager is not None
    
    def test_analysis_manager_init(self):
        """Test d'initialisation de AnalysisManager."""
        from src.views.analysis_manager import AnalysisManager
        
        manager = AnalysisManager()
        
        assert manager is not None
    
    def test_analyze_file(self):
        """Test d'analyse de fichier."""
        from src.views.analysis_manager import AnalysisManager
        
        manager = AnalysisManager()
        
        # Mock analyzer
        with patch('src.views.analysis_manager.analyze_file') as mock_analyze:
            mock_analyze.return_value = "Analyse terminée"
            
            result = manager.analyze_file("test.txt")
            
            assert mock_analyze.called


class TestEpaperview:
    """Tests pour la vue ePaper."""
    
    def test_epaper_view_import(self):
        """Test d'import de EpaperView."""
        from src.views.epaper_view import EpaperView
        
        assert EpaperView is not None
    
    def test_epaper_view_init(self, tmp_path):
        """Test d'initialisation de EpaperView."""
        from src.views.epaper_view import EpaperView
        
        view = EpaperView(tmp_path)
        
        assert view is not None


class TestInterfaceHelpers:
    """Tests pour les helpers d'interface."""
    
    def test_interface_helpers_import(self):
        """Test d'import de InterfaceHelpers."""
        from src.views.interface_helpers import InterfaceHelpers
        
        helpers = InterfaceHelpers()
        
        assert helpers is not None
    
    def test_format_message(self):
        """Test de formatage de message."""
        from src.views.interface_helpers import InterfaceHelpers
        
        helpers = InterfaceHelpers()
        
        # Test format message
        formatted = helpers.format_message("Hello World")
        
        assert formatted is not None


# Tests d'initialisation complète
class TestAppInitialization:
    """Tests de l'initialisation complète de l'app."""
    
    @pytest.fixture
    def mock_configs(self):
        """Mock configurations pour tests."""
        configs = Mock()
        configs.DEFAULT_MICROPHONE_INDEX = 1
        configs.DEFAULT_VOICE = "fr_FR-siwis-medium"
        configs.DEFAULT_MODEL = "qwen3-coder"
        configs.WEB_PORT = 7860
        configs.SAMPLE_RATE = 16000
        
        return configs
    
    def test_app_factory_import(self):
        """Test d'import de AppFactory."""
        from src.core.app_factory import AppFactory
        
        assert AppFactory is not None
    
    def test_app_factory_create(self, mock_configs):
        """Test de création d'app via factory."""
        from src.core.app_factory import AppFactory
        
        # Setup mocks
        with patch('src.core.app_factory.ConversationService') as mock_conv_service_cls:
            with patch('src.core.app_factory.TTSService') as mock_tts_service_cls:
                with patch('src.core.app_factory.WakeWordService') as mock_wake_service_cls:
                    with patch('src.core.app_factory.SpeechRecognitionService') as mock_speech_service_cls:
                        with patch('src.core.app_factory.LLMService') as mock_llm_service_cls:
                            with patch('src.core.app_factory.SystemMonitor') as mock_system_monitor_cls:
                                with patch('src.core.app_factory.AudioPipeline') as mock_audio_pipeline_cls:
                                    with patch('src.core.app_factory.ConversationHandler') as mock_conv_handler_cls:
                                        with patch('src.core.app_factory.PromptManager') as mock_prompt_manager_cls:
                                            with patch('src.core.app_factory.GradioWebInterface') as mock_interface_manager_cls:
                                                
                                                # Create mocks instances
                                                mock_conv_service_instance = Mock()
                                                mock_tts_service_instance = Mock()
                                                mock_wake_service_instance = Mock()
                                                mock_speech_service_instance = Mock()
                                                mock_llm_service_instance = Mock()
                                                mock_system_monitor_instance = Mock()
                                                mock_audio_pipeline_instance = Mock()
                                                mock_conv_handler_instance = Mock()
                                                mock_prompt_manager_instance = Mock()
                                                mock_interface_manager_instance = Mock()
                                                
                                                mock_conv_service_cls.return_value = mock_conv_service_instance
                                                mock_tts_service_cls.return_value = mock_tts_service_instance
                                                mock_wake_service_cls.return_value = mock_wake_service_instance
                                                mock_speech_service_cls.return_value = mock_speech_service_instance
                                                mock_llm_service_cls.return_value = mock_llm_service_instance
                                                mock_system_monitor_cls.return_value = mock_system_monitor_instance
                                                mock_audio_pipeline_cls.return_value = mock_audio_pipeline_instance
                                                mock_conv_handler_cls.return_value = mock_conv_handler_instance
                                                mock_prompt_manager_cls.return_value = mock_prompt_manager_instance
                                                mock_interface_manager_cls.return_value = mock_interface_manager_instance
                                                
                                                factory = AppFactory()
                                                
                                                app = factory.create(mock_configs)
                                                
                                                assert app is not None
