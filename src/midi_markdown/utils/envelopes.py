"""ADSR envelope generators for parameter automation.

This module provides ADSR (Attack-Decay-Sustain-Release) envelope generators
for creating dynamic parameter changes in MIDI automation. ADSR envelopes
are fundamental to synthesis and are commonly used for amplitude, filter
cutoff, and other parameter modulations.

Key Features:
- Classic ADSR envelope (Attack-Decay-Sustain-Release)
- AR envelope (Attack-Release, no sustain)
- AD envelope (Attack-Decay, no sustain or release)
- Configurable curve shapes (linear, exponential)
- Time-based interpolation
- Amplitude scaling

Usage:
    envelope = ADSREnvelope(
        attack_time=0.1,
        decay_time=0.2,
        sustain_level=0.7,
        release_time=0.3
    )
    value_at_attack = envelope.value_at_time(0.05)
    value_at_sustain = envelope.value_at_time(0.4)
"""

from __future__ import annotations

import math
from typing import Literal

CurveType = Literal["linear", "exponential"]


class ADSREnvelope:
    """ADSR (Attack-Decay-Sustain-Release) envelope generator.

    An ADSR envelope consists of four stages:
    1. Attack: Rise from 0 to peak (1.0) over attack_time
    2. Decay: Fall from peak to sustain_level over decay_time
    3. Sustain: Hold at sustain_level until note off
    4. Release: Fall from sustain_level to 0 over release_time

    Attributes:
        attack_time: Time to reach peak in seconds
        decay_time: Time to reach sustain level in seconds
        sustain_level: Level to hold during sustain (0.0-1.0)
        release_time: Time to fade to zero in seconds
        peak_level: Maximum level reached (default: 1.0)
        curve_type: Shape of envelope curves ('linear' or 'exponential')

    Example:
        >>> # Classic ADSR for filter cutoff
        >>> envelope = ADSREnvelope(
        ...     attack_time=0.1,
        ...     decay_time=0.2,
        ...     sustain_level=0.7,
        ...     release_time=0.3
        ... )
        >>> envelope.value_at_time(0.05)   # Mid-attack
        0.5
        >>> envelope.value_at_time(0.3)    # In sustain
        0.7
    """

    def __init__(
        self,
        attack_time: float,
        decay_time: float,
        sustain_level: float,
        release_time: float,
        peak_level: float = 1.0,
        curve_type: CurveType = "linear",
        note_off_time: float | None = None,
    ):
        """Initialize ADSR envelope.

        Args:
            attack_time: Attack duration in seconds (must be >= 0)
            decay_time: Decay duration in seconds (must be >= 0)
            sustain_level: Sustain level 0.0-1.0 (0 = silence, 1 = peak)
            release_time: Release duration in seconds (must be >= 0)
            peak_level: Maximum level at end of attack (default: 1.0)
            curve_type: Envelope curve shape (default: 'linear')
            note_off_time: Time when note off occurs (default: None = infinite sustain)

        Raises:
            ValueError: If time values are negative or sustain_level outside 0-1
        """
        if attack_time < 0:
            msg = f"Attack time must be >= 0, got {attack_time}"
            raise ValueError(msg)
        if decay_time < 0:
            msg = f"Decay time must be >= 0, got {decay_time}"
            raise ValueError(msg)
        if release_time < 0:
            msg = f"Release time must be >= 0, got {release_time}"
            raise ValueError(msg)
        if not 0.0 <= sustain_level <= 1.0:
            msg = f"Sustain level must be 0.0-1.0, got {sustain_level}"
            raise ValueError(msg)
        if curve_type not in ("linear", "exponential"):
            msg = f"Invalid curve_type '{curve_type}'. Must be 'linear' or 'exponential'"
            raise ValueError(msg)

        self.attack_time = float(attack_time)
        self.decay_time = float(decay_time)
        self.sustain_level = float(sustain_level)
        self.release_time = float(release_time)
        self.peak_level = float(peak_level)
        self.curve_type = curve_type
        self.note_off_time = float(note_off_time) if note_off_time is not None else None

    def value_at_time(self, time_seconds: float) -> float:
        """Calculate envelope value at a specific time.

        Args:
            time_seconds: Time in seconds since envelope start

        Returns:
            Envelope value (0.0-peak_level)

        Example:
            >>> env = ADSREnvelope(0.1, 0.2, 0.7, 0.3)
            >>> env.value_at_time(0.0)    # Start of attack
            0.0
            >>> env.value_at_time(0.1)    # End of attack (peak)
            1.0
            >>> env.value_at_time(0.3)    # End of decay (sustain)
            0.7
        """
        if time_seconds < 0:
            return 0.0

        # Attack phase: 0 → peak_level
        if time_seconds < self.attack_time:
            t = time_seconds / self.attack_time
            return self._apply_curve(0.0, self.peak_level, t)

        # Special case: exactly at attack boundary with zero attack
        if time_seconds == self.attack_time == 0:
            # Proceed to decay check
            pass
        elif time_seconds == self.attack_time:
            # At exact end of attack, check if decay is zero
            if self.decay_time == 0:
                return self.sustain_level * self.peak_level
            # Otherwise at peak
            return self.peak_level

        # Decay phase: peak_level → sustain_level
        decay_start = self.attack_time
        decay_end = self.attack_time + self.decay_time
        if time_seconds <= decay_end:
            if self.decay_time == 0:
                return self.sustain_level * self.peak_level
            t = (time_seconds - decay_start) / self.decay_time
            return self._apply_curve(self.peak_level, self.sustain_level * self.peak_level, t)

        # Sustain phase: hold at sustain_level
        sustain_value = self.sustain_level * self.peak_level
        if self.note_off_time is None:
            # Infinite sustain
            return sustain_value

        if time_seconds < self.note_off_time:
            # Still in sustain phase
            return sustain_value

        # Release phase: sustain_level → 0
        release_start = self.note_off_time
        release_end = self.note_off_time + self.release_time
        if time_seconds <= release_end:
            if self.release_time == 0:
                return 0.0
            t = (time_seconds - release_start) / self.release_time
            return self._apply_curve(sustain_value, 0.0, t)

        # After release: silence
        return 0.0

    def _apply_curve(self, start: float, end: float, t: float) -> float:
        """Apply curve shape to linear interpolation parameter.

        Args:
            start: Starting value
            end: Ending value
            t: Linear interpolation parameter (0.0-1.0)

        Returns:
            Interpolated value with curve applied
        """
        # Clamp t to [0, 1]
        t = max(0.0, min(1.0, t))

        if self.curve_type == "linear":
            # Linear interpolation
            return start + (end - start) * t
        # exponential
        # Exponential curve using natural exponential
        # For rising: use 1 - e^(-4t) for smooth acceleration
        # For falling: use e^(-4t) for smooth deceleration
        if end > start:
            # Rising exponential
            curved_t = 1.0 - math.exp(-4.0 * t)
        else:
            # Falling exponential
            curved_t = math.exp(-4.0 * t)
        return start + (end - start) * curved_t

    def set_note_off(self, time_seconds: float) -> None:
        """Set the time when note off occurs (triggers release phase).

        Args:
            time_seconds: Time in seconds when note off occurs

        Raises:
            ValueError: If note_off_time is before end of decay phase
        """
        min_time = self.attack_time + self.decay_time
        if time_seconds < min_time:
            msg = f"Note off time ({time_seconds}s) must be >= attack + decay ({min_time}s)"
            raise ValueError(msg)
        self.note_off_time = float(time_seconds)

    def total_duration(self) -> float | None:
        """Calculate total envelope duration.

        Returns:
            Total duration in seconds, or None if sustain is infinite
        """
        if self.note_off_time is None:
            return None
        return self.note_off_time + self.release_time

    def __repr__(self) -> str:
        """String representation of the envelope."""
        return (
            f"ADSREnvelope(attack={self.attack_time}s, "
            f"decay={self.decay_time}s, "
            f"sustain={self.sustain_level}, "
            f"release={self.release_time}s, "
            f"curve={self.curve_type})"
        )


class AREnvelope:
    """AR (Attack-Release) envelope generator (no sustain phase).

    An AR envelope is simpler than ADSR:
    1. Attack: Rise from 0 to peak over attack_time
    2. Release: Fall from peak to 0 over release_time

    This is useful for percussive sounds or parameter sweeps that
    don't need a sustain phase.

    Attributes:
        attack_time: Time to reach peak in seconds
        release_time: Time to fade to zero in seconds
        peak_level: Maximum level reached (default: 1.0)
        curve_type: Shape of envelope curves ('linear' or 'exponential')

    Example:
        >>> # Percussive envelope
        >>> envelope = AREnvelope(attack_time=0.01, release_time=0.5)
        >>> envelope.value_at_time(0.0)    # Start
        0.0
        >>> envelope.value_at_time(0.01)   # Peak
        1.0
        >>> envelope.value_at_time(0.26)   # Mid-release
        0.5
    """

    def __init__(
        self,
        attack_time: float,
        release_time: float,
        peak_level: float = 1.0,
        curve_type: CurveType = "linear",
    ):
        """Initialize AR envelope.

        Args:
            attack_time: Attack duration in seconds (must be >= 0)
            release_time: Release duration in seconds (must be >= 0)
            peak_level: Maximum level at end of attack (default: 1.0)
            curve_type: Envelope curve shape (default: 'linear')

        Raises:
            ValueError: If time values are negative or invalid curve_type
        """
        if attack_time < 0:
            msg = f"Attack time must be >= 0, got {attack_time}"
            raise ValueError(msg)
        if release_time < 0:
            msg = f"Release time must be >= 0, got {release_time}"
            raise ValueError(msg)
        if curve_type not in ("linear", "exponential"):
            msg = f"Invalid curve_type '{curve_type}'. Must be 'linear' or 'exponential'"
            raise ValueError(msg)

        self.attack_time = float(attack_time)
        self.release_time = float(release_time)
        self.peak_level = float(peak_level)
        self.curve_type = curve_type

    def value_at_time(self, time_seconds: float) -> float:
        """Calculate envelope value at a specific time.

        Args:
            time_seconds: Time in seconds since envelope start

        Returns:
            Envelope value (0.0-peak_level)
        """
        if time_seconds < 0:
            return 0.0

        # Attack phase
        if time_seconds < self.attack_time:
            t = time_seconds / self.attack_time
            return self._apply_curve(0.0, self.peak_level, t)

        # At exact end of attack
        if time_seconds == self.attack_time:
            if self.release_time == 0:
                return 0.0
            return self.peak_level

        # Release phase
        release_end = self.attack_time + self.release_time
        if time_seconds <= release_end:
            if self.release_time == 0:
                return 0.0
            t = (time_seconds - self.attack_time) / self.release_time
            return self._apply_curve(self.peak_level, 0.0, t)

        # After release
        return 0.0

    def _apply_curve(self, start: float, end: float, t: float) -> float:
        """Apply curve shape to linear interpolation parameter."""
        t = max(0.0, min(1.0, t))

        if self.curve_type == "linear":
            return start + (end - start) * t
        # exponential
        curved_t = 1.0 - math.exp(-4.0 * t) if end > start else math.exp(-4.0 * t)
        return start + (end - start) * curved_t

    def total_duration(self) -> float:
        """Calculate total envelope duration."""
        return self.attack_time + self.release_time

    def __repr__(self) -> str:
        """String representation of the envelope."""
        return (
            f"AREnvelope(attack={self.attack_time}s, "
            f"release={self.release_time}s, "
            f"curve={self.curve_type})"
        )


class ADEnvelope:
    """AD (Attack-Decay) envelope generator (no sustain or release).

    An AD envelope is even simpler:
    1. Attack: Rise from 0 to peak over attack_time
    2. Decay: Fall from peak to end_level over decay_time

    This is useful for one-shot parameter changes or short modulations.

    Attributes:
        attack_time: Time to reach peak in seconds
        decay_time: Time to reach end_level in seconds
        peak_level: Maximum level reached (default: 1.0)
        end_level: Final level at end of decay (default: 0.0)
        curve_type: Shape of envelope curves ('linear' or 'exponential')

    Example:
        >>> # Quick filter sweep
        >>> envelope = ADEnvelope(attack_time=0.1, decay_time=0.4)
        >>> envelope.value_at_time(0.1)    # Peak
        1.0
        >>> envelope.value_at_time(0.5)    # End
        0.0
    """

    def __init__(
        self,
        attack_time: float,
        decay_time: float,
        peak_level: float = 1.0,
        end_level: float = 0.0,
        curve_type: CurveType = "linear",
    ):
        """Initialize AD envelope.

        Args:
            attack_time: Attack duration in seconds (must be >= 0)
            decay_time: Decay duration in seconds (must be >= 0)
            peak_level: Maximum level at end of attack (default: 1.0)
            end_level: Final level at end of decay (default: 0.0)
            curve_type: Envelope curve shape (default: 'linear')

        Raises:
            ValueError: If time values are negative or invalid curve_type
        """
        if attack_time < 0:
            msg = f"Attack time must be >= 0, got {attack_time}"
            raise ValueError(msg)
        if decay_time < 0:
            msg = f"Decay time must be >= 0, got {decay_time}"
            raise ValueError(msg)
        if curve_type not in ("linear", "exponential"):
            msg = f"Invalid curve_type '{curve_type}'. Must be 'linear' or 'exponential'"
            raise ValueError(msg)

        self.attack_time = float(attack_time)
        self.decay_time = float(decay_time)
        self.peak_level = float(peak_level)
        self.end_level = float(end_level)
        self.curve_type = curve_type

    def value_at_time(self, time_seconds: float) -> float:
        """Calculate envelope value at a specific time.

        Args:
            time_seconds: Time in seconds since envelope start

        Returns:
            Envelope value (between end_level and peak_level)
        """
        if time_seconds < 0:
            return self.end_level

        # Attack phase
        if time_seconds < self.attack_time:
            t = time_seconds / self.attack_time
            return self._apply_curve(self.end_level, self.peak_level, t)

        # At exact end of attack
        if time_seconds == self.attack_time:
            if self.decay_time == 0:
                return self.end_level
            return self.peak_level

        # Decay phase
        decay_end = self.attack_time + self.decay_time
        if time_seconds <= decay_end:
            if self.decay_time == 0:
                return self.end_level
            t = (time_seconds - self.attack_time) / self.decay_time
            return self._apply_curve(self.peak_level, self.end_level, t)

        # After decay
        return self.end_level

    def _apply_curve(self, start: float, end: float, t: float) -> float:
        """Apply curve shape to linear interpolation parameter."""
        t = max(0.0, min(1.0, t))

        if self.curve_type == "linear":
            return start + (end - start) * t
        # exponential
        curved_t = 1.0 - math.exp(-4.0 * t) if end > start else math.exp(-4.0 * t)
        return start + (end - start) * curved_t

    def total_duration(self) -> float:
        """Calculate total envelope duration."""
        return self.attack_time + self.decay_time

    def __repr__(self) -> str:
        """String representation of the envelope."""
        return (
            f"ADEnvelope(attack={self.attack_time}s, "
            f"decay={self.decay_time}s, "
            f"curve={self.curve_type})"
        )


def scale_envelope_to_range(
    envelope: ADSREnvelope | AREnvelope | ADEnvelope,
    min_val: float,
    max_val: float,
    time_seconds: float,
) -> float:
    """Scale envelope value to a specific range at given time.

    Takes an envelope (normalized 0-1 or 0-peak) and scales its value
    at a specific time to a target min/max range. This is useful for
    applying envelopes to MIDI parameters.

    Args:
        envelope: Any envelope instance (ADSR, AR, or AD)
        min_val: Minimum value of the target range
        max_val: Maximum value of the target range
        time_seconds: Time to sample the envelope

    Returns:
        Scaled envelope value in target range

    Example:
        >>> env = ADSREnvelope(0.1, 0.2, 0.7, 0.3)
        >>> # Scale to MIDI CC range (0-127)
        >>> scale_envelope_to_range(env, 0, 127, 0.1)  # Peak
        127.0
        >>> scale_envelope_to_range(env, 0, 127, 0.3)  # Sustain
        88.9
    """
    normalized_value = envelope.value_at_time(time_seconds)
    value_range = max_val - min_val
    return min_val + normalized_value * value_range
