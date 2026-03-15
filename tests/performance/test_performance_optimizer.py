"""
Tests pour PerformanceOptimizer.
"""

import pytest
from src.core.performance_optimizer import PerformanceOptimizer


class TestPerformanceOptimizer:
    """Tests pour PerformanceOptimizer."""
    
    def test_optimizer_init(self):
        """Test l'initialisation de PerformanceOptimizer."""
        optimizer = PerformanceOptimizer()
        assert optimizer is not None
    
    def test_optimize_memory(self):
        """Test optimize_memory."""
        optimizer = PerformanceOptimizer()
        result = optimizer.optimize_memory(aggressive=False)
        assert isinstance(result, bool)
    
    def test_optimize_models(self):
        """Test optimize_models."""
        optimizer = PerformanceOptimizer()
        result = optimizer.optimize_models()
        assert isinstance(result, bool)
    
    def test_get_optimization_profile(self):
        """Test get_optimization_profile."""
        optimizer = PerformanceOptimizer()
        profile = optimizer.get_optimization_profile()
        assert isinstance(profile, dict)
