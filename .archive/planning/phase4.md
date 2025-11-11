# Phase 4: CLI Refinement & Integration

**Status**: Not yet implemented

**Objective**: Polish CLI experience, unify error handling across all modes, and ensure seamless integration between compile/play/repl/inspect commands.

**Context**: The project already uses Typer with Rich for CLI. Commands are well-organized in `src/midi_markdown/cli/commands/`. Phase 4 focuses on refinement, not rewriting.

---

## Current State Assessment

**Existing Commands** (all implemented):
- ✅ `compile` - Full-featured with --format option (midi/table/csv/json)
- ✅ `validate` - Semantic validation without compilation
- ✅ `check` - Fast syntax-only validation
- ✅ `play` - Real-time playback with TUI (Phase 3)
- ✅ `repl` - Interactive REPL (Phase 2)
- ✅ `inspect` - Display MIDI events without output file (Phase 1)
- ✅ `version` - Show version information
- ⚠️ `library` - Stubbed placeholder (list/info/validate)

**CLI Infrastructure**:
- ✅ Typer framework in place
- ✅ Rich for output formatting
- ✅ Error formatting infrastructure (`cli/errors.py`)
- ✅ Modular command structure

**Gaps to Address**:
- ⚠️ Inconsistent error handling across commands
- ⚠️ Missing unified error handler context manager
- ⚠️ No progress indicators for long operations
- ⚠️ Error messages could be more helpful (source context, suggestions)
- ⚠️ Missing helper commands (ports, examples)
- ⚠️ Incomplete library command implementation
- ⚠️ Integration testing gaps

---

## Stage 1: Unified Error Handling System

**Goal**: Create consistent, mode-aware error handling across all CLI commands

### Step 1.1: Analyze Current Error Handling Patterns

- [ ] Review error handling in each command:
  - `compile.py` - How are parse/validation/generation errors handled?
  - `play.py` - How are MIDI port/playback errors handled?
  - `repl.py` - How does error recovery work?
  - `validate.py` - What validation error format is used?
- [ ] Identify common error types:
  - `ParseError` - Lark syntax errors
  - `ValidationError` - Semantic validation failures
  - `FileNotFoundError` - Missing MMD files
  - `MIDIError` - Port/device errors (play mode)
  - `KeyboardInterrupt` - User cancellation
- [ ] Document current exit codes (if any)

### Step 1.2: Create Error Handler Context Manager

- [ ] Create `src/midi_markdown/cli/error_handler.py`:
  ```python
  """Unified error handling for all CLI commands."""

  from __future__ import annotations

  import sys
  from contextlib import contextmanager
  from typing import TYPE_CHECKING

  from rich.console import Console

  if TYPE_CHECKING:
      from midi_markdown.runtime.player import RealtimePlayer


  @dataclass
  class ErrorContext:
      """Context for error handling behavior."""
      mode: str  # "compile", "play", "repl", "validate"
      debug: bool = False
      player: RealtimePlayer | None = None
      console: Console | None = None


  @contextmanager
  def cli_error_handler(ctx: ErrorContext):
      """
      Mode-aware error handling context manager.

      Handles:
      - KeyboardInterrupt (Ctrl+C) with cleanup
      - ParseError (syntax errors)
      - ValidationError (semantic errors)
      - FileNotFoundError (missing files)
      - RuntimeError (MIDI/player errors)
      - Generic exceptions (with stack trace in debug mode)

      Exit codes:
      - 0: Success
      - 1: General error
      - 2: Parse error
      - 3: Validation error
      - 4: File not found
      - 5: MIDI/runtime error
      - 130: Keyboard interrupt (standard)
      """
      console = ctx.console or Console()

      try:
          yield

      except KeyboardInterrupt:
          console.print("\n[yellow]⚠[/yellow] Cancelled by user")

          # Mode-specific cleanup
          if ctx.mode == "play" and ctx.player:
              console.print("[dim]Sending all-notes-off...[/dim]")
              ctx.player.stop()  # Sends MIDI panic

          sys.exit(130)

      except ParseError as e:
          from midi_markdown.cli.errors import format_parse_error
          format_parse_error(console, e, debug=ctx.debug)
          sys.exit(2)

      except ValidationError as e:
          from midi_markdown.cli.errors import format_validation_error
          format_validation_error(console, e, debug=ctx.debug)
          sys.exit(3)

      except FileNotFoundError as e:
          console.print(f"[red]Error:[/red] File not found: {e.filename}")
          if ctx.debug:
              console.print_exception()
          sys.exit(4)

      except RuntimeError as e:
          # MIDI port errors, player errors, etc.
          console.print(f"[red]Runtime Error:[/red] {e}")
          if ctx.debug:
              console.print_exception()
          sys.exit(5)

      except Exception as e:
          console.print(f"[red]Unexpected Error:[/red] {type(e).__name__}: {e}")
          if ctx.debug:
              console.print_exception(show_locals=True)
          else:
              console.print("[dim]Run with --debug for full traceback[/dim]")
          sys.exit(1)
  ```

### Step 1.3: Add --debug Flag to All Commands

- [ ] Update `compile.py` to add `debug: bool = typer.Option(False)`
- [ ] Update `play.py` to add `debug: bool = typer.Option(False)`
- [ ] Update `validate.py` to add `debug: bool = typer.Option(False)`
- [ ] Update `inspect.py` to add `debug: bool = typer.Option(False)`
- [ ] Note: `repl.py` already has `--debug` flag
- [ ] Note: `check.py` can add `--debug` for consistency

### Step 1.4: Integrate Error Handler in All Commands

- [ ] Wrap command logic in `cli_error_handler`:
  ```python
  # Example for compile.py
  def compile(..., debug: bool = typer.Option(False)):
      console = Console()
      ctx = ErrorContext(mode="compile", debug=debug, console=console)

      with cli_error_handler(ctx):
          # Existing compile logic
          parser = MMLParser()
          doc = parser.parse_file(input_file)
          # ... rest of compilation
  ```
- [ ] Apply to all commands: compile, validate, check, play, inspect
- [ ] REPL already has error recovery, but add handler for startup errors

### Step 1.5: Test Error Handling

- [ ] Create `tests/integration/test_error_handling.py`:
  ```python
  def test_parse_error_exit_code():
      """Test parse errors return exit code 2."""

  def test_validation_error_exit_code():
      """Test validation errors return exit code 3."""

  def test_file_not_found_exit_code():
      """Test missing files return exit code 4."""

  def test_keyboard_interrupt_cleanup():
      """Test Ctrl+C sends MIDI panic in play mode."""

  def test_debug_flag_shows_traceback():
      """Test --debug shows full exception traceback."""
  ```
- [ ] **Success criteria**: All commands handle errors consistently, exit codes are standardized

---

## Stage 2: Enhanced Error Formatting

**Goal**: Improve error messages with source context, highlighting, and suggestions

### Step 2.1: Audit Current Error Formatting

- [ ] Review `src/midi_markdown/cli/errors.py`:
  - What error formatting functions exist?
  - Do they show source context?
  - Do they highlight error locations?
  - Do they provide suggestions?
- [ ] Identify gaps in current implementation

### Step 2.2: Enhance Parse Error Formatting

- [ ] Update `format_parse_error()` in `cli/errors.py`:
  - Show 3 lines of context (before/current/after)
  - Use Rich syntax highlighting for MMD source
  - Add `^^^` pointer to exact error location
  - Provide "Did you mean?" suggestions for common mistakes
  - Example output:
    ```
    ❌ Parse Error at line 12, column 5 in song.mmd

       10 │ [00:01.000]
       11 │ - note_on 1.60 80 1b
       12 │ - noe_off 1.60
           │   ^^^ unexpected token
       13 │ [00:02.000]

    💡 Suggestion: Did you mean 'note_off'?

    Run with --debug for full traceback
    ```

### Step 2.3: Enhance Validation Error Formatting

- [ ] Update `format_validation_error()` in `cli/errors.py`:
  - Show specific validation failure (e.g., "MIDI channel 17 out of range")
  - Indicate valid range (e.g., "Valid channels: 1-16")
  - Provide correction hint if possible
  - Example output:
    ```
    ❌ Validation Error at line 15 in song.mmd

       15 │ - cc 17.7.100

    Invalid MIDI channel: 17
    Valid channels: 1-16

    💡 Suggestion: Change to a channel between 1 and 16
    ```

### Step 2.4: Add "Explain" Helper (Future)

- [ ] Design error code system (deferred to future phase):
  - E001: Unexpected token
  - E002: Invalid MIDI value
  - E003: Timing not monotonic
  - etc.
- [ ] Stub out `mmdc explain E001` command for future:
  ```python
  @app.command()
  def explain(error_code: str):
      """Explain error codes in detail (COMING SOON)."""
      console = Console()
      console.print(f"[yellow]Error code explanations coming soon![/yellow]")
      console.print(f"Requested: {error_code}")
  ```

### Step 2.5: Test Enhanced Error Messages

- [ ] Create `tests/unit/test_error_formatting.py`:
  ```python
  def test_parse_error_shows_context():
      """Test parse errors show source context."""

  def test_parse_error_shows_pointer():
      """Test parse errors highlight exact location."""

  def test_validation_error_shows_valid_range():
      """Test validation errors show valid value ranges."""

  def test_error_suggestions():
      """Test 'Did you mean?' suggestions."""
  ```
- [ ] **Success criteria**: Error messages are clear, helpful, and actionable

---

## Stage 3: Progress Indicators for Long Operations

**Goal**: Add progress feedback for compilation, validation, and large file processing

### Step 3.1: Identify Long-Running Operations

- [ ] Audit operations that take >1 second:
  - Large file parsing (>1000 lines)
  - Alias resolution (many nested aliases)
  - Variable expansion (deep loops)
  - MIDI file generation (many events)
  - Multi-file imports (device libraries)

### Step 3.2: Add Progress to Compilation

- [ ] Update `compile.py` to show progress for large files:
  ```python
  from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

  # For large files (>500 events estimated)
  with Progress(
      SpinnerColumn(),
      TextColumn("[progress.description]{task.description}"),
      BarColumn(),
      TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
      console=console
  ) as progress:

      # Parsing phase
      task = progress.add_task("Parsing MML...", total=100)
      doc = parser.parse_file(input_file)
      progress.update(task, advance=25)

      # Alias resolution phase
      progress.update(task, description="Resolving aliases...", advance=25)
      # ... alias resolution

      # Validation phase
      progress.update(task, description="Validating...", advance=25)
      # ... validation

      # MIDI generation phase
      progress.update(task, description="Generating MIDI...", advance=25)
      # ... MIDI generation
  ```

### Step 3.3: Add Progress to Validation

- [ ] Update `validate.py` to show progress for large files:
  - Similar structure to compile, but skip MIDI generation phase
  - Focus on parse → resolve → validate pipeline

### Step 3.4: Make Progress Conditional

- [ ] Only show progress for "large" files (heuristic):
  - File size > 50 KB
  - OR estimated events > 500
  - OR --verbose flag is set
- [ ] For small files, keep simple status messages
- [ ] Respect `--no-progress` flag if added

### Step 3.5: Test Progress Indicators

- [ ] Create large test file (`tests/fixtures/large_file.mmd` with 1000+ events)
- [ ] Manual testing: verify progress bars appear and update smoothly
- [ ] **Success criteria**: Long operations show progress, small files don't clutter output

---

## Stage 4: Helper Commands & Utilities

**Goal**: Add convenience commands for common workflows

### Step 4.1: Implement `ports` Command

- [ ] Create `src/midi_markdown/cli/commands/ports.py`:
  ```python
  """List available MIDI ports."""

  from rich.console import Console
  from rich.table import Table

  from midi_markdown.runtime.midi_io import MIDIOutputManager


  def ports() -> None:
      """List available MIDI input and output ports.

      Useful for finding the correct port name for the play command.

      Examples:
          mmdc ports
      """
      console = Console()
      manager = MIDIOutputManager()

      # Output ports
      output_ports = manager.list_ports()

      if output_ports:
          table = Table(title="MIDI Output Ports", show_header=True)
          table.add_column("Index", style="cyan", justify="right")
          table.add_column("Port Name", style="green")

          for i, port_name in enumerate(output_ports):
              table.add_row(str(i), port_name)

          console.print(table)
      else:
          console.print("[yellow]No MIDI output ports found[/yellow]")
          console.print()
          console.print("[dim]💡 Tip:[/dim]")
          console.print("  macOS: Enable IAC Driver in Audio MIDI Setup")
          console.print("  Linux: Install snd-virmidi or snd-aloop kernel module")
          console.print("  Windows: Install loopMIDI or VirtualMIDI driver")

      # TODO: Add input ports when MIDI input is implemented
  ```
- [ ] Register command in `cli/main.py`
- [ ] Note: `play --list-ports` already exists, but dedicated command is more discoverable

### Step 4.2: Implement `examples` Command

- [ ] Create `src/midi_markdown/cli/commands/examples.py`:
  ```python
  """Show example MMD snippets and usage patterns."""

  from rich.console import Console
  from rich.markdown import Markdown
  from rich.panel import Panel
  from rich.syntax import Syntax


  EXAMPLES = {
      "hello": {
          "title": "Hello World - Simple Note",
          "code": '''---
  title: "Hello MIDI"
  tempo: 120
  ppq: 480
  ---

  [00:00.000]
  - note_on 1.60 80 1b  # Middle C
  ''',
          "description": "Simplest possible MMD file with one note"
      },

      "timing": {
          "title": "Timing Paradigms",
          "code": '''# Absolute time
  [00:00.000]
  - note_on 1.60 80 1b

  # Relative time
  [+1b]
  - note_on 1.64 80 1b

  # Musical time
  [2.1.0]
  - note_on 1.67 80 1b
  ''',
          "description": "Three timing modes: absolute, relative, and musical"
      },

      "cc": {
          "title": "Control Changes",
          "code": '''[00:00.000]
  - cc 1.7.100   # Volume to 100
  - cc 1.10.64   # Pan to center
  - cc 1.11.127  # Expression maximum
  ''',
          "description": "Common MIDI CC messages for automation"
      },

      "loop": {
          "title": "Loop Pattern",
          "code": '''@loop from [00:00.000] to [00:04.000] every 1b
    - note_on 1.60 80 0.5b
  @end
  ''',
          "description": "Repeat a pattern over a time range"
      }
  }


  def examples(
      name: str | None = typer.Argument(None, help="Example name")
  ) -> None:
      """Show example MMD snippets.

      Run without arguments to list all examples.
      Run with example name to see full code.

      Examples:
          mmdc examples          # List all
          mmdc examples hello    # Show hello world
          mmdc examples timing   # Show timing modes
      """
      console = Console()

      if name is None:
          # List all examples
          console.print("[bold cyan]Available Examples:[/bold cyan]\n")

          for key, example in EXAMPLES.items():
              console.print(f"  [green]{key:12}[/green] - {example['title']}")
              console.print(f"               [dim]{example['description']}[/dim]\n")

          console.print("[dim]Run[/dim] [cyan]mmdc examples <name>[/cyan] [dim]to see full code[/dim]")
          return

      # Show specific example
      if name not in EXAMPLES:
          console.print(f"[red]Unknown example:[/red] {name}")
          console.print(f"[dim]Run[/dim] [cyan]mmdc examples[/cyan] [dim]to list all[/dim]")
          raise typer.Exit(1)

      example = EXAMPLES[name]

      console.print(f"\n[bold cyan]{example['title']}[/bold cyan]")
      console.print(f"[dim]{example['description']}[/dim]\n")

      syntax = Syntax(example['code'], "yaml", theme="monokai", line_numbers=True)
      console.print(Panel(syntax, title=f"{name}.mmd", border_style="cyan"))

      console.print("\n[dim]💡 Tip:[/dim] Copy this code to a .mmd file and compile it!")
      console.print(f"[dim]    mmdc compile {name}.mmd[/dim]")
  ```
- [ ] Register command in `cli/main.py`

### Step 4.3: Improve `version` Command

- [ ] Enhance existing `version.py` to show more info:
  ```python
  def version() -> None:
      """Show version and system information."""
      console = Console()

      # Version info
      console.print(f"[bold cyan]MIDI Markdown (MML)[/bold cyan]")
      console.print(f"Version: [green]{__version__}[/green]")
      console.print(f"Python: [dim]{sys.version.split()[0]}[/dim]")
      console.print()

      # Check dependencies
      try:
          import mido
          console.print(f"✓ mido: [dim]{mido.__version__}[/dim]")
      except ImportError:
          console.print("✗ mido: [red]not installed[/red]")

      try:
          import rtmidi
          console.print(f"✓ python-rtmidi: [dim]{rtmidi.__version__}[/dim]")
      except ImportError:
          console.print("✗ python-rtmidi: [red]not installed[/red]")

      console.print()
      console.print("[dim]Project:[/dim] https://github.com/yourusername/midi-markdown")
      console.print("[dim]Docs:[/dim]    https://midi-markdown.readthedocs.io/")
  ```

### Step 4.4: Complete `library` Command

- [ ] Implement `library list` in `cli/commands/library.py`:
  ```python
  def library_list() -> None:
      """List available device libraries."""
      console = Console()

      # Scan devices/ directory
      devices_dir = Path(__file__).parent.parent.parent.parent / "devices"

      if not devices_dir.exists():
          console.print("[yellow]No device libraries found[/yellow]")
          return

      libraries = list(devices_dir.glob("*.mmd"))

      if not libraries:
          console.print("[yellow]No device libraries found[/yellow]")
          return

      table = Table(title="Device Libraries", show_header=True)
      table.add_column("Name", style="cyan")
      table.add_column("File", style="dim")
      table.add_column("Aliases", style="green", justify="right")

      for lib_file in sorted(libraries):
          name = lib_file.stem
          # TODO: Parse file and count aliases
          alias_count = "?"
          table.add_row(name, lib_file.name, alias_count)

      console.print(table)
  ```
- [ ] Implement `library info <name>`
- [ ] Implement `library validate <file>`

### Step 4.5: Test Helper Commands

- [ ] Test `ports` command (mocked MIDI ports)
- [ ] Test `examples` command (list and show)
- [ ] Test enhanced `version` command
- [ ] Test `library` commands
- [ ] **Success criteria**: All helper commands work and provide useful information

---

## Stage 5: Documentation & Help Text

**Goal**: Comprehensive help text, examples, and command documentation

### Step 5.1: Enhance Command Docstrings

- [ ] Review and improve docstrings for all commands:
  - Clear one-line summary
  - Detailed description of behavior
  - Multiple usage examples
  - Note any caveats or requirements
- [ ] Example format:
  ```python
  def compile(...) -> None:
      """Compile MMD file to MIDI format.

      Parses an MMD source file, resolves aliases, validates MIDI commands,
      and generates a standard MIDI file (.mid) or exports to other formats
      (table, CSV, JSON).

      Examples:
          # Basic compilation
          mmdc compile song.mmd

          # Custom output path
          mmdc compile song.mmd -o output/song.mid

          # Export to CSV for analysis
          mmdc compile song.mmd --format csv -o events.csv

          # High-resolution MIDI (960 PPQ)
          mmdc compile song.mmd --ppq 960

          # Verbose output showing all steps
          mmdc compile song.mmd -v

      Format options:
          - midi: Standard MIDI file (default)
          - table: Pretty-printed table in terminal
          - csv: midicsv-compatible CSV format
          - json: Complete MIDI event data
          - json-simple: Simplified JSON for music analysis
      """
  ```

### Step 5.2: Add Command Grouping (Optional)

- [ ] Consider organizing commands in logical groups:
  - **File Operations**: compile, validate, check, inspect
  - **Live Performance**: play, repl
  - **Utilities**: version, ports, examples, library
- [ ] Typer supports command groups with `Typer(rich_markup_mode="rich")`
- [ ] May require refactoring `main.py` structure

### Step 5.3: Create CLI Cheat Sheet

- [ ] Add `mmdc cheatsheet` command (or `--help-cheatsheet`):
  ```python
  @app.command()
  def cheatsheet() -> None:
      """Show quick reference of common commands."""
      console = Console()

      markdown_content = '''
  # MMD CLI Cheat Sheet

  ## Compilation
  ```bash
  mmdc compile song.mmd              # Compile to MIDI
  mmdc compile song.mmd --format csv # Export to CSV
  mmdc validate song.mmd             # Check validity
  mmdc check song.mmd                # Syntax only (fast)
  ```

  ## Playback
  ```bash
  mmdc play song.mmd --port 0        # Play with TUI
  mmdc play song.mmd --no-ui         # Simple playback
  mmdc ports                         # List MIDI ports
  ```

  ## Development
  ```bash
  mmdc repl                          # Interactive REPL
  mmdc inspect song.mmd              # View events
  mmdc examples                      # Show examples
  ```

  ## Help
  ```bash
  mmdc --help                        # General help
  mmdc compile --help                # Command help
  mmdc version                       # Version info
  ```
  '''

      console.print(Markdown(markdown_content))
  ```

### Step 5.4: Update README CLI Section

- [ ] Ensure README.md has comprehensive CLI documentation
- [ ] Add section on error codes and troubleshooting
- [ ] Add section on common workflows

### Step 5.5: Test Help Text

- [ ] Run `mmdc --help` - verify output is clear
- [ ] Run `mmdc <command> --help` for each command
- [ ] Verify examples in docstrings are accurate
- [ ] **Success criteria**: Help text is comprehensive and useful

---

## Stage 6: Integration Testing

**Goal**: Comprehensive testing of all commands and their interactions

### Step 6.1: Create Integration Test Suite

- [ ] Create `tests/integration/test_cli_integration.py`:
  ```python
  """Integration tests for CLI commands."""

  import pytest
  from typer.testing import CliRunner
  from midi_markdown.cli.main import app


  @pytest.mark.integration
  class TestCLIIntegration:
      """Test interactions between CLI commands."""

      def test_compile_then_inspect(self, tmp_path):
          """Test compile followed by inspect on same file."""

      def test_validate_before_compile(self, tmp_path):
          """Test validation catches errors before compilation."""

      def test_check_faster_than_validate(self, tmp_path):
          """Test check command is faster than validate."""

      def test_compile_all_formats(self, tmp_path):
          """Test compilation to all output formats."""

      def test_play_after_compile(self, tmp_path, mock_midi_port):
          """Test play command after successful compilation."""

      def test_version_command(self):
          """Test version command shows version info."""

      def test_ports_command(self, mock_midi_port):
          """Test ports command lists MIDI ports."""

      def test_examples_command(self):
          """Test examples command shows examples."""
  ```

### Step 6.2: Test Error Handling Across Commands

- [ ] Create `tests/integration/test_cli_errors.py`:
  ```python
  """Test error handling in CLI commands."""

  def test_compile_parse_error_exit_code():
      """Test compile with syntax error returns exit code 2."""

  def test_compile_validation_error_exit_code():
      """Test compile with validation error returns exit code 3."""

  def test_play_missing_port_error():
      """Test play with invalid port shows helpful error."""

  def test_debug_flag_shows_traceback():
      """Test --debug flag shows full exception."""

  def test_keyboard_interrupt_cleanup():
      """Test Ctrl+C cleanup in play mode."""
  ```

### Step 6.3: Test Backwards Compatibility

- [ ] Verify existing workflows still work:
  - Basic compile without options
  - Compile with custom output path
  - Validate command
  - Check command
- [ ] Verify output formats haven't changed unexpectedly
- [ ] Verify exit codes are consistent

### Step 6.4: Manual Testing Checklist

- [ ] Test on different terminal sizes
- [ ] Test with different color schemes
- [ ] Test with `NO_COLOR` environment variable
- [ ] Test piping output to file
- [ ] Test running in CI/CD environment (no TTY)

### Step 6.5: Performance Testing

- [ ] Benchmark CLI startup time (should be <0.5s)
- [ ] Benchmark command execution for small files (<1s)
- [ ] Verify progress indicators don't slow down processing
- [ ] **Success criteria**: All integration tests pass, no regressions

---

## Stage 7: Polish & Cleanup

**Goal**: Final refinements and consistency improvements

### Step 7.1: Consistent Output Styling

- [ ] Audit all commands for consistent use of Rich styles:
  - Success messages: `[green]✓[/green]`
  - Errors: `[red]✗[/red]` or `[red]Error:[/red]`
  - Info: `[cyan]...[/cyan]`
  - Warnings: `[yellow]⚠[/yellow]`
  - Hints: `[dim]💡 Tip:[/dim]`

### Step 7.2: Consolidate Console Instances

- [ ] Ensure all commands use consistent Console configuration:
  ```python
  def create_console(no_color: bool = False) -> Console:
      """Create standardized Console instance."""
      return Console(
          color_system="auto" if not no_color else None,
          force_terminal=True if sys.stdout.isatty() else False
      )
  ```
- [ ] Apply to all commands

### Step 7.3: Add Shell Completion (Future)

- [ ] Note: Typer has built-in completion support
- [ ] Document how to enable:
  ```bash
  # Bash
  mmdc --install-completion bash

  # Zsh
  mmdc --install-completion zsh
  ```
- [ ] This is already available with Typer, just document it

### Step 7.4: Create CLI Design Guidelines Document

- [ ] Document CLI conventions for future development:
  - Error message format
  - Progress indicator usage
  - Color scheme
  - Exit codes
  - Debug flag behavior

### Step 7.5: Final Review

- [ ] Run all tests: `pytest`
- [ ] Run all commands manually
- [ ] Review all help text
- [ ] Update CHANGELOG
- [ ] **Success criteria**: CLI is polished, consistent, and well-documented

---

## Validation Checklist

**Before marking Phase 4 complete:**

- [ ] All commands use unified error handler
- [ ] Error messages show source context and suggestions
- [ ] Long operations show progress indicators
- [ ] Helper commands implemented (ports, examples, enhanced version)
- [ ] Library command fully functional
- [ ] All commands have comprehensive help text
- [ ] Integration tests pass (>90% coverage for CLI)
- [ ] Manual testing completed on multiple platforms
- [ ] Documentation updated (README, CLAUDE.md)
- [ ] CLI is consistent, polished, and production-ready

---

## Dependencies

**No new dependencies required** - Phase 4 uses existing infrastructure:
- Typer (already installed)
- Rich (already installed)
- pytest + CliRunner (already in dev dependencies)

---

## Estimated Effort

- **Stage 1** (Unified Error Handling): 6-8 hours
- **Stage 2** (Enhanced Error Formatting): 4-6 hours
- **Stage 3** (Progress Indicators): 3-4 hours
- **Stage 4** (Helper Commands): 4-6 hours
- **Stage 5** (Documentation): 3-4 hours
- **Stage 6** (Integration Testing): 6-8 hours
- **Stage 7** (Polish): 2-3 hours

**Total: 28-39 hours** (approximately 1 week of focused development)

---

## Success Criteria

✅ Phase 4 is complete when:

1. **Error Handling**: All commands use unified error handler with mode-aware behavior
2. **Error Messages**: Errors show source context, highlighting, and suggestions
3. **Progress**: Long operations show progress indicators
4. **Utilities**: Helper commands (ports, examples) are implemented and useful
5. **Documentation**: All commands have comprehensive help text with examples
6. **Testing**: Integration tests achieve >90% CLI coverage
7. **Polish**: CLI is consistent, professional, and production-ready
8. **User Experience**: New users can discover and use all features via help text

---

## Notes for Implementation

- **Preserve existing functionality**: All current commands must continue to work
- **Test frequently**: Run tests after each stage
- **Incremental commits**: Commit after each stage for easy rollback
- **User feedback**: The goal is to make the CLI delightful to use
- **Error messages matter**: Helpful errors save users hours of frustration

---

**Last Updated**: 2025-11-05
