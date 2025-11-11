import platform
import psutil
import torch
import importlib
import importlib.metadata
from datetime import datetime
from typing import Dict, List, Optional
from .logger import logger  # Import relatif

class SystemMonitor:
    """Moniteur système avancé pour l'assistant vocal."""
    
    def __init__(self):
        self.start_time = datetime.now()
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
        """Retourne les informations système sous forme de texte détaillé."""
        try:
            cuda_available = False
            gpus = []
            try:
                if torch.cuda.is_available():
                    cuda_available = True
                    for i in range(torch.cuda.device_count()):
                        gpus.append({
                            "name": torch.cuda.get_device_name(i),
                            "memoryMB": round(torch.cuda.get_device_properties(i).total_memory / 1024**2)
                        })
            except Exception:
                pass
            
            modules_to_check = [
                "gradio", "numpy", "pyaudio", "torch", "whisper", 
                "webrtcvad", "psutil", "librosa", "piper", "pvporcupine",
                "openai", "faster_whisper"
            ]
            
            info_lines = [
                "="*80,
                "📊 DÉMARRAGE DE L'APPLICATION - INFORMATIONS SYSTÈME".center(80),
                "="*80,
                f"📅 Date et heure      : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"🖥️  OS                : {platform.system()} {platform.release()} ({platform.version()})",
                f"🐍 Python            : {platform.python_version()} ({platform.architecture()[0]})",
                f"🧠 CPU               : {platform.processor()}",
                f"   • Cœurs physiques : {psutil.cpu_count(logical=False) or 'N/A'}",
                f"   • Cœurs logiques  : {psutil.cpu_count(logical=True) or 'N/A'}",
                f"   • Fréquence       : {f'{psutil.cpu_freq().current:.1f} MHz' if psutil.cpu_freq() else 'N/A'}",
            ]
            
            # Mémoire
            vm = psutil.virtual_memory()
            info_lines.extend([
                f"💾 Mémoire totale    : {vm.total/1024**3:.2f} GB",
                f"   • Disponible      : {vm.available/1024**3:.2f} GB ({vm.percent:.1f}%)",
                f"   • Utilisée        : {vm.used/1024**3:.2f} GB",
            ])
            
            # Disques
            try:
                for partition in psutil.disk_partitions():
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        info_lines.append(
                            f"📂 {partition.mountpoint:<10} : "
                            f"{usage.used/1024**3:.1f}/{usage.total/1024**3:.1f} GB "
                            f"({usage.percent:.1f}%)"
                        )
                    except Exception:
                        continue
            except Exception:
                info_lines.append("📂 Disques           : Information non disponible")
            
            # GPU
            if gpus:
                for gpu in gpus:
                    info_lines.append(f"🎮 [GPU] Détecté      : {gpu['name']} ({gpu['memoryMB']} MB VRAM)")
            else:
                info_lines.append("🎮 [GPU] Aucun GPU détecté ou non supporté")
            
            info_lines.append(f"⚡ CUDA disponible    : {'✅ Oui' if cuda_available else '❌ Non'}")
            
            # Modules
            info_lines.append("\n📦 Versions des modules :")
            for mod in modules_to_check:
                try:
                    if mod == "piper":
                        try:
                            ver = importlib.metadata.version("piper-tts")
                        except importlib.metadata.PackageNotFoundError:
                            ver = "Installée, version inconnue"
                    elif mod == "librosa":
                        try:
                            import librosa
                            ver = librosa.__version__
                        except Exception:
                            ver = "Non installé"
                    elif mod == "whisper":
                        try:
                            import whisper
                            ver = getattr(whisper, '__version__', 'Installé')
                        except Exception:
                            ver = "Installé"
                    else:
                        try:
                            module = importlib.import_module(mod)
                            ver = getattr(module, '__version__', 'Version non disponible')
                            if ver is None:
                                ver = 'Version non disponible'
                        except Exception:
                            ver = "Non installé"
                except Exception:
                    ver = "Non installé"
                info_lines.append(f"   • {mod.strip():<18}: {ver}")
            
            info_lines.append("="*80)
            return "\n".join(info_lines)
            
        except Exception as e:
            logger.error(f"Erreur informations système: {e}")
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
