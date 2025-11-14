"""Formatting utilities for displaying MIDI events as Rich tables."""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.console import Console
from rich.table import Table
from rich.text import Text

if TYPE_CHECKING:
    from midi_markdown.core.ir import EventType, IRProgram, MIDIEvent


def display_events_table(
    ir_program: IRProgram,
    max_events: int | None = 100,
    show_stats: bool = True,
    console: Console | None = None,
) -> None:
    """Display MIDI events as formatted Rich table.

    Args:
        ir_program: Compiled IR program to display
        max_events: Maximum number of events to show (None for all)
        show_stats: Whether to show summary statistics
        console: Optional Rich Console instance (creates new one if not provided)

    Example:
        >>> from midi_markdown.core import compile_ast_to_ir
        >>> from midi_markdown.parser.parser import MMDParser
        >>> parser = MMDParser()
        >>> doc = parser.parse_file("song.mmd")
        >>> ir = compile_ast_to_ir(doc)
        >>> display_events_table(ir, max_events=50)
    """
    if console is None:
        console = Console()

    # Show summary statistics first
    if show_stats:
        summary = get_event_summary(ir_program)
        console.print()
        console.print("[bold cyan]Program Summary[/]")
        console.print(f"  Events: [bold]{summary['total_events']}[/]")
        console.print(
            f"  Duration: [bold]{summary['duration_seconds']:.2f}s[/] "
            f"({summary['duration_ticks']} ticks)"
        )
        console.print(f"  Tempo: [bold]{summary['initial_tempo']} BPM[/]")
        console.print(f"  Resolution: [bold]{summary['resolution']} PPQ[/]")
        console.print(f"  Channels used: [bold]{', '.join(map(str, summary['channels_used']))}[/]")
        console.print()

    # Create table
    table = Table(
        title="[bold magenta]MIDI Event Timeline[/]",
        show_header=True,
        header_style="bold cyan",
        show_lines=False,
        expand=False,
    )

    # Add columns
    table.add_column("Time (musical)", style="cyan", justify="right", width=12)
    table.add_column("Time (sec)", style="blue", justify="right", width=10)
    table.add_column("Type", style="magenta", width=14)
    table.add_column("Ch", style="green", justify="center", width=4)
    table.add_column("Details", style="white", width=40)

    # Determine which events to display
    events_to_show = ir_program.events[:max_events] if max_events else ir_program.events

    # Add events to table
    for event in events_to_show:
        musical_time = format_musical_time(event.time, ir_program.resolution)
        time_seconds = f"{event.time_seconds:.3f}" if event.time_seconds is not None else "---"

        # Color code event type
        event_type_text = _get_styled_event_type(event.type)

        # Channel display
        channel_str = str(event.channel) if event.channel is not None else "-"

        # Event details
        details = format_event_details(event)

        table.add_row(
            musical_time,
            time_seconds,
            event_type_text,
            channel_str,
            details,
        )

    # Display table
    console.print(table)

    # Show truncation message if needed
    if max_events and len(ir_program.events) > max_events:
        remaining = len(ir_program.events) - max_events
        console.print(f"\n[dim]... and {remaining} more event{'s' if remaining != 1 else ''}[/]")
        console.print("[dim]Use --limit to show more events[/]")


def format_event_details(event: MIDIEvent) -> str:
    """Format event-specific details for display.

    Args:
        event: MIDI event to format

    Returns:
        Formatted details string
    """
    event_type = event.type.name.lower()

    if event_type in {"note_on", "note_off"}:
        note_name = _note_number_to_name(event.data1)
        return f"{note_name} (#{event.data1}) vel:{event.data2}"

    if event_type == "control_change":
        cc_name = _get_cc_name(event.data1)
        return f"CC#{event.data1} ({cc_name}) val:{event.data2}"

    if event_type == "program_change":
        return f"Program {event.data1}"

    if event_type == "pitch_bend":
        # Convert from 0-16383 to -8192 to +8191
        bend_value = event.data1 - 8192
        return f"Bend: {bend_value:+d}"

    if event_type == "channel_pressure":
        return f"Pressure: {event.data1}"

    if event_type == "poly_pressure":
        note_name = _note_number_to_name(event.data1)
        return f"{note_name} pressure: {event.data2}"

    if event_type == "tempo":
        return f"{event.data1} BPM"

    if event_type == "time_signature":
        # data1 is numerator, data2 is denominator (as power of 2)
        if event.metadata:
            num = event.metadata.get("numerator", event.data1)
            denom_power = event.metadata.get("denominator", event.data2)
            denom = 2**denom_power if denom_power else 4
            return f"{num}/{denom}"
        return f"{event.data1}/{2**event.data2 if event.data2 else 4}"

    if event_type in {"marker", "text"}:
        text = event.metadata.get("text", "") if event.metadata else ""
        return f'"{text}"'

    if event_type == "sysex":
        if event.metadata and "bytes" in event.metadata:
            data_bytes = event.metadata["bytes"]
            if len(data_bytes) > 8:
                return f"SysEx: {len(data_bytes)} bytes"
            hex_str = " ".join(f"{b:02X}" for b in data_bytes)
            return f"SysEx: {hex_str}"
        return "SysEx"

    # Generic display for unknown types
    if event.data2 is not None:
        return f"data1:{event.data1} data2:{event.data2}"
    if event.data1 is not None:
        return f"data1:{event.data1}"
    return ""


def format_musical_time(tick: int, ppq: int) -> str:
    """Format tick position as bars.beats.ticks.

    Assumes 4/4 time signature. For accurate display with time signature
    changes, the IRProgram would need to track those changes.

    Args:
        tick: Absolute tick position
        ppq: Pulses per quarter note (ticks per beat)

    Returns:
        Formatted string like "1.1.000" or "8.3.240"
    """
    beats_per_bar = 4  # Assume 4/4 time
    ticks_per_beat = ppq

    total_beats = tick // ticks_per_beat
    tick_in_beat = tick % ticks_per_beat

    bar = (total_beats // beats_per_bar) + 1
    beat = (total_beats % beats_per_bar) + 1

    return f"{bar}.{beat}.{tick_in_beat:03d}"


def get_event_summary(ir_program: IRProgram) -> dict:
    """Calculate summary statistics for IR program.

    Args:
        ir_program: Compiled IR program

    Returns:
        Dictionary with summary statistics
    """
    channels_used = set()
    for event in ir_program.events:
        if event.channel is not None:
            channels_used.add(event.channel)

    return {
        "total_events": len(ir_program.events),
        "duration_ticks": ir_program.duration_ticks,
        "duration_seconds": ir_program.duration_seconds,
        "initial_tempo": ir_program.initial_tempo,
        "resolution": ir_program.resolution,
        "channels_used": sorted(channels_used) if channels_used else [],
    }


def _get_styled_event_type(event_type: EventType) -> Text:
    """Get styled text for event type with color coding.

    Args:
        event_type: Event type enum

    Returns:
        Rich Text object with appropriate styling
    """
    type_name = event_type.name.lower()
    type_display = type_name.replace("_", " ").title()

    # Color code by event type
    if type_name in ("note_on", "note_off"):
        style = "bold magenta"
    elif type_name == "control_change":
        style = "yellow"
    elif type_name == "program_change":
        style = "blue"
    elif type_name == "tempo":
        style = "bold green"
    elif type_name in ("pitch_bend", "channel_pressure", "poly_pressure"):
        style = "cyan"
    elif type_name in ("marker", "text"):
        style = "dim"
    else:
        style = "white"

    return Text(type_display, style=style)


def _note_number_to_name(note: int) -> str:
    """Convert MIDI note number to note name.

    Args:
        note: MIDI note number (0-127)

    Returns:
        Note name like "C4", "A#5", "Gb3"
    """
    if note < 0 or note > 127:
        return f"?{note}"

    note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    octave = (note // 12) - 1
    note_name = note_names[note % 12]

    return f"{note_name}{octave}"


def _get_cc_name(cc_number: int) -> str:
    """Get common name for control change number.

    Args:
        cc_number: CC number (0-127)

    Returns:
        CC name if known, otherwise "Unknown"
    """
    cc_names = {
        0: "Bank Select",
        1: "Modulation",
        2: "Breath",
        4: "Foot",
        5: "Portamento Time",
        6: "Data Entry MSB",
        7: "Volume",
        8: "Balance",
        10: "Pan",
        11: "Expression",
        32: "Bank Select LSB",
        64: "Sustain",
        65: "Portamento",
        66: "Sostenuto",
        67: "Soft Pedal",
        68: "Legato",
        69: "Hold 2",
        71: "Resonance",
        72: "Release Time",
        73: "Attack Time",
        74: "Brightness",
        84: "Portamento Control",
        91: "Reverb",
        92: "Tremolo",
        93: "Chorus",
        94: "Detune",
        95: "Phaser",
        120: "All Sound Off",
        121: "Reset Controllers",
        123: "All Notes Off",
    }

    return cc_names.get(cc_number, "Unknown")
