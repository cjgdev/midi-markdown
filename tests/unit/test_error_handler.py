"""Unit tests for CLI error handler."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from rich.console import Console

from midi_markdown.alias.errors import AliasError
from midi_markdown.cli.error_handler import ErrorContext, cli_error_handler
from midi_markdown.expansion.errors import ExpansionError
from midi_markdown.utils.validation.errors import ValidationError


def test_error_context_creation():
    """Test ErrorContext dataclass creation with all fields."""
    ctx = ErrorContext(
        mode="compile",
        debug=True,
        source_file=Path("test.mmd"),
        no_color=True,
        no_emoji=True,
        player=None,
        console=None,
    )

    assert ctx.mode == "compile"
    assert ctx.debug is True
    assert ctx.source_file == Path("test.mmd")
    assert ctx.no_color is True
    assert ctx.no_emoji is True
    assert ctx.player is None
    assert ctx.console is None


def test_error_context_defaults():
    """Test ErrorContext with default values."""
    ctx = ErrorContext(mode="validate")

    assert ctx.mode == "validate"
    assert ctx.debug is False
    assert ctx.source_file is None
    assert ctx.no_color is False
    assert ctx.no_emoji is False
    assert ctx.player is None
    assert ctx.console is None


def test_successful_execution():
    """Test that successful code execution doesn't raise."""
    console = Console()
    ctx = ErrorContext(mode="compile", console=console)

    with cli_error_handler(ctx):
        # No exception - should complete successfully
        pass


def test_keyboard_interrupt_exit_code():
    """Test that KeyboardInterrupt exits with code 130."""
    console = Console()
    ctx = ErrorContext(mode="compile", console=console)

    with pytest.raises(SystemExit) as exc_info, cli_error_handler(ctx):
        raise KeyboardInterrupt

    assert exc_info.value.code == 130


def test_validation_error_exit_code():
    """Test that validation errors exit with code 3."""
    console = Console()
    ctx = ErrorContext(mode="validate", source_file=Path("test.mmd"), console=console)

    with patch("midi_markdown.cli.errors.show_validation_error"):
        with pytest.raises(SystemExit) as exc_info, cli_error_handler(ctx):
            msg = "Invalid MIDI value"
            raise ValidationError(msg)

        assert exc_info.value.code == 3


def test_expansion_error_exit_code():
    """Test that expansion errors exit with code 1."""
    console = Console()
    ctx = ErrorContext(mode="compile", console=console)

    with patch("midi_markdown.cli.errors.show_expansion_error"):
        with pytest.raises(SystemExit) as exc_info, cli_error_handler(ctx):
            msg = "Variable not defined"
            raise ExpansionError(msg)

        assert exc_info.value.code == 1


def test_alias_error_exit_code():
    """Test that alias errors exit with code 1."""
    console = Console()
    ctx = ErrorContext(mode="compile", console=console)

    with patch("midi_markdown.cli.errors.show_alias_error"):
        with pytest.raises(SystemExit) as exc_info, cli_error_handler(ctx):
            msg = "Alias not found"
            raise AliasError(msg)

        assert exc_info.value.code == 1


def test_file_not_found_exit_code():
    """Test that file not found errors exit with code 4."""
    console = Console()
    ctx = ErrorContext(mode="compile", console=console)

    with patch("midi_markdown.cli.errors.show_file_not_found_error"):
        with pytest.raises(SystemExit) as exc_info, cli_error_handler(ctx):
            msg = "test.mmd"
            raise FileNotFoundError(msg)

        assert exc_info.value.code == 4


def test_runtime_error_exit_code():
    """Test that runtime errors exit with code 5."""
    console = Console()
    ctx = ErrorContext(mode="play", console=console)

    with patch("midi_markdown.cli.errors.show_runtime_error"):
        with pytest.raises(SystemExit) as exc_info, cli_error_handler(ctx):
            msg = "MIDI port not found"
            raise RuntimeError(msg)

        assert exc_info.value.code == 5


def test_generic_exception_exit_code():
    """Test that unexpected exceptions exit with code 1."""
    console = Console()
    ctx = ErrorContext(mode="compile", console=console)

    with pytest.raises(SystemExit) as exc_info, cli_error_handler(ctx):
        msg = "Unexpected error"
        raise ValueError(msg)

    assert exc_info.value.code == 1


def test_debug_mode_shows_traceback():
    """Test that debug mode enables traceback display."""
    console = Mock(spec=Console)
    ctx = ErrorContext(mode="compile", debug=True, console=console)

    with pytest.raises(SystemExit), cli_error_handler(ctx):
        msg = "Test error"
        raise ValueError(msg)

    # Verify console.print_exception was called
    console.print_exception.assert_called_once()


def test_no_debug_shows_hint():
    """Test that without debug mode, hint is shown instead of traceback."""
    console = Mock(spec=Console)
    ctx = ErrorContext(mode="compile", debug=False, console=console)

    with pytest.raises(SystemExit), cli_error_handler(ctx):
        msg = "Test error"
        raise ValueError(msg)

    # Verify hint message was printed
    printed_messages = [call[0][0] for call in console.print.call_args_list]
    assert any("--debug" in msg for msg in printed_messages)


def test_play_mode_cleanup():
    """Test that play mode calls player.stop() on error."""
    console = Console()
    player = Mock()
    player.stop = Mock()
    ctx = ErrorContext(mode="play", player=player, console=console)

    with pytest.raises(SystemExit), cli_error_handler(ctx):
        raise KeyboardInterrupt

    # Verify player.stop() was called
    player.stop.assert_called_once()


def test_play_mode_cleanup_handles_exception():
    """Test that player.stop() exceptions are ignored during cleanup."""
    console = Console()
    player = Mock()
    player.stop = Mock(side_effect=Exception("Cleanup error"))
    ctx = ErrorContext(mode="play", player=player, console=console)

    # Should not raise cleanup exception, only exit
    with pytest.raises(SystemExit) as exc_info, cli_error_handler(ctx):
        raise KeyboardInterrupt

    assert exc_info.value.code == 130
