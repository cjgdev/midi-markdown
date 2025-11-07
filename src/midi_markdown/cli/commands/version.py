"""Version command implementation."""

from __future__ import annotations

import sys

from rich.console import Console

from midi_markdown import __version__


def version() -> None:
    """Show version and system information.

    Displays the MIDI Markup Language version, Python version, and
    checks for required dependencies.

    Examples:
        midimarkup version
    """
    console = Console()

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
        console.print(f"  [green]✓[/green] mido: [dim]{mido_version}[/dim]")
    except ImportError:
        console.print("  [red]✗[/red] mido: [red]not installed[/red]")

    try:
        import rtmidi

        rtmidi_version = getattr(rtmidi, "__version__", "unknown")
        console.print(f"  [green]✓[/green] python-rtmidi: [dim]{rtmidi_version}[/dim]")
    except ImportError:
        console.print("  [red]✗[/red] python-rtmidi: [red]not installed[/red]")

    try:
        import lark

        lark_version = getattr(lark, "__version__", "unknown")
        console.print(f"  [green]✓[/green] lark: [dim]{lark_version}[/dim]")
    except ImportError:
        console.print("  [red]✗[/red] lark: [red]not installed[/red]")

    try:
        import rich

        rich_version = getattr(rich, "__version__", "unknown")
        console.print(f"  [green]✓[/green] rich: [dim]{rich_version}[/dim]")
    except ImportError:
        console.print("  [red]✗[/red] rich: [red]not installed[/red]")

    try:
        import typer

        typer_version = getattr(typer, "__version__", "unknown")
        console.print(f"  [green]✓[/green] typer: [dim]{typer_version}[/dim]")
    except ImportError:
        console.print("  [red]✗[/red] typer: [red]not installed[/red]")

    console.print()
    console.print("[dim]Project:[/dim] [cyan]https://github.com/cjgdev/midi-markdown[/cyan]")
    console.print("[dim]Issues:[/dim]  [cyan]https://github.com/cjgdev/midi-markdown/issues[/cyan]")
    console.print()
