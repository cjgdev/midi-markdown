# Getting Started with MIDI Markdown

Get up and running with MMD in 5 minutes.

## What is MMD?

MIDI Markdown (MMD) is a human-readable, text-based format for creating MIDI sequences. Write MIDI commands in a simple, markdown-inspired syntax and compile them to standard MIDI files.

## Prerequisites

- **Python 3.12+**
- **UV** package manager (recommended) or pip

## Quick Installation

```bash
# Clone the repository
git clone https://github.com/cjgdev/midi-markdown.git
cd midi-markdown

# Install with UV (recommended)
uv sync

# Verify installation
uv run mmdc version
```

For detailed installation instructions, see [Installation Guide](installation.md).

## Your First MMD File

Create a file called `hello.mmd`:

```yaml
---
title: "Hello MIDI"
tempo: 120
time_signature: [4, 4]
ppq: 480
---

# Simple melody
[00:00.000]
- note_on 1.60 80 1b   # Middle C, velocity 80, duration 1 beat

[00:01.000]
- note_on 1.64 80 1b   # E

[00:02.000]
- note_on 1.67 80 1b   # G

[00:03.000]
- note_on 1.72 80 2b   # C (octave higher), 2 beats

[00:05.000]
- end_of_track
```

## Compile to MIDI

```bash
# Create output directory
mkdir -p output

# Compile your file
uv run mmdc compile hello.mmd -o output/hello.mid

# Success! You should see:
# ✅ Compilation successful (0.12s)
```

## Play Your MIDI File

```bash
# macOS
open output/hello.mid

# Linux with timidity
timidity output/hello.mid

# Windows
start output/hello.mid
```

## Understanding the Syntax

### Frontmatter (YAML)
```yaml
---
title: "Song Title"       # Song metadata
tempo: 120                # BPM
time_signature: [4, 4]    # Time signature
ppq: 480                  # Pulses per quarter note
---
```

### Timing Markers
```
[00:00.000]              # Absolute time: mm:ss.milliseconds
[1.1.0]                  # Musical time: bars.beats.ticks
[+1b]                    # Relative: +1 beat from previous
[@]                      # Simultaneous with previous event
```

### MIDI Commands
```
- note_on 1.60 80 1b     # Channel.note velocity duration
- note_off 1.60          # Channel.note
- cc 1.7.100             # Channel.controller.value (CC7 = volume)
- pc 1.5                 # Channel.program (change instrument)
- tempo 140              # Change tempo
- marker "Chorus"        # Add marker
```

## Next Steps

### Learn by Example
Work through the progressive examples:

```bash
# Start with the basics
uv run mmdc compile examples/00_basics/01_hello_world.mmd
uv run mmdc compile examples/00_basics/02_minimal_midi.mmd
uv run mmdc compile examples/00_basics/03_simple_click_track.mmd

# Move to intermediate
uv run mmdc compile examples/01_timing/01_tempo_changes.mmd
uv run mmdc compile examples/02_midi_features/01_multi_channel_basic.mmd

# Explore advanced features
uv run mmdc compile examples/03_advanced/10_comprehensive_song.mmd
uv run mmdc compile examples/04_device_libraries/01_device_import.mmd
```

See [examples-guide.md](examples-guide.md) for a complete learning path.

### Read the Guides

- **[Basic Syntax](../user-guide/mmd-syntax.md)** - Detailed syntax reference
- **[Timing Systems](../user-guide/timing-system.md)** - All four timing paradigms
- **[Alias System](../user-guide/alias-system.md)** - Create reusable command shortcuts
- **[Device Libraries](../user-guide/device-libraries.md)** - Control hardware with high-level commands
- **[Real-time Playback](../user-guide/realtime-playback.md)** - Live MIDI playback with interactive Terminal UI

### Reference Documentation

- **[Language Specification](../reference/specification.md)** - Complete MMD reference (1,300+ lines)
- **[CLI Commands](../cli-reference/overview.md)** - Command-line reference
- **[MIDI Commands](../user-guide/midi-commands.md)** - Quick MIDI command lookup

## Common Commands

```bash
# Compile with verbose output
uv run mmdc compile song.mmd -o output.mid -v

# Validate before compiling
uv run mmdc validate song.mmd

# Quick syntax check (faster)
uv run mmdc check song.mmd

# Real-time playback (NEW)
uv run mmdc play song.mmd --port "IAC Driver Bus 1"
uv run mmdc play --list-ports  # List available MIDI ports

# Custom PPQ (higher resolution)
uv run mmdc compile song.mmd --ppq 960

# Single-track MIDI (format 0)
uv run mmdc compile song.mmd --format 0
```

## Getting Help

- **Documentation**: Browse the [docs/](../index.md) directory
- **Examples**: Study the [examples/](https://github.com/cjgdev/midi-markdown/tree/main/examples) directory (51 examples across 7 categories)
- **Issues**: Report bugs on [GitHub](https://github.com/cjgdev/midi-markdown/issues)
- **CLI Help**: Run `uv run mmdc --help`

## What's Next?

Now that you've created your first MIDI file, explore these topics:

1. **Real-time playback** - Play MIDI files live with interactive TUI ([Real-time Playback Guide](../user-guide/realtime-playback.md))
2. **Multi-channel compositions** - Use multiple instruments (example 05)
3. **Control change automation** - Automate volume, pan, effects (example 06)
4. **Variables and loops** - Create patterns efficiently (examples 10-11)
5. **Device libraries** - Control guitar processors, effects units (example 13)
6. **Musical timing** - Work in bars.beats.ticks (example 12)

Happy MIDI composing! 🎵
