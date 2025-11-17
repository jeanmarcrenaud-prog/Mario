from src.adapters.dummy_audio_input import DummyAudioInput

def test_record_returns_dummy_data():
    dummy = DummyAudioInput()
    data = dummy.record()
    assert isinstance(data, bytes)
    assert data == b"dummy_audio_data"
