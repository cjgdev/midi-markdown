# MMD Syntax Reference

> **Audience**: Users
> **Level**: Beginner to Intermediate

Complete reference for MIDI Markdown (MMD) syntax. This document covers all syntax elements, timing formats, MIDI commands, and directives.

## Table of Contents

- [Document Structure](#document-structure)
- [Frontmatter](#frontmatter)
- [Timing Markers](#timing-markers)
- [MIDI Commands](#midi-commands)
- [Directives](#directives)
- [Comments](#comments)
- [Advanced Features](#advanced-features)
  - [Random Expressions](#random-expressions)
- [Examples](#examples)
- [See Also](#see-also)

---

## Document Structure

An MMD file consists of four main parts:

1. **Frontmatter** (YAML) - Document properties and metadata
2. **Imports** - Device libraries and shared definitions
3. **Definitions** - Variables, aliases, and constants
4. **Events** - Timed MIDI commands

### Basic Example

```yaml
---
title: "My First Song"
author: "Your Name"
tempo: 120
ppq: 480
---

# This is a comment
@define MAIN_CHANNEL 1

[00:00.000]
- tempo 120
- note_on 1.C4 100 1b
```

---

## Frontmatter

Frontmatter uses YAML syntax and must appear at the beginning of the file, enclosed in `---` delimiters.

### Required Properties

None! All frontmatter properties are optional with sensible defaults.

### Common Properties

```yaml
---
title: "Song Title"                 # Document title
author: "Your Name"                 # Author name
description: "What this does"       # Brief description
tempo: 120                          # Default tempo (BPM)
time_signature: [4, 4]              # Time signature [numerator, denominator]
ppq: 480                            # Pulses per quarter note (resolution)
midi_format: 1                      # MIDI file format (0, 1, or 2)
default_channel: 1                  # Default MIDI channel (1-16)
default_velocity: 100               # Default note velocity (0-127)
---
```

### MIDI Format Types

- **Format 0**: Single track (all channels combined)
- **Format 1**: Multi-track synchronous (most common)
- **Format 2**: Multi-track asynchronous (rarely used)

### Device Configuration

```yaml
---
devices:
  - cortex: channel 1
  - h90: channel 2
  - helix: channel 3
---
```

### Full Example

```yaml
---
title: "Live Performance Automation"
author: "Guitarist"
description: "Preset changes and effects automation"
tempo: 128
time_signature: [4, 4]
ppq: 480
midi_format: 1
default_channel: 1
devices:
  - cortex: channel 1
  - h90: channel 2
---
```

---

## Timing Markers

MML supports four timing paradigms that can be mixed freely in the same document.

### 1. Absolute Timecode

Format: `[mm:ss.milliseconds]`

Specifies exact time from the start of the song.

```markdown
[00:00.000]              # Start (0 seconds)
[00:01.500]              # 1.5 seconds
[01:23.250]              # 1 minute, 23.25 seconds
[00:00.050]              # 50 milliseconds
```

**Use cases:**
- Syncing to existing audio/video
- Precise timing requirements
- Non-musical automation

### 2. Musical Time

Format: `[bars.beats.ticks]`

Specifies time in musical units relative to tempo and time signature.

```markdown
[1.1.000]                # Bar 1, beat 1, tick 0 (downbeat)
[2.3.240]                # Bar 2, beat 3, tick 240
[8.4.120]                # Bar 8, beat 4, tick 120
[4.2.0]                  # Bar 4, beat 2
```

**Requirements:**
- Requires `tempo` in frontmatter or a tempo event
- Requires `time_signature` for correct beat counting (defaults to 4/4)

**Use cases:**
- Musical compositions
- Tempo-synchronized automation
- Score-based arrangements

**Common Tick Values** (at 480 PPQ):
- Quarter note = 480 ticks
- Eighth note = 240 ticks
- Sixteenth note = 120 ticks
- Thirty-second note = 60 ticks

### 3. Relative Delta

Format: `[+duration]`

Specifies time relative to the previous event.

```markdown
[+0.500s]                # 500ms after previous
[+250ms]                 # 250 milliseconds after previous
[+1b]                    # 1 beat after previous
[+2.1.0]                 # 2 bars and 1 beat after previous
[+1.5s]                  # 1.5 seconds after previous
```

**Units:**
- `s` = seconds
- `ms` = milliseconds
- `b` = beats
- `t` = ticks
- `bars.beats.ticks` = musical time delta

**Use cases:**
- Sequential patterns
- Delays between commands
- Device-specific timing (e.g., Quad Cortex bank/preset delays)

### 4. Simultaneous Execution

Format: `[@]`

Executes at the same time as the previous event.

```markdown
[00:00.000]
- note_on 1.C4 100 1b    # Middle C
[@]
- note_on 1.E4 100 1b    # Major third (same time)
[@]
- note_on 1.G4 100 1b    # Perfect fifth (same time)
# Result: C major chord
```

**Use cases:**
- Chords (multiple simultaneous notes)
- Multi-channel commands at same time
- Grouped parameter changes

### Timing Rules

1. **Monotonically increasing**: Time must always move forward (except `[@]`)
2. **First event must be absolute**: Document must start with absolute or musical time
3. **Musical time requires tempo**: Cannot use musical time without tempo defined

#### Correct Timing

```markdown
# ✅ Correct - monotonically increasing
[00:00.000]
- tempo 120

[00:01.000]
- note_on 1.60 100 1b

[+500ms]
- note_off 1.60 64
```

#### Incorrect Timing

```markdown
# ❌ Wrong - time goes backwards
[00:02.000]
- note_on 1.60 100 1b

[00:01.000]              # Error: time before previous event
- note_on 1.62 100 1b
```

---

## MIDI Commands

MML supports all standard MIDI commands with human-readable syntax.

### Channel Voice Messages

#### Note Commands

**Note On with Duration** (automatic note-off):

```markdown
- note_on <channel>.<note> <velocity> <duration>
```

```markdown
[00:00.000]
- note_on 1.C4 100 1b          # Middle C, velocity 100, 1 beat
- note_on 1.60 127 500ms       # MIDI note 60, velocity 127, 500ms
- note_on 2.D#5 80 2b          # D# in octave 5, 2 beats
- note_on 1.Bb3 90 250ms       # B-flat, 250ms
```

**Note On/Off (manual control)**:

```markdown
- note_on <channel>.<note> <velocity>
- note_off <channel>.<note> <release_velocity>
```

```markdown
[00:00.000]
- note_on 1.C4 100             # Note on

[00:01.000]
- note_off 1.C4 64             # Note off with release velocity
```

**Note Names**:
- Format: `[Note][Accidental][Octave]`
- Notes: C, D, E, F, G, A, B
- Accidentals: `#` (sharp), `b` (flat)
- Octaves: -1 to 9
- Range: C-1 (0) to G9 (127)

**Examples:**
```markdown
C4    # Middle C (MIDI note 60)
C#4   # C sharp
Db4   # D flat (enharmonic to C#4)
A3    # A below middle C
G9    # Highest note (MIDI 127)
```

**Velocity Range**: 0-127
- 0 = silent (effectively note off)
- 64 = medium
- 127 = maximum

**Duration Units**:
- `b` = beats
- `s` = seconds
- `ms` = milliseconds
- `t` = ticks

#### Program Change

```markdown
- program_change <channel>.<program>
- pc <channel>.<program>         # Shorthand
```

```markdown
[00:00.000]
- pc 1.0                         # Program 0 (often piano)
- pc 1.42                        # Program 42
- program_change 2.127           # Program 127 on channel 2
```

**Range**: 0-127 (128 programs per channel)

**Common MIDI Programs** (General MIDI):
- 0-7: Piano
- 8-15: Chromatic Percussion
- 24-31: Guitar
- 32-39: Bass
- 40-47: Strings
- 48-55: Ensemble

#### Control Change (CC)

```markdown
- control_change <channel>.<controller>.<value>
- cc <channel>.<controller>.<value>   # Shorthand
```

```markdown
[00:00.000]
- cc 1.7.127                     # Volume (CC#7) maximum
- cc 1.10.64                     # Pan (CC#10) center
- cc 1.11.100                    # Expression (CC#11)
- cc 2.1.0                       # Mod wheel (CC#1) minimum
- cc 1.64.127                    # Sustain pedal on
- cc 1.64.0                      # Sustain pedal off
```

**Range**:
- Controller: 0-127
- Value: 0-127

**Common Controllers:**
- CC#1: Modulation Wheel
- CC#7: Channel Volume
- CC#10: Pan (0=left, 64=center, 127=right)
- CC#11: Expression
- CC#64: Sustain Pedal (0-63=off, 64-127=on)
- CC#74: Filter Cutoff
- CC#91: Reverb Depth
- CC#93: Chorus Depth

#### Pitch Bend

```markdown
- pitch_bend <channel>.<value>
- pb <channel>.<value>           # Shorthand
```

```markdown
[00:00.000]
- pb 1.0                         # No bend (center)
- pb 1.8192                      # Center (alternative)
- pb 1.+2000                     # Bend up
- pb 1.-4096                     # Bend down
- pb 1.16383                     # Maximum bend up
- pb 1.-8192                     # Maximum bend down
```

**Range**:
- -8192 to +8191 (signed)
- OR 0 to 16383 (unsigned, 8192 = center)

**Note**: Pitch bend range (semitones) is controlled by RPN#0 (Pitch Bend Sensitivity).

#### Aftertouch / Pressure

**Channel Pressure** (monophonic aftertouch):

```markdown
- channel_pressure <channel>.<value>
- cp <channel>.<value>           # Shorthand
```

```markdown
[00:00.000]
- cp 1.64                        # Medium pressure
- cp 1.127                       # Maximum pressure
```

**Polyphonic Pressure** (per-note aftertouch):

```markdown
- poly_pressure <channel>.<note>.<value>
- pp <channel>.<note>.<value>    # Shorthand
```

```markdown
[00:00.000]
- pp 1.C4.80                     # Pressure on middle C
- pp 1.60.100                    # Pressure on note 60
```

**Range**: 0-127

#### Channel Reset Commands

```markdown
- all_notes_off <channel>        # CC#123 - Stop all notes
- all_sound_off <channel>        # CC#120 - Immediate silence
- reset_controllers <channel>    # CC#121 - Reset all controllers
```

```markdown
[00:10.000]
- all_notes_off 1                # Emergency stop
```

### System Common Messages

#### System Exclusive (SysEx)

Send manufacturer-specific commands.

```markdown
- sysex <hex_bytes>
- sysex_file "path/to/file.syx"
```

**Inline hex bytes:**
```markdown
[00:00.000]
- sysex F0 00 01 06 02 F7       # Single line
```

**Multi-line:**
```markdown
[00:00.000]
- sysex F0 00 01 06
        02 03 04 05
        06 07 08 09
        F7
```

**From file:**
```markdown
[00:00.000]
- sysex_file "patches/bank_dump.syx"
```

**Note**: SysEx messages must start with `F0` and end with `F7`.

#### Song Position / Select

```markdown
- song_position <beats>          # Set position (0-16383 beats)
- song_select <song>             # Select song (0-127)
```

#### MIDI Timecode

```markdown
- mtc_quarter_frame <value>      # MIDI Time Code (0-127)
```

#### Tune Request

```markdown
- tune_request                   # Ask analog synths to tune
```

### System Real-Time Messages

Transport and clock control.

```markdown
# Transport
- clock_start                    # Start sequencer
- clock_stop                     # Stop sequencer
- clock_continue                 # Continue from current position
- clock_tick                     # Single timing clock pulse (24 per quarter)

# System
- active_sensing                 # Keep-alive message
- system_reset                   # Reset all devices
```

### Meta Events (MIDI File Only)

Meta events are stored in MIDI files but not sent to devices during playback.

#### Tempo

```markdown
- tempo <bpm>
```

```markdown
[00:00.000]
- tempo 120                      # 120 BPM
- tempo 132.5                    # Fractional BPM supported
- tempo 90                       # Slow
```

**Range**: Typically 20-300 BPM (no hard limit)

#### Time Signature

```markdown
- time_signature <num>/<denom> [<clocks>] [<32nds>]
```

```markdown
[00:00.000]
- time_signature 4/4             # Common time
- time_signature 3/4             # Waltz
- time_signature 6/8             # Compound meter
- time_signature 7/8             # Odd meter
- time_signature 5/4             # Take Five
```

**Optional parameters:**
- `clocks`: MIDI clocks per metronome click (default: 24)
- `32nds`: Number of 32nd notes per quarter (default: 8)

#### Key Signature

```markdown
- key_signature <key> [<mode>]
```

```markdown
[00:00.000]
- key_signature C                # C major (default)
- key_signature Cm               # C minor
- key_signature F#               # F# major
- key_signature Bbm              # B-flat minor
- key_signature G                # G major
```

#### Text and Metadata Events

```markdown
- text "Any text content"
- copyright "© 2025 Your Name"
- track_name "Lead Guitar"
- instrument_name "Stratocaster"
- lyric "These are the lyrics"
- marker "Chorus"
- cue_point "Lighting change here"
- device_name "Quad Cortex"
```

```markdown
[00:00.000]
- marker "Intro"
- text "Song begins"

[00:16.000]
- marker "Verse 1"
- lyric "First line of verse"

[00:32.000]
- marker "Chorus"
```

**Use cases:**
- **marker**: Section boundaries (Intro, Verse, Chorus)
- **text**: General annotations
- **lyric**: Karaoke-style lyrics
- **cue_point**: Synchronization cues

#### End of Track

```markdown
- end_of_track
```

Usually auto-generated by the compiler, but can be explicit:

```markdown
[00:45.000]
- text "The End"
- end_of_track
```

---

## Directives

Directives start with `@` and provide advanced functionality.

### Imports

Import device libraries and shared definitions.

```markdown
@import "path/to/file.mmd"
```

```markdown
@import "devices/quad_cortex.mmd"
@import "devices/eventide_h90.mmd"
@import "shared/common_macros.mmd"
```

**Features:**
- Loads alias definitions from external files
- Circular import detection
- Relative paths from current file

**See Also**: [Device Libraries Guide](device-libraries.md)

### Variables

Define constants and expressions.

```markdown
@define VARIABLE_NAME value
```

```markdown
@define MAIN_CHANNEL 1
@define INTRO_TEMPO 90
@define VERSE_PRESET 10
@define CHORUS_PRESET 15
```

**Usage:**
```markdown
[00:00.000]
- tempo ${INTRO_TEMPO}
- pc ${MAIN_CHANNEL}.${VERSE_PRESET}
```

**Expressions:**
```markdown
@define NEXT_PRESET ${VERSE_PRESET + 1}
@define HALF_TEMPO ${INTRO_TEMPO / 2}
@define SCALED_VALUE ${BASE_VALUE * 1.5}
```

**Operators**: `+`, `-`, `*`, `/`, `%`, `(`, `)`

### Aliases

Create reusable command shortcuts.

**Basic syntax:**
```markdown
@alias name parameter_list "description"
```

**Single-command alias:**
```markdown
@alias cortex_preset pc.{channel}.{preset} "Load preset"
@alias h90_mix cc.{channel}.84.{value} "Set A/B mix"
```

**Multi-command alias (macro):**
```markdown
@alias cortex_load {channel}.{setlist}.{group}.{preset} "Complete preset load"
  - cc {channel}.32.{setlist}
  - cc {channel}.0.{group}
  - pc {channel}.{preset}
@end
```

**Parameter types:**
```markdown
{name}                           # Basic parameter (0-127)
{name:0-127}                     # Explicit range
{name=default}                   # Optional with default
{channel:1-16}                   # MIDI channel
{note}                           # Note name or number
{percent:0-100}                  # Percentage (scaled to 0-127)
{velocity:0-127}                 # Note velocity
{bool:0-1}                       # Boolean
{mode=option1:0,option2:1}       # Enum values
```

**Usage:**
```markdown
[00:00.000]
- cortex_preset 1 5              # Expands to: pc 1.5
- cortex_load 1 2 0 10           # Expands to 3 CC/PC commands
```

**See Also**: [Alias System Guide](alias-system.md)

### Loops

Repeat commands without manual duplication.

```markdown
@loop <count> times every <interval>
  - commands to repeat
@end
```

```markdown
# Click track (16 beats)
@loop 16 times every 1b
  - note_on 1.42 100 0.1s
@end
```

**Complex example:**
```markdown
# 8-bar bass line
@loop 32 times every 1b
  - note_on 1.36 85 0.9b
@end
```

**Interval units**: `b` (beats), `s` (seconds), `ms` (milliseconds), `t` (ticks)

### Sweeps

Smooth parameter automation over time.

```markdown
@sweep from [<start_time>] to [<end_time>] every <interval>
  - cc <channel>.<controller>.ramp(<start_val>, <end_val>, <type>)
@end
```

**Ramp types:**
- `linear`: Constant rate (default)
- `exponential`: Accelerates
- `logarithmic`: Decelerates

**Volume fade in:**
```markdown
@sweep from [00:00.000] to [00:04.000] every 100ms
  - cc 1.7.ramp(0, 127, linear)
@end
```

**Filter sweep:**
```markdown
@sweep from [00:04.000] to [00:08.000] every 50ms
  - cc 1.74.ramp(0, 127, exponential)
@end
```

**Pan automation:**
```markdown
@sweep from [00:09.000] to [00:13.000] every 75ms
  - cc 1.10.ramp(0, 127, linear)
@end
```

**Multiple concurrent sweeps:**
```markdown
[00:18.000]
- note_on 1.65 100 4s

# Pan left to right
@sweep from [00:18.000] to [00:22.000] every 75ms
  - cc 1.10.ramp(0, 127, linear)
@end

# Expression swell
@sweep from [00:18.000] to [00:22.000] every 80ms
  - cc 1.11.ramp(0, 127, exponential)
@end
```

### Conditionals

Conditional command execution.

```markdown
@if <condition>
  - commands
@elif <condition>
  - commands
@else
  - commands
@end
```

```markdown
@if ${DEVICE_TYPE} == "cortex"
  - cortex_load_preset 1 10
@elif ${DEVICE_TYPE} == "h90"
  - h90_preset 2 5
@else
  - pc 1.10
@end
```

**Note**: Currently conditionals work in aliases, but document-level conditionals are planned.

### Tracks

Multi-track support (MIDI Format 1).

```markdown
@track <name> channel=<channel>
```

```markdown
## Track 1: Control
@track control channel=1
[00:00.000]
- tempo 120
- marker "Start"

## Track 2: Melody
@track melody channel=2
[00:00.000]
- note_on 2.C4 100 1b
```

**Note**: Track blocks are parsed but full multi-track MIDI file generation is in development.

---

## Comments

### Single-Line Comments

```markdown
# This is a comment
// This is also a comment

[00:00.000]
- tempo 120              # Inline comment
- note_on 1.C4 100 1b    // Another inline comment
```

### Multi-Line Comments

```markdown
/*
  This is a multi-line comment.
  It can span multiple lines.
  Useful for documenting sections.
*/

[00:00.000]
- tempo 120
```

### Section Headers

Use markdown headers as visual separators:

```markdown
# ============================================
# Intro Section
# ============================================

[00:00.000]
- tempo 120

# ============================================
# Verse 1
# ============================================

[00:16.000]
- marker "Verse 1"
```

---

## Advanced Features

### Simultaneous Commands

Execute multiple commands at the same time using `[@]`:

```markdown
# C major chord
[00:00.000]
- note_on 1.C4 100 2b
[@]
- note_on 1.E4 100 2b
[@]
- note_on 1.G4 100 2b

# Multi-channel setup
[00:00.000]
- cc 1.7.100             # Channel 1 volume
[@]
- cc 2.7.90              # Channel 2 volume
[@]
- cc 3.7.80              # Channel 3 volume
```

### Multi-Channel Patterns

```markdown
@define SYNTH_CHANNEL 1
@define BASS_CHANNEL 2
@define DRUMS_CHANNEL 10

# Setup all channels
[00:00.000]
- cc ${SYNTH_CHANNEL}.7.80
[@]
- cc ${BASS_CHANNEL}.7.70
[@]
- cc ${DRUMS_CHANNEL}.7.100

# Play on different channels
[00:01.000]
- note_on ${SYNTH_CHANNEL}.C4 100 1b
[@]
- note_on ${BASS_CHANNEL}.C2 90 1b
[@]
- note_on ${DRUMS_CHANNEL}.C1 127 100ms
```

### Device-Specific Timing

Some devices (e.g., Quad Cortex) require delays between bank and preset changes:

```markdown
@alias cortex_load {channel}.{setlist}.{group}.{preset} "Load preset with delays"
  - cc {channel}.32.{setlist}
  [+100ms]
  - cc {channel}.0.{group}
  [+100ms]
  - pc {channel}.{preset}
@end
```

### Expression Evaluation

```markdown
@define BASE_NOTE 60
@define INTERVAL 7

[00:00.000]
- note_on 1.${BASE_NOTE} 100 1b

[00:01.000]
- note_on 1.${BASE_NOTE + INTERVAL} 100 1b      # Perfect fifth

[00:02.000]
- note_on 1.${BASE_NOTE + INTERVAL * 2} 100 1b  # Two fifths
```

### Random Expressions

Generate random values for creating variations and humanized sequences.

**Basic syntax:**
```markdown
random(min, max)                    # Random value between min and max
random(min, max, seed=number)       # Reproducible with fixed seed
```

**Supported contexts:**
```markdown
# Random velocity for humanized dynamics
[00:00.000]
- note_on 1.60 random(70, 100) 1b

# Random note selection
[00:01.000]
- note_on 1.random(C3, C5) 80 1b

# Random CC value for parameter variation
[00:02.000]
- cc 1.74.random(30, 90)            # Random filter cutoff
```

**Use cases:**
- **Humanization**: Add subtle velocity variation (±5-15%) for natural feel
- **Generative melodies**: Random note selection from specified range
- **Parameter variation**: Evolving CC values (filter, reverb, pan, etc.)
- **Reproducibility**: Use `seed` parameter for consistent testing

**Examples:**
```markdown
# Humanized drum pattern
@loop 8 times every 1b
  - note_on 1.36.random(100, 127) 0.5b    # Kick with varying velocity
@end

# Generative arpeggio
@loop 16 times every 0.5b
  - note_on 1.random(C4, G4).random(70, 100) 0.5b
@end

# Reproducible variation
- note_on 1.60 random(70, 90, seed=42) 1b   # Same value each run
```

**Limitations:**
- Cannot use random in timing markers or durations
- Cannot use random in variable definitions (`@define`)
- For advanced techniques, see [Generative Music Guide](generative-music.md)

---

## Examples

### Complete Song Structure

```yaml
---
title: "Complete Song Example"
author: "Composer"
tempo: 128
time_signature: [4, 4]
ppq: 480
midi_format: 1
---

@define MAIN_CHANNEL 1
@define INTRO_PRESET 1
@define VERSE_PRESET 5
@define CHORUS_PRESET 10

# ============================================
# Intro (8 bars)
# ============================================

[1.1.0]
- tempo 128
- marker "Intro"
- pc ${MAIN_CHANNEL}.${INTRO_PRESET}

# Simple arpeggio
@loop 32 times every 0.5b
  - note_on 1.C4 90 0.4b
  - note_on 1.E4 90 0.4b
  - note_on 1.G4 90 0.4b
  - note_on 1.E4 90 0.4b
@end

# ============================================
# Verse 1 (16 bars)
# ============================================

[9.1.0]
- marker "Verse 1"
- pc ${MAIN_CHANNEL}.${VERSE_PRESET}

# Melody line
[9.1.0]
- note_on 1.C5 100 1b
[10.1.0]
- note_on 1.D5 100 1b
[11.1.0]
- note_on 1.E5 100 2b

# ============================================
# Chorus (8 bars)
# ============================================

[25.1.0]
- marker "Chorus"
- pc ${MAIN_CHANNEL}.${CHORUS_PRESET}

# Volume swell
@sweep from [25.1.0] to [33.1.0] every 8t
  - cc 1.7.ramp(60, 127, linear)
@end

# Chords
[25.1.0]
- note_on 1.C4 110 4b
[@]
- note_on 1.E4 110 4b
[@]
- note_on 1.G4 110 4b

[29.1.0]
- note_on 1.F4 110 4b
[@]
- note_on 1.A4 110 4b
[@]
- note_on 1.C5 110 4b

# ============================================
# End
# ============================================

[33.1.0]
- marker "End"
- all_notes_off 1
- end_of_track
```

### Live Performance Automation

```yaml
---
title: "Live Performance"
author: "Guitarist"
ppq: 480
---

@import "devices/quad_cortex.mmd"
@import "devices/eventide_h90.mmd"

@define CORTEX_CH 1
@define H90_CH 2

# ============================================
# Song Start
# ============================================

[00:00.000]
- marker "Intro - Clean"
- cortex_load ${CORTEX_CH} 1 0 0    # Setlist 1, Group 0, Preset 0
- h90_preset ${H90_CH} 10           # Reverb preset

# ============================================
# Verse - Add Drive
# ============================================

[00:30.000]
- marker "Verse - Drive"
- cortex_load ${CORTEX_CH} 1 0 5    # Switch to drive preset

# Gradually increase gain
@sweep from [00:30.000] to [00:45.000] every 200ms
  - cc ${CORTEX_CH}.21.ramp(0, 100, linear)
@end

# ============================================
# Chorus - Full Drive
# ============================================

[01:00.000]
- marker "Chorus - Full"
- cortex_load ${CORTEX_CH} 1 1 10   # Heavy preset
- h90_preset ${H90_CH} 25           # Big reverb + delay

# ============================================
# Solo - Wah Effect
# ============================================

[01:30.000]
- marker "Solo"
- cortex_scene ${CORTEX_CH} 2       # Solo scene

# Auto-wah sweep
@loop 8 times every 1b
  @sweep from [+0b] to [+0.5b] every 50ms
    - cc ${CORTEX_CH}.1.ramp(0, 127, exponential)
  @end
  @sweep from [+0.5b] to [+1b] every 50ms
    - cc ${CORTEX_CH}.1.ramp(127, 0, logarithmic)
  @end
@end

# ============================================
# End
# ============================================

[02:30.000]
- marker "Outro"
- cortex_load ${CORTEX_CH} 1 0 0    # Back to clean

# Fade out
@sweep from [02:30.000] to [02:45.000] every 100ms
  - cc ${CORTEX_CH}.7.ramp(127, 0, linear)
@end

[02:45.000]
- all_sound_off ${CORTEX_CH}
- all_sound_off ${H90_CH}
```

---

## See Also

- [Quickstart Guide](../getting-started/quickstart.md) - Get started quickly
- [Alias System Guide](alias-system.md) - Deep dive into aliases
- [Device Libraries Guide](device-libraries.md) - Using device libraries
- [Timing System Guide](timing-system.md) - Understanding timing paradigms (coming soon)
- [CLI Reference](../cli-reference/overview.md) - Command-line tools
- [Examples Directory](https://github.com/cjgdev/midi-markdown/tree/main/examples) - 51 runnable examples across 7 categories

---

**Next Steps:**
1. Try the [quickstart guide](../getting-started/quickstart.md) to compile your first file
2. Explore [example files](https://github.com/cjgdev/midi-markdown/tree/main/examples) for real-world patterns
3. Learn about [device libraries](device-libraries.md) for your gear
4. Read the [alias system guide](alias-system.md) for advanced automation
