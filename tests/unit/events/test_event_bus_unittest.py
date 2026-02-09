import unittest

from src.events.event_bus import EventBus
from src.events.events import AUDIO_PLAYED, INTENT_DETECTED


class EventBusTests(unittest.TestCase):
    def test_publish_notifies_subscribers_in_order(self):
        bus = EventBus()
        seen = []

        bus.subscribe(INTENT_DETECTED, lambda payload: seen.append(("first", payload)))
        bus.subscribe(INTENT_DETECTED, lambda payload: seen.append(("second", payload)))

        bus.publish(INTENT_DETECTED, {"text": "bonjour"})

        self.assertEqual(
            seen,
            [
                ("first", {"text": "bonjour"}),
                ("second", {"text": "bonjour"}),
            ],
        )

    def test_unsubscribe_removes_callback(self):
        bus = EventBus()
        seen = []

        def on_audio(payload):
            seen.append(payload)

        bus.subscribe(AUDIO_PLAYED, on_audio)
        bus.unsubscribe(AUDIO_PLAYED, on_audio)
        bus.publish(AUDIO_PLAYED, "ok")

        self.assertEqual(seen, [])


if __name__ == "__main__":
    unittest.main()
