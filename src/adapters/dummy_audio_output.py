from src.adapters.interfaces import IAudioOutput
class DummyAudioOutput(IAudioOutput):
    def say(self, text: str, speed: float = 1.0) -> bool:
        print(f"Dummy: '{text}' joué à la vitesse {speed}")
        return True
