import pytest
from unittest.mock import MagicMock, patch
from src.ui.interface import AssistantInterface


@pytest.fixture
def mock_dependencies():
    """Mock de toutes les dépendances externes pour éviter les effets réels."""
    with patch("src.ui.interface.WakeWordDetector") as mock_wake, \
         patch("src.ui.interface.SpeechRecognizer"), \
         patch("src.ui.interface.TextToSpeech"), \
         patch("src.ui.interface.AudioPlayer"), \
         patch("src.ui.interface.LLMClient"), \
         patch("src.ui.interface.FileAnalyzer"), \
         patch("src.ui.interface.InterfaceHelpers") as mock_helpers, \
         patch("src.ui.interface.AnalysisManager"):

        mock_wake_instance = MagicMock()
        mock_wake_instance.initialize_porcupine.return_value = True
        mock_wake_instance.is_running = False
        mock_wake.return_value = mock_wake_instance

        mock_helpers_instance = MagicMock()
        mock_helpers.return_value = mock_helpers_instance

        yield mock_wake_instance, mock_helpers_instance


def test_create_interface_gradio_safe(mock_dependencies):
    """Vérifie que l'interface Gradio peut être créée sans exécuter de code réel."""
    _, mock_helpers = mock_dependencies
    mock_helpers.get_theme.return_value = "default"

    # ⚠️ On mocke tous les sous-composants Gradio pour éviter la construction réelle
    with patch("src.ui.interface.gr.Blocks", MagicMock()) as mock_blocks, \
         patch("src.ui.interface.gr.Row", MagicMock()), \
         patch("src.ui.interface.gr.Column", MagicMock()), \
         patch("src.ui.interface.gr.Accordion", MagicMock()), \
         patch("src.ui.interface.gr.Markdown", MagicMock()), \
         patch("src.ui.interface.gr.Dropdown", MagicMock()), \
         patch("src.ui.interface.gr.Button", MagicMock()), \
         patch("src.ui.interface.gr.Textbox", MagicMock()), \
         patch("src.ui.interface.gr.File", MagicMock()), \
         patch("src.ui.interface.gr.Chatbot", MagicMock()), \
         patch("src.ui.interface.gr.Slider", MagicMock()):

        assistant = AssistantInterface()
        result = assistant.create_interface()
        assert result is not None
        mock_blocks.assert_called_once()

import gradio as gr

def test_setup_events():
    interface = AssistantInterface()

    # Initialisez les attributs avec des MagicMock
    interface.stop_btn = MagicMock()
    interface.restart_btn = MagicMock()
    interface.user_input = MagicMock()
    interface.file_upload = MagicMock()
    interface.analysis_btn = MagicMock()
    interface.send_to_ollama_btn = MagicMock()
    interface.ollama_dropdown = MagicMock()  # Ajout de ollama_dropdown
    interface.refresh_btn = MagicMock()
    interface.status_text = MagicMock()
    interface.chatbot = MagicMock()
    interface.analysis_path = MagicMock()
    interface.analysis_report = MagicMock()
    interface.analysis_summary = MagicMock()

    # Mock des méthodes Gradio
    interface.stop_btn.click = MagicMock()
    interface.restart_btn.click = MagicMock()
    interface.user_input.submit = MagicMock()
    interface.file_upload.change = MagicMock()
    interface.analysis_btn.click = MagicMock()
    interface.send_to_ollama_btn.click = MagicMock()
    interface.refresh_btn.click = MagicMock()

    # Mock des méthodes pour éviter les effets de bord
    with patch.object(interface, '_get_load_inputs', return_value=[]):
        with patch.object(interface, '_get_restart_inputs', return_value=[]):
            with patch.object(interface, '_get_chat_inputs', return_value=[]):
                # Appeler _setup_events
                interface._setup_events()

    # Vérifiez que les méthodes ont été appelées
    interface.stop_btn.click.assert_called_once()
    interface.restart_btn.click.assert_called_once()
    interface.user_input.submit.assert_called_once()
    interface.file_upload.change.assert_called_once()
    interface.analysis_btn.click.assert_called_once()
    interface.send_to_ollama_btn.click.assert_called_once()
    interface.refresh_btn.click.assert_called_once()

def test_handle_file_upload_invalid_file():
    interface = AssistantInterface()
    with patch.object(interface.analysis_manager, 'analyze_single_file', side_effect=ValueError("Fichier invalide")):
        chat_history, user_input = interface._handle_file_upload("chemin/vers/fichier_invalide.txt")
        assert len(chat_history) == 1
        assert "Erreur" in chat_history[0]["content"]
