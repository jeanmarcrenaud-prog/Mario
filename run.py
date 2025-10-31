#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import socket
# Assurez-vous que le chemin racine du projet est dans le PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.main import AssistantVocal
from src.utils.logger import logger

def is_port_in_use(port: int) -> bool:
    """Vérifie si un port est déjà utilisé."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def check_if_already_running(port: int = 7860):
    """Vérifie si le programme est déjà lancé sur le port spécifié."""
    if is_port_in_use(port):
        print(f"[ERREUR] Le programme est déjà lancé sur le port {port}.")
        print("Veuillez arrêter l'instance existante ou utiliser un autre port.")
        exit(1)

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
    check_if_already_running(port=7860) 
    # Force l'encodage UTF-8 pour éviter les erreurs d'encodage dans le terminal Windows
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    main()
