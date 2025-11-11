"""Tests for ADSR envelope generators.

This module tests the ADSREnvelope, AREnvelope, and ADEnvelope classes
for creating dynamic parameter changes in MIDI automation.
"""

from __future__ import annotations

import pytest

from midi_markdown.utils.envelopes import (
    ADEnvelope,
    ADSREnvelope,
    AREnvelope,
    scale_envelope_to_range,
)


class TestADSREnvelopeBasics:
    """Test basic ADSR envelope functionality."""

    def test_create_adsr_envelope(self):
        """Test creating an ADSR envelope."""
        env = ADSREnvelope(attack_time=0.1, decay_time=0.2, sustain_level=0.7, release_time=0.3)
        assert env.attack_time == 0.1
        assert env.decay_time == 0.2
        assert env.sustain_level == 0.7
        assert env.release_time == 0.3
        assert env.peak_level == 1.0
        assert env.curve_type == "linear"

    def test_adsr_with_custom_peak(self):
        """Test ADSR with custom peak level."""
        env = ADSREnvelope(0.1, 0.2, 0.7, 0.3, peak_level=0.8)
        assert env.peak_level == 0.8

    def test_adsr_with_exponential_curve(self):
        """Test ADSR with exponential curve."""
        env = ADSREnvelope(0.1, 0.2, 0.7, 0.3, curve_type="exponential")
        assert env.curve_type == "exponential"

    def test_negative_attack_time(self):
        """Test that negative attack time raises error."""
        with pytest.raises(ValueError, match="Attack time must be >= 0"):
            ADSREnvelope(-0.1, 0.2, 0.7, 0.3)

    def test_negative_decay_time(self):
        """Test that negative decay time raises error."""
        with pytest.raises(ValueError, match="Decay time must be >= 0"):
            ADSREnvelope(0.1, -0.2, 0.7, 0.3)

    def test_negative_release_time(self):
        """Test that negative release time raises error."""
        with pytest.raises(ValueError, match="Release time must be >= 0"):
            ADSREnvelope(0.1, 0.2, 0.7, -0.3)

    def test_invalid_sustain_level_too_low(self):
        """Test that sustain level < 0 raises error."""
        with pytest.raises(ValueError, match="Sustain level must be 0.0-1.0"):
            ADSREnvelope(0.1, 0.2, -0.1, 0.3)

    def test_invalid_sustain_level_too_high(self):
        """Test that sustain level > 1 raises error."""
        with pytest.raises(ValueError, match="Sustain level must be 0.0-1.0"):
            ADSREnvelope(0.1, 0.2, 1.5, 0.3)

    def test_invalid_curve_type(self):
        """Test that invalid curve type raises error."""
        with pytest.raises(ValueError, match="Invalid curve_type"):
            ADSREnvelope(0.1, 0.2, 0.7, 0.3, curve_type="invalid")

    def test_repr(self):
        """Test string representation."""
        env = ADSREnvelope(0.1, 0.2, 0.7, 0.3)
        repr_str = repr(env)
        assert "ADSREnvelope" in repr_str
        assert "attack=0.1s" in repr_str
        assert "sustain=0.7" in repr_str


class TestADSREnvelopePhases:
    """Test ADSR envelope phase transitions."""

    def test_attack_phase_start(self):
        """Test envelope at start of attack (t=0)."""
        env = ADSREnvelope(0.1, 0.2, 0.7, 0.3)
        assert env.value_at_time(0.0) == 0.0

    def test_attack_phase_middle(self):
        """Test envelope in middle of attack."""
        env = ADSREnvelope(0.1, 0.2, 0.7, 0.3)
        # Linear: at t=0.05 (halfway through 0.1s attack), value should be 0.5
        value = env.value_at_time(0.05)
        assert abs(value - 0.5) < 0.01

    def test_attack_phase_end(self):
        """Test envelope at end of attack (peak)."""
        env = ADSREnvelope(0.1, 0.2, 0.7, 0.3)
        assert env.value_at_time(0.1) == 1.0

    def test_decay_phase_middle(self):
        """Test envelope in middle of decay."""
        env = ADSREnvelope(0.1, 0.2, 0.7, 0.3)
        # At t=0.2 (halfway through decay from 1.0 to 0.7)
        # Linear: (1.0 + 0.7) / 2 = 0.85
        value = env.value_at_time(0.2)
        assert abs(value - 0.85) < 0.01

    def test_decay_phase_end(self):
        """Test envelope at end of decay (sustain level)."""
        env = ADSREnvelope(0.1, 0.2, 0.7, 0.3)
        # At t=0.3 (attack=0.1 + decay=0.2)
        assert abs(env.value_at_time(0.3) - 0.7) < 0.01

    def test_sustain_phase_infinite(self):
        """Test envelope during infinite sustain (no note off)."""
        env = ADSREnvelope(0.1, 0.2, 0.7, 0.3)
        # Without note_off, sustain holds forever
        assert abs(env.value_at_time(1.0) - 0.7) < 0.01
        assert abs(env.value_at_time(10.0) - 0.7) < 0.01

    def test_release_phase_with_note_off(self):
        """Test envelope release phase after note off."""
        env = ADSREnvelope(0.1, 0.2, 0.7, 0.3, note_off_time=0.5)
        # At t=0.5, note off triggers release from 0.7
        # At t=0.65 (halfway through 0.3s release), value should be ~0.35
        value = env.value_at_time(0.65)
        assert abs(value - 0.35) < 0.01

    def test_release_phase_end(self):
        """Test envelope at end of release."""
        env = ADSREnvelope(0.1, 0.2, 0.7, 0.3, note_off_time=0.5)
        # At t=0.8 (note_off=0.5 + release=0.3)
        assert abs(env.value_at_time(0.8) - 0.0) < 0.01

    def test_after_release(self):
        """Test envelope after release phase ends."""
        env = ADSREnvelope(0.1, 0.2, 0.7, 0.3, note_off_time=0.5)
        # After t=0.8, envelope should be silent
        assert env.value_at_time(1.0) == 0.0
        assert env.value_at_time(10.0) == 0.0


class TestADSREnvelopeZeroTimes:
    """Test ADSR with zero-duration phases."""

    def test_zero_attack_time(self):
        """Test envelope with instant attack."""
        env = ADSREnvelope(0.0, 0.2, 0.7, 0.3)
        # Should instantly reach peak
        assert env.value_at_time(0.0) == 1.0

    def test_zero_decay_time(self):
        """Test envelope with instant decay."""
        env = ADSREnvelope(0.1, 0.0, 0.7, 0.3)
        # At t=0.1, should instantly be at sustain
        assert abs(env.value_at_time(0.1) - 0.7) < 0.01

    def test_zero_release_time(self):
        """Test envelope with instant release."""
        env = ADSREnvelope(0.1, 0.2, 0.7, 0.0, note_off_time=0.5)
        # At note_off, should instantly go to 0
        assert env.value_at_time(0.5) == 0.0

    def test_all_zero_times(self):
        """Test envelope with all zero times."""
        env = ADSREnvelope(0.0, 0.0, 0.5, 0.0, note_off_time=0.0)
        # With zero attack and zero decay, returns sustain level (0.5)
        # The decay check happens before release check, so we get sustain value
        assert abs(env.value_at_time(0.0) - 0.5) < 0.01


class TestADSREnvelopeCurveTypes:
    """Test ADSR envelope curve shapes."""

    def test_linear_attack(self):
        """Test linear attack curve."""
        env = ADSREnvelope(0.1, 0.2, 0.7, 0.3, curve_type="linear")
        # Linear: at halfway, value should be exactly 0.5
        assert abs(env.value_at_time(0.05) - 0.5) < 0.01

    def test_exponential_attack(self):
        """Test exponential attack curve."""
        env = ADSREnvelope(0.1, 0.2, 0.7, 0.3, curve_type="exponential")
        # Exponential: at halfway, value should be > 0.5 (accelerating)
        value = env.value_at_time(0.05)
        assert value > 0.5

    def test_linear_decay(self):
        """Test linear decay curve."""
        env = ADSREnvelope(0.1, 0.2, 0.7, 0.3, curve_type="linear")
        # At t=0.2 (halfway through decay), linear should be 0.85
        assert abs(env.value_at_time(0.2) - 0.85) < 0.01

    def test_exponential_decay(self):
        """Test exponential decay curve."""
        env = ADSREnvelope(0.1, 0.2, 0.7, 0.3, curve_type="exponential")
        # Exponential decay starts slower, so at halfway should be > linear
        # Linear at t=0.2 would be 0.85, exponential should be > 0.85
        value = env.value_at_time(0.2)
        assert value > 0.85


class TestADSREnvelopeNoteOff:
    """Test ADSR envelope note-off behavior."""

    def test_set_note_off(self):
        """Test setting note off time dynamically."""
        env = ADSREnvelope(0.1, 0.2, 0.7, 0.3)
        env.set_note_off(0.5)
        assert env.note_off_time == 0.5

    def test_note_off_too_early(self):
        """Test that note off before decay end raises error."""
        env = ADSREnvelope(0.1, 0.2, 0.7, 0.3)
        # Note off must be >= attack + decay = 0.3
        with pytest.raises(ValueError, match="Note off time.*must be >="):
            env.set_note_off(0.2)

    def test_total_duration_infinite(self):
        """Test total duration with infinite sustain."""
        env = ADSREnvelope(0.1, 0.2, 0.7, 0.3)
        assert env.total_duration() is None

    def test_total_duration_finite(self):
        """Test total duration with note off."""
        env = ADSREnvelope(0.1, 0.2, 0.7, 0.3, note_off_time=0.5)
        # Total = note_off + release = 0.5 + 0.3 = 0.8
        assert env.total_duration() == 0.8


class TestAREnvelopeBasics:
    """Test basic AR envelope functionality."""

    def test_create_ar_envelope(self):
        """Test creating an AR envelope."""
        env = AREnvelope(attack_time=0.1, release_time=0.3)
        assert env.attack_time == 0.1
        assert env.release_time == 0.3
        assert env.peak_level == 1.0
        assert env.curve_type == "linear"

    def test_ar_with_custom_peak(self):
        """Test AR with custom peak level."""
        env = AREnvelope(0.1, 0.3, peak_level=0.8)
        assert env.peak_level == 0.8

    def test_ar_negative_times(self):
        """Test that negative times raise errors."""
        with pytest.raises(ValueError):
            AREnvelope(-0.1, 0.3)
        with pytest.raises(ValueError):
            AREnvelope(0.1, -0.3)

    def test_ar_repr(self):
        """Test AR string representation."""
        env = AREnvelope(0.1, 0.3)
        repr_str = repr(env)
        assert "AREnvelope" in repr_str
        assert "attack=0.1s" in repr_str


class TestAREnvelopePhases:
    """Test AR envelope phase transitions."""

    def test_ar_attack_start(self):
        """Test AR at start of attack."""
        env = AREnvelope(0.1, 0.3)
        assert env.value_at_time(0.0) == 0.0

    def test_ar_attack_middle(self):
        """Test AR in middle of attack."""
        env = AREnvelope(0.1, 0.3)
        value = env.value_at_time(0.05)
        assert abs(value - 0.5) < 0.01

    def test_ar_attack_end(self):
        """Test AR at end of attack (peak)."""
        env = AREnvelope(0.1, 0.3)
        assert env.value_at_time(0.1) == 1.0

    def test_ar_release_middle(self):
        """Test AR in middle of release."""
        env = AREnvelope(0.1, 0.3)
        # At t=0.25 (halfway through release from peak)
        value = env.value_at_time(0.25)
        assert abs(value - 0.5) < 0.01

    def test_ar_release_end(self):
        """Test AR at end of release."""
        env = AREnvelope(0.1, 0.3)
        # At t=0.4 (attack=0.1 + release=0.3)
        assert abs(env.value_at_time(0.4) - 0.0) < 0.01

    def test_ar_after_release(self):
        """Test AR after release ends."""
        env = AREnvelope(0.1, 0.3)
        assert env.value_at_time(1.0) == 0.0

    def test_ar_total_duration(self):
        """Test AR total duration."""
        env = AREnvelope(0.1, 0.3)
        assert env.total_duration() == 0.4


class TestADEnvelopeBasics:
    """Test basic AD envelope functionality."""

    def test_create_ad_envelope(self):
        """Test creating an AD envelope."""
        env = ADEnvelope(attack_time=0.1, decay_time=0.4)
        assert env.attack_time == 0.1
        assert env.decay_time == 0.4
        assert env.peak_level == 1.0
        assert env.end_level == 0.0
        assert env.curve_type == "linear"

    def test_ad_with_custom_levels(self):
        """Test AD with custom peak and end levels."""
        env = ADEnvelope(0.1, 0.4, peak_level=0.8, end_level=0.2)
        assert env.peak_level == 0.8
        assert env.end_level == 0.2

    def test_ad_negative_times(self):
        """Test that negative times raise errors."""
        with pytest.raises(ValueError):
            ADEnvelope(-0.1, 0.4)
        with pytest.raises(ValueError):
            ADEnvelope(0.1, -0.4)

    def test_ad_repr(self):
        """Test AD string representation."""
        env = ADEnvelope(0.1, 0.4)
        repr_str = repr(env)
        assert "ADEnvelope" in repr_str
        assert "attack=0.1s" in repr_str


class TestADEnvelopePhases:
    """Test AD envelope phase transitions."""

    def test_ad_attack_start(self):
        """Test AD at start of attack."""
        env = ADEnvelope(0.1, 0.4)
        # With default end_level=0.0, should start at 0
        assert env.value_at_time(0.0) == 0.0

    def test_ad_attack_middle(self):
        """Test AD in middle of attack."""
        env = ADEnvelope(0.1, 0.4)
        value = env.value_at_time(0.05)
        assert abs(value - 0.5) < 0.01

    def test_ad_attack_end(self):
        """Test AD at end of attack (peak)."""
        env = ADEnvelope(0.1, 0.4)
        assert env.value_at_time(0.1) == 1.0

    def test_ad_decay_middle(self):
        """Test AD in middle of decay."""
        env = ADEnvelope(0.1, 0.4)
        # At t=0.3 (halfway through decay from 1.0 to 0.0)
        value = env.value_at_time(0.3)
        assert abs(value - 0.5) < 0.01

    def test_ad_decay_end(self):
        """Test AD at end of decay."""
        env = ADEnvelope(0.1, 0.4)
        # At t=0.5 (attack=0.1 + decay=0.4)
        assert abs(env.value_at_time(0.5) - 0.0) < 0.01

    def test_ad_after_decay(self):
        """Test AD after decay ends."""
        env = ADEnvelope(0.1, 0.4)
        assert env.value_at_time(1.0) == 0.0

    def test_ad_total_duration(self):
        """Test AD total duration."""
        env = ADEnvelope(0.1, 0.4)
        assert env.total_duration() == 0.5

    def test_ad_with_nonzero_end_level(self):
        """Test AD with non-zero end level."""
        env = ADEnvelope(0.1, 0.4, end_level=0.3)
        # Should decay to 0.3, not 0.0
        assert abs(env.value_at_time(0.5) - 0.3) < 0.01
        assert abs(env.value_at_time(1.0) - 0.3) < 0.01


class TestEnvelopeScaling:
    """Test envelope scaling to different ranges."""

    def test_scale_adsr_to_midi_range(self):
        """Test scaling ADSR to MIDI CC range (0-127)."""
        env = ADSREnvelope(0.1, 0.2, 0.7, 0.3)

        # At peak (t=0.1), should be 127
        value = scale_envelope_to_range(env, 0, 127, 0.1)
        assert abs(value - 127.0) < 0.1

        # At sustain (t=0.3), should be ~89 (0.7 * 127)
        value = scale_envelope_to_range(env, 0, 127, 0.3)
        assert abs(value - 88.9) < 0.5

    def test_scale_ar_to_custom_range(self):
        """Test scaling AR to custom range."""
        env = AREnvelope(0.1, 0.3)

        # At peak, should be max value
        value = scale_envelope_to_range(env, 50, 100, 0.1)
        assert abs(value - 100.0) < 0.1

        # At start, should be min value
        value = scale_envelope_to_range(env, 50, 100, 0.0)
        assert abs(value - 50.0) < 0.1

    def test_scale_ad_to_negative_range(self):
        """Test scaling AD to range with negative values."""
        env = ADEnvelope(0.1, 0.4)

        # At peak, should be max
        value = scale_envelope_to_range(env, -50, 50, 0.1)
        assert abs(value - 50.0) < 0.1

        # At end, should be min
        value = scale_envelope_to_range(env, -50, 50, 0.5)
        assert abs(value - (-50.0)) < 0.1


class TestEnvelopeEdgeCases:
    """Test edge cases and special scenarios."""

    def test_negative_time(self):
        """Test envelope with negative time."""
        env = ADSREnvelope(0.1, 0.2, 0.7, 0.3)
        # Negative time should return 0
        assert env.value_at_time(-1.0) == 0.0

    def test_sustain_zero(self):
        """Test ADSR with zero sustain level."""
        env = ADSREnvelope(0.1, 0.2, 0.0, 0.3)
        # At sustain phase, value should be 0
        assert abs(env.value_at_time(0.5) - 0.0) < 0.01

    def test_sustain_one(self):
        """Test ADSR with sustain at peak (1.0)."""
        env = ADSREnvelope(0.1, 0.2, 1.0, 0.3)
        # Sustain at peak means no decay
        assert abs(env.value_at_time(0.3) - 1.0) < 0.01

    def test_ar_zero_attack(self):
        """Test AR with instant attack."""
        env = AREnvelope(0.0, 0.3)
        assert env.value_at_time(0.0) == 1.0

    def test_ad_zero_decay(self):
        """Test AD with instant decay."""
        env = ADEnvelope(0.1, 0.0)
        # At t=0.1, should instantly be at end_level
        assert env.value_at_time(0.1) == 0.0


class TestEnvelopeRealWorld:
    """Test real-world use cases for envelopes."""

    def test_filter_cutoff_envelope(self):
        """Test ADSR for filter cutoff automation."""
        # Classic synth filter: fast attack, medium decay, high sustain
        env = ADSREnvelope(0.01, 0.3, 0.6, 0.5, note_off_time=2.0)

        # Should quickly rise to peak
        assert env.value_at_time(0.01) == 1.0

        # Then decay to sustain
        assert abs(env.value_at_time(0.31) - 0.6) < 0.05

        # Hold during sustain
        assert abs(env.value_at_time(1.0) - 0.6) < 0.01

    def test_percussive_envelope(self):
        """Test AR for percussive sounds."""
        # Fast attack, medium release
        env = AREnvelope(0.005, 0.2)

        # Quick attack to peak
        assert abs(env.value_at_time(0.005) - 1.0) < 0.01

        # Decay to silence
        assert abs(env.value_at_time(0.205) - 0.0) < 0.01

    def test_pad_swell_envelope(self):
        """Test AD for pad swell effect."""
        # Slow attack, slow decay
        env = ADEnvelope(2.0, 3.0)

        # Gradual rise
        value_1s = env.value_at_time(1.0)
        assert 0.4 < value_1s < 0.6

        # Peak at 2s
        assert abs(env.value_at_time(2.0) - 1.0) < 0.01

        # Gradual fall
        value_3_5s = env.value_at_time(3.5)
        assert 0.4 < value_3_5s < 0.6
