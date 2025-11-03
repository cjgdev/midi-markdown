"""Version command implementation."""

from __future__ import annotations

from rich.console import Console

from midi_markdown import __version__

console = Console()


def version() -> None:
    """Show version information."""
    console.print(f"[bold]MIDI Markdown[/bold] v{__version__}")
    console.print("Human-readable MIDI markup language compiler")
