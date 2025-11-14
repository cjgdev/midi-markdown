"""Rich UI components for TUI display.

This module provides reusable Rich components for rendering the TUI:
- Header: File name, port, title
- Progress bar: Visual playback progress
- Event list: Scrolling MIDI event history
- Status bar: Time, tempo, state
- Controls: Keyboard shortcut help
"""

from __future__ import annotations

from typing import Any

from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich.table import Table
from rich.text import Text


def render_header(file_name: str, port_name: str, title: str | None = None) -> Panel:
    """Render header panel with file and port information.

    Args:
        file_name: Name of the MML file being played
        port_name: MIDI output port name
        title: Optional song title from metadata

    Returns:
        Rich Panel containing header information
    """
    title_text = title if title else "Untitled"
    content = Text()
    content.append(f"♪ {title_text}\n", style="bold cyan")
    content.append("File: ", style="dim")
    content.append(f"{file_name}\n", style="white")
    content.append("Port: ", style="dim")
    content.append(f"{port_name}", style="green")

    return Panel(content, title="MIDI Playback", border_style="cyan")


def render_progress_bar(position_ms: float, total_duration_ms: float) -> Progress:
    """Render progress bar showing playback position.

    Args:
        position_ms: Current playback position in milliseconds
        total_duration_ms: Total duration in milliseconds

    Returns:
        Rich Progress object with single task
    """
    progress = Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=40),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        expand=False,
    )

    # Format time as MM:SS
    current_sec = int(position_ms / 1000)
    total_sec = int(total_duration_ms / 1000)
    current_time = f"{current_sec // 60:02d}:{current_sec % 60:02d}"
    total_time = f"{total_sec // 60:02d}:{total_sec % 60:02d}"

    progress.add_task(
        f"[cyan]{current_time}[/cyan] / {total_time}",
        total=total_duration_ms,
        completed=position_ms,
    )

    return progress


def render_event_list(events: list[Any], max_rows: int = 10) -> Panel:
    """Render scrolling list of recent MIDI events.

    Args:
        events: List of EventInfo objects
        max_rows: Maximum number of events to display

    Returns:
        Rich Panel containing event table
    """
    table = Table(show_header=True, header_style="bold cyan", box=None, padding=(0, 1))
    table.add_column("Time", style="dim", width=8)
    table.add_column("Type", style="cyan", width=12)
    table.add_column("Ch", style="magenta", width=3, justify="right")
    table.add_column("Data", style="white")

    # Show most recent events first (reversed)
    recent_events = list(reversed(events[-max_rows:]))

    if not recent_events:
        table.add_row("", "[dim]No events yet...[/dim]", "", "")
    else:
        for event in recent_events:
            time_sec = event.time_ms / 1000
            time_str = f"{time_sec:>7.2f}s"
            table.add_row(time_str, event.type, str(event.channel), event.data)

    return Panel(table, title="Recent Events", border_style="blue")


def render_status_bar(state: str, tempo: float, position_ticks: int) -> Text:
    """Render status bar with current playback state.

    Args:
        state: Current state ("playing", "paused", "stopped")
        tempo: Current tempo in BPM
        position_ticks: Current position in ticks

    Returns:
        Rich Text object with status information
    """
    status_text = Text()

    # State indicator with color
    if state == "playing":
        status_text.append("▶ PLAYING", style="bold green")
    elif state == "paused":
        status_text.append("⏸ PAUSED", style="bold yellow")
    else:
        status_text.append("⏹ STOPPED", style="bold red")

    status_text.append(" │ ", style="dim")
    status_text.append(f"Tempo: {tempo:.1f} BPM", style="white")
    status_text.append(" │ ", style="dim")
    status_text.append(f"Tick: {position_ticks}", style="cyan")

    return status_text


def render_controls() -> Panel:
    """Render keyboard controls help panel.

    Returns:
        Rich Panel with keyboard shortcut information
    """
    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("Key", style="bold cyan", width=14)
    table.add_column("Action", style="white", width=30)

    table.add_row("SPACE", "Play / Pause")
    table.add_row("←  →", "Seek ±5 seconds")
    table.add_row("Shift+←  →", "Seek ±1 beat")
    table.add_row("Ctrl+←  →", "Seek ±1 bar")
    table.add_row("Q", "Quit")

    return Panel(table, title="Controls", border_style="yellow")
