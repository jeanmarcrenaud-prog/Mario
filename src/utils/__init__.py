# Changez ceci :
# from .system_monitor import SystemMonitor

# En ceci :
# Lazy import to avoid torch dependency issues in tests
def __getattr__(name):
    if name == "SystemMonitor":
        from .system_monitor import SystemMonitor
        return SystemMonitor
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "SystemMonitor",
]
