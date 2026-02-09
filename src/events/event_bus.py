"""Simple synchronous event bus for in-process events."""

from collections import defaultdict
from collections.abc import Callable
from typing import Any


class EventBus:
    """In-process pub/sub event bus."""

    def __init__(self) -> None:
        self._subs: dict[str, list[Callable[[Any], None]]] = defaultdict(list)

    def subscribe(self, event_name: str, fn: Callable[[Any], None]) -> None:
        """Register a subscriber callback for an event name."""
        self._subs[event_name].append(fn)

    def unsubscribe(self, event_name: str, fn: Callable[[Any], None]) -> None:
        """Unregister a subscriber callback if it exists."""
        subscribers = self._subs.get(event_name)
        if not subscribers:
            return
        try:
            subscribers.remove(fn)
        except ValueError:
            return
        if not subscribers:
            del self._subs[event_name]

    def publish(self, event_name: str, payload: Any = None) -> None:
        """Publish a payload to all subscribers in registration order."""
        for fn in list(self._subs.get(event_name, [])):
            fn(payload)
