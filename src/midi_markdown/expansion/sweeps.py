"""
Sweep implementation for MIDI Markup Language.

Provides @sweep directive for value interpolation with:
- Multiple interpolation curves (linear, exponential, logarithmic, ease-in/out)
- Time-based or step-based interpolation
- Support for any MIDI value parameter

Phase 3 of Variables Implementation.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum


class RampType(Enum):
    """Types of interpolation curves for sweeps."""

    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    LOGARITHMIC = "logarithmic"
    EASE_IN = "ease_in"
    EASE_OUT = "ease_out"
    EASE_IN_OUT = "ease_in_out"


@dataclass
class RampSpec:
    """
    Specification for an interpolation ramp.

    Defines how values should be interpolated between start and end.
    """

    ramp_type: RampType
    start_value: float
    end_value: float

    def interpolate(self, t: float) -> float:
        """
        Interpolate a value at position t.

        Args:
            t: Position in range [0.0, 1.0] where 0 = start, 1 = end

        Returns:
            Interpolated value
        """
        # Clamp t to [0, 1]
        t = max(0.0, min(1.0, t))

        if self.ramp_type == RampType.LINEAR:
            return self._linear(t)
        if self.ramp_type == RampType.EXPONENTIAL:
            return self._exponential(t)
        if self.ramp_type == RampType.LOGARITHMIC:
            return self._logarithmic(t)
        if self.ramp_type == RampType.EASE_IN:
            return self._ease_in(t)
        if self.ramp_type == RampType.EASE_OUT:
            return self._ease_out(t)
        if self.ramp_type == RampType.EASE_IN_OUT:
            return self._ease_in_out(t)
        # Fallback to linear
        return self._linear(t)

    def _linear(self, t: float) -> float:
        """Linear interpolation: y = start + (end - start) * t"""
        return self.start_value + (self.end_value - self.start_value) * t

    def _exponential(self, t: float) -> float:
        """
        Exponential interpolation: accelerates over time.
        Uses formula: start + (end - start) * t^2
        """
        return self.start_value + (self.end_value - self.start_value) * (t**2)

    def _logarithmic(self, t: float) -> float:
        """
        Logarithmic interpolation: decelerates over time.
        Uses formula: start + (end - start) * sqrt(t)
        """
        return self.start_value + (self.end_value - self.start_value) * math.sqrt(t)

    def _ease_in(self, t: float) -> float:
        """
        Ease-in interpolation: slow start, then accelerate.
        Uses cubic easing: t^3
        """
        return self.start_value + (self.end_value - self.start_value) * (t**3)

    def _ease_out(self, t: float) -> float:
        """
        Ease-out interpolation: fast start, then decelerate.
        Uses inverted cubic easing: 1 - (1-t)^3
        """
        t_inv = 1.0 - t
        return self.start_value + (self.end_value - self.start_value) * (1 - t_inv**3)

    def _ease_in_out(self, t: float) -> float:
        """
        Ease-in-out interpolation: slow start, accelerate middle, slow end.
        Uses smoothstep formula: 3t^2 - 2t^3
        """
        smooth_t = (3 * t * t) - (2 * t * t * t)
        return self.start_value + (self.end_value - self.start_value) * smooth_t


@dataclass
class SweepDefinition:
    """
    Represents a complete @sweep definition.

    Contains all information needed to expand a sweep into events.
    """

    command_type: str  # e.g., 'cc', 'pitch_bend', 'pressure'
    channel: int
    data1: int | None  # Controller number for CC, None for pitch bend/pressure
    ramp: RampSpec
    steps: int  # Number of intermediate values to generate
    interval_ticks: int  # Time between steps in MIDI ticks
    start_time: int = 0  # Absolute start time in ticks
    source_line: int = 0  # For error reporting


class SweepExpander:
    """
    Expands sweep definitions into concrete MIDI events.

    Features:
    - Generates interpolated values using specified ramp type
    - Creates evenly-spaced events over time
    - Rounds values to valid MIDI ranges
    """

    def __init__(self, ppq: int = 480):
        """
        Initialize sweep expander.

        Args:
            ppq: Pulses per quarter note (for time calculations)
        """
        self.ppq = ppq

    def expand(self, sweep_def: SweepDefinition) -> list[dict]:
        """
        Expand a sweep definition into a list of timed events.

        Args:
            sweep_def: Sweep definition to expand

        Returns:
            List of event dictionaries with absolute timing and interpolated values
        """
        events = []

        # Generate events for each step
        for step in range(sweep_def.steps + 1):  # +1 to include end value
            # Calculate position in range [0.0, 1.0]
            t = step / float(sweep_def.steps) if sweep_def.steps > 0 else 1.0

            # Interpolate value
            raw_value = sweep_def.ramp.interpolate(t)

            # Round and clamp to MIDI value range
            midi_value = self._clamp_midi_value(raw_value, sweep_def.command_type)

            # Calculate absolute time for this step
            event_time = sweep_def.start_time + (step * sweep_def.interval_ticks)

            # Create event based on command type
            event = self._create_event(
                command_type=sweep_def.command_type,
                channel=sweep_def.channel,
                data1=sweep_def.data1,
                value=midi_value,
                time=event_time,
            )

            if event:
                events.append(event)

        return events

    def _clamp_midi_value(self, value: float, command_type: str) -> int:
        """
        Clamp and round a value to valid MIDI range.

        Args:
            value: Raw interpolated value
            command_type: Type of MIDI command

        Returns:
            Value clamped to appropriate range and rounded to int
        """
        if command_type == "pitch_bend":
            # Pitch bend range: -8192 to +8191
            return int(max(-8192, min(8191, round(value))))
        # Standard MIDI values: 0-127
        return int(max(0, min(127, round(value))))

    def _create_event(
        self, command_type: str, channel: int, data1: int | None, value: int, time: int
    ) -> dict | None:
        """
        Create an event dictionary for a sweep step.

        Args:
            command_type: Type of MIDI command
            channel: MIDI channel (1-16)
            data1: First data byte (controller number for CC)
            value: Interpolated value
            time: Absolute time in ticks

        Returns:
            Event dictionary or None if invalid
        """
        event = {
            "type": command_type,
            "channel": channel,
            "time": time,
        }

        if command_type == "cc":
            # Control Change: data1 = controller, data2 = value
            if data1 is None:
                return None
            event["data1"] = data1
            event["data2"] = value

        elif command_type == "pitch_bend":
            # Pitch Bend: single value (-8192 to +8191)
            event["data1"] = value

        elif command_type == "pressure":
            # Channel Pressure: single value (0-127)
            event["data1"] = value

        else:
            # Unknown command type
            return None

        return event


def parse_ramp_type(ramp_str: str) -> RampType:
    """
    Parse a ramp type string into RampType enum.

    Supported formats:
    - "linear", "lin"
    - "exponential", "exp"
    - "logarithmic", "log"
    - "ease-in", "ease_in"
    - "ease-out", "ease_out"
    - "ease-in-out", "ease_in_out"

    Args:
        ramp_str: Ramp type string

    Returns:
        RampType enum value

    Raises:
        ValueError: If ramp type is invalid
    """
    ramp_str = ramp_str.strip().lower().replace("-", "_")

    ramp_map = {
        "linear": RampType.LINEAR,
        "lin": RampType.LINEAR,
        "exponential": RampType.EXPONENTIAL,
        "exp": RampType.EXPONENTIAL,
        "logarithmic": RampType.LOGARITHMIC,
        "log": RampType.LOGARITHMIC,
        "ease_in": RampType.EASE_IN,
        "easein": RampType.EASE_IN,
        "ease_out": RampType.EASE_OUT,
        "easeout": RampType.EASE_OUT,
        "ease_in_out": RampType.EASE_IN_OUT,
        "easeinout": RampType.EASE_IN_OUT,
    }

    if ramp_str in ramp_map:
        return ramp_map[ramp_str]
    msg = f"Invalid ramp type: {ramp_str}"
    raise ValueError(msg)


def parse_sweep_interval(
    interval_str: str | tuple,
    ppq: int = 480,
    tempo: float = 120.0,
    time_signature: tuple[int, int] = (4, 4),
) -> int:
    """
    Parse an interval string or tuple into MIDI ticks.

    Reuses interval parsing from loops module for consistency.

    Supported formats:
    - "2b" or "2 beats" -> 2 beats
    - "480t" or "480 ticks" -> 480 ticks
    - "500ms" -> 500 milliseconds
    - "1.2.0" -> 1 bar, 2 beats, 0 ticks (BBT)
    - (2.0, 'b') -> 2 beats (tuple from parser)
    - (500.0, 'ms') -> 500 milliseconds (tuple from parser)

    Args:
        interval_str: Interval specification string or (value, unit) tuple
        ppq: Pulses per quarter note
        tempo: Current tempo in BPM
        time_signature: Time signature as (numerator, denominator) tuple

    Returns:
        Interval in MIDI ticks

    Raises:
        ValueError: If format is invalid
    """
    # Import here to avoid circular dependency
    from .loops import parse_interval

    loop_interval = parse_interval(interval_str)
    return loop_interval.to_ticks(ppq, tempo, time_signature)
