# Loops and Patterns Reference

**Version:** 1.0.0
**Status:** Stable

## Overview

The `@loop` directive provides a powerful way to eliminate repetitive code by automatically generating repeated MIDI command sequences. Loops are essential for creating drum patterns, rhythmic sequences, and any repeating musical structure.

## Table of Contents

1. [Basic Syntax](#basic-syntax)
2. [Loop Timing Modes](#loop-timing-modes)
3. [Interval Specifications](#interval-specifications)
4. [Loop Variable Access](#loop-variable-access)
5. [Practical Examples](#practical-examples)
6. [Best Practices](#best-practices)
7. [Common Patterns](#common-patterns)
8. [Troubleshooting](#troubleshooting)

---

## Basic Syntax

### Standard Loop Structure

```mmd
@loop <count> times at [<start_time>] every <interval>
  # Commands to repeat
@end
```

**Parameters:**
- `<count>`: Number of iterations (positive integer)
- `[<start_time>]`: Optional timing marker (absolute, musical, or relative)
- `<interval>`: Time between iterations (with unit: s, ms, b, t, or musical notation)

### Minimal Loop (No Explicit Start Time)

```mmd
@loop <count> times every <interval>
  # Commands to repeat
@end
```

When `at [<start_time>]` is omitted, the loop begins immediately after the previous event or timing marker.

---

## Loop Timing Modes

The `at [<start_time>]` clause controls when the loop begins execution. Understanding these timing modes is critical for precise musical placement.

### 1. Absolute Timing

Loop starts at an absolute time from the beginning of the song.

**Format:** `[HH:MM.SSS]` or `[MM:SS.MS]`

```mmd
@loop 4 times at [00:05.000] every 1b
  - note_on 10.C1 100 1b      # Kick drum
@end
```

**Result:** Loop starts at exactly 5 seconds into the song, regardless of preceding timing markers.

**Use case:** When you need precise synchronization to absolute timestamps.

### 2. Musical Timing

Loop starts at a specific bar/beat/tick position.

**Format:** `[bars.beats.ticks]`

```mmd
@loop 4 times at [1.1.0] every 1b
  - note_on 10.C1 100 1b      # Kick
  - note_on 10.D1 80 1b       # Snare
@end
```

**Result:** Loop starts at bar 1, beat 1, tick 0 (the beginning of the song in musical time).

**Use case:** When working with bar/beat-based compositions. Respects time signature and tempo changes.

### 3. Relative Timing

Loop starts relative to the previous timing marker.

**Format:** `[+duration]` where duration includes a unit (s, ms, b, or musical notation)

```mmd
[00:05.000]
@loop 4 times at [+2s] every 1b
  - note_on 10.C1 100 1b
@end
```

**Result:** Loop starts 2 seconds after the previous marker (at 00:07.000).

```mmd
[1.1.0]
@loop 4 times at [+4b] every 1b
  - note_on 10.C1 100 1b
@end
```

**Result:** Loop starts 4 beats after bar 1, beat 1 (at bar 2, beat 1 in 4/4 time).

**Use case:** When you want loop timing to flow naturally from preceding events.

### 4. Implicit Timing

Loop starts immediately after the previous event or timing marker.

**Format:** Omit the `at [<start_time>]` clause entirely

```mmd
[5.1.0]
@loop 4 times every 1b
  - note_on 10.C1 100 1b      # Starts at bar 5, beat 1
@end
```

**Result:** Loop inherits the timing context from the previous marker.

**Use case:** When loop should flow directly from preceding timing context without additional offset.

---

## Important Timing Notes

### Independence of Loop Timing

**Critical:** Loop timing with `at [<start_time>]` is **independent** of preceding standalone timing markers.

```mmd
# This does NOT work as you might expect:
[00:10.000]
@loop 4 times at [00:00.000] every 1b
  - note_on 10.C1 100 1b
@end
```

**Result:** Loop starts at the beginning of the song (00:00.000), **NOT** 10 seconds later.

### Relative vs. Absolute

To make loop timing relative to a preceding marker, use the `[+duration]` syntax:

```mmd
# CORRECT - Relative timing
[00:10.000]
@loop 4 times at [+0s] every 1b   # Starts at 00:10.000
  - note_on 10.C1 100 1b
@end
```

Or omit the `at` clause to inherit the timing context:

```mmd
# CORRECT - Implicit timing
[00:10.000]
@loop 4 times every 1b            # Starts at 00:10.000
  - note_on 10.C1 100 1b
@end
```

---

## Interval Specifications

The `every <interval>` clause defines the time between loop iterations.

### Supported Units

| Unit | Description | Example |
|------|-------------|---------|
| `s` | Seconds | `every 0.5s` |
| `ms` | Milliseconds | `every 250ms` |
| `b` | Beats | `every 1b` |
| `t` | Ticks | `every 120t` |
| Musical | Bars.beats.ticks | `every 0.0.240` |

### Examples

```mmd
# Beat-based (most common for rhythmic patterns)
@loop 16 times every 1b
  - note_on 10.F#2 random(60,90) 0.1b  # Hi-hat every beat
@end

# Millisecond-based (precise timing)
@loop 8 times every 500ms
  - cc 1.74.random(40,100)
@end

# Tick-based (sub-beat precision)
@loop 4 times every 240t
  - note_on 10.C1 100 0.1b  # Every 16th note at 480 PPQ
@end

# Musical notation (bars.beats.ticks)
@loop 2 times every 2.0.0
  - marker "Section ${i}"
@end
```

### Fractional Beats

Fractional beats are supported for precise subdivision:

```mmd
@loop 8 times every 0.5b    # Every 8th note
  - note_on 10.F#2 80 0.1b
@end

@loop 16 times every 0.25b  # Every 16th note
  - note_on 10.F#2 60 0.05b
@end
```

---

## Loop Variable Access

### Loop Index Variable

Each loop iteration has access to a zero-based index variable `${i}`.

**Note:** This feature is planned but not yet implemented in the current version (v1.0.0). The specification reserves this syntax for future use.

**Planned syntax:**

```mmd
@loop 8 times every 1b
  - text "Beat ${i}"           # Iteration 0, 1, 2, ..., 7
  - note_on 1.${60 + i} 100 1b # Ascending notes C4-G4
@end
```

**Current workaround:** Use variables and nested structures:

```mmd
@define base_note 60

@loop 8 times every 1b
  - note_on 1.${base_note} 100 1b
@end

@define base_note ${base_note + 1}
```

---

## Practical Examples

### Example 1: Basic Drum Pattern

```mmd
---
title: "Basic 4/4 Drum Loop"
tempo: 120
time_signature: 4/4
---

# Kick on beats 1 and 3
@loop 8 times at [1.1.0] every 2b
  - note_on 10.C1 100 0.1b
@end

# Snare on beats 2 and 4
@loop 8 times at [1.2.0] every 2b
  - note_on 10.D1 90 0.1b
@end

# Hi-hat every 8th note
@loop 32 times at [1.1.0] every 0.5b
  - note_on 10.F#2 random(60,80) 0.1b
@end
```

### Example 2: Relative Timing Flow

```mmd
# Intro section
[00:00.000]
- marker "Intro"

# Start loop 4 beats after intro marker
@loop 4 times at [+4b] every 1b
  - note_on 10.C1 100 0.5b
@end

# Next loop starts immediately after previous
@loop 4 times every 1b
  - note_on 10.D1 80 0.5b
@end
```

### Example 3: Humanized Hi-Hat Pattern

```mmd
@loop 16 times at [00:00.000] every 0.25b
  - note_on 10.F#2 random(60,90) 0.1b
@end
```

**Result:** 16 hi-hat hits with randomized velocity for natural feel.

### Example 4: Click Track Generator

```mmd
---
title: "Click Track"
tempo: 120
time_signature: 4/4
ppq: 480
---

@loop 160 times at [0.1.0] every 1b
  - note_on 10.C4 100 50ms   # Click on every beat
@end
```

**Result:** 160 beats of metronome click (40 bars in 4/4 time).

### Example 5: Multi-Track Loop

```mmd
## Track 1: Kick
@track kick channel=10

@loop 4 times at [1.1.0] every 1b
  - note_on 10.C1 100 1b      # Kick
@end

## Track 2: Snare
@track snare channel=10

@loop 4 times at [1.1.0] every 1b
  [@]                         # Simultaneous with kick
  - note_on 10.D1 80 1b       # Snare
@end
```

### Example 6: Modulation Loop

```mmd
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
```

**Result:** Creates a rhythmic pulsing modulation effect during chorus.

### Example 7: Implicit Timing

```mmd
[5.1.0]
- marker "Verse"

@loop 4 times every 1b
  - note_on 10.C1 100 1b      # Starts at bar 5, beat 1
@end
```

---

## Best Practices

### 1. Choose Appropriate Timing Mode

- **Absolute timing** `at [MM:SS.MS]`: Use for precise synchronization to timestamps
- **Musical timing** `at [bars.beats.ticks]`: Use for bar/beat-based compositions
- **Relative timing** `at [+duration]`: Use when loop should flow from preceding events
- **Implicit timing** (no `at` clause): Use when loop inherits timing context

### 2. Use Beat-Based Intervals for Rhythmic Patterns

```mmd
# GOOD - Musical context clear
@loop 16 times every 1b
  - note_on 10.C1 100 0.5b
@end

# AVOID - Less readable for rhythmic content
@loop 16 times every 500ms
  - note_on 10.C1 100 250ms
@end
```

### 3. Combine Loops with Random Values

```mmd
@loop 16 times at [00:00.000] every 0.25b
  - note_on 10.F#2 random(60,90) 0.1b
@end
```

**Benefit:** Creates humanized, non-mechanical patterns.

### 4. Use Comments to Explain Loop Purpose

```mmd
# Verse drum pattern (16 bars)
@loop 64 times at [16.1.0] every 1b
  - note_on 10.C1 100 0.5b
@end
```

### 5. Keep Loop Bodies Simple

**GOOD:**
```mmd
@loop 4 times every 1b
  - note_on 10.C1 100 1b
@end
```

**AVOID (too complex):**
```mmd
@loop 4 times every 1b
  - note_on 10.C1 100 1b
  - cc 1.7.100
  [@]
  - cc 1.10.64
  [+0.5b]
  - note_on 10.D1 80 0.5b
  # ... 20 more commands
@end
```

**Better:** Break complex patterns into multiple loops or explicit timing.

### 6. Avoid Hardcoded Absolute Timing in Loops

**AVOID:**
```mmd
@loop 4 times every 1b
  [00:10.000]  # Don't do this - timing gets overwritten
  - note_on 10.C1 100 1b
@end
```

**Result:** Only the first iteration uses loop timing; subsequent iterations are unpredictable.

---

## Common Patterns

### Pattern 1: Basic Metronome

```mmd
@loop 64 times at [1.1.0] every 1b
  - note_on 10.C4 100 50ms
@end
```

### Pattern 2: Kick and Snare (4/4)

```mmd
# Kick on 1 and 3
@loop 16 times at [1.1.0] every 2b
  - note_on 10.C1 100 0.5b
@end

# Snare on 2 and 4
@loop 16 times at [1.2.0] every 2b
  - note_on 10.D1 90 0.5b
@end
```

### Pattern 3: Hi-Hat Groove (16th Notes)

```mmd
@loop 64 times at [1.1.0] every 0.25b
  - note_on 10.F#2 random(60,90) 0.1b
@end
```

### Pattern 4: Evolving Filter Automation

```mmd
@loop 32 times at [00:00.000] every 0.5b
  - cc 1.74.random(30,90)
@end
```

### Pattern 5: Arpeggio Pattern

```mmd
@loop 8 times at [1.1.0] every 0.25b
  - note_on 1.C4 80 0.2b
  [+0.25b]
  - note_on 1.E4 80 0.2b
  [+0.25b]
  - note_on 1.G4 80 0.2b
  [+0.25b]
  - note_on 1.C5 80 0.2b
@end
```

### Pattern 6: Section Markers

```mmd
@loop 4 times at [1.1.0] every 8.0.0
  - marker "Section"
@end
```

**Result:** Places markers at bars 1, 9, 17, 25.

---

## Troubleshooting

### Issue 1: Loop Starts at Wrong Time

**Symptom:**
```mmd
[00:10.000]
@loop 4 times at [00:00.000] every 1b
  - note_on 10.C1 100 1b
@end
```

Loop starts at 00:00.000 instead of 00:10.000.

**Cause:** Absolute timing `at [00:00.000]` overrides preceding marker.

**Fix:** Use relative timing or omit `at` clause:
```mmd
[00:10.000]
@loop 4 times every 1b
  - note_on 10.C1 100 1b
@end
```

### Issue 2: Timing Not Increasing

**Symptom:** Validation error about non-monotonic timing.

**Cause:** Loop interval is zero or negative.

**Fix:** Ensure `every <interval>` has a positive value:
```mmd
@loop 4 times every 1b  # GOOD
@loop 4 times every 0b  # BAD - zero interval
```

### Issue 3: Loop Doesn't Repeat Expected Number of Times

**Symptom:** Loop generates fewer events than expected.

**Cause:** Count is set incorrectly or loop body contains timing that conflicts with interval.

**Fix:** Verify count and avoid hardcoded timing markers inside loop body:
```mmd
@loop 4 times every 1b      # Will generate 4 iterations
  - note_on 10.C1 100 1b
@end
```

### Issue 4: Commands Inside Loop Execute at Same Time

**Symptom:** All commands in loop body execute simultaneously.

**Cause:** No relative timing between commands inside loop body.

**Fix:** Use `[@]` for simultaneous events or `[+duration]` for sequential timing:
```mmd
@loop 4 times every 1b
  - note_on 10.C1 100 0.1b
  [@]                        # Simultaneous with kick
  - note_on 10.D1 80 0.1b
@end
```

---

## See Also

- **[Timing System](../user-guide/timing-system.md)** - Complete timing system documentation
- **[Sweep Automation](sweep-automation.md)** - Automated parameter ramping with @sweep
- **[Examples: Loops and Patterns](https://github.com/cjgdev/midi-markdown/blob/main/examples/03_advanced/01_loops_and_patterns.mmd)** - Working loop examples
- **[Examples: Arpeggiator](https://github.com/cjgdev/midi-markdown/blob/main/examples/03_advanced/05_arpeggiator.mmd)** - Arpeggio patterns using loops
- **[Specification](https://github.com/cjgdev/midi-markdown/blob/main/spec.md#loops-and-patterns)** - Official language specification

---

**Document Version:** 1.0.0
**Last Updated:** 2025-11-11
**Status:** Stable (MVP Complete)
