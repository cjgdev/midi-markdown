# Phase 0: IR Layer & Architecture Preparation

## Overview

Phase 0 creates an **Intermediate Representation (IR) layer** between the AST and MIDI file output. This architectural change enables:
- **Phase 1 REPL**: Interactive command evaluation
- **Phase 2 Live Playback**: Real-time MIDI output
- **Phase 3+ Diagnostics**: Timing analysis, event inspection, alternative outputs

## Current Architecture

```
MML Source → Parser → AST → EventGenerator → MIDIEvent list → MIDIGenerator → .mid file
```

**Current Components:**
- `src/midi_markdown/parser/` - Lark parser + transformer → AST
- `src/midi_markdown/parser/ast_nodes.py` - AST data structures
- `src/midi_markdown/midi/events.py` - EventGenerator (AST → MIDIEvent list)
- `src/midi_markdown/midi/generator.py` - MIDIGenerator (MIDIEvent → .mid file)
- `src/midi_markdown/cli/commands/compile.py` - CLI orchestration

## Proposed Architecture

```
MML Source → Parser → AST → Compiler → IR → Codegen → Output (MIDI/JSON/etc.)
                                ↓
                              REPL (Phase 1)
                              Live Player (Phase 2)
                              Diagnostics (Phase 3)
```

**New Components:**
- `src/midi_markdown/core/ir.py` - IR data structures
- `src/midi_markdown/core/compiler.py` - AST → IR compilation
- `src/midi_markdown/codegen/midi_file.py` - IR → MIDI file generation

## Implementation Strategy

### Three-Stage Incremental Approach

**Stage 0.1: Add IR Layer (Minimal Changes)**
- Extend existing `MIDIEvent` with time representation
- Extract compiler logic from `EventGenerator`
- Update pipeline, maintain backward compatibility
- **Risk: LOW** - No file moves, all tests should pass

**Stage 0.2: Create Core Package (Foundation for REPL)**
- Create `core/` package for IR types and compiler
- Add `parse_interactive()` for REPL
- **Risk: MEDIUM** - File organization changes

**Stage 0.3: Reorganize Codegen (Enable Multiple Outputs)**
- Create `codegen/` package
- Change generator to return bytes instead of writing files
- **Risk: LOW** - Internal refactoring

---

## Stage 0.1: Add IR Layer (Minimal Changes)

### Goal
Add intermediate representation without breaking existing API or moving files.

### Changes Required

#### Change 1: Extend MIDIEvent with Time Representation

**File: `src/midi_markdown/midi/events.py`**

**Current MIDIEvent:**
```python
@dataclass
class MIDIEvent:
    time: int              # Ticks only
    type: EventType
    channel: int | None
    data1: int | None
    data2: int | None
    metadata: dict | None = None
```

**Add time_seconds field:**
```python
@dataclass
class MIDIEvent:
    time: int              # Absolute tick position
    type: EventType
    channel: int | None
    data1: int | None
    data2: int | None
    time_seconds: float | None = None  # NEW: Absolute time in seconds
    metadata: dict | None = None
```

**Location:** Line ~50 in `events.py`

**Rationale:**
- Enables time-based queries for REPL/diagnostics
- Optional field maintains backward compatibility
- Computed during event generation using tempo map

#### Change 2: Create IRProgram Wrapper

**File: `src/midi_markdown/midi/events.py` (add at end)**

**New dataclass:**
```python
@dataclass
class IRProgram:
    """Intermediate representation of compiled MMD program.

    This structure sits between the AST and final output formats,
    enabling REPL, live playback, and diagnostics.
    """
    resolution: int                    # PPQ (ticks per quarter note)
    initial_tempo: int                 # Starting BPM
    events: list[MIDIEvent]            # Sorted by time
    metadata: dict[str, Any]           # Frontmatter + computed info

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
        tracks = {e.metadata.get('track', 0) for e in self.events if e.metadata}
        return len(tracks)

    @property
    def event_count(self) -> int:
        """Total number of events."""
        return len(self.events)
```

**Location:** After `EventGenerator` class (~line 300)

**Rationale:**
- Wraps events with program-level metadata
- Provides convenient properties for CLI display
- Foundation for REPL session state

#### Change 3: Update EventGenerator to Compute time_seconds

**File: `src/midi_markdown/midi/events.py`**

**Current `generate()` method:** (lines ~140-280)
```python
def generate(self, document: MMLDocument) -> list[MIDIEvent]:
    """Generate MIDI events from MMD document."""
    # ... existing logic ...
    events.sort(key=lambda e: e.time)
    return events
```

**Updated to return IRProgram:**
```python
def generate(self, document: MMLDocument) -> IRProgram:
    """Generate IR program from MMD document."""
    # ... existing event generation logic ...

    # NEW: Compute time_seconds for each event
    events = self._add_time_seconds(events)

    # Sort by time
    events.sort(key=lambda e: e.time)

    # NEW: Create IRProgram wrapper
    return IRProgram(
        resolution=self.ppq,
        initial_tempo=document.frontmatter.get('tempo', 120),
        events=events,
        metadata={
            'title': document.frontmatter.get('title', 'Untitled'),
            'author': document.frontmatter.get('author', ''),
            'description': document.frontmatter.get('description', ''),
            'version': document.frontmatter.get('version', '1.0'),
        }
    )

def _add_time_seconds(self, events: list[MIDIEvent]) -> list[MIDIEvent]:
    """Add time_seconds field to events using tempo map."""
    # Build tempo map from tempo events
    tempo_map = []
    current_tempo = 120  # Default BPM

    for event in events:
        if event.type == EventType.TEMPO:
            current_tempo = event.data1
            tempo_map.append((event.time, current_tempo))

    if not tempo_map:
        tempo_map.append((0, current_tempo))

    # Convert ticks to seconds for each event
    for event in events:
        event.time_seconds = self._ticks_to_seconds(event.time, tempo_map)

    return events

def _ticks_to_seconds(self, ticks: int, tempo_map: list[tuple[int, int]]) -> float:
    """Convert tick position to seconds using tempo map."""
    seconds = 0.0
    prev_tick = 0
    prev_tempo = tempo_map[0][1]

    for tempo_tick, tempo_bpm in tempo_map:
        if tempo_tick > ticks:
            break

        # Add time for segment at previous tempo
        if tempo_tick > prev_tick:
            tick_delta = tempo_tick - prev_tick
            seconds += self._ticks_to_seconds_at_tempo(tick_delta, prev_tempo)

        prev_tick = tempo_tick
        prev_tempo = tempo_bpm

    # Add remaining time at final tempo
    if ticks > prev_tick:
        tick_delta = ticks - prev_tick
        seconds += self._ticks_to_seconds_at_tempo(tick_delta, prev_tempo)

    return seconds

def _ticks_to_seconds_at_tempo(self, ticks: int, bpm: int) -> float:
    """Convert ticks to seconds at constant tempo."""
    # seconds_per_quarter = 60 / bpm
    # seconds = ticks / ppq * seconds_per_quarter
    return (ticks / self.ppq) * (60.0 / bpm)
```

**Location:** Add new methods after existing `generate()` method

**Rationale:**
- Time in seconds enables natural REPL queries ("show events at 2.5 seconds")
- Tempo map handles tempo changes correctly
- Computed once during compilation, not repeatedly during playback

#### Change 4: Update MIDIGenerator to Accept IRProgram

**File: `src/midi_markdown/midi/generator.py`**

**Current signature:**
```python
def generate(self, events: list[MIDIEvent], output_path: Path) -> None:
    """Generate MIDI file from events."""
```

**Updated signature:**
```python
def generate(self, ir_program: IRProgram, output_path: Path) -> None:
    """Generate MIDI file from IR program."""
    events = ir_program.events
    # ... rest of existing logic unchanged ...
```

**Location:** Line ~30 in `generator.py`

**Rationale:**
- Minimal change to existing code
- Access to program metadata for MIDI file meta events
- Maintains file-writing behavior for now

#### Change 5: Update CLI Pipeline

**File: `src/midi_markdown/cli/commands/compile.py`**

**Current pipeline** (lines ~170-250):
```python
# Generate MIDI events
console.print("[dim]Generating MIDI events...[/dim]")
generator = EventGenerator(ppq=ppq)
events = generator.generate(ast)

if verbose:
    console.print(f"  [dim]Generated:[/dim] [bold cyan]{len(events)}[/bold cyan] [dim]events[/dim]")

# Write MIDI file
console.print("[dim]Writing MIDI file...[/dim]")
midi_gen = MIDIGenerator(ppq=ppq, format=format)
midi_gen.generate(events, output_file)
```

**Updated pipeline:**
```python
# Compile to IR
console.print("[dim]Compiling to IR...[/dim]")
generator = EventGenerator(ppq=ppq)
ir_program = generator.generate(ast)

if verbose:
    console.print(f"  [dim]Generated:[/dim] [bold cyan]{ir_program.event_count}[/bold cyan] [dim]events[/dim]")
    console.print(f"  [dim]Duration:[/dim] [bold cyan]{ir_program.duration_seconds:.2f}s[/bold cyan]")
    console.print(f"  [dim]Tracks:[/dim] [bold cyan]{ir_program.track_count}[/bold cyan]")

# Generate MIDI file
console.print("[dim]Writing MIDI file...[/dim]")
midi_gen = MIDIGenerator(ppq=ppq, format=format)
midi_gen.generate(ir_program, output_file)
```

**Location:** In `compile()` function around line 200

**Rationale:**
- Uses new IRProgram API
- Displays richer statistics
- Maintains same CLI behavior

### Testing Stage 0.1

**Run full test suite:**
```bash
just test
# or
uv run pytest
```

**Expected results:**
- All 750+ tests pass
- No API breaks
- New time_seconds field populated

**Key tests to verify:**
1. `tests/unit/test_midi_commands.py` - Event generation still works
2. `tests/integration/test_end_to_end.py` - Full pipeline works
3. `tests/integration/test_cli.py` - CLI still compiles files

**Manual verification:**
```bash
just compile examples/00_hello_world.mmd output/test.mid
# Should show new duration/track stats
```

### Stage 0.1 Success Criteria

- ✅ All tests pass
- ✅ CLI compiles examples successfully
- ✅ IRProgram wrapper provides metadata
- ✅ time_seconds field populated correctly
- ✅ No breaking changes to existing API

---

## Stage 0.2: Create Core Package (Foundation for REPL)

### Goal
Organize IR types and compiler logic into `core/` package, add REPL support to parser.

### Changes Required

#### Change 1: Create Core Package

**New directory structure:**
```
src/midi_markdown/core/
├── __init__.py
├── ir.py          # Move IRProgram + MIDIEvent here
└── compiler.py    # Extract compiler logic from EventGenerator
```

#### Change 2: Move IR Types to core/ir.py

**File: `src/midi_markdown/core/__init__.py`** (NEW)
```python
"""Core data structures and compilation logic."""

from .ir import EventType, MIDIEvent, IRProgram

__all__ = [
    "EventType",
    "MIDIEvent",
    "IRProgram",
]
```

**File: `src/midi_markdown/core/ir.py`** (NEW)
```python
"""Intermediate Representation (IR) data structures.

The IR layer sits between the AST and output formats, enabling:
- REPL: Interactive evaluation and inspection
- Live playback: Real-time MIDI output
- Diagnostics: Timing analysis, event queries
- Multiple outputs: MIDI files, JSON, CSV, etc.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class EventType(Enum):
    """MIDI event types."""
    NOTE_ON = "note_on"
    NOTE_OFF = "note_off"
    CONTROL_CHANGE = "control_change"
    PROGRAM_CHANGE = "program_change"
    PITCH_BEND = "pitch_bend"
    CHANNEL_PRESSURE = "channel_pressure"
    POLY_PRESSURE = "poly_pressure"
    TEMPO = "tempo"
    TIME_SIGNATURE = "time_signature"
    KEY_SIGNATURE = "key_signature"
    MARKER = "marker"
    TEXT = "text"
    LYRIC = "lyric"
    SYSEX = "sysex"
    SONG_POSITION = "song_position"
    SONG_SELECT = "song_select"


@dataclass
class MIDIEvent:
    """A single MIDI event with timing information.

    Attributes:
        time: Absolute position in ticks
        type: Event type (note_on, cc, etc.)
        channel: MIDI channel (1-16) or None for meta/system events
        data1: First data byte (note number, CC number, etc.)
        data2: Second data byte (velocity, CC value, etc.)
        time_seconds: Absolute position in seconds (computed from tempo map)
        metadata: Additional context (source line, track, etc.)
    """
    time: int
    type: EventType
    channel: int | None
    data1: int | None
    data2: int | None
    time_seconds: float | None = None
    metadata: dict | None = None


@dataclass
class IRProgram:
    """Intermediate representation of compiled MMD program.

    This structure sits between the AST and final output formats,
    enabling REPL, live playback, and diagnostics.

    Attributes:
        resolution: PPQ (ticks per quarter note)
        initial_tempo: Starting tempo in BPM
        events: Sorted list of MIDI events
        metadata: Document frontmatter + computed information
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
        tracks = {e.metadata.get('track', 0) for e in self.events if e.metadata}
        return len(tracks)

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
            e for e in self.events
            if e.time_seconds and abs(e.time_seconds - seconds) <= tolerance
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
            e for e in self.events
            if e.time_seconds and start <= e.time_seconds <= end
        ]

    def events_by_type(self, event_type: EventType) -> list[MIDIEvent]:
        """Get all events of specific type."""
        return [e for e in self.events if e.type == event_type]

    def events_by_channel(self, channel: int) -> list[MIDIEvent]:
        """Get all events on specific channel."""
        return [e for e in self.events if e.channel == channel]
```

**Migration steps:**
1. Copy `EventType` and `MIDIEvent` from `midi/events.py` to `core/ir.py`
2. Move `IRProgram` from `midi/events.py` to `core/ir.py`
3. Update imports in `midi/events.py` to import from `core.ir`
4. Update imports in `midi/generator.py` to import from `core.ir`
5. Update imports in `cli/commands/compile.py`

#### Change 3: Extract Compiler Logic

**File: `src/midi_markdown/core/compiler.py`** (NEW)
```python
"""AST to IR compilation.

Converts parsed AST (from parser) into executable IR (intermediate representation).
The IR can then be sent to various outputs: MIDI files, JSON, live playback, REPL.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .ir import EventType, IRProgram, MIDIEvent

if TYPE_CHECKING:
    from ..parser.ast_nodes import MMLDocument


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
    # For now, delegate to EventGenerator
    # Later, extract all logic here
    from ..midi.events import EventGenerator

    generator = EventGenerator(ppq=ppq)
    return generator.generate(document)
```

**Update `core/__init__.py`:**
```python
"""Core data structures and compilation logic."""

from .compiler import compile_ast_to_ir
from .ir import EventType, IRProgram, MIDIEvent

__all__ = [
    "EventType",
    "MIDIEvent",
    "IRProgram",
    "compile_ast_to_ir",
]
```

**Rationale:**
- Clean entry point for compilation
- Hides EventGenerator implementation details
- Easy to refactor internals later without breaking API

#### Change 4: Add parse_interactive() to Parser

**File: `src/midi_markdown/parser/parser.py`**

**Add new method:**
```python
def parse_interactive(self, text: str) -> tuple[bool, MMLDocument | Exception]:
    """Parse MMD text for REPL, handling incomplete input.

    This method supports interactive parsing where input may be incomplete
    (e.g., user is still typing). It distinguishes between:
    - Incomplete input: Need more text (returns False, None)
    - Invalid but complete: Syntax error (returns True, Exception)
    - Valid and complete: Success (returns True, AST)

    Args:
        text: MMD source text (may be incomplete)

    Returns:
        Tuple of (complete, result):
        - (False, None): Input incomplete, need more
        - (True, Exception): Input complete but invalid
        - (True, AST): Input complete and valid

    Example:
        >>> parser = MMLParser()
        >>> complete, result = parser.parse_interactive("[00:01.0")
        >>> assert not complete  # Incomplete timing marker
        >>> complete, result = parser.parse_interactive("[00:01.000]\\n- cc 1.7.64")
        >>> assert complete and isinstance(result, MMLDocument)
    """
    from lark import UnexpectedEOF, UnexpectedInput

    try:
        return True, self.parse_string(text)
    except UnexpectedEOF:
        # Need more input
        return False, None
    except UnexpectedInput as e:
        # Complete but invalid
        return True, e
    except Exception as e:
        # Other errors (file not found, etc.)
        return True, e
```

**Location:** After existing `parse_string()` method (~line 60)

**Rationale:**
- REPL needs to know if input is incomplete vs invalid
- UnexpectedEOF means more input needed (e.g., unclosed bracket)
- UnexpectedInput means syntax error (e.g., invalid command)
- Foundation for Phase 1 REPL implementation

### Testing Stage 0.2

**Update imports in test files:**
```bash
# Find files importing from midi.events
grep -r "from midi_markdown.midi.events import" tests/

# Update to import from core.ir
# Example: EventType, MIDIEvent → from midi_markdown.core.ir import ...
```

**Run test suite:**
```bash
just test
```

**Test new parse_interactive() method:**
```python
# Add to tests/unit/test_parser.py

def test_parse_interactive_incomplete():
    parser = MMLParser()
    complete, result = parser.parse_interactive("[00:01.0")
    assert not complete
    assert result is None

def test_parse_interactive_invalid():
    parser = MMLParser()
    complete, result = parser.parse_interactive("- invalid_command")
    assert complete
    assert isinstance(result, Exception)

def test_parse_interactive_valid():
    parser = MMLParser()
    complete, result = parser.parse_interactive("[00:01.000]\n- cc 1.7.64")
    assert complete
    assert isinstance(result, MMLDocument)
```

### Stage 0.2 Success Criteria

- ✅ IR types in `core/ir.py`
- ✅ `compile_ast_to_ir()` function works
- ✅ `parse_interactive()` handles incomplete input
- ✅ All tests pass with new imports
- ✅ CLI still works unchanged
- ✅ Foundation ready for Phase 1 REPL

---

## Stage 0.3: Reorganize Codegen (Enable Multiple Outputs)

### Goal
Separate output generation from compilation, enable multiple output formats (MIDI, JSON, CSV, etc.)

### Changes Required

#### Change 1: Create Codegen Package

**New directory structure:**
```
src/midi_markdown/codegen/
├── __init__.py
└── midi_file.py    # Move from midi/generator.py
```

#### Change 2: Move and Update MIDI Generator

**File: `src/midi_markdown/codegen/__init__.py`** (NEW)
```python
"""Code generation for various output formats."""

from .midi_file import generate_midi_file

__all__ = ["generate_midi_file"]
```

**File: `src/midi_markdown/codegen/midi_file.py`** (MOVED from `midi/generator.py`)

**Key changes:**

1. **Import from core:**
```python
from ..core.ir import EventType, IRProgram, MIDIEvent
```

2. **Change generate() to return bytes:**
```python
def generate_midi_file(ir_program: IRProgram, format: int = 1) -> bytes:
    """Generate Standard MIDI File from IR program.

    Args:
        ir_program: Compiled IR program
        format: MIDI file format (0, 1, or 2)

    Returns:
        MIDI file as bytes

    Example:
        >>> ir = compile_ast_to_ir(ast)
        >>> midi_bytes = generate_midi_file(ir)
        >>> Path("output.mid").write_bytes(midi_bytes)
    """
    from io import BytesIO
    import mido

    # Create MIDI file
    midi = mido.MidiFile(type=format, ticks_per_beat=ir_program.resolution)

    # ... existing conversion logic ...

    # Write to BytesIO
    buffer = BytesIO()
    midi.save(file=buffer)
    return buffer.getvalue()
```

**Rationale:**
- Returning bytes decouples generation from I/O
- Enables in-memory testing without file system
- CLI handles file writing, generator handles format
- Easy to add other generators (JSON, CSV, etc.)

#### Change 3: Update CLI to Write Files

**File: `src/midi_markdown/cli/commands/compile.py`**

**Update import:**
```python
from midi_markdown.codegen import generate_midi_file
```

**Update pipeline:**
```python
# Generate MIDI file
console.print("[dim]Generating MIDI file...[/dim]")
midi_bytes = generate_midi_file(ir_program, format=format)

# Write to disk
output_file.write_bytes(midi_bytes)
```

**Rationale:**
- CLI controls file I/O
- Generator is pure function (IR → bytes)
- Easier to test and compose

#### Change 4: Add JSON Output (Optional Bonus)

**File: `src/midi_markdown/codegen/json_output.py`** (NEW)
```python
"""JSON output for diagnostics and inspection."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.ir import IRProgram


def generate_json(ir_program: IRProgram, pretty: bool = True) -> str:
    """Generate JSON representation of IR program.

    Useful for:
    - Debugging compilation issues
    - Analyzing event sequences
    - Integration with other tools

    Args:
        ir_program: Compiled IR program
        pretty: Pretty-print with indentation

    Returns:
        JSON string
    """
    data = {
        "metadata": ir_program.metadata,
        "resolution": ir_program.resolution,
        "initial_tempo": ir_program.initial_tempo,
        "duration_ticks": ir_program.duration_ticks,
        "duration_seconds": ir_program.duration_seconds,
        "event_count": ir_program.event_count,
        "track_count": ir_program.track_count,
        "events": [
            {
                "time": event.time,
                "time_seconds": event.time_seconds,
                "type": event.type.value,
                "channel": event.channel,
                "data1": event.data1,
                "data2": event.data2,
                "metadata": event.metadata,
            }
            for event in ir_program.events
        ],
    }

    return json.dumps(data, indent=2 if pretty else None)
```

**Add to CLI:**
```python
@app.command()
def export(
    input_file: Annotated[Path, typer.Argument(...)],
    output: Annotated[Path | None, typer.Option("-o", "--output")] = None,
    format: Annotated[str, typer.Option()] = "json",
    pretty: Annotated[bool, typer.Option()] = True,
) -> None:
    """Export MMD to various formats (json, csv, etc.)"""
    # Parse and compile
    ast = parser.parse_file(input_file)
    ir = compile_ast_to_ir(ast)

    # Generate output
    if format == "json":
        from midi_markdown.codegen.json_output import generate_json
        content = generate_json(ir, pretty=pretty)
    else:
        raise ValueError(f"Unsupported format: {format}")

    # Write or print
    if output:
        output.write_text(content)
        console.print(f"[green]Exported to:[/green] {output}")
    else:
        console.print(content)
```

### Testing Stage 0.3

**Test MIDI generation:**
```bash
just compile examples/00_hello_world.mmd output/test.mid
# Verify .mid file still works
```

**Test JSON export:**
```bash
just run export examples/00_hello_world.mmd -o output/test.json
# Verify JSON structure
```

**Run full test suite:**
```bash
just test
```

**Update test imports:**
- Replace `from midi_markdown.midi.generator import ...`
- With `from midi_markdown.codegen import ...`

### Stage 0.3 Success Criteria

- ✅ MIDI generator moved to `codegen/`
- ✅ `generate_midi_file()` returns bytes
- ✅ CLI writes files correctly
- ✅ All tests pass
- ✅ JSON export works (bonus)
- ✅ Ready for multiple output formats

---

## Summary of Changes

### Files Created (9 new files)

1. **`phase0.md`** - This implementation plan
2. **`src/midi_markdown/core/__init__.py`** - Core package init
3. **`src/midi_markdown/core/ir.py`** - IR data structures
4. **`src/midi_markdown/core/compiler.py`** - AST→IR compilation
5. **`src/midi_markdown/codegen/__init__.py`** - Codegen package init
6. **`src/midi_markdown/codegen/midi_file.py`** - MIDI file generation
7. **`src/midi_markdown/codegen/json_output.py`** - JSON export (optional)

### Files Modified (5 files)

1. **`src/midi_markdown/midi/events.py`**
   - Add `time_seconds` field to MIDIEvent
   - Update `generate()` to return IRProgram
   - Add tempo map and time conversion methods

2. **`src/midi_markdown/midi/generator.py`**
   - Update to accept IRProgram (Stage 0.1)
   - Later: Move to `codegen/midi_file.py` (Stage 0.3)

3. **`src/midi_markdown/parser/parser.py`**
   - Add `parse_interactive()` method

4. **`src/midi_markdown/cli/commands/compile.py`**
   - Update pipeline to use IRProgram
   - Update to use `generate_midi_file()`
   - Display richer statistics

5. **`pyproject.toml`**
   - No changes needed (all internal refactoring)

### Test Updates Required

**Import updates (~15-20 files):**
- Replace `from midi_markdown.midi.events import MIDIEvent, EventType`
- With `from midi_markdown.core.ir import MIDIEvent, EventType`
- Replace `from midi_markdown.midi.generator import MIDIGenerator`
- With `from midi_markdown.codegen import generate_midi_file`

**API updates (~5-10 files):**
- Update tests using `EventGenerator.generate()` to expect `IRProgram`
- Update tests using `MIDIGenerator.generate()` to use new signature

**New tests to add:**
- `tests/unit/test_ir.py` - IRProgram methods
- `tests/unit/test_compiler.py` - AST→IR compilation
- `tests/unit/test_parser_interactive.py` - Interactive parsing
- `tests/unit/test_json_export.py` - JSON output (optional)

---

## Implementation Checklist

### Stage 0.1: Add IR Layer (2-3 hours)

- [ ] Add `time_seconds` field to MIDIEvent
- [ ] Create IRProgram dataclass with properties
- [ ] Add `_add_time_seconds()` method to EventGenerator
- [ ] Add `_ticks_to_seconds()` tempo map conversion
- [ ] Update `EventGenerator.generate()` to return IRProgram
- [ ] Update `MIDIGenerator.generate()` to accept IRProgram
- [ ] Update CLI pipeline in `compile.py`
- [ ] Run test suite, fix any failures
- [ ] Manually test compilation of examples
- [ ] Commit: "feat: Add IR layer with time_seconds"

### Stage 0.2: Create Core Package (2-3 hours)

- [ ] Create `src/midi_markdown/core/` directory
- [ ] Create `core/__init__.py`
- [ ] Create `core/ir.py` and move IR types
- [ ] Add query methods to IRProgram (events_at_time, etc.)
- [ ] Create `core/compiler.py` with compile_ast_to_ir()
- [ ] Add `parse_interactive()` to parser
- [ ] Update imports in `midi/events.py`
- [ ] Update imports in `midi/generator.py`
- [ ] Update imports in `cli/commands/compile.py`
- [ ] Update test imports (~15 files)
- [ ] Add tests for parse_interactive()
- [ ] Run test suite, fix any failures
- [ ] Commit: "refactor: Create core package with IR types"

### Stage 0.3: Reorganize Codegen (2-3 hours)

- [ ] Create `src/midi_markdown/codegen/` directory
- [ ] Create `codegen/__init__.py`
- [ ] Move `midi/generator.py` → `codegen/midi_file.py`
- [ ] Update `generate_midi_file()` to return bytes
- [ ] Update CLI to write bytes to file
- [ ] Update test imports (~10 files)
- [ ] (Optional) Create `codegen/json_output.py`
- [ ] (Optional) Add `export` command to CLI
- [ ] Run test suite, fix any failures
- [ ] Test JSON export if implemented
- [ ] Commit: "refactor: Create codegen package, generate_midi_file returns bytes"

### Final Verification

- [ ] Run full test suite: `just test`
- [ ] Run type checking: `just typecheck`
- [ ] Run linting: `just lint`
- [ ] Test all examples compile: `just examples`
- [ ] Verify CLI help still works: `just run --help`
- [ ] Update CLAUDE.md with new architecture
- [ ] Document IR layer in docs/
- [ ] Commit: "docs: Update architecture docs for Phase 0"

---

## Risk Assessment

### Low Risk Changes
- Adding `time_seconds` field (optional, backward compatible)
- Creating IRProgram wrapper (just adds metadata)
- Adding `parse_interactive()` method (new, no impact on existing)

### Medium Risk Changes
- Moving IR types to `core/` (import updates needed)
- Extracting compiler logic (API changes)
- Moving generator to `codegen/` (package restructure)

### High Risk Changes
- None! All changes maintain backward compatibility

### Rollback Plan
Each stage is independently committable. If issues arise:
1. **Stage 0.1 fails**: Revert commit, keep existing architecture
2. **Stage 0.2 fails**: Revert core/ package, IRProgram still works
3. **Stage 0.3 fails**: Revert codegen/ package, keep generator in midi/

---

## Next Steps After Phase 0

Once Phase 0 is complete, the architecture will support:

### Phase 1: REPL
- Interactive parser ready (`parse_interactive()`)
- IR program can be inspected and modified
- Events can be queried by time/type/channel

### Phase 2: Live Playback
- IR program has time_seconds for scheduling
- Events can be filtered and sent to MIDI output
- Real-time performance enabled

### Phase 3: Diagnostics
- IR program can be analyzed and visualized
- JSON export enables integration with tools
- Event queries enable debugging

---

## Questions & Design Decisions

### Q: Should we extend MIDIEvent or create separate IREvent?
**Decision:** Extend MIDIEvent with `time_seconds` field
**Rationale:** Less duplication, simpler migration, backward compatible

### Q: Should parse_interactive() be in core or parser?
**Decision:** Add to existing MMLParser in `parser/parser.py`
**Rationale:** Parser already exists, no need for wrapper

### Q: Should validator move to core/?
**Decision:** Keep in `utils/validation/`, import from core if needed
**Rationale:** Already well-organized, no need to move

### Q: Should we rename EventGenerator to Compiler?
**Decision:** Keep EventGenerator, add `compile_ast_to_ir()` function
**Rationale:** Less disruption, can refactor internals later

### Q: Should generate_midi_file() write files or return bytes?
**Decision:** Return bytes (Stage 0.3)
**Rationale:** Pure function, easier to test, CLI handles I/O

---

## Estimated Timeline

- **Stage 0.1:** 2-3 hours (minimal IR layer)
- **Stage 0.2:** 2-3 hours (core package)
- **Stage 0.3:** 2-3 hours (codegen package)
- **Testing/docs:** 1-2 hours
- **Total:** 7-11 hours

## Success Metrics

- ✅ All 750+ tests pass
- ✅ All examples compile successfully
- ✅ CLI behavior unchanged
- ✅ New IR layer enables REPL queries
- ✅ Code coverage maintained or improved
- ✅ Type checking passes
- ✅ Documentation updated

---

## Conclusion

Phase 0 establishes the IR layer foundation for REPL, live playback, and diagnostics while maintaining full backward compatibility. The three-stage approach minimizes risk and ensures each change can be independently tested and committed.

The conservative strategy of extending existing structures (MIDIEvent, MMLParser) rather than creating parallel systems reduces code duplication and migration effort while still achieving the architectural goals.

After Phase 0, the codebase will be ready for:
- **Phase 1:** Interactive REPL with event inspection
- **Phase 2:** Live MIDI playback with real-time control
- **Phase 3:** Diagnostic tools and alternative outputs
