# MMD Example Library

Comprehensive example library demonstrating all MIDI Markdown features.

## Quick Start

```bash
# Compile any example to MIDI
mmdc compile examples/00_basics/01_hello_world.mmd

# Play back with TUI
mmdc play examples/00_basics/01_hello_world.mmd --port "IAC Driver"

# View events as table
mmdc compile examples/00_basics/01_hello_world.mmd --format table

# Export to CSV for analysis
mmdc compile examples/02_midi_features/02_cc_automation.mmd --format csv -o events.csv
```

## Categories

### 🎵 [00_basics/](00_basics/) - Start Here

Perfect for first-time users. Learn fundamental MMD concepts.

- **01_hello_world.mmd** - Absolute minimum MMD file (3 notes)
- **02_minimal_midi.mmd** - Basic MIDI commands (note_on, note_off, cc, pc)
- **03_simple_click_track.mmd** - Metronome pattern with tempo
- **04_song_structure_markers.mmd** - Text markers for song sections

**Start with**: `01_hello_world.mmd`

### ⏱️ [01_timing/](01_timing/) - Timing Paradigms

Master MML's four timing systems.

- **01_tempo_changes.mmd** - Dynamic tempo automation
- **02_musical_timing.mmd** - Bars.beats.ticks timing with time signatures
- **03_timing_paradigms.mmd** - All four timing modes demonstrated
- **04_relative_timing.mmd** - Relative delta timing patterns

**Learn about**: Absolute time, musical time, relative deltas, simultaneous events

### 🎹 [02_midi_features/](02_midi_features/) - MIDI Commands

Complete MIDI 1.0 command coverage.

- **01_multi_channel_basic.mmd** - Multiple MIDI channels
- **02_cc_automation.mmd** - Control change messages (filter, volume, pan)
- **03_pitch_bend_pressure.mmd** - Pitch bend and channel pressure
- **04_system_messages.mmd** - SysEx and system messages
- **05_bass_line.mmd** - Bass patterns and rhythms
- **06_chord_progressions.mmd** - Simultaneous notes for chords
- **07_drums_and_percussion.mmd** - GM drum map (channel 10)
- **08_midi_clock.mmd** - MIDI clock and transport control
- **09_pitch_bend_modulation.mmd** - Advanced pitch bend techniques with curves and envelopes

**Covers**: Note on/off, CC, PC, pitch bend, aftertouch, SysEx, MIDI clock, drums, chords, modulation

### 🚀 [03_advanced/](03_advanced/) - Advanced Features

Power features for complex compositions.

- **01_loops_and_patterns.mmd** - @loop directive for repetition
- **02_sweep_automation.mmd** - @sweep for parameter ramping
- **03_alias_showcase.mmd** - Complete alias system demonstration
- **04_computed_values.mmd** - Computed values and expressions
- **05_arpeggiator.mmd** - Arpeggio patterns with loops
- **06_polyrhythm.mmd** - Complex rhythmic patterns
- **07_modulation_and_expression.mmd** - CC automation techniques
- **08_modulation_showcase.mmd** - Advanced modulation (curves, waves, envelopes)
- **09_generative_pattern.mmd** - Variables and computed values
- **10_comprehensive_song.mmd** - All features combined
- **11_multi_file_project.mmd** - Organizing large projects with imports and modules
- **12_common_mistakes.mmd** - Debugging guide with intentional errors and fixes
- **13_performance_comparison.mmd** - Optimized vs naive implementations

**Master**: Loops, sweeps, aliases, variables, expressions, automation, project organization, optimization, modulation

### 🎲 [05_generative/](05_generative/) - Generative & Random Techniques

Create evolving, non-repetitive music using random() expressions and wave modulation.

- **01_random_humanization.mmd** - Add natural variations to MIDI with random velocity, note selection, and CC values
- **02_algorithmic_drums.mmd** - Professional drum patterns using random velocity, ghost notes, and polyrhythms
- **03_generative_ambient.mmd** - Evolving pad textures with random notes and LFO modulation
- **04_random_cc_automation.mmd** - Generative parameter automation for filters, resonance, pan, and expression
- **05_evolving_textures.mmd** - Complex layered textures with multiple randomization sources
- **06_scale_constrained_melody.mmd** - Generative melodies constrained to musical scales

**Techniques**: Random velocity, random note ranges, random CC values, wave modulation, layered randomization, humanization, scale constraints

### 🎸 [04_device_libraries/](04_device_libraries/) - Hardware Control

Real-world device control examples.

- **01_device_import.mmd** - @import device libraries
- **02_quad_cortex_live_set.mmd** - Neural DSP Quad Cortex presets
- **03_h90_preset_automation.mmd** - Eventide H90 automation
- **04_helix_song_switching.mmd** - Line 6 Helix snapshots
- **05_hx_stomp_pedalboard.mmd** - HX Stomp setlist
- **06_live_performance_aliases.mmd** - Multi-device live performance
- **07_hx_effects_live.mmd** - HX Effects live performance automation
- **08_hx_stomp_xl_set.mmd** - HX Stomp XL complete setlist
- **09_multi_device_orchestration.mmd** - Coordinating multiple devices in a single performance

**Devices**: Quad Cortex, H90, Helix, HX Stomp, HX Effects, HX Stomp XL

### 📚 [06_tutorials/](06_tutorials/) - Step-by-Step Learning

Progressive 4-part tutorial series.

- **01_melody.mmd** - Part 1: Simple melody
- **02_chords.mmd** - Part 2: Add chord accompaniment
- **03_drums.mmd** - Part 3: Add drum track
- **04_full_song.mmd** - Part 4: Complete production

**Follow in order** for comprehensive learning path.

## Example Count by Category

| Category | Count | Difficulty |
|----------|-------|------------|
| Basics | 4 | Beginner |
| Timing | 4 | Beginner |
| MIDI Features | 9 | Beginner-Intermediate |
| Advanced | 13 | Intermediate-Advanced |
| Generative | 6 | Intermediate-Advanced |
| Device Libraries | 9 | Intermediate |
| Tutorials | 4 | Beginner → Advanced |
| **TOTAL** | **49** | All levels |

## Running Examples

All examples are fully compilable and playable:

```bash
# Compile all examples
for file in examples/**/*.mmd; do
  mmdc compile "$file" -o output/$(basename "$file" .mmd).mid
done

# Validate all examples
mmdc validate examples/**/*.mmd

# Play an example
mmdc play examples/06_tutorials/04_full_song.mmd
```

## Learning Paths

### 📚 Beginner Track (Core Features)

1. **Start Here**: [00_basics/01_hello_world.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/00_basics/01_hello_world.mmd) - Understand basic structure
2. **Learn Timing**: [00_basics/02_minimal_midi.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/00_basics/02_minimal_midi.mmd) - See how timing works
3. **Add Commands**: [00_basics/03_simple_click_track.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/00_basics/03_simple_click_track.mmd) - Repeated patterns
4. **Structure Songs**: [00_basics/04_song_structure_markers.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/00_basics/04_song_structure_markers.mmd) - Organize with markers
5. **Automation**: [02_midi_features/02_cc_automation.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/02_midi_features/02_cc_automation.mmd) - Control parameters over time
6. **Multiple Channels**: [02_midi_features/01_multi_channel_basic.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/02_midi_features/01_multi_channel_basic.mmd) - Multi-instrument songs
7. **Full Example**: [03_advanced/10_comprehensive_song.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/03_advanced/10_comprehensive_song.mmd) - Everything together

### 🚀 Advanced Track (Power Features)

8. **Loops**: [03_advanced/01_loops_and_patterns.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/03_advanced/01_loops_and_patterns.mmd) - Eliminate repetitive code with @loop
9. **Automation**: [03_advanced/02_sweep_automation.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/03_advanced/02_sweep_automation.mmd) - Smooth parameter changes with @sweep
10. **Musical Time**: [01_timing/02_musical_timing.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/01_timing/02_musical_timing.mmd) - Work in bars/beats/ticks
11. **Timing Paradigms**: [01_timing/03_timing_paradigms.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/01_timing/03_timing_paradigms.mmd) - Master all timing modes
12. **Random Humanization**: [05_generative/01_random_humanization.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/05_generative/01_random_humanization.mmd) - Natural variations with random() expressions
13. **Generative Ambient**: [05_generative/03_generative_ambient.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/05_generative/03_generative_ambient.mmd) - Evolving pads with random notes and LFO
14. **Device Control**: [04_device_libraries/01_device_import.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/04_device_libraries/01_device_import.mmd) - High-level device commands with @import
15. **Multi-File Projects**: [03_advanced/11_multi_file_project.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/03_advanced/11_multi_file_project.mmd) - Organize large projects

### 🎸 Alias System (Advanced Abstraction)

16. **Alias Basics**: [03_advanced/03_alias_showcase.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/03_advanced/03_alias_showcase.mmd) - Complete alias system tour
17. **Real-World**: [04_device_libraries/06_live_performance_aliases.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/04_device_libraries/06_live_performance_aliases.mmd) - Production-ready performance automation

### 🎼 Musical Examples (Inspiration)

18. **Drums**: [02_midi_features/07_drums_and_percussion.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/02_midi_features/07_drums_and_percussion.mmd) - GM drum patterns
19. **Algorithmic Drums**: [05_generative/02_algorithmic_drums.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/05_generative/02_algorithmic_drums.mmd) - Professional drum pattern generation
20. **Bass**: [02_midi_features/05_bass_line.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/02_midi_features/05_bass_line.mmd) - Groove patterns
21. **Chords**: [02_midi_features/06_chord_progressions.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/02_midi_features/06_chord_progressions.mmd) - Harmonic ideas
22. **Arpeggios**: [03_advanced/05_arpeggiator.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/03_advanced/05_arpeggiator.mmd) - Arpeggiator patterns
23. **Polyrhythm**: [03_advanced/06_polyrhythm.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/03_advanced/06_polyrhythm.mmd) - Complex rhythms
24. **CC Automation**: [05_generative/04_random_cc_automation.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/05_generative/04_random_cc_automation.mmd) - Generative parameter modulation
25. **Evolving Textures**: [05_generative/05_evolving_textures.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/05_generative/05_evolving_textures.mmd) - Complex layered soundscapes
26. **Scale Melodies**: [05_generative/06_scale_constrained_melody.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/05_generative/06_scale_constrained_melody.mmd) - Musical scale constraints

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

See: [03_advanced/01_loops_and_patterns.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/03_advanced/01_loops_and_patterns.mmd)

### 📊 Sweeps (@sweep)

The @sweep feature creates smooth automation:

```mml
# Fade volume from 0 to 127 over 4 seconds with ease-in curve
@sweep cc 1.7 from 00:00.000 to 00:04.000 every 100ms
  ramp ease-in from 0 to 127
@end
```

Supports 6 ramp types: linear, exponential, logarithmic, ease-in, ease-out, ease-in-out

See: [03_advanced/02_sweep_automation.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/03_advanced/02_sweep_automation.mmd)

### 🎲 Random & Generative (random())

The random() function adds natural variation to melodies, velocity, and parameters:

```mml
# Random velocity (60-100) for humanization
- note_on 1.C4 random(60,100) 0.5b

# Random note selection from range
- note_on 1.random(C4,G4) 80 0.5b

# Random CC values for evolving automation
- cc 1.74.random(50,90)

# In loops for continuous variation
@loop 8 times at [00:16.000] every 0.25b
  - cc 1.74.random(40,100)
@end
```

Perfect for humanization, generative music, evolving pad textures, and algorithmic patterns

See: [05_generative/01_random_humanization.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/05_generative/01_random_humanization.mmd), [05_generative/03_generative_ambient.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/05_generative/03_generative_ambient.mmd), [05_generative/04_random_cc_automation.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/05_generative/04_random_cc_automation.mmd)

### 🎵 Musical Timing

Musical time keeps events in musical position:

```mml
[1.1.0]    # Bar 1, Beat 1, Tick 0
[1.2.0]    # Bar 1, Beat 2
[1.3.120]  # Bar 1, Beat 3, Tick 120 (16th note subdivision)
```

Benefits: tempo-independent, time signature aware, DAW-compatible

See: [01_timing/02_musical_timing.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/01_timing/02_musical_timing.mmd)

### 📦 Device Imports (@import)

Device libraries provide high-level control:

```mml
@import "devices/quad_cortex.mmd"

# Instead of: cc 1.32.2; cc 1.0.0; pc 1.5
# Use readable command:
- cortex_load 1.2.0.5  # Load setlist 2, scene 0, preset 5
```

Available libraries: Neural DSP Quad Cortex, Eventide H90, Line 6 Helix, HX Stomp, HX Effects, HX Stomp XL

See: [04_device_libraries/01_device_import.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/04_device_libraries/01_device_import.mmd)

## Feature Coverage

| Feature | Examples | Status |
|---------|----------|--------|
| **Timing (Absolute)** | All examples | ✅ Complete |
| **Timing (Musical)** | 02_musical_timing, 03_timing_paradigms | ✅ Complete |
| **Timing (Relative)** | Most examples, 04_relative_timing | ✅ Complete |
| **Timing (All Modes)** | 03_timing_paradigms | ✅ Complete |
| **Note Commands** | 01-04, bass, chords, drums | ✅ Complete |
| **Control Change** | 02_cc_automation, modulation | ✅ Complete |
| **Program Change** | 01_multi_channel_basic, device examples | ✅ Complete |
| **Pitch Bend** | 03_pitch_bend_pressure, 09_pitch_bend_modulation | ✅ Complete |
| **Pitch Bend Modulation** | 09_pitch_bend_modulation | ✅ Complete |
| **Pressure/Aftertouch** | 03_pitch_bend_pressure | ✅ Complete |
| **MIDI Clock** | 08_midi_clock | ✅ Complete |
| **Meta Events** | 01-04 | ✅ Complete |
| **Tempo Changes** | 01_tempo_changes | ✅ Complete |
| **Markers** | 04_song_structure_markers | ✅ Complete |
| **Variables (@define)** | generative examples | ✅ Complete |
| **Loops (@loop)** | 01_loops_and_patterns, arpeggiator, polyrhythm | ✅ Complete |
| **Sweeps (@sweep)** | 02_sweep_automation, modulation | ✅ Complete |
| **Imports (@import)** | 01_device_import, 11_multi_file_project, all device examples | ✅ Complete |
| **Aliases** | alias_showcase, device examples | ✅ Complete |
| **Multi-Channel** | 01_multi_channel_basic, tutorials | ✅ Complete |
| **SysEx** | 04_system_messages | ✅ Complete |
| **Comments** | All examples | ✅ Complete |
| **Random Expressions** | 01_random_humanization, 02_algorithmic_drums, 03_generative_ambient, 04_random_cc_automation | ✅ Complete |
| **Wave Modulation** | 03_generative_ambient, 05_evolving_textures | ✅ Complete |
| **Scale Constraints** | 06_scale_constrained_melody | ✅ Complete |
| **Project Organization** | 11_multi_file_project | ✅ Complete |
| **Debugging** | 12_common_mistakes | ✅ Complete |
| **Performance** | 13_performance_comparison | ✅ Complete |
| **Multi-Device** | 09_multi_device_orchestration | ✅ Complete |

## Creating Your Own

Use these examples as templates for your own MIDI automation:

1. **Copy an example** that matches your use case
2. **Modify the frontmatter** (title, author, etc.)
3. **Adjust timing and commands** to fit your needs
4. **Test with validation**: `mmdc validate your_file.mmd`
5. **Compile to MIDI**: `mmdc compile your_file.mmd -o output.mid`
6. **Test in your DAW** or with `mmdc play`

## Contributing Examples

Have a cool MMD example? We welcome contributions!

**Guidelines**:
1. Follow existing example format (frontmatter + inline comments)
2. Place in appropriate category directory
3. Test compilation: `mmdc compile your_example.mmd`
4. Add descriptive comments explaining concepts
5. Update this README with your example description
6. Submit PR with description of what it demonstrates

See [CONTRIBUTING.md](../developer-guide/contributing.md) for details.

## Quick Reference

| To Learn... | See Example |
|-------------|-------------|
| Basic syntax | 00_basics/01-02 |
| Timing (absolute) | 00_basics/01-04 |
| Timing (musical) | 01_timing/02_musical_timing |
| Timing (all modes) | 01_timing/03_timing_paradigms |
| Timing (relative) | 01_timing/04_relative_timing |
| Notes and durations | 00_basics/03_simple_click_track |
| CC automation | 02_midi_features/02_cc_automation |
| Tempo changes | 01_timing/01_tempo_changes |
| Multi-channel | 02_midi_features/01_multi_channel_basic |
| MIDI clock | 02_midi_features/08_midi_clock |
| Pitch bend modulation | 02_midi_features/09_pitch_bend_modulation |
| Loops | 03_advanced/01_loops_and_patterns |
| Smooth automation | 03_advanced/02_sweep_automation |
| Multi-file projects | 03_advanced/11_multi_file_project |
| Debugging | 03_advanced/12_common_mistakes |
| Performance | 03_advanced/13_performance_comparison |
| Humanization (random) | 05_generative/01_random_humanization |
| Algorithmic drums | 05_generative/02_algorithmic_drums |
| Generative ambient | 05_generative/03_generative_ambient |
| Random CC automation | 05_generative/04_random_cc_automation |
| Evolving textures | 05_generative/05_evolving_textures |
| Scale melodies | 05_generative/06_scale_constrained_melody |
| Device control | 04_device_libraries/01_device_import |
| Aliases | 03_advanced/03_alias_showcase |
| Live performance | 04_device_libraries/06_live_performance_aliases |
| Multi-device | 04_device_libraries/09_multi_device_orchestration |
| Complete song | 03_advanced/10_comprehensive_song |
| Drums | 02_midi_features/07_drums_and_percussion |
| Bass | 02_midi_features/05_bass_line |
| Chords | 02_midi_features/06_chord_progressions |
| Tutorial series | 06_tutorials/01-04 |

## See Also

- **[Quickstart Guide](../getting-started/quickstart.md)** - Get started with MML
- **[MMD Syntax Reference](../user-guide/mmd-syntax.md)** - Complete syntax documentation
- **[Tutorial: Your First Song](../getting-started/first-song.md)** - Step-by-step guide
- **[Device Library Guide](../user-guide/device-libraries.md)** - Using device libraries
- **[Specification](https://github.com/cjgdev/midi-markdown/blob/main/spec.md)** - Complete MMD language specification
- **[Alias System Guide](../user-guide/alias-system.md)** - How to use and create aliases
- **[Device Library Creation](../user-guide/device-libraries.md)** - Create your own device libraries

## Additional Resources

- **[Device Libraries](../devices/)** - Available device alias libraries (6 devices)
- **[Test Fixtures](../tests/fixtures/)** - More example files used in testing
- **[Project README](https://github.com/cjgdev/midi-markdown/blob/main/README.md)** - Project overview and installation

---

**Total Examples**: 49 files across 7 categories
**Skill Levels**: Beginner → Advanced
**Coverage**: All MMD features demonstrated
