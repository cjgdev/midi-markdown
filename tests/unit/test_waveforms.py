"""Tests for waveform generators (LFO effects).

This module tests the WaveGenerator class and related utility functions
for creating periodic modulation patterns in MIDI automation.
"""

from __future__ import annotations

import math

import pytest

from midi_markdown.utils.waveforms import (
    WaveGenerator,
    create_lfo_wave,
    create_tremolo_wave,
    create_vibrato_wave,
)


class TestWaveGeneratorBasics:
    """Test basic WaveGenerator functionality."""

    def test_create_sine_wave(self):
        """Test creating a sine wave generator."""
        wave = WaveGenerator("sine", frequency_hz=1.0, min_val=0, max_val=127)
        assert wave.wave_type == "sine"
        assert wave.frequency_hz == 1.0
        assert wave.min_val == 0.0
        assert wave.max_val == 127.0

    def test_create_triangle_wave(self):
        """Test creating a triangle wave generator."""
        wave = WaveGenerator("triangle", frequency_hz=2.0, min_val=0, max_val=100)
        assert wave.wave_type == "triangle"
        assert wave.frequency_hz == 2.0

    def test_create_square_wave(self):
        """Test creating a square wave generator."""
        wave = WaveGenerator("square", frequency_hz=0.5, min_val=0, max_val=127)
        assert wave.wave_type == "square"

    def test_create_sawtooth_wave(self):
        """Test creating a sawtooth wave generator."""
        wave = WaveGenerator("sawtooth", frequency_hz=3.0, min_val=0, max_val=127)
        assert wave.wave_type == "sawtooth"

    def test_invalid_wave_type(self):
        """Test that invalid wave type raises error."""
        with pytest.raises(ValueError, match="Invalid wave_type"):
            WaveGenerator("invalid", frequency_hz=1.0, min_val=0, max_val=127)

    def test_invalid_frequency(self):
        """Test that zero/negative frequency raises error."""
        with pytest.raises(ValueError, match="Frequency must be positive"):
            WaveGenerator("sine", frequency_hz=0.0, min_val=0, max_val=127)

        with pytest.raises(ValueError, match="Frequency must be positive"):
            WaveGenerator("sine", frequency_hz=-1.0, min_val=0, max_val=127)

    def test_phase_offset(self):
        """Test wave generator with phase offset."""
        wave = WaveGenerator(
            "sine", frequency_hz=1.0, min_val=0, max_val=127, phase_offset=math.pi / 2
        )
        assert wave.phase_offset == math.pi / 2

    def test_period_calculation(self):
        """Test period calculation from frequency."""
        wave = WaveGenerator("sine", frequency_hz=2.0, min_val=0, max_val=127)
        assert wave.period_seconds() == 0.5

        wave2 = WaveGenerator("sine", frequency_hz=0.5, min_val=0, max_val=127)
        assert wave2.period_seconds() == 2.0

    def test_repr(self):
        """Test string representation."""
        wave = WaveGenerator("sine", frequency_hz=2.0, min_val=0, max_val=127)
        repr_str = repr(wave)
        assert "WaveGenerator" in repr_str
        assert "sine" in repr_str
        assert "2.0Hz" in repr_str


class TestSineWave:
    """Test sine wave generation."""

    def test_sine_wave_at_zero(self):
        """Test sine wave value at t=0."""
        wave = WaveGenerator("sine", frequency_hz=1.0, min_val=0, max_val=127)
        # At t=0, sin(0) = 0, which maps to center (63.5)
        value = wave.value_at_time(0.0)
        assert abs(value - 63.5) < 0.1

    def test_sine_wave_at_quarter_period(self):
        """Test sine wave value at quarter period (peak)."""
        wave = WaveGenerator("sine", frequency_hz=1.0, min_val=0, max_val=127)
        # At t=0.25s (1Hz), sin(π/2) = 1, which maps to max (127)
        value = wave.value_at_time(0.25)
        assert abs(value - 127.0) < 0.1

    def test_sine_wave_at_half_period(self):
        """Test sine wave value at half period (center)."""
        wave = WaveGenerator("sine", frequency_hz=1.0, min_val=0, max_val=127)
        # At t=0.5s, sin(π) = 0, which maps to center (63.5)
        value = wave.value_at_time(0.5)
        assert abs(value - 63.5) < 0.1

    def test_sine_wave_at_three_quarters_period(self):
        """Test sine wave value at three quarters period (trough)."""
        wave = WaveGenerator("sine", frequency_hz=1.0, min_val=0, max_val=127)
        # At t=0.75s, sin(3π/2) = -1, which maps to min (0)
        value = wave.value_at_time(0.75)
        assert abs(value - 0.0) < 0.1

    def test_sine_wave_full_period(self):
        """Test sine wave value at full period (back to start)."""
        wave = WaveGenerator("sine", frequency_hz=1.0, min_val=0, max_val=127)
        # At t=1.0s, sin(2π) = 0, which maps to center (63.5)
        value = wave.value_at_time(1.0)
        assert abs(value - 63.5) < 0.1

    def test_sine_wave_symmetry(self):
        """Test that sine wave is symmetric."""
        wave = WaveGenerator("sine", frequency_hz=1.0, min_val=0, max_val=127)

        # Values at symmetric points should be equidistant from center
        v1 = wave.value_at_time(0.25)  # Peak
        v2 = wave.value_at_time(0.75)  # Trough
        center = 63.5

        assert abs((v1 - center) - (center - v2)) < 0.1


class TestTriangleWave:
    """Test triangle wave generation."""

    def test_triangle_wave_at_zero(self):
        """Test triangle wave at start (minimum)."""
        wave = WaveGenerator("triangle", frequency_hz=1.0, min_val=0, max_val=127)
        value = wave.value_at_time(0.0)
        # Triangle starts at minimum
        assert abs(value - 0.0) < 0.1

    def test_triangle_wave_at_quarter_period(self):
        """Test triangle wave at quarter period (midpoint rising)."""
        wave = WaveGenerator("triangle", frequency_hz=1.0, min_val=0, max_val=127)
        value = wave.value_at_time(0.25)
        # Triangle is at center while rising at quarter period
        assert abs(value - 63.5) < 0.1

    def test_triangle_wave_at_half_period(self):
        """Test triangle wave at half period (peak)."""
        wave = WaveGenerator("triangle", frequency_hz=1.0, min_val=0, max_val=127)
        value = wave.value_at_time(0.5)
        # Triangle reaches maximum at half period
        assert abs(value - 127.0) < 0.1

    def test_triangle_wave_linearity(self):
        """Test that triangle wave rises/falls linearly."""
        wave = WaveGenerator("triangle", frequency_hz=1.0, min_val=0, max_val=127)

        # Check linear rise in first quarter
        v0 = wave.value_at_time(0.0)
        v1 = wave.value_at_time(0.125)
        v2 = wave.value_at_time(0.25)

        # Differences should be equal (linear)
        diff1 = v1 - v0
        diff2 = v2 - v1
        assert abs(diff1 - diff2) < 1.0


class TestSquareWave:
    """Test square wave generation."""

    def test_square_wave_at_zero(self):
        """Test square wave at start (high)."""
        wave = WaveGenerator("square", frequency_hz=1.0, min_val=0, max_val=127)
        value = wave.value_at_time(0.0)
        # Square starts at maximum
        assert abs(value - 127.0) < 0.1

    def test_square_wave_first_half(self):
        """Test square wave in first half of period (high)."""
        wave = WaveGenerator("square", frequency_hz=1.0, min_val=0, max_val=127)

        # All values in first half should be maximum
        for t in [0.0, 0.1, 0.2, 0.3, 0.4, 0.49]:
            value = wave.value_at_time(t)
            assert abs(value - 127.0) < 0.1

    def test_square_wave_second_half(self):
        """Test square wave in second half of period (low)."""
        wave = WaveGenerator("square", frequency_hz=1.0, min_val=0, max_val=127)

        # All values in second half should be minimum
        for t in [0.51, 0.6, 0.7, 0.8, 0.9, 0.99]:
            value = wave.value_at_time(t)
            assert abs(value - 0.0) < 0.1

    def test_square_wave_binary(self):
        """Test that square wave has only two values."""
        wave = WaveGenerator("square", frequency_hz=1.0, min_val=0, max_val=127)

        values = [wave.value_at_time(t / 20.0) for t in range(20)]
        unique_values = set(values)

        # Should have only 2 unique values (min and max)
        assert len(unique_values) == 2


class TestSawtoothWave:
    """Test sawtooth wave generation."""

    def test_sawtooth_wave_at_zero(self):
        """Test sawtooth wave at start (minimum)."""
        wave = WaveGenerator("sawtooth", frequency_hz=1.0, min_val=0, max_val=127)
        value = wave.value_at_time(0.0)
        # Sawtooth starts at minimum
        assert abs(value - 0.0) < 0.1

    def test_sawtooth_wave_at_half_period(self):
        """Test sawtooth wave at half period (center)."""
        wave = WaveGenerator("sawtooth", frequency_hz=1.0, min_val=0, max_val=127)
        value = wave.value_at_time(0.5)
        # Sawtooth at center at half period
        assert abs(value - 63.5) < 0.1

    def test_sawtooth_wave_at_almost_full_period(self):
        """Test sawtooth wave just before full period (maximum)."""
        wave = WaveGenerator("sawtooth", frequency_hz=1.0, min_val=0, max_val=127)
        value = wave.value_at_time(0.99)
        # Sawtooth at maximum just before reset
        assert value > 120.0

    def test_sawtooth_wave_linearity(self):
        """Test that sawtooth wave rises linearly."""
        wave = WaveGenerator("sawtooth", frequency_hz=1.0, min_val=0, max_val=127)

        # Check linear rise
        values = [wave.value_at_time(t / 10.0) for t in range(10)]

        # Calculate differences between consecutive values
        diffs = [values[i + 1] - values[i] for i in range(len(values) - 1)]

        # All differences should be approximately equal (linear)
        avg_diff = sum(diffs) / len(diffs)
        for diff in diffs:
            assert abs(diff - avg_diff) < 1.0


class TestPhaseOffset:
    """Test phase offset functionality."""

    def test_sine_wave_phase_offset_90deg(self):
        """Test sine wave with 90 degree phase offset."""
        wave_no_offset = WaveGenerator(
            "sine", frequency_hz=1.0, min_val=0, max_val=127, phase_offset=0.0
        )
        wave_with_offset = WaveGenerator(
            "sine", frequency_hz=1.0, min_val=0, max_val=127, phase_offset=math.pi / 2
        )

        # Value at t=0 with π/2 offset should equal value at t=0.25 without offset
        v1 = wave_with_offset.value_at_time(0.0)
        v2 = wave_no_offset.value_at_time(0.25)

        assert abs(v1 - v2) < 0.1

    def test_phase_offset_180deg(self):
        """Test phase offset of 180 degrees (inverted)."""
        wave_no_offset = WaveGenerator(
            "sine", frequency_hz=1.0, min_val=0, max_val=127, phase_offset=0.0
        )
        wave_inverted = WaveGenerator(
            "sine", frequency_hz=1.0, min_val=0, max_val=127, phase_offset=math.pi
        )

        # Values should be inverted around center
        v1 = wave_no_offset.value_at_time(0.25)  # Peak
        v2 = wave_inverted.value_at_time(0.25)  # Trough

        center = 63.5
        assert abs((v1 - center) + (v2 - center)) < 0.1


class TestFrequency:
    """Test different frequency settings."""

    def test_frequency_2hz(self):
        """Test 2Hz frequency (2 cycles per second)."""
        wave = WaveGenerator("sine", frequency_hz=2.0, min_val=0, max_val=127)

        # At 2Hz, full cycle completes in 0.5s
        v_start = wave.value_at_time(0.0)
        v_end = wave.value_at_time(0.5)

        # Should be back to start value after half a second
        assert abs(v_start - v_end) < 0.1

    def test_frequency_05hz(self):
        """Test 0.5Hz frequency (half cycle per second)."""
        wave = WaveGenerator("sine", frequency_hz=0.5, min_val=0, max_val=127)

        # At 0.5Hz, full cycle completes in 2s
        v_start = wave.value_at_time(0.0)
        v_end = wave.value_at_time(2.0)

        # Should be back to start value after 2 seconds
        assert abs(v_start - v_end) < 0.1

    def test_high_frequency(self):
        """Test high frequency (100Hz)."""
        wave = WaveGenerator("sine", frequency_hz=100.0, min_val=0, max_val=127)

        # At 100Hz, full cycle completes in 0.01s
        period = wave.period_seconds()
        assert abs(period - 0.01) < 0.0001


class TestValueRange:
    """Test different value ranges."""

    def test_custom_range(self):
        """Test wave with custom min/max range."""
        wave = WaveGenerator("sine", frequency_hz=1.0, min_val=50, max_val=100)

        # Generate many values
        values = [wave.value_at_time(t / 100.0) for t in range(100)]

        # All values should be within range
        assert all(50 <= v <= 100 for v in values)

        # Should reach approximately min and max
        assert min(values) < 52
        assert max(values) > 98

    def test_negative_range(self):
        """Test wave with negative values."""
        wave = WaveGenerator("sine", frequency_hz=1.0, min_val=-50, max_val=50)

        # At t=0, should be at center (0)
        value = wave.value_at_time(0.0)
        assert abs(value - 0.0) < 0.1

        # At t=0.25, should be at max (50)
        value = wave.value_at_time(0.25)
        assert abs(value - 50.0) < 0.1

        # At t=0.75, should be at min (-50)
        value = wave.value_at_time(0.75)
        assert abs(value - (-50.0)) < 0.1

    def test_reversed_range(self):
        """Test wave with reversed range (max < min)."""
        wave = WaveGenerator("sine", frequency_hz=1.0, min_val=127, max_val=0)

        # Should work but with inverted values
        v1 = wave.value_at_time(0.25)  # Should be at "max" (which is 0)
        assert v1 < 10

        v2 = wave.value_at_time(0.75)  # Should be at "min" (which is 127)
        assert v2 > 117


class TestPresetWaves:
    """Test preset wave generators."""

    def test_create_vibrato_wave(self):
        """Test vibrato wave creation."""
        vibrato = create_vibrato_wave(frequency_hz=6.0, depth_cents=30)

        assert vibrato.wave_type == "sine"
        assert vibrato.frequency_hz == 6.0

        # Should oscillate around center pitch (8192)
        values = [vibrato.value_at_time(t / 20.0) for t in range(20)]
        avg_value = sum(values) / len(values)
        assert abs(avg_value - 8192) < 100  # Close to center

    def test_create_tremolo_wave(self):
        """Test tremolo wave creation."""
        tremolo = create_tremolo_wave(frequency_hz=4.5, depth_percent=40)

        assert tremolo.wave_type == "sine"
        assert tremolo.frequency_hz == 4.5

        # Should oscillate in upper range (60% to 100% of 127)
        values = [tremolo.value_at_time(t / 20.0) for t in range(20)]
        assert min(values) > 70  # Above 60%
        assert max(values) > 120  # Near 100%

    def test_create_lfo_wave(self):
        """Test generic LFO wave creation."""
        lfo = create_lfo_wave("triangle", frequency_hz=0.5, min_val=20, max_val=110)

        assert lfo.wave_type == "triangle"
        assert lfo.frequency_hz == 0.5
        assert lfo.min_val == 20.0
        assert lfo.max_val == 110.0


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_negative_time(self):
        """Test wave generation with negative time values."""
        wave = WaveGenerator("sine", frequency_hz=1.0, min_val=0, max_val=127)

        # Should handle negative time (phase wraps around)
        value = wave.value_at_time(-0.25)
        # This should be equivalent to t=0.75 (three quarters)
        assert value < 10  # Near minimum

    def test_very_large_time(self):
        """Test wave generation with very large time values."""
        wave = WaveGenerator("sine", frequency_hz=1.0, min_val=0, max_val=127)

        # Should handle large time values
        value = wave.value_at_time(1000.0)
        # Should still produce valid value
        assert 0 <= value <= 127

    def test_zero_amplitude(self):
        """Test wave with zero amplitude (min == max)."""
        wave = WaveGenerator("sine", frequency_hz=1.0, min_val=64, max_val=64)

        # All values should be constant
        values = [wave.value_at_time(t / 10.0) for t in range(10)]
        assert all(abs(v - 64.0) < 0.1 for v in values)
