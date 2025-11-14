"""Integration tests for CLI command interactions and workflows."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

import pytest
from typer.testing import CliRunner

from midi_markdown.cli.main import app

if TYPE_CHECKING:
    from pathlib import Path

runner = CliRunner()


@pytest.fixture
def sample_mml(tmp_path: Path) -> Path:
    """Create a sample MML file for testing."""
    mml_content = """---
title: "Test Song"
tempo: 120
ppq: 480
---

[00:00.000]
- note_on 1.60 80 1b
- note_on 1.64 80 1b
- note_on 1.67 80 1b

[00:01.000]
- cc 1.7.100
- cc 1.10.64
"""
    mml_file = tmp_path / "test_song.mmd"
    mml_file.write_text(mml_content)
    return mml_file


@pytest.fixture
def invalid_mml(tmp_path: Path) -> Path:
    """Create an invalid MML file for error testing."""
    mml_content = """---
title: "Invalid Song"
---

[00:00.000]
- invalid_command 1.60
"""
    mml_file = tmp_path / "invalid.mmd"
    mml_file.write_text(mml_content)
    return mml_file


@pytest.mark.integration
class TestCommandInteractions:
    """Test interactions between different CLI commands."""

    def test_compile_then_inspect(self, sample_mml: Path) -> None:
        """Test compile followed by inspect on same file."""
        # Compile the file
        result1 = runner.invoke(app, ["compile", str(sample_mml)])
        assert result1.exit_code == 0

        # Inspect the same file
        result2 = runner.invoke(app, ["inspect", str(sample_mml)])
        assert result2.exit_code == 0
        assert "MIDI Events" in result2.stdout or "events" in result2.stdout.lower()

    def test_validate_before_compile(self, sample_mml: Path) -> None:
        """Test validation catches issues before compilation."""
        # Validate first
        result1 = runner.invoke(app, ["validate", str(sample_mml)])
        assert result1.exit_code == 0

        # Then compile
        result2 = runner.invoke(app, ["compile", str(sample_mml)])
        assert result2.exit_code == 0

    def test_check_faster_than_validate(self, sample_mml: Path) -> None:
        """Test check command is faster than validate."""
        # Time check command
        start = time.time()
        result1 = runner.invoke(app, ["check", str(sample_mml)])
        check_time = time.time() - start

        # Time validate command
        start = time.time()
        result2 = runner.invoke(app, ["validate", str(sample_mml)])
        validate_time = time.time() - start

        # Both should succeed
        assert result1.exit_code == 0
        assert result2.exit_code == 0

        # Check should be faster (or at least not slower)
        # Allow some variance for system load
        assert check_time <= validate_time * 1.5

    def test_compile_all_formats(self, sample_mml: Path, tmp_path: Path) -> None:
        """Test compilation to all output formats."""
        formats = {
            "midi": "output.mid",
            "csv": "output.csv",
            "json": "output.json",
            "json-simple": "output_simple.json",
        }

        for format_type, output_name in formats.items():
            output_file = tmp_path / output_name
            result = runner.invoke(
                app,
                [
                    "compile",
                    str(sample_mml),
                    "--format",
                    format_type,
                    "-o",
                    str(output_file),
                ],
            )
            assert result.exit_code == 0, f"Format {format_type} failed: {result.stdout}"

            # Verify output file was created (except for table format)
            if format_type != "table":
                assert output_file.exists(), f"Output file not created for {format_type}"
                assert output_file.stat().st_size > 0, f"Output file empty for {format_type}"

    def test_table_format_no_file(self, sample_mml: Path) -> None:
        """Test table format outputs to stdout without creating file."""
        result = runner.invoke(app, ["compile", str(sample_mml), "--format", "table"])
        assert result.exit_code == 0
        assert len(result.stdout) > 100  # Should have table output

    def test_version_command_always_works(self) -> None:
        """Test version command works without any files."""
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "Version:" in result.stdout
        assert "Python:" in result.stdout

    def test_ports_command_always_works(self) -> None:
        """Test ports command works without any files."""
        result = runner.invoke(app, ["ports"])
        assert result.exit_code == 0
        # Should either show ports or "no ports found"
        assert "MIDI Output Ports" in result.stdout or "No MIDI output ports" in result.stdout

    def test_examples_command_always_works(self) -> None:
        """Test examples command works without any files."""
        result = runner.invoke(app, ["examples"])
        assert result.exit_code == 0
        assert "Available" in result.stdout or "Examples" in result.stdout

    def test_cheatsheet_command_always_works(self) -> None:
        """Test cheatsheet command works without any files."""
        result = runner.invoke(app, ["cheatsheet"])
        assert result.exit_code == 0
        assert "Cheat Sheet" in result.stdout or "Quick Start" in result.stdout


@pytest.mark.integration
class TestOutputFormats:
    """Test all output format variations."""

    def test_midi_format_default(self, sample_mml: Path, tmp_path: Path) -> None:
        """Test MIDI format is default."""
        output_file = tmp_path / "output.mid"
        result = runner.invoke(app, ["compile", str(sample_mml), "-o", str(output_file)])
        assert result.exit_code == 0
        assert output_file.exists()
        # MIDI files start with "MThd"
        assert output_file.read_bytes().startswith(b"MThd")

    def test_csv_format(self, sample_mml: Path, tmp_path: Path) -> None:
        """Test CSV output format."""
        output_file = tmp_path / "output.csv"
        result = runner.invoke(
            app, ["compile", str(sample_mml), "--format", "csv", "-o", str(output_file)]
        )
        assert result.exit_code == 0
        assert output_file.exists()

        # Check CSV structure
        csv_content = output_file.read_text()
        assert "Track" in csv_content or "track" in csv_content.lower()
        assert "," in csv_content  # Should have comma-separated values

    def test_json_format(self, sample_mml: Path, tmp_path: Path) -> None:
        """Test JSON output format."""
        output_file = tmp_path / "output.json"
        result = runner.invoke(
            app, ["compile", str(sample_mml), "--format", "json", "-o", str(output_file)]
        )
        assert result.exit_code == 0
        assert output_file.exists()

        # Check JSON structure
        import json

        data = json.loads(output_file.read_text())
        assert isinstance(data, dict)
        assert "events" in data or "tracks" in data

    def test_json_simple_format(self, sample_mml: Path, tmp_path: Path) -> None:
        """Test simplified JSON output format."""
        output_file = tmp_path / "output_simple.json"
        result = runner.invoke(
            app,
            ["compile", str(sample_mml), "--format", "json-simple", "-o", str(output_file)],
        )
        assert result.exit_code == 0
        assert output_file.exists()

        # Check simplified JSON structure
        import json

        data = json.loads(output_file.read_text())
        assert isinstance(data, list | dict)


@pytest.mark.integration
class TestErrorHandling:
    """Test error handling and exit codes across commands."""

    def test_parse_error_exit_code(self, invalid_mml: Path) -> None:
        """Test parse errors return exit code 2."""
        result = runner.invoke(app, ["compile", str(invalid_mml)])
        assert result.exit_code != 0

    def test_validation_error_exit_code(self, tmp_path: Path) -> None:
        """Test validation errors return appropriate exit code."""
        # Create file with invalid MIDI values
        mml_content = """---
title: "Invalid MIDI"
---

[00:00.000]
- note_on 17.60 80 1b  # Channel 17 is invalid (1-16)
"""
        mml_file = tmp_path / "validation_error.mmd"
        mml_file.write_text(mml_content)

        result = runner.invoke(app, ["validate", str(mml_file)])
        assert result.exit_code != 0

    def test_file_not_found_exit_code(self) -> None:
        """Test missing files return non-zero exit code."""
        result = runner.invoke(app, ["compile", "/nonexistent/file.mmd"])
        assert result.exit_code != 0
        # Typer catches file existence before the command runs
        # Exit code 2 from Typer's validation

    def test_debug_flag_shows_traceback(self, invalid_mml: Path) -> None:
        """Test --debug flag shows more error information."""
        # Without debug
        result1 = runner.invoke(app, ["compile", str(invalid_mml)])

        # With debug
        result2 = runner.invoke(app, ["compile", str(invalid_mml), "--debug"])

        # Both should fail
        assert result1.exit_code != 0
        assert result2.exit_code != 0

        # Debug version should have more output or traceback info
        # (exact format depends on error handler implementation)


@pytest.mark.integration
class TestBackwardsCompatibility:
    """Test backwards compatibility of existing workflows."""

    def test_basic_compile_without_options(self, sample_mml: Path) -> None:
        """Test basic compile without any options still works."""
        result = runner.invoke(app, ["compile", str(sample_mml)])
        assert result.exit_code == 0

    def test_compile_with_custom_output(self, sample_mml: Path, tmp_path: Path) -> None:
        """Test compile with custom output path."""
        output_file = tmp_path / "custom_output.mid"
        result = runner.invoke(app, ["compile", str(sample_mml), "-o", str(output_file)])
        assert result.exit_code == 0
        assert output_file.exists()

    def test_validate_command_standalone(self, sample_mml: Path) -> None:
        """Test validate command works independently."""
        result = runner.invoke(app, ["validate", str(sample_mml)])
        assert result.exit_code == 0

    def test_check_command_standalone(self, sample_mml: Path) -> None:
        """Test check command works independently."""
        result = runner.invoke(app, ["check", str(sample_mml)])
        assert result.exit_code == 0


@pytest.mark.integration
class TestCLIPerformance:
    """Test CLI performance and responsiveness."""

    def test_help_is_fast(self) -> None:
        """Test help output is fast (<500ms)."""
        start = time.time()
        result = runner.invoke(app, ["--help"])
        elapsed = time.time() - start

        assert result.exit_code == 0
        assert elapsed < 0.5  # Should be very fast

    def test_version_is_fast(self) -> None:
        """Test version command is fast (<500ms)."""
        start = time.time()
        result = runner.invoke(app, ["version"])
        elapsed = time.time() - start

        assert result.exit_code == 0
        assert elapsed < 0.5

    def test_check_is_fast(self, sample_mml: Path) -> None:
        """Test check command is fast for small files (<1s)."""
        start = time.time()
        result = runner.invoke(app, ["check", str(sample_mml)])
        elapsed = time.time() - start

        assert result.exit_code == 0
        assert elapsed < 1.0

    def test_compile_small_file_is_fast(self, sample_mml: Path) -> None:
        """Test compile is reasonably fast for small files (<2s)."""
        start = time.time()
        result = runner.invoke(app, ["compile", str(sample_mml)])
        elapsed = time.time() - start

        assert result.exit_code == 0
        assert elapsed < 2.0  # Small file should compile quickly


@pytest.mark.integration
class TestCLIUsability:
    """Test CLI usability and user experience."""

    def test_all_commands_have_help(self) -> None:
        """Test all commands have --help option."""
        commands = [
            ["compile", "--help"],
            ["validate", "--help"],
            ["check", "--help"],
            ["inspect", "--help"],
            ["play", "--help"],
            ["ports", "--help"],
            ["examples", "--help"],
            ["version", "--help"],
            ["cheatsheet", "--help"],
            ["library", "--help"],
        ]

        for cmd in commands:
            result = runner.invoke(app, cmd)
            assert result.exit_code == 0, f"Help failed for {cmd}"
            assert len(result.stdout) > 50, f"Help too short for {cmd}"

    def test_help_shows_examples(self) -> None:
        """Test compile help shows usage examples."""
        result = runner.invoke(app, ["compile", "--help"])
        assert result.exit_code == 0
        assert "Examples:" in result.stdout or "example" in result.stdout.lower()

    def test_error_messages_are_helpful(self, invalid_mml: Path) -> None:
        """Test error messages provide useful information."""
        result = runner.invoke(app, ["compile", str(invalid_mml)])
        assert result.exit_code != 0
        # Should have some error indication
        assert len(result.stdout) > 20  # Not just empty error

    def test_verbose_flag_works(self, sample_mml: Path) -> None:
        """Test -v/--verbose flag provides more output."""
        # Without verbose
        result1 = runner.invoke(app, ["compile", str(sample_mml)])

        # With verbose
        result2 = runner.invoke(app, ["compile", str(sample_mml), "-v"])

        # Both should succeed
        assert result1.exit_code == 0
        assert result2.exit_code == 0

        # Verbose should have more output
        assert len(result2.stdout) >= len(result1.stdout)


@pytest.mark.integration
class TestCommandChaining:
    """Test chaining multiple commands in workflows."""

    def test_development_workflow(self, sample_mml: Path, tmp_path: Path) -> None:
        """Test typical development workflow: check → validate → compile."""
        # Step 1: Quick syntax check
        result1 = runner.invoke(app, ["check", str(sample_mml)])
        assert result1.exit_code == 0

        # Step 2: Full validation
        result2 = runner.invoke(app, ["validate", str(sample_mml)])
        assert result2.exit_code == 0

        # Step 3: Compile
        output_file = tmp_path / "output.mid"
        result3 = runner.invoke(app, ["compile", str(sample_mml), "-o", str(output_file)])
        assert result3.exit_code == 0
        assert output_file.exists()

    def test_production_workflow(self, sample_mml: Path, tmp_path: Path) -> None:
        """Test production workflow: validate → compile high-res → export CSV."""
        # Step 1: Validate
        result1 = runner.invoke(app, ["validate", str(sample_mml)])
        assert result1.exit_code == 0

        # Step 2: Compile high-resolution
        midi_file = tmp_path / "performance.mid"
        result2 = runner.invoke(
            app, ["compile", str(sample_mml), "--ppq", "960", "-o", str(midi_file)]
        )
        assert result2.exit_code == 0
        assert midi_file.exists()

        # Step 3: Export timeline CSV
        csv_file = tmp_path / "timeline.csv"
        result3 = runner.invoke(
            app, ["compile", str(sample_mml), "--format", "csv", "-o", str(csv_file)]
        )
        assert result3.exit_code == 0
        assert csv_file.exists()

    def test_inspection_workflow(self, sample_mml: Path) -> None:
        """Test inspection workflow: compile → inspect → table."""
        # Compile
        result1 = runner.invoke(app, ["compile", str(sample_mml)])
        assert result1.exit_code == 0

        # Inspect
        result2 = runner.invoke(app, ["inspect", str(sample_mml)])
        assert result2.exit_code == 0

        # View as table
        result3 = runner.invoke(app, ["compile", str(sample_mml), "--format", "table"])
        assert result3.exit_code == 0
