"""
Tests unitaires pour TTSService.
"""

from src.services.tts_service import TTSService


class TestTTSService:
    """Tests pour TTSService."""
    
    def test_service_init(self):
        """Test l'initialisation de TTSService."""
        service = TTSService()
        assert service is not None
        assert service.is_available
    
    def test_speak_returns_bool(self):
        """Test que speak retourne un booléen."""
        service = TTSService()
        result = service.speak("Test")
        assert isinstance(result, bool)
    
    def test_get_available_voices_returns_list(self):
        """Test que get_available_voices retourne une liste."""
        service = TTSService()
        voices = service.get_available_voices()
        assert isinstance(voices, list)
