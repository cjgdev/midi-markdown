"""MIDI event representation and generation.

DEPRECATED: This module now re-exports from core.ir for backward compatibility.
New code should import directly from midi_markdown.core.ir instead.
"""

from __future__ import annotations

# Re-export from core for backward compatibility
from midi_markdown.core.ir import (
    EventType,
    IRProgram,
    MIDIEvent,
    create_ir_program,
    string_to_event_type,
)

__all__ = [
    "EventType",
    "IRProgram",
    "MIDIEvent",
    "create_ir_program",
    "string_to_event_type",
]
