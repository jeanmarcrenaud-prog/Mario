#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# Assurez-vous que le chemin racine du projet est dans le PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.main import AssistantVocal
from src.utils.logger import logger

def main():
    try:
        # Démarrage de l'assistant vocal
        logger.info("Démarrage de l'assistant vocal")
        assistant = AssistantVocal()
        assistant.run()
    except KeyboardInterrupt:
        logger.info("Arrêt demandé par l'utilisateur.")
    except Exception as e:
        logger.error(f"Erreur inattendue : {e}", exc_info=True)
    finally:
        logger.info("Arrêt de l'application.")

if __name__ == "__main__":
    # Force l'encodage UTF-8 pour éviter les erreurs d'encodage dans le terminal Windows
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    main()
