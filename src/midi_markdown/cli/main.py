"""CLI entry point for MIDI Markdown.

This module provides the main command-line interface using Typer.
All command implementations are in the commands/ package.
"""

from __future__ import annotations

from typing import Annotated, Optional

import typer

from midi_markdown import __version__

from .commands import (
    check,
    compile,
    library_info,
    library_list,
    library_validate,
    validate,
    version,
)


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        from rich.console import Console

        console = Console()
        console.print(f"[bold]MIDI Markdown[/bold] v{__version__}")
        console.print("Human-readable MIDI markup language compiler")
        raise typer.Exit()


# Create app instance
app = typer.Typer(
    name="midimarkup",
    help="MIDI Markup Language (MML) compiler and tools for creating MIDI sequences",
    add_completion=True,
    no_args_is_help=True,
    callback=lambda version_flag: None,  # Placeholder, will be replaced below
)


@app.callback()
def main(
    version_flag: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            "-V",
            help="Show version and exit",
            callback=version_callback,
            is_eager=True,
        ),
    ] = None,
) -> None:
    """MIDI Markup Language (MML) compiler and tools."""
    pass


# Register main commands
app.command()(compile)
app.command()(validate)
app.command()(check)
app.command()(version)

# Create library subcommand group
library_app = typer.Typer(
    help="Device library management",
    no_args_is_help=True,
)
app.add_typer(library_app, name="library")

# Register library subcommands
library_app.command("list")(library_list)
library_app.command("info")(library_info)
library_app.command("validate")(library_validate)


def cli() -> None:
    """Main CLI entry point."""
    app()
