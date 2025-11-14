"""Play command for real-time MIDI playback."""

from __future__ import annotations

import sys
import threading
import time
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from midi_markdown.cli.encoding_utils import safe_emoji
from midi_markdown.core.compiler import compile_ast_to_ir
from midi_markdown.parser.parser import MMDParser
from midi_markdown.runtime.midi_io import MIDIOutputManager
from midi_markdown.runtime.player import RealtimePlayer
from midi_markdown.runtime.tui import (
    KeyboardInputHandler,
    TUIDisplayManager,
    TUIState,
)


def play(
    input_file: Annotated[Path | None, typer.Argument(help="MML file to play")] = None,
    port: Annotated[
        str | None, typer.Option("--port", "-p", help="MIDI output port name or index")
    ] = None,
    list_ports: Annotated[
        bool, typer.Option("--list-ports", help="List available MIDI output ports")
    ] = False,
    no_ui: Annotated[
        bool, typer.Option("--no-ui", help="Disable TUI and use simple progress display")
    ] = False,
    debug: Annotated[
        bool,
        typer.Option("--debug", help="Show full error tracebacks"),
    ] = False,
) -> None:
    """Play MML file in real-time to MIDI output.

    Examples:
        midimarkup play song.mmd --port "IAC Driver Bus 1"
        midimarkup play song.mmd --port 0
        midimarkup play song.mmd --port 0 --no-ui
        midimarkup play --list-ports
    """
    console = Console()

    # List ports mode
    if list_ports:
        manager = MIDIOutputManager()
        ports = manager.list_ports()

        console.print("[bold cyan]Available MIDI output ports:[/bold cyan]")
        if ports:
            for i, port_name in enumerate(ports):
                console.print(f"  [cyan]{i}:[/cyan] {port_name}")
        else:
            console.print("  [dim]No MIDI ports found[/dim]")
        return

    # Require input_file for playback
    if not input_file:
        console.print("[red]Error: INPUT_FILE is required for playback[/red]")
        console.print("[dim]Use --list-ports to see available MIDI ports[/dim]")
        raise typer.Exit(1)

    # Require --port for playback
    if not port:
        console.print("[red]Error: --port is required for playback[/red]")
        console.print("[dim]Use --list-ports to see available MIDI ports[/dim]")
        raise typer.Exit(1)

    # Check file exists
    if not input_file.exists():
        console.print(f"[red]Error: File not found: {input_file}[/red]")
        raise typer.Exit(1)

    # Compile MML file
    console.print(f"[cyan]Compiling:[/cyan] {input_file}")
    try:
        parser = MMDParser()
        doc = parser.parse_file(input_file)
        ir_program = compile_ast_to_ir(doc)
    except Exception as e:
        console.print(f"[red]Compilation error:[/red] {e}")
        raise typer.Exit(1)

    # Create player
    console.print(f"[cyan]Opening MIDI port:[/cyan] {port}")
    try:
        player = RealtimePlayer(ir_program, port)
    except Exception as e:
        console.print(f"[red]MIDI error:[/red] {e}")
        raise typer.Exit(1)

    # Show playback info
    duration_ms = player.get_duration_ms()
    duration_s = duration_ms / 1000
    console.print(f"[cyan]Duration:[/cyan] {duration_s:.2f}s ({ir_program.event_count} events)")
    console.print()

    # Choose playback mode
    if no_ui:
        _play_simple(console, player, duration_ms, ir_program.event_count)
    # Check if TTY is available for TUI
    elif not sys.stdin.isatty():
        console.print("[yellow]Warning: No TTY detected, falling back to simple mode[/yellow]")
        _play_simple(console, player, duration_ms, ir_program.event_count)
    else:
        # Get title from frontmatter if available
        title = doc.frontmatter.get("title", None) if doc.frontmatter else None
        _play_with_tui(player, input_file.name, port, title, duration_ms, ir_program)


def _play_simple(
    console: Console, player: RealtimePlayer, duration_ms: float, event_count: int
) -> None:
    """Simple playback mode with spinner progress indicator."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Playing...", total=None)

        player.play()

        # Wait for completion
        while not player.is_complete():
            time.sleep(0.1)

        progress.update(task, description="[green]Playback complete")

    console.print()
    check_mark = safe_emoji("✓", "[OK]")
    console.print(f"[green]{check_mark}[/green] Done")


def _play_with_tui(
    player: RealtimePlayer,
    file_name: str,
    port_name: str,
    title: str | None,
    duration_ms: float,
    ir_program,
) -> None:
    """Interactive TUI playback mode with live event visualization."""
    from midi_markdown.runtime.tui.state import EventInfo

    # Create thread-safe state
    tui_state = TUIState(
        total_duration_ms=duration_ms,
        initial_tempo=ir_program.initial_tempo,
        max_events=20,
    )

    # Set up event callback to update TUI state
    def on_event_sent(metadata: dict) -> None:
        """Callback when scheduler sends MIDI event."""
        # Update position from event metadata
        if "tick" in metadata:
            tick = metadata["tick"]
            time_ms = player.tempo_tracker.ticks_to_ms(tick)
            tui_state.update_position(time_ms, tick)

        # Add event to history
        event_type = metadata.get("type", "unknown")
        channel = metadata.get("channel", 0)
        event_info = EventInfo(
            time_ms=time_ms if "tick" in metadata else 0.0,
            type=event_type,
            channel=channel,
            data=f"Ch{channel}",
        )
        tui_state.add_event(event_info)

    # Wire callback to scheduler
    player.scheduler.on_event_sent = on_event_sent

    # Create display manager
    display_manager = TUIDisplayManager(
        state=tui_state,
        file_name=file_name,
        port_name=port_name,
        title=title,
        refresh_rate=30,
    )

    # Create keyboard handler with callbacks
    quit_flag = threading.Event()

    # Seek interval in milliseconds (5 seconds)
    SEEK_INTERVAL_MS = 5000.0

    def on_play_pause() -> None:
        """Toggle play/pause."""
        if player.scheduler.state == "playing":
            player.pause()
            tui_state.set_state("paused")
        elif player.scheduler.state == "paused":
            player.resume()
            tui_state.set_state("playing")
        else:
            player.play()
            tui_state.set_state("playing")

    def on_quit() -> None:
        """Stop playback and quit."""
        player.stop()
        tui_state.set_state("stopped")
        quit_flag.set()

    def on_seek_forward() -> None:
        """Seek forward by SEEK_INTERVAL_MS."""
        # Get current position from state
        snapshot = tui_state.get_state_snapshot()
        current_pos_ms = snapshot["position_ms"]
        total_duration_ms = snapshot["total_duration_ms"]

        # Calculate new position (clamped to duration)
        new_pos_ms = min(current_pos_ms + SEEK_INTERVAL_MS, total_duration_ms)

        # Seek player
        player.seek(new_pos_ms)

        # Update TUI state position
        new_ticks = player.tempo_tracker.ms_to_ticks(new_pos_ms)
        tui_state.update_position(new_pos_ms, new_ticks)

    def on_seek_backward() -> None:
        """Seek backward by SEEK_INTERVAL_MS."""
        # Get current position from state
        snapshot = tui_state.get_state_snapshot()
        current_pos_ms = snapshot["position_ms"]

        # Calculate new position (clamped to 0)
        new_pos_ms = max(current_pos_ms - SEEK_INTERVAL_MS, 0.0)

        # Seek player
        player.seek(new_pos_ms)

        # Update TUI state position
        new_ticks = player.tempo_tracker.ms_to_ticks(new_pos_ms)
        tui_state.update_position(new_pos_ms, new_ticks)

    def on_seek_beat_forward() -> None:
        """Seek forward by 1 beat."""
        snapshot = tui_state.get_state_snapshot()
        current_pos_ms = snapshot["position_ms"]

        # Seek forward 1 beat
        new_pos_ms = player.seek_beats(1, current_pos_ms)

        # Update TUI state position
        new_ticks = player.tempo_tracker.ms_to_ticks(new_pos_ms)
        tui_state.update_position(new_pos_ms, new_ticks)

    def on_seek_beat_backward() -> None:
        """Seek backward by 1 beat."""
        snapshot = tui_state.get_state_snapshot()
        current_pos_ms = snapshot["position_ms"]

        # Seek backward 1 beat
        new_pos_ms = player.seek_beats(-1, current_pos_ms)

        # Update TUI state position
        new_ticks = player.tempo_tracker.ms_to_ticks(new_pos_ms)
        tui_state.update_position(new_pos_ms, new_ticks)

    def on_seek_bar_forward() -> None:
        """Seek forward by 1 bar."""
        snapshot = tui_state.get_state_snapshot()
        current_pos_ms = snapshot["position_ms"]

        # Seek forward 1 bar
        new_pos_ms = player.seek_bars(1, current_pos_ms)

        # Update TUI state position
        new_ticks = player.tempo_tracker.ms_to_ticks(new_pos_ms)
        tui_state.update_position(new_pos_ms, new_ticks)

    def on_seek_bar_backward() -> None:
        """Seek backward by 1 bar."""
        snapshot = tui_state.get_state_snapshot()
        current_pos_ms = snapshot["position_ms"]

        # Seek backward 1 bar
        new_pos_ms = player.seek_bars(-1, current_pos_ms)

        # Update TUI state position
        new_ticks = player.tempo_tracker.ms_to_ticks(new_pos_ms)
        tui_state.update_position(new_pos_ms, new_ticks)

    keyboard_handler = KeyboardInputHandler(
        on_play_pause=on_play_pause,
        on_quit=on_quit,
        on_seek_forward=on_seek_forward,
        on_seek_backward=on_seek_backward,
        on_seek_beat_forward=on_seek_beat_forward,
        on_seek_beat_backward=on_seek_beat_backward,
        on_seek_bar_forward=on_seek_bar_forward,
        on_seek_bar_backward=on_seek_bar_backward,
    )

    # Start display and keyboard listener
    display_manager.start()
    keyboard_handler.start()

    # Start playback
    player.play()
    tui_state.set_state("playing")

    # Main update loop
    try:
        while not player.is_complete() and not quit_flag.is_set():
            # Update display (position updates happen via callback)
            display_manager.update_display()

            # Sleep for refresh interval
            time.sleep(display_manager.refresh_interval)

        # Mark as complete
        tui_state.set_state("stopped")
        display_manager.update_display()

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        player.stop()
        tui_state.set_state("stopped")

    finally:
        # Cleanup
        keyboard_handler.stop()
        display_manager.stop()
