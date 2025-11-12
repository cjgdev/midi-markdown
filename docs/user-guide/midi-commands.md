# MIDI Commands Reference

> **Audience**: Users
> **Level**: Beginner to Intermediate

Complete reference for all MIDI commands supported by MIDI Markdown. This guide covers channel voice messages, meta events, system messages, and provides practical examples for each command type.

## Table of Contents

- [Overview](#overview)
- [Channel Voice Messages](#channel-voice-messages)
  - [Note Commands](#note-commands)
  - [Control Change (CC)](#control-change-cc)
  - [Program Change](#program-change)
  - [Pitch Bend](#pitch-bend)
  - [Pressure/Aftertouch](#pressureaftertouch)
- [Meta Events](#meta-events)
  - [Tempo](#tempo)
  - [Time Signature](#time-signature)
  - [Key Signature](#key-signature)
  - [Text and Markers](#text-and-markers)
  - [Track End](#track-end)
- [System Messages](#system-messages)
  - [System Exclusive (SysEx)](#system-exclusive-sysex)
  - [System Common](#system-common)
  - [System Real-Time](#system-real-time)
- [Channel Mode Messages](#channel-mode-messages)
- [Common CC Numbers](#common-cc-numbers)
- [Note Names Reference](#note-names-reference)
- [Value Ranges Summary](#value-ranges-summary)
- [Examples by Use Case](#examples-by-use-case)

---

## Overview

MIDI commands in MMD are written as list items (prefixed with `-`) and placed after timing markers. All commands follow the pattern:

```markdown
[timing_marker]
- command_name parameters
```

Commands can use both full names and shorthand aliases for common operations.

---

## Channel Voice Messages

Channel voice messages are the most commonly used MIDI commands. They control note playback, instrument selection, and parameter automation on specific MIDI channels (1-16).

### Note Commands

Note commands trigger sound on MIDI instruments. MMD supports both note names (C4, D#5) and MIDI note numbers (0-127).

#### Note On with Automatic Note Off

The most common way to play notes - MMD automatically generates the note_off message:

```markdown
# Basic syntax
- note_on <channel>.<note> <velocity> <duration>

# Examples with note names
[00:00.000]
- note_on 1.C4 100 1b          # Middle C, velocity 100, 1 beat
- note_on 1.D#5 80 2b          # D# in octave 5, 2 beats
- note_on 2.Gb3 64 500ms       # G flat, 500 milliseconds

# Examples with MIDI note numbers
[00:01.000]
- note_on 1.60 127 1b          # Note 60 (C4), max velocity
- note_on 1.72 90 750ms        # Note 72 (C5), 750ms duration
```

**Parameters:**
- `channel`: MIDI channel (1-16)
- `note`: Note name (C-1 to G9) or MIDI number (0-127)
- `velocity`: How hard the note is struck (0-127, 0 = silent, 127 = loudest)
- `duration`: How long to sustain (beats `b`, milliseconds `ms`, or seconds `s`)

**Note Names:**
- Use sharps (#) or flats (b): `C#4`, `Db4`
- Octave range: C-1 (note 0) to G9 (note 127)
- Middle C is C4 (note 60)

#### Manual Note Control

For advanced control, send note_on and note_off separately:

```markdown
# Note on without automatic off
[00:00.000]
- note_on 1.C4 100

# Later, manually turn off
[00:02.000]
- note_off 1.C4 64              # With release velocity
```

**Use cases:**
- Overlapping notes on the same pitch
- Dynamic note duration based on conditions
- Fine control over note timing

---

### Control Change (CC)

Control Change messages adjust instrument parameters like volume, pan, modulation, and effects. CC messages use controller numbers 0-127 to control different parameters.

#### Basic Syntax

```markdown
# Full form
- control_change <channel>.<controller>.<value>

# Shorthand (recommended)
- cc <channel>.<controller>.<value>
```

**Parameters:**
- `channel`: MIDI channel (1-16)
- `controller`: CC number (0-127)
- `value`: Parameter value (0-127)

#### Common Examples

```markdown
[00:00.000]
# Volume (CC#7)
- cc 1.7.127                   # Maximum volume
- cc 1.7.0                     # Silence

# Pan (CC#10)
- cc 1.10.0                    # Hard left
- cc 1.10.64                   # Center
- cc 1.10.127                  # Hard right

# Expression (CC#11)
- cc 1.11.100                  # High expression
- cc 1.11.50                   # Medium expression

# Modulation Wheel (CC#1)
- cc 2.1.0                     # No modulation
- cc 2.1.64                    # Medium modulation
- cc 2.1.127                   # Full modulation

# Sustain Pedal (CC#64)
- cc 1.64.127                  # Pedal down (on)
- cc 1.64.0                    # Pedal up (off)

# Filter Cutoff (CC#74)
- cc 1.74.80                   # Adjust filter brightness
```

#### Automation Example

```markdown
# Fade in volume over 4 seconds
[00:00.000]
- cc 1.7.0

[00:01.000]
- cc 1.7.32

[00:02.000]
- cc 1.7.64

[00:03.000]
- cc 1.7.96

[00:04.000]
- cc 1.7.127
```

See [Common CC Numbers](#common-cc-numbers) for a complete reference table.

---

### Program Change

Program Change (PC) messages switch between different instrument sounds or presets on a MIDI device.

#### Basic Syntax

```markdown
# Full form
- program_change <channel>.<program>

# Shorthand (recommended)
- pc <channel>.<program>
```

**Parameters:**
- `channel`: MIDI channel (1-16)
- `program`: Preset/patch number (0-127)

**Note:** Most devices display programs as 1-128, but MIDI uses 0-127. Subtract 1 from the displayed number.

#### Examples

```markdown
[00:00.000]
- pc 1.0                       # Load program 0 (display: 1)
- pc 1.42                      # Load program 42 (display: 43)
- pc 2.127                     # Load program 127 (display: 128)

# With bank select (combine with CC#0 and CC#32)
[00:01.000]
- cc 1.32.0                    # Bank Select LSB
- cc 1.0.1                     # Bank Select MSB
- pc 1.5                       # Program 5 in bank 1
```

#### Use Cases

```markdown
# Song structure with preset changes
[00:00.000]
- marker "Intro"
- pc 1.10                      # Clean guitar

[00:08.000]
- marker "Verse"
- pc 1.15                      # Slightly overdriven

[00:16.000]
- marker "Chorus"
- pc 1.30                      # Full distortion
```

---

### Pitch Bend

Pitch Bend smoothly bends the pitch of notes up or down, commonly used for guitar bends, vibrato, and pitch effects.

#### Basic Syntax

```markdown
# Full form
- pitch_bend <channel>.<value>

# Shorthand (recommended)
- pb <channel>.<value>
```

**Parameters:**
- `channel`: MIDI channel (1-16)
- `value`: Bend amount (see range below)

**Value Range:**
- `-8192` to `+8191` (signed format, 0 = center)
- `0` to `16383` (unsigned format, 8192 = center)
- `0` or `8192` = no bend (center position)

#### Examples

```markdown
[00:00.000]
# Center position (no bend)
- pb 1.0

# Bend up
[00:01.000]
- pb 1.2000                    # Slight bend up
[00:02.000]
- pb 1.4000                    # Medium bend up
[00:03.000]
- pb 1.8191                    # Maximum bend up

# Return to center
[00:04.000]
- pb 1.0

# Bend down (negative values)
[00:05.000]
- pb 1.-2000                   # Slight bend down
[00:06.000]
- pb 1.-8192                   # Maximum bend down

# Return to center
[00:07.000]
- pb 1.0
```

#### Pitch Wheel Automation

```markdown
# Guitar-style bend
[00:00.000]
- note_on 1.60 100 2000ms      # Play note
[@]
- pb 1.0                       # Start at center

[00:00.500]
- pb 1.2000                    # Bend up gradually

[00:01.000]
- pb 1.4000                    # Continue bending

[00:01.500]
- pb 1.0                       # Return to pitch
```

**Note:** The actual pitch change depends on the device's pitch bend range setting (typically ±2 semitones, but can be configured up to ±12 or more).

---

### Pressure/Aftertouch

Pressure messages add expression after a note is played, simulating pressing harder on a key or string.

#### Channel Pressure (Monophonic Aftertouch)

Applies pressure to all sounding notes on a channel:

```markdown
# Full form
- channel_pressure <channel>.<value>

# Shorthand (recommended)
- cp <channel>.<value>

# Examples
[00:00.000]
- cp 1.30                      # Light pressure
- cp 1.64                      # Medium pressure
- cp 1.127                     # Maximum pressure
- cp 1.0                       # Release pressure
```

**Parameters:**
- `channel`: MIDI channel (1-16)
- `value`: Pressure amount (0-127)

#### Polyphonic Pressure (Per-Note Aftertouch)

Applies pressure to individual notes:

```markdown
# Full form
- poly_pressure <channel>.<note>.<value>

# Shorthand (recommended)
- pp <channel>.<note>.<value>

# Examples
[00:00.000]
- pp 1.60.80                   # Pressure on C4
- pp 1.64.90                   # Pressure on E4
- pp 1.67.100                  # Pressure on G4

# Increase pressure on C4
[00:01.000]
- pp 1.60.127                  # Maximum pressure
```

**Parameters:**
- `channel`: MIDI channel (1-16)
- `note`: Note name or MIDI number
- `value`: Pressure amount (0-127)

#### Combined Expression Example

```markdown
# Play note with dynamic expression
[00:00.000]
- note_on 1.C4 100 4000ms      # Play 4-second note

# Add pitch bend
[00:01.000]
- pb 1.2000

# Add channel pressure
[@]
- cp 1.80

# Increase both
[00:02.000]
- pb 1.4000
[@]
- cp 1.120

# Release both
[00:03.000]
- pb 1.0
[@]
- cp 1.0
```

---

## Meta Events

Meta events are MIDI file-only messages that don't produce sound but provide structure, tempo, and metadata. They are not sent to MIDI devices during playback.

### Tempo

Sets the playback tempo in beats per minute (BPM).

```markdown
- tempo <bpm>

# Examples
[00:00.000]
- tempo 120                    # 120 BPM (common default)
- tempo 132.5                  # Fractional BPM supported
- tempo 90                     # Slow ballad
- tempo 180                    # Fast techno

# Tempo changes during song
[00:00.000]
- tempo 100                    # Start slow
- marker "Intro"

[00:08.000]
- tempo 120                    # Speed up for verse
- marker "Verse"

[00:16.000]
- tempo 140                    # Fast chorus
- marker "Chorus"
```

**Range:** 1-300 BPM (practical range 40-240)

---

### Time Signature

Defines the musical meter (beats per bar and beat unit).

```markdown
- time_signature <numerator>/<denominator> [<clocks>] [<32nds>]

# Common examples
[00:00.000]
- time_signature 4/4           # Four-four time (default)
- time_signature 3/4           # Waltz time
- time_signature 6/8           # Compound meter
- time_signature 7/8           # Odd meter
- time_signature 5/4           # Take Five
- time_signature 12/8          # Slow compound time

# With optional parameters (advanced)
- time_signature 4/4 24 8      # Custom MIDI clock settings
```

**Parameters:**
- `numerator`: Beats per bar (1-32)
- `denominator`: Beat unit (2, 4, 8, 16, 32)
- `clocks`: MIDI clocks per metronome tick (optional, default 24)
- `32nds`: 32nd notes per quarter note (optional, default 8)

**Common Time Signatures:**
- 4/4: Rock, pop, most Western music
- 3/4: Waltz, minuet
- 6/8: Slow blues, Irish jigs
- 7/8: Progressive rock, Balkan folk
- 5/4: Jazz (Take Five)
- 12/8: Slow shuffle, compound time

---

### Key Signature

Sets the key signature for music notation (does not affect playback).

```markdown
- key_signature <key> [<mode>]

# Major keys
[00:00.000]
- key_signature C              # C major (default)
- key_signature G              # G major (1 sharp)
- key_signature F              # F major (1 flat)
- key_signature F#             # F# major (6 sharps)
- key_signature Bb             # Bb major (2 flats)

# Minor keys (add 'm' suffix)
- key_signature Am             # A minor (relative to C major)
- key_signature Dm             # D minor
- key_signature Cm             # C minor
- key_signature F#m            # F# minor
- key_signature Bbm            # Bb minor
```

**Parameters:**
- `key`: Note name (C, C#, D, Eb, etc.)
- `mode`: Major (default) or minor (add 'm' suffix)

**Use Cases:**
- Music notation display
- Score generation
- Educational materials
- Does NOT affect audio playback

---

### Text and Markers

Text meta events add labels, lyrics, copyright notices, and structure markers to MIDI files.

#### Markers

Structure markers for song sections:

```markdown
- marker "label"

[00:00.000]
- marker "Intro"

[00:08.000]
- marker "Verse 1"

[00:16.000]
- marker "Chorus"

[00:24.000]
- marker "Verse 2"

[00:32.000]
- marker "Bridge"

[00:40.000]
- marker "Outro"
```

Markers appear in DAW timelines and help navigate song structure.

#### Generic Text

General text annotations:

```markdown
- text "Any text content"

[00:00.000]
- text "Recording session: 2025-11-07"
- text "Tempo automation begins here"
```

#### Copyright

Copyright and attribution information:

```markdown
[00:00.000]
- copyright "© 2025 Your Name. All rights reserved."
- copyright "Licensed under CC BY-SA 4.0"
```

#### Track and Instrument Names

Label tracks and specify instruments:

```markdown
# Track name (usually at time 0)
[00:00.000]
- track_name "Lead Guitar"
- instrument_name "Quad Cortex"

# In multi-track files
## Track: Drums
[00:00.000]
- track_name "Drums"
- instrument_name "Roland TR-808"

## Track: Bass
[00:00.000]
- track_name "Bass"
- instrument_name "Moog Sub 37"
```

#### Lyrics

Synchronized lyrics (one syllable per event):

```markdown
[00:00.000]
- lyric "Hel-"
[00:00.500]
- lyric "lo "
[00:01.000]
- lyric "world"
```

#### Cue Points

Performance cues and instructions:

```markdown
[00:15.500]
- cue_point "Preset change on next beat"
[00:16.000]
- cue_point "Guitar solo begins"
```

#### Device Name

Specify target MIDI device:

```markdown
[00:00.000]
- device_name "H90 Effects"
- device_name "Quad Cortex Channel 1"
```

---

### Track End

Marks the end of a track (usually auto-generated by the compiler):

```markdown
- end_of_track
```

**Note:** You typically don't need to write this manually - the compiler adds it automatically at the end of each track.

---

## System Messages

System messages control MIDI devices at a system level, not tied to specific channels.

### System Exclusive (SysEx)

SysEx messages send manufacturer-specific data like patch dumps, device configuration, or custom commands.

#### Inline Hex Bytes

```markdown
- sysex <hex_bytes>

# Examples
[00:00.000]
# Roland device identity request
- sysex F0 41 10 00 11 F7

# Yamaha parameter change
[00:01.000]
- sysex F0 43 10 4C 00 00 7E 00 F7

# Universal SysEx (non-manufacturer specific)
[00:02.000]
- sysex F0 7E 00 06 01 F7
```

**Format:**
- Start with `F0` (SysEx start)
- Manufacturer ID (1-3 bytes)
- Data bytes
- End with `F7` (SysEx end)

#### Multi-line SysEx

For long messages, split across lines:

```markdown
[00:00.000]
- sysex F0 00 01 06
        02 03 04 05
        06 07 08 09
        F7
```

#### SysEx from File

Load SysEx data from external file:

```markdown
- sysex_file "path/to/patch_dump.syx"
- sysex_file "devices/quad_cortex/preset_01.syx"
```

**Common Use Cases:**
- Loading device presets
- Firmware updates
- Device configuration
- Patch librarian operations

---

### System Common

System common messages coordinate timing and song position across devices.

#### MIDI Time Code (MTC)

Quarter-frame MTC messages for SMPTE sync:

```markdown
- mtc_quarter_frame <value>

[00:00.000]
- mtc_quarter_frame 0
- mtc_quarter_frame 64
- mtc_quarter_frame 127
```

**Range:** 0-127

#### Song Position

Set song position in MIDI beats (sixteenth notes):

```markdown
- song_position <beats>

[00:00.000]
- song_position 0              # Song start
- song_position 16             # One bar (in 4/4)
- song_position 64             # Four bars
```

**Range:** 0-16383 beats

#### Song Select

Select a song number:

```markdown
- song_select <song>

[00:00.000]
- song_select 0                # Song 0
- song_select 5                # Song 5
```

**Range:** 0-127

#### Tune Request

Request all analog synthesizers to tune their oscillators:

```markdown
[00:00.000]
- tune_request
```

No parameters. Analog synths respond by tuning.

---

### System Real-Time

Real-time messages control MIDI clock and transport.

#### Transport Control

```markdown
# Start MIDI clock from beginning
- clock_start

# Stop MIDI clock
- clock_stop

# Continue from current position
- clock_continue

# Send single timing clock pulse (24 per quarter note)
- clock_tick
```

#### Example Transport Sequence

```markdown
[00:00.000]
- clock_start                  # Start playback

[00:08.000]
- clock_stop                   # Stop at 8 seconds

[00:10.000]
- clock_continue               # Resume from stop point
```

#### System Maintenance

```markdown
# Keep-alive message (sent every ~300ms during inactivity)
- active_sensing

# Reset all devices to power-on state
- system_reset
```

**Warning:** `system_reset` will reset all connected devices - use with caution!

---

## Channel Mode Messages

Channel mode messages control how a MIDI channel responds to note messages.

### All Sound Off

Immediately silence all sounds (faster than all_notes_off):

```markdown
- all_sound_off <channel>

[00:00.000]
- all_sound_off 1              # Emergency stop on channel 1
- all_sound_off 2              # Stop channel 2
```

**Use Case:** Emergency stop, panic button

### Reset All Controllers

Reset all controllers (CC values) to defaults:

```markdown
- reset_all_controllers <channel>

[00:00.000]
- reset_all_controllers 1      # Reset channel 1 controllers
```

Resets:
- Modulation (CC#1) → 0
- Expression (CC#11) → 127
- Sustain (CC#64) → 0
- Pitch bend → center
- Channel pressure → 0

### All Notes Off

Turn off all currently playing notes (with natural release):

```markdown
- all_notes_off <channel>

[00:00.000]
- all_notes_off 1              # Stop all notes on channel 1
```

**Difference from all_sound_off:**
- `all_notes_off`: Natural release (respects envelope)
- `all_sound_off`: Immediate silence (instant cutoff)

### Mono/Poly Mode

```markdown
# Enable polyphonic mode (multiple notes simultaneously)
- poly_mode <channel>

# Enable monophonic mode (one note at a time)
- mono_mode <channel>.<num_channels>

# Local control on/off
- local_control <channel>.<on|off>

# Examples
[00:00.000]
- poly_mode 1                  # Channel 1: polyphonic
- mono_mode 2.1                # Channel 2: monophonic, 1 voice
- local_control 1.off          # Disconnect keyboard from sound
```

---

## Common CC Numbers

Standard MIDI CC numbers and their typical uses:

| CC# | Name | Range | Description |
|-----|------|-------|-------------|
| 0 | Bank Select MSB | 0-127 | Select sound bank (Most Significant Byte) |
| 1 | Modulation Wheel | 0-127 | Vibrato depth, typically controlled by mod wheel |
| 2 | Breath Controller | 0-127 | Wind instrument breath control |
| 4 | Foot Controller | 0-127 | Expression pedal input |
| 5 | Portamento Time | 0-127 | Time to glide between notes |
| 7 | Channel Volume | 0-127 | Main volume for the channel |
| 8 | Balance | 0-127 | Balance between sounds (0=left, 127=right) |
| 10 | Pan | 0-127 | Stereo position (0=left, 64=center, 127=right) |
| 11 | Expression | 0-127 | Sub-volume control (percentage of CC#7) |
| 32 | Bank Select LSB | 0-127 | Select sound bank (Least Significant Byte) |
| 64 | Sustain Pedal | 0-63/64-127 | Off (<64) / On (≥64), binary on/off |
| 65 | Portamento On/Off | 0-63/64-127 | Off / On |
| 66 | Sostenuto | 0-63/64-127 | Sustain currently held notes |
| 67 | Soft Pedal | 0-127 | Reduce volume/brightness |
| 71 | Filter Resonance | 0-127 | Filter resonance (harmonic intensity) |
| 72 | Release Time | 0-127 | Envelope release time |
| 73 | Attack Time | 0-127 | Envelope attack time |
| 74 | Filter Cutoff | 0-127 | Filter brightness/cutoff frequency |
| 91 | Reverb Send | 0-127 | Amount of reverb effect |
| 93 | Chorus Send | 0-127 | Amount of chorus effect |
| 120 | All Sound Off | 0 | Immediate silence all channels |
| 121 | Reset All Controllers | 0 | Reset all CCs to defaults |
| 123 | All Notes Off | 0 | Stop all notes (natural release) |
| 124 | Omni Mode Off | 0 | Respond only to channel messages |
| 125 | Omni Mode On | 0 | Respond to all channel messages |
| 126 | Mono Mode On | varies | Monophonic mode with voice count |
| 127 | Poly Mode On | 0 | Polyphonic mode |

### CC Example by Category

```markdown
# Volume and Expression
[00:00.000]
- cc 1.7.100                   # Volume
- cc 1.11.80                   # Expression (% of volume)

# Pan and Balance
- cc 1.10.64                   # Center pan
- cc 1.8.64                    # Center balance

# Modulation and Effects
- cc 1.1.50                    # Modulation wheel
- cc 1.91.64                   # Reverb send
- cc 1.93.40                   # Chorus send

# Filter Controls (synthesizers)
- cc 1.74.80                   # Filter cutoff
- cc 1.71.60                   # Resonance

# Pedals and Switches
- cc 1.64.127                  # Sustain on
- cc 1.64.0                    # Sustain off
- cc 1.67.100                  # Soft pedal

# Envelope (synthesizers)
- cc 1.73.70                   # Attack time
- cc 1.72.50                   # Release time
```

---

## Note Names Reference

### Note Name Format

MIDI supports note names from C-1 (note 0) to G9 (note 127).

**Format:** `[Note][Accidental][Octave]`
- Note: C, D, E, F, G, A, B
- Accidental: # (sharp), b (flat), or none (natural)
- Octave: -1 to 9

### Enharmonic Equivalents

These pairs refer to the same pitch:
- C# = Db (C sharp = D flat)
- D# = Eb (D sharp = E flat)
- F# = Gb (F sharp = G flat)
- G# = Ab (G sharp = A flat)
- A# = Bb (A sharp = B flat)

**Note:** E#/Fb and B#/Cb are theoretical but not commonly used.

### Octave Reference

| Octave | Notes | MIDI Numbers | Use |
|--------|-------|--------------|-----|
| -1 | C-1 to B-1 | 0-11 | Sub-bass (rarely used) |
| 0 | C0 to B0 | 12-23 | Deep bass, organ pedals |
| 1 | C1 to B1 | 24-35 | Bass guitar, tuba |
| 2 | C2 to B2 | 36-47 | Bass instruments, kick drum |
| 3 | C3 to B3 | 48-59 | Low male vocals, cello |
| 4 | C4 to B4 | 60-71 | Middle C, guitar, piano center |
| 5 | C5 to B5 | 72-83 | High vocals, violin |
| 6 | C6 to B6 | 84-95 | Soprano, flute |
| 7 | C7 to B7 | 96-107 | Piccolo, whistle |
| 8 | C8 to B8 | 108-119 | Very high (rarely used) |
| 9 | C9 to G9 | 120-127 | Extreme high (rarely used) |

### Middle C

Middle C can be notated as:
- Note name: `C4`
- MIDI number: `60`
- Frequency: ~261.63 Hz

```markdown
# These are equivalent
- note_on 1.C4 100 1b
- note_on 1.60 100 1b
```

### Common Instrument Ranges

```markdown
# Piano (A0 to C8): notes 21-108
[00:00.000]
- note_on 1.A0 80 1b           # Lowest piano note
- note_on 1.C8 80 1b           # Highest piano note

# Guitar Standard Tuning (E2 to E6): notes 40-88
- note_on 1.E2 100 1b          # Low E string
- note_on 1.E4 100 1b          # High E string

# Bass Guitar (E1 to G3): notes 28-55
- note_on 1.E1 100 1b          # Low E string
- note_on 1.G3 100 1b          # High note

# Male Vocals (E2 to E4): notes 40-64
# Female Vocals (C4 to C6): notes 60-84
```

---

## Value Ranges Summary

Quick reference for all MIDI value ranges:

| Parameter | Range | Notes |
|-----------|-------|-------|
| **Channels** | 1-16 | MIDI supports 16 channels |
| **Note Numbers** | 0-127 | C-1 (0) to G9 (127) |
| **Velocity** | 0-127 | 0 = silent/off, 127 = maximum |
| **CC Values** | 0-127 | Controller value range |
| **CC Numbers** | 0-127 | 128 different controllers |
| **Program Numbers** | 0-127 | 128 presets per bank |
| **Pitch Bend** | -8192 to +8191 | Or 0 to 16383 (0/8192 = center) |
| **Pressure** | 0-127 | Aftertouch amount |
| **Tempo** | 1-300 BPM | Practical: 40-240 BPM |
| **Song Position** | 0-16383 | In MIDI beats (1/16 notes) |
| **Song Select** | 0-127 | Song number |

### Binary Controllers (On/Off)

Some CCs are treated as switches:
- **0-63:** Off
- **64-127:** On

Examples: Sustain (CC#64), Portamento (CC#65), Sostenuto (CC#66)

```markdown
[00:00.000]
- cc 1.64.127                  # Sustain ON
- cc 1.64.0                    # Sustain OFF
- cc 1.64.63                   # OFF (< 64)
- cc 1.64.64                   # ON (≥ 64)
```

---

## Examples by Use Case

### Basic Melody

```markdown
---
title: "Simple Melody"
ppq: 480
---

[00:00.000]
- tempo 120
- time_signature 4/4

# Four-bar melody
[1.1.000]
- note_on 1.C4 100 1b
[1.2.000]
- note_on 1.D4 100 1b
[1.3.000]
- note_on 1.E4 100 1b
[1.4.000]
- note_on 1.F4 100 2b

[2.2.000]
- note_on 1.G4 100 1b
[2.3.000]
- note_on 1.A4 100 1b
[2.4.000]
- note_on 1.B4 100 1b
[3.1.000]
- note_on 1.C5 100 4b          # Whole note
```

### Multi-Channel Arrangement

```markdown
---
title: "Multi-Channel Demo"
midi_format: 1
---

[00:00.000]
- tempo 100
- time_signature 4/4

# Channel 1: Lead
[1.1.000]
- pc 1.24                      # Acoustic Guitar
- cc 1.7.110                   # Volume
- note_on 1.E4 100 2b

# Channel 2: Bass
[@]
- pc 2.33                      # Acoustic Bass
- cc 2.7.100
- note_on 2.E2 100 2b

# Channel 10: Drums (GM standard)
[@]
- note_on 10.36 100 1b         # Kick
[@]
- note_on 10.42 80 1b          # Hi-hat
```

### Volume Fade In/Out

```markdown
[00:00.000]
# Fade in over 5 seconds
- cc 1.7.0
[00:01.000]
- cc 1.7.25
[00:02.000]
- cc 1.7.50
[00:03.000]
- cc 1.7.75
[00:04.000]
- cc 1.7.100
[00:05.000]
- cc 1.7.127

# Music plays here...

# Fade out over 5 seconds
[00:30.000]
- cc 1.7.127
[00:31.000]
- cc 1.7.100
[00:32.000]
- cc 1.7.75
[00:33.000]
- cc 1.7.50
[00:34.000]
- cc 1.7.25
[00:35.000]
- cc 1.7.0
```

### Pan Automation (Left-Right Sweep)

```markdown
[00:00.000]
# Start hard left
- cc 1.10.0

# Move to center over 4 seconds
[00:01.000]
- cc 1.10.32
[00:02.000]
- cc 1.10.64                   # Center
[00:03.000]
- cc 1.10.96
[00:04.000]
- cc 1.10.127                  # Hard right
```

### Pitch Bend Vibrato

```markdown
[00:00.000]
- note_on 1.60 100 4000ms      # Long note

# Create vibrato with pitch bend
[00:00.000]
- pb 1.0
[00:00.200]
- pb 1.500
[00:00.400]
- pb 1.-500
[00:00.600]
- pb 1.500
[00:00.800]
- pb 1.-500
[00:01.000]
- pb 1.0                       # Return to center
```

### Preset Change with Bank Select

```markdown
[00:00.000]
# Load preset from specific bank
- cc 1.32.0                    # Bank LSB = 0
- cc 1.0.2                     # Bank MSB = 2
- pc 1.10                      # Program 10 in bank 2

[00:04.000]
# Change to different bank
- cc 1.32.1                    # Bank LSB = 1
- cc 1.0.0                     # Bank MSB = 0
- pc 1.25                      # Program 25 in bank 1
```

### Song Structure with Markers

```markdown
[00:00.000]
- tempo 120
- marker "Intro"
- text "8-bar intro"

[00:08.000]
- marker "Verse 1"

[00:16.000]
- marker "Chorus"
- tempo 130                    # Speed up for chorus

[00:24.000]
- marker "Verse 2"
- tempo 120                    # Back to original tempo

[00:32.000]
- marker "Bridge"

[00:40.000]
- marker "Chorus"
- tempo 130

[00:48.000]
- marker "Outro"
- tempo 110                    # Slow down
```

### Emergency Stop

```markdown
# Something went wrong - stop everything!
[00:05.000]
- all_sound_off 1              # Stop channel 1
- all_sound_off 2              # Stop channel 2
- all_sound_off 3              # Stop channel 3
- reset_all_controllers 1      # Reset controllers
- pb 1.0                       # Center pitch bend
```

---

## Next Steps

- **[Timing System](timing-system.md)** - Learn about timing markers and formats
- **[Variables and Loops](variables-loops.md)** - Automate repetitive patterns
- **[Alias System](alias-system.md)** - Create reusable command shortcuts
- **[Device Libraries](device-libraries.md)** - Use device-specific commands

## See Also

- **[MML Syntax Reference](mmd-syntax.md)** - Complete language syntax
- **[Compile Command](../cli-reference/compile.md)** - Compile MMD to MIDI
- **[Example Files](https://github.com/cjgdev/midi-markdown/tree/main/examples)** - 51 real-world MMD examples
- **[Troubleshooting](../reference/troubleshooting.md)** - Common issues and solutions
