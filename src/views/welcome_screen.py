#!/usr/bin/env python3
"""
Écran d'accueil et menu principal de l'application.
"""

# Explicitly import the rich SystemMonitor class, not the simple one
from src.utils.system_monitor import SystemMonitor  # This imports the rich one directly
from src.core.app_factory import create_assistant, create_assistant_with_simulation, create_minimal_assistant
from src.utils.logger import logger

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

def show_system_info(console: Console) -> None:
    """Affiche les informations système détaillées."""
    try:
        # Now this will call the correct static method
        system_info_text = SystemMonitor.get_system_info_text()
        
        console.print("\n[bold blue]📊 Informations Système[/bold blue]")
        console.print(system_info_text)
        
    except Exception as e:
        logger.error(f"Erreur affichage infos système: {e}")
        console.print(f"[red]❌ Erreur: {e}[/red]")

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
