"""Integration tests for the CLI."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from midi_markdown.cli.main import app

runner = CliRunner()


@pytest.mark.integration
@pytest.mark.cli
class TestCLI:
    """Test suite for CLI commands."""

    def test_version_command(self) -> None:
        """Test that version command works."""
        result = runner.invoke(app, ["version"])

        assert result.exit_code == 0
        assert "MIDI Markup Language" in result.stdout
        assert "0.1.0" in result.stdout

    def test_help_command(self) -> None:
        """Test that help command works."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "MIDI Markup Language" in result.stdout
        assert "compile" in result.stdout
        assert "validate" in result.stdout

    def test_compile_command_basic(self, tmp_path: Path, valid_fixtures_dir: Path) -> None:
        """Test basic compile command."""
        input_file = valid_fixtures_dir / "basic.mmd"
        output_file = tmp_path / "output.mid"

        result = runner.invoke(
            app,
            ["compile", str(input_file), "-o", str(output_file)],
        )

        assert result.exit_code == 0
        assert output_file.exists()
        assert "Compilation successful" in result.stdout

    def test_compile_command_invalid_file(self) -> None:
        """Test compile command with non-existent file."""
        result = runner.invoke(
            app,
            ["compile", "nonexistent.mmd"],
        )

        assert result.exit_code != 0

    def test_validate_command(self, valid_fixtures_dir: Path) -> None:
        """Test validate command."""
        input_file = valid_fixtures_dir / "basic.mmd"

        result = runner.invoke(app, ["validate", str(input_file)])

        assert result.exit_code == 0
        assert "Validation passed" in result.stdout

    def test_validate_command_invalid(self, invalid_fixtures_dir: Path) -> None:
        """Test validate command with invalid file."""
        input_file = invalid_fixtures_dir / "syntax_error.mmd"

        result = runner.invoke(app, ["validate", str(input_file)])

        assert result.exit_code != 0
        assert "error" in result.stdout.lower()

    def test_library_list_command(self) -> None:
        """Test library list command."""
        result = runner.invoke(app, ["library", "list"])

        # Should not crash even though not implemented
        assert "library" in result.stdout.lower()

    def test_compile_with_format_0_option(self, tmp_path: Path, valid_fixtures_dir: Path) -> None:
        """Test compile command with --midi-format 0 (single-track)."""
        import mido

        input_file = valid_fixtures_dir / "basic.mmd"
        output_file = tmp_path / "format0.mid"

        result = runner.invoke(
            app,
            ["compile", str(input_file), "-o", str(output_file), "--midi-format", "0"],
        )

        assert result.exit_code == 0
        assert output_file.exists()

        # Verify Format 0
        mid = mido.MidiFile(str(output_file))
        assert mid.type == 0

    def test_compile_with_format_1_option(self, tmp_path: Path, valid_fixtures_dir: Path) -> None:
        """Test compile command with --midi-format 1 (multi-track) explicit."""
        import mido

        input_file = valid_fixtures_dir / "basic.mmd"
        output_file = tmp_path / "format1.mid"

        result = runner.invoke(
            app,
            ["compile", str(input_file), "-o", str(output_file), "--midi-format", "1"],
        )

        assert result.exit_code == 0
        assert output_file.exists()

        # Verify Format 1
        mid = mido.MidiFile(str(output_file))
        assert mid.type == 1

    def test_compile_with_format_2_option(self, tmp_path: Path, valid_fixtures_dir: Path) -> None:
        """Test compile command with --midi-format 2 (independent sequences)."""
        import mido

        input_file = valid_fixtures_dir / "basic.mmd"
        output_file = tmp_path / "format2.mid"

        result = runner.invoke(
            app,
            ["compile", str(input_file), "-o", str(output_file), "--midi-format", "2"],
        )

        assert result.exit_code == 0
        assert output_file.exists()

        # Verify Format 2
        mid = mido.MidiFile(str(output_file))
        assert mid.type == 2

    def test_compile_format_default_is_1(self, tmp_path: Path, valid_fixtures_dir: Path) -> None:
        """Test compile command without --midi-format defaults to Format 1."""
        import mido

        input_file = valid_fixtures_dir / "basic.mmd"
        output_file = tmp_path / "default.mid"

        result = runner.invoke(
            app,
            ["compile", str(input_file), "-o", str(output_file)],
        )

        assert result.exit_code == 0
        assert output_file.exists()

        # Verify default is Format 1
        mid = mido.MidiFile(str(output_file))
        assert mid.type == 1

    def test_compile_output_format_table(self, valid_fixtures_dir: Path) -> None:
        """Test compile command with --format table."""
        input_file = valid_fixtures_dir / "basic.mmd"

        result = runner.invoke(
            app,
            ["compile", str(input_file), "--format", "table"],
        )

        assert result.exit_code == 0
        assert "Program Summary" in result.stdout
        assert "MIDI Event Timeline" in result.stdout

    def test_compile_output_format_csv(self, valid_fixtures_dir: Path) -> None:
        """Test compile command with --format csv."""
        input_file = valid_fixtures_dir / "basic.mmd"

        result = runner.invoke(
            app,
            ["compile", str(input_file), "--format", "csv"],
        )

        assert result.exit_code == 0
        # Check for CSV headers
        assert "Header" in result.stdout or "Tempo" in result.stdout

    def test_compile_output_format_json(self, valid_fixtures_dir: Path) -> None:
        """Test compile command with --format json."""
        import json

        input_file = valid_fixtures_dir / "basic.mmd"

        result = runner.invoke(
            app,
            ["compile", str(input_file), "--format", "json"],
        )

        assert result.exit_code == 0
        # Verify JSON is valid
        data = json.loads(result.stdout)
        assert "metadata" in data
        assert "events" in data

    def test_compile_output_format_json_simple(self, valid_fixtures_dir: Path) -> None:
        """Test compile command with --format json-simple."""
        import json

        input_file = valid_fixtures_dir / "basic.mmd"

        result = runner.invoke(
            app,
            ["compile", str(input_file), "--format", "json-simple"],
        )

        assert result.exit_code == 0
        # Verify JSON is valid
        data = json.loads(result.stdout)
        assert "metadata" in data
        assert "events" in data

    def test_inspect_command_basic(self, valid_fixtures_dir: Path) -> None:
        """Test inspect command with default table format."""
        input_file = valid_fixtures_dir / "basic.mmd"

        result = runner.invoke(app, ["inspect", str(input_file)])

        assert result.exit_code == 0
        assert "Program Summary" in result.stdout
        assert "MIDI Event Timeline" in result.stdout

    def test_inspect_command_csv(self, valid_fixtures_dir: Path) -> None:
        """Test inspect command with CSV format."""
        input_file = valid_fixtures_dir / "basic.mmd"

        result = runner.invoke(app, ["inspect", str(input_file), "--format", "csv"])

        assert result.exit_code == 0
        # Check for CSV content
        assert "Tempo" in result.stdout or "Header" in result.stdout

    def test_inspect_command_json(self, valid_fixtures_dir: Path) -> None:
        """Test inspect command with JSON format."""
        import json

        input_file = valid_fixtures_dir / "basic.mmd"

        result = runner.invoke(app, ["inspect", str(input_file), "--format", "json"])

        assert result.exit_code == 0
        # Verify JSON is valid
        data = json.loads(result.stdout)
        assert "metadata" in data
        assert "events" in data

    def test_inspect_command_json_simple(self, valid_fixtures_dir: Path) -> None:
        """Test inspect command with simplified JSON format."""
        import json

        input_file = valid_fixtures_dir / "basic.mmd"

        result = runner.invoke(app, ["inspect", str(input_file), "--format", "json-simple"])

        assert result.exit_code == 0
        # Verify JSON is valid
        data = json.loads(result.stdout)
        assert "metadata" in data
        assert "events" in data

    def test_inspect_command_with_limit(self, valid_fixtures_dir: Path) -> None:
        """Test inspect command with --limit option."""
        input_file = valid_fixtures_dir / "basic.mmd"

        result = runner.invoke(app, ["inspect", str(input_file), "--limit", "10"])

        assert result.exit_code == 0
        assert "Program Summary" in result.stdout

    def test_inspect_command_no_stats(self, valid_fixtures_dir: Path) -> None:
        """Test inspect command with --no-stats option."""
        input_file = valid_fixtures_dir / "basic.mmd"

        result = runner.invoke(app, ["inspect", str(input_file), "--no-stats"])

        assert result.exit_code == 0
        assert "Program Summary" not in result.stdout
        assert "MIDI Event Timeline" in result.stdout

    def test_inspect_command_invalid_format(self, valid_fixtures_dir: Path) -> None:
        """Test inspect command with invalid format."""
        input_file = valid_fixtures_dir / "basic.mmd"

        result = runner.invoke(app, ["inspect", str(input_file), "--format", "invalid"])

        assert result.exit_code != 0
        assert "Invalid format" in result.stdout
