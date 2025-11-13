# Sweep Automation Reference

Complete reference for the `@sweep` directive in MIDI Markdown.

## Overview

The `@sweep` directive creates smooth, automated parameter changes over time by generating a series of MIDI Control Change (CC) messages with interpolated values. This is essential for:

- Volume fades (in/out)
- Filter sweeps (opening/closing)
- Panning automation (left/right movement)
- Expression swells
- Any gradual parameter change

Unlike setting discrete CC values at specific times, sweeps generate a continuous stream of values for natural, smooth automation.

## Syntax

```mml
@sweep from [<start_time>] to [<end_time>] every <interval>
  - cc <channel>.<controller>.ramp(<start_value>, <end_value> [, <ramp_type>])
@end
```

### Parameters

- **`from [<start_time>]`**: When the sweep begins (any timing format)
- **`to [<end_time>]`**: When the sweep ends (any timing format)
- **`every <interval>`**: How often to generate CC messages (timing units)
- **`<channel>`**: MIDI channel (1-16)
- **`<controller>`**: CC controller number (0-127)
- **`<start_value>`**: Initial CC value (0-127)
- **`<end_value>`**: Final CC value (0-127)
- **`<ramp_type>`**: Interpolation curve (optional, defaults to `linear`)

### Timing Formats

Start and end times support all MMD timing paradigms:

**Absolute Time:**
```mml
@sweep from [00:00.000] to [00:04.000] every 100ms
  - cc 1.7.ramp(0, 127)
@end
```

**Musical Time:**
```mml
@sweep from [1.1.0] to [5.1.0] every 8t
  - cc 1.7.ramp(0, 127)
@end
```

**Relative Time:**
```mml
[00:10.000]
@sweep from [+0s] to [+4s] every 100ms
  - cc 1.7.ramp(0, 127)
@end
```

### Interval Units

The `every` parameter accepts these time units:

- **`ms`** - milliseconds (e.g., `every 100ms`)
- **`s`** - seconds (e.g., `every 0.5s`)
- **`b`** - beats (e.g., `every 1b`)
- **`t`** - ticks (e.g., `every 16t`)

**Choosing an Interval:**

- **Smooth automation**: 50-100ms (20-10 messages per second)
- **Very smooth**: 25-50ms (40-20 messages per second)
- **Efficient/less dense**: 100-200ms (10-5 messages per second)
- **Musical sync**: Beat or tick subdivisions (`8t`, `16t`, `0.25b`)

## Ramp Types

Ramp types control how values transition from start to end. Each creates a different acceleration curve.

### Linear (Default)

Constant rate of change - values increase/decrease uniformly.

```mml
@sweep from [00:00.000] to [00:04.000] every 100ms
  - cc 1.7.ramp(0, 127, linear)
@end
```

**Use cases:**
- Simple fades
- Predictable automation
- Default behavior if ramp type omitted

**Curve:** Straight line (y = x)

### Exponential

Starts slow, accelerates toward the end - creates dramatic builds.

```mml
@sweep from [00:04.500] to [00:08.500] every 50ms
  - cc 1.74.ramp(0, 127, exponential)
@end
```

**Use cases:**
- Filter opening (dramatic reveal)
- Build-ups before drops
- Crescendos with impact
- Acceleration effects

**Curve:** Exponential growth (y = x²)

### Logarithmic

Starts fast, decelerates toward the end - creates natural arrivals.

```mml
@sweep from [00:09.000] to [00:13.000] every 75ms
  - cc 1.10.ramp(0, 64, logarithmic)
@end
```

**Use cases:**
- Natural fade-outs
- Smooth arrivals
- Decelerating pans
- Settling effects

**Curve:** Logarithmic decay (y = log(x))

### Ease-In

Slow start, fast finish - gradual acceleration.

```mml
@sweep from [00:00.000] to [00:04.000] every 100ms
  - cc 1.7.ramp(0, 100, ease-in)
@end
```

**Use cases:**
- Gentle fade-ins
- Gradual builds
- Natural volume swells

**Curve:** Cubic ease-in (Bezier approximation)

### Ease-Out

Fast start, slow finish - gradual deceleration.

```mml
@sweep from [00:02.000] to [00:06.000] every 100ms
  - cc 1.7.ramp(127, 0, ease-out)
@end
```

**Use cases:**
- Natural fade-outs
- Smooth arrivals
- Volume decays

**Curve:** Cubic ease-out (Bezier approximation)

### Ease-In-Out

Slow at both ends, fast in the middle - S-curve motion.

```mml
@sweep from [00:04.000] to [00:08.000] every 100ms
  - cc 1.11.ramp(0, 127, ease-in-out)
@end
```

**Use cases:**
- Smooth musical automation
- Natural expression swells
- Professional-sounding pans

**Curve:** Cubic ease-in-out (S-shaped Bezier)

## Common Controllers

### Volume (CC #7)

```mml
# Fade in
@sweep from [00:00.000] to [00:04.000] every 100ms
  - cc 1.7.ramp(0, 127, linear)
@end

# Fade out
@sweep from [00:13.500] to [00:17.500] every 100ms
  - cc 1.7.ramp(127, 0, linear)
@end
```

### Pan (CC #10)

```mml
# Pan left to right
@sweep from [00:18.000] to [00:22.000] every 75ms
  - cc 1.10.ramp(0, 127, linear)
@end

# Pan center to left
@sweep from [00:09.000] to [00:13.000] every 75ms
  - cc 1.10.ramp(64, 0, logarithmic)
@end
```

Values: `0` = hard left, `64` = center, `127` = hard right

### Expression (CC #11)

```mml
# Expression swell
@sweep from [00:18.000] to [00:22.000] every 80ms
  - cc 1.11.ramp(0, 127, exponential)
@end
```

### Filter Cutoff (CC #74)

```mml
# Filter opening
@sweep from [00:04.500] to [00:08.500] every 50ms
  - cc 1.74.ramp(0, 127, exponential)
@end

# Filter closing
@sweep from [00:08.500] to [00:12.500] every 50ms
  - cc 1.74.ramp(127, 0, logarithmic)
@end
```

### Modulation Wheel (CC #1)

```mml
# Modulation increase
@sweep from [00:23.000] to [00:27.000] every 90ms
  - cc 1.1.ramp(0, 100, linear)
@end
```

## Examples

### Simple Volume Fade-In

```mml
[00:00.000]
- note_on 1.60 100 4s

@sweep from [00:00.000] to [00:04.000] every 100ms
  - cc 1.7.ramp(0, 127, linear)
@end
```

Fades volume from silence to full over 4 seconds with linear curve.

### Filter Opening (Exponential)

```mml
[00:04.500]
- note_on 1.48 100 4s

@sweep from [00:04.500] to [00:08.500] every 50ms
  - cc 1.74.ramp(0, 127, exponential)
@end
```

Opens filter cutoff with dramatic acceleration for build-up effect.

### Smooth Pan Movement (Logarithmic)

```mml
[00:09.000]
- note_on 1.64 90 4s

@sweep from [00:09.000] to [00:13.000] every 75ms
  - cc 1.10.ramp(0, 64, logarithmic)
@end
```

Pans from hard left to center with natural deceleration.

### Multiple Concurrent Sweeps

```mml
[00:18.000]
- note_on 1.65 100 4s

# Pan from left to right (linear)
@sweep from [00:18.000] to [00:22.000] every 75ms
  - cc 1.10.ramp(0, 127, linear)
@end

# Expression swell (exponential)
@sweep from [00:18.000] to [00:22.000] every 80ms
  - cc 1.11.ramp(0, 127, exponential)
@end
```

Combines pan and expression automation simultaneously for rich movement.

### Dramatic Build-Up (Multi-Parameter)

```mml
[00:23.000]
- note_on 1.60 95 4s
- note_on 1.64 95 4s
- note_on 1.67 95 4s

# Volume swell
@sweep from [00:23.000] to [00:27.000] every 100ms
  - cc 1.7.ramp(20, 127, linear)
@end

# Filter opens dramatically
@sweep from [00:23.000] to [00:27.000] every 80ms
  - cc 1.74.ramp(0, 127, exponential)
@end

# Modulation increases
@sweep from [00:23.000] to [00:27.000] every 90ms
  - cc 1.1.ramp(0, 100, linear)
@end

# Impact hit at peak
[00:27.000]
- note_on 10.36 127 0.1s
```

Combines volume, filter, and modulation sweeps for maximum dramatic impact.

### Musical Time Sweep

```mml
[1.1.0]
- note_on 1.60 100 4b

# Sweep over 4 bars with 8-tick intervals
@sweep from [1.1.0] to [5.1.0] every 8t
  - cc 1.7.ramp(0, 127, linear)
@end
```

Uses musical timing (bars.beats.ticks) for tempo-synchronized automation.

## Best Practices

### 1. Choose Appropriate Intervals

**Too fast (< 25ms):**
- Generates excessive MIDI messages
- Can overwhelm MIDI bandwidth
- May cause timing issues

**Too slow (> 200ms):**
- Audible stepping/zipper noise
- Choppy automation
- Unnatural transitions

**Recommended:** 50-100ms for smooth automation

### 2. Match Ramp Type to Musical Context

- **Linear**: Neutral, predictable (fades, general automation)
- **Exponential**: Dramatic builds, energy increases
- **Logarithmic**: Natural decays, smooth arrivals
- **Ease-in/out/in-out**: Musical, professional-sounding automation

### 3. Synchronize with Musical Events

Align sweep start/end times with:
- Note onsets
- Section boundaries (verse, chorus)
- Downbeats (bar 1, beat 1)
- Song structure changes

### 4. Layer Multiple Parameters

Combine sweeps for richer automation:
```mml
# Simultaneous volume, filter, and pan
@sweep from [00:00.000] to [00:04.000] every 100ms
  - cc 1.7.ramp(0, 127)     # Volume
@end

@sweep from [00:00.000] to [00:04.000] every 80ms
  - cc 1.74.ramp(0, 127)    # Filter
@end

@sweep from [00:00.000] to [00:04.000] every 75ms
  - cc 1.10.ramp(0, 64)     # Pan
@end
```

### 5. Consider Performance Impact

- Each sweep generates multiple MIDI messages
- Use longer intervals for dense arrangements
- Optimize for device MIDI bandwidth

## Technical Notes

### Event Generation

A sweep generates CC messages at regular intervals:

```
Duration = end_time - start_time
Number of events = Duration / interval
```

**Example:**
```mml
@sweep from [00:00.000] to [00:04.000] every 100ms
  - cc 1.7.ramp(0, 127)
@end
```
- Duration: 4 seconds = 4000ms
- Interval: 100ms
- Events generated: 4000 / 100 = 40 CC messages

### Value Interpolation

Values are interpolated using the specified ramp type:

**Linear:**
```
value(t) = start + (end - start) * (t / duration)
```

**Exponential:**
```
value(t) = start + (end - start) * (t / duration)²
```

**Logarithmic:**
```
value(t) = start + (end - start) * log(1 + t/duration) / log(2)
```

### MIDI Bandwidth

Standard MIDI bandwidth: ~3125 bytes/second

CC message size: 3 bytes (status + controller + value)

Maximum CC rate: ~1000 messages/second (theoretical)

Recommended: < 100 messages/second (< 10ms interval)

## Troubleshooting

### Problem: Choppy/Stepped Automation

**Solution:** Decrease interval (use smaller time step)
```mml
# Before (choppy)
@sweep from [00:00.000] to [00:04.000] every 500ms
  - cc 1.7.ramp(0, 127)
@end

# After (smooth)
@sweep from [00:00.000] to [00:04.000] every 50ms
  - cc 1.7.ramp(0, 127)
@end
```

### Problem: MIDI Overload

**Solution:** Increase interval (reduce message density)
```mml
# Before (too dense)
@sweep from [00:00.000] to [00:04.000] every 10ms
  - cc 1.7.ramp(0, 127)
@end

# After (optimized)
@sweep from [00:00.000] to [00:04.000] every 100ms
  - cc 1.7.ramp(0, 127)
@end
```

### Problem: Automation Too Slow/Fast

**Solution:** Adjust ramp type
```mml
# Too linear - change to exponential for drama
@sweep from [00:00.000] to [00:04.000] every 100ms
  - cc 1.74.ramp(0, 127, exponential)
@end

# Too aggressive - change to logarithmic for smoothness
@sweep from [00:00.000] to [00:04.000] every 100ms
  - cc 1.7.ramp(127, 0, logarithmic)
@end
```

### Problem: Sweep Doesn't Align with Notes

**Solution:** Use precise timing or relative timing
```mml
# Absolute timing - ensure exact alignment
[00:05.000]
- note_on 1.60 100 4s

@sweep from [00:05.000] to [00:09.000] every 100ms
  - cc 1.7.ramp(0, 127)
@end

# OR use relative timing
[00:05.000]
- note_on 1.60 100 4s

@sweep from [+0s] to [+4s] every 100ms
  - cc 1.7.ramp(0, 127)
@end
```

## See Also

- **[Loop Automation](loops-and-patterns.md)** - Repetitive patterns with `@loop`
- **[Timing System](../user-guide/timing-system.md)** - MMD timing formats
- **[MIDI Commands](../user-guide/midi-commands.md)** - MIDI CC and command reference
- **[Examples: Sweep Automation](https://github.com/cjgdev/midi-markdown/blob/main/examples/03_advanced/02_sweep_automation.mmd)** - Working examples
- **[Specification](https://github.com/cjgdev/midi-markdown/blob/main/spec.md)** - Complete MMD language spec

## Quick Reference

| Ramp Type | Behavior | Use Case |
|-----------|----------|----------|
| `linear` | Constant rate | Simple fades, neutral automation |
| `exponential` | Accelerates | Dramatic builds, energy increases |
| `logarithmic` | Decelerates | Natural decays, smooth arrivals |
| `ease-in` | Slow start | Gentle builds, gradual swells |
| `ease-out` | Slow finish | Natural fade-outs, arrivals |
| `ease-in-out` | S-curve | Musical automation, professional |

| Controller | CC # | Use |
|------------|------|-----|
| Volume | 7 | Master volume |
| Pan | 10 | Stereo positioning (0=L, 64=C, 127=R) |
| Expression | 11 | Dynamic expression |
| Filter Cutoff | 74 | Brightness/timbre |
| Modulation | 1 | Vibrato, tremolo depth |
| Resonance | 71 | Filter resonance |

---

**Version:** 1.0.0
**Last Updated:** 2025-11-11
