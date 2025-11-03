"""
MIDI Markup Language (MML) AST Node Definitions

This module provides the data classes that represent the Abstract Syntax Tree (AST)
for parsed MML documents. These are simple, flat data structures designed for
ease of use and efficient processing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Timing:
    """Represents a timing specification in MML.

    Timing can be one of four types:
    - absolute: [mm:ss.mmm] format (e.g., [01:23.250])
    - musical: [bars.beats.ticks] format (e.g., [8.4.120])
    - relative: [+value unit] format (e.g., [+1b], [+500ms])
    - simultaneous: [@] - execute at same time as previous event
    """

    type: str  # 'absolute', 'musical', 'relative', 'simultaneous'
    value: Any  # Format depends on type - see docstring
    raw: str  # Original raw timing string for debugging


@dataclass
class MIDICommand:
    """Represents a MIDI command in the AST.

    This is a flexible structure that can represent any MIDI command type:
    - Channel voice: note_on, note_off, cc, pc, pitch_bend, etc.
    - System: sysex
    - Meta: tempo, marker, time_signature, etc.
    - Alias: calls to user-defined aliases
    """

    type: str  # Command type (e.g., 'note_on', 'control_change', 'program_change')
    channel: int | None = None  # MIDI channel (1-16)
    data1: int | None = None  # First data byte (e.g., note number, CC number)
    data2: int | None = None  # Second data byte (e.g., velocity, CC value)
    params: dict[str, Any] = field(default_factory=dict)  # Additional parameters
    timing: Timing | None = None  # Associated timing information
    source_line: int = 0  # Line number in source file for error reporting


@dataclass
class ConditionalBranch:
    """Represents a conditional branch in an alias definition (Stage 7).

    A conditional branch is part of an @if/@elif/@else structure within
    an alias. Each branch has an optional condition (None for @else) and
    a list of commands to execute if the condition is true.

    Example:
        @if {device} == "cortex"
          - pc {ch}.{preset}
        @elif {device} == "h90"
          - cc {ch}.71.{preset}
        @else
          - pc {ch}.{preset}
        @end
    """

    condition: dict[str, Any] | None  # Condition dict (None for @else branch)
    commands: list[
        str | MIDICommand | Timing | DefineStatement | SweepStatement
    ]  # Commands (may include define/sweep)
    branch_type: str  # 'if', 'elif', or 'else' for debugging


@dataclass
class DefineStatement:
    """Represents a @define statement within an alias.

    Used for creating alias-local variables that can be referenced
    with ${VAR_NAME} syntax within the same alias.

    Example:
        @define MIDI_VAL 100
        - cc {ch}.7.${MIDI_VAL}
    """

    name: str  # Variable name
    value: Any  # Expression, literal, or variable reference
    source_line: int = 0  # Line number for error reporting


@dataclass
class SweepStatement:
    """Represents a @sweep statement within an alias.

    Used for generating automated parameter ramps with timing.

    Example:
        @sweep from [0.0.0] to [+1000ms] every 50ms
          - cc {ch}.1.ramp(0, 127)
        @end
    """

    start_time: Timing | None  # Start timing (may be None for default)
    end_time: Timing | None  # End timing (may be None for default)
    interval: str  # Interval string (e.g., "50ms")
    commands: list[str | MIDICommand]  # Commands to sweep (with ramp expressions)
    source_line: int = 0  # Line number for error reporting


@dataclass
class AliasDefinition:
    """Represents an alias definition in MML.

    Aliases can be:
    - Simple: Single command template with parameter substitution
    - Macro: Multiple commands with full command blocks
    - Conditional: Macro with @if/@elif/@else branches (Stage 7)
    - Advanced: With @define and @sweep statements
    """

    name: str  # Alias name
    parameters: list[dict[str, Any]]  # Parameter definitions (name, type, range, etc.)
    commands: list[
        str | MIDICommand | Timing | DefineStatement | SweepStatement
    ]  # Commands to expand
    description: str | None = None  # Optional description for documentation
    computed_values: dict[str, str] = field(
        default_factory=dict
    )  # Computed parameter expressions (Stage 6)
    conditional_branches: list[ConditionalBranch] | None = None  # Conditional branches (Stage 7)
    is_macro: bool = False  # True if this is a macro alias (multi-command)
    has_conditionals: bool = False  # True if this alias uses conditional logic (Stage 7)


@dataclass
class Track:
    """Represents a track in multi-track mode.

    MML supports multi-track MIDI files where each track can be defined
    separately and merged during compilation.
    """

    name: str  # Track name
    channel: int | None = None  # Optional default channel for this track
    events: list[Any] = field(default_factory=list)  # Events in this track


@dataclass
class MMLDocument:
    """Represents a complete parsed MML document.

    This is the root of the AST and contains all parsed elements:
    - YAML frontmatter (metadata)
    - Import statements
    - Variable definitions (@define)
    - Alias definitions (@alias)
    - Tracks (in multi-track mode)
    - Events (MIDI commands with timing)
    - Additional metadata
    """

    frontmatter: dict[str, Any] = field(default_factory=dict)  # Parsed YAML frontmatter
    imports: list[str] = field(default_factory=list)  # @import paths
    defines: dict[str, Any] = field(default_factory=dict)  # @define variables
    aliases: dict[str, AliasDefinition] = field(default_factory=dict)  # @alias definitions
    tracks: list[Track] = field(default_factory=list)  # @track definitions
    events: list[Any] = field(default_factory=list)  # Top-level events
    metadata: dict[str, Any] = field(default_factory=dict)  # Additional metadata


# ============================================================================
# Utility Functions
# ============================================================================


def validate_midi_value(
    value: int, min_val: int = 0, max_val: int = 127, param_name: str = "value"
) -> bool:
    """Validate a MIDI value is in the correct range.

    Args:
        value: Value to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        param_name: Name of parameter for error messages

    Returns:
        True if valid

    Raises:
        ValueError: If value is out of range or not an integer
    """
    if not isinstance(value, int):
        raise ValueError(f"{param_name} must be an integer")
    if not (min_val <= value <= max_val):
        raise ValueError(f"{param_name} {value} out of range [{min_val}, {max_val}]")
    return True


def timing_to_ticks(
    timing: Timing, ppq: int = 480, tempo: int = 120, time_signature: tuple = (4, 4)
) -> int:
    """Convert a Timing object to absolute ticks.

    Args:
        timing: Timing object to convert
        ppq: Pulses per quarter note (resolution)
        tempo: Current tempo in BPM
        time_signature: Time signature as (numerator, denominator)

    Returns:
        Absolute tick value
    """
    if timing.type == "absolute":
        # Convert seconds to ticks
        seconds = timing.value
        microseconds_per_quarter = 60_000_000 / tempo
        ticks = int((seconds * 1_000_000) / microseconds_per_quarter * ppq)
        return ticks

    if timing.type == "musical":
        bar, beat, tick = timing.value
        # Calculate based on time signature
        beats_per_bar = time_signature[0]
        ticks = ((bar - 1) * beats_per_bar + (beat - 1)) * ppq + tick
        return ticks

    if timing.type == "relative":
        # Relative timing needs previous event context
        # This would be resolved during event generation
        return 0  # Placeholder

    if timing.type == "simultaneous":
        # Same tick as previous event
        return 0  # Placeholder

    return 0
