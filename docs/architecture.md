# Architecture Overview

This document describes the complete architecture of the MIDI Markdown (MMD) compiler, including the compilation pipeline, core components, data structures, and runtime playback system.

---

## System Overview

MML is a multi-stage compiler that transforms human-readable MIDI markup into executable MIDI sequences. The system follows a modular architecture with clear separation of concerns:

```
Input (.mmd)
    ↓
┌─────────────────────────────────────────────────────┐
│  COMPILATION PIPELINE (Parse → Expand → Validate)  │
├─────────────────────────────────────────────────────┤
│ 1. Parser         → Lark grammar → AST              │
│ 2. Import Resolver → Device library loading         │
│ 3. Alias Resolver  → Alias expansion to MIDI        │
│ 4. Command Expander → Variables, loops, sweeps      │
│ 5. Validator      → Range/timing/value validation   │
│ 6. IR Compiler    → AST → Intermediate Repr.        │
└─────────────────────────────────────────────────────┘
    ↓
┌──────────────────────┬──────────────────────────────┐
│ CODE GENERATION      │ RUNTIME (Phase 3)            │
├──────────────────────┼──────────────────────────────┤
│ - MIDI files (.mid)  │ - Real-time MIDI I/O         │
│ - JSON export        │ - Event scheduler            │
│ - CSV export         │ - Tempo tracker              │
│ - Table display      │ - TUI player                 │
└──────────────────────┴──────────────────────────────┘
    ↓                           ↓
Output files         Live MIDI Output
```

### Design Principles

1. **Human-readable first** — Markdown-inspired syntax designed for readability and scannability
2. **Device-agnostic core** — Base MIDI commands work universally; device-specific aliases extend functionality
3. **Timing flexibility** — Support four timing paradigms (absolute, musical, relative, simultaneous)
4. **Validation-friendly** — Syntax designed to make errors obvious
5. **Composable** — Reusable aliases, imports, and modular components

### Technology Stack

- **Language**: Python 3.12+ with modern type hints
- **Parser**: Lark (LALR parser with contextual lexer)
- **MIDI I/O**: Mido (MIDI file generation), python-rtmidi (real-time I/O)
- **CLI**: Typer (declarative CLI with type hints), Rich (beautiful terminal output)
- **Testing**: pytest (1090+ tests), mypy (static type checking)
- **Code Quality**: Ruff (linting/formatting), Just (task runner)

---

## Compilation Pipeline

The compiler follows a seven-stage pipeline transforming MMD source to MIDI output:

### Stage 1: Parser (Lark Grammar → AST)

**File**: `src/midi_markdown/parser/`

The parser converts MMD text into an Abstract Syntax Tree (AST) using Lark's LALR parser:

```python
class MMLParser:
    def parse_file(self, filepath: str) -> MMLDocument: ...
    def parse_string(self, text: str) -> MMLDocument: ...
```

**Components**:
- **mml.lark** — Lark grammar definition (MIDI commands, timing, directives)
- **parser.py** — Parser wrapper class (~40 lines)
- **transformer.py** — AST transformation (~1,370 lines, handles all parse tree nodes)
- **ast_nodes.py** — AST data structures (MMLDocument, Track, MIDICommand, Timing, etc.)

**Key Features**:
- Contextual lexer handles comments, strings in different contexts
- Position tracking enabled (line, column information for errors)
- YAML frontmatter parsed separately before grammar parsing
- Auto note_off generation for notes with duration
- Forward reference support for variables (resolved in later stages)

**Output**: `MMLDocument` AST with frontmatter, tracks/events, defines, imports, and aliases

### Stage 2: Import Resolver

**File**: `src/midi_markdown/alias/imports.py`

Loads device library files referenced via `@import` statements:

```python
# Example: @import "devices/quad_cortex.mmd"
loaded_aliases = import_resolver.load_imports(document.imports)
```

**Handles**:
- File loading and parsing of device library MMD files
- Cycle detection (prevents circular imports)
- Merges loaded aliases into document's alias dictionary

**Output**: Flattened alias dictionary combining document-level and imported aliases

### Stage 3: Alias Resolver

**File**: `src/midi_markdown/alias/resolver.py`

Expands alias calls to base MIDI commands with recursive resolution:

```python
resolver = AliasResolver(all_aliases, max_depth=10)
expanded_events = resolver.resolve_alias_call("cortex_load", [1, 2, 0, 5])
# Returns list of MIDICommand objects
```

**Features**:
- **Parameter binding** — Matches arguments to alias parameters
- **Parameter types** — Supports int, note, percent, bool, enum, range, channel types
- **Conditional branching** — @if/@elif/@else evaluation
- **Computed values** — Expression evaluation ({var = expr})
- **Nested aliases** — Aliases can call other aliases
- **Cycle detection** — Stack-based recursion with max_depth limit (default: 10)
- **Relative timing** — Accumulates timing within aliases ([+100ms], [+1b])

**Key Rules**:
- Resolution order: document-level aliases → imported aliases → error
- Max depth prevents stack overflow (hardcoded at 10)
- Cycle detection: O(n) check on each recursive call
- All parameters must be defined before use (except forward references)

**Output**: List of expanded MIDICommand events with resolved parameters

### Stage 4: Command Expander

**File**: `src/midi_markdown/expansion/`

Expands advanced features: variables, loops, and sweeps:

**Components**:
- **expander.py** — Main orchestrator (~1,000 lines)
- **variables.py** — @define and ${} substitution
- **loops.py** — @loop expansion (unrolls into individual events)
- **sweeps.py** — @sweep ramp expansion (automated parameter changes)

**Example - Loop Expansion**:
```python
@loop i 1 4
  [+0.500s]
  - pc 1.${i}
@end

# Expands to 4 separate pc commands at 0.5s intervals
```

**Timing Calculation** (all four paradigms):
```
1. ABSOLUTE: [mm:ss.ms] → ticks = seconds * (ppq * tempo / 60)
2. MUSICAL:  [bars.beats.ticks] → computed from time signature
3. RELATIVE: [+value unit] → current_time + delta (ms, s, b, m, t)
4. SIMULTANEOUS: [@] → current_time (no time advance)
```

**Output**: Expanded event list with all variables, loops, and sweeps resolved

### Stage 5: Validator

**File**: `src/midi_markdown/utils/validation/`

Validates entire compilation pipeline:

**Components**:
- **document_validator.py** — Structure validation (track names, imports, etc.)
- **timing_validator.py** — Timing monotonicity (events must be in order)
- **value_validator.py** — MIDI value ranges (channels 1-16, CC/note 0-127, etc.)

**Validation Rules**:
- Timing: Events must have monotonically increasing times within each track
- Channels: 1-16 (MIDI standard)
- Notes: 0-127 (C-1 to G9)
- CC/PC/Velocity: 0-127
- Pitch Bend: -8192 to +8191
- All aliases must be defined
- All imported files must exist

**Output**: Validated event list (throws ValidationError on failure)

### Stage 6: IR Compiler

**File**: `src/midi_markdown/core/`

Converts validated AST to Intermediate Representation (IR):

```python
ir_program = compile_ast_to_ir(
    document=expanded_document,
    tempo=bpm,
    ppq=ticks_per_beat,
    time_signature=(4, 4)
)
```

**IR Data Structures**:
```python
@dataclass
class MIDIEvent:
    time: int                    # Absolute ticks
    type: str                    # "note_on", "cc", "pc", "pitch_bend", etc.
    channel: int                 # 1-16
    data1: int | None            # Note/CC number
    data2: int | None            # Velocity/Value
    metadata: dict              # source_line, source_file, track

@dataclass
class IRProgram:
    events: list[MIDIEvent]
    metadata: dict              # tempo, ppq, time_signature, duration
```

**Features**:
- Query methods: `events_by_time()`, `events_by_channel()`, `by_type()`
- Metadata preserved for debugging (source file, line number, track)
- Foundation for real-time playback, diagnostics, and code generation

**Output**: IRProgram (queryable, structured event list)

### Stage 7: Code Generation

**File**: `src/midi_markdown/codegen/`

Generates output from IR in multiple formats:

**Components**:
- **midi_file.py** — MIDI file writer using mido (formats 0/1/2)
- **csv_export.py** — midicsv-compatible CSV format (for spreadsheet analysis)
- **json_export.py** — JSON export (complete and simplified formats)

**Output Formats**:
- `.mid` — Standard MIDI File (binary)
- `.csv` — Spreadsheet-compatible event list
- `.json` — Programmatic access to events and metadata
- **Table** — Rich terminal display (diagnostics/debugging)

---

## Core Components

### Parser Layer (`src/midi_markdown/parser/`)

**Lark Grammar** (`mml.lark`):
- LALR parser with contextual lexer for different token contexts
- ~12KB grammar covering all MIDI commands, timing formats, and directives
- Tokenization rules: ABSOLUTE_TIME, MUSICAL_TIME, RELATIVE_TIME, NOTE_NAME, DURATION, etc.
- Supports YAML-style frontmatter before grammar parsing

**Transformer** (`transformer.py`):
- Converts Lark parse tree to AST (~1,370 lines)
- ~100 transform methods (one per grammar rule)
- Validates parameter types during transformation
- Handles forward references for variables (stored as tuples until resolution)
- Converts note names (C#4, Db5) to MIDI note numbers

**AST Nodes** (`ast_nodes.py`):
```python
@dataclass
class MMLDocument:
    frontmatter: dict[str, Any]      # Tempo, time_signature, metadata
    tracks: list[Track]              # Multi-track mode
    events: list[Any]                # Single-track mode
    defines: list[DefineStatement]   # Variable definitions
    imports: list[ImportStatement]   # Device library imports
    aliases: list[AliasDefinition]   # Alias definitions

@dataclass
class Timing:
    mode: str                         # "absolute", "musical", "relative", "simultaneous"
    value: int | tuple[int, ...]     # Absolute ticks or (bars, beats, ticks)

@dataclass
class MIDICommand:
    type: str                         # "note_on", "cc", "pc", "pitch_bend", etc.
    channel: int | None               # 1-16 (or None for document-level commands)
    data1: int | None                 # Note/CC number
    data2: int | None                 # Velocity/Value
    duration: int | None              # For note commands (generates note_off)
```

### Alias Layer (`src/midi_markdown/alias/`)

**Resolver** (`resolver.py`):
- Recursive alias expansion with cycle detection
- Parameter binding and type checking
- Conditional evaluation (@if/@elif/@else)
- Expression evaluation for computed values
- Relative timing accumulation

**Imports** (`imports.py`):
- Loads device library MMD files
- Detects circular imports
- Merges imported aliases with document-level aliases

**Models** (`models.py`):
```python
@dataclass
class AliasDefinition:
    name: str
    parameters: list[Parameter]      # Parameter definitions
    commands: list[Any]              # Command list (AST nodes)
    description: str | None

@dataclass
class Parameter:
    name: str
    type: str                         # "int", "note", "percent", "enum", etc.
    min: int | None
    max: int | None
    default: Any | None
    enum_values: dict[str, int] | None
```

### Expansion Layer (`src/midi_markdown/expansion/`)

**Expander** (`expander.py`):
- Main orchestrator coordinating all expansions
- Variable substitution and symbol table management
- Loop unrolling (expands @loop into individual events)
- Sweep expansion (automated parameter ramping)
- Timing calculation for all four paradigms

**Variables** (`variables.py`):
- Maintains symbol table during expansion
- Substitutes ${variable} references in commands
- Validates all variables are defined before use

**Loops** (`loops.py`):
- Unrolls @loop directives into individual events
- Supports loop variables (loop counters)
- Accumulates timing across loop iterations

**Sweeps** (`sweeps.py`):
- Expands @sweep ramps into CC/pitch_bend changes
- Generates intermediate values for smooth automation
- Supports different ramp types (linear, exponential, etc.)

### Validation Layer (`src/midi_markdown/utils/validation/`)

**Document Validator** (`document_validator.py`):
- Checks frontmatter required fields
- Validates track configuration
- Checks for undefined aliases/imports
- Validates import file existence

**Timing Validator** (`timing_validator.py`):
- Ensures timing is monotonically increasing per track
- Checks timing values are within valid ranges
- Detects timing conflicts

**Value Validator** (`value_validator.py`):
- MIDI value range validation (0-127 for most values)
- Channel range (1-16)
- Pitch bend range (-8192 to +8191)
- Velocity range (0-127)

### Codegen Layer (`src/midi_markdown/codegen/`)

**MIDI File** (`midi_file.py`):
```python
def generate_midi_file(ir_program: IRProgram, format: int = 1) -> bytes:
    """Generate MIDI file bytes from IR program."""
    # Returns raw MIDI file data (can be written to .mid file)
```

**CSV Export** (`csv_export.py`):
- Exports to midicsv-compatible format
- One row per MIDI event with columns: Time, Type, Channel, Data1, Data2
- Suitable for spreadsheet analysis and debugging

**JSON Export** (`json_export.py`):
- Complete format: Full event details + metadata
- Simplified format: Minimal field set for API consumption
- Includes timing, channels, event types, source information

### Runtime Layer (`src/midi_markdown/runtime/`) — Phase 3

**MIDI I/O** (`midi_io.py`):
```python
class MIDIOutput:
    def __init__(self, port_index: int | str | None = None):
        # Initialize MIDI output port using python-rtmidi

    def send_message(self, message: MIDIMessage) -> None:
        # Send MIDI message to output port

    @classmethod
    def list_ports(cls) -> list[str]:
        # Get available MIDI output ports
```

**Tempo Tracker** (`tempo_tracker.py`):
- Maintains tempo map (tempo changes over time)
- Converts absolute ticks to milliseconds
- Handles dynamic tempo changes during playback
- Accounts for PPQ (ticks per quarter note)

**Scheduler** (`scheduler.py`):
- Sub-5ms timing precision
- Hybrid sleep/busy-wait algorithm (sleep 95%, busy-wait final 5ms)
- Thread-based event scheduling
- Handles MIDI message queueing

**Player** (`player.py`):
```python
class RealtimePlayer:
    def __init__(self, ir_program: IRProgram, midi_output: MIDIOutput):
        pass

    def play(self, tempo_bpm: int = 120) -> None:
        # Start playback from current position

    def pause(self) -> None:
        # Pause playback (resumable)

    def stop(self) -> None:
        # Stop and reset to beginning

    def resume(self) -> None:
        # Resume from paused position

    @property
    def is_playing(self) -> bool:
        # Check if currently playing
```

**Terminal UI** (`tui/`):
- **state.py** — Thread-safe state management with locks
- **components.py** — Rich UI components (progress bars, time display, port info)
- **display.py** — TUIDisplayManager with 30 FPS refresh rate
- **input.py** — KeyboardInputHandler (Space=play/pause, Q=quit, R=reset)

**TUI Features**:
- Real-time progress indicator (bar + time)
- Current playing event display
- MIDI port information
- Keyboard controls (non-blocking)
- Thread-safe state updates

---

## Data Flow & Structures

### Input Processing

```
.mmd file (text)
    ↓
Parser (parse_string)
    ↓
MMLDocument AST
├─ frontmatter: {tempo, time_signature, ...}
├─ events: [Command, Timing, Command, ...]
├─ imports: [ImportStatement, ...]
└─ aliases: [AliasDefinition, ...]
```

### Intermediate Representation

```
Expanded + Validated AST
    ↓
IR Compiler
    ↓
IRProgram
├─ events: [MIDIEvent, ...]
│  └─ Each MIDIEvent:
│     ├─ time: int (absolute ticks)
│     ├─ type: "note_on" | "cc" | "pc" | ...
│     ├─ channel: 1-16
│     ├─ data1: 0-127 (note/CC number)
│     ├─ data2: 0-127 (velocity/value)
│     └─ metadata: {source_line, source_file, track}
├─ metadata: {tempo, ppq, time_signature, duration}
└─ Query methods:
   ├─ events_by_time(start, end) → [events]
   ├─ events_by_channel(ch) → [events]
   └─ by_type(type) → [events]
```

### Output Formats

**MIDI File**:
- Binary format: Standard MIDI File (format 0/1/2)
- Tick-based timing (60 ticks per beat by default, configurable)
- Optimized delta-time encoding

**CSV Export**:
```
Time,Type,Channel,Data1,Data2
0,program_change,1,0,
480,control_change,1,7,100
960,note_on,2,60,80
```

**JSON Export**:
```json
{
  "metadata": {
    "tempo": 120,
    "ppq": 480,
    "time_signature": [4, 4],
    "duration_seconds": 50.5
  },
  "events": [
    {
      "time": 0,
      "type": "program_change",
      "channel": 1,
      "data1": 0,
      "data2": null
    }
  ]
}
```

---

## Testing Architecture

### Test Organization

- **Unit Tests** (`tests/unit/`) — 598 tests, fast (<5 seconds)
  - Component-level testing in isolation
  - Mock external dependencies
  - Examples: `test_timing.py`, `test_aliases.py`, `test_loops.py`

- **Integration Tests** (`tests/integration/`) — 242 tests
  - Multi-component workflows
  - CLI command testing
  - Device library testing
  - Examples: `test_cli.py`, `test_end_to_end.py`

### Test Markers

```python
@pytest.mark.unit           # Fast, isolated tests (598 tests)
@pytest.mark.integration    # Multi-component tests (242 tests)
@pytest.mark.e2e            # End-to-end workflows
@pytest.mark.cli            # CLI command tests
@pytest.mark.slow           # Long-running tests (>1 second)
```

### Test Fixtures

**Valid Fixtures** (`tests/fixtures/valid/`):
- 25 well-formed MMD files covering all features
- Used for positive testing and validation
- Include: timing systems, aliases, loops, sweeps, device imports

**Invalid Fixtures** (`tests/fixtures/invalid/`):
- 12 known error cases
- Used for validation testing
- Verify error messages and recovery

### Running Tests

```bash
# All tests
just test              # All tests with coverage (1090+)
just test-unit         # Unit tests only (598)
just test-integration  # Integration tests only (242)
just test-e2e          # End-to-end compilation

# Specific
uv run pytest tests/unit/test_timing.py  # Single file
uv run pytest -k "test_absolute_timing"  # By name
uv run pytest -x                         # Stop on first failure
```

### Coverage

- **Current**: 72.53% overall (1090 tests)
- **Target**: 80%+ overall
- **Critical paths**: Parser (75.81%), Diagnostics (88.77%), Codegen (85%+)
- **Reports**: HTML in `htmlcov/`, XML for CI/CD

---

## Key Technical Details

### Timing Paradigms

All four timing systems compile to absolute ticks:

1. **Absolute Timecode**: `[mm:ss.milliseconds]`
   ```
   [01:23.500]     # 1 minute, 23.5 seconds
   Formula: ticks = seconds * (ppq * tempo / 60)
   ```

2. **Musical Time**: `[bars.beats.ticks]`
   ```
   [8.2.120]       # Bar 8, Beat 2, Tick 120
   Requires: tempo + time_signature from frontmatter
   Formula: ((bars-1) * beats_per_bar + (beats-1)) * ppq + ticks
   ```

3. **Relative Delta**: `[+value unit]`
   ```
   [+500ms]        # 500 milliseconds from current position
   [+1b]           # 1 beat (music time unit)
   [+2.1.0]        # 2 bars, 1 beat (musical time relative)
   Units: ms, s, b (beats), m (measures), t (ticks)
   ```

4. **Simultaneous**: `[@]`
   ```
   [00:00.000]
   - cc 1.7.100
   [@]             # Same time as previous event
   - cc 2.7.100
   ```

### Command Abbreviations

All command types use abbreviated forms (NOT full names):
- `pc` = Program Change (NOT `program_change`)
- `cc` = Control Change (NOT `control_change`)
- `note_on` = Note On (standard)
- `note_off` = Note Off (standard)
- `pitch_bend` = Pitch Bend
- `pressure` = Channel Pressure / Aftertouch

### Alias Parameter Types

Aliases support multiple parameter types:

```python
@alias cortex_load {ch:1-16}.{setlist:0-5}.{group:0-3}.{preset:0-4}
@alias h90_reverb {type=hall:1,room:2,plate:3}.{time:0.0-10.0}
@alias toggle {name}.{on=:0,off:127}
```

**Types**:
- `int`, `int:min-max` — Integer with optional range
- `note`, `note:C1-C8` — MIDI note names with optional range
- `channel:1-16` — Channel (1-16)
- `percent:0-100` — Percentage (0-100)
- `bool` — Boolean (true/false, 1/0, on/off)
- `enum=name:value,...` — Named enumeration
- `{param=default}` — Default values

### Symbol Table Resolution

Variable resolution follows this order:

1. Check local scope (current loop iteration)
2. Check parent scopes (nested loops)
3. Check document scope (@define statements)
4. Check alias parameters
5. Forward reference (return tuple for later resolution)

---

## Architecture Highlights

### Separation of Concerns

- **Parser**: Grammar + AST transformation (no business logic)
- **Alias Resolver**: Semantic expansion (recursive with cycle detection)
- **Command Expander**: Advanced features (variables, loops, sweeps)
- **Validator**: Constraint enforcement (ranges, timing, existence)
- **Codegen**: Output format generation (multiple formats)
- **Runtime**: Real-time playback (separate from compilation)

### Immutability

- AST nodes are frozen after parsing
- Transformations create new nodes (no mutation)
- Enables validation and debugging consistency

### Error Recovery

- Parser provides position tracking (line, column)
- Helpful error messages with suggestions
- Spell-correction for alias name typos (Levenshtein distance)

### Performance

- Single-pass parsing (Lark LALR)
- Lazy evaluation of complex features (loops, sweeps)
- Event scheduling uses hybrid sleep/busy-wait (sub-5ms precision)
- Streaming output generation (doesn't load entire MIDI in memory)

### Extensibility

- Device libraries as separate MMD files
- Alias system enables semantic command layers
- Multiple output formats without recompilation
- Plugin-ready architecture for future device/format support

---

## References

- **Full Specification**: See [spec.md](https://github.com/cjgdev/midi-markdown/blob/main/spec.md) (1,300+ lines)
- **CLI Design**: See [CLAUDE.md](https://github.com/cjgdev/midi-markdown/blob/main/CLAUDE.md) (implementation patterns)
- **Parser Details**: See [developer-guide/architecture/parser-summary.md](developer-guide/architecture/parser-summary.md)
- **Examples**: See [examples/](https://github.com/cjgdev/midi-markdown/tree/main/examples) (51 working examples)
- **Device Libraries**: See [devices/](https://github.com/cjgdev/midi-markdown/tree/main/devices) (6 pre-built libraries)
