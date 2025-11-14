# MIDI Markdown (MMD) Specification
**Version 1.0.0**

## Table of Contents
1. [Introduction](#introduction)
2. [Design Principles](#design-principles)
3. [File Structure](#file-structure)
4. [Timing Specification](#timing-specification)
5. [MIDI Command Coverage](#midi-command-coverage)
6. [Alias System](#alias-system)
7. [Advanced Features](#advanced-features)
8. [Device Library Examples](#device-library-examples)
9. [Complete Example](#complete-example)
10. [Implementation Guidelines](#implementation-guidelines)
11. [CLI Interface](#cli-interface)
12. [Error Handling](#error-handling)

---

## Introduction

MIDI Markdown (MMD) is a human-readable, text-based format for creating and automating MIDI sequences. It's designed specifically for live performance automation, particularly for devices like the Neural DSP Quad Cortex and Eventide H90, but supports all MIDI commands and devices.

### Key Features
- **Human-readable syntax** inspired by Markdown
- **Device-agnostic core** with extensible device libraries
- **Multiple timing paradigms** (absolute, relative, musical)
- **Powerful alias system** for device-specific commands
- **Advanced features**: loops, variables, expressions, multi-track support

---

## Design Principles

1. **Human-readable first**: Syntax should be intuitive and scannable
2. **Device-agnostic core**: Base MIDI commands work universally, device libraries extend
3. **Timing flexibility**: Support multiple timing paradigms
4. **Validation-friendly**: Syntax makes errors obvious
5. **Composable**: Reusable blocks, imports, and macros

---

## File Structure

### Document Header
Use YAML-style frontmatter to define document properties:

```markdown
---
title: "Song Title or Automation Name"
author: "Your Name"
midi_format: 1          # 0=single track, 1=multi-track sync, 2=multi-track async
ppq: 480                # Pulses per quarter note (resolution)
default_channel: 1      # 1-16
default_velocity: 100   # 0-127
devices:
  - cortex: channel 1
  - h90: channel 2
---
```

### Imports
Import device libraries and shared definitions:

```markdown
@import "devices/quad_cortex.mmd"
@import "devices/eventide_h90.mmd"
@import "shared/common_macros.mmd"
```

### Global Definitions
Define constants and variables:

```markdown
@define MAIN_TEMPO 120
@define VERSE_PRESET 1
@define CHORUS_PRESET 5
```

---

## Timing Specification

MML supports multiple timing formats that can be mixed in the same document:

### Absolute Timecode
```markdown
[00:00.000]              # mm:ss.milliseconds
[00:01.500]              # 1.5 seconds
[01:23.250]              # 1 minute, 23.25 seconds
```

### Musical Time (Bars.Beats.Ticks)
```markdown
[1.1.000]                # Bar 1, beat 1, tick 0
[2.3.240]                # Bar 2, beat 3, tick 240
[8.4.120]                # Bar 8, beat 4, tick 120
```

### Relative Delta
```markdown
[+0.500s]                # 500ms after previous event
[+1b]                    # 1 beat after previous
[+2.1.0]                 # 2 bars and 1 beat after previous
[+250ms]                 # 250 milliseconds after previous
```

### Simultaneous Execution
```markdown
[@]                      # Execute at same time as previous event
```

### Timing Units
- `s` = seconds
- `ms` = milliseconds
- `b` = beats
- `t` = ticks
- Bars/beats use musical time notation

---

## MIDI Command Coverage

### Channel Voice Messages

#### Note Commands
```markdown
# Note On (with automatic note off)
- note_on <channel>.<note> <velocity> <duration>
- note_on 1.C4 100 1b        # Middle C, velocity 100, 1 beat duration
- note_on 1.60 127 500ms     # MIDI note 60, velocity 127, 500ms
- note_on 2.D#5 80 2b        # D# in octave 5

# Note On (manual control)
- note_on 1.C4 100           # Note on without auto-off
- note_off 1.C4 64           # Note off with release velocity

# Note ranges: C-1 to G9 (MIDI 0-127)
```

#### Program Change
```markdown
- program_change <channel>.<program>
- pc <channel>.<program>     # Shorthand alias
- pc 1.42                    # Load program 42 on channel 1
- program_change 2.0         # Load program 0 on channel 2
```

#### Control Change (CC)
```markdown
- control_change <channel>.<controller>.<value>
- cc <channel>.<controller>.<value>   # Shorthand

# Common examples
- cc 1.7.127                 # Volume (CC#7) max on channel 1
- cc 1.10.64                 # Pan (CC#10) center
- cc 1.11.100                # Expression (CC#11)
- cc 2.1.0                   # Mod wheel (CC#1) minimum
```

#### Pitch Bend
```markdown
- pitch_bend <channel>.<value>
- pb <channel>.<value>       # Shorthand

- pb 1.0                     # Center (no bend)
- pb 1.8192                  # Center (alternative notation)
- pb 1.+2000                 # Bend up
- pb 1.-4096                 # Bend down
- pb 1.16383                 # Maximum bend up

# Range: -8192 to +8191, or 0 to 16383

# Modulation support - smooth vibrato and pitch effects
- pb 1.wave(sine, 8192, freq=5.5, depth=5)              # Vibrato
- pb 1.curve(-4096, 4096, ease-in-out)                  # Pitch sweep
- pb 1.envelope(ar, attack=0.5, release=1.0)            # Pitch envelope
```

#### Aftertouch/Pressure
```markdown
# Channel Pressure (monophonic aftertouch)
- channel_pressure <channel>.<value>
- cp <channel>.<value>       # Shorthand
- cp 1.64

# Polyphonic Aftertouch (per-note pressure)
- poly_pressure <channel>.<note>.<value>
- pp <channel>.<note>.<value>    # Shorthand
- pp 1.C4.80
- pp 1.60.100

# Modulation support - dynamic pressure swells and envelopes
- cp 1.curve(0, 127, ease-in-out)                       # Pressure swell
- cp 1.envelope(adsr, attack=0.2, decay=0.1, sustain=0.8, release=0.3)  # ADSR pressure
- pp 1.60.wave(sine, 64, freq=3.0, depth=40)           # Per-note vibrato effect
```

#### Channel Reset Commands
```markdown
- all_notes_off <channel>        # CC#123
- all_sound_off <channel>        # CC#120
- reset_controllers <channel>    # CC#121
- local_control <channel>.<on|off>
- mono_mode <channel>.<num_channels>
- poly_mode <channel>
```

### System Common Messages

#### System Exclusive (SysEx)
```markdown
# Inline hex bytes
- sysex <hex_bytes>
- sysex F0 00 01 06 02 F7

# From file
- sysex_file "path/to/patch_dump.syx"

# Multi-line
- sysex F0 00 01 06
        02 03 04 05
        F7
```

#### MIDI Timecode
```markdown
- mtc_quarter_frame <value>      # 0-127
```

#### Song Position/Select
```markdown
- song_position <beats>          # Position in beats
- song_select <song>             # Song number (0-127)
```

#### Tune Request
```markdown
- tune_request                   # Ask all devices to tune
```

### System Real-Time Messages

```markdown
# Transport control
- clock_start                    # Start MIDI clock
- clock_stop                     # Stop MIDI clock
- clock_continue                 # Continue from current position
- clock_tick                     # Send one timing clock pulse

# System messages
- active_sensing                 # Keep-alive message
- system_reset                   # Reset all devices
```

### Meta Events (MIDI File Only)

#### Tempo
```markdown
- tempo <bpm>
- tempo 120                      # 120 BPM
- tempo 132.5                    # Fractional BPM supported
```

#### Time Signature
```markdown
- time_signature <num>/<denom> [<clocks>] [<32nds>]
- time_signature 4/4
- time_signature 6/8
- time_signature 7/8 24 8
- time_signature 3/4
```

#### Key Signature
```markdown
- key_signature <key> [<mode>]
- key_signature C                # C major (default)
- key_signature Cm               # C minor
- key_signature F#               # F# major
- key_signature Bbm              # Bb minor
```

#### Text/Metadata Events
```markdown
- text "Any text content"
- copyright "© 2025 Your Name"
- track_name "Lead Guitar"
- instrument_name "Quad Cortex"
- lyric "Hello world"
- marker "Chorus"
- cue_point "Preset change here"
- device_name "H90 Effects"
```

#### Track End
```markdown
- end_of_track                   # Usually auto-generated
```

---

## Alias System

The alias system allows you to create reusable, device-specific command shortcuts.

### Basic Alias Definition

```markdown
@alias <name> <midi_command> [description]

# Simple examples
@alias cortex_preset pc.{channel}.{preset} "Load preset"
@alias h90_mix cc.{channel}.84.{value} "Set A/B mix"
```

### Parameter Types

#### Basic Parameters
```markdown
{name}                           # Any value (0-127 default range)
{name:0-127}                     # Explicit range
{name:40-300}                    # Custom range (e.g., BPM)
```

#### Default Values
```markdown
{name=default_value}             # Optional parameter with default
{channel=1}                      # Defaults to channel 1
{velocity=100}                   # Defaults to velocity 100
```

#### Named/Enum Values
```markdown
{param=option1:value1,option2:value2,option3:value3}

# Example
@alias h90_routing cc.{ch}.85.{mode=series:0,parallel:1,a_only:2,b_only:3}

# Usage
- h90_routing 2 parallel         # Uses value 1
- h90_routing 2 a_only           # Uses value 2
```

#### Special Types
```markdown
{note}                           # Note name or number (C-1 to G9)
{channel:1-16}                   # MIDI channel
{bool:0-1}                       # Boolean as 0/1
{percent:0-100}                  # Percentage (auto-scaled to 0-127)
{velocity:0-127}                 # Note velocity
```

### Multi-Command Aliases (Macros)

```markdown
@alias <name> {param1}.{param2}... "Description"
  - command1 ...
  - command2 ...
  - command3 ...
@end

# Example: Full preset load sequence
@alias cortex_load {channel}.{setlist}.{group}.{preset} "Load complete preset"
  - cc {channel}.32.{setlist}
  - cc {channel}.0.{group}
  - pc {channel}.{preset}
@end

# Usage
- cortex_load 1 2 0 5            # Expands to 3 MIDI commands
```

### Computed Values

Aliases can include computed values that transform parameters before use:

```markdown
@alias cortex_tempo {channel} {bpm:40-300} "Set Quad Cortex tempo"
  {midi_val = int((${bpm} - 40) * 127 / 260)}
  - cc {channel}.14.{midi_val}
@end

# Usage
- cortex_tempo 1 120            # 120 BPM → MIDI value 39
```

Computed values support arithmetic operators (`+`, `-`, `*`, `/`, `%`), built-in functions (`int()`, `abs()`, `min()`, `max()`, `round()`), and MIDI helper functions (`clamp()`, `scale_range()`, `msb()`, `lsb()`). See [docs/user-guide/computed_values.md](docs/user-guide/computed_values.md) for details.

### Conditional Aliases

```markdown
@alias smart_load {channel}.{preset}.{device_type} "Load based on device"
  @if {device_type} == "cortex"
    - pc {channel}.{preset}
  @elif {device_type} == "h90"
    - cc {channel}.71.{preset}
  @end
@end
```

---

## Advanced Features

### Variables and Expressions

#### Variable Definition
```markdown
@define VARIABLE_NAME value

@define INTRO_TEMPO 90
@define VERSE_PRESET 10
@define CHORUS_PRESET 15
@define MAIN_CHANNEL 1
```

#### Variable Usage
```markdown
- tempo ${INTRO_TEMPO}
- pc ${MAIN_CHANNEL}.${VERSE_PRESET}
```

#### Expressions
```markdown
@define NEXT_PRESET ${VERSE_PRESET + 1}
@define HALF_TEMPO ${INTRO_TEMPO / 2}
@define SCALED_VALUE ${BASE_VALUE * 1.5}

# Supported operators: + - * / % ( )
```

### Multi-Track Support

```markdown
## Track 1: Control
@track control channel=1
[00:00.000]
- tempo 120
- marker "Start"

## Track 2: Automation
@track automation channel=2
[00:00.000]
- cc 2.7.0

## Track 3: Notes
@track melody channel=3
[00:00.000]
- note_on 3.C4 100 1b
```

### Loops and Patterns

#### Simple Loops

**Syntax:**
```markdown
@loop <count> times at [<start_time>] every <interval>
  # Commands to repeat
@end
```

**Loop Timing Semantics:**

The `at [<start_time>]` clause specifies when the loop begins execution:

- **Absolute timing** `[HH:MM.SSS]`: Loop starts at an absolute time from the beginning of the song
  ```markdown
  @loop 4 times at [00:05.000] every 1b  # Starts at 5 seconds into the song
  ```

- **Musical timing** `[bars.beats.ticks]`: Loop starts at a specific bar/beat/tick position
  ```markdown
  @loop 4 times at [1.1.0] every 1b      # Starts at bar 1, beat 1, tick 0
  ```

- **Relative timing** `[+duration]`: Loop starts relative to the previous timing marker
  ```markdown
  [00:05.000]
  @loop 4 times at [+2s] every 1b        # Starts 2 seconds after 00:05.000 (at 00:07.000)
  ```

- **Omitting `at` clause**: Loop starts immediately after the previous event or timing marker
  ```markdown
  [00:05.000]
  @loop 4 times every 1b                 # Starts at 00:05.000
  ```

**Important Notes:**
- Loop timing is **independent** of preceding standalone timing markers
- Using `at [00:00.000]` after `[00:10.000]` means the loop starts at the beginning of the song, NOT at 10 seconds
- For relative timing to preceding markers, use `at [+duration]` syntax or omit the `at` clause entirely

**Examples:**
```markdown
# Example 1: Absolute timing - starts at bar 1
@loop 4 times at [1.1.0] every 1b
  - note_on 10.C1 100 1b      # Kick
  - note_on 10.D1 80 1b       # Snare
@end

# Example 2: Relative timing - starts 4 beats after previous marker
[1.1.0]
@loop 4 times at [+4b] every 1b
  - note_on 10.C1 100 1b
@end

# Example 3: Implicit timing - starts at previous marker
[5.1.0]
@loop 4 times every 1b
  - note_on 10.C1 100 1b      # Starts at bar 5, beat 1
@end
```

#### Value Sweeps/Ramps
```markdown
@sweep from [<start_time>] to [<end_time>] every <interval>
  - cc <channel>.<controller> ramp(<start_val>, <end_val>)
@end

# Example: Volume fade in
@sweep from [1.1.0] to [5.1.0] every 8t
  - cc 1.7 ramp(0, 127)
@end

# Ramp types: linear (default), exponential, logarithmic
- cc 1.7 ramp(0, 127, exponential)
- cc 1.7 ramp(127, 0, logarithmic)
```

### Conditional Logic

```markdown
@if <condition>
  # Commands
@elif <condition>
  # Commands
@else
  # Commands
@end

# Example
@if ${DEVICE_TYPE} == "cortex"
  - cortex_load_preset 1 10
@elif ${DEVICE_TYPE} == "h90"
  - h90_preset 2 5
@else
  - pc 1.10
@end
```

### Comments

```markdown
# Single line comment

## Section header comment (H2 style)

- pc 1.5    # Inline comment

/*
  Multi-line comment block
  Can span several lines
  Useful for documentation
*/

// C-style single line comment also supported
```

### Random Values

The `random()` function generates random values within a specified range, perfect for humanization and generative music techniques.

**Syntax:**
```markdown
random(min, max)
```

**Supported Contexts:**

*Velocity Randomization:*
```markdown
# Random velocity for natural feel
- note_on 1.C4 random(70,100) 0.5b

# Drum humanization
- note_on 10.F#2 random(40,60) 0.1b    # Hi-hat with velocity variation
- note_on 10.C1 random(95,110) 0.25b   # Kick with subtle variation
```

*Note Range Randomization:*
```markdown
# Random note selection from range
- note_on 1.random(C3,C5) 80 0.5b

# Generative melody
- note_on 1.random(D4,A4) random(70,90) 0.25b
```

*CC Automation:*
```markdown
# Random filter cutoff
- cc 1.74.random(50,90)

# Random pan position
- cc 1.10.random(20,107)

# Evolving modulation with loops
@loop 8 times at [00:16.000] every 0.25b
  - cc 1.74.random(40,100)
@end
```

**Important Limitations:**

❌ **Not Supported:**
- Timing expressions: `[00:08.random(-10,10)]` - timing must be deterministic
- Tick durations: `random(190,290)t` - use beat durations instead
- @define values: `@define VEL random(40,60)` - use inline random() only
- Numeric note IDs: `note_on 10.42.random(80,100)` - use note names (F#2)

✅ **Supported:**
- Velocity parameter (2nd position in note commands)
- Note ranges with note names (C4, F#2, etc.)
- CC values (3rd parameter in cc commands)
- Beat durations: `random(0.1,0.5)b`

**Practical Applications:**

*Humanization:*
```markdown
# Natural hi-hat groove
@loop 16 times at [00:00.000] every 0.25b
  - note_on 10.F#2 random(60,90) 0.1b
@end
```

*Generative Ambient:*
```markdown
# Evolving pad texture
@loop 8 times at [00:00.000] every 4b
  - note_on 1.random(C3,E4) random(60,80) 4b
@end
```

*CC Parameter Variation:*
```markdown
# Random filter automation
@loop 32 times at [00:00.000] every 0.5b
  - cc 1.74.random(30,90)
@end
```

See [docs/user-guide/generative-music.md](docs/user-guide/generative-music.md) for comprehensive guide and [examples/04_generative/](examples/04_generative/) for working examples.

### Enhanced Modulation

MML provides three powerful modulation types for smooth, natural-sounding parameter automation that goes beyond simple linear ramps. Modulation expressions can be used in **any parameter context** including CC values, pitch bend, and aftertouch/pressure.

#### Bezier Curves

Smooth parameter transitions using cubic Bezier interpolation.

**Syntax:**
```markdown
curve(start_value, end_value, curve_type)
```

**Curve Types:**
- `ease-in`: Slow start, fast finish (gradual builds)
- `ease-out`: Fast start, slow finish (natural arrivals)
- `ease-in-out`: S-curve motion (smooth musical automation)
- `linear`: Constant rate (predictable changes)
- `bezier(p0, p1, p2, p3)`: Custom curve with control points

**Examples:**
```markdown
# Natural filter opening
[00:00.000]
- cc 1.74.curve(0, 127, ease-out)

# Volume fade-in
[00:02.000]
- cc 1.7.curve(0, 100, ease-in)

# Smooth expression swell
[00:04.000]
- cc 1.11.curve(0, 127, ease-in-out)

# Custom Bezier with precise control
[00:06.000]
- cc 1.74.curve(0, 127, bezier(0, 20, 100, 127))
```

#### Waveforms (LFO)

Periodic modulation using Low Frequency Oscillators for vibrato, tremolo, and filter sweeps.

**Syntax:**
```markdown
wave(wave_type, base_value [, freq=Hz] [, phase=offset] [, depth=percent])
```

**Wave Types:**
- `sine`: Smooth oscillation (vibrato, tremolo)
- `triangle`: Linear rise/fall (gentle modulation)
- `square`: Abrupt switching (rhythmic effects)
- `sawtooth`: Ramp pattern (stepped automation)

**Parameters:**
- `base_value`: Center value for oscillation (0-127)
- `freq`: Frequency in Hz (default: 1.0)
- `phase`: Phase offset 0.0-1.0 (default: 0.0, where 0.25 = 90°)
- `depth`: Modulation depth as percentage (default: 50%)

**Examples:**
```markdown
# Classic vibrato (5 Hz for pitch)
[00:00.000]
- cc 1.1.wave(sine, 64, freq=5.0, depth=10)

# Tremolo effect (3-5 Hz for volume)
[00:02.000]
- cc 1.7.wave(sine, 100, freq=4.0, depth=30)

# Filter sweep (slow triangle)
[00:04.000]
- cc 1.74.wave(triangle, 64, freq=0.5, depth=60)

# Auto-pan (stereo with phase offset)
[00:06.000]
[@]
- cc 1.10.wave(sine, 64, freq=2.0, depth=80)            # Left
[@]
- cc 2.10.wave(sine, 64, freq=2.0, phase=0.5, depth=80)  # Right (180° out of phase)
```

#### Envelopes

Dynamic parameter shaping with attack, decay, sustain, and release phases.

**ADSR Envelope** (Attack-Decay-Sustain-Release):
```markdown
envelope(adsr, attack=time, decay=time, sustain=level, release=time [, curve=type])
```

**AR Envelope** (Attack-Release):
```markdown
envelope(ar, attack=time, release=time [, curve=type])
```

**AD Envelope** (Attack-Decay):
```markdown
envelope(ad, attack=time, decay=time [, curve=type])
```

**Parameters:**
- `attack`: Time to reach peak (seconds)
- `decay`: Time from peak to sustain (seconds, ADSR/AD only)
- `sustain`: Sustain level 0.0-1.0 (ADSR only)
- `release`: Time from sustain to zero (seconds, ADSR/AR only)
- `curve`: Optional curve type (`linear` or `exponential`)

**Examples:**
```markdown
# Synth pad filter envelope
[00:00.000]
- note_on 1.60.80 4b
- cc 1.74.envelope(adsr, attack=0.5, decay=0.3, sustain=0.7, release=1.0)

# Percussive filter hit
[00:04.000]
- cc 1.74.envelope(ar, attack=0.01, release=0.2)

# Plucked string filter
[00:06.000]
- cc 1.74.envelope(ad, attack=0.02, decay=0.5)

# Natural exponential envelope
[00:08.000]
- cc 1.74.envelope(ar, attack=0.1, release=0.4, curve=exponential)
```

**Practical Applications:**

*Filter Automation:*
```markdown
# Dynamic filter with envelope
[00:00.000]
- note_on 1.60.80 4b
- cc 1.74.envelope(adsr, attack=0.1, decay=0.2, sustain=0.6, release=0.3)

# Slow filter LFO for evolving pads
[00:04.000]
- cc 1.74.wave(sine, 64, freq=0.2, depth=60)
```

*Vibrato and Pitch Effects:*
```markdown
# Natural vibrato using CC#1 (mod wheel)
[00:00.000]
- cc 1.1.wave(sine, 64, freq=6.0, depth=8)

# Pitch bend vibrato (wider range, more natural)
[00:02.000]
- pb 1.wave(sine, 8192, freq=5.5, depth=5)

# Smooth pitch sweep for transitions
[00:04.000]
- pb 1.curve(-4096, 4096, ease-in-out)

# Pitch dive with envelope
[00:06.000]
- pb 1.envelope(ad, attack=0.01, decay=1.5)
```

*Volume Automation:*
```markdown
# Smooth fade-in
[00:00.000]
- cc 1.7.curve(0, 100, ease-out)

# Volume swell
[00:02.000]
- cc 1.7.envelope(ar, attack=2.0, release=1.5)
```

*Pressure/Aftertouch Effects:*
```markdown
# Channel pressure swell for expressive pads
[00:00.000]
- note_on 1.60.80 4b
- cp 1.curve(0, 127, ease-in-out)

# Polyphonic pressure vibrato (per-note expression)
[00:04.000]
- note_on 1.C4.100 4b
- pp 1.C4.wave(sine, 64, freq=3.0, depth=40)

# Dynamic pressure envelope following note
[00:08.000]
- note_on 1.60.100 4b
- cp 1.envelope(adsr, attack=0.2, decay=0.1, sustain=0.8, release=0.3)
```

### Groups and Sections

```markdown
@section "Intro" from [0.0.0] to [8.1.0]
  # All commands in this section
  - tempo 120
  - marker "Intro Start"
@end

@group "Verse Effects"
  # Logically grouped commands
  - h90_preset 2 10
  - cortex_scene 1 1
@end
```

---

## Device Library Examples

### Quad Cortex Device Library
**File: devices/quad_cortex.mmd**

```markdown
---
device: Neural DSP Quad Cortex
manufacturer: Neural DSP
version: 3.0.0
default_channel: 1
documentation: https://neuraldsp.com/quad-cortex
---

# ============================================
# Setlist / Preset Commands
# ============================================

@alias cortex_preset_group cc.{ch}.0.{group:0-127} "Select preset group (0-127)"
@alias cortex_setlist cc.{ch}.32.{setlist:0-127} "Select setlist (0-127)"
@alias cortex_preset pc.{ch}.{preset:0-127} "Load preset (0-127)"

@alias cortex_load {ch}.{setlist}.{group}.{preset} "Complete preset load sequence"
  - cc {ch}.32.{setlist}
  - cc {ch}.0.{group}
  - pc {ch}.{preset}
@end

# ============================================
# Scene Commands
# ============================================

@alias cortex_scene pc.{ch}.{scene:0-7} "Switch to scene (0=A, 1=B, ..., 7=H)"
@alias cortex_scene_a pc.{ch}.0 "Scene A"
@alias cortex_scene_b pc.{ch}.1 "Scene B"
@alias cortex_scene_c pc.{ch}.2 "Scene C"
@alias cortex_scene_d pc.{ch}.3 "Scene D"

@alias cortex_scene_up cc.{ch}.71.127 "Next scene"
@alias cortex_scene_down cc.{ch}.71.0 "Previous scene"

# ============================================
# Expression Pedals
# ============================================

@alias cortex_exp1 cc.{ch}.11.{value:0-127} "Expression pedal 1"
@alias cortex_exp2 cc.{ch}.12.{value:0-127} "Expression pedal 2"
@alias cortex_exp3 cc.{ch}.13.{value:0-127} "Expression pedal 3"
@alias cortex_exp4 cc.{ch}.14.{value:0-127} "Expression pedal 4"

# ============================================
# Stomp Switches (A-H)
# ============================================

@alias cortex_stomp_a_on cc.{ch}.81.127 "Stomp A on"
@alias cortex_stomp_a_off cc.{ch}.81.0 "Stomp A off"
@alias cortex_stomp_a cc.{ch}.81.{state:0-127} "Stomp A (0=off, 127=on)"

@alias cortex_stomp_b_on cc.{ch}.82.127 "Stomp B on"
@alias cortex_stomp_b_off cc.{ch}.82.0 "Stomp B off"
@alias cortex_stomp_b cc.{ch}.82.{state:0-127} "Stomp B"

@alias cortex_stomp_c_on cc.{ch}.83.127 "Stomp C on"
@alias cortex_stomp_c_off cc.{ch}.83.0 "Stomp C off"

# ... Continue for D-H (CC#84-88)

# ============================================
# Tempo Control
# ============================================

@alias cortex_tap_tempo cc.{ch}.80.127 "Tap tempo"
@alias cortex_tempo cc.{ch}.14.{bpm:40-300} "Set tempo BPM" {
  # Convert BPM (40-300) to MIDI value (0-127)
  value = int((bpm - 40) * 127 / 260)
}

# ============================================
# Tuner
# ============================================

@alias cortex_tuner_on cc.{ch}.68.127 "Tuner on"
@alias cortex_tuner_off cc.{ch}.68.0 "Tuner off"
@alias cortex_tuner_toggle cc.{ch}.68.{state:0-127} "Tuner toggle"

# ============================================
# Transport / Looper
# ============================================

@alias cortex_play_pause cc.{ch}.85.127 "Play/Pause"
@alias cortex_stop cc.{ch}.86.127 "Stop"
@alias cortex_record cc.{ch}.87.127 "Record"
@alias cortex_undo cc.{ch}.88.127 "Undo"
@alias cortex_redo cc.{ch}.89.127 "Redo"
```

### Eventide H90 Device Library
**File: devices/eventide_h90.mmd**

```markdown
---
device: Eventide H90
manufacturer: Eventide
version: 1.0.0
default_channel: 2
documentation: https://www.eventideaudio.com/h90
---

# ============================================
# Program/Preset Selection
# ============================================

@alias h90_preset pc.{ch}.{preset:0-127} "Load preset (0-127)"
@alias h90_preset_up cc.{ch}.71.127 "Next preset"
@alias h90_preset_down cc.{ch}.71.0 "Previous preset"

# ============================================
# Algorithm Selection (Dual Algorithm Engine)
# ============================================

@alias h90_algo_a cc.{ch}.82.{algo:0-52} "Select algorithm for path A"
@alias h90_algo_b cc.{ch}.83.{algo:0-52} "Select algorithm for path B"

# Named algorithm shortcuts
@alias h90_algo_a_blackhole cc.{ch}.82.0 "BlackHole reverb on A"
@alias h90_algo_a_shimmer cc.{ch}.82.1 "Shimmer reverb on A"
@alias h90_algo_a_modfactory cc.{ch}.82.10 "ModFactory on A"

# ============================================
# Mix and Routing
# ============================================

@alias h90_mix cc.{ch}.84.{percent:0-100} "A/B mix (0=A only, 100=B only)"
@alias h90_routing cc.{ch}.85.{mode=series:0,parallel:1,a_only:2,b_only:3} "Routing mode"

# ============================================
# Expression and Control
# ============================================

@alias h90_exp_pedal cc.{ch}.4.{value:0-127} "Expression pedal input"
@alias h90_knob_1 cc.{ch}.75.{value:0-127} "Rotary knob 1"
@alias h90_knob_2 cc.{ch}.76.{value:0-127} "Rotary knob 2"
@alias h90_knob_3 cc.{ch}.77.{value:0-127} "Rotary knob 3"

# ============================================
# Performance Controls
# ============================================

@alias h90_tap_tempo cc.{ch}.80.127 "Tap tempo"
@alias h90_bypass cc.{ch}.102.{state=active:127,bypassed:0} "Bypass toggle"
@alias h90_play cc.{ch}.89.127 "Play/Pause button"
@alias h90_infinity cc.{ch}.90.127 "Infinity (freeze) button"
@alias h90_hotswitch cc.{ch}.91.127 "HotSwitch toggle"

# ============================================
# Effect Parameters (Common)
# ============================================

@alias h90_decay cc.{ch}.92.{value:0-127} "Decay/Feedback"
@alias h90_mod_rate cc.{ch}.93.{value:0-127} "Modulation rate"
@alias h90_mod_depth cc.{ch}.94.{value:0-127} "Modulation depth"
@alias h90_filter cc.{ch}.95.{value:0-127} "Filter cutoff"

# ============================================
# Macros for Common Setups
# ============================================

@alias h90_dual_reverb {ch}.{preset} "Load and set up dual reverb"
  - pc {ch}.{preset}
  - cc {ch}.85.1              # Parallel routing
  - cc {ch}.84.64             # 50/50 mix
@end

@alias h90_serial_fx {ch}.{preset}.{mix_percent} "Serial effects chain"
  - pc {ch}.{preset}
  - cc {ch}.85.0              # Series routing
  - cc {ch}.84.{mix_percent}  # Custom mix
@end
```

---

## Complete Example

**File: live_set_example.mmd**

```markdown
---
title: "Live Performance Set - Song Name"
author: "Artist Name"
date: "2025-10-29"
midi_format: 1
ppq: 480
default_channel: 1
default_velocity: 100
devices:
  - cortex: channel 1
  - h90: channel 2
---

@import "devices/quad_cortex.mmd"
@import "devices/eventide_h90.mmd"

# ============================================
# Global Definitions
# ============================================

@define SONG_TEMPO 128
@define INTRO_TEMPO 100

@define INTRO_PRESET 1
@define VERSE_PRESET 2
@define CHORUS_PRESET 3
@define BRIDGE_PRESET 4
@define OUTRO_PRESET 5

# ============================================
# Track 1: Master Control & Markers
# ============================================

## Track 1: Master
@track master

# --- INTRO ---
[00:00.000] # Song start
- tempo ${INTRO_TEMPO}
- time_signature 4/4
- key_signature Am
- marker "Intro"
- cortex_load 1 1 0 ${INTRO_PRESET}
- h90_preset 2 20
- h90_mix 2 30%

[00:08.000]
- text "Tempo ramp begins"

[00:12.000] # Tempo build-up
- tempo 110

[00:16.000]
- tempo ${SONG_TEMPO}

# --- VERSE 1 ---
[00:16.000]
- marker "Verse 1"
- cortex_scene 1 1           # Scene B for clean tone
- h90_mix 2 20%              # Reduce reverb

[00:32.000]
- marker "Pre-Chorus"
- cortex_stomp_a_on 1        # Engage drive pedal
- h90_mix 2 40%

# --- CHORUS ---
[00:40.000]
- marker "Chorus"
- cortex_preset 1 ${CHORUS_PRESET}
- h90_preset 2 21
- h90_routing 2 parallel
- h90_mix 2 60%

[00:56.000]
- marker "Verse 2"
- cortex_preset 1 ${VERSE_PRESET}
- cortex_stomp_a_off 1
- h90_mix 2 20%

# --- BRIDGE ---
[01:28.000]
- marker "Bridge"
- tempo 110                  # Slow down
- cortex_preset 1 ${BRIDGE_PRESET}
- h90_preset 2 25            # Shimmer reverb

[01:36.000]
- cortex_scene 1 3           # Scene D for lead

# --- FINAL CHORUS ---
[01:44.000]
- marker "Final Chorus"
- tempo ${SONG_TEMPO}
- cortex_preset 1 ${CHORUS_PRESET}
- h90_routing 2 series
- h90_mix 2 70%

# --- OUTRO ---
[02:16.000]
- marker "Outro"
- cortex_preset 1 ${OUTRO_PRESET}
- tempo 100

[02:32.000]
- h90_infinity 2 127         # Freeze reverb

[02:40.000]
- all_notes_off 1
- all_notes_off 2

# ============================================
# Track 2: Expression Automation
# ============================================

## Track 2: Expression
@track expression

# Verse dynamics - subtle expression
[00:16.000]
- cortex_exp1 1 30

[00:24.000]
- cortex_exp1 1 50

# Chorus swell
@sweep from [40.1.0] to [48.1.0] every 32t
  - cortex_exp1 1 ramp(0, 127)
@end

# Reset after chorus
[00:56.000]
- cortex_exp1 1 0

# Bridge swell (slower)
@sweep from [88.1.0] to [100.1.0] every 64t
  - cortex_exp2 1 ramp(0, 127, exponential)
@end

# Final chorus - hold expression high
[01:44.000]
- cortex_exp1 1 110

# Outro fade
@sweep from [136.1.0] to [160.1.0] every 16t
  - cortex_exp1 1 ramp(110, 0, logarithmic)
@end

# ============================================
# Track 3: H90 Automation
# ============================================

## Track 3: H90 Effects
@track h90_automation

# Intro - gradual mix increase
@sweep from [0.1.0] to [16.1.0] every 16t
  - h90_mix 2 ramp(30, 50)
@end

# Chorus - modulation pulse
@loop 4 times at [40.1.0] every 2b
  - h90_knob_1 2 100
  [@]
  - h90_knob_2 2 80
  [+1b]
  - h90_knob_1 2 40
  [@]
  - h90_knob_2 2 30
@end

# Bridge - decay increase for ambient feel
[01:28.000]
- h90_decay 2 100

[01:36.000]
- h90_mod_depth 2 90         # Deep modulation

# Final chorus - max everything
[01:44.000]
- h90_decay 2 127
- h90_mod_depth 2 127
- h90_mix 2 75%

# Outro - freeze and fade
[02:16.000]
- h90_decay 2 127

[02:32.000]
- h90_infinity 2 127

# ============================================
# Track 4: Click/Metronome (Optional)
# ============================================

## Track 4: Click
@track click channel=10

# Generate click track
@loop 160 times at [0.1.0] every 1b
  - note_on 10.C4 100 50ms   # Click on beat 1
@end
```

---

## Implementation Guidelines

### Parser Architecture

```
┌─────────────────┐
│  Input (.mmd)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Lexer/Tokenizer│  → Break into tokens
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Parser (AST)   │  → Build syntax tree
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Import Resolver│  → Load device libraries
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Alias Resolver │  → Expand aliases
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Validator      │  → Check ranges, timing
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  MIDI Generator │  → Convert to MIDI events
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Output (.mid)  │
└─────────────────┘
```

### Validation Rules

1. **Timing Validation**
   - Timing must be monotonically increasing within tracks
   - Musical time requires tempo and time signature to be defined
   - Relative timing requires a previous event

2. **Value Ranges**
   - MIDI values: 0-127 (most commands)
   - Channel numbers: 1-16
   - Note numbers: 0-127 (C-1 to G9)
   - Pitch bend: -8192 to +8191 or 0 to 16383
   - Tempo: 20-999 BPM (practical range)

3. **Alias Validation**
   - All referenced aliases must be defined or imported
   - Parameter counts must match alias definition
   - Parameter values must be within specified ranges
   - Named values must match defined options

4. **Track Validation**
   - Track names must be unique
   - Channel assignments must be valid (1-16)
   - Multi-track files require format 1 or 2

5. **Import Validation**
   - Imported files must exist and be valid MML
   - Circular imports are not allowed
   - Import paths are relative to current file

### Data Structures

#### Event Object
```python
{
  "time": <absolute_ticks>,
  "type": "note_on|note_off|cc|pc|...",
  "channel": <1-16>,
  "data1": <0-127>,
  "data2": <0-127>,
  "metadata": {
    "source_line": <line_number>,
    "source_file": "<filename>",
    "track": "<track_name>"
  }
}
```

#### Alias Object
```python
{
  "name": "<alias_name>",
  "parameters": [
    {
      "name": "<param_name>",
      "type": "int|note|percent|enum",
      "min": <min_value>,
      "max": <max_value>,
      "default": <default_value>,
      "enum_values": {"name": value, ...}
    }
  ],
  "commands": [<command_list>],
  "description": "<description_text>"
}
```

---

## CLI Interface

### Basic Commands

```bash
# Compile MMD to MIDI
mmdc compile <input.mmd> -o <output.mid>
mmdc compile song.mmd -o song.mid

# Compile with options
mmdc compile song.mmd -o song.mid --ppq 960
mmdc compile song.mmd -o song.mid --format 1

# Validate without compiling
mmdc validate song.mmd
mmdc validate song.mmd --verbose

# Check syntax only (no validation)
mmdc check song.mmd
```

### Advanced Options

```bash
# Split tracks into separate MIDI files
mmdc compile song.mmd --split-tracks
# Produces: song_track1.mid, song_track2.mid, etc.

# Dry run (show what would be generated)
mmdc compile song.mmd --dry-run

# Show statistics
mmdc compile song.mmd --stats
# Output: 245 events, 3 tracks, duration 3:25

# Compile range of time
mmdc compile song.mmd --from 00:30.0 --to 01:15.0

# Override definitions
mmdc compile song.mmd -D TEMPO=140 -D PRESET=5
```

### Device Library Management

**Implemented:**
```bash
# List available libraries (✅ Implemented)
mmdc library list

# Validate library (✅ Implemented)
mmdc library validate devices/quad_cortex.mmd

# Show library info (✅ Implemented)
mmdc library info quad_cortex
```

**Planned (Future):**
```bash
# Search for libraries (🚧 Planned)
mmdc library search "eventide"

# Install library from repository (🚧 Planned)
mmdc library install eventide-h90

# Create new library template (🚧 Planned)
mmdc library create my_device.mmd
```

### Interactive Mode

**Implemented:**
```bash
# Start REPL (✅ Implemented)
mmdc repl

# REPL commands:
> load devices/quad_cortex.mmd
> alias cortex_preset
> send cortex_preset 1 5
> monitor on
> quit
```

**Planned (Future):**
```bash
# REPL with device preset (🚧 Planned)
mmdc repl --device cortex --channel 1
```

### Output Formats

**Implemented:**
```bash
# Export to JSON (✅ Implemented via compile)
mmdc compile song.mmd --format json -o events.json

# Export to CSV (✅ Implemented via compile)
mmdc compile song.mmd --format csv -o events.csv

# Table display (✅ Implemented via compile)
mmdc compile song.mmd --format table
```

### Real-Time Playback

**Implemented:**
```bash
# Send MIDI in real-time with TUI (✅ Implemented)
mmdc play song.mmd --port 0

# List MIDI ports (✅ Implemented)
mmdc ports
```

**Planned (Future):**
```bash
# Convert MIDI to MMD (🚧 Planned)
mmdc import song.mid -o song.mmd

# Merge multiple MMD files (🚧 Planned)
mmdc merge song1.mmd song2.mmd -o combined.mmd

# Monitor MIDI input and generate MMD (🚧 Planned)
mmdc learn --device cortex --channel 1 -o learned.mmd
```

---

## Error Handling

### Error Message Format

```
Error: <ErrorType> at line <line>:<column> in <file>
  <line_content>
  <error_indicator>

<detailed_message>

Suggestion: <helpful_suggestion>
```

### Example Errors

#### Invalid MIDI Value
```
Error: ValueError at line 45:12 in song.mmd
  - cc 1.7.255
           ^^^
Value 255 exceeds maximum allowed (127) for CC parameter

Suggestion: Use a value between 0 and 127
```

#### Undefined Alias
```
Error: UndefinedAlias at line 23:3 in song.mmd
  - cortex_load_preset_123 1 5
    ^^^^^^^^^^^^^^^^^^^^^^

Alias 'cortex_load_preset_123' is not defined

Suggestion: Did you mean 'cortex_load_preset'?
Available aliases: cortex_load, cortex_preset, cortex_scene
```

#### Timing Error
```
Error: TimingError at line 67:1 in song.mmd
  [00:30.000]

Time 00:30.000 is before previous event at 00:45.000
Timing must be monotonically increasing

Suggestion: Use relative timing [+15.0s] or fix absolute time
```

#### Parameter Count Mismatch
```
Error: ParameterError at line 34:3 in song.mmd
  - cortex_load 1 2 5
                    ^

Expected 4 parameters for 'cortex_load', got 3
Required: {channel} {setlist} {group} {preset}

Suggestion: Add missing preset parameter
Example: cortex_load 1 2 0 5
```

### Warning Messages

```
Warning: OverlappingNote at line 89:3 in song.mmd
  - note_on 1.C4 100 2b

Note C4 on channel 1 is already playing (started at line 85)
Previous note will be cut off

Suggestion: Add note_off command or adjust timing
```

```
Warning: UnusedAlias in devices/custom.mmd
  @alias my_custom_command pc.{ch}.{preset}

Alias 'my_custom_command' is defined but never used

Suggestion: Remove unused alias or check for typos
```

---

## Future Extensions

### Planned Features

1. **Live Performance Mode**
   - Real-time MIDI sending while parsing
   - Sync with DAW or hardware clock
   - Setlist navigation

2. **MIDI Learn**
   - Capture MIDI and auto-generate markup
   - Device interrogation
   - Automatic alias creation

3. **Visual Editor**
   - GUI for creating/editing markup files
   - Timeline view with events
   - Drag-and-drop timing adjustment

4. **Enhanced Modulation**
   ```markdown
   - cc 1.7 curve(bezier, 0, 100, 127, 30)
   - cc 1.10 wave(sine, 2Hz, 32, 96)
   - pb 1 envelope(attack:0.5s, decay:1s, sustain:80, release:2s)
   ```

5. **Generative Features**
   ```markdown
   @random_pattern 16 steps at [1.1.0]
     - note_on 1 scale(C, minor) random(80, 110) 1b
   @end
   ```

6. **OSC Integration**
   ```markdown
   - osc "/fx/reverb/mix" 0.75
   - osc "/ableton/track/1/volume" -6.0
   ```

7. **Python/Lua Scripting**
   ```markdown
   @python
   for i in range(8):
       emit(f"note_on 1.{60+i} 100 250ms")
       wait("250ms")
   @end
   ```

8. **Standard Library**
   - Community-maintained device libraries
   - Shareable macros and patterns
   - Version management

9. **Conditional Compilation**
   ```markdown
   @ifdef LIVE_MODE
     - cortex_load 1 1 0 1
   @else
     - cortex_load 1 2 0 5
   @endif
   ```

10. **MIDI 2.0 Support**
    - High-resolution controllers (32-bit)
    - Per-note controllers
    - Profile configuration

---

## Appendix

### MIDI Note Names

```
C-1  = 0      C4 (Middle C) = 60    C9  = 120
C#-1 = 1      C#4           = 61    C#9 = 121
D-1  = 2      D4            = 62    D9  = 122
...
G9   = 127 (highest MIDI note)
```

### Standard MIDI CC Numbers

```
0   - Bank Select MSB
1   - Modulation Wheel
2   - Breath Controller
4   - Foot Controller
7   - Channel Volume
10  - Pan
11  - Expression
64  - Sustain Pedal (0-63=off, 64-127=on)
65  - Portamento On/Off
71  - Resonance
74  - Brightness
84  - Portamento Control
91  - Reverb Send
93  - Chorus Send
120 - All Sound Off
121 - Reset All Controllers
123 - All Notes Off
```

### MIDI File Format Types

```
Format 0: Single track (all events in one track)
Format 1: Multi-track synchronous (tracks play simultaneously)
Format 2: Multi-track asynchronous (independent sequences)
```

### PPQ (Pulses Per Quarter Note)

Common values:
- 96 PPQ   - Low resolution, older gear
- 192 PPQ  - Standard resolution
- 480 PPQ  - High resolution (recommended)
- 960 PPQ  - Very high resolution for precise timing

---

**End of Specification v1.0.0**

For updates and examples, visit: [github.com/cjgdev/midi-markdown](https://github.com/cjgdev/midi-markdown)

For questions and support: [GitHub Issues](https://github.com/cjgdev/midi-markdown/issues)
