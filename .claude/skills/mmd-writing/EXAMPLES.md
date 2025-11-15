# MMD Pattern Library

Common patterns and working examples for MIDI Markdown. Copy and adapt these patterns for your own use.

## Table of Contents

1. [Basic Patterns](#basic-patterns)
2. [Drums and Percussion](#drums-and-percussion)
3. [Musical Elements](#musical-elements)
4. [Automation and Effects](#automation-and-effects)
5. [Device Control](#device-control)
6. [Generative Techniques](#generative-techniques)

## Basic Patterns

### Minimal MMD File

```mmd
---
title: "Hello World"
ppq: 480
tempo: 120
time_signature: [4, 4]
---

[00:00.000]
- tempo 120
- note_on 1.C4 100 1b
- note_on 1.E4 100 1b
- note_on 1.G4 100 1b
```

### Simple Click Track

```mmd
---
title: "Click Track"
ppq: 480
tempo: 120
time_signature: [4, 4]
---

@loop 32 times at [1.1.0] every 1b
  - note_on 10.C4 100 50ms
@end
```

### Song Structure with Markers

```mmd
[00:00.000]
- marker "Intro"
- tempo 100

[00:16.000]
- marker "Verse 1"
- tempo 120

[00:48.000]
- marker "Chorus"

[01:20.000]
- marker "Verse 2"

[01:52.000]
- marker "Bridge"
- tempo 110

[02:24.000]
- marker "Final Chorus"
- tempo 120

[03:00.000]
- marker "Outro"
```

## Drums and Percussion

### Basic Drum Pattern (GM Drum Map)

```mmd
# Standard rock beat
@loop 16 times at [1.1.0] every 1b
  - note_on 10.C1 100 0.1b      # Kick (MIDI note 36)
  [@]
  - note_on 10.F#2 60 0.1b      # Hi-hat (42)

  [+0.5b]
  - note_on 10.D1 80 0.1b       # Snare (38)
  [@]
  - note_on 10.F#2 60 0.1b      # Hi-hat
@end
```

### Humanized Hi-Hat Pattern

```mmd
# Natural-sounding hi-hats with velocity variation
@loop 16 times at [00:00.000] every 0.25b
  - note_on 10.F#2 random(60,90) 0.1b
@end
```

### Complex Drum Loop

```mmd
# 4-bar drum pattern with variations
@loop 4 times at [1.1.0] every 4b
  # Bar 1
  - note_on 10.C1 110 0.1b      # Kick
  - note_on 10.F#2 70 0.1b      # Closed hi-hat

  [+1b]
  - note_on 10.D1 90 0.1b       # Snare
  - note_on 10.F#2 65 0.1b

  [+1b]
  - note_on 10.C1 105 0.1b      # Kick
  - note_on 10.F#2 70 0.1b

  [+0.5b]
  - note_on 10.C1 100 0.1b      # Kick (off-beat)

  [+0.5b]
  - note_on 10.D1 95 0.1b       # Snare
  - note_on 10.F#2 60 0.1b
@end
```

## Musical Elements

### Chord Progression

```mmd
# C - F - Am - G progression (whole notes)
[1.1.0]
- note_on 1.C4 80 4b    # C major
[@]
- note_on 1.E4 80 4b
[@]
- note_on 1.G4 80 4b

[2.1.0]
- note_on 1.F3 80 4b    # F major
[@]
- note_on 1.A3 80 4b
[@]
- note_on 1.C4 80 4b

[3.1.0]
- note_on 1.A3 80 4b    # A minor
[@]
- note_on 1.C4 80 4b
[@]
- note_on 1.E4 80 4b

[4.1.0]
- note_on 1.G3 80 4b    # G major
[@]
- note_on 1.B3 80 4b
[@]
- note_on 1.D4 80 4b
```

### Bass Line

```mmd
# Simple bass pattern
@loop 4 times at [1.1.0] every 4b
  - note_on 1.C2 100 0.5b
  [+0.5b]
  - note_on 1.C2 80 0.25b
  [+0.75b]
  - note_on 1.C2 90 0.5b
  [+0.5b]
  - note_on 1.G2 95 0.5b
@end
```

### Arpeggiator Pattern

```mmd
# C major arpeggio (ascending)
@loop 4 times at [1.1.0] every 1b
  - note_on 1.C4 90 0.25b
  [+0.25b]
  - note_on 1.E4 85 0.25b
  [+0.25b]
  - note_on 1.G4 85 0.25b
  [+0.25b]
  - note_on 1.C5 90 0.25b
@end
```

## Automation and Effects

### Volume Fade In

```mmd
# Smooth fade from silence to full
@sweep from [00:00.000] to [00:04.000] every 100ms
  - cc 1.7 ramp(0, 100, ease-out)
@end
```

### Volume Fade Out

```mmd
# Smooth fade to silence
@sweep from [00:30.000] to [00:34.000] every 100ms
  - cc 1.7 ramp(100, 0, ease-in)
@end
```

### Filter Sweep

```mmd
# Filter opening (exponential curve)
@sweep from [1.1.0] to [5.1.0] every 8t
  - cc 1.74 ramp(0, 127, exponential)
@end

# Filter closing (logarithmic curve)
@sweep from [9.1.0] to [13.1.0] every 8t
  - cc 1.74 ramp(127, 0, logarithmic)
@end
```

### Pan Automation

```mmd
# Pan from left to right
@sweep from [00:00.000] to [00:08.000] every 50ms
  - cc 1.10 ramp(0, 127, linear)
@end

# Auto-pan (stereo LFO)
[00:00.000]
[@]
- cc 1.10.wave(sine, 64, freq=2.0, depth=80)            # Left
[@]
- cc 2.10.wave(sine, 64, freq=2.0, phase=0.5, depth=80)  # Right (180°)
```

### Expression Swell

```mmd
# Natural expression curve
[00:00.000]
- cc 1.11.curve(0, 127, ease-in-out)

# With envelope
[00:04.000]
- cc 1.11.envelope(ar, attack=2.0, release=1.5)
```

### Vibrato (Mod Wheel)

```mmd
# Vibrato using CC#1 (5 Hz)
[00:00.000]
- cc 1.1.wave(sine, 64, freq=5.0, depth=10)
```

### Tremolo (Volume)

```mmd
# Tremolo effect (4 Hz)
[00:00.000]
- cc 1.7.wave(sine, 100, freq=4.0, depth=30)
```

### Pitch Bend Effects

```mmd
# Pitch dive
[00:00.000]
- pb 1.envelope(ad, attack=0.01, decay=1.5)

# Pitch vibrato
[00:02.000]
- pb 1.wave(sine, 8192, freq=5.5, depth=5)

# Smooth pitch sweep
[00:04.000]
- pb 1.curve(-4096, 4096, ease-in-out)
```

### Filter Envelope (ADSR)

```mmd
# Synth-style filter envelope
[00:00.000]
- note_on 1.60.80 4b
[@]
- cc 1.74.envelope(adsr, attack=0.5, decay=0.3, sustain=0.7, release=1.0)
```

## Device Control

### Quad Cortex Preset Loading

```mmd
@import "devices/quad_cortex.mmd"

[00:00.000]
- cortex_load 1.1.0.5       # Channel 1, Setlist 1, Scene 0, Preset 5

[00:16.000]
- cortex_scene 1 1          # Switch to Scene B

[00:32.000]
- cortex_stomp_a_on 1       # Engage stomp A
```

### Eventide H90 Automation

```mmd
@import "devices/eventide_h90.mmd"

[00:00.000]
- h90_preset 2 20           # Load preset 20 on channel 2

[00:08.000]
- h90_mix 2 50              # Set A/B mix to 50%

[00:16.000]
- h90_routing 2 parallel    # Parallel routing
```

### Multi-Device Coordination

```mmd
@import "devices/quad_cortex.mmd"
@import "devices/eventide_h90.mmd"

[00:00.000]
- marker "Intro - Clean"
- cortex_preset 1 0
- h90_preset 2 10
- h90_mix 2 20

[00:32.000]
- marker "Verse - Driven"
- cortex_stomp_a_on 1       # Drive on
- h90_mix 2 40

[01:04.000]
- marker "Chorus - Full"
- cortex_scene 1 2
- h90_routing 2 series
- h90_mix 2 70
```

## Generative Techniques

### Random Velocity Humanization

```mmd
# Natural velocity variation
@loop 16 times at [00:00.000] every 0.25b
  - note_on 1.C4 random(70,100) 0.5b
@end
```

### Generative Ambient Pad

```mmd
# Evolving pad with random notes
@loop 8 times at [00:00.000] every 4b
  - note_on 1.random(C3,E4) random(60,80) 4b
@end
```

### Random CC Automation

```mmd
# Evolving filter automation
@loop 32 times at [00:00.000] every 0.5b
  - cc 1.74.random(30,90)
@end
```

### Algorithmic Drum Pattern

```mmd
# Kick on beats 1 and 3 (consistent)
@loop 16 times at [1.1.0] every 2b
  - note_on 10.C1 110 0.1b
@end

# Hi-hat with random velocity
@loop 64 times at [1.1.0] every 0.25b
  - note_on 10.F#2 random(50,80) 0.1b
@end

# Snare with ghost notes (random)
@loop 16 times at [1.2.0] every 2b
  - note_on 10.D1 random(85,100) 0.1b
@end
```

### Layered Textures

```mmd
# Layer 1: Sustained bass note
[00:00.000]
- note_on 1.C2 70 32b

# Layer 2: Evolving pad
[@]
@loop 8 times at [00:00.000] every 4b
  - note_on 2.random(C3,G3) random(50,70) 4b
@end

# Layer 3: Random high notes
[@]
@loop 16 times at [00:00.000] every 2b
  - note_on 3.random(C5,C6) random(30,50) random(0.5,2.0)b
@end

# Layer 4: Filter automation
[@]
- cc 1.74.wave(sine, 64, freq=0.1, depth=60)
```

---

## Working Example Files

For more comprehensive examples, see the project's `examples/` directory:

- `examples/00_basics/` - Start here (4 files)
- `examples/01_timing/` - Timing paradigms (4 files)
- `examples/02_midi_features/` - MIDI commands (9 files)
- `examples/03_advanced/` - Advanced features (13 files)
- `examples/04_device_libraries/` - Device control (9 files)
- `examples/05_generative/` - Generative techniques (6 files)
- `examples/06_tutorials/` - Progressive learning (4 files)

Total: 49 working example files

## Pattern Categories

### Timing Patterns
- Absolute timing for sync with audio/video
- Musical timing for tempo-aware sequences
- Relative timing for pattern building
- Simultaneous execution for chords

### Automation Patterns
- Linear ramps for simple fades
- Exponential curves for natural crescendos/decrescendos
- LFO modulation for vibrato, tremolo, auto-pan
- Envelope shapes for filter, volume, expression

### Musical Patterns
- Chord progressions (triads, 7th chords)
- Bass lines (root notes, walking bass)
- Arpeggios (ascending, descending, patterns)
- Drum grooves (rock, electronic, jazz)

### Performance Patterns
- Preset changes with smooth transitions
- Multi-device coordination
- Scene switching synchronized across devices
- Expression automation following song structure

---

For syntax details, see REFERENCE.md in this skill directory.
For CLI usage, see the mmd-cli skill.
