import pytest
from unittest.mock import MagicMock
from src.ui.interface import AssistantInterface

@pytest.fixture
def mock_assistant(monkeypatch):
    """Crée un AssistantInterface avec tous les mocks nécessaires."""
    assistant = AssistantInterface.__new__(AssistantInterface)

    assistant.llm_client = MagicMock(name="LLMClient")
    assistant.tts = MagicMock(name="TextToSpeech")
    assistant.audio_player = MagicMock(name="AudioPlayer")

    assistant.chat_update_lock = MagicMock()
    assistant.chat_update_lock.__enter__ = lambda s: None
    assistant.chat_update_lock.__exit__ = lambda s, a, b, c: None

    # Historique simulé
    assistant.chat_history = []

    # ⚠️ Ne pas assigner chat_history_gradio — c’est une propriété
    # Mais on peut mocker son getter si nécessaire
    type(assistant).chat_history_gradio = property(lambda self: [
        (msg["role"], msg["content"]) for msg in self.chat_history
    ])

    # Helpers mockés
    assistant.helpers = MagicMock(name="InterfaceHelpers")
    assistant.helpers.generate_llm_response.return_value = "Bonjour, humain 👋"
    assistant.helpers.play_tts_response.return_value = None

    return assistant


def test_handle_user_message(mock_assistant):
    """Teste la logique complète de génération + TTS."""
    message = "Salut toi !"
    ollama_model = "mistral"
    piper_voice = "fr-FR-mario-medium"
    speed = 1.0

    history, _ = mock_assistant._handle_user_message(
        message, ollama_model, piper_voice, speed
    )

    # ✅ Vérifie que le helper de génération a bien été appelé
    mock_assistant.helpers.generate_llm_response.assert_called_once_with(
        mock_assistant.llm_client, ollama_model, mock_assistant.chat_history
    )

    # ✅ Vérifie que la réponse vocale est bien demandée
    mock_assistant.helpers.play_tts_response.assert_called_once_with(
        mock_assistant.tts, piper_voice, "Bonjour, humain 👋", speed, mock_assistant.audio_player
    )

    # ✅ Vérifie que l'historique du chat contient bien les deux messages
    assert len(mock_assistant.chat_history) == 2
    assert mock_assistant.chat_history[0]["role"] == "user"
    assert mock_assistant.chat_history[1]["role"] == "assistant"
    assert "humain" in mock_assistant.chat_history[1]["content"]
