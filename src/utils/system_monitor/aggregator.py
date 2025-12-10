"""Orchestrateur principal qui agrége les collecteurs."""

from typing import Dict, Any
from .collectors import CPUCollector, MemoryCollector, DiskCollector


class SystemMonitor:
    """Moniteur système qui agrège tous les collecteurs."""
    
    def __init__(self):
        """Initialiser les collecteurs."""
        self.cpu_collector = CPUCollector()
        self.memory_collector = MemoryCollector()
        self.disk_collector = DiskCollector()
    
    def collect_all(self) -> Dict[str, Any]:
        """Collecter toutes les données système."""
        return {
            "cpu": self.cpu_collector.collect(),
            "memory": self.memory_collector.collect(),
            "disk": self.disk_collector.collect(),
        }
    
    def get_system_info(self) -> Dict[str, Any]:
        """Retourner les informations système agrégées."""
        return self.collect_all()