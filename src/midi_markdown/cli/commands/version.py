"""Version command implementation."""

from __future__ import annotations

import sys

from rich.console import Console

from midi_markdown import __version__
from midi_markdown.cli.encoding_utils import safe_emoji


def version() -> None:
    """Show version and system information.

    Displays the MIDI Markup Language version, Python version, and
    checks for required dependencies.

    Examples:
        midimarkup version
    """
    console = Console()

    # Get emoji symbols once
    check = safe_emoji("✓", "[OK]")
    cross = safe_emoji("✗", "[X]")

    # Header
    console.print()
    console.print("[bold cyan]MIDI Markup Language (MML)[/bold cyan]")
    console.print(f"Version: [green bold]{__version__}[/green bold]")
    console.print("Human-readable MIDI markup language compiler")
    console.print()

    # Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    console.print(f"[dim]Python:[/dim] [cyan]{python_version}[/cyan]")
    console.print()

    # Check dependencies
    console.print("[bold]Dependencies:[/bold]")

    try:
        import mido

        mido_version = getattr(mido, "__version__", "unknown")
        console.print(f"  [green]{check}[/green] mido: [dim]{mido_version}[/dim]")
    except ImportError:
        console.print(f"  [red]{cross}[/red] mido: [red]not installed[/red]")

    try:
        import rtmidi

        rtmidi_version = getattr(rtmidi, "__version__", "unknown")
        console.print(f"  [green]{check}[/green] python-rtmidi: [dim]{rtmidi_version}[/dim]")
    except ImportError:
        console.print(f"  [red]{cross}[/red] python-rtmidi: [red]not installed[/red]")

    try:
        import lark

        lark_version = getattr(lark, "__version__", "unknown")
        console.print(f"  [green]{check}[/green] lark: [dim]{lark_version}[/dim]")
    except ImportError:
        console.print(f"  [red]{cross}[/red] lark: [red]not installed[/red]")

    try:
        import rich

        rich_version = getattr(rich, "__version__", "unknown")
        console.print(f"  [green]{check}[/green] rich: [dim]{rich_version}[/dim]")
    except ImportError:
        console.print(f"  [red]{cross}[/red] rich: [red]not installed[/red]")

    try:
        import typer

        typer_version = getattr(typer, "__version__", "unknown")
        console.print(f"  [green]{check}[/green] typer: [dim]{typer_version}[/dim]")
    except ImportError:
        console.print(f"  [red]{cross}[/red] typer: [red]not installed[/red]")

    console.print()
    console.print("[dim]Project:[/dim] [cyan]https://github.com/cjgdev/midi-markdown[/cyan]")
    console.print("[dim]Issues:[/dim]  [cyan]https://github.com/cjgdev/midi-markdown/issues[/cyan]")
    console.print()
