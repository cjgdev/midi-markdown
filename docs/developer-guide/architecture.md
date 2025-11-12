# MMD Architecture Overview

**Date**: 2025-11-08
**Status**: Production-ready
**Version**: 0.1.0

## Table of Contents

1. [Introduction](#introduction)
2. [High-Level Architecture](#high-level-architecture)
3. [Pipeline Overview](#pipeline-overview)
4. [Core Components](#core-components)
5. [Data Flow](#data-flow)
6. [Design Principles](#design-principles)
7. [Extension Points](#extension-points)
8. [Key Design Decisions](#key-design-decisions)

---

## Introduction

MIDI Markdown (MMD) is a human-readable, text-based format for creating and automating MIDI sequences. The implementation follows a **multi-stage compilation pipeline** that transforms MMD source code into executable MIDI output or real-time playback.

This document provides a comprehensive overview of the architecture, intended for developers who want to understand, maintain, or extend the codebase.

### Architecture Goals

- **Separation of concerns**: Each stage has clear responsibilities
- **Intermediate representation**: Enable multiple output formats and runtime modes
- **Extensibility**: Easy to add new commands, output formats, or features
- **Error handling**: Rich error reporting with source location tracking
- **Performance**: Efficient parsing and compilation for large files

---

## High-Level Architecture

The MMD compiler follows a traditional compiler architecture with these major phases:

```
┌─────────────────────────────────────────────────────────────────┐
│                         Input Layer                             │
│  .mmd files (MIDI Markdown source code)                 │
└──────────────────────────┬──────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Frontend (Parser)                          │
│  - Lark-based LALR parser (mml.lark grammar)                   │
│  - Lexical analysis + syntactic analysis                        │
│  - AST generation with position tracking                        │
└──────────────────────────┬──────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│                   Semantic Analysis Layer                       │
│  - Import resolution (device libraries)                         │
│  - Alias resolution (expand shortcuts to MIDI)                  │
│  - Variable resolution (symbol table)                           │
└──────────────────────────┬──────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Expansion Layer                              │
│  - Loop expansion (@loop)                                       │
│  - Sweep expansion (@sweep)                                     │
│  - Variable substitution (${var})                               │
│  - Expression evaluation                                        │
└──────────────────────────┬──────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│                   Validation Layer                              │
│  - MIDI value range checking (0-127, channels 1-16)            │
│  - Timing monotonicity verification                             │
│  - Type validation                                              │
└──────────────────────────┬──────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│              IR Compiler (AST → IR)                            │
│  - Convert expanded AST to MIDIEvent list                      │
│  - Build tempo map                                              │
│  - Compute time_seconds for all events                         │
│  - Create IRProgram structure                                   │
└──────────────────────────┬──────────────────────────────────────┘
                           ↓
┌──────────────────┬───────────────────┬──────────────────────────┐
│   Codegen        │   Runtime         │   Diagnostic             │
│   - MIDI files   │   - Live playback │   - Table display        │
│   - JSON export  │   - Event sched.  │   - CSV export           │
│   - CSV export   │   - TUI player    │   - JSON inspection      │
└──────────────────┴───────────────────┴──────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│                        Output Layer                             │
│  .mid files | Real-time MIDI | JSON/CSV | Terminal display     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Pipeline Overview

The compilation process follows this linear pipeline:

### Stage 1: Parsing
**Input**: MMD source code (string or file)
**Output**: AST (Abstract Syntax Tree)
**Components**: `parser/parser.py`, `parser/transformer.py`, `parser/mml.lark`

The parser uses Lark (LALR parser generator) to convert MMD text into a structured AST. Position tracking is enabled for error reporting.

### Stage 2: Import Resolution
**Input**: AST with `@import` statements
**Output**: AST with loaded device library aliases
**Components**: `alias/imports.py`

Loads device library files and merges alias definitions. Detects circular imports.

### Stage 3: Alias Resolution
**Input**: AST with alias calls
**Output**: AST with aliases expanded to MIDI commands
**Components**: `alias/resolver.py`, `alias/conditionals.py`, `alias/computation.py`

Expands alias shortcuts (e.g., `cortex_load 1.2.3.4`) into full MIDI command sequences. Handles parameter substitution, defaults, enums, and conditionals.

### Stage 4: Command Expansion
**Input**: AST with loops, sweeps, variables
**Output**: Expanded event list (dictionaries)
**Components**: `expansion/expander.py`, `expansion/loops.py`, `expansion/sweeps.py`, `expansion/variables.py`

- Processes `@define` statements (symbol table)
- Expands `@loop` directives (repeat patterns)
- Expands `@sweep` statements (automated parameter changes)
- Substitutes variables (`${var}`)

### Stage 5: Validation
**Input**: Expanded event list
**Output**: Validated event list (or errors)
**Components**: `utils/validation/`

- Checks MIDI value ranges (notes 0-127, channels 1-16, etc.)
- Verifies timing monotonicity (times must increase)
- Validates required fields

### Stage 6: IR Compilation
**Input**: Validated event dictionaries
**Output**: IRProgram (intermediate representation)
**Components**: `core/compiler.py`, `core/ir.py`

Converts event dictionaries to `MIDIEvent` objects and wraps them in an `IRProgram` structure. Computes `time_seconds` for all events using tempo map.

### Stage 7: Output Generation
**Input**: IRProgram
**Output**: MIDI file bytes, JSON, CSV, or live playback
**Components**: `codegen/`, `runtime/`, `diagnostics/`

- **MIDI files**: `codegen/midi_file.py` (pure function, returns bytes)
- **JSON export**: `codegen/json_export.py` (complete or simplified)
- **CSV export**: `codegen/csv_export.py` (midicsv-compatible)
- **Live playback**: `runtime/player.py` (real-time MIDI I/O with TUI)
- **Diagnostics**: `diagnostics/formatter.py` (Rich table display)

---

## Core Components

### 1. Parser (`src/midi_markdown/parser/`)

**Responsibility**: Convert MMD source text to AST

**Key Files**:
- `mml.lark` (280 lines): Lark grammar in EBNF format
- `parser.py` (120 lines): MMLParser class, file/string parsing
- `transformer.py` (1,370 lines): MMLTransformer converts parse tree → AST
- `ast_nodes.py` (450+ lines): AST data structures (30+ node types)

**Technology**: [Lark](https://github.com/lark-parser/lark) LALR parser with contextual lexer

**Key Features**:
- Full source position tracking (line/column)
- YAML frontmatter parsing
- Support for all timing modes (absolute, musical, relative, simultaneous)
- Expression parsing (math, variables, ramps)
- Comprehensive error messages

**Example Usage**:
```python
from midi_markdown.parser.parser import MMLParser

parser = MMLParser()
doc = parser.parse_file("song.mmd")  # Returns MMLDocument AST
```

See [architecture/parser.md](architecture/parser.md) for detailed parser documentation.

---

### 2. Import Resolver (`src/midi_markdown/alias/imports.py`)

**Responsibility**: Load device library files and merge alias definitions

**Key Features**:
- Resolves `@import "devices/device_name.mmd"` statements
- Detects circular imports
- Validates device library format
- Returns merged alias dictionary

**Example**:
```python
from midi_markdown.alias.imports import resolve_imports

imports = ["devices/quad_cortex.mmd", "devices/eventide_h90.mmd"]
aliases = resolve_imports(imports, base_path=".")
# Returns: {"cortex_load": {...}, "h90_preset": {...}, ...}
```

---

### 3. Alias Resolver (`src/midi_markdown/alias/resolver.py`)

**Responsibility**: Expand alias calls to MIDI commands

**Key Features**:
- Parameter substitution (numeric, note, percent, enum, bool)
- Default parameter values
- Nested alias support (aliases calling aliases)
- Cycle detection (max depth: 10)
- Conditional logic (`@if/@elif/@else`)
- Computed values (expression evaluation)

**Parameter Types**:
- `{value}` - Basic integer parameter
- `{value:0-127}` - Range-constrained parameter
- `{value=64}` - Parameter with default
- `{note}` - Note name (C4, D#5, etc.)
- `{percent:0-100}` - Percentage (converted to 0-127)
- `{mode=option1:0,option2:1}` - Enum parameter

**Example**:
```python
from midi_markdown.alias.resolver import AliasResolver

# Define alias
alias_def = {
    "name": "cortex_load",
    "parameters": [
        {"name": "ch", "type": "int", "min": 1, "max": 16},
        {"name": "preset", "type": "int", "min": 0, "max": 127}
    ],
    "commands": [
        {"type": "cc", "channel": "{ch}", "data1": 0, "data2": 0},
        {"type": "pc", "channel": "{ch}", "data1": "{preset}"}
    ]
}

# Expand alias call
resolver = AliasResolver(aliases={"cortex_load": alias_def})
expanded = resolver.expand_alias("cortex_load", [1, 5])
# Returns: [
#   {"type": "cc", "channel": 1, "data1": 0, "data2": 0},
#   {"type": "pc", "channel": 1, "data1": 5}
# ]
```

---

### 4. Command Expander (`src/midi_markdown/expansion/expander.py`)

**Responsibility**: Orchestrate all expansion operations (variables, loops, sweeps)

**Key Components**:
- **SymbolTable** (`variables.py`): Stores `@define` variables
- **LoopExpander** (`loops.py`): Expands `@loop` directives
- **SweepExpander** (`sweeps.py`): Expands `@sweep` statements
- **SafeComputationEngine** (`alias/computation.py`): Evaluates expressions

**Loop Expansion**:
```mml
@loop 4 [00:00.000] +500ms
  - note_on 1.60 100 500ms
@end
```
Generates 4 note events at 0ms, 500ms, 1000ms, 1500ms.

**Sweep Expansion**:
```mml
@sweep cc 1.7 0->127 [00:00.000] 5s linear
```
Generates CC messages ramping from 0 to 127 over 5 seconds.

**Variable Substitution**:
```mml
@define base_note 60
@define velocity 100

[00:00.000]
- note_on 1.${base_note} ${velocity} 1b
```

**Example Usage**:
```python
from midi_markdown.expansion.expander import CommandExpander

expander = CommandExpander(ppq=480, tempo=120.0, time_signature=(4, 4))
expanded_events = expander.process_ast(ast_nodes)
# Returns list of event dictionaries with all expansions applied
```

---

### 5. Validation Layer (`src/midi_markdown/utils/validation/`)

**Responsibility**: Ensure all values are valid before IR compilation

**Validators**:
- **value_validator.py**: MIDI value ranges (0-127, channels 1-16, pitch bend -8192 to +8191)
- **timing_validator.py**: Timing monotonicity (events must be in chronological order)
- **document_validator.py**: Document structure (required frontmatter fields, track validity)

**Example**:
```python
from midi_markdown.utils.validation import validate_midi_value

# Raises ValidationError if out of range
validate_midi_value(128, "note", range_min=0, range_max=127)
```

---

### 6. IR Layer (`src/midi_markdown/core/`)

**Responsibility**: Intermediate representation enabling multiple outputs and runtime modes

**Key Data Structures**:

```python
@dataclass
class MIDIEvent:
    """Single MIDI event with absolute timing."""
    time: int                      # Absolute time in ticks
    type: EventType                # NOTE_ON, CC, PC, etc.
    channel: int                   # 1-16
    data1: int                     # Note/controller number
    data2: int                     # Velocity/value
    time_seconds: float | None     # Computed from tempo map
    metadata: dict | None          # Source location, track info

@dataclass
class IRProgram:
    """Complete compiled program."""
    resolution: int                # PPQ (ticks per quarter note)
    initial_tempo: int             # Starting tempo in BPM
    events: list[MIDIEvent]        # Sorted event list
    metadata: dict[str, Any]       # Document frontmatter

    # Query methods
    def events_at_time(self, seconds: float) -> list[MIDIEvent]
    def events_in_range(self, start: float, end: float) -> list[MIDIEvent]
    def events_by_type(self, event_type: EventType) -> list[MIDIEvent]
    def events_by_channel(self, channel: int) -> list[MIDIEvent]
```

**Compiler**:
```python
from midi_markdown.core import compile_ast_to_ir

ir_program = compile_ast_to_ir(ast_document, ppq=480)
print(f"Duration: {ir_program.duration_seconds}s")
print(f"Events: {ir_program.event_count}")
```

See [ir-specification.md](ir-specification.md) for complete IR documentation.

---

### 7. Codegen Layer (`src/midi_markdown/codegen/`)

**Responsibility**: Generate output formats from IRProgram

**Output Formats**:

1. **MIDI Files** (`midi_file.py`):
   - Standard MIDI File generation (formats 0, 1, 2)
   - Pure function: returns bytes (caller writes file)
   - Uses `mido` library

2. **JSON Export** (`json_export.py`):
   - Complete format: all event details + metadata
   - Simplified format: minimal event info
   - Human-readable timestamps

3. **CSV Export** (`csv_export.py`):
   - midicsv-compatible format
   - Spreadsheet/database friendly
   - Track number, time (ticks), event type, parameters

**Example**:
```python
from midi_markdown.codegen.midi_file import generate_midi_file
from pathlib import Path

# Pure function - returns bytes
midi_bytes = generate_midi_file(ir_program, midi_format=1)

# Caller writes file
Path("output.mid").write_bytes(midi_bytes)
```

---

### 8. Runtime Layer (`src/midi_markdown/runtime/`)

**Responsibility**: Real-time MIDI playback with interactive TUI

**Components**:

1. **MIDI I/O** (`midi_io.py`):
   - Port enumeration and management
   - Uses `python-rtmidi` library
   - Send MIDI messages to hardware/virtual devices

2. **Event Scheduler** (`scheduler.py`):
   - Sub-5ms timing precision
   - Hybrid sleep/busy-wait algorithm
   - Handles tempo changes

3. **Tempo Tracker** (`tempo_tracker.py`):
   - Builds tempo map from events
   - Converts ticks → milliseconds
   - Handles dynamic tempo changes

4. **Realtime Player** (`player.py`):
   - High-level API: play(), pause(), stop(), resume()
   - Thread-safe state management
   - Coordinate scheduler + MIDI I/O

5. **TUI** (`tui/`):
   - Rich-based terminal interface
   - 30 FPS display refresh
   - Keyboard controls (Space=pause, Q=quit, R=restart)
   - Progress bar, event timeline, playback stats

**Example**:
```python
from midi_markdown.runtime.player import RealtimePlayer
from midi_markdown.runtime.midi_io import list_midi_ports

# List available MIDI ports
ports = list_midi_ports()
print(ports)  # [(0, "IAC Driver Bus 1"), ...]

# Play with TUI
player = RealtimePlayer(ir_program, port_number=0)
player.play()  # Blocks until playback complete
```

---

### 9. CLI Layer (`src/midi_markdown/cli/`)

**Responsibility**: User-facing command-line interface

**Framework**: Typer + Rich

**Commands** (`commands/`):
- `compile.py`: Compile MMD → MIDI/JSON/CSV
- `validate.py`: Validate MMD without compiling
- `check.py`: Syntax check only (no validation)
- `play.py`: Real-time playback
- `inspect.py`: Display event timeline
- `version.py`: Show version info
- `library.py`: Device library management (future)

**Error Formatting** (`errors.py`):
- Rich terminal output with colors
- Source code context (3 lines before/after)
- Error codes (E1xx-E4xx)
- "Did you mean?" suggestions (Levenshtein distance)

**Example**:
```bash
# Compile MMD to MIDI
mmdc compile song.mmd -o output.mid

# Real-time playback
mmdc play song.mmd --port 0

# Export to JSON
mmdc compile song.mmd --format json -o events.json

# Inspect event timeline
mmdc inspect song.mmd
```

---

## Data Flow

### Compilation Flow (MML → MIDI)

```
.mmd file
    ↓
[Parser] parse_file()
    ↓
MMLDocument (AST)
    ↓
[ImportResolver] resolve_imports()
    ↓
MMLDocument + aliases (AST)
    ↓
[AliasResolver] expand_aliases()
    ↓
MMLDocument (expanded AST)
    ↓
[CommandExpander] process_ast()
    ↓
list[dict] (expanded events)
    ↓
[Validator] validate()
    ↓
list[dict] (validated events)
    ↓
[IR Compiler] compile_ast_to_ir()
    ↓
IRProgram
    ↓
[Codegen] generate_midi_file()
    ↓
bytes (MIDI file)
    ↓
Path.write_bytes()
    ↓
.mid file
```

### Playback Flow (MML → Real-time MIDI)

```
.mmd file
    ↓
[Same as above through IR Compiler]
    ↓
IRProgram
    ↓
[RealtimePlayer] __init__(ir_program, port)
    ↓
[TempoTracker] build_tempo_map()
    ↓
[EventScheduler] schedule_events()
    ↓
[MIDIOutput] send_message()
    ↓
MIDI hardware/virtual device
```

---

## Design Principles

### 1. Separation of Concerns
Each layer has a single, well-defined responsibility. The parser knows nothing about MIDI, the IR knows nothing about file formats.

### 2. Intermediate Representation
The IR layer decouples parsing from output generation, enabling:
- Multiple output formats (MIDI, JSON, CSV)
- Multiple execution modes (compile, playback, REPL)
- Event queries and analysis
- Future optimizations

### 3. Pure Functions
Output generators are pure functions that return data (bytes, strings) rather than writing files. This improves testability and composability.

**Good**:
```python
midi_bytes = generate_midi_file(ir_program)
Path("output.mid").write_bytes(midi_bytes)
```

**Bad**:
```python
generate_midi_file(ir_program, output_path="output.mid")  # Side effect
```

### 4. Immutable Data Structures
AST nodes and IR structures use dataclasses with immutable defaults. Transformations create new structures rather than mutating.

### 5. Error Handling with Context
All errors include source location (file, line, column) for actionable error messages.

### 6. Type Safety
Modern Python type hints throughout (Python 3.12+):
```python
def compile_ast_to_ir(document: MMLDocument, ppq: int = 480) -> IRProgram:
    ...
```

### 7. Testability
- Unit tests for each component (1090+ tests)
- Integration tests for full pipeline
- Fixtures for both valid and invalid inputs
- 72.53% code coverage (target: 80%+)

---

## Extension Points

### Adding New MIDI Commands

1. **Add to grammar** (`parser/mml.lark`):
```ebnf
command_name: "note_on" | "cc" | "new_command"
```

2. **Update transformer** (`parser/transformer.py`):
```python
def midi_command(self, items):
    # Handle new_command
    ...
```

3. **Add validation** (`utils/validation/value_validator.py`):
```python
if cmd["type"] == "new_command":
    validate_range(cmd["data1"], 0, 127)
```

4. **Add codegen** (`codegen/midi_file.py`):
```python
elif event.type == EventType.NEW_COMMAND:
    msg = Message("new_command", ...)
```

### Adding New Output Formats

1. **Create module** (`codegen/new_format.py`):
```python
def export_new_format(ir_program: IRProgram) -> str:
    """Export IR program to new format."""
    ...
    return output_string
```

2. **Update CLI** (`cli/commands/compile.py`):
```python
if format == "new_format":
    output = export_new_format(ir_program)
```

### Adding New Timing Modes

1. **Update grammar** (`parser/mml.lark`)
2. **Add TimingType enum** (`parser/ast_nodes.py`)
3. **Update transformer** (`parser/transformer.py`)
4. **Update expander** (`expansion/expander.py`)

### Adding New Device Libraries

1. **Create device file** (`devices/device_name.mmd`):
```mml
---
device: "Device Name"
manufacturer: "Company"
---

@alias device_command {param1} {param2} "Description"
  - cc {param1}.0.{param2}
@end
```

2. **Document in user guide** (`docs/user-guide/device-libraries.md`)

---

## Key Design Decisions

### Why Lark for Parsing?

**Decision**: Use Lark LALR parser instead of hand-written recursive descent

**Rationale**:
- Grammar-first design (separate .lark file)
- Fast, deterministic LALR parsing
- Position tracking built-in
- Transformer pattern for clean AST generation
- Well-maintained, pure Python

**Alternatives considered**: PLY, PyParsing, ANTLR, custom parser

### Why Intermediate Representation?

**Decision**: Add IR layer between AST and output (Phase 0)

**Rationale**:
- Enables REPL mode (future)
- Enables real-time playback (Phase 3)
- Enables event queries and analysis
- Decouples parsing from output generation
- Simplifies testing

**Trade-off**: Additional layer of abstraction, but worth it for flexibility

### Why Pure Functions for Codegen?

**Decision**: Codegen returns bytes/strings instead of writing files

**Rationale**:
- Easier to test (no file I/O in tests)
- More composable (caller decides what to do with bytes)
- Enables in-memory compilation (REPL, web apps)
- Cleaner separation of concerns

### Why Typer + Rich for CLI?

**Decision**: Use Typer framework with Rich terminal output

**Rationale**:
- Declarative command definitions (type hints)
- Automatic help generation
- Beautiful terminal output (colors, tables, progress)
- Accessibility support (--no-color)
- Modern Python 3.12+ patterns

**Alternatives considered**: Click, argparse, custom CLI

### Why Symbol Table for Variables?

**Decision**: Use symbol table pattern for `@define` variables

**Rationale**:
- Standard compiler pattern
- Supports scoping (future: local scopes)
- Clean separation from AST
- Extensible to functions/macros

---

## Summary

The MMD architecture follows proven compiler design patterns:

✅ **Multi-stage pipeline**: Clear separation of parsing, expansion, validation, compilation
✅ **Intermediate representation**: Enables multiple outputs and runtime modes
✅ **Pure functions**: Testable, composable codegen
✅ **Type safety**: Modern Python 3.12+ type hints
✅ **Rich error handling**: Source location tracking, helpful messages
✅ **Extensibility**: Clear extension points for new features

This design supports the current MVP implementation (1090+ tests, 72.53% coverage) and provides a solid foundation for future enhancements (REPL, MIDI 2.0, OSC, scripting).

---

**Next Steps**:
- Read [ir-specification.md](ir-specification.md) for IR layer details
- Read [architecture/parser.md](architecture/parser.md) for parser internals
- Read [contributing.md](contributing.md) for contribution guidelines
- Explore source code starting from `src/midi_markdown/parser/parser.py`

**Document Version**: 1.0
**Last Updated**: 2025-11-08
