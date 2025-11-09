# MML Example Library

Comprehensive example library demonstrating all MIDI Markup Language features.

## Quick Start

```bash
# Compile any example to MIDI
midimarkup compile examples/00_basics/00_hello_world.mml

# Play back with TUI
midimarkup play examples/00_basics/00_hello_world.mml --port "IAC Driver"

# View events as table
midimarkup compile examples/00_basics/00_hello_world.mml --format table

# Export to CSV for analysis
midimarkup compile examples/02_midi_features/06_cc_automation.mml --format csv -o events.csv
```

## Categories

### 🎵 [00_basics/](00_basics/) - Start Here

Perfect for first-time users. Learn fundamental MML concepts.

- **00_hello_world.mml** - Absolute minimum MML file (3 notes)
- **01_minimal_midi.mml** - Basic MIDI commands (note_on, note_off, cc, pc)
- **02_simple_click_track.mml** - Metronome pattern with tempo
- **03_song_structure_markers.mml** - Text markers for song sections

**Start with**: `00_hello_world.mml`

### ⏱️ [01_timing/](01_timing/) - Timing Paradigms

Master MML's four timing systems.

- **04_tempo_changes.mml** - Dynamic tempo automation
- **12_musical_timing.mml** - Bars.beats.ticks timing with time signatures

**Learn about**: Absolute time, musical time, relative deltas, simultaneous events

### 🎹 [02_midi_features/](02_midi_features/) - MIDI Commands

Complete MIDI 1.0 command coverage.

- **05_multi_channel_basic.mml** - Multiple MIDI channels
- **06_cc_automation.mml** - Control change messages (filter, volume, pan)
- **07_pitch_bend_pressure.mml** - Pitch bend and channel pressure
- **08_system_messages.mml** - SysEx and system messages
- **bass_line.mml** - Bass patterns and rhythms
- **chord_progressions.mml** - Simultaneous notes for chords
- **drums_and_percussion.mml** - GM drum map (channel 10)

**Covers**: Note on/off, CC, PC, pitch bend, aftertouch, SysEx, drums, chords

### 🚀 [03_advanced/](03_advanced/) - Advanced Features

Power features for complex compositions.

- **09_comprehensive_song.mml** - All features combined
- **10_loops_and_patterns.mml** - @loop directive for repetition
- **11_sweep_automation.mml** - @sweep for parameter ramping
- **alias_showcase.mml** - Complete alias system demonstration
- **arpeggiator.mml** - Arpeggio patterns with loops
- **generative_pattern.mml** - Variables and computed values
- **modulation_and_expression.mml** - CC automation techniques
- **polyrhythm.mml** - Complex rhythmic patterns

**Master**: Loops, sweeps, aliases, variables, expressions, automation

### 🎸 [04_device_libraries/](04_device_libraries/) - Hardware Control

Real-world device control examples.

- **13_device_import.mml** - @import device libraries
- **live_performance_aliases.mml** - Multi-device live performance
- **quad_cortex_live_set.mml** - Neural DSP Quad Cortex presets
- **h90_preset_automation.mml** - Eventide H90 automation
- **helix_song_switching.mml** - Line 6 Helix snapshots
- **hx_stomp_pedalboard.mml** - HX Stomp setlist

**Devices**: Quad Cortex, H90, Helix, HX Stomp, HX Effects, HX Stomp XL

### 📚 [05_tutorials/](05_tutorials/) - Step-by-Step Learning

Progressive 4-part tutorial series.

- **tutorial_1_melody.mml** - Part 1: Simple melody
- **tutorial_2_chords.mml** - Part 2: Add chord accompaniment
- **tutorial_3_drums.mml** - Part 3: Add drum track
- **tutorial_4_full_song.mml** - Part 4: Complete production

**Follow in order** for comprehensive learning path.

## Example Count by Category

| Category | Count | Difficulty |
|----------|-------|------------|
| Basics | 4 | Beginner |
| Timing | 2 | Beginner |
| MIDI Features | 7 | Beginner-Intermediate |
| Advanced | 8 | Intermediate-Advanced |
| Device Libraries | 6 | Intermediate |
| Tutorials | 4 | Beginner → Advanced |
| **TOTAL** | **31** | All levels |

## Running Examples

All examples are fully compilable and playable:

```bash
# Compile all examples
for file in examples/**/*.mml; do
  midimarkup compile "$file" -o output/$(basename "$file" .mml).mid
done

# Validate all examples
midimarkup validate examples/**/*.mml

# Play an example
midimarkup play examples/05_tutorials/tutorial_4_full_song.mml
```

## Learning Paths

### 📚 Beginner Track (Core Features)

1. **Start Here**: [00_basics/00_hello_world.mml](00_basics/00_hello_world.mml) - Understand basic structure
2. **Learn Timing**: [00_basics/01_minimal_midi.mml](00_basics/01_minimal_midi.mml) - See how timing works
3. **Add Commands**: [00_basics/02_simple_click_track.mml](00_basics/02_simple_click_track.mml) - Repeated patterns
4. **Structure Songs**: [00_basics/03_song_structure_markers.mml](00_basics/03_song_structure_markers.mml) - Organize with markers
5. **Automation**: [02_midi_features/06_cc_automation.mml](02_midi_features/06_cc_automation.mml) - Control parameters over time
6. **Multiple Channels**: [02_midi_features/05_multi_channel_basic.mml](02_midi_features/05_multi_channel_basic.mml) - Multi-instrument songs
7. **Full Example**: [03_advanced/09_comprehensive_song.mml](03_advanced/09_comprehensive_song.mml) - Everything together

### 🚀 Advanced Track (Power Features)

8. **Loops**: [03_advanced/10_loops_and_patterns.mml](03_advanced/10_loops_and_patterns.mml) - Eliminate repetitive code with @loop
9. **Automation**: [03_advanced/11_sweep_automation.mml](03_advanced/11_sweep_automation.mml) - Smooth parameter changes with @sweep
10. **Musical Time**: [01_timing/12_musical_timing.mml](01_timing/12_musical_timing.mml) - Work in bars/beats/ticks
11. **Device Control**: [04_device_libraries/13_device_import.mml](04_device_libraries/13_device_import.mml) - High-level device commands with @import

### 🎸 Alias System (Advanced Abstraction)

12. **Alias Basics**: [03_advanced/alias_showcase.mml](03_advanced/alias_showcase.mml) - Complete alias system tour
13. **Real-World**: [04_device_libraries/live_performance_aliases.mml](04_device_libraries/live_performance_aliases.mml) - Production-ready performance automation

### 🎼 Musical Examples (Inspiration)

14. **Drums**: [02_midi_features/drums_and_percussion.mml](02_midi_features/drums_and_percussion.mml) - GM drum patterns
15. **Bass**: [02_midi_features/bass_line.mml](02_midi_features/bass_line.mml) - Groove patterns
16. **Chords**: [02_midi_features/chord_progressions.mml](02_midi_features/chord_progressions.mml) - Harmonic ideas
17. **Arpeggios**: [03_advanced/arpeggiator.mml](03_advanced/arpeggiator.mml) - Arpeggiator patterns
18. **Polyrhythm**: [03_advanced/polyrhythm.mml](03_advanced/polyrhythm.mml) - Complex rhythms

## Feature Highlights

### 🔄 Loops (@loop)

The @loop feature eliminates repetitive code:

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

See: [03_advanced/10_loops_and_patterns.mml](03_advanced/10_loops_and_patterns.mml)

### 📊 Sweeps (@sweep)

The @sweep feature creates smooth automation:

```mml
# Fade volume from 0 to 127 over 4 seconds with ease-in curve
@sweep cc 1.7 from 00:00.000 to 00:04.000 every 100ms
  ramp ease-in from 0 to 127
@end
```

Supports 6 ramp types: linear, exponential, logarithmic, ease-in, ease-out, ease-in-out

See: [03_advanced/11_sweep_automation.mml](03_advanced/11_sweep_automation.mml)

### 🎵 Musical Timing

Musical time keeps events in musical position:

```mml
[1.1.0]    # Bar 1, Beat 1, Tick 0
[1.2.0]    # Bar 1, Beat 2
[1.3.120]  # Bar 1, Beat 3, Tick 120 (16th note subdivision)
```

Benefits: tempo-independent, time signature aware, DAW-compatible

See: [01_timing/12_musical_timing.mml](01_timing/12_musical_timing.mml)

### 📦 Device Imports (@import)

Device libraries provide high-level control:

```mml
@import "devices/quad_cortex.mml"

# Instead of: cc 1.32.2; cc 1.0.0; pc 1.5
# Use readable command:
- cortex_load 1.2.0.5  # Load setlist 2, scene 0, preset 5
```

Available libraries: Neural DSP Quad Cortex, Eventide H90, Line 6 Helix, HX Stomp, HX Effects, HX Stomp XL

See: [04_device_libraries/13_device_import.mml](04_device_libraries/13_device_import.mml)

## Feature Coverage

| Feature | Examples | Status |
|---------|----------|--------|
| **Timing (Absolute)** | All examples | ✅ Complete |
| **Timing (Musical)** | 12_musical_timing | ✅ Complete |
| **Timing (Relative)** | Most examples | ✅ Complete |
| **Note Commands** | 00-03, 05, 09-11, bass, chords, drums | ✅ Complete |
| **Control Change** | 05-06, 09, 11, modulation | ✅ Complete |
| **Program Change** | 05, 13, device examples | ✅ Complete |
| **Pitch Bend** | 07, 09, 11 | ✅ Complete |
| **Pressure/Aftertouch** | 07 | ✅ Complete |
| **Meta Events** | 01, 03-04, 09 | ✅ Complete |
| **Tempo Changes** | 04, 09, 12 | ✅ Complete |
| **Markers** | 03, 09, 10-13 | ✅ Complete |
| **Variables (@define)** | 04-05, 09-10, generative | ✅ Complete |
| **Loops (@loop)** | 10, arpeggiator, polyrhythm | ✅ Complete |
| **Sweeps (@sweep)** | 11, modulation | ✅ Complete |
| **Imports (@import)** | 13, all device examples | ✅ Complete |
| **Aliases** | alias_showcase, device examples | ✅ Complete |
| **Multi-Channel** | 05, 09, tutorials | ✅ Complete |
| **SysEx** | 08 | ✅ Complete |
| **Comments** | All examples | ✅ Complete |

## Creating Your Own

Use these examples as templates for your own MIDI automation:

1. **Copy an example** that matches your use case
2. **Modify the frontmatter** (title, author, etc.)
3. **Adjust timing and commands** to fit your needs
4. **Test with validation**: `midimarkup validate your_file.mml`
5. **Compile to MIDI**: `midimarkup compile your_file.mml -o output.mid`
6. **Test in your DAW** or with `midimarkup play`

## Contributing Examples

Have a cool MML example? We welcome contributions!

**Guidelines**:
1. Follow existing example format (frontmatter + inline comments)
2. Place in appropriate category directory
3. Test compilation: `midimarkup compile your_example.mml`
4. Add descriptive comments explaining concepts
5. Update this README with your example description
6. Submit PR with description of what it demonstrates

See [CONTRIBUTING.md](../docs/developer-guide/contributing.md) for details.

## Quick Reference

| To Learn... | See Example |
|-------------|-------------|
| Basic syntax | 00_basics/00-01 |
| Timing (absolute) | 00_basics/01-03 |
| Timing (musical) | 01_timing/12 |
| Notes and durations | 00_basics/02, 02_midi_features/05 |
| CC automation | 02_midi_features/06 |
| Tempo changes | 01_timing/04 |
| Multi-channel | 02_midi_features/05 |
| Loops | 03_advanced/10 |
| Smooth automation | 03_advanced/11 |
| Device control | 04_device_libraries/13 |
| Aliases | 03_advanced/alias_showcase |
| Live performance | 04_device_libraries/live_performance |
| Complete song | 03_advanced/09 |
| Drums | 02_midi_features/drums_and_percussion |
| Bass | 02_midi_features/bass_line |
| Chords | 02_midi_features/chord_progressions |
| Tutorial series | 05_tutorials/tutorial_1-4 |

## See Also

- **[Quickstart Guide](../docs/getting-started/quickstart.md)** - Get started with MML
- **[MML Syntax Reference](../docs/user-guide/mml-syntax.md)** - Complete syntax documentation
- **[Tutorial: Your First Song](../docs/getting-started/first-song.md)** - Step-by-step guide
- **[Device Library Guide](../docs/user-guide/device-libraries.md)** - Using device libraries
- **[Specification](../spec.md)** - Complete MML language specification
- **[Alias System Guide](../docs/alias_system_guide.md)** - How to use and create aliases
- **[Device Library Creation](../docs/device_library_creation.md)** - Create your own device libraries

## Additional Resources

- **[Device Libraries](../devices/)** - Available device alias libraries (6 devices)
- **[Test Fixtures](../tests/fixtures/)** - More example files used in testing
- **[Project README](../README.md)** - Project overview and installation

---

**Total Examples**: 31 files across 6 categories
**Skill Levels**: Beginner → Advanced
**Coverage**: All MML features demonstrated
