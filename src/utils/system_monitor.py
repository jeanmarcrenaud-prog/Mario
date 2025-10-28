import platform
import psutil
import torch
import importlib
import importlib.metadata
from datetime import datetime
from ..utils.logger import logger

def get_system_info() -> str:
    """Retourne les informations système."""
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

    modules_to_check = ["gradio", "numpy", "pyaudio", "torch", "whisper", "webrtcvad", "psutil", "librosa", "piper"]
    info_lines = [
        "="*70,
        "DÉMARRAGE DE L'APPLICATION".center(70),
        "="*70,
        f"Date et heure      : {datetime.now()}",
        f"OS                : {platform.system()} {platform.release()} ({platform.version()})",
        f"Python            : {platform.python_version()} ({platform.architecture()[0]})",
        f"CPU               : {platform.processor()}",
        f" - Cœurs physiques: {psutil.cpu_count(logical=False)} | Logiques: {psutil.cpu_count(logical=True)}",
        f" - Fréquence CPU  : {psutil.cpu_freq().current:.1f} MHz" if psutil.cpu_freq() else "",
        f"Mémoire totale    : {psutil.virtual_memory().total/1024**3:.2f} GB",
        f"Mémoire dispo     : {psutil.virtual_memory().available/1024**3:.2f} GB",
    ]

    if gpus:
        for gpu in gpus:
            info_lines.append(f"[GPU] Détecté       : {gpu['name']} ({gpu['memoryMB']} MB VRAM)")
    else:
        info_lines.append("[GPU] Aucun GPU détecté ou non supporté")

    info_lines.append(f"CUDA disponible   : {'Oui' if cuda_available else 'Non'}")

    info_lines.append("\nVersions des modules :")
    for mod in modules_to_check:
        try:
            if mod == "piper":
                try:
                    try:
                        ver = importlib.metadata.version("piper-tts")
                    except importlib.metadata.PackageNotFoundError:
                        ver = "Installée, version inconnue"
                except Exception:
                    ver = "Non installé"
            elif mod == "librosa":
                try:
                    import librosa
                    ver = librosa.__version__
                except Exception:
                    ver = "Non installé"
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
        info_lines.append(f" - {mod.strip():<15}: {ver}")

    info_lines.append("="*70)
    return "\n".join(info_lines)

def get_system_stats() -> dict:
    """Retourne les statistiques système en temps réel."""
    try:
        stats = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "timestamp": datetime.now().isoformat()
        }
        if torch.cuda.is_available():
            stats["gpu_memory_used"] = torch.cuda.memory_allocated() / 1024**2
            stats["gpu_memory_total"] = torch.cuda.get_device_properties(0).total_memory / 1024**2
        return stats
    except Exception as e:
        logger.debug(f"Erreur stats système: {e}")
        return {}
