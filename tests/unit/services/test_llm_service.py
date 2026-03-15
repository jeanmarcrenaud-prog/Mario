"""
Tests unitaires pour LLMService.
"""

import pytest
from src.services.llm_service import LLMService


class TestLLMService:
    """Tests pour LLMService."""
    
    def test_detect_and_create_returns_service(self):
        """Test que detect_and_create retourne un service."""
        service = LLMService.detect_and_create()
        assert service is not None
    
    def test_get_service_info_returns_dict(self):
        """Test que get_service_info retourne un dict."""
        service = LLMService.detect_and_create()
        info = service.get_service_info()
        assert isinstance(info, dict)
        assert 'service_type' in info
