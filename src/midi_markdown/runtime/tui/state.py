"""Thread-safe state management for TUI.

This module provides the TUIState class for managing UI state updates from
multiple threads (main UI thread, scheduler thread, keyboard thread).
"""

from __future__ import annotations

import threading
from collections import deque
from dataclasses import dataclass
from typing import Any


@dataclass
class EventInfo:
    """Information about a MIDI event for display."""

    time_ms: float
    type: str
    channel: int
    data: str  # Human-readable data (e.g., "Note: C4, Velocity: 80")


class TUIState:
    """Thread-safe state container for TUI updates.

    This class manages all state that needs to be shared between threads:
    - Main UI thread: Reads state for rendering
    - Scheduler thread: Updates position and events
    - Keyboard thread: Updates playback state

    All public methods are thread-safe using a lock.
    """

    def __init__(self, total_duration_ms: float, initial_tempo: float, max_events: int = 20):
        """Initialize TUI state.

        Args:
            total_duration_ms: Total duration of playback in milliseconds
            initial_tempo: Initial tempo in BPM
            max_events: Maximum number of events to keep in history
        """
        self._lock = threading.Lock()

        # Playback state
        self._position_ms: float = 0.0
        self._position_ticks: int = 0
        self._tempo: float = initial_tempo
        self._state: str = "stopped"  # stopped, playing, paused
        self._total_duration_ms: float = total_duration_ms

        # Event history (fixed-size circular buffer)
        self._event_history: deque[EventInfo] = deque(maxlen=max_events)

    def update_position(self, position_ms: float, position_ticks: int) -> None:
        """Update current playback position.

        Args:
            position_ms: Current position in milliseconds
            position_ticks: Current position in ticks
        """
        with self._lock:
            self._position_ms = position_ms
            self._position_ticks = position_ticks

    def update_tempo(self, tempo: float) -> None:
        """Update current tempo.

        Args:
            tempo: Tempo in BPM
        """
        with self._lock:
            self._tempo = tempo

    def set_state(self, state: str) -> None:
        """Set playback state.

        Args:
            state: One of "stopped", "playing", "paused"
        """
        with self._lock:
            self._state = state

    def add_event(self, event_info: EventInfo) -> None:
        """Add event to history buffer.

        Args:
            event_info: Event information to add
        """
        with self._lock:
            self._event_history.append(event_info)

    def get_state_snapshot(self) -> dict[str, Any]:
        """Get atomic snapshot of current state.

        Returns:
            Dictionary with all state fields
        """
        with self._lock:
            return {
                "position_ms": self._position_ms,
                "position_ticks": self._position_ticks,
                "tempo": self._tempo,
                "state": self._state,
                "total_duration_ms": self._total_duration_ms,
                "event_history": list(self._event_history),  # Copy the deque
            }

    def clear_events(self) -> None:
        """Clear event history buffer."""
        with self._lock:
            self._event_history.clear()

    def reset(self) -> None:
        """Reset state to initial values."""
        with self._lock:
            self._position_ms = 0.0
            self._position_ticks = 0
            self._state = "stopped"
            self._event_history.clear()
