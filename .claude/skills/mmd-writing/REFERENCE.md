# MMD Syntax Reference

Complete syntax reference for MIDI Markdown. This file provides detailed explanations of all MMD features.

## Table of Contents

1. [File Structure](#file-structure)
2. [Timing Specification](#timing-specification)
3. [MIDI Commands](#midi-commands)
4. [Advanced Features](#advanced-features)
5. [Modulation System](#modulation-system)
6. [Alias System](#alias-system)

## File Structure

### Frontmatter (YAML Header)

All MMD files must start with YAML frontmatter:

```yaml
---
title: "Song Title"              # Optional but recommended
author: "Artist Name"            # Optional
midi_format: 1                   # 0=single track, 1=multi-track sync, 2=async
ppq: 480                         # Pulses per quarter note (96, 192, 480, 960)
default_channel: 1               # Default MIDI channel (1-16)
default_velocity: 100            # Default note velocity (0-127)
tempo: 120                       # Default tempo in BPM
time_signature: [4, 4]           # [numerator, denominator]
---
```

**Field Details**:
- `midi_format`: Type 0 (single track), 1 (multi-track synchronous), 2 (multi-track asynchronous)
- `ppq`: Higher = better resolution, but larger files. 480 recommended.
- `time_signature`: Numerator = beats per bar, Denominator = note value per beat

### Imports

Load device libraries and shared definitions at the top of file (after frontmatter):

```mmd
@import "devices/quad_cortex.mmd"
@import "devices/eventide_h90.mmd"
@import "shared/common_patterns.mmd"
```

Import paths are relative to the current file or absolute from project root.

### Global Definitions

Define constants and variables after imports:

```mmd
@define MAIN_TEMPO 120
@define VERSE_PRESET 1
@define CHORUS_PRESET 5
@define BRIDGE_PRESET 8
```

## Timing Specification

### Absolute Timecode

Format: `[mm:ss.milliseconds]`

```mmd
[00:00.000]    # 0 seconds (song start)
[00:01.500]    # 1.5 seconds
[00:30.000]    # 30 seconds
[01:23.250]    # 1 minute, 23.25 seconds
[10:05.100]    # 10 minutes, 5.1 seconds
```

**Use When**:
- Working with audio/video sync
- Precise absolute timing required
- No tempo changes

### Musical Time

Format: `[bars.beats.ticks]`

```mmd
[1.1.0]        # Bar 1, beat 1, tick 0 (start)
[1.2.0]        # Bar 1, beat 2
[1.3.240]      # Bar 1, beat 3, tick 240 (16th note @ 480 PPQ)
[2.1.0]        # Bar 2, beat 1
[8.4.120]      # Bar 8, beat 4, tick 120
```

**Important**:
- Bars and beats are 1-indexed (start at 1, not 0)
- Ticks are 0-indexed
- Requires `tempo` and `time_signature` in frontmatter
- Automatically adjusts when tempo changes

**Tick Subdivisions** (at 480 PPQ):
- Quarter note = 480 ticks
- Eighth note = 240 ticks
- Sixteenth note = 120 ticks
- Thirty-second note = 60 ticks

**Use When**:
- Creating musical sequences
- Working with bars/beats
- Want timing to adapt to tempo changes

### Relative Timing

Format: `[+duration unit]`

```mmd
[+500ms]       # 500 milliseconds after previous
[+1s]          # 1 second after previous
[+1b]          # 1 beat after previous
[+2b]          # 2 beats after previous
[+0.5b]        # Half beat after previous
[+120t]        # 120 ticks after previous
[+2.1.0]       # 2 bars and 1 beat after previous
```

**Units**:
- `s` - seconds
- `ms` - milliseconds
- `b` - beats
- `t` - ticks
- `bars.beats.ticks` - musical delta

**Use When**:
- Creating patterns relative to previous events
- Building sequences with consistent spacing
- Don't need absolute timing

### Simultaneous Execution

Format: `[@]`

```mmd
[00:00.000]
- note_on 1.C4 100 1b    # C major chord

[@]                       # Same time as previous
- note_on 1.E4 100 1b

[@]                       # Same time as previous
- note_on 1.G4 100 1b
```

**Use When**:
- Creating chords
- Executing multiple commands at exact same time
- Multi-channel coordination

## MIDI Commands

### Note Commands

**Note On** (with automatic note off):
```mmd
- note_on <channel>.<note> <velocity> <duration>
```

Examples:
```mmd
- note_on 1.C4 100 1b           # Middle C, velocity 100, 1 beat
- note_on 1.60 127 500ms        # MIDI note 60, max velocity, 500ms
- note_on 2.D#5 80 2b           # D# in octave 5, velocity 80, 2 beats
- note_on 1.Gb3 90 250ms        # G flat in octave 3
```

**Note Names**: `C`, `C#`/`Db`, `D`, `D#`/`Eb`, `E`, `F`, `F#`/`Gb`, `G`, `G#`/`Ab`, `A`, `A#`/`Bb`, `B`
**Octave Range**: -1 to 9 (MIDI 0-127)
**Middle C**: `C4` = MIDI note 60

**Manual Note Control**:
```mmd
- note_on 1.C4 100              # Note on without auto-off
- note_off 1.C4 64              # Note off with release velocity
```

### Program Change

```mmd
- program_change <channel>.<program>
- pc <channel>.<program>         # Shorthand
```

Examples:
```mmd
- program_change 1.42           # Load program 42 on channel 1
- pc 2.0                        # Load program 0 on channel 2
- pc 1.${MY_PRESET}             # Using variable
```

Range: Programs 0-127

### Control Change (CC)

```mmd
- control_change <channel>.<controller>.<value>
- cc <channel>.<controller>.<value>   # Shorthand
```

Examples:
```mmd
- cc 1.7.127                    # Volume max
- cc 1.10.64                    # Pan center
- cc 1.11.100                   # Expression
- cc 2.1.0                      # Mod wheel minimum
- cc 1.64.127                   # Sustain pedal on
- cc 1.64.0                     # Sustain pedal off
```

**Common CC Numbers**:
- CC#0 - Bank Select MSB
- CC#1 - Modulation Wheel
- CC#2 - Breath Controller
- CC#4 - Foot Controller
- CC#7 - Channel Volume
- CC#10 - Pan
- CC#11 - Expression
- CC#64 - Sustain Pedal (0-63=off, 64-127=on)
- CC#65 - Portamento On/Off
- CC#71 - Resonance
- CC#74 - Brightness/Filter Cutoff
- CC#84 - Portamento Control
- CC#91 - Reverb Send
- CC#93 - Chorus Send
- CC#120 - All Sound Off
- CC#121 - Reset All Controllers
- CC#123 - All Notes Off

### Pitch Bend

```mmd
- pitch_bend <channel>.<value>
- pb <channel>.<value>           # Shorthand
```

Examples:
```mmd
- pb 1.0                        # Center (no bend)
- pb 1.8192                     # Center (alternative notation)
- pb 1.+2000                    # Bend up
- pb 1.-4096                    # Bend down
- pb 1.16383                    # Maximum bend up
- pb 1.-8192                    # Maximum bend down

# With modulation
- pb 1.wave(sine, 8192, freq=5.5, depth=5)              # Vibrato
- pb 1.curve(-4096, 4096, ease-in-out)                  # Pitch sweep
- pb 1.envelope(ar, attack=0.5, release=1.0)            # Pitch envelope
```

**Range**:
- -8192 to +8191 (signed, center at 0)
- 0 to 16383 (unsigned, center at 8192)

### Aftertouch/Pressure

**Channel Pressure** (monophonic):
```mmd
- channel_pressure <channel>.<value>
- cp <channel>.<value>           # Shorthand

- cp 1.64                       # Set pressure to 64
- cp 1.curve(0, 127, ease-in-out)                       # Pressure swell
- cp 1.envelope(adsr, attack=0.2, decay=0.1, sustain=0.8, release=0.3)
```

**Polyphonic Pressure** (per-note):
```mmd
- poly_pressure <channel>.<note>.<value>
- pp <channel>.<note>.<value>    # Shorthand

- pp 1.C4.80                    # Pressure for C4
- pp 1.60.100                   # Pressure for MIDI note 60
- pp 1.60.wave(sine, 64, freq=3.0, depth=40)           # Per-note vibrato
```

### Meta Events

**Tempo**:
```mmd
- tempo <bpm>

- tempo 120                     # 120 BPM
- tempo 132.5                   # Fractional BPM supported
- tempo ${MAIN_TEMPO}           # Using variable
```

**Time Signature**:
```mmd
- time_signature <num>/<denom> [<clocks>] [<32nds>]

- time_signature 4/4
- time_signature 6/8
- time_signature 7/8
- time_signature 3/4
- time_signature 5/4
```

**Key Signature**:
```mmd
- key_signature <key> [<mode>]

- key_signature C               # C major
- key_signature Cm              # C minor
- key_signature F#              # F# major
- key_signature Bbm             # Bb minor
```

**Text Events**:
```mmd
- text "Any text content"
- copyright "© 2025 Your Name"
- track_name "Lead Guitar"
- instrument_name "Quad Cortex"
- lyric "Hello world"
- marker "Chorus"
- cue_point "Preset change here"
- device_name "H90 Effects"
```

## Advanced Features

### Variables

Define constants that can be reused:

```mmd
@define VARIABLE_NAME value

@define MAIN_TEMPO 120
@define VERSE_PRESET 10
@define CHORUS_PRESET 15
@define MAIN_CHANNEL 1
```

Use with `${}` syntax:
```mmd
- tempo ${MAIN_TEMPO}
- pc ${MAIN_CHANNEL}.${VERSE_PRESET}
```

Expressions:
```mmd
@define NEXT_PRESET ${VERSE_PRESET + 1}
@define HALF_TEMPO ${MAIN_TEMPO / 2}
@define SCALED_VALUE ${BASE_VALUE * 1.5}
```

Supported operators: `+`, `-`, `*`, `/`, `%`, `(`, `)`

### Loops

Syntax:
```mmd
@loop <count> times at [<start_time>] every <interval>
  # Commands to repeat
@end
```

Examples:
```mmd
# Basic loop
@loop 4 times at [00:00.000] every 1b
  - note_on 1.C4 100 0.5b
@end

# Drum pattern
@loop 16 times at [1.1.0] every 1b
  - note_on 10.C1 100 0.1b      # Kick
  - note_on 10.D1 80 0.1b       # Snare
@end

# Omit 'at' to start at previous marker
[00:05.000]
@loop 4 times every 1b
  - note_on 1.C4 100 1b
@end
```

**Loop Timing**:
- `at [time]` - Absolute start time (independent of previous markers)
- `at [+delta]` - Relative to previous marker
- Omit `at` - Starts at previous marker

### Sweeps/Ramps

Syntax:
```mmd
@sweep from [<start_time>] to [<end_time>] every <interval>
  - cc <channel>.<controller> ramp(<start_val>, <end_val> [, <curve_type>])
@end
```

Examples:
```mmd
# Volume fade in
@sweep from [00:00.000] to [00:04.000] every 100ms
  - cc 1.7 ramp(0, 127)
@end

# With curve types
@sweep from [1.1.0] to [5.1.0] every 8t
  - cc 1.74 ramp(0, 127, exponential)
@end
```

**Ramp Types**:
- `linear` (default) - Constant rate
- `exponential` - Accelerating change
- `logarithmic` - Decelerating change
- `ease-in` - Slow start, fast finish
- `ease-out` - Fast start, slow finish
- `ease-in-out` - S-curve (slow-fast-slow)

### Random Values

Generate random values for humanization and generative music:

```mmd
random(min, max)
```

**Supported Contexts**:

✅ **Velocity**:
```mmd
- note_on 1.C4 random(70,100) 0.5b
- note_on 10.F#2 random(40,60) 0.1b
```

✅ **Note Ranges** (with note names):
```mmd
- note_on 1.random(C3,C5) 80 0.5b
- note_on 1.random(D4,A4) random(70,90) 0.25b
```

✅ **CC Values**:
```mmd
- cc 1.74.random(50,90)
- cc 1.10.random(20,107)
```

✅ **Beat Durations**:
```mmd
- note_on 1.C4 80 random(0.1,0.5)b
```

❌ **NOT Supported**:
- Timing expressions: `[00:08.random(-10,10)]`
- @define values: `@define VEL random(40,60)`
- Numeric note IDs: `note_on 10.42.random(80,100)`

## Modulation System

### Bezier Curves

Smooth parameter transitions using cubic Bezier interpolation.

Syntax:
```mmd
curve(start_value, end_value, curve_type)
```

**Curve Types**:
- `ease-in` - Slow start, fast finish (builds, crescendos)
- `ease-out` - Fast start, slow finish (arrivals, decrescendos)
- `ease-in-out` - S-curve (smooth musical automation)
- `linear` - Constant rate
- `bezier(p0, p1, p2, p3)` - Custom curve with control points

Examples:
```mmd
- cc 1.74.curve(0, 127, ease-out)        # Natural filter opening
- cc 1.7.curve(0, 100, ease-in)          # Volume fade-in
- cc 1.11.curve(0, 127, ease-in-out)     # Expression swell
- cc 1.74.curve(0, 127, linear)          # Linear ramp
- cc 1.74.curve(0, 127, bezier(0, 20, 100, 127))  # Custom
```

### Waveforms (LFO)

Periodic modulation using Low Frequency Oscillators.

Syntax:
```mmd
wave(wave_type, base_value [, freq=Hz] [, phase=offset] [, depth=percent])
```

**Wave Types**:
- `sine` - Smooth oscillation (vibrato, tremolo)
- `triangle` - Linear rise/fall (gentle modulation)
- `square` - Abrupt switching (rhythmic effects)
- `sawtooth` - Ramp pattern (stepped automation)

**Parameters**:
- `base_value` - Center value for oscillation (0-127)
- `freq` - Frequency in Hz (default: 1.0)
- `phase` - Phase offset 0.0-1.0 (default: 0.0, where 0.25 = 90°)
- `depth` - Modulation depth as percentage (default: 50%)

Examples:
```mmd
# Vibrato (5-6 Hz for pitch)
- cc 1.1.wave(sine, 64, freq=5.0, depth=10)

# Tremolo (3-5 Hz for volume)
- cc 1.7.wave(sine, 100, freq=4.0, depth=30)

# Filter sweep (slow)
- cc 1.74.wave(triangle, 64, freq=0.5, depth=60)

# Auto-pan (stereo with phase offset)
[@]
- cc 1.10.wave(sine, 64, freq=2.0, depth=80)            # Left
[@]
- cc 2.10.wave(sine, 64, freq=2.0, phase=0.5, depth=80)  # Right (180°)
```

### Envelopes

Dynamic parameter shaping with attack, decay, sustain, and release phases.

**ADSR Envelope**:
```mmd
envelope(adsr, attack=time, decay=time, sustain=level, release=time [, curve=type])
```

**AR Envelope**:
```mmd
envelope(ar, attack=time, release=time [, curve=type])
```

**AD Envelope**:
```mmd
envelope(ad, attack=time, decay=time [, curve=type])
```

**Parameters**:
- `attack` - Time to reach peak (seconds)
- `decay` - Time from peak to sustain (seconds)
- `sustain` - Sustain level 0.0-1.0
- `release` - Time from sustain to zero (seconds)
- `curve` - Optional: `linear` or `exponential`

Examples:
```mmd
# Synth pad filter envelope
[00:00.000]
- note_on 1.60.80 4b
- cc 1.74.envelope(adsr, attack=0.5, decay=0.3, sustain=0.7, release=1.0)

# Percussive filter hit
- cc 1.74.envelope(ar, attack=0.01, release=0.2)

# Plucked string filter
- cc 1.74.envelope(ad, attack=0.02, decay=0.5)

# Exponential envelope
- cc 1.74.envelope(ar, attack=0.1, release=0.4, curve=exponential)
```

## Alias System

### Simple Aliases

```mmd
@alias <name> <midi_command> [description]

@alias my_preset pc.{ch}.{preset} "Load preset"
```

### Parameter Types

**Basic**:
```mmd
{name}                           # Any value (0-127)
{name:0-127}                     # Explicit range
{name:40-300}                    # Custom range
```

**Defaults**:
```mmd
{name=default}                   # Optional with default
{channel=1}
{velocity=100}
```

**Enums**:
```mmd
{param=opt1:val1,opt2:val2}

@alias routing cc.{ch}.85.{mode=series:0,parallel:1}
- routing 1.parallel             # Uses value 1
```

**Special Types**:
```mmd
{note}                           # Note name or number
{channel:1-16}                   # MIDI channel
{bool:0-1}                       # Boolean
{percent:0-100}                  # Auto-scaled to 0-127
{velocity:0-127}                 # Note velocity
```

### Multi-Command Aliases

```mmd
@alias <name> {param1}.{param2}... "Description"
  - command1 ...
  - command2 ...
@end

@alias cortex_load {ch}.{setlist}.{group}.{preset} "Full load"
  - cc {ch}.32.{setlist}
  - cc {ch}.0.{group}
  - pc {ch}.{preset}
@end
```

### Computed Values

```mmd
@alias cortex_tempo {ch} {bpm:40-300} "Set tempo"
  {midi_val = int((${bpm} - 40) * 127 / 260)}
  - cc {ch}.14.{midi_val}
@end
```

Supports: `+`, `-`, `*`, `/`, `%`, `int()`, `abs()`, `min()`, `max()`, `round()`, `clamp()`, `scale_range()`, `msb()`, `lsb()`

### Conditional Aliases

```mmd
@alias smart_load {ch}.{preset}.{device} "Device-aware load"
  @if {device} == "cortex"
    - pc {ch}.{preset}
  @elif {device} == "h90"
    - cc {ch}.71.{preset}
  @end
@end
```

## Comments

```mmd
# Single line comment

## Section header (H2 style)

- pc 1.5    # Inline comment

/*
  Multi-line comment block
  Can span several lines
*/

// C-style single line comment
```

---

For practical examples, see EXAMPLES.md in this skill directory.
For complete language specification, see spec.md in project root.
