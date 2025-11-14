"""Integration tests for CLI helper commands (discoverability and workflows)."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from midi_markdown.cli.main import app

runner = CliRunner()


@pytest.mark.integration
class TestCLIDiscoverability:
    """Tests for CLI command discoverability and help system."""

    def test_main_help_shows_all_commands(self) -> None:
        """Test that main help shows all available commands."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        # Core commands
        assert "compile" in result.stdout
        assert "validate" in result.stdout
        assert "check" in result.stdout
        assert "inspect" in result.stdout
        assert "play" in result.stdout
        # Helper commands
        assert "ports" in result.stdout
        assert "examples" in result.stdout
        assert "version" in result.stdout
        assert "library" in result.stdout
        assert "repl" in result.stdout

    def test_ports_help(self) -> None:
        """Test ports command help text."""
        result = runner.invoke(app, ["ports", "--help"])

        assert result.exit_code == 0
        assert "List available MIDI" in result.stdout
        assert "ports" in result.stdout.lower()

    def test_examples_help(self) -> None:
        """Test examples command help text."""
        result = runner.invoke(app, ["examples", "--help"])

        assert result.exit_code == 0
        assert "example" in result.stdout.lower()
        assert "MML" in result.stdout

    def test_version_help(self) -> None:
        """Test version command help text."""
        result = runner.invoke(app, ["version", "--help"])

        assert result.exit_code == 0
        assert "version" in result.stdout.lower() or "system" in result.stdout.lower()

    def test_library_help(self) -> None:
        """Test library subcommand help text."""
        result = runner.invoke(app, ["library", "--help"])

        assert result.exit_code == 0
        assert "library" in result.stdout.lower() or "device" in result.stdout.lower()
        assert "list" in result.stdout
        assert "info" in result.stdout
        assert "validate" in result.stdout


@pytest.mark.integration
class TestLearningWorkflow:
    """Tests for learning workflow - how new users discover MML."""

    def test_new_user_discovers_examples(self) -> None:
        """Test that new users can discover and view examples."""
        # Step 1: User runs midimarkup without args and sees examples command
        result = runner.invoke(app, [])
        assert "examples" in result.stdout

        # Step 2: User runs examples to see list
        result = runner.invoke(app, ["examples"])
        assert result.exit_code == 0
        assert "hello" in result.stdout
        assert "timing" in result.stdout

        # Step 3: User views hello example
        result = runner.invoke(app, ["examples", "hello"])
        assert result.exit_code == 0
        assert "note_on" in result.stdout
        assert "Middle C" in result.stdout

    def test_new_user_discovers_device_libraries(self) -> None:
        """Test that new users can discover device libraries."""
        # Step 1: User runs library list
        result = runner.invoke(app, ["library", "list"])
        assert result.exit_code == 0

        # Should show libraries or "not found" message
        assert "Device Libraries" in result.stdout or "not found" in result.stdout.lower()

    def test_new_user_checks_midi_ports(self) -> None:
        """Test that new users can check MIDI ports before playing."""
        # User runs ports command to see available ports
        result = runner.invoke(app, ["ports"])
        assert result.exit_code == 0

        # Should show ports table or setup instructions
        assert "MIDI Output Ports" in result.stdout or "No MIDI output ports found" in result.stdout


@pytest.mark.integration
class TestDeviceLibraryWorkflow:
    """Tests for device library exploration workflow."""

    def test_explore_device_libraries(self) -> None:
        """Test complete workflow of exploring device libraries."""
        devices_dir = Path(__file__).parent.parent.parent / "devices"
        if not devices_dir.exists() or not list(devices_dir.glob("*.mmd")):
            pytest.skip("No device libraries found")

        # Step 1: List all libraries
        result = runner.invoke(app, ["library", "list"])
        assert result.exit_code == 0
        assert "Device Libraries" in result.stdout

        # Step 2: Get info about a specific library (use first one found)
        libraries = sorted(
            [f.stem for f in devices_dir.glob("*.mmd") if not f.stem.startswith("README")]
        )
        if not libraries:
            pytest.skip("No device libraries found")

        lib_name = libraries[0]
        result = runner.invoke(app, ["library", "info", lib_name])
        assert result.exit_code == 0
        assert f"Library: {lib_name}" in result.stdout
        assert "Aliases:" in result.stdout

        # Step 3: Validate the library
        lib_file = devices_dir / f"{lib_name}.mmd"
        result = runner.invoke(app, ["library", "validate", str(lib_file)])
        assert result.exit_code in {0, 1}  # May fail validation
        assert "Validation" in result.stdout


@pytest.mark.integration
class TestVersionInformationWorkflow:
    """Tests for version and system information workflow."""

    def test_check_version_and_dependencies(self) -> None:
        """Test that users can check version and dependencies."""
        result = runner.invoke(app, ["version"])

        assert result.exit_code == 0
        assert "Version:" in result.stdout
        assert "Python:" in result.stdout
        assert "Dependencies:" in result.stdout
        # Check for key dependencies
        assert "mido" in result.stdout
        assert "lark" in result.stdout
        assert "rich" in result.stdout

    def test_quick_version_flag(self) -> None:
        """Test --version/-V flag for quick version check."""
        result = runner.invoke(app, ["--version"])

        assert result.exit_code == 0
        assert "MIDI" in result.stdout  # Accept "MIDI Markdown" or "MIDI Markup"
        assert "0.1.0" in result.stdout


@pytest.mark.integration
class TestCLIConsistency:
    """Tests for CLI consistency and conventions."""

    def test_all_commands_have_help(self) -> None:
        """Test that all commands have --help option."""
        commands = [
            ["compile"],
            ["validate"],
            ["check"],
            ["inspect"],
            ["play"],
            ["ports"],
            ["examples"],
            ["version"],
            ["library"],
            ["repl"],
        ]

        for command in commands:
            result = runner.invoke(app, [*command, "--help"])
            assert result.exit_code == 0, f"Command {' '.join(command)} --help failed"
            assert len(result.stdout) > 50, f"Command {' '.join(command)} help is too short"

    def test_library_subcommands_have_help(self) -> None:
        """Test that library subcommands have --help option."""
        subcommands = ["list", "info", "validate"]

        for subcmd in subcommands:
            result = runner.invoke(app, ["library", subcmd, "--help"])
            assert result.exit_code == 0, f"library {subcmd} --help failed"
            assert len(result.stdout) > 50, f"library {subcmd} help is too short"


@pytest.mark.integration
class TestErrorHandling:
    """Tests for error handling in helper commands."""

    def test_examples_unknown_name(self) -> None:
        """Test error message for unknown example name."""
        result = runner.invoke(app, ["examples", "nonexistent"])

        assert result.exit_code == 1
        assert "Unknown example:" in result.stdout
        assert "Available examples:" in result.stdout

    def test_library_info_unknown_device(self) -> None:
        """Test error message for unknown device library."""
        result = runner.invoke(app, ["library", "info", "nonexistent_device"])

        assert result.exit_code == 1
        assert "Library not found:" in result.stdout
        assert "Available libraries:" in result.stdout

    def test_library_validate_invalid_path(self) -> None:
        """Test error for validating non-existent file."""
        result = runner.invoke(app, ["library", "validate", "/tmp/nonexistent_file.mmd"])

        # Typer should catch this before the command runs
        assert result.exit_code != 0


@pytest.mark.integration
class TestOutputFormatting:
    """Tests for consistent output formatting across helper commands."""

    def test_commands_use_rich_formatting(self) -> None:
        """Test that helper commands use Rich formatting."""
        # These commands should produce Rich-formatted output with colors/tables
        commands = [
            ["ports"],
            ["examples"],
            ["version"],
            ["library", "list"],
        ]

        for command in commands:
            result = runner.invoke(app, command)
            # Check that output contains Rich formatting elements
            # (Even without color, Rich adds structure like tables, panels)
            assert len(result.stdout) > 0
            assert result.exit_code == 0

    def test_version_output_format(self) -> None:
        """Test version command output format."""
        result = runner.invoke(app, ["version"])

        assert result.exit_code == 0
        # Should have clear sections
        assert "Version:" in result.stdout
        assert "Python:" in result.stdout
        assert "Dependencies:" in result.stdout
        # Should show checkmarks or indicators for dependencies
        assert "✓" in result.stdout or "✗" in result.stdout or "unknown" in result.stdout
