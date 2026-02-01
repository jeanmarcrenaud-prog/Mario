from dataclasses import dataclass
from typing import Optional

@dataclass
class Settings:
    """Paramètres de l'assistant."""
    microphone_index: int = 0
    voice_name: str = "fr_FR-siwis-medium"
    llm_model: str = "qwen3-coder:latest"
    speech_speed: float = 1.0
    wake_word: str = "mario"
    web_port: int = 7860
    sample_rate: int = 16000
    openai_api_key: str = ""

    @classmethod
    def from_config(cls, config):
        """Crée une instance à partir de la configuration."""
        return cls(
            microphone_index=getattr(config, 'DEFAULT_MICROPHONE_INDEX', 0),
            voice_name=getattr(config, 'DEFAULT_VOICE', 'fr_FR-siwis-medium'),
            llm_model=getattr(config, 'DEFAULT_MODEL', 'gpt-3.5-turbo'),
            web_port=getattr(config, 'WEB_PORT', 7860),
            sample_rate=getattr(config, 'SAMPLE_RATE', 16000),
            openai_api_key=getattr(config, 'OPENAI_API_KEY', ''),
        )
