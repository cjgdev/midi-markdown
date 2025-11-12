# MMDC CLI Usage Skill

## Purpose
This skill helps users effectively use the MIDI Markdown Compiler (mmdc) command-line interface for compiling, validating, playing, and inspecting MMD files.

## When to Use This Skill
- User wants to compile MMD to MIDI
- User needs to validate or check MMD syntax
- User wants to play MMD files with real-time MIDI output
- User needs to inspect or export MMD in different formats
- User is troubleshooting compilation or validation errors

## Core Commands

### Compile MMD to MIDI
```bash
# Basic compilation
mmdc compile input.mmd -o output.mid

# With custom resolution
mmdc compile song.mmd -o song.mid --ppq 960

# Export to different formats
mmdc compile song.mmd --format json -o events.json
mmdc compile song.mmd --format csv -o events.csv
mmdc compile song.mmd --format table  # Display in terminal
```

### Validate Without Compiling
```bash
# Full validation (recommended before compilation)
mmdc validate song.mmd

# Verbose output with details
mmdc validate song.mmd --verbose

# Just syntax check (no semantic validation)
mmdc check song.mmd
```

### Real-Time Playback
```bash
# Play with TUI (interactive terminal UI)
mmdc play song.mmd --port 0

# List available MIDI ports
mmdc play --list-ports

# Play with specific port by name
mmdc play song.mmd --port "IAC Driver Bus 1"
```

### Inspect Events
```bash
# Display event timeline as table
mmdc inspect song.mmd

# With more detail
mmdc inspect song.mmd --verbose

# Filter by event type
mmdc inspect song.mmd --type note_on
mmdc inspect song.mmd --type cc
```

## Common Options

### Output Formats
- `--format midi` (default) - Standard MIDI file
- `--format json` - JSON representation
- `--format csv` - CSV export (midicsv-compatible)
- `--format table` - Terminal table display

### Resolution/PPQ
- `--ppq 480` (default) - High resolution
- `--ppq 960` - Very high resolution
- `--ppq 192` - Standard resolution

### Verbosity
- `--verbose` - Detailed output
- `--quiet` - Minimal output
- `--debug` - Debug information

## Workflow Examples

### Development Workflow
```bash
# 1. Check syntax while writing
mmdc check song.mmd

# 2. Full validation before compilation
mmdc validate song.mmd

# 3. Inspect events to verify
mmdc inspect song.mmd

# 4. Compile to MIDI
mmdc compile song.mmd -o output.mid

# 5. Test playback
mmdc play song.mmd --port 0
```

### Quick Test Loop
```bash
# Edit, validate, play cycle
mmdc validate song.mmd && mmdc play song.mmd --port 0
```

### Batch Processing
```bash
# Compile all MMD files in directory
for file in *.mmd; do
  mmdc compile "$file" -o "output/$(basename "$file" .mmd).mid"
done

# Validate all examples
mmdc validate examples/**/*.mmd
```

## Troubleshooting

### Validation Errors
```bash
# Get detailed error information
mmdc validate song.mmd --verbose

# Check just syntax first
mmdc check song.mmd

# Inspect specific section
mmdc inspect song.mmd
```

### Playback Issues
```bash
# List all available MIDI ports
mmdc play --list-ports

# Test with different port
mmdc play song.mmd --port 1

# Check events are correct
mmdc inspect song.mmd
```

### Compilation Failures
```bash
# Validate first to see errors
mmdc validate song.mmd

# Check for import issues
mmdc check song.mmd --verbose

# Export to JSON for debugging
mmdc compile song.mmd --format json -o debug.json
```

## Tips and Best Practices

### Always Validate First
Before compiling, always validate to catch errors early:
```bash
mmdc validate song.mmd && mmdc compile song.mmd -o output.mid
```

### Use Inspect for Debugging
When timing or values seem wrong, inspect the events:
```bash
mmdc inspect song.mmd | grep "note_on"
mmdc inspect song.mmd --type cc
```

### Test with Playback
Real-time playback helps verify timing and automation:
```bash
mmdc play song.mmd --port 0
# Use spacebar to pause, Q to quit, R to restart
```

### Export for Analysis
JSON and CSV formats are great for analysis:
```bash
# JSON for programmatic access
mmdc compile song.mmd --format json -o events.json

# CSV for spreadsheet analysis
mmdc compile song.mmd --format csv -o events.csv
```

## Integration with Other Tools

### Using with UV (Python Package Manager)
```bash
# Run from project directory
uv run mmdc compile song.mmd -o output.mid

# Or after installation
mmdc compile song.mmd -o output.mid
```

### Using with Just (Task Runner)
```bash
# If project has justfile
just compile input.mmd output.mid
just validate song.mmd
just run play song.mmd
```

### Piping Output
```bash
# Validate and capture output
mmdc validate song.mmd 2>&1 | tee validation.log

# Inspect and filter
mmdc inspect song.mmd | grep "00:10"
```

## Error Codes

Common exit codes:
- `0` - Success
- `1` - Validation error
- `2` - File not found
- `3` - Compilation error
- `4` - Runtime error (playback)

## Getting Help

```bash
# General help
mmdc --help

# Command-specific help
mmdc compile --help
mmdc validate --help
mmdc play --help
mmdc inspect --help

# Version information
mmdc --version
```

## Quick Reference

| Task | Command |
|------|---------|
| Compile to MIDI | `mmdc compile input.mmd -o output.mid` |
| Validate | `mmdc validate song.mmd` |
| Syntax check | `mmdc check song.mmd` |
| Play with TUI | `mmdc play song.mmd --port 0` |
| List MIDI ports | `mmdc play --list-ports` |
| Inspect events | `mmdc inspect song.mmd` |
| Export JSON | `mmdc compile song.mmd --format json -o out.json` |
| Export CSV | `mmdc compile song.mmd --format csv -o out.csv` |
| Table display | `mmdc compile song.mmd --format table` |

## See Also
- MMD Writing Skill - For help writing MMD files
- examples/ - Example MMD files to compile and test
- docs/user-guide/ - Complete user documentation
- spec.md - Full MMD language specification
