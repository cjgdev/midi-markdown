# Phase 5: Testing & Documentation - Detailed Implementation Plan

**Status**: Not yet implemented
**Objective**: Ensure reliability, maintainability, and usability through comprehensive testing and documentation
**Context**: Phases 0-4 complete (IR layer, diagnostics, REPL, real-time playback, CLI refinement)

---

## Current State Assessment

**What's Already Done** (Per CLAUDE.md and implementation status):
- ✅ **Test Coverage**: 1328+ tests, 72.53% code coverage
  - 1090+ unit tests across 31 test files
  - 238 integration tests (14 files)
  - 37 test fixtures (25 valid + 12 invalid MMD files)
- ✅ **Documentation**: Substantial documentation exists
  - README.md - Comprehensive project README
  - CLAUDE.md - Project instructions
  - spec.md - Complete MMD specification (1300+ lines)
  - docs/cli_design_guidelines.md - CLI standards (717 lines)
  - docs/alias_system_guide.md, device_library_creation.md, alias_api_reference.md
  - Phase progress trackers for Stages 3-7
- ✅ **Examples**: 16 runnable examples + README in examples/
- ✅ **Device Libraries**: 6 MIDI device libraries in devices/

**What Needs Work**:
- ⚠️ **Coverage gaps** in specific areas (parser 75.81%, some codegen modules)
- ⚠️ **Performance benchmarking** not formalized
- ⚠️ **User documentation** scattered, needs centralization
- ⚠️ **API documentation** not generated
- ⚠️ **Tutorial content** minimal
- ⚠️ **Video/screenshot documentation** missing for TUI features

---

## Stage 1: Test Coverage Enhancement

**Goal**: Achieve 85%+ code coverage and fill critical testing gaps

### Step 1.1: Analyze Coverage Gaps

- [ ] Run coverage report with details:
  ```bash
  uv run pytest --cov=src/midi_markdown --cov-report=html --cov-report=term-missing
  ```
- [ ] Identify modules below 80% coverage:
  - Current known gaps: parser (75.81%), some codegen modules
- [ ] Prioritize critical paths:
  - Parser edge cases (incomplete input, malformed syntax)
  - IR compiler (all MIDI command types)
  - Real-time scheduler (timing accuracy, edge cases)
  - Error handler (all error types, all modes)
  - TUI display (state management, rendering)
- [ ] Document coverage goals for each module

### Step 1.2: Enhance Parser Test Coverage

**Current**: Parser at 75.81% coverage

- [ ] Test incomplete input handling:
  ```python
  def test_parser_incomplete_frontmatter():
      """Test parser with incomplete YAML frontmatter"""

  def test_parser_incomplete_timing_marker():
      """Test parser with incomplete timing markers"""

  def test_parser_incomplete_alias_block():
      """Test parser with unclosed @alias blocks"""
  ```

- [ ] Test error recovery:
  ```python
  def test_parser_recoverable_syntax_errors():
      """Test parser gracefully handles recoverable errors"""

  def test_parser_multiple_errors_in_document():
      """Test parser reports multiple errors in one pass"""
  ```

- [ ] Test edge cases:
  ```python
  def test_parser_empty_file():
      """Test parser with completely empty file"""

  def test_parser_only_comments():
      """Test parser with file containing only comments"""

  def test_parser_unicode_characters():
      """Test parser handles Unicode in comments and strings"""

  def test_parser_very_long_lines():
      """Test parser with extremely long lines (>10000 chars)"""
  ```

- [ ] Test `parse_interactive()` for REPL:
  ```python
  def test_parser_interactive_multiline():
      """Test interactive parser accumulates multi-line input"""

  def test_parser_interactive_incomplete_detection():
      """Test interactive parser detects incomplete input"""
  ```

- [ ] **Success criteria**: Parser coverage >85%

### Step 1.3: Enhance IR Compiler Test Coverage

- [ ] Test all MIDI command types:
  ```python
  def test_ir_compile_note_commands():
      """Test note_on, note_off, auto note_off"""

  def test_ir_compile_control_change():
      """Test CC commands with all CC numbers"""

  def test_ir_compile_program_change():
      """Test PC commands with all program numbers"""

  def test_ir_compile_pitch_bend():
      """Test pitch bend with full range (-8192 to +8191)"""

  def test_ir_compile_channel_pressure():
      """Test channel pressure (aftertouch)"""

  def test_ir_compile_poly_pressure():
      """Test polyphonic pressure"""

  def test_ir_compile_tempo_changes():
      """Test tempo change events"""

  def test_ir_compile_time_signature():
      """Test time signature changes"""

  def test_ir_compile_key_signature():
      """Test key signature changes"""

  def test_ir_compile_markers():
      """Test marker and text events"""

  def test_ir_compile_sysex():
      """Test system exclusive messages"""
  ```

- [ ] Test timing conversions:
  ```python
  def test_ir_timing_absolute_to_ticks():
      """Test absolute time (mm:ss.ms) to tick conversion"""

  def test_ir_timing_musical_to_ticks():
      """Test musical time (bars.beats.ticks) to absolute ticks"""

  def test_ir_timing_relative_to_ticks():
      """Test relative time (+delta) to absolute ticks"""

  def test_ir_timing_simultaneous():
      """Test simultaneous timing ([@]) uses previous event time"""

  def test_ir_timing_with_tempo_changes():
      """Test tick-to-time conversion with tempo changes"""
  ```

- [ ] Test multi-track compilation:
  ```python
  def test_ir_compile_multi_track():
      """Test multi-track MMD compiles to separate IR tracks"""

  def test_ir_compile_track_merging():
      """Test merging tracks into single track"""
  ```

- [ ] **Success criteria**: IR compiler coverage >90%

### Step 1.4: Enhance Runtime Test Coverage

**Focus**: Real-time playback components

- [ ] Test MIDI I/O:
  ```python
  def test_midi_output_manager_list_ports():
      """Test listing MIDI output ports"""

  def test_midi_output_manager_open_port():
      """Test opening MIDI output port"""

  def test_midi_output_manager_send_message():
      """Test sending MIDI message"""

  def test_midi_output_manager_error_handling():
      """Test error handling for missing ports"""
  ```

- [ ] Test scheduler timing:
  ```python
  def test_scheduler_timing_accuracy():
      """Test scheduler delivers messages within 5ms window"""

  def test_scheduler_pause_resume():
      """Test pause/resume correctly adjusts timing"""

  def test_scheduler_stop_panic():
      """Test stop sends all-notes-off on all channels"""

  def test_scheduler_high_event_density():
      """Test scheduler handles >100 events/second"""
  ```

- [ ] Test tempo tracker:
  ```python
  def test_tempo_tracker_constant_tempo():
      """Test tempo tracker with constant tempo"""

  def test_tempo_tracker_tempo_changes():
      """Test tempo tracker with multiple tempo changes"""

  def test_tempo_tracker_tick_to_ms_conversion():
      """Test accurate tick-to-millisecond conversion"""
  ```

- [ ] Test realtime player:
  ```python
  def test_player_play_complete_song():
      """Test player plays entire IR program"""

  def test_player_keyboard_interrupt():
      """Test Ctrl+C sends panic and stops gracefully"""

  def test_player_port_not_found():
      """Test graceful error when MIDI port unavailable"""
  ```

- [ ] Test TUI components:
  ```python
  def test_tui_state_updates():
      """Test TUI state updates correctly"""

  def test_tui_display_rendering():
      """Test TUI renders without errors"""

  def test_tui_keyboard_input():
      """Test TUI handles keyboard input (Space, Q, R)"""

  def test_tui_non_terminal_fallback():
      """Test TUI gracefully handles non-terminal environment"""
  ```

- [ ] **Success criteria**: Runtime coverage >80%

### Step 1.5: Enhance CLI Test Coverage

- [ ] Test error handler with all error types:
  ```python
  def test_cli_error_handler_parse_error():
      """Test error handler with ParseError"""

  def test_cli_error_handler_validation_error():
      """Test error handler with ValidationError"""

  def test_cli_error_handler_file_not_found():
      """Test error handler with FileNotFoundError"""

  def test_cli_error_handler_runtime_error():
      """Test error handler with RuntimeError"""

  def test_cli_error_handler_keyboard_interrupt():
      """Test error handler with KeyboardInterrupt"""

  def test_cli_error_handler_debug_mode():
      """Test error handler shows traceback in debug mode"""
  ```

- [ ] Test all commands with edge cases:
  ```python
  def test_compile_empty_file():
      """Test compile with empty MMD file"""

  def test_compile_large_file():
      """Test compile with >1000 event file"""

  def test_validate_with_warnings():
      """Test validate shows warnings but passes"""

  def test_play_no_midi_ports():
      """Test play gracefully handles no MIDI ports"""

  def test_repl_long_session():
      """Test REPL with >100 commands"""
  ```

- [ ] Test progress indicators:
  ```python
  def test_progress_shown_for_large_files():
      """Test progress bar appears for files >50KB"""

  def test_progress_not_shown_for_small_files():
      """Test progress bar doesn't appear for small files"""

  def test_progress_no_progress_flag():
      """Test --no-progress disables progress indicators"""
  ```

- [ ] **Success criteria**: CLI coverage >85%

### Step 1.6: Create Coverage Report Dashboard

- [ ] Generate detailed HTML coverage report:
  ```bash
  uv run pytest --cov=src/midi_markdown --cov-report=html:htmlcov
  ```

- [ ] Create coverage badge for README:
  ```bash
  uv run pytest --cov=src/midi_markdown --cov-report=json
  # Use coverage.json to generate badge
  ```

- [ ] Set up coverage tracking:
  - Track coverage over time
  - Set minimum coverage threshold (85%)
  - Fail CI if coverage drops below threshold

- [ ] **Success criteria**: Overall coverage >85%, all critical modules >80%

---

## Stage 2: Performance Benchmarking

**Goal**: Establish performance baselines and ensure no regressions

### Step 2.1: Create Benchmark Suite

- [ ] Create `benchmarks/` directory structure:
  ```
  benchmarks/
  ├── __init__.py
  ├── conftest.py           # Benchmark fixtures
  ├── benchmark_parser.py   # Parser benchmarks
  ├── benchmark_compiler.py # IR compiler benchmarks
  ├── benchmark_scheduler.py# Scheduler timing benchmarks
  ├── benchmark_cli.py      # CLI startup benchmarks
  └── fixtures/             # Benchmark test files
      ├── small_file.mmd    # <100 events
      ├── medium_file.mmd   # 100-500 events
      └── large_file.mmd    # >1000 events
  ```

- [ ] Install benchmarking tools:
  ```toml
  [tool.pytest.ini_options]
  markers = [
      "benchmark: marks tests as benchmarks (deselect with '-m \"not benchmark\"')"
  ]
  ```

### Step 2.2: Parser Performance Benchmarks

- [ ] Create `benchmarks/benchmark_parser.py`:
  ```python
  """Benchmark parser performance."""

  import pytest
  from pathlib import Path
  from midi_markdown.parser.parser import MMLParser


  @pytest.mark.benchmark
  def test_parse_small_file_speed(benchmark, small_mmd_file):
      """Benchmark parsing small file (<100 events)."""
      parser = MMLParser()

      result = benchmark(parser.parse_file, small_mmd_file)

      # Assert reasonable performance
      # Small files should parse in <50ms
      assert benchmark.stats['mean'] < 0.05


  @pytest.mark.benchmark
  def test_parse_medium_file_speed(benchmark, medium_mmd_file):
      """Benchmark parsing medium file (100-500 events)."""
      parser = MMLParser()

      result = benchmark(parser.parse_file, medium_mmd_file)

      # Medium files should parse in <200ms
      assert benchmark.stats['mean'] < 0.2


  @pytest.mark.benchmark
  def test_parse_large_file_speed(benchmark, large_mmd_file):
      """Benchmark parsing large file (>1000 events)."""
      parser = MMLParser()

      result = benchmark(parser.parse_file, large_mmd_file)

      # Large files should parse in <1s
      assert benchmark.stats['mean'] < 1.0
  ```

- [ ] **Target**: Parser handles 1000 events in <1 second

### Step 2.3: Compiler Performance Benchmarks

- [ ] Create `benchmarks/benchmark_compiler.py`:
  ```python
  """Benchmark IR compiler performance."""

  @pytest.mark.benchmark
  def test_compile_to_ir_speed(benchmark, parsed_document):
      """Benchmark AST → IR compilation."""
      from midi_markdown.core.compiler import compile_ast_to_ir

      result = benchmark(compile_ast_to_ir, parsed_document, ppq=480)

      # Compilation should be fast
      assert benchmark.stats['mean'] < 0.1


  @pytest.mark.benchmark
  def test_midi_file_generation_speed(benchmark, ir_program):
      """Benchmark IR → MIDI file generation."""
      from midi_markdown.codegen.midi_file import generate_midi_file

      result = benchmark(generate_midi_file, ir_program)

      # MIDI generation should be fast
      assert benchmark.stats['mean'] < 0.1
  ```

- [ ] **Target**: Full compile pipeline (parse → IR → MIDI) in <500ms for medium files

### Step 2.4: Scheduler Timing Benchmarks

- [ ] Create `benchmarks/benchmark_scheduler.py`:
  ```python
  """Benchmark scheduler timing accuracy."""

  import time
  import threading
  from collections import deque


  @pytest.mark.benchmark
  def test_scheduler_latency():
      """Measure scheduler message delivery latency."""
      from midi_markdown.runtime.scheduler import MIDIScheduler

      # Use mock MIDI port that records timestamps
      class RecordingPort:
          def __init__(self):
              self.messages = []

          def send(self, msg):
              self.messages.append((time.perf_counter(), msg))

      port = RecordingPort()
      scheduler = MIDIScheduler(port)

      # Schedule 100 messages at 10ms intervals
      start_time = time.perf_counter()
      scheduled_times = []
      for i in range(100):
          delay = i * 0.01  # 10ms intervals
          scheduled_times.append(start_time + delay)
          scheduler.schedule(f"message_{i}", delay)

      scheduler.start()
      time.sleep(1.5)  # Wait for completion
      scheduler.stop()

      # Calculate timing errors
      errors = []
      for expected_time, (actual_time, msg) in zip(scheduled_times, port.messages):
          error = abs(actual_time - expected_time) * 1000  # Convert to ms
          errors.append(error)

      # Verify timing accuracy
      avg_error = sum(errors) / len(errors)
      max_error = max(errors)

      print(f"Average latency: {avg_error:.2f}ms")
      print(f"Max latency: {max_error:.2f}ms")

      # Should be within 5ms on average
      assert avg_error < 5.0
      # Max should be within 10ms
      assert max_error < 10.0
  ```

- [ ] **Target**: Average latency <5ms, max latency <10ms

### Step 2.5: CLI Startup Benchmarks

- [ ] Create `benchmarks/benchmark_cli.py`:
  ```python
  """Benchmark CLI startup and command execution."""

  import subprocess
  import time


  @pytest.mark.benchmark
  def test_cli_startup_speed():
      """Measure CLI startup time (import + initialization)."""
      # Measure time to show help
      start = time.perf_counter()
      result = subprocess.run(
          ["uv", "run", "mmdc", "--help"],
          capture_output=True,
          text=True
      )
      elapsed = time.perf_counter() - start

      assert result.returncode == 0
      # CLI should start in <1 second
      assert elapsed < 1.0

      print(f"CLI startup time: {elapsed:.3f}s")


  @pytest.mark.benchmark
  def test_compile_command_speed(benchmark, small_mmd_file, tmp_path):
      """Benchmark full compile command execution."""
      output_file = tmp_path / "output.mid"

      def run_compile():
          result = subprocess.run(
              [
                  "uv", "run", "mmdc", "compile",
                  str(small_mmd_file),
                  "-o", str(output_file)
              ],
              capture_output=True,
              text=True
          )
          return result

      result = benchmark(run_compile)

      # Small file should compile in <2 seconds
      assert benchmark.stats['mean'] < 2.0
  ```

- [ ] **Target**: CLI startup <1s, small file compile <2s

### Step 2.6: TUI Display Performance

- [ ] Benchmark display refresh rate:
  ```python
  @pytest.mark.benchmark
  def test_tui_display_refresh_rate():
      """Measure TUI display rendering performance."""
      from midi_markdown.runtime.tui.display import TUIDisplayManager
      from midi_markdown.core.ir import IRProgram

      # Create test IR program with 1000 events
      ir_program = create_large_ir_program(event_count=1000)

      display = TUIDisplayManager(ir_program)
      display.start()

      # Measure time to render 300 frames (10 seconds at 30 FPS)
      start = time.perf_counter()
      for i in range(300):
          display.update(current_event=i, current_time=i * 0.033)
          time.sleep(0.001)  # Minimal sleep
      elapsed = time.perf_counter() - start

      display.stop()

      # Should maintain 30 FPS (0.033s per frame)
      avg_frame_time = elapsed / 300
      print(f"Average frame time: {avg_frame_time*1000:.2f}ms")

      # Each frame should render in <33ms for 30 FPS
      assert avg_frame_time < 0.033
  ```

- [ ] **Target**: Maintain 30 FPS (33ms per frame) with 1000+ events

### Step 2.7: Memory Usage Benchmarks

- [ ] Test memory efficiency:
  ```python
  import tracemalloc


  @pytest.mark.benchmark
  def test_parse_memory_usage():
      """Measure memory usage during parsing."""
      tracemalloc.start()

      parser = MMLParser()
      doc = parser.parse_file("large_file.mmd")

      current, peak = tracemalloc.get_traced_memory()
      tracemalloc.stop()

      print(f"Current memory: {current / 1024 / 1024:.2f} MB")
      print(f"Peak memory: {peak / 1024 / 1024:.2f} MB")

      # Should use <100MB for large files
      assert peak < 100 * 1024 * 1024
  ```

- [ ] **Target**: <100MB memory for 1000+ event files

### Step 2.8: Document Performance Baseline

- [ ] Create `docs/performance.md`:
  ```markdown
  # Performance Benchmarks

  ## Baseline Measurements

  **Test System:**
  - OS: macOS 14.0
  - CPU: Apple M1
  - Python: 3.12.9
  - Date: November 2025

  ### Parser Performance
  - Small files (<100 events): 15ms average
  - Medium files (100-500 events): 80ms average
  - Large files (>1000 events): 400ms average

  ### Compiler Performance
  - Parse → IR → MIDI (medium file): 250ms average

  ### Scheduler Timing Accuracy
  - Average latency: 2.3ms
  - Max latency: 4.8ms
  - Timing accuracy: ±5ms

  ### CLI Performance
  - Startup time: 0.45s
  - Small file compile: 0.8s

  ### TUI Display
  - Average frame time: 18ms
  - Refresh rate: 30 FPS sustained
  ```

- [ ] **Success criteria**: All benchmarks documented, performance targets defined

---

## Stage 3: User Documentation

**Goal**: Create comprehensive, user-friendly documentation for all audiences

### Step 3.1: Restructure Documentation

- [ ] Create organized docs/ structure:
  ```
  docs/
  ├── index.md                    # Documentation hub
  ├── getting-started/
  │   ├── installation.md         # Install guide
  │   ├── quickstart.md          # 5-minute quickstart
  │   └── first-song.md          # Tutorial: first MMD song
  ├── user-guide/
  │   ├── mml-syntax.md          # Complete syntax reference
  │   ├── timing-system.md       # Timing paradigms explained
  │   ├── midi-commands.md       # All MIDI commands
  │   ├── aliases.md             # Alias system guide
  │   ├── variables-loops.md     # Advanced features
  │   └── device-libraries.md    # Using device libraries
  ├── cli-reference/
  │   ├── compile.md             # compile command reference
  │   ├── validate.md            # validate command reference
  │   ├── play.md                # play command reference
  │   ├── repl.md                # REPL guide
  │   └── inspect.md             # inspect command reference
  ├── developer-guide/
  │   ├── architecture.md        # Architecture overview
  │   ├── ir-specification.md    # IR layer spec
  │   ├── contributing.md        # Contribution guide
  │   └── api-reference.md       # Python API docs
  ├── tutorials/
  │   ├── basic-melody.md        # Tutorial 1
  │   ├── multi-channel.md       # Tutorial 2
  │   ├── live-performance.md    # Tutorial 3
  │   └── custom-devices.md      # Tutorial 4
  └── reference/
      ├── performance.md         # Performance benchmarks
      ├── troubleshooting.md     # Common issues
      └── faq.md                 # Frequently asked questions
  ```

### Step 3.2: Write Getting Started Guide

- [ ] Create `docs/getting-started/installation.md`:
  ```markdown
  # Installation Guide

  ## Prerequisites
  - Python 3.12 or higher
  - pip or uv package manager

  ## Installing with pipx (Recommended)

  pipx is the recommended way to install MMD CLI tools:

  \```bash
  pipx install midi-markdown
  \```

  ## Installing with pip

  \```bash
  pip install midi-markdown
  \```

  ## Installing from Source

  \```bash
  git clone https://github.com/cjgdev/midi-markdown.git
  cd midi-markdown
  uv sync
  \```

  ## Platform-Specific Setup

  ### macOS

  1. Enable IAC Driver for MIDI playback:
     - Open Audio MIDI Setup
     - Window → Show MIDI Studio
     - Double-click IAC Driver
     - Check "Device is online"

  ### Linux

  1. Install ALSA MIDI support:
     \```bash
     sudo apt-get install libasound2-dev
     \```

  2. Load virtual MIDI module:
     \```bash
     sudo modprobe snd-virmidi
     \```

  ### Windows

  1. Install loopMIDI virtual MIDI driver:
     - Download from https://www.tobias-erichsen.de/software/loopmidi.html
     - Install and create virtual port

  ## Verifying Installation

  \```bash
  mmdc version
  mmdc ports  # Should show MIDI ports
  \```
  ```

- [ ] Create `docs/getting-started/quickstart.md`:
  ```markdown
  # 5-Minute Quickstart

  ## Your First MMD Song

  1. Create a file named `hello.mmd`:

  \```yaml
  ---
  title: "Hello MIDI"
  tempo: 120
  ppq: 480
  ---

  [00:00.000]
  - note_on 1.60 80 1b  # Middle C

  [00:01.000]
  - note_on 1.64 80 1b  # E

  [00:02.000]
  - note_on 1.67 80 1b  # G
  \```

  2. Compile to MIDI:

  \```bash
  mmdc compile hello.mmd
  \```

  3. Play it back:

  \```bash
  mmdc play hello.mmd
  \```

  4. View events as table:

  \```bash
  mmdc compile hello.mmd --format table
  \```

  ## Next Steps

  - [First Song Tutorial](first-song.md) - Build a complete song
  - [MML Syntax Guide](../user-guide/mml-syntax.md) - Learn the syntax
  - [CLI Reference](../cli-reference/) - Explore all commands
  ```

- [ ] Create `docs/getting-started/first-song.md`:
  ```markdown
  # Tutorial: Your First Song

  This tutorial walks through creating a simple 8-bar song with melody and chords.

  ## Step 1: Project Setup

  Create a new directory and file:

  \```bash
  mkdir my-song
  cd my-song
  touch song.mmd
  \```

  ## Step 2: Add Frontmatter

  Every MMD file starts with YAML frontmatter:

  \```yaml
  ---
  title: "My First Song"
  tempo: 120
  time_signature: [4, 4]
  ppq: 480
  ---
  \```

  ## Step 3: Add Melody Track

  Use musical timing (bars.beats.ticks):

  \```yaml
  # Melody - Channel 1
  [1.1.0]
  - note_on 1.60 80 1b  # C

  [1.2.0]
  - note_on 1.62 80 1b  # D

  [1.3.0]
  - note_on 1.64 80 1b  # E

  [1.4.0]
  - note_on 1.65 80 1b  # F
  \```

  ## Step 4: Add Chord Accompaniment

  Use aliases for chords:

  \```yaml
  # Define chord alias
  @alias chord {ch}.{root}.{vel}.{dur} "Major chord"
    - note_on {ch}.{root}.{vel} {dur}
    [@]
    - note_on {ch}.{root+4}.{vel} {dur}
    [@]
    - note_on {ch}.{root+7}.{vel} {dur}
  @end

  # Chords - Channel 2
  [1.1.0]
  - chord 2.60.60.4b  # C major, whole note

  [2.1.0]
  - chord 2.65.60.4b  # F major, whole note
  \```

  ## Step 5: Compile and Test

  \```bash
  # Quick syntax check
  mmdc check song.mmd

  # Full validation
  mmdc validate song.mmd

  # Compile to MIDI
  mmdc compile song.mmd

  # Play back
  mmdc play song.mmd
  \```

  ## Step 6: Iterate

  Use the REPL for live editing:

  \```bash
  mmdc repl
  \```

  ## Complete Example

  See [examples/09_comprehensive_song.mmd](../../examples/09_comprehensive_song.mmd)
  for a complete working example.
  ```

### Step 3.3: Write CLI Reference

- [ ] Document each command comprehensively:
  - compile.md - All options, examples, output formats
  - validate.md - Validation levels, error codes
  - check.md - Syntax-only validation
  - play.md - Real-time playback, TUI controls
  - repl.md - Interactive features, meta-commands
  - inspect.md - Event inspection and analysis
  - library.md - Device library management

- [ ] Include screenshots/recordings for TUI features:
  - Record asciinema session of `play` command
  - Take screenshots of REPL session
  - Capture table output examples

### Step 3.4: Write Tutorials

- [ ] **Tutorial 1: Basic Melody** (`docs/tutorials/basic-melody.md`)
  - Simple melody with single channel
  - Absolute timing
  - Basic note commands

- [ ] **Tutorial 2: Multi-Channel Composition** (`docs/tutorials/multi-channel.md`)
  - Multiple instruments
  - Musical timing (bars.beats.ticks)
  - Program change and CC messages

- [ ] **Tutorial 3: Live Performance Setup** (`docs/tutorials/live-performance.md`)
  - Using device libraries
  - Real-time playback
  - MIDI routing
  - Performance tips

- [ ] **Tutorial 4: Custom Device Libraries** (`docs/tutorials/custom-devices.md`)
  - Creating device library
  - Defining aliases
  - Parameter types
  - Testing and validation

### Step 3.5: Write Troubleshooting Guide

- [ ] Create `docs/reference/troubleshooting.md`:
  ```markdown
  # Troubleshooting Guide

  ## Installation Issues

  ### "No module named 'rtmidi'"

  **Problem:** python-rtmidi not installed

  **Solution:**
  \```bash
  pip install python-rtmidi
  \```

  ### MIDI Port Errors

  **Problem:** "No MIDI output ports found"

  **Solution:** See [Installation Guide](../getting-started/installation.md)
  for platform-specific MIDI setup.

  ## Parse Errors

  ### "Unexpected token at line X"

  **Problem:** Syntax error in MMD file

  **Solution:**
  1. Check for typos in command names
  2. Verify timing markers are complete: `[00:00.000]`
  3. Ensure all alias blocks have @end
  4. Use `mmdc check file.mmd --debug` for details

  ## Playback Issues

  ### Audio Glitches / Timing Problems

  **Problem:** Inconsistent playback timing

  **Solution:**
  1. Reduce system load (close other applications)
  2. Increase buffer size in MIDI software
  3. Use --no-ui flag to reduce CPU usage
  4. Check timing with `mmdc play --dry-run`

  ### No Sound

  **Problem:** MIDI playing but no audio

  **Solution:**
  1. Verify MIDI routing (port → synthesizer)
  2. Check synthesizer is receiving on correct channel
  3. Verify channel volume (CC #7) is not 0

  ## Performance Issues

  ### Slow Compilation

  **Problem:** Compile takes >10 seconds

  **Solution:**
  1. Check file size (>1MB may be too large)
  2. Simplify loops and variables
  3. Use `--no-progress` flag
  4. Profile with `--debug`

  ## Common Mistakes

  ### Forgot to Enable IAC Driver (macOS)

  **Symptom:** No MIDI ports available

  **Fix:** See macOS setup in Installation Guide

  ### Invalid MIDI Values

  **Symptom:** Validation errors about range

  **Fix:** MIDI values must be:
  - Channels: 1-16
  - Notes: 0-127
  - Velocity: 0-127
  - CC values: 0-127
  - PC values: 0-127

  ## Getting Help

  1. Check [FAQ](faq.md)
  2. Search [GitHub Issues](https://github.com/cjgdev/midi-markdown/issues)
  3. Open new issue with:
     - MMD file (minimal example)
     - Error message (full output)
     - System info (`mmdc version`)
  ```

### Step 3.6: Create FAQ

- [ ] Create `docs/reference/faq.md` with common questions:
  - What is MML?
  - How is this different from traditional MIDI sequencing?
  - Can I use this with my DAW?
  - What MIDI devices are supported?
  - Can I convert existing MIDI files to MML?
  - How do I contribute?

### Step 3.7: Update README.md

- [ ] Enhance main README with:
  - Eye-catching example
  - Feature highlights
  - Quick start section
  - Link to full documentation
  - Showcase video/GIF of TUI
  - Badge for test coverage
  - Badge for Python version
  - Badge for license

- [ ] **Success criteria**: Complete, searchable documentation covering all features

---

## Stage 4: API Documentation

**Goal**: Generate comprehensive API documentation for developers

### Step 4.1: Add Docstrings to All Public APIs

- [ ] Audit and enhance docstrings:
  ```python
  # Example comprehensive docstring
  def compile_ast_to_ir(
      document: MMLDocument,
      ppq: int = 480,
      validate: bool = True
  ) -> IRProgram:
      """Compile MMD AST to Intermediate Representation.

      Converts a parsed MMD document into an IRProgram containing
      absolute-timed MIDI events ready for output generation.

      Args:
          document: Parsed MMD document (from MMLParser)
          ppq: Pulses per quarter note (resolution)
          validate: Run validation before compilation

      Returns:
          IRProgram with compiled events and metadata

      Raises:
          ValidationError: If validation enabled and document invalid
          CompilationError: If compilation fails

      Example:
          >>> parser = MMLParser()
          >>> doc = parser.parse_file("song.mmd")
          >>> ir = compile_ast_to_ir(doc, ppq=480)
          >>> print(f"Compiled {ir.event_count} events")

      See Also:
          - MMLParser: For parsing MMD files
          - IRProgram: IR data structure
          - generate_midi_file(): For MIDI file generation
      """
  ```

- [ ] Ensure all modules have module-level docstrings
- [ ] Ensure all classes have class docstrings
- [ ] Ensure all public methods have docstrings with Args/Returns/Raises

### Step 4.2: Install Sphinx or MkDocs

- [ ] Choose documentation generator:
  - **Option A: Sphinx** - More powerful, industry standard
  - **Option B: MkDocs** - Simpler, better default theme

- [ ] For MkDocs (recommended):
  ```bash
  uv add mkdocs mkdocs-material mkdocstrings[python]
  ```

- [ ] Initialize documentation:
  ```bash
  mkdocs new .
  ```

- [ ] Configure `mkdocs.yml`:
  ```yaml
  site_name: MIDI Markdown Documentation
  site_url: https://midi-markdown.readthedocs.io/
  repo_url: https://github.com/cjgdev/midi-markdown
  repo_name: cjgdev/midi-markdown

  theme:
    name: material
    palette:
      primary: indigo
      accent: cyan
    features:
      - navigation.instant
      - navigation.tracking
      - navigation.sections
      - toc.integrate
      - search.suggest
      - content.code.annotate

  plugins:
    - search
    - mkdocstrings:
        handlers:
          python:
            options:
              show_source: true
              show_root_heading: true
              heading_level: 2

  markdown_extensions:
    - pymdownx.highlight
    - pymdownx.superfences
    - pymdownx.inlinehilite
    - pymdownx.snippets
    - admonition
    - pymdownx.details

  nav:
    - Home: index.md
    - Getting Started:
      - Installation: getting-started/installation.md
      - Quickstart: getting-started/quickstart.md
      - First Song: getting-started/first-song.md
    - User Guide:
      - MMD Syntax: user-guide/mml-syntax.md
      - Timing System: user-guide/timing-system.md
      - MIDI Commands: user-guide/midi-commands.md
      - Aliases: user-guide/aliases.md
      - Device Libraries: user-guide/device-libraries.md
    - CLI Reference:
      - compile: cli-reference/compile.md
      - validate: cli-reference/validate.md
      - play: cli-reference/play.md
      - repl: cli-reference/repl.md
      - inspect: cli-reference/inspect.md
    - Tutorials:
      - Basic Melody: tutorials/basic-melody.md
      - Multi-Channel: tutorials/multi-channel.md
      - Live Performance: tutorials/live-performance.md
      - Custom Devices: tutorials/custom-devices.md
    - Developer Guide:
      - Architecture: developer-guide/architecture.md
      - IR Specification: developer-guide/ir-specification.md
      - Contributing: developer-guide/contributing.md
      - API Reference: developer-guide/api-reference.md
    - Reference:
      - Performance: reference/performance.md
      - Troubleshooting: reference/troubleshooting.md
      - FAQ: reference/faq.md
  ```

### Step 4.3: Generate API Reference

- [ ] Create `docs/developer-guide/api-reference.md`:
  ```markdown
  # API Reference

  ## Parser

  ::: midi_markdown.parser.parser
      options:
        show_root_heading: true
        heading_level: 3

  ## Core (IR Layer)

  ::: midi_markdown.core.ir
      options:
        show_root_heading: true
        heading_level: 3

  ::: midi_markdown.core.compiler
      options:
        show_root_heading: true
        heading_level: 3

  ## Codegen

  ::: midi_markdown.codegen.midi_file
      options:
        show_root_heading: true
        heading_level: 3

  ::: midi_markdown.codegen.csv_export
      options:
        show_root_heading: true
        heading_level: 3

  ::: midi_markdown.codegen.json_export
      options:
        show_root_heading: true
        heading_level: 3

  ## Runtime (Real-time Playback)

  ::: midi_markdown.runtime.player
      options:
        show_root_heading: true
        heading_level: 3

  ::: midi_markdown.runtime.scheduler
      options:
        show_root_heading: true
        heading_level: 3

  ::: midi_markdown.runtime.midi_io
      options:
        show_root_heading: true
        heading_level: 3

  ## Validation

  ::: midi_markdown.utils.validation
      options:
        show_root_heading: true
        heading_level: 3
  ```

- [ ] Test documentation builds:
  ```bash
  mkdocs serve
  # Visit http://localhost:8000
  ```

- [ ] Fix any docstring issues found during build

### Step 4.4: Deploy Documentation

- [ ] Set up GitHub Pages or Read the Docs:
  ```bash
  mkdocs gh-deploy
  ```

- [ ] Configure custom domain (if desired)

- [ ] Set up automatic deployment on push to main:
  ```yaml
  # .github/workflows/docs.yml
  name: Deploy Documentation

  on:
    push:
      branches: [main]

  jobs:
    deploy:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v3
        - uses: actions/setup-python@v4
          with:
            python-version: 3.12
        - run: pip install mkdocs mkdocs-material mkdocstrings[python]
        - run: mkdocs gh-deploy --force
  ```

- [ ] **Success criteria**: Published API documentation at public URL

---

## Stage 5: Example Library Expansion

**Goal**: Provide comprehensive example library for learning

### Step 5.1: Categorize Existing Examples

- [ ] Current examples/ directory has 16 files
- [ ] Organize into categories:
  ```
  examples/
  ├── README.md
  ├── 00_basics/
  │   ├── 00_hello_world.mmd
  │   ├── 01_minimal_midi.mmd
  │   └── 02_simple_click_track.mmd
  ├── 01_timing/
  │   ├── 12_musical_timing.mmd
  │   └── 04_tempo_changes.mmd
  ├── 02_midi_features/
  │   ├── 05_multi_channel_basic.mmd
  │   ├── 06_cc_automation.mmd
  │   ├── 07_pitch_bend_pressure.mmd
  │   └── 08_system_messages.mmd
  ├── 03_advanced/
  │   ├── 10_loops_and_patterns.mmd
  │   ├── 11_sweep_automation.mmd
  │   ├── alias_showcase.mmd
  │   └── 09_comprehensive_song.mmd
  ├── 04_device_libraries/
  │   ├── 13_device_import.mmd
  │   └── live_performance_aliases.mmd
  └── 05_tutorials/
      ├── tutorial_1_melody.mmd
      ├── tutorial_2_chords.mmd
      ├── tutorial_3_drums.mmd
      └── tutorial_4_full_song.mmd
  ```

### Step 5.2: Add Missing Example Types

- [ ] **Drums and Percussion** example:
  ```yaml
  ---
  title: "Drum Pattern Example"
  tempo: 120
  time_signature: [4, 4]
  ppq: 480
  ---

  # GM Drum Map (Channel 10)
  # Kick: 36, Snare: 38, Hi-hat: 42

  # 8-bar drum loop
  @loop from [1.1.0] to [9.1.0] every 1b
    # Kick on 1 and 3
    - note_on 10.36 100 0.25b
  @end

  @loop from [1.1.0] to [9.1.0] every 1b offset 2b
    # Snare on 2 and 4
    - note_on 10.38 80 0.25b
  @end

  @loop from [1.1.0] to [9.1.0] every 0.5b
    # Hi-hat on 8ths
    - note_on 10.42 60 0.25b
  @end
  ```

- [ ] **Chord Progressions** example
- [ ] **Bass Line** example
- [ ] **Arpeggiator** example
- [ ] **Modulation and Expression** example
- [ ] **Polyrhythm** example
- [ ] **Generative Pattern** example

### Step 5.3: Create Tutorial Example Series

- [ ] 4-part tutorial series with progressive complexity:
  1. **Melody** - Simple single-line melody
  2. **Chords** - Add chord accompaniment
  3. **Drums** - Add drum track
  4. **Full Song** - Combine all elements + automation

- [ ] Each tutorial includes:
  - Inline comments explaining every concept
  - Step-by-step progression
  - Link to corresponding tutorial document

### Step 5.4: Add Genre-Specific Examples

- [ ] **Electronic** - Four-on-the-floor beat with bassline
- [ ] **Jazz** - Swing feel with walking bass
- [ ] **Classical** - String quartet arrangement
- [ ] **Rock** - Guitar, bass, drums arrangement

### Step 5.5: Create Device Library Examples

- [ ] One example per supported device:
  - **Quad Cortex** example
  - **Eventide H90** example
  - **Line 6 Helix** example
  - **HX Stomp** example

- [ ] Each example demonstrates:
  - Loading presets
  - Switching banks
  - Controlling parameters
  - Scene changes

### Step 5.6: Update Examples README

- [ ] Create comprehensive `examples/README.md`:
  ```markdown
  # MMD Example Library

  This directory contains example MMD files demonstrating all features.

  ## Quick Links

  - 🎵 [Basics](00_basics/) - Start here
  - ⏱️ [Timing](01_timing/) - Timing paradigms
  - 🎹 [MIDI Features](02_midi_features/) - CC, PC, pitch bend
  - 🚀 [Advanced](03_advanced/) - Loops, sweeps, aliases
  - 🎸 [Device Libraries](04_device_libraries/) - Using devices
  - 📚 [Tutorials](05_tutorials/) - Step-by-step guides

  ## Running Examples

  \```bash
  # Compile to MIDI
  mmdc compile examples/00_basics/00_hello_world.mmd

  # Play back
  mmdc play examples/00_basics/00_hello_world.mmd

  # View events
  mmdc compile examples/00_basics/00_hello_world.mmd --format table
  \```

  ## Example Categories

  ### Basics (Start Here)
  - [00_hello_world.mmd](00_basics/00_hello_world.mmd) - Absolute minimum
  - [01_minimal_midi.mmd](00_basics/01_minimal_midi.mmd) - Basic MIDI commands
  - [02_simple_click_track.mmd](00_basics/02_simple_click_track.mmd) - Metronome

  ### Timing
  - [12_musical_timing.mmd](01_timing/12_musical_timing.mmd) - Bars.beats.ticks
  - [04_tempo_changes.mmd](01_timing/04_tempo_changes.mmd) - Dynamic tempo

  ### MIDI Features
  - [05_multi_channel_basic.mmd](02_midi_features/05_multi_channel_basic.mmd) - Multiple channels
  - [06_cc_automation.mmd](02_midi_features/06_cc_automation.mmd) - Control changes
  - [07_pitch_bend_pressure.mmd](02_midi_features/07_pitch_bend_pressure.mmd) - Pitch bend
  - [08_system_messages.mmd](02_midi_features/08_system_messages.mmd) - SysEx

  ### Advanced
  - [10_loops_and_patterns.mmd](03_advanced/10_loops_and_patterns.mmd) - @loop directive
  - [11_sweep_automation.mmd](03_advanced/11_sweep_automation.mmd) - @sweep directive
  - [alias_showcase.mmd](03_advanced/alias_showcase.mmd) - Alias system
  - [09_comprehensive_song.mmd](03_advanced/09_comprehensive_song.mmd) - All features

  ### Device Libraries
  - [13_device_import.mmd](04_device_libraries/13_device_import.mmd) - @import
  - [live_performance_aliases.mmd](04_device_libraries/live_performance_aliases.mmd) - Live use

  ### Tutorials
  - [tutorial_1_melody.mmd](05_tutorials/tutorial_1_melody.mmd) - Part 1
  - [tutorial_2_chords.mmd](05_tutorials/tutorial_2_chords.mmd) - Part 2
  - [tutorial_3_drums.mmd](05_tutorials/tutorial_3_drums.mmd) - Part 3
  - [tutorial_4_full_song.mmd](05_tutorials/tutorial_4_full_song.mmd) - Part 4

  ## Contributing Examples

  Have a cool MMD example? Please contribute!

  1. Ensure it follows existing example format
  2. Add comprehensive inline comments
  3. Test it compiles and plays correctly
  4. Submit PR with description
  ```

- [ ] **Success criteria**: 30+ examples covering all features

---

## Stage 6: Contributing Guide

**Goal**: Make it easy for others to contribute

### Step 6.1: Create CONTRIBUTING.md

- [ ] Create comprehensive contributing guide:
  ```markdown
  # Contributing to MIDI Markdown

  Thank you for considering contributing! This guide will help you
  get started.

  ## Ways to Contribute

  - 🐛 Report bugs
  - 💡 Suggest features
  - 📝 Improve documentation
  - 🎵 Add example files
  - 🎸 Create device libraries
  - 🔧 Fix issues
  - ✨ Add features

  ## Getting Started

  1. Fork the repository
  2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/midi-markdown.git`
  3. Install dependencies: `uv sync`
  4. Create branch: `git checkout -b feature/my-feature`
  5. Make changes
  6. Run tests: `uv run pytest`
  7. Commit changes: `git commit -m "Add feature"`
  8. Push: `git push origin feature/my-feature`
  9. Open Pull Request

  ## Development Setup

  ### Prerequisites
  - Python 3.12+
  - uv package manager
  - Just (optional but recommended)

  ### Installation

  \```bash
  # Clone repository
  git clone https://github.com/cjgdev/midi-markdown.git
  cd midi-markdown

  # Install dependencies
  uv sync

  # Run tests
  uv run pytest
  \```

  ### Using Just Commands

  \```bash
  just test          # Run all tests
  just fmt           # Format code
  just lint          # Lint code
  just check         # Run all checks
  just qa            # Quality assurance (fmt + lint + test)
  \```

  ## Code Style

  - Follow [PEP 8](https://pep8.org/)
  - Use `ruff format` for formatting
  - Use `ruff check` for linting
  - Use type hints for all public APIs
  - Maximum line length: 100 characters

  ## Testing

  - Write tests for all new features
  - Maintain >80% code coverage
  - Run full test suite before submitting PR
  - Add integration tests for CLI commands

  ## Documentation

  - Update docstrings for all changes
  - Add examples to help text
  - Update relevant documentation files
  - Add tutorial if adding major feature

  ## Pull Request Process

  1. **Before submitting:**
     - Run `just qa` to ensure code quality
     - Update documentation
     - Add tests
     - Update CHANGELOG.md

  2. **PR description should include:**
     - What does this PR do?
     - Why is this change needed?
     - How has it been tested?
     - Screenshots (if UI changes)

  3. **Review process:**
     - Maintainer will review within 1-2 weeks
     - Address feedback
     - Once approved, maintainer will merge

  ## Reporting Bugs

  Use GitHub Issues with:
  - Clear title
  - Minimal MMD example reproducing bug
  - Expected vs actual behavior
  - System info (`mmdc version`)
  - Full error output

  ## Suggesting Features

  Open GitHub Issue with:
  - Clear description of feature
  - Use cases
  - Example syntax (if language feature)
  - Willingness to implement

  ## Code of Conduct

  Be respectful, inclusive, and constructive.
  See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
  ```

### Step 6.2: Create Issue Templates

- [ ] Create `.github/ISSUE_TEMPLATE/bug_report.md`
- [ ] Create `.github/ISSUE_TEMPLATE/feature_request.md`
- [ ] Create `.github/ISSUE_TEMPLATE/documentation.md`

### Step 6.3: Create PR Template

- [ ] Create `.github/PULL_REQUEST_TEMPLATE.md`:
  ```markdown
  ## Description

  <!-- What does this PR do? -->

  ## Motivation

  <!-- Why is this change needed? -->

  ## Testing

  <!-- How has this been tested? -->

  - [ ] Unit tests added/updated
  - [ ] Integration tests added/updated
  - [ ] Manual testing performed

  ## Documentation

  - [ ] Docstrings updated
  - [ ] CLI help text updated
  - [ ] Documentation updated
  - [ ] CHANGELOG.md updated

  ## Checklist

  - [ ] Code follows style guidelines (`just fmt`, `just lint`)
  - [ ] All tests pass (`just test`)
  - [ ] Coverage maintained/improved
  - [ ] No breaking changes (or documented in CHANGELOG)

  ## Screenshots (if applicable)

  <!-- Add screenshots for UI changes -->
  ```

### Step 6.4: Set Up CI/CD

- [ ] Create GitHub Actions workflow (if not exists):
  ```yaml
  # .github/workflows/ci.yml
  name: CI

  on:
    push:
      branches: [main]
    pull_request:
      branches: [main]

  jobs:
    test:
      runs-on: ${{ matrix.os }}
      strategy:
        matrix:
          os: [ubuntu-latest, macos-latest, windows-latest]
          python-version: ['3.12', '3.13']

      steps:
        - uses: actions/checkout@v3
        - name: Set up Python
          uses: actions/setup-python@v4
          with:
            python-version: ${{ matrix.python-version }}

        - name: Install uv
          run: pip install uv

        - name: Install dependencies
          run: uv sync

        - name: Run linting
          run: uv run ruff check .

        - name: Run formatting check
          run: uv run ruff format --check .

        - name: Run type checking
          run: uv run mypy src

        - name: Run tests
          run: uv run pytest --cov=src --cov-report=xml

        - name: Upload coverage
          uses: codecov/codecov-action@v3
          with:
            file: ./coverage.xml
  ```

- [ ] **Success criteria**: Clear contribution guidelines, easy onboarding

---

## Stage 7: Release Preparation

**Goal**: Prepare for stable release

### Step 7.1: Version 1.0 Checklist

- [ ] All Phase 5 stages complete
- [ ] Test coverage >85%
- [ ] All documentation complete
- [ ] All examples working
- [ ] Performance benchmarks documented
- [ ] No critical bugs
- [ ] Security audit complete

### Step 7.2: Create CHANGELOG

- [ ] Format: Keep a Changelog style
- [ ] Document all changes since v0.1.0
- [ ] Group by: Added, Changed, Fixed, Deprecated, Removed

### Step 7.3: Update Version Numbers

- [ ] Update `__version__` in `__init__.py`
- [ ] Update `pyproject.toml` version
- [ ] Update documentation references

### Step 7.4: Create Release Notes

- [ ] Highlight major features
- [ ] Include upgrade guide
- [ ] Note breaking changes
- [ ] Link to documentation

### Step 7.5: Tag and Release

- [ ] Create Git tag: `git tag -a v1.0.0 -m "Release v1.0.0"`
- [ ] Push tag: `git push origin v1.0.0`
- [ ] Create GitHub Release
- [ ] Publish to PyPI (if public)

---

## Validation Checklist

**Before marking Phase 5 complete:**

### Testing
- [ ] Test coverage >85% overall
- [ ] All critical modules >80% coverage
- [ ] Performance benchmarks documented
- [ ] All tests passing on all platforms
- [ ] No flaky tests
- [ ] Integration tests cover all workflows

### Documentation
- [ ] Installation guide complete
- [ ] Quickstart guide complete
- [ ] User guide complete (all features)
- [ ] CLI reference complete (all commands)
- [ ] API documentation published
- [ ] Tutorials complete (4+ tutorials)
- [ ] Troubleshooting guide complete
- [ ] FAQ complete

### Examples
- [ ] 30+ examples covering all features
- [ ] Examples organized by category
- [ ] All examples tested and working
- [ ] Examples README comprehensive

### Developer Experience
- [ ] Contributing guide complete
- [ ] Issue templates created
- [ ] PR template created
- [ ] CI/CD working
- [ ] Code of Conduct added

### Release Ready
- [ ] CHANGELOG complete
- [ ] Version numbers updated
- [ ] Release notes drafted
- [ ] No critical bugs
- [ ] Security audit complete

---

## Success Criteria Summary

✅ **Phase 5 is complete when:**

1. **Testing**: 85%+ code coverage with comprehensive test suite
2. **Documentation**: Complete user and developer documentation published
3. **Examples**: 30+ examples covering all features and use cases
4. **Performance**: Benchmarks documented and meeting targets
5. **Contribution**: Clear contribution guidelines and easy onboarding
6. **Release**: Ready for v1.0 stable release

---

## Estimated Effort

- **Stage 1** (Test Coverage): 10-12 hours
- **Stage 2** (Performance Benchmarking): 6-8 hours
- **Stage 3** (User Documentation): 12-16 hours
- **Stage 4** (API Documentation): 4-6 hours
- **Stage 5** (Example Library): 6-8 hours
- **Stage 6** (Contributing Guide): 3-4 hours
- **Stage 7** (Release Prep): 2-3 hours

**Total: 43-57 hours** (approximately 1-1.5 weeks of focused work)

---

## Notes for Implementation

1. **Incremental approach**: Complete one stage at a time, commit frequently
2. **Test everything**: Run full test suite after each major change
3. **Document as you go**: Don't save documentation for last
4. **Get feedback**: Share draft documentation with users early
5. **Prioritize critical paths**: Focus on most-used features first
6. **Automate where possible**: Use CI/CD, automated docs generation
7. **Celebrate milestones**: Each stage completion is a win!

---

**Last Updated**: November 7, 2025
**Version**: 1.0
**Current Phase**: 4 Complete, Phase 5 Planning
