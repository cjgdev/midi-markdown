"""Code generation for various output formats.

This package contains generators for different output formats:
- MIDI files (.mid)
- JSON (diagnostics and inspection)
- Future: CSV, OSC, etc.
"""

from __future__ import annotations

from .midi_file import generate_midi_file

__all__ = ["generate_midi_file"]
