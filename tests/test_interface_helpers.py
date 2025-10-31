# tests/test_interface_helpers.py
import pytest
from src.ui.interface_helpers import InterfaceHelpers

class TestInterfaceHelpers:
    """Tests for InterfaceHelpers"""
    
    def test_initialization(self):
        """Test InterfaceHelpers initialization"""
        helpers = InterfaceHelpers()
        assert helpers is not None
    
    def test_format_file_size(self):
        """Test file size formatting"""
        helpers = InterfaceHelpers()
        
        # Test various sizes
        assert helpers.format_file_size(1024) == "1.0 KB"
        assert helpers.format_file_size(1048576) == "1.0 MB"
        assert helpers.format_file_size(1073741824) == "1.0 GB"
    
    def test_truncate_text(self):
        """Test text truncation"""
        helpers = InterfaceHelpers()
        
        long_text = "A" * 100
        truncated = helpers.truncate_text(long_text, 50)
        
        assert len(truncated) <= 53  # Account for "..."
        assert "..." in truncated
    
    def test_sanitize_filename(self):
        """Test filename sanitization"""
        helpers = InterfaceHelpers()
        
        unsafe_name = "file/with\\invalid*chars?.txt"
        safe_name = helpers.sanitize_filename(unsafe_name)
        
        # Should remove or replace invalid characters
        assert "/" not in safe_name
        assert "\\" not in safe_name
        assert "*" not in safe_name
        assert "?" not in safe_name

