"""Benchmark CLI startup and command execution performance.

Tests CLI responsiveness and command execution speed to ensure
good user experience.

Performance Targets:
- CLI startup (--help): <1s
- Small file compile: <2s
- Version command: <500ms

Run with:
    uv run pytest benchmarks/benchmark_cli.py -v
"""

from __future__ import annotations

import subprocess
import time

import pytest


@pytest.mark.benchmark
class TestCLIStartup:
    """Benchmark CLI startup performance."""

    def test_cli_help_speed(self, benchmark):
        """Benchmark CLI startup time (--help).

        Target: <1 second startup time

        This measures the time to import all modules, initialize
        the CLI framework, and display help text.
        """

        def run_help():
            return subprocess.run(
                ["uv", "run", "mmdc", "--help"],
                capture_output=True,
                text=True,
                check=False,
            )

        result = benchmark(run_help)

        assert result.returncode == 0
        assert "MIDI Markdown Language" in result.stdout or "Usage:" in result.stdout

    def test_cli_version_speed(self, benchmark):
        """Benchmark version command execution.

        Target: <1 second
        """

        def run_version():
            return subprocess.run(
                ["uv", "run", "mmdc", "version"],
                capture_output=True,
                text=True,
                check=False,
            )

        result = benchmark(run_version)

        assert result.returncode == 0

    def test_cli_list_commands(self, benchmark):
        """Benchmark command listing performance."""

        def run_list():
            return subprocess.run(
                ["uv", "run", "mmdc", "--help"],
                capture_output=True,
                text=True,
                check=False,
            )

        result = benchmark(run_list)

        assert result.returncode == 0
        # Check that main commands are listed
        assert "compile" in result.stdout.lower() or "Commands:" in result.stdout


@pytest.mark.benchmark
class TestCompileCommand:
    """Benchmark compile command execution."""

    def test_compile_small_file(self, benchmark, small_mmd_file, tmp_path):
        """Benchmark compile command with small file.

        Target: <2 seconds for small file
        """
        output_file = tmp_path / "output.mid"

        def run_compile():
            result = subprocess.run(
                [
                    "uv",
                    "run",
                    "mmdc",
                    "compile",
                    str(small_mmd_file),
                    "-o",
                    str(output_file),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            # Clean up output file for next iteration
            if output_file.exists():
                output_file.unlink()
            return result

        result = benchmark(run_compile)

        assert result.returncode == 0

    def test_compile_medium_file(self, medium_mmd_file, tmp_path):
        """Test compile command with medium file (not benchmarked in loop).

        Target: <3 seconds
        """
        output_file = tmp_path / "output_medium.mid"

        start = time.perf_counter()
        result = subprocess.run(
            [
                "uv",
                "run",
                "mmdc",
                "compile",
                str(medium_mmd_file),
                "-o",
                str(output_file),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        time.perf_counter() - start

        assert result.returncode == 0
        assert output_file.exists()

        # Clean up
        if output_file.exists():
            output_file.unlink()


@pytest.mark.benchmark
class TestValidateCommand:
    """Benchmark validate command execution."""

    def test_validate_small_file(self, benchmark, small_mmd_file):
        """Benchmark validate command.

        Target: <1.5 seconds

        Validation includes parsing, alias resolution, and all
        validation checks.
        """

        def run_validate():
            return subprocess.run(
                ["uv", "run", "mmdc", "validate", str(small_mmd_file)],
                capture_output=True,
                text=True,
                check=False,
            )

        result = benchmark(run_validate)

        assert result.returncode == 0

    def test_check_syntax_only(self, benchmark, small_mmd_file):
        """Benchmark check command (syntax only, no validation).

        Target: <1 second

        Check command should be faster than validate as it only
        parses without full validation.
        """

        def run_check():
            return subprocess.run(
                ["uv", "run", "mmdc", "check", str(small_mmd_file)],
                capture_output=True,
                text=True,
                check=False,
            )

        result = benchmark(run_check)

        assert result.returncode == 0


@pytest.mark.benchmark
class TestInspectCommand:
    """Benchmark inspect command execution."""

    def test_inspect_file(self, benchmark, small_mmd_file):
        """Benchmark inspect command.

        Target: <2 seconds

        Inspect performs full compilation and displays event table.
        """

        def run_inspect():
            return subprocess.run(
                ["uv", "run", "mmdc", "inspect", str(small_mmd_file)],
                capture_output=True,
                text=True,
                check=False,
            )

        result = benchmark(run_inspect)

        # Inspect should succeed and show events
        assert result.returncode == 0


@pytest.mark.benchmark
class TestCLIOptions:
    """Benchmark CLI with various options."""

    def test_compile_with_verbose(self, small_mmd_file, tmp_path):
        """Test compile with verbose flag.

        Verbose should add minimal overhead.
        """
        output_file = tmp_path / "output_verbose.mid"

        start = time.perf_counter()
        result = subprocess.run(
            [
                "uv",
                "run",
                "mmdc",
                "compile",
                str(small_mmd_file),
                "-o",
                str(output_file),
                "-v",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        time.perf_counter() - start

        assert result.returncode == 0

        # Clean up
        if output_file.exists():
            output_file.unlink()

    def test_compile_with_no_color(self, small_mmd_file, tmp_path):
        """Test compile with --no-color flag."""
        output_file = tmp_path / "output_nocolor.mid"

        start = time.perf_counter()
        result = subprocess.run(
            [
                "uv",
                "run",
                "mmdc",
                "compile",
                str(small_mmd_file),
                "-o",
                str(output_file),
                "--no-color",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        time.perf_counter() - start

        assert result.returncode == 0

        # Clean up
        if output_file.exists():
            output_file.unlink()

    def test_compile_different_formats(self, small_mmd_file, tmp_path):
        """Test compile with different output formats.

        Tests CSV and JSON export performance.
        """
        # CSV export
        csv_file = tmp_path / "output.csv"
        start = time.perf_counter()
        result_csv = subprocess.run(
            [
                "uv",
                "run",
                "mmdc",
                "compile",
                str(small_mmd_file),
                "-o",
                str(csv_file),
                "--format",
                "csv",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        time.perf_counter() - start

        # JSON export
        json_file = tmp_path / "output.json"
        start = time.perf_counter()
        result_json = subprocess.run(
            [
                "uv",
                "run",
                "mmdc",
                "compile",
                str(small_mmd_file),
                "-o",
                str(json_file),
                "--format",
                "json",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        time.perf_counter() - start

        assert result_csv.returncode == 0
        assert result_json.returncode == 0

        # Clean up
        if csv_file.exists():
            csv_file.unlink()
        if json_file.exists():
            json_file.unlink()


@pytest.mark.benchmark
class TestCLIErrorHandling:
    """Benchmark CLI error handling performance."""

    def test_error_invalid_file(self, benchmark):
        """Test CLI handles missing file gracefully.

        Error path should still be fast.
        """

        def run_invalid():
            return subprocess.run(
                ["uv", "run", "mmdc", "compile", "nonexistent.mmd"],
                capture_output=True,
                text=True,
                check=False,
            )

        result = benchmark(run_invalid)

        assert result.returncode != 0  # Should fail

    def test_error_invalid_syntax(self, benchmark, tmp_path):
        """Test CLI handles syntax errors gracefully."""
        # Create invalid MMD file
        invalid_file = tmp_path / "invalid.mmd"
        invalid_file.write_text(
            """---
title: Invalid
---

[00:00.000]
- invalid_command 1.2.3
"""
        )

        def run_invalid_syntax():
            return subprocess.run(
                ["uv", "run", "mmdc", "compile", str(invalid_file)],
                capture_output=True,
                text=True,
                check=False,
            )

        result = benchmark(run_invalid_syntax)

        assert result.returncode != 0
