import sys
import os

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)


def main() -> int:
    from src.core.app_runner import run_application
    return run_application()


if __name__ == "__main__":
    raise SystemExit(main())