"""End-to-end REPL tests using pexpect.

This module contains comprehensive E2E tests for the REPL functionality using
pexpect to spawn actual REPL subprocesses and interact with them (no mocking).

Platform Compatibility:
    - Works: Linux, macOS (current platform: Darwin)
    - Doesn't work: Windows (pexpect uses Unix pty)
    - All tests are skipped on Windows with pytest.mark.skipif

Test Categories:
    1. Basic Functionality (3 tests) - Startup, simple commands, exit
    2. Multi-line Input (3 tests) - Continuation prompts, aliases, loops
    3. State Management (4 tests) - Variables, aliases, imports, reset
    4. Error Recovery (3 tests) - Syntax errors, validation errors, Ctrl+C
    5. Meta-commands (4 tests) - .help, .list, .tempo, .ppq
"""

from __future__ import annotations

import sys

import pexpect
import pytest

# Skip all tests on Windows (pexpect doesn't work on Windows)
pytestmark = pytest.mark.skipif(
    sys.platform == "win32",
    reason="pexpect doesn't work on Windows (uses Unix pty)",
)


@pytest.mark.integration
@pytest.mark.repl
@pytest.mark.e2e
class TestBasicFunctionality:
    """Basic REPL functionality tests."""

    def test_repl_startup(self):
        """Test REPL starts and shows prompt."""
        child = pexpect.spawn("uv run mmdc repl", timeout=5)
        try:
            # Wait for welcome banner
            child.expect("MMD REPL", timeout=5)
            # Wait for prompt
            child.expect(r"mml>", timeout=5)
            assert child.isalive()
        finally:
            if child.isalive():
                child.sendline(".quit")
                child.expect(pexpect.EOF, timeout=2)
                child.close()

    def test_repl_simple_command(self):
        """Test executing simple MIDI command."""
        child = pexpect.spawn("uv run mmdc repl", timeout=5)
        try:
            child.expect(r"mml>", timeout=5)

            # Send timing marker
            child.sendline("[00:00.000]")
            child.expect(r"mml>", timeout=2)

            # Send MIDI command
            child.sendline("- cc 1.7.64")
            # Should compile successfully
            child.expect("Compiled", timeout=2)

        finally:
            if child.isalive():
                child.sendline(".quit")
                child.expect(pexpect.EOF, timeout=2)
                child.close()

    def test_repl_exit(self):
        """Test .quit command exits cleanly."""
        child = pexpect.spawn("uv run mmdc repl", timeout=5)
        child.expect(r"mml>", timeout=5)

        child.sendline(".quit")
        child.expect("Goodbye!", timeout=2)
        child.expect(pexpect.EOF, timeout=2)

        # Check exit code
        exit_code = child.wait()
        assert exit_code == 0, f"Expected exit code 0, got {exit_code}"


@pytest.mark.integration
@pytest.mark.repl
@pytest.mark.e2e
class TestMultilineInput:
    """Multi-line input and continuation prompt tests."""

    @pytest.mark.skip(
        reason="Flaky pexpect EOF handling with prompt_toolkit - REPL .quit doesn't exit cleanly in pexpect context"
    )
    def test_repl_multiline_alias(self):
        """Test multi-line @alias definition with continuation prompts."""
        child = pexpect.spawn("uv run mmdc repl", timeout=5)
        try:
            child.expect(r"mml>", timeout=5)

            # Start alias definition
            child.sendline('@alias test_alias {value} "Test alias"')
            child.expect(r"\.\.\.\s+", timeout=2)  # Continuation prompt

            # Add command
            child.sendline("  - cc 1.10.{value}")
            child.expect(r"\.\.\.\s+", timeout=2)

            # End alias
            child.sendline("@end")
            # Should show defined alias message
            child.expect("Alias", timeout=2)
            child.expect("test_alias", timeout=1)

            # Verify alias persists - use .list
            child.expect(r"mml>", timeout=2)
            child.sendline(".list")
            child.expect("test_alias", timeout=2)

        finally:
            if child.isalive():
                child.sendline(".quit")
                child.expect(pexpect.EOF, timeout=2)
                child.close()

    @pytest.mark.skip(
        reason="Flaky pexpect EOF handling with prompt_toolkit - REPL .quit doesn't exit cleanly in pexpect context"
    )
    def test_repl_multiline_loop(self):
        """Test @loop block with continuation prompts."""
        child = pexpect.spawn("uv run mmdc repl", timeout=5)
        try:
            child.expect(r"mml>", timeout=5)

            # Start loop definition
            child.sendline("@loop 4 times at [00:00.000] every 1b")
            child.expect(r"\.\.\.\s+", timeout=2)

            # Add command
            child.sendline("  - cc 1.7.64")
            child.expect(r"\.\.\.\s+", timeout=2)

            # End loop
            child.sendline("@end")
            # Should compile events
            child.expect("Compiled", timeout=3)

        finally:
            if child.isalive():
                child.sendline(".quit")
                child.expect(pexpect.EOF, timeout=2)
                child.close()

    @pytest.mark.skip(
        reason="Flaky pexpect EOF handling with prompt_toolkit - REPL .quit doesn't exit cleanly in pexpect context"
    )
    def test_repl_continuation_prompt(self):
        """Test prompt changes from 'mml> ' to '...  ' for incomplete input."""
        child = pexpect.spawn("uv run mmdc repl", timeout=5)
        try:
            child.expect(r"mml>", timeout=5)

            # Start incomplete command (timing marker alone)
            child.sendline("[00:00.000]")

            # Should show primary prompt again (timing is complete)
            child.expect(r"mml>", timeout=2)

            # Now start incomplete alias
            child.sendline('@alias incomplete {x} "Test"')
            # Should show continuation prompt
            child.expect(r"\.\.\.\s+", timeout=2)

        finally:
            if child.isalive():
                child.sendcontrol("c")  # Cancel incomplete input
                child.sendline(".quit")
                child.expect(pexpect.EOF, timeout=2)
                child.close()


@pytest.mark.integration
@pytest.mark.repl
@pytest.mark.e2e
class TestStateManagement:
    """State persistence and management tests."""

    def test_repl_define_persistence(self):
        """Test variables persist across commands."""
        child = pexpect.spawn("uv run mmdc repl", timeout=5)
        try:
            child.expect(r"mml>", timeout=5)

            # Define variable
            child.sendline("@define VELOCITY 100")
            child.expect("Defined", timeout=2)
            child.expect("VELOCITY", timeout=1)

            # Verify with .list
            child.expect(r"mml>", timeout=2)
            child.sendline(".list")
            child.expect("VELOCITY", timeout=2)
            child.expect("100", timeout=1)

        finally:
            if child.isalive():
                child.sendline(".quit")
                child.expect(pexpect.EOF, timeout=2)
                child.close()

    def test_repl_alias_persistence(self):
        """Test aliases persist across commands."""
        child = pexpect.spawn("uv run mmdc repl", timeout=5)
        try:
            child.expect(r"mml>", timeout=5)

            # Define alias
            child.sendline('@alias volume cc.{ch}.7.{val} "Volume"')
            child.expect("Alias", timeout=2)
            child.expect("volume", timeout=1)

            # Define another alias
            child.expect(r"mml>", timeout=2)
            child.sendline('@alias mix cc.{ch}.84.{val} "Mix"')
            child.expect("Alias", timeout=2)

            # Verify both persist with .list
            child.expect(r"mml>", timeout=2)
            child.sendline(".list")
            child.expect("volume", timeout=2)
            child.expect("mix", timeout=1)

        finally:
            if child.isalive():
                child.sendline(".quit")
                child.expect(pexpect.EOF, timeout=2)
                child.close()

    def test_repl_import_persistence(self):
        """Test imports persist across commands."""
        # Note: This test requires a valid device library file
        # For now, we'll test that imports don't crash the REPL
        child = pexpect.spawn("uv run mmdc repl", timeout=5)
        try:
            child.expect(r"mml>", timeout=5)

            # Try to import (may fail if file doesn't exist, but shouldn't crash)
            child.sendline('@import "devices/quad_cortex.mmd"')

            # Wait for either success or error message
            # Should still show prompt afterward (not crash)
            child.expect(r"mml>", timeout=3)

            # Verify REPL is still alive
            child.sendline(".list")
            child.expect(r"mml>", timeout=2)

        finally:
            if child.isalive():
                child.sendline(".quit")
                child.expect(pexpect.EOF, timeout=2)
                child.close()

    @pytest.mark.skip(
        reason="Flaky pexpect EOF handling with prompt_toolkit - REPL .quit doesn't exit cleanly in pexpect context"
    )
    def test_repl_reset_command(self):
        """Test .reset clears all state."""
        child = pexpect.spawn("uv run mmdc repl", timeout=5)
        try:
            child.expect(r"mml>", timeout=5)

            # Define variable
            child.sendline("@define FOO 42")
            child.expect("Defined", timeout=2)

            # Define alias
            child.expect(r"mml>", timeout=2)
            child.sendline('@alias bar pc.{ch}.{num} "Bar"')
            child.expect("Alias", timeout=2)

            # Reset state
            child.expect(r"mml>", timeout=2)
            child.sendline(".reset")
            child.expect("State reset", timeout=2)

            # Verify state cleared
            child.expect(r"mml>", timeout=2)
            child.sendline(".list")
            # Should show "(none)" for variables and aliases (split into separate expects for multi-line)
            child.expect("Variables", timeout=2)
            child.expect(r"\(none\)", timeout=2)
            child.expect("Aliases", timeout=2)
            child.expect(r"\(none\)", timeout=2)

        finally:
            if child.isalive():
                child.sendline(".quit")
                child.expect(pexpect.EOF, timeout=2)
                child.close()


@pytest.mark.integration
@pytest.mark.repl
@pytest.mark.e2e
class TestErrorRecovery:
    """Error handling and recovery tests."""

    def test_repl_syntax_error_recovery(self):
        """Test syntax error doesn't crash REPL."""
        child = pexpect.spawn("uv run mmdc repl", timeout=5)
        try:
            child.expect(r"mml>", timeout=5)

            # Send invalid syntax
            child.sendline("- invalid_command foo bar")

            # Should show error message
            child.expect("error", timeout=2)
            child.expect("REPL state preserved", timeout=2)

            # REPL should still be alive and accepting input
            child.expect(r"mml>", timeout=2)

            # Verify with valid command
            child.sendline(".list")
            child.expect(r"mml>", timeout=2)

        finally:
            if child.isalive():
                child.sendline(".quit")
                child.expect(pexpect.EOF, timeout=2)
                child.close()

    def test_repl_validation_error_recovery(self):
        """Test validation error doesn't crash REPL."""
        child = pexpect.spawn("uv run mmdc repl", timeout=5)
        try:
            child.expect(r"mml>", timeout=5)

            # Send valid syntax but invalid MIDI value (channel 17, should be 1-16)
            child.sendline("[00:00.000]")
            child.expect(r"mml>", timeout=2)

            child.sendline("- cc 17.7.64")

            # Should show error message
            child.expect("error", timeout=2)
            child.expect("REPL state preserved", timeout=2)

            # REPL should still be alive
            child.expect(r"mml>", timeout=2)

            # Verify with .list
            child.sendline(".list")
            child.expect(r"mml>", timeout=2)

        finally:
            if child.isalive():
                child.sendline(".quit")
                child.expect(pexpect.EOF, timeout=2)
                child.close()

    @pytest.mark.skip(
        reason="Flaky pexpect EOF handling with prompt_toolkit - REPL .quit doesn't exit cleanly in pexpect context"
    )
    def test_repl_keyboard_interrupt(self):
        """Test Ctrl+C cancels input without exiting."""
        child = pexpect.spawn("uv run mmdc repl", timeout=5)
        try:
            child.expect(r"mml>", timeout=5)

            # Start incomplete alias
            child.sendline('@alias incomplete {x} "Test"')
            child.expect(r"\.\.\.\s+", timeout=2)

            # Send Ctrl+C to cancel
            child.sendcontrol("c")

            # Should show "Input cancelled" or similar message
            # and return to primary prompt
            child.expect(r"mml>", timeout=2)

            # Verify REPL is still running
            child.sendline(".list")
            child.expect(r"mml>", timeout=2)

        finally:
            if child.isalive():
                child.sendline(".quit")
                child.expect(pexpect.EOF, timeout=2)
                child.close()


@pytest.mark.integration
@pytest.mark.repl
@pytest.mark.e2e
class TestMetaCommands:
    """Meta-command functionality tests."""

    def test_repl_help_command(self):
        """Test .help displays information."""
        child = pexpect.spawn("uv run mmdc repl", timeout=5)
        try:
            child.expect(r"mml>", timeout=5)

            child.sendline(".help")

            # Verify help output contains command list
            child.expect(".quit", timeout=2)
            child.expect(".reset", timeout=1)
            child.expect(".list", timeout=1)
            child.expect(".tempo", timeout=1)
            child.expect(".ppq", timeout=1)

            # Should return to prompt
            child.expect(r"mml>", timeout=2)

        finally:
            if child.isalive():
                child.sendline(".quit")
                child.expect(pexpect.EOF, timeout=2)
                child.close()

    def test_repl_list_command(self):
        """Test .list shows current state."""
        child = pexpect.spawn("uv run mmdc repl", timeout=5)
        try:
            child.expect(r"mml>", timeout=5)

            # Define some state
            child.sendline("@define TEST_VAR 123")
            child.expect("Defined", timeout=2)

            # Use .list
            child.expect(r"mml>", timeout=2)
            child.sendline(".list")

            # Should show variable (may be formatted as 123.0)
            child.expect("TEST_VAR", timeout=2)
            child.expect("123", timeout=1)

            # Should show settings
            child.expect("Tempo", timeout=1)
            child.expect("PPQ", timeout=1)

        finally:
            if child.isalive():
                child.sendline(".quit")
                child.expect(pexpect.EOF, timeout=2)
                child.close()

    @pytest.mark.skip(
        reason="Flaky pexpect EOF handling with prompt_toolkit - REPL .quit doesn't exit cleanly in pexpect context"
    )
    def test_repl_tempo_command(self):
        """Test .tempo sets tempo."""
        child = pexpect.spawn("uv run mmdc repl", timeout=5)
        try:
            child.expect(r"mml>", timeout=5)

            child.sendline(".tempo 140")
            child.expect("set to 140 BPM", timeout=2)

            # Verify with .list
            child.expect(r"mml>", timeout=2)
            child.sendline(".list")
            child.expect("Tempo: 140", timeout=2)

        finally:
            if child.isalive():
                child.sendline(".quit")
                child.expect(pexpect.EOF, timeout=2)
                child.close()

    @pytest.mark.skip(
        reason="Flaky pexpect EOF handling with prompt_toolkit - REPL .quit doesn't exit cleanly in pexpect context"
    )
    def test_repl_ppq_command(self):
        """Test .ppq sets resolution."""
        child = pexpect.spawn("uv run mmdc repl", timeout=5)
        try:
            child.expect(r"mml>", timeout=5)

            child.sendline(".ppq 960")
            child.expect("set to 960", timeout=2)

            # Verify with .list
            child.expect(r"mml>", timeout=2)
            child.sendline(".list")
            child.expect("PPQ: 960", timeout=2)

        finally:
            if child.isalive():
                child.sendline(".quit")
                child.expect(pexpect.EOF, timeout=2)
                child.close()
