"""Paquetage system_monitor - Monitoring complet du système.

Organisation modulaire :
- base.py : Classes abstraites et interfaces
- collectors.py : Collecteurs spécialisés (CPU, Mémoire, Disque, Processus)
- aggregator.py : Orchestrateur qui agrége les données
- display.py : Affichage Rich
"""

from .aggregator import SystemMonitor

__all__ = [
    "SystemMonitor",
]