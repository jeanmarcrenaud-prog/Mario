from __future__ import annotations
from typing import Any, Protocol


class ISpeechRecognitionAdapter(Protocol):
    """Port for speech recognition adapters."""

    def load_model(self) -> None:
        """Load the speech recognition model."""
        ...

    def unload_model(self) -> None:
        """Unload the speech recognition model to free resources."""
        ...

    def transcribe_array(self, audio: Any, **kwargs: Any) -> str:
        """Transcribe audio from a numpy array."""
        ...

    def transcribe_file(self, path: str, **kwargs: Any) -> str:
        """Transcribe audio from a file."""
        ...

    def get_available_models(self) -> list[str]:
        """Return the list of available models."""
        ...
