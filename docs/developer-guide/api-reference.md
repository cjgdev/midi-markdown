# API Reference

This page provides auto-generated API documentation for the MIDI Markdown implementation.

## Overview

The MMD codebase is organized into several key packages:

- **Parser** - Lark-based parsing and AST generation
- **Core/IR** - Intermediate Representation layer
- **Codegen** - Output format generation (MIDI, CSV, JSON)
- **Runtime** - Real-time MIDI playback
- **Validation** - Document and value validation
- **Alias** - Alias resolution and device libraries
- **Expansion** - Command expansion (variables, loops, sweeps)
- **CLI** - Command-line interface

---

## Parser

### MMDParser

::: midi_markdown.parser.parser.MMDParser
    options:
      show_source: true
      heading_level: 3

### AST Nodes

::: midi_markdown.parser.ast_nodes
    options:
      show_source: true
      heading_level: 3
      members:
        - MMLDocument
        - Track
        - Timing
        - MIDICommand
        - AliasCall
        - LoopStatement
        - SweepStatement
        - DefineStatement
        - ImportStatement
        - AliasDefinition

---

## Core / Intermediate Representation

### IR Data Structures

::: midi_markdown.core.ir
    options:
      show_source: true
      heading_level: 3
      members:
        - EventType
        - MIDIEvent
        - IRProgram

### IR Compiler

::: midi_markdown.core.compiler
    options:
      show_source: true
      heading_level: 3
      members:
        - compile_ast_to_ir

---

## Code Generation

### MIDI File Generation

::: midi_markdown.codegen.midi_file
    options:
      show_source: true
      heading_level: 3
      members:
        - generate_midi_file

### CSV Export

::: midi_markdown.codegen.csv_export
    options:
      show_source: true
      heading_level: 3
      members:
        - export_to_csv

### JSON Export

::: midi_markdown.codegen.json_export
    options:
      show_source: true
      heading_level: 3
      members:
        - export_to_json

---

## Runtime / Real-time Playback

### MIDI I/O

::: midi_markdown.runtime.midi_io
    options:
      show_source: true
      heading_level: 3
      members:
        - MIDIPortManager
        - list_midi_ports

### Event Scheduler

::: midi_markdown.runtime.scheduler
    options:
      show_source: true
      heading_level: 3
      members:
        - EventScheduler

### Tempo Tracker

::: midi_markdown.runtime.tempo_tracker
    options:
      show_source: true
      heading_level: 3
      members:
        - TempoTracker

### Realtime Player

::: midi_markdown.runtime.player
    options:
      show_source: true
      heading_level: 3
      members:
        - RealtimePlayer

### TUI Components

::: midi_markdown.runtime.tui.state
    options:
      show_source: true
      heading_level: 4
      members:
        - PlaybackState
        - TUIState

::: midi_markdown.runtime.tui.components
    options:
      show_source: true
      heading_level: 4
      members:
        - create_header
        - create_progress_panel
        - create_event_timeline
        - create_controls_panel

::: midi_markdown.runtime.tui.display
    options:
      show_source: true
      heading_level: 4
      members:
        - TUIDisplayManager

---

## Validation

### Document Validator

::: midi_markdown.utils.validation.document_validator
    options:
      show_source: true
      heading_level: 3
      members:
        - validate_document

### Timing Validator

::: midi_markdown.utils.validation.timing_validator
    options:
      show_source: true
      heading_level: 3
      members:
        - validate_timing
        - is_timing_monotonic

### Value Validator

::: midi_markdown.utils.validation.value_validator
    options:
      show_source: true
      heading_level: 3
      members:
        - validate_midi_value
        - validate_channel
        - validate_note
        - validate_cc_number
        - validate_pc_number
        - validate_pitch_bend

---

## Alias System

### Alias Resolver

::: midi_markdown.alias.resolver
    options:
      show_source: true
      heading_level: 3
      members:
        - AliasResolver
        - resolve_aliases

### Import Resolver

::: midi_markdown.alias.imports
    options:
      show_source: true
      heading_level: 3
      members:
        - resolve_imports

### Alias Models

::: midi_markdown.alias.models
    options:
      show_source: true
      heading_level: 3
      members:
        - AliasParameter
        - AliasDefinition

### Conditionals

::: midi_markdown.alias.conditionals
    options:
      show_source: true
      heading_level: 3
      members:
        - evaluate_condition

### Computation

::: midi_markdown.alias.computation
    options:
      show_source: true
      heading_level: 3
      members:
        - evaluate_expression

---

## Command Expansion

### Command Expander

::: midi_markdown.expansion.expander
    options:
      show_source: true
      heading_level: 3
      members:
        - CommandExpander
        - expand_commands

### Variables

::: midi_markdown.expansion.variables
    options:
      show_source: true
      heading_level: 3
      members:
        - resolve_variables

### Loops

::: midi_markdown.expansion.loops
    options:
      show_source: true
      heading_level: 3
      members:
        - expand_loop

### Sweeps

::: midi_markdown.expansion.sweeps
    options:
      show_source: true
      heading_level: 3
      members:
        - expand_sweep

---

## Utilities

### Parameter Types

::: midi_markdown.utils.parameter_types
    options:
      show_source: true
      heading_level: 3
      members:
        - parse_note
        - parse_percent
        - parse_bool_param

### Constants

::: midi_markdown.constants
    options:
      show_source: true
      heading_level: 3
      members:
        - MIDI_CHANNEL_MIN
        - MIDI_CHANNEL_MAX
        - MIDI_VALUE_MIN
        - MIDI_VALUE_MAX
        - MIDI_NOTE_MIN
        - MIDI_NOTE_MAX
        - PITCH_BEND_MIN
        - PITCH_BEND_MAX
        - DEFAULT_PPQ
        - DEFAULT_TEMPO

---

## CLI

### Main Application

::: midi_markdown.cli.main
    options:
      show_source: true
      heading_level: 3
      members:
        - cli

### Error Formatting

::: midi_markdown.cli.errors
    options:
      show_source: true
      heading_level: 3
      members:
        - format_error
        - format_validation_error
        - format_parse_error

---

## Type Reference

### Common Types

```python
# Timing modes
TimingMode = Literal["absolute", "musical", "relative", "simultaneous"]

# Event types
EventType = Literal[
    "note_on",
    "note_off",
    "cc",
    "pc",
    "pitch_bend",
    "poly_pressure",
    "channel_pressure",
    "tempo",
    "time_signature",
    "marker",
    "text",
    "sysex"
]

# Command types in AST
CommandType = Literal[
    "note_on",
    "note_off",
    "cc",
    "pc",
    "pitch_bend",
    "poly_pressure",
    "channel_pressure",
    "tempo",
    "time_signature",
    "marker",
    "text",
    "sysex"
]

# Parameter types for aliases
ParameterType = Literal["int", "note", "percent", "bool", "enum"]
```

### Data Structures

```python
# MIDI Event (IR layer)
@dataclass
class MIDIEvent:
    time: int                          # Absolute ticks
    type: EventType                    # Event type
    channel: int | None = None         # 1-16 for channel events
    data1: int | None = None           # Note/CC number, etc.
    data2: int | None = None           # Velocity/value, etc.
    metadata: dict[str, Any] = field(default_factory=dict)

# Timing
@dataclass
class Timing:
    mode: str                          # "absolute", "musical", "relative", "simultaneous"
    value: int | tuple[int, ...]      # Absolute ticks or (bars, beats, ticks)

# MIDI Command (AST)
@dataclass
class MIDICommand:
    type: str                          # Command type
    channel: int                       # 1-16
    data1: int | None = None           # Note/CC number
    data2: int | None = None           # Velocity/value
    duration: int | None = None        # For notes with duration
```

---

## Implementation Notes

### Pipeline Overview

```
Input (.mmd)
    ↓
Parser                → Parse to AST (Lark grammar + transformer)
    ↓
Import Resolver       → Load device library aliases
    ↓
Alias Resolver        → Expand alias calls to MIDI commands
    ↓
Command Expander      → Expand variables, loops, sweeps, conditionals
    ↓
Validator             → Check ranges, timing, values
    ↓
IR Compiler           → Convert to Intermediate Representation
    ↓
IRProgram             → Query-able event list with metadata
    ↓
┌───────────────────┬──────────────────────────┐
│ Codegen           │ Runtime (Phase 3)        │
│ - MIDI file       │ - Real-time MIDI I/O     │
│ - JSON export     │ - Event scheduler        │
│ - CSV export      │ - Tempo tracker          │
│                   │ - TUI player             │
└───────────────────┴──────────────────────────┘
    ↓                          ↓
Output (.mid, .json)    Live MIDI Output
```

### Key Design Patterns

1. **Functional Core**: Codegen functions are pure (no side effects)
2. **Immutable AST**: AST nodes are frozen dataclasses
3. **Progressive Enhancement**: Each pipeline stage adds information
4. **Type Safety**: Full type hints with mypy validation
5. **Error Context**: All errors track source location

### Testing Strategy

- **1090+ tests** (72.53% coverage)
- **Unit tests**: Component isolation
- **Integration tests**: Multi-component workflows
- **E2E tests**: Full compilation pipeline
- **Fixtures**: 37 test MMD files (25 valid, 12 invalid)

---

## See Also

- [Parser Design](architecture/parser.md) - Parser and lexer architecture details
- [Language Specification](../reference/specification.md) - Complete MMD spec
- [CLAUDE.md](https://github.com/cjgdev/midi-markdown/blob/main/CLAUDE.md) - Developer context
