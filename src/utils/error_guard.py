from functools import wraps
from typing import Any, Callable, List, Dict
from ..utils.logger import logger
import traceback

class ErrorHandler:
    """Gestionnaire d'erreurs centralisé."""
    
    def __init__(self, module_name: str = "App"):
        self.module_name = module_name
        self.error_count = 0
        self.errors: List[Dict[str, Any]] = []
    
    def handle(self, error: Exception, context: str = "") -> None:
        """Capture et enregistre une erreur."""
        self.error_count += 1
        error_info = {
            "error": str(error),
            "type": type(error).__name__,
            "context": context,
            "traceback": traceback.format_exc()
        }
        self.errors.append(error_info)
        logger.error(f"[{self.module_name}] {context}: {error}")
    
    def get_errors(self) -> list:
        """Retourne la liste des erreurs."""
        return self.errors
    
    def clear_errors(self) -> None:
        """Efface les erreurs enregistrées."""
        self.errors.clear()
        self.error_count = 0

_global_error_handler = ErrorHandler("Global")

def get_error_handler() -> ErrorHandler:
    """Retourne le gestionnaire d'erreurs global."""
    return _global_error_handler

def safe_run(module_name: str = "App", return_on_error: Any = None, log_traceback: bool = True):
    """Décorateur pour capturer et logguer proprement les erreurs."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_traceback:
                    logger.exception(f"[{module_name}] Erreur dans {func.__name__}: {e}")
                else:
                    logger.error(f"[{module_name}] Erreur dans {func.__name__}: {e}")
                _global_error_handler.handle(e, f"{func.__module__}.{func.__name__}")
                return return_on_error
        return wrapper
    return decorator

def retry(max_attempts: int = 3, delay: float = 1.0):
    """Décorateur pour réessayer une fonction en cas d'erreur."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:  # noqa: E722
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(f"[Retry] {func.__name__} échoué (attempt {attempt+1}/{max_attempts}): {e}")
                        time.sleep(delay)
                    else:
                        logger.error(f"[Retry] {func.__name__} a échoué après {max_attempts} tentatives")
            if last_exception:
                raise last_exception
            return None
        return wrapper
    return decorator

def suppress_errors(return_value: Any = None, log: bool = True):
    """Décorateur pour supprimer les erreurs et retourner une valeur par défaut."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log:
                    logger.debug(f"[Suppress] {func.__name__}: {e}")
                return return_value
        return wrapper
    return decorator
