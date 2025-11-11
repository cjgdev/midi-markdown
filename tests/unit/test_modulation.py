"""Tests for modulation expression expansion.

This module tests the expansion of curve, wave, and envelope expressions
into sequences of MIDI values for parameter automation.
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


class TestCurveExpansion:
    """Test curve expression expansion."""

    def test_expand_ease_in_curve(self):
        """Test expanding an ease-in curve."""
        expr = CurveExpression(
            start_value=0, end_value=127, curve_type="ease-in", control_points=None
        )
        values = expand_curve_expression(expr, num_steps=10)

        assert len(values) == 10
        assert values[0] == 0  # Start
        assert values[-1] == 127  # End
        # Ease-in should be slower at start
        assert values[1] < 127 / 9

    def test_expand_ease_out_curve(self):
        """Test expanding an ease-out curve."""
        expr = CurveExpression(
            start_value=0, end_value=127, curve_type="ease-out", control_points=None
        )
        values = expand_curve_expression(expr, num_steps=10)

        assert len(values) == 10
        assert values[0] == 0
        assert values[-1] == 127
        # Ease-out should be faster at start
        assert values[1] > 127 / 9

    def test_expand_linear_curve(self):
        """Test expanding a linear curve."""
        expr = CurveExpression(
            start_value=0, end_value=100, curve_type="linear", control_points=None
        )
        values = expand_curve_expression(expr, num_steps=11)

        assert len(values) == 11
        assert values[0] == 0
        assert values[5] == 50  # Midpoint
        assert values[-1] == 100

    def test_expand_custom_bezier(self):
        """Test expanding a custom Bezier curve."""
        expr = CurveExpression(
            start_value=0, end_value=127, curve_type="bezier", control_points=(0, 40, 90, 127)
        )
        values = expand_curve_expression(expr, num_steps=10)

        assert len(values) == 10
        assert values[0] == 0
        assert values[-1] == 127

    def test_expand_reverse_curve(self):
        """Test expanding a curve with end < start."""
        expr = CurveExpression(
            start_value=127, end_value=0, curve_type="ease-in", control_points=None
        )
        values = expand_curve_expression(expr, num_steps=10)

        assert len(values) == 10
        assert values[0] == 127
        assert values[-1] == 0
        # Should be monotonically decreasing
        for i in range(len(values) - 1):
            assert values[i] >= values[i + 1]

    def test_expand_single_step(self):
        """Test expanding with a single step."""
        expr = CurveExpression(
            start_value=0, end_value=127, curve_type="linear", control_points=None
        )
        values = expand_curve_expression(expr, num_steps=1)

        assert len(values) == 1
        assert values[0] == 0  # At t=0


class TestWaveExpansion:
    """Test wave expression expansion."""

    def test_expand_sine_wave(self):
        """Test expanding a sine wave."""
        expr = WaveExpression(wave_type="sine", base_value=64, frequency=1.0, phase=None, depth=50)
        values = expand_wave_expression(expr, duration_seconds=1.0, sample_rate=10)

        assert len(values) == 10
        # Sine wave should oscillate around base value
        assert min(values) < 64
        assert max(values) > 64

    def test_expand_triangle_wave(self):
        """Test expanding a triangle wave."""
        expr = WaveExpression(
            wave_type="triangle", base_value=64, frequency=1.0, phase=None, depth=50
        )
        values = expand_wave_expression(expr, duration_seconds=1.0, sample_rate=10)

        assert len(values) == 10
        assert min(values) < 64
        assert max(values) > 64

    def test_expand_square_wave(self):
        """Test expanding a square wave."""
        expr = WaveExpression(
            wave_type="square", base_value=64, frequency=1.0, phase=None, depth=50
        )
        values = expand_wave_expression(expr, duration_seconds=1.0, sample_rate=10)

        assert len(values) == 10
        # Square wave should have only two distinct values
        unique_values = set(values)
        assert len(unique_values) <= 3  # Allow for rounding

    def test_expand_sawtooth_wave(self):
        """Test expanding a sawtooth wave."""
        expr = WaveExpression(
            wave_type="sawtooth", base_value=64, frequency=1.0, phase=None, depth=50
        )
        values = expand_wave_expression(expr, duration_seconds=1.0, sample_rate=10)

        assert len(values) == 10
        assert min(values) < 64
        assert max(values) > 64

    def test_wave_with_phase_offset(self):
        """Test wave with phase offset."""
        expr = WaveExpression(
            wave_type="sine",
            base_value=64,
            frequency=1.0,
            phase=0.25,  # 90 degree offset
            depth=50,
        )
        values = expand_wave_expression(expr, duration_seconds=1.0, sample_rate=10)

        assert len(values) == 10
        # With 90° phase, sine starts at peak instead of center
        assert values[0] > 64

    def test_wave_with_custom_depth(self):
        """Test wave with custom modulation depth."""
        expr = WaveExpression(
            wave_type="sine",
            base_value=64,
            frequency=1.0,
            phase=None,
            depth=20,  # Smaller depth
        )
        values = expand_wave_expression(expr, duration_seconds=1.0, sample_rate=10)

        # Range should be smaller with 20% depth
        value_range = max(values) - min(values)
        assert value_range < 50  # Less than 50% of full range

    def test_wave_high_frequency(self):
        """Test wave with high frequency."""
        expr = WaveExpression(
            wave_type="sine",
            base_value=64,
            frequency=10.0,  # 10 Hz
            phase=None,
            depth=50,
        )
        values = expand_wave_expression(expr, duration_seconds=1.0, sample_rate=100)

        # Should complete ~10 cycles
        assert len(values) == 100


class TestEnvelopeExpansion:
    """Test envelope expression expansion."""

    def test_expand_adsr_envelope(self):
        """Test expanding an ADSR envelope."""
        expr = EnvelopeExpression(
            envelope_type="adsr", attack=0.1, decay=0.2, sustain=0.7, release=0.3, curve="linear"
        )
        values = expand_envelope_expression(
            expr, duration_seconds=1.0, note_off_time=0.5, sample_rate=100
        )

        assert len(values) == 100
        # Should start at 0
        assert values[0] == 0
        # Should reach peak around t=0.1 (10 samples)
        assert values[10] > values[0]
        # Should be at sustain around t=0.3-0.5
        sustain_value = int(0.7 * 127)
        assert abs(values[40] - sustain_value) < 10

    def test_expand_ar_envelope(self):
        """Test expanding an AR envelope."""
        expr = EnvelopeExpression(
            envelope_type="ar", attack=0.1, decay=None, sustain=None, release=0.3, curve="linear"
        )
        values = expand_envelope_expression(expr, duration_seconds=0.5, sample_rate=100)

        assert len(values) == 50
        # Should start at 0
        assert values[0] == 0
        # Should reach peak around t=0.1
        peak_idx = 10
        assert values[peak_idx] > values[0]
        # Should be back to 0 at end
        assert values[-1] == 0

    def test_expand_ad_envelope(self):
        """Test expanding an AD envelope."""
        expr = EnvelopeExpression(
            envelope_type="ad", attack=0.1, decay=0.4, sustain=None, release=None, curve="linear"
        )
        values = expand_envelope_expression(expr, duration_seconds=0.5, sample_rate=100)

        assert len(values) == 50
        # Should start at 0
        assert values[0] == 0
        # Should reach peak around t=0.1
        assert values[10] > values[0]
        # Should decay back close to 0 (last sample at t=0.49, just before t=0.5 completion)
        assert values[-1] < 10  # Close to 0, allowing for sampling before completion

    def test_envelope_exponential_curve(self):
        """Test envelope with exponential curve."""
        expr = EnvelopeExpression(
            envelope_type="ar",
            attack=0.1,
            decay=None,
            sustain=None,
            release=0.3,
            curve="exponential",
        )
        values = expand_envelope_expression(expr, duration_seconds=0.5, sample_rate=100)

        assert len(values) == 50
        # Exponential attack should be different from linear
        assert values[5] != values[10] // 2

    def test_envelope_missing_parameters_adsr(self):
        """Test ADSR with missing parameters raises error."""
        expr = EnvelopeExpression(
            envelope_type="adsr",
            attack=0.1,
            decay=None,  # Missing!
            sustain=0.7,
            release=0.3,
            curve="linear",
        )

        with pytest.raises(ValueError, match="ADSR envelope requires"):
            expand_envelope_expression(expr, duration_seconds=1.0)

    def test_envelope_missing_parameters_ar(self):
        """Test AR with missing parameters raises error."""
        expr = EnvelopeExpression(
            envelope_type="ar",
            attack=0.1,
            decay=None,
            sustain=None,
            release=None,  # Missing!
            curve="linear",
        )

        with pytest.raises(ValueError, match="AR envelope requires"):
            expand_envelope_expression(expr, duration_seconds=1.0)


class TestModulationExpansion:
    """Test generic modulation expression expansion."""

    def test_expand_curve_via_generic(self):
        """Test expanding curve through generic function."""
        expr = CurveExpression(
            start_value=0, end_value=127, curve_type="linear", control_points=None
        )
        context = {"num_steps": 10, "min_val": 0, "max_val": 127}
        values = expand_modulation_expression(expr, context)

        assert len(values) == 10
        assert values[0] == 0
        assert values[-1] == 127

    def test_expand_wave_via_generic(self):
        """Test expanding wave through generic function."""
        expr = WaveExpression(wave_type="sine", base_value=64, frequency=1.0, phase=None, depth=50)
        context = {"duration_seconds": 1.0, "sample_rate": 10, "min_val": 0, "max_val": 127}
        values = expand_modulation_expression(expr, context)

        assert len(values) == 10

    def test_expand_envelope_via_generic(self):
        """Test expanding envelope through generic function."""
        expr = EnvelopeExpression(
            envelope_type="ar", attack=0.1, decay=None, sustain=None, release=0.3, curve="linear"
        )
        context = {"duration_seconds": 0.5, "sample_rate": 100, "min_val": 0, "max_val": 127}
        values = expand_modulation_expression(expr, context)

        assert len(values) == 50

    def test_expand_unknown_type_raises_error(self):
        """Test that unknown expression type raises TypeError."""
        expr = "not a modulation expression"
        context = {}

        with pytest.raises(TypeError, match="Unknown modulation expression type"):
            expand_modulation_expression(expr, context)  # type: ignore


class TestModulationEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_curve_clamping_to_midi_range(self):
        """Test that curve values are clamped to MIDI range."""
        expr = CurveExpression(
            start_value=-50,  # Below MIDI range
            end_value=200,  # Above MIDI range
            curve_type="linear",
            control_points=None,
        )
        values = expand_curve_expression(expr, num_steps=10, min_val=0, max_val=127)

        # All values should be within MIDI range
        assert all(0 <= v <= 127 for v in values)

    def test_wave_clamping_to_midi_range(self):
        """Test that wave values are clamped to MIDI range."""
        expr = WaveExpression(
            wave_type="sine",
            base_value=100,
            frequency=1.0,
            phase=None,
            depth=100,  # Large depth
        )
        values = expand_wave_expression(
            expr, duration_seconds=1.0, sample_rate=10, min_val=0, max_val=127
        )

        # All values should be within MIDI range
        assert all(0 <= v <= 127 for v in values)

    def test_envelope_short_duration(self):
        """Test envelope with very short duration."""
        expr = EnvelopeExpression(
            envelope_type="ar", attack=0.01, decay=None, sustain=None, release=0.01, curve="linear"
        )
        values = expand_envelope_expression(expr, duration_seconds=0.05, sample_rate=100)

        assert len(values) == 5
        assert all(0 <= v <= 127 for v in values)

    def test_wave_zero_frequency(self):
        """Test wave with very low frequency."""
        expr = WaveExpression(
            wave_type="sine",
            base_value=64,
            frequency=0.1,  # Very slow
            phase=None,
            depth=50,
        )
        values = expand_wave_expression(expr, duration_seconds=1.0, sample_rate=10)

        # Should still generate valid values
        assert len(values) == 10
        assert all(0 <= v <= 127 for v in values)
