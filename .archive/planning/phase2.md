# Phase 2: REPL (Interactive Command-Line Interface)

## Overview

Phase 2 adds an interactive Read-Eval-Print Loop (REPL) to the MMD compiler, enabling users to experiment with MIDI commands, test device libraries, and develop MMD files interactively. This phase builds on the completed Phase 1 diagnostic features.

**Prerequisites**: Phase 1 complete (diagnostic output features, Rich table display, CSV/JSON export)

**Estimated Time**: 12-16 hours

## Goals

- Provide interactive shell for MMD development
- Support line-by-line and multi-line input with continuation prompts
- Implement context-aware autocompletion (commands, aliases, variables)
- Graceful error recovery without crashing
- Session persistence (save/load state)
- Meta-commands for REPL control (.help, .load, .save, .reset)
- Maintain state across interactions (variables, aliases, tempo, resolution)

---

## Stage 2.1: Install prompt_toolkit

**Objective**: Add prompt_toolkit dependency for REPL infrastructure

### Tasks

#### Task 2.1.1: Add dependency

**File to modify**: `pyproject.toml`

**Changes**:
```toml
dependencies = [
    # ... existing dependencies ...
    "prompt-toolkit>=3.0.0",
]
```

#### Task 2.1.2: Install and verify

**Commands**:
```bash
uv sync
uv run python -c "from prompt_toolkit import PromptSession; print('prompt_toolkit installed')"
```

### Success Criteria

- ✅ prompt_toolkit available in virtual environment
- ✅ Can import PromptSession, Completer, and History classes
- ✅ No dependency conflicts
- ✅ `uv sync` completes successfully

---

## Stage 2.2: Create REPL State Management

**Objective**: Implement stateful REPL session with variable/alias/import tracking

### Tasks

#### Task 2.2.1: Create runtime package

**Files to create**:
- `src/midi_markdown/runtime/__init__.py`
- `src/midi_markdown/runtime/repl_state.py`

**Implementation**:

```python
# src/midi_markdown/runtime/__init__.py
"""Runtime components for interactive MMD execution."""

from __future__ import annotations

from .repl_state import REPLState

__all__ = [
    "REPLState",
]
```

#### Task 2.2.2: Implement REPLState class

**File**: `src/midi_markdown/runtime/repl_state.py`

**Requirements**:
- Store variables (from @define)
- Store aliases (from @alias and @import)
- Store imports (loaded device libraries)
- Track tempo and resolution (PPQ)
- Track last compiled IR for inspection
- Support session save/load to JSON
- Provide reset() method

**Key class**:
```python
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import json
from typing import Any

@dataclass
class REPLState:
    """Encapsulated REPL state - no global variables."""

    variables: dict[str, Any] = field(default_factory=dict)
    aliases: dict[str, Any] = field(default_factory=dict)
    imports: list[str] = field(default_factory=list)
    tempo: int = 120
    resolution: int = 480
    time_signature: tuple[int, int] = (4, 4)
    last_ir: Any | None = None  # Last compiled IRProgram

    def reset(self) -> None:
        """Clear all state to initial values."""
        self.__init__()

    def save_session(self, path: Path) -> None:
        """Persist state to JSON file."""
        # Serialize to JSON (excluding last_ir which is not serializable)

    def load_session(self, path: Path) -> None:
        """Restore state from JSON file."""
        # Deserialize from JSON and update state

    def update_from_frontmatter(self, frontmatter: dict[str, Any]) -> None:
        """Update state from MMD frontmatter."""
        # Extract tempo, ppq, time_signature from frontmatter
```

#### Task 2.2.3: Add unit tests

**File to create**: `tests/unit/test_repl_state.py`

**Test coverage**:
- `test_repl_state_initialization()` - Default values
- `test_repl_state_reset()` - Clear all state
- `test_repl_state_save_load()` - Session persistence
- `test_repl_state_update_from_frontmatter()` - Frontmatter parsing

### Success Criteria

- ✅ REPLState class stores all necessary session data
- ✅ reset() clears state to defaults
- ✅ save_session() creates valid JSON file
- ✅ load_session() restores state from JSON
- ✅ All unit tests pass
- ✅ Code coverage ≥ 85% for repl_state.py

---

## Stage 2.3: Implement Music-Aware Completer

**Objective**: Provide context-sensitive autocompletion for MMD syntax

### Tasks

#### Task 2.3.1: Create completer module

**File to create**: `src/midi_markdown/runtime/completer.py`

**Requirements**:
- Complete MIDI commands (note_on, note_off, cc, pc, pitch_bend, etc.)
- Complete alias names from loaded device libraries
- Complete variable names from @define statements
- Complete note names (C, C#, Db, D, etc. with octaves 0-9)
- Complete meta-commands (.help, .load, .save, .reset, .list, .inspect)
- Context-aware: only suggest relevant completions based on current input

**Key class**:
```python
from __future__ import annotations

from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document

from .repl_state import REPLState

class MusicCompleter(Completer):
    """Context-aware completer for MMD syntax."""

    def __init__(self, state: REPLState) -> None:
        self.state = state
        self.midi_commands = [
            "note_on", "note_off", "cc", "pc", "pitch_bend",
            "poly_pressure", "channel_pressure", "sysex",
        ]
        self.meta_commands = [
            ".help", ".load", ".save", ".reset", ".list",
            ".inspect", ".tempo", ".ppq", ".quit", ".exit",
        ]
        self.note_names = self._generate_note_names()

    def _generate_note_names(self) -> list[str]:
        """Generate all valid note names (C0-G9, with sharps/flats)."""
        # C, C#, Db, D, D#, Eb, etc. for octaves 0-9

    def get_completions(
        self,
        document: Document,
        complete_event: Any,
    ) -> Iterator[Completion]:
        """Provide context-sensitive completions."""
        word = document.get_word_before_cursor()
        line = document.current_line_before_cursor.strip()

        # Meta-commands (start with .)
        if line.startswith('.'):
            yield from self._complete_meta_commands(word)

        # Variables (after ${)
        elif '${' in line and '}' not in line.split('${')[-1]:
            yield from self._complete_variables(word)

        # Aliases (after dash or at start of command)
        elif line.startswith('-') or line.startswith('['):
            yield from self._complete_aliases(word)

        # MIDI commands
        else:
            yield from self._complete_midi_commands(word)
```

#### Task 2.3.2: Add unit tests

**File to create**: `tests/unit/test_completer.py`

**Test coverage**:
- `test_complete_midi_commands()` - Basic MIDI command completion
- `test_complete_meta_commands()` - Meta-command completion
- `test_complete_aliases()` - Alias name completion from state
- `test_complete_variables()` - Variable name completion
- `test_complete_note_names()` - Note name completion
- `test_context_aware_completion()` - Only relevant suggestions

### Success Criteria

- ✅ Completer suggests MIDI commands
- ✅ Completer suggests aliases from loaded libraries
- ✅ Completer suggests variables from @define
- ✅ Completer suggests meta-commands starting with .
- ✅ Completions are context-aware (not all suggestions at once)
- ✅ All unit tests pass
- ✅ Code coverage ≥ 80% for completer.py

---

## Stage 2.4: Implement Multi-line Input Handling

**Objective**: Support incomplete input detection and continuation prompts

### Tasks

#### Task 2.4.1: Create REPL core module

**File to create**: `src/midi_markdown/runtime/repl.py`

**Requirements**:
- Detect incomplete input using Lark's `UnexpectedEOF` exception
- Buffer multi-line input until complete
- Change prompt to `...  ` for continuation lines
- Parse buffered input when complete
- Handle parsing errors gracefully

**Key class**:
```python
from __future__ import annotations

from lark.exceptions import UnexpectedEOF, UnexpectedInput

from ..parser.parser import MMLParser
from .repl_state import REPLState

class MMLRepl:
    """Core REPL logic for MMD interactive shell."""

    def __init__(self) -> None:
        self.parser = MMLParser()
        self.state = REPLState()
        self.buffer: list[str] = []  # Multi-line input buffer

    def try_parse(self, text: str) -> tuple[bool, Any]:
        """
        Try parsing accumulated input.

        Returns:
            (complete, result):
                - (False, None): Incomplete input, need more lines
                - (True, ast): Successfully parsed, return AST
                - (True, error): Complete but invalid, return error
        """
        try:
            doc = self.parser.parse_string(text)
            return (True, doc)
        except UnexpectedEOF:
            # Need more input (incomplete @alias, @loop, etc.)
            return (False, None)
        except UnexpectedInput as e:
            # Complete but invalid syntax
            return (True, e)
        except Exception as e:
            # Other errors (file not found, etc.)
            return (True, e)

    def is_complete(self, text: str) -> bool:
        """Check if input is complete (for prompt_toolkit)."""
        complete, _ = self.try_parse(text)
        return complete
```

#### Task 2.4.2: Add unit tests

**File to create**: `tests/unit/test_repl.py`

**Test coverage**:
- `test_try_parse_complete_valid()` - Complete valid input
- `test_try_parse_complete_invalid()` - Complete invalid input
- `test_try_parse_incomplete_alias()` - Incomplete @alias block
- `test_try_parse_incomplete_loop()` - Incomplete @loop block
- `test_is_complete()` - Completion detection

### Success Criteria

- ✅ try_parse() detects incomplete input (returns False, None)
- ✅ try_parse() returns parsed AST for valid complete input
- ✅ try_parse() returns exception for invalid complete input
- ✅ is_complete() accurately detects input completeness
- ✅ All unit tests pass
- ✅ Code coverage ≥ 85% for repl.py

---

## Stage 2.5: Implement REPL Evaluation Logic

**Objective**: Execute parsed MMD in REPL context and update state

### Tasks

#### Task 2.5.1: Add evaluation method to MMLRepl

**File to modify**: `src/midi_markdown/runtime/repl.py`

**Requirements**:
- Handle @define statements (update state.variables)
- Handle @alias statements (update state.aliases)
- Handle @import statements (load device libraries, update state.imports)
- Handle frontmatter (update state.tempo, state.resolution, state.time_signature)
- Compile MIDI commands to IR and store in state.last_ir
- Display summary of results (event count, duration, etc.)

**Key method**:
```python
from rich.console import Console

from ..core import compile_ast_to_ir
from ..diagnostics import display_events_table

class MMLRepl:
    # ... existing methods ...

    def evaluate(self, doc: MMLDocument) -> None:
        """
        Evaluate parsed MMD document in REPL context.

        Updates state and displays results.
        """
        console = Console()

        # 1. Update state from frontmatter
        if doc.frontmatter:
            self.state.update_from_frontmatter(doc.frontmatter)

        # 2. Register @define variables
        for define_stmt in doc.defines:
            self.state.variables[define_stmt.name] = define_stmt.value
            console.print(f"[green]✓[/green] Defined variable: {define_stmt.name} = {define_stmt.value}")

        # 3. Register @alias definitions
        for alias_def in doc.aliases:
            self.state.aliases[alias_def.name] = alias_def
            console.print(f"[green]✓[/green] Defined alias: {alias_def.name}")

        # 4. Load @import device libraries
        for import_stmt in doc.imports:
            if import_stmt.path not in self.state.imports:
                self.state.imports.append(import_stmt.path)
                # Load aliases from device library
                console.print(f"[green]✓[/green] Imported: {import_stmt.path}")

        # 5. Compile MIDI events to IR
        if doc.events or doc.tracks:
            ppq = self.state.resolution
            ir_program = compile_ast_to_ir(doc, ppq=ppq)
            self.state.last_ir = ir_program

            # Display summary
            console.print(f"[cyan]Compiled:[/cyan] {ir_program.event_count} events")
            console.print(f"[cyan]Duration:[/cyan] {ir_program.duration_seconds:.2f}s")

            # Show event table (limited to 10 events in REPL)
            display_events_table(ir_program, max_events=10, show_stats=False, console=console)
```

#### Task 2.5.2: Add unit tests

**File to modify**: `tests/unit/test_repl.py`

**Test coverage**:
- `test_evaluate_define()` - @define updates state.variables
- `test_evaluate_alias()` - @alias updates state.aliases
- `test_evaluate_import()` - @import updates state.imports
- `test_evaluate_frontmatter()` - Frontmatter updates tempo/ppq
- `test_evaluate_events()` - MIDI commands compile to IR

### Success Criteria

- ✅ evaluate() updates state correctly for all directive types
- ✅ evaluate() compiles MIDI events to IR
- ✅ evaluate() displays summary without errors
- ✅ State persists across multiple evaluate() calls
- ✅ All unit tests pass
- ✅ Code coverage ≥ 85% for evaluation logic

---

## Stage 2.6: Implement Error Recovery

**Objective**: Handle errors gracefully without crashing REPL

### Tasks

#### Task 2.6.1: Add error handler to MMLRepl

**File to modify**: `src/midi_markdown/runtime/repl.py`

**Requirements**:
- Display syntax errors with helpful messages
- Display validation errors with context
- Display import errors (file not found, circular imports)
- Never exit REPL on error (always return to prompt)
- Use Rich formatting for error messages

**Key method**:
```python
from lark.exceptions import UnexpectedInput, UnexpectedToken

from ..cli.errors import format_parse_error, format_validation_error

class MMLRepl:
    # ... existing methods ...

    def handle_error(self, error: Exception, source_text: str = "") -> None:
        """
        Display error without crashing REPL.

        Args:
            error: Exception to display
            source_text: Source text that caused error (for syntax errors)
        """
        console = Console()

        if isinstance(error, (UnexpectedInput, UnexpectedToken)):
            # Syntax error - show formatted parse error
            formatted = format_parse_error(error, source_text, filename="<repl>")
            console.print(formatted)
            console.print("[yellow]💡 Tip:[/yellow] Check syntax and try again")

        elif isinstance(error, ValidationError):
            # Validation error - show formatted validation error
            formatted = format_validation_error(error)
            console.print(formatted)

        elif isinstance(error, FileNotFoundError):
            # Import error
            console.print(f"[red]✗ Error:[/red] File not found: {error.filename}")

        else:
            # Generic error
            console.print(f"[red]✗ Error:[/red] {error}")

        console.print("[dim]REPL state preserved - continue working[/dim]")
```

#### Task 2.6.2: Add unit tests

**File to modify**: `tests/unit/test_repl.py`

**Test coverage**:
- `test_handle_syntax_error()` - Syntax errors don't crash
- `test_handle_validation_error()` - Validation errors don't crash
- `test_handle_import_error()` - Import errors don't crash
- `test_error_preserves_state()` - State unchanged after error

### Success Criteria

- ✅ handle_error() displays formatted error messages
- ✅ handle_error() never raises exceptions
- ✅ REPL state preserved after errors
- ✅ All error types handled gracefully
- ✅ All unit tests pass
- ✅ Code coverage ≥ 80% for error handling

---

## Stage 2.7: Create REPL Command Loop

**Objective**: Implement main interactive loop with prompt_toolkit

### Tasks

#### Task 2.7.1: Implement meta-command handler

**File to modify**: `src/midi_markdown/runtime/repl.py`

**Requirements**:
- `.help` - Show available commands and syntax
- `.load <file>` - Load MMD file into REPL
- `.save <file>` - Save session state to file
- `.reset` - Clear all state
- `.list` - Show current variables/aliases/imports
- `.inspect` - Show last compiled IR as table
- `.tempo <bpm>` - Set tempo
- `.ppq <value>` - Set resolution
- `.quit` / `.exit` - Exit REPL

**Key method**:
```python
class MMLRepl:
    # ... existing methods ...

    def handle_meta_command(self, line: str) -> bool:
        """
        Handle REPL meta-commands.

        Returns:
            True if should exit REPL, False otherwise
        """
        console = Console()
        parts = line.split()
        command = parts[0]
        args = parts[1:] if len(parts) > 1 else []

        if command in [".quit", ".exit"]:
            return True

        elif command == ".help":
            self._show_help()

        elif command == ".reset":
            self.state.reset()
            self.buffer.clear()
            console.print("[green]✓[/green] State reset")

        elif command == ".list":
            self._list_state()

        elif command == ".inspect":
            self._inspect_last_ir()

        elif command == ".load":
            if not args:
                console.print("[red]✗ Error:[/red] Usage: .load <file>")
            else:
                self._load_file(Path(args[0]))

        elif command == ".save":
            if not args:
                console.print("[red]✗ Error:[/red] Usage: .save <file>")
            else:
                self.state.save_session(Path(args[0]))
                console.print(f"[green]✓[/green] Session saved to {args[0]}")

        elif command == ".tempo":
            if not args:
                console.print(f"[cyan]Current tempo:[/cyan] {self.state.tempo} BPM")
            else:
                self.state.tempo = int(args[0])
                console.print(f"[green]✓[/green] Tempo set to {self.state.tempo} BPM")

        elif command == ".ppq":
            if not args:
                console.print(f"[cyan]Current PPQ:[/cyan] {self.state.resolution}")
            else:
                self.state.resolution = int(args[0])
                console.print(f"[green]✓[/green] PPQ set to {self.state.resolution}")

        else:
            console.print(f"[red]✗ Unknown command:[/red] {command}")
            console.print("[yellow]💡 Tip:[/yellow] Type .help for available commands")

        return False
```

#### Task 2.7.2: Implement main REPL loop

**File to modify**: `src/midi_markdown/runtime/repl.py`

**Key function**:
```python
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory

def run_repl(debug: bool = False) -> None:
    """Run interactive MMD REPL."""
    repl = MMLRepl()
    session = PromptSession(
        history=FileHistory('.mmd_history'),
        completer=MusicCompleter(repl.state),
        enable_history_search=True,
    )

    console = Console()
    console.print("[bold green]MML REPL v0.1.0[/bold green]")
    console.print("Type [bold].help[/bold] for commands, [bold].quit[/bold] to exit")
    console.print()

    while True:
        try:
            # Use different prompt for continuation lines
            prompt_str = 'mml> ' if not repl.buffer else '...  '
            line = session.prompt(prompt_str)

            # Empty line
            if not line.strip():
                continue

            # Meta-command
            if line.startswith('.'):
                should_exit = repl.handle_meta_command(line)
                if should_exit:
                    console.print("[dim]Goodbye![/dim]")
                    break
                continue

            # Accumulate multi-line input
            repl.buffer.append(line)
            text = '\n'.join(repl.buffer)

            # Try parsing
            complete, result = repl.try_parse(text)

            if complete:
                # Complete input - evaluate or show error
                if isinstance(result, Exception):
                    repl.handle_error(result, text)
                else:
                    repl.evaluate(result)

                # Clear buffer for next input
                repl.buffer.clear()

            # else: incomplete input, continue accumulating

        except KeyboardInterrupt:
            # Ctrl+C clears buffer but doesn't exit
            repl.buffer.clear()
            console.print("[dim]Input cancelled[/dim]")
            continue

        except EOFError:
            # Ctrl+D exits REPL
            console.print("\n[dim]Goodbye![/dim]")
            break

        except Exception as e:
            # Unexpected error - display but don't crash
            if debug:
                console.print_exception()
            else:
                console.print(f"[red]✗ Unexpected error:[/red] {e}")
            repl.buffer.clear()
```

#### Task 2.7.3: Add integration tests

**File to create**: `tests/integration/test_repl_integration.py`

**Test coverage**:
- `test_repl_basic_commands()` - Simple MIDI commands work
- `test_repl_multi_line_input()` - Continuation prompts work
- `test_repl_state_persistence()` - Variables persist across commands
- `test_repl_error_recovery()` - Errors don't crash REPL
- `test_repl_meta_commands()` - .help, .reset, etc. work

### Success Criteria

- ✅ REPL loop starts without errors
- ✅ Prompts change for continuation lines (mml> vs ...  )
- ✅ Multi-line input accumulates correctly
- ✅ Ctrl+C cancels input without exiting
- ✅ Ctrl+D exits REPL cleanly
- ✅ All meta-commands work
- ✅ All integration tests pass

---

## Stage 2.8: Add REPL CLI Command

**Objective**: Add `mmdc repl` command to CLI

### Tasks

#### Task 2.8.1: Create repl command module

**File to create**: `src/midi_markdown/cli/commands/repl.py`

**Implementation**:
```python
"""REPL command for interactive MMD development."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from ...runtime.repl import run_repl


def repl(
    debug: Annotated[
        bool,
        typer.Option(
            "--debug",
            help="Enable debug mode (show full tracebacks)",
        ),
    ] = False,
    session: Annotated[
        Path | None,
        typer.Option(
            "--load-session",
            "-s",
            help="Load saved session state from file",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
        ),
    ] = None,
) -> None:
    """Start interactive REPL for MMD development.

    The REPL provides an interactive shell for experimenting with MMD syntax,
    testing device libraries, and developing MIDI sequences line-by-line.

    Features:
        - Context-aware autocompletion (Tab key)
        - Multi-line input support (automatic continuation prompts)
        - Command history (Up/Down arrows)
        - Session persistence (save/load state)
        - Meta-commands (.help, .load, .save, .reset, etc.)
        - Graceful error recovery

    Examples:
        mmdc repl
        mmdc repl --debug
        mmdc repl --load-session my_session.json

    Meta-commands:
        .help          Show available commands
        .quit          Exit REPL
        .reset         Clear all state
        .list          Show variables/aliases/imports
        .inspect       Show last compiled IR
        .load <file>   Load MMD file
        .save <file>   Save session state
        .tempo [bpm]   Get/set tempo
        .ppq [value]   Get/set resolution
    """
    # TODO: Load session if provided
    run_repl(debug=debug)
```

#### Task 2.8.2: Register command in CLI

**File to modify**: `src/midi_markdown/cli/commands/__init__.py`

**Changes**:
```python
from .repl import repl

__all__ = [
    # ... existing exports ...
    "repl",
]
```

**File to modify**: `src/midi_markdown/cli/main.py`

**Changes**:
```python
from .commands import (
    # ... existing imports ...
    repl,
)

# Register main commands
# ... existing commands ...
app.command()(repl)
```

#### Task 2.8.3: Add CLI integration tests

**File to create**: `tests/integration/test_repl_cli.py`

**Test coverage**:
- `test_repl_command_exists()` - Command registered
- `test_repl_help()` - Help text displays
- `test_repl_basic_usage()` - Can start REPL (use pexpect)

### Success Criteria

- ✅ `mmdc repl` command exists
- ✅ `mmdc repl --help` shows documentation
- ✅ REPL starts without errors
- ✅ All CLI integration tests pass

---

## Stage 2.9: Test REPL Features

**Objective**: Comprehensive end-to-end testing of REPL functionality

### Tasks

#### Task 2.9.1: Install pexpect for REPL testing

**File to modify**: `pyproject.toml`

**Changes**:
```toml
[tool.uv.dev-dependencies]
# ... existing dev dependencies ...
pexpect = "^4.9.0"
```

**Commands**:
```bash
uv sync
uv run python -c "import pexpect; print('pexpect installed')"
```

#### Task 2.9.2: Create comprehensive REPL tests

**File to create**: `tests/integration/test_repl_end_to_end.py`

**Test coverage**:

**Basic functionality**:
- `test_repl_startup()` - REPL starts and shows prompt
- `test_repl_simple_command()` - Execute simple MIDI command
- `test_repl_exit()` - .quit command exits cleanly

**Multi-line input**:
- `test_repl_multiline_alias()` - @alias block with continuation
- `test_repl_multiline_loop()` - @loop block with continuation
- `test_repl_continuation_prompt()` - Prompt changes to `...  `

**State management**:
- `test_repl_define_persistence()` - Variables persist across commands
- `test_repl_alias_persistence()` - Aliases persist across commands
- `test_repl_import_persistence()` - Imports persist across commands
- `test_repl_reset_command()` - .reset clears state

**Error recovery**:
- `test_repl_syntax_error_recovery()` - Syntax error doesn't crash
- `test_repl_validation_error_recovery()` - Validation error doesn't crash
- `test_repl_keyboard_interrupt()` - Ctrl+C cancels input

**Meta-commands**:
- `test_repl_help_command()` - .help displays information
- `test_repl_list_command()` - .list shows state
- `test_repl_tempo_command()` - .tempo sets tempo
- `test_repl_save_load_session()` - Session persistence

**Example test using pexpect**:
```python
import pexpect
import pytest


@pytest.mark.integration
@pytest.mark.repl
def test_repl_basic_command():
    """Test executing a simple MIDI command in REPL."""
    # Start REPL
    child = pexpect.spawn('mmdc repl', timeout=5)

    try:
        # Wait for prompt
        child.expect('mml> ')

        # Send simple command
        child.sendline('[00:00.000]')
        child.expect('mml> ')
        child.sendline('- note_on 1.60.80 1b')
        child.expect('Compiled: 2 events')  # note_on + note_off

        # Exit
        child.sendline('.quit')
        child.expect(pexpect.EOF)

    finally:
        child.close()


@pytest.mark.integration
@pytest.mark.repl
def test_repl_multiline_alias():
    """Test multi-line @alias definition."""
    child = pexpect.spawn('mmdc repl', timeout=5)

    try:
        child.expect('mml> ')

        # Start alias definition
        child.sendline('@alias test_alias {value}')
        child.expect('...  ')  # Continuation prompt

        # Complete alias
        child.sendline('  - cc 1.10.{value}')
        child.expect('...  ')
        child.sendline('@end')
        child.expect('Defined alias: test_alias')

        # Verify alias persists
        child.sendline('.list')
        child.expect('test_alias')

        child.sendline('.quit')
        child.expect(pexpect.EOF)

    finally:
        child.close()
```

#### Task 2.9.3: Run full test suite

**Commands**:
```bash
# Run all REPL tests
just test -m repl

# Run with coverage
just test-cov -m repl

# Integration tests only
just test-integration
```

### Success Criteria

- ✅ All REPL unit tests pass (≥15 tests)
- ✅ All REPL integration tests pass (≥12 tests)
- ✅ Code coverage ≥ 75% for runtime/ package
- ✅ pexpect tests work on Linux/macOS (may skip on Windows)
- ✅ No regressions in existing tests (all 840+ tests still pass)
- ✅ REPL works end-to-end for realistic workflows

---

## Completion Checklist

### Code Quality

- [ ] All new code has type annotations
- [ ] All new functions have docstrings
- [ ] Ruff formatting applied (`just fmt`)
- [ ] Ruff linting passes (`just lint`)
- [ ] mypy type checking passes (`just typecheck`)
- [ ] No new warnings or errors

### Testing

- [ ] Unit tests: ≥15 new tests for REPL components
- [ ] Integration tests: ≥12 new tests for REPL workflows
- [ ] Code coverage ≥ 75% for runtime/ package
- [ ] All existing tests still pass (840+ tests)
- [ ] Manual testing: REPL works for realistic scenarios

### Documentation

- [ ] CLAUDE.md updated with Phase 2 completion status
- [ ] README.md updated with REPL usage examples
- [ ] CLI help text accurate (`mmdc repl --help`)
- [ ] Inline code comments for complex logic

### Features

- [ ] REPL starts and shows prompt
- [ ] Single-line commands work
- [ ] Multi-line input with continuation prompts
- [ ] Context-aware autocompletion (Tab key)
- [ ] Command history (Up/Down arrows)
- [ ] Error recovery without crashing
- [ ] All meta-commands work (.help, .quit, .reset, etc.)
- [ ] State persists across commands
- [ ] Session save/load works

---

## Risk Assessment

### High Risk

**Complex multi-line parsing**:
- **Risk**: Lark's `UnexpectedEOF` detection may not work for all cases
- **Mitigation**: Extensive testing with nested blocks, edge cases
- **Fallback**: Allow users to type `@end` explicitly to complete blocks

**State management complexity**:
- **Risk**: State updates from frontmatter/imports may conflict
- **Mitigation**: Clear precedence rules (last value wins, document in code)
- **Fallback**: Add .reset command to clear corrupted state

### Medium Risk

**Autocompletion performance**:
- **Risk**: Large device libraries (100+ aliases) may slow completions
- **Mitigation**: Cache completions, lazy-load device libraries
- **Fallback**: Make completion optional (disable with flag)

**pexpect compatibility**:
- **Risk**: pexpect doesn't work on Windows
- **Mitigation**: Skip pexpect tests on Windows (pytest.skipif)
- **Fallback**: Manual testing on Windows, automated on Linux/macOS

### Low Risk

**Session persistence**:
- **Risk**: JSON serialization may fail for complex state
- **Mitigation**: Exclude non-serializable fields (last_ir)
- **Fallback**: Document .save limitations, save frontmatter only

---

## Next Steps After Phase 2

Once Phase 2 is complete, the next phase is:

**Phase 3: Real-time MIDI Playback**
- Add python-rtmidi for live MIDI output
- Implement event scheduler with sub-5ms timing precision
- Add .play command to REPL for immediate playback
- Live TUI display of playing events
- MIDI port selection and configuration

See [mml_implementation_plan.md](mml_implementation_plan.md) lines 348-600 for Phase 3 details.

---

## Summary

Phase 2 adds a fully interactive REPL to MML, enabling rapid experimentation and development. This phase is critical for making MMD accessible to musicians who want to explore device libraries and test MIDI commands without writing full .mmd files. The REPL will serve as the foundation for Phase 3 (real-time playback) and Phase 4 (live performance mode).

**Estimated completion**: 12-16 hours across 9 stages
**Test impact**: +27 new tests (15 unit + 12 integration)
**Coverage goal**: 75%+ for runtime/ package
