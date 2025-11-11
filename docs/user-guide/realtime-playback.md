# Real-time MIDI Playback Guide

> Complete guide to using MIDI Markdown's real-time playback engine with interactive Terminal UI

## Overview

MML's real-time playback engine enables live MIDI performance directly from `.mmd` files to connected MIDI devices. Instead of compiling to a `.mid` file, the `play` command sends MIDI events in real-time with sub-5ms timing precision.

**Key Features:**
- **Interactive Terminal UI** with live event visualization
- **Keyboard controls** for play/pause/stop
- **Tempo tracking** with dynamic tempo changes
- **Sub-5ms timing precision** using hybrid scheduler
- **MIDI port management** with automatic device detection
- **Simple mode** for automation and CI environments

## Quick Start

### 1. List Available MIDI Ports

Before playback, discover available MIDI output ports on your system:

```bash
mmdc play --list-ports
```

**Example Output:**
```
Available MIDI output ports:
  0: IAC Driver Bus 1
  1: IAC Driver MIDI Markdown
  2: Quad Cortex USB MIDI
  3: Eventide H90 MIDI
```

### 2. Play with Interactive TUI

Launch playback with the full Terminal UI experience:

```bash
mmdc play song.mmd --port "IAC Driver Bus 1"
```

**Or use port index:**
```bash
mmdc play song.mmd --port 0
```

### 3. Simple Mode (No UI)

For automation, CI/CD, or non-TTY environments:

```bash
mmdc play song.mmd --port 0 --no-ui
```

## Terminal UI Display

When using the default TUI mode, you'll see a Rich-based interface with real-time updates:

```
╭─────────────────────────────────────────────────────────────╮
│            MIDI Markup Realtime Player                      │
│                                                              │
│ File:  song.mmd                                             │
│ Port:  IAC Driver Bus 1                                     │
│ Title: My Performance Song                                  │
╰─────────────────────────────────────────────────────────────╯

Progress: ████████████████░░░░░░░░░░░░░░░░░░░ 45%  00:23 / 00:50

Status: ▶ PLAYING  |  Tempo: 120.0 BPM  |  Tick: 11040

╭─────────────────── Recent Events ───────────────────╮
│ Time     Type            Channel  Data              │
│ 00:22.5  NOTE_ON         1        C4, Vel: 80       │
│ 00:22.0  NOTE_OFF        1        C4, Vel: 0        │
│ 00:21.5  CONTROL_CHANGE  1        CC7: 100          │
│ 00:21.0  PROGRAM_CHANGE  1        PC: 10            │
│ 00:20.5  NOTE_ON         1        E4, Vel: 85       │
│ ...                                                  │
╰─────────────────────────────────────────────────────╯

╭──────────────────── Controls ───────────────────────╮
│ [Space]  Play / Pause                               │
│ [Q]      Quit                                       │
│ [R]      Restart (future)                           │
╰─────────────────────────────────────────────────────╯
```

### TUI Components

1. **Header Panel** - File name, MIDI port, and song title (from frontmatter)
2. **Progress Bar** - Visual timeline with MM:SS time display and percentage
3. **Status Bar** - Playback state (PLAYING/PAUSED/STOPPED), current tempo, and tick position
4. **Event History** - Last 20 MIDI events sent, with timestamps and details
5. **Controls Panel** - Available keyboard shortcuts

### Display Refresh

- **30 FPS refresh rate** for smooth, flicker-free updates
- **Thread-safe state** synchronized across display, scheduler, and keyboard threads
- **Live event capture** via scheduler callbacks

## Keyboard Controls

| Key   | Action           | Description                                      |
|-------|------------------|--------------------------------------------------|
| Space | Play / Pause     | Toggle playback. Press again to resume.         |
| Q     | Quit             | Stop playback and exit immediately.             |
| R     | Restart (future) | Return to start and play from beginning. (TODO) |

**Notes:**
- Keyboard controls work during playback without blocking MIDI output
- Uses `readchar` library for cross-platform non-blocking input
- Ctrl+C also triggers graceful shutdown

## Port Selection

### By Name (Recommended)

Specify the exact port name:

```bash
mmdc play song.mmd --port "IAC Driver Bus 1"
```

**Advantages:**
- Clear and explicit
- Works across systems if device name matches
- Self-documenting in scripts

### By Index

Use numeric index from `--list-ports`:

```bash
mmdc play song.mmd --port 0
```

**Advantages:**
- Shorter command
- Useful for scripting with consistent port order

**Caution:** Port indices may change if MIDI devices are connected/disconnected.

## Platform Notes

### macOS

**Virtual MIDI Ports:**

1. Open **Audio MIDI Setup** (`/Applications/Utilities/`)
2. Window → Show MIDI Studio
3. Double-click **IAC Driver**
4. Enable "Device is online"
5. Create buses (e.g., "IAC Driver Bus 1")

**Testing Playback:**

Use a MIDI monitor app like [MIDI Monitor](https://www.snoize.com/MIDIMonitor/) to verify events are being sent.

### Linux

**Virtual MIDI Ports:**

Install `virmidi` kernel module:

```bash
sudo modprobe snd-virmidi
```

Or use ALSA loopback:

```bash
sudo modprobe snd-aloop
```

List ports:

```bash
aconnect -o
```

### Windows

**Virtual MIDI Ports:**

Install a virtual MIDI driver like:
- [loopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html)
- [VirtualMIDI](https://www.tobias-erichsen.de/software/virtualmidi.html)

Create a virtual port, then use with MML:

```bash
mmdc play song.mmd --port "loopMIDI Port"
```

## Timing Precision

The playback engine uses a **hybrid sleep/busy-wait scheduler** for sub-5ms timing precision:

1. **Coarse sleep** for events >10ms away
2. **Busy-wait** for final <5ms before event send
3. **Tempo tracking** with dynamic tempo map for tempo changes
4. **Tick-to-ms conversion** respecting frontmatter PPQ and time signature

**Result:** Accurate playback suitable for live performance and automation tasks.

## Simple Mode

### When to Use

- **Automation scripts** that need exit codes
- **CI/CD pipelines** testing MIDI output
- **Non-TTY environments** (no terminal available)
- **Background processes** where TUI isn't needed

### Example

```bash
mmdc play automation.mmd --port 0 --no-ui
```

**Output:**
```
Compiling: automation.mmd
Opening MIDI port: IAC Driver Bus 1
Duration: 30.50s (104 events)

⠋ Playing...

✓ Done
```

### Exit Codes

- `0` - Playback completed successfully
- `1` - Error (file not found, port error, compilation error)

## Troubleshooting

### "Error: File not found"

**Cause:** MMD file path is incorrect.

**Solution:**
```bash
# Use absolute path
mmdc play /path/to/song.mmd --port 0

# Or relative from current directory
mmdc play ./song.mmd --port 0
```

### "Error: --port is required for playback"

**Cause:** Forgot to specify MIDI output port.

**Solution:**
```bash
# List ports first
mmdc play --list-ports

# Then specify port
mmdc play song.mmd --port "IAC Driver Bus 1"
```

### "Error: No MIDI ports found"

**Cause:** No MIDI output devices are available on your system.

**Solution:**
- **macOS:** Enable IAC Driver in Audio MIDI Setup
- **Linux:** Load `snd-virmidi` or `snd-aloop` kernel module
- **Windows:** Install loopMIDI or VirtualMIDI driver

### "Compilation error"

**Cause:** Syntax error or validation failure in MMD file.

**Solution:**
```bash
# Validate syntax first
mmdc validate song.mmd

# Check for detailed errors
mmdc compile song.mmd --format table
```

### "No TTY detected, falling back to simple mode"

**Cause:** Running in environment without terminal (CI/CD, background process).

**Behavior:** Automatically falls back to simple mode (same as `--no-ui`).

**Solution:** This is normal! If you want TUI, run in a proper terminal.

### Keyboard controls not working

**Cause:** `readchar` library not installed or not supported.

**Solution:**
```bash
# Reinstall with optional dependencies
pip install --upgrade mmdc[tui]

# Or install readchar directly
pip install readchar
```

## Advanced Usage

### Scripting Example

Automate playback in a shell script:

```bash
#!/bin/bash

# Script: play_setlist.sh
# Plays a setlist of MMD files to Quad Cortex

MIDI_PORT="Quad Cortex USB MIDI"

for song in setlist/*.mmd; do
    echo "Playing: $song"
    mmdc play "$song" --port "$MIDI_PORT" --no-ui

    if [ $? -ne 0 ]; then
        echo "Error playing $song"
        exit 1
    fi

    sleep 2  # Pause between songs
done

echo "Setlist complete!"
```

### Integration with DAW

Route MMD playback to your DAW:

1. Create virtual MIDI port (IAC Bus on macOS)
2. Set DAW to listen on that port
3. Play MMD file to virtual port
4. DAW records incoming MIDI

```bash
mmdc play song.mmd --port "IAC Driver Bus 1"
```

### Live Performance Workflow

1. **Rehearsal**: Use TUI mode to verify timing and events
2. **Soundcheck**: Test with `--no-ui` for stability
3. **Performance**: Run in background with script automation
4. **Backup**: Keep compiled `.mid` files for safety

## Implementation Details

### Architecture

```
┌─────────────────────────────────────────────┐
│          RealtimePlayer (High-level)        │
│   - play() / pause() / resume() / stop()    │
└──────────────┬──────────────────────────────┘
               │
       ┌───────┴────────┐
       │                │
┌──────▼──────┐  ┌──────▼──────────────────┐
│  Scheduler  │  │    TempoTracker         │
│  (Thread)   │  │  - Tempo map            │
│             │  │  - Tick-to-ms           │
│  - Events   │◄─┤  - Dynamic tempo        │
│  - Timing   │  └─────────────────────────┘
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│   MIDIOutputManager │
│   (python-rtmidi)   │
│   - Port selection  │
│   - Send messages   │
└─────────────────────┘
```

### Thread Model

1. **Main Thread** - TUI display loop (30 FPS refresh)
2. **Scheduler Thread** - Event timing and MIDI send
3. **Keyboard Thread** - Non-blocking input capture

**Synchronization:** Thread-safe `TUIState` with lock-based state snapshots.

### Dependencies

- `python-rtmidi` - Real-time MIDI I/O
- `rich` - Terminal UI components
- `readchar` - Cross-platform keyboard input (optional, fallback available)

## See Also

- [CLI Reference](../cli-reference/overview.md) - Complete `play` command documentation
- [Getting Started](../getting-started/quickstart.md) - Introduction to MML
- [Examples](../getting-started/examples-guide.md) - Sample MMD files to try

## Feedback

Encounter issues with real-time playback? Please report at:
https://github.com/cjgdev/midi-markdown/issues
