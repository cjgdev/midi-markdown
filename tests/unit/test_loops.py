"""
Unit tests for loop implementation.
"""

import pytest

from midi_markdown.expansion.loops import (
    IntervalType,
    LoopCommand,
    LoopDefinition,
    LoopExpander,
    LoopInterval,
    parse_interval,
)
from midi_markdown.expansion.variables import SymbolTable


class TestLoopInterval:
    """Test LoopInterval conversion to ticks."""

    def test_beats_to_ticks(self):
        """Test beat interval conversion."""
        interval = LoopInterval(value=2.0, interval_type=IntervalType.BEATS)
        ticks = interval.to_ticks(ppq=480, tempo=120.0)
        assert ticks == 960  # 2 beats * 480 ppq

    def test_ticks_interval(self):
        """Test ticks interval (passthrough)."""
        interval = LoopInterval(value=240.0, interval_type=IntervalType.TICKS)
        ticks = interval.to_ticks(ppq=480, tempo=120.0)
        assert ticks == 240

    def test_milliseconds_to_ticks(self):
        """Test millisecond interval conversion."""
        interval = LoopInterval(value=500.0, interval_type=IntervalType.MILLISECONDS)
        # 500ms = 0.5s, at 120 BPM = 2 beats/sec = 1 beat = 480 ticks
        ticks = interval.to_ticks(ppq=480, tempo=120.0)
        assert ticks == 480

    def test_bbt_to_ticks(self):
        """Test BBT (Bars.Beats.Ticks) interval conversion."""
        # 1 bar, 2 beats, 100 ticks
        interval = LoopInterval(value=(1, 2, 100), interval_type=IntervalType.BBT)
        # 1 bar = 4 beats, + 2 beats = 6 beats = 6 * 480 + 100 = 2980
        ticks = interval.to_ticks(ppq=480, tempo=120.0)
        assert ticks == 2980

    def test_bbt_zero(self):
        """Test BBT with zero values."""
        interval = LoopInterval(value=(0, 0, 0), interval_type=IntervalType.BBT)
        ticks = interval.to_ticks(ppq=480, tempo=120.0)
        assert ticks == 0


class TestParseInterval:
    """Test interval string parsing."""

    def test_parse_beats_short(self):
        """Test parsing '2b' format."""
        interval = parse_interval("2b")
        assert interval.value == 2.0
        assert interval.interval_type == IntervalType.BEATS

    def test_parse_beats_long(self):
        """Test parsing '2 beats' format."""
        interval = parse_interval("2 beats")
        assert interval.value == 2.0
        assert interval.interval_type == IntervalType.BEATS

    def test_parse_ticks_short(self):
        """Test parsing '480t' format."""
        interval = parse_interval("480t")
        assert interval.value == 480.0
        assert interval.interval_type == IntervalType.TICKS

    def test_parse_ticks_long(self):
        """Test parsing '480 ticks' format."""
        interval = parse_interval("480 ticks")
        assert interval.value == 480.0
        assert interval.interval_type == IntervalType.TICKS

    def test_parse_milliseconds(self):
        """Test parsing '500ms' format."""
        interval = parse_interval("500ms")
        assert interval.value == 500.0
        assert interval.interval_type == IntervalType.MILLISECONDS

    def test_parse_bbt(self):
        """Test parsing '1.2.0' BBT format."""
        interval = parse_interval("1.2.0")
        assert interval.value == (1, 2, 0)
        assert interval.interval_type == IntervalType.BBT

    def test_parse_float_beats(self):
        """Test parsing float beat values."""
        interval = parse_interval("1.5b")
        assert interval.value == 1.5
        assert interval.interval_type == IntervalType.BEATS

    def test_parse_default_beats(self):
        """Test parsing bare number defaults to beats."""
        interval = parse_interval("4")
        assert interval.value == 4.0
        assert interval.interval_type == IntervalType.BEATS

    def test_parse_invalid_format(self):
        """Test that invalid format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid interval format"):
            parse_interval("invalid")

    def test_parse_invalid_bbt(self):
        """Test that invalid BBT format raises ValueError.

        Note: With improved BBT validation, "1.2.x" is now rejected earlier
        because the third part is non-numeric, so it falls through to the
        default parser which also fails.
        """
        with pytest.raises(ValueError, match="Invalid interval format"):
            parse_interval("1.2.x")


class TestLoopExpander:
    """Test loop expansion logic."""

    @pytest.fixture
    def symbols(self):
        """Create a symbol table with some test variables."""
        table = SymbolTable()
        table.define("BASE_VALUE", 10)
        return table

    @pytest.fixture
    def expander(self, symbols):
        """Create a LoopExpander instance."""
        return LoopExpander(parent_symbols=symbols, ppq=480, tempo=120.0)

    def test_simple_loop_expansion(self, expander):
        """Test expanding a simple loop without variables."""
        loop_def = LoopDefinition(
            count=3,
            interval=LoopInterval(value=1.0, interval_type=IntervalType.BEATS),
            commands=[
                LoopCommand(command={"type": "pc", "channel": 1, "data1": 5}, relative_time=0)
            ],
            start_time=0,
        )

        events = expander.expand(loop_def)

        assert len(events) == 3
        assert events[0]["time"] == 0
        assert events[1]["time"] == 480  # 1 beat = 480 ticks
        assert events[2]["time"] == 960  # 2 beats = 960 ticks

    def test_loop_variables(self, expander):
        """Test that loop variables are defined correctly."""
        loop_def = LoopDefinition(
            count=3,
            interval=LoopInterval(value=1.0, interval_type=IntervalType.BEATS),
            commands=[
                LoopCommand(
                    command={"type": "pc", "channel": 1, "data1": ("var", "LOOP_INDEX")},
                    relative_time=0,
                )
            ],
            start_time=0,
        )

        events = expander.expand(loop_def)

        assert len(events) == 3
        assert events[0]["data1"] == 0  # LOOP_INDEX starts at 0
        assert events[1]["data1"] == 1
        assert events[2]["data1"] == 2

    def test_loop_iteration_variable(self, expander):
        """Test LOOP_ITERATION (1-indexed) variable."""
        loop_def = LoopDefinition(
            count=3,
            interval=LoopInterval(value=1.0, interval_type=IntervalType.BEATS),
            commands=[
                LoopCommand(
                    command={"type": "pc", "channel": 1, "data1": ("var", "LOOP_ITERATION")},
                    relative_time=0,
                )
            ],
            start_time=0,
        )

        events = expander.expand(loop_def)

        assert len(events) == 3
        assert events[0]["data1"] == 1  # LOOP_ITERATION starts at 1
        assert events[1]["data1"] == 2
        assert events[2]["data1"] == 3

    def test_loop_count_variable(self, expander):
        """Test LOOP_COUNT variable."""
        loop_def = LoopDefinition(
            count=5,
            interval=LoopInterval(value=1.0, interval_type=IntervalType.BEATS),
            commands=[
                LoopCommand(
                    command={
                        "type": "cc",
                        "channel": 1,
                        "data1": 7,
                        "data2": ("var", "LOOP_COUNT"),
                    },
                    relative_time=0,
                )
            ],
            start_time=0,
        )

        events = expander.expand(loop_def)

        assert len(events) == 5
        # All events should have LOOP_COUNT = 5
        for event in events:
            assert event["data2"] == 5

    def test_parent_variable_access(self, expander):
        """Test that loop can access parent scope variables."""
        loop_def = LoopDefinition(
            count=2,
            interval=LoopInterval(value=1.0, interval_type=IntervalType.BEATS),
            commands=[
                LoopCommand(
                    command={"type": "pc", "channel": 1, "data1": ("var", "BASE_VALUE")},
                    relative_time=0,
                )
            ],
            start_time=0,
        )

        events = expander.expand(loop_def)

        assert len(events) == 2
        assert events[0]["data1"] == 10  # BASE_VALUE from parent
        assert events[1]["data1"] == 10

    def test_multiple_commands_per_iteration(self, expander):
        """Test loop with multiple commands per iteration."""
        loop_def = LoopDefinition(
            count=2,
            interval=LoopInterval(value=1.0, interval_type=IntervalType.BEATS),
            commands=[
                LoopCommand(command={"type": "pc", "channel": 1, "data1": 5}, relative_time=0),
                LoopCommand(
                    command={"type": "cc", "channel": 1, "data1": 7, "data2": 100},
                    relative_time=120,
                ),
            ],
            start_time=0,
        )

        events = expander.expand(loop_def)

        assert len(events) == 4  # 2 iterations * 2 commands
        # First iteration
        assert events[0]["time"] == 0
        assert events[1]["time"] == 120  # relative_time offset
        # Second iteration
        assert events[2]["time"] == 480  # 1 beat later
        assert events[3]["time"] == 600  # 480 + 120

    def test_loop_with_non_zero_start_time(self, expander):
        """Test loop starting at non-zero time."""
        loop_def = LoopDefinition(
            count=2,
            interval=LoopInterval(value=1.0, interval_type=IntervalType.BEATS),
            commands=[
                LoopCommand(command={"type": "pc", "channel": 1, "data1": 5}, relative_time=0)
            ],
            start_time=1920,  # Start at 4 beats
        )

        events = expander.expand(loop_def)

        assert len(events) == 2
        assert events[0]["time"] == 1920
        assert events[1]["time"] == 2400  # 1920 + 480

    def test_nested_dict_variable_resolution(self, expander):
        """Test variable resolution in nested dicts."""
        loop_def = LoopDefinition(
            count=2,
            interval=LoopInterval(value=1.0, interval_type=IntervalType.BEATS),
            commands=[
                LoopCommand(
                    command={"type": "custom", "nested": {"value": ("var", "LOOP_INDEX")}},
                    relative_time=0,
                )
            ],
            start_time=0,
        )

        events = expander.expand(loop_def)

        assert len(events) == 2
        assert events[0]["nested"]["value"] == 0
        assert events[1]["nested"]["value"] == 1

    def test_list_variable_resolution(self, expander):
        """Test variable resolution in lists."""
        loop_def = LoopDefinition(
            count=2,
            interval=LoopInterval(value=1.0, interval_type=IntervalType.BEATS),
            commands=[
                LoopCommand(
                    command={"type": "custom", "values": [("var", "LOOP_INDEX"), 10, 20]},
                    relative_time=0,
                )
            ],
            start_time=0,
        )

        events = expander.expand(loop_def)

        assert len(events) == 2
        assert events[0]["values"] == [0, 10, 20]
        assert events[1]["values"] == [1, 10, 20]

    def test_undefined_variable_preserved(self, expander):
        """Test that undefined variables are preserved as tuples."""
        loop_def = LoopDefinition(
            count=2,
            interval=LoopInterval(value=1.0, interval_type=IntervalType.BEATS),
            commands=[
                LoopCommand(
                    command={"type": "pc", "channel": 1, "data1": ("var", "UNDEFINED")},
                    relative_time=0,
                )
            ],
            start_time=0,
        )

        events = expander.expand(loop_def)

        assert len(events) == 2
        # Undefined variable should be preserved as tuple
        assert events[0]["data1"] == ("var", "UNDEFINED")
        assert events[1]["data1"] == ("var", "UNDEFINED")


class TestLoopIntervalTypes:
    """Test different interval types in loops."""

    @pytest.fixture
    def expander(self):
        """Create a LoopExpander instance."""
        return LoopExpander(parent_symbols=SymbolTable(), ppq=480, tempo=120.0)

    def test_ticks_interval(self, expander):
        """Test loop with ticks interval."""
        loop_def = LoopDefinition(
            count=3,
            interval=LoopInterval(value=240.0, interval_type=IntervalType.TICKS),
            commands=[
                LoopCommand(command={"type": "pc", "channel": 1, "data1": 5}, relative_time=0)
            ],
            start_time=0,
        )

        events = expander.expand(loop_def)
        assert events[0]["time"] == 0
        assert events[1]["time"] == 240
        assert events[2]["time"] == 480

    def test_milliseconds_interval(self, expander):
        """Test loop with milliseconds interval."""
        loop_def = LoopDefinition(
            count=2,
            interval=LoopInterval(value=500.0, interval_type=IntervalType.MILLISECONDS),
            commands=[
                LoopCommand(command={"type": "pc", "channel": 1, "data1": 5}, relative_time=0)
            ],
            start_time=0,
        )

        events = expander.expand(loop_def)
        # 500ms = 0.5s at 120 BPM = 1 beat = 480 ticks
        assert events[0]["time"] == 0
        assert events[1]["time"] == 480

    def test_bbt_interval(self, expander):
        """Test loop with BBT interval."""
        loop_def = LoopDefinition(
            count=2,
            interval=LoopInterval(value=(0, 2, 0), interval_type=IntervalType.BBT),  # 2 beats
            commands=[
                LoopCommand(command={"type": "pc", "channel": 1, "data1": 5}, relative_time=0)
            ],
            start_time=0,
        )

        events = expander.expand(loop_def)
        # 2 beats = 960 ticks
        assert events[0]["time"] == 0
        assert events[1]["time"] == 960


class TestLoopDataclasses:
    """Test loop dataclasses."""

    def test_loop_command_creation(self):
        """Test creating LoopCommand."""
        cmd = LoopCommand(command={"type": "pc", "channel": 1, "data1": 5}, relative_time=100)
        assert cmd.command["type"] == "pc"
        assert cmd.relative_time == 100

    def test_loop_definition_creation(self):
        """Test creating LoopDefinition."""
        interval = LoopInterval(value=1.0, interval_type=IntervalType.BEATS)
        loop_def = LoopDefinition(count=5, interval=interval, start_time=480, source_line=10)
        assert loop_def.count == 5
        assert loop_def.interval == interval
        assert loop_def.start_time == 480
        assert loop_def.source_line == 10
        assert loop_def.commands == []  # Default empty list

    def test_loop_definition_with_commands(self):
        """Test LoopDefinition with commands."""
        interval = LoopInterval(value=1.0, interval_type=IntervalType.BEATS)
        commands = [
            LoopCommand(command={"type": "pc"}, relative_time=0),
            LoopCommand(command={"type": "cc"}, relative_time=100),
        ]
        loop_def = LoopDefinition(count=3, interval=interval, commands=commands)
        assert len(loop_def.commands) == 2
        assert loop_def.commands[0].command["type"] == "pc"
        assert loop_def.commands[1].command["type"] == "cc"
