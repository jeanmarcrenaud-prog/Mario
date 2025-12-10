import sys
import traceback
from typing import Callable, Optional

from rich.console import Console
from rich.prompt import Confirm

from src.utils.logger import logger
from src.config.config import config
from src.core.app_factory import create_assistant
from src.views.welcome_screen import show_welcome_screen, show_main_menu, show_system_info
from src.utils.setup import configure_logger_with_config


def _install_global_exception_handler(console: Console) -> None:
    def global_exception_handler(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            logger.info("Arrêt manuel du programme (Ctrl+C)")
            console.print("\n🛑 Arrêt manuel du programme (Ctrl+C)")
            return

        error_message = f"{exc_type.__name__}: {exc_value}"
        detailed_trace = "".join(traceback.format_tb(exc_traceback))
        logger.critical(
            "💥 Exception fatale: %s\nTraceback:\n%s",
            error_message,
            detailed_trace,
        )
        console.print("\n❌ Une erreur critique est survenue.")
        console.print("Consultez 'logs/app.log' pour les détails.")
        console.print(f"Détail: {error_message}")

    sys.excepthook = global_exception_handler


def _should_return_to_menu(console: Console, prompt: str) -> bool:
    return Confirm.ask(f"\n[payload]{prompt}[/payload]", default=True)


def _run_assistant_loop(console: Console) -> bool:
    assistant = create_assistant()
    if not assistant:
        console.print("[red]❌ Erreur lors de la création de l'assistant[/red]")
        return False

    console.print("\n[bold green]🤖 Assistant démarré ![/bold green]")
    console.print("[italic]Appuyez sur Ctrl+C pour quitter[/italic]\n")

    try:
        assistant.run()
    except KeyboardInterrupt:
        logger.info("🛑 Arrêt manuel de l'assistant")
        console.print("\n[yellow]👋 Assistant arrêté[/yellow]")

    return _should_return_to_menu(
        console, "[yellow]Retourner au menu principal ?[/yellow]"
    )


def _handle_menu_choice(choice: str, console: Console) -> bool:
    if choice == "5":
        console.print("[bold red]👋 Au revoir ![/bold red]")
        return False

    if choice == "4":
        show_system_info(console)
        return _should_return_to_menu(
            console, "[yellow]Retourner au menu ?[/yellow]"
        )

    return _run_assistant_loop(console)


def run_application(
    *,
    console_factory: Callable[[], Console] = Console,
) -> int:
    console = console_factory()

    configure_logger_with_config(logger)
    _install_global_exception_handler(console)

    logger.info("🚀 Démarrage de l'assistant vocal")
    logger.info(
        "Configuration chargée - Voix: %s, Modèle: %s",
        config.DEFAULT_VOICE,
        config.DEFAULT_MODEL,
    )

    show_welcome_screen(console)

    try:
        while True:
            choice = show_main_menu(console)
            if not _handle_menu_choice(choice, console):
                break

    except KeyboardInterrupt:
        logger.info("🛑 Arrêt manuel de l'application")
        console.print("\n[yellow]👋 Application arrêtée par l'utilisateur[/yellow]")
        return 1

    except Exception as e:
        logger.critical("💥 Erreur fatale: %s", e)
        logger.error(traceback.format_exc())
        console.print(f"\n[red]💥 Erreur fatale: {e}[/red]")
        return 1

    return 0