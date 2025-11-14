"""
Parameter Type Conversion Utilities

Provides functions to convert various parameter types (note names, percentages,
booleans) to MIDI values. Used by both the parser and alias system.
"""

from __future__ import annotations

from midi_markdown.constants import (
    MIDI_NOTE_MAX,
    MIDI_NOTE_MIN,
    SEMITONES_PER_OCTAVE,
)


def note_to_midi(note_name: str) -> int:
    """Convert note name (e.g., 'C4', 'D#5', 'Bb3') to MIDI number.

    Args:
        note_name: Note name with optional sharp (#) or flat (b) and octave.
                  Examples: 'C4', 'D#5', 'Bb3', 'F#2'

    Returns:
        MIDI note number (0-127), where C4 = 60

    Raises:
        ValueError: If note name is invalid or out of MIDI range

    Examples:
        >>> note_to_midi('C4')
        60
        >>> note_to_midi('C#4')
        61
        >>> note_to_midi('Db4')
        61
        >>> note_to_midi('A4')
        69
    """
    if not note_name:
        msg = "Note name cannot be empty"
        raise ValueError(msg)

    note_map = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}

    # Parse note name
    base_note = note_name[0].upper()

    if base_note not in note_map:
        msg = f"Invalid note name '{note_name}': base note must be A-G"
        raise ValueError(msg)

    octave_start = 1
    modifier = 0

    # Handle sharps/flats
    if len(note_name) > 1 and note_name[1] in "#b":
        octave_start = 2
        if note_name[1] == "#":
            modifier = 1
        else:  # flat
            modifier = -1

    # Get octave
    try:
        if octave_start >= len(note_name):
            msg = f"Invalid note name '{note_name}': missing octave number"
            raise ValueError(msg)

        octave_str = note_name[octave_start:]

        # Handle negative octaves (e.g., C-1)
        octave = int(octave_str) if octave_str.startswith("-") else int(octave_str)

    except ValueError:
        msg = f"Invalid note name '{note_name}': invalid octave '{note_name[octave_start:]}'"
        raise ValueError(msg)

    # Calculate MIDI number (C4 = MIDI_MIDDLE_C = 60)
    # MIDI numbers: C-1=0, C0=12, C1=24, ..., C4=60, ..., G9=127
    midi_num = note_map[base_note] + modifier + (octave + 1) * SEMITONES_PER_OCTAVE

    # Validate range
    if not (MIDI_NOTE_MIN <= midi_num <= MIDI_NOTE_MAX):
        msg = (
            f"Note '{note_name}' (MIDI {midi_num}) is out of valid MIDI range "
            f"[{MIDI_NOTE_MIN}-{MIDI_NOTE_MAX}]. Valid octave range is -1 to 9."
        )
        raise ValueError(msg)

    return midi_num


def percent_to_midi(value: int | float) -> int:
    """Convert percentage (0-100) to MIDI value (0-127).

    Args:
        value: Percentage value (0-100)

    Returns:
        MIDI value (0-127)

    Raises:
        ValueError: If value is not in range 0-100

    Examples:
        >>> percent_to_midi(0)
        0
        >>> percent_to_midi(50)
        63
        >>> percent_to_midi(75)
        95
        >>> percent_to_midi(100)
        127
    """
    try:
        numeric_value = float(value)
    except (ValueError, TypeError):
        msg = f"Invalid percent value '{value}': must be a number"
        raise ValueError(msg)

    if not (0 <= numeric_value <= 100):
        msg = f"Percent value {numeric_value} is out of valid range [0-100]"
        raise ValueError(msg)

    # Scale 0-100 to 0-127
    midi_value = int(numeric_value * 127 / 100)

    # Ensure we don't exceed MIDI max due to rounding
    return min(midi_value, 127)


def bool_to_midi(value: str | bool | int) -> int:
    """Convert boolean value to MIDI (0 or 127).

    Accepts various representations of true/false:
    - Boolean: True, False
    - Strings: "true", "false", "on", "off", "yes", "no", "1", "0" (case-insensitive)
    - Integers: 1 (true), 0 (false)

    Args:
        value: Boolean value in various formats

    Returns:
        127 for true values, 0 for false values

    Raises:
        ValueError: If value cannot be interpreted as boolean

    Examples:
        >>> bool_to_midi(True)
        127
        >>> bool_to_midi(False)
        0
        >>> bool_to_midi("on")
        127
        >>> bool_to_midi("OFF")
        0
        >>> bool_to_midi(1)
        127
        >>> bool_to_midi(0)
        0
    """
    # Handle actual boolean type
    if isinstance(value, bool):
        return 127 if value else 0

    # Handle integer type
    if isinstance(value, int):
        if value == 1:
            return 127
        if value == 0:
            return 0
        msg = f"Invalid boolean integer value {value}: must be 0 or 1"
        raise ValueError(msg)

    # Handle string type
    if isinstance(value, str):
        normalized = value.lower().strip()

        # True values
        if normalized in ("true", "on", "yes", "1"):
            return 127

        # False values
        if normalized in ("false", "off", "no", "0"):
            return 0

        msg = (
            f"Invalid boolean string '{value}': must be one of "
            f"true/false, on/off, yes/no, or 1/0 (case-insensitive)"
        )
        raise ValueError(msg)

    # Unknown type
    msg = f"Invalid boolean value type {type(value).__name__}: expected bool, int, or str"
    raise ValueError(msg)
