"""Modulation expression expansion for enhanced parameter automation.

This module expands curve, wave, and envelope expressions into sequences of
MIDI CC messages over time. It works with the sweep expansion system to
generate smooth, natural-sounding parameter changes.

Phase 6 Stage 7 - Enhanced Modulation
"""

from __future__ import annotations

from typing import Any

from midi_markdown.parser.ast_nodes import (
    CurveExpression,
    EnvelopeExpression,
    WaveExpression,
)
from midi_markdown.utils.curves import (
    BezierCurve,
    create_ease_in_bezier,
    create_ease_in_out_bezier,
    create_ease_out_bezier,
    create_linear_bezier,
    scale_bezier_to_range,
)
from midi_markdown.utils.envelopes import (
    ADEnvelope,
    ADSREnvelope,
    AREnvelope,
    scale_envelope_to_range,
)
from midi_markdown.utils.waveforms import WaveGenerator


def expand_curve_expression(
    expr: CurveExpression, num_steps: int, min_val: float = 0.0, max_val: float = 127.0
) -> list[int]:
    """Expand a curve expression into a list of MIDI values.

    Args:
        expr: CurveExpression AST node
        num_steps: Number of interpolation steps to generate
        min_val: Minimum MIDI value (default: 0)
        max_val: Maximum MIDI value (default: 127)

    Returns:
        List of interpolated MIDI values (integers 0-127)

    Example:
        >>> expr = CurveExpression(0, 127, 'ease-in', None)
        >>> values = expand_curve_expression(expr, 10)
        >>> len(values)
        10
        >>> values[0]  # Start value
        0
        >>> values[-1]  # End value
        127
    """
    # Create the appropriate Bezier curve
    if expr.curve_type == "ease-in":
        normalized_curve = create_ease_in_bezier()
    elif expr.curve_type == "ease-out":
        normalized_curve = create_ease_out_bezier()
    elif expr.curve_type == "ease-in-out":
        normalized_curve = create_ease_in_out_bezier()
    elif expr.curve_type == "linear":
        normalized_curve = create_linear_bezier()
    elif expr.curve_type == "bezier" and expr.control_points:
        # Custom Bezier curve with explicit control points
        normalized_curve = BezierCurve(*expr.control_points)
    else:
        # Fallback to linear
        normalized_curve = create_linear_bezier()

    # Scale the normalized curve to the target range
    scaled_curve = scale_bezier_to_range(normalized_curve, expr.start_value, expr.end_value)

    # Generate interpolated values
    values = []
    for i in range(num_steps):
        t = i / (num_steps - 1) if num_steps > 1 else 0.0
        value = scaled_curve.interpolate(t)
        # Clamp to MIDI range and convert to int
        midi_value = int(max(min_val, min(max_val, value)))
        values.append(midi_value)

    return values


def expand_wave_expression(
    expr: WaveExpression,
    duration_seconds: float,
    sample_rate: float = 100.0,
    min_val: float = 0.0,
    max_val: float = 127.0,
) -> list[int]:
    """Expand a wave expression into a list of MIDI values over time.

    Args:
        expr: WaveExpression AST node
        duration_seconds: Total duration of the wave in seconds
        sample_rate: Samples per second (default: 100 Hz = 10ms resolution)
        min_val: Minimum MIDI value (default: 0)
        max_val: Maximum MIDI value (default: 127)

    Returns:
        List of MIDI values sampled at the given rate

    Example:
        >>> expr = WaveExpression('sine', 64, frequency=5.0)
        >>> values = expand_wave_expression(expr, 1.0, sample_rate=10)
        >>> len(values)  # 1 second at 10 Hz = 10 samples
        10
    """
    # Determine wave parameters
    frequency = expr.frequency if expr.frequency is not None else 1.0
    phase = expr.phase if expr.phase is not None else 0.0
    depth = expr.depth if expr.depth is not None else 50.0

    # Calculate min/max based on depth (percentage of range)
    value_range = max_val - min_val
    modulation_range = (depth / 100.0) * value_range
    wave_min = expr.base_value - modulation_range / 2
    wave_max = expr.base_value + modulation_range / 2

    # Clamp to MIDI range
    wave_min = max(min_val, wave_min)
    wave_max = min(max_val, wave_max)

    # Create wave generator
    wave = WaveGenerator(
        wave_type=expr.wave_type,
        frequency_hz=frequency,
        min_val=wave_min,
        max_val=wave_max,
        phase_offset=phase * 2.0 * 3.14159,  # Convert 0-1 to radians
    )

    # Generate samples
    num_samples = int(duration_seconds * sample_rate)
    values = []
    for i in range(num_samples):
        time_seconds = i / sample_rate
        value = wave.value_at_time(time_seconds)
        # Clamp and convert to int
        midi_value = int(max(min_val, min(max_val, value)))
        values.append(midi_value)

    return values


def expand_envelope_expression(
    expr: EnvelopeExpression,
    duration_seconds: float,
    note_off_time: float | None = None,
    sample_rate: float = 100.0,
    min_val: float = 0.0,
    max_val: float = 127.0,
) -> list[int]:
    """Expand an envelope expression into a list of MIDI values over time.

    Args:
        expr: EnvelopeExpression AST node
        duration_seconds: Total duration to sample
        note_off_time: Time when note off occurs (for ADSR/AR envelopes)
        sample_rate: Samples per second (default: 100 Hz = 10ms resolution)
        min_val: Minimum MIDI value (default: 0)
        max_val: Maximum MIDI value (default: 127)

    Returns:
        List of MIDI values sampled at the given rate

    Example:
        >>> expr = EnvelopeExpression('adsr', 0.1, 0.2, 0.7, 0.3, 'linear')
        >>> values = expand_envelope_expression(expr, 1.0, note_off_time=0.5)
        >>> len(values)  # 1 second at 100 Hz = 100 samples
        100
    """
    # Create the appropriate envelope
    if expr.envelope_type == "adsr":
        if (
            expr.attack is None
            or expr.decay is None
            or expr.sustain is None
            or expr.release is None
        ):
            msg = "ADSR envelope requires attack, decay, sustain, and release parameters"
            raise ValueError(msg)

        envelope: ADSREnvelope | AREnvelope | ADEnvelope = ADSREnvelope(
            attack_time=expr.attack,
            decay_time=expr.decay,
            sustain_level=expr.sustain,
            release_time=expr.release,
            curve_type=expr.curve,
            note_off_time=note_off_time,
        )

    elif expr.envelope_type == "ar":
        if expr.attack is None or expr.release is None:
            msg = "AR envelope requires attack and release parameters"
            raise ValueError(msg)

        envelope = AREnvelope(
            attack_time=expr.attack, release_time=expr.release, curve_type=expr.curve
        )

    elif expr.envelope_type == "ad":
        if expr.attack is None or expr.decay is None:
            msg = "AD envelope requires attack and decay parameters"
            raise ValueError(msg)

        envelope = ADEnvelope(attack_time=expr.attack, decay_time=expr.decay, curve_type=expr.curve)

    else:
        msg = f"Unknown envelope type: {expr.envelope_type}"
        raise ValueError(msg)

    # Generate samples
    num_samples = int(duration_seconds * sample_rate)
    values = []
    for i in range(num_samples):
        time_seconds = i / sample_rate
        # Scale envelope value (0-1 or 0-peak) to MIDI range
        value = scale_envelope_to_range(envelope, min_val, max_val, time_seconds)
        # Clamp and convert to int
        midi_value = int(max(min_val, min(max_val, value)))
        values.append(midi_value)

    return values


def expand_modulation_expression(
    expr: CurveExpression | WaveExpression | EnvelopeExpression, context: dict[str, Any]
) -> list[int]:
    """Expand any modulation expression based on sweep context.

    This is the main entry point called by the sweep expander. It determines
    the expression type and delegates to the appropriate expansion function.

    Args:
        expr: Modulation expression AST node
        context: Sweep context with timing information
            - 'num_steps': Number of interpolation steps
            - 'duration_seconds': Total duration in seconds
            - 'min_val': Minimum MIDI value (default: 0)
            - 'max_val': Maximum MIDI value (default: 127)
            - 'note_off_time': Optional note-off time for envelopes

    Returns:
        List of MIDI values to use at each sweep step

    Raises:
        TypeError: If expression type is unknown
    """
    min_val = context.get("min_val", 0.0)
    max_val = context.get("max_val", 127.0)

    if isinstance(expr, CurveExpression):
        num_steps = context.get("num_steps", 10)
        return expand_curve_expression(expr, num_steps, min_val, max_val)

    if isinstance(expr, WaveExpression):
        duration_seconds = context.get("duration_seconds", 1.0)
        sample_rate = context.get("sample_rate", 100.0)
        return expand_wave_expression(expr, duration_seconds, sample_rate, min_val, max_val)

    if isinstance(expr, EnvelopeExpression):
        duration_seconds = context.get("duration_seconds", 1.0)
        sample_rate = context.get("sample_rate", 100.0)
        note_off_time = context.get("note_off_time")
        return expand_envelope_expression(
            expr, duration_seconds, note_off_time, sample_rate, min_val, max_val
        )

    msg = f"Unknown modulation expression type: {type(expr)}"
    raise TypeError(msg)
