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


class TestCurveAdvancedEdgeCases:
    """Test advanced edge cases for curve expressions."""

    def test_curve_with_zero_steps(self):
        """Test curve expansion with zero steps."""
        expr = CurveExpression(
            start_value=0, end_value=127, curve_type="linear", control_points=None
        )
        # Zero steps should return empty list
        values = expand_curve_expression(expr, num_steps=0)
        assert len(values) == 0

    def test_curve_with_negative_values(self):
        """Test curve with negative start/end values."""
        expr = CurveExpression(
            start_value=-100, end_value=50, curve_type="linear", control_points=None
        )
        values = expand_curve_expression(expr, num_steps=10, min_val=0, max_val=127)
        # Values should be clamped to [0, 127]
        assert all(0 <= v <= 127 for v in values)
        assert values[0] == 0  # -100 clamped to 0

    def test_curve_with_very_large_values(self):
        """Test curve with values far exceeding MIDI range."""
        expr = CurveExpression(
            start_value=1000, end_value=2000, curve_type="linear", control_points=None
        )
        values = expand_curve_expression(expr, num_steps=10, min_val=0, max_val=127)
        # All values should be clamped to max
        assert all(v == 127 for v in values)

    def test_curve_with_large_step_count(self):
        """Test curve with very large number of steps."""
        expr = CurveExpression(
            start_value=0, end_value=127, curve_type="linear", control_points=None
        )
        values = expand_curve_expression(expr, num_steps=10000)
        assert len(values) == 10000
        # First and last should still be correct
        assert values[0] == 0
        assert values[-1] == 127

    def test_curve_with_inverted_range(self):
        """Test curve where start > end."""
        expr = CurveExpression(
            start_value=127, end_value=0, curve_type="ease-in", control_points=None
        )
        values = expand_curve_expression(expr, num_steps=10)
        # Should decrease monotonically
        assert values[0] == 127
        assert values[-1] == 0
        for i in range(len(values) - 1):
            assert values[i] >= values[i + 1]

    def test_curve_with_same_start_and_end(self):
        """Test curve where start equals end (constant)."""
        expr = CurveExpression(
            start_value=64, end_value=64, curve_type="linear", control_points=None
        )
        values = expand_curve_expression(expr, num_steps=10)
        # All values should be close to 64 (within 1 due to interpolation rounding)
        assert all(abs(v - 64) <= 1 for v in values)

    def test_curve_bezier_with_none_control_points(self):
        """Test bezier curve with None control points (fallback to linear)."""
        expr = CurveExpression(
            start_value=0, end_value=127, curve_type="bezier", control_points=None
        )
        values = expand_curve_expression(expr, num_steps=10)
        # Should fallback to linear
        assert len(values) == 10
        assert values[0] == 0
        assert values[-1] == 127

    def test_curve_with_custom_midi_range(self):
        """Test curve with non-standard MIDI range."""
        expr = CurveExpression(
            start_value=0, end_value=200, curve_type="linear", control_points=None
        )
        # Custom range: 10-100
        values = expand_curve_expression(expr, num_steps=10, min_val=10, max_val=100)
        # Values should be clamped to [10, 100]
        assert all(10 <= v <= 100 for v in values)


class TestWaveAdvancedEdgeCases:
    """Test advanced edge cases for wave expressions."""

    def test_wave_with_zero_depth(self):
        """Test wave with zero modulation depth."""
        expr = WaveExpression(wave_type="sine", base_value=64, frequency=1.0, phase=None, depth=0)
        values = expand_wave_expression(expr, duration_seconds=1.0, sample_rate=10)
        # All values should be at base value (no modulation)
        assert all(v == 64 for v in values)

    def test_wave_with_depth_over_100(self):
        """Test wave with depth > 100% (should clamp to range)."""
        expr = WaveExpression(wave_type="sine", base_value=64, frequency=1.0, phase=None, depth=200)
        values = expand_wave_expression(expr, duration_seconds=1.0, sample_rate=10)
        # Should clamp to MIDI range [0, 127]
        assert all(0 <= v <= 127 for v in values)

    def test_wave_with_base_value_outside_range(self):
        """Test wave with base value outside MIDI range."""
        expr = WaveExpression(wave_type="sine", base_value=150, frequency=1.0, phase=None, depth=50)
        values = expand_wave_expression(expr, duration_seconds=1.0, sample_rate=10)
        # Should clamp all values to [0, 127]
        assert all(0 <= v <= 127 for v in values)

    def test_wave_with_negative_base_value(self):
        """Test wave with negative base value."""
        expr = WaveExpression(wave_type="sine", base_value=-50, frequency=1.0, phase=None, depth=50)
        values = expand_wave_expression(expr, duration_seconds=1.0, sample_rate=10)
        # Should clamp to [0, 127]
        assert all(0 <= v <= 127 for v in values)

    def test_wave_with_zero_duration(self):
        """Test wave with zero duration."""
        expr = WaveExpression(wave_type="sine", base_value=64, frequency=1.0, phase=None, depth=50)
        values = expand_wave_expression(expr, duration_seconds=0.0, sample_rate=10)
        # Should return empty list
        assert len(values) == 0

    def test_wave_with_very_high_sample_rate(self):
        """Test wave with very high sample rate."""
        expr = WaveExpression(wave_type="sine", base_value=64, frequency=1.0, phase=None, depth=50)
        values = expand_wave_expression(expr, duration_seconds=0.1, sample_rate=10000)
        # Should generate 1000 samples (0.1s * 10000 Hz)
        assert len(values) == 1000
        assert all(0 <= v <= 127 for v in values)

    def test_wave_with_very_low_sample_rate(self):
        """Test wave with very low sample rate."""
        expr = WaveExpression(wave_type="sine", base_value=64, frequency=1.0, phase=None, depth=50)
        values = expand_wave_expression(expr, duration_seconds=1.0, sample_rate=1)
        # Should generate 1 sample
        assert len(values) == 1
        assert 0 <= values[0] <= 127

    def test_wave_with_phase_wrap_around(self):
        """Test wave with phase > 1.0 (should wrap around)."""
        expr = WaveExpression(wave_type="sine", base_value=64, frequency=1.0, phase=1.5, depth=50)
        values = expand_wave_expression(expr, duration_seconds=1.0, sample_rate=10)
        # Phase should wrap, still generate valid values
        assert len(values) == 10
        assert all(0 <= v <= 127 for v in values)

    def test_wave_with_custom_range(self):
        """Test wave with custom min/max range."""
        expr = WaveExpression(wave_type="sine", base_value=64, frequency=1.0, phase=None, depth=50)
        values = expand_wave_expression(
            expr, duration_seconds=1.0, sample_rate=10, min_val=20, max_val=100
        )
        # All values should be in custom range
        assert all(20 <= v <= 100 for v in values)


class TestEnvelopeAdvancedEdgeCases:
    """Test advanced edge cases for envelope expressions."""

    def test_envelope_ad_missing_decay(self):
        """Test AD envelope with missing decay parameter."""
        expr = EnvelopeExpression(
            envelope_type="ad", attack=0.1, decay=None, sustain=None, release=None, curve="linear"
        )
        with pytest.raises(ValueError, match="AD envelope requires"):
            expand_envelope_expression(expr, duration_seconds=1.0)

    def test_envelope_invalid_type(self):
        """Test envelope with invalid envelope type."""
        expr = EnvelopeExpression(
            envelope_type="invalid",
            attack=0.1,
            decay=0.2,
            sustain=0.7,
            release=0.3,
            curve="linear",
        )
        with pytest.raises(ValueError, match="Unknown envelope type"):
            expand_envelope_expression(expr, duration_seconds=1.0)

    def test_envelope_with_zero_duration(self):
        """Test envelope with zero duration."""
        expr = EnvelopeExpression(
            envelope_type="ar", attack=0.1, decay=None, sustain=None, release=0.3, curve="linear"
        )
        values = expand_envelope_expression(expr, duration_seconds=0.0, sample_rate=100)
        # Should return empty list
        assert len(values) == 0

    def test_envelope_with_very_long_duration(self):
        """Test envelope with very long duration."""
        expr = EnvelopeExpression(
            envelope_type="ar", attack=0.1, decay=None, sustain=None, release=0.3, curve="linear"
        )
        values = expand_envelope_expression(expr, duration_seconds=100.0, sample_rate=10)
        # Should generate 1000 samples (100s * 10 Hz)
        assert len(values) == 1000
        # Most values should be zero (after release completes at 0.4s)
        assert values[-1] == 0

    def test_envelope_with_very_low_sample_rate(self):
        """Test envelope with very low sample rate (under-sampling)."""
        expr = EnvelopeExpression(
            envelope_type="ar", attack=0.1, decay=None, sustain=None, release=0.3, curve="linear"
        )
        # Use 1 second duration to get at least 1 sample (int(1.0 * 1) = 1)
        values = expand_envelope_expression(expr, duration_seconds=1.0, sample_rate=1)
        # Should generate at least 1 sample
        assert len(values) == 1
        # With sample rate 1 Hz, we get sample at t=0 (in attack phase)
        assert values[0] >= 0

    def test_envelope_adsr_with_early_note_off(self):
        """Test ADSR with note-off during attack phase."""
        expr = EnvelopeExpression(
            envelope_type="adsr",
            attack=1.0,  # Long attack
            decay=0.2,
            sustain=0.7,
            release=0.3,
            curve="linear",
        )
        # Note off at 0.5s (halfway through attack)
        # This should still work but might not be typical
        values = expand_envelope_expression(
            expr, duration_seconds=2.0, note_off_time=0.5, sample_rate=10
        )
        assert len(values) == 20
        assert all(0 <= v <= 127 for v in values)

    def test_envelope_with_custom_range(self):
        """Test envelope with custom min/max range."""
        expr = EnvelopeExpression(
            envelope_type="ar", attack=0.1, decay=None, sustain=None, release=0.3, curve="linear"
        )
        values = expand_envelope_expression(
            expr, duration_seconds=0.5, sample_rate=100, min_val=30, max_val=90
        )
        # All values should be in custom range
        assert all(30 <= v <= 90 for v in values)

    def test_envelope_adsr_with_zero_sustain(self):
        """Test ADSR with sustain level of 0."""
        expr = EnvelopeExpression(
            envelope_type="adsr",
            attack=0.1,
            decay=0.2,
            sustain=0.0,  # Zero sustain
            release=0.3,
            curve="linear",
        )
        values = expand_envelope_expression(expr, duration_seconds=1.0, sample_rate=100)
        # Should have some values during attack/decay, then 0 during sustain
        assert len(values) == 100
        # After decay phase (0.3s = 30 samples), should be at sustain (0)
        assert values[40] == 0  # During sustain

    def test_envelope_adsr_with_sustain_equal_to_peak(self):
        """Test ADSR with sustain level equal to peak (no decay)."""
        expr = EnvelopeExpression(
            envelope_type="adsr",
            attack=0.1,
            decay=0.2,
            sustain=1.0,  # Sustain at peak
            release=0.3,
            curve="linear",
        )
        values = expand_envelope_expression(expr, duration_seconds=1.0, sample_rate=100)
        # Peak should be reached and held
        peak_idx = 10  # 0.1s * 100 Hz
        # After attack, should stay at max
        assert values[peak_idx] == 127
        assert values[50] == 127  # Much later in sustain


class TestModulationContextHandling:
    """Test modulation expression expansion with various context configurations."""

    def test_curve_with_missing_num_steps(self):
        """Test curve expansion with missing num_steps (should use default)."""
        expr = CurveExpression(
            start_value=0, end_value=127, curve_type="linear", control_points=None
        )
        context = {"min_val": 0, "max_val": 127}
        # Should use default num_steps=10
        values = expand_modulation_expression(expr, context)
        assert len(values) == 10

    def test_wave_with_missing_duration(self):
        """Test wave expansion with missing duration (should use default)."""
        expr = WaveExpression(wave_type="sine", base_value=64, frequency=1.0, phase=None, depth=50)
        context = {"sample_rate": 10, "min_val": 0, "max_val": 127}
        # Should use default duration_seconds=1.0
        values = expand_modulation_expression(expr, context)
        assert len(values) == 10

    def test_envelope_with_missing_sample_rate(self):
        """Test envelope expansion with missing sample_rate (should use default)."""
        expr = EnvelopeExpression(
            envelope_type="ar", attack=0.1, decay=None, sustain=None, release=0.3, curve="linear"
        )
        context = {"duration_seconds": 1.0, "min_val": 0, "max_val": 127}
        # Should use default sample_rate=100.0
        values = expand_modulation_expression(expr, context)
        assert len(values) == 100

    def test_modulation_with_custom_midi_ranges(self):
        """Test all modulation types with custom MIDI ranges."""
        # Test curve
        curve_expr = CurveExpression(
            start_value=0, end_value=200, curve_type="linear", control_points=None
        )
        curve_values = expand_modulation_expression(
            curve_expr, {"num_steps": 10, "min_val": 10, "max_val": 100}
        )
        assert all(10 <= v <= 100 for v in curve_values)

        # Test wave
        wave_expr = WaveExpression(
            wave_type="sine", base_value=64, frequency=1.0, phase=None, depth=100
        )
        wave_values = expand_modulation_expression(
            wave_expr, {"duration_seconds": 1.0, "sample_rate": 10, "min_val": 20, "max_val": 80}
        )
        assert all(20 <= v <= 80 for v in wave_values)

        # Test envelope
        env_expr = EnvelopeExpression(
            envelope_type="ar", attack=0.1, decay=None, sustain=None, release=0.3, curve="linear"
        )
        env_values = expand_modulation_expression(
            env_expr, {"duration_seconds": 0.5, "sample_rate": 100, "min_val": 40, "max_val": 90}
        )
        assert all(40 <= v <= 90 for v in env_values)

    def test_envelope_with_note_off_in_context(self):
        """Test envelope expansion with note_off_time in context."""
        expr = EnvelopeExpression(
            envelope_type="adsr",
            attack=0.1,
            decay=0.2,
            sustain=0.7,
            release=0.3,
            curve="linear",
        )
        context = {
            "duration_seconds": 1.0,
            "sample_rate": 100,
            "note_off_time": 0.5,
            "min_val": 0,
            "max_val": 127,
        }
        values = expand_modulation_expression(expr, context)
        assert len(values) == 100
        # Should trigger release at note_off_time


class TestModulationIntegration:
    """Test integration scenarios with modulation expressions."""

    def test_multiple_curves_in_sequence(self):
        """Test generating multiple curves with different types."""
        curve_types = ["ease-in", "ease-out", "ease-in-out", "linear"]
        for curve_type in curve_types:
            expr = CurveExpression(
                start_value=0, end_value=127, curve_type=curve_type, control_points=None
            )
            values = expand_curve_expression(expr, num_steps=10)
            assert len(values) == 10
            assert values[0] == 0
            assert values[-1] == 127

    def test_multiple_wave_types(self):
        """Test all wave types produce valid output."""
        wave_types = ["sine", "triangle", "square", "sawtooth"]
        for wave_type in wave_types:
            expr = WaveExpression(
                wave_type=wave_type, base_value=64, frequency=1.0, phase=None, depth=50
            )
            values = expand_wave_expression(expr, duration_seconds=1.0, sample_rate=10)
            assert len(values) == 10
            assert all(0 <= v <= 127 for v in values)

    def test_multiple_envelope_types(self):
        """Test all envelope types produce valid output."""
        # Test ADSR
        adsr = EnvelopeExpression(
            envelope_type="adsr", attack=0.1, decay=0.2, sustain=0.7, release=0.3, curve="linear"
        )
        adsr_values = expand_envelope_expression(adsr, duration_seconds=1.0, sample_rate=100)
        assert len(adsr_values) == 100

        # Test AR
        ar = EnvelopeExpression(
            envelope_type="ar", attack=0.1, decay=None, sustain=None, release=0.3, curve="linear"
        )
        ar_values = expand_envelope_expression(ar, duration_seconds=0.5, sample_rate=100)
        assert len(ar_values) == 50

        # Test AD
        ad = EnvelopeExpression(
            envelope_type="ad", attack=0.1, decay=0.4, sustain=None, release=None, curve="linear"
        )
        ad_values = expand_envelope_expression(ad, duration_seconds=0.5, sample_rate=100)
        assert len(ad_values) == 50

    def test_curve_types_with_different_ranges(self):
        """Test that all curve types work with various value ranges."""
        test_ranges = [(0, 127), (20, 100), (64, 64), (127, 0), (-50, 200)]
        for start, end in test_ranges:
            expr = CurveExpression(
                start_value=start, end_value=end, curve_type="ease-in", control_points=None
            )
            values = expand_curve_expression(expr, num_steps=10)
            assert len(values) == 10
            # Values should be clamped to MIDI range
            assert all(0 <= v <= 127 for v in values)
