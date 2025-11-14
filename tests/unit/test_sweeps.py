"""
Unit tests for sweep implementation.
"""

import pytest

from midi_markdown.expansion.sweeps import (
    RampSpec,
    RampType,
    SweepDefinition,
    SweepExpander,
    parse_ramp_type,
    parse_sweep_interval,
)


class TestRampSpec:
    """Test RampSpec interpolation curves."""

    def test_linear_interpolation(self):
        """Test linear interpolation from 0 to 100."""
        ramp = RampSpec(RampType.LINEAR, 0.0, 100.0)

        assert ramp.interpolate(0.0) == 0.0
        assert ramp.interpolate(0.25) == 25.0
        assert ramp.interpolate(0.5) == 50.0
        assert ramp.interpolate(0.75) == 75.0
        assert ramp.interpolate(1.0) == 100.0

    def test_linear_reverse(self):
        """Test linear interpolation from 100 to 0."""
        ramp = RampSpec(RampType.LINEAR, 100.0, 0.0)

        assert ramp.interpolate(0.0) == 100.0
        assert ramp.interpolate(0.5) == 50.0
        assert ramp.interpolate(1.0) == 0.0

    def test_exponential_interpolation(self):
        """Test exponential interpolation (t^2)."""
        ramp = RampSpec(RampType.EXPONENTIAL, 0.0, 100.0)

        assert ramp.interpolate(0.0) == 0.0
        assert abs(ramp.interpolate(0.5) - 25.0) < 0.1  # 0.5^2 * 100 = 25
        assert ramp.interpolate(1.0) == 100.0

        # Should accelerate: value at 0.5 < linear 0.5
        linear_mid = 50.0
        exp_mid = ramp.interpolate(0.5)
        assert exp_mid < linear_mid

    def test_logarithmic_interpolation(self):
        """Test logarithmic interpolation (sqrt(t))."""
        ramp = RampSpec(RampType.LOGARITHMIC, 0.0, 100.0)

        assert ramp.interpolate(0.0) == 0.0
        assert abs(ramp.interpolate(0.25) - 50.0) < 0.1  # sqrt(0.25) * 100 = 50
        assert ramp.interpolate(1.0) == 100.0

        # Should decelerate: value at 0.5 > linear 0.5
        linear_mid = 50.0
        log_mid = ramp.interpolate(0.5)
        assert log_mid > linear_mid

    def test_ease_in_interpolation(self):
        """Test ease-in interpolation (t^3)."""
        ramp = RampSpec(RampType.EASE_IN, 0.0, 100.0)

        assert ramp.interpolate(0.0) == 0.0
        assert abs(ramp.interpolate(0.5) - 12.5) < 0.1  # 0.5^3 * 100 = 12.5
        assert ramp.interpolate(1.0) == 100.0

        # Should start slow: value at 0.5 < exponential 0.5
        ease_mid = ramp.interpolate(0.5)
        assert ease_mid < 25.0  # Less than exponential

    def test_ease_out_interpolation(self):
        """Test ease-out interpolation."""
        ramp = RampSpec(RampType.EASE_OUT, 0.0, 100.0)

        assert ramp.interpolate(0.0) == 0.0
        assert ramp.interpolate(1.0) == 100.0

        # Should start fast then slow down
        # At t=0.5, should be past halfway
        mid_value = ramp.interpolate(0.5)
        assert mid_value > 50.0  # More than linear

    def test_ease_in_out_interpolation(self):
        """Test ease-in-out interpolation (smoothstep)."""
        ramp = RampSpec(RampType.EASE_IN_OUT, 0.0, 100.0)

        assert ramp.interpolate(0.0) == 0.0
        assert ramp.interpolate(0.5) == 50.0  # Smoothstep crosses at 0.5
        assert ramp.interpolate(1.0) == 100.0

        # Should be slow at start and end
        early = ramp.interpolate(0.25)
        late = ramp.interpolate(0.75)
        # Due to smoothstep, these should be symmetric around 50
        assert abs((100 - late) - early) < 1.0

    def test_clamp_t_below_zero(self):
        """Test that t < 0 is clamped to 0."""
        ramp = RampSpec(RampType.LINEAR, 0.0, 100.0)
        assert ramp.interpolate(-0.5) == 0.0

    def test_clamp_t_above_one(self):
        """Test that t > 1 is clamped to 1."""
        ramp = RampSpec(RampType.LINEAR, 0.0, 100.0)
        assert ramp.interpolate(1.5) == 100.0

    def test_negative_range(self):
        """Test interpolation with negative values."""
        ramp = RampSpec(RampType.LINEAR, -50.0, 50.0)

        assert ramp.interpolate(0.0) == -50.0
        assert ramp.interpolate(0.5) == 0.0
        assert ramp.interpolate(1.0) == 50.0


class TestParseRampType:
    """Test ramp type string parsing."""

    @pytest.mark.parametrize(
        ("input_str", "expected"),
        [
            # Linear variations
            ("linear", RampType.LINEAR),
            ("lin", RampType.LINEAR),
            ("LINEAR", RampType.LINEAR),
            # Exponential variations
            ("exponential", RampType.EXPONENTIAL),
            ("exp", RampType.EXPONENTIAL),
            ("EXP", RampType.EXPONENTIAL),
            # Logarithmic variations
            ("logarithmic", RampType.LOGARITHMIC),
            ("log", RampType.LOGARITHMIC),
            ("LOG", RampType.LOGARITHMIC),
            # Ease-in variations
            ("ease-in", RampType.EASE_IN),
            ("ease_in", RampType.EASE_IN),
            ("easein", RampType.EASE_IN),
            # Ease-out variations
            ("ease-out", RampType.EASE_OUT),
            ("ease_out", RampType.EASE_OUT),
            ("easeout", RampType.EASE_OUT),
            # Ease-in-out variations
            ("ease-in-out", RampType.EASE_IN_OUT),
            ("ease_in_out", RampType.EASE_IN_OUT),
            ("easeinout", RampType.EASE_IN_OUT),
        ],
    )
    def test_parse_ramp_types(self, input_str, expected):
        """Test parsing various ramp type strings (case-insensitive)."""
        assert parse_ramp_type(input_str) == expected

    def test_parse_invalid(self):
        """Test that invalid ramp type raises ValueError."""
        with pytest.raises(ValueError, match="Invalid ramp type"):
            parse_ramp_type("invalid")


class TestParseSweepInterval:
    """Test sweep interval parsing."""

    def test_parse_beats(self):
        """Test parsing beat intervals."""
        ticks = parse_sweep_interval("2b", ppq=480)
        assert ticks == 960  # 2 beats * 480 ppq

    def test_parse_ticks(self):
        """Test parsing tick intervals."""
        ticks = parse_sweep_interval("240t", ppq=480)
        assert ticks == 240

    def test_parse_milliseconds(self):
        """Test parsing millisecond intervals."""
        ticks = parse_sweep_interval("500ms", ppq=480, tempo=120.0)
        assert ticks == 480  # 500ms = 1 beat at 120 BPM

    def test_parse_bbt(self):
        """Test parsing BBT intervals."""
        ticks = parse_sweep_interval("1.2.0", ppq=480)
        # 1 bar (4 beats) + 2 beats = 6 beats = 2880 ticks
        assert ticks == 2880


class TestSweepExpander:
    """Test sweep expansion logic."""

    @pytest.fixture
    def expander(self):
        """Create a SweepExpander instance."""
        return SweepExpander(ppq=480)

    def test_simple_cc_sweep(self, expander):
        """Test expanding a simple CC sweep."""
        ramp = RampSpec(RampType.LINEAR, 0.0, 127.0)
        sweep_def = SweepDefinition(
            command_type="cc",
            channel=1,
            data1=7,  # Volume controller
            ramp=ramp,
            steps=4,
            interval_ticks=100,
            start_time=0,
        )

        events = expander.expand(sweep_def)

        # Should generate 5 events (steps + 1)
        assert len(events) == 5

        # Check times
        assert events[0]["time"] == 0
        assert events[1]["time"] == 100
        assert events[2]["time"] == 200
        assert events[3]["time"] == 300
        assert events[4]["time"] == 400

        # Check values (linear from 0 to 127)
        assert events[0]["data2"] == 0
        assert events[1]["data2"] == 32  # 127/4 ≈ 32
        assert events[2]["data2"] == 64
        assert events[3]["data2"] == 95
        assert events[4]["data2"] == 127

        # Check structure
        for event in events:
            assert event["type"] == "cc"
            assert event["channel"] == 1
            assert event["data1"] == 7

    def test_pitch_bend_sweep(self, expander):
        """Test pitch bend sweep."""
        ramp = RampSpec(RampType.LINEAR, -8192.0, 8191.0)
        sweep_def = SweepDefinition(
            command_type="pitch_bend",
            channel=1,
            data1=None,  # Pitch bend doesn't use data1
            ramp=ramp,
            steps=2,
            interval_ticks=480,
            start_time=0,
        )

        events = expander.expand(sweep_def)

        assert len(events) == 3

        # Check pitch bend values
        assert events[0]["data1"] == -8192
        assert events[1]["data1"] == 0  # Middle
        assert events[2]["data1"] == 8191

        # Check structure
        for event in events:
            assert event["type"] == "pitch_bend"
            assert event["channel"] == 1
            assert "data2" not in event  # Pitch bend only has data1

    def test_pressure_sweep(self, expander):
        """Test channel pressure sweep."""
        ramp = RampSpec(RampType.LINEAR, 0.0, 127.0)
        sweep_def = SweepDefinition(
            command_type="pressure",
            channel=1,
            data1=None,
            ramp=ramp,
            steps=2,
            interval_ticks=240,
            start_time=0,
        )

        events = expander.expand(sweep_def)

        assert len(events) == 3

        # Check pressure values
        assert events[0]["data1"] == 0
        assert events[1]["data1"] == 64
        assert events[2]["data1"] == 127

        # Check structure
        for event in events:
            assert event["type"] == "pressure"
            assert event["channel"] == 1

    def test_exponential_curve(self, expander):
        """Test exponential interpolation curve."""
        ramp = RampSpec(RampType.EXPONENTIAL, 0.0, 100.0)
        sweep_def = SweepDefinition(
            command_type="cc",
            channel=1,
            data1=7,
            ramp=ramp,
            steps=4,
            interval_ticks=100,
            start_time=0,
        )

        events = expander.expand(sweep_def)

        # Values should accelerate (early values < linear)
        linear_quarter = 25
        actual_quarter = events[1]["data2"]
        assert actual_quarter < linear_quarter

    def test_logarithmic_curve(self, expander):
        """Test logarithmic interpolation curve."""
        ramp = RampSpec(RampType.LOGARITHMIC, 0.0, 100.0)
        sweep_def = SweepDefinition(
            command_type="cc",
            channel=1,
            data1=7,
            ramp=ramp,
            steps=4,
            interval_ticks=100,
            start_time=0,
        )

        events = expander.expand(sweep_def)

        # Values should decelerate (early values > linear)
        linear_quarter = 25
        actual_quarter = events[1]["data2"]
        assert actual_quarter > linear_quarter

    def test_value_clamping_upper(self, expander):
        """Test that values are clamped to MIDI range (upper bound)."""
        ramp = RampSpec(RampType.LINEAR, 0.0, 200.0)  # Exceeds 127
        sweep_def = SweepDefinition(
            command_type="cc",
            channel=1,
            data1=7,
            ramp=ramp,
            steps=2,
            interval_ticks=100,
            start_time=0,
        )

        events = expander.expand(sweep_def)

        # Final value should be clamped to 127
        assert events[-1]["data2"] == 127

    def test_value_clamping_lower(self, expander):
        """Test that values are clamped to MIDI range (lower bound)."""
        ramp = RampSpec(RampType.LINEAR, -50.0, 50.0)
        sweep_def = SweepDefinition(
            command_type="cc",
            channel=1,
            data1=7,
            ramp=ramp,
            steps=2,
            interval_ticks=100,
            start_time=0,
        )

        events = expander.expand(sweep_def)

        # First value should be clamped to 0
        assert events[0]["data2"] == 0

    def test_pitch_bend_range(self, expander):
        """Test pitch bend range clamping."""
        ramp = RampSpec(RampType.LINEAR, -10000.0, 10000.0)  # Exceeds range
        sweep_def = SweepDefinition(
            command_type="pitch_bend",
            channel=1,
            data1=None,
            ramp=ramp,
            steps=2,
            interval_ticks=100,
            start_time=0,
        )

        events = expander.expand(sweep_def)

        # Should be clamped to -8192 and +8191
        assert events[0]["data1"] == -8192
        assert events[-1]["data1"] == 8191

    def test_non_zero_start_time(self, expander):
        """Test sweep starting at non-zero time."""
        ramp = RampSpec(RampType.LINEAR, 0.0, 100.0)
        sweep_def = SweepDefinition(
            command_type="cc",
            channel=1,
            data1=7,
            ramp=ramp,
            steps=2,
            interval_ticks=480,
            start_time=1920,  # Start at 4 beats
        )

        events = expander.expand(sweep_def)

        assert events[0]["time"] == 1920
        assert events[1]["time"] == 2400
        assert events[2]["time"] == 2880

    def test_single_step_sweep(self, expander):
        """Test sweep with single step (2 events: start and end)."""
        ramp = RampSpec(RampType.LINEAR, 0.0, 127.0)
        sweep_def = SweepDefinition(
            command_type="cc",
            channel=1,
            data1=7,
            ramp=ramp,
            steps=1,
            interval_ticks=480,
            start_time=0,
        )

        events = expander.expand(sweep_def)

        assert len(events) == 2
        assert events[0]["data2"] == 0
        assert events[1]["data2"] == 127

    def test_zero_steps_sweep(self, expander):
        """Test sweep with zero steps (single event at end value)."""
        ramp = RampSpec(RampType.LINEAR, 0.0, 127.0)
        sweep_def = SweepDefinition(
            command_type="cc",
            channel=1,
            data1=7,
            ramp=ramp,
            steps=0,
            interval_ticks=480,
            start_time=0,
        )

        events = expander.expand(sweep_def)

        # Should generate 1 event (steps + 1)
        assert len(events) == 1
        assert events[0]["data2"] == 127  # End value


class TestSweepDefinition:
    """Test SweepDefinition dataclass."""

    def test_create_sweep_definition(self):
        """Test creating a SweepDefinition."""
        ramp = RampSpec(RampType.LINEAR, 0.0, 127.0)
        sweep_def = SweepDefinition(
            command_type="cc",
            channel=1,
            data1=7,
            ramp=ramp,
            steps=10,
            interval_ticks=100,
            start_time=0,
            source_line=42,
        )

        assert sweep_def.command_type == "cc"
        assert sweep_def.channel == 1
        assert sweep_def.data1 == 7
        assert sweep_def.ramp == ramp
        assert sweep_def.steps == 10
        assert sweep_def.interval_ticks == 100
        assert sweep_def.start_time == 0
        assert sweep_def.source_line == 42

    def test_sweep_definition_defaults(self):
        """Test SweepDefinition default values."""
        ramp = RampSpec(RampType.LINEAR, 0.0, 127.0)
        sweep_def = SweepDefinition(
            command_type="cc",
            channel=1,
            data1=7,
            ramp=ramp,
            steps=5,
            interval_ticks=100,
        )

        assert sweep_def.start_time == 0
        assert sweep_def.source_line == 0
