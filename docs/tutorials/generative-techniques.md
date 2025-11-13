# Generative Techniques in MML
## A Step-by-Step Tutorial

Creating music with procedural and algorithmic techniques is a powerful way to explore new sonic possibilities while minimizing repetitive coding. This tutorial walks you through increasingly sophisticated generative music techniques using MML's `random()` expressions, loops, and other tools.

### What is Generative Music?

Generative music uses algorithms and randomness to create variations of musical patterns automatically. Rather than manually writing every note, you define rules and let the system generate them. This is useful for:

- **Humanization**: Adding natural variations to robotic MIDI patterns
- **Exploration**: Discovering new melodies and rhythms through algorithmic variation
- **Efficiency**: Creating complex polyrhythmic and layered patterns with minimal code
- **Live Performance**: Generating fresh variations in real-time during performances
- **Ambient Music**: Creating evolving soundscapes that never repeat exactly

The key insight is that **controlled randomness within boundaries** creates musicality, while pure randomness creates chaos. Throughout this tutorial, we'll learn to control randomness to stay musical.

---

## Lesson 1: Your First Random Pattern - Simple Velocity Variation

**Learning Objective**: Understand how to use the `random()` function to add human-like dynamics to static patterns.

### The Problem

When you write the same velocity over and over, MIDI sounds robotic:

```markdown
[00:00.000]
- note_on 1.C4 80 0.5b
[00:00.480]
- note_on 1.D4 80 0.5b
[00:00.960]
- note_on 1.E4 80 0.5b
```

All notes have identical velocity (80), which sounds mechanical. Real musicians vary dynamics subtly.

### The Solution

Use `random(min, max)` to generate values within a range:

```markdown
---
title: "Lesson 1: Velocity Humanization"
tempo: 120
time_signature: [4, 4]
ppq: 480
---

# Basic robotic pattern
[00:00.000]
- marker "Robotic - No Variation"
- note_on 1.C4 80 0.5b
[00:00.480]
- note_on 1.D4 80 0.5b
[00:00.960]
- note_on 1.E4 80 0.5b
[00:01.440]
- note_on 1.F4 80 0.5b

# Humanized with velocity variation
[00:02.000]
- marker "Humanized - Velocity Variation"
- note_on 1.C4 random(75,85) 0.5b
[00:02.480]
- note_on 1.D4 random(75,85) 0.5b
[00:02.960]
- note_on 1.E4 random(75,85) 0.5b
[00:03.440]
- note_on 1.F4 random(75,85) 0.5b

# Larger variation range (more expressive)
[00:04.000]
- marker "Expressive - Wide Range"
- note_on 1.C4 random(60,100) 0.5b
[00:04.480]
- note_on 1.D4 random(60,100) 0.5b
[00:04.960]
- note_on 1.E4 random(60,100) 0.5b
[00:05.440]
- note_on 1.F4 random(60,100) 0.5b
```

### How It Works

The `random()` function takes two parameters:
- **Minimum value** (first parameter)
- **Maximum value** (second parameter)

Each time a note with `random()` velocity is generated, it picks a random integer between those bounds. The key is **choosing the right range**:

- **Subtle variation** (±5): `random(75,85)` - Professional, almost imperceptible
- **Moderate variation** (±20): `random(60,100)` - Natural, expressive
- **Wide variation** (±30+): `random(50,110)` - Very dynamic, less polished

### Pro Tips

1. **Preserve musical intent**: If you want a downbeat accent, make it louder on average:
   ```markdown
   [00:00.000]
   - note_on 1.C4 random(100,110) 0.5b  # Downbeat - higher velocity
   [00:00.480]
   - note_on 1.D4 random(70,80) 0.5b    # Offbeat - lower velocity
   ```

2. **Keep ranges within 0-127**: MIDI velocities range from 0 (silent) to 127 (loudest)

3. **Combine with note durations**: Variable velocity + variable timing creates extra humanity

### Try It Yourself

Create a 4-bar pattern where:
- Notes on strong beats (1, 3) use `random(85,100)`
- Notes on weak beats (2, 4) use `random(60,75)`
- All notes are quarter notes (1b duration)

Save as `lesson1_humanization.mmd` and compile it to hear the difference!

---

## Lesson 2: Random Note Selection - Creating Melodies

**Learning Objective**: Use randomness to generate melodic variations from a defined note range.

### Building on Lesson 1

In Lesson 1, we varied velocity. Now we'll also vary the **pitch itself** while keeping timing fixed.

### The Concept

Instead of playing the same note repeatedly, pick randomly from a range of valid notes:

```markdown
---
title: "Lesson 2: Random Melody Generation"
tempo: 120
time_signature: [4, 4]
ppq: 480
---

# Static melody (boring)
[00:00.000]
- marker "Static Melody"
- note_on 1.C4 80 0.5b
[00:00.480]
- note_on 1.C4 80 0.5b
[00:00.960]
- note_on 1.C4 80 0.5b
[00:01.440]
- note_on 1.C4 80 0.5b

# Randomized within C major pentatonic scale
[00:02.000]
- marker "Random Pentatonic"
- note_on 1.random(C4,G4) random(75,90) 0.5b
[00:02.480]
- note_on 1.random(C4,G4) random(75,90) 0.5b
[00:02.960]
- note_on 1.random(C4,G4) random(75,90) 0.5b
[00:03.440]
- note_on 1.random(C4,G4) random(75,90) 0.5b

# Wider melodic range (2 octaves)
[00:04.000]
- marker "Wide Range Random"
- note_on 1.random(C4,C6) random(60,95) 0.5b
[00:04.480]
- note_on 1.random(C4,C6) random(60,95) 0.5b
[00:04.960]
- note_on 1.random(C4,C6) random(60,95) 0.5b
[00:05.440]
- note_on 1.random(C4,C6) random(60,95) 0.5b

# Using MIDI note numbers instead of note names
[00:06.000]
- marker "MIDI Numbers"
- note_on 1.random(60,84) random(75,90) 0.5b
[00:06.480]
- note_on 1.random(60,84) random(75,90) 0.5b
[00:06.960]
- note_on 1.random(60,84) random(75,90) 0.5b
[00:07.440]
- note_on 1.random(60,84) random(75,90) 0.5b
```

### Understanding Ranges

When you write `random(C4,G4)`, MMD picks a random note between C4 (MIDI 60) and G4 (MIDI 67).

**Common useful ranges**:
- **Pentatonic scale** (5 notes, pleasing): `random(C4,G4)` includes all white keys in that octave
- **One octave**: `random(C4,C5)`
- **Two octaves**: `random(C4,C6)`
- **Narrow range** (3-4 notes): `random(C4,D#4)`

### Musical Scales and Random Selection

The `random()` function picks **all notes in the range**, including sharps/flats. If you want a specific scale (like C major without accidentals), you need to be selective:

```markdown
# This includes ALL notes from C4 to G4 (including C#, D#, F#, etc.)
- note_on 1.random(C4,G4) 80 0.5b

# For true C major pentatonic (C,D,E,G,A), use @define with specific notes
@define PENT_NOTES ["C4", "D4", "E4", "G4", "A4"]
```

However, including all notes sometimes creates beautiful microtonal effects!

### Try It Yourself

Create a 16-bar ambient drone where:
1. Each bar has 4 quarter notes
2. Notes are randomly selected from a range (e.g., C3 to G3)
3. Each note has humanized velocity: `random(50,70)`
4. At bars 9-16, expand the range upward: C3 to G4

Save as `lesson2_random_melody.mmd` and listen to how the melody "evolves" over time!

---

## Lesson 3: CC Automation - Filter Sweeps

**Learning Objective**: Use randomness to create evolving parameter automation (like filter cutoff, resonance, reverb).

### Beyond Note Randomness

In Lessons 1 & 2, we randomized notes and velocity. Now let's randomize **effect parameters** using Control Change (CC) messages combined with loops.

### The Concept

Control Change (CC) messages automate synth parameters. CC#74 is commonly filter cutoff. Here's how to create an evolving filter sweep:

```markdown
---
title: "Lesson 3: Random CC Automation"
tempo: 120
time_signature: [4, 4]
ppq: 480
---

# Static filter (no movement)
[00:00.000]
- marker "Static Filter"
- cc 1.74.64
- @loop 8 times every 1b
    - note_on 1.C4 80 0.5b
- @end

# Humanized filter with subtle variation
[00:08.000]
- marker "Subtle Filter Variation"
@loop 8 times at [00:08.000] every 0.5b
  - cc 1.74.random(62,66)
@end

# Large sweep (evolving filter)
[00:12.000]
- marker "Large Filter Sweep"
@loop 32 times at [00:12.000] every 0.125b
  - cc 1.74.random(40,100)
@end

# Controlled sweep direction (closing filter)
[00:20.000]
- marker "Controlled Sweep"
- cc 1.74.100  # Start high
- note_on 1.C4 80 2b
[00:22.000]
- cc 1.74.80
[00:23.000]
- cc 1.74.60
[00:24.000]
- cc 1.74.40   # End low
```

### Common CC Parameters

- **CC#1**: Modulation wheel (0-127)
- **CC#7**: Volume (0-127)
- **CC#10**: Pan (0=left, 64=center, 127=right)
- **CC#11**: Expression (0-127)
- **CC#74**: Filter cutoff on many synths (0-127)
- **CC#91**: Reverb amount (0-127)
- **CC#93**: Chorus amount (0-127)

### Combining Notes + CC Randomness

The most musical approach combines random notes with evolving CC:

```markdown
[00:00.000]
- marker "Pad with Evolving Filter"
- note_on 1.G3 random(60,75) 4b  # Hold note for 4 beats
@loop 16 times at [00:00.000] every 0.25b
  - cc 1.74.random(50,100)        # Filter sweeps during note
@end
```

### Try It Yourself

Create a 16-second pad where:
1. One note plays for the full 16 seconds: `note_on 1.D3 random(70,80) 16s`
2. Every 250ms, send a random CC#74 value: `cc 1.74.random(40,100)`
3. At the 8-second mark, change the range: `cc 1.74.random(80,127)` (open filter)

The effect should be an evolving, breathing pad!

---

## Lesson 4: Combining Techniques - Layered Randomization

**Learning Objective**: Blend multiple random parameters to create complex, evolving musical structures.

### Putting It All Together

Now we'll combine lessons 1-3: random velocity, random notes, and random CC values in the same composition.

### Complex Example: Algorithmic Ambient Piece

```markdown
---
title: "Lesson 4: Layered Randomization"
tempo: 90
time_signature: [4, 4]
ppq: 480
---

# Layer 1: Bass drone
[00:00.000]
- marker "Layer 1: Bass"
- note_on 1.G2 random(50,65) 8b   # 8-beat bass note
@loop 32 times at [00:00.000] every 0.25b
  - cc 1.7.random(100,110)         # Volume automation (subtle)
@end

# Layer 2: Melodic counterpoint (different channel)
[00:00.000]
- marker "Layer 2: Melody"
@loop 16 times at [00:00.000] every 0.5b
  - note_on 2.random(D4,A4) random(70,85) 0.4b
@end

# Layer 3: Filter on melody channel
[00:00.000]
@loop 64 times at [00:00.000] every 0.125b
  - cc 2.74.random(40,100)         # Rapid filter movement
@end

# Section B: More movement
[00:32.000]
- marker "Section B: Intensify"

# Faster melodic movement
[00:32.000]
@loop 32 times at [00:32.000] every 0.25b
  - note_on 2.random(C4,G5) random(65,100) 0.2b
@end

# Faster filter modulation
[00:32.000]
@loop 128 times at [00:32.000] every 0.0625b
  - cc 2.74.random(30,110)
@end

# Bass evolves with more energy
[00:32.000]
- note_on 1.F#2 random(60,80) 8b
@loop 64 times at [00:32.000] every 0.125b
  - cc 1.7.random(90,127)          # More dynamic volume
@end

# Coda: Return to stillness
[00:64.000]
- marker "Coda"
- note_on 1.G2 random(40,60) 16b
- note_on 2.G4 random(50,70) 16b
@loop 128 times at [00:64.000] every 0.125b
  - cc 2.74.random(70,80)          # Narrow filter (less movement)
@end
```

### Design Principles for Layered Randomization

1. **Use different channels for different instruments** (channel 1 = bass, channel 2 = melody)
2. **Vary the randomness ranges by section** (quiet intro, intense middle, quiet outro)
3. **Use different `@loop` intervals** for each layer (bass every 0.25b, melody every 0.5b)
4. **Add markers** to structure your composition clearly
5. **Change ranges over time** to create narrative (quieter → louder → quieter)

### Try It Yourself

Create a 60-second piece with:
1. **Bass layer** (channel 1): 2-beat notes on G2, with volume automation every 0.5b
2. **Chord layer** (channel 3): 1-beat notes randomly chosen from G3/B3/D4, velocity 70-85
3. **Lead layer** (channel 2): 0.5-beat rapid melodies from D4-A5, with filter sweep via CC#74

Make sure each layer has a different loop frequency to create natural variation!

---

## Lesson 5: Integration with Modulation - Advanced Techniques

**Learning Objective**: Understand how randomness integrates with MML's advanced features like `@sweep`, `@loop` offsets, and conditional expressions.

### Beyond Basic Random()

The `random()` function is powerful, but MMD has other advanced tools that work beautifully with generative techniques.

### @sweep + Randomization

The `@sweep` directive creates ramps. Combine it with randomization:

```markdown
---
title: "Lesson 5: Advanced Modulation"
tempo: 120
time_signature: [4, 4]
ppq: 480
---

# Sweep creates smooth parameter changes
[00:00.000]
- marker "Controlled Sweep"
@sweep cc 1.74 from 30 to 100 over 8b
@end

# But with random note selection during the sweep
[00:00.000]
@loop 16 times at [00:00.000] every 0.5b
  - note_on 1.random(C3,G4) random(70,90) 0.4b
@end

# Pitch bend sweep with random timing
[00:08.000]
- marker "Pitch Bend Modulation"
- note_on 1.C4 80 4b
@sweep pitch_bend 1 from -2000 to 2000 over 4b
@end

# During pitch bend, CC automation happens independently
[00:08.000]
@loop 32 times at [00:08.000] every 0.125b
  - cc 1.1.random(0,127)           # Mod wheel random movement
@end
```

### Loop Offsets for Phasing Effects

Use loop counts and offsets to create phasing:

```markdown
[00:00.000]
# Melody loop
@loop 16 times at [00:00.000] every 1b
  - note_on 1.random(C4,G4) random(70,90) 0.5b
@end

# Same melody on channel 2, but offset by 0.5b
[00:00.250]  # Half beat offset
@loop 16 times at [00:00.250] every 1b
  - note_on 2.random(C4,G4) random(70,90) 0.5b
@end
```

This creates a beautiful "phase" effect where the two melodies align and diverge.

### Variables in Generative Context

While `random()` doesn't require variables, using `@define` lets you control global parameters:

```markdown
@define MIN_VEL 50
@define MAX_VEL 100
@define MIN_NOTE C3
@define MAX_NOTE G5
@define SWEEP_TIME 8b

[00:00.000]
- marker "Using Variables"
@loop 16 times at [00:00.000] every 0.5b
  - note_on 1.random(${MIN_NOTE},${MAX_NOTE}) \
             random(${MIN_VEL},${MAX_VEL}) 0.4b
@end

# Easy to adjust everything from the top!
```

### Try It Yourself

Create a "pulsing pad" 30-second piece:
1. Use `@sweep` to gradually open a filter from 40 to 100 over 30 seconds on channel 1
2. During the 30 seconds, play random notes from C3-G4 with `@loop` every 0.5b
3. On channel 2, play the same notes but offset by 0.25b for a phasing effect
4. Add random volume automation (CC#7) on channel 1: `cc 1.7.random(80,120)`

This combines sweeps + randomness + phasing for a complex, evolving texture!

---

## Practical Tips & Best Practices

### Musicality Through Constraint

The secret to generative music is **constraint**. Pure randomness sounds chaotic. Musical randomness has rules:

✓ **DO**:
- Use note ranges that are musically coherent (pentatonic, modal, diatonic)
- Keep velocity ranges within 15-20 points of your "average" velocity
- Use loops with musical subdivisions (beats, half-beats, eighth-notes)
- Add markers to label sections and maintain narrative

✗ **DON'T**:
- Randomize every single parameter (too chaotic)
- Use velocity ranges wider than 0-127
- Loop with non-musical intervals (0.37b is awkward)
- Create 10 hours of automation without structure

### Performance Considerations

- **MIDI limitations**: Rapid CC changes (every 0.06b = 16th notes at 120 BPM) can overwhelm some devices
- **CPU usage**: Very long loops with many events can slow compilation
- **Playback smoothness**: Filter sweeps at 1ms intervals are fine; faster than that may cause jitter

### Real-World Application: Humanizing Drum Machines

Here's how to take a rigid drum pattern and make it sound human:

```markdown
@define KICK_VEL_MIN 95
@define KICK_VEL_MAX 115
@define SNARE_VEL_MIN 100
@define SNARE_VEL_MAX 125
@define HAT_VEL_MIN 40
@define HAT_VEL_MAX 60

[00:00.000]
- marker "Humanized Drums"

# 4-bar drum loop
@loop 4 times every 4b
  # Bar: kick on 1,3 with variation
  - note_on 10.C2 random(${KICK_VEL_MIN},${KICK_VEL_MAX}) 0.2b
  [+0.5b]
  - note_on 10.F#2 random(${HAT_VEL_MIN},${HAT_VEL_MAX}) 0.15b
  [+0.25b]
  - note_on 10.F#2 random(${HAT_VEL_MIN},${HAT_VEL_MAX}) 0.15b
  [+0.75b]
  - note_on 10.D2 random(${SNARE_VEL_MIN},${SNARE_VEL_MAX}) 0.2b
  [+0.5b]
  - note_on 10.F#2 random(${HAT_VEL_MIN},${HAT_VEL_MAX}) 0.15b
  [+0.25b]
  - note_on 10.F#2 random(${HAT_VEL_MIN},${HAT_VEL_MAX}) 0.15b
@end
```

---

## Next Steps & Further Exploration

### Recommended Reading

- [Random Expressions Reference](../reference/random-expressions.md) - Complete `random()` syntax and limitations
- [Loops & Patterns Guide](../reference/loops-and-patterns.md) - Advanced `@loop` techniques
- [Sweep & Automation Guide](../reference/sweep-automation.md) - Detailed `@sweep` documentation

### Example Files to Study

The `examples/05_generative/` directory contains full working examples:

- **random_humanization.mmd** - Foundational velocity and note randomization (start here!)
- **algorithmic_drums.mmd** - Professional drum patterns with humanization
- **random_cc_automation.mmd** - CC sweeps and filter modulation
- **generative_ambient.mmd** - Complex layered ambient piece using all techniques

### Exercises to Try

1. **Humanize a boring pattern**: Take any static MIDI pattern and add 2-3 layers of randomization
2. **Create a 60-second generative piece**: Use all 5 lessons in one composition
3. **Generative drum fills**: Create fills that are mostly random but with structured breaks
4. **Modulation matrix**: Randomize 4+ CC parameters simultaneously on different @loop intervals

### Advanced Topics (Future Learning)

While not covered in this tutorial, MMD also supports:

- **Conditional logic** (`@if`/`@elif`/`@else`) - Create branching generative patterns
- **Custom aliases** - Create reusable generative "instrument definitions"
- **REPL mode** - Interactive generative experimentation (see `mml repl`)
- **Computed values** - Mathematical expressions beyond `random()`

### Troubleshooting

**"My pattern sounds too random/chaotic"**
→ Narrow your ranges. Use `random(75,80)` instead of `random(0,127)`

**"All my notes are the same octave"**
→ Expand your note range. Use `random(C3,C6)` instead of `random(C4,C4)`

**"CC changes are too jerky"**
→ Decrease loop interval. Use `every 0.125b` instead of `every 1b`

**"My file won't compile"**
→ Check that `random()` is only used in parameter positions (velocity, note, CC value), not timing
→ Ensure minimum < maximum in all `random()` calls

---

## Summary

You've learned to:

1. **Lesson 1**: Add velocity humanization with subtle ranges
2. **Lesson 2**: Generate melodies by randomizing note selection
3. **Lesson 3**: Automate effect parameters with random CC values
4. **Lesson 4**: Layer multiple randomization sources for complex textures
5. **Lesson 5**: Integrate randomization with advanced features like `@sweep`

The key principle: **Generative music uses randomness within musical constraints to create variation without chaos.**

Compile any of the example files and listen to them multiple times - each playback will be slightly different, creating the feeling of a live, breathing performance. This is the power of generative techniques!

Happy creating! 🎵

---

*Last updated: November 2025*
*See the `examples/05_generative/` directory for runnable examples and more advanced techniques.*
