"""
Unit tests for CommandExpander @sweep processing.

Phase 4: Tests @sweep statement processing and expansion.
"""

import pytest

from midi_markdown.expansion.errors import InvalidSweepConfigError
from midi_markdown.expansion.expander import CommandExpander


class TestSweepProcessing:
    """Test @sweep statement processing."""

    @pytest.fixture
    def expander(self):
        return CommandExpander(ppq=480, tempo=120.0, source_file="test.mmd")

    def test_simple_sweep_expansion(self, expander):
        """Test basic sweep with start/end/interval."""
        nodes = [
            {
                "type": "sweep",
                "start_time": 0,
                "end_time": 960,  # 2 beats
                "interval": "480t",  # 480 ticks per step
                "commands": [],
                "source_line": 1,
            }
        ]

        events = expander.process_ast(nodes)

        # Sweep without commands doesn't generate events, but updates stats and time
        assert len(events) == 0  # No commands = no events
        assert expander.stats.sweeps_expanded == 1
        assert expander.current_time == 960  # Time should advance to end_time

    def test_sweep_invalid_times_error(self, expander):
        """Test error on end_time <= start_time."""
        nodes = [
            {
                "type": "sweep",
                "start_time": 1000,
                "end_time": 500,  # Before start!
                "interval": "100t",
                "commands": [],
                "source_line": 1,
            }
        ]

        with pytest.raises(InvalidSweepConfigError, match="must be after start time"):
            expander.process_ast(nodes)

    def test_sweep_invalid_interval_error(self, expander):
        """Test error on malformed interval string."""
        nodes = [
            {
                "type": "sweep",
                "start_time": 0,
                "end_time": 1000,
                "interval": "bad_format",  # Invalid
                "commands": [],
                "source_line": 1,
            }
        ]

        with pytest.raises(InvalidSweepConfigError, match="Invalid sweep interval"):
            expander.process_ast(nodes)

    def test_sweep_updates_current_time(self, expander):
        """Test that current_time = end_time after sweep."""
        nodes = [
            {
                "type": "sweep",
                "start_time": 0,
                "end_time": 2000,
                "interval": "500t",
                "commands": [],
                "source_line": 1,
            }
        ]

        expander.process_ast(nodes)

        assert expander.current_time == 2000

    def test_sweep_updates_stats(self, expander):
        """Test that sweeps_expanded counter increments."""
        nodes = [
            {
                "type": "sweep",
                "start_time": 0,
                "end_time": 1000,
                "interval": "250t",
                "commands": [],
                "source_line": 1,
            },
            {
                "type": "sweep",
                "start_time": 2000,
                "end_time": 3000,
                "interval": "250t",
                "commands": [],
                "source_line": 5,
            },
        ]

        expander.process_ast(nodes)

        assert expander.stats.sweeps_expanded == 2

    def test_sweep_generates_events(self, expander):
        """Test that sweep generates events."""
        nodes = [
            {
                "type": "sweep",
                "start_time": 0,
                "end_time": 480,  # 1 beat
                "interval": "120t",  # 8th note
                "commands": [
                    {
                        "type": "cc",
                        "channel": 1,
                        "data1": 7,
                        "data2": {"type": "ramp", "start": 0, "end": 127, "ramp_type": "linear"},
                    }
                ],
                "source_line": 1,
            }
        ]

        events = expander.process_ast(nodes)

        # Should generate at least 2 events (start and end)
        assert len(events) >= 2


class TestSweepRampParsing:
    """Test parsing of ramp expressions in sweep commands."""

    @pytest.fixture
    def expander(self):
        return CommandExpander(ppq=480, tempo=120.0, source_file="test.mmd")

    def test_linear_ramp_parsing(self, expander):
        """Test parsing linear ramp from CC command."""
        from midi_markdown.parser.ast_nodes import MIDICommand

        ramp_dict = {"type": "ramp", "start": 0, "end": 127, "ramp_type": "linear"}
        cmd = MIDICommand(type="cc", channel=1, data1=7, data2=ramp_dict)

        nodes = [
            {
                "type": "sweep",
                "start_time": 0,
                "end_time": 1000,
                "interval": "100t",
                "commands": [cmd],
                "source_line": 1,
            }
        ]

        events = expander.process_ast(nodes)
        assert len(events) > 0
        # Verify all events are CC type
        for event in events:
            assert event["type"] == "cc"
            assert event["channel"] == 1
            assert event["data1"] == 7

    def test_exponential_ramp_parsing(self, expander):
        """Test parsing exponential ramp."""
        from midi_markdown.parser.ast_nodes import MIDICommand

        ramp_dict = {"type": "ramp", "start": 0, "end": 127, "ramp_type": "exponential"}
        cmd = MIDICommand(type="cc", channel=1, data1=74, data2=ramp_dict)

        nodes = [
            {
                "type": "sweep",
                "start_time": 0,
                "end_time": 1000,
                "interval": "100t",
                "commands": [cmd],
                "source_line": 1,
            }
        ]

        events = expander.process_ast(nodes)
        assert len(events) > 0

    def test_logarithmic_ramp_parsing(self, expander):
        """Test parsing logarithmic ramp."""
        from midi_markdown.parser.ast_nodes import MIDICommand

        ramp_dict = {"type": "ramp", "start": 0, "end": 127, "ramp_type": "logarithmic"}
        cmd = MIDICommand(type="cc", channel=1, data1=10, data2=ramp_dict)

        nodes = [
            {
                "type": "sweep",
                "start_time": 0,
                "end_time": 1000,
                "interval": "100t",
                "commands": [cmd],
                "source_line": 1,
            }
        ]

        events = expander.process_ast(nodes)
        assert len(events) > 0

    def test_ease_in_ramp_parsing(self, expander):
        """Test parsing ease-in ramp."""
        from midi_markdown.parser.ast_nodes import MIDICommand

        ramp_dict = {"type": "ramp", "start": 0, "end": 127, "ramp_type": "ease-in"}
        cmd = MIDICommand(type="cc", channel=1, data1=11, data2=ramp_dict)

        nodes = [
            {
                "type": "sweep",
                "start_time": 0,
                "end_time": 1000,
                "interval": "100t",
                "commands": [cmd],
                "source_line": 1,
            }
        ]

        events = expander.process_ast(nodes)
        assert len(events) > 0

    def test_ease_out_ramp_parsing(self, expander):
        """Test parsing ease-out ramp."""
        from midi_markdown.parser.ast_nodes import MIDICommand

        ramp_dict = {"type": "ramp", "start": 0, "end": 127, "ramp_type": "ease-out"}
        cmd = MIDICommand(type="cc", channel=1, data1=11, data2=ramp_dict)

        nodes = [
            {
                "type": "sweep",
                "start_time": 0,
                "end_time": 1000,
                "interval": "100t",
                "commands": [cmd],
                "source_line": 1,
            }
        ]

        events = expander.process_ast(nodes)
        assert len(events) > 0

    def test_ease_in_out_ramp_parsing(self, expander):
        """Test parsing ease-in-out ramp."""
        from midi_markdown.parser.ast_nodes import MIDICommand

        ramp_dict = {"type": "ramp", "start": 0, "end": 127, "ramp_type": "ease-in-out"}
        cmd = MIDICommand(type="cc", channel=1, data1=11, data2=ramp_dict)

        nodes = [
            {
                "type": "sweep",
                "start_time": 0,
                "end_time": 1000,
                "interval": "100t",
                "commands": [cmd],
                "source_line": 1,
            }
        ]

        events = expander.process_ast(nodes)
        assert len(events) > 0

    def test_custom_range_ramp(self, expander):
        """Test ramp with custom start/end range."""
        from midi_markdown.parser.ast_nodes import MIDICommand

        ramp_dict = {"type": "ramp", "start": 20, "end": 100, "ramp_type": "linear"}
        cmd = MIDICommand(type="cc", channel=1, data1=7, data2=ramp_dict)

        nodes = [
            {
                "type": "sweep",
                "start_time": 0,
                "end_time": 480,  # 1 beat
                "interval": "120t",  # 4 steps
                "commands": [cmd],
                "source_line": 1,
            }
        ]

        events = expander.process_ast(nodes)
        # First event should be around 20, last around 100
        assert events[0]["data2"] >= 18
        assert events[0]["data2"] <= 22
        assert events[-1]["data2"] >= 98
        assert events[-1]["data2"] <= 102

    def test_reverse_ramp(self, expander):
        """Test ramp from high to low."""
        from midi_markdown.parser.ast_nodes import MIDICommand

        ramp_dict = {"type": "ramp", "start": 127, "end": 0, "ramp_type": "linear"}
        cmd = MIDICommand(type="cc", channel=1, data1=7, data2=ramp_dict)

        nodes = [
            {
                "type": "sweep",
                "start_time": 0,
                "end_time": 480,
                "interval": "120t",
                "commands": [cmd],
                "source_line": 1,
            }
        ]

        events = expander.process_ast(nodes)
        # First event should be high, last should be low
        assert events[0]["data2"] > events[-1]["data2"]
        assert events[-1]["data2"] <= 5
