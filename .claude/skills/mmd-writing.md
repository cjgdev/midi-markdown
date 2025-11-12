# MMD Writing Skill

## Purpose
This skill helps users write MIDI Markdown (MMD) files with correct syntax, timing, MIDI commands, and advanced features.

## When to Use This Skill
- User wants to create or edit MMD files
- User needs help with MMD syntax
- User is implementing MIDI automation or sequences
- User needs guidance on timing, aliases, or advanced features
- User is troubleshooting MMD syntax or validation errors

## File Structure

### Basic MMD File Template
```mmd
---
title: "Song or Automation Name"
author: "Your Name"
midi_format: 1
ppq: 480
default_channel: 1
default_velocity: 100
---

@import "devices/quad_cortex.mmd"

@define MAIN_TEMPO 120

[00:00.000]
- tempo ${MAIN_TEMPO}
- marker "Start"

[00:01.000]
- note_on 1.C4 100 1b
```

### Frontmatter (YAML Header)
Required at start of file:
```yaml
---
title: "Song Title"              # Optional but recommended
author: "Artist Name"            # Optional
midi_format: 1                   # 0=single track, 1=multi-track sync
ppq: 480                         # Pulses per quarter note (resolution)
default_channel: 1               # Default MIDI channel (1-16)
default_velocity: 100            # Default note velocity (0-127)
tempo: 120                       # Default tempo in BPM
time_signature: [4, 4]           # [numerator, denominator]
---
```

## Timing Systems

### 1. Absolute Time (mm:ss.milliseconds)
```mmd
[00:00.000]    # Start at 0 seconds
[00:01.500]    # 1.5 seconds
[01:23.250]    # 1 minute, 23.25 seconds
```

### 2. Musical Time (bars.beats.ticks)
```mmd
[1.1.0]        # Bar 1, beat 1, tick 0
[1.2.0]        # Bar 1, beat 2
[2.1.240]      # Bar 2, beat 1, tick 240
[8.4.120]      # Bar 8, beat 4, tick 120
```

### 3. Relative Timing (delta from previous)
```mmd
[00:00.000]
- note_on 1.C4 100 1b

[+500ms]       # 500ms after previous
- note_on 1.D4 100 1b

[+1b]          # 1 beat after previous
- note_on 1.E4 100 1b

[+2.0.0]       # 2 bars after previous
- note_on 1.F4 100 1b
```

### 4. Simultaneous Execution
```mmd
[00:00.000]
- note_on 1.C4 100 1b    # C major chord

[@]                       # Same time as previous
- note_on 1.E4 100 1b

[@]
- note_on 1.G4 100 1b
```

### Timing Units
- `s` - seconds
- `ms` - milliseconds
- `b` - beats
- `t` - ticks

## MIDI Commands

### Note Commands
```mmd
# Note On with automatic note off
- note_on 1.C4 100 1b           # Channel 1, middle C, velocity 100, 1 beat
- note_on 1.60 127 500ms        # Using MIDI note number
- note_on 2.D#5 80 2b           # D# in octave 5

# Manual note control
- note_on 1.C4 100              # Note on without auto-off
- note_off 1.C4 64              # Note off with release velocity
```

### Program Change
```mmd
- program_change 1.42           # Load program 42 on channel 1
- pc 1.5                        # Shorthand (pc = program_change)
```

### Control Change (CC)
```mmd
- control_change 1.7.127        # Volume max on channel 1
- cc 1.7.127                    # Shorthand (cc = control_change)
- cc 1.10.64                    # Pan center
- cc 1.11.100                   # Expression
- cc 2.1.0                      # Mod wheel minimum on channel 2
```

Common CC numbers:
- CC#1 - Mod Wheel
- CC#7 - Volume
- CC#10 - Pan
- CC#11 - Expression
- CC#64 - Sustain Pedal
- CC#74 - Filter Cutoff (brightness)

### Pitch Bend
```mmd
- pitch_bend 1.0                # Center (no bend)
- pb 1.8192                     # Center (alternative)
- pb 1.+2000                    # Bend up
- pb 1.-4096                    # Bend down
- pb 1.16383                    # Maximum bend up

# With modulation
- pb 1.wave(sine, 8192, freq=5.5, depth=5)              # Vibrato
- pb 1.curve(-4096, 4096, ease-in-out)                  # Pitch sweep
- pb 1.envelope(ar, attack=0.5, release=1.0)            # Pitch envelope
```

### Aftertouch/Pressure
```mmd
# Channel Pressure (monophonic aftertouch)
- channel_pressure 1.64
- cp 1.64                       # Shorthand

# Polyphonic Aftertouch (per-note)
- poly_pressure 1.C4.80
- pp 1.60.100                   # Shorthand

# With modulation
- cp 1.curve(0, 127, ease-in-out)                       # Pressure swell
- pp 1.60.wave(sine, 64, freq=3.0, depth=40)           # Per-note vibrato
```

### Meta Events
```mmd
- tempo 120                     # Set tempo to 120 BPM
- time_signature 4/4            # Set time signature
- time_signature 6/8
- marker "Chorus"               # Add marker
- text "Performance note"       # Add text event
- track_name "Lead Guitar"      # Name the track
```

## Advanced Features

### Variables (@define)
```mmd
@define MAIN_TEMPO 120
@define VERSE_PRESET 10
@define CHORUS_PRESET 15

[00:00.000]
- tempo ${MAIN_TEMPO}
- pc 1.${VERSE_PRESET}

# With expressions
@define NEXT_PRESET ${VERSE_PRESET + 1}
@define HALF_TEMPO ${MAIN_TEMPO / 2}
```

### Loops (@loop)
```mmd
# Basic loop
@loop 4 times at [00:00.000] every 1b
  - note_on 1.C4 100 0.5b
@end

# Drum pattern loop
@loop 16 times at [1.1.0] every 1b
  - note_on 10.C1 100 0.1b      # Kick
  - note_on 10.D1 80 0.1b       # Snare
@end

# Omit 'at' to start at previous timing marker
[00:05.000]
@loop 4 times every 1b
  - note_on 1.C4 100 1b
@end
```

### Sweeps (@sweep)
```mmd
# Volume fade in
@sweep from [00:00.000] to [00:04.000] every 100ms
  - cc 1.7 ramp(0, 127)
@end

# With curve types
@sweep from [1.1.0] to [5.1.0] every 8t
  - cc 1.74 ramp(0, 127, exponential)
@end

# Ramp types: linear, exponential, logarithmic, ease-in, ease-out, ease-in-out
```

### Random Values (random())
```mmd
# Random velocity for humanization
- note_on 1.C4 random(70,100) 0.5b

# Random note selection
- note_on 1.random(C3,C5) 80 0.5b

# Random CC values
- cc 1.74.random(50,90)

# In loops for variation
@loop 8 times at [00:16.000] every 0.25b
  - cc 1.74.random(40,100)
@end
```

**Important**: random() works in:
- ✅ Velocity parameter (note commands)
- ✅ Note ranges (with note names like C4, F#2)
- ✅ CC values
- ✅ Beat durations (e.g., random(0.1,0.5)b)
- ❌ NOT in timing expressions
- ❌ NOT in @define values
- ❌ NOT with numeric note IDs

### Modulation (curves, waves, envelopes)

#### Bezier Curves
```mmd
# Smooth parameter transitions
- cc 1.74.curve(0, 127, ease-out)        # Natural filter opening
- cc 1.7.curve(0, 100, ease-in)          # Volume fade-in
- cc 1.11.curve(0, 127, ease-in-out)     # Expression swell
- cc 1.74.curve(0, 127, linear)          # Linear ramp

# Custom Bezier with control points
- cc 1.74.curve(0, 127, bezier(0, 20, 100, 127))
```

Curve types: `ease-in`, `ease-out`, `ease-in-out`, `linear`, `bezier(p0,p1,p2,p3)`

#### Waveforms (LFO)
```mmd
# Vibrato and tremolo
- cc 1.1.wave(sine, 64, freq=5.0, depth=10)      # Vibrato
- cc 1.7.wave(sine, 100, freq=4.0, depth=30)     # Tremolo

# Filter sweep
- cc 1.74.wave(triangle, 64, freq=0.5, depth=60)

# Auto-pan (stereo with phase offset)
[@]
- cc 1.10.wave(sine, 64, freq=2.0, depth=80)             # Left
[@]
- cc 2.10.wave(sine, 64, freq=2.0, phase=0.5, depth=80)  # Right (180°)
```

Wave types: `sine`, `triangle`, `square`, `sawtooth`
Parameters: `freq=Hz`, `phase=0.0-1.0`, `depth=percent`

#### Envelopes
```mmd
# ADSR envelope (Attack-Decay-Sustain-Release)
- cc 1.74.envelope(adsr, attack=0.5, decay=0.3, sustain=0.7, release=1.0)

# AR envelope (Attack-Release)
- cc 1.74.envelope(ar, attack=0.01, release=0.2)

# AD envelope (Attack-Decay)
- cc 1.74.envelope(ad, attack=0.02, decay=0.5)

# With curve type
- cc 1.74.envelope(ar, attack=0.1, release=0.4, curve=exponential)
```

Envelope types: `adsr`, `ar`, `ad`
Curve types: `linear`, `exponential`

### Imports (@import)
```mmd
@import "devices/quad_cortex.mmd"
@import "devices/eventide_h90.mmd"
@import "shared/common_patterns.mmd"

# Then use device-specific aliases
- cortex_load 1.2.0.5       # Load Quad Cortex preset
- h90_preset 2.20           # Load H90 preset
```

Available device libraries:
- `devices/quad_cortex.mmd` - Neural DSP Quad Cortex
- `devices/eventide_h90.mmd` - Eventide H90
- `devices/helix.mmd` - Line 6 Helix
- `devices/hx_stomp.mmd` - HX Stomp
- `devices/hx_effects.mmd` - HX Effects
- `devices/hx_stomp_xl.mmd` - HX Stomp XL

### Aliases (@alias)
```mmd
# Simple alias
@alias my_preset pc.{ch}.{preset} "Load preset"

# Usage
- my_preset 1.42

# Multi-command alias
@alias cortex_load {ch}.{setlist}.{group}.{preset} "Full preset load"
  - cc {ch}.32.{setlist}
  - cc {ch}.0.{group}
  - pc {ch}.{preset}
@end

# With default parameters
@alias volume_set {ch}.{value=100} "Set volume with default"
  - cc {ch}.7.{value}
@end

# With enums
@alias routing {ch}.{mode=series:0,parallel:1} "Set routing mode"
  - cc {ch}.85.{mode}
@end

# Usage
- routing 1.parallel        # Uses value 1
```

### Comments
```mmd
# Single line comment

## Section header (H2 style)

- pc 1.5    # Inline comment

/*
  Multi-line comment block
  Useful for documentation
*/

// C-style comment also supported
```

## Common Patterns

### Drum Pattern
```mmd
@loop 16 times at [1.1.0] every 1b
  - note_on 10.C1 100 0.1b      # Kick (GM drum map)
  - note_on 10.D1 80 0.1b       # Snare
  - note_on 10.F#2 60 0.1b      # Hi-hat
@end
```

### Chord Progression
```mmd
[00:00.000]
- note_on 1.C4 80 4b    # C major
[@]
- note_on 1.E4 80 4b
[@]
- note_on 1.G4 80 4b

[00:04.000]
- note_on 1.F3 80 4b    # F major
[@]
- note_on 1.A3 80 4b
[@]
- note_on 1.C4 80 4b
```

### Volume Automation
```mmd
# Smooth fade in
@sweep from [00:00.000] to [00:04.000] every 100ms
  - cc 1.7 ramp(0, 100, ease-out)
@end

# Fade out
@sweep from [00:30.000] to [00:34.000] every 100ms
  - cc 1.7 ramp(100, 0, ease-in)
@end
```

### Expression Pedal Swell
```mmd
# With device library
@import "devices/quad_cortex.mmd"

@sweep from [00:00.000] to [00:08.000] every 50ms
  - cortex_exp1 1 ramp(0, 127, exponential)
@end
```

### Humanized Hi-Hat Pattern
```mmd
@loop 16 times at [00:00.000] every 0.25b
  - note_on 10.F#2 random(60,90) 0.1b
@end
```

### Generative Ambient Pad
```mmd
@loop 8 times at [00:00.000] every 4b
  - note_on 1.random(C3,E4) random(60,80) 4b
@end
```

## Best Practices

### 1. Always Include Frontmatter
```mmd
---
title: "My Song"
ppq: 480
tempo: 120
time_signature: [4, 4]
---
```

### 2. Use Musical Timing for Music
Musical timing adjusts with tempo changes:
```mmd
[1.1.0]     # Bar 1, beat 1
[2.1.0]     # Bar 2, beat 1
```

### 3. Use Variables for Reusable Values
```mmd
@define MAIN_TEMPO 128
@define INTRO_PRESET 1

- tempo ${MAIN_TEMPO}
- pc 1.${INTRO_PRESET}
```

### 4. Add Comments and Markers
```mmd
# --- INTRO ---
[00:00.000]
- marker "Intro"
- text "Clean tone"

# --- VERSE 1 ---
[00:16.000]
- marker "Verse 1"
```

### 5. Use Loops to Avoid Repetition
```mmd
# Instead of 16 repeated lines, use:
@loop 16 times at [1.1.0] every 1b
  - note_on 10.C1 100 0.1b
@end
```

### 6. Import Device Libraries
```mmd
@import "devices/quad_cortex.mmd"

# Use readable aliases instead of raw MIDI
- cortex_load 1.2.0.5    # Clear intent
# vs
- cc 1.32.2              # What does this do?
- cc 1.0.0
- pc 1.5
```

### 7. Validate Before Compiling
```bash
mmdc validate song.mmd
mmdc compile song.mmd -o output.mid
```

## Common Mistakes to Avoid

### ❌ Wrong: Timing going backwards
```mmd
[00:10.000]
- note_on 1.C4 100 1b

[00:05.000]    # Error: time went backwards!
- note_on 1.D4 100 1b
```

### ✅ Correct: Monotonically increasing timing
```mmd
[00:05.000]
- note_on 1.C4 100 1b

[00:10.000]
- note_on 1.D4 100 1b
```

### ❌ Wrong: Values out of range
```mmd
- cc 1.7.255        # CC values max at 127
- note_on 18.C4     # Channels are 1-16
- pc 1.-5           # Program numbers are 0-127
```

### ✅ Correct: Valid MIDI ranges
```mmd
- cc 1.7.127        # 0-127
- note_on 16.C4     # Channels 1-16
- pc 1.0            # Programs 0-127
```

### ❌ Wrong: Missing timing marker
```mmd
- note_on 1.C4 100 1b    # Error: no timing marker before first event
```

### ✅ Correct: Always start with timing
```mmd
[00:00.000]
- note_on 1.C4 100 1b
```

### ❌ Wrong: Using random() in timing or @define
```mmd
[00:08.random(-10,10)]          # Not supported
@define VEL random(40,60)       # Not supported
```

### ✅ Correct: Use random() in values
```mmd
[00:08.000]
- note_on 1.C4 random(40,60) 1b    # Supported
```

## Quick Syntax Reference

| Element | Syntax | Example |
|---------|--------|---------|
| Timing (absolute) | `[mm:ss.ms]` | `[00:30.500]` |
| Timing (musical) | `[bar.beat.tick]` | `[4.2.240]` |
| Timing (relative) | `[+duration]` | `[+500ms]`, `[+1b]` |
| Timing (simultaneous) | `[@]` | `[@]` |
| Note on | `note_on ch.note vel dur` | `note_on 1.C4 100 1b` |
| Control change | `cc ch.controller.value` | `cc 1.7.127` |
| Program change | `pc ch.program` | `pc 1.42` |
| Pitch bend | `pb ch.value` | `pb 1.8192` |
| Tempo | `tempo bpm` | `tempo 120` |
| Marker | `marker "text"` | `marker "Chorus"` |
| Variable | `@define NAME value` | `@define TEMPO 120` |
| Variable use | `${NAME}` | `${TEMPO}` |
| Loop | `@loop N times...@end` | See above |
| Sweep | `@sweep from...to...@end` | See above |
| Random | `random(min,max)` | `random(60,100)` |
| Curve | `curve(start,end,type)` | `curve(0,127,ease-in)` |
| Wave | `wave(type,base,params)` | `wave(sine,64,freq=5.0)` |
| Envelope | `envelope(type,params)` | `envelope(adsr,attack=0.5...)` |
| Import | `@import "path"` | `@import "devices/..."` |
| Comment | `#`, `//`, `/* */` | `# Comment` |

## Example Files to Reference

Check these examples for patterns:
- `examples/00_basics/01_hello_world.mmd` - Minimal syntax
- `examples/01_timing/03_timing_paradigms.mmd` - All timing modes
- `examples/02_midi_features/02_cc_automation.mmd` - CC automation
- `examples/03_advanced/01_loops_and_patterns.mmd` - Loop examples
- `examples/05_generative/01_random_humanization.mmd` - Random expressions
- `examples/04_device_libraries/02_quad_cortex_live_set.mmd` - Real performance

## See Also
- MMDC CLI Usage Skill - For compiling and testing
- spec.md - Complete language specification
- examples/ - Working example files
- docs/user-guide/ - User documentation
