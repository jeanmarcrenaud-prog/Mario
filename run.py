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
        from src.core.app_factory import create_assistant
        from src.main import show_welcome_screen, show_main_menu, show_system_info
        from rich.console import Console
        from rich.prompt import Confirm
        # Configuration du logger avec les paramètres de config
        from src.utils.setup import configure_logger_with_config
        configure_logger_with_config(logger)
        
        # Configuration du handler d'exceptions global
        def global_exception_handler(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                logger.info("Arrêt manuel du programme (Ctrl+C)")
                print("\\n🛑 Arrêt manuel du programme (Ctrl+C)")
                return

            error_message = f"{exc_type.__name__}: {exc_value}"
            detailed_trace = "".join(traceback.format_tb(exc_traceback))
            logger.critical("💥 Exception fatale: %s\\nTraceback:\\n%s", error_message, detailed_trace)

            print("\\n❌ Une erreur critique est survenue.")
            print("Consultez 'logs/app.log' pour les détails.")
            print(f"Détail: {error_message}")

        sys.excepthook = global_exception_handler
        
        # Logger le démarrage
        logger.info("🚀 Démarrage de l'assistant vocal")
        logger.info(f"Configuration chargée - Voix: {config.DEFAULT_VOICE}, Modèle: {config.DEFAULT_MODEL}")
        
        # Afficher l'écran de bienvenue et le menu principal
        console = Console()
        show_welcome_screen(console)
        # Menu principal
        while True:
            choice = show_main_menu(console)
            
            if choice == "5":
                console.print("[bold red]👋 Au revoir ![/bold red]")
                break
            
            elif choice == "4":
                show_system_info(console)
                if not Confirm.ask("\\n[yellow]Retourner au menu ?[/yellow]", default=True):
                    break
                    
            else:
                # Démarrer l'assistant via la factory (composition root)
                assistant = create_assistant()
                if assistant:
                    console.print("\\n[bold green]🤖 Assistant démarré ![/bold green]")
                    console.print("[italic]Appuyez sur Ctrl+C pour quitter[/italic]\\n")

                    try:
                        assistant.run()
                    except KeyboardInterrupt:
                        logger.info("🛑 Arrêt manuel de l'assistant")
                        console.print("\\n[yellow]👋 Assistant arrêté[/yellow]")
                    
                    if not Confirm.ask("\\n[yellow]Retourner au menu principal ?[/yellow]", default=True):
                        console.print("[bold red]👋 Au revoir ![/bold red]")
                        break
                else:
                    console.print("[red]❌ Erreur lors de la création de l'assistant[/red]")
                    
    except KeyboardInterrupt:
        logger.info("🛑 Arrêt manuel de l'application")
        console.print("\\n[yellow]👋 Application arrêtée par l'utilisateur[/yellow]")
    except Exception as e:
        logger.critical(f"💥 Erreur fatale: {e}")
        import traceback
        logger.error(traceback.format_exc())
        console.print(f"\\n[red]💥 Erreur fatale: {e}[/red]")
        return 1
    
    return 0


if __name__ == "__main__":
    main()