"""Unit tests for expansion and timing error formatting (Phase 4, Stage 3)."""

from __future__ import annotations

from unittest.mock import Mock

from rich.console import Console

from midi_markdown.alias.errors import AliasMaxDepthError, AliasRecursionError
from midi_markdown.cli.errors import (
    _create_call_chain_table,
    _create_expansion_help_table,
    _create_timing_help_table,
    show_alias_error,
    show_expansion_error,
    show_validation_error,
)
from midi_markdown.expansion.errors import (
    InvalidLoopConfigError,
    InvalidSweepConfigError,
)
from midi_markdown.utils.validation import ValidationError


class TestExpansionHelpTables:
    """Test expansion error help table creation."""

    def test_loop_error_help_table(self):
        """Test help table for loop configuration errors."""
        error = InvalidLoopConfigError(
            "Invalid loop syntax", line=10, file="test.mmd", suggestion="Use correct loop syntax"
        )

        table = _create_expansion_help_table(error, no_color=False)
        assert table is not None

    def test_sweep_error_help_table(self):
        """Test help table for sweep configuration errors."""
        error = InvalidSweepConfigError(
            "Invalid sweep syntax", line=15, file="test.mmd", suggestion="Use correct sweep syntax"
        )

        table = _create_expansion_help_table(error, no_color=False)
        assert table is not None

    def test_expansion_help_table_no_color(self):
        """Test expansion help table with no_color flag."""
        error = InvalidLoopConfigError(
            "Invalid loop", line=10, file="test.mmd", suggestion="Fix loop"
        )

        table = _create_expansion_help_table(error, no_color=True)
        assert table is not None

    def test_non_loop_sweep_error_returns_none(self):
        """Test that non-loop/sweep errors return None."""
        from midi_markdown.expansion.errors import UndefinedVariableError

        error = UndefinedVariableError("foo", line=10, file="test.mmd", similar_names=["bar"])

        table = _create_expansion_help_table(error, no_color=False)
        assert table is None


class TestTimingHelpTables:
    """Test timing error help table creation."""

    def test_timing_help_table_for_monotonicity_error(self):
        """Test timing help table for monotonicity errors."""
        error_message = "Time must be monotonically increasing"

        table = _create_timing_help_table(error_message, no_color=False)
        assert table is not None

    def test_timing_help_table_for_musical_time_error(self):
        """Test timing help table for musical time errors."""
        error_message = "Musical time requires tempo to be defined"

        table = _create_timing_help_table(error_message, no_color=False)
        assert table is not None

    def test_timing_help_table_for_relative_timing_error(self):
        """Test timing help table for relative timing errors."""
        error_message = "Relative timing requires a previous event"

        table = _create_timing_help_table(error_message, no_color=False)
        assert table is not None

    def test_timing_help_table_for_simultaneous_error(self):
        """Test timing help table for simultaneous timing errors."""
        error_message = "Simultaneous timing [@] requires a previous event"

        table = _create_timing_help_table(error_message, no_color=False)
        assert table is not None

    def test_timing_help_table_no_color(self):
        """Test timing help table with no_color flag."""
        error_message = "Events must appear in chronological order"

        table = _create_timing_help_table(error_message, no_color=True)
        assert table is not None

    def test_non_timing_error_returns_none(self):
        """Test that non-timing errors return None."""
        error_message = "Channel 99 out of range [1-16]"

        table = _create_timing_help_table(error_message, no_color=False)
        assert table is None


class TestAliasCallChainTables:
    """Test alias call chain visualization."""

    def test_call_chain_table_simple(self):
        """Test call chain table with simple recursion."""
        call_chain = [("alias_a", [1, 2]), ("alias_b", [3])]
        final_alias = "alias_a"

        table = _create_call_chain_table(call_chain, final_alias, no_color=False)
        assert table is not None

    def test_call_chain_table_deep_nesting(self):
        """Test call chain table with deep nesting."""
        call_chain = [
            ("alias_1", [10]),
            ("alias_2", [20]),
            ("alias_3", [30]),
            ("alias_4", [40]),
        ]
        final_alias = "alias_5"

        table = _create_call_chain_table(call_chain, final_alias, no_color=False)
        assert table is not None

    def test_call_chain_table_no_args(self):
        """Test call chain table with aliases that have no arguments."""
        call_chain = [("alias_x", []), ("alias_y", [])]
        final_alias = "alias_x"

        table = _create_call_chain_table(call_chain, final_alias, no_color=False)
        assert table is not None

    def test_call_chain_table_no_color(self):
        """Test call chain table with no_color flag."""
        call_chain = [("foo", [1]), ("bar", [2])]
        final_alias = "baz"

        table = _create_call_chain_table(call_chain, final_alias, no_color=True)
        assert table is not None


class TestExpansionErrorDisplay:
    """Test expansion error display integration."""

    def test_loop_error_displays_help_table(self):
        """Test that loop errors display help table."""
        error = InvalidLoopConfigError("Missing 'times' keyword", line=10, file="test.mmd")

        console = Mock(spec=Console)
        show_expansion_error(error, console, no_color=False, no_emoji=False)

        # Verify console.print was called multiple times (error + table + suggestion)
        assert console.print.call_count >= 2

    def test_sweep_error_displays_help_table(self):
        """Test that sweep errors display help table."""
        error = InvalidSweepConfigError("Invalid sweep duration", line=15, file="test.mmd")

        console = Mock(spec=Console)
        show_expansion_error(error, console, no_color=False, no_emoji=False)

        assert console.print.call_count >= 2


class TestTimingErrorDisplay:
    """Test timing error display integration."""

    def test_timing_error_displays_help_table(self):
        """Test that E212 timing errors display help table."""
        error = ValidationError(
            "Time 00:01.000 is before previous event at 00:02.000",
            line=10,
            column=5,
            error_code="E212",
            suggestion="Events must appear in chronological order",
        )

        console = Mock(spec=Console)
        show_validation_error(error, None, console, no_color=False, no_emoji=False)

        # Verify console.print was called (error + table + suggestion)
        assert console.print.call_count >= 2

    def test_timing_error_no_color(self):
        """Test timing error display with no_color flag."""
        error = ValidationError(
            "Musical time requires tempo",
            error_code="E212",
            suggestion="Add tempo to frontmatter",
        )

        console = Mock(spec=Console)
        show_validation_error(error, None, console, no_color=True, no_emoji=False)

        assert console.print.called


class TestAliasErrorDisplay:
    """Test alias error display with call chain visualization."""

    def test_recursion_error_displays_call_chain(self):
        """Test that alias recursion errors display call chain table."""
        call_chain = [("alias_a", [1, 2]), ("alias_b", [3])]
        error = AliasRecursionError("alias_a", call_chain)

        console = Mock(spec=Console)
        show_alias_error(error, console, no_color=False, no_emoji=False)

        # Verify console.print was called for header, table, and suggestion
        assert console.print.call_count >= 3

    def test_max_depth_error_displays_call_chain(self):
        """Test that max depth errors display call chain table."""
        call_chain = [("a", [1]), ("b", [2]), ("c", [3])]
        error = AliasMaxDepthError("d", 11, 10, call_chain)

        console = Mock(spec=Console)
        show_alias_error(error, console, no_color=False, no_emoji=False)

        assert console.print.call_count >= 3

    def test_recursion_error_no_color(self):
        """Test recursion error display with no_color flag."""
        call_chain = [("foo", []), ("bar", [])]
        error = AliasRecursionError("foo", call_chain)

        console = Mock(spec=Console)
        show_alias_error(error, console, no_color=True, no_emoji=False)

        assert console.print.called

    def test_max_depth_error_no_emoji(self):
        """Test max depth error display with no_emoji flag."""
        call_chain = [("x", [10]), ("y", [20])]
        error = AliasMaxDepthError("z", 6, 5, call_chain)

        console = Mock(spec=Console)
        show_alias_error(error, console, no_color=False, no_emoji=True)

        assert console.print.called


class TestIntegratedErrorFormatting:
    """Test integrated error formatting scenarios."""

    def test_timing_error_has_e212_code(self):
        """Test that timing validators assign E212 code."""

        # This would be tested via integration, but we verify the error structure
        error = ValidationError("Timing error", error_code="E212", suggestion="Fix timing")
        assert error.error_code == "E212"
        assert error.suggestion is not None

    def test_expansion_errors_have_suggestions(self):
        """Test that expansion errors have helpful suggestions."""
        loop_error = InvalidLoopConfigError(
            "Missing times keyword",
            line=10,
            file="test.mmd",
            suggestion="Use: @loop <count> times every <interval>",
        )
        assert loop_error.suggestion is not None

        sweep_error = InvalidSweepConfigError(
            "Missing duration",
            line=15,
            file="test.mmd",
            suggestion="Specify sweep duration with units (e.g., 2s, 4b)",
        )
        assert sweep_error.suggestion is not None

    def test_alias_errors_have_call_chain(self):
        """Test that alias recursion errors have call_chain attribute."""
        call_chain = [("a", [1]), ("b", [2])]
        error = AliasRecursionError("a", call_chain)

        assert hasattr(error, "call_chain")
        assert error.call_chain == call_chain
        assert error.alias_name == "a"

    def test_alias_max_depth_has_depth_info(self):
        """Test that max depth errors have depth information."""
        call_chain = [("x", []), ("y", [])]
        error = AliasMaxDepthError("z", 11, 10, call_chain)

        assert hasattr(error, "current_depth")
        assert hasattr(error, "max_depth")
        assert error.current_depth == 11
        assert error.max_depth == 10
