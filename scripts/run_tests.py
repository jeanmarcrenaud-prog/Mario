import sys
import pathlib
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / "src"))

if __name__ == "__main__":
    pytest.main(["-v", "--color=yes", "--maxfail=3"])
