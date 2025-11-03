"""Check command implementation - syntax checking only."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

console = Console()


def check(
    input_file: Annotated[
        Path,
        typer.Argument(
            help="Input .mml file to check",
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
    """Check MML file syntax only (no validation).

    Performs a quick syntax check without full validation or compilation.
    """
    console.print(f"[cyan]Checking syntax:[/cyan] {input_file}")

    try:
        # Parse the file - this checks syntax
        if verbose:
            console.print("  [dim]Parsing file...[/dim]")

        from midi_markdown.parser.parser import MMLParser

        parser = MMLParser()
        doc = parser.parse_file(input_file)

        # Success!
        console.print("[green]✓[/green] Syntax is valid")
        if verbose:
            console.print(f"  [dim]Parsed: {len(doc.events)} event(s)[/dim]")
            console.print("  [dim]Note: Use 'validate' command for full validation[/dim]")

    except Exception as e:
        console.print(f"[red]✗ Syntax error:[/red] {e}")
        if verbose:
            import traceback

            console.print(f"[dim]{traceback.format_exc()}[/dim]")
        raise typer.Exit(code=1)
