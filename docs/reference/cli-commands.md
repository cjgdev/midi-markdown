# CLI Command Reference

The `midimarkup` CLI provides commands to compile, validate, and check MML files.

## Quick Start

```bash
# Using uv run (recommended)
uv run midimarkup <command> [options]

# Or activate virtual environment first
source .venv/bin/activate
midimarkup <command> [options]

# Short alias 'mml' also available
uv run mml compile song.mml -o output.mid
```

---

## Commands

### compile

Converts a `.mml` file to a standard MIDI `.mid` file.

**Usage:**
```bash
uv run midimarkup compile INPUT_FILE [OPTIONS]
```

**Arguments:**
- `INPUT_FILE` - Path to `.mml` file to compile

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
uv run midimarkup compile examples/00_hello_world.mml

# Specify output file
uv run midimarkup compile examples/00_hello_world.mml -o output/hello.mid

# Verbose output (shows compilation stages)
uv run midimarkup compile song.mml -o output.mid -v

# High-resolution MIDI (960 PPQ)
uv run midimarkup compile song.mml --ppq 960

# Single-track MIDI (format 0)
uv run midimarkup compile song.mml --format 0

# Skip validation for faster compilation
uv run midimarkup compile song.mml --no-validate
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
[cyan]Compiling:[/cyan] song.mml
[cyan]Output:[/cyan] output/song.mid
  [dim]Parsing MML file...[/dim]
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
uv run midimarkup validate INPUT_FILE [OPTIONS]
```

**Arguments:**
- `INPUT_FILE` - Path to `.mml` file to validate

**Options:**
- `-v, --verbose` - Show detailed validation steps
- `--no-color` - Disable colored output
- `--no-emoji` - Disable emoji in output

**Examples:**
```bash
# Validate a single file
uv run midimarkup validate examples/alias_showcase.mml

# Validate with verbose output
uv run midimarkup validate song.mml -v

# Validate all examples
for file in examples/*.mml; do
    echo "Validating $file..."
    uv run midimarkup validate "$file"
done
```

**Success Output:**
```
✅ Validation passed
File: examples/00_hello_world.mml
Events: 3
```

---

### check

Quick syntax-only check without full validation (faster than `validate`).

**Usage:**
```bash
uv run midimarkup check INPUT_FILE [OPTIONS]
```

**Arguments:**
- `INPUT_FILE` - Path to `.mml` file to check

**Options:**
- `--no-color` - Disable colored output
- `--no-emoji` - Disable emoji in output

**Examples:**
```bash
# Quick syntax check
uv run midimarkup check song.mml

# Check multiple files
uv run midimarkup check examples/0*.mml

# Use during development for fast feedback
watch -n 2 'uv run midimarkup check song.mml'
```

**Success Output:**
```
✅ Syntax check passed
File: song.mml
```

---

### version

Display version information.

**Usage:**
```bash
uv run midimarkup version
```

**Output:**
```
MIDI Markup Language (MML) Compiler
Version: 0.1.0
```

---

### library

Manage device libraries (commands are currently stubbed).

**Usage:**
```bash
uv run midimarkup library <subcommand> [OPTIONS]
```

**Subcommands:**
- `list` - List available device libraries
- `info NAME` - Show information about a specific library
- `validate PATH` - Validate a device library file

**Examples:**
```bash
# List available device libraries
uv run midimarkup library list

# Show library info
uv run midimarkup library info quad_cortex

# Validate a library
uv run midimarkup library validate devices/quad_cortex.mml
```

**Note:** Library commands are currently stubbed and will show a warning message.

---

## Error Messages

The compiler provides detailed error messages with context and suggestions:

```
❌ error[E101]: Unexpected token 'foo'
  → examples/bad.mml:12:5

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

### Beginner (00-03)
```bash
# 00: Simplest possible MML file
uv run midimarkup compile examples/00_hello_world.mml -o output/00.mid

# 01: Basic metadata and meta events
uv run midimarkup compile examples/01_minimal_midi.mml -o output/01.mid

# 02: Click track with repeated notes
uv run midimarkup compile examples/02_simple_click_track.mml -o output/02.mid

# 03: Song sections with markers
uv run midimarkup compile examples/03_song_structure_markers.mml -o output/03.mid
```

### Intermediate (04-07)
```bash
# 04: Tempo changes throughout a song
uv run midimarkup compile examples/04_tempo_changes.mml -o output/04.mid

# 05: Multiple MIDI channels (synth, bass, drums)
uv run midimarkup compile examples/05_multi_channel_basic.mml -o output/05.mid

# 06: Control Change automation
uv run midimarkup compile examples/06_cc_automation.mml -o output/06.mid

# 07: Pitch bend and aftertouch
uv run midimarkup compile examples/07_pitch_bend_pressure.mml -o output/07.mid
```

### Advanced (08-13)
```bash
# 08: SysEx and system messages
uv run midimarkup compile examples/08_system_messages.mml -o output/08.mid

# 09: Comprehensive song with all features
uv run midimarkup compile examples/09_comprehensive_song.mml -o output/09.mid

# 10: Loops and patterns
uv run midimarkup compile examples/10_loops_and_patterns.mml -o output/10.mid

# 11: Sweep automation
uv run midimarkup compile examples/11_sweep_automation.mml -o output/11.mid

# 12: Musical timing (bars.beats.ticks)
uv run midimarkup compile examples/12_musical_timing.mml -o output/12.mid

# 13: Device library imports
uv run midimarkup compile examples/13_device_import.mml -o output/13.mid
```

---

## Common Workflows

### Development Workflow
```bash
# 1. Check syntax while writing (fast feedback)
uv run midimarkup check my_song.mml

# 2. Validate when ready (full validation)
uv run midimarkup validate my_song.mml

# 3. Compile to MIDI with verbose output
uv run midimarkup compile my_song.mml -o output/my_song.mid -v

# 4. Play the result (macOS example)
open output/my_song.mid
```

### Batch Processing
```bash
# Create output directory
mkdir -p output

# Compile all examples
for file in examples/[0-9][0-9]_*.mml; do
    name=$(basename "$file" .mml)
    echo "Compiling $name..."
    uv run midimarkup compile "$file" -o "output/${name}.mid"
done

# Validate all examples
for file in examples/[0-9][0-9]_*.mml; do
    echo "=== $file ==="
    uv run midimarkup validate "$file" || echo "FAILED"
done
```

### Testing Different Formats
```bash
# Format 0 (single track) - all events merged
uv run midimarkup compile song.mml -o output/format0.mid --format 0

# Format 1 (multi-track) - default, tracks preserved
uv run midimarkup compile song.mml -o output/format1.mid --format 1

# High-resolution MIDI (960 PPQ instead of 480)
uv run midimarkup compile song.mml -o output/hires.mid --ppq 960
```

---

## Tips & Best Practices

1. **Use `-v` for debugging** - Shows detailed compilation stages
2. **Check first, validate second** - `check` is faster for syntax-only feedback
3. **Create output directory first** - `mkdir -p output` before compiling
4. **Use version control** - Track your `.mml` files with git
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
A: Use `--no-validate` flag: `uv run midimarkup compile file.mml --no-validate`

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

- [Getting Started Guide](../getting-started.md) - Quick start tutorial
- [Examples README](../../examples/README.md) - Learning path with examples
- [Language Specification](../../spec.md) - Complete MML reference
- [Alias System Guide](../guides/alias-system.md) - Using device aliases
