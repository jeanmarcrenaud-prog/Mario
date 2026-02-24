#!/usr/bin/env python3
"""
Écran d'accueil et menu principal de l'application.
"""

from src.utils.system_monitor import SystemMonitor
from src.core.app_factory import (
    create_assistant,
    create_assistant_with_simulation,
    create_minimal_assistant,
)
from src.utils.logger import logger

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.text import Text
from rich import box
from rich.style import Style
from datetime import datetime


def show_system_info(console: Console) -> None:
    """Affiche les informations système détaillées."""
    try:
        system_info_text = SystemMonitor.get_system_info_text()
        
        console.print("\n[bold cyan]INFO Systeme[/bold cyan]\n")
        console.print(system_info_text)
        
    except Exception as e:
        logger.error(f"Erreur affichage infos systeme: {e}")
        console.print(Panel(
            f"[red]Erreur: {e}[/red]",
            title="[red]Erreur[/red]",
            border_style="red"
        ))


def show_welcome_screen(console: Console) -> None:
    """Affiche l'écran d'accueil stylé."""
    console.clear()
    console.print()
    
    console.print(Panel(
        """
  MARIO - Assistant Vocal Intelligent
  Version 1.0.0
        """,
        title="*Bienvenue*",
        border_style="cyan",
        padding=(1, 2)
    ))
    
    console.print()


def show_status_bar(console: Console) -> None:
    """Affiche une barre de statut en bas de l'écran."""
    now = datetime.now()
    status = Text()
    status.append(f" {now.strftime('%Y-%m-%d %H:%M')} ", style="bold black on white")
    status.append(" | ", style="dim")
    status.append("[OK] System", style="green")
    status.append(" | ", style="dim")
    status.append("RAM: ", style="dim")
    
    try:
        import psutil
        mem = psutil.virtual_memory()
        status.append(f"{mem.percent:.0f}%", style="yellow" if mem.percent > 70 else "green")
    except:
        pass
    
    console.print(status, justify="center")


def show_main_menu(console: Console) -> str:
    """Affiche le menu principal et retourne le choix."""
    console.print()
    
    menu_content = Text()
    
    menu_content.append("+------------- MENU PRINCIPAL -------------+\n", style="bold cyan")
    
    options = [
        ("1", "*", "green", "Assistant Vocal Normal", "Reconnaissance vocale"),
        ("2", "~", "yellow", "Assistant avec Simulation", "Mode test"),
        ("3", "!", "magenta", "Assistant Minimal", "Mode leger"),
        ("4", "#", "blue", "Afficher Infos Systeme", "Ressources"),
        ("5", "q", "red", "Quitter", "Fermer"),
    ]
    
    for num, icon, color, title, desc in options:
        menu_content.append(f"| [{num}] ", style="white")
        menu_content.append(f"{icon} ", style=color)
        menu_content.append(f"{title:<28}", style=f"bold {color}")
        menu_content.append(f"-> {desc}", style="dim")
        menu_content.append("\n")
    
    menu_content.append("+-------------------------------------------+", style="bold cyan")
    
    console.print(Panel(
        menu_content,
        border_style="cyan",
        padding=(0, 1),
        expand=False
    ))
    
    console.print()
    
    choice = Prompt.ask(
        " > Votre choix",
        choices=["1", "2", "3", "4", "5"],
        default="1",
        show_choices=False
    )
    
    return choice


def show_submenu_assistant(console: Console) -> None:
    """Affiche le sous-menu de configuration de l'assistant."""
    console.print()
    
    table = Table(title="⚙️ Configuration de l'Assistant", box=box.DOUBLE, show_header=True, header_style="bold cyan")
    table.add_column("Option", style="cyan", no_wrap=True, width=8)
    table.add_column("Description", style="white")
    table.add_column("Statut", style="green", width=15)
    
    table.add_row("1", "Mode Standard", "✅ Actif")
    table.add_row("2", "Mode Silencieux", "⏸️ Inactif")
    table.add_row("3", "Retour au menu", "↩️")
    
    console.print(table)


def create_assistant_from_choice(choice: str, console: Console = None):
    """Crée l'assistant en fonction du choix."""
    if console is None:
        console = Console()
    
    factory_map = {
        "1": ("Assistant Vocal Normal", create_assistant, "🎙️"),
        "2": ("Assistant avec Simulation", create_assistant_with_simulation, "🧪"),
        "3": ("Assistant Minimal", create_minimal_assistant, "⚡")
    }
    
    if choice in factory_map:
        mode_name, factory_func, icon = factory_map[choice]
        
        console.print()
        
        with Progress(
            SpinnerColumn(style="cyan"),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task(description=f"[cyan]⚡ Initialisation de {mode_name}...[/cyan]", total=None)
            assistant = factory_func()
            progress.update(task, completed=True)
        
        console.print()
        console.print(Panel.fit(
            f"[bold green]{icon} {mode_name} est prêt ![/bold green]\n\n"
            f"[dim]Vous pouvez maintenant interagir avec l'assistant.[/dim]",
            border_style="green",
            padding=(1, 2)
        ))
        
        return assistant
    
    return None


def show_goodbye(console: Console) -> None:
    """Affiche l'écran d'au revoir."""
    console.print()
    console.print(Panel.fit(
        """
[bold cyan]Merci d'avoir utilisé Mario ![/bold cyan]

[yellow]👋 À bientôt[/yellow]
        """,
        title="[bold]Au Revoir[/bold]",
        border_style="cyan",
        padding=(1, 2)
    ))
    console.print()


def show_loading(console: Console, message: str) -> None:
    """Affiche une animation de chargement."""
    with Progress(
        SpinnerColumn(style="cyan"),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task(description=f"[cyan]{message}[/cyan]", total=None)
        import time
        time.sleep(1)


def show_error(console: Console, title: str, message: str) -> None:
    """Affiche un message d'erreur stylisé."""
    console.print(Panel(
        f"[bold red]{message}[/bold red]",
        title=f"[bold red]❌ {title}[/bold red]",
        border_style="red",
        padding=(1, 2)
    ))


def show_success(console: Console, title: str, message: str) -> None:
    """Affiche un message de succès stylisé."""
    console.print(Panel(
        f"[bold green]{message}[/bold green]",
        title=f"[bold green]✅ {title}[/bold green]",
        border_style="green",
        padding=(1, 2)
    ))
