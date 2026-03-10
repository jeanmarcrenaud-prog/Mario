"""
Tests complets pour les modules core
"""
import pytest
from unittest.mock import MagicMock, Mock, patch


class TestIntentRouter:
    """Tests complets pour la routage d'intention."""
    
    def test_intent_router_init(self):
        """Test d'initialisation de IntentRouter."""
        from src.core.intent_router import IntentRouter
        
        router = IntentRouter()
        
        assert router is not None
    
    def test_categorize(self):
        """Test de catégorisation d'intention."""
        from src.core.intent_router import IntentRouter
        
        router = IntentRouter()
        
        # Test existance de route_intent
        result = router.route_intent("test")
        assert result is not None
        assert "response" in result
    
    def test_route(self):
        """Test de routage d'intention."""
        from src.core.intent_router import IntentRouter
        
        router = IntentRouter()
        
        # Test routage
        result = router.route_intent("test python")
        assert result is not None


class TestPerformanceOptimizer:
    """Tests pour l'optimiseur de performance."""
    
    def test_optimizer_init(self):
        """Test d'initialisation de PerformanceOptimizer."""
        from src.core.performance_optimizer import PerformanceOptimizer
        
        optimizer = PerformanceOptimizer()
        
        assert optimizer is not None
    
    def test_optimize_memory(self):
        """Test d'optimisation de mémoire."""
        from src.core.performance_optimizer import PerformanceOptimizer
        
        optimizer = PerformanceOptimizer()
        
        result = optimizer.optimize_memory()
        
        assert result is True  # Méthode returns True on success
    
    def test_optimize_models(self):
        """Test d'optimisation de modèles."""
        from src.core.performance_optimizer import PerformanceOptimizer
        
        optimizer = PerformanceOptimizer()
        
        result = optimizer.optimize_models()
        
        assert result is True  # Méthode returns True on success
    
    def test_get_resource_usage(self):
        """Test de récupération d'usage de ressources."""
        from src.core.performance_optimizer import PerformanceOptimizer
        
        optimizer = PerformanceOptimizer()
        
        usage = optimizer.get_resource_usage()
        
        assert usage is not None
    
    def test_get_system_stats(self):
        """Test de récupération stats système."""
        from src.core.performance_optimizer import PerformanceOptimizer
        
        optimizer = PerformanceOptimizer()
        
        stats = optimizer.get_performance_report()
        
        assert stats is not None
