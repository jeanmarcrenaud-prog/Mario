import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from ..config import config

def setup_logger(name: str = "AssistantVocal") -> logging.Logger:
    """Configure et retourne un logger compatible Windows."""
    
    # Création du dossier logs
    os.makedirs(config.LOG_FOLDER, exist_ok=True)
    
    # Configuration du logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Nettoyage des handlers existants
    if logger.handlers:
        logger.handlers.clear()
    
    # Handler fichier avec rotation
    file_handler = RotatingFileHandler(
        os.path.join(config.LOG_FOLDER, "app.log"),
        maxBytes=10*1024*1024,
        backupCount=3,
        encoding='utf-8'  # UTF-8 pour supporter les emojis
    )
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ))
    
    # Handler console avec encodage forcé pour Windows
    class WindowsSafeStreamHandler(logging.StreamHandler):
        def __init__(self, stream=None):
            super().__init__(stream)
            # Forcer l'encodage UTF-8 pour la console Windows
            if sys.platform == "win32":
                try:
                    import io
                    self.stream = io.TextIOWrapper(
                        self.stream.buffer, 
                        encoding='utf-8', 
                        errors='replace'
                    )
                except:
                    pass
        
        def emit(self, record):
            try:
                msg = self.format(record)
                # Remplacer les emojis par du texte pour Windows si nécessaire
                if sys.platform == "win32":
                    msg = self._replace_emojis(msg)
                
                # Utiliser un encodage sûr
                if hasattr(self.stream, 'buffer'):
                    # Pour les streams binaires (stdout/stderr)
                    self.stream.buffer.write(msg.encode('utf-8', errors='replace') + self.terminator.encode('utf-8'))
                else:
                    # Pour les streams texte
                    self.stream.write(msg + self.terminator)
                
                self.flush()
            except UnicodeEncodeError:
                # Fallback: remplacer les caractères problématiques
                try:
                    safe_msg = msg.encode('utf-8', errors='replace').decode('utf-8')
                    if hasattr(self.stream, 'buffer'):
                        self.stream.buffer.write(safe_msg.encode('utf-8') + self.terminator.encode('utf-8'))
                    else:
                        self.stream.write(safe_msg + self.terminator)
                    self.flush()
                except Exception:
                    pass
            except Exception:
                self.handleError(record)
        
        def _replace_emojis(self, text):
            """Remplace les emojis par du texte lisible."""
            replacements = {
                '✅': '[OK]',
                '❌': '[ERREUR]',
                '⚠️': '[ATTENTION]',
                '🔄': '[CHARGEMENT]',
                '🎤': '[MICRO]',
                '🔊': '[AUDIO]',
                '🔔': '[ALERTE]',
                '🧹': '[NETTOYAGE]',
                '🎧': '[ECOUTE]',
                '⏹️': '[ARRET]',
                '🔇': '[SILENCE]',
                '📊': '[STATS]',
                '📁': '[FICHIER]',
                '🔧': '[OUTIL]',
                '⏰': '[TIMEOUT]',
                '🎯': '[CACHE]',
                '🌐': '[RESEAU]',
                '🔍': '[RECHERCHE]'
            }
            for emoji, text_replacement in replacements.items():
                text = text.replace(emoji, text_replacement)
            return text
    
    console_handler = WindowsSafeStreamHandler()
    console_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    ))
    
    # Ajout des handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logger()
