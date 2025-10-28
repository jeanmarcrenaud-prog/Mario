#!/usr/bin/env python3
"""
Script de lancement de l'assistant vocal
"""

import sys
import os
import logging

# Ajout du dossier src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('logs', 'assistant.log')),
        logging.StreamHandler()
    ]
)

from src.main import AssistantVocal

if __name__ == "__main__":
    try:
        assistant = AssistantVocal()
        assistant.run()
    except Exception as e:
        logging.error(f"Erreur critique au démarrage: {e}")
        sys.exit(1)
