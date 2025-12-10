"""Classe de base abstraite pour les collecteurs de données système."""

from abc import ABC, abstractmethod
from typing import Dict, Any
from datetime import datetime


class DataCollector(ABC):
    """Interface abstraite pour les collecteurs de données."""
    
    def __init__(self):
        self.last_updated: datetime = None
        self.data: Dict[str, Any] = {}
    
    @abstractmethod
    def collect(self) -> Dict[str, Any]:
        """Collecter les données."""
        pass
    
    def get_data(self) -> Dict[str, Any]:
        """Retourner les données collées."""
        return self.data
    
    def _update_timestamp(self) -> None:
        """Mettre à jour l'heure de dernière modification."""
        self.last_updated = datetime.now()