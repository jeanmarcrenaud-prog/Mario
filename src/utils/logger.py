import logging
import os
import sys
import traceback
from logging.handlers import RotatingFileHandler
from functools import wraps
from ..config import config

# ===============================================================
# Préparation du dossier log
# ===============================================================
os.makedirs(config.LOG_FOLDER, exist_ok=True)
LOG_FILE = os.path.join(config.LOG_FOLDER, "app.log")

# ===============================================================
# Définition du niveau de log depuis la config (str ou int)
# ===============================================================
raw_level = getattr(config, "LOG_LEVEL", "INFO")

# Accepte soit un int (ex: logging.INFO) soit une chaîne ("INFO")
if isinstance(raw_level, int):
    LOG_LEVEL = raw_level
else:
    try:
        LOG_LEVEL = getattr(logging, str(raw_level).upper(), logging.INFO)
    except Exception:
        print(f"[logger] Niveau de log invalide: {raw_level}, fallback INFO")
        LOG_LEVEL = logging.INFO

# Validation de la valeur finale
if LOG_LEVEL not in (
    logging.DEBUG,
    logging.INFO,
    logging.WARNING,
    logging.ERROR,
    logging.CRITICAL,
):
    print(f"[logger] Niveau de log inconnu: {LOG_LEVEL}, fallback INFO")
    LOG_LEVEL = logging.INFO

# ===============================================================
# Configuration du logger principal
# ===============================================================
logger = logging.getLogger("AssistantVocal")
logger.setLevel(LOG_LEVEL)
logger.handlers.clear()

# ---------------------------------------------------------------
# Handler fichier avec rotation
# ---------------------------------------------------------------
file_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=5 * 1024 * 1024,  # 5 Mo
    backupCount=3,
    encoding="utf-8"
)
file_formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] (%(threadName)s) %(name)s: %(message)s"
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# ---------------------------------------------------------------
# Handler console compatible Windows (UTF-8)
# ---------------------------------------------------------------
class WindowsSafeStreamHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            msg = self.format(record)
            if sys.platform == "win32":
                msg = self._replace_emojis(msg)
            stream = self.stream
            if hasattr(stream, "buffer"):
                stream.buffer.write(msg.encode("utf-8", errors="replace") + self.terminator.encode("utf-8"))
            else:
                stream.write(msg + self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)

    def _replace_emojis(self, text):
        """Remplace les emojis par du texte pour compatibilité Windows."""
        replacements = {
            "✅": "[OK]",
            "❌": "[ERREUR]",
            "⚠️": "[ATTENTION]",
            "🔄": "[CHARGEMENT]",
            "🎤": "[MICRO]",
            "🔊": "[AUDIO]",
            "🔔": "[ALERTE]",
            "🧹": "[NETTOYAGE]",
            "🎧": "[ECOUTE]",
            "⏹️": "[ARRET]",
            "🔇": "[SILENCE]",
            "📊": "[STATS]",
            "📁": "[FICHIER]",
            "🔧": "[OUTIL]",
            "⏰": "[TIMEOUT]",
            "🎯": "[CACHE]",
            "🌐": "[RESEAU]",
            "🔍": "[RECHERCHE]",
        }
        for emoji, rep in replacements.items():
            text = text.replace(emoji, rep)
        return text


console_handler = WindowsSafeStreamHandler()
console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

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
__all__ = ["logger", "safe_run"]
