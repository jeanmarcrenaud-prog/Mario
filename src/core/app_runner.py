import sys
import traceback
import threading
from typing import Callable, Optional

from rich.console import Console
from rich.prompt import Confirm

from src.utils.logger import logger
from src.config.config import config
from src.core.app_factory import create_assistant
from src.views.welcome_screen import show_welcome_screen, show_main_menu, show_system_info
from src.utils.setup import configure_logger_with_config

# ────────────────────────────────────────────────────────────────────────────────
# 1️⃣  Import de l’interface Gradio
# ────────────────────────────────────────────────────────────────────────────────
from src.views.web_interface_gradio import GradioWebInterface
# -------------------------------------------------------------------------------

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
    """
    Crée l’assistant vocal et lance l’interface Gradio (option 1 du menu).
    """
    assistant = create_assistant()
    if not assistant:
        console.print("[red]❌ Erreur lors de la création de l'assistant[/red]")
        return False

    # ────────────────────────────────────────────────────────────────────────────────
    # 2️⃣  Lancement de l’interface Gradio dans un thread séparé
    # ────────────────────────────────────────────────────────────────────────────────
    web = GradioWebInterface(assistant)
    threading.Thread(target=web.launch, daemon=True).start()
    console.print(
        "[green]✅ Interface Gradio lancée sur http://localhost:7860[/green]"
    )
    # -------------------------------------------------------------------------------

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
        console.print("[bold red]Au revoir ![/bold red]")
        return False

    if choice == "4":
        show_system_info(console)
        
        try:
            from src.utils.system_monitor import SystemMonitor
            monitor = SystemMonitor()
            stats = monitor.get_system_stats()
            alerts = monitor.get_performance_alerts()
            outdated = monitor.check_outdated_packages()
            
            message_parts = []
            
            if alerts:
                clean_alerts = [a.replace("⚠️", "Attention").replace("🔋", "Batterie") for a in alerts]
                message_parts.append("Problemes detectes: " + ", ".join(clean_alerts))
            
            if outdated:
                pkg_names = [f"{p['name']} {p['current']} vers {p['latest']}" for p in outdated[:3]]
                message_parts.append(f"Modules a mettre a jour: {', '.join(pkg_names)}")
            
            if message_parts:
                message = ". ".join(message_parts)
            else:
                cpu = stats.get('cpu_percent', 0)
                mem = stats.get('memory_percent', 0)
                message = f"Systeme normal. Processeur a {cpu:.0f} pour cent, memoire a {mem:.0f} pour cent. Modules a jour. Tout va bien."
            
            from src.services.tts_service import TTSService
            tts = TTSService.create_with_piper()
            tts.speak(message)
        except Exception as e:
            logger.debug(f"TTS non disponible: {e}")
        
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

    logger.info("Demarrage de l'assistant vocal")
    logger.info(
        "Configuration chargée - Voix: %s, Modèle: %s",
        config.DEFAULT_VOICE,
        config.DEFAULT_MODEL,
    )

    show_welcome_screen(console)
    
    try:
        from src.services.tts_service import TTSService
        tts = TTSService.create_with_piper()
        tts.speak("Mario, ton chat t'ecoute")
    except Exception as e:
        logger.debug(f"TTS non disponible: {e}")
    
    try:
        while True:
            choice = show_main_menu(console)
            if not _handle_menu_choice(choice, console):
                break

    except KeyboardInterrupt:
        logger.info("Arret manuel de l'application")
        console.print("\n[yellow]Au revoir![/yellow]")
        return 1

    except Exception as e:
        logger.critical("Erreur fatale: %s", e)
        logger.error(traceback.format_exc())
        console.print(f"\n[red]Erreur fatale: {e}[/red]")
        return 1

    return 0