"""
Unit tests for CommandExpander @loop processing.

Phase 4: Tests @loop statement processing and expansion.
"""

import pytest

from midi_markdown.expansion.errors import InvalidLoopConfigError
from midi_markdown.expansion.expander import CommandExpander


class TestLoopProcessing:
    """Test @loop statement processing."""

    @pytest.fixture
    def expander(self):
        return CommandExpander(ppq=480, tempo=120.0, source_file="test.mmd")

    def test_simple_loop_expansion(self, expander):
        """Test basic loop with count and interval."""
        nodes = [
            {
                "type": "loop",
                "count": 3,
                "interval": "1b",  # 1 beat
                "start_time": None,
                "statements": [{"type": "pc", "channel": 1, "data1": 10}],
                "source_line": 1,
            }
        ]

        events = expander.process_ast(nodes)

        # Should generate 3 events, 480 ticks apart
        assert len(events) == 3
        assert events[0]["time"] == 0
        assert events[1]["time"] == 480
        assert events[2]["time"] == 960
        assert expander.stats.loops_expanded == 1

    def test_loop_with_beat_interval(self, expander):
        """Test loop with beat interval (1b, 2b)."""
        nodes = [
            {
                "type": "loop",
                "count": 2,
                "interval": "2b",  # 2 beats
                "start_time": None,
                "statements": [{"type": "pc", "channel": 1, "data1": 5}],
                "source_line": 1,
            }
        ]

        events = expander.process_ast(nodes)

        # 2 beats = 960 ticks at 480 PPQ
        assert events[0]["time"] == 0
        assert events[1]["time"] == 960

    def test_loop_with_tick_interval(self, expander):
        """Test loop with tick interval (480t)."""
        nodes = [
            {
                "type": "loop",
                "count": 2,
                "interval": "240t",  # 240 ticks
                "start_time": None,
                "statements": [{"type": "pc", "channel": 1, "data1": 5}],
                "source_line": 1,
            }
        ]

        events = expander.process_ast(nodes)

        assert events[0]["time"] == 0
        assert events[1]["time"] == 240

    def test_loop_with_bbt_interval(self, expander):
        """Test loop with BBT interval (bars.beats.ticks)."""
        nodes = [
            {
                "type": "loop",
                "count": 2,
                "interval": "1.0.0",  # 1 bar = 4 beats = 1920 ticks
                "start_time": None,
                "statements": [{"type": "pc", "channel": 1, "data1": 5}],
                "source_line": 1,
            }
        ]

        events = expander.process_ast(nodes)

        # 1 bar = 4 beats = 1920 ticks at 4/4
        assert events[0]["time"] == 0
        assert events[1]["time"] == 1920

    def test_loop_invalid_count_error(self, expander):
        """Test error on invalid loop count (<= 0)."""
        nodes = [
            {
                "type": "loop",
                "count": 0,  # Invalid
                "interval": "1b",
                "statements": [],
                "source_line": 1,
            }
        ]

        with pytest.raises(InvalidLoopConfigError, match="count must be positive"):
            expander.process_ast(nodes)

    def test_loop_invalid_interval_error(self, expander):
        """Test error on malformed interval string."""
        nodes = [
            {
                "type": "loop",
                "count": 2,
                "interval": "invalid",  # Malformed
                "statements": [],
                "source_line": 1,
            }
        ]

        with pytest.raises(InvalidLoopConfigError, match="Invalid loop interval"):
            expander.process_ast(nodes)

    def test_loop_updates_current_time(self, expander):
        """Test that current_time advances after loop."""
        nodes = [
            {
                "type": "loop",
                "count": 3,
                "interval": "1b",
                "start_time": None,
                "statements": [{"type": "pc", "channel": 1, "data1": 10}],
                "source_line": 1,
            }
        ]

        expander.process_ast(nodes)

        # After 3 iterations of 1 beat each = 1440 ticks
        assert expander.current_time == 1440

    def test_loop_updates_stats(self, expander):
        """Test that loops_expanded counter increments."""
        nodes = [
            {
                "type": "loop",
                "count": 2,
                "interval": "1b",
                "statements": [{"type": "pc", "channel": 1, "data1": 10}],
                "source_line": 1,
            },
            {
                "type": "loop",
                "count": 3,
                "interval": "1b",
                "statements": [{"type": "cc", "channel": 1, "data1": 7, "data2": 100}],
                "source_line": 5,
            },
        ]

        expander.process_ast(nodes)

        assert expander.stats.loops_expanded == 2
