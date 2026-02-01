"""Collecteurs spécialises pour CPU, Mémoire, Disque, Processus."""

import psutil
from typing import Dict, Any
from .base import DataCollector


class CPUCollector(DataCollector):
    """Collecteur de données CPU."""
    
    def collect(self) -> Dict[str, Any]:
        """Collecter les données de CPU."""
        self.data = {
            "percent": psutil.cpu_percent(interval=1),
            "cores_physical": psutil.cpu_count(logical=False),
            "cores_logical": psutil.cpu_count(logical=True),
        }
        self._update_timestamp()
        return self.data


class MemoryCollector(DataCollector):
    """Collecteur de données Mémoire."""
    
    def collect(self) -> Dict[str, Any]:
        """Collecter les données de mémoire."""
        vm = psutil.virtual_memory()
        self.data = {
            "total_gb": round(vm.total / (1024**3), 2),
            "available_gb": round(vm.available / (1024**3), 2),
            "used_gb": round(vm.used / (1024**3), 2),
            "percent": vm.percent,
        }
        self._update_timestamp()
        return self.data


class DiskCollector(DataCollector):
    """Collecteur de données Disque."""
    
    def collect(self) -> Dict[str, Any]:
        """Collecter les données de disque."""
        disk = psutil.disk_usage("/")
        self.data = {
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "percent": disk.percent,
        }
        self._update_timestamp()
        return self.data