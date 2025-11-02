import pytest
from unittest.mock import patch
from src.utils.system_monitor import SystemMonitor

def test_get_cpu_usage():
    monitor = SystemMonitor()
    with patch('psutil.cpu_percent', return_value=42.0):
        cpu_usage = monitor.get_cpu_usage()
        assert cpu_usage == 42.0

def test_get_memory_usage():
    monitor = SystemMonitor()
    mock_memory = type('Memory', (), {'percent': 75.5})
    with patch('psutil.virtual_memory', return_value=mock_memory):
        memory_usage = monitor.get_memory_usage()
        assert memory_usage == 75.5

def test_get_disk_usage():
    monitor = SystemMonitor()
    mock_disk_usage = type('DiskUsage', (), {'percent': 60.0})
    with patch('psutil.disk_usage', return_value=mock_disk_usage):
        disk_usage = monitor.get_disk_usage("/")
        assert disk_usage == 60.0

def test_get_system_info_text():
    info_text = SystemMonitor.get_system_info_text()
    assert isinstance(info_text, str)
    assert "DÉMARRAGE DE L'APPLICATION" in info_text

def test_get_system_stats():
    stats = SystemMonitor.get_system_stats()
    assert isinstance(stats, dict)
    assert "cpu_percent" in stats
    assert "memory_percent" in stats
