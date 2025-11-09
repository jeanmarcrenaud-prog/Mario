import sys
import os
import traceback

# Ajouter le dossier courant au path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def main():
    try:
        # Importer les modules
        from src.utils.logger import logger, setup_logger
        from src.config.config import config
        from src.main import AssistantVocal
        
        # Configuration du logger avec les paramètres de config
        from src.utils.setup import configure_logger_with_config
        configure_logger_with_config(logger)
        
        # Configuration du handler d'exceptions global
        def global_exception_handler(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                logger.info("Arrêt manuel du programme (Ctrl+C)")
                print("\n🛑 Arrêt manuel du programme (Ctrl+C)")
                return

            error_message = f"{exc_type.__name__}: {exc_value}"
            detailed_trace = "".join(traceback.format_tb(exc_traceback))
            logger.critical("💥 Exception fatale: %s\nTraceback:\n%s", error_message, detailed_trace)

            print("\n❌ Une erreur critique est survenue.")
            print("Consultez 'logs/app.log' pour les détails.")
            print(f"Détail: {error_message}")

        sys.excepthook = global_exception_handler
        
        # Logger le démarrage
        logger.info("🚀 Démarrage de l'assistant vocal")
        logger.info(f"Configuration chargée - Voix: {config.DEFAULT_VOICE}, Modèle: {config.DEFAULT_MODEL}")
        
        # Démarrer l'assistant
        assistant = AssistantVocal()
        assistant.run()
        
    except Exception as e:
        print(f"Erreur fatale au démarrage: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
