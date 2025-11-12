"""Validate command implementation."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from midi_markdown.cli.encoding_utils import safe_emoji
from midi_markdown.cli.error_handler import ErrorContext, cli_error_handler
from midi_markdown.cli.progress import (
    ValidationProgress,
    create_validation_progress,
    should_show_progress,
)


def validate(
    input_file: Annotated[
        Path,
        typer.Argument(
            help="Input .mmd file to validate",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
        ),
    ],
    verbose: Annotated[
        bool,
        typer.Option("-v", "--verbose", help="Verbose output"),
    ] = False,
    debug: Annotated[
        bool,
        typer.Option("--debug", help="Show full error tracebacks"),
    ] = False,
    no_progress: Annotated[
        bool,
        typer.Option("--no-progress", help="Disable progress indicators"),
    ] = False,
) -> None:
    """Validate MML file syntax and structure without compiling.

    Performs comprehensive validation of an MML file including:
    - Syntax checking (parse errors, unexpected tokens)
    - Semantic validation (MIDI value ranges, timing constraints)
    - Alias resolution and parameter validation
    - Import validation (device library dependencies)
    - Variable and loop expansion validation

    This command is faster than full compilation and useful for quick error
    checking during development. It catches most issues without generating output.

    Examples:
        # Basic validation
        midimarkup validate song.mmd

        # Verbose validation showing all steps
        midimarkup validate song.mmd -v

        # Validate with full error tracebacks
        midimarkup validate song.mmd --debug

        # Validate large file with progress indicator
        midimarkup validate large_composition.mmd --verbose

        # Quick validation in CI/CD pipeline
        midimarkup validate *.mmd --no-progress

    Exit Codes:
        0  Validation passed - file is valid
        2  Parse error - syntax mistakes
        3  Validation error - invalid MIDI values or structure
        4  File not found or not readable

    Notes:
        - Validation is a prerequisite for compilation
        - Use `check` command for even faster syntax-only validation
        - Progress indicators appear for files >50KB or >500 events
        - Validation includes all alias expansion and imports
    """
    console = Console()

    # Create error context
    ctx = ErrorContext(
        mode="validate",
        debug=debug,
        source_file=input_file,
        console=console,
    )

    with cli_error_handler(ctx):
        console.print(f"[cyan]Validating:[/cyan] {input_file}")

        # 1. Parse MML file
        if verbose:
            console.print("  [dim]Parsing file...[/dim]")

        from midi_markdown.parser.parser import MMDParser

        parser = MMDParser()
        doc = parser.parse_file(input_file)

        if verbose:
            console.print(f"  [dim]Parsed: {len(doc.events)} event(s)[/dim]")

        # Determine if we should show progress (for large files or verbose mode)
        use_progress = should_show_progress(input_file, doc, verbose, no_progress)

        # Use progress indicator for large files
        if use_progress:
            progress_bar = create_validation_progress(console)
            progress_ctx = ValidationProgress(progress_bar)
        else:
            # No progress for small files in non-verbose mode
            from contextlib import nullcontext

            progress_ctx = nullcontext()

        with progress_ctx as progress:
            # Parsing phase complete
            if isinstance(progress, ValidationProgress):
                progress.parsing_complete()

            # 2. Run value validation
            if verbose:
                console.print("  [dim]Validating MIDI values...[/dim]")

            from midi_markdown.utils import DocumentValidator, TimingValidator

            doc_validator = DocumentValidator()
            value_errors = doc_validator.validate(doc)

            # 3. Run timing validation
            if isinstance(progress, ValidationProgress):
                progress.aliases_complete()

            if verbose:
                console.print("  [dim]Validating timing...[/dim]")

            timing_validator = TimingValidator()
            timing_errors = timing_validator.validate(doc)

            if isinstance(progress, ValidationProgress):
                progress.validation_complete()

            # 4. Collect all errors
            all_errors = value_errors + timing_errors

            if all_errors:
                cross = safe_emoji("✗", "[X]")
                console.print(
                    f"\n[red]{cross} Validation failed with {len(all_errors)} error(s):[/red]\n"
                )
                for error in all_errors:
                    console.print(f"  [red]-[/red] {error}")
                console.print()
                raise typer.Exit(code=1)

        # Success!
        check = safe_emoji("✓", "[OK]")
        console.print(f"[green]{check}[/green] Validation passed")
        console.print("  [dim]File is valid and ready for compilation[/dim]")
