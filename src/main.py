#!/usr/bin/env python3
"""
Point d'entrée principal de l'application.
Utilise la composition root pour l'injection de dépendances.
"""

from src.core.app_factory import create_assistant, create_assistant_with_simulation, create_minimal_assistant
from src.utils.logger import logger
from src.utils.system_monitor import SystemMonitor

# ✅ Import Rich pour l'interface interactive
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich import box

def show_welcome_screen(console):
    """Affiche l'écran d'accueil stylé."""
    console.print(Panel("""
[bold blue]███╗   ███╗ █████╗ ██████╗ ██╗ ██████╗ 
████╗ ████║██╔══██╗██╔══██╗██║██╔═══██╗
██╔████╔██║███████║██████╔╝██║██║   ██║
██║╚██╔╝██║██╔══██║██╔══██╗██║██║   ██║
██║ ╚═╝ ██║██║  ██║██║  ██║██║╚██████╔╝
╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝ ╚═════╝ 
[/bold blue]
[bold green]Assistant Vocal Intelligent[/bold green]
[yellow]Version 1.0.0[/yellow]
""", expand=False))

def show_system_info(console):
    """Affiche les informations système avec spinner."""
    monitor = SystemMonitor()  # Instanciation de SystemMonitor
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="📊 Analyse du système en cours...", total=None)
        system_info_text = monitor.get_system_info_text()  # Appel de la méthode sur l'instance
    console.print("\n[bold cyan]📋 Configuration Système :[/bold cyan]")
    console.print(system_info_text)

def show_main_menu(console):
    """Affiche le menu principal et retourne le choix."""
    table = Table(title="🎮 Menu Principal", box=box.ROUNDED)
    table.add_column("Option", style="cyan", no_wrap=True)
    table.add_column("Description", style="magenta")
    
    table.add_row("1", "🎙️  Assistant Vocal Normal")
    table.add_row("2", "🧪 Assistant avec Simulation")
    table.add_row("3", "⚡ Assistant Minimal (Tests)")
    table.add_row("4", "📊 Afficher Infos Système")
    table.add_row("5", "🚪 Quitter")
    
    console.print(table)
    
    choice = Prompt.ask(
        "\n[bold yellow]Choisissez une option[/bold yellow]", 
        choices=["1", "2", "3", "4", "5"],
        default="1"
    )
    
    return choice

def create_assistant_from_choice(choice):
    """Crée l'assistant en fonction du choix."""
    factory_map = {
        "1": ("Assistant Vocal Normal", create_assistant),
        "2": ("Assistant avec Simulation", create_assistant_with_simulation),
        "3": ("Assistant Minimal", create_minimal_assistant)
    }
    
    if choice in factory_map:
        mode_name, factory_func = factory_map[choice]
        console = Console()
        console.print(f"[bold blue]🔧 Initialisation : {mode_name}[/bold blue]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description=f"🚀 Chargement {mode_name.lower()}...", total=None)
            assistant = factory_func()
        
        console.print(f"[bold green]✅ {mode_name} prêt ![/bold green]")
        return assistant
    
    return None

def main():
    """Fonction principale avec menu interactif."""
    console = Console()
    
    try:
        # Écran d'accueil
        show_welcome_screen(console)        
        
        # Menu principal
        while True:
            choice = show_main_menu(console)
            
            if choice == "5":
                console.print("[bold red]👋 Au revoir ![/bold red]")
                break
            
            elif choice == "4":
                show_system_info(console)
                if not Confirm.ask("\n[yellow]Retourner au menu ?[/yellow]"):
                    break
                    
            else:
                # Créer et lancer l'assistant
                assistant = create_assistant_from_choice(choice)
                if assistant:
                    console.print("\n[bold green]🤖 Assistant démarré ![/bold green]")
                    console.print("[italic]Appuyez sur Ctrl+C pour quitter[/italic]\n")
                    
                    try:
                        assistant.run()
                    except KeyboardInterrupt:
                        logger.info("🛑 Arrêt manuel de l'assistant")
                        console.print("\n[yellow]👋 Assistant arrêté[/yellow]")
                    
                    if not Confirm.ask("\n[yellow]Retourner au menu principal ?[/yellow]"):
                        console.print("[bold red]👋 Au revoir ![/bold red]")
                        break
                else:
                    console.print("[red]❌ Erreur lors de la création de l'assistant[/red]")
                    
    except KeyboardInterrupt:
        logger.info("🛑 Arrêt manuel de l'application")
        console.print("\n[yellow]👋 Application arrêtée par l'utilisateur[/yellow]")
    except Exception as e:
        logger.critical(f"💥 Erreur fatale: {e}")
        import traceback
        logger.error(traceback.format_exc())
        console.print(f"\n[red]💥 Erreur fatale: {e}[/red]")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
