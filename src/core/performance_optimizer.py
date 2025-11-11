import psutil
import torch
import gc
import threading
import time
from typing import Dict, List, Optional
from ..utils.logger import logger

class PerformanceOptimizer:
    """Optimiseur de performance avancé pour l'assistant vocal."""
    
    def __init__(self):
        self.is_monitoring = False
        self.monitoring_thread = None
        self.performance_stats = {
            "cpu_usage": [],
            "memory_usage": [],
            "gpu_memory": [],
            "disk_io": [],
            "network_io": [],
            "response_times": []
        }
        self.alert_thresholds = {
            "cpu_max": 80.0,
            "memory_max": 85.0,
            "gpu_memory_max": 85.0,
            "disk_io_max": 90.0,
            "network_io_max": 100.0,  # MB/s
            "response_time_max": 5.0
        }
        self.model_cache = {}  # Cache pour les modèles
        self.last_optimization = time.time()
        self.optimization_cooldown = 60  # 1 minute entre optimisations
        logger.info("PerformanceOptimizer avancé initialisé")
    
    def start_monitoring(self):
        """Démarre le monitoring des performances."""
        if self.is_monitoring:
            logger.warning("Monitoring déjà actif")
            return
        
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitoring_thread.start()
        logger.info("Monitoring des performances démarré")
    
    def stop_monitoring(self):
        """Arrête le monitoring des performances."""
        self.is_monitoring = False
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=2.0)
        logger.info("Monitoring des performances arrêté")
    
    def _monitor_loop(self):
        """Boucle de monitoring en arrière-plan."""
        last_disk_io = psutil.disk_io_counters()
        last_net_io = psutil.net_io_counters()
        
        while self.is_monitoring:
            try:
                # Collecter les statistiques
                stats = self._collect_stats(last_disk_io, last_net_io)
                
                # Mettre à jour les compteurs pour le prochain cycle
                last_disk_io = psutil.disk_io_counters()
                last_net_io = psutil.net_io_counters()
                
                # Stocker les stats
                self._store_stats(stats)
                
                # Vérifier les alertes
                alerts = self._check_alerts(stats)
                if alerts:
                    for alert in alerts:
                        logger.warning(f"🚨 Performance: {alert}")
                
                # Auto-optimisation si nécessaire
                if self._should_auto_optimize(stats):
                    self._trigger_auto_optimization()
                
                # Pause de 5 secondes
                time.sleep(5)
                
            except Exception as e:
                logger.debug(f"Erreur monitoring: {e}")
                time.sleep(5)
    
    def _collect_stats(self, last_disk_io=None, last_net_io=None) -> Dict:
        """Collecte les statistiques système avancées."""
        try:
            stats = {
                "timestamp": time.time(),
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory_percent": psutil.virtual_memory().percent,
                "memory_available_gb": psutil.virtual_memory().available / (1024**3),
                "memory_used_gb": psutil.virtual_memory().used / (1024**3)
            }
            
            # GPU stats si disponible
            if torch.cuda.is_available():
                try:
                    stats["gpu_memory_used_mb"] = torch.cuda.memory_allocated() / (1024**2)
                    stats["gpu_memory_reserved_mb"] = torch.cuda.memory_reserved() / (1024**2)
                    stats["gpu_memory_total_mb"] = torch.cuda.get_device_properties(0).total_memory / (1024**2)
                    stats["gpu_utilization"] = self._get_gpu_utilization()
                except Exception as e:
                    logger.debug(f"Erreur stats GPU: {e}")
            
            # I/O disque
            if last_disk_io:
                try:
                    current_disk_io = psutil.disk_io_counters()
                    read_bytes_per_sec = (current_disk_io.read_bytes - last_disk_io.read_bytes) / 5  # 5 secondes
                    write_bytes_per_sec = (current_disk_io.write_bytes - last_disk_io.write_bytes) / 5
                    stats["disk_read_mbps"] = read_bytes_per_sec / (1024**2)
                    stats["disk_write_mbps"] = write_bytes_per_sec / (1024**2)
                except Exception as e:
                    logger.debug(f"Erreur stats disque: {e}")
            
            # I/O réseau
            if last_net_io:
                try:
                    current_net_io = psutil.net_io_counters()
                    bytes_per_sec = (current_net_io.bytes_sent + current_net_io.bytes_recv - 
                                   last_net_io.bytes_sent - last_net_io.bytes_recv) / 5
                    stats["network_mbps"] = bytes_per_sec / (1024**2)
                except Exception as e:
                    logger.debug(f"Erreur stats réseau: {e}")
            
            return stats
            
        except Exception as e:
            logger.debug(f"Erreur collecte stats: {e}")
            return {}
    
    def _get_gpu_utilization(self) -> float:
        """Récupère l'utilisation GPU (simplifié)."""
        try:
            # Pour une implémentation plus précise, vous pouvez utiliser nvidia-ml-py
            # Mais pour l'instant, on utilise une estimation basique
            if torch.cuda.is_available():
                # Vérifier si des tensors CUDA sont actifs
                if torch.cuda.memory_allocated() > 0:
                    return 50.0  # Estimation
            return 0.0
        except Exception:
            return 0.0
    
    def _store_stats(self, stats: Dict):
        """Stocke les statistiques avec limitation."""
        if not stats:
            return
        
        # Ajouter aux listes (limiter à 100 points)
        for key in ["cpu_percent", "memory_percent", "disk_read_mbps", "disk_write_mbps", "network_mbps"]:
            if key in stats:
                self.performance_stats[key].append(stats[key])
                if len(self.performance_stats[key]) > 100:
                    self.performance_stats[key] = self.performance_stats[key][-100:]
        
        # GPU memory
        if "gpu_memory_used_mb" in stats:
            self.performance_stats["gpu_memory"].append(stats["gpu_memory_used_mb"])
            if len(self.performance_stats["gpu_memory"]) > 100:
                self.performance_stats["gpu_memory"] = self.performance_stats["gpu_memory"][-100:]
    
    def _check_alerts(self, stats: Dict) -> List[str]:
        """Vérifie les alertes de performance avancées."""
        alerts = []
        
        if not stats:
            return alerts
        
        # CPU
        cpu_percent = stats.get("cpu_percent", 0)
        if cpu_percent > self.alert_thresholds["cpu_max"]:
            alerts.append(f"CPU élevé: {cpu_percent:.1f}%")
        
        # Mémoire
        memory_percent = stats.get("memory_percent", 0)
        if memory_percent > self.alert_thresholds["memory_max"]:
            alerts.append(f"Mémoire élevée: {memory_percent:.1f}%")
        
        # GPU
        if "gpu_memory_used_mb" in stats and "gpu_memory_total_mb" in stats:
            gpu_percent = (stats["gpu_memory_used_mb"] / stats["gpu_memory_total_mb"]) * 100
            if gpu_percent > self.alert_thresholds["gpu_memory_max"]:
                alerts.append(f"GPU mémoire élevée: {gpu_percent:.1f}%")
        
        # Disque I/O
        if "disk_read_mbps" in stats:
            if stats["disk_read_mbps"] > self.alert_thresholds["disk_io_max"]:
                alerts.append(f"Disque lecture élevée: {stats['disk_read_mbps']:.1f} MB/s")
        if "disk_write_mbps" in stats:
            if stats["disk_write_mbps"] > self.alert_thresholds["disk_io_max"]:
                alerts.append(f"Disque écriture élevée: {stats['disk_write_mbps']:.1f} MB/s")
        
        # Réseau I/O
        if "network_mbps" in stats:
            if stats["network_mbps"] > self.alert_thresholds["network_io_max"]:
                alerts.append(f"Réseau élevé: {stats['network_mbps']:.1f} MB/s")
        
        return alerts
    
    def optimize_memory(self, aggressive: bool = False):
        """Optimise l'utilisation mémoire avancée."""
        try:
            logger.info(f"🧹 Optimisation mémoire {'agressive' if aggressive else 'normale'}")
            
            # Nettoyer le cache CUDA
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                if aggressive:
                    torch.cuda.ipc_collect()
                logger.info("🧹 Cache CUDA nettoyé")
            
            # Forcer le garbage collector
            collected = gc.collect()
            logger.info(f"🧹 Garbage collection: {collected} objets")
            
            # Nettoyage plus agressif si demandé
            if aggressive:
                # Nettoyer les caches Python
                import sys
                if hasattr(sys, 'clear_cache'):
                    sys.clear_cache()
                
                # Vider les caches de bibliothèques
                self._clear_library_caches()
            
            # Vérifier la mémoire
            memory = psutil.virtual_memory()
            logger.info(f"📊 Mémoire après optimisation: {memory.percent:.1f}%")
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur optimisation mémoire: {e}")
            return False
    
    def _clear_library_caches(self):
        """Nettoie les caches des bibliothèques."""
        try:
            # Whisper cache
            import whisper
            if hasattr(whisper, '_cache'):
                whisper._cache.clear()
            
            # NumPy cache
            import numpy as np
            if hasattr(np, 'clear_cache'):
                np.clear_cache()
                
        except Exception as e:
            logger.debug(f"Erreur nettoyage caches: {e}")
    
    def optimize_models(self, unload_unused: bool = True):
        """Optimise les modèles chargés."""
        try:
            logger.info("⚡ Optimisation des modèles")
            
            # Nettoyer les caches
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            # Décharger les modèles inutilisés si demandé
            if unload_unused and hasattr(self, '_unload_unused_models'):
                unloaded = self._unload_unused_models()
                if unloaded:
                    logger.info(f"🗑️ {unloaded} modèles déchargés")
            
            logger.info("✅ Optimisation modèles terminée")
            return True
            
        except Exception as e:
            logger.error(f"Erreur optimisation modèles: {e}")
            return False
    
    def _unload_unused_models(self) -> int:
        """Décharge les modèles inutilisés."""
        unloaded_count = 0
        try:
            # Ici vous pouvez implémenter la logique de déchargement
            # basée sur le temps d'inactivité des modèles
            current_time = time.time()
            
            models_to_remove = []
            for model_name, model_info in self.model_cache.items():
                if current_time - model_info.get('last_used', 0) > 300:  # 5 minutes
                    models_to_remove.append(model_name)
            
            for model_name in models_to_remove:
                del self.model_cache[model_name]
                unloaded_count += 1
                logger.info(f"🗑️ Modèle {model_name} déchargé")
                
        except Exception as e:
            logger.debug(f"Erreur déchargement modèles: {e}")
        
        return unloaded_count
    
    def get_performance_report(self) -> Dict:
        """Retourne un rapport de performance détaillé."""
        try:
            # Statistiques récentes
            recent_stats = {}
            for key, values in self.performance_stats.items():
                if values:
                    recent_stats[key] = {
                        "current": values[-1] if values else 0,
                        "average": sum(values) / len(values) if values else 0,
                        "max": max(values) if values else 0,
                        "min": min(values) if values else 0,
                        "trend": self._calculate_trend(values) if len(values) > 1 else "stable"
                    }
            
            # Utilisation système actuelle
            current_stats = self._collect_stats()
            
            report = {
                "timestamp": time.time(),
                "recent_stats": recent_stats,
                "current_stats": current_stats,
                "alerts": self._check_alerts(current_stats),
                "recommendations": self._get_detailed_recommendations(current_stats),
                "system_health": self._calculate_system_health(current_stats),
                "optimization_history": self._get_optimization_history()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Erreur rapport performance: {e}")
            return {"error": str(e)}
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calcule la tendance d'une série de valeurs."""
        if len(values) < 2:
            return "stable"
        
        # Comparer les dernières valeurs avec les précédentes
        recent_avg = sum(values[-5:]) / min(5, len(values))
        previous_avg = sum(values[-10:-5]) / min(5, max(1, len(values) - 5))
        
        if recent_avg > previous_avg * 1.1:
            return "increasing"
        elif recent_avg < previous_avg * 0.9:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_system_health(self, current_stats: Dict) -> Dict:
        """Calcule la santé globale du système."""
        try:
            health_score = 100
            issues = []
            
            # CPU
            cpu_percent = current_stats.get("cpu_percent", 0)
            if cpu_percent > 80:
                health_score -= 20
                issues.append("CPU surchargé")
            elif cpu_percent > 60:
                health_score -= 10
            
            # Mémoire
            memory_percent = current_stats.get("memory_percent", 0)
            if memory_percent > 85:
                health_score -= 25
                issues.append("Mémoire critique")
            elif memory_percent > 70:
                health_score -= 15
                issues.append("Mémoire élevée")
            
            # GPU
            if "gpu_memory_used_mb" in current_stats and "gpu_memory_total_mb" in current_stats:
                gpu_percent = (current_stats["gpu_memory_used_mb"] / current_stats["gpu_memory_total_mb"]) * 100
                if gpu_percent > 85:
                    health_score -= 20
                    issues.append("GPU mémoire élevée")
                elif gpu_percent > 70:
                    health_score -= 10
            
            return {
                "score": max(0, health_score),
                "status": self._get_health_status(health_score),
                "issues": issues
            }
        except Exception as e:
            logger.debug(f"Erreur calcul santé: {e}")
            return {"score": 50, "status": "unknown", "issues": []}
    
    def _get_health_status(self, score: int) -> str:
        """Retourne le statut de santé basé sur le score."""
        if score >= 80:
            return "excellent"
        elif score >= 60:
            return "good"
        elif score >= 40:
            return "fair"
        elif score >= 20:
            return "poor"
        else:
            return "critical"
    
    def _get_detailed_recommendations(self, current_stats: Dict) -> List[str]:
        """Génère des recommandations détaillées d'optimisation."""
        recommendations = []
        
        if not current_stats:
            return recommendations
        
        # CPU
        cpu_percent = current_stats.get("cpu_percent", 0)
        if cpu_percent > 80:
            recommendations.append("📉 Réduire charge CPU: fermer applications inutiles")
        elif cpu_percent > 60:
            recommendations.append("⚠️ CPU modérément chargé: surveiller utilisation")
        
        # Mémoire
        memory_percent = current_stats.get("memory_percent", 0)
        memory_available = current_stats.get("memory_available_gb", 0)
        if memory_percent > 85:
            recommendations.append("🚨 Libérer mémoire: redémarrer assistant")
        elif memory_percent > 70:
            recommendations.append("🧹 Optimiser mémoire: exécuter gc.collect()")
        elif memory_available < 2:
            recommendations.append("💾 Mémoire faible: libérer espace disque")
        
        # GPU
        if "gpu_memory_used_mb" in current_stats and "gpu_memory_total_mb" in current_stats:
            gpu_percent = (current_stats["gpu_memory_used_mb"] / current_stats["gpu_memory_total_mb"]) * 100
            if gpu_percent > 85:
                recommendations.append("🎮 Libérer GPU: décharger modèles inutilisés")
            elif gpu_percent > 70:
                recommendations.append("⚠️ GPU chargé: surveiller utilisation")
        
        # I/O disque
        if "disk_read_mbps" in current_stats:
            if current_stats["disk_read_mbps"] > 50:
                recommendations.append("💾 Disque lecture intense: optimiser accès fichiers")
        if "disk_write_mbps" in current_stats:
            if current_stats["disk_write_mbps"] > 50:
                recommendations.append("💾 Disque écriture intense: réduire écritures")
        
        # Réseau
        if "network_mbps" in current_stats:
            if current_stats["network_mbps"] > 50:
                recommendations.append("🌐 Réseau chargé: vérifier connexions")
        
        # Recommandations générales
        if not recommendations:
            recommendations.extend([
                "✅ Système en excellent état",
                "📈 Performance optimale maintenue",
                "🔧 Continuer monitoring régulier"
            ])
        else:
            recommendations.append("📊 Surveiller tendances sur 5-10 minutes")
        
        return recommendations
    
    def _get_optimization_history(self) -> List[Dict]:
        """Retourne l'historique des optimisations."""
        # Pour l'instant, retourner un historique vide
        # Vous pouvez implémenter un système de logging persistant
        return []
    
    def auto_optimize(self, force: bool = False):
        """Optimisation automatique avancée basée sur les statistiques."""
        try:
            if not force and not self._should_optimize():
                return False
            
            current_stats = self._collect_stats()
            alerts = self._check_alerts(current_stats)
            
            optimizations_performed = []
            aggressive_mode = len(alerts) > 2  # Mode agressif si plusieurs alertes
            
            # Optimisation mémoire
            if (current_stats.get("memory_percent", 0) > 75 or 
                len(alerts) > 1 or 
                aggressive_mode):
                logger.info(f"⚡ Auto-optimisation mémoire {'agressive' if aggressive_mode else 'normale'}")
                self.optimize_memory(aggressive=aggressive_mode)
                optimizations_performed.append("Mémoire optimisée")
            
            # Optimisation GPU
            if ("gpu_memory_used_mb" in current_stats and 
                "gpu_memory_total_mb" in current_stats):
                gpu_percent = (current_stats["gpu_memory_used_mb"] / current_stats["gpu_memory_total_mb"]) * 100
                if gpu_percent > 75:
                    logger.info("⚡ Auto-optimisation GPU")
                    self.optimize_models()
                    optimizations_performed.append("GPU optimisé")
            
            # Déchargement modèles inutilisés
            if len(self.model_cache) > 5:  # Si plus de 5 modèles en cache
                unloaded = self._unload_unused_models()
                if unloaded > 0:
                    optimizations_performed.append(f"{unloaded} modèles déchargés")
            
            self.last_optimization = time.time()
            
            if optimizations_performed:
                logger.info(f"✅ Auto-optimisations: {', '.join(optimizations_performed)}")
                return True
            else:
                logger.info("✅ Pas d'optimisations nécessaires")
                return False
                
        except Exception as e:
            logger.error(f"Erreur auto-optimisation: {e}")
            return False
    
    def _should_optimize(self) -> bool:
        """Vérifie si une optimisation est nécessaire."""
        # Ne pas optimiser trop fréquemment
        if time.time() - self.last_optimization < self.optimization_cooldown:
            return False
        
        # Vérifier si des alertes sont actives
        current_stats = self._collect_stats()
        alerts = self._check_alerts(current_stats)
        
        return len(alerts) > 0
    
    def _should_auto_optimize(self, stats: Dict) -> bool:
        """Vérifie si une auto-optimisation est nécessaire."""
        # Optimiser si plusieurs ressources sont surchargées
        alert_count = len(self._check_alerts(stats))
        return alert_count >= 2
    
    def _trigger_auto_optimization(self):
        """Déclenche une optimisation automatique."""
        logger.info("⚡ Déclenchement auto-optimisation")
        threading.Thread(target=self.auto_optimize, daemon=True).start()
    
    def get_resource_usage(self) -> Dict:
        """Retourne l'utilisation actuelle des ressources détaillée."""
        try:
            stats = self._collect_stats()
            usage = {
                "cpu": f"{stats.get('cpu_percent', 0):.1f}%",
                "memory": f"{stats.get('memory_percent', 0):.1f}% ({stats.get('memory_available_gb', 0):.2f}GB dispo)",
                "memory_used": f"{stats.get('memory_used_gb', 0):.2f}GB"
            }
            
            if "gpu_memory_used_mb" in stats and "gpu_memory_total_mb" in stats:
                gpu_percent = (stats["gpu_memory_used_mb"] / stats["gpu_memory_total_mb"]) * 100
                usage["gpu"] = f"{gpu_percent:.1f}% ({stats['gpu_memory_used_mb']:.0f}MB/{stats['gpu_memory_total_mb']:.0f}MB)"
                if "gpu_utilization" in stats:
                    usage["gpu_utilization"] = f"{stats['gpu_utilization']:.1f}%"
            
            if "disk_read_mbps" in stats:
                usage["disk_io"] = f"R:{stats['disk_read_mbps']:.1f}MB/s W:{stats['disk_write_mbps']:.1f}MB/s"
            
            if "network_mbps" in stats:
                usage["network"] = f"{stats['network_mbps']:.1f}MB/s"
            
            return usage
            
        except Exception as e:
            logger.error(f"Erreur usage ressources: {e}")
            return {"error": str(e)}
    
    def set_thresholds(self, **thresholds):
        """Définit les seuils d'alerte personnalisés."""
        for key, value in thresholds.items():
            if key in self.alert_thresholds:
                old_value = self.alert_thresholds[key]
                self.alert_thresholds[key] = value
                logger.info(f"🔧 Seuil {key}: {old_value} → {value}")
    
    def get_optimization_profile(self) -> Dict:
        """Retourne le profil d'optimisation actuel."""
        return {
            "thresholds": self.alert_thresholds.copy(),
            "cooldown": self.optimization_cooldown,
            "cached_models": len(self.model_cache),
            "monitoring_active": self.is_monitoring,
            "last_optimization": self.last_optimization
        }
    
    def set_optimization_profile(self, profile: Dict):
        """Définit le profil d'optimisation."""
        if "thresholds" in profile:
            self.alert_thresholds.update(profile["thresholds"])
        if "cooldown" in profile:
            self.optimization_cooldown = profile["cooldown"]
        logger.info("✅ Profil d'optimisation mis à jour")
