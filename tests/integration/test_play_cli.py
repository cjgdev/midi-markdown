"""Integration tests for play CLI command."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock

import pytest
from typer.testing import CliRunner

from midi_markdown.cli.main import app
from midi_markdown.core.ir import EventType, IRProgram, MIDIEvent

if TYPE_CHECKING:
    from pathlib import Path

runner = CliRunner()


def strip_ansi(text: str) -> str:
    """Strip ANSI escape codes from text."""
    ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
    return ansi_escape.sub("", text)


@pytest.fixture
def mock_compile(monkeypatch: Any) -> tuple[MagicMock, MagicMock]:
    """Mock MMDParser and compile_ast_to_ir."""
    import sys

    play_module = sys.modules["midi_markdown.cli.commands.play"]

    mock_ir = IRProgram(
        resolution=480,
        initial_tempo=120,
        events=[
            MIDIEvent(time=0, type=EventType.NOTE_ON, channel=1, data1=60, data2=80),
            MIDIEvent(time=480, type=EventType.NOTE_OFF, channel=1, data1=60, data2=0),
        ],
        metadata={"title": "Test Song"},
    )

    # Mock MMDParser
    mock_doc = MagicMock()
    mock_parser_instance = MagicMock()
    mock_parser_instance.parse_file.return_value = mock_doc
    mock_parser_class = MagicMock(return_value=mock_parser_instance)

    # Mock compile_ast_to_ir
    mock_compile_func = MagicMock(return_value=mock_ir)

    monkeypatch.setattr(play_module, "MMDParser", mock_parser_class)
    monkeypatch.setattr(play_module, "compile_ast_to_ir", mock_compile_func)

    return mock_parser_instance, mock_compile_func


@pytest.fixture
def mock_realtime_player(monkeypatch: Any) -> MagicMock:
    """Mock RealtimePlayer class."""
    import sys

    play_module = sys.modules["midi_markdown.cli.commands.play"]

    mock_player_instance = MagicMock()
    mock_player_instance.get_duration_ms.return_value = 500.0
    mock_player_instance.is_complete.side_effect = [False, False, True]  # Complete after 3 polls

    mock_player_class = MagicMock(return_value=mock_player_instance)
    monkeypatch.setattr(play_module, "RealtimePlayer", mock_player_class)

    return mock_player_instance


@pytest.fixture
def mock_midi_manager(monkeypatch: Any) -> MagicMock:
    """Mock MIDIOutputManager for port listing."""
    import sys

    play_module = sys.modules["midi_markdown.cli.commands.play"]

    mock_manager = MagicMock()
    mock_manager.list_ports.return_value = ["Test Port 1", "Test Port 2", "IAC Driver"]

    mock_class = MagicMock(return_value=mock_manager)
    monkeypatch.setattr(play_module, "MIDIOutputManager", mock_class)

    return mock_manager


@pytest.mark.integration
class TestPlayCLI:
    """Integration tests for play CLI command."""

    def test_play_help(self) -> None:
        """Test play command help text."""
        result = runner.invoke(app, ["play", "--help"])

        assert result.exit_code == 0
        # Strip ANSI codes for reliable string matching
        clean_output = strip_ansi(result.output)
        assert "Play MML file" in clean_output
        assert "--port" in clean_output
        assert "--list-ports" in clean_output

    def test_play_list_ports(self, mock_midi_manager: MagicMock) -> None:
        """Test --list-ports shows available MIDI ports."""
        result = runner.invoke(app, ["play", "--list-ports"])

        if result.exit_code != 0:
            pass
        assert result.exit_code == 0
        assert "Available MIDI output ports" in result.output
        assert "Test Port 1" in result.output
        assert "Test Port 2" in result.output
        assert "IAC Driver" in result.output

    def test_play_list_ports_empty(self, monkeypatch: Any) -> None:
        """Test --list-ports with no ports available."""
        import sys

        play_module = sys.modules["midi_markdown.cli.commands.play"]

        mock_manager = MagicMock()
        mock_manager.list_ports.return_value = []
        mock_class = MagicMock(return_value=mock_manager)
        monkeypatch.setattr(play_module, "MIDIOutputManager", mock_class)

        result = runner.invoke(app, ["play", "--list-ports"])

        assert result.exit_code == 0
        assert "No MIDI ports found" in result.output

    def test_play_missing_port(self, tmp_path: Path) -> None:
        """Test error when --port is not provided."""
        # Create dummy file
        test_file = tmp_path / "test.mmd"
        test_file.write_text("---\ntitle: Test\n---\n")

        result = runner.invoke(app, ["play", str(test_file)])

        assert result.exit_code == 1
        assert "Error: --port is required" in result.output
        assert "--list-ports" in result.output

    def test_play_missing_file(self) -> None:
        """Test error when file doesn't exist."""
        result = runner.invoke(app, ["play", "nonexistent.mmd", "--port", "Test Port"])

        assert result.exit_code == 1
        assert "File not found" in result.output

    def test_play_compilation_error(self, tmp_path: Path, monkeypatch: Any) -> None:
        """Test error handling for compilation failure."""
        import sys

        play_module = sys.modules["midi_markdown.cli.commands.play"]

        # Create file
        test_file = tmp_path / "invalid.mmd"
        test_file.write_text("---\ntitle: Invalid\n---\n")

        # Mock MMDParser to raise exception
        mock_parser_instance = MagicMock()
        mock_parser_instance.parse_file.side_effect = ValueError("Invalid syntax at line 5")
        mock_parser_class = MagicMock(return_value=mock_parser_instance)

        monkeypatch.setattr(play_module, "MMDParser", mock_parser_class)

        result = runner.invoke(app, ["play", str(test_file), "--port", "Test Port"])

        assert result.exit_code == 1
        assert "Compilation error" in result.output
        assert "Invalid syntax" in result.output

    def test_play_midi_error(
        self, tmp_path: Path, mock_compile: tuple[MagicMock, MagicMock], monkeypatch: Any
    ) -> None:
        """Test error handling for MIDI port issues."""
        import sys

        play_module = sys.modules["midi_markdown.cli.commands.play"]

        # Create file
        test_file = tmp_path / "test.mmd"
        test_file.write_text("---\ntitle: Test\n---\n")

        # Mock RealtimePlayer to raise exception
        def mock_player_error(ir_program: Any, port: Any) -> None:
            msg = "Port 'Test Port' not found"
            raise RuntimeError(msg)

        monkeypatch.setattr(play_module, "RealtimePlayer", mock_player_error)

        result = runner.invoke(app, ["play", str(test_file), "--port", "Test Port"])

        assert result.exit_code == 1
        assert "MIDI error" in result.output
        assert "not found" in result.output

    def test_play_success(
        self,
        tmp_path: Path,
        mock_compile: tuple[MagicMock, MagicMock],
        mock_realtime_player: MagicMock,
    ) -> None:
        """Test successful playback with --no-ui (simple mode)."""
        # Create file
        test_file = tmp_path / "test.mmd"
        test_file.write_text("---\ntitle: Test\n---\n")

        mock_parser, mock_compile_func = mock_compile

        result = runner.invoke(app, ["play", str(test_file), "--port", "Test Port", "--no-ui"])

        assert result.exit_code == 0
        assert "Compiling" in result.output
        assert "Opening MIDI port" in result.output
        assert "Duration" in result.output
        assert "Playing" in result.output or "Playback complete" in result.output
        assert "Done" in result.output

        # Verify mocks were called
        mock_parser.parse_file.assert_called_once()
        mock_compile_func.assert_called_once()
        mock_realtime_player.play.assert_called_once()
        mock_realtime_player.is_complete.assert_called()
