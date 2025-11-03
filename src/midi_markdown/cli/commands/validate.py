"""Validate command implementation."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

console = Console()


def validate(
    input_file: Annotated[
        Path,
        typer.Argument(
            help="Input .mml file to validate",
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
) -> None:
    """Validate MML file syntax and structure.

    Checks the MML file for syntax errors, invalid values, and structural issues
    without generating a MIDI file.
    """
    console.print(f"[cyan]Validating:[/cyan] {input_file}")

    try:
        # 1. Parse MML file
        if verbose:
            console.print("  [dim]Parsing file...[/dim]")

        from midi_markdown.parser.parser import MMLParser

        parser = MMLParser()
        doc = parser.parse_file(input_file)

        if verbose:
            console.print(f"  [dim]Parsed: {len(doc.events)} event(s)[/dim]")

        # 2. Run value validation
        if verbose:
            console.print("  [dim]Validating MIDI values...[/dim]")

        from midi_markdown.utils import DocumentValidator, TimingValidator

        doc_validator = DocumentValidator()
        value_errors = doc_validator.validate(doc)

        # 3. Run timing validation
        if verbose:
            console.print("  [dim]Validating timing...[/dim]")

        timing_validator = TimingValidator()
        timing_errors = timing_validator.validate(doc)

        # 4. Collect all errors
        all_errors = value_errors + timing_errors

        if all_errors:
            console.print(f"\n[red]✗ Validation failed with {len(all_errors)} error(s):[/red]\n")
            for error in all_errors:
                console.print(f"  [red]•[/red] {error}")
            console.print()
            raise typer.Exit(code=1)

        # Success!
        console.print("[green]✓[/green] Validation passed")
        console.print("  [dim]File is valid and ready for compilation[/dim]")

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {e}")
        if verbose:
            import traceback

            console.print(f"[dim]{traceback.format_exc()}[/dim]")
        raise typer.Exit(code=1)
