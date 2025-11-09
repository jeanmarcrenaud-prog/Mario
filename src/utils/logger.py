import logging
import os
import sys
import traceback
from logging.handlers import RotatingFileHandler
from functools import wraps

# ===============================================================
# Configuration de base du logger (sans dépendance sur config)
# ===============================================================
def setup_logger():
    """Configure le logger avec des valeurs par défaut."""
    # Créer le dossier logs dans le répertoire du projet
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    log_folder = os.path.join(project_root, "logs")
    os.makedirs(log_folder, exist_ok=True)
    log_file = os.path.join(log_folder, "app.log")
    
    # Configuration par défaut
    log_level = logging.INFO
    
    # Logger principal
    logger = logging.getLogger("AssistantVocal")
    logger.setLevel(log_level)
    logger.handlers.clear()
    
    # Handler fichier avec rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5 Mo
        backupCount=3,
        encoding="utf-8"
    )
    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] (%(threadName)s) %(name)s: %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Handler console
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger

# Créer une instance de logger
logger = setup_logger()

# ===============================================================
# Gestionnaire global des exceptions non interceptées
# ===============================================================
def handle_uncaught_exceptions(exc_type, exc_value, exc_traceback):
    """Capture les exceptions globales non gérées."""
    if issubclass(exc_type, KeyboardInterrupt):
        logger.info("Arrêt manuel du programme (Ctrl+C)")
        return
    logger.critical(
        "Exception non interceptée : %s\nTraceback:\n%s",
        exc_value,
        "".join(traceback.format_tb(exc_traceback)),
    )

sys.excepthook = handle_uncaught_exceptions

# ===============================================================
# Décorateur de sécurité pour fonctions critiques
# ===============================================================
def safe_run(module_name=""):
    """
    Décorateur qui capture les exceptions dans une fonction
    et les journalise sans interrompre le programme.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.exception("[%s] Erreur dans %s: %s", module_name, func.__name__, e)
                return None
        return wrapper
    return decorator

# ===============================================================
# Export
# ===============================================================
__all__ = ["logger", "safe_run", "setup_logger"]
