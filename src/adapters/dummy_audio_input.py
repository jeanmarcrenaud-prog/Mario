from src.adapters.interfaces import IAudioInput
class DummyAudioInput(IAudioInput):
    def record(self) -> bytes:
        # Retourne des données audio factices pour les tests
        return b"dummy_audio_data"
