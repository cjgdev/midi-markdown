# Frequently Asked Questions (FAQ)

> **Audience**: All users
> **Level**: Beginner to Advanced

Quick answers to common questions about MIDI Markdown.

---

## General Questions

### What is MIDI Markdown (MMD)?

MML is a human-readable, text-based format for creating MIDI sequences. It uses Markdown-inspired syntax to define MIDI events with precise timing, making it ideal for:

- **Live performance automation** (controlling hardware devices like Neural DSP Quad Cortex, Eventide H90)
- **DAW composition** (creating MIDI files for import)
- **MIDI scripting** (programmatic MIDI generation)
- **Education** (learning MIDI concepts in a readable format)

Think of it as "Markdown for MIDI" - easy to write, easy to read, easy to version control.

---

### How is MMD different from ABC notation or LilyPond?

| Feature | MMD | ABC Notation | LilyPond |
|---------|-----|--------------|----------|
| **Focus** | MIDI automation | Sheet music | Professional engraving |
| **Target** | Hardware devices, DAWs | Folk music notation | Classical sheet music |
| **MIDI Coverage** | Complete (all MIDI commands) | Basic (notes, chords) | Complete but complex |
| **Timing** | Absolute/musical/relative | Musical only | Musical only |
| **CC Automation** | ✅ Full support | ❌ No | ⚠️ Limited |
| **Device Control** | ✅ Built-in aliases | ❌ No | ❌ No |
| **Learning Curve** | Gentle | Gentle | Steep |

**Summary**: MMD is purpose-built for MIDI performance and automation, not sheet music notation.

---

### Can I use MMD for live performance?

**Yes!** This is MML's primary use case. Features designed for live performance:

- **Real-time playback** - `mmdc play` sends MIDI to hardware in real-time
- **Device libraries** - Pre-built commands for Quad Cortex, H90, Helix, etc.
- **Precise timing** - Sub-5ms scheduling accuracy
- **Aliases** - Create shortcuts for complex preset changes
- **Loops and patterns** - Repeat sections without duplication

**Example live setup**:
```yaml
# Load preset on Quad Cortex during song intro
[00:00.000]
- cortex_load 1.2.3.5  # Setlist 2, Group 3, Preset 5

# Switch to different preset at chorus
[00:32.000]
- cortex_load 1.2.4.2  # Setlist 2, Group 4, Preset 2
```

See: [Live Performance Tutorial](../tutorials/live-performance.md) (coming soon)

---

### What MIDI devices are supported?

**All MIDI devices are supported** because MMD generates standard MIDI. However, some devices have **device libraries** with pre-built aliases:

**Currently available**:
- Neural DSP Quad Cortex (86 aliases)
- Eventide H90 (61 aliases)
- Line 6 Helix Floor/LT/Rack (49 aliases)
- Line 6 HX Effects (40+ aliases)
- Line 6 HX Stomp (39 aliases)
- Line 6 HX Stomp XL (40+ aliases)

**Don't see your device?** You can:
1. Use raw MIDI commands (PC, CC, SysEx)
2. Create your own device library (see [Device Library Creation Guide](../user-guide/device-libraries.md))

---

### Is MMD free and open source?

**Yes!** MMD is MIT licensed and completely free:

- ✅ Use commercially without restrictions
- ✅ Modify and distribute freely
- ✅ No attribution required (but appreciated!)
- ✅ Open source on GitHub

**Source code**: [github.com/cjgdev/midi-markdown](https://github.com/cjgdev/midi-markdown)

---

## Installation & Setup

### How do I install MML?

**Option 1: pipx (recommended)**:
```bash
pipx install midi-markdown
```

**Option 2: pip**:
```bash
pip install midi-markdown
```

**Option 3: Standalone executable**:
Download from [GitHub Releases](https://github.com/cjgdev/midi-markdown/releases) (no Python required).

See: [Installation Guide](../getting-started/installation.md)

---

### What operating systems are supported?

MML works on all major platforms:

- ✅ **macOS** (10.14+)
- ✅ **Linux** (Ubuntu, Debian, Fedora, Arch)
- ✅ **Windows** (10/11)

Real-time MIDI playback requires:
- **macOS**: IAC Driver (built-in)
- **Linux**: ALSA (`libasound2-dev`)
- **Windows**: Virtual MIDI port (loopMIDI recommended)

See: [Troubleshooting MIDI Playback](troubleshooting.md#midi-playback-issues)

---

### Can I use MMD without Python installed?

**Yes!** Download the standalone executable from GitHub Releases:

- No Python installation required
- No dependencies to manage
- Self-contained binary for your platform
- Same features as pip-installed version

---

## Syntax & Language

### Do I have to use YAML frontmatter?

**Yes**, frontmatter is required for document metadata:

```yaml
---
title: "My Song"
ppq: 480
---
```

**Minimum required**:
- `ppq` - Pulses per quarter note (timing resolution)

**Commonly used**:
- `title`, `author` - Metadata stored in MIDI file
- `tempo` - Initial tempo (can also be set with `tempo` command)
- `time_signature` - Required for musical timing (`[1.1.0]`)
- `midi_format` - 0 (single track), 1 (multi-track), 2 (patterns)

---

### Can I use note names instead of MIDI numbers?

**Yes!** MMD supports standard note names:

```yaml
# ✅ All of these are equivalent (MIDI note 60 = C4)
- note_on 1.60 80 1000ms
- note_on 1.C4 80 1000ms
- note_on 1.B#3 80 1000ms  # Enharmonic equivalent
```

**Supported formats**:
- `C4`, `D5`, `A#3`, `Gb2` (sharps and flats)
- Octave range: C-1 to G9 (MIDI 0-127)
- Middle C = C4 = MIDI note 60

---

### What timing formats are supported?

MML supports **four timing paradigms**:

**1. Absolute timecode** (most common):
```yaml
[00:01.500]  # 1.5 seconds from start
[01:23.250]  # 1 minute 23.25 seconds
```

**2. Musical time** (bars.beats.ticks):
```yaml
[1.1.0]      # Bar 1, Beat 1, Tick 0
[4.3.240]    # Bar 4, Beat 3, Tick 240
```

**3. Relative delta** (from previous event):
```yaml
[+500ms]     # 500ms after previous event
[+2b]        # 2 beats after previous event
[+1.2.0]     # 1 bar, 2 beats after previous
```

**4. Simultaneous** (same time as previous):
```yaml
[@]          # Execute at same time as previous event
```

See: [Timing System Guide](../user-guide/timing-system.md)

---

### How do I add comments?

**Single-line comments** (like Python, Bash):
```yaml
# This is a comment
- note_on 1.60 80 1000ms  # Inline comment
```

**Multi-line comments** (like C, JavaScript):
```yaml
/*
This is a multi-line comment
spanning multiple lines
*/
```

---

### Can I split my MMD file into multiple files?

**Yes!** Use `@import` to include other files:

```yaml
# Import device library
@import "devices/quad_cortex.mmd"

# Import shared song sections
@import "sections/verse.mmd"
@import "sections/chorus.mmd"
```

**Import paths** are relative to the current file.

**Use cases**:
- Device library sharing
- Song section organization
- Alias library reuse

---

## Features & Capabilities

### Can I create loops or repeated patterns?

**Yes!** Use `@loop` directive:

```yaml
@loop 4  # Repeat 4 times
  [+1b]
  - note_on 10.36 100 100ms  # Kick
  [+1b]
  - note_on 10.38 80 100ms   # Snare
@end
```

**Features**:
- Timing accumulates automatically
- Supports variable substitution
- Nest loops up to reasonable depth

See: [Loops Example](https://github.com/cjgdev/midi-markdown/blob/main/examples/03_advanced/01_loops_and_patterns.mmd)

---

### Can I automate CC parameters (filters, reverb, etc.)?

**Yes!** Use `cc` (control change) commands:

```yaml
# Manual CC automation
[00:00.000]
- cc 1.74.0      # Filter closed

[00:02.000]
- cc 1.74.127    # Filter open

# Automated sweep
[00:00.000]
@sweep 1.74 0 127 4000ms linear  # 4-second filter sweep
```

**Common CC numbers**:
- 1: Modulation wheel
- 7: Volume
- 10: Pan
- 11: Expression
- 74: Brightness/Filter cutoff
- 91: Reverb
- 93: Chorus

See: [MIDI CC Reference](../user-guide/midi-commands.md#control-change)

---

### Can I send SysEx messages?

**Yes!** Use `sysex` command:

```yaml
[00:00.000]
- sysex F0.43.10.4C.00.00.7E.00.F7
```

**Format**: Hexadecimal bytes separated by dots.

**Use cases**:
- Device-specific configuration
- Patch dumps
- Custom device control

---

### Can I create my own aliases for my devices?

**Yes!** Aliases are a core MMD feature:

```yaml
@alias my_preset {channel}.{preset_num}
  - cc {channel}.0.0
  - pc {channel}.{preset_num}
@end

# Use it
[00:00.000]
- my_preset 1.5
```

**Advanced features**:
- Parameter types (note, percent, enum)
- Default values
- Nested aliases
- Conditional logic

See: [Alias System Guide](../user-guide/alias-system.md)

---

### Does MMD support MIDI 2.0?

**Not yet.** MMD currently generates **MIDI 1.0** files (the standard supported by all devices).

MIDI 2.0 support is planned for a future release.

---

## Random Functions (Phase 6)

### What is random() and how do I use it?

`random()` generates random numbers within a specified range for creating variation in MIDI sequences. Use it to add humanization, randomness, or generative patterns without manual variation:

```yaml
# Random velocity
- note_on 1.60 random(60, 100) 1b

# Random CC values
- cc 1.74.random(0, 127)
```

The basic syntax is `random(min, max)` where both values are inclusive integers (0-127 for MIDI values).

---

### Where can I use random() expressions?

`random()` works in **command parameters** where numeric values are expected:

- **Velocity**: `note_on 1.60 random(60, 100) 1b`
- **CC values**: `cc 1.74.random(0, 127)`
- **Note numbers**: `note_on 1.random(48, 72) 80 0.5b`
- **Pitch bend**: `pitch_bend 1.random(-2000, 2000)`
- **Multiple per command**: `note_on 1.random(60, 72) random(70, 90) 0.5b`

See: [Random Expressions Reference](./random-expressions.md)

---

### Why doesn't random() work in timing/duration/define?

`random()` is designed for **MIDI parameter values** (velocity, CC, notes), not for **timing control**. Timing must be deterministic (known in advance) to:

- Schedule events correctly
- Synchronize with hardware devices
- Support live performance playback

If you need randomized timing, use multiple loops with fixed timing instead, or create separate variations of your sequence.

---

### How do I make random patterns reproducible?

Use the **seed parameter** in `random()` calls to make generation reproducible:

```yaml
# Same seed = same random sequence every time
@loop 8
  [+1b]
  - note_on 1.random(48, 72, seed=42) random(60, 100, seed=42) 0.5b
@end
```

Without a seed, each `random()` call generates a different value. With `seed=N`, the same seed always produces the same value for that call.

See: [Random Expressions Guide](./random-expressions.md#seed-parameter)

---

### Can I combine random() with modulation features?

**Yes!** You can use random values in notes and CC values while using modulation for automation:

```yaml
# Random notes with wave modulation
[00:00.000]
- note_on 1.random(48, 72) 80 2b
- cc 1.74.wave(sine, 70, freq=0.5, depth=30)

# Random CC with fixed value
[00:02.000]
- cc 1.74.random(40, 90)
```

However, you **cannot** use random values for timing or modulation parameters (frequency, depth, duration) - those must be deterministic.

See: [Modulation Guide](../user-guide/modulation.md) and [Random Expressions](./random-expressions.md#combining-random-with-modulation)

---

### What's the difference between random() and wave() modulation?

**random()** and **wave()** serve different purposes:

| Feature | random() | wave() |
|---------|----------|--------|
| **Purpose** | Introduce unpredictability | Create periodic oscillation |
| **Pattern** | Unpredictable variation | Repeating waveform (sine/square/triangle) |
| **Use case** | Humanization, generative patterns | Tremolo, vibrato, LFO-style modulation |
| **Determinism** | With seed (reproducible) | Always repeating (deterministic) |
| **MIDI application** | Velocity, CC values, notes | CC automation, pitch bend effects |

**Example comparison**:
```yaml
# random() - unpredictable
- cc 1.74.random(20, 100)  # Each call is different

# wave() - periodic
- cc 1.74.wave(sine, 60, freq=1.0, depth=20)  # Smooth oscillation
```

See: [Modulation Guide](../user-guide/modulation.md) and [Generative Music Guide](../user-guide/generative-music.md)

---

## Computed Values in Aliases (Stage 4)

### How do computed value blocks work in aliases?

Computed value blocks allow aliases to calculate parameter values dynamically at expansion time:

```yaml
@alias scaled_cc {ch}.{param}.{input:0-100}
  - cc {ch}.{param}.{computed = (${input} * 127 / 100)}
@end

# Use it - scales 0-100% input to 0-127 MIDI range
[00:00.000]
- scaled_cc 1.7.75  # 75% of volume = MIDI value 95
```

Computed values bridge the gap between human-readable parameters and MIDI values, enabling powerful abstractions.

---

### What expressions can I use in computed values?

Computed values support **arithmetic expressions** with the following operations:

- **Arithmetic**: `+`, `-`, `*`, `/` (standard order of operations)
- **Parentheses**: `(expression)` for grouping
- **Integer division**: Results automatically rounded/truncated
- **Parameter references**: `${param_name}` to reference other parameters

```yaml
@alias ramped_cc {ch}.{param}.{start:0-100}.{end:0-100}.{time_ms}
  - cc {ch}.{param}.{computed = (${start} * 127 / 100)}
  @sweep {ch}.{param} ${computed} {computed = (${end} * 127 / 100)} {time_ms}ms linear
@end
```

See: [Alias System Guide](../user-guide/alias-system.md#computed-values)

---

## Modulation Features (Stage 7)

### When should I use curve vs wave vs envelope?

**curve()** - Smooth transitions between values:
```yaml
@sweep 1.74 0 127 5000ms curve ease-in  # Natural-sounding filter sweep
```

**wave()** - Repeating oscillation (LFO-style):
```yaml
@modulate wave sine 1.1.0 0.5s 8  # Vibrato (0.5s period, 8 Hz)
```

**envelope()** - Amplitude shaping (ADSR-style, future):
```yaml
@envelope 1.1.0 attack:100ms decay:200ms sustain:80 release:500ms
```

Use **curve** for organic transitions, **wave** for oscillating effects, and **envelope** for complex amplitude shaping.

---

### How do I create vibrato or tremolo effects?

**Vibrato** (pitch modulation) using pitch bend:
```yaml
[00:00.000]
- note_on 1.60 80 2000ms
- @modulate wave sine 1.pb 0.5s 5  # 5Hz vibrato
```

**Tremolo** (volume modulation) using CC 7 (volume):
```yaml
[00:00.000]
- note_on 1.60 80 2000ms
- @modulate wave sine 1.7.0 0.3s 4  # 4Hz tremolo
```

Both use `@modulate wave sine` with different CC channels and frequencies. Adjust the period (0.5s, 0.3s) and PPQ for different rates.

---

### Can I layer multiple modulations?

**Yes!** Stack multiple `@modulate` directives for complex effects:

```yaml
[00:00.000]
- note_on 1.60 80 3000ms

# Layer 1: Vibrato (pitch bend)
- @modulate wave sine 1.pb 0.4s 6

# Layer 2: Tremolo (volume)
- @modulate wave sine 1.7.0 1.2s 2

# Layer 3: Filter sweep (automation)
- @sweep 1.74 30 100 3000ms linear
```

Each modulation runs independently in parallel, creating complex, expressive sounds. Start simple and add layers gradually to avoid overwhelming the effect.

---

## Workflow & Integration

### Can I version control my MMD files?

**Yes! This is a major advantage of text-based formats.**

```bash
git add song.mmd
git commit -m "Added chorus section"
git push
```

**Benefits**:
- Track changes over time
- Collaborate with others
- Branching for variations
- Code review for complex sequences

---

### Can I convert existing MIDI files to MML?

**Not yet.** MIDI → MMD conversion is planned for a future release.

**Workaround**: Use `mmdc inspect` to view MIDI file contents and manually recreate in MML:

```bash
mmdc inspect existing.mid
```

---

### Can I use MMD with my DAW?

**Yes!** Compile to MIDI and import:

```bash
mmdc compile song.mmd -o output.mid
```

Then drag `output.mid` into your DAW:
- Ableton Live
- FL Studio
- Logic Pro
- Pro Tools
- Cubase
- Reaper
- Any MIDI-compatible DAW

---

### Can I trigger MMD playback from another application?

**Yes!** Use the CLI in scripts:

```bash
# Shell script
mmdc play setlist/song1.mmd --port "IAC Driver"

# Python script
import subprocess
subprocess.run(["mmdc", "play", "song.mmd", "--port", "IAC Driver"])
```

**Use cases**:
- Automated setlist playback
- MIDI sequencer integration
- Live performance scripting

---

## Performance & Optimization

### How fast is MMD compilation?

**Very fast!** Performance benchmarks:

- Small files (<100 events): <50ms
- Medium files (100-500 events): <200ms
- Large files (1000+ events): <1s

**Tips for faster compilation**:
- Use `mmdc check` for syntax-only validation (faster)
- Break large files into sections with `@import`
- Use `--dry-run` flag to skip file writing

See: [Performance Benchmarks](../../benchmarks/)

---

### How accurate is real-time MIDI playback?

**Sub-5ms scheduling accuracy** with hybrid sleep/busy-wait algorithm.

**Measured latency**: <2ms average on modern hardware.

**Good enough for**:
- Live performance
- Tight MIDI synchronization
- Multi-device setups

**Not suitable for**:
- Audio synthesis (use DAW for sub-millisecond precision)

---

### Can I compile very large files (10,000+ events)?

**Yes**, but compile time increases linearly with event count.

**Best practices for large files**:
- Use `@loop` to reduce source file size
- Split into multiple files with `@import`
- Consider multi-track format (`midi_format: 1`)

---

## Troubleshooting

### Why am I getting parse errors?

**Common causes**:

1. **Invalid syntax** - Check command spelling
2. **Out-of-range values** - MIDI values must be 0-127
3. **Missing frontmatter** - File must start with `---`
4. **Timing errors** - Events must be chronologically ordered

See: [Troubleshooting Guide](troubleshooting.md)

---

### Why is there no sound when I play?

**Checklist**:

1. **MIDI port configured?**
   ```bash
   mmdc play --list-ports  # List available ports
   ```

2. **Port selected?**
   ```bash
   mmdc play song.mmd --port "Your Port Name"
   ```

3. **Instruments loaded?** (in DAW)
   - Assign synths to MIDI channels

4. **Permissions?** (Linux)
   ```bash
   sudo usermod -a -G audio $USER  # Add to audio group
   ```

See: [MIDI Playback Troubleshooting](troubleshooting.md#midi-playback-issues)

---

### Why do my notes sound robotic?

**Problem**: Using exact velocities and no expression.

**Solution**: Add variation and expression:

```yaml
# ❌ Robotic
- note_on 1.60 80 1000ms
- note_on 1.62 80 1000ms
- note_on 1.64 80 1000ms

# ✅ Expressive
- note_on 1.60 75 1000ms   # Vary velocity
- note_on 1.62 82 1000ms
- note_on 1.64 78 1000ms

# Add modulation
[00:01.000]
- cc 1.1.30  # Modulation wheel

# Add pitch bend
[00:02.000]
- pb 1.100   # Slight pitch bend
```

**Humanization tips**:
- Vary velocity (70-85 instead of constant 80)
- Add subtle CC automation (modulation, expression)
- Use pitch bend for expression
- Vary note durations slightly

---

## Getting Help

### Where can I find more examples?

Check the `examples/` directory in the project:

- `00_hello_world.mmd` - Simplest possible file
- `01-08` - Feature-specific examples
- `09_comprehensive_song.mmd` - Complete song demonstration
- `10-13` - Advanced features (loops, sweeps, musical timing, imports)
- `alias_showcase.mmd` - Alias system demonstration
- `live_performance_aliases.mmd` - Real-world live performance

---

### Where can I get help or report bugs?

**GitHub Issues**: [github.com/cjgdev/midi-markdown/issues](https://github.com/cjgdev/midi-markdown/issues)

**Before posting**:
1. Check [Troubleshooting Guide](troubleshooting.md)
2. Search existing issues
3. Include MMD file and error message
4. Specify version: `mmdc version`

---

### How can I contribute?

**Contributions welcome!**

- 🐛 Report bugs
- 💡 Suggest features
- 📝 Improve documentation
- 🎸 Create device libraries
- 💻 Submit pull requests

See: [Contributing Guide](../developer-guide/contributing.md)

---

### Is there a community forum or Discord?

**Not yet.** For now, use GitHub Issues for questions and discussions.

A Discord server may be created if there's sufficient community interest.

---

## See Also

- [Quickstart Guide](../getting-started/quickstart.md) - 5-minute introduction
- [First Song Tutorial](../getting-started/first-song.md) - Step-by-step song creation
- [Troubleshooting Guide](troubleshooting.md) - Common issues and solutions
- [CLI Reference](../cli-reference/overview.md) - All commands documented
- [MML Syntax Guide](../user-guide/mmd-syntax.md) - Complete syntax reference

---

**Still have questions?** [Open an issue on GitHub](https://github.com/cjgdev/midi-markdown/issues) or check the [documentation](../index.md).
