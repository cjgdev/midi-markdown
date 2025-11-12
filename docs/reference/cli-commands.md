# CLI Commands Reference

Complete reference for all MIDI Markdown CLI commands.

## Overview

The `mmdc` command-line tool provides several commands for working with MMD files. Each command is documented in detail in the [CLI Reference](../cli-reference/overview.md) section.

## Quick Reference

### Compilation Commands

- **[compile](../cli-reference/compile.md)** - Compile MMD to MIDI, JSON, or CSV
- **[validate](../cli-reference/validate.md)** - Validate MMD files without compiling
- **[check](../cli-reference/check.md)** - Quick syntax check

### Playback Commands

- **[play](../cli-reference/play.md)** - Real-time MIDI playback with TUI
- **[inspect](../cli-reference/inspect.md)** - Inspect compiled events

### Interactive Commands

- **[repl](../cli-reference/repl.md)** - Interactive REPL mode

## Common Usage Patterns

### Compile to MIDI
```bash
mmdc compile song.mmd -o output.mid
```

### Validate Before Compiling
```bash
mmdc validate song.mmd && mmdc compile song.mmd -o output.mid
```

### Real-time Playback
```bash
mmdc play song.mmd --port 0
```

### Export to JSON
```bash
mmdc compile song.mmd --format json -o events.json
```

## See Also

- [CLI Reference Overview](../cli-reference/overview.md) - Detailed command documentation
- [Getting Started](../getting-started/quickstart.md) - Introduction to MMD
- [User Guide](../user-guide/mmd-syntax.md) - MMD syntax reference
