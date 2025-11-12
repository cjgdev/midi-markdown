# Enhanced Modulation

MIDI Markdown provides three powerful modulation types for smooth, natural-sounding parameter automation: **Bezier curves**, **waveforms** (LFO), and **envelopes**. These go far beyond simple linear ramps, enabling professional-quality automation for filters, volume, pitch, and any MIDI parameter.

## Overview

Modulation expressions can be used in **any parameter context**: CC values, pitch bend, and aftertouch/pressure. This provides smooth transitions and periodic variations across all MIDI message types:

```mml
# CC: Bezier curve for smooth filter opening
- cc 1.74.curve(0, 127, ease-out)

# CC: Sine wave for vibrato
- cc 1.1.wave(sine, 64, freq=5.0, depth=10)

# CC: ADSR envelope for dynamic filter
- cc 1.74.envelope(adsr, attack=0.1, decay=0.2, sustain=0.7, release=0.3)

# Pitch bend: Natural vibrato effect
- pitch_bend 1.wave(sine, 8192, freq=5.5, depth=5)

# Channel pressure: Expression swell
- channel_pressure 1.curve(0, 127, ease-in-out)
```

---

## Bezier Curves

Bezier curves provide smooth parameter transitions using cubic interpolation. They're perfect for automation that needs to feel natural and musical.

### Syntax

```mml
curve(start_value, end_value, curve_type)
```

### Parameters

- **start_value**: Starting value (0-127 for CC, -8192 to +8191 for pitch bend)
- **end_value**: Ending value (same range as start)
- **curve_type**: Interpolation type (see below)

### Curve Types

#### Preset Curves

| Type | Description | Best For |
|------|-------------|----------|
| `ease-in` | Slow start, fast finish | Gradual filter opens, crescendos |
| `ease-out` | Fast start, slow finish | Natural fade-ins, decelerandos |
| `ease-in-out` | S-curve motion | Smooth musical automation |
| `linear` | Constant rate | Predictable, metronomic changes |

#### Custom Bezier

For precise control, specify your own control points:

```mml
curve(start, end, bezier(p0, p1, p2, p3))
```

Control points define the shape of the cubic Bezier curve. Values are normalized (0.0-1.0) and scaled to the start/end range.

### Examples

```mml
# Natural filter opening (slow start, fast finish)
[00:00.000]
- cc 1.74.curve(0, 127, ease-in)

# Volume fade-in (fast start, slow finish)
[00:02.000]
- cc 1.7.curve(0, 100, ease-out)

# Smooth expression swell
[00:04.000]
- cc 1.11.curve(0, 127, ease-in-out)

# Linear comparison
[00:06.000]
- cc 1.74.curve(127, 0, linear)

# Custom curve with precise control
[00:08.000]
- cc 1.74.curve(0, 127, bezier(0, 20, 100, 127))
```

### Curve Characteristics

**Ease-In** starts slowly and accelerates:
- Best for gradual builds
- Feels like gathering momentum
- Control points: (0, 0.42, 0, 1)

**Ease-Out** starts fast and decelerates:
- Best for natural arrivals
- Feels like coming to rest
- Control points: (0, 0.58, 1, 1)

**Ease-In-Out** accelerates then decelerates:
- Most natural for musical automation
- S-curve motion
- Control points: (0, 0.42, 0.58, 1)

---

## Waveforms (LFO)

Waveforms create periodic modulation using Low Frequency Oscillators (LFOs). They're ideal for vibrato, tremolo, auto-pan, and filter sweeps.

### Syntax

```mml
wave(wave_type, base_value [, freq=Hz] [, phase=offset] [, depth=percent])
```

### Parameters

- **wave_type**: Waveform shape (sine, triangle, square, sawtooth)
- **base_value**: Center value for oscillation (0-127)
- **freq**: Frequency in Hz (default: 1.0)
- **phase**: Phase offset 0.0-1.0 (default: 0.0, where 0.25 = 90°)
- **depth**: Modulation depth as percentage (default: 50%)

### Wave Types

| Type | Shape | Characteristics | Best For |
|------|-------|----------------|----------|
| `sine` | Smooth oscillation | Natural, continuous | Vibrato, tremolo |
| `triangle` | Linear rise/fall | Smooth but not rounded | Gentle modulation |
| `square` | Abrupt switching | Hard transitions | Rhythmic effects |
| `sawtooth` | Ramp pattern | Rising or falling ramps | Stepped automation |

### Examples

```mml
# Classic vibrato (5 Hz is typical for pitch)
[00:00.000]
- cc 1.1.wave(sine, 64, freq=5.0, depth=10)

# Tremolo effect (3-5 Hz for volume)
[00:02.000]
- cc 1.7.wave(sine, 100, freq=4.0, depth=30)

# Filter sweep (slow triangle)
[00:04.000]
- cc 1.74.wave(triangle, 64, freq=0.5, depth=60)

# Rhythmic gating (square wave)
[00:06.000]
- cc 1.7.wave(square, 100, freq=2.0, depth=80)

# Auto-pan (sine with phase offset for stereo)
[00:08.000]
- cc 1.10.wave(sine, 64, freq=2.0, depth=80)          # Left
[@]
- cc 2.10.wave(sine, 64, freq=2.0, phase=0.5, depth=80)  # Right (180° out of phase)
```

### Frequency Guidelines

| Effect | Typical Range | Notes |
|--------|---------------|-------|
| Vibrato | 5-7 Hz | Pitch modulation |
| Tremolo | 3-5 Hz | Volume modulation |
| Chorus | 0.1-1 Hz | Very slow |
| Filter LFO | 0.2-2 Hz | Evolving pads |
| Rhythmic | 1-4 Hz | Synced to tempo |

### Depth Guidelines

- **Subtle** (5-15%): Natural vibrato, gentle motion
- **Moderate** (20-40%): Noticeable but musical
- **Strong** (50-70%): Obvious effect
- **Extreme** (80-100%): Full range modulation

---

## Envelopes

Envelopes shape parameters over time, following attack, decay, sustain, and release phases. Perfect for dynamic filter sweeps, volume automation, and time-varying effects.

### Envelope Types

#### ADSR (Attack-Decay-Sustain-Release)

Full envelope with four phases. Classic for synth sounds.

```mml
envelope(adsr, attack=time, decay=time, sustain=level, release=time [, curve=type])
```

**Parameters:**
- `attack`: Time to reach peak (seconds)
- `decay`: Time from peak to sustain (seconds)
- `sustain`: Sustain level 0.0-1.0 (relative to peak)
- `release`: Time from sustain to zero (seconds)
- `curve`: Optional curve type (`linear` or `exponential`)

**Example:**
```mml
# Synth pad filter envelope
[00:00.000]
- note_on 1.60.80 4b
- cc 1.74.envelope(adsr, attack=0.5, decay=0.3, sustain=0.7, release=1.0)
```

**Phases:**
1. **Attack**: 0 → peak (over attack time)
2. **Decay**: peak → sustain level (over decay time)
3. **Sustain**: Held at sustain level (until note off)
4. **Release**: sustain → 0 (over release time)

#### AR (Attack-Release)

Simple two-phase envelope. Great for percussive sounds.

```mml
envelope(ar, attack=time, release=time [, curve=type])
```

**Parameters:**
- `attack`: Time to reach peak
- `release`: Time from peak to zero
- `curve`: Optional curve type

**Example:**
```mml
# Percussive filter hit
[00:00.000]
- cc 1.74.envelope(ar, attack=0.01, release=0.2)
```

**Phases:**
1. **Attack**: 0 → peak (over attack time)
2. **Release**: peak → 0 (over release time)

#### AD (Attack-Decay)

Attack and decay only, no sustain. Perfect for plucked/struck sounds.

```mml
envelope(ad, attack=time, decay=time [, curve=type])
```

**Parameters:**
- `attack`: Time to reach peak
- `decay`: Time from peak to zero
- `curve`: Optional curve type

**Example:**
```mml
# Plucked string filter envelope
[00:00.000]
- cc 1.74.envelope(ad, attack=0.02, decay=0.5)
```

**Phases:**
1. **Attack**: 0 → peak (over attack time)
2. **Decay**: peak → 0 (over decay time)

### Curve Types

Envelopes support two curve shapes:

**Linear** (default):
- Constant rate of change
- Predictable, mathematical
- Good for electronic sounds

**Exponential**:
- Natural decay/growth
- More organic feel
- Better for acoustic simulation

```mml
# Linear envelope (default)
- cc 1.74.envelope(ar, attack=0.1, release=0.3)

# Exponential envelope (more natural)
- cc 1.74.envelope(ar, attack=0.1, release=0.3, curve=exponential)
```

### Envelope Timing Guidelines

| Sound Type | Attack | Decay | Sustain | Release |
|-----------|--------|-------|---------|---------|
| Pad | 0.5-2.0s | 0.2-0.5s | 0.6-0.8 | 1.0-3.0s |
| Pluck | 0.01-0.05s | 0.1-0.5s | — | — |
| Percussion | 0.001-0.01s | — | — | 0.05-0.2s |
| Brass | 0.05-0.1s | 0.1-0.2s | 0.7-0.9 | 0.1-0.3s |
| Strings | 0.1-0.3s | 0.2-0.4s | 0.8-0.9 | 0.3-1.0s |

---

## Practical Applications

### Filter Automation

```mml
# Smooth filter opening
[00:00.000]
- cc 1.74.curve(30, 110, ease-out)

# Dynamic filter with envelope
[00:02.000]
- note_on 1.60.80 4b
- cc 1.74.envelope(adsr, attack=0.1, decay=0.2, sustain=0.6, release=0.3)

# Slow filter LFO for evolving pads
[00:06.000]
- cc 1.74.wave(sine, 64, freq=0.2, depth=60)
```

### Vibrato and Pitch Effects

```mml
# CC vibrato (mod wheel)
[00:00.000]
- cc 1.1.wave(sine, 64, freq=6.0, depth=8)

# Pitch bend vibrato (more natural for pitch)
[00:02.000]
- pitch_bend 1.wave(sine, 8192, freq=5.5, depth=5)

# Pitch sweep with curve
[00:04.000]
- pitch_bend 1.curve(-4096, 4096, ease-in-out)

# Pitch dive with envelope
[00:06.000]
- pitch_bend 1.envelope(ad, attack=0.01, decay=1.5)
```

### Tremolo and Volume

```mml
# Tremolo (volume)
[00:00.000]
- cc 1.7.wave(triangle, 100, freq=4.0, depth=25)

# Volume swell with envelope
[00:02.000]
- cc 1.7.envelope(ar, attack=2.0, release=1.5)
```

### Volume Automation

```mml
# Smooth fade-in
[00:00.000]
- cc 1.7.curve(0, 100, ease-out)

# Volume swell
[00:02.000]
- cc 1.7.envelope(ar, attack=2.0, release=1.5)

# Rhythmic volume modulation
[00:04.000]
- cc 1.7.wave(square, 90, freq=2.0, depth=40)
```

### Expression and Dynamics

```mml
# Musical expression curve (CC#11)
[00:00.000]
- cc 1.11.curve(40, 120, ease-in-out)

# Breath controller envelope (CC#2)
[00:02.000]
- cc 1.2.envelope(adsr, attack=0.3, decay=0.2, sustain=0.8, release=0.5)
```

### Pressure and Aftertouch

Channel pressure and polyphonic pressure (aftertouch) support all modulation types, enabling expressive per-note or per-channel dynamics:

```mml
# Channel pressure swell for pads
[00:00.000]
- note_on 1.60.80 4b
- channel_pressure 1.curve(0, 127, ease-in-out)

# Channel pressure with envelope
[00:04.000]
- note_on 1.60.100 4b
- channel_pressure 1.envelope(adsr, attack=0.2, decay=0.1, sustain=0.8, release=0.3)

# Polyphonic pressure vibrato (per-note expression)
[00:08.000]
- note_on 1.C4.100 4b
- poly_pressure 1.C4.wave(sine, 64, freq=3.0, depth=40)

# Multiple notes with independent pressure
[00:12.000]
- note_on 1.C4.100 4b
- poly_pressure 1.C4.curve(0, 127, ease-in)
[@]
- note_on 1.E4.100 4b
- poly_pressure 1.E4.curve(0, 100, ease-out)
```

---

## Advanced Techniques

### Multi-Parameter Modulation

Combine multiple modulations for complex effects:

```mml
# Simultaneous filter and resonance
[00:00.000]
[@]
- cc 1.74.curve(20, 120, ease-in-out)  # Cutoff
[@]
- cc 1.71.curve(10, 80, ease-in-out)   # Resonance
```

### Stereo Effects

Create stereo width with phase-shifted modulation:

```mml
# Auto-pan with phase offset
[00:00.000]
[@]
- cc 1.10.wave(sine, 64, freq=1.5, depth=80)            # Left
[@]
- cc 2.10.wave(sine, 64, freq=1.5, phase=0.5, depth=80)  # Right (180° out)
```

### Layered LFOs

Stack multiple LFOs for complex motion:

```mml
# Dual LFO modulation
[00:00.000]
[@]
- cc 1.74.wave(sine, 64, freq=0.5, depth=30)    # Slow drift
[@]
- cc 1.71.wave(triangle, 50, freq=5.0, depth=15)  # Fast texture
```

### Time-Varying Effects

```mml
# Long evolving filter
[00:00.000]
- cc 1.74.envelope(ad, attack=10.0, decay=15.0, curve=exponential)

# Slow build with curve
[00:10.000]
- cc 1.7.curve(20, 127, ease-in)
```

---

## Tips and Best Practices

### Choosing the Right Modulation Type

**Use Curves when:**
- You need a one-time transition
- You want precise start and end values
- Musical phrasing is important

**Use Waveforms when:**
- You need continuous, periodic motion
- Creating vibrato, tremolo, or chorus
- Rhythmic effects are desired

**Use Envelopes when:**
- Modulation follows note timing
- You need attack/release behavior
- Simulating acoustic instruments

### Performance Optimization

- **Sample Rate**: Default 100 Hz is usually sufficient
- **Frequency**: LFO frequencies above 20 Hz may need higher sample rates
- **Duration**: Long envelopes/curves use more events

### Musicality

- **Subtle is better**: Start with small depth values (10-20%)
- **Match the tempo**: Consider rhythmic alignment for LFOs
- **Layer carefully**: Too many modulations can sound chaotic
- **Test with sound**: What looks good on paper may not sound good

### Common Pitfalls

❌ **Don't overdo depth** - 100% depth is rarely musical
❌ **Don't use square waves everywhere** - They're very harsh
❌ **Don't forget phase offset** - Essential for stereo effects
❌ **Don't use linear for everything** - Exponential sounds more natural

---

## Reference

Modulation expressions work in **all parameter contexts**. Use the same syntax with different MIDI message types.

### Curve Syntax

```mml
# CC values
cc {channel}.{cc_number}.curve(start, end, curve_type)

# Pitch bend
pitch_bend {channel}.curve(start, end, curve_type)

# Channel pressure
channel_pressure {channel}.curve(start, end, curve_type)

# Polyphonic pressure
poly_pressure {channel}.{note}.curve(start, end, curve_type)

curve_type:
  - ease-in
  - ease-out
  - ease-in-out
  - linear
  - bezier(p0, p1, p2, p3)
```

### Wave Syntax

```mml
# CC values
cc {channel}.{cc_number}.wave(type, base [, freq=Hz] [, phase=0-1] [, depth=percent])

# Pitch bend
pitch_bend {channel}.wave(type, base [, freq=Hz] [, phase=0-1] [, depth=percent])

# Channel/poly pressure
channel_pressure {channel}.wave(type, base [, freq=Hz] [, phase=0-1] [, depth=percent])
poly_pressure {channel}.{note}.wave(type, base [, freq=Hz] [, phase=0-1] [, depth=percent])

type:
  - sine
  - triangle
  - square
  - sawtooth
```

### Envelope Syntax

```mml
# CC values
cc {channel}.{cc_number}.envelope(type, params [, curve=type])

# Pitch bend
pitch_bend {channel}.envelope(type, params [, curve=type])

# Channel/poly pressure
channel_pressure {channel}.envelope(type, params [, curve=type])
poly_pressure {channel}.{note}.envelope(type, params [, curve=type])

ADSR: envelope(adsr, attack=t, decay=t, sustain=lvl, release=t [, curve=type])
AR:   envelope(ar, attack=t, release=t [, curve=type])
AD:   envelope(ad, attack=t, decay=t [, curve=type])

curve: linear | exponential
```

### Value Ranges

| Context | Range | Resolution |
|---------|-------|------------|
| CC values | 0-127 | 7-bit |
| Pitch bend | -8192 to +8191 | 14-bit |
| Channel pressure | 0-127 | 7-bit |
| Poly pressure | 0-127 | 7-bit |

---

## See Also

- [MIDI Commands Reference](midi-commands.md) - Available CC numbers
- [Timing System](timing-system.md) - Timing with modulation
- [Examples](https://github.com/cjgdev/midi-markdown/blob/main/examples/03_advanced/08_modulation_showcase.mmd) - Complete modulation showcase
- [Alias System](alias-system.md) - Creating modulation aliases
