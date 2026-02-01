import platform
import psutil
import torch
import importlib
import importlib.metadata
from datetime import datetime
from typing import Dict, List, Optional

# ✅ Import Rich
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

from .logger import logger  # Import relatif

class SystemMonitor:
    """Moniteur système avancé pour l'assistant vocal."""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.console = Console()  # ✅ Console Rich
        logger.info("SystemMonitor initialisé")
    
    def get_cpu_usage(self) -> float:
        """Récupère l'utilisation du CPU."""
        return psutil.cpu_percent(interval=1)

    def get_cpu_detailed(self) -> Dict:
        """Récupère des informations détaillées sur le CPU."""
        try:
            return {
                "percent": psutil.cpu_percent(interval=1, percpu=True),
                "cores_physical": psutil.cpu_count(logical=False),
                "cores_logical": psutil.cpu_count(logical=True),
                "frequency": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {},
                "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else (0, 0, 0)
            }
        except Exception as e:
            logger.debug(f"Erreur CPU détaillé: {e}")
            return {}

    def get_memory_usage(self) -> float:
        """Récupère l'utilisation de la mémoire."""
        return psutil.virtual_memory().percent

    def get_memory_detailed(self) -> Dict:
        """Récupère des informations détaillées sur la mémoire."""
        try:
            vm = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return {
                "virtual": {
                    "total_gb": round(vm.total / (1024**3), 2),
                    "available_gb": round(vm.available / (1024**3), 2),
                    "used_gb": round(vm.used / (1024**3), 2),
                    "percent": vm.percent
                },
                "swap": {
                    "total_gb": round(swap.total / (1024**3), 2),
                    "used_gb": round(swap.used / (1024**3), 2),
                    "percent": swap.percent
                }
            }
        except Exception as e:
            logger.debug(f"Erreur mémoire détaillée: {e}")
            return {}

    def get_disk_usage(self, path: str = "/") -> float:
        """Récupère l'utilisation du disque pour un chemin donné."""
        try:
            disk_usage = psutil.disk_usage(path)
            return disk_usage.percent
        except Exception as e:
            logger.debug(f"Erreur disque {path}: {e}")
            return 0.0

    def get_disk_detailed(self) -> List[Dict]:
        """Récupère des informations détaillées sur tous les disques."""
        try:
            disk_info = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info.append({
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total_gb": round(usage.total / (1024**3), 2),
                        "used_gb": round(usage.used / (1024**3), 2),
                        "free_gb": round(usage.free / (1024**3), 2),
                        "percent": round((usage.used / usage.total) * 100, 1)
                    })
                except Exception:
                    continue
            return disk_info
        except Exception as e:
            logger.debug(f"Erreur disques détaillés: {e}")
            return []

    def get_network_stats(self) -> Dict:
        """Récupère les statistiques réseau."""
        try:
            net_io = psutil.net_io_counters()
            return {
                "bytes_sent_mb": round(net_io.bytes_sent / (1024**2), 2),
                "bytes_recv_mb": round(net_io.bytes_recv / (1024**2), 2),
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv
            }
        except Exception as e:
            logger.debug(f"Erreur réseau: {e}")
            return {}

    def get_gpu_info(self) -> List[Dict]:
        """Récupère les informations GPU."""
        gpus = []
        try:
            if torch.cuda.is_available():
                for i in range(torch.cuda.device_count()):
                    try:
                        props = torch.cuda.get_device_properties(i)
                        gpus.append({
                            "id": i,
                            "name": torch.cuda.get_device_name(i),
                            "memory_total_mb": round(props.total_memory / (1024**2)),
                            "memory_used_mb": round(torch.cuda.memory_allocated(i) / (1024**2)),
                            "memory_cached_mb": round(torch.cuda.memory_reserved(i) / (1024**2)),
                            "compute_capability": f"{props.major}.{props.minor}"
                        })
                    except Exception as e:
                        logger.debug(f"Erreur GPU {i}: {e}")
                        continue
        except Exception as e:
            logger.debug(f"Erreur GPU général: {e}")
        
        return gpus

    def get_system_info(self) -> dict:
        """Récupère des informations générales sur le système."""
        return {
            "cpu": self.get_cpu_usage(),
            "memory": self.get_memory_usage(),
            "disk": self.get_disk_usage(),
            "timestamp": datetime.now().isoformat()
        }

    def get_detailed_system_info(self) -> Dict:
        """Récupère des informations système détaillées."""
        return {
            "cpu": self.get_cpu_detailed(),
            "memory": self.get_memory_detailed(),
            "disk": self.get_disk_detailed(),
            "network": self.get_network_stats(),
            "gpu": self.get_gpu_info(),
            "uptime": self.get_uptime(),
            "timestamp": datetime.now().isoformat()
        }

    def get_uptime(self) -> Dict:
        """Récupère les informations de uptime."""
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            app_uptime = datetime.now() - self.start_time
            
            return {
                "system_days": uptime.days,
                "system_hours": uptime.seconds // 3600,
                "app_days": app_uptime.days,
                "app_hours": app_uptime.seconds // 3600,
                "boot_time": boot_time.isoformat()
            }
        except Exception as e:
            logger.debug(f"Erreur uptime: {e}")
            return {}

    @staticmethod
    def get_system_info_text() -> str:
        """Retourne les informations système sous forme de texte détaillé avec Rich."""
        try:
            # ✅ Création d'une console virtuelle pour capturer la sortie
            from io import StringIO
            from rich.console import Console as RichConsole
            
            string_buffer = StringIO()
            rich_console = RichConsole(file=string_buffer, force_terminal=False)
            
            # ✅ Panel principal
            rich_console.print(Panel("[bold blue]📊 Informations Système[/bold blue]", expand=False))

            # ✅ Tableau des infos système
            sys_table = Table(title="Système", box=box.SIMPLE)
            sys_table.add_column("Composant", style="cyan", no_wrap=True)
            sys_table.add_column("Détails", style="magenta")

            sys_table.add_row("Date/Heure", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            sys_table.add_row("OS", f"{platform.system()} {platform.release()}")
            sys_table.add_row("Python", f"{platform.python_version()} ({platform.architecture()[0]})")
            sys_table.add_row("CPU", platform.processor() or "Inconnu")
            sys_table.add_row("Cœurs physiques", str(psutil.cpu_count(logical=False) or "N/A"))
            sys_table.add_row("Cœurs logiques", str(psutil.cpu_count(logical=True) or "N/A"))
            
            if psutil.cpu_freq():
                sys_table.add_row("Fréquence CPU", f"{psutil.cpu_freq().current:.1f} MHz")

            rich_console.print(sys_table)

            # ✅ Mémoire
            vm = psutil.virtual_memory()
            mem_table = Table(title="Mémoire", box=box.SIMPLE)
            mem_table.add_column("Type", style="cyan")
            mem_table.add_column("Valeur", style="green")
            mem_table.add_row("Totale", f"{vm.total / 1024**3:.2f} GB")
            mem_table.add_row("Utilisée", f"{vm.used / 1024**3:.2f} GB")
            mem_table.add_row("Disponible", f"{vm.available / 1024**3:.2f} GB ({vm.percent:.1f}%)")
            rich_console.print(mem_table)

            # ✅ Disques
            disk_table = Table(title="Disques", box=box.SIMPLE)
            disk_table.add_column("Point de montage", style="cyan")
            disk_table.add_column("Utilisation", style="yellow")
            try:
                for partition in psutil.disk_partitions():
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        percent = (usage.used / usage.total) * 100
                        disk_table.add_row(
                            partition.mountpoint,
                            f"{usage.used / 1024**3:.1f}/{usage.total / 1024**3:.1f} GB ({percent:.1f}%)"
                        )
                    except Exception:
                        continue
            except Exception:
                disk_table.add_row("Erreur", "Impossible de lire les disques")
            rich_console.print(disk_table)

            # ✅ GPU
            gpu_table = Table(title="GPU", box=box.SIMPLE)
            gpu_table.add_column("Nom", style="cyan")
            gpu_table.add_column("VRAM", style="blue")
            try:
                if torch.cuda.is_available():
                    for i in range(torch.cuda.device_count()):
                        props = torch.cuda.get_device_properties(i)
                        gpu_table.add_row(
                            torch.cuda.get_device_name(i),
                            f"{props.total_memory / 1024**2:.0f} MB"
                        )
                else:
                    gpu_table.add_row("Aucun GPU", "CUDA non disponible")
            except Exception as e:
                gpu_table.add_row("Erreur", str(e))
            rich_console.print(gpu_table)

            # ✅ Modules
            modules_table = Table(title="Modules", box=box.SIMPLE)
            modules_table.add_column("Module", style="cyan")
            modules_table.add_column("Version", style="green")

            modules_to_check = [
                "gradio", "numpy", "pyaudio", "torch", "whisper",
                "webrtcvad", "psutil", "librosa", "piper",
                "openai", "faster_whisper"
            ]

            for mod in modules_to_check:
                try:
                    if mod == "piper":
                        ver = importlib.metadata.version("piper-tts")
                    elif mod == "librosa":
                        import librosa
                        ver = librosa.__version__
                    elif mod == "whisper":
                        import whisper
                        ver = getattr(whisper, '__version__', 'Installé')
                    else:
                        module = importlib.import_module(mod)
                        ver = getattr(module, '__version__', 'Version non disponible')
                except Exception:
                    ver = "[red]Non installé[/red]"
                modules_table.add_row(mod, ver)
            rich_console.print(modules_table)

            return string_buffer.getvalue()

        except Exception as e:
            logger.error(f"Erreur informations système avec Rich: {e}")
            return f"❌ Erreur récupération infos système: {e}"

    def get_system_stats(self) -> dict:
        """Retourne les statistiques système en temps réel."""
        try:
            vm = psutil.virtual_memory()
            stats = {
                "cpu_percent": psutil.cpu_percent(interval=0.5),
                "memory_percent": vm.percent,
                "memory_available_gb": round(vm.available / (1024**3), 2),
                "timestamp": datetime.now().isoformat()
            }
            
            # Ajouter GPU si disponible
            if torch.cuda.is_available():
                try:
                    stats["gpu_memory_used_mb"] = round(torch.cuda.memory_allocated() / (1024**2), 2)
                    stats["gpu_memory_total_mb"] = round(torch.cuda.get_device_properties(0).total_memory / (1024**2), 2)
                    stats["gpu_utilization"] = "N/A"  # Torch ne fournit pas l'utilisation GPU directement
                except Exception as e:
                    logger.debug(f"Erreur stats GPU: {e}")
            
            return stats
        except Exception as e:
            logger.debug(f"Erreur stats système: {e}")
            return {}

    def get_performance_alerts(self) -> List[str]:
        """Retourne des alertes de performance si nécessaire."""
        alerts = []
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=0.5)
            if cpu_percent > 80:
                alerts.append(f"⚠️  CPU élevé: {cpu_percent:.1f}%")
            
            # Mémoire
            memory_percent = psutil.virtual_memory().percent
            if memory_percent > 85:
                alerts.append(f"⚠️  Mémoire élevée: {memory_percent:.1f}%")
            
            # Disque
            disk_percent = psutil.disk_usage("/").percent
            if disk_percent > 90:
                alerts.append(f"⚠️  Disque presque plein: {disk_percent:.1f}%")
            
            # GPU
            if torch.cuda.is_available():
                gpu_memory_used = torch.cuda.memory_allocated() / (1024**2)
                gpu_memory_total = torch.cuda.get_device_properties(0).total_memory / (1024**2)
                gpu_percent = (gpu_memory_used / gpu_memory_total) * 100
                if gpu_percent > 85:
                    alerts.append(f"⚠️  GPU mémoire élevée: {gpu_percent:.1f}%")
                    
        except Exception as e:
            logger.debug(f"Erreur alertes performance: {e}")
        
        return alerts

    def get_resource_usage_summary(self) -> str:
        """Retourne un résumé de l'utilisation des ressources."""
        try:
            stats = self.get_system_stats()
            summary = [
                f"📊 Ressources:",
                f"   • CPU: {stats.get('cpu_percent', 0):.1f}%",
                f"   • RAM: {stats.get('memory_percent', 0):.1f}%",
            ]
            
            if 'gpu_memory_used_mb' in stats:
                gpu_used = stats['gpu_memory_used_mb']
                gpu_total = stats['gpu_memory_total_mb']
                gpu_percent = (gpu_used / gpu_total) * 100 if gpu_total > 0 else 0
                summary.append(f"   • GPU: {gpu_percent:.1f}% ({gpu_used:.0f}MB)")
            
            return " | ".join(summary)
            
        except Exception as e:
            logger.debug(f"Erreur résumé ressources: {e}")
            return "📊 Ressources: N/A"
