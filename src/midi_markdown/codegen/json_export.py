"""JSON export for MIDI events in complete and simplified formats.

This module exports IRProgram data to JSON in two formats:
- Complete: Full MIDI data with exact timing (for programmatic use)
- Simplified: Human-readable format with note names and readable times (for analysis)
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from midi_markdown.core.ir import IRProgram


def export_to_json(
    ir_program: IRProgram,
    format: str = "complete",
    pretty: bool = True,
) -> str:
    """Export IRProgram to JSON format.

    Args:
        ir_program: Compiled IR program to export
        format: "complete" (full MIDI data) or "simplified" (human-readable)
        pretty: Pretty-print with indentation (default: True)

    Returns:
        JSON string

    Example:
        >>> from midi_markdown.core import compile_ast_to_ir
        >>> from midi_markdown.parser.parser import MMDParser
        >>> parser = MMDParser()
        >>> doc = parser.parse_file("song.mmd")
        >>> ir = compile_ast_to_ir(doc)
        >>> json_complete = export_to_json(ir, format="complete")
        >>> json_simple = export_to_json(ir, format="simplified")
    """
    if format == "simplified":
        data = _build_simplified_format(ir_program)
    else:  # default to complete
        data = _build_complete_format(ir_program)

    # Serialize to JSON
    if pretty:
        return json.dumps(data, indent=2, ensure_ascii=False)
    return json.dumps(data, ensure_ascii=False)


def _build_complete_format(ir_program: IRProgram) -> dict[str, Any]:
    """Build complete JSON format with full MIDI data.

    Args:
        ir_program: IR program to export

    Returns:
        Dictionary ready for JSON serialization
    """
    metadata = _build_metadata(ir_program)

    # Convert events to complete format
    events = []
    for event in ir_program.events:
        event_dict = {
            "time": event.time,
            "time_seconds": event.time_seconds,
            "type": event.type.name.lower(),
            "channel": event.channel if event.channel != 0 else None,  # 0 = no channel
            "data1": event.data1 if event.data1 is not None else None,
            "data2": event.data2 if event.data2 is not None else None,
        }

        # Include metadata if present
        if event.metadata:
            event_dict["metadata"] = event.metadata

        events.append(event_dict)

    return {
        "metadata": metadata,
        "events": events,
    }


def _build_simplified_format(ir_program: IRProgram) -> dict[str, Any]:
    """Build simplified JSON format with human-readable data.

    Args:
        ir_program: IR program to export

    Returns:
        Dictionary ready for JSON serialization
    """
    metadata = _build_metadata(ir_program)

    # Convert events to simplified format
    events = []
    for event in ir_program.events:
        event_type = event.type.name.lower()

        # Base event with readable times
        base_dict = {
            "time": f"{event.time_seconds:.3f}s" if event.time_seconds else "0.000s",
            "musical_time": _format_musical_time(event.time, ir_program.resolution),
        }

        # Add channel if present
        if event.channel is not None and event.channel != 0:
            base_dict["channel"] = event.channel

        # Format event based on type
        if event_type == "note_on":
            event_dict = {
                **base_dict,
                "type": "note_on",
                "note": _note_number_to_name(event.data1),
                "note_number": event.data1,
                "velocity": event.data2,
            }

        elif event_type == "note_off":
            event_dict = {
                **base_dict,
                "type": "note_off",
                "note": _note_number_to_name(event.data1),
                "note_number": event.data1,
                "velocity": event.data2,
            }

        elif event_type == "control_change":
            event_dict = {
                **base_dict,
                "type": "control_change",
                "controller": _get_cc_name(event.data1),
                "controller_number": event.data1,
                "value": event.data2,
            }

        elif event_type == "program_change":
            event_dict = {
                **base_dict,
                "type": "program_change",
                "program": event.data1,
            }

        elif event_type == "pitch_bend":
            # Convert to signed value (-8192 to +8191)
            bend_value = event.data1 - 8192
            event_dict = {
                **base_dict,
                "type": "pitch_bend",
                "value": bend_value,
            }

        elif event_type == "channel_pressure":
            event_dict = {
                **base_dict,
                "type": "channel_pressure",
                "pressure": event.data1,
            }

        elif event_type == "poly_pressure":
            event_dict = {
                **base_dict,
                "type": "poly_pressure",
                "note": _note_number_to_name(event.data1),
                "note_number": event.data1,
                "pressure": event.data2,
            }

        elif event_type == "tempo":
            event_dict = {
                "time": base_dict["time"],
                "musical_time": base_dict["musical_time"],
                "type": "tempo",
                "bpm": event.data1,
            }

        elif event_type == "time_signature":
            # Get from metadata or use defaults
            if event.metadata and "numerator" in event.metadata:
                numerator = event.metadata.get("numerator")
                denom_power = event.metadata.get("denominator", 2)
            else:
                numerator = 4
                denom_power = 2

            event_dict = {
                "time": base_dict["time"],
                "musical_time": base_dict["musical_time"],
                "type": "time_signature",
                "numerator": numerator,
                "denominator": 2**denom_power,
            }

        elif event_type == "key_signature":
            # Extract key signature info
            sharps_flats = event.data1 if event.data1 is not None else 0
            mode = "minor" if event.data2 == 1 else "major"
            event_dict = {
                "time": base_dict["time"],
                "musical_time": base_dict["musical_time"],
                "type": "key_signature",
                "sharps_flats": sharps_flats,
                "mode": mode,
            }

        elif event_type == "marker":
            text = event.metadata.get("text", "") if event.metadata else ""
            event_dict = {
                "time": base_dict["time"],
                "musical_time": base_dict["musical_time"],
                "type": "marker",
                "text": text,
            }

        elif event_type == "text":
            text = event.metadata.get("text", "") if event.metadata else ""
            event_dict = {
                "time": base_dict["time"],
                "musical_time": base_dict["musical_time"],
                "type": "text",
                "text": text,
            }

        else:
            # Generic format for other event types
            event_dict = {
                **base_dict,
                "type": event_type,
            }
            if event.data1 is not None:
                event_dict["data1"] = event.data1
            if event.data2 is not None:
                event_dict["data2"] = event.data2

        events.append(event_dict)

    return {
        "metadata": metadata,
        "events": events,
    }


def _build_metadata(ir_program: IRProgram) -> dict[str, Any]:
    """Build metadata dictionary from IR program.

    Args:
        ir_program: IR program

    Returns:
        Metadata dictionary
    """
    metadata = {
        "title": ir_program.metadata.get("title", "Untitled"),
        "duration_ticks": ir_program.duration_ticks,
        "duration_seconds": round(ir_program.duration_seconds, 3),
        "resolution": ir_program.resolution,
        "initial_tempo": ir_program.initial_tempo,
        "event_count": ir_program.event_count,
        "track_count": ir_program.track_count,
    }

    # Add optional metadata fields if present
    if ir_program.metadata.get("author"):
        metadata["author"] = ir_program.metadata["author"]

    if ir_program.metadata.get("description"):
        metadata["description"] = ir_program.metadata["description"]

    if "version" in ir_program.metadata:
        metadata["version"] = ir_program.metadata["version"]

    return metadata


def _format_musical_time(tick: int, ppq: int) -> str:
    """Format tick position as bars.beats.ticks.

    Assumes 4/4 time signature.

    Args:
        tick: Absolute tick position
        ppq: Pulses per quarter note

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
        CC name if known, otherwise "CC{number}"
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

    return cc_names.get(cc_number, f"CC{cc_number}")
