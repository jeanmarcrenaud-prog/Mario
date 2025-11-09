import logging
from ..config.config import config

def configure_logger_with_config(logger):
    """Configure le logger avec les paramètres de config."""
    try:
        # Convertir le niveau de log
        raw_level = config.LOG_LEVEL
        if isinstance(raw_level, int):
            log_level = raw_level
        else:
            try:
                log_level = getattr(logging, str(raw_level).upper(), logging.INFO)
            except Exception:
                print(f"[logger] Niveau de log invalide: {raw_level}, fallback INFO")
                log_level = logging.INFO
        
        # Validation du niveau
        if log_level not in (
            logging.DEBUG,
            logging.INFO,
            logging.WARNING,
            logging.ERROR,
            logging.CRITICAL,
        ):
            print(f"[logger] Niveau de log inconnu: {log_level}, fallback INFO")
            log_level = logging.INFO
        
        # Appliquer le niveau
        logger.setLevel(log_level)
        
        # Configurer les handlers si nécessaire
        # (le logger est déjà configuré de base)
        
    except Exception as e:
        print(f"Erreur configuration logger: {e}")

# Export
__all__ = ["configure_logger_with_config"]
