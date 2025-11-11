"""Tests for timing support in alias definitions."""

from __future__ import annotations

import pytest

from midi_markdown.alias.resolver import AliasResolver
from midi_markdown.parser.ast_nodes import Timing
from midi_markdown.parser.parser import MMDParser


class TestAliasTiming:
    """Test timing statements in alias bodies."""

    def test_simple_relative_timing_in_alias(self):
        """Test alias with single relative timing statement."""
        mml = """
@alias test_timing {ch} {val} "Test timing"
  - cc {ch}.7.0
  [+100ms]
  - cc {ch}.7.{val}
@end
"""
        parser = MMDParser()
        doc = parser.parse_string(mml)

        # Check alias was parsed
        assert "test_timing" in doc.aliases
        alias = doc.aliases["test_timing"]

        # Check commands list contains timing
        assert len(alias.commands) == 3
        assert isinstance(alias.commands[0], str)  # First command
        assert isinstance(alias.commands[1], Timing)  # Timing statement
        assert alias.commands[1].type == "relative"
        assert alias.commands[1].value == (100.0, "ms")
        assert isinstance(alias.commands[2], str)  # Second command

    def test_multiple_relative_timings(self):
        """Test alias with multiple consecutive timing statements."""
        mml = """
@alias test_multi_timing {ch} "Multiple timings"
  - cc {ch}.0.1
  [+50ms]
  - cc {ch}.32.2
  [+100ms]
  - pc {ch}.5
@end
"""
        parser = MMDParser()
        doc = parser.parse_string(mml)

        alias = doc.aliases["test_multi_timing"]
        assert len(alias.commands) == 5

        # Verify structure: cmd, timing, cmd, timing, cmd
        assert isinstance(alias.commands[0], str)
        assert isinstance(alias.commands[1], Timing)
        assert alias.commands[1].value == (50.0, "ms")
        assert isinstance(alias.commands[2], str)
        assert isinstance(alias.commands[3], Timing)
        assert alias.commands[3].value == (100.0, "ms")
        assert isinstance(alias.commands[4], str)

    def test_timing_in_conditional_branches(self):
        """Test timing statements in @if/@elif/@else branches."""
        mml = """
@alias test_conditional_timing {ch} {mode} "Timing in conditionals"
  @if {mode} == 0
    - cc {ch}.7.0
    [+50ms]
    - cc {ch}.7.64
  @else
    - cc {ch}.7.127
    [+100ms]
    - cc {ch}.7.0
  @end
@end
"""
        parser = MMDParser()
        doc = parser.parse_string(mml)

        # Check alias was parsed
        assert "test_conditional_timing" in doc.aliases
        alias = doc.aliases["test_conditional_timing"]

        # Verify the conditional structure was captured
        assert alias.has_conditionals
        assert len(alias.conditional_branches) > 0

        # Verify timing is captured in the conditional branches
        for branch in alias.conditional_branches:
            timing_found = any(isinstance(cmd, Timing) for cmd in branch.commands)
            assert timing_found, f"No timing found in {branch.branch_type} branch"


class TestAliasTimingResolution:
    """Test alias resolution with timing."""

    def test_resolve_alias_with_timing(self):
        """Test that timing is applied to resolved commands."""
        mml = """
@alias test_timing {ch} {val} "Test timing"
  - cc {ch}.7.0
  [+100ms]
  - cc {ch}.7.{val}
@end
"""
        parser = MMDParser()
        doc = parser.parse_string(mml)
        resolver = AliasResolver(doc.aliases)

        # Resolve alias
        commands = resolver.resolve("test_timing", [1, 100])

        # Should get 2 commands
        assert len(commands) == 2

        # First command has no timing (or inherits from call site)
        assert commands[0].type == "control_change"
        assert commands[0].channel == 1
        assert commands[0].data1 == 7
        assert commands[0].data2 == 0

        # Second command has +100ms timing
        assert commands[1].type == "control_change"
        assert commands[1].channel == 1
        assert commands[1].data1 == 7
        assert commands[1].data2 == 100
        assert commands[1].timing is not None
        assert commands[1].timing.type == "relative"
        assert commands[1].timing.value == (100.0, "ms")

    def test_accumulated_relative_timing(self):
        """Test that multiple relative timings accumulate."""
        mml = """
@alias test_accumulate {ch} "Accumulate timing"
  - cc {ch}.0.1
  [+50ms]
  [+50ms]
  - cc {ch}.0.2
@end
"""
        parser = MMDParser()
        doc = parser.parse_string(mml)
        resolver = AliasResolver(doc.aliases)

        commands = resolver.resolve("test_accumulate", [1])

        # Second command should have accumulated 100ms timing
        assert len(commands) == 2
        assert commands[1].timing.value == (100.0, "ms")

    def test_seconds_timing(self):
        """Test that seconds timing is preserved."""
        mml = """
@alias test_seconds {ch} "Seconds timing"
  - cc {ch}.7.0
  [+1s]
  - cc {ch}.7.127
@end
"""
        parser = MMDParser()
        doc = parser.parse_string(mml)
        resolver = AliasResolver(doc.aliases)

        commands = resolver.resolve("test_seconds", [1])

        # Timing is preserved as seconds (event generator converts later)
        assert commands[1].timing.type == "relative"
        # Value can be either (1.0, 's') or (1000.0, 'ms') depending on resolution
        assert commands[1].timing.value[0] in (1.0, 1000.0)

    def test_timing_reset_between_commands(self):
        """Test that timing resets after each command."""
        mml = """
@alias test_reset {ch} "Reset timing"
  - cc {ch}.0.1
  [+100ms]
  - cc {ch}.0.2
  - cc {ch}.0.3
@end
"""
        parser = MMDParser()
        doc = parser.parse_string(mml)
        resolver = AliasResolver(doc.aliases)

        commands = resolver.resolve("test_reset", [1])

        assert len(commands) == 3
        # Only second command has timing
        assert commands[0].timing is None
        assert commands[1].timing.value == (100.0, "ms")
        assert commands[2].timing is None


class TestAliasTimingErrors:
    """Test error handling for timing in aliases."""

    def test_musical_timing_not_supported(self):
        """Test that musical timing (bars.beats.ticks) raises error in aliases."""
        from midi_markdown.alias.errors import AliasError

        # Musical timing format [bars.beats.ticks] is absolute positioning
        # and should not be allowed in aliases (only relative timing allowed)
        mml = """
@alias test_musical_timing {ch} "Musical timing"
  - cc {ch}.7.0
  [1.1.0]
  - cc {ch}.7.127
@end
"""
        parser = MMDParser()
        doc = parser.parse_string(mml)
        resolver = AliasResolver(doc.aliases)

        # Should raise error when trying to resolve alias with musical timing
        with pytest.raises(AliasError, match="Musical timing.*not supported.*alias"):
            resolver.resolve("test_musical_timing", [1])

    def test_absolute_timing_not_supported(self):
        """Test that absolute timing (mm:ss.mmm) raises error in aliases."""
        from midi_markdown.alias.errors import AliasError

        # Absolute timing format [mm:ss.mmm] is absolute positioning
        # and should not be allowed in aliases (only relative timing allowed)
        mml = """
@alias test_absolute_timing {ch} "Absolute timing"
  - cc {ch}.7.0
  [00:05.000]
  - cc {ch}.7.127
@end
"""
        parser = MMDParser()
        doc = parser.parse_string(mml)
        resolver = AliasResolver(doc.aliases)

        # Should raise error when trying to resolve alias with absolute timing
        with pytest.raises(AliasError, match="Absolute timing.*not supported.*alias"):
            resolver.resolve("test_absolute_timing", [1])
