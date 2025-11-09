# src/events/event_bus.py
```
"""Simple synchronous event bus for in‑process events."""
from collections import defaultdict

class EventBus:
    def __init__(self):
        self._subs = defaultdict(list)

    def subscribe(self, event_name: str, fn):
        self._subs[event_name].append(fn)

    def publish(self, event_name: str, payload=None):
        for fn in self._subs.get(event_name, []):
            fn(payload)