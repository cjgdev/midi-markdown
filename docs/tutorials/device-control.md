# Tutorial: Live Performance Device Control

**Level**: Intermediate/Advanced
**Estimated Time**: 2-3 hours
**Prerequisites**: Completed [Multi-Channel Tutorial](multi-channel.md), own hardware MIDI device

## Goal

In this tutorial, you will learn how to:
- Control hardware devices (Quad Cortex, H90, Helix) during live performance
- Import and use device libraries
- Automate preset changes and effect switches
- Coordinate device changes with backing tracks
- Handle timing delays required by hardware
- Create complete live performance sequences

By the end, you'll have a working MMD file that controls your guitar processor or effects unit in sync with a backing track.

## Prerequisites

Before starting this tutorial, you should:
- Have completed the [Multi-Channel Tutorial](multi-channel.md)
- Own a MIDI-controllable device (Neural DSP Quad Cortex, Eventide H90, Line 6 Helix, etc.)
- Understand your device's MIDI implementation
- Have MIDI cables or USB-MIDI connection
- Know your device's MIDI channel (usually channel 1)

## What You'll Build

You'll create a live performance sequence with:
- Automated preset changes for song sections
- Scene/snapshot switching for variations
- Expression pedal automation for swells
- Footswitch control for effects
- Proper timing delays for reliable operation
- Real-world performance scenarios

## Supported Devices

This tutorial covers:
- **Neural DSP Quad Cortex** (`devices/quad_cortex.mmd`) - 86 aliases
- **Eventide H90** (`devices/eventide_h90.mmd`) - 61 aliases
- **Line 6 Helix** (`devices/helix.mmd`) - 49 aliases
- **Line 6 HX Stomp** (`devices/hx_stomp.mmd`) - 39 aliases

Choose the section that matches your device, or follow the Quad Cortex example and adapt for your device.

## Step 1: Understanding Device Libraries

Device libraries provide human-readable aliases for complex MIDI commands.

**Without device library (raw MIDI):**
```markdown
# What does this do? Hard to read!
[00:00.000]
- cc 1.32.2      # Bank select MSB
[00:00.100]
- cc 1.0.0       # Bank select LSB
[00:00.200]
- pc 1.5         # Program change
```

**With device library (alias):**
```markdown
# Clear and self-documenting!
@import "../devices/quad_cortex.mmd"

[00:00.000]
- qc_load_preset 1 2 0 5   # Channel 1, Group 2, Setlist 0, Preset 5
```

**What device libraries provide:**
1. **Descriptive names**: `qc_load_preset` instead of raw CC/PC messages
2. **Parameter validation**: Ensures values are in valid ranges
3. **Timing delays**: Built-in delays for reliable device operation
4. **Documentation**: Comments explain each alias
5. **Multi-message macros**: Complex sequences in single command

**Test library import:**

Create a file named `device_test.mmd`:

```markdown
---
title: "Device Library Test"
author: "Your Name"
tempo: 120
ppq: 480
---

# Import your device library
@import "../devices/quad_cortex.mmd"

[00:00.000]
- tempo 120
- text "Testing device library import"
```

**Validate:**
```bash
mmdc validate device_test.mmd
```

If successful, the library loaded all aliases without errors.

## Step 2: Basic Preset Loading (Quad Cortex)

Let's start with simple preset changes.

Create `live_performance.mmd`:

```markdown
---
title: "Live Performance - Song 1"
author: "Your Name"
tempo: 120
time_signature: [4, 4]
ppq: 480
---

# Import Neural DSP Quad Cortex library
@import "../devices/quad_cortex.mmd"

# ============================================
# SONG: Example Song
# Tempo: 120 BPM, Key: E minor
# ============================================

[00:00.000]
- tempo 120
- time_signature 4/4
- marker "Intro - Clean Tone"

# Load clean preset for intro
# Parameters: channel, group, setlist, preset
[00:00.000]
- qc_load_preset 1 0 0 0   # Channel 1, Group 0, Setlist 0, Preset 0
```

**What this does:**
- **`qc_load_preset`**: Alias that expands to 3 MIDI messages:
  1. CC#0 (Bank MSB) = group (0-1)
  2. CC#32 (Bank LSB) = setlist (0-11)
  3. PC = preset number (0-127)
- **Built-in 100ms delays**: Ensures reliable loading
- **Self-documenting**: Clear what preset is being loaded

**Understanding Quad Cortex addressing:**
- **Group**: 0 = presets 0-127, 1 = presets 128-256
- **Setlist**: 0-11 (12 setlists available)
- **Preset**: 0-127 within each setlist

**Test preset loading:**
```bash
mmdc compile live_performance.mmd -o live_performance.mid
```

Connect your Quad Cortex and play the MIDI file. Preset 0 should load.

## Step 3: Scene Switching

Add scene changes for different sections within the same preset.

```markdown
---
title: "Live Performance - Song 1"
author: "Your Name"
tempo: 120
time_signature: [4, 4]
ppq: 480
---

@import "../devices/quad_cortex.mmd"

# ============================================
# SONG STRUCTURE
# ============================================

[00:00.000]
- tempo 120
- marker "Intro - Clean (Scene A)"

# Load preset and select Scene A
[00:00.000]
- qc_load_preset 1 0 0 5    # Load Preset 5
[00:00.300]
- qc_scene_a 1               # Switch to Scene A (clean)

# Intro section (8 bars)
[00:00.000]
- note_on 1.E3 80 1b
[00:02.000]
- note_on 1.G3 80 1b
[00:04.000]
- note_on 1.B3 80 1b
[00:06.000]
- note_on 1.E4 80 2b

[00:16.000]
- marker "Verse - Crunch (Scene B)"

# Switch to Scene B (crunch tone)
[00:16.000]
- qc_scene_b 1               # Switch to Scene B

# Verse backing (8 bars)
[00:16.000]
- note_on 1.E3 90 1b
[00:18.000]
- note_on 1.G3 90 1b
[00:20.000]
- note_on 1.B3 90 1b
[00:22.000]
- note_on 1.E4 90 2b

[00:32.000]
- marker "Chorus - Lead (Scene C)"

# Switch to Scene C (lead tone with delay)
[00:32.000]
- qc_scene_c 1               # Switch to Scene C

# Chorus melody (8 bars)
[00:32.000]
- note_on 1.E4 100 500ms
[00:32.500]
- note_on 1.G4 100 500ms
[00:33.000]
- note_on 1.B4 100 1000ms
```

**What this does:**
- **Scenes**: Quick preset variations (A-H available)
- **qc_scene_a**, **qc_scene_b**, **qc_scene_c**: Named scene aliases
- **Timing**: 300ms after preset load ensures preset is ready
- **Song structure**: Different scenes for intro/verse/chorus

**Scene switching advantages:**
- **Fast**: Much faster than loading new presets (~50ms vs ~200ms)
- **Seamless**: No audio dropout
- **Organized**: Keep related tones in one preset

**Scene latency warning (from library docs):**
> Scene switching via MIDI has ~100-130ms latency in CorOS 2.0+. For backing track sync, send scene changes 1/16 note early or use -50ms track delay.

**Test with scenes:**
```bash
mmdc compile live_performance.mmd -o live_performance.mid
```

## Step 4: Expression Pedal Automation

Add expression pedal swells for dynamic effects.

```markdown
[00:32.000]
- marker "Solo - Expression Swell"

# Start expression at heel (0)
[00:32.000]
- qc_exp1 1 0

# Load solo preset with Scene D
[00:32.000]
- qc_load_preset 1 0 1 3
[00:32.300]
- qc_scene_d 1

# Expression pedal swell (0 → 127 over 4 beats)
[00:33.000]
- qc_exp1 1 32    # 25%

[00:34.000]
- qc_exp1 1 64    # 50%

[00:35.000]
- qc_exp1 1 96    # 75%

[00:36.000]
- qc_exp1 1 127   # 100% (full toe)

# Hold at full expression for solo
[00:36.000]
- note_on 1.G4 110 500ms
[00:36.500]
- note_on 1.A4 110 500ms
[00:37.000]
- note_on 1.B4 110 1000ms

# Swell back down
[00:38.000]
- qc_exp1 1 96

[00:39.000]
- qc_exp1 1 64

[00:40.000]
- qc_exp1 1 0     # Back to heel
```

**What this does:**
- **`qc_exp1`**: Expression Pedal 1 control (CC#1)
- **Values 0-127**: 0 = heel position, 127 = toe position
- **Gradual changes**: Creates smooth swell effect
- **Typical use**: Wah, volume, delay mix, reverb amount

**Expression pedal warning (from library):**
> MIDI expression has significant latency compared to physical expression pedals. Not recommended for real-time wah or volume. Use physical pedals for best results.

**When to use MIDI expression:**
- Pre-programmed swells (like above)
- Slow parameter changes
- Automated filter sweeps
- Backing track sync

**When to use physical expression:**
- Real-time wah control
- Dynamic volume swells
- Interactive performance

## Step 5: Footswitch Control

Add stomp switch automation for effects on/off.

```markdown
[00:40.000]
- marker "Bridge - Ambient"

# Switch to ambient preset
[00:40.000]
- qc_load_preset 1 0 2 1

# Turn on delay (Stomp A) and reverb (Stomp B)
[00:40.300]
- qc_stomp_a_on 1
- qc_stomp_b_on 1

# Ambient chords (4 bars)
[00:40.000]
- note_on 1.E3 70 2b
[@]
- note_on 1.B3 70 2b
[@]
- note_on 1.E4 70 2b

[00:44.000]
- note_on 1.G3 70 2b
[@]
- note_on 1.D4 70 2b
[@]
- note_on 1.G4 70 2b

[00:48.000]
- marker "Final Chorus - Big"

# Turn off delay, keep reverb
[00:48.000]
- qc_stomp_a_off 1
- qc_stomp_b_on 1

# Turn on chorus (Stomp C)
[00:48.000]
- qc_stomp_c_on 1

# Big chorus section
[00:48.000]
- note_on 1.E4 110 1b
[00:50.000]
- note_on 1.G4 110 1b
[00:52.000]
- note_on 1.B4 110 2b
```

**What this does:**
- **Footswitch aliases**: qc_stomp_a_on, qc_stomp_b_on, etc.
- **8 stomps available**: A-H (CC#35-42)
- **Explicit on/off**: `_on` suffix forces active, `_off` forces bypass
- **Toggle version**: `qc_stomp_a 1 127` toggles state

**Stomp assignments (in your preset):**
- Stomp A: Delay
- Stomp B: Reverb
- Stomp C: Chorus
- Stomp D-H: Drive, compressor, EQ, etc.

**Important note:**
> Footswitches control whatever is assigned to them in your preset. You must configure stomp assignments in the Quad Cortex UI first.

## Step 6: Complete Live Performance

Here's a complete 2-song setlist with all techniques:

```markdown
---
title: "Live Performance - 2 Song Set"
author: "Your Name"
tempo: 120
time_signature: [4, 4]
ppq: 480
---

# Import Quad Cortex device library
@import "../devices/quad_cortex.mmd"

# ============================================
# SONG 1: "Electric Dreams"
# Key: E minor, Tempo: 120 BPM
# Presets: Setlist 0
# ============================================

[00:00.000]
- tempo 120
- time_signature 4/4
- marker "Song 1 - Intro"

# Initialize: Load clean preset
[00:00.000]
- qc_load_preset 1 0 0 0    # Clean preset, Scene A
[00:00.300]
- qc_scene_a 1
- qc_exp1 1 0                # Expression at heel

# Intro: Clean arpeggios (8 bars)
[00:00.000]
- note_on 1.E3 80 1b
[00:02.000]
- note_on 1.B3 80 1b
[00:04.000]
- note_on 1.E4 80 1b
[00:06.000]
- note_on 1.G4 80 2b

[00:16.000]
- marker "Song 1 - Verse"

# Verse: Switch to Scene B (light crunch)
[00:16.000]
- qc_scene_b 1

# Verse rhythm (8 bars)
[00:16.000]
- note_on 1.E3 90 500ms
[00:16.500]
- note_on 1.E3 85 500ms
[00:17.000]
- note_on 1.G3 90 1000ms
[00:18.000]
- note_on 1.E3 90 500ms
[00:18.500]
- note_on 1.E3 85 500ms
[00:19.000]
- note_on 1.G3 90 1000ms

[00:32.000]
- marker "Song 1 - Chorus"

# Chorus: Switch to Scene C (drive + delay)
[00:32.000]
- qc_scene_c 1
- qc_stomp_a_on 1            # Delay on

# Chorus power chords (8 bars)
[00:32.000]
- note_on 1.E2 100 1b
[@]
- note_on 1.E3 100 1b
[00:34.000]
- note_on 1.G2 100 1b
[@]
- note_on 1.G3 100 1b
[00:36.000]
- note_on 1.B2 100 1b
[@]
- note_on 1.B3 100 1b
[00:38.000]
- note_on 1.D3 100 2b
[@]
- note_on 1.D4 100 2b

[00:48.000]
- marker "Song 1 - Solo"

# Solo: Scene D (lead tone) + expression swell
[00:48.000]
- qc_scene_d 1
- qc_exp1 1 0                # Start at heel

# Expression swell over 4 bars
[00:49.000]
- qc_exp1 1 42
[00:50.000]
- qc_exp1 1 84
[00:51.000]
- qc_exp1 1 127              # Full expression

# Solo melody
[00:48.000]
- note_on 1.B4 110 500ms
[00:48.500]
- note_on 1.D5 110 500ms
[00:49.000]
- note_on 1.E5 110 1000ms
[00:50.000]
- note_on 1.D5 110 500ms
[00:50.500]
- note_on 1.B4 110 500ms
[00:51.000]
- note_on 1.G4 110 2000ms

# Swell back down
[00:54.000]
- qc_exp1 1 64
[00:55.000]
- qc_exp1 1 0

[00:64.000]
- marker "Song 1 - Outro"

# Outro: Back to clean Scene A
[00:64.000]
- qc_scene_a 1
- qc_stomp_a_off 1           # Delay off

# Final chord
[00:64.000]
- note_on 1.E2 80 4b
[@]
- note_on 1.E3 80 4b

[00:72.000]
- text "End of Song 1"

# ============================================
# SONG 2: "Midnight Sky"
# Key: A minor, Tempo: 95 BPM
# Presets: Setlist 1
# ============================================

[00:80.000]
- tempo 95
- marker "Song 2 - Intro"

# Load different preset for Song 2
[00:80.000]
- qc_load_preset 1 0 1 0     # Setlist 1, Preset 0
[00:80.300]
- qc_scene_a 1

# Ambient intro with reverb (4 bars)
[00:80.000]
- qc_stomp_b_on 1            # Reverb on

[00:80.000]
- note_on 1.A3 75 2b
[@]
- note_on 1.E4 75 2b
[00:84.736]
- note_on 1.C4 75 2b
[@]
- note_on 1.G4 75 2b

[00:96.000]
- marker "Song 2 - Verse"

# Verse: Scene B
[00:96.000]
- qc_scene_b 1

# Verse pattern (picking)
[00:96.000]
- note_on 1.A3 85 500ms
[00:96.631]
- note_on 1.C4 85 500ms
[00:97.263]
- note_on 1.E4 85 500ms
[00:97.894]
- note_on 1.A4 85 500ms

[00:128.000]
- marker "Song 2 - Chorus"

# Chorus: Scene C with delay
[00:128.000]
- qc_scene_c 1
- qc_stomp_a_on 1

# Chorus strumming (8 bars)
[00:128.000]
- note_on 1.A2 95 1b
[@]
- note_on 1.A3 95 1b
[00:130.526]
- note_on 1.F2 95 1b
[@]
- note_on 1.F3 95 1b

[00:160.000]
- marker "Song 2 - End"

# Final ambient chord
[00:160.000]
- qc_scene_a 1
- qc_stomp_a_off 1
- qc_stomp_b_on 1

[00:160.000]
- note_on 1.A2 70 8b
[@]
- note_on 1.E3 70 8b
[@]
- note_on 1.A3 70 8b

[00:180.000]
- text "End of Song 2"
- end_of_track
```

**What this does:**
- **2 complete songs** with different tempos and keys
- **Preset per song**: Song 1 uses Setlist 0, Song 2 uses Setlist 1
- **Scene changes**: A/B/C/D scenes for different sections
- **Stomp automation**: Delay and reverb on/off
- **Expression swells**: Automated for solo section
- **Markers**: Help navigate in DAW
- **Tempo changes**: Song 1 = 120 BPM, Song 2 = 95 BPM

**Compile and test:**
```bash
mmdc compile live_performance.mmd -o live_performance.mid
mmdc compile live_performance.mmd --format table  # View timeline
```

## Step 7: Using Other Devices

### Eventide H90 Example

```markdown
@import "../devices/eventide_h90.mmd"

[00:00.000]
- marker "Intro - Shimmer Reverb"

# Load Program 5 (Shimmer algorithm)
[00:00.000]
- h90_program 1 5            # Channel 1, Program 5

# Set mix to 40% wet
[00:00.000]
- h90_mix 1 50

# Intro chords
[00:00.000]
- note_on 1.E3 80 2b

[00:16.000]
- marker "Verse - Mod Delay"

# Switch to Program 12 (ModEchoVerb)
[00:16.000]
- h90_program 1 12

# Adjust quick knob for delay time
[00:16.100]
- h90_quick_knob1 1 64       # Medium delay time

[00:32.000]
- marker "Chorus - Freeze"

# Engage HotSwitch 1 (Freeze function)
[00:32.000]
- h90_hotswitch1 1

# Frozen pad continues under chorus
```

**H90 key differences:**
- **No default CC mappings**: Must configure in H90 System Menu first
- **Program Change**: 0-99 (with PC Offset) or 1-100 (without)
- **HotSwitches**: Program-level snapshots (3 available: HS1-3)
- **Performance parameters**: Algorithm-specific (Freeze, Warp, Repeat)
- **Firmware bug warning**: v1.9.4+ has PC+CC conflict, use v1.8.6

### Line 6 Helix Example

```markdown
@import "../devices/helix.mmd"

[00:00.000]
- marker "Intro - Clean"

# Load Setlist 0, Preset 5
[00:00.000]
- helix_load 1 0 5           # Channel 1, Setlist 0, Preset 5

# Switch to Snapshot 1
[00:00.200]
- helix_snap_1 1

[00:16.000]
- marker "Verse - Crunch"

# Switch to Snapshot 2 (different tone, same preset)
[00:16.000]
- helix_snap_2 1

[00:32.000]
- marker "Chorus - Lead"

# Load different preset with Snapshot 3
[00:32.000]
- helix_load 1 0 8
[00:32.200]
- helix_snap_3 1

# Toggle footswitch 1 (delay on)
[00:32.400]
- helix_fs1 1

[00:48.000]
- marker "Solo - Looper"

# Engage looper
[00:48.000]
- helix_looper_on 1
```

**Helix key differences:**
- **Snapshots**: 8 snapshots per preset (instant recall)
- **Setlist + Preset**: Two-level organization
- **Footswitches**: 8 or 12 depending on model (Floor/LT/Rack)
- **Command Center**: Can assign MIDI to any footswitch
- **Looper**: Built-in 6-switch looper control

## Troubleshooting

### Problem: Preset doesn't load

**Solutions:**
1. **Check MIDI channel**: Ensure device is on channel 1 (or adjust in aliases)
2. **Verify preset exists**: Preset numbers must exist in your device
3. **Check group/setlist**: Quad Cortex has 2 groups × 12 setlists
4. **Add more delay**: Try 200ms between CC and PC messages

### Problem: Scene changes too slow

**Solution**: Scene MIDI latency is ~100-130ms on Quad Cortex. Options:
1. Send scene change 1/16 note (125ms @ 120BPM) early
2. Use -50ms track delay on MIDI track in DAW
3. Enable "Ignore Duplicate PC" in device settings

### Problem: Expression pedal doesn't work

**Possible causes:**
1. **Not mapped**: Assign expression to a parameter in your preset
2. **MIDI channel**: Expression is channel-specific (use channel 1)
3. **Hardware better**: For real-time control, use physical expression pedal

### Problem: Footswitches toggle unexpectedly

**Solution**: Quad Cortex footswitch CCs toggle on ANY value. Use explicit on/off aliases:
```markdown
- qc_stomp_a_on 1     # Forces ON (CC value 127)
- qc_stomp_a_off 1    # Forces OFF (CC value 0)
```

### Problem: Compilation succeeds but device doesn't respond

**Checklist:**
1. **MIDI connected**: Verify cable/USB connection
2. **MIDI channel**: Device listening to channel 1?
3. **MIDI enabled**: Device MIDI settings enabled?
4. **Timing**: Add longer delays (200-300ms)
5. **Test with simple command**: Try just one preset load

## Next Steps

Now that you understand device control, try:

1. **Create full setlist**: Multiple songs with automated changes
2. **Add click track**: Use channel 10 for metronome (drummers)
3. **Use variables**: Define preset numbers with `@define CLEAN_PRESET 5`
4. **Add loops**: Repeat chorus sections with `@loop`
5. **Layer devices**: Control Quad Cortex + H90 simultaneously
6. **MIDI learn**: Map device parameters and create custom aliases
7. **Real-time playback**: Use `mmdc play` for live performance

## Step 8: Using Computed Values in Device Aliases (Phase 6)

Phase 6 introduces **computed values** - mathematical expressions in device aliases that let you parameterize complex sequences. This is powerful for device control because it lets you write flexible aliases that adapt based on inputs.

### Understanding Computed Values

Device aliases can now include computed parameters that calculate values based on inputs:

```markdown
@alias qc_tempo_to_cc {ch}.{bpm} "Convert BPM to CC value for tempo-synced delay"
  # Example: Map BPM to delay feedback
  # Higher BPM = higher feedback CC value
  {feedback = ${bpm} / 120 * 127}  # Normalize 120 BPM to 127
  [00:00.000]
  - cc {ch}.91.{feedback}        # Send as reverb parameter (CC#91)
@end

# Use it
[00:00.000]
- qc_tempo_to_cc 1 140          # Adjust delay feedback based on 140 BPM song
```

### Real-World Example: BPM-Linked Filter Expression

Here's a practical example that scales expression pedal range based on song tempo:

```markdown
@alias cortex_tempo_expression {ch}.{bpm}.{velocity} "Expression scaled to tempo"
  # Faster songs (high BPM) get more aggressive expression range
  {expr_range = (${bpm} - 80) / 2}     # Range increases with BPM
  {expr_value = ${velocity} * ${expr_range} / 100}
  [00:00.000]
  - qc_exp1 {ch}.{expr_value}
@end

# Use it for different tempos
[00:00.000]
- tempo 120
- cortex_tempo_expression 1 120 100   # 120 BPM, full velocity

[00:32.000]
- tempo 140
- cortex_tempo_expression 1 140 100   # 140 BPM, wider expression range
```

### Using Computed Values with Device Presets

Computed values shine when automating preset selection based on musical parameters:

```markdown
@alias h90_preset_for_section {ch}.{section_num}.{tempo} "Auto-select H90 program based on section"
  # Map section number to H90 program (0-99)
  {program = ${section_num} * 10 + (${tempo} / 60)}  # Section determines base, tempo determines variant
  [00:00.000]
  - h90_program {ch}.{program}
@end

# Use it
[00:00.000]
- tempo 120
- h90_preset_for_section 1 0 120      # Section 0, 120 BPM -> Program 2
[00:16.000]
- h90_preset_for_section 1 1 120      # Section 1, 120 BPM -> Program 12
```

### Referencing Existing Device Aliases

The built-in device aliases in `quad_cortex.mmd` and `eventide_h90.mmd` now support computed values. Check the device library documentation for aliases that accept calculated parameters.

**See also:**
- [Device Library Creation Guide](../user-guide/device-libraries.md) - Writing computed value aliases
- [Alias API Reference](../user-guide/alias-api.md) - Complete computed value syntax
- [quad_cortex.mmd](https://github.com/cjgdev/midi-markdown/blob/main/devices/quad_cortex.mmd) - Examples of computed alias patterns
- [eventide_h90.mmd](https://github.com/cjgdev/midi-markdown/blob/main/devices/eventide_h90.mmd) - H90-specific computed aliases

## Advanced Techniques

### Technique 1: Multi-Device Control

Control multiple devices in one song:

```markdown
@import "../devices/quad_cortex.mmd"
@import "../devices/eventide_h90.mmd"

[00:00.000]
# Quad Cortex on channel 1
- qc_load_preset 1 0 0 5
- qc_scene_a 1

# H90 on channel 2 (set in device)
- h90_program 2 12
- h90_mix 2 64
```

### Technique 2: Expression Mapping

Create custom expression curves:

```markdown
# Exponential swell (slow start, fast finish)
[00:00.000]
- qc_exp1 1 0
[00:01.000]
- qc_exp1 1 16     # 12.5%
[00:02.000]
- qc_exp1 1 48     # 37.5%
[00:03.000]
- qc_exp1 1 96     # 75%
[00:04.000]
- qc_exp1 1 127    # 100%
```

### Technique 3: Macro Aliases

Create your own convenience aliases in your MMD file:

```markdown
@alias my_intro_tone {ch} "Load my intro preset and scene"
  - qc_load_preset {ch} 0 0 5
  [+300ms]
  - qc_scene_a {ch}
  - qc_exp1 {ch} 0
@end

# Use it
[00:00.000]
- my_intro_tone 1
```

## Additional Resources

- [Quad Cortex MIDI Spec](https://support.neuraldsp.com/hc/en-us/articles/360014480320-MIDI-Specification)
- [H90 Manual](https://cdn.eventideaudio.com/manuals/h90/1.1/content/)
- [Helix MIDI Guide](https://line6.com/support/page/kb/effects-controllers/helix/helix-owners-manuals-r872/)
- [Device Library Creation Guide](../user-guide/device-libraries.md)
- [Alias System Guide](../user-guide/alias-system.md)
- [MML Specification](https://github.com/cjgdev/midi-markdown/blob/main/spec.md)
- [Example: 01_device_import.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/04_device_libraries/01_device_import.mmd)

## Summary

In this tutorial, you learned:

- How to import and use device libraries
- Loading presets with proper timing delays
- Switching scenes/snapshots for quick tone changes
- Automating expression pedals for swells
- Controlling footswitches/stomps for effects
- Creating complete live performance sequences
- Handling multi-device setups
- Device-specific considerations (Quad Cortex, H90, Helix)
- Troubleshooting common MIDI control issues

You now have the skills to create professional live performance automation with MML. Connect your device, create your setlist, and let MMD handle the preset changes while you focus on playing!
