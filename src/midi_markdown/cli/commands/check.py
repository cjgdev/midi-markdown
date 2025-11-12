"""Check command implementation - syntax checking only."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from midi_markdown.cli.encoding_utils import safe_emoji
from midi_markdown.cli.error_handler import ErrorContext, cli_error_handler


def check(
    input_file: Annotated[
        Path,
        typer.Argument(
            help="Input .mmd file to check",
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
) -> None:
    """Check MML file syntax only - fast syntax validation.

    Performs a quick syntax check by parsing the MML file without performing
    full semantic validation or compilation. This is the fastest way to catch
    syntax errors like typos, missing brackets, or malformed commands.

    The check command only verifies that the file can be parsed - it does NOT:
    - Validate MIDI value ranges (e.g., channel 1-16)
    - Check timing monotonicity
    - Resolve or validate aliases
    - Expand variables or loops
    - Verify imports exist

    Use this for rapid feedback during editing, then use `validate` or `compile`
    for comprehensive checking before performance.

    Examples:
        # Quick syntax check
        midimarkup check song.mmd

        # Check with verbose output
        midimarkup check song.mmd -v

        # Check multiple files quickly
        midimarkup check *.mmd

        # Check with debug output on errors
        midimarkup check song.mmd --debug

    Exit Codes:
        0  Syntax is valid - file can be parsed
        2  Parse error - syntax mistakes found
        4  File not found or not readable

    Performance:
        The check command is typically 5-10x faster than full validation,
        making it ideal for editor integration and rapid development workflows.

    Notes:
        - This command only checks syntax, not semantics
        - Always validate or compile before using in performance
        - Use in watch mode or editor save hooks for instant feedback
    """
    console = Console()

    # Create error context
    ctx = ErrorContext(
        mode="check",
        debug=debug,
        source_file=input_file,
        console=console,
    )

    with cli_error_handler(ctx):
        console.print(f"[cyan]Checking syntax:[/cyan] {input_file}")

        # Parse the file - this checks syntax
        if verbose:
            console.print("  [dim]Parsing file...[/dim]")

        from midi_markdown.parser.parser import MMDParser

        parser = MMDParser()
        doc = parser.parse_file(input_file)

        # Success!
        check_mark = safe_emoji("✓", "[OK]")
        console.print(f"[green]{check_mark}[/green] Syntax is valid")
        if verbose:
            console.print(f"  [dim]Parsed: {len(doc.events)} event(s)[/dim]")
            console.print("  [dim]Note: Use 'validate' command for full validation[/dim]")
