import os
import shutil
from pathlib import Path

# Répertoire racine du projet
ROOT = Path(__file__).resolve().parent

# Dossiers à supprimer récursivement
CLEAN_DIRS = [
    "__pycache__",
    ".pytest_cache",
    "htmlcov",
    "logs",
    "build",
    "dist",
    ".eggs",
]

# Fichiers spécifiques à supprimer
CLEAN_FILES = [
    ".coverage",
    "coverage.xml",
    "pytestdebug.log",
    "debug.log",
]

# Extensions à supprimer dans tout le projet
CLEAN_EXTENSIONS = [
    ".pyc", ".pyo", ".pyd", ".log", ".tmp", ".bak",
]

def remove_path(path: Path):
    """Supprime un fichier ou dossier en silence."""
    try:
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
            print(f"🧹 Dossier supprimé : {path}")
        elif path.is_file():
            path.unlink(missing_ok=True)
            print(f"🧽 Fichier supprimé : {path}")
    except Exception as e:
        print(f"⚠️ Impossible de supprimer {path}: {e}")

def cleanup_project():
    """Nettoie le projet Mario de tous les fichiers temporaires et logs."""
    print("🧼 Nettoyage du projet Mario...")
    count = 0

    # Supprimer les dossiers et fichiers connus
    for item in CLEAN_DIRS:
        target = ROOT / item
        if target.exists():
            remove_path(target)
            count += 1

    for file_name in CLEAN_FILES:
        target = ROOT / file_name
        if target.exists():
            remove_path(target)
            count += 1

    # Supprimer récursivement les fichiers temporaires par extension
    for path in ROOT.rglob("*"):
        if path.suffix.lower() in CLEAN_EXTENSIONS:
            remove_path(path)
            count += 1

    print(f"✅ Nettoyage terminé ({count} éléments supprimés).")

if __name__ == "__main__":
    cleanup_project()
