"""Intermediate Representation (IR) data structures.

The IR layer sits between the AST and output formats, enabling:
- REPL: Interactive evaluation and inspection
- Live playback: Real-time MIDI output
- Diagnostics: Timing analysis, event queries
- Multiple outputs: MIDI files, JSON, CSV, etc.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any


class EventType(Enum):
    """MIDI event types for Intermediate Representation.

    This enum covers all MIDI event types supported by MML:
    - Channel Voice Messages (NOTE_ON, NOTE_OFF, CC, PC, etc.)
    - System Common Messages (SYSEX, MTC, Song Position/Select)
    - Meta Events for MIDI files (TEMPO, TIME_SIGNATURE, MARKER, TEXT)

    See Also:
        - MIDI 1.0 Specification: https://www.midi.org/specifications
        - Standard MIDI Files Specification (SMF)
    """

    # Channel Voice Messages
    NOTE_ON = auto()
    NOTE_OFF = auto()
    CONTROL_CHANGE = auto()
    PROGRAM_CHANGE = auto()
    PITCH_BEND = auto()
    CHANNEL_PRESSURE = auto()
    POLY_PRESSURE = auto()

    # System Common Messages
    SYSEX = auto()
    MTC_QUARTER_FRAME = auto()
    SONG_POSITION = auto()
    SONG_SELECT = auto()

    # Meta Events (for MIDI files)
    TEMPO = auto()
    TIME_SIGNATURE = auto()
    KEY_SIGNATURE = auto()
    MARKER = auto()
    TEXT = auto()


@dataclass
class MIDIEvent:
    """Represents a single MIDI event in the Intermediate Representation.

    The MIDIEvent is the core data structure in the IR layer, representing
    a single MIDI message with absolute timing. Events are created during
    compilation from AST and can be queried, filtered, and converted to
    various output formats.

    Attributes:
        time: Absolute time in ticks (PPQ-based, e.g., 480 ticks = 1 quarter note at PPQ=480)
        type: Event type from EventType enum (NOTE_ON, CC, TEMPO, etc.)
        channel: MIDI channel (1-16, or 0 for meta events with no channel)
        data1: First data byte (note number for notes, CC number for CC, etc.)
        data2: Second data byte (velocity for notes, CC value for CC, etc.)
        time_seconds: Absolute time in seconds (computed from tempo map during IR creation)
        metadata: Optional metadata dict with source location, track name, etc.

    Example:
        >>> # Create a Note On event at 1 second (480 ticks at 120 BPM, PPQ=480)
        >>> event = MIDIEvent(
        ...     time=480,
        ...     type=EventType.NOTE_ON,
        ...     channel=1,
        ...     data1=60,  # Middle C
        ...     data2=80,  # Velocity
        ...     time_seconds=1.0,
        ...     metadata={"source_line": 10, "track": "Main"}
        ... )
        >>> print(f"Note {event.data1} at {event.time_seconds}s")
        Note 60 at 1.0s

    See Also:
        - IRProgram: Container for collections of MIDIEvent objects
        - string_to_event_type: Convert string types to EventType enum
    """

    time: int
    type: EventType
    channel: int
    data1: int = 0
    data2: int = 0
    time_seconds: float | None = None
    metadata: dict[str, Any] | None = None


def string_to_event_type(type_str: str) -> EventType:
    """Convert string type to EventType enum.

    Args:
        type_str: String type from CommandExpander (e.g., 'tempo', 'cc', 'note_on')

    Returns:
        Corresponding EventType enum value

    Raises:
        ValueError: If type_str is not a recognized event type
    """
    # Map string types to EventType enums
    type_map = {
        "note_on": EventType.NOTE_ON,
        "note_off": EventType.NOTE_OFF,
        "program_change": EventType.PROGRAM_CHANGE,
        "pc": EventType.PROGRAM_CHANGE,
        "control_change": EventType.CONTROL_CHANGE,
        "cc": EventType.CONTROL_CHANGE,
        "pitch_bend": EventType.PITCH_BEND,
        "pb": EventType.PITCH_BEND,
        "channel_pressure": EventType.CHANNEL_PRESSURE,
        "cp": EventType.CHANNEL_PRESSURE,
        "poly_pressure": EventType.POLY_PRESSURE,
        "pp": EventType.POLY_PRESSURE,
        "sysex": EventType.SYSEX,
        "tempo": EventType.TEMPO,
        "time_signature": EventType.TIME_SIGNATURE,
        "key_signature": EventType.KEY_SIGNATURE,
        "marker": EventType.MARKER,
        "text": EventType.TEXT,
        "mtc_quarter_frame": EventType.MTC_QUARTER_FRAME,
        "song_position": EventType.SONG_POSITION,
        "song_select": EventType.SONG_SELECT,
    }

    event_type = type_map.get(type_str)
    if event_type is None:
        msg = f"Unknown event type: {type_str}"
        raise ValueError(msg)
    return event_type


def create_ir_program(
    events: list[MIDIEvent],
    ppq: int,
    initial_tempo: int,
    frontmatter: dict[str, Any] | None = None,
) -> IRProgram:
    """Create IR program from events and metadata.

    This helper function wraps events in an IRProgram structure and computes
    time_seconds for all events using the tempo map.

    Args:
        events: List of MIDI events (will be sorted by time)
        ppq: Pulses per quarter note
        initial_tempo: Starting tempo in BPM
        frontmatter: Document frontmatter metadata

    Returns:
        IRProgram with computed time_seconds
    """
    # Sort events by time
    events.sort(key=lambda e: e.time)

    # Build tempo map and compute time_seconds
    tempo_map: list[tuple[int, int]] = [(0, initial_tempo)]

    for event in events:
        if event.type == EventType.TEMPO and event.data1:
            tempo_map.append((event.time, event.data1))

    tempo_map.sort(key=lambda x: x[0])

    # Compute time_seconds for each event
    for event in events:
        event.time_seconds = _ticks_to_seconds_standalone(event.time, tempo_map, ppq)

    # Create metadata dict
    metadata = {
        "title": frontmatter.get("title", "Untitled") if frontmatter else "Untitled",
        "author": frontmatter.get("author", "") if frontmatter else "",
        "description": frontmatter.get("description", "") if frontmatter else "",
        "version": frontmatter.get("version", "1.0") if frontmatter else "1.0",
    }

    return IRProgram(
        resolution=ppq,
        initial_tempo=initial_tempo,
        events=events,
        metadata=metadata,
    )


def _ticks_to_seconds_standalone(ticks: int, tempo_map: list[tuple[int, int]], ppq: int) -> float:
    """Convert tick position to seconds using tempo map.

    Standalone version for use outside EventGenerator.

    Args:
        ticks: Absolute tick position
        tempo_map: List of (tick, bpm) tuples
        ppq: Pulses per quarter note

    Returns:
        Time in seconds
    """
    seconds = 0.0
    prev_tick = 0
    prev_tempo = tempo_map[0][1]

    for tempo_tick, tempo_bpm in tempo_map:
        if tempo_tick > ticks:
            break

        # Add time for segment at previous tempo
        if tempo_tick > prev_tick:
            tick_delta = tempo_tick - prev_tick
            seconds += (tick_delta / ppq) * (60.0 / prev_tempo)

        prev_tick = tempo_tick
        prev_tempo = tempo_bpm

    # Add remaining time at final tempo
    if ticks > prev_tick:
        tick_delta = ticks - prev_tick
        seconds += (tick_delta / ppq) * (60.0 / prev_tempo)

    return seconds


@dataclass
class IRProgram:
    """Intermediate representation of a compiled MML program.

    The IRProgram is the central data structure after compilation, containing
    all MIDI events with computed timing. It sits between the AST (syntactic
    representation) and output formats (MIDI files, JSON, live playback).

    This IR layer enables:
    - Query operations (events by time, type, channel)
    - Multiple output formats from single compilation
    - REPL with interactive inspection
    - Live playback with real-time scheduling
    - Diagnostic analysis (timing, event counts, duration)

    Attributes:
        resolution: PPQ (Pulses Per Quarter note), typically 480 or 960
        initial_tempo: Starting tempo in BPM (before any tempo changes)
        events: Sorted list of MIDIEvent objects (sorted by time)
        metadata: Dictionary with document metadata (title, author, etc.)

    Example:
        >>> from midi_markdown.parser.parser import MMDParser
        >>> from midi_markdown.core.compiler import compile_ast_to_ir
        >>> parser = MMDParser()
        >>> doc = parser.parse_file("examples/00_basics/00_hello_world.mmd")
        >>> ir = compile_ast_to_ir(doc, ppq=480)
        >>> print(f"Duration: {ir.duration_seconds:.2f}s")
        Duration: 2.00s
        >>> print(f"Events: {ir.event_count}")
        Events: 4
        >>> # Query events by type
        >>> notes = ir.events_by_type(EventType.NOTE_ON)
        >>> print(f"Note events: {len(notes)}")
        Note events: 2

    See Also:
        - compile_ast_to_ir: Main compilation function
        - create_ir_program: Helper for creating IR from events
        - MIDIEvent: Individual event structure
    """

    resolution: int
    initial_tempo: int
    events: list[MIDIEvent]
    metadata: dict[str, Any]

    @property
    def duration_ticks(self) -> int:
        """Total duration in ticks."""
        return max((e.time for e in self.events), default=0)

    @property
    def duration_seconds(self) -> float:
        """Total duration in seconds."""
        return max((e.time_seconds for e in self.events if e.time_seconds), default=0.0)

    @property
    def track_count(self) -> int:
        """Number of unique tracks."""
        tracks = {e.metadata.get("track", 0) for e in self.events if e.metadata}
        return len(tracks) if tracks else 1

    @property
    def event_count(self) -> int:
        """Total number of events."""
        return len(self.events)

    def events_at_time(self, seconds: float, tolerance: float = 0.01) -> list[MIDIEvent]:
        """Get events at specific time (within tolerance).

        Args:
            seconds: Time in seconds
            tolerance: Time window in seconds (default 10ms)

        Returns:
            List of events within time window
        """
        return [
            e
            for e in self.events
            if e.time_seconds is not None and abs(e.time_seconds - seconds) <= tolerance
        ]

    def events_in_range(self, start: float, end: float) -> list[MIDIEvent]:
        """Get events in time range.

        Args:
            start: Start time in seconds
            end: End time in seconds

        Returns:
            List of events in range [start, end]
        """
        return [
            e for e in self.events if e.time_seconds is not None and start <= e.time_seconds <= end
        ]

    def events_by_type(self, event_type: EventType) -> list[MIDIEvent]:
        """Get all events of specific type."""
        return [e for e in self.events if e.type == event_type]

    def events_by_channel(self, channel: int) -> list[MIDIEvent]:
        """Get all events on specific channel."""
        return [e for e in self.events if e.channel == channel]
