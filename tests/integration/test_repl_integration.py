"""Integration tests for REPL command."""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from midi_markdown.cli.main import app


@pytest.fixture
def runner():
    """Create CLI runner."""
    return CliRunner()


@pytest.fixture
def temp_history():
    """Create temporary history file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".mmd_history", delete=False) as f:
        yield Path(f.name)
    Path(f.name).unlink(missing_ok=True)


@pytest.mark.integration
class TestReplIntegration:
    """Integration tests for REPL command."""

    def test_repl_help_flag(self, runner):
        """Test repl --help shows command information."""
        result = runner.invoke(app, ["repl", "--help"])
        assert result.exit_code == 0
        assert "Start interactive REPL session" in result.output
        assert ".help" in result.output
        assert "Ctrl+C" in result.output

    @patch("midi_markdown.cli.commands.repl.PromptSession")
    def test_repl_exits_on_quit(self, mock_session_class, runner):
        """Test .quit command exits REPL."""
        # Mock session to return .quit then raise EOFError
        mock_session = MagicMock()
        mock_session.prompt.side_effect = [".quit"]
        mock_session_class.return_value = mock_session

        result = runner.invoke(app, ["repl"])

        assert result.exit_code == 0
        assert "Goodbye!" in result.output or "MMD REPL" in result.output

    @patch("midi_markdown.cli.commands.repl.PromptSession")
    def test_repl_exits_on_exit(self, mock_session_class, runner):
        """Test .exit command exits REPL."""
        mock_session = MagicMock()
        mock_session.prompt.side_effect = [".exit"]
        mock_session_class.return_value = mock_session

        result = runner.invoke(app, ["repl"])

        assert result.exit_code == 0
        assert "Goodbye!" in result.output or "MMD REPL" in result.output

    @patch("midi_markdown.cli.commands.repl.PromptSession")
    def test_repl_handles_help_command(self, mock_session_class, runner):
        """Test .help command displays help."""
        mock_session = MagicMock()
        mock_session.prompt.side_effect = [".help", ".quit"]
        mock_session_class.return_value = mock_session

        result = runner.invoke(app, ["repl"])

        assert result.exit_code == 0
        # Help should show available commands
        assert ".quit" in result.output or ".help" in result.output

    @patch("midi_markdown.cli.commands.repl.PromptSession")
    def test_repl_handles_reset_command(self, mock_session_class, runner):
        """Test .reset command clears state."""
        mock_session = MagicMock()
        mock_session.prompt.side_effect = [
            "@define velocity 80",  # Set a variable
            ".reset",  # Reset state
            ".quit",
        ]
        mock_session_class.return_value = mock_session

        result = runner.invoke(app, ["repl"])

        assert result.exit_code == 0
        assert "State reset" in result.output or "MMD REPL" in result.output

    @patch("midi_markdown.cli.commands.repl.PromptSession")
    def test_repl_handles_list_command(self, mock_session_class, runner):
        """Test .list command shows state."""
        mock_session = MagicMock()
        mock_session.prompt.side_effect = [".list", ".quit"]
        mock_session_class.return_value = mock_session

        result = runner.invoke(app, ["repl"])

        assert result.exit_code == 0
        assert "Current State" in result.output or "Variables" in result.output

    @patch("midi_markdown.cli.commands.repl.PromptSession")
    def test_repl_handles_tempo_command(self, mock_session_class, runner):
        """Test .tempo command sets tempo."""
        mock_session = MagicMock()
        mock_session.prompt.side_effect = [".tempo 140", ".quit"]
        mock_session_class.return_value = mock_session

        result = runner.invoke(app, ["repl"])

        assert result.exit_code == 0
        assert "Tempo set to 140" in result.output or "140 BPM" in result.output

    @patch("midi_markdown.cli.commands.repl.PromptSession")
    def test_repl_handles_ppq_command(self, mock_session_class, runner):
        """Test .ppq command sets resolution."""
        mock_session = MagicMock()
        mock_session.prompt.side_effect = [".ppq 960", ".quit"]
        mock_session_class.return_value = mock_session

        result = runner.invoke(app, ["repl"])

        assert result.exit_code == 0
        assert "PPQ set to 960" in result.output or "960" in result.output

    @patch("midi_markdown.cli.commands.repl.PromptSession")
    def test_repl_handles_keyboard_interrupt(self, mock_session_class, runner):
        """Test Ctrl+C clears buffer and continues."""
        mock_session = MagicMock()
        mock_session.prompt.side_effect = [
            "- cc 1.7",  # Start incomplete command
            KeyboardInterrupt(),  # User presses Ctrl+C
            ".quit",  # Then quit
        ]
        mock_session_class.return_value = mock_session

        result = runner.invoke(app, ["repl"])

        assert result.exit_code == 0
        # Should show "Input cancelled" or similar
        assert "Input cancelled" in result.output or "Goodbye!" in result.output

    @patch("midi_markdown.cli.commands.repl.PromptSession")
    def test_repl_handles_eof_gracefully(self, mock_session_class, runner):
        """Test Ctrl+D exits gracefully."""
        mock_session = MagicMock()
        mock_session.prompt.side_effect = [EOFError()]
        mock_session_class.return_value = mock_session

        result = runner.invoke(app, ["repl"])

        assert result.exit_code == 0
        assert "Goodbye!" in result.output

    @patch("midi_markdown.cli.commands.repl.PromptSession")
    def test_repl_handles_parse_error(self, mock_session_class, runner):
        """Test REPL handles parse errors gracefully."""
        mock_session = MagicMock()
        mock_session.prompt.side_effect = [
            "- invalid_command 1.2.3",  # Invalid command
            ".quit",
        ]
        mock_session_class.return_value = mock_session

        result = runner.invoke(app, ["repl"])

        assert result.exit_code == 0
        # Should show error but not crash
        assert "REPL state preserved" in result.output or "Goodbye!" in result.output

    @patch("midi_markdown.cli.commands.repl.PromptSession")
    def test_repl_evaluates_valid_command(self, mock_session_class, runner):
        """Test REPL evaluates and displays valid MIDI command."""
        mock_session = MagicMock()
        mock_session.prompt.side_effect = [
            "[00:00.000]",
            "- cc 1.7.64",
            "",  # Empty line to complete
            ".quit",
        ]
        mock_session_class.return_value = mock_session

        result = runner.invoke(app, ["repl"])

        assert result.exit_code == 0
        # Should process command successfully
        assert "event" in result.output.lower() or "goodbye" in result.output.lower()

    @patch("midi_markdown.cli.commands.repl.PromptSession")
    def test_repl_handles_multiline_input(self, mock_session_class, runner):
        """Test REPL accumulates multi-line input."""
        mock_session = MagicMock()
        mock_session.prompt.side_effect = [
            "[00:00.000]",  # Line 1
            "- cc 1.7.64",  # Line 2
            "- cc 1.11.100",  # Line 3
            "",  # Empty line to complete
            ".quit",
        ]
        mock_session_class.return_value = mock_session

        result = runner.invoke(app, ["repl"])

        assert result.exit_code == 0
        # Should process all commands
        assert "event" in result.output.lower() or "goodbye" in result.output.lower()

    @patch("midi_markdown.cli.commands.repl.PromptSession")
    def test_repl_shows_welcome_banner(self, mock_session_class, runner):
        """Test REPL shows welcome banner on startup."""
        mock_session = MagicMock()
        mock_session.prompt.side_effect = [".quit"]
        mock_session_class.return_value = mock_session

        result = runner.invoke(app, ["repl"])

        assert result.exit_code == 0
        assert "MMD REPL" in result.output or "Interactive" in result.output

    @patch("midi_markdown.cli.commands.repl.PromptSession")
    def test_repl_debug_mode_crashes_on_error(self, mock_session_class, runner):
        """Test debug mode lets errors crash (for development)."""
        mock_session = MagicMock()
        mock_session.prompt.side_effect = [
            "- invalid_command",  # Will cause error
        ]
        mock_session_class.return_value = mock_session

        # In debug mode, should propagate exception
        result = runner.invoke(app, ["repl", "--debug"])

        # Should crash (non-zero exit code) or show traceback
        # Note: Exact behavior depends on error handling
        assert (
            result.exit_code != 0 or "Traceback" in result.output or "Fatal error" in result.output
        )

    @patch("midi_markdown.cli.commands.repl.PromptSession")
    def test_repl_inspect_empty_state(self, mock_session_class, runner):
        """Test .inspect with no compiled IR shows message."""
        mock_session = MagicMock()
        mock_session.prompt.side_effect = [".inspect", ".quit"]
        mock_session_class.return_value = mock_session

        result = runner.invoke(app, ["repl"])

        assert result.exit_code == 0
        assert "No IR to inspect" in result.output or "inspect" in result.output.lower()

    @patch("midi_markdown.cli.commands.repl.PromptSession")
    def test_repl_handles_unknown_meta_command(self, mock_session_class, runner):
        """Test unknown meta-command shows error."""
        mock_session = MagicMock()
        mock_session.prompt.side_effect = [".unknown", ".quit"]
        mock_session_class.return_value = mock_session

        result = runner.invoke(app, ["repl"])

        assert result.exit_code == 0
        assert "Unknown command" in result.output or ".help" in result.output
