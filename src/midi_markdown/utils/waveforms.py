"""Waveform generators for LFO (Low Frequency Oscillator) effects.

This module provides waveform generators for creating periodic modulation
patterns commonly used in synthesizers and MIDI automation. It supports
four standard waveform types: sine, triangle, square, and sawtooth.

Key Features:
- Sine wave: smooth, natural modulation
- Triangle wave: linear rising/falling
- Square wave: binary on/off switching
- Sawtooth wave: linear ramp up or down
- Frequency specification in Hz
- Phase offset support
- Amplitude and DC offset control

Usage:
    wave = WaveGenerator('sine', frequency_hz=2.0, min_val=0, max_val=127)
    value_at_0s = wave.value_at_time(0.0)
    value_at_0_25s = wave.value_at_time(0.25)
"""

from __future__ import annotations

import math
from typing import Literal

WaveType = Literal["sine", "triangle", "square", "sawtooth"]


class WaveGenerator:
    """Generate periodic waveforms for LFO modulation effects.

    This class creates periodic waveforms suitable for MIDI automation,
    such as vibrato (pitch modulation), tremolo (amplitude modulation),
    and filter sweeps.

    Attributes:
        wave_type: Type of waveform ('sine', 'triangle', 'square', 'sawtooth')
        frequency_hz: Frequency in Hertz (cycles per second)
        min_val: Minimum value of the waveform
        max_val: Maximum value of the waveform
        phase_offset: Phase offset in radians (0 to 2π)

    Example:
        >>> # Create a 2Hz sine wave oscillating between 0 and 127
        >>> wave = WaveGenerator('sine', 2.0, 0, 127)
        >>> wave.value_at_time(0.0)    # Start of cycle
        63.5
        >>> wave.value_at_time(0.125)  # 1/8 of a second (quarter cycle)
        127.0
        >>> wave.value_at_time(0.25)   # Half cycle
        63.5
    """

    def __init__(
        self,
        wave_type: WaveType,
        frequency_hz: float,
        min_val: float,
        max_val: float,
        phase_offset: float = 0.0,
    ):
        """Initialize waveform generator.

        Args:
            wave_type: Type of waveform ('sine', 'triangle', 'square', 'sawtooth')
            frequency_hz: Frequency in Hertz (must be > 0)
            min_val: Minimum value of the waveform
            max_val: Maximum value of the waveform
            phase_offset: Phase offset in radians (default: 0.0)

        Raises:
            ValueError: If frequency_hz <= 0 or invalid wave_type
        """
        if frequency_hz <= 0:
            msg = f"Frequency must be positive, got {frequency_hz}"
            raise ValueError(msg)

        if wave_type not in ("sine", "triangle", "square", "sawtooth"):
            msg = (
                f"Invalid wave_type '{wave_type}'. "
                "Must be 'sine', 'triangle', 'square', or 'sawtooth'"
            )
            raise ValueError(msg)

        self.wave_type = wave_type
        self.frequency_hz = float(frequency_hz)
        self.min_val = float(min_val)
        self.max_val = float(max_val)
        self.phase_offset = float(phase_offset)

        # Precompute amplitude and DC offset for efficiency
        self.amplitude = (max_val - min_val) / 2.0
        self.dc_offset = (max_val + min_val) / 2.0

    def value_at_time(self, time_seconds: float) -> float:
        """Calculate waveform value at a specific time.

        Args:
            time_seconds: Time in seconds (can be negative)

        Returns:
            Waveform value at the specified time

        Example:
            >>> wave = WaveGenerator('sine', 1.0, 0, 100)
            >>> wave.value_at_time(0.0)   # Start
            50.0
            >>> wave.value_at_time(0.25)  # Quarter cycle
            100.0
            >>> wave.value_at_time(0.5)   # Half cycle
            50.0
        """
        # Calculate phase: 2π * frequency * time + phase_offset
        phase = 2.0 * math.pi * self.frequency_hz * time_seconds + self.phase_offset

        # Generate waveform based on type
        if self.wave_type == "sine":
            normalized = self._sine_wave(phase)
        elif self.wave_type == "triangle":
            normalized = self._triangle_wave(phase)
        elif self.wave_type == "square":
            normalized = self._square_wave(phase)
        else:  # sawtooth
            normalized = self._sawtooth_wave(phase)

        # Scale to output range: DC_offset + amplitude * normalized
        return self.dc_offset + self.amplitude * normalized

    def _sine_wave(self, phase: float) -> float:
        """Generate sine wave value (-1 to +1) at given phase.

        Args:
            phase: Phase in radians

        Returns:
            Sine wave value in range [-1, 1]
        """
        return math.sin(phase)

    def _triangle_wave(self, phase: float) -> float:
        """Generate triangle wave value (-1 to +1) at given phase.

        Triangle wave is a linear ramp from -1 to +1 and back.
        Formula: 2 * |2 * (phase/(2π) - floor(phase/(2π) + 0.5))| - 1

        Args:
            phase: Phase in radians

        Returns:
            Triangle wave value in range [-1, 1]
        """
        # Normalize phase to [0, 1)
        t = (phase / (2.0 * math.pi)) % 1.0

        # Triangle: rise from -1 to +1 in first half, fall in second half
        if t < 0.5:
            # Rising: -1 to +1
            return 4.0 * t - 1.0
        # Falling: +1 to -1
        return 3.0 - 4.0 * t

    def _square_wave(self, phase: float) -> float:
        """Generate square wave value (-1 or +1) at given phase.

        Square wave alternates between -1 and +1.

        Args:
            phase: Phase in radians

        Returns:
            Square wave value: -1 or +1
        """
        # Normalize phase to [0, 1)
        t = (phase / (2.0 * math.pi)) % 1.0

        # Square: +1 for first half of cycle, -1 for second half
        return 1.0 if t < 0.5 else -1.0

    def _sawtooth_wave(self, phase: float) -> float:
        """Generate sawtooth wave value (-1 to +1) at given phase.

        Sawtooth wave is a linear ramp from -1 to +1.
        Formula: 2 * (phase/(2π) - floor(phase/(2π) + 0.5))

        Args:
            phase: Phase in radians

        Returns:
            Sawtooth wave value in range [-1, 1]
        """
        # Normalize phase to [0, 1)
        t = (phase / (2.0 * math.pi)) % 1.0

        # Sawtooth: linear ramp from -1 to +1
        return 2.0 * t - 1.0

    def period_seconds(self) -> float:
        """Get the period of the waveform in seconds.

        Returns:
            Period in seconds (1 / frequency)

        Example:
            >>> wave = WaveGenerator('sine', 2.0, 0, 127)
            >>> wave.period_seconds()
            0.5
        """
        return 1.0 / self.frequency_hz

    def __repr__(self) -> str:
        """String representation of the waveform generator."""
        return (
            f"WaveGenerator(type={self.wave_type}, "
            f"freq={self.frequency_hz}Hz, "
            f"range=[{self.min_val}, {self.max_val}], "
            f"phase={self.phase_offset:.2f})"
        )


def create_vibrato_wave(frequency_hz: float = 5.0, depth_cents: int = 50) -> WaveGenerator:
    """Create a sine wave for vibrato effect (pitch modulation).

    Vibrato is typically a sine wave modulating pitch at 5-7 Hz with
    a depth of 20-50 cents (hundredths of a semitone).

    Args:
        frequency_hz: Vibrato rate in Hz (default: 5.0, typical 5-7 Hz)
        depth_cents: Vibrato depth in cents (default: 50, typical 20-50)

    Returns:
        WaveGenerator configured for vibrato

    Note:
        For pitch bend, you'll need to scale cents to pitch bend range.
        Typical: ±2 semitones = ±8192 pitch bend units.
        Formula: pitch_bend_value = (cents / 200) * 8192

    Example:
        >>> vibrato = create_vibrato_wave(frequency_hz=6.0, depth_cents=30)
        >>> # Use with pitch bend (-8192 to +8192 range)
        >>> center = 8192  # Center pitch
        >>> # At time 0.0, vibrato is at center
    """
    # Convert cents to pitch bend range
    # ±depth_cents around center (8192)
    # depth_cents / 100 = semitones
    # ±2 semitones = ±8192 pitch bend units
    # So: depth_units = (depth_cents / 200) * 8192
    depth_units = (depth_cents / 200.0) * 8192.0

    return WaveGenerator(
        "sine",
        frequency_hz=frequency_hz,
        min_val=8192 - depth_units,  # Below center
        max_val=8192 + depth_units,  # Above center
        phase_offset=0.0,
    )


def create_tremolo_wave(frequency_hz: float = 4.0, depth_percent: int = 30) -> WaveGenerator:
    """Create a sine wave for tremolo effect (amplitude modulation).

    Tremolo is typically a sine wave modulating volume/amplitude at
    3-5 Hz with a depth of 20-50%.

    Args:
        frequency_hz: Tremolo rate in Hz (default: 4.0, typical 3-5 Hz)
        depth_percent: Tremolo depth as percentage (default: 30, typical 20-50%)

    Returns:
        WaveGenerator configured for tremolo

    Note:
        The waveform oscillates between (100-depth)% and 100% of full volume.
        For MIDI CC (0-127), this maps to a range around the target volume.

    Example:
        >>> tremolo = create_tremolo_wave(frequency_hz=4.5, depth_percent=40)
        >>> # At full volume (127), oscillates between 76 and 127
        >>> target_volume = 127
        >>> # Scale the wave to modulate around target volume
    """
    # Depth percentage determines how much below max we go
    # depth_percent=30 means oscillate from 70% to 100%
    min_percentage = 100 - depth_percent
    max_percentage = 100

    # Map to MIDI CC range (0-127)
    min_val = (min_percentage / 100.0) * 127.0
    max_val = (max_percentage / 100.0) * 127.0

    return WaveGenerator(
        "sine", frequency_hz=frequency_hz, min_val=min_val, max_val=max_val, phase_offset=0.0
    )


def create_lfo_wave(
    wave_type: WaveType, frequency_hz: float, min_val: float = 0.0, max_val: float = 127.0
) -> WaveGenerator:
    """Create a generic LFO (Low Frequency Oscillator) wave.

    This is a general-purpose LFO generator that can be used for any
    parameter modulation (filter cutoff, pan, effects parameters, etc.).

    Args:
        wave_type: Type of waveform ('sine', 'triangle', 'square', 'sawtooth')
        frequency_hz: LFO rate in Hz
        min_val: Minimum parameter value (default: 0)
        max_val: Maximum parameter value (default: 127)

    Returns:
        WaveGenerator configured as LFO

    Example:
        >>> # Filter sweep with triangle wave
        >>> lfo = create_lfo_wave('triangle', frequency_hz=0.5, min_val=20, max_val=110)
        >>> # Slow triangle wave for filter cutoff automation
    """
    return WaveGenerator(
        wave_type, frequency_hz=frequency_hz, min_val=min_val, max_val=max_val, phase_offset=0.0
    )
