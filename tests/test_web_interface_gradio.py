"""
Test pour l'interface web Gradio de l'Assistant Vocal Intelligent
==============================================================
"""

import pytest
from unittest.mock import MagicMock, patch
from src.ui.web_interface_gradio import GradioWebInterface

@pytest.fixture
def mock_assistant_controller():
    mock_controller = MagicMock()
    mock_controller.settings.llm_model = "gpt-3.5-turbo"
    mock_controller.settings.voice_name = "default"
    return mock_controller

def test_gradio_web_interface_initialization(mock_assistant_controller):
    """Test l'initialisation de l'interface Gradio."""
    interface = GradioWebInterface(mock_assistant_controller)
    assert interface.assistant == mock_assistant_controller
    assert interface.demo is None
    assert interface.chat_history == []

@patch('gradio.Blocks')
def test_create_interface(mock_gr_blocks, mock_assistant_controller):
    """Test la création de l'interface Gradio."""
    interface = GradioWebInterface(mock_assistant_controller)
    interface.create_interface()
    assert interface.demo is not None

@patch.object(GradioWebInterface, '_handle_chat')
def test_handle_chat(mock_handle_chat, mock_assistant_controller):
    """Test la gestion du chat."""
    interface = GradioWebInterface(mock_assistant_controller)
    interface._handle_chat("Test message", 0.7)
    mock_handle_chat.assert_called_once()

@patch.object(GradioWebInterface, '_handle_file_analysis')
def test_handle_file_analysis(mock_handle_file_analysis, mock_assistant_controller):
    """Test la gestion de l'analyse de fichiers."""
    interface = GradioWebInterface(mock_assistant_controller)
    interface._handle_file_analysis("dummy_file_path")
    mock_handle_file_analysis.assert_called_once()
