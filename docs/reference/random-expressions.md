# Random Expressions Technical Reference

Complete API reference for `random()` expressions in MIDI Markdown (MMD). This document covers syntax, contexts, parameters, and implementation details for generating random values in MIDI sequences.

## Quick Reference / Cheat Sheet

```markdown
# Basic integer range (0-127)
random(min, max)
random(0, 127)

# Note name range
random(note1, note2)
random(C3, C5)

# With reproducible seed
random(min, max, seed=42)
random(C3, C5, seed=42)

# Supported contexts
note_on 1.random(60, 72) 80 1b          # Note number random
note_on 1.60 random(70, 90) 1b          # Velocity random
cc 1.7.random(0, 127)                   # CC value random
@loop 8 times - note_on 1.60 random(70, 90) 1b  # In loops
```

## Syntax Specification

### Basic Syntax

The `random()` function generates random values within a specified range. The syntax is:

```
random(min_value, max_value)
random(min_value, max_value, seed=integer)
```

### Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `min_value` | Integer or Note Name | Lower bound (inclusive) | `0`, `64`, `"C3"` |
| `max_value` | Integer or Note Name | Upper bound (inclusive) | `127`, `96`, `"C5"` |
| `seed` | Integer (optional) | Reproducibility seed | `42`, `123` |

### Return Value

Random integer within `[min_value, max_value]` inclusive. Value is selected uniformly from the range.

```
random(0, 127)      → Returns one of: 0, 1, 2, ..., 127 (128 possible values)
random(C3, C5)      → Returns MIDI note between 48-72 (25 possible values)
random(64, 96, seed=42)  → Always returns 81 (same seed = same value)
```

## Parameter Types and Ranges

### Integer Parameters

**Valid range**: 0-16383 (supports MIDI CC, velocity, pitch bend, and extended ranges)

```markdown
# Standard MIDI range (0-127)
random(0, 127)

# Velocity humanization (70-100)
random(70, 100)

# CC values (full range)
random(0, 127)

# Pitch bend (pitch bend extends to 16383)
random(0, 16383)
```

**Validation**:
- `min_value` must be ≤ `max_value`
- Non-integer values will be converted if possible
- Out-of-range values pass through to validator layer

### Note Name Parameters

**Supported notation**: Scientific pitch notation with optional accidentals

```markdown
# Natural notes
random(C3, C5)
random(A2, G7)

# With sharps
random(C#3, C#5)
random(F#4, F#6)

# With flats
random(Db3, Db5)
random(Bb2, Bb4)

# Enharmonic equivalents
random(C#4, E4)     # Same as: random(61, 76)
random(Db4, E4)     # Also: random(61, 76) - enharmonic
```

**MIDI note ranges** (for reference):
| Note Range | MIDI Values |
|-----------|-------------|
| C-2 to C8 | 0-127 (standard) |
| C0 to C8 | 12-132 (extended) |

### Seed Parameter

**Optional parameter** for reproducible randomness.

```markdown
# Same seed always produces same value
random(0, 127, seed=42)     → 81 (reproducible)
random(0, 127, seed=42)     → 81 (same seed, same value)
random(0, 127, seed=123)    → Different value

# Without seed, values vary
random(0, 127)              → Random value
random(0, 127)              → Different random value each call
```

**Seed types**:
- Positive integers: `seed=42`, `seed=1`, `seed=65535`
- Zero is valid: `seed=0`
- Negative integers: Accepted but converted by Python's `random.seed()`

## Supported Contexts (Where It Works)

### CC Value Context
Generate random MIDI CC values.

```markdown
[00:00.000]
- cc 1.7.random(0, 127)
```

**Valid**: CC number in data1 position, value in data2 position
```markdown
- cc CHANNEL.NUMBER.random(MIN, MAX)
```

### Note Velocity Context
Generate random velocity for notes.

```markdown
[00:00.000]
- note_on 1.60 random(70, 90) 1b
```

**Valid**: Velocity in data2 position
```markdown
- note_on CHANNEL.NOTE random(MIN, MAX) DURATION
```

### Note Number Context
Generate random note values.

```markdown
[00:00.000]
- note_on 1.random(60, 72) 80 1b
```

**Valid**: Note in data1 position (supports both numeric and name ranges)
```markdown
- note_on CHANNEL.random(MIN_NOTE, MAX_NOTE) VELOCITY DURATION
```

### Loop Contexts
Random works perfectly within `@loop` structures.

```markdown
@loop 8 times at [00:00.000] every 0.5b
  - cc 1.7.random(64, 96)
@end

@loop 16 times every 1b
  - note_on 1.random(C3, C5) random(70, 90) 0.25b
@end
```

**Behavior**: Each loop iteration generates a new random value (unless seed is fixed)

### Multiple Random in Single Command

Multiple random expressions can appear in a single command:

```markdown
[00:00.000]
- note_on 1.random(60, 72) random(70, 90) 1b
```

Each random() call generates independently.

## Unsupported Contexts (Where It Doesn't Work)

### Timing Values ❌

**INVALID**: Cannot use random in timing markers

```markdown
# WRONG - timing cannot be random
[00:random(00, 60).000]      ❌ Invalid
[random(0, 10):30.500]       ❌ Invalid
[random(1, 8).4.0]           ❌ Invalid
[+random(100, 500)ms]        ❌ Invalid
```

**Why**: Timing must be pre-calculated before MIDI event generation. Random values require expansion at event time, but timing needs to be fixed for proper sequencing.

**Workaround**: Use variables with loop intervals instead:
```markdown
@loop 5 times at [00:00.000] every random(0.5, 1.0)b
  - note_on 1.60 80 0.25b
@end
```

### Duration Tick Values ❌

**INVALID**: Cannot use random for note duration

```markdown
# WRONG - duration cannot be random
- note_on 1.60 80 random(0.5, 2.0)b   ❌ Invalid
- note_on 1.60 80 random(480, 960)t   ❌ Invalid
```

**Why**: Duration is part of the note timing specification. Timing constraints require fixed durations.

**Workaround**: Create separate note_on/note_off commands at known times:
```markdown
[00:00.000]
- note_on 1.60 80
[00:random(0.5, 1.5)s]        # Duration varies via timing gap
- note_off 1.60
```

### @define Values ❌

**INVALID**: Cannot use random in variable definitions

```markdown
# WRONG - @define cannot include random
@define MIN_VEL random(70, 90)    ❌ Invalid
@define RANDOM_CC random(0, 127)  ❌ Invalid
```

**Why**: Variable definitions are evaluated at parse time, before command expansion. Random expansion happens during event generation.

**Workaround**: Use random directly in command, not in variable:
```markdown
[00:00.000]
- note_on 1.60 random(70, 90) 1b   # OK - random evaluated at expansion time
```

### Numeric Note Values ❌

**INVALID**: Cannot use random in numeric note specification when number is in channel.note position

```markdown
# WRONG - numeric random in note position doesn't expand correctly
- note_on 10.random(36, 42) 80 1b        ❌ May fail to parse
- note_on {ch}.random(36, 48) 80 1b      ❌ In aliases, problematic
```

**Why**: Parser tries to interpret `10.random(...)` as channel + random expression, which conflicts with the dot-separated syntax.

**Workaround**: Use note names or put random elsewhere:
```markdown
# CORRECT - use note names
- note_on 1.random(C2, E2) 80 1b

# CORRECT - random in velocity instead
- note_on 1.36 random(70, 90) 1b
```

### Within Alias Parameters ❌

**INVALID**: Cannot use random directly as alias parameter value

```markdown
@alias my_note {ch}.{note} "Custom note"
  - note_on {ch}.{note} 80 1b
@end

# WRONG - random as parameter value
- my_note 1.random(C3, C5)    ❌ Invalid
```

**Why**: Alias parameters expect concrete values, not expressions. Random expansion happens after alias resolution.

**Workaround**: Use random in the expanded command, not the alias call:
```markdown
# CORRECT - random in the MMD command, not alias call
- note_on 1.random(C3, C5) 80 1b
```

## Context Compatibility Matrix

| Context | Supported | Notes |
|---------|-----------|-------|
| CC value (data2) | ✅ Yes | `cc 1.7.random(0, 127)` |
| Note velocity (data2) | ✅ Yes | `note_on 1.60 random(70, 90) 1b` |
| Note number (data1) | ✅ Yes | `note_on 1.random(C3, C5) 80 1b` |
| Pitch bend value | ✅ Yes | `pitch_bend 1.random(0, 16383)` |
| Pressure value | ✅ Yes | `pressure 1.random(0, 127)` |
| In @loop | ✅ Yes | Fresh random per iteration |
| In loop with seed | ✅ Yes | Same value per iteration if seed fixed |
| Timing markers | ❌ No | Cannot randomize timing |
| Note duration | ❌ No | Must be fixed |
| Variable definitions | ❌ No | Cannot use in @define |
| Alias parameters | ❌ No | Use in expanded command instead |

## Code Examples

### Example 1: Velocity Humanization

Add subtle randomness to note velocities for realistic feel:

```markdown
---
title: Humanized Drum Pattern
tempo: 120
---

[00:00.000]
@loop 32 times every 0.25b
  - note_on 1.36 random(65, 75) 0.1b   # Kick with velocity variation
@end

[00:08.000]
@loop 32 times every 0.25b
  - note_on 2.38 random(68, 78) 0.1b   # Snare with humanized dynamics
@end
```

### Example 2: Generative Melody

Create varied melodic patterns:

```markdown
@loop 16 times at [00:00.000] every 0.5b
  - note_on 1.random(C3, G3) random(70, 90) 0.25b
@end

@loop 16 times at [00:08.000] every 0.5b
  - note_on 1.random(C4, G4) random(75, 95) 0.25b
@end
```

### Example 3: CC Automation with Variation

Add randomness to filter or effect parameter automation:

```markdown
[00:00.000]
@loop 64 times every 0.5b
  - cc 1.74.random(20, 100)   # Filter cutoff with variation
@end

# Separate parallel automation
[00:00.000]
@loop 64 times every 0.5b
  - cc 1.11.random(80, 110)   # Expression pedal variation
@end
```

### Example 4: Reproducible Variations

Use seeds for consistent, repeatable randomness:

```markdown
# First pass (seed=42): Consistent random velocities
@loop 8 times - note_on 1.60 random(70, 90, seed=42) 0.5b
@end

# Later in song: Same seed = same pattern
[00:16.000]
@loop 8 times - note_on 1.64 random(70, 90, seed=42) 0.5b
@end
```

### Example 5: Combining with Device Aliases

Random within device-specific preset selection:

```markdown
@import "devices/quad_cortex.mmd"

[00:00.000]
# Random preset number (0-99)
- cortex_load 1.random(0, 5).random(0, 3).random(0, 8)

# Random effect parameter
[+1000ms]
- cc 1.71.random(0, 127)
```

## Implementation Details

### Architecture

Random expression handling is implemented across multiple layers:

**1. Parser Layer** (`src/midi_markdown/parser/`)
- Grammar recognizes `random(min, max)` and `random(min, max, seed=N)` syntax
- `RandomExpression` AST node created during parsing
- No expansion at parse time

**2. Expansion Layer** (`src/midi_markdown/expansion/random.py`)
- `RandomValueExpander` class handles expansion to concrete integers
- Called during event expansion after variable/loop expansion
- Supports both integer and note name parameters

**3. Validation Layer**
- Values are validated after random expansion
- Ensures generated values are within MIDI ranges

### Processing Pipeline

```
Input MMD (with random expressions)
    ↓
Parse → Create RandomExpression AST node
    ↓
Variable expansion (if @define)
    ↓
Loop expansion (create copies with new randoms)
    ↓
Random expansion → Expand RandomExpression to concrete integer
    ↓
Validation → Check value is in valid MIDI range
    ↓
MIDI event generation
    ↓
Output (MIDI file)
```

### RandomValueExpander Class

The core implementation:

```python
class RandomValueExpander:
    def expand_random(self, expr: RandomExpression) -> int:
        """Expand RandomExpression to integer value."""
        min_val = self._parse_value(expr.min_value)
        max_val = self._parse_value(expr.max_value)

        if min_val > max_val:
            raise ValueError("min > max")

        if expr.seed is not None:
            random.seed(expr.seed)

        return random.randint(min_val, max_val)

    def _parse_value(self, value: Any) -> int:
        """Convert note name or integer to MIDI value."""
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                return note_to_midi(value)
```

### Distribution and Seeding

**Distribution**: Uniform distribution via Python's `random.randint()`.

```python
# All values equally likely
random(0, 127)  → ~1/128 chance for each value
```

**Seeding**: Reproducible with `seed` parameter.

```python
# Same seed in sequence always produces same next value
random.seed(42)
random.randint(0, 127)  → 81
random.randint(0, 127)  → 60
random.randint(0, 127)  → 50

# Re-seed, same sequence
random.seed(42)
random.randint(0, 127)  → 81
random.randint(0, 127)  → 60
random.randint(0, 127)  → 50
```

## Edge Cases and Limitations

### Edge Case 1: Single-Value Range

When `min == max`, always returns that value:

```markdown
random(64, 64)      → Always 64
random(C4, C4)      → Always 60 (MIDI C4)
```

**Use case**: Can be used for explicit fixed values, though not recommended.

### Edge Case 2: Very Large Ranges

Supports full pitch bend range and beyond:

```markdown
random(0, 16383)    → Pitch bend full range (±8192 from center)
random(-8192, 8191) → Signed pitch bend range
```

### Edge Case 3: Note Name Boundary Cases

Edge cases in note name parsing:

```markdown
random(C-1, C8)     → Works (extended MIDI)
random(C0, C7)      → Works
random(C#3, C#3)    → Single note
```

### Limitation 1: No Weighted Distributions

Random is uniformly distributed. Cannot specify weighted or curved distributions.

```markdown
# NOT SUPPORTED - no way to bias towards center
random(C3, C5, distribution="normal")  ❌

# WORKAROUND - create custom loop pattern
@loop 10 times - note_on 1.C4 80 0.1b   # Center note often
@end
@loop 3 times - note_on 1.C3 80 0.1b    # Occasional low note
@end
```

### Limitation 2: Seed Scope

Seed affects global Python `random` state. Multiple random calls share state:

```markdown
[00:00.000]
- note_on 1.random(60, 72, seed=42) random(70, 90, seed=42) 1b

# Both use seed=42, so they're reproducible together
# But using seed in one place affects others
```

**Best practice**: Use seed only when you need deterministic output for specific features.

### Limitation 3: No Correlations

Each `random()` call is independent. Cannot specify that values should be related:

```markdown
# NOT SUPPORTED - no correlation between the two randoms
- note_on 1.random(60, 72) random(70, 100) 1b

# If you want correlated values, use variables (future feature)
# For now, accept independence or manually craft patterns
```

## Error Examples and Solutions

### Error 1: Min Greater Than Max

```markdown
# WRONG
- cc 1.7.random(100, 50)   ❌ ValueError: min > max

# CORRECT
- cc 1.7.random(50, 100)   ✅ OK
```

**Solution**: Swap min and max values.

### Error 2: Invalid Note Name

```markdown
# WRONG
- note_on 1.random(X3, C5) 80 1b   ❌ ValueError: Invalid note name 'X3'

# CORRECT
- note_on 1.random(C3, C5) 80 1b   ✅ OK
```

**Solution**: Use valid note names (A-G with optional # or b).

### Error 3: Type Mismatch in Parameters

```markdown
# WRONG - mixing note names and numbers
- note_on 1.random(C3, 72) 80 1b   ⚠️ May fail

# CORRECT - both note names
- note_on 1.random(C3, C5) 80 1b   ✅ OK

# CORRECT - both numbers
- note_on 1.random(48, 72) 80 1b   ✅ OK
```

**Solution**: Keep min/max parameters consistent (both notes or both integers).

### Error 4: Random in Timing (Common Mistake)

```markdown
# WRONG - timing cannot be random
[00:random(00, 60).000]
- note_on 1.60 80 1b

# ERROR: Timing must be fixed for proper sequencing

# CORRECT - use loop interval variation (future feature)
@loop 5 times at [00:00.000] every random(0.5, 1.0)b
  - note_on 1.60 80 0.25b
@end

# OR - vary with explicit timing
[00:00.000]
- note_on 1.60 80 0.25b
[00:00.500]
- note_on 1.62 80 0.25b
[00:01.250]
- note_on 1.64 80 0.25b
```

**Solution**: Use loop intervals or explicit timing instead.

### Error 5: Out of MIDI Range

```markdown
# WARNS - value may be outside MIDI range
- note_on 1.random(100, 200) 80 1b   ⚠️ 200 is out of MIDI range

# Actually expands to valid note, but validation will warn
# If critical, restrict range:

# CORRECT
- note_on 1.random(60, 127) 80 1b   ✅ Valid MIDI notes
```

**Solution**: Ensure min/max values are within valid MIDI ranges (0-127 typically).

### Error 6: Random in Alias Definition (Common Mistake)

```markdown
@alias humanized_note {ch}.{note}
  - note_on {ch}.{note} random(70, 90) 1b  # ✅ OK here
@end

# CORRECT - random in expanded command
- humanized_note 1.60

# WRONG - random as parameter
- humanized_note 1.random(60, 72)   ❌ Invalid
```

**Solution**: Put random in the alias definition body, not in parameter calls.

## Performance Considerations

### Overhead

Random expansion adds minimal overhead:
- Single `random.randint()` call per expression
- Note name parsing cached by `note_to_midi()` function
- Negligible impact on compilation time

### Loop Performance

Large loops with random expressions are efficient:

```markdown
# 1000 random values in a loop - still instant compilation
@loop 1000 times every 0.1b
  - cc 1.7.random(0, 127)
@end
```

### Seed Performance

Using seeds has no measurable performance difference:

```markdown
# No performance penalty for seeded randomness
random(0, 127, seed=42)  # Same speed as unseeded
```

## Related Features

### Variables (@define)

While `@define` cannot contain random expressions, variables can be used alongside random:

```markdown
@define CHANNEL 1
@define NOTE C4

[00:00.000]
- note_on ${CHANNEL}.${NOTE} random(70, 90) 1b
```

### Loops (@loop)

Random integrates seamlessly with loops:

```markdown
@loop 8 times every 0.5b
  - note_on 1.random(C3, C5) random(70, 90) 0.25b
@end
```

Each iteration gets fresh random values (unless seeded).

### Sweeps (@sweep)

Random can be used in sweep bodies:

```markdown
@sweep from [0.0.0] to [+1000ms] every 100ms
  - cc 1.7.random(60, 100)
@end
```

### Combining Random with Modulation

You can combine `random()` expressions with modulation features like curves, waves, and envelopes for even more expressive results:

**Random with Curves:**
```mmd
# Random velocity with smooth curve modulation
- note_on 1.C4 random(70,100) 1b
- cc 1.74.curve(random(30,60), random(80,110), ease-in-out)
```

**Random with Waves:**
```mmd
# Random LFO depth and frequency
- cc 1.1.wave(sine, random(40,80), freq=random(2.0,6.0), depth=random(20,60))
```

**Random with Envelopes:**
```mmd
# Random envelope parameters for variation
- cc 1.74.envelope(adsr, attack=random(0.1,0.5), decay=random(0.2,0.6), sustain=random(0.6,0.9), release=random(0.5,1.5))
```

These combinations are particularly useful for:
- Creating evolving pad textures
- Humanizing synthesized performances
- Generative ambient soundscapes
- Algorithmic composition with controlled randomness

See the [Generative Music Guide](../user-guide/generative-music.md) and [Modulation Guide](../user-guide/modulation.md) for more detailed examples.

## Testing

Comprehensive test suite for random expressions:

```bash
# Run all random-specific tests
just test -k "test_random"

# Unit tests (RandomValueExpander)
just test -k "TestRandomValueExpander"

# Integration tests (in loops and commands)
just test -k "TestRandomInLoops or TestRandomInCommands"

# Edge cases
just test -k "TestRandomEdgeCases"
```

Test coverage includes:
- Integer and note name generation
- Seed reproducibility
- Range validation
- Loop integration
- Command expansion
- Error handling

## Summary

Random expressions provide a powerful tool for:
- Humanizing MIDI sequences (velocity variation)
- Generative music (random melodies)
- Parameter automation variation
- Creating controlled randomness with seeds

Supported in note velocity, note number, and CC value contexts. Works seamlessly with loops. Not supported for timing, duration, or variable definitions. Use for generative and variation features, not for timing control.
