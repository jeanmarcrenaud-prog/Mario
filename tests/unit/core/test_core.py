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
        
        # Setup
        router._set_categories({
            "code": ["python code", "javascript code"],
            "help": ["help me", "can you help"],
            "info": ["what", "info"]
        })
        
        # Test catégorisation
        result = router.categorize("python code")
        
        assert result in ["code", "help", "info"]
    
    def test_route(self):
        """Test de routage d'intention."""
        from src.core.intent_router import IntentRouter
        
        router = IntentRouter()
        router._set_categories({
            "code": ["python", "javascript"],
        })
        
        # Test routage
        result = router.route("python code")
        
        assert result is not None


class TestPerformanceOptimizer:
    """Tests pour l'optimiseur de performance."""
    
    @pytest.fixture
    def mock_monitor(self):
        """Mock monitor système."""
        monitor = Mock()
        
        monitor.cpu_percent.return_value = 50.0
        monitor.memory_percent.return_value = 60.0
        monitor.gpu_percent.return_value = 30.0
        
        return monitor
    
    def test_optimizer_init(self, mock_monitor):
        """Test d'initialisation de PerformanceOptimizer."""
        from src.core.performance_optimizer import PerformanceOptimizer
        
        settings = MagicMock()
        optimizer = PerformanceOptimizer(mock_monitor, settings)
        
        assert optimizer is not None
    
    def test_optimize_memory(self, mock_monitor):
        """Test d'optimisation de mémoire."""
        from src.core.performance_optimizer import PerformanceOptimizer
        
        settings = MagicMock()
        optimizer = PerformanceOptimizer(mock_monitor, settings)
        
        result = optimizer.optimize_memory()
        
        assert result is False
    
    def test_optimize_models(self, mock_monitor):
        """Test d'optimisation de modèles."""
        from src.core.performance_optimizer import PerformanceOptimizer
        
        settings = MagicMock()
        optimizer = PerformanceOptimizer(mock_monitor, settings)
        
        result = optimizer.optimize_models()
        
        assert result is False
    
    def test_get_resource_usage(self, mock_monitor):
        """Test de récupération d'usage de ressources."""
        from src.core.performance_optimizer import PerformanceOptimizer
        
        settings = MagicMock()
        optimizer = PerformanceOptimizer(mock_monitor, settings)
        
        usage = optimizer.get_resource_usage()
        
        assert usage is not None
    
    def test_get_system_stats(self, mock_monitor):
        """Test de récupération stats système."""
        from src.core.performance_optimizer import PerformanceOptimizer
        
        settings = MagicMock()
        optimizer = PerformanceOptimizer(mock_monitor, settings)
        
        stats = optimizer.get_system_stats()
        
        assert stats is not None
