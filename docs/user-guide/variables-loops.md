# Variables and Loops User Guide

This guide covers two powerful MMD features that help you write more maintainable and efficient MIDI automation: **variables** for reusable values and **loops** for repeating patterns.

## Table of Contents

1. [Variables](#variables)
   - [Defining Variables](#defining-variables)
   - [Using Variables](#using-variables)
   - [Variable Expressions](#variable-expressions)
   - [Variable Scope](#variable-scope)
2. [Loops](#loops)
   - [Basic Loop Syntax](#basic-loop-syntax)
   - [Loop Timing](#loop-timing)
   - [Multi-Command Loops](#multi-command-loops)
   - [Loop Variables](#loop-variables)
3. [Combining Variables and Loops](#combining-variables-and-loops)
4. [Practical Examples](#practical-examples)
5. [Best Practices](#best-practices)
6. [Reference](#reference)

---

## Variables

Variables let you define reusable values once and reference them throughout your MMD file. This makes your automation easier to maintain and modify.

### Defining Variables

Use the `@define` directive to create variables:

```mml
@define VARIABLE_NAME value
```

**Examples:**

```mml
# Numeric values
@define MAIN_CHANNEL 1
@define VERSE_PRESET 10
@define CHORUS_PRESET 15

# Tempo values
@define INTRO_TEMPO 90
@define SONG_TEMPO 120
@define OUTRO_TEMPO 100

# MIDI CC values
@define FILTER_OPEN 127
@define FILTER_CLOSED 20
@define VOLUME_MAX 100
```

### Using Variables

Reference variables using the `${VARIABLE_NAME}` syntax:

```mml
@define MAIN_CHANNEL 1
@define VERSE_PRESET 10

[00:00.000]
- pc ${MAIN_CHANNEL}.${VERSE_PRESET}  # Expands to: pc 1.10
- tempo ${SONG_TEMPO}                  # Expands to: tempo 120
- cc ${MAIN_CHANNEL}.7.${VOLUME_MAX}  # Expands to: cc 1.7.100
```

**Variables work in all command contexts:**

```mml
@define CH 1
@define NOTE 60
@define VEL 80
@define DUR 1b

[00:00.000]
- note_on ${CH}.${NOTE} ${VEL} ${DUR}
- cc ${CH}.74.64
- pc ${CH}.5
```

### Variable Expressions

Variables can contain computed expressions using arithmetic operators:

**Supported Operators:**
- Addition: `+`
- Subtraction: `-`
- Multiplication: `*`
- Division: `/`
- Modulo: `%`
- Parentheses: `(` `)`

**Examples:**

```mml
@define BASE_PRESET 10
@define NEXT_PRESET ${BASE_PRESET} + 1      # 11
@define PREV_PRESET ${BASE_PRESET} - 1      # 9
@define DOUBLE_PRESET ${BASE_PRESET} * 2    # 20
@define HALF_TEMPO ${SONG_TEMPO} / 2        # 60

# Complex expressions
@define SCALED_VALUE (${BASE_VALUE} * 1.5) + 10
@define CHANNEL_OFFSET ${BASE_CHANNEL} + (${SECTION} * 4)
```

**Variable References in Expressions:**

```mml
@define INTRO_TEMPO 90
@define VERSE_TEMPO 120
@define BRIDGE_TEMPO ${INTRO_TEMPO} + 10    # 100
@define CHORUS_TEMPO ${VERSE_TEMPO} + 8     # 128
```

### Variable Scope

Variables are **global** within a file and can be referenced anywhere after definition:

```mml
---
title: "Variable Scope Example"
---

@define MAIN_CHANNEL 1

[00:00.000]
- pc ${MAIN_CHANNEL}.1  # ✅ Works - defined above

@define VERSE_PRESET 10

[00:05.000]
- pc ${MAIN_CHANNEL}.${VERSE_PRESET}  # ✅ Works - both defined

@define CHORUS_PRESET ${VERSE_PRESET} + 5

[00:10.000]
- pc ${MAIN_CHANNEL}.${CHORUS_PRESET}  # ✅ Works - expands to 15
```

**Best Practice:** Define all variables at the top of your file for clarity:

```mml
---
title: "My Song"
---

# ============================================
# Global Variables
# ============================================

@define MAIN_CHANNEL 1
@define INTRO_TEMPO 90
@define VERSE_PRESET 10
@define CHORUS_PRESET 15

# ============================================
# Song Content
# ============================================

[00:00.000]
- tempo ${INTRO_TEMPO}
- pc ${MAIN_CHANNEL}.${VERSE_PRESET}
```

---

## Loops

The `@loop` directive eliminates repetitive code by repeating command sequences automatically.

### Basic Loop Syntax

```mml
@loop N times every DURATION
  - commands to repeat
@end
```

**Components:**
- **N times** - Number of iterations (integer)
- **every DURATION** - Time interval between iterations
- **commands** - One or more MIDI commands to repeat
- **@end** - Closes the loop block

**Simple Example:**

```mml
# Manual repetition (tedious)
[00:00.000]
- note_on 1.42 100 0.1s
[00:00.500]
- note_on 1.42 100 0.1s
[00:01.000]
- note_on 1.42 100 0.1s
# ... repeat 13 more times

# With @loop (concise)
[00:00.000]
@loop 16 times every 0.5s
  - note_on 1.42 100 0.1s
@end
```

### Loop Timing

Loops support all MMD timing units:

#### Beat-Based Timing

```mml
# Every quarter note (1 beat)
@loop 16 times every 1b
  - note_on 1.42 100 0.1s
@end

# Every eighth note (0.5 beats)
@loop 32 times every 0.5b
  - note_on 1.60 80 0.25b
@end

# Every sixteenth note (0.25 beats)
@loop 64 times every 0.25b
  - note_on 1.F#2 60 0.1b
@end
```

#### Time-Based Timing

```mml
# Every second
@loop 10 times every 1s
  - cc 1.7.100
@end

# Every 500 milliseconds
@loop 20 times every 500ms
  - note_on 1.C4 80 100ms
@end

# Every 250ms
@loop 40 times every 250ms
  - note_on 10.F#2 70 50ms  # Hi-hat
@end
```

#### Tick-Based Timing

```mml
# Every 240 ticks (at PPQ=480, this is 1 eighth note)
@loop 16 times every 240t
  - note_on 1.60 80 200t
@end

# Every 120 ticks (sixteenth note at PPQ=480)
@loop 32 times every 120t
  - note_on 1.42 70 100t
@end
```

#### Musical Time (Bars.Beats.Ticks)

```mml
# Every bar (4/4 time)
@loop 8 times every 1.0.0
  - marker "Bar ${LOOP_ITERATION}"
@end

# Every 2 bars
@loop 4 times every 2.0.0
  - pc 1.${LOOP_ITERATION}
@end

# Every half bar (2 beats in 4/4)
@loop 16 times every 0.2.0
  - note_on 1.36 100 0.45b  # Kick
@end
```

### Multi-Command Loops

Loops can contain multiple commands that execute together each iteration:

```mml
# Kick and snare pattern
@loop 8 times every 4b
  # Kick on beat 1
  - note_on 10.36 100 0.25b

  # Snare on beat 3
  [+2b]
  - note_on 10.38 90 0.25b
@end
```

**With Simultaneous Events:**

```mml
@loop 4 times every 4b
  # Play chord (3 notes simultaneously)
  - note_on 1.C4 80 4b
  [@]
  - note_on 1.E4 80 4b
  [@]
  - note_on 1.G4 80 4b
@end
```

**With Relative Timing:**

```mml
@loop 16 times every 1b
  # Hi-hat on every beat
  - note_on 10.42 70 0.1b

  # Ghost note on offbeat (half beat later)
  [+0.5b]
  - note_on 10.42 40 0.1b
@end
```

### Loop Variables

Loops automatically provide built-in variables for iteration tracking:

**Available Loop Variables:**
- `${LOOP_INDEX}` - Current iteration (0-indexed: 0, 1, 2, ...)
- `${LOOP_ITERATION}` - Current iteration (1-indexed: 1, 2, 3, ...)
- `${LOOP_COUNT}` - Total number of iterations

**Examples:**

```mml
# Section markers every 4 bars
@loop 8 times every 4.0.0
  - marker "Section ${LOOP_ITERATION}"
@end
# Generates: "Section 1", "Section 2", ..., "Section 8"

# Incremental preset loading
@loop 10 times every 5s
  - pc 1.${LOOP_INDEX}
  - text "Loading preset ${LOOP_ITERATION} of ${LOOP_COUNT}"
@end
# Loads presets 0-9 with status messages

# Velocity ramp (fade in)
@loop 8 times every 1b
  - note_on 1.60 ${LOOP_INDEX * 16} 0.9b
@end
# Velocities: 0, 16, 32, 48, 64, 80, 96, 112
```

---

## Combining Variables and Loops

Variables and loops work together for maximum flexibility:

### Variables Control Loop Parameters

```mml
@define PATTERN_LENGTH 16
@define BEAT_INTERVAL 0.5b

@loop ${PATTERN_LENGTH} times every ${BEAT_INTERVAL}
  - note_on 1.60 80 0.25b
@end
```

### Loop Variables with Computed Expressions

```mml
@define BASE_NOTE 60
@define OCTAVE_OFFSET 12

@loop 8 times every 1b
  # Ascending melody
  - note_on 1.${BASE_NOTE + LOOP_INDEX} 80 0.9b
@end
# Plays: C4, C#4, D4, D#4, E4, F4, F#4, G4

@loop 4 times every 4b
  # Octave jumps
  - note_on 1.${BASE_NOTE + (LOOP_ITERATION * OCTAVE_OFFSET)} 90 3.5b
@end
# Plays: C4 (60), C5 (72), C6 (84), C7 (96)
```

### Multiple Loops with Shared Variables

```mml
@define DRUM_CHANNEL 10
@define BAR_COUNT 8

# Kick drum every bar
@loop ${BAR_COUNT} times every 4b
  - note_on ${DRUM_CHANNEL}.36 100 0.25b
@end

# Hi-hat every beat (4x as many iterations)
@loop ${BAR_COUNT * 4} times every 1b
  - note_on ${DRUM_CHANNEL}.42 70 0.1b
@end
```

---

## Practical Examples

### Example 1: Click Track with Markers

```mml
---
title: "Click Track"
tempo: 120
time_signature: [4, 4]
ppq: 480
---

@define TOTAL_BARS 16

[00:00.000]
- marker "Click Track Start"

# Bar markers
@loop ${TOTAL_BARS} times every 4b
  - marker "Bar ${LOOP_ITERATION}"
@end

# Click every beat
@loop ${TOTAL_BARS * 4} times every 1b
  - note_on 1.42 100 0.1s
@end
```

### Example 2: Arpeggiator Pattern

```mml
---
title: "Arpeggiator"
tempo: 128
---

@define BASE_NOTE 60     # C4
@define PATTERN_LENGTH 16
@define NOTE_INTERVAL 0.25b

[00:00.000]
- marker "C Major Arpeggio"

@loop ${PATTERN_LENGTH} times every ${NOTE_INTERVAL}
  - note_on 1.${BASE_NOTE + (LOOP_INDEX % 4) * 4} 80 0.2b
@end
# Pattern: C, E, G, C, C, E, G, C, ...
```

**Explanation:**
- `LOOP_INDEX % 4` cycles through 0, 1, 2, 3
- Multiply by 4 semitones: 0, 4, 7, 12 (C major arpeggio)
- Add to BASE_NOTE (60) for final notes

### Example 3: Volume Automation with Loops

```mml
---
title: "Volume Fade"
tempo: 120
---

@define FADE_STEPS 16
@define FADE_INTERVAL 250ms
@define START_VOLUME 0
@define END_VOLUME 100

[00:00.000]
- marker "Fade In"

@loop ${FADE_STEPS} times every ${FADE_INTERVAL}
  - cc 1.7.${START_VOLUME + (LOOP_INDEX * ((END_VOLUME - START_VOLUME) / (FADE_STEPS - 1)))}
@end
# Volume ramps from 0 to 100 over 4 seconds (16 steps * 250ms)
```

### Example 4: Polyrhythmic Drum Pattern

```mml
---
title: "Polyrhythm"
tempo: 120
---

@define DRUM_CH 10
@define PATTERN_BARS 8

[00:00.000]
- marker "Polyrhythm Start"

# Kick: every 4 beats (quarter note)
@loop ${PATTERN_BARS * 4} times every 1b
  - note_on ${DRUM_CH}.36 100 0.25b
@end

# Snare: every 3 beats (triplet feel)
@loop ${PATTERN_BARS * 5} times every 0.75b
  - note_on ${DRUM_CH}.38 85 0.2b
@end

# Hi-hat: every 2 beats (eighth notes)
@loop ${PATTERN_BARS * 8} times every 0.5b
  - note_on ${DRUM_CH}.42 70 0.1b
@end
```

### Example 5: Live Performance Setlist

```mml
---
title: "Live Setlist Automation"
---

@define CORTEX_CH 1
@define SONG_COUNT 10
@define SONG_LENGTH 300s  # 5 minutes per song

# Load presets for each song
@loop ${SONG_COUNT} times every ${SONG_LENGTH}
  - marker "Song ${LOOP_ITERATION}"
  - pc ${CORTEX_CH}.${LOOP_INDEX}
  - text "Now playing: Song ${LOOP_ITERATION} of ${SONG_COUNT}"
@end
```

---

## Best Practices

### Variables

✅ **DO:**
- Define variables at the top of your file
- Use UPPERCASE names for constants
- Group related variables together
- Add comments explaining complex calculations
- Use descriptive names (not `A`, `B`, `C`)

```mml
# ✅ GOOD
@define MAIN_CHANNEL 1
@define VERSE_PRESET 10
@define INTRO_TEMPO 90

# ❌ BAD
@define A 1
@define B 10
@define C 90
```

❌ **DON'T:**
- Redefine variables (first definition wins)
- Use variables before defining them
- Create circular dependencies

```mml
# ❌ BAD - circular reference
@define X ${Y} + 1
@define Y ${X} + 1
```

### Loops

✅ **DO:**
- Use loops for repetitive patterns (3+ repetitions)
- Choose appropriate timing units (beats for musical, ms for precise)
- Add markers inside loops for section tracking
- Use loop variables for incremental changes

```mml
# ✅ GOOD - 16 iterations, clear intent
@loop 16 times every 1b
  - note_on 1.42 100 0.1s
@end

# ✅ GOOD - loop variable for progression
@loop 8 times every 4b
  - marker "Bar ${LOOP_ITERATION}"
  - pc 1.${LOOP_INDEX}
@end
```

❌ **DON'T:**
- Use loops for 1-2 repetitions (not worth it)
- Nest loops deeply (hard to read)
- Create loops with 0 iterations

```mml
# ❌ BAD - just write it twice
@loop 2 times every 1b
  - note_on 1.60 80 0.5b
@end

# ❌ BAD - deeply nested, confusing
@loop 4 times every 4b
  @loop 4 times every 1b
    @loop 4 times every 0.25b
      - note_on 1.60 80 0.1b
    @end
  @end
@end
```

### Combining Variables and Loops

✅ **DO:**
- Use variables to make loops configurable
- Leverage loop variables for mathematical progressions
- Comment complex expressions

```mml
# ✅ GOOD - configurable pattern
@define PATTERN_REPEATS 8
@define BASE_NOTE 60

@loop ${PATTERN_REPEATS} times every 1b
  # Ascending scale: C, D, E, F, G, A, B, C
  - note_on 1.${BASE_NOTE + LOOP_INDEX * 2} 80 0.9b
@end
```

---

## Reference

### @define Directive

**Syntax:**
```mml
@define VARIABLE_NAME value
@define VARIABLE_NAME ${expression}
```

**Examples:**
```mml
@define CHANNEL 1
@define PRESET 10
@define CALCULATED ${PRESET * 2}
```

**Operators:** `+`, `-`, `*`, `/`, `%`, `(`, `)`

### Variable Substitution

**Syntax:**
```mml
${VARIABLE_NAME}
```

**Context:** Works in all command parameters (channel, note, velocity, CC values, etc.)

### @loop Directive

**Syntax:**
```mml
@loop N times every DURATION
  - commands
@end
```

**Duration Units:**
- Beats: `1b`, `0.5b`, `2.5b`
- Milliseconds: `500ms`, `1000ms`
- Seconds: `1s`, `2.5s`
- Ticks: `240t`, `120t`
- Musical time: `1.0.0`, `0.2.0`

**Loop Variables:**
- `${LOOP_INDEX}` - 0-indexed (0, 1, 2, ...)
- `${LOOP_ITERATION}` - 1-indexed (1, 2, 3, ...)
- `${LOOP_COUNT}` - Total iterations

### Complete Syntax Example

```mml
---
title: "Variables and Loops Reference"
tempo: 120
---

# Variables
@define CHANNEL 1
@define BASE_NOTE 60
@define VELOCITY 80
@define PATTERN_COUNT 8
@define INTERVAL 1b

# Loop with variables
@loop ${PATTERN_COUNT} times every ${INTERVAL}
  - note_on ${CHANNEL}.${BASE_NOTE + LOOP_INDEX} ${VELOCITY} 0.9b
  - text "Note ${LOOP_ITERATION} of ${LOOP_COUNT}"
@end
```

---

## See Also

### User Guides
- [MML Syntax Reference](mmd-syntax.md) - Complete syntax documentation
- [Timing System](timing-system.md) - All timing paradigms explained
- [Generative Music](generative-music.md) - Random values and modulation
- [Device Libraries](device-libraries.md) - High-level device control

### Examples
- [01_loops_and_patterns.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/03_advanced/01_loops_and_patterns.mmd) - Loop demonstrations
- [variables_basic.mmd](https://github.com/cjgdev/midi-markdown/blob/main/tests/fixtures/variables_basic.mmd) - Variable examples
- [05_arpeggiator.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/03_advanced/05_arpeggiator.mmd) - Variables + loops for arpeggios
- [06_polyrhythm.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/03_advanced/06_polyrhythm.mmd) - Multiple loops in polyrhythm

### Specification
- [Complete MMD Specification](https://github.com/cjgdev/midi-markdown/blob/main/spec.md#variables-and-expressions) - Variables section
- [Complete MMD Specification](https://github.com/cjgdev/midi-markdown/blob/main/spec.md#loops-and-patterns) - Loops section

---

**Questions or Issues?** See [GitHub Issues](https://github.com/cjgdev/midi-markdown/issues)
