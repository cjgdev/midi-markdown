# Implementation Plan: Adding REPL, Live Playback, and Diagnostics to MMD Compiler

**Target:** Claude Code  
**Context:** Existing MMD compiler with Lark parser, CLI tool, test suite, and MIDI file generation using mido

---

## Phase 0: Architecture Preparation & Refactoring

**Objective:** Restructure existing code to enable sharing between compile/REPL/play modes

### Step 0.1: Analyze Current Architecture
- [ ] Review existing codebase structure and identify:
  - Entry point and CLI command structure
  - Parser implementation and grammar location
  - MIDI generation pipeline (parse → compile → MIDI file)
  - Test organization and coverage areas
  - Current error handling patterns
- [ ] Document the current data flow from MMD source to MIDI file

### Step 0.2: Create Intermediate Representation (IR) Layer
- [ ] Define IR data structures in new `mmlc/core/ir.py`:
  ```python
  from dataclasses import dataclass
  from enum import Enum
  
  class EventType(Enum):
      NOTE_ON = "note_on"
      NOTE_OFF = "note_off"
      CONTROL_CHANGE = "control_change"
      PROGRAM_CHANGE = "program_change"
      TEMPO_CHANGE = "tempo"
  
  @dataclass
  class IREvent:
      tick: int              # Absolute tick position
      time: float            # Absolute time in seconds
      event_type: EventType
      channel: int
      data: dict             # Event-specific data
      track: int = 0
  
  @dataclass
  class IRProgram:
      resolution: int        # PPQN
      initial_tempo: int     # BPM
      events: list[IREvent]
      metadata: dict
  ```

### Step 0.3: Refactor Existing Compiler to Use IR
- [ ] Insert IR generation stage between parsing and MIDI file creation
- [ ] Modify existing MIDI file generator to consume IR instead of AST directly
- [ ] Create `mmlc/core/compiler.py` with `compile_ast_to_ir(ast) -> IRProgram`
- [ ] Create `mmlc/codegen/midi_file.py` with `generate_midi_file(ir_program) -> bytes`
- [ ] Update existing compile command to use new pipeline: `parse → compile_to_ir → generate_midi_file`
- [ ] **Success criteria:** All existing tests pass with refactored architecture

### Step 0.4: Extract Reusable Services
- [ ] Create `mmlc/core/parser.py` wrapper around Lark parser:
  ```python
  class MMLParser:
      def __init__(self, grammar_file: Path):
          self.parser = Lark.open(grammar_file, parser='lalr', 
                                 propagate_positions=True)
      
      def parse(self, text: str):
          """Parse MMD text, raise appropriate exceptions"""
          return self.parser.parse(text)
      
      def parse_interactive(self, text: str):
          """Parse for REPL, handle incomplete input"""
          # Returns InteractiveParser for multi-line handling
  ```
- [ ] Create `mmlc/core/validator.py` for semantic validation (if not already separated)
- [ ] **Success criteria:** Parser and validator can be instantiated and used independently

---

## Phase 1: Diagnostic Output Features

**Objective:** Add table/CSV/JSON export for MIDI events before tackling interactive features

### Step 1.1: Install Rich Library
- [ ] Add `rich>=13.0.0` to `pyproject.toml` dependencies
- [ ] Verify Rich works in current environment with simple test

### Step 1.2: Implement Rich Table Display
- [ ] Create `mmlc/diagnostics/formatter.py`:
  ```python
  from rich.console import Console
  from rich.table import Table
  from mmlc.core.ir import IRProgram, EventType
  
  def display_events_table(ir_program: IRProgram, max_events: int = 100):
      """Display MIDI events as formatted table"""
      console = Console()
      table = Table(title="MIDI Event Timeline", show_header=True)
      
      table.add_column("Time", style="cyan", justify="right")
      table.add_column("Tick", style="blue", justify="right")
      table.add_column("Type", style="magenta")
      table.add_column("Ch", style="green", justify="center")
      table.add_column("Details", style="yellow")
      
      for event in ir_program.events[:max_events]:
          # Format and add rows
      
      console.print(table)
      if len(ir_program.events) > max_events:
          console.print(f"... and {len(ir_program.events) - max_events} more events")
  ```

### Step 1.3: Implement CSV Export (midicsv format)
- [ ] Create `mmlc/codegen/csv_export.py`:
  ```python
  def export_to_csv(ir_program: IRProgram) -> str:
      """Export to midicsv-compatible format"""
      lines = []
      # Track, Time, Type, Channel, Note, Velocity format
      for event in ir_program.events:
          # Convert IREvent to CSV line
      return '\n'.join(lines)
  ```

### Step 1.4: Implement JSON Export
- [ ] Create `mmlc/codegen/json_export.py`:
  ```python
  def export_to_json(ir_program: IRProgram, format: str = 'complete') -> str:
      """
      Export to JSON with two formats:
      - complete: Full MIDI data with exact timing
      - simplified: Normalized for music analysis
      """
  ```

### Step 1.5: Add CLI Commands for Diagnostics
- [ ] Add `--format` option to existing compile command:
  ```python
  @app.command()
  def compile(
      source: Path,
      output: Path = None,
      format: str = typer.Option("midi", help="Output format: midi, table, csv, json")
  ):
      # Parse and compile to IR
      # Based on format, call appropriate export function
  ```
- [ ] Add dedicated `inspect` command:
  ```python
  @app.command()
  def inspect(
      source: Path,
      format: str = typer.Option("table", help="Display format: table, csv, json"),
      limit: int = typer.Option(100, help="Max events to display")
  ):
      """Analyze MMD file and display MIDI events without creating output file"""
  ```

### Step 1.6: Test Diagnostic Features
- [ ] Write tests for table display (capture Rich output)
- [ ] Write tests for CSV export (validate midicsv format)
- [ ] Write tests for JSON export (validate schema)
- [ ] Add integration tests for CLI commands
- [ ] **Success criteria:** Can compile MMD and display/export in all formats

---

## Phase 2: REPL Implementation

**Objective:** Build interactive REPL with line-by-line parsing and graceful error recovery

### Step 2.1: Install prompt_toolkit
- [ ] Add `prompt-toolkit>=3.0.0` to `pyproject.toml` dependencies

### Step 2.2: Create REPL State Management
- [ ] Create `mmlc/runtime/repl.py`:
  ```python
  @dataclass
  class REPLState:
      """Encapsulated REPL state - no globals"""
      variables: dict = field(default_factory=dict)
      aliases: dict = field(default_factory=dict)
      imports: list = field(default_factory=list)
      tempo: int = 120
      resolution: int = 480
      
      def reset(self):
          """Clear all state"""
          self.__init__()
      
      def save_session(self, path: Path):
          """Persist state to file"""
      
      def load_session(self, path: Path):
          """Restore state from file"""
  ```

### Step 2.3: Implement Music-Aware Completer
- [ ] Create completer in `mmlc/runtime/repl.py`:
  ```python
  from prompt_toolkit.completion import Completer, Completion
  
  class MusicCompleter(Completer):
      def __init__(self, state: REPLState):
          self.state = state
      
      def get_completions(self, document, complete_event):
          """Provide context-sensitive completions"""
          word = document.get_word_before_cursor()
          line = document.current_line_before_cursor
          
          # Note names when appropriate context
          # Chord types after "chord"
          # Variable names from state
          # Command names (.load, .save, .help)
  ```

### Step 2.4: Implement Multi-line Input Handling
- [ ] Add incomplete input detection using Lark's `UnexpectedEOF`:
  ```python
  class MMLRepl:
      def __init__(self):
          self.parser = MMLParser(grammar_file)
          self.state = REPLState()
          self.buffer = []
      
      def try_parse(self, text: str):
          """
          Try parsing accumulated input.
          Returns: (success: bool, result_or_error)
          """
          try:
              tree = self.parser.parse(text)
              return True, tree
          except UnexpectedEOF:
              return False, None  # Need more input
          except UnexpectedInput as e:
              return True, e  # Complete but invalid
  ```

### Step 2.5: Implement REPL Evaluation Logic
- [ ] Add evaluation that updates state and shows results:
  ```python
  def evaluate(self, ast):
      """
      Evaluate AST in REPL context:
      - Update state (tempo, variables, aliases)
      - Compile to IR if needed
      - Display results (notes, events, etc.)
      """
      # For definitions: update state
      # For sequences: compile and display summary
      # For queries: show current state
  ```

### Step 2.6: Implement Error Recovery
- [ ] Add graceful error handling for REPL:
  ```python
  def handle_error(self, error: Exception):
      """Display error without crashing REPL"""
      console = Console()
      if isinstance(error, UnexpectedInput):
          # Show syntax error with suggestions
      elif isinstance(error, ValidationError):
          # Show semantic error with hints
      # Always return to prompt, never exit
  ```

### Step 2.7: Create REPL Command Loop
- [ ] Implement main REPL loop:
  ```python
  from prompt_toolkit import PromptSession
  from prompt_toolkit.history import FileHistory
  
  def run_repl(debug: bool = False):
      repl = MMLRepl()
      session = PromptSession(
          history=FileHistory('.mmd_history'),
          completer=repl.completer,
          enable_history_search=True
      )
      
      console = Console()
      console.print("[bold green]MML REPL[/] - Type .help for commands")
      
      while True:
          try:
              prompt_str = 'mml> ' if not repl.buffer else '...  '
              line = session.prompt(prompt_str)
              
              if line.startswith('.'):
                  # Handle meta-commands (.help, .load, .save, .reset)
                  continue
              
              repl.buffer.append(line)
              text = '\n'.join(repl.buffer)
              
              success, result = repl.try_parse(text)
              if success:
                  if isinstance(result, Exception):
                      repl.handle_error(result)
                  else:
                      repl.evaluate(result)
                  repl.buffer = []
              # else: need more input, continue loop
              
          except KeyboardInterrupt:
              repl.buffer = []
              continue
          except EOFError:
              break
  ```

### Step 2.8: Add REPL CLI Command
- [ ] Add REPL command to CLI:
  ```python
  @app.command()
  def repl(
      debug: bool = typer.Option(False, "--debug"),
      session: Path = typer.Option(None, "--load-session")
  ):
      """Start interactive REPL for MMD development"""
      if session and session.exists():
          # Load saved session
      run_repl(debug=debug)
  ```

### Step 2.9: Test REPL Features
- [ ] Install `pexpect` for REPL testing
- [ ] Create tests using `pexpect.replwrap`:
  ```python
  def test_repl_basic_commands():
      repl = replwrap.REPLWrapper(
          cmd_or_spawn="mmlc repl",
          orig_prompt="mml> "
      )
      result = repl.run_command("tempo 140")
      assert "140" in result
  ```
- [ ] Test multi-line input
- [ ] Test error recovery
- [ ] Test state persistence
- [ ] **Success criteria:** REPL accepts input, shows completions, recovers from errors

---

## Phase 3: Real-time MIDI Playback

**Objective:** Add live playback mode with sub-5ms timing precision and live TUI display

### Step 3.1: Install Real-time MIDI Dependencies
- [ ] Add `python-rtmidi>=1.5.0` to `pyproject.toml` 
- [ ] Verify mido detects rtmidi backend: `python -c "import mido; print(mido.backend)"`

### Step 3.2: Implement Event Scheduler
- [ ] Create `mmlc/runtime/scheduler.py`:
  ```python
  import threading
  import queue
  import time
  from dataclasses import dataclass, field
  
  @dataclass(order=True)
  class ScheduledEvent:
      time: float
      message: Any = field(compare=False)
  
  class MIDIScheduler:
      def __init__(self, port_name: str):
          self.port = mido.open_output(port_name)
          self.event_queue = queue.PriorityQueue()
          self.running = False
          self.paused = False
          self.thread = None
          self.start_time = None
          self.pause_offset = 0.0
      
      def start(self):
          """Start scheduler thread"""
          self.running = True
          self.start_time = time.perf_counter()
          self.thread = threading.Thread(target=self._run, daemon=True)
          self.thread.start()
      
      def _run(self):
          """Scheduler loop with hybrid sleep + busy-wait"""
          while self.running:
              try:
                  event = self.event_queue.get(timeout=0.1)
                  
                  # Wait until event time
                  target_time = event.time + self.pause_offset
                  sleep_time = target_time - time.perf_counter()
                  
                  if sleep_time > 0.002:
                      time.sleep(sleep_time * 0.9)  # Sleep 90%
                  
                  while time.perf_counter() < target_time:
                      pass  # Busy-wait for precision
                  
                  if not self.paused:
                      self.port.send(event.message)
                      
              except queue.Empty:
                  continue
      
      def schedule(self, message, delay: float):
          """Schedule message for future delivery"""
          scheduled_time = time.perf_counter() + delay
          self.event_queue.put(ScheduledEvent(scheduled_time, message))
      
      def stop(self):
          """Stop playback and send all-notes-off"""
          self.running = False
          if self.thread:
              self.thread.join(timeout=1.0)
          self._send_panic()
      
      def _send_panic(self):
          """Send all-notes-off on all channels"""
          for channel in range(16):
              self.port.send(mido.Message('control_change', 
                                         channel=channel, 
                                         control=123, 
                                         value=0))
  ```

### Step 3.3: Implement Tempo Tracker
- [ ] Add tempo tracking to scheduler:
  ```python
  class TempoTracker:
      def __init__(self, initial_tempo: int, resolution: int):
          self.tempo = initial_tempo
          self.resolution = resolution  # PPQN
          self.tempo_changes = []  # List of (tick, tempo)
      
      def add_tempo_change(self, tick: int, new_tempo: int):
          """Record tempo change at specific tick"""
          self.tempo_changes.append((tick, new_tempo))
          self.tempo_changes.sort()
      
      def ticks_to_seconds(self, tick: int) -> float:
          """Convert absolute tick to seconds accounting for tempo changes"""
          # Calculate time with tempo changes
  ```

### Step 3.4: Create Real-time Player
- [ ] Create `mmlc/runtime/player.py`:
  ```python
  class RealtimePlayer:
      def __init__(self, port_name: str = None, show_display: bool = True):
          if port_name is None:
              # Auto-select first available port
              ports = mido.get_output_names()
              if not ports:
                  raise RuntimeError("No MIDI output ports available")
              port_name = ports[0]
          
          self.scheduler = MIDIScheduler(port_name)
          self.tempo_tracker = None
          self.show_display = show_display
          self.live_display = None
      
      def play(self, ir_program: IRProgram):
          """Play IR program in real-time"""
          self.tempo_tracker = TempoTracker(
              ir_program.initial_tempo,
              ir_program.resolution
          )
          
          # Pre-calculate all timing
          scheduled_events = []
          for ir_event in ir_program.events:
              midi_msg = self._ir_to_midi_message(ir_event)
              delay = ir_event.time  # Already calculated in IR
              scheduled_events.append((delay, midi_msg))
          
          # Start playback
          self.scheduler.start()
          
          # Schedule all events
          base_time = time.perf_counter()
          for delay, msg in scheduled_events:
              self.scheduler.schedule(msg, delay)
          
          # Wait for completion
          max_time = max(delay for delay, _ in scheduled_events)
          time.sleep(max_time + 1.0)
          
          self.scheduler.stop()
      
      def _ir_to_midi_message(self, ir_event: IREvent):
          """Convert IREvent to mido.Message"""
          if ir_event.event_type == EventType.NOTE_ON:
              return mido.Message('note_on', 
                                 channel=ir_event.channel,
                                 note=ir_event.data['note'],
                                 velocity=ir_event.data['velocity'])
          # Handle other event types
  ```

### Step 3.5: Implement Pre-validation
- [ ] Add validation phase before playback:
  ```python
  def validate_for_playback(ir_program: IRProgram) -> list[str]:
      """
      Comprehensive validation before playback.
      Returns list of errors, empty if valid.
      """
      errors = []
      
      # Check for overlapping notes (same note/channel)
      # Validate MIDI value ranges
      # Check for extremely short/long events
      # Verify tempo changes are sensible
      
      return errors
  ```

### Step 3.6: Add Playback Controls
- [ ] Implement pause/resume/stop:
  ```python
  class RealtimePlayer:
      def pause(self):
          self.scheduler.paused = True
          self.pause_start = time.perf_counter()
      
      def resume(self):
          pause_duration = time.perf_counter() - self.pause_start
          self.scheduler.pause_offset += pause_duration
          self.scheduler.paused = False
      
      def stop(self):
          self.scheduler.stop()
  ```

### Step 3.7: Add Play CLI Command
- [ ] Add play command:
  ```python
  @app.command()
  def play(
      source: Path,
      port: str = typer.Option(None, "--port", "-p", 
                               help="MIDI output port name"),
      tempo: int = typer.Option(None, "--tempo", "-t",
                               help="Override tempo (BPM)"),
      dry_run: bool = typer.Option(False, "--dry-run",
                                   help="Validate without playing"),
      no_display: bool = typer.Option(False, "--no-display",
                                      help="Disable live TUI display"),
      window_size: int = typer.Option(7, "--window-size",
                                     help="Number of events visible in display")
  ):
      """Play MMD file in real-time"""
      console = Console()
      
      # Parse and compile
      with console.status("[blue]Compiling MML...[/]"):
          ir_program = compile_mml_file(source)
      
      if tempo:
          ir_program.initial_tempo = tempo
      
      # Pre-validate
      errors = validate_for_playback(ir_program)
      if errors:
          for error in errors:
              console.print(f"[red]Error:[/] {error}")
          raise typer.Exit(1)
      
      if dry_run:
          console.print("[green]✓[/] Validation passed, ready to play")
          display_events_table(ir_program, max_events=20)
          return
      
      # List available ports
      if not port:
          ports = mido.get_output_names()
          console.print(f"Available MIDI ports: {', '.join(ports)}")
          port = ports[0] if ports else None
      
      # Play with or without display
      player = RealtimePlayer(port, show_display=not no_display)
      
      if no_display:
          console.print(f"[green]▶[/] Playing on port: {port}")
          with console.status("[blue]Playing...[/]"):
              player.play(ir_program)
          console.print("[green]✓[/] Playback complete")
      else:
          # Display handles all output
          player.play(ir_program)
  ```

### Step 3.8: Test Playback Features
- [ ] Create mock MIDI port for testing:
  ```python
  class RecordingMidiPort:
      def __init__(self):
          self.messages = []
          self.start_time = time.perf_counter()
      
      def send(self, message):
          elapsed = time.perf_counter() - self.start_time
          self.messages.append({
              'time': elapsed,
              'message': message
          })
  ```
- [ ] Test scheduler timing accuracy
- [ ] Test tempo changes
- [ ] Test panic/emergency stop
- [ ] Test pre-validation catches errors

### Step 3.9: Implement Live Playback TUI (Text User Interface)

**Objective:** Create a non-scrolling, updating display that shows playback progress like a graphical interface

#### Step 3.9.1: Design TUI Layout Structure

Create a fixed-viewport display with:
- **Top border:** Column headers (Time, Type, Channel, Details)
- **Bottom border:** Playback metadata (PPQ, Tempo, Position in bars.beats.ticks, Position in seconds)
- **Content area:** Scrolling event list with current event highlighted
- **Visual hierarchy:** Past events dimmed, current event highlighted in box, upcoming events dimmed

```
┌┐Time┌───┬┐Type┌───┬┐Ch┌┬┐Details┌─────────────┐
│ 1.2.240 │ note_on │ 1  │ C4 vel:100          │ (dimmed)
│ 1.3.000 │ note_off│ 1  │ C4 vel:64           │ (dimmed)
├─────────┴─────────┴────┴──────────────────────┤
│▶2.1.000 │ note_on │ 1  │ D4 vel:105          │◀ (highlighted/boxed)
├─────────┬─────────┬────┬──────────────────────┤
│ 2.1.240 │ note_off│ 1  │ D4 vel:64           │ (dimmed)
│ 2.2.000 │ cc      │ 1  │ CC#7 val:80         │ (dimmed)
└─────────┴─────────┴────┴──────────────────────┘
 PPQ: 480 | Tempo: 120 BPM | 2.1.000 | 00:04.125s
```

#### Step 3.9.2: Install Rich Live Display Dependencies

Rich's `Live` class provides the updating display capability. Verify it's already available with Rich installation.

#### Step 3.9.3: Create Live Display Manager

- [ ] Create `mmlc/runtime/live_display.py`:
  ```python
  from rich.live import Live
  from rich.table import Table
  from rich.console import Console
  from rich.panel import Panel
  from rich.text import Text
  from rich.box import ROUNDED
  from dataclasses import dataclass
  import time
  
  @dataclass
  class PlaybackState:
      """Current playback state for display"""
      current_tick: int = 0
      current_time: float = 0.0
      current_bar: int = 1
      current_beat: int = 1
      current_tick_in_beat: int = 0
      current_tempo: int = 120
      ppqn: int = 480
      current_event_index: int = 0
  
  class LivePlaybackDisplay:
      """
      Non-scrolling TUI that updates in place during playback.
      Shows current event highlighted with past/future events dimmed.
      """
      
      def __init__(self, ir_program, window_size: int = 7):
          """
          Args:
              ir_program: IRProgram to display
              window_size: Number of events visible at once (odd recommended)
          """
          self.ir_program = ir_program
          self.window_size = window_size
          self.half_window = window_size // 2
          
          self.state = PlaybackState(
              ppqn=ir_program.resolution,
              current_tempo=ir_program.initial_tempo
          )
          
          self.console = Console()
          self.live = None
          self.running = False
          
          # Detect terminal capabilities
          if not self.console.is_terminal:
              self.use_simple_mode = True
          else:
              self.use_simple_mode = False
              try:
                  width, height = self.console.size
                  if height < 15 or width < 60:
                      self.console.print("[yellow]Warning: Terminal too small[/]")
                      self.window_size = min(window_size, max(3, height - 8))
              except:
                  self.use_simple_mode = True
      
      def start(self):
          """Start the live display"""
          if self.use_simple_mode:
              return
          
          self.running = True
          self.live = Live(
              self._render_display(),
              console=self.console,
              refresh_per_second=30,  # 30 FPS
              screen=False
          )
          self.live.start()
          
      def stop(self):
          """Stop the live display"""
          self.running = False
          if self.live:
              self.live.stop()
      
      def update_state(self, 
                      current_tick: int,
                      current_time: float,
                      current_event_index: int,
                      current_tempo: int = None):
          """Update playback state (called from player thread)"""
          self.state.current_tick = current_tick
          self.state.current_time = current_time
          self.state.current_event_index = current_event_index
          
          if current_tempo is not None:
              self.state.current_tempo = current_tempo
          
          # Calculate bars.beats.ticks
          self._calculate_musical_time()
          
          # Update display
          if self.live:
              self.live.update(self._render_display())
      
      def _calculate_musical_time(self):
          """Convert absolute tick to bars.beats.ticks"""
          beats_per_bar = 4  # TODO: Handle time signature changes
          ticks_per_beat = self.state.ppqn
          
          total_beats = self.state.current_tick // ticks_per_beat
          tick_in_beat = self.state.current_tick % ticks_per_beat
          
          bar = (total_beats // beats_per_bar) + 1
          beat = (total_beats % beats_per_bar) + 1
          
          self.state.current_bar = bar
          self.state.current_beat = beat
          self.state.current_tick_in_beat = tick_in_beat
      
      def _render_display(self) -> Panel:
          """Render the complete display"""
          table = Table(
              show_header=True,
              header_style="bold cyan",
              box=ROUNDED,
              expand=True,
              show_edge=True
          )
          
          # Add columns
          table.add_column("Time", style="cyan", width=12, justify="right")
          table.add_column("Type", style="magenta", width=12)
          table.add_column("Ch", style="green", width=4, justify="center")
          table.add_column("Details", style="yellow", width=30)
          
          # Calculate visible event range
          current_idx = self.state.current_event_index
          start_idx = max(0, current_idx - self.half_window)
          end_idx = min(len(self.ir_program.events), 
                       current_idx + self.half_window + 1)
          
          # Add events to table
          for idx in range(start_idx, end_idx):
              event = self.ir_program.events[idx]
              
              musical_time = self._format_musical_time(event.tick)
              event_type = event.event_type.value
              channel = str(event.channel)
              details = self._format_event_details(event)
              
              # Style based on position
              if idx == current_idx:
                  # Current: highlighted with box
                  style = "bold white on blue"
                  time_text = Text(f"▶ {musical_time}", style=style)
                  type_text = Text(event_type, style=style)
                  ch_text = Text(channel, style=style)
                  det_text = Text(details, style=style)
              else:
                  # Past/future: dimmed
                  style = "dim"
                  time_text = Text(f"  {musical_time}", style=style)
                  type_text = Text(event_type, style=style)
                  ch_text = Text(channel, style=style)
                  det_text = Text(details, style=style)
              
              table.add_row(time_text, type_text, ch_text, det_text)
          
          # Create footer
          footer = self._create_footer()
          
          # Wrap in panel
          panel = Panel(
              table,
              title="[bold green]♪ Live Playback[/]",
              subtitle=footer,
              border_style="green",
              expand=True
          )
          
          return panel
      
      def _format_musical_time(self, tick: int) -> str:
          """Format tick as bars.beats.ticks"""
          ticks_per_beat = self.state.ppqn
          beats_per_bar = 4
          
          total_beats = tick // ticks_per_beat
          tick_in_beat = tick % ticks_per_beat
          
          bar = (total_beats // beats_per_bar) + 1
          beat = (total_beats % beats_per_bar) + 1
          
          return f"{bar}.{beat}.{tick_in_beat:03d}"
      
      def _format_event_details(self, event) -> str:
          """Format event-specific details"""
          if event.event_type.value == "note_on":
              note = event.data.get('note', '?')
              velocity = event.data.get('velocity', '?')
              return f"Note {note} vel:{velocity}"
          elif event.event_type.value == "note_off":
              note = event.data.get('note', '?')
              velocity = event.data.get('velocity', '?')
              return f"Note {note} vel:{velocity}"
          elif event.event_type.value == "control_change":
              cc = event.data.get('control', '?')
              value = event.data.get('value', '?')
              return f"CC#{cc} val:{value}"
          elif event.event_type.value == "program_change":
              program = event.data.get('program', '?')
              return f"Program {program}"
          elif event.event_type.value == "tempo":
              tempo = event.data.get('tempo', '?')
              return f"{tempo} BPM"
          else:
              return str(event.data)
      
      def _create_footer(self) -> str:
          """Create footer with playback metadata"""
          musical_pos = (f"{self.state.current_bar}."
                        f"{self.state.current_beat}."
                        f"{self.state.current_tick_in_beat:03d}")
          
          time_pos = f"{self.state.current_time:07.3f}s"
          
          footer = (f"PPQ: {self.state.ppqn} | "
                   f"Tempo: {self.state.current_tempo} BPM | "
                   f"{musical_pos} | "
                   f"{time_pos}")
          
          return footer
  ```

#### Step 3.9.4: Integrate Live Display with RealtimePlayer

- [ ] Modify `mmlc/runtime/player.py` to use live display:
  ```python
  class RealtimePlayer:
      def play(self, ir_program: IRProgram):
          """Play IR program with live TUI"""
          
          # Initialize display
          if self.show_display:
              self.live_display = LivePlaybackDisplay(
                  ir_program,
                  window_size=7
              )
              self.live_display.start()
          
          try:
              # ... existing playback code ...
              
              # Schedule events with display updates
              for delay, msg, ir_event, idx in scheduled_events:
                  self.scheduler.schedule(msg, delay)
                  
                  # Update display 50ms before event
                  if self.live_display:
                      display_delay = max(0, delay - 0.05)
                      self.scheduler.schedule_callback(
                          display_delay,
                          self._update_display,
                          ir_event.tick,
                          ir_event.time,
                          idx,
                          self._get_current_tempo(ir_event.tick)
                      )
              
              # Wait for completion
              max_time = max(delay for delay, _, _, _ in scheduled_events)
              time.sleep(max_time + 1.0)
              
          finally:
              if self.live_display:
                  self.live_display.stop()
              self.scheduler.stop()
      
      def _update_display(self, tick, time_sec, event_idx, tempo):
          """Callback to update display"""
          if self.live_display:
              self.live_display.update_state(tick, time_sec, event_idx, tempo)
  ```

#### Step 3.9.5: Enhance Scheduler for Display Callbacks

- [ ] Modify `mmlc/runtime/scheduler.py` to support callbacks:
  ```python
  @dataclass(order=True)
  class ScheduledCallback:
      time: float
      callback: Any = field(compare=False)
      args: tuple = field(default_factory=tuple, compare=False)
  
  class MIDIScheduler:
      def schedule_callback(self, delay: float, callback, *args):
          """Schedule callback for future execution"""
          scheduled_time = time.perf_counter() + delay
          event = ScheduledCallback(scheduled_time, callback, args)
          self.event_queue.put(event)
      
      def _run(self):
          """Enhanced loop handling MIDI and callbacks"""
          while self.running:
              try:
                  event = self.event_queue.get(timeout=0.1)
                  
                  # Wait until event time
                  target_time = event.time + self.pause_offset
                  sleep_time = target_time - time.perf_counter()
                  
                  if sleep_time > 0.002:
                      time.sleep(sleep_time * 0.9)
                  
                  while time.perf_counter() < target_time:
                      pass
                  
                  if not self.paused:
                      if isinstance(event, ScheduledCallback):
                          event.callback(*event.args)
                      else:
                          self.port.send(event.message)
                          
              except queue.Empty:
                  continue
  ```

#### Step 3.9.6: Test Live Display

- [ ] Add tests for live display:
  ```python
  def test_live_display_rendering():
      """Test display renders without crashing"""
      ir_program = create_test_ir_program()
      display = LivePlaybackDisplay(ir_program, window_size=5)
      
      display.update_state(0, 0.0, 0)
      output = display._render_display()
      assert output is not None
      
      display.update_state(480, 1.0, 5)
      output = display._render_display()
      assert output is not None
  
  def test_musical_time_formatting():
      """Test bars.beats.ticks calculation"""
      display = LivePlaybackDisplay(create_test_ir_program())
      
      assert display._format_musical_time(0) == "1.1.000"
      assert display._format_musical_time(480) == "1.2.000"
      assert display._format_musical_time(1920) == "2.1.000"
  
  def test_display_fallback_non_terminal():
      """Test graceful handling of non-terminal"""
      ir_program = create_test_ir_program()
      display = LivePlaybackDisplay(ir_program)
      
      display.start()
      display.stop()  # Should not crash
  ```

- [ ] **Success criteria:** Can play MMD with live TUI showing:
  - Non-scrolling, updating interface
  - Current event highlighted in box
  - Past and future events dimmed
  - Column headers in top border
  - Playback metadata (PPQ, Tempo, bars.beats.ticks, seconds) in bottom border
  - Smooth 30 FPS updates
  - Graceful fallback for non-terminal environments

---

## Phase 4: CLI Refinement & Integration

**Objective:** Polish CLI experience and ensure all modes work seamlessly

### Step 4.1: Migrate to Typer (if not already using)
- [ ] If current CLI uses Click or argparse, migrate to Typer
- [ ] Organize commands in logical groups
- [ ] Add rich help text and examples

### Step 4.2: Implement Unified Error Handling
- [ ] Create error handling context manager:
  ```python
  from contextlib import contextmanager
  
  @contextmanager
  def mode_error_handler(mode: str, debug: bool = False):
      """Context manager for mode-appropriate error handling"""
      try:
          yield
      except KeyboardInterrupt:
          console.print("\n[yellow]Cancelled[/]")
          if mode == 'play':
              # Send MIDI panic
          sys.exit(130)
      except ParseError as e:
          format_parse_error(e)
          sys.exit(10 if mode == 'compile' else 0)
      # Handle other error types
  ```

### Step 4.3: Add Progress Indicators
- [ ] Use Rich progress bars for long operations:
  ```python
  from rich.progress import track
  
  for event in track(ir_program.events, description="Generating MIDI..."):
      # Process event
  ```

### Step 4.4: Improve Error Messages
- [ ] Enhance error formatting with Rich:
  ```python
  def format_compiler_error(error, source_text):
      console = Console()
      
      # Show source context with line numbers
      # Point to error location with ^
      # Provide suggestion if available
      # Add "help: run 'mmlc explain E001' for more info"
  ```

### Step 4.5: Add Version and Info Commands
- [ ] Add metadata commands:
  ```python
  @app.command()
  def version():
      """Show version information"""
  
  @app.command()
  def ports():
      """List available MIDI ports"""
  
  @app.command()
  def examples():
      """Show example MMD snippets"""
  ```

### Step 4.6: Document All Commands
- [ ] Add comprehensive docstrings
- [ ] Create examples in help text
- [ ] Write user guide in README

### Step 4.7: Integration Testing
- [ ] Test all command combinations
- [ ] Test error handling in each mode
- [ ] Test output formats work together
- [ ] Verify backwards compatibility with existing usage
- [ ] **Success criteria:** All commands work, help is clear, errors are helpful

---

## Phase 5: Testing & Documentation

**Objective:** Ensure reliability and usability

### Step 5.1: Expand Test Coverage
- [ ] Add tests for IR layer
- [ ] Add tests for each export format
- [ ] Add integration tests for each command
- [ ] Add performance tests for scheduler timing
- [ ] Aim for >80% code coverage

### Step 5.2: Create Example Files
- [ ] Create `examples/` directory with:
  - `basic.mmd` - Simple melody
  - `tempo_changes.mmd` - Variable tempo
  - `multi_channel.mmd` - Multiple instruments
  - `repl_session.txt` - Example REPL interaction
  - `device_profiles/` - Example device libraries

### Step 5.3: Write User Documentation
- [ ] Update README with:
  - Installation instructions (including rtmidi setup)
  - Quick start guide
  - Command reference
  - REPL usage guide
  - Live playback guide with screenshots
  - Troubleshooting section
- [ ] Create `docs/` directory with:
  - Architecture overview
  - IR specification
  - Export format specifications
  - Contributing guide

### Step 5.4: Performance Benchmarking
- [ ] Create benchmark suite:
  ```python
  def benchmark_compile_speed():
      # Measure parse → IR → MIDI time
  
  def benchmark_scheduler_latency():
      # Measure actual vs expected timing
  
  def benchmark_display_refresh():
      # Measure TUI update performance
  ```
- [ ] Document performance characteristics

### Step 5.5: Create Migration Guide
- [ ] Document changes from old to new architecture
- [ ] Show before/after examples
- [ ] Explain breaking changes (if any)

---

## Phase 6: Polish & Release Preparation

### Step 6.1: Add Configuration File Support
- [ ] Support `mml.toml` or `.mmdrc`:
  ```toml
  [midi]
  default_port = "IAC Driver Bus 1"
  ppqn = 480
  
  [repl]
  history_size = 1000
  auto_save_session = true
  
  [playback]
  latency_compensation = 0.005
  display_window_size = 7
  ```

### Step 6.2: Add Shell Completion
- [ ] Generate completions for bash/zsh/fish
- [ ] Add installation instructions to docs

### Step 6.3: Optimize Performance
- [ ] Profile critical paths
- [ ] Optimize IR generation if needed
- [ ] Reduce import time for CLI responsiveness
- [ ] Optimize display refresh for large event counts

### Step 6.4: Final Testing
- [ ] Test on multiple platforms (Linux, macOS, Windows)
- [ ] Test with different MIDI devices
- [ ] Test with large MMD files
- [ ] Stress test REPL with long sessions
- [ ] Test live display in various terminal sizes
- [ ] Verify no memory leaks in long-running processes

### Step 6.5: Create Release Checklist
- [ ] Version bump
- [ ] Changelog
- [ ] Tag release
- [ ] Build distributions
- [ ] Test installation from PyPI

---

## Success Criteria Summary

**Compile Mode:**
- ✓ Parse MMD to IR to MIDI file
- ✓ Export to table/CSV/JSON formats
- ✓ Comprehensive error messages
- ✓ All existing tests pass

**REPL Mode:**
- ✓ Interactive prompt with history
- ✓ Auto-completion for notes/chords/commands
- ✓ Multi-line input support
- ✓ Graceful error recovery
- ✓ Session save/load

**Play Mode:**
- ✓ Real-time MIDI output with <5ms latency
- ✓ Pre-validation before playback
- ✓ Tempo changes handled correctly
- ✓ Stop/panic works reliably
- ✓ Works with hardware and software MIDI ports
- ✓ **Live TUI display with:**
  - **Non-scrolling, updating interface**
  - **Current event highlighted in box**
  - **Past and future events dimmed**
  - **Column headers in top border**
  - **Playback metadata (PPQ, Tempo, bars.beats.ticks, seconds) in bottom border**
  - **Smooth 30 FPS updates**
  - **Graceful fallback for non-terminal environments**

**Overall:**
- ✓ 80%+ shared code between modes
- ✓ Mode-specific error handling
- ✓ Professional CLI with Typer + Rich
- ✓ Comprehensive documentation
- ✓ >80% test coverage

---

## CLI Usage Examples

**Compile Mode:**
```bash
# Standard MIDI file compilation
mmlc compile song.mmd

# Export to different formats
mmlc compile song.mmd --format csv
mmlc compile song.mmd --format json
mmlc compile song.mmd --format table

# Inspect without creating output
mmlc inspect song.mmd
mmlc inspect song.mmd --limit 50
```

**REPL Mode:**
```bash
# Start interactive session
mmlc repl

# Load previous session
mmlc repl --load-session last.pkl

# Debug mode
mmlc repl --debug
```

**Play Mode:**
```bash
# Play with default live display
mmlc play song.mmd

# Play with custom window size
mmlc play song.mmd --window-size 11

# Play without live display
mmlc play song.mmd --no-display

# Dry run validation
mmlc play song.mmd --dry-run

# Specific MIDI port and tempo override
mmlc play song.mmd --port "IAC Driver" --tempo 140
```

---

## Implementation Notes for Claude Code

1. **Preserve existing functionality:** All changes must maintain backward compatibility. Existing compile behavior must work exactly as before.

2. **Test after each phase:** Run the full test suite after completing each phase. Fix any regressions immediately.

3. **Reference project files:** Use `view` tool to examine existing code before modifying. Understand current patterns and match coding style.

4. **Incremental commits:** Make logical commits after each step. This enables easy rollback if needed.

5. **Use existing patterns:** If the codebase has established patterns for error handling, logging, or testing, follow them.

6. **Dependencies:** Check if any required libraries are already installed before adding new dependencies.

7. **Platform compatibility:** Test MIDI functionality on the development platform. Note any platform-specific considerations in documentation.

8. **Terminal compatibility:** The live TUI display uses Rich's Live feature. Test in different terminal emulators and ensure graceful fallback for non-terminal environments (pipes, CI/CD).

9. **Ask for clarification:** If existing code structure is unclear or conflicts with this plan, ask before proceeding.