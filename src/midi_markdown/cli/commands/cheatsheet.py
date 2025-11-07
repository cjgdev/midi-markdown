"""Cheatsheet command - quick reference guide."""

from __future__ import annotations

from rich.console import Console
from rich.markdown import Markdown


def cheatsheet() -> None:
    """Show quick reference of common MML commands and workflows.

    Displays a concise cheat sheet covering the most frequently used
    commands and workflows for MIDI Markup Language.

    Examples:
        midimarkup cheatsheet
    """
    console = Console()

    markdown_content = """
# MIDI Markup Language - CLI Cheat Sheet

## Quick Start

```bash
# Create a simple MML file
echo '---
title: "Hello MIDI"
tempo: 120
ppq: 480
---

[00:00.000]
- note_on 1.60 80 1b  # Middle C
' > hello.mml

# Compile to MIDI
midimarkup compile hello.mml

# Play it back
midimarkup play hello.mml --port 0
```

## File Operations

```bash
# Compile MML to MIDI file
midimarkup compile song.mml

# Compile with custom output path
midimarkup compile song.mml -o output/track.mid

# Compile with high resolution (960 PPQ)
midimarkup compile song.mml --ppq 960

# Export to CSV for analysis
midimarkup compile song.mml --format csv -o events.csv

# Export to JSON
midimarkup compile song.mml --format json -o data.json

# Display events as table
midimarkup compile song.mml --format table
```

## Validation & Checking

```bash
# Full validation (recommended before performance)
midimarkup validate song.mml

# Quick syntax check (fast, for development)
midimarkup check song.mml

# Inspect MIDI events without creating files
midimarkup inspect song.mml

# Validate with verbose output
midimarkup validate song.mml -v
```

## Live Performance

```bash
# List available MIDI ports
midimarkup ports

# Play with interactive TUI
midimarkup play song.mml --port 0

# Play without TUI (simple playback)
midimarkup play song.mml --port "IAC Driver" --no-ui

# Start interactive REPL for live composition
midimarkup repl
```

## Device Libraries

```bash
# List all installed device libraries
midimarkup library list

# View library details
midimarkup library info quad_cortex

# Validate a device library
midimarkup library validate devices/custom.mml
```

## Learning & Help

```bash
# Show example MML snippets
midimarkup examples

# View specific example
midimarkup examples hello
midimarkup examples timing
midimarkup examples loop

# Get help for any command
midimarkup --help
midimarkup compile --help

# Check version and dependencies
midimarkup version
```

## Common Workflows

### Development Workflow
```bash
# 1. Edit MML file in your editor
# 2. Quick syntax check on save
midimarkup check song.mml

# 3. Full validation before testing
midimarkup validate song.mml

# 4. Compile to MIDI
midimarkup compile song.mml

# 5. Test playback
midimarkup play song.mml --port 0
```

### Production Workflow
```bash
# 1. Validate all files
midimarkup validate *.mml

# 2. Compile with high resolution
midimarkup compile setlist.mml --ppq 960 -o performance.mid

# 3. Verify MIDI output
midimarkup inspect setlist.mml

# 4. Export for documentation
midimarkup compile setlist.mml --format csv -o timeline.csv
```

### Live Performance Setup
```bash
# 1. Check MIDI ports
midimarkup ports

# 2. Test playback
midimarkup play song.mml --port 0

# 3. Use REPL for interactive control
midimarkup repl
```

## Tips & Tricks

- Use `--verbose` (`-v`) to see detailed compilation steps
- Use `--debug` to see full error tracebacks
- Set `NO_COLOR` environment variable for plain text output
- Use `--no-progress` in CI/CD pipelines
- Combine with device libraries: `@import "devices/quad_cortex.mml"`
- Export to CSV/JSON for programmatic analysis

## Exit Codes

- `0` - Success
- `1` - General error
- `2` - Parse/syntax error
- `3` - Validation error
- `4` - File not found
- `5` - MIDI/runtime error
- `130` - Cancelled by user (Ctrl+C)

## More Information

- Documentation: https://github.com/cjgdev/midi-markdown
- Examples: `midimarkup examples`
- Issues: https://github.com/cjgdev/midi-markdown/issues
"""

    console.print()
    console.print(Markdown(markdown_content))
    console.print()
