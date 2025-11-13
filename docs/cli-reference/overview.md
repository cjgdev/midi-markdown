# CLI Command Reference

The `mmdc` CLI provides commands to compile, validate, and check MMD files.

## Quick Start

```bash
# Using uv run (recommended)
uv run mmdc <command> [options]

# Or activate virtual environment first
source .venv/bin/activate
mmdc <command> [options]

# Short alias 'mml' also available
uv run mml compile song.mmd -o output.mid
```

---

## Commands

### compile

Converts a `.mmd` file to a standard MIDI `.mid` file.

**Usage:**
```bash
uv run mmdc compile INPUT_FILE [OPTIONS]
```

**Arguments:**
- `INPUT_FILE` - Path to `.mmd` file to compile

**Options:**
- `-o, --output PATH` - Output MIDI file path (default: input name with `.mid` extension)
- `--ppq INTEGER` - Pulses per quarter note (default: 480)
- `--format INTEGER` - MIDI format: 0=single track, 1=multi-track (default: 1)
- `-v, --verbose` - Show detailed compilation steps
- `--no-validate` - Skip validation step (faster, but less safe)
- `--no-color` - Disable colored output (for CI/accessibility)
- `--no-emoji` - Disable emoji in output (for CI/accessibility)

**Examples:**
```bash
# Basic compilation
uv run mmdc compile examples/00_basics/01_hello_world.mmd

# Specify output file
uv run mmdc compile examples/00_basics/01_hello_world.mmd -o output/hello.mid

# Verbose output (shows compilation stages)
uv run mmdc compile song.mmd -o output.mid -v

# High-resolution MIDI (960 PPQ)
uv run mmdc compile song.mmd --ppq 960

# Single-track MIDI (format 0)
uv run mmdc compile song.mmd --format 0

# Skip validation for faster compilation
uv run mmdc compile song.mmd --no-validate
```

**Success Output:**
```
╭─────────── ✅ Compilation successful (0.16s) ───────────╮
│ Events: 104                                             │
│ Tracks: 1 (Main)                                        │
│ Duration: 0:50 (50s)                                    │
│ Input: 8.7 KB → Output: 0.5 KB                          │
╰────────────────── output/song.mid ─────────────────────╯
```

**Verbose Output:**
```
[cyan]Compiling:[/cyan] song.mmd
[cyan]Output:[/cyan] output/song.mid
  [dim]Parsing MMD file...[/dim]
  [dim]Parsed:[/dim] [bold cyan]38[/bold cyan] [dim]events,[/dim] [bold cyan]0[/bold cyan] [dim]tracks[/dim]
  [dim]Loading[/dim] [bold cyan]4[/bold cyan] [bold magenta]import[/bold magenta][bold](s)[/bold][dim]...[/dim]
  [dim]Loaded[/dim] [bold cyan]157[/bold cyan] [bold magenta]alias[/bold magenta][bold](es)[/bold] [dim]from imports[/dim]
  [green]✓ Validation passed[/green]
  [dim]Expanding commands...[/dim]
  [dim]Expanded:[/dim] [bold cyan]104[/bold cyan] [dim]events[/dim]
  [dim]Generating MIDI events...[/dim]
  [dim]Writing MIDI file...[/dim]
```

---

### validate

Performs full validation including syntax, timing, value ranges, and MIDI constraints.

**Usage:**
```bash
uv run mmdc validate INPUT_FILE [OPTIONS]
```

**Arguments:**
- `INPUT_FILE` - Path to `.mmd` file to validate

**Options:**
- `-v, --verbose` - Show detailed validation steps
- `--no-color` - Disable colored output
- `--no-emoji` - Disable emoji in output

**Examples:**
```bash
# Validate a single file
uv run mmdc validate examples/03_advanced/alias_showcase.mmd

# Validate with verbose output
uv run mmdc validate song.mmd -v

# Validate all examples
for file in examples/**/*.mmd; do
    echo "Validating $file..."
    uv run mmdc validate "$file"
done
```

**Success Output:**
```
✅ Validation passed
File: examples/00_basics/01_hello_world.mmd
Events: 3
```

---

### check

Quick syntax-only check without full validation (faster than `validate`).

**Usage:**
```bash
uv run mmdc check INPUT_FILE [OPTIONS]
```

**Arguments:**
- `INPUT_FILE` - Path to `.mmd` file to check

**Options:**
- `--no-color` - Disable colored output
- `--no-emoji` - Disable emoji in output

**Examples:**
```bash
# Quick syntax check
uv run mmdc check song.mmd

# Check multiple files
uv run mmdc check examples/0*.mmd

# Use during development for fast feedback
watch -n 2 'uv run mmdc check song.mmd'
```

**Success Output:**
```
✅ Syntax check passed
File: song.mmd
```

---

### version

Display version information.

**Usage:**
```bash
uv run mmdc version
```

**Output:**
```
MIDI Markdown (MMD) Compiler
Version: 0.1.0
```

---

### library

Manage device libraries.

**Usage:**
```bash
uv run mmdc library <subcommand> [OPTIONS]
```

**Subcommands:**
- `list` - List available device libraries
- `info NAME` - Show information about a specific library
- `validate PATH` - Validate a device library file

**Examples:**
```bash
# List available device libraries
uv run mmdc library list

# Show library info
uv run mmdc library info quad_cortex

# Validate a library
uv run mmdc library validate devices/quad_cortex.mmd
```

---

### ports

List available MIDI output ports for real-time playback.

**Usage:**
```bash
uv run mmdc ports
```

**Output:**
```
Available MIDI Ports:
  0: IAC Driver Bus 1
  1: Network Session 1
  2: Bluetooth MIDI
```

**Usage in playback:**
```bash
# Use port number with play command
uv run mmdc play song.mmd --port 0
```

---

### examples

Show example MMD code snippets for quick reference.

**Usage:**
```bash
uv run mmdc examples [CATEGORY]
```

**Categories:**
- `basic` - Simple MIDI commands
- `timing` - Different timing paradigms
- `loops` - Loop patterns
- `devices` - Device library usage
- `all` - Show all examples (default)

**Output:**
```
MMD Examples

Basic Note On:
[00:00.000]
- note_on 1.60 100 1b

CC Automation:
[00:00.000]
- cc 1.7.100
```

---

### cheatsheet

Display a quick reference guide for MMD syntax.

**Usage:**
```bash
uv run mmdc cheatsheet
```

**Output:**
```
MMD Syntax Cheatsheet

Timing:
  [00:00.000]     Absolute (mm:ss.ms)
  [1.1.0]         Musical (bar.beat.tick)
  [+500ms]        Relative delta
  [@]             Simultaneous

Commands:
  note_on 1.60 100 1b    Note on with duration
  cc 1.7.127             Control change
  pc 1.5                 Program change
  tempo 120              Set tempo
```

---

## Phase 6: Generative & Modulation Features

The compiler now supports **random value generation** and **modulation expressions** for creating dynamic, evolving MIDI sequences. These features are automatically expanded during compilation.

### Random Values

Use `random()` expressions to inject variation into note velocities, CC values, or note numbers:

```mml
# Humanized velocity variation
- note_on 1.60.random(70, 100) 1b

# Varying CC values
- cc 1.74.random(30, 90)

# Random note for generative melodies
- note_on 1.random(C3, C5).80 1b
```

The compiler expands each `random()` call to a specific random value during compilation, creating variation each time you compile.

**Reference:** See [Generative Music Guide](../user-guide/generative-music.md) and [Random Expressions Reference](../reference/random-expressions.md)

### Modulation Expressions

Smooth parameter automation using curves, waveforms, and envelopes:

```mml
# Bezier curve for smooth filter opening
- cc 1.74.curve(0, 127, ease-out)

# Sine wave LFO for vibrato
- cc 1.1.wave(sine, 64, freq=5.0, depth=10)

# ADSR envelope for dynamic control
- cc 1.74.envelope(adsr, attack=0.1, decay=0.2, sustain=0.7, release=0.3)
```

The compiler converts these expressions into discrete MIDI CC events sampled at regular intervals, creating smooth automation that works with any MIDI device.

**Reference:** See [Modulation Guide](../user-guide/modulation.md) and [Modulation Reference](../reference/modulation-reference.md)

### Compilation Notes

- Both features expand during the **command expansion phase** (shown in verbose output)
- Random values are fixed at compile time—recompile to generate new variations
- Modulation sampling rate is controlled by PPQ resolution (higher PPQ = finer automation)
- Combine with loops and variables for parametric, evolving compositions

---

## Error Messages

The compiler provides detailed error messages with context and suggestions:

```
❌ error[E101]: Unexpected token 'foo'
  → examples/bad.mmd:12:5

   10 │ [00:01.000]
   11 │ - note_on 1.60 80 1b
   12 │ - foo
       │   ^^^ unexpected token
   13 │ [00:02.000]

💡 Expected: note_on, note_off, cc, pc, pitch_bend, etc.
   Did you mean 'note_off'?
```

**Error Format:**
- **Error code** - E1xx (parse), E2xx (validation), E3xx (expansion), E4xx (file)
- **File location** - Line and column numbers
- **Source context** - Shows the problematic code
- **Suggestion** - Helpful hints and "Did you mean?" corrections

---

## Working Examples

All numbered examples (00-13) should compile successfully:

### Beginner (Basics)
```bash
# 01: Simplest possible MMD file
uv run mmdc compile examples/00_basics/01_hello_world.mmd -o output/01_hello.mid

# 02: Basic metadata and meta events
uv run mmdc compile examples/00_basics/02_minimal_midi.mmd -o output/02_minimal.mid

# 03: Click track with repeated notes
uv run mmdc compile examples/00_basics/03_simple_click_track.mmd -o output/03_click.mid

# 04: Song sections with markers
uv run mmdc compile examples/00_basics/04_song_structure_markers.mmd -o output/04_structure.mid
```

### Intermediate (Timing & MIDI Features)
```bash
# Tempo changes throughout a song
uv run mmdc compile examples/01_timing/01_tempo_changes.mmd -o output/tempo_changes.mid

# Multiple MIDI channels (synth, bass, drums)
uv run mmdc compile examples/02_midi_features/01_multi_channel_basic.mmd -o output/multi_channel.mid

# Control Change automation
uv run mmdc compile examples/02_midi_features/02_cc_automation.mmd -o output/cc_automation.mid

# Pitch bend and aftertouch
uv run mmdc compile examples/02_midi_features/03_pitch_bend_pressure.mmd -o output/pitch_bend.mid

# SysEx and system messages
uv run mmdc compile examples/02_midi_features/04_system_messages.mmd -o output/system_messages.mid
```

### Advanced (Patterns & Device Control)
```bash
# Loops and patterns
uv run mmdc compile examples/03_advanced/01_loops_and_patterns.mmd -o output/loops.mid

# Sweep automation
uv run mmdc compile examples/03_advanced/02_sweep_automation.mmd -o output/sweeps.mid

# Comprehensive song with all features
uv run mmdc compile examples/03_advanced/10_comprehensive_song.mmd -o output/comprehensive.mid

# Musical timing (bars.beats.ticks)
uv run mmdc compile examples/01_timing/02_musical_timing.mmd -o output/musical_timing.mid

# Device library imports
uv run mmdc compile examples/04_device_libraries/01_device_import.mmd -o output/device_import.mid
```

---

## Common Workflows

### Development Workflow
```bash
# 1. Check syntax while writing (fast feedback)
uv run mmdc check my_song.mmd

# 2. Validate when ready (full validation)
uv run mmdc validate my_song.mmd

# 3. Compile to MIDI with verbose output
uv run mmdc compile my_song.mmd -o output/my_song.mid -v

# 4. Play the result (macOS example)
open output/my_song.mid
```

### Batch Processing
```bash
# Create output directory
mkdir -p output

# Compile all examples
for file in examples/[0-9][0-9]_*.mmd; do
    name=$(basename "$file" .mmd)
    echo "Compiling $name..."
    uv run mmdc compile "$file" -o "output/${name}.mid"
done

# Validate all examples
for file in examples/[0-9][0-9]_*.mmd; do
    echo "=== $file ==="
    uv run mmdc validate "$file" || echo "FAILED"
done
```

### Testing Different Formats
```bash
# Format 0 (single track) - all events merged
uv run mmdc compile song.mmd -o output/format0.mid --format 0

# Format 1 (multi-track) - default, tracks preserved
uv run mmdc compile song.mmd -o output/format1.mid --format 1

# High-resolution MIDI (960 PPQ instead of 480)
uv run mmdc compile song.mmd -o output/hires.mid --ppq 960
```

---

## Tips & Best Practices

1. **Use `-v` for debugging** - Shows detailed compilation stages
2. **Check first, validate second** - `check` is faster for syntax-only feedback
3. **Create output directory first** - `mkdir -p output` before compiling
4. **Use version control** - Track your `.mmd` files with git
5. **Start with examples** - Study examples 00-13 for learning
6. **Validate before committing** - Ensure files compile successfully
7. **Use absolute paths** - Or run commands from project root

---

## Troubleshooting

**Q: "No such file or directory" error?**
A: Create the output directory first: `mkdir -p output`

**Q: Parse errors in examples?**
A: All numbered examples (00-13) should compile successfully. If not, please report an issue.

**Q: "Validation failed" but syntax check passes?**
A: `check` only verifies syntax. `validate` also checks MIDI ranges, timing, etc.

**Q: Want to skip validation for faster compilation?**
A: Use `--no-validate` flag: `uv run mmdc compile file.mmd --no-validate`

**Q: Colors not showing in terminal?**
A: Some terminals don't support colors. Use `--no-color` for plain output.

**Q: Emoji not displaying correctly?**
A: Use `--no-emoji` flag or set `NO_COLOR` environment variable.

---

## Environment Variables

- `NO_COLOR` - Disables colored output when set (standard)
- `FORCE_COLOR` - Forces colored output even in non-TTY environments

---

## Exit Codes

- `0` - Success
- `1` - Error (parse, validation, compilation failure)
- `2` - Invalid command-line arguments

---

## See Also

- [Getting Started Guide](../getting-started/quickstart.md) - Quick start tutorial
- [Examples Guide](../getting-started/examples-guide.md) - Learning path with examples
- [Language Specification](../reference/specification.md) - Complete MMD reference
- [Alias System Guide](../user-guide/alias-system.md) - Using device aliases
