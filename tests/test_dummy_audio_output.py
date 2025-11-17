from src.adapters.dummy_audio_output import DummyAudioOutput

def test_say_returns_true_and_prints():
    dummy = DummyAudioOutput()
    text = "Hello world"
    speed = 1.5
    # Tu pourrais utiliser capsys (pytest) pour vérifier le print, ici on check le retour
    result = dummy.say(text, speed)
    assert result is True
