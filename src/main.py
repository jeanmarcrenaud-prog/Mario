#!/usr/bin/env python3
"""
Point d'entrée principal de l'application.
Utilise la composition root pour l'injection de dépendances.
"""

from src.core.app_factory import create_assistant
from src.utils.logger import logger

def main():
    """Fonction principale de l'application."""
    try:
        # Création de l'assistant via la factory (composition root)
        assistant = create_assistant()
        
        # Démarrage de l'assistant
        assistant.run()
        
    except KeyboardInterrupt:
        logger.info("🛑 Arrêt manuel de l'application")
    except Exception as e:
        logger.critical(f"💥 Erreur fatale: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
