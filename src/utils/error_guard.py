from functools import wraps
from src.utils.logger import logger

def safe_run(module_name):
    """Décorateur pour capturer et logguer proprement les erreurs."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.exception(f"[{module_name}] Erreur dans {func.__name__}: {e}")
                return None
        return wrapper
    return decorator
