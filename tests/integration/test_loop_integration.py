"""
Integration tests for loop functionality.

Phase 3: Tests loop expansion with LoopExpander and EventGenerator.
"""

from pathlib import Path

import pytest

from midi_markdown.expansion.loops import (
    IntervalType,
    LoopCommand,
    LoopDefinition,
    LoopExpander,
    LoopInterval,
)
from midi_markdown.expansion.variables import SymbolTable


class TestLoopExpanderIntegration:
    """Test LoopExpander with realistic scenarios."""

    @pytest.fixture
    def expander(self):
        """Create a LoopExpander with symbol table."""
        symbols = SymbolTable()
        return LoopExpander(parent_symbols=symbols, ppq=480, tempo=120.0)

    def test_simple_loop_expansion(self, expander):
        """Test expanding a simple loop with PC commands."""
        # Create a loop that generates 3 PC commands, 1 beat apart
        loop_def = LoopDefinition(
            count=3,
            interval=LoopInterval(value=1.0, interval_type=IntervalType.BEATS),
            commands=[
                LoopCommand(command={"type": "pc", "channel": 1, "data1": 10}, relative_time=0)
            ],
            start_time=0,
        )

        events = expander.expand(loop_def)

        # Should generate 3 events
        assert len(events) == 3

        # Check timing - 1 beat = 480 ticks at 480 PPQ
        assert events[0]["time"] == 0
        assert events[1]["time"] == 480
        assert events[2]["time"] == 960

        # Check all have same command
        for event in events:
            assert event["type"] == "pc"
            assert event["channel"] == 1
            assert event["data1"] == 10

    def test_loop_with_variables(self, expander):
        """Test loop using LOOP_INDEX variable."""
        # Add a base variable to symbol table
        expander.parent_symbols.define("BASE", 10)

        # Create loop that uses LOOP_INDEX
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

        # Should have incremental LOOP_INDEX values
        assert events[0]["data1"] == 0  # LOOP_INDEX starts at 0
        assert events[1]["data1"] == 1
        assert events[2]["data1"] == 2

    def test_loop_with_parent_variable(self, expander):
        """Test loop accessing parent scope variables."""
        # Define variable in parent scope
        expander.parent_symbols.define("PRESET", 42)

        loop_def = LoopDefinition(
            count=2,
            interval=LoopInterval(value=1.0, interval_type=IntervalType.BEATS),
            commands=[
                LoopCommand(
                    command={"type": "pc", "channel": 1, "data1": ("var", "PRESET")},
                    relative_time=0,
                )
            ],
            start_time=0,
        )

        events = expander.expand(loop_def)

        # All events should use parent variable value
        assert events[0]["data1"] == 42
        assert events[1]["data1"] == 42

    def test_loop_with_multiple_commands(self, expander):
        """Test loop with multiple commands per iteration."""
        loop_def = LoopDefinition(
            count=2,
            interval=LoopInterval(value=1.0, interval_type=IntervalType.BEATS),
            commands=[
                LoopCommand(command={"type": "pc", "channel": 1, "data1": 10}, relative_time=0),
                LoopCommand(
                    command={"type": "cc", "channel": 1, "data1": 7, "data2": 100},
                    relative_time=120,
                ),
            ],
            start_time=0,
        )

        events = expander.expand(loop_def)

        # Should generate 4 events (2 iterations * 2 commands)
        assert len(events) == 4

        # First iteration
        assert events[0]["time"] == 0
        assert events[0]["type"] == "pc"
        assert events[1]["time"] == 120  # 120 ticks offset
        assert events[1]["type"] == "cc"

        # Second iteration (480 ticks later)
        assert events[2]["time"] == 480
        assert events[2]["type"] == "pc"
        assert events[3]["time"] == 600  # 480 + 120
        assert events[3]["type"] == "cc"

    def test_loop_with_ticks_interval(self, expander):
        """Test loop with ticks-based interval."""
        loop_def = LoopDefinition(
            count=3,
            interval=LoopInterval(value=240.0, interval_type=IntervalType.TICKS),
            commands=[
                LoopCommand(command={"type": "pc", "channel": 1, "data1": 5}, relative_time=0)
            ],
            start_time=0,
        )

        events = expander.expand(loop_def)

        # Should be spaced 240 ticks apart
        assert events[0]["time"] == 0
        assert events[1]["time"] == 240
        assert events[2]["time"] == 480

    def test_loop_with_bbt_interval(self, expander):
        """Test loop with BBT (Bars.Beats.Ticks) interval."""
        # 1 bar, 0 beats, 0 ticks = 4 beats = 1920 ticks at 4/4
        loop_def = LoopDefinition(
            count=2,
            interval=LoopInterval(value=(1, 0, 0), interval_type=IntervalType.BBT),
            commands=[
                LoopCommand(command={"type": "pc", "channel": 1, "data1": 5}, relative_time=0)
            ],
            start_time=0,
        )

        events = expander.expand(loop_def)

        # 1 bar = 4 beats = 1920 ticks
        assert events[0]["time"] == 0
        assert events[1]["time"] == 1920

    def test_loop_with_non_zero_start(self, expander):
        """Test loop starting at non-zero time."""
        loop_def = LoopDefinition(
            count=2,
            interval=LoopInterval(value=1.0, interval_type=IntervalType.BEATS),
            commands=[
                LoopCommand(command={"type": "pc", "channel": 1, "data1": 5}, relative_time=0)
            ],
            start_time=2400,  # Start at 5 beats
        )

        events = expander.expand(loop_def)

        assert events[0]["time"] == 2400
        assert events[1]["time"] == 2880  # 2400 + 480


class TestLoopScoping:
    """Test loop variable scoping."""

    def test_loop_variables_isolated_per_iteration(self):
        """Test that loop variables are independent per iteration."""
        symbols = SymbolTable()
        expander = LoopExpander(parent_symbols=symbols, ppq=480, tempo=120.0)

        loop_def = LoopDefinition(
            count=3,
            interval=LoopInterval(value=1.0, interval_type=IntervalType.BEATS),
            commands=[
                LoopCommand(
                    command={
                        "type": "cc",
                        "channel": 1,
                        "data1": ("var", "LOOP_INDEX"),
                        "data2": ("var", "LOOP_ITERATION"),
                    },
                    relative_time=0,
                )
            ],
            start_time=0,
        )

        events = expander.expand(loop_def)

        # Check that LOOP_INDEX and LOOP_ITERATION are different
        assert events[0]["data1"] == 0  # LOOP_INDEX
        assert events[0]["data2"] == 1  # LOOP_ITERATION

        assert events[1]["data1"] == 1
        assert events[1]["data2"] == 2

        assert events[2]["data1"] == 2
        assert events[2]["data2"] == 3

    def test_loop_count_constant(self):
        """Test that LOOP_COUNT is the same for all iterations."""
        symbols = SymbolTable()
        expander = LoopExpander(parent_symbols=symbols, ppq=480, tempo=120.0)

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

        # LOOP_COUNT should be 5 for all events
        for event in events:
            assert event["data2"] == 5


class TestLoopIntervalParsing:
    """Test interval parsing for loops."""

    def test_parse_beats_interval(self):
        """Test parsing beat interval strings."""
        from midi_markdown.expansion.loops import parse_interval

        interval = parse_interval("2b")
        assert interval.value == 2.0
        assert interval.interval_type == IntervalType.BEATS

    def test_parse_ticks_interval(self):
        """Test parsing tick interval strings."""
        from midi_markdown.expansion.loops import parse_interval

        interval = parse_interval("480t")
        assert interval.value == 480.0
        assert interval.interval_type == IntervalType.TICKS

    def test_parse_milliseconds_interval(self):
        """Test parsing millisecond interval strings."""
        from midi_markdown.expansion.loops import parse_interval

        interval = parse_interval("500ms")
        assert interval.value == 500.0
        assert interval.interval_type == IntervalType.MILLISECONDS

    def test_parse_bbt_interval(self):
        """Test parsing BBT interval strings."""
        from midi_markdown.expansion.loops import parse_interval

        interval = parse_interval("1.2.100")
        assert interval.value == (1, 2, 100)
        assert interval.interval_type == IntervalType.BBT


class TestLoopsBasicFixture:
    """Test the loops_basic.mmd fixture file."""

    def test_loops_basic_file(self, parser):
        """Test that loops_basic.mmd parses correctly."""
        fixture_path = Path(__file__).parent.parent / "fixtures" / "loops_basic.mmd"

        # This will be implemented when parser grammar is fully integrated
        doc = parser.parse_file(fixture_path)

        # Check that loops were parsed
        # (Specific assertions depend on parser output structure)
        assert doc is not None
