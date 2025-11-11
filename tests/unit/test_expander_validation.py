"""
Unit tests for CommandExpander validation, error handling, and statistics.

Phase 4: Tests event validation, error handling, and statistics tracking.
"""

import pytest

from midi_markdown.expansion.errors import (
    InvalidLoopConfigError,
    InvalidSweepConfigError,
    TimingConflictError,
    UndefinedVariableError,
    ValueRangeError,
)
from midi_markdown.expansion.expander import CommandExpander, ExpansionStats


class TestEventValidation:
    """Test event validation."""

    def test_valid_channel_range(self, expander):
        """Test valid channel range (1-16)."""
        events = [
            {"type": "pc", "channel": 1, "data1": 10, "time": 0},
            {"type": "pc", "channel": 16, "data1": 10, "time": 100},
        ]

        # Should not raise
        expander._validate_events(events)

    def test_invalid_channel_error(self, expander):
        """Test error on invalid channel (0, 17+)."""
        events = [{"type": "pc", "channel": 0, "data1": 10, "time": 0}]

        with pytest.raises(ValueRangeError, match="channel"):
            expander._validate_events(events)

    def test_valid_midi_values(self, expander):
        """Test valid MIDI values (0-127)."""
        events = [{"type": "cc", "channel": 1, "data1": 0, "data2": 127, "time": 0}]

        # Should not raise
        expander._validate_events(events)

    def test_invalid_midi_value_error(self, expander):
        """Test error on out-of-range values (128+)."""
        events = [{"type": "cc", "channel": 1, "data1": 128, "data2": 50, "time": 0}]

        with pytest.raises(ValueRangeError, match="data1"):
            expander._validate_events(events)

    # NOTE: This test was removed because _validate_events() sorts events before
    # validation, so non-monotonic timing is handled by reordering rather than error.
    # Timing monotonicity is properly tested in test_timing_validation.py using
    # the TimingValidator module, which validates document order without sorting.
    def test_timing_monotonicity_handled_by_sorting(self, expander):
        """Test that non-monotonic times are handled by sorting."""
        events = [
            {"type": "pc", "time": 1000, "channel": 1, "data1": 10},
            {"type": "pc", "time": 500, "channel": 1, "data1": 10},  # Earlier!
        ]

        # Should not raise - events are sorted before validation
        expander._validate_events(events)


class TestErrorHandling:
    """Test expansion error handling."""

    def test_undefined_variable_error_format(self):
        """Test UndefinedVariableError message format."""
        error = UndefinedVariableError("MISSING", line=10, file="test.mmd")

        error_str = str(error)
        assert "test.mmd:10" in error_str
        assert "MISSING" in error_str

    def test_undefined_variable_suggestions(self):
        """Test 'did you mean' suggestions."""
        similar = ["PRESENT", "PRESET"]
        error = UndefinedVariableError("PRSET", line=5, file="test.mmd", similar_names=similar)

        error_str = str(error)
        assert "Did you mean" in error_str
        assert "PRESENT" in error_str or "PRESET" in error_str

    def test_invalid_loop_config_error(self):
        """Test InvalidLoopConfigError."""
        error = InvalidLoopConfigError(
            "count must be positive", line=3, file="test.mmd", suggestion="Use a positive integer"
        )

        error_str = str(error)
        assert "count must be positive" in error_str
        assert "Use a positive integer" in error_str

    def test_invalid_sweep_config_error(self):
        """Test InvalidSweepConfigError."""
        error = InvalidSweepConfigError("end before start", line=7, file="test.mmd")

        error_str = str(error)
        assert "end before start" in error_str

    def test_timing_conflict_error(self):
        """Test TimingConflictError."""
        error = TimingConflictError("time decreased", event_time=500, line=12, file="test.mmd")

        error_str = str(error)
        assert "500" in error_str
        assert "chronological" in error_str

    def test_value_range_error(self):
        """Test ValueRangeError with helpful message."""
        error = ValueRangeError("velocity", 200, 0, 127, line=15, file="test.mmd")

        error_str = str(error)
        assert "velocity" in error_str
        assert "200" in error_str
        assert "0-127" in error_str or "[0-127]" in error_str


class TestStatistics:
    """Test expansion statistics tracking."""

    def test_stats_initialization(self):
        """Test that stats start at zero."""
        expander = CommandExpander()

        stats = expander.get_stats()
        assert stats.defines_processed == 0
        assert stats.loops_expanded == 0
        assert stats.sweeps_expanded == 0
        assert stats.events_generated == 0
        assert stats.variables_substituted == 0

    def test_stats_updated_during_processing(self):
        """Test that counters increment during processing."""
        expander = CommandExpander()

        nodes = [
            {"type": "define", "name": "CH", "value": 1, "line": 1},
            {"type": "define", "name": "PRESET", "value": 10, "line": 2},
            # Regular command with variables
            {"type": "pc", "channel": ("var", "CH"), "data1": ("var", "PRESET")},
            # Loop
            {
                "type": "loop",
                "count": 2,
                "interval": "1b",
                "statements": [{"type": "cc", "channel": 1, "data1": 7, "data2": 100}],
                "source_line": 3,
            },
        ]

        events = expander.process_ast(nodes)
        stats = expander.get_stats()

        assert stats.defines_processed == 2
        assert stats.loops_expanded == 1
        assert stats.events_generated == len(events)
        # Regular command has 2 variable substitutions (CH and PRESET)
        assert stats.variables_substituted == 2

    def test_get_stats_method(self):
        """Test get_stats() returns ExpansionStats."""
        expander = CommandExpander()
        stats = expander.get_stats()

        assert isinstance(stats, ExpansionStats)
