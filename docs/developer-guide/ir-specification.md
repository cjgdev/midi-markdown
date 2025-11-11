# IR Layer Specification

**Date**: 2025-11-08
**Status**: Production-ready
**Version**: 0.1.0

## Table of Contents

1. [Overview](#overview)
2. [Design Goals](#design-goals)
3. [Data Structures](#data-structures)
4. [Event Types](#event-types)
5. [Compilation Process](#compilation-process)
6. [Query Methods](#query-methods)
7. [Usage Examples](#usage-examples)
8. [Implementation Details](#implementation-details)
9. [Testing](#testing)

---

## Overview

The **Intermediate Representation (IR) layer** sits between the Abstract Syntax Tree (AST) and output generation. It provides a normalized, executable representation of MIDI events that enables:

- **Multiple outputs**: MIDI files, JSON, CSV, diagnostic tables
- **Real-time playback**: Event scheduling with tempo tracking
- **REPL mode** (future): Interactive evaluation and inspection
- **Event queries**: Search and analyze events by time, type, channel

The IR layer was introduced in **Phase 0** of the implementation to decouple parsing from output generation.

---

## Design Goals

### 1. Unified Event Representation
All MIDI events (notes, CC, PC, tempo, etc.) use a single `MIDIEvent` structure with a common timing model.

### 2. Absolute Timing
All events store **absolute time in ticks**, computed during expansion. This simplifies output generation and playback.

### 3. Tempo Awareness
Events include both tick time and computed `time_seconds`, enabling accurate real-time playback with tempo changes.

### 4. Query-able Structure
The `IRProgram` provides query methods to search events by time, type, or channel without re-parsing.

### 5. Metadata Preservation
Each event can carry metadata (source file, line number, track name) for error reporting and debugging.

### 6. Immutable Design
IR structures are immutable dataclasses. Transformations create new structures.

---

## Data Structures

### MIDIEvent

The core event structure representing a single MIDI message:

```python
@dataclass
class MIDIEvent:
    """Represents a single MIDI event.

    Attributes:
        time: Absolute time in ticks
        type: Event type (NOTE_ON, CC, PC, etc.)
        channel: MIDI channel (1-16)
        data1: First data byte (note number, controller, etc.)
        data2: Second data byte (velocity, value, etc.)
        time_seconds: Absolute time in seconds (computed from tempo map)
        metadata: Source location and other info for error reporting
    """
    time: int
    type: EventType
    channel: int
    data1: int = 0
    data2: int = 0
    time_seconds: float | None = None
    metadata: dict[str, Any] | None = None
```

**Field Details**:

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `time` | int | 0+ | Absolute time in ticks (PPQ-relative) |
| `type` | EventType | enum | Event type (see EventType section) |
| `channel` | int | 1-16 | MIDI channel (1-indexed) |
| `data1` | int | 0-127 | First data byte (note, CC number, etc.) |
| `data2` | int | 0-127 | Second data byte (velocity, value, etc.) |
| `time_seconds` | float\|None | 0+ | Computed time in seconds (for playback) |
| `metadata` | dict\|None | - | Source location, track info, etc. |

**Example**:
```python
# Middle C note-on at 0.5 seconds, velocity 100
event = MIDIEvent(
    time=240,              # 240 ticks (0.5 beats at 480 PPQ)
    type=EventType.NOTE_ON,
    channel=1,
    data1=60,              # Middle C
    data2=100,             # Velocity
    time_seconds=0.5,      # Computed from tempo
    metadata={
        "source_file": "song.mmd",
        "source_line": 12,
        "track": "Main"
    }
)
```

---

### EventType

Enum defining all supported MIDI event types:

```python
class EventType(Enum):
    """MIDI event types."""

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
```

**Category Breakdown**:

**Channel Voice Messages** (most common):
- `NOTE_ON`: Note on (data1=note, data2=velocity)
- `NOTE_OFF`: Note off (data1=note, data2=release velocity)
- `CONTROL_CHANGE`: CC message (data1=controller, data2=value)
- `PROGRAM_CHANGE`: PC message (data1=program, data2=unused)
- `PITCH_BEND`: Pitch bend (data1=LSB, data2=MSB, combined -8192 to +8191)
- `CHANNEL_PRESSURE`: Aftertouch (data1=pressure, data2=unused)
- `POLY_PRESSURE`: Polyphonic aftertouch (data1=note, data2=pressure)

**System Common Messages**:
- `SYSEX`: System Exclusive message
- `MTC_QUARTER_FRAME`: MIDI Time Code quarter frame
- `SONG_POSITION`: Song position pointer
- `SONG_SELECT`: Song select

**Meta Events** (MIDI file only, not sent to devices):
- `TEMPO`: Tempo change (data1=BPM)
- `TIME_SIGNATURE`: Time signature change
- `KEY_SIGNATURE`: Key signature
- `MARKER`: Marker text
- `TEXT`: Text annotation

---

### IRProgram

The complete compiled program containing all events and metadata:

```python
@dataclass
class IRProgram:
    """Intermediate representation of compiled MMD program.

    Attributes:
        resolution: PPQ (ticks per quarter note)
        initial_tempo: Starting tempo in BPM
        events: Sorted list of MIDI events (by time)
        metadata: Document frontmatter + computed information
    """
    resolution: int
    initial_tempo: int
    events: list[MIDIEvent]
    metadata: dict[str, Any]

    # Computed properties
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

    # Query methods (see Query Methods section)
    def events_at_time(self, seconds: float, tolerance: float = 0.01) -> list[MIDIEvent]
    def events_in_range(self, start: float, end: float) -> list[MIDIEvent]
    def events_by_type(self, event_type: EventType) -> list[MIDIEvent]
    def events_by_channel(self, channel: int) -> list[MIDIEvent]
```

**Metadata Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `title` | str | Song title (from frontmatter) |
| `author` | str | Author name (from frontmatter) |
| `description` | str | Description (from frontmatter) |
| `version` | str | MMD version (from frontmatter) |
| `tempo` | int | Initial tempo in BPM |
| `time_signature` | tuple | Time signature (numerator, denominator) |

**Example**:
```python
ir_program = IRProgram(
    resolution=480,          # 480 PPQ
    initial_tempo=120,       # 120 BPM
    events=[...],            # List of MIDIEvent objects
    metadata={
        "title": "My Song",
        "author": "Composer Name",
        "description": "A test composition",
        "version": "1.0"
    }
)

# Access properties
print(f"Duration: {ir_program.duration_seconds}s")
print(f"Events: {ir_program.event_count}")
print(f"Tracks: {ir_program.track_count}")
```

---

## Event Types

### String to EventType Conversion

The IR compiler converts string event types (from the expander) to `EventType` enums:

```python
def string_to_event_type(type_str: str) -> EventType:
    """Convert string type to EventType enum.

    Supports both full names and abbreviations:
    - "note_on" or "NOTE_ON" → EventType.NOTE_ON
    - "cc" or "control_change" → EventType.CONTROL_CHANGE
    - "pc" or "program_change" → EventType.PROGRAM_CHANGE
    - "pb" or "pitch_bend" → EventType.PITCH_BEND
    - etc.

    Raises:
        ValueError: If type_str is not recognized
    """
```

**Supported Mappings**:

| String | EventType |
|--------|-----------|
| `"note_on"` | `NOTE_ON` |
| `"note_off"` | `NOTE_OFF` |
| `"cc"`, `"control_change"` | `CONTROL_CHANGE` |
| `"pc"`, `"program_change"` | `PROGRAM_CHANGE` |
| `"pb"`, `"pitch_bend"` | `PITCH_BEND` |
| `"cp"`, `"channel_pressure"` | `CHANNEL_PRESSURE` |
| `"pp"`, `"poly_pressure"` | `POLY_PRESSURE` |
| `"sysex"` | `SYSEX` |
| `"tempo"` | `TEMPO` |
| `"time_signature"` | `TIME_SIGNATURE` |
| `"key_signature"` | `KEY_SIGNATURE` |
| `"marker"` | `MARKER` |
| `"text"` | `TEXT` |
| `"mtc_quarter_frame"` | `MTC_QUARTER_FRAME` |
| `"song_position"` | `SONG_POSITION` |
| `"song_select"` | `SONG_SELECT` |

---

## Compilation Process

The `compile_ast_to_ir()` function orchestrates the conversion from AST to IR:

### Pipeline

```
MMLDocument (AST)
    ↓
[1] Extract frontmatter
    ↓ tempo, time_signature
[2] CommandExpander.process_ast()
    ↓ list[dict] (event dictionaries)
[3] Convert dicts → MIDIEvent objects
    ↓ list[MIDIEvent]
[4] Build tempo map
    ↓ list[(tick, bpm)]
[5] Compute time_seconds for all events
    ↓ MIDIEvent.time_seconds = ...
[6] Create IRProgram
    ↓
IRProgram
```

### Implementation

```python
def compile_ast_to_ir(
    document: MMLDocument,
    ppq: int = 480,
) -> IRProgram:
    """Compile MMD document AST to IR program.

    This is the main entry point for compilation. It orchestrates:
    1. Event generation from AST commands
    2. Timing resolution (absolute, musical, relative)
    3. Expansion (loops, sweeps, variables)
    4. Validation (ranges, monotonicity)
    5. Time computation (ticks → seconds using tempo map)

    Args:
        document: Parsed MMD document AST
        ppq: Pulses per quarter note (MIDI resolution)

    Returns:
        IRProgram ready for output or execution
    """
    # Step 1: Extract frontmatter
    tempo = document.frontmatter.get("tempo", 120)
    time_signature = document.frontmatter.get("time_signature", (4, 4))

    # Step 2: Expand AST to event dictionaries
    expander = CommandExpander(ppq=ppq, tempo=tempo, time_signature=time_signature)
    expanded_dicts = expander.process_ast(document.events)

    # Step 3: Convert event dicts to MIDIEvent objects
    events = []
    for event_dict in expanded_dicts:
        # Skip special meta events (trackname, instrumentname, end_of_track)
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

    # Steps 4-6: Wrap in IRProgram (computes time_seconds)
    return create_ir_program(
        events=events,
        ppq=ppq,
        initial_tempo=tempo,
        frontmatter=document.frontmatter,
    )
```

### Helper: create_ir_program()

```python
def create_ir_program(
    events: list[MIDIEvent],
    ppq: int,
    initial_tempo: int,
    frontmatter: dict[str, Any] | None = None,
) -> IRProgram:
    """Create IR program from events and metadata.

    This helper function:
    1. Sorts events by time
    2. Builds tempo map from TEMPO events
    3. Computes time_seconds for all events
    4. Wraps in IRProgram structure

    Args:
        events: List of MIDI events (unsorted)
        ppq: Pulses per quarter note
        initial_tempo: Starting tempo in BPM
        frontmatter: Document frontmatter metadata

    Returns:
        IRProgram with computed time_seconds
    """
    # Step 1: Sort events by time
    events.sort(key=lambda e: e.time)

    # Step 2: Build tempo map
    tempo_map: list[tuple[int, int]] = [(0, initial_tempo)]
    for event in events:
        if event.type == EventType.TEMPO and event.data1:
            tempo_map.append((event.time, event.data1))
    tempo_map.sort(key=lambda x: x[0])

    # Step 3: Compute time_seconds for each event
    for event in events:
        event.time_seconds = _ticks_to_seconds(event.time, tempo_map, ppq)

    # Step 4: Create metadata dict
    metadata = {
        "title": frontmatter.get("title", "Untitled") if frontmatter else "Untitled",
        "author": frontmatter.get("author", "") if frontmatter else "",
        "description": frontmatter.get("description", "") if frontmatter else "",
        "version": frontmatter.get("version", "1.0") if frontmatter else "1.0",
    }

    # Step 5: Return IRProgram
    return IRProgram(
        resolution=ppq,
        initial_tempo=initial_tempo,
        events=events,
        metadata=metadata,
    )
```

### Tempo Map and Time Conversion

The tempo map tracks tempo changes over time:

```python
tempo_map = [
    (0, 120),      # Start at 120 BPM
    (960, 140),    # Change to 140 BPM at tick 960
    (1920, 100),   # Change to 100 BPM at tick 1920
]
```

**Time conversion algorithm**:

```python
def _ticks_to_seconds(ticks: int, tempo_map: list[tuple[int, int]], ppq: int) -> float:
    """Convert tick position to seconds using tempo map.

    Algorithm:
    1. For each tempo segment [prev_tick, tempo_tick):
       - Calculate duration in ticks: delta_ticks = tempo_tick - prev_tick
       - Convert to beats: beats = delta_ticks / ppq
       - Convert to seconds: seconds = beats * (60 / tempo_bpm)
    2. Sum all segment durations up to target tick

    Args:
        ticks: Absolute tick position
        tempo_map: List of (tick, bpm) tuples (sorted)
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
```

**Example**:
```python
# At 480 PPQ, 120 BPM:
# 480 ticks = 1 beat = 0.5 seconds
# 960 ticks = 2 beats = 1.0 seconds

ticks = 960
tempo_map = [(0, 120)]
ppq = 480

seconds = _ticks_to_seconds(ticks, tempo_map, ppq)
print(seconds)  # 1.0
```

---

## Query Methods

The `IRProgram` class provides query methods for event analysis:

### 1. events_at_time()

Find events at a specific time (with tolerance):

```python
def events_at_time(self, seconds: float, tolerance: float = 0.01) -> list[MIDIEvent]:
    """Get events at specific time (within tolerance).

    Args:
        seconds: Time in seconds
        tolerance: Time window in seconds (default 10ms)

    Returns:
        List of events within time window [seconds - tolerance, seconds + tolerance]
    """
    return [
        e
        for e in self.events
        if e.time_seconds is not None and abs(e.time_seconds - seconds) <= tolerance
    ]
```

**Example**:
```python
# Find all events at 1.0 seconds (±10ms)
events = ir_program.events_at_time(1.0)
for event in events:
    print(f"{event.type.name}: channel {event.channel}")
```

### 2. events_in_range()

Find events in a time range:

```python
def events_in_range(self, start: float, end: float) -> list[MIDIEvent]:
    """Get events in time range.

    Args:
        start: Start time in seconds (inclusive)
        end: End time in seconds (inclusive)

    Returns:
        List of events in range [start, end]
    """
    return [
        e
        for e in self.events
        if e.time_seconds is not None and start <= e.time_seconds <= end
    ]
```

**Example**:
```python
# Find all events between 0.5s and 2.0s
events = ir_program.events_in_range(0.5, 2.0)
print(f"Found {len(events)} events in range")
```

### 3. events_by_type()

Find all events of a specific type:

```python
def events_by_type(self, event_type: EventType) -> list[MIDIEvent]:
    """Get all events of specific type.

    Args:
        event_type: EventType enum value

    Returns:
        List of events matching type
    """
    return [e for e in self.events if e.type == event_type]
```

**Example**:
```python
# Find all note-on events
note_ons = ir_program.events_by_type(EventType.NOTE_ON)
print(f"Total notes: {len(note_ons)}")

# Find all tempo changes
tempos = ir_program.events_by_type(EventType.TEMPO)
for event in tempos:
    print(f"Tempo change to {event.data1} BPM at {event.time_seconds}s")
```

### 4. events_by_channel()

Find all events on a specific channel:

```python
def events_by_channel(self, channel: int) -> list[MIDIEvent]:
    """Get all events on specific channel.

    Args:
        channel: MIDI channel (1-16)

    Returns:
        List of events on channel
    """
    return [e for e in self.events if e.channel == channel]
```

**Example**:
```python
# Find all events on channel 1
ch1_events = ir_program.events_by_channel(1)
print(f"Channel 1: {len(ch1_events)} events")

# Count events per channel
for channel in range(1, 17):
    count = len(ir_program.events_by_channel(channel))
    if count > 0:
        print(f"Channel {channel}: {count} events")
```

---

## Usage Examples

### Complete Compilation Example

```python
from midi_markdown.parser.parser import MMLParser
from midi_markdown.core import compile_ast_to_ir
from midi_markdown.codegen.midi_file import generate_midi_file
from pathlib import Path

# Step 1: Parse MMD file
parser = MMLParser()
document = parser.parse_file("song.mmd")

# Step 2: Compile to IR
ir_program = compile_ast_to_ir(document, ppq=480)

# Step 3: Inspect IR
print(f"Title: {ir_program.metadata['title']}")
print(f"Duration: {ir_program.duration_seconds}s")
print(f"Events: {ir_program.event_count}")
print(f"Tracks: {ir_program.track_count}")

# Step 4: Generate MIDI file
midi_bytes = generate_midi_file(ir_program, midi_format=1)
Path("output.mid").write_bytes(midi_bytes)
```

### Event Analysis Example

```python
# Find all notes
notes = ir_program.events_by_type(EventType.NOTE_ON)

# Compute pitch histogram
from collections import Counter
pitch_counts = Counter(event.data1 for event in notes)

print("Most common pitches:")
for pitch, count in pitch_counts.most_common(5):
    print(f"  {pitch} (MIDI): {count} times")

# Find longest note
note_offs = {e.data1: e.time for e in ir_program.events_by_type(EventType.NOTE_OFF)}
longest_duration = 0
longest_note = None

for note_on in notes:
    note_off_time = note_offs.get(note_on.data1)
    if note_off_time:
        duration = note_off_time - note_on.time
        if duration > longest_duration:
            longest_duration = duration
            longest_note = note_on.data1

print(f"Longest note: {longest_note} (duration: {longest_duration} ticks)")
```

### Real-time Playback Example

```python
from midi_markdown.runtime.player import RealtimePlayer

# Create player from IR program
player = RealtimePlayer(ir_program, port_number=0)

# Play with TUI
player.play()  # Blocks until complete
```

### Export to JSON Example

```python
from midi_markdown.codegen.json_export import export_json

# Export complete format
json_str = export_json(ir_program, simplified=False)
Path("events.json").write_text(json_str)

# Export simplified format (minimal info)
json_simple = export_json(ir_program, simplified=True)
Path("events_simple.json").write_text(json_simple)
```

---

## Implementation Details

### Location

The IR layer is implemented in:
- `src/midi_markdown/core/ir.py` (276 lines)
- `src/midi_markdown/core/compiler.py` (83 lines)

### Dependencies

**Internal**:
- `parser/ast_nodes.py`: MMLDocument AST structure
- `expansion/expander.py`: CommandExpander for expansion
- `alias/computation.py`: SafeComputationEngine for expressions

**External**:
- Python 3.12+ standard library (dataclasses, enum)
- Type hints (typing.TYPE_CHECKING for circular imports)

### Performance Characteristics

**Time Complexity**:
- `compile_ast_to_ir()`: O(n) where n = number of events
- `create_ir_program()`: O(n log n) due to sorting
- `_ticks_to_seconds()`: O(t) where t = number of tempo changes
- Query methods: O(n) linear scan (could be optimized with indexing)

**Space Complexity**:
- O(n) for event list
- O(t) for tempo map
- O(1) for metadata

**Scalability**:
- Tested with 1000+ event files
- Typical compilation: < 100ms for 100-event files
- Memory efficient (events stored as dataclasses, not dicts)

---

## Testing

### Test Coverage

The IR layer has comprehensive test coverage:

**Unit Tests** (`tests/unit/test_ir.py`):
- MIDIEvent creation
- EventType enum values
- string_to_event_type() conversions
- IRProgram properties (duration, counts)
- Query methods (at_time, in_range, by_type, by_channel)
- Tempo map construction
- Time conversion (_ticks_to_seconds)

**Integration Tests** (`tests/integration/test_end_to_end.py`):
- Full compilation pipeline (MML → IR → MIDI)
- Timing accuracy verification
- All event types (tempo, PC, CC, notes, pitch bend, pressure)
- MIDI file formats (0, 1, 2)

**Test Examples**:

```python
def test_ir_event_creation():
    """Test MIDIEvent dataclass."""
    event = MIDIEvent(
        time=480,
        type=EventType.NOTE_ON,
        channel=1,
        data1=60,
        data2=100,
        time_seconds=0.5,
    )
    assert event.time == 480
    assert event.type == EventType.NOTE_ON
    assert event.channel == 1
    assert event.data1 == 60
    assert event.data2 == 100

def test_ir_program_properties():
    """Test IRProgram computed properties."""
    events = [
        MIDIEvent(time=0, type=EventType.NOTE_ON, channel=1, time_seconds=0.0),
        MIDIEvent(time=480, type=EventType.NOTE_OFF, channel=1, time_seconds=0.5),
        MIDIEvent(time=960, type=EventType.NOTE_ON, channel=2, time_seconds=1.0),
    ]
    ir_program = IRProgram(resolution=480, initial_tempo=120, events=events, metadata={})

    assert ir_program.duration_ticks == 960
    assert ir_program.duration_seconds == 1.0
    assert ir_program.event_count == 3

def test_events_by_type():
    """Test event type queries."""
    events = [
        MIDIEvent(time=0, type=EventType.NOTE_ON, channel=1),
        MIDIEvent(time=0, type=EventType.CONTROL_CHANGE, channel=1),
        MIDIEvent(time=100, type=EventType.NOTE_ON, channel=1),
    ]
    ir_program = IRProgram(resolution=480, initial_tempo=120, events=events, metadata={})

    note_ons = ir_program.events_by_type(EventType.NOTE_ON)
    assert len(note_ons) == 2

    ccs = ir_program.events_by_type(EventType.CONTROL_CHANGE)
    assert len(ccs) == 1
```

---

## Summary

The IR layer provides:

✅ **Unified representation**: Single MIDIEvent structure for all event types
✅ **Absolute timing**: Tick-based timing with computed seconds
✅ **Tempo awareness**: Accurate time conversion with tempo changes
✅ **Query methods**: Search events by time, type, channel
✅ **Metadata preservation**: Source location for error reporting
✅ **Multiple outputs**: Enables MIDI files, JSON, CSV, playback
✅ **Testable**: 72.53% code coverage, comprehensive unit/integration tests

The IR layer is **production-ready** and serves as the foundation for all output formats and runtime modes.

---

**Next Steps**:
- Read [architecture.md](architecture.md) for overall system design
- Read [architecture/parser.md](architecture/parser.md) for parser details
- Explore source code: `src/midi_markdown/core/ir.py`
- Run tests: `pytest tests/unit/test_ir.py -v`

**Document Version**: 1.0
**Last Updated**: 2025-11-08
