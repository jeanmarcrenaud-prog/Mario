"""Affichage des informations système avec Rich."""

from rich.console import Console
from rich.table import Table
from .aggregator import SystemMonitor


def display_system_info(console: Console, monitor: SystemMonitor) -> None:
    """Afficher les informations système de manière jol ie."""
    data = monitor.get_system_info()
    
    table = Table(title="📄 Informations Système")
    table.add_column("Catégorie", style="cyan")
    table.add_column("Métrique", style="magenta")
    table.add_column("Valeur", style="green")
    
    # CPU
    cpu_data = data["cpu"]
    table.add_row("CPU", "Utilisation (%)", f"{cpu_data['percent']:.1f}%")
    table.add_row("CPU", "Cores (physiques)", str(cpu_data["cores_physical"]))
    table.add_row("CPU", "Cores (logiques)", str(cpu_data["cores_logical"]))
    
    # Mémoire
    mem_data = data["memory"]
    table.add_row("Mémoire", "Total (GB)", f"{mem_data['total_gb']:.1f}")
    table.add_row("Mémoire", "Utilisation (%)", f"{mem_data['percent']:.1f}%")
    table.add_row("Mémoire", "Disponible (GB)", f"{mem_data['available_gb']:.1f}")
    
    # Disque
    disk_data = data["disk"]
    table.add_row("Disque", "Total (GB)", f"{disk_data['total_gb']:.1f}")
    table.add_row("Disque", "Utilisation (%)", f"{disk_data['percent']:.1f}%")
    table.add_row("Disque", "Libre (GB)", f"{disk_data['free_gb']:.1f}")
    
    console.print(table)