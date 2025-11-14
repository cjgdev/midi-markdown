"""CSV export for MIDI events in midicsv-compatible format.

This module exports IRProgram data to the midicsv CSV format, which can be
imported into spreadsheet programs, databases, or text processing tools.

Format specification: https://www.fourmilab.ch/webtools/midicsv/
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from midi_markdown.core.ir import EventType, IRProgram, MIDIEvent


def export_to_csv(ir_program: IRProgram, include_header: bool = True) -> str:
    """Export IRProgram to midicsv-compatible CSV format.

    Args:
        ir_program: Compiled IR program to export
        include_header: Include file header and footer records

    Returns:
        CSV string in midicsv format

    Example:
        >>> from midi_markdown.core import compile_ast_to_ir
        >>> from midi_markdown.parser.parser import MMDParser
        >>> parser = MMDParser()
        >>> doc = parser.parse_file("song.mmd")
        >>> ir = compile_ast_to_ir(doc)
        >>> csv = export_to_csv(ir)
        >>> print(csv)
        0, 0, Header, 1, 1, 480
        1, 0, Start_track
        1, 0, Tempo, 500000
        ...
    """
    lines = []

    # Add file header if requested
    if include_header:
        # Header: track 0, time 0, Header, format, nTracks, division
        # Format 1 = single track, nTracks = 1, division = PPQ
        lines.append(f"0, 0, Header, 1, 1, {ir_program.resolution}")

    # Track start marker
    lines.append("1, 0, Start_track")

    # Convert all events to CSV lines
    for event in ir_program.events:
        csv_line = _format_event_as_csv(event, track=1, ppq=ir_program.resolution)
        if csv_line:  # Skip events that don't export to CSV
            lines.append(csv_line)

    # Track end marker (at max time)
    max_time = ir_program.duration_ticks
    lines.append(f"1, {max_time}, End_track")

    # Add file footer if requested
    if include_header:
        lines.append("0, 0, End_of_file")

    return "\n".join(lines)


def _format_event_as_csv(event: MIDIEvent, track: int, ppq: int) -> str:
    """Format single MIDI event as CSV line.

    Args:
        event: MIDI event to format
        track: Track number (1-based)
        ppq: Pulses per quarter note (for tempo conversion)

    Returns:
        CSV line string, or empty string if event should be skipped
    """
    event_name = _event_type_to_midicsv_name(event.type)
    if not event_name:
        return ""  # Skip unsupported event types

    time = event.time
    event_type_name = event.type.name.lower()

    # Channel voice events (note_on, note_off, cc, pc, pitch_bend, etc.)
    if event_type_name in {"note_on", "note_off", "control_change"}:
        return f"{track}, {time}, {event_name}, {event.channel}, {event.data1}, {event.data2}"

    if event_type_name == "program_change":
        return f"{track}, {time}, {event_name}, {event.channel}, {event.data1}"

    if event_type_name == "pitch_bend":
        # Pitch bend: data1 is 14-bit value (0-16383, center at 8192)
        return f"{track}, {time}, {event_name}, {event.channel}, {event.data1}"

    if event_type_name == "channel_pressure":
        return f"{track}, {time}, {event_name}, {event.channel}, {event.data1}"

    if event_type_name == "poly_pressure":
        return f"{track}, {time}, {event_name}, {event.channel}, {event.data1}, {event.data2}"

    # Meta events (tempo, time signature, markers, text)
    if event_type_name == "tempo":
        # Convert BPM to microseconds per quarter note
        # microseconds_per_qn = 60,000,000 / BPM
        bpm = event.data1
        microseconds_per_qn = int(60_000_000 / bpm) if bpm > 0 else 500000
        return f"{track}, {time}, {event_name}, {microseconds_per_qn}"

    if event_type_name == "time_signature":
        # Time signature: numerator, denominator (as power of 2), clocks, notesq
        # Try to get from metadata first, then data1/data2, finally defaults
        if event.metadata and "numerator" in event.metadata:
            numerator = event.metadata.get("numerator")
            denominator_power = event.metadata.get("denominator", 2)  # 2^2 = 4 (quarter note)
        elif event.data1 is not None:
            numerator = event.data1
            denominator_power = event.data2 if event.data2 is not None else 2
        else:
            # Default to 4/4 if no data available
            numerator = 4
            denominator_power = 2  # 2^2 = 4

        # midicsv format: Numerator, Denominator_power, Clocks_per_click, Notes_per_quarter
        # Use standard values for clocks (24) and notes per quarter (8)
        clocks_per_click = 24
        notes_per_quarter = 8
        return f"{track}, {time}, {event_name}, {numerator}, {denominator_power}, {clocks_per_click}, {notes_per_quarter}"

    if event_type_name == "key_signature":
        # Key signature: sharps/flats (-7 to +7), major/minor (0/1)
        # For now, use data1 as sharps/flats, data2 as major(0)/minor(1)
        sharps_flats = event.data1 if event.data1 is not None else 0
        mode = "minor" if event.data2 == 1 else "major"
        return f'{track}, {time}, {event_name}, {sharps_flats}, "{mode}"'

    if event_type_name == "marker":
        # Marker text event
        text = event.metadata.get("text", "") if event.metadata else ""
        # Escape quotes: " becomes ""
        escaped_text = text.replace('"', '""')
        return f'{track}, {time}, {event_name}, "{escaped_text}"'

    if event_type_name == "text":
        # Generic text event
        text = event.metadata.get("text", "") if event.metadata else ""
        escaped_text = text.replace('"', '""')
        return f'{track}, {time}, {event_name}, "{escaped_text}"'

    if event_type_name == "sysex":
        # System exclusive: length, data bytes
        if event.metadata and "bytes" in event.metadata:
            data_bytes = event.metadata["bytes"]
            length = len(data_bytes)
            # Format: Track, Time, System_exclusive, Length, byte1, byte2, ...
            bytes_str = ", ".join(str(b) for b in data_bytes)
            return f"{track}, {time}, {event_name}, {length}, {bytes_str}"
        return ""  # Skip if no data

    # System common messages
    if event_type_name in {"mtc_quarter_frame", "song_position", "song_select"}:
        return f"{track}, {time}, {event_name}, {event.data1}"

    # Unknown event type - skip
    return ""


def _event_type_to_midicsv_name(event_type: EventType) -> str:
    """Map EventType enum to midicsv event name.

    Args:
        event_type: EventType enum value

    Returns:
        midicsv event name, or empty string if unsupported

    Note:
        Channel events get "_c" suffix (e.g., "Note_on_c")
        Meta events use simple names (e.g., "Tempo")
    """
    from midi_markdown.core.ir import EventType

    # Channel voice messages (all get "_c" suffix)
    channel_events = {
        EventType.NOTE_ON: "Note_on_c",
        EventType.NOTE_OFF: "Note_off_c",
        EventType.CONTROL_CHANGE: "Control_c",
        EventType.PROGRAM_CHANGE: "Program_c",
        EventType.PITCH_BEND: "Pitch_bend_c",
        EventType.CHANNEL_PRESSURE: "Channel_aftertouch_c",
        EventType.POLY_PRESSURE: "Poly_aftertouch_c",
    }

    # Meta events (no suffix)
    meta_events = {
        EventType.TEMPO: "Tempo",
        EventType.TIME_SIGNATURE: "Time_signature",
        EventType.KEY_SIGNATURE: "Key_signature",
        EventType.MARKER: "Marker",
        EventType.TEXT: "Text",
    }

    # System common messages
    system_events = {
        EventType.SYSEX: "System_exclusive",
        EventType.MTC_QUARTER_FRAME: "MIDI_time_code",
        EventType.SONG_POSITION: "Song_position",
        EventType.SONG_SELECT: "Song_select",
    }

    # Check each mapping
    if event_type in channel_events:
        return channel_events[event_type]
    if event_type in meta_events:
        return meta_events[event_type]
    if event_type in system_events:
        return system_events[event_type]
    return ""  # Unsupported event type
