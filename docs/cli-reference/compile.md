# Command: compile

> **Audience**: Users
> **Level**: Beginner to Advanced

Compile MMD source files to MIDI or other output formats.

---

## Synopsis

```bash
mmdc compile [OPTIONS] INPUT_FILE
mml compile [OPTIONS] INPUT_FILE         # Shorter alias
```

---

## Description

The `compile` command is the primary MMD workflow tool. It parses your `.mmd` source file, resolves aliases and imports, expands advanced features (loops, variables, sweeps), validates MIDI commands, and generates output in your chosen format.

**Default behavior**: Compiles to Standard MIDI File (`.mid`) with the same basename as input.

**What compile does**:

1. **Parse** - Parse MMD syntax to AST (Abstract Syntax Tree)
2. **Import** - Load device libraries (`@import` statements)
3. **Resolve** - Expand aliases to base MIDI commands
4. **Expand** - Process loops, variables, sweeps, conditionals
5. **Validate** - Check MIDI values, timing, channel ranges
6. **Compile** - Convert to Intermediate Representation (IR)
7. **Generate** - Create output file in specified format

---

## Options

### Input/Output

#### `INPUT_FILE` (required)
Path to `.mmd` source file to compile.

```bash
mmdc compile song.mmd
mmdc compile path/to/performance.mmd
```

#### `-o, --output PATH`
Output file path. Default: same as input with `.mid` extension.

```bash
# Default output: song.mid
mmdc compile song.mmd

# Custom output path
mmdc compile song.mmd -o output/final.mid

# Different name
mmdc compile song.mmd --output performance.mid
```

---

### Output Format

#### `--format, -f FORMAT`
Output format selection. Default: `midi`

**Available formats**:
- `midi` - Standard MIDI File (.mid) - **default**
- `table` - Pretty-printed terminal table (no file output)
- `csv` - midicsv-compatible CSV format
- `json` - Complete MIDI event data with metadata
- `json-simple` - Simplified JSON for music analysis

```bash
# MIDI file (default)
mmdc compile song.mmd

# Display as formatted table
mmdc compile song.mmd --format table

# Export to CSV for Excel/spreadsheets
mmdc compile song.mmd --format csv -o events.csv

# Export to JSON for programmatic processing
mmdc compile song.mmd --format json -o data.json

# Simplified JSON (easier to parse)
mmdc compile song.mmd --format json-simple -o simple.json
```

**Format comparison**:

| Format | Use Case | File Output | Includes Metadata |
|--------|----------|-------------|-------------------|
| `midi` | DAW import, playback | Yes (.mid) | MIDI standard |
| `table` | Quick inspection | No (terminal) | Yes |
| `csv` | Spreadsheet analysis | Yes (.csv) | Yes |
| `json` | Scripting, tools | Yes (.json) | Complete |
| `json-simple` | Music analysis | Yes (.json) | Simplified |

---

### MIDI Configuration

#### `--ppq PULSES`
Pulses per quarter note (MIDI resolution). Default: `480`

Higher PPQ = finer timing resolution but larger files.

```bash
# Standard resolution (default)
mmdc compile song.mmd --ppq 480

# High resolution for precise timing
mmdc compile song.mmd --ppq 960

# Lower resolution for smaller files
mmdc compile song.mmd --ppq 240
```

**Common PPQ values**:
- `96` - Very low (old hardware)
- `240` - Low (small files)
- `480` - Standard (recommended)
- `960` - High precision
- `1920` - Ultra-high precision

**Note**: PPQ can also be set in frontmatter:
```yaml
---
ppq: 960
---
```

---

#### `--midi-format FORMAT`
MIDI file format. Default: `1` (multi-track)

**Format types**:
- `0` - Single-track format (all events in one track)
- `1` - Multi-track format (separate tracks) - **default**
- `2` - Async multi-track (independent sequences, rare)

```bash
# Multi-track (default, best for DAWs)
mmdc compile song.mmd --midi-format 1

# Single-track (simpler, all events merged)
mmdc compile song.mmd --midi-format 0

# Async multi-track (advanced, rarely used)
mmdc compile song.mmd --midi-format 2
```

**When to use each format**:
- **Format 0**: Simple sequences, single instrument, click tracks
- **Format 1**: Multi-channel songs, DAW import, most use cases
- **Format 2**: Independent patterns, experimental compositions

---

### Validation

#### `--validate / --no-validate`
Enable or disable validation. Default: `--validate` (enabled)

Validation checks for:
- MIDI value ranges (0-127 for notes, CC, velocities)
- Channel numbers (1-16)
- Pitch bend range (-8192 to +8191)
- Timing monotonicity (events in chronological order)
- Undefined aliases
- Invalid parameter counts

```bash
# Validate (default, recommended)
mmdc compile song.mmd --validate

# Skip validation (faster, but dangerous)
mmdc compile song.mmd --no-validate
```

**⚠️ Warning**: Using `--no-validate` may produce invalid MIDI files that crash devices or software. Only use for quick syntax checks.

---

### Output Control

#### `-v, --verbose`
Show detailed compilation steps.

```bash
mmdc compile song.mmd --verbose
```

**Verbose output shows**:
- Parsing progress
- Import loading
- Alias resolution count
- Expansion details
- Validation results
- Compilation timing

**Example verbose output**:
```
Compiling: song.mmd
Output: song.mid
  Parsing MMD file...
  Parsed: 38 events, 0 tracks
  Loading 4 import(s)...
  Loaded 157 alias(es) from imports
  ✓ Validation passed
  Expanding commands...
  Expanded: 104 events
  Compiling to IR...
  Generating MIDI file (Format 1, PPQ 480)...
  ✓ Compilation successful (0.16s)
```

---

#### `--no-progress`
Disable progress bars/spinners (for scripting).

Progress indicators appear automatically for:
- Large files (>50KB)
- Files with >500 events
- Verbose mode (`-v`)

```bash
# Disable progress for CI/scripts
mmdc compile large_song.mmd --no-progress
```

---

### Accessibility

#### `--no-color`
Disable colored output (for accessibility or piping).

```bash
mmdc compile song.mmd --no-color
```

**Also enabled by**:
- `NO_COLOR` environment variable
- `CI` environment variable (CI/CD pipelines)

---

#### `--no-emoji`
Disable emoji in output (for screen readers or terminals without emoji support).

```bash
mmdc compile song.mmd --no-emoji
```

**Changes**:
- ✅ → [OK]
- ❌ → [ERROR]
- 💡 → [HINT]

---

### Debugging

#### `--debug`
Show full error tracebacks (for bug reports).

```bash
mmdc compile broken.mmd --debug
```

**Normal error**:
```
❌ error[E101]: Unexpected token 'foo'
  → song.mmd:12:5
```

**Debug error** (with `--debug`):
```
❌ error[E101]: Unexpected token 'foo'
  → song.mmd:12:5

Traceback (most recent call last):
  File "...parser.py", line 45, in parse_file
    ...
```

---

## Examples

### Basic Usage

```bash
# Simplest usage - compile to MIDI
mmdc compile song.mmd

# Result: song.mid created
```

---

### Custom Output Path

```bash
# Save to specific directory
mmdc compile song.mmd -o output/performance.mid

# Save with different name
mmdc compile verse.mmd -o song_verse.mid
```

---

### High-Resolution MIDI

```bash
# Double standard resolution for precise timing
mmdc compile song.mmd --ppq 960 -o precise.mid
```

**Use case**: Submillisecond timing accuracy for live performance.

---

### Export for Analysis

```bash
# Export to CSV for spreadsheet analysis
mmdc compile song.mmd --format csv -o events.csv

# Open in Excel/Google Sheets
# Columns: Track, Time, Type, Channel, Data1, Data2, Text
```

---

### Quick Inspection

```bash
# Display events as formatted table (no file created)
mmdc compile song.mmd --format table
```

**Output**:
```
┌─────────┬──────────────┬─────────┬──────────┬────────┐
│ Time    │ Event        │ Channel │ Data     │ Note   │
├─────────┼──────────────┼─────────┼──────────┼────────┤
│ 0:00.00 │ Tempo        │ -       │ 120 BPM  │        │
│ 0:00.00 │ Note On      │ 1       │ 60 / 80  │ C4     │
│ 0:01.00 │ Note Off     │ 1       │ 60       │ C4     │
└─────────┴──────────────┴─────────┴──────────┴────────┘
```

---

### JSON Export

```bash
# Complete JSON with all metadata
mmdc compile song.mmd --format json -o data.json

# Simplified JSON (easier to parse)
mmdc compile song.mmd --format json-simple -o simple.json
```

**JSON structure** (`json` format):
```json
{
  "ppq": 480,
  "format": 1,
  "tracks": [
    {
      "name": "Master",
      "events": [
        {
          "time": 0,
          "type": "tempo",
          "tempo_bpm": 120,
          "microseconds_per_quarter": 500000
        },
        {
          "time": 0,
          "type": "note_on",
          "channel": 1,
          "note": 60,
          "velocity": 80
        }
      ]
    }
  ]
}
```

---

### Verbose Compilation

```bash
# See what's happening during compilation
mmdc compile song.mmd -v
```

**Useful for**:
- Debugging slow compilations
- Understanding import resolution
- Checking expansion results
- Verifying validation passes

---

### CI/CD Integration

```bash
# Disable color and progress for scripts
mmdc compile song.mmd --no-color --no-progress

# Check exit code
if [ $? -eq 0 ]; then
  echo "Compilation successful"
else
  echo "Compilation failed"
  exit 1
fi
```

---

### Single-Track Output

```bash
# Compile to single-track format (all events in one track)
mmdc compile song.mmd --midi-format 0 -o single.mid
```

**Use case**: Simpler MIDI files for basic playback devices.

---

### Development Workflow

```bash
# Quick syntax check (skip validation for speed)
mmdc compile dev.mmd --no-validate --format table

# Full compilation with validation
mmdc compile dev.mmd -v

# Export to JSON for testing
mmdc compile dev.mmd --format json | jq '.tracks[0].events'
```

---

## Output Format Details

### MIDI Format

Standard MIDI File (.mid) ready for:
- DAW import (Ableton, FL Studio, Logic, etc.)
- Hardware sequencers
- MIDI players
- Real-time playback (`mmdc play`)

**Features**:
- Standard-compliant SMF
- Configurable format (0, 1, 2)
- Configurable PPQ resolution
- All MIDI 1.0 message types

---

### Table Format

Human-readable terminal output with Rich formatting.

**Features**:
- Color-coded event types
- Note names (C4, D#5) alongside MIDI numbers
- Formatted timing (mm:ss.ms)
- Compact display

**Best for**: Quick inspection, debugging, demonstration

---

### CSV Format

midicsv-compatible CSV format for spreadsheet analysis.

**Columns**:
- Track number
- Time (ticks)
- Event type
- Channel
- Data1 (note/CC number)
- Data2 (velocity/value)
- Text (for meta events)

**Compatible with**:
- Excel / Google Sheets
- Python pandas
- R data analysis
- Database import

**Example**:
```csv
Track,Time,Type,Channel,Data1,Data2,Text
0,0,Tempo,,,120,
0,0,Note_on,1,60,80,
0,480,Note_off,1,60,0,
```

---

### JSON Format

Complete MIDI event data in JSON format.

**Two modes**:
- `json` - Complete data with all metadata
- `json-simple` - Simplified for music analysis tools

**Use cases**:
- Programmatic MIDI processing
- Web applications
- Music analysis tools
- Data visualization

---

## Performance

### Compilation Speed

**Benchmarks** (on typical hardware):

| File Size | Events | Compile Time |
|-----------|--------|--------------|
| Small     | <100   | <50ms        |
| Medium    | 100-500 | <200ms      |
| Large     | 1000+  | <1s          |

**Tips for faster compilation**:
1. Use `--no-validate` (only for development)
2. Use `mmdc check` for syntax-only checks
3. Break large files into sections with `@import`
4. Use `@loop` to reduce source file size

---

### File Size

**MIDI file size** depends on:
- Number of events
- PPQ resolution
- Number of tracks
- SysEx messages (if any)

**Typical sizes**:
- 1-minute song: 2-5 KB
- 5-minute song: 10-20 KB
- Complex automation: 50-100 KB

**Comparison**:
- Higher PPQ = Larger files (but more precise timing)
- Format 1 (multi-track) slightly larger than Format 0

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0    | Success |
| 1    | Parse error |
| 2    | Validation error |
| 3    | Expansion error |
| 4    | I/O error |

**Script usage**:
```bash
if mmdc compile song.mmd; then
  echo "Compilation succeeded"
else
  echo "Compilation failed with code $?"
fi
```

---

## Common Issues

### "Parse error: Unexpected token"

**Problem**: Syntax error in MMD file.

**Solution**: Check command spelling and syntax. See [Troubleshooting Guide](../reference/troubleshooting.md#parse-errors).

---

### "Validation error: MIDI value out of range"

**Problem**: Used value outside valid MIDI range (0-127).

**Solution**: Fix the value:
```yaml
# ❌ Wrong
- cc 1.7.200  # Value > 127

# ✅ Correct
- cc 1.7.127  # Max value
```

---

### "Timing must be monotonically increasing"

**Problem**: Events are out of chronological order.

**Solution**: Sort timing markers in ascending order:
```yaml
# ❌ Wrong
[00:03.000]
[00:02.000]  # Goes backwards!

# ✅ Correct
[00:02.000]
[00:03.000]
```

---

### "Import not found"

**Problem**: Imported file doesn't exist.

**Solution**: Check import path (relative to current file):
```yaml
# ❌ Wrong
@import "/absolute/path/device.mmd"

# ✅ Correct
@import "devices/device.mmd"
@import "../shared/aliases.mmd"
```

---

### Output file not created

**Problem**: Permission error or invalid path.

**Solution**:
```bash
# Check parent directory exists
mkdir -p output/

# Compile with explicit path
mmdc compile song.mmd -o output/song.mid

# Check permissions
ls -la output/
```

---

## Tips & Tricks

### Validate Before Important Work

```bash
# Always validate before live performance
mmdc compile setlist.mmd --validate -v
```

---

### Use Appropriate PPQ

```bash
# Standard resolution for most use cases
mmdc compile song.mmd --ppq 480

# High precision for automation-heavy songs
mmdc compile automation.mmd --ppq 960

# Lower resolution for simple click tracks
mmdc compile click.mmd --ppq 240
```

---

### Quick Development Cycle

```bash
# 1. Check syntax (fastest)
mmdc check song.mmd

# 2. Inspect events
mmdc compile song.mmd --format table

# 3. Full compile
mmdc compile song.mmd -v
```

---

### CSV Analysis Workflow

```bash
# Export to CSV
mmdc compile song.mmd --format csv -o events.csv

# Analyze with Python
python3 << EOF
import pandas as pd
df = pd.read_csv('events.csv')
print(df.groupby('Type').size())
EOF
```

---

## See Also

- [validate command](validate.md) - Validation-only mode
- [check command](check.md) - Syntax check only
- [inspect command](inspect.md) - Detailed event inspection
- [play command](play.md) - Real-time MIDI playback
- [Troubleshooting Guide](../reference/troubleshooting.md) - Common issues
- [First Song Tutorial](../getting-started/first-song.md) - Complete example

---

**Next Steps**: Learn about [validation](validate.md) or try [real-time playback](play.md).
