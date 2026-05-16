# event_bus.py

import streamlit as st
from typing import Callable, Dict, List, Any

class EventBus:
    """A global event bus for cross-page communication."""

    def __init__(self):
        if "event_bus" not in st.session_state:
            st.session_state.event_bus = {
                "listeners": {},     # event_name → list of callbacks
                "queue": []          # queued events to process
            }

        self._listeners: Dict[str, List[Callable]] = st.session_state.event_bus["listeners"]
        self._queue: List[tuple] = st.session_state.event_bus["queue"]

    # -------------------------
    # Event registration
    # -------------------------
    def on(self, event_name: str, callback: Callable):
        """Register a callback for an event."""
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(callback)

    # -------------------------
    # Event emission
    # -------------------------
    def emit(self, event_name: str, payload: Any = None):
        """Emit an event with optional payload."""
        self._queue.append((event_name, payload))

    # -------------------------
    # Event processing
    # -------------------------
    def process(self):
        """Process all queued events."""
        while self._queue:
            event_name, payload = self._queue.pop(0)
            if event_name in self._listeners:
                for callback in self._listeners[event_name]:
                    callback(payload)


# Singleton accessor
def get_event_bus() -> EventBus:
    return EventBus()
