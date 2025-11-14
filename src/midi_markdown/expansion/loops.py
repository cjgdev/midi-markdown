"""
Loop implementation for MIDI Markup Language.

Provides @loop directive for repeating event sequences with:
- Iteration control (count)
- Timing intervals (beats, ticks, ms, BBT)
- Loop variables (LOOP_INDEX, LOOP_ITERATION, LOOP_COUNT)
- Scoped variable resolution

Phase 3 of Variables Implementation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .variables import SymbolTable


class IntervalType(Enum):
    """Types of intervals for loop spacing."""

    BEATS = "beats"
    TICKS = "ticks"
    MILLISECONDS = "ms"
    BBT = "bbt"  # Bars.Beats.Ticks


@dataclass
class LoopInterval:
    """Represents a loop timing interval."""

    value: float | tuple[int, int, int]  # float for beats/ticks/ms, tuple for BBT
    interval_type: IntervalType

    def to_ticks(self, ppq: int, tempo: float, time_signature: tuple[int, int] = (4, 4)) -> int:
        """
        Convert interval to absolute ticks.

        Args:
            ppq: Pulses per quarter note
            tempo: Current tempo in BPM
            time_signature: Time signature as (numerator, denominator) tuple

        Returns:
            Interval in MIDI ticks
        """
        if self.interval_type == IntervalType.BEATS:
            # 1 beat = 1 quarter note = ppq ticks
            return int(self.value * ppq)

        if self.interval_type == IntervalType.TICKS:
            return int(self.value)

        if self.interval_type == IntervalType.MILLISECONDS:
            # Convert ms to ticks: (ms / 1000) * (bpm / 60) * ppq
            seconds = self.value / 1000.0
            beats = seconds * (tempo / 60.0)
            return int(beats * ppq)

        if self.interval_type == IntervalType.BBT:
            # BBT format: (bars, beats, ticks)
            bars, beats, ticks = self.value
            # Use time signature numerator for beats per bar
            beats_per_bar = time_signature[0]
            total_beats = (bars * beats_per_bar) + beats
            return int((total_beats * ppq) + ticks)

        msg = f"Unknown interval type: {self.interval_type}"
        raise ValueError(msg)


@dataclass
class LoopCommand:
    """
    Represents a single command within a loop body.

    Stores the command tree/dict and timing information.
    """

    command: Any  # Command dict or tree from parser
    relative_time: int = 0  # Ticks relative to loop iteration start


@dataclass
class LoopDefinition:
    """
    Represents a complete @loop definition.

    Contains all information needed to expand a loop into events.
    """

    count: int  # Number of iterations
    interval: LoopInterval  # Spacing between iterations
    commands: list[LoopCommand] = field(default_factory=list)
    start_time: int = 0  # Absolute start time in ticks
    source_line: int = 0  # For error reporting


class LoopExpander:
    """
    Expands loop definitions into concrete MIDI events.

    Features:
    - Iterates loop count times
    - Applies interval spacing
    - Creates scoped symbol tables for each iteration
    - Provides loop variables: LOOP_INDEX, LOOP_ITERATION, LOOP_COUNT
    """

    def __init__(
        self,
        parent_symbols: SymbolTable,
        ppq: int = 480,
        tempo: float = 120.0,
        time_signature: tuple[int, int] = (4, 4),
    ):
        """
        Initialize loop expander.

        Args:
            parent_symbols: Parent symbol table for variable resolution
            ppq: Pulses per quarter note
            tempo: Current tempo in BPM
            time_signature: Time signature as (numerator, denominator) tuple
        """
        self.parent_symbols = parent_symbols
        self.ppq = ppq
        self.tempo = tempo
        self.time_signature = time_signature

    def expand(self, loop_def: LoopDefinition) -> list[dict]:
        """
        Expand a loop definition into a list of timed events.

        Args:
            loop_def: Loop definition to expand

        Returns:
            List of event dictionaries with absolute timing
        """
        expanded_events = []
        interval_ticks = loop_def.interval.to_ticks(self.ppq, self.tempo, self.time_signature)

        for iteration in range(loop_def.count):
            # Create scoped symbol table for this iteration
            iteration_symbols = SymbolTable(parent=self.parent_symbols)

            # Define loop variables (0-indexed)
            iteration_symbols.define("LOOP_INDEX", iteration, line=loop_def.source_line)
            iteration_symbols.define("LOOP_ITERATION", iteration + 1, line=loop_def.source_line)
            iteration_symbols.define("LOOP_COUNT", loop_def.count, line=loop_def.source_line)

            # Calculate base time for this iteration
            iteration_base_time = loop_def.start_time + (iteration * interval_ticks)

            # Process each command in the loop body
            for loop_cmd in loop_def.commands:
                # Calculate absolute time for this command
                event_time = iteration_base_time + loop_cmd.relative_time

                # Create event with resolved variables
                event = self._create_event(loop_cmd.command, event_time, iteration_symbols)

                if event:
                    expanded_events.append(event)

        return expanded_events

    def _create_event(self, command: Any, time: int, symbols: SymbolTable) -> dict | None:
        """
        Create an event from a command, resolving variables.

        Args:
            command: Command dict or tree from parser
            time: Absolute time in ticks
            symbols: Symbol table for variable resolution

        Returns:
            Event dictionary or None if command cannot be converted
        """
        # If command is already a dict (from parser), use it directly
        if isinstance(command, dict):
            event = command.copy()
            event["time"] = time

            # Resolve any variable references in the command
            return self._resolve_command_variables(event, symbols)

        # If command is a tree, it needs to be converted by the parser
        # For now, return None - this will be handled by EventGenerator integration
        return None

    def _resolve_command_variables(self, event: dict, symbols: SymbolTable) -> dict:
        """
        Recursively resolve variable references in an event dict.

        Args:
            event: Event dictionary potentially containing variable tuples
            symbols: Symbol table for resolution

        Returns:
            Event with all variables resolved
        """
        resolved = {}

        for key, value in event.items():
            if isinstance(value, tuple) and len(value) == 2 and value[0] == "var":
                # Variable reference tuple: ('var', 'NAME')
                try:
                    resolved[key] = symbols.resolve(value[1])
                except ValueError:
                    # Variable undefined - keep as tuple for later resolution
                    resolved[key] = value
            elif isinstance(value, dict):
                # Recursive resolution for nested dicts
                resolved[key] = self._resolve_command_variables(value, symbols)
            elif isinstance(value, list):
                # Resolve list items
                resolved[key] = [
                    self._resolve_command_variables(item, symbols)
                    if isinstance(item, dict)
                    else symbols.resolve(item[1])
                    if isinstance(item, tuple) and len(item) == 2 and item[0] == "var"
                    else item
                    for item in value
                ]
            else:
                resolved[key] = value

        return resolved


def parse_interval(interval_str: str | tuple) -> LoopInterval:
    """
    Parse an interval string or tuple into a LoopInterval object.

    Supported formats:
    - "2b" or "2 beats" -> 2 beats
    - "480t" or "480 ticks" -> 480 ticks
    - "500ms" -> 500 milliseconds
    - "1.2.0" -> 1 bar, 2 beats, 0 ticks (BBT)
    - (2.0, 'b') -> 2 beats (tuple from parser)
    - (500.0, 'ms') -> 500 milliseconds (tuple from parser)

    Args:
        interval_str: Interval specification string or (value, unit) tuple

    Returns:
        LoopInterval object

    Raises:
        ValueError: If format is invalid
    """
    # Handle tuple format from parser: (value, unit)
    if isinstance(interval_str, tuple):
        if len(interval_str) == 2:
            value, unit = interval_str
            # Convert tuple to string format: "value+unit"
            interval_str = f"{value}{unit}"
        else:
            msg = f"Invalid interval format: {interval_str}"
            raise ValueError(msg)

    interval_str = interval_str.strip().lower()

    # BBT format: digits.digits.digits (bars.beats.ticks)
    # Must have exactly 2 dots and all parts must be numeric to avoid matching decimal durations like "1.25b"
    if interval_str.count(".") == 2:
        parts = interval_str.split(".")
        # Ensure we have exactly 3 parts and all are numeric (no unit suffixes)
        if len(parts) == 3 and all(part.isdigit() for part in parts):
            try:
                bars = int(parts[0])
                beats = int(parts[1])
                ticks = int(parts[2])
                return LoopInterval(value=(bars, beats, ticks), interval_type=IntervalType.BBT)
            except ValueError:
                msg = f"Invalid BBT format: {interval_str}"
                raise ValueError(msg)

    # Milliseconds: ends with 'ms'
    if interval_str.endswith("ms"):
        try:
            value = float(interval_str[:-2])
            if value <= 0:
                msg = f"Duration must be positive, got {value}ms"
                raise ValueError(msg)
            return LoopInterval(value=value, interval_type=IntervalType.MILLISECONDS)
        except ValueError as e:
            if "positive" in str(e):
                raise  # Re-raise our custom error
            msg = f"Invalid milliseconds format: {interval_str}"
            raise ValueError(msg) from e

    # Ticks: ends with 't' or 'ticks'
    if interval_str.endswith(("t", "ticks")):
        suffix = "t" if interval_str.endswith("t") else "ticks"
        try:
            value = float(interval_str[: -len(suffix)].strip())
            if value <= 0:
                msg = f"Duration must be positive, got {value}t"
                raise ValueError(msg)
            return LoopInterval(value=value, interval_type=IntervalType.TICKS)
        except ValueError as e:
            if "positive" in str(e):
                raise  # Re-raise our custom error
            msg = f"Invalid ticks format: {interval_str}"
            raise ValueError(msg) from e

    # Beats: ends with 'b' or 'beats' or 'beat'
    if interval_str.endswith(("b", "beats", "beat")):
        suffix = (
            "b"
            if interval_str.endswith("b")
            else ("beats" if interval_str.endswith("beats") else "beat")
        )
        try:
            value = float(interval_str[: -len(suffix)].strip())
            if value <= 0:
                msg = f"Duration must be positive, got {value}b"
                raise ValueError(msg)
            return LoopInterval(value=value, interval_type=IntervalType.BEATS)
        except ValueError as e:
            if "positive" in str(e):
                raise  # Re-raise our custom error
            msg = f"Invalid beats format: {interval_str}"
            raise ValueError(msg) from e

    # Default: try to parse as number of beats
    try:
        value = float(interval_str)
        if value <= 0:
            msg = f"Duration must be positive, got {value}"
            raise ValueError(msg)
        return LoopInterval(value=value, interval_type=IntervalType.BEATS)
    except ValueError as e:
        if "positive" in str(e):
            raise  # Re-raise our custom error
        msg = f"Invalid interval format: {interval_str}"
        raise ValueError(msg) from e
