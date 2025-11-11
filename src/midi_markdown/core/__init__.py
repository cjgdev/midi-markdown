"""Core data structures and compilation logic.

This package contains the Intermediate Representation (IR) layer that sits
between the AST and output formats, enabling REPL, live playback, and diagnostics.
"""

from __future__ import annotations

from .compiler import compile_ast_to_ir
from .ir import EventType, IRProgram, MIDIEvent, create_ir_program, string_to_event_type

__all__ = [
    "EventType",
    "IRProgram",
    "MIDIEvent",
    "compile_ast_to_ir",
    "create_ir_program",
    "string_to_event_type",
]
