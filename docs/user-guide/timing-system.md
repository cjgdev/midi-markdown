# Timing System Guide

**Audience**: Beginners to Advanced
**Level**: Comprehensive
**Estimated Reading Time**: 15-20 minutes

## Table of Contents

- [Introduction](#introduction)
- [The Four Timing Paradigms](#the-four-timing-paradigms)
  - [Absolute Timecode](#absolute-timecode)
  - [Musical Time](#musical-time)
  - [Relative Delta](#relative-delta)
  - [Simultaneous](#simultaneous)
- [When to Use Each Paradigm](#when-to-use-each-paradigm)
- [Mixing Timing Paradigms](#mixing-timing-paradigms)
- [PPQ and Resolution](#ppq-and-resolution)
- [Tempo and Time Signature](#tempo-and-time-signature)
- [Converting Between Paradigms](#converting-between-paradigms)
- [Timing Best Practices](#timing-best-practices)
- [Common Mistakes and Troubleshooting](#common-mistakes-and-troubleshooting)
- [Practical Examples](#practical-examples)
- [See Also](#see-also)

## Introduction

One of MML's most powerful features is its **flexible timing system** that supports four different paradigms for specifying when MIDI events occur. This flexibility allows you to choose the most natural and intuitive way to express timing for your specific use case.

### Why Four Paradigms?

Different musical and automation contexts benefit from different timing representations:

- **Absolute timecode** is ideal for syncing with video or audio recordings
- **Musical time** is natural for composing music with bars and beats
- **Relative delta** is perfect for sequential patterns and loops
- **Simultaneous** allows layering multiple events at the same moment

All four paradigms can be **mixed freely** within the same document, giving you complete flexibility.

### Key Concepts

Before diving into each paradigm, understand these core concepts:

1. **Timing markers** specify *when* an event occurs
2. **Timing must be monotonically increasing** within a track (later events can't occur before earlier ones)
3. **All timing is converted to MIDI ticks** internally
4. **PPQ (Pulses Per Quarter note)** determines timing resolution (default: 480)

## The Four Timing Paradigms

### Absolute Timecode

**Format**: `[mm:ss.milliseconds]`

Absolute timecode specifies the exact clock time when an event should occur, measured from the start of the composition (time zero).

#### Syntax

```
[minutes:seconds.milliseconds]
```

- `minutes`: Integer minutes (0+)
- `seconds`: Integer seconds (0-59)
- `milliseconds`: Integer milliseconds (0-999)

#### Examples

```markdown
# Simple absolute timing
[00:00.000]
- note_on 1.60.80 1b    # At the very start

[00:01.000]
- note_off 1.60         # Exactly 1 second later

[00:02.500]
- cc 1.7.100            # At 2.5 seconds

[01:23.750]
- pc 1.5                # At 1 minute, 23.75 seconds
```

#### When to Use

- **Video/audio sync**: When aligning MIDI to a specific timestamp in a recording
- **Live performance cues**: When you need precise timing relative to a click track
- **Automation sequences**: When timing must match real-world clock time
- **Non-musical content**: When bars/beats don't make sense for your context

#### Advantages

- **Intuitive**: Easy to read and understand ("this happens at 1:30")
- **Precise**: Millisecond accuracy
- **Independent**: Doesn't require tempo or time signature
- **Universal**: Same meaning regardless of musical context

#### Limitations

- **Not tempo-aware**: Changing tempo doesn't affect absolute times
- **Less musical**: Doesn't align naturally with bars and beats
- **Manual calculation**: Need to calculate timings yourself

### Musical Time

**Format**: `[bars.beats.ticks]`

Musical time specifies when events occur in terms of musical measures, beats, and MIDI ticks. This is the most natural representation for composed music.

#### Syntax

```
[bars.beats.ticks]
```

- `bars`: Bar/measure number (1-based, starting at 1)
- `beats`: Beat within the bar (1-based, starting at 1)
- `ticks`: MIDI ticks within the beat (0-based, 0 to PPQ-1)

#### Requirements

Musical time **requires** two pieces of frontmatter:

```yaml
---
tempo: 120        # BPM (required)
time_signature: 4/4  # Meter (required, defaults to 4/4)
---
```

#### Examples

```markdown
---
tempo: 120
time_signature: 4/4
---

# Musical timing examples
[1.1.0]
- note_on 1.60.80 1b    # Bar 1, beat 1, start

[1.2.0]
- note_on 1.62.80 1b    # Bar 1, beat 2

[1.3.0]
- note_on 1.64.80 1b    # Bar 1, beat 3

[1.4.0]
- note_on 1.65.80 1b    # Bar 1, beat 4

[2.1.0]
- note_on 1.67.80 1b    # Bar 2, beat 1

[2.1.240]
- note_on 1.69.80 0.5b  # Bar 2, beat 1, half-beat later (240 ticks @ PPQ 480)
```

#### Time Signatures

Musical time works with **any time signature**:

```markdown
---
tempo: 90
time_signature: 3/4  # Waltz time
---

[1.1.0]   # Bar 1, beat 1
[1.2.0]   # Bar 1, beat 2
[1.3.0]   # Bar 1, beat 3
[2.1.0]   # Bar 2, beat 1
```

```markdown
---
tempo: 140
time_signature: 6/8  # Compound meter
---

[1.1.0]   # Bar 1, beat 1 (dotted quarter note)
[1.2.0]   # Bar 1, beat 2 (dotted quarter note)
[2.1.0]   # Bar 2, beat 1
```

#### When to Use

- **Composing music**: When thinking in bars and beats
- **Song structure**: When working with verse/chorus/bridge sections
- **Working with DAWs**: When aligning with a digital audio workstation
- **Tempo-based content**: When tempo changes should affect timing

#### Advantages

- **Musical**: Natural for musicians and composers
- **Tempo-aware**: Respects tempo and time signature
- **Structure**: Easy to see song structure and form
- **DAW compatibility**: Matches sequencer grid

#### Limitations

- **Requires frontmatter**: Must specify tempo and time signature
- **Calculation needed**: Need to think in ticks for sub-beat timing
- **Less precise**: Harder to specify exact millisecond timing

### Relative Delta

**Format**: `[+duration]`

Relative delta specifies timing as an **offset from the previous event**, rather than an absolute position. This is ideal for sequential patterns and loops.

#### Syntax

```
[+duration]
```

Duration can be specified in multiple units:

- `[+Xms]` - Milliseconds (e.g., `[+500ms]`)
- `[+Xs]` - Seconds (e.g., `[+2.5s]`)
- `[+Xb]` - Beats (e.g., `[+1b]`, `[+0.5b]`)
- `[+bars.beats.ticks]` - Musical delta (e.g., `[+1.0.0]` = one bar)

#### Examples

```markdown
# Millisecond deltas
[00:00.000]
- note_on 1.60.80 1b

[+500ms]              # 500ms after previous event
- note_on 1.62.80 1b

[+250ms]              # 250ms after that (total: 750ms from start)
- note_on 1.64.80 1b
```

```markdown
# Beat deltas (requires tempo in frontmatter)
---
tempo: 120
---

[00:00.000]
- note_on 1.60.80 1b

[+1b]                 # One beat later
- note_on 1.62.80 1b

[+0.5b]               # Half beat later
- note_on 1.64.80 1b

[+2b]                 # Two beats later
- note_on 1.65.80 1b
```

```markdown
# Musical deltas
---
tempo: 120
time_signature: 4/4
---

[1.1.0]
- note_on 1.60.80 1b

[+0.1.0]              # One beat forward (bar 1, beat 2)
- note_on 1.62.80 1b

[+1.0.0]              # One bar forward (bar 2, beat 2)
- note_on 1.64.80 1b
```

#### When to Use

- **Sequential patterns**: When events follow a consistent rhythm
- **Loops**: When timing is relative to loop iteration
- **Delays**: When you need "wait X time then do Y"
- **Device programming**: When devices need delays between commands (e.g., Quad Cortex preset changes)

#### Advantages

- **Intuitive for sequences**: Natural for patterns and rhythms
- **Easy to adjust**: Change one timing, rest follow automatically
- **Flexible units**: Choose the most appropriate unit (ms, s, beats)
- **Perfect for loops**: Each iteration starts fresh

#### Limitations

- **Requires reference point**: Must have a previous absolute or musical time
- **Harder to read timing**: Need to mentally sum deltas to know absolute position
- **Can't skip backward**: Always moves forward in time

### Simultaneous

**Format**: `[@]`

The simultaneous marker indicates that events should occur at **exactly the same time** as the previous event. This is essential for chords, layered sounds, and multi-channel automation.

#### Syntax

```
[@]
```

Simple and unambiguous - means "same time as previous".

#### Examples

```markdown
# Chord (three notes at once)
[00:00.000]
- note_on 1.60.80 1b    # C
[@]
- note_on 1.64.80 1b    # E
[@]
- note_on 1.67.80 1b    # G

# Multi-channel event
[00:01.000]
- cc 1.7.127            # Channel 1 volume to max
[@]
- cc 2.7.127            # Channel 2 volume to max
[@]
- cc 3.7.127            # Channel 3 volume to max
```

```markdown
# Preset change with simultaneous settings
[00:00.000]
- pc 1.5                # Change preset
[@]
- cc 1.73.64            # Attack time
[@]
- cc 1.75.80            # Decay time
[@]
- cc 1.91.100           # Reverb level
```

#### When to Use

- **Chords**: Multiple notes sounding together
- **Multi-channel sync**: Same event to multiple channels
- **Snapshot recalls**: Multiple CCs at once to restore a state
- **Layered sounds**: Triggering multiple sounds simultaneously

#### Advantages

- **Zero latency**: Truly simultaneous in MIDI output
- **Simple syntax**: Easy to read and write
- **Explicit intent**: Makes simultaneity clear in the source

#### Limitations

- **Requires previous event**: Must have a timing reference
- **Can be verbose**: Lots of `[@]` lines for complex chords
- **No independent timing**: All events share the same timestamp

## When to Use Each Paradigm

Here's a quick decision guide:

| Use Case | Best Paradigm | Why |
|----------|---------------|-----|
| Syncing to video | Absolute | Exact timestamps match video frames |
| Composing a song | Musical | Natural bar/beat structure |
| Click track | Musical or Absolute | Either works; musical is more readable |
| Automation sequence | Relative | Sequential "wait then do" pattern |
| Device preset change | Relative | Devices need delays between commands |
| Chords | Simultaneous | Notes must sound together |
| Multi-channel sync | Simultaneous | Same timing across channels |
| Loop patterns | Relative | Each iteration starts fresh |
| Song structure | Musical | Verse at bar 1, chorus at bar 9, etc. |

## Mixing Timing Paradigms

One of MML's most powerful features is the ability to **mix paradigms freely** within the same document. The only rule: **timing must always increase** (monotonically).

### Example: Song with Mixed Paradigms

```markdown
---
title: "Mixed Timing Example"
tempo: 120
time_signature: 4/4
---

# Intro: Musical time for structure
[1.1.0]
- marker "Intro"
[@]
- note_on 1.48.80 4b    # 4-bar intro note

# Verse: Musical time
[5.1.0]
- marker "Verse 1"
- note_on 1.60.80 1b
[5.2.0]
- note_on 1.62.80 1b
[5.3.0]
- note_on 1.64.80 1b

# Quick fill: Relative time for pattern
[+250ms]
- note_on 1.65.70 250ms
[+250ms]
- note_on 1.67.70 250ms

# Chorus: Back to musical time
[9.1.0]
- marker "Chorus"
- note_on 1.72.90 1b    # High note
[@]
- note_on 1.60.90 1b    # Bass note (simultaneous)
[@]
- note_on 1.64.90 1b    # Chord tone (simultaneous)

# Outro: Absolute time for final sync point
[00:45.000]
- marker "Final Hit"
- note_on 1.48.127 2b
[@]
- cc 1.7.0              # Volume to zero (fade out)
```

### Rules for Mixing

1. **Start with absolute or musical**: First event needs a reference point
2. **Relative follows any paradigm**: `[+X]` adds to previous time
3. **Simultaneous follows any paradigm**: `[@]` uses previous time
4. **Musical time requires frontmatter**: Can't use bars.beats.ticks without tempo
5. **Time must increase**: Each new timing must be ≥ previous timing

### Common Patterns

```markdown
# Pattern 1: Musical structure + relative patterns
[1.1.0]                   # Musical: bar 1
- note_on 1.60.80 1b
[+500ms]                  # Relative: add 500ms
- note_on 1.62.80 1b
[+500ms]                  # Relative: add 500ms more
- note_on 1.64.80 1b
[2.1.0]                   # Musical: back to bar structure
- note_on 1.65.80 1b

# Pattern 2: Absolute base + simultaneous chords
[00:00.000]               # Absolute: exact time
- note_on 1.60.80 1b      # Root
[@]                       # Simultaneous: chord tone
- note_on 1.64.80 1b      # Third
[@]                       # Simultaneous: chord tone
- note_on 1.67.80 1b      # Fifth

# Pattern 3: Musical + simultaneous multi-channel
[1.1.0]                   # Musical: bar 1, beat 1
- cc 1.7.100              # Channel 1 volume
[@]                       # Simultaneous: all channels at once
- cc 2.7.100              # Channel 2 volume
[@]
- cc 3.7.100              # Channel 3 volume
```

## PPQ and Resolution

**PPQ (Pulses Per Quarter note)** is a fundamental MIDI concept that determines the **timing resolution** of your composition.

### What is PPQ?

PPQ defines how many MIDI "ticks" occur in one quarter note. Higher PPQ means finer timing resolution.

- **PPQ 480** (default): 480 ticks per quarter note
- **PPQ 960**: 960 ticks per quarter note (2x resolution)
- **PPQ 240**: 240 ticks per quarter note (0.5x resolution)

### How PPQ Affects Timing

```markdown
# With PPQ 480 (default)
---
tempo: 120
ppq: 480
---

[1.1.0]     # Bar 1, beat 1, tick 0
[1.1.240]   # Bar 1, beat 1, tick 240 (halfway through beat)
[1.2.0]     # Bar 1, beat 2, tick 0
```

```markdown
# With PPQ 960 (higher resolution)
---
tempo: 120
ppq: 960
---

[1.1.0]     # Bar 1, beat 1, tick 0
[1.1.480]   # Bar 1, beat 1, tick 480 (halfway through beat)
[1.2.0]     # Bar 1, beat 2, tick 0
```

### Choosing PPQ

| PPQ | Resolution | Use Case |
|-----|------------|----------|
| 96 | Low | Simple sequences, low memory |
| 240 | Medium | Standard MIDI files |
| 480 | High (default) | Professional production |
| 960 | Very high | Fine automation, complex timing |
| 1920 | Extreme | Scientific precision (rarely needed) |

### PPQ in CLI

Specify PPQ when compiling:

```bash
mmdc compile song.mmd --ppq 960
```

Or in frontmatter:

```yaml
---
ppq: 960
---
```

**Note**: Frontmatter PPQ takes precedence over CLI flag.

### Common PPQ Values

- **480**: MMD default, Logic Pro default, widely compatible
- **960**: Cubase/Nuendo default, very precise
- **384**: Pro Tools default (unusual but supported)
- **96**: Old MIDI files, simple applications

## Tempo and Time Signature

Musical time and beat-based relative timing depend on **tempo** and **time signature** specified in frontmatter.

### Tempo

**Tempo** specifies the speed in BPM (beats per minute).

```yaml
---
tempo: 120    # 120 BPM (quarter note = 500ms)
---
```

Common tempos:
- **60 BPM**: One beat per second (1000ms per beat)
- **90 BPM**: Slow ballad (666.67ms per beat)
- **120 BPM**: Moderate tempo (500ms per beat)
- **140 BPM**: Upbeat rock (428.57ms per beat)
- **180 BPM**: Fast electronic (333.33ms per beat)

### Time Signature

**Time signature** defines the meter (beats per bar and beat division).

```yaml
---
time_signature: 4/4    # 4 beats per bar, quarter note gets the beat
---
```

Common time signatures:
- **4/4**: Common time (4 quarter notes per bar)
- **3/4**: Waltz time (3 quarter notes per bar)
- **6/8**: Compound duple (2 dotted quarter notes per bar)
- **5/4**: Quintuple meter (5 quarter notes per bar)
- **7/8**: Odd meter (7 eighth notes per bar)

### How They Interact

```markdown
---
tempo: 120          # 120 BPM
time_signature: 4/4 # 4 beats per bar
ppq: 480            # 480 ticks per quarter note
---

# Each bar = 4 beats = 4 quarter notes = 1920 ticks (4 × 480)
# Each beat = 1 quarter note = 480 ticks
# At 120 BPM: each beat = 500ms, each bar = 2000ms

[1.1.0]    # Time: 0ms (bar 1, beat 1)
[1.2.0]    # Time: 500ms (bar 1, beat 2)
[1.3.0]    # Time: 1000ms (bar 1, beat 3)
[1.4.0]    # Time: 1500ms (bar 1, beat 4)
[2.1.0]    # Time: 2000ms (bar 2, beat 1)
```

```markdown
---
tempo: 90           # 90 BPM (slower)
time_signature: 3/4 # 3 beats per bar
ppq: 480
---

# Each bar = 3 beats = 3 quarter notes = 1440 ticks (3 × 480)
# Each beat = 1 quarter note = 480 ticks
# At 90 BPM: each beat = 666.67ms, each bar = 2000ms

[1.1.0]    # Time: 0ms (bar 1, beat 1)
[1.2.0]    # Time: 666.67ms (bar 1, beat 2)
[1.3.0]    # Time: 1333.33ms (bar 1, beat 3)
[2.1.0]    # Time: 2000ms (bar 2, beat 1)
```

### Dynamic Tempo Changes

Use the `tempo` command to change tempo mid-composition:

```markdown
---
tempo: 120    # Starting tempo
time_signature: 4/4
---

[1.1.0]
- tempo 120   # Confirm starting tempo
- note_on 1.60.80 1b

[5.1.0]
- tempo 140   # Speed up at bar 5
- note_on 1.62.80 1b

[9.1.0]
- tempo 100   # Slow down at bar 9
- note_on 1.64.80 1b
```

## Converting Between Paradigms

Sometimes you need to convert between timing paradigms. Here are formulas and examples.

### Absolute to Musical

**Formula**:
```
Given:
  - Absolute time in milliseconds: T_ms
  - Tempo in BPM: tempo
  - PPQ: ppq
  - Time signature: beats_per_bar / beat_division

Calculate:
  ms_per_beat = 60000 / tempo
  ticks_per_beat = ppq
  ticks_total = (T_ms / ms_per_beat) * ticks_per_beat

  bars = floor(ticks_total / (beats_per_bar * ticks_per_beat)) + 1
  remaining_ticks = ticks_total % (beats_per_bar * ticks_per_beat)
  beats = floor(remaining_ticks / ticks_per_beat) + 1
  ticks = remaining_ticks % ticks_per_beat

Result: [bars.beats.ticks]
```

**Example**:
```
Given:
  - Time: 00:03.000 (3000ms)
  - Tempo: 120 BPM
  - PPQ: 480
  - Time signature: 4/4

Calculate:
  ms_per_beat = 60000 / 120 = 500ms
  ticks_per_beat = 480
  ticks_total = (3000 / 500) * 480 = 2880 ticks

  bars = floor(2880 / (4 * 480)) + 1 = floor(2880 / 1920) + 1 = 1 + 1 = 2
  remaining_ticks = 2880 % 1920 = 960
  beats = floor(960 / 480) + 1 = 2 + 1 = 3
  ticks = 960 % 480 = 0

Result: [2.3.0] (bar 2, beat 3)
```

### Musical to Absolute

**Formula**:
```
Given:
  - Musical time: [bars.beats.ticks]
  - Tempo in BPM: tempo
  - PPQ: ppq
  - Time signature: beats_per_bar / beat_division

Calculate:
  ms_per_beat = 60000 / tempo
  ticks_per_beat = ppq

  total_ticks = ((bars - 1) * beats_per_bar + (beats - 1)) * ticks_per_beat + ticks
  T_ms = (total_ticks / ticks_per_beat) * ms_per_beat

Result: [mm:ss.milliseconds]
```

**Example**:
```
Given:
  - Musical time: [3.2.240]
  - Tempo: 120 BPM
  - PPQ: 480
  - Time signature: 4/4

Calculate:
  ms_per_beat = 60000 / 120 = 500ms
  ticks_per_beat = 480

  total_ticks = ((3 - 1) * 4 + (2 - 1)) * 480 + 240
              = (2 * 4 + 1) * 480 + 240
              = (8 + 1) * 480 + 240
              = 4320 + 240
              = 4560 ticks

  T_ms = (4560 / 480) * 500 = 9.5 * 500 = 4750ms = 4.75 seconds

Result: [00:04.750]
```

### Relative to Absolute/Musical

Relative timing requires summing with the previous event's time:

```markdown
[00:00.000]     # Absolute: 0ms
- note_on 1.60.80 1b

[+500ms]        # Relative: +500ms → Absolute: 500ms
- note_on 1.62.80 1b

[+250ms]        # Relative: +250ms → Absolute: 750ms
- note_on 1.64.80 1b
```

To convert, maintain a running sum of the current absolute time.

## Timing Best Practices

### 1. Choose the Right Paradigm

**Use musical time** for most compositions:
```markdown
---
tempo: 120
time_signature: 4/4
---

[1.1.0]
- marker "Intro"
```

**Use absolute time** for sync points:
```markdown
[00:00.000]
- marker "Video sync point"
```

**Use relative time** for patterns:
```markdown
[1.1.0]
- note_on 1.60.80 1b
[+500ms]
- note_on 1.62.80 1b
[+500ms]
- note_on 1.64.80 1b
```

### 2. Be Consistent Within Sections

Pick one paradigm for a section and stick with it:

```markdown
# Good: Consistent musical time
[1.1.0]
- note_on 1.60.80 1b
[1.2.0]
- note_on 1.62.80 1b
[1.3.0]
- note_on 1.64.80 1b

# Bad: Mixing unnecessarily
[1.1.0]
- note_on 1.60.80 1b
[00:00.500]
- note_on 1.62.80 1b
[+500ms]
- note_on 1.64.80 1b
```

### 3. Use Comments for Clarity

```markdown
# Intro section (bars 1-4)
[1.1.0]
- marker "Intro"

# Main riff
[5.1.0]
- marker "Verse 1"

# Quick fill before chorus
[+250ms]
- note_on 1.65.70 250ms
```

### 4. Align with Grid for Musical Time

Prefer clean beat boundaries:

```markdown
# Good: On the grid
[1.1.0]
[1.2.0]
[1.3.0]
[2.1.0]

# Acceptable: Deliberate off-grid
[1.1.240]  # Deliberately half-beat
[1.2.360]  # Deliberately 3/4 beat
```

### 5. Use Simultaneous for True Sync

For events that must happen together, use `[@]`:

```markdown
# Chord: truly simultaneous
[1.1.0]
- note_on 1.60.80 1b
[@]
- note_on 1.64.80 1b
[@]
- note_on 1.67.80 1b
```

### 6. Leverage Relative for Device Programming

Many MIDI devices need delays between commands:

```markdown
# Quad Cortex preset change (needs delay)
[00:00.000]
- cc 1.32.0      # Bank LSB
[+10ms]          # Small delay
- cc 1.0.1       # Bank MSB
[+10ms]          # Small delay
- pc 1.5         # Program Change
```

## Common Mistakes and Troubleshooting

### Mistake 1: Non-Monotonic Timing

**Error**: Timing must always increase.

```markdown
# Wrong: Time goes backward
[00:02.000]
- note_on 1.60.80 1b
[00:01.000]     # ❌ Error: 1s < 2s
- note_on 1.62.80 1b
```

**Fix**: Ensure each timing is ≥ previous:

```markdown
# Correct: Time increases
[00:01.000]
- note_on 1.60.80 1b
[00:02.000]     # ✓ 2s > 1s
- note_on 1.62.80 1b
```

### Mistake 2: Musical Time Without Tempo

**Error**: Musical time requires tempo in frontmatter.

```markdown
# Wrong: No tempo specified
[1.1.0]     # ❌ Error: Requires tempo
- note_on 1.60.80 1b
```

**Fix**: Add frontmatter:

```markdown
# Correct: Tempo specified
---
tempo: 120
---

[1.1.0]     # ✓ Works
- note_on 1.60.80 1b
```

### Mistake 3: Relative Time Without Reference

**Error**: Relative time needs a previous absolute/musical time.

```markdown
# Wrong: First event is relative
[+500ms]    # ❌ Error: No reference point
- note_on 1.60.80 1b
```

**Fix**: Start with absolute or musical:

```markdown
# Correct: Start with absolute
[00:00.000]
- note_on 1.60.80 1b
[+500ms]    # ✓ Relative to 00:00.000
- note_on 1.62.80 1b
```

### Mistake 4: Simultaneous Without Previous Event

**Error**: `[@]` needs a previous event to reference.

```markdown
# Wrong: First event is simultaneous
[@]         # ❌ Error: No previous event
- note_on 1.60.80 1b
```

**Fix**: Start with a timed event:

```markdown
# Correct: Simultaneous follows timed
[00:00.000]
- note_on 1.60.80 1b
[@]         # ✓ Same time as previous
- note_on 1.64.80 1b
```

### Mistake 5: Wrong Tick Values

**Error**: Ticks must be 0 to PPQ-1 within a beat.

```markdown
---
tempo: 120
ppq: 480
---

# Wrong: Tick overflow
[1.1.480]   # ❌ Error: Tick 480 is actually beat 2
- note_on 1.60.80 1b
```

**Fix**: Use correct beat:

```markdown
# Correct: Move to next beat
[1.2.0]     # ✓ Bar 1, beat 2, tick 0
- note_on 1.60.80 1b
```

Or use correct tick range:

```markdown
# Correct: Tick within range
[1.1.479]   # ✓ Last tick of beat 1
- note_on 1.60.80 1b
```

## Practical Examples

### Example 1: Click Track

```markdown
---
title: "Click Track - 4 bars"
tempo: 120
time_signature: 4/4
---

# Bar 1
[1.1.0]
- note_on 10.76.127 100ms   # Downbeat (high)
[1.2.0]
- note_on 10.75.100 100ms   # Beat 2
[1.3.0]
- note_on 10.75.100 100ms   # Beat 3
[1.4.0]
- note_on 10.75.100 100ms   # Beat 4

# Bar 2
[2.1.0]
- note_on 10.76.127 100ms   # Downbeat (high)
[2.2.0]
- note_on 10.75.100 100ms
[2.3.0]
- note_on 10.75.100 100ms
[2.4.0]
- note_on 10.75.100 100ms

# Bar 3
[3.1.0]
- note_on 10.76.127 100ms   # Downbeat (high)
[3.2.0]
- note_on 10.75.100 100ms
[3.3.0]
- note_on 10.75.100 100ms
[3.4.0]
- note_on 10.75.100 100ms

# Bar 4
[4.1.0]
- note_on 10.76.127 100ms   # Downbeat (high)
[4.2.0]
- note_on 10.75.100 100ms
[4.3.0]
- note_on 10.75.100 100ms
[4.4.0]
- note_on 10.75.100 100ms
```

### Example 2: CC Automation

```markdown
---
title: "Filter Sweep"
---

# Absolute time automation: Smooth filter sweep over 4 seconds
[00:00.000]
- cc 1.74.0        # Filter cutoff: closed

[00:00.500]
- cc 1.74.32       # 1/8 open

[00:01.000]
- cc 1.74.64       # 1/4 open

[00:01.500]
- cc 1.74.96       # 3/8 open

[00:02.000]
- cc 1.74.127      # Fully open

[00:02.500]
- cc 1.74.96       # Start closing

[00:03.000]
- cc 1.74.64

[00:03.500]
- cc 1.74.32

[00:04.000]
- cc 1.74.0        # Fully closed
```

### Example 3: Song Structure

```markdown
---
title: "Complete Song Structure"
tempo: 120
time_signature: 4/4
---

# Intro (bars 1-4)
[1.1.0]
- marker "Intro"
- note_on 1.48.80 4b    # Sustained bass note

# Verse 1 (bars 5-12)
[5.1.0]
- marker "Verse 1"
- note_on 1.60.80 1b
[5.2.0]
- note_on 1.62.80 1b
[5.3.0]
- note_on 1.64.80 1b
[5.4.0]
- note_on 1.65.80 1b

# (Continue verse pattern...)
[8.1.0]
- note_on 1.67.80 1b

# Pre-Chorus (bars 13-14)
[13.1.0]
- marker "Pre-Chorus"
- note_on 1.69.85 0.5b
[+250ms]
- note_on 1.71.85 0.5b
[+250ms]
- note_on 1.72.85 0.5b

# Chorus (bars 15-22)
[15.1.0]
- marker "Chorus"
- note_on 1.72.90 1b    # High note
[@]
- note_on 1.60.90 1b    # Bass note
[@]
- note_on 1.64.90 1b    # Chord

# Bridge (bars 23-26)
[23.1.0]
- marker "Bridge"
- tempo 100             # Slow down
- note_on 1.65.70 2b

# Final Chorus (bars 27-34)
[27.1.0]
- marker "Final Chorus"
- tempo 120             # Back to tempo
- note_on 1.72.90 1b

# Outro (bars 35-38)
[35.1.0]
- marker "Outro"
- note_on 1.48.80 4b    # Same as intro
```

### Example 4: Multi-Channel Sync

```markdown
---
title: "Multi-Channel Scene Change"
---

# Scene 1: All channels clean
[00:00.000]
- marker "Scene 1: Clean"
- cc 1.7.100    # Ch 1: Volume full
[@]
- cc 2.7.100    # Ch 2: Volume full
[@]
- cc 3.7.0      # Ch 3: Muted
[@]
- cc 1.91.20    # Ch 1: Reverb low
[@]
- cc 2.91.20    # Ch 2: Reverb low

# Scene 2: Lead channel up, rhythm down
[00:10.000]
- marker "Scene 2: Lead Focus"
- cc 1.7.127    # Ch 1: Volume max (lead)
[@]
- cc 2.7.70     # Ch 2: Volume reduced (rhythm)
[@]
- cc 1.91.80    # Ch 1: Reverb high (lead)
[@]
- cc 2.91.30    # Ch 2: Reverb med (rhythm)

# Scene 3: All channels big
[00:20.000]
- marker "Scene 3: Full Band"
- cc 1.7.110    # Ch 1: Volume high
[@]
- cc 2.7.110    # Ch 2: Volume high
[@]
- cc 3.7.110    # Ch 3: Volume high
[@]
- cc 1.91.100   # All reverb high
[@]
- cc 2.91.100
[@]
- cc 3.91.100
```

### Example 5: Device Preset Change with Delays

```markdown
---
title: "Quad Cortex Preset Changes"
---

# Preset changes need delays between CC messages

# Change to Preset 5 in Bank 0.1
[00:00.000]
- marker "Preset: Clean Tone"
- cc 1.32.0      # Bank LSB = 0
[+10ms]
- cc 1.0.1       # Bank MSB = 1
[+10ms]
- pc 1.5         # Preset 5

# Change to Preset 12 in Bank 2.3
[00:05.000]
- marker "Preset: Heavy Distortion"
- cc 1.32.2      # Bank LSB = 2
[+10ms]
- cc 1.0.3       # Bank MSB = 3
[+10ms]
- pc 1.12        # Preset 12

# Change to Preset 0 in Bank 0.0
[00:10.000]
- marker "Preset: Bypass"
- cc 1.32.0      # Bank LSB = 0
[+10ms]
- cc 1.0.0       # Bank MSB = 0
[+10ms]
- pc 1.0         # Preset 0
```

## See Also

- [Getting Started Guide](../getting-started/quickstart.md) - Basic MMD introduction
- [MIDI Commands Reference](midi-commands.md) - All MIDI command types
- [Frontmatter Reference](../reference/frontmatter.md) - Document metadata options
- [Alias System Guide](alias-system.md) - Creating reusable command shortcuts
- [CLI Reference](../cli-reference/overview.md) - Command-line options including `--ppq`
- [Spec: Timing Specification](https://github.com/cjgdev/midi-markdown/blob/main/spec.md#timing-specification) - Formal timing rules
