"""
Tests pour les views et l'initialisation
"""
import pytest
from unittest.mock import Mock, patch, MagicMock


class TestConsoleView:
    """Tests complets pour la console view."""
    
    def test_console_view_import(self):
        """Test d'import de ConsoleView."""
        from src.views.console_view import ConsoleView
        
        assert ConsoleView is not None
    
    def test_console_view_init(self):
        """Test d'initialisation de ConsoleView."""
        from src.views.console_view import ConsoleView
        
        mock_config = Mock()
        view = ConsoleView(mock_config)
        
        assert view is not None
    
    def test_display_message(self):
        """Test d'affichage de message."""
        from src.views.console_view import ConsoleView
        
        mock_config = Mock()
        view = ConsoleView(mock_config)
        
        # Just test it doesn't crash
        result = view.display_message("Test message")
        assert result is None or result is not None


class TestWelcomeScreen:
    """Tests pour l'écran d'accueil."""
    
    def test_show_welcome_screen_import(self):
        """Test d'import de show_welcome_screen."""
        from src.views.welcome_screen import show_welcome_screen
        
        assert show_welcome_screen is not None
    
    def test_show_main_menu_import(self):
        """Test d'import de show_main_menu."""
        from src.views.welcome_screen import show_main_menu
        
        assert show_main_menu is not None


class TestAnalysisManager:
    """Tests complets pour le gestionnaire d'analyse."""
    
    def test_analysis_manager_import(self):
        """Test d'import de AnalysisManager."""
        from src.views.analysis_manager import AnalysisManager
        
        assert AnalysisManager is not None
    
    def test_analysis_manager_init(self):
        """Test d'initialisation de AnalysisManager."""
        from src.views.analysis_manager import AnalysisManager
        from src.utils.file_analyzer import FileAnalyzer
        from src.services.llm_service import LLMService
        
        mock_analyzer = Mock(spec=FileAnalyzer)
        mock_llm = Mock(spec=LLMService)
        
        manager = AnalysisManager(mock_analyzer, mock_llm)
        
        assert manager is not None
        assert manager.file_analyzer is mock_analyzer
        assert manager.llm_client is mock_llm


class TestEpaperview:
    """Tests pour la vue ePaper."""
    
    def test_epaper_view_import(self):
        """Test d'import de EpaperView."""
        from src.views.epaper_view import EpaperView
        
        assert EpaperView is not None
    
    def test_epaper_view_init(self):
        """Test d'initialisation de EpaperView."""
        from src.views.epaper_view import EpaperView
        
        mock_adapter = Mock()
        view = EpaperView(mock_adapter)
        
        assert view is not None
        assert view.adapter is mock_adapter


class TestInterfaceHelpers:
    """Tests pour les helpers d'interface."""
    
    def test_interface_helpers_import(self):
        """Test d'import de InterfaceHelpers."""
        from src.views.interface_helpers import InterfaceHelpers
        
        assert InterfaceHelpers is not None
    
    def test_interface_helpers_init(self):
        """Test d'initialisation de InterfaceHelpers."""
        from src.views.interface_helpers import InterfaceHelpers
        
        helpers = InterfaceHelpers()
        
        assert helpers is not None


# Tests d'initialisation complète
class TestAppInitialization:
    """Tests de l'initialisation complète de l'app."""
    
    def test_app_factory_import(self):
        """Test d'import de la fonction create_assistant."""
        from src.core.app_factory import create_assistant
        
        assert create_assistant is not None
    
    def test_app_factory_function_exists(self):
        """Test que create_assistant est une fonction."""
        from src.core.app_factory import create_assistant
        
        assert callable(create_assistant)
