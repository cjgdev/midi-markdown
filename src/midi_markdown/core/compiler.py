"""AST to IR compilation.

Converts parsed AST (from parser) into executable IR (intermediate representation).
The IR can then be sent to various outputs: MIDI files, JSON, live playback, REPL.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .ir import EventType, IRProgram, MIDIEvent, create_ir_program, string_to_event_type

if TYPE_CHECKING:
    from ..parser.ast_nodes import MMLDocument


def compile_ast_to_ir(
    document: MMLDocument,
    ppq: int = 480,
) -> IRProgram:
    """Compile MML document AST to IR program.

    This is the main entry point for compilation. It orchestrates:
    1. Event generation from AST commands
    2. Timing resolution (absolute, musical, relative)
    3. Expansion (loops, sweeps, variables)
    4. Validation (ranges, monotonicity)
    5. Time computation (ticks → seconds using tempo map)

    Args:
        document: Parsed MML document AST
        ppq: Pulses per quarter note (MIDI resolution)

    Returns:
        IRProgram ready for output or execution

    Example:
        >>> from midi_markdown.parser.parser import MMLParser
        >>> from midi_markdown.core import compile_ast_to_ir
        >>> parser = MMLParser()
        >>> doc = parser.parse_file("song.mml")
        >>> ir = compile_ast_to_ir(doc, ppq=480)
        >>> print(f"Duration: {ir.duration_seconds}s, Events: {ir.event_count}")
    """
    # Import here to avoid circular dependency
    from ..expansion.expander import CommandExpander

    # Get tempo and time signature from frontmatter
    tempo = document.frontmatter.get("tempo", 120)
    time_signature = document.frontmatter.get("time_signature", (4, 4))

    # Expand AST to event dictionaries
    expander = CommandExpander(ppq=ppq, tempo=tempo, time_signature=time_signature)
    expanded_dicts = expander.process_ast(document.events)

    # Convert event dicts to MIDIEvent objects
    events = []
    for event_dict in expanded_dicts:
        # Skip meta events that are handled specially or not in EventType enum
        # - end_of_track: automatically added by MIDI file writer
        # - trackname/instrumentname: handled separately by MIDI file writer
        event_type = event_dict["type"]
        if event_type in ("end_of_track", "trackname", "instrumentname"):
            continue

        midi_event = MIDIEvent(
            time=event_dict["time"],
            type=string_to_event_type(event_type),
            channel=event_dict.get("channel", 0),
            data1=event_dict.get("data1", 0),
            data2=event_dict.get("data2", 0),
            metadata=event_dict.get("metadata"),
        )
        events.append(midi_event)

    # Wrap in IRProgram (computes time_seconds)
    return create_ir_program(
        events=events,
        ppq=ppq,
        initial_tempo=tempo,
        frontmatter=document.frontmatter,
    )
