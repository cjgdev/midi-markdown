# Modulation API Reference

Technical reference for Stage 7 modulation expressions: curves, waves, and envelopes. For tutorials and examples, see [user-guide/modulation.md](../user-guide/modulation.md).

---

## Quick Syntax Reference

Modulation expressions work in **all parameter contexts**: CC values, pitch bend, and aftertouch/pressure.

```mml
# Bezier curve - smooth parameter transitions
cc {ch}.{cc}.curve(start, end, type)
pitch_bend {ch}.curve(start, end, type)
channel_pressure {ch}.curve(start, end, type)

# Waveform (LFO) - periodic modulation
cc {ch}.{cc}.wave(type, base [, freq=Hz] [, phase=0-1] [, depth=percent])
pitch_bend {ch}.wave(type, base [, freq=Hz] [, phase=0-1] [, depth=percent])
poly_pressure {ch}.{note}.wave(type, base [, freq=Hz] [, phase=0-1] [, depth=percent])

# Envelope - time-based parameter shaping
cc {ch}.{cc}.envelope(adsr|ar|ad, params [, curve=type])
pitch_bend {ch}.envelope(adsr|ar|ad, params [, curve=type])
channel_pressure {ch}.envelope(adsr|ar|ad, params [, curve=type])
```

---

## curve() - Bezier Curve Expressions

Smooth parameter transitions using cubic Bezier interpolation.

### Syntax

```mml
curve(start_value, end_value, curve_type)
```

### Parameters

| Parameter | Type | Range | Description |
|-----------|------|-------|-------------|
| `start_value` | int | 0-127 (CC), -8192 to +8191 (pitch) | Initial value |
| `end_value` | int | 0-127 (CC), -8192 to +8191 (pitch) | Final value |
| `curve_type` | string | See types below | Interpolation shape |

### Curve Types

#### Preset Curves

| Type | Control Points | Use Case |
|------|-----------------|----------|
| `linear` | (0, 0, 1, 1) | Constant rate, metronomic |
| `ease-in` | (0, 0.42, 0, 1) | Slow start, fast finish (builds) |
| `ease-out` | (0, 0.58, 1, 1) | Fast start, slow finish (arrivals) |
| `ease-in-out` | (0, 0.42, 0.58, 1) | S-curve, most natural (swells) |

#### Custom Bezier

```mml
curve(start, end, bezier(p0, p1, p2, p3))
```

Custom control points define exact curve shape. Values normalized 0.0-1.0, scaled to start/end range.

### Return Value

Generates time-interpolated CC values between start and end over the event duration.

### Behavior

- Evaluates over time from event timing to next event (or document end)
- Continuous smooth interpolation between two values
- Works with any MIDI value parameter (CC, note velocity, pitch bend center)

### Example

```mml
# CC automation
[00:00.000]
- cc 1.74.curve(0, 127, ease-out)        # Filter open: fast then slow
- cc 1.7.curve(0, 100, ease-in)          # Volume build: slow then fast

# Pitch bend sweep
[00:04.000]
- pitch_bend 1.curve(-4096, 4096, ease-in-out)  # Smooth pitch sweep

# Channel pressure swell
[00:08.000]
- channel_pressure 1.curve(0, 127, ease-in-out)  # Expression swell
```

### Compatibility

- **MIDI**: Works with any CC number (0-127), pitch bend (-8192 to +8191), and pressure (0-127)
- **Timing**: Respects document tempo and timing mode
- **Channels**: All 16 MIDI channels supported
- **Contexts**: CC values, pitch_bend, channel_pressure, poly_pressure

### Error Conditions

- `InvalidValue`: start/end outside valid range
- `InvalidCurveType`: curve_type not recognized
- `SyntaxError`: Custom bezier requires exactly 4 control points

---

## wave() - Waveform (LFO) Expressions

Periodic modulation using Low Frequency Oscillators (LFOs).

### Syntax

```mml
wave(wave_type, base_value [, freq=Hz] [, phase=offset] [, depth=percent])
```

### Parameters

| Parameter | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `wave_type` | string | sine, triangle, square, sawtooth | — | Waveform shape |
| `base_value` | int | 0-127 (CC), -8192 to +8191 (pitch) | — | Center oscillation value |
| `freq` | float | 0.1-20.0 Hz | 1.0 | Oscillation frequency |
| `phase` | float | 0.0-1.0 | 0.0 | Phase offset (0.25 = 90°) |
| `depth` | int | 0-100 percent | 50 | Modulation depth |

### Wave Types

| Type | Shape | Characteristics | Best For |
|------|-------|---------------|----------|
| `sine` | Smooth oscillation | Natural, continuous | Vibrato, tremolo, smooth motion |
| `triangle` | Linear rise/fall | Smooth but angular | Gentle modulation, sweeps |
| `square` | Abrupt switching | Hard transitions | Rhythmic gating, on/off effects |
| `sawtooth` | Rising/falling ramp | Stepped automation | Stepped effects, ramps |

### Frequency Guidelines

| Effect | Hz Range | Notes |
|--------|----------|-------|
| Vibrato (pitch) | 5-7 | Standard pitch modulation |
| Tremolo (volume) | 3-5 | Natural amplitude variation |
| Filter LFO | 0.2-2 | Evolving pads and textures |
| Chorus | 0.1-1 | Very slow, smooth motion |
| Rhythmic | 1-4 Hz | Tempo-synced effects |

### Depth Guidelines

| Level | Depth % | Characteristics |
|-------|---------|-----------------|
| Subtle | 5-15 | Natural vibrato, barely noticeable |
| Moderate | 20-40 | Noticeable, musical |
| Strong | 50-70 | Obvious effect |
| Extreme | 80-100 | Full-range, dramatic |

### Return Value

Generates continuous periodic CC values oscillating around base_value with specified amplitude.

### Behavior

- Starts at phase offset (0.0 = at minimum, 0.25 = at base, 0.5 = at maximum, 0.75 = at base)
- Continues indefinitely until next event (or document end)
- Frequency independent of tempo (Hz is absolute time)

### Example

```mml
# CC vibrato: 6 Hz sine at center (64), ±10% depth
[00:00.000]
- cc 1.1.wave(sine, 64, freq=6.0, depth=10)

# Pitch bend vibrato (more natural for pitch)
[00:01.000]
- pitch_bend 1.wave(sine, 8192, freq=5.5, depth=5)

# Auto-pan stereo (180° phase shift between channels)
[00:02.000]
[@]
- cc 1.10.wave(sine, 64, freq=1.5, phase=0.0, depth=80)    # Left
[@]
- cc 2.10.wave(sine, 64, freq=1.5, phase=0.5, depth=80)    # Right

# Slow filter sweep (triangle, 30 seconds per cycle)
[00:04.000]
- cc 1.74.wave(triangle, 64, freq=0.033, depth=60)

# Polyphonic pressure vibrato (per-note expression)
[00:06.000]
- poly_pressure 1.C4.wave(sine, 64, freq=3.0, depth=40)
```

### Compatibility

- **MIDI**: Works with any CC number (0-127), pitch bend (-8192 to +8191), and pressure (0-127)
- **Contexts**: CC values, pitch_bend, channel_pressure, poly_pressure
- **Polyphony**: Independent LFO per voice when applied to note velocity/expressions
- **Stacking**: Multiple LFOs can modulate different parameters simultaneously

### Error Conditions

- `InvalidValue`: base_value outside valid range
- `InvalidWaveType`: wave_type not recognized
- `InvalidFrequency`: freq outside 0.1-20.0 Hz range
- `InvalidPhase`: phase outside 0.0-1.0
- `InvalidDepth`: depth outside 0-100%

---

## envelope() - Envelope Expressions

Time-based parameter shaping following ADSR (Attack-Decay-Sustain-Release), AR, or AD envelope phases.

### Syntax - ADSR (Attack-Decay-Sustain-Release)

```mml
envelope(adsr, attack=time, decay=time, sustain=level, release=time [, curve=type])
```

**Parameters:**

| Parameter | Type | Range | Description |
|-----------|------|-------|-------------|
| `attack` | float | 0.0-60.0 s | Time to reach peak from 0 |
| `decay` | float | 0.0-60.0 s | Time from peak to sustain level |
| `sustain` | float | 0.0-1.0 | Sustain level as fraction of peak |
| `release` | float | 0.0-60.0 s | Time from sustain to 0 |
| `curve` | string | linear, exponential | Curve shape (default: linear) |

**Phases:**
1. Attack: 0 → max over `attack` seconds
2. Decay: max → (max × sustain) over `decay` seconds
3. Sustain: Holds at (max × sustain) indefinitely
4. Release: (max × sustain) → 0 over `release` seconds

**Example:**
```mml
[00:00.000]
- note_on 1.60.80 4b
- cc 1.74.envelope(adsr, attack=0.5, decay=0.3, sustain=0.7, release=1.0)
```

### Syntax - AR (Attack-Release)

```mml
envelope(ar, attack=time, release=time [, curve=type])
```

**Parameters:**

| Parameter | Type | Range | Description |
|-----------|------|-------|-------------|
| `attack` | float | 0.0-60.0 s | Time to reach peak |
| `release` | float | 0.0-60.0 s | Time from peak to 0 |
| `curve` | string | linear, exponential | Curve shape |

**Phases:**
1. Attack: 0 → max over `attack` seconds
2. Release: max → 0 over `release` seconds

**Example:**
```mml
[00:00.000]
- cc 1.74.envelope(ar, attack=0.01, release=0.2)  # Percussive hit
```

### Syntax - AD (Attack-Decay)

```mml
envelope(ad, attack=time, decay=time [, curve=type])
```

**Parameters:**

| Parameter | Type | Range | Description |
|-----------|------|-------|-------------|
| `attack` | float | 0.0-60.0 s | Time to reach peak |
| `decay` | float | 0.0-60.0 s | Time from peak to 0 |
| `curve` | string | linear, exponential | Curve shape |

**Phases:**
1. Attack: 0 → max over `attack` seconds
2. Decay: max → 0 over `decay` seconds

**Example:**
```mml
[00:00.000]
- cc 1.74.envelope(ad, attack=0.02, decay=0.5)  # Plucked string
```

### Curve Types

| Type | Behavior | Characteristics |
|------|----------|-----------------|
| `linear` | Constant rate change | Predictable, mathematical, electronic |
| `exponential` | Logarithmic rate | Natural decay/growth, organic |

### Return Value

Time-interpolated parameter values following specified envelope shape.

### Behavior

- Sustain phase continues until next event (or document end)
- Release triggered by next event or silence
- Times are in seconds; scaled to document timing resolution
- Envelope peak is target CC value (0-127); sustain is fractional

### Envelope Timing Guidelines

| Sound Type | Attack | Decay | Sustain | Release |
|-----------|--------|-------|---------|---------|
| Pad | 0.5-2.0 s | 0.2-0.5 s | 0.6-0.8 | 1.0-3.0 s |
| Pluck | 0.01-0.05 s | 0.1-0.5 s | — | — |
| Percussion | 0.001-0.01 s | — | — | 0.05-0.2 s |
| Brass | 0.05-0.1 s | 0.1-0.2 s | 0.7-0.9 | 0.1-0.3 s |
| Strings | 0.1-0.3 s | 0.2-0.4 s | 0.8-0.9 | 0.3-1.0 s |

### Example

```mml
# CC: Synth pad filter with slow attack, smooth sustain, long release
[00:00.000]
- note_on 1.60.80 4b
- cc 1.74.envelope(adsr, attack=1.0, decay=0.3, sustain=0.75, release=2.0, curve=exponential)

# CC: Percussive hit with instant attack, quick decay
[00:04.000]
- cc 1.74.envelope(ar, attack=0.005, release=0.15, curve=linear)

# Pitch bend: Pitch dive effect
[00:08.000]
- pitch_bend 1.envelope(ad, attack=0.01, decay=1.5)

# Channel pressure: Dynamic expression envelope
[00:12.000]
- note_on 1.60.100 4b
- channel_pressure 1.envelope(adsr, attack=0.2, decay=0.1, sustain=0.8, release=0.3)
```

### Compatibility

- **MIDI**: Works with any CC number (0-127), pitch bend (-8192 to +8191), and pressure (0-127)
- **Contexts**: CC values, pitch_bend, channel_pressure, poly_pressure
- **Velocity**: Can modulate note velocity for dynamic articulation
- **Stacking**: Multiple envelopes on different CCs create complex evolving textures

### Error Conditions

- `InvalidTime`: attack/decay/release outside 0-60 s
- `InvalidSustain`: sustain outside 0.0-1.0
- `InvalidCurveType`: curve_type not recognized
- `MissingParameter`: Required parameter (attack, release) not specified
- `InvalidEnvelopeType`: envelope type not adsr, ar, or ad

---

## General Modulation Behavior

### Peak Value Calculation

All modulation expressions generate values from 0 to target CC value:

```
Curve/Wave/Envelope:  0 ─────────────► target_value
CC range:             0-127
Pitch bend range:     -8192 to +8191
```

### Timing Interaction

Modulation expressions respect document timing:
- **Absolute timing**: Duration to next event is modulation duration
- **Musical timing**: Bars.beats.ticks converted to milliseconds using tempo
- **Relative timing**: [+time] increments from current position

### Event Generation

Modulation expressions generate intermediate events:
- Default sample rate: 100 Hz (events every 10 ms)
- Adjustable for performance vs. smoothness tradeoff
- Events respects minimum timing resolution

### Simultaneous Modulation

Multiple modulations on same event use simultaneous timing (`[@]`):

```mml
[00:00.000]
[@]
- cc 1.74.curve(30, 110, ease-out)    # Filter
[@]
- cc 1.71.curve(20, 100, ease-out)    # Resonance
```

---

## Compatibility Notes

### MIDI Limitations

- **CC Range**: 0-127 per MIDI spec
- **Pitch Bend**: -8192 to +8191 per MIDI spec (14-bit resolution)
- **Pressure**: 0-127 per MIDI spec (7-bit resolution)
- **Resolution**: 14-bit for pitch bend, 7-bit for CC and pressure
- **Sample Rate**: Default 100 Hz is sufficient for most audio (Nyquist ~50 Hz)

### Device Compatibility

Some devices may not support all modulation parameters:
- Check device documentation for CC number support
- Pitch bend support varies (most modern devices support)
- LFO frequency response depends on device processing

### Performance

- **Curve**: Minimal overhead; generates single continuous transition
- **Wave**: Continuous generation; CPU scales with frequency
- **Envelope**: Scales with sustain duration; release cleanup optimized

---

## Error Handling

### Parameter Validation

All parameters validated at parse time:
- Type checking (int vs float)
- Range validation (0-127 for CC, etc.)
- Required parameters checked

### Runtime Errors

- Invalid curve types produce parse errors
- Out-of-range values caught in validation phase
- Missing required envelope parameters flagged

### Helpful Error Messages

```
Error: Invalid curve type 'ease'
  expected: ease-in, ease-out, ease-in-out, linear, bezier(...)
  did you mean: ease-in-out?

Error: Wave frequency 25.0 Hz out of range
  expected: 0.1-20.0 Hz
```

---

## See Also

- [user-guide/modulation.md](../user-guide/modulation.md) - Tutorials, examples, and practical applications
- [cli-reference/compile.md](../cli-reference/compile.md) - CLI compilation options
- [user-guide/midi-commands.md](../user-guide/midi-commands.md) - MIDI CC numbers and pitch bend
