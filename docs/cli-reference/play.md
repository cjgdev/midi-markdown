# Command: play

> **Audience**: Users
> **Level**: Beginner to Advanced

Play MMD files in real-time to MIDI output devices with interactive terminal UI.

---

## Synopsis

```bash
mmdc play [OPTIONS] [INPUT_FILE]
mml play [OPTIONS] [INPUT_FILE]         # Shorter alias
```

---

## Description

The `play` command provides **real-time MIDI playback** of compiled MMD files directly to hardware or software MIDI devices. Unlike `compile` which generates MIDI files, `play` sends MIDI messages in real-time with sub-5ms timing precision.

**Key Features**:
- Interactive Terminal UI (TUI) with 30 FPS refresh
- Real-time event visualization and progress tracking
- Keyboard controls (Space/Arrow keys/Q/R) for playback control
- Multiple seeking modes: time-based (5s), beat-based (1 beat), and bar-based (1 bar)
- Musical navigation using Shift/Ctrl + arrow keys
- Support for virtual MIDI ports (IAC, loopMIDI, ALSA)
- Tempo tracking and dynamic tempo changes
- Event scheduling with microsecond precision

**What play does**:

1. **Parse** - Parse MMD file to AST
2. **Compile** - Convert to Intermediate Representation (IR)
3. **Connect** - Open MIDI output port
4. **Schedule** - Queue events with precise timing
5. **Play** - Send MIDI messages in real-time
6. **Display** - Show progress and live event feed in TUI

**Typical use cases**:
- Live performance automation (preset changes, CC automation)
- Testing MIDI sequences before recording
- Controlling hardware synthesizers and effects processors
- Syncing with DAWs via virtual MIDI ports

---

## Options

### Port Selection

#### `--port, -p PORT`
MIDI output port name or index (required for playback).

```bash
# By port name (recommended)
mmdc play song.mmd --port "IAC Driver Bus 1"

# By port index
mmdc play song.mmd --port 0

# Shorter alias
mml play song.mmd -p "Network Session 1"
```

**Finding port names**: Use `--list-ports` to see available ports.

---

#### `--list-ports`
List available MIDI output ports and exit.

```bash
# Show all available MIDI ports
mmdc play --list-ports

# Example output:
# Available MIDI output ports:
#   0: IAC Driver Bus 1
#   1: Network Session 1
#   2: QuadCortex MIDI 1
```

**Note**: This command doesn't require an input file.

---

### Display Options

#### `--no-ui`
Disable interactive TUI and use simple progress display.

```bash
# Simple mode (no keyboard controls)
mmdc play song.mmd --port 0 --no-ui
```

**When to use**:
- Running in non-interactive environment (CI/scripts)
- Terminal doesn't support TUI features
- Piping output to logs
- Automated playback scenarios

**Output difference**:
- **With TUI** (default): Full-screen interactive display with progress bar, event list, and keyboard controls
- **No UI**: Simple spinner with "Playing..." message

---

### Debugging

#### `--debug`
Show full error tracebacks instead of formatted errors.

```bash
mmdc play song.mmd --port 0 --debug
```

**Useful for**: Bug reports, troubleshooting MIDI issues, development.

---

## Interactive TUI

The default playback mode features a rich Terminal UI with:

### Display Components

**Header**:
```
╭──────────────────────────────────────────────╮
│  🎵 MMD Player - Live MIDI Playback          │
│  File: performance.mmd                       │
│  Port: IAC Driver Bus 1                      │
│  Title: Live Performance Automation          │
╰──────────────────────────────────────────────╯
```

**Progress Bar**:
```
Progress: ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 45%
Time: 0:23 / 0:50 (27s remaining)
Tempo: 120 BPM | Events: 104 total
```

**Live Event Feed** (last 20 events):
```
Recent Events:
  0:23.245  Note On    Ch1  C4 (60) vel=80
  0:23.250  CC         Ch1  #7 (Volume) = 100
  0:23.500  Note Off   Ch1  C4 (60)
  0:24.000  PC         Ch1  Preset 5
```

**Footer**:
```
Controls: [Space] Play/Pause | [← →] ±5s | [Shift+← →] ±1 beat | [Ctrl+← →] ±1 bar | [Q] Quit
Status: ▶ Playing
```

### Keyboard Controls

| Key | Action | Description |
|-----|--------|-------------|
| **Space** | Play/Pause | Toggle playback (preserves position) |
| **← →** | Seek Time | Jump backward/forward 5 seconds |
| **Shift+← →** | Seek Beat | Jump backward/forward 1 beat |
| **Ctrl+← →** | Seek Bar | Jump backward/forward 1 bar |
| **Q** | Quit | Stop playback and exit |
| **R** | Restart | Jump back to beginning (future) |
| **Ctrl+C** | Cancel | Same as Q (graceful exit) |
| **Ctrl+D** | Exit | Immediate exit |

**Playback States**:
- `▶ Playing` - Active playback
- `⏸ Paused` - Paused (resume with Space)
- `⏹ Stopped` - Playback complete or quit

---

## Platform-Specific Setup

### macOS - IAC Driver

**IAC Driver** provides virtual MIDI ports for routing between applications.

**Setup**:
1. Open **Audio MIDI Setup** (Applications > Utilities)
2. Window > Show MIDI Studio
3. Double-click **IAC Driver** icon
4. Check "Device is online"
5. Add buses as needed (e.g., "Bus 1", "Bus 2")

**Usage**:
```bash
# List IAC ports
mmdc play --list-ports
# Output: 0: IAC Driver Bus 1

# Play to IAC
mmdc play song.mmd --port "IAC Driver Bus 1"
```

**Connecting to DAW**:
- In your DAW (Logic, Ableton, etc.), select "IAC Driver Bus 1" as MIDI input
- MMD player sends MIDI → IAC → DAW receives

---

### Linux - ALSA

**ALSA** (Advanced Linux Sound Architecture) provides MIDI support on Linux.

**Setup**:
```bash
# Install ALSA utilities
sudo apt-get install alsa-utils

# List MIDI ports
aconnect -l

# Create virtual port (optional)
sudo modprobe snd-virmidi
```

**Usage**:
```bash
# List ports
mmdc play --list-ports

# Play to ALSA port
mmdc play song.mmd --port "TiMidity port 0"
```

**Virtual MIDI** (virmidi):
```bash
# Load virmidi kernel module (creates 4 virtual ports)
sudo modprobe snd-virmidi

# Make persistent (add to /etc/modules)
echo "snd-virmidi" | sudo tee -a /etc/modules
```

---

### Windows - loopMIDI

**loopMIDI** by Tobias Erichsen provides virtual MIDI ports on Windows.

**Setup**:
1. Download loopMIDI from [tobias-erichsen.de](https://www.tobias-erichsen.de/software/loopmidi.html)
2. Install and run loopMIDI
3. Click **+** to add virtual port (e.g., "loopMIDI Port 1")
4. Leave loopMIDI running in background

**Usage**:
```bash
# List ports
mmdc play --list-ports
# Output: 0: loopMIDI Port 1

# Play to loopMIDI
mmdc play song.mmd --port "loopMIDI Port 1"
```

**Connecting to DAW**:
- In DAW, select "loopMIDI Port 1" as MIDI input
- MMD player sends MIDI → loopMIDI → DAW receives

---

## Examples

### List Available Ports

```bash
# Show all MIDI output ports
mmdc play --list-ports
```

**Example output**:
```
Available MIDI output ports:
  0: IAC Driver Bus 1
  1: Network Session 1
  2: QuadCortex MIDI 1
  3: H90 MIDI 1
```

---

### Play to Virtual Port (macOS)

```bash
# Play to IAC Driver (default virtual port on macOS)
mmdc play performance.mmd --port "IAC Driver Bus 1"
```

**Use case**: Route MIDI to DAW (Logic, Ableton) for recording.

---

### Play to Hardware Device

```bash
# Play directly to hardware synthesizer
mmdc play song.mmd --port "QuadCortex MIDI 1"
```

**Use case**: Live performance automation, preset changes, CC automation.

---

### Play by Port Index

```bash
# Use port index instead of name
mmdc play song.mmd --port 0
```

**When to use**: Scripting, when port names are long or contain special characters.

---

### Simple Mode (No UI)

```bash
# Disable TUI for non-interactive use
mmdc play song.mmd --port 0 --no-ui
```

**Output**:
```
Compiling: song.mmd
Opening MIDI port: IAC Driver Bus 1
Duration: 50.00s (104 events)

⠋ Playing...
✓ Done
```

**Use case**: Automated playback, scripts, CI/CD testing.

---

### Interactive Playback with Controls

```bash
# Full TUI with keyboard controls
mmdc play setlist.mmd --port "IAC Driver Bus 1"
```

**During playback**:
- Press **Space** to pause/resume
- Press **Q** to quit early
- Press **R** to restart from beginning

---

### Multiple Devices

```bash
# First, identify your devices
mmdc play --list-ports

# Play to specific device by name
mmdc play quad_cortex_presets.mmd --port "QuadCortex MIDI 1"
mmdc play h90_automation.mmd --port "H90 MIDI 1"
```

---

### Testing Before Performance

```bash
# Test automation sequence before live show
mmdc play setlist.mmd --port "IAC Driver Bus 1"

# Watch event feed in TUI to verify timing
# Press Q to stop early if issues found
# Edit MMD file, recompile, test again
```

---

## Performance

### Timing Precision

**Scheduler**: Sub-5ms event timing precision
- Hybrid sleep/busy-wait algorithm
- Adaptive scheduling for system load
- No drift over long sequences

**TUI Refresh**: 30 FPS (33ms refresh interval)
- Non-blocking display updates
- Thread-safe state management
- No impact on MIDI timing

---

### Resource Usage

**Memory**: ~10-20 MB for typical sequences
**CPU**: <5% on modern hardware
**Latency**: <5ms end-to-end (parse → MIDI out)

**Tested with**:
- 1000+ event sequences
- 30-minute performances
- Dynamic tempo changes
- Concurrent CC automation

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0    | Playback completed successfully |
| 1    | Compilation error (invalid MML) |
| 2    | MIDI port not found or unavailable |
| 3    | File not found |
| 4    | Playback interrupted (Ctrl+C, Q) |

**Script usage**:
```bash
if mmdc play song.mmd --port 0; then
  echo "Playback successful"
else
  echo "Playback failed with code $?"
fi
```

---

## Common Issues

### "MIDI port not found"

**Problem**: Specified port doesn't exist or isn't available.

**Solution**:
```bash
# List all available ports
mmdc play --list-ports

# Use exact port name from list
mmdc play song.mmd --port "IAC Driver Bus 1"
```

**Common causes**:
- Port name misspelled (case-sensitive)
- Virtual MIDI driver not running (loopMIDI, IAC)
- Hardware device not connected or powered off
- Port in use by another application

---

### "No TTY detected, falling back to simple mode"

**Problem**: TUI can't be displayed in current environment.

**Explanation**: This happens when running in non-interactive environments (scripts, CI/CD).

**Solution**: This is expected behavior, playback continues in simple mode.

**Manual fallback**:
```bash
# Explicitly use simple mode
mmdc play song.mmd --port 0 --no-ui
```

---

### TUI not refreshing properly

**Problem**: Display freezes or doesn't update smoothly.

**Possible causes**:
- Terminal doesn't support ANSI escape codes
- Terminal too small (minimum 80x24 recommended)
- Running over SSH without proper terminal emulation

**Solutions**:
```bash
# Use simple mode
mmdc play song.mmd --port 0 --no-ui

# Or use modern terminal emulator (iTerm2, Windows Terminal, Alacritty)
```

---

### Events not playing at correct time

**Problem**: MIDI events arrive too early or too late.

**Diagnosis**:
```bash
# Check if issue is timing or compilation
mmdc inspect song.mmd --format table

# Verify event times are correct
```

**Common causes**:
- System under heavy load (close other apps)
- Incorrect tempo in frontmatter
- Musical timing without time signature
- PPQ too low (try higher resolution)

**Solutions**:
```bash
# Increase PPQ for better precision
mmdc compile song.mmd --ppq 960

# Verify frontmatter
---
tempo: 120
time_signature: "4/4"
ppq: 480
---
```

---

### Hardware device not responding

**Problem**: MIDI port opens but device doesn't respond.

**Checklist**:
1. Verify device is powered on
2. Check MIDI cable connections (if hardware)
3. Confirm device is in MIDI receive mode
4. Verify channel numbers match (1-16)
5. Test with known-working MIDI file

**Debugging**:
```bash
# Inspect compiled events
mmdc inspect song.mmd --format table

# Verify channels, note numbers, CC values
# Compare with device manual
```

---

### "Permission denied" error

**Problem**: Can't access MIDI port due to permissions (Linux).

**Solution** (Linux):
```bash
# Add user to 'audio' group
sudo usermod -a -G audio $USER

# Log out and back in for changes to take effect

# Verify group membership
groups
```

---

## Tips & Tricks

### Quick Port Selection

```bash
# Create shell alias for your main port
alias mml-play='mmdc play --port "IAC Driver Bus 1"'

# Usage
mml-play song.mmd
```

---

### Pause, Resume, and Seek

```bash
# Start playback
mmdc play setlist.mmd --port 0

# During playback:
# - Press Space to pause at current position
# - Press ← → to seek backward/forward 5 seconds (time-based)
# - Press Shift+← → to seek backward/forward 1 beat (musical)
# - Press Ctrl+← → to seek backward/forward 1 bar (musical)
# - Make notes of issues
# - Press Space to resume from same position
# - Press Q to quit
```

**Seeking modes explained**:
- **Time-based** (Arrow keys): Fixed 5-second intervals, independent of tempo/time signature
- **Beat-based** (Shift+Arrow): Jump by 1 beat (respects tempo and PPQ)
- **Bar-based** (Ctrl+Arrow): Jump by 1 bar (respects time signature, e.g., 4 beats in 4/4)

**Use cases for seeking**:
- **Time seeking**: Quick navigation through long performances
- **Beat seeking**: Fine-tune position for precise musical timing
- **Bar seeking**: Jump between song sections (verse, chorus, bridge)
- **Combined**: Use bar seeking for large jumps, beat seeking for fine adjustments

---

### Musical Navigation (Beat and Bar Seeking)

Musical seeking respects your song's time signature and tempo, making it perfect for navigating through structured compositions:

```bash
# Example: Song in 4/4 time at 120 BPM
mmdc play song.mmd --port 0

# During playback:
# - Ctrl+→ jumps forward 4 beats (1 bar in 4/4)
# - Shift+→ jumps forward 1 beat (0.5 seconds at 120 BPM)
# - Ctrl+← jumps backward 1 bar
# - Shift+← jumps backward 1 beat
```

**Why musical seeking matters**:
- **Tempo-aware**: Beat/bar length adjusts with tempo changes
- **Time signature aware**: Bar seeking respects 3/4, 4/4, 5/4, etc.
- **Musically aligned**: Land on downbeats, not arbitrary time points
- **Workflow**: Jump to bar 8 (chorus), then fine-tune with beat seeking

**Examples by time signature**:
```yaml
# 4/4 time (common time)
time_signature: "4/4"
# 1 bar = 4 beats, 1 beat = quarter note

# 3/4 time (waltz)
time_signature: "3/4"
# 1 bar = 3 beats, 1 beat = quarter note

# 6/8 time (compound meter)
time_signature: "6/8"
# 1 bar = 6 beats, 1 beat = eighth note (compound feel: 2 dotted quarters)

# 5/4 time (progressive rock)
time_signature: "5/4"
# 1 bar = 5 beats, 1 beat = quarter note
```

**Practical workflow**:
```bash
# 1. Start playback
mmdc play setlist.mmd --port 0

# 2. Jump to chorus (e.g., bar 16) using Ctrl+→ repeatedly
#    (Or set up markers in your MMD file)

# 3. Fine-tune position with Shift+← → to land exactly on the downbeat

# 4. Test timing, adjust if needed

# 5. Press Q to quit when done
```

---

### Testing Specific Sections

```bash
# Edit MMD to comment out unwanted sections
# [00:00.000]
# - note_on 1.60 80 1b
# ...
# #[01:00.000]  # Comment out everything after 1 minute
# #- pc 1.10

# Play reduced file
mmdc play test_section.mmd --port 0
```

---

### DAW Integration Workflow

```bash
# 1. Setup virtual MIDI port (IAC/loopMIDI)
# 2. Configure DAW to receive from virtual port
# 3. Arm MIDI track in DAW for recording
# 4. Play MMD file
mmdc play automation.mmd --port "IAC Driver Bus 1"

# 5. DAW records incoming MIDI
# 6. Edit recorded MIDI in DAW if needed
```

---

### Live Performance Checklist

```bash
# Before show:
# 1. Test all devices
mmdc play --list-ports

# 2. Validate MMD files
mmdc validate setlist_*.mmd

# 3. Test playback
mmdc play setlist_01.mmd --port "QuadCortex MIDI 1"

# 4. Create backup copy of MMD files

# 5. Have device libraries ready
ls devices/*.mmd

# During show:
# - Use TUI to monitor playback
# - Press Q to skip songs if needed
# - Have backup MIDI files ready
```

---

### Event Debugging

```bash
# 1. Inspect events before playing
mmdc inspect song.mmd --format table --limit 50

# 2. Verify timing and values
# 3. Play and watch TUI event feed
mmdc play song.mmd --port 0

# 4. Compare TUI feed with inspect output
# 5. Fix any discrepancies in MMD source
```

---

## Advanced Usage

### Scripted Playback

```bash
#!/bin/bash
# play_setlist.sh - Automated setlist playback

PORT="IAC Driver Bus 1"

for song in setlist_*.mmd; do
  echo "Now playing: $song"
  mmdc play "$song" --port "$PORT" --no-ui
  sleep 2  # Pause between songs
done
```

---

### Multi-Device Setup

```bash
# Play different files to different devices
mmdc play guitar.mmd --port "QuadCortex MIDI 1" &
PID1=$!

mmdc play keys.mmd --port "Synthesizer MIDI 1" &
PID2=$!

# Wait for both to complete
wait $PID1
wait $PID2
```

---

### Tempo Control

```yaml
---
title: "Dynamic Tempo Performance"
tempo: 120  # Starting tempo
---

[00:00.000]
- tempo 140  # Speed up at verse

[01:00.000]
- tempo 100  # Slow down for chorus

[02:00.000]
- tempo 120  # Back to normal
```

```bash
# Play with tempo changes
mmdc play dynamic_tempo.mmd --port 0

# TUI will show current tempo in real-time
```

---

## See Also

- [compile command](compile.md) - Generate MIDI files for DAW import
- [inspect command](inspect.md) - Debug event timing and values
- [validate command](validate.md) - Verify MMD before playback
- [Real-time Playback Guide](../user-guide/realtime-playback.md) - Detailed playback documentation
- [Troubleshooting Guide](../reference/troubleshooting.md) - MIDI port and playback issues
- [First Song Tutorial](../getting-started/first-song.md) - Learn MMD basics

---

**Next Steps**: Try [inspecting events](inspect.md) or learn about [device libraries](../user-guide/device-libraries.md).
