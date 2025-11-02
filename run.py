import sys
import traceback
from src.utils.logger import logger, safe_run
from src.main import AssistantVocal

# ===============================================================
# Gestion globale des exceptions au niveau du programme principal
# ===============================================================
def global_exception_handler(exc_type, exc_value, exc_traceback):
    """Capture toute exception non gérée au niveau du processus principal."""
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

# ===============================================================
# Fonction principale protégée
# ===============================================================
@safe_run("Main")
def main():
    """Point d’entrée principal de l’assistant vocal."""
    logger.info("🚀 Démarrage de l'assistant vocal")

    assistant = AssistantVocal()

    try:
        assistant.run()
    except Exception as e:
        logger.exception("Erreur lors du démarrage ou de l'exécution de l'assistant: %s", e)
        print("❌ Erreur pendant l'exécution de l'assistant vocal. Consultez les logs.")
    finally:
        logger.info("⏹️ Arrêt du programme")
        logger.info("🧹 Nettoyage des ressources...")

# ===============================================================
# Exécution
# ===============================================================
if __name__ == "__main__":
    main()
