import os
import sys
from pathlib import Path

def test_import_structure():
    """Test that the core packages can be imported without errors."""
    import src.main  # should succeed
    import src.services
    import src.adapters
    import src.controllers
    import src.interfaces
    assert True
