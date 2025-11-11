"""Terminal User Interface (TUI) for real-time MIDI playback visualization.

This package provides a live terminal UI with:
- Real-time event display
- Progress tracking
- Keyboard controls
- Thread-safe state management
"""

from __future__ import annotations

from .components import (
    render_controls,
    render_event_list,
    render_header,
    render_progress_bar,
    render_status_bar,
)
from .display import TUIDisplayManager
from .input import KeyboardInputHandler
from .state import TUIState

__all__ = [
    "KeyboardInputHandler",
    "TUIDisplayManager",
    "TUIState",
    "render_controls",
    "render_event_list",
    "render_header",
    "render_progress_bar",
    "render_status_bar",
]
