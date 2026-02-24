import platform
import psutil
import torch
import importlib
import importlib.metadata
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
from io import StringIO

from rich.console import Console as RichConsole
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
from rich.style import Style

from .logger import logger


class SystemMonitor:
    """Moniteur système avancé pour l'assistant vocal."""
    
    def __init__(self):
        self.start_time = datetime.now()
        self._cpu_history: List[float] = []
        self._memory_history: List[float] = []
        self._history_max_size = 60
        logger.info("SystemMonitor initialisé")
    
    def _color_value(self, value: float, thresholds=(80, 50)) -> Style:
        """Return a Rich style based on usage thresholds."""
        if value > thresholds[0]:
            return Style(color="red", bold=True)
        if value > thresholds[1]:
            return Style(color="yellow")
        return Style(color="green")
        
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

    def get_cpu_temp(self) -> Optional[float]:
        """Récupère la température CPU."""
        try:
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                if temps:
                    for name, entries in temps.items():
                        if 'cpu' in name.lower() or name == 'coretemp':
                            for entry in entries:
                                if entry.current:
                                    return round(entry.current, 1)
            return None
        except Exception as e:
            logger.debug(f"Erreur température CPU: {e}")
            return None

    def get_gpu_temp(self) -> Optional[float]:
        """Récupère la température GPU (NVIDIA)."""
        try:
            import subprocess
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return float(result.stdout.strip())
        except Exception:
            pass
        return None

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
                    is_ssd = self._is_ssd(partition.device)
                    disk_info.append({
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "type": "SSD" if is_ssd else "HDD",
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

    def _is_ssd(self, device: str) -> bool:
        """Détecte si un disque est un SSD."""
        try:
            if platform.system() == "Windows":
                import subprocess
                result = subprocess.run(
                    ["wmic", "diskdrive", "get", "model,mediatype"],
                    capture_output=True, text=True, timeout=5
                )
                return "SSD" in result.stdout or "Solid" in result.stdout
            else:
                return False
        except Exception:
            return False

    def get_disk_io_stats(self) -> Dict:
        """Récupère les statistiques I/O des disques."""
        try:
            io = psutil.disk_io_counters()
            return {
                "read_bytes_mb": round(io.read_bytes / (1024**2), 2),
                "write_bytes_mb": round(io.write_bytes / (1024**2), 2),
                "read_count": io.read_count,
                "write_count": io.write_count,
                "read_time_ms": io.read_time,
                "write_time_ms": io.write_time
            }
        except Exception as e:
            logger.debug(f"Erreur I/O disque: {e}")
            return {}

    def get_network_stats(self) -> Dict:
        """Récupère les statistiques réseau."""
        try:
            net_io = psutil.net_io_counters()
            return {
                "bytes_sent_mb": round(net_io.bytes_sent / (1024**2), 2),
                "bytes_recv_mb": round(net_io.bytes_recv / (1024**2), 2),
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
                "errin": net_io.errin,
                "errout": net_io.errout
            }
        except Exception as e:
            logger.debug(f"Erreur réseau: {e}")
            return {}

    def get_network_interfaces(self) -> List[Dict]:
        """Récupère les interfaces réseau."""
        try:
            interfaces = []
            net_if_addrs = psutil.net_if_addrs()
            for name, addresses in net_if_addrs.items():
                for addr in addresses:
                    if addr.family.name == "AF_INET":
                        interfaces.append({
                            "name": name,
                            "ip": addr.address,
                            "netmask": addr.netmask
                        })
            return interfaces
        except Exception as e:
            logger.debug(f"Erreur interfaces réseau: {e}")
            return []

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
                            "compute_capability": f"{props.major}.{props.minor}",
                            "temperature": self.get_gpu_temp()
                        })
                    except Exception as e:
                        logger.debug(f"Erreur GPU {i}: {e}")
                        continue
        except Exception as e:
            logger.debug(f"Erreur GPU général: {e}")
        
        return gpus

    def get_process_count(self) -> Dict:
        """Récupère le nombre de processus et threads."""
        try:
            return {
                "process_count": len(psutil.pids()),
                "thread_count": sum(p.num_threads() for p in psutil.process_iter(['num_threads']))
            }
        except Exception as e:
            logger.debug(f"Erreur processus: {e}")
            return {"process_count": 0, "thread_count": 0}

    def get_top_processes(self, limit: int = 5, sort_by: str = "cpu") -> List[Dict]:
        """Retourne les processus les plus consommateurs."""
        try:
            processes = []
            for p in psutil.process_iter(['name', 'cpu_percent', 'memory_percent', 'num_threads']):
                try:
                    processes.append({
                        "name": p.info['name'] or "Unknown",
                        "cpu": p.info['cpu_percent'] or 0,
                        "memory": p.info['memory_percent'] or 0,
                        "threads": p.info['num_threads'] or 0
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            reverse = True if sort_by == "cpu" else True
            processes.sort(key=lambda x: x.get(sort_by, 0), reverse=reverse)
            return processes[:limit]
        except Exception as e:
            logger.debug(f"Erreur top processus: {e}")
            return []

    def get_battery_status(self) -> Optional[Dict]:
        """Récupère le statut de la batterie."""
        try:
            if hasattr(psutil, "sensors_battery"):
                battery = psutil.sensors_battery()
                if battery:
                    return {
                        "percent": battery.percent,
                        "time_left_minutes": battery.secsleft // 60 if battery.secsleft != psutil.POWER_TIME_UNLIMITED else None,
                        "is_charging": battery.is_charging,
                        "power_plugged": battery.power_plugged
                    }
            return None
        except Exception as e:
            logger.debug(f"Erreur batterie: {e}")
            return None

    def get_audio_devices(self) -> List[Dict]:
        """Récupère les périphériques audio."""
        audio_devices = []
        try:
            import subprocess
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["powershell", "-Command", "Get-WmiObject Win32_SoundDevice | Select-Object Name, Status"],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    for line in result.stdout.split('\n')[1:]:
                        if line.strip():
                            audio_devices.append({"name": line.strip(), "type": "output"})
            else:
                import sounddevice as sd
                devices = sd.query_devices()
                for i, dev in enumerate(devices):
                    audio_devices.append({
                        "name": dev.get('name', f'Device {i}'),
                        "type": "input" if dev.get('max_input_channels', 0) > 0 else "output"
                    })
        except Exception as e:
            logger.debug(f"Erreur audio: {e}")
        return audio_devices

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
            "network_interfaces": self.get_network_interfaces(),
            "gpu": self.get_gpu_info(),
            "uptime": self.get_uptime(),
            "processes": self.get_process_count(),
            "top_processes": self.get_top_processes(),
            "battery": self.get_battery_status(),
            "audio": self.get_audio_devices(),
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
        """Return a plain text string with all system stats."""
        monitor = SystemMonitor()
        lines = []
        
        lines.append("=" * 60)
        lines.append("INFORMATIONS SYSTEME")
        lines.append("=" * 60)
        
        lines.append("\n--- SYSTEME ---")
        lines.append(f"Date/Heure: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"OS: {platform.system()} {platform.release()}")
        lines.append(f"Python: {platform.python_version()} ({platform.architecture()[0]})")
        lines.append(f"CPU: {platform.processor() or 'Inconnu'}")
        lines.append(f"Coeurs physiques: {psutil.cpu_count(logical=False) or 'N/A'}")
        lines.append(f"Coeurs logiques: {psutil.cpu_count(logical=True) or 'N/A'}")
        
        cpu_temp = monitor.get_cpu_temp()
        if cpu_temp:
            lines.append(f"Temp CPU: {cpu_temp}C")
        
        freq = psutil.cpu_freq()
        if freq:
            lines.append(f"Frequence CPU: {freq.current:.1f} MHz")
        
        proc_count = monitor.get_process_count()
        lines.append(f"Processus: {proc_count.get('process_count', 'N/A')}")
        lines.append(f"Threads: {proc_count.get('thread_count', 'N/A')}")
        
        lines.append("\n--- MEMOIRE ---")
        vm = psutil.virtual_memory()
        lines.append(f"Totale: {vm.total / 1024**3:.2f} GB")
        lines.append(f"Utilisee: {vm.used / 1024**3:.2f} GB")
        lines.append(f"Disponible: {vm.available / 1024**3:.2f} GB ({vm.percent:.1f}%)")
        
        lines.append("\n--- DISQUES ---")
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                is_ssd = monitor._is_ssd(part.device)
                lines.append(f"{part.mountpoint} ({'SSD' if is_ssd else 'HDD'}): "
                           f"{usage.used / 1024**3:.1f}/{usage.total / 1024**3:.1f} GB ({usage.percent:.1f}%)")
            except Exception:
                continue
        
        lines.append("\n--- RESEAU ---")
        net_stats = monitor.get_network_stats()
        lines.append(f"Envoye: {net_stats.get('bytes_sent_mb', 0):.2f} MB")
        lines.append(f"Recu: {net_stats.get('bytes_recv_mb', 0):.2f} MB")
        interfaces = monitor.get_network_interfaces()
        for iface in interfaces[:3]:
            lines.append(f"Interface {iface['name']}: {iface.get('ip', 'N/A')}")
        
        lines.append("\n--- GPU ---")
        if torch.cuda.is_available():
            for i in range(torch.cuda.device_count()):
                props = torch.cuda.get_device_properties(i)
                total_mb = props.total_memory / (1024**2)
                used_mb = torch.cuda.memory_allocated(i) / (1024**2)
                gpu_temp = monitor.get_gpu_temp()
                temp_str = f"{gpu_temp}C" if gpu_temp else "N/A"
                lines.append(f"{torch.cuda.get_device_name(i)}")
                lines.append(f"  VRAM: {total_mb:.0f} MB, Temp: {temp_str}, Util: {used_mb:.0f} MB ({used_mb/total_mb*100:.1f}%)")
        else:
            lines.append("Aucun GPU detected")
        
        battery = monitor.get_battery_status()
        if battery:
            lines.append("\n--- BATTERIE ---")
            lines.append(f"Niveau: {battery['percent']}%")
            lines.append(f"Etat: {'En charge' if battery['is_charging'] else 'Sur batterie'}")
            if battery.get('time_left_minutes'):
                lines.append(f"Temps restant: {battery['time_left_minutes']} min")
        
        top_procs = monitor.get_top_processes(5)
        if top_procs:
            lines.append("\n--- TOP PROCESSUS ---")
            lines.append(f"{'Nom':<30} {'CPU %':<10} {'RAM %':<10} {'Threads'}")
            for p in top_procs:
                lines.append(f"{p['name'][:30]:<30} {p['cpu']:<10.1f} {p['memory']:<10.1f} {p['threads']}")
        
        lines.append("\n--- MODULES ---")
        whitelist = ["gradio", "numpy", "pyaudio", "torch", "whisper", "webrtcvad", "psutil", "librosa", "piper-tts", "openai", "ollama", "fastapi"]
        for mod in whitelist:
            try:
                if mod == "piper-tts":
                    ver = importlib.metadata.version("piper-tts")
                else:
                    module = importlib.import_module(mod)
                    ver = getattr(module, "__version__", "N/A")
            except Exception:
                ver = "N/A"
            lines.append(f"{mod}: {ver}")
        
        boot = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot
        lines.append(f"\nUptime systeme: {uptime.days}d {uptime.seconds//3600}h")
        
        return "\n".join(lines)
    
    def get_system_stats(self) -> dict:
        """Retourne les statistiques système en temps réel."""
        try:
            vm = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=0.5)
            
            self._cpu_history.append(cpu_percent)
            self._memory_history.append(vm.percent)
            if len(self._cpu_history) > self._history_max_size:
                self._cpu_history.pop(0)
                self._memory_history.pop(0)
            
            stats = {
                "cpu_percent": cpu_percent,
                "cpu_temp": self.get_cpu_temp(),
                "memory_percent": vm.percent,
                "memory_available_gb": round(vm.available / (1024**3), 2),
                "cpu_history": self._cpu_history.copy(),
                "memory_history": self._memory_history.copy(),
                "timestamp": datetime.now().isoformat()
            }
            
            if torch.cuda.is_available():
                try:
                    stats["gpu_memory_used_mb"] = round(torch.cuda.memory_allocated() / (1024**2), 2)
                    stats["gpu_memory_total_mb"] = round(torch.cuda.get_device_properties(0).total_memory / (1024**2), 2)
                    stats["gpu_temp"] = self.get_gpu_temp()
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
            cpu_percent = psutil.cpu_percent(interval=0.5)
            if cpu_percent > 80:
                alerts.append(f"⚠️  CPU élevé: {cpu_percent:.1f}%")
            
            cpu_temp = self.get_cpu_temp()
            if cpu_temp and cpu_temp > 80:
                alerts.append(f"⚠️  Température CPU élevée: {cpu_temp}°C")
            
            memory_percent = psutil.virtual_memory().percent
            if memory_percent > 85:
                alerts.append(f"⚠️  Mémoire élevée: {memory_percent:.1f}%")
            
            disk_percent = psutil.disk_usage("/").percent
            if disk_percent > 90:
                alerts.append(f"⚠️  Disque presque plein: {disk_percent:.1f}%")
            
            if torch.cuda.is_available():
                try:
                    gpu_memory_used = torch.cuda.memory_allocated() / (1024**2)
                    gpu_memory_total = torch.cuda.get_device_properties(0).total_memory / (1024**2)
                    gpu_percent = (gpu_memory_used / gpu_memory_total) * 100
                    if gpu_percent > 85:
                        alerts.append(f"⚠️  GPU mémoire élevée: {gpu_percent:.1f}%")
                    
                    gpu_temp = self.get_gpu_temp()
                    if gpu_temp and gpu_temp > 85:
                        alerts.append(f"⚠️  Température GPU élevée: {gpu_temp}°C")
                except Exception:
                    pass
            
            battery = self.get_battery_status()
            if battery and battery['percent'] < 20 and not battery['is_charging']:
                alerts.append(f"🔋 Batterie faible: {battery['percent']}%")
                    
        except Exception as e:
            logger.debug(f"Erreur alertes performance: {e}")
        
        return alerts

    def check_outdated_packages(self) -> List[Dict]:
        """Vérifie les packages obsolètes."""
        outdated = []
        try:
            import subprocess
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--outdated", "--format=json"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0 and result.stdout:
                import json
                packages = json.loads(result.stdout)
                important_packages = ["torch", "numpy", "gradio", "whisper", "piper-tts", "ollama", "fastapi", "psutil", "librosa"]
                for pkg in packages:
                    if pkg["name"].lower() in important_packages:
                        outdated.append({
                            "name": pkg["name"],
                            "current": pkg["version"],
                            "latest": pkg["latest_version"]
                        })
        except Exception as e:
            logger.debug(f"Erreur verification mises a jour: {e}")
        return outdated

    def get_resource_usage_summary(self) -> str:
        """Retourne un résumé de l'utilisation des ressources."""
        try:
            stats = self.get_system_stats()
            summary = [
                f"📊 Ressources:",
                f"   • CPU: {stats.get('cpu_percent', 0):.1f}%",
                f"   • RAM: {stats.get('memory_percent', 0):.1f}%",
            ]
            
            if stats.get('cpu_temp'):
                summary.append(f"   • Temp CPU: {stats['cpu_temp']}°C")
            
            if 'gpu_memory_used_mb' in stats:
                gpu_used = stats['gpu_memory_used_mb']
                gpu_total = stats['gpu_memory_total_mb']
                gpu_percent = (gpu_used / gpu_total) * 100 if gpu_total > 0 else 0
                summary.append(f"   • GPU: {gpu_percent:.1f}% ({gpu_used:.0f}MB)")
                if stats.get('gpu_temp'):
                    summary[-1] += f" | {stats['gpu_temp']}°C"
            
            return " | ".join(summary)
            
        except Exception as e:
            logger.debug(f"Erreur résumé ressources: {e}")
            return "📊 Ressources: N/A"
