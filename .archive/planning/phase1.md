# Phase 1: Diagnostic Output Features

## Overview

Phase 1 adds diagnostic and inspection capabilities to the MMD compiler, enabling users to view MIDI events in multiple formats before implementing interactive features. This phase builds directly on the Phase 0 IR layer.

**Prerequisites**: Phase 0 complete (IR layer, core package, codegen package)

**Estimated Time**: 6-8 hours

## Goals

- Display MIDI events as formatted tables
- Export events to CSV (midicsv-compatible format)
- Export events to JSON for analysis/integration
- Add CLI commands for inspection without file output
- Maintain backward compatibility with existing compile command

---

## Stage 1.1: Install Rich Library ✓

**Status**: Already installed (used by CLI)

### Verification

```bash
uv run python -c "from rich.console import Console; from rich.table import Table; print('Rich is installed')"
```

### Success Criteria

- ✅ Rich library available
- ✅ Can create Console and Table objects
- ✅ No version conflicts with existing dependencies

---

## Stage 1.2: Implement Rich Table Display

**Objective**: Create formatted table view of MIDI events using Rich

### Tasks

#### Task 1.2.1: Create diagnostics package

**Files to create**:
- `src/midi_markdown/diagnostics/__init__.py`
- `src/midi_markdown/diagnostics/formatter.py`

**Implementation**:

```python
# src/midi_markdown/diagnostics/__init__.py
"""Diagnostic tools for inspecting compiled MMD programs."""

from __future__ import annotations

from .formatter import display_events_table, format_event_details

__all__ = [
    "display_events_table",
    "format_event_details",
]
```

#### Task 1.2.2: Implement table formatter

**File**: `src/midi_markdown/diagnostics/formatter.py`

**Requirements**:
- Display MIDI events in a Rich table
- Columns: Time (musical), Time (seconds), Type, Channel, Details
- Color coding by event type
- Support for limiting displayed events
- Show summary stats (total events, duration, channels used)

**Key functions**:
```python
def display_events_table(
    ir_program: IRProgram,
    max_events: int | None = 100,
    show_stats: bool = True,
) -> None:
    """Display MIDI events as formatted table."""

def format_event_details(event: MIDIEvent) -> str:
    """Format event-specific data for display."""

def format_musical_time(tick: int, ppq: int) -> str:
    """Format tick as bars.beats.ticks."""

def get_event_summary(ir_program: IRProgram) -> dict:
    """Calculate summary statistics."""
```

**Color scheme**:
- Time: cyan
- Type: magenta (note_on), red (note_off), yellow (cc), blue (pc), green (tempo)
- Channel: green
- Details: white

#### Task 1.2.3: Add unit tests

**File**: `tests/unit/test_diagnostics_formatter.py`

**Test cases**:
- Test table rendering doesn't crash
- Test format_musical_time() calculations
- Test format_event_details() for each event type
- Test summary statistics calculation
- Test limiting displayed events
- Test handling empty IR programs

### Success Criteria

- ✅ Can display any IRProgram as a formatted table
- ✅ Musical time displayed as bars.beats.ticks
- ✅ Event details are readable and color-coded
- ✅ Summary shows correct statistics
- ✅ All tests pass

---

## Stage 1.3: Implement CSV Export

**Objective**: Export to midicsv-compatible format for analysis in external tools

### Tasks

#### Task 1.3.1: Create CSV exporter

**File**: `src/midi_markdown/codegen/csv_export.py`

**Requirements**:
- Follow midicsv format specification
- Include header row with format version
- Track number, time, event type, channel, data1, data2
- Support all MIDI event types from EventType enum
- Handle meta events (tempo, time signature, markers, text)

**midicsv format**:
```
Track, Time, Event Type, Channel, Data1, Data2
0, 0, Header, 1, 1, 480
1, 0, Start_track
1, 0, Tempo, 500000
1, 0, Time_signature, 4, 2, 24, 8
1, 0, Program_c, 0, 0
1, 0, Note_on_c, 0, 60, 90
1, 480, Note_off_c, 0, 60, 64
1, 960, End_track
```

**Key function**:
```python
def export_to_csv(ir_program: IRProgram) -> str:
    """Export IRProgram to midicsv-compatible CSV format.

    Args:
        ir_program: Compiled IR program

    Returns:
        CSV string in midicsv format
    """
```

#### Task 1.3.2: Update codegen package

**File**: `src/midi_markdown/codegen/__init__.py`

Add CSV export to exports:
```python
from .csv_export import export_to_csv

__all__ = ["generate_midi_file", "export_to_csv"]
```

#### Task 1.3.3: Add integration tests

**File**: `tests/integration/test_csv_export.py`

**Test cases**:
- Test CSV header format
- Test note events export correctly
- Test control change events
- Test tempo change events
- Test markers and text events
- Test multi-track support
- Verify CSV is parseable (use csv.DictReader)
- Compare CSV reimport to original IR

### Success Criteria

- ✅ CSV output follows midicsv specification
- ✅ All MIDI event types export correctly
- ✅ CSV can be read by midicsv tools
- ✅ Round-trip test: MMD → IR → CSV → validation
- ✅ All tests pass

---

## Stage 1.4: Implement JSON Export

**Objective**: Export to JSON for programmatic analysis and web integration

### Tasks

#### Task 1.4.1: Create JSON exporter

**File**: `src/midi_markdown/codegen/json_export.py`

**Requirements**:
- Two export formats: `complete` and `simplified`
- Complete: Full MIDI data with exact timing
- Simplified: Normalized for music analysis (human-readable times, note names)
- Include IRProgram metadata
- Pretty-print by default

**Complete format**:
```json
{
  "metadata": {
    "title": "Example Song",
    "duration_ticks": 3840,
    "duration_seconds": 8.0,
    "resolution": 480,
    "initial_tempo": 120,
    "event_count": 24,
    "track_count": 1
  },
  "events": [
    {
      "time": 0,
      "time_seconds": 0.0,
      "type": "tempo",
      "channel": null,
      "data1": 120,
      "data2": null
    },
    {
      "time": 0,
      "time_seconds": 0.0,
      "type": "note_on",
      "channel": 1,
      "data1": 60,
      "data2": 90
    }
  ]
}
```

**Simplified format**:
```json
{
  "metadata": { ... },
  "events": [
    {
      "time": "0.0s",
      "musical_time": "1.1.000",
      "type": "note",
      "channel": 1,
      "note": "C4",
      "velocity": 90,
      "duration": "1 beat"
    }
  ]
}
```

**Key functions**:
```python
def export_to_json(
    ir_program: IRProgram,
    format: str = "complete",
    pretty: bool = True,
) -> str:
    """Export IRProgram to JSON format.

    Args:
        ir_program: Compiled IR program
        format: "complete" or "simplified"
        pretty: Pretty-print with indentation

    Returns:
        JSON string
    """

def _note_number_to_name(note: int) -> str:
    """Convert MIDI note number to name (e.g., 60 → "C4")."""

def _format_duration(ticks: int, ppq: int, tempo: int) -> str:
    """Format duration in human-readable form."""
```

#### Task 1.4.2: Update codegen package

**File**: `src/midi_markdown/codegen/__init__.py`

Add JSON export:
```python
from .json_export import export_to_json

__all__ = ["generate_midi_file", "export_to_csv", "export_to_json"]
```

#### Task 1.4.3: Add integration tests

**File**: `tests/integration/test_json_export.py`

**Test cases**:
- Test complete format exports all fields
- Test simplified format is human-readable
- Test JSON is valid (use json.loads)
- Test note names in simplified format
- Test duration formatting
- Test handling of all event types
- Test pretty-print vs compact output

### Success Criteria

- ✅ JSON output is valid and well-formatted
- ✅ Complete format preserves all MIDI data
- ✅ Simplified format is human-readable
- ✅ Can parse JSON back into Python structures
- ✅ All tests pass

---

## Stage 1.5: Add CLI Commands for Diagnostics

**Objective**: Provide user-facing commands to access diagnostic features

### Tasks

#### Task 1.5.1: Add --format option to compile command

**File**: `src/midi_markdown/cli/commands/compile.py`

**Changes**:
- Add `format` parameter to compile() function
- Support: `midi` (default), `table`, `csv`, `json`, `json-simple`
- When format is not `midi`, skip MIDI file generation
- Display/export to stdout or file based on format

**Implementation**:
```python
def compile(
    input_file: Annotated[Path, typer.Argument(...)],
    output: Annotated[Path | None, typer.Option("-o", "--output")] = None,
    format: Annotated[str, typer.Option("--format", "-f")] = "midi",
    ppq: Annotated[int, typer.Option("--ppq")] = 480,
    midi_format: Annotated[int, typer.Option("--midi-format")] = 1,
    verbose: Annotated[bool, typer.Option("-v", "--verbose")] = False,
    no_color: Annotated[bool, typer.Option("--no-color")] = False,
) -> None:
    """Compile MMD file to various output formats.

    Formats:
        midi: Standard MIDI file (default)
        table: Display events as formatted table
        csv: Export to midicsv format
        json: Export to JSON (complete format)
        json-simple: Export to JSON (simplified format)
    """
    # Parse and compile to IR
    # Based on format:
    #   - midi: generate_midi_file() and write
    #   - table: display_events_table()
    #   - csv: export_to_csv() and print/write
    #   - json/json-simple: export_to_json() and print/write
```

**Output behavior**:
- If `output` is provided: write to file
- If `output` is None and format is not `midi`: write to stdout
- If format is `midi` and output is None: auto-generate filename

#### Task 1.5.2: Add inspect command

**File**: `src/midi_markdown/cli/commands/inspect.py` (NEW)

**Purpose**: Analyze MMD file without creating output file

**Implementation**:
```python
from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from midi_markdown.core import compile_ast_to_ir
from midi_markdown.diagnostics import display_events_table
from midi_markdown.parser.parser import MMLParser


def inspect(
    input_file: Annotated[Path, typer.Argument(...)],
    format: Annotated[str, typer.Option("--format", "-f")] = "table",
    limit: Annotated[int | None, typer.Option("--limit", "-n")] = 100,
    no_stats: Annotated[bool, typer.Option("--no-stats")] = False,
    verbose: Annotated[bool, typer.Option("-v", "--verbose")] = False,
) -> None:
    """Inspect MMD file and display MIDI events without creating output.

    This is useful for quickly checking what events are generated
    without writing a MIDI file.

    Examples:
        mmdc inspect song.mmd
        mmdc inspect song.mmd --limit 50
        mmdc inspect song.mmd --format json
    """
    console = Console()

    # Parse
    parser = MMLParser()
    doc = parser.parse_file(input_file)

    # Compile to IR
    ir_program = compile_ast_to_ir(doc, ppq=480)

    # Display based on format
    if format == "table":
        display_events_table(ir_program, max_events=limit, show_stats=not no_stats)
    elif format == "csv":
        from midi_markdown.codegen import export_to_csv
        console.print(export_to_csv(ir_program))
    elif format == "json":
        from midi_markdown.codegen import export_to_json
        console.print(export_to_json(ir_program, format="complete"))
    elif format == "json-simple":
        from midi_markdown.codegen import export_to_json
        console.print(export_to_json(ir_program, format="simplified"))
    else:
        console.print(f"[red]Error:[/] Unknown format: {format}")
        raise typer.Exit(1)
```

#### Task 1.5.3: Update CLI command registration

**File**: `src/midi_markdown/cli/commands/__init__.py`

Add inspect to exports:
```python
from .inspect import inspect

__all__ = [
    "compile",
    "validate",
    "check",
    "version",
    "library",
    "inspect",  # NEW
]
```

**File**: `src/midi_markdown/cli/main.py`

Register inspect command:
```python
from .commands import compile, validate, check, version, library, inspect

app.command()(compile)
app.command()(validate)
app.command()(check)
app.command()(version)
app.add_typer(library.app, name="library")
app.command()(inspect)  # NEW
```

### Success Criteria

- ✅ `mmdc compile --format table` displays events
- ✅ `mmdc compile --format csv -o output.csv` creates CSV
- ✅ `mmdc compile --format json` outputs to stdout
- ✅ `mmdc inspect` command works
- ✅ Help text is clear and includes examples
- ✅ All output formats accessible via CLI

---

## Stage 1.6: Test Diagnostic Features

**Objective**: Comprehensive testing of all diagnostic functionality

### Tasks

#### Task 1.6.1: Unit tests for formatter

**File**: `tests/unit/test_diagnostics_formatter.py`

**Coverage**:
- Table rendering for various event types
- Musical time formatting
- Event detail formatting
- Summary statistics
- Edge cases (empty program, single event, thousands of events)

#### Task 1.6.2: Unit tests for CSV export

**File**: `tests/unit/test_csv_export.py`

**Coverage**:
- CSV format compliance
- All event types
- Header/footer structure
- Multi-track export

#### Task 1.6.3: Unit tests for JSON export

**File**: `tests/unit/test_json_export.py`

**Coverage**:
- Complete format structure
- Simplified format structure
- Note name conversion
- Duration formatting
- JSON validity

#### Task 1.6.4: Integration tests for CLI

**File**: `tests/integration/test_cli_diagnostics.py`

**Coverage**:
- `compile --format table` command
- `compile --format csv` with output file
- `compile --format json` to stdout
- `inspect` command with various options
- Error handling for invalid formats
- Output file creation

#### Task 1.6.5: End-to-end verification

**Manual testing checklist**:
- [ ] Compile example files in all formats
- [ ] Verify CSV can be opened in Excel/Google Sheets
- [ ] Verify JSON can be parsed by jq
- [ ] Check table output looks good in different terminal widths
- [ ] Test with empty MMD file
- [ ] Test with large MMD file (1000+ events)

### Success Criteria

- ✅ All unit tests pass
- ✅ All integration tests pass
- ✅ Code coverage >80% for new code
- ✅ No regressions in existing functionality
- ✅ Manual testing checklist complete

---

## Implementation Checklist

### Stage 1.1: Rich Library ✓
- [x] Verify Rich is installed
- [x] No action needed (already available)

### Stage 1.2: Rich Table Display
- [ ] Create `src/midi_markdown/diagnostics/__init__.py`
- [ ] Create `src/midi_markdown/diagnostics/formatter.py`
- [ ] Implement `display_events_table()`
- [ ] Implement `format_event_details()`
- [ ] Implement `format_musical_time()`
- [ ] Implement `get_event_summary()`
- [ ] Create `tests/unit/test_diagnostics_formatter.py`
- [ ] Write tests for all formatter functions
- [ ] Verify tests pass

### Stage 1.3: CSV Export
- [ ] Create `src/midi_markdown/codegen/csv_export.py`
- [ ] Implement `export_to_csv()`
- [ ] Update `src/midi_markdown/codegen/__init__.py`
- [ ] Create `tests/integration/test_csv_export.py`
- [ ] Write CSV format tests
- [ ] Verify CSV is midicsv-compatible
- [ ] Verify tests pass

### Stage 1.4: JSON Export
- [ ] Create `src/midi_markdown/codegen/json_export.py`
- [ ] Implement `export_to_json()` with both formats
- [ ] Implement `_note_number_to_name()`
- [ ] Implement `_format_duration()`
- [ ] Update `src/midi_markdown/codegen/__init__.py`
- [ ] Create `tests/integration/test_json_export.py`
- [ ] Write JSON format tests
- [ ] Verify JSON validity
- [ ] Verify tests pass

### Stage 1.5: CLI Commands
- [ ] Update `src/midi_markdown/cli/commands/compile.py` with --format option
- [ ] Create `src/midi_markdown/cli/commands/inspect.py`
- [ ] Update `src/midi_markdown/cli/commands/__init__.py`
- [ ] Update `src/midi_markdown/cli/main.py` to register inspect
- [ ] Test CLI commands manually
- [ ] Verify help text is clear

### Stage 1.6: Testing
- [ ] Create `tests/unit/test_diagnostics_formatter.py` (if not done)
- [ ] Create `tests/unit/test_csv_export.py` (if not done)
- [ ] Create `tests/unit/test_json_export.py` (if not done)
- [ ] Create `tests/integration/test_cli_diagnostics.py`
- [ ] Run full test suite
- [ ] Check code coverage
- [ ] Complete manual testing checklist
- [ ] Fix any issues found

### Final Verification
- [ ] All 780+ tests pass (including 20+ new tests)
- [ ] No regressions in existing functionality
- [ ] All diagnostic formats work correctly
- [ ] CLI commands have good UX
- [ ] Documentation updated in CLAUDE.md
- [ ] Ready for Phase 2 (REPL)

---

## Success Metrics

**Functionality**:
- ✅ Can display MIDI events as formatted table
- ✅ Can export to CSV (midicsv-compatible)
- ✅ Can export to JSON (complete and simplified)
- ✅ CLI provides easy access to all formats
- ✅ inspect command works without output file

**Quality**:
- ✅ All tests pass (target: 800+ tests)
- ✅ Code coverage >80% for new modules
- ✅ No performance regressions
- ✅ Error handling is robust

**Usability**:
- ✅ Help text is clear and includes examples
- ✅ Output formats are well-documented
- ✅ Diagnostic output is readable and useful

---

## Risk Assessment

### Low Risk
- Table formatting (Rich is well-tested)
- CSV export (midicsv format is straightforward)
- CLI integration (existing patterns established)

### Medium Risk
- JSON export (need to ensure all event types covered)
- Large file handling (tables with 10,000+ events)
- Terminal width handling (tables in narrow terminals)

### Mitigation Strategies
- Comprehensive test coverage for all event types
- Pagination/limiting for large event lists
- Fallback formatting for narrow terminals
- Clear error messages for edge cases

---

## Next Steps After Phase 1

Once Phase 1 is complete:
- **Phase 2: REPL** - Interactive command-line interface
- **Phase 3: Live Playback** - Real-time MIDI output with TUI display
- **Phase 4: CLI Polish** - Refinement and integration
- **Phase 5: Testing & Documentation** - Comprehensive coverage
- **Phase 6: Release Preparation** - Final polish

Phase 1 provides essential diagnostic tools that will be useful throughout development and for end users debugging their MMD files.
