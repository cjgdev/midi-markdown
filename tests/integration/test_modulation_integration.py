"""Integration tests for modulation expressions.

This module tests the full pipeline from parsing MML code with modulation
expressions through transformation and expansion to final MIDI values.
"""

from __future__ import annotations

import pytest

from midi_markdown.expansion.modulation import (
    expand_curve_expression,
    expand_envelope_expression,
    expand_modulation_expression,
    expand_wave_expression,
)
from midi_markdown.parser.ast_nodes import (
    CurveExpression,
    EnvelopeExpression,
    WaveExpression,
)


class TestModulationExpansion:
    """Test expansion of modulation expressions."""

    def test_curve_expansion_produces_correct_range(self):
        """Test that curve expansion produces values in correct range."""
        expr = CurveExpression(
            start_value=0, end_value=127, curve_type="linear", control_points=None
        )

        values = expand_curve_expression(expr, num_steps=10)

        # All values should be in MIDI range
        assert all(0 <= v <= 127 for v in values)
        # Should start at 0 and end at 127
        assert values[0] == 0
        assert values[-1] == 127
        # Should be monotonically increasing
        for i in range(len(values) - 1):
            assert values[i] <= values[i + 1]

    def test_wave_expansion_produces_correct_range(self):
        """Test that wave expansion produces values in correct range."""
        expr = WaveExpression(wave_type="sine", base_value=64, frequency=1.0, phase=None, depth=50)

        values = expand_wave_expression(expr, duration_seconds=1.0, sample_rate=10)

        # All values should be in MIDI range
        assert all(0 <= v <= 127 for v in values)
        # Should have some variation
        assert len(set(values)) > 1
        # Should oscillate around base value
        assert min(values) < 64
        assert max(values) > 64

    def test_envelope_expansion_produces_correct_range(self):
        """Test that envelope expansion produces values in correct range."""
        expr = EnvelopeExpression(
            envelope_type="ar", attack=0.1, decay=None, sustain=None, release=0.3, curve="linear"
        )

        values = expand_envelope_expression(expr, duration_seconds=0.5, sample_rate=100)

        # All values should be in MIDI range
        assert all(0 <= v <= 127 for v in values)
        # Should start at 0
        assert values[0] == 0
        # Should reach peak during attack
        assert max(values) > 100


class TestCurveVariations:
    """Test different curve types produce expected behaviors."""

    def test_ease_in_vs_linear(self):
        """Test that ease-in curve is slower at start than linear."""
        ease_in = CurveExpression(0, 127, "ease-in", None)
        linear = CurveExpression(0, 127, "linear", None)

        ease_in_values = expand_curve_expression(ease_in, num_steps=10)
        linear_values = expand_curve_expression(linear, num_steps=10)

        # At midpoint, ease-in should be behind linear
        assert ease_in_values[5] < linear_values[5]

    def test_ease_out_vs_linear(self):
        """Test that ease-out curve is faster at start than linear."""
        ease_out = CurveExpression(0, 127, "ease-out", None)
        linear = CurveExpression(0, 127, "linear", None)

        ease_out_values = expand_curve_expression(ease_out, num_steps=10)
        linear_values = expand_curve_expression(linear, num_steps=10)

        # At midpoint, ease-out should be ahead of linear
        assert ease_out_values[5] > linear_values[5]

    def test_custom_bezier_curve(self):
        """Test custom Bezier curve with control points."""
        expr = CurveExpression(
            start_value=0, end_value=127, curve_type="bezier", control_points=(0, 40, 90, 127)
        )

        values = expand_curve_expression(expr, num_steps=20)

        # Should produce smooth interpolation
        assert len(values) == 20
        assert values[0] == 0
        assert values[-1] == 127
        # Should be monotonically increasing with these control points
        for i in range(len(values) - 1):
            assert values[i] <= values[i + 1]


class TestWaveVariations:
    """Test different wave types and parameters."""

    def test_different_wave_types(self):
        """Test that different wave types produce different patterns."""
        base = 64
        freq = 1.0

        sine = WaveExpression("sine", base, freq, None, 50)
        triangle = WaveExpression("triangle", base, freq, None, 50)
        square = WaveExpression("square", base, freq, None, 50)
        sawtooth = WaveExpression("sawtooth", base, freq, None, 50)

        sine_values = expand_wave_expression(sine, 1.0, 20)
        triangle_values = expand_wave_expression(triangle, 1.0, 20)
        square_values = expand_wave_expression(square, 1.0, 20)
        sawtooth_values = expand_wave_expression(sawtooth, 1.0, 20)

        # All should oscillate
        assert len(set(sine_values)) > 2
        assert len(set(triangle_values)) > 2
        assert len(set(sawtooth_values)) > 2

        # Square should have mostly 2 values
        assert len(set(square_values)) <= 4  # Allow for rounding

        # Patterns should be different
        assert sine_values != triangle_values
        assert sine_values != square_values

    def test_wave_frequency_effect(self):
        """Test that frequency affects oscillation rate."""
        slow_wave = WaveExpression("sine", 64, 0.5, None, 50)  # 0.5 Hz
        fast_wave = WaveExpression("sine", 64, 2.0, None, 50)  # 2.0 Hz

        slow_values = expand_wave_expression(slow_wave, 1.0, 100)
        fast_values = expand_wave_expression(fast_wave, 1.0, 100)

        # Count zero crossings (transitions through base value)
        def count_crossings(values, base):
            crossings = 0
            for i in range(len(values) - 1):
                if (values[i] <= base < values[i + 1]) or (values[i] >= base > values[i + 1]):
                    crossings += 1
            return crossings

        slow_crossings = count_crossings(slow_values, 64)
        fast_crossings = count_crossings(fast_values, 64)

        # Fast wave should have more crossings
        assert fast_crossings > slow_crossings

    def test_wave_depth_effect(self):
        """Test that depth parameter affects modulation range."""
        shallow = WaveExpression("sine", 64, 1.0, None, 20)  # 20% depth
        deep = WaveExpression("sine", 64, 1.0, None, 80)  # 80% depth

        shallow_values = expand_wave_expression(shallow, 1.0, 50)
        deep_values = expand_wave_expression(deep, 1.0, 50)

        shallow_range = max(shallow_values) - min(shallow_values)
        deep_range = max(deep_values) - min(deep_values)

        # Deep modulation should have larger range
        assert deep_range > shallow_range * 2


class TestEnvelopeVariations:
    """Test different envelope types and parameters."""

    def test_adsr_envelope_phases(self):
        """Test that ADSR envelope has all expected phases."""
        expr = EnvelopeExpression(
            envelope_type="adsr", attack=0.1, decay=0.1, sustain=0.7, release=0.2, curve="linear"
        )

        # Generate for full duration including release
        values = expand_envelope_expression(
            expr, duration_seconds=1.0, note_off_time=0.5, sample_rate=100
        )

        # Should have 100 samples
        assert len(values) == 100

        # Attack phase (0.0-0.1s, samples 0-9): rising
        assert values[0] == 0
        assert values[9] > values[0]

        # Decay phase (0.1-0.2s, samples 10-19): falling to sustain
        assert values[10] > values[19]

        # Sustain phase (0.2-0.5s, samples 20-49): relatively stable
        sustain_samples = values[25:45]
        sustain_variation = max(sustain_samples) - min(sustain_samples)
        assert sustain_variation < 20  # Should be relatively stable

        # Release phase (0.5-0.7s, samples 50-69): falling to 0
        assert values[50] > values[69]

    def test_ar_envelope_simple(self):
        """Test simple attack-release envelope."""
        expr = EnvelopeExpression(
            envelope_type="ar", attack=0.1, decay=None, sustain=None, release=0.2, curve="linear"
        )

        values = expand_envelope_expression(expr, duration_seconds=0.5, sample_rate=100)

        # Attack: 0-10 samples rising
        assert values[0] == 0
        assert values[10] > values[0]

        # Release: 10-30 samples falling
        assert values[10] > values[30]

    def test_ad_envelope_simple(self):
        """Test simple attack-decay envelope."""
        expr = EnvelopeExpression(
            envelope_type="ad", attack=0.1, decay=0.3, sustain=None, release=None, curve="linear"
        )

        values = expand_envelope_expression(expr, duration_seconds=0.5, sample_rate=100)

        # Attack: 0-10 samples rising
        assert values[0] == 0
        assert values[10] > values[0]

        # Decay: 10-40 samples falling
        assert values[10] > values[40]

    def test_exponential_vs_linear_envelope(self):
        """Test that exponential envelopes differ from linear."""
        linear_env = EnvelopeExpression("ar", 0.1, None, None, 0.2, "linear")
        exp_env = EnvelopeExpression("ar", 0.1, None, None, 0.2, "exponential")

        linear_values = expand_envelope_expression(linear_env, 0.5, sample_rate=100)
        exp_values = expand_envelope_expression(exp_env, 0.5, sample_rate=100)

        # Values should be different (exponential has different shape)
        assert linear_values != exp_values

        # Both should start at 0 and reach similar peaks
        assert linear_values[0] == exp_values[0] == 0
        assert abs(max(linear_values) - max(exp_values)) < 10


class TestGenericExpansion:
    """Test generic modulation expression expansion."""

    def test_expand_curve_via_generic_function(self):
        """Test expanding curve through generic dispatcher."""
        expr = CurveExpression(0, 127, "linear", None)
        context = {"num_steps": 10, "min_val": 0, "max_val": 127}

        values = expand_modulation_expression(expr, context)

        assert len(values) == 10
        assert values[0] == 0
        assert values[-1] == 127

    def test_expand_wave_via_generic_function(self):
        """Test expanding wave through generic dispatcher."""
        expr = WaveExpression("sine", 64, 1.0, None, 50)
        context = {"duration_seconds": 1.0, "sample_rate": 10, "min_val": 0, "max_val": 127}

        values = expand_modulation_expression(expr, context)

        assert len(values) == 10
        assert all(0 <= v <= 127 for v in values)

    def test_expand_envelope_via_generic_function(self):
        """Test expanding envelope through generic dispatcher."""
        expr = EnvelopeExpression("ar", 0.1, None, None, 0.3, "linear")
        context = {"duration_seconds": 0.5, "sample_rate": 100, "min_val": 0, "max_val": 127}

        values = expand_modulation_expression(expr, context)

        assert len(values) == 50
        assert all(0 <= v <= 127 for v in values)

    def test_unknown_expression_type_raises_error(self):
        """Test that unknown expression type raises TypeError."""
        expr = "not a modulation expression"
        context = {}

        with pytest.raises(TypeError, match="Unknown modulation expression type"):
            expand_modulation_expression(expr, context)  # type: ignore


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_curve_with_reversed_range(self):
        """Test curve with start > end (descending)."""
        expr = CurveExpression(127, 0, "linear", None)
        values = expand_curve_expression(expr, num_steps=10)

        # Should descend from 127 to 0
        assert values[0] == 127
        assert values[-1] == 0
        # Should be monotonically decreasing
        for i in range(len(values) - 1):
            assert values[i] >= values[i + 1]

    def test_curve_with_single_step(self):
        """Test curve with only one step."""
        expr = CurveExpression(0, 127, "linear", None)
        values = expand_curve_expression(expr, num_steps=1)

        assert len(values) == 1
        assert values[0] == 0  # At t=0

    def test_wave_with_very_low_frequency(self):
        """Test wave with very slow oscillation."""
        expr = WaveExpression("sine", 64, 0.1, None, 50)  # 0.1 Hz
        values = expand_wave_expression(expr, duration_seconds=1.0, sample_rate=20)

        # Should still generate valid values
        assert len(values) == 20
        assert all(0 <= v <= 127 for v in values)

    def test_envelope_with_very_short_duration(self):
        """Test envelope with minimal duration."""
        expr = EnvelopeExpression("ar", 0.01, None, None, 0.01, "linear")
        values = expand_envelope_expression(expr, duration_seconds=0.05, sample_rate=100)

        assert len(values) == 5
        assert all(0 <= v <= 127 for v in values)

    def test_modulation_clamping_to_midi_range(self):
        """Test that extreme values are clamped to MIDI range."""
        # Curve with values outside MIDI range
        expr = CurveExpression(-50, 200, "linear", None)
        values = expand_curve_expression(expr, num_steps=20, min_val=0, max_val=127)

        # All values should be clamped
        assert all(0 <= v <= 127 for v in values)
        assert values[0] == 0  # Clamped from -50
        assert values[-1] == 127  # Clamped from 200
