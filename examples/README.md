# MIDI Markdown Examples

This directory contains example MML files demonstrating various features of MIDI Markdown, organized from beginner to advanced.

## Example Files

### Beginner Examples (00-03)

- **[00_hello_world.mml](00_hello_world.mml)** - The simplest possible MML file (single note)
- **[01_minimal_midi.mml](01_minimal_midi.mml)** - Basic metadata and meta events
- **[02_simple_click_track.mml](02_simple_click_track.mml)** - Metronome/click track with repeated notes
- **[03_song_structure_markers.mml](03_song_structure_markers.mml)** - Song sections with markers

### Intermediate Examples (04-07)

- **[04_tempo_changes.mml](04_tempo_changes.mml)** - Dynamic tempo automation throughout a song
- **[05_multi_channel_basic.mml](05_multi_channel_basic.mml)** - Multiple MIDI channels (synth, bass, drums)
- **[06_cc_automation.mml](06_cc_automation.mml)** - Control Change automation (volume, pan, modulation, filter)
- **[07_pitch_bend_pressure.mml](07_pitch_bend_pressure.mml)** - Pitch bend and aftertouch examples

### Advanced Examples (08-09)

- **[08_system_messages.mml](08_system_messages.mml)** - SysEx, system common, and real-time messages
- **[09_comprehensive_song.mml](09_comprehensive_song.mml)** - Full song combining all features

### Feature-Specific Examples (10-13)

- **[10_loops_and_patterns.mml](10_loops_and_patterns.mml)** - **NEW!** Loop patterns with @loop (click tracks, rhythms, polyrhythms)
- **[11_sweep_automation.mml](11_sweep_automation.mml)** - **NEW!** Smooth parameter automation with @sweep (fades, filter sweeps, ramp types)
- **[12_musical_timing.mml](12_musical_timing.mml)** - **NEW!** Musical time notation [bars.beats.ticks] (tempo-independent positioning)
- **[13_device_import.mml](13_device_import.mml)** - **NEW!** Device library imports with @import (Quad Cortex, H90, Helix, Kemper)

### Alias System Examples

- **[alias_showcase.mml](alias_showcase.mml)** - Complete alias system feature demonstration (parameter types, conditionals, nesting, computed values)
- **[live_performance_aliases.mml](live_performance_aliases.mml)** - Real-world live performance automation with Quad Cortex

## Feature Coverage

| Feature | Examples | Status |
|---------|----------|--------|
| **Timing (Absolute)** | All examples | ✅ Complete |
| **Timing (Musical)** | 12 | ✅ Complete |
| **Note Commands** | 00, 02, 05, 09, 10 | ✅ Complete |
| **Control Change** | 05, 06, 09, 11 | ✅ Complete |
| **Pitch Bend** | 07, 09, 11 | ✅ Complete |
| **Pressure/Aftertouch** | 07 | ✅ Complete |
| **Meta Events** | 01, 03, 04, 09 | ✅ Complete |
| **Tempo Changes** | 04, 09, 12 | ✅ Complete |
| **Markers** | 03, 09, 10-13 | ✅ Complete |
| **Variables (@define)** | 04, 05, 09, 10 | ✅ Complete |
| **Loops (@loop)** | **10** | ✅ Complete |
| **Sweeps (@sweep)** | **11** | ✅ Complete |
| **Imports (@import)** | **13** | ✅ Complete |
| **Aliases** | alias_showcase, live_performance_aliases | ✅ Complete |
| **Multi-Channel** | 05, 09 | ✅ Complete |
| **SysEx** | 08 | ✅ Complete |
| **Comments** | All examples | ✅ Complete |

## Running Examples

### Compile to MIDI

```bash
midimarkup compile examples/00_hello_world.mml -o output.mid
```

### Validate Syntax

```bash
midimarkup validate examples/04_tempo_changes.mml
```

### Check Syntax Only

```bash
midimarkup check examples/09_comprehensive_song.mml
```

### Try New Features

```bash
# Loop patterns (replaces manual repetition)
midimarkup compile examples/10_loops_and_patterns.mml -o loops.mid

# Smooth automation with different ramp curves
midimarkup compile examples/11_sweep_automation.mml -o sweeps.mid

# Tempo-independent musical timing
midimarkup compile examples/12_musical_timing.mml -o musical.mid

# Device-specific control with imports
midimarkup compile examples/13_device_import.mml -o device_control.mid
```

## Learning Path

### 📚 Beginner Track (Core Features)

1. **Start Here**: [00_hello_world.mml](00_hello_world.mml) - Understand basic structure
2. **Learn Timing**: [01_minimal_midi.mml](01_minimal_midi.mml) - See how timing works
3. **Add Commands**: [02_simple_click_track.mml](02_simple_click_track.mml) - Repeated patterns
4. **Structure Songs**: [03_song_structure_markers.mml](03_song_structure_markers.mml) - Organize with markers
5. **Automation**: [06_cc_automation.mml](06_cc_automation.mml) - Control parameters over time
6. **Multiple Channels**: [05_multi_channel_basic.mml](05_multi_channel_basic.mml) - Multi-instrument songs
7. **Full Example**: [09_comprehensive_song.mml](09_comprehensive_song.mml) - Everything together

### 🚀 Advanced Track (Power Features)

8. **Loops**: [10_loops_and_patterns.mml](10_loops_and_patterns.mml) - Eliminate repetitive code with @loop
9. **Automation**: [11_sweep_automation.mml](11_sweep_automation.mml) - Smooth parameter changes with @sweep
10. **Musical Time**: [12_musical_timing.mml](12_musical_timing.mml) - Work in bars/beats/ticks
11. **Device Control**: [13_device_import.mml](13_device_import.mml) - High-level device commands with @import

### 🎸 Alias System (Advanced Abstraction)

12. **Alias Basics**: [alias_showcase.mml](alias_showcase.mml) - Complete alias system tour
13. **Real-World**: [live_performance_aliases.mml](live_performance_aliases.mml) - Production-ready performance automation

## Feature Highlights

### 🔄 Loops (@loop)

The @loop feature (introduced in Example 10) eliminates repetitive code:

**Before (manual repetition):**
```mml
- note_on 1.42 100 0.1s
[+1b]
- note_on 1.42 100 0.1s
[+1b]
- note_on 1.42 100 0.1s
[+1b]
# ... repeat 13 more times
```

**After (using @loop):**
```mml
@loop 16 times every 1b
  - note_on 1.42 100 0.1s
@end
```

### 📊 Sweeps (@sweep)

The @sweep feature (introduced in Example 11) creates smooth automation:

```mml
# Fade volume from 0 to 127 over 4 seconds with ease-in curve
@sweep cc 1.7 from 00:00.000 to 00:04.000 every 100ms
  ramp ease-in from 0 to 127
@end
```

Supports 6 ramp types: linear, exponential, logarithmic, ease-in, ease-out, ease-in-out

### 🎵 Musical Timing

Musical time (introduced in Example 12) keeps events in musical position:

```mml
[1.1.0]    # Bar 1, Beat 1, Tick 0
[1.2.0]    # Bar 1, Beat 2
[1.3.120]  # Bar 1, Beat 3, Tick 120 (16th note subdivision)
```

Benefits: tempo-independent, time signature aware, DAW-compatible

### 📦 Device Imports (@import)

Device libraries (introduced in Example 13) provide high-level control:

```mml
@import "devices/quad_cortex.mml"

# Instead of: cc 1.32.2; cc 1.0.0; pc 1.5
# Use readable command:
- cortex_load 1.2.0.5  # Load setlist 2, scene 0, preset 5
```

Available libraries: Neural DSP Quad Cortex, Eventide H90, Kemper Profiler, Line 6 Helix

## Creating Your Own

Use these examples as templates for your own MIDI automation:

1. Copy an example that matches your use case
2. Modify the frontmatter (title, author, etc.)
3. Adjust timing and commands to fit your needs
4. Test with `midimarkup validate`
5. Compile to MIDI and test in your DAW

## Contributing

Have a great example to share? Please contribute by:

1. Creating a new numbered example (14+)
2. Adding comprehensive comments
3. Including a description in this README
4. Testing thoroughly

## Additional Resources

- **[Specification](../spec.md)** - Complete MML language specification
- **[Device Libraries](../devices/)** - Available device alias libraries
- **[Alias System Guide](../docs/alias_system_guide.md)** - How to use and create aliases
- **[Device Library Creation](../docs/device_library_creation.md)** - Create your own device libraries

## Quick Reference

| To Learn... | See Example |
|-------------|-------------|
| Basic syntax | 00, 01 |
| Timing (absolute) | 01, 02, 03 |
| Timing (musical) | **12** |
| Notes and durations | 02, 05, 09 |
| CC automation | 06 |
| Tempo changes | 04, 12 |
| Multi-channel | 05, 09 |
| Loops | **10** |
| Smooth automation | **11** |
| Device control | **13** |
| Aliases | alias_showcase |
| Live performance | live_performance_aliases |
| Complete song | 09 |
