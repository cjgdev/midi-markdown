# Generative Music with Random Values

MIDI Markdown provides random value generation for creating evolving, humanized, and unpredictable musical sequences. The `random()` function generates different values each time a sequence is played, enabling techniques like **humanization** (subtle variations), **variation** (musical variety), and **generative patterns** (evolving compositions).

## Overview

Random expressions inject variation into MIDI sequences, perfect for:

```mml
# Humanized velocity variation
[00:00.000]
- note_on 1.60.random(70, 100) 4b

# Varying CC values for evolving pads
[00:02.000]
- cc 1.74.random(30, 90)

# Random notes for generative melodies
[00:04.000]
- note_on 1.random(C3, C5).80 1b
```

Random expressions complement deterministic modulation (curves, waves, envelopes) by adding controlled unpredictability to otherwise repetitive patterns.

---

## Random Value Basics

### Syntax

```mml
random(min_value, max_value [, seed=number])
```

### Parameters

- **min_value**: Minimum value (integer 0-127 or note name like C3)
- **max_value**: Maximum value (integer 0-127 or note name like C5)
- **seed** (optional): Reproducible randomness (same seed = same sequence)

### Return Type

Always returns an integer MIDI value (0-127 for CC/velocity, 0-127 for note numbers, 12-107 for typical playable notes).

### Examples

```mml
# Random CC value (0-127)
random(0, 127)

# Random velocity (70-100 for natural dynamics)
random(70, 100)

# Random note (C3 to C5, MIDI 48-72)
random(C3, C5)

# Reproducible random (always same sequence)
random(64, 96, seed=42)
```

---

## Where Random Works

### Velocity (Note Velocity)

Humanize note velocity for natural dynamics:

```mml
[00:00.000]
- note_on 1.60.random(60, 100) 1b

[00:01.000]
- note_on 1.64.random(60, 100) 1b

[00:02.000]
- note_on 1.67.random(60, 100) 1b
```

Each note gets a different random velocity, creating natural-sounding dynamics instead of uniform volumes.

### Note Ranges

Generate melodies with random note selection:

```mml
[00:00.000]
- note_on 1.random(C4, G4).80 1b

[00:01.000]
- note_on 1.random(C4, G4).80 1b

[00:02.000]
- note_on 1.random(C4, G4).80 1b
```

Each note is randomly selected from the C4-G4 range, creating unpredictable melodic variation.

### CC Values

Vary MIDI CC parameters (cutoff, resonance, pan, etc.):

```mml
[00:00.000]
- cc 1.74.random(20, 100)    # Random filter cutoff

[00:02.000]
- cc 1.71.random(30, 80)     # Random resonance

[00:04.000]
- cc 1.10.random(40, 90)     # Random pan position
```

Perfect for creating variation in filter settings, modulation depth, or any parameter that accepts 0-127.

---

## Where Random DOESN'T Work

### Timing and Durations

Random cannot be used for timing values:

```mml
# ❌ INVALID - random timing not supported
[+random(100ms, 500ms)]
- note_on 1.60.80 1b

# ❌ INVALID - random duration not supported
- note_on 1.60.80 random(1b, 2b)
```

**Reason**: Timing must be deterministic and monotonically increasing for proper MIDI sequencing. Use **loops** or **sweeps** for timed variations instead.

### Numeric Note IDs in Expressions

Random works with note names but not in all contexts:

```mml
# ✅ VALID - note name range
- note_on 1.random(C3, C5).80 1b

# ⚠️ CAUTION - only use integer ranges for direct numbers
- note_on 1.random(48, 72).80 1b   # Works but less readable

# ❌ INVALID - don't mix random with expressions
- note_on 1.(60 + random(0, 12)).80 1b   # Not supported in expressions
```

---

## Practical Techniques

### Humanization

Subtle variations make sequences sound less mechanical:

#### Dynamic Variation

```mml
# Humanize velocity across a drum pattern
[00:00.000]
- note_on 1.36.random(95, 127) 0.5b   # Kick (strong)
- cc 1.10.random(40, 60)               # Pan variation

[00:00.500]
- note_on 2.38.random(70, 90) 0.5b    # Snare (subtle)
- cc 2.10.random(40, 60)

[00:01.000]
- note_on 1.42.random(50, 70) 0.5b    # Hi-hat (light)
- cc 1.10.random(40, 60)
```

#### Timing Variations (Groove)

Use velocity variation to simulate timing micro-adjustments:

```mml
# Electric bass with subtle dynamics (humanized feel)
[00:00.000]
- note_on 1.36.random(70, 100) 0.5b

[00:00.500]
- note_on 1.41.random(70, 95) 0.5b

[00:01.000]
- note_on 1.43.random(75, 100) 0.5b
```

### Variation Techniques

#### Evolving Melodies

Generate different melodies each performance:

```mml
# Random arpeggio pattern
[00:00.000]
- note_on 1.random(C4, E4).random(60, 100) 0.5b

[00:00.500]
- note_on 1.random(E4, G4).random(60, 100) 0.5b

[00:01.000]
- note_on 1.random(G4, C5).random(60, 100) 0.5b

[00:01.500]
- note_on 1.random(C4, E4).random(60, 100) 0.5b
```

#### Random Control Changes

Vary filter, reverb, or effect parameters:

```mml
# Evolving filter with random CC value
[00:00.000]
- cc 1.74.random(30, 70)

[00:02.000]
- cc 1.74.random(40, 80)

[00:04.000]
- cc 1.74.random(50, 90)

[00:06.000]
- cc 1.74.random(60, 100)
```

### Generative Patterns

Combine random with loops for procedural generation:

```mml
# Generative bass line (different each loop)
@loop 4
  [+1b]
  - note_on 1.random(24, 36).random(90, 127) 0.5b
@end

# Generative arpeggio (varying note range)
@loop 8
  [+0.5b]
  - note_on 1.random(C3, C5).random(70, 100) 0.5b
@end
```

---

## Combining Random with Modulation

Random adds unpredictability to otherwise smooth modulation. Use together for complex effects:

### Random Modulation Base

Start modulation from a random value:

```mml
# Filter cutoff starts random, then modulates smoothly
[00:00.000]
- cc 1.74.curve(random(20, 50), 120, ease-in-out)

# Volume swell with random starting point
[00:02.000]
- cc 1.7.curve(random(20, 40), 127, ease-out)
```

### Random Depth with Waveforms

Combine random depth with periodic modulation:

```mml
# Random depth LFO (varying intensity)
[00:00.000]
- cc 1.74.wave(sine, 64, freq=2.0, depth=random(10, 40))

# Random frequency with fixed depth (varying speed)
[00:02.000]
- cc 1.7.wave(triangle, 80, freq=random(0.5, 3.0), depth=25)
```

### Random Envelope Parameters

Create variation in envelope shape:

```mml
# Varying attack time with random envelope
[00:00.000]
- note_on 1.60.80 2b
- cc 1.74.envelope(ar, attack=random(0.1, 0.5), release=0.5)

# Varying release time
[00:02.000]
- note_on 1.64.80 2b
- cc 1.74.envelope(ar, attack=0.2, release=random(0.3, 1.5))
```

### Stereo Randomization

Random pan and width for stereo effects:

```mml
# Random pan with wave modulation
[00:00.000]
[@]
- cc 1.10.wave(sine, random(30, 90), freq=1.5, depth=20)
[@]
- cc 2.10.wave(sine, random(30, 90), freq=1.5, phase=0.5, depth=20)
```

---

## Reproducibility with Seeds

### Deterministic Randomness

Use `seed` parameter for reproducible sequences:

```mml
# Same seed = same random values each time
[00:00.000]
- note_on 1.60.random(60, 100, seed=42) 1b
- cc 1.74.random(30, 100, seed=42)

[00:01.000]
- note_on 1.64.random(60, 100, seed=42) 1b
- cc 1.74.random(30, 100, seed=42)
```

### Using Seeds Strategically

```mml
# Different seeds for different sections
@loop 4
  [+4b]
  # Verse uses seed 1 (fixed variation)
  - note_on 1.random(C3, G3).random(70, 100, seed=1) 1b
@end

@loop 4
  [+4b]
  # Chorus uses seed 2 (different fixed variation)
  - note_on 1.random(C4, G4).random(70, 100, seed=2) 1b
@end
```

**Without seeds**: Random values change every time you play.

**With seeds**: Same sequence reproducible across performances (useful for testing, demos, or consistent variations).

---

## Best Practices

### Range Selection

| Purpose | Min-Max | Notes |
|---------|---------|-------|
| Subtle humanization | ±5-10% of normal value | Feels natural, less noticeable |
| Moderate variation | ±15-25% range | Obvious but still musical |
| Strong variation | ±40-50% range | Dramatic, noticeable effect |
| Extreme variation | Full range (0-127) | Chaotic, use sparingly |

### Velocity Humanization Guidelines

```mml
# For notes that should be strong
random(80, 127)

# For notes that should be moderate
random(60, 100)

# For light notes (hi-hats, rolls)
random(40, 80)

# For very subtle variation
random(88, 100)
```

### When to Use Random vs. Modulation

| Situation | Use Random | Use Modulation |
|-----------|-----------|-----------------|
| One-time variation | ✅ | ❌ |
| Humanization | ✅ | ❌ |
| Periodic changes | ❌ | ✅ |
| Smooth transitions | ❌ | ✅ |
| Evolving effects | ✅ | ✅ (both) |
| Generative patterns | ✅ | ✅ (both) |

### Common Pitfalls

❌ **Don't use random for timing** - Causes sequencing issues (use loops instead)

❌ **Don't randomize every parameter** - Creates chaos, loses musicality

❌ **Don't use extreme ranges for velocity** - Unnatural dynamics (stay in musical range)

❌ **Don't combine too many randoms** - Multiple random sources can conflict

✅ **DO use seeds for testing** - Reproducibility helps debugging

✅ **DO layer random with structure** - Combine with loops and patterns

✅ **DO start subtle** - Increase variation gradually until musical

---

## Advanced Techniques

### Generative Polyrhythms

Stack loops with different random patterns:

```mml
# Generative polyrhythm with multiple random sources
@loop 8
  [+1.5b]
  - note_on 1.random(C4, E4).random(70, 100) 0.5b
@end

@loop 6
  [+2b]
  - note_on 2.random(F3, A3).random(80, 110) 0.5b
@end
```

### Evolving Pad with Random Modulation

```mml
# Pad evolves with both random base and wave modulation
[00:00.000]
- note_on 1.48.80 16b
- cc 1.74.wave(sine, random(40, 80), freq=0.3, depth=30)

[00:08.000]
- cc 1.71.curve(random(20, 40), 80, ease-in-out)
```

### Humanized Drum Loop

```mml
@define kick_pattern
  [00:00.000]
  - note_on 1.36.random(95, 127) 0.5b
  - cc 1.10.random(45, 55)

  [00:02.000]
  - note_on 1.36.random(85, 110) 0.5b
  - cc 1.10.random(45, 55)
@end

@loop 4
  [+4b]
  @kick_pattern
@end
```

### Random Sweep Depths

Combine random with multiple modulation types:

```mml
# Filter cutoff with random envelope and wave
[00:00.000]
- note_on 1.60.80 4b
[@]
- cc 1.74.curve(random(30, 50), 110, ease-out)
[@]
- cc 1.71.wave(sine, random(30, 70), freq=1.0, depth=20)
```

---

## Performance Considerations

### Random Distribution

- `random(min, max)` uses uniform distribution (all values equally likely)
- Generated values are truly random (not pseudo-random seeded by default)
- With `seed=N`, sequences are reproducible across runs

### CPU Impact

- Each `random()` call is very fast (<1ms)
- Multiple random calls in same event have minimal impact
- Safe to use in loops without performance concerns

### Variation Quantity

```mml
# Moderate randomness (musical)
@loop 100
  [+0.25b]
  - note_on 1.60.random(75, 85) 0.25b   # 10-value range
@end

# Extreme randomness (less musical but possible)
@loop 100
  [+0.25b]
  - note_on 1.random(C0, C8).random(0, 127) 0.25b   # Full chaos
@end
```

---

## Comparison: Random vs. Deterministic

### Without Random (Mechanical)

```mml
@loop 8
  [+0.5b]
  - note_on 1.60.80 0.5b   # Same every time
  - cc 1.74.70             # Same every time
@end
```

Result: Identical every performance, lacks humanization.

### With Random (Natural)

```mml
@loop 8
  [+0.5b]
  - note_on 1.60.random(70, 100) 0.5b   # Different velocity
  - cc 1.74.random(60, 80)               # Different filter
@end
```

Result: Natural variation, different each performance.

### With Seeds (Reproducible Random)

```mml
@loop 8
  [+0.5b]
  - note_on 1.60.random(70, 100, seed=1) 0.5b   # Reproducible
  - cc 1.74.random(60, 80, seed=1)               # Reproducible
@end
```

Result: Same variation every performance (controlled randomness).

---

## Integration Examples

### Humanized Synth Line

```mml
---
tempo: 120
time_signature: 4/4
---

[00:00.000]
- note_on 1.60.random(75, 95) 1b
- cc 1.74.curve(random(40, 60), 80, ease-out)

[00:01.000]
- note_on 1.62.random(75, 95) 1b
- cc 1.74.curve(random(45, 65), 80, ease-out)

[00:02.000]
- note_on 1.65.random(75, 95) 1b
- cc 1.74.curve(random(50, 70), 80, ease-out)

[00:03.000]
- note_on 1.67.random(75, 95) 1b
- cc 1.74.curve(random(55, 75), 80, ease-out)
```

### Generative Ambient Pad

```mml
---
tempo: 60
---

# Base pad with evolving filter
[00:00.000]
- note_on 1.48.60 120b
- cc 1.74.wave(sine, random(50, 70), freq=0.2, depth=40)

# Add resonance variation
[00:04.000]
- cc 1.71.curve(random(20, 40), random(60, 80), ease-in-out)

# Auto-pan with random center
[00:08.000]
- cc 1.10.wave(sine, random(30, 90), freq=0.5, depth=50)
```

### Percussive Loop with Humanization

```mml
@loop 4
  # Kick with humanized velocity and filter variation
  [00:00.000]
  - note_on 1.36.random(100, 127) 0.5b
  - cc 1.74.random(80, 127)

  # Snare with velocity variation
  [00:02.000]
  - note_on 2.38.random(80, 100) 0.5b

  # Hi-hat with varying pan
  [00:02.500]
  - note_on 1.42.random(60, 80) 0.25b
  - cc 1.10.random(40, 90)
@end
```

---

## Troubleshooting

### Random values seem the same

**Issue**: Using `random(min, max)` without seed can sometimes appear repetitive due to random variation.

**Solution**: Use `seed=N` if you need consistent variation testing, or accept the natural randomness.

### Range is too wide

**Issue**: `random(0, 127)` for velocity sounds unnatural (jumps between ppp and fff).

**Solution**: Use narrower ranges like `random(70, 90)` for more subtle, musical variation.

### Random notes are out of key

**Issue**: `random(C0, C8)` generates unwanted low/high notes.

**Solution**: Specify exact range: `random(C3, C5)` or `random(48, 72)`.

### Can't use random in timing

**Issue**: Trying `[+random(100ms, 500ms)]` causes error.

**Solution**: Use loops with fixed timing instead. Random timing is not supported for sequencing safety.

---

## See Also

- [Modulation Guide](modulation.md) - Curves, waves, and envelopes for smooth automation
- [MIDI Commands Reference](midi-commands.md) - Available CC numbers for variation
- [MML Syntax](mmd-syntax.md) - Core syntax and language features
- [Timing System](timing-system.md) - Timing patterns with variation

### Complete Working Examples

Six comprehensive examples demonstrating all random() techniques:

- [01_random_humanization.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/05_generative/01_random_humanization.mmd) - Velocity, note, and CC humanization
- [02_algorithmic_drums.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/05_generative/02_algorithmic_drums.mmd) - Professional drum pattern generation
- [03_generative_ambient.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/05_generative/03_generative_ambient.mmd) - Evolving pad textures with random notes and LFO
- [04_random_cc_automation.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/05_generative/04_random_cc_automation.mmd) - Generative parameter automation
- [05_evolving_textures.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/05_generative/05_evolving_textures.mmd) - Complex layered textures with multiple randomization sources
- [06_scale_constrained_melody.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/05_generative/06_scale_constrained_melody.mmd) - Generative melodies constrained to musical scales

See [Examples Guide](../getting-started/examples-guide.md#categories) for learning paths and feature matrix.

---

## Reference

### Random Syntax Summary

```mml
# Integer range
random(0, 127)
random(64, 96)

# Note name range
random(C3, C5)
random(C#4, E5)
random(Bb3, G4)

# With reproducible seed
random(70, 100, seed=42)
random(C4, G4, seed=1)

# In context
- note_on {ch}.random(C3, C5).{velocity} 1b
- cc {ch}.{number}.random(30, 100)
- note_on {ch}.{note}.random(60, 100) 0.5b
```

### Supported Contexts

| Context | Example | Status |
|---------|---------|--------|
| Velocity | `note_on 1.60.random(70, 100) 1b` | ✅ Works |
| Note | `note_on 1.random(C3, C5).80 1b` | ✅ Works |
| CC Value | `cc 1.74.random(30, 100)` | ✅ Works |
| Pitch Bend | `pitch_bend 1.random(0, 16384)` | ✅ Works |
| Timing | `[+random(100ms, 500ms)]` | ❌ Not Supported |
| Duration | `note_on 1.60.80 random(1b, 4b)` | ❌ Not Supported |
