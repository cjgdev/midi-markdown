# Alias System User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Basic Concepts](#basic-concepts)
3. [Creating Simple Aliases](#creating-simple-aliases)
4. [Parameter Types](#parameter-types)
5. [Advanced Features](#advanced-features)
6. [Using Device Libraries](#using-device-libraries)
7. [Best Practices](#best-practices)
8. [Examples](#examples)

## Introduction

The MIDI Markdown (MMD) alias system allows you to create reusable, named shortcuts for common MIDI command sequences. Instead of writing repetitive MIDI commands, you can define an alias once and use it throughout your document with different parameters.

**Why use aliases?**

- **Readability**: `cortex_scene 1 3` is more readable than `cc 1.34.3`
- **Reusability**: Define once, use many times
- **Device abstraction**: Hide device-specific MIDI details behind meaningful names
- **Maintainability**: Change the implementation in one place
- **Live performance**: Create high-level commands for song sections

## Basic Concepts

### What is an Alias?

An alias is a named template that expands to one or more MIDI commands. Think of it as a function or macro that takes parameters and generates MIDI messages.

**Anatomy of an alias:**

```markdown
@alias alias_name {param1} {param2} "Description"
  - midi_command using {param1}
  - midi_command using {param2}
@end
```

### How Aliases Work

1. **Definition**: You define an alias with parameters
2. **Usage**: You call the alias with arguments
3. **Expansion**: The system replaces parameter placeholders with your arguments
4. **Execution**: The expanded MIDI commands are sent at the specified time

## Creating Simple Aliases

### Your First Alias

Let's create a simple alias for a program change:

```markdown
@alias quick_preset {channel} {preset} "Quick preset change"
  - pc {channel}.{preset}
@end
```

**Using the alias:**

```markdown
[00:00.000]
- quick_preset 1 42
```

This expands to:

```markdown
[00:00.000]
- pc 1.42
```

### Multi-Command Aliases

Aliases can expand to multiple MIDI commands:

```markdown
@alias scene_with_reverb {ch} {scene} {reverb_level} "Scene change with reverb"
  - cc {ch}.34.{scene}
  - cc {ch}.100.{reverb_level}
@end
```

**Usage:**

```markdown
[00:05.000]
- scene_with_reverb 1 3 95
```

**Expands to:**

```markdown
[00:05.000]
- cc 1.34.3
- cc 1.100.95
```

## Parameter Types

MML supports several parameter types with automatic conversion and validation.

### Generic Parameters

Default type - accepts integers in range 0-127:

```markdown
@alias simple_cc {ch} {cc_num} {value} "Generic CC"
  - cc {ch}.{cc_num}.{value}
@end
```

### Range Parameters

Specify custom min/max values:

```markdown
@alias tempo_change {bpm:40-300} "Set tempo"
  - tempo {bpm}
@end
```

### Note Parameters

Accepts note names (C4, D#5, Bb3) or MIDI note numbers:

```markdown
@alias play_note {ch} {note:note} {velocity} "Play a note"
  - note {ch}.{note}.{velocity} 500ms
@end
```

**Usage:**

```markdown
- play_note 1 C#4 100   # Note name
- play_note 1 60 100    # MIDI number
```

### Percent Parameters

Accepts 0-100 and automatically converts to MIDI 0-127:

```markdown
@alias mix_level {ch} {level:percent} "Mix level as percentage"
  - cc {ch}.7.{level}
@end
```

**Usage:**

```markdown
- mix_level 1 75    # Converts 75% → 95 MIDI
```

### Enum Parameters

Named values that map to numbers:

```markdown
@alias amp_channel {ch} {channel=clean:0,crunch:1,lead:2} "Amp channel switch"
  - cc {ch}.12.{channel}
@end
```

**Usage:**

```markdown
- amp_channel 1 clean    # Uses value 0
- amp_channel 1 lead     # Uses value 2
```

### Bool Parameters

Accepts true/false, on/off, 1/0, yes/no:

```markdown
@alias toggle_tuner {ch} {enabled:bool} "Toggle tuner"
  - cc {ch}.68.{enabled}
@end
```

**Usage:**

```markdown
- toggle_tuner 1 on      # Converts to 127
- toggle_tuner 1 off     # Converts to 0
```

### Default Values

Parameters can have default values:

```markdown
@alias preset_change {ch=1} {preset} "Preset with default channel"
  - pc {ch}.{preset}
@end
```

**Usage:**

```markdown
- preset_change 42        # Uses channel 1 (default)
- preset_change 2 42      # Uses channel 2 (explicit)
```

## Advanced Features

### Timing in Aliases

**NEW**: Aliases can include timing delays for proper MIDI sequencing. This is essential for devices that require delays between certain MIDI messages.

```markdown
@alias qc_load_preset {ch} {group} {setlist} {preset} "Load preset with timing"
  - cc {ch}.0.{group}
  [+100ms]
  - cc {ch}.32.{setlist}
  [+100ms]
  - pc {ch}.{preset}
@end
```

**Why use timing in aliases?**

- **Hardware requirements**: Many MIDI devices (like Neural DSP Quad Cortex) require 50-100ms delays between Bank Select and Program Change messages
- **Reliability**: Prevents messages from being lost or processed in wrong order
- **Consistency**: Define timing delays once in the alias, use everywhere

**Supported timing types:**

- `[+Xms]` - Relative timing in milliseconds
- `[+Xs]` - Relative timing in seconds

**Example usage:**

```markdown
[00:00.000]
- qc_load_preset 1 0 2 5    # Automatic 100ms delays between messages
```

**Expanded output:**

```markdown
- cc 1.0.0           # Bank group at time 0ms
- cc 1.32.2          # Setlist at time +100ms
- pc 1.5             # Preset at time +200ms
```

**Note**: Beat-based (`[+1b]`) and tick-based (`[+480t]`) timing are not supported in aliases since they require tempo context. Use milliseconds or seconds instead.

### Nested Aliases

Aliases can call other aliases:

```markdown
@alias reverb_cc {ch} {level} "Reverb CC"
  - cc {ch}.91.{level}
@end

@alias ambient_preset {ch} {preset} {reverb} "Preset with reverb"
  - pc {ch}.{preset}
  - reverb_cc {ch} {reverb}
@end
```

**Usage:**

```markdown
- ambient_preset 1 10 127
```

**Expands to:**

```markdown
- pc 1.10
- cc 1.91.127
```

### Computed Values

Define calculated values using expressions:

```markdown
@alias bpm_to_midi {ch} {bpm:40-300} "Convert BPM to MIDI value"
  {midi_val = int((${bpm} - 40) * 127 / 260)}
  - cc {ch}.81.{midi_val}
@end
```

**Note**: Computed values are currently in development.

### Conditional Logic (Stage 7)

Create device-aware aliases with conditional branching:

```markdown
@alias device_load {ch} {preset} {device=cortex:0,helix:1,kemper:2} "Device-specific load"
  @if {device} == 0
    # Quad Cortex uses PC
    - pc {ch}.{preset}
  @elif {device} == 1
    # Helix uses CC 69 for snapshots
    - cc {ch}.69.{preset}
  @else
    # Kemper uses PC
    - pc {ch}.{preset}
  @end
@end
```

**Usage:**

```markdown
- device_load 1 5 cortex    # Generates: pc 1.5
- device_load 2 3 helix     # Generates: cc 2.69.3
- device_load 1 7 kemper    # Generates: pc 1.7
```

## Using Device Libraries

Device libraries are pre-built collections of aliases for popular MIDI devices.

### Importing Libraries

Use `@import` to load a device library:

```markdown
---
title: My Performance
---

@import "devices/quad_cortex.mmd"
@import "devices/helix.mmd"

[00:00.000]
- qc_scene 1 0
- helix_snap_1 2
```

**Note**: Import system is currently in development (Stage 8).

### Available Libraries

MML includes libraries for:

- **Neural DSP Quad Cortex** (`devices/quad_cortex.mmd`)
  - Preset/scene management
  - Expression pedals
  - Stomp switches
  - Tuner, tap tempo

- **Eventide H90** (`devices/eventide_h90.mmd`)
  - Dual algorithm control
  - Program changes
  - Expression mapping

- **Line 6 Helix Floor/LT/Rack** (`devices/helix.mmd`)
  - Setlist/preset navigation
  - 8 snapshots
  - Footswitch control
  - Looper commands

- **Line 6 HX Effects** (`devices/hx_effects.mmd`)
  - Preset navigation (32 banks × 4)
  - 4 snapshots
  - Effects-only control

- **Line 6 HX Stomp** (`devices/hx_stomp.mmd`)
  - Direct preset addressing
  - 3 snapshots
  - Compact model controls

- **Line 6 HX Stomp XL** (`devices/hx_stomp_xl.mmd`)
  - Direct preset addressing
  - 4 snapshots
  - 8 footswitches

### Library Alias Examples

**Quad Cortex:**

```markdown
- cortex_preset 1 42              # Load preset 42
- cortex_scene 1 3                # Scene D
- cortex_scene_a 1                # Scene A shortcut
- cortex_exp1 1 64                # Expression pedal 1
- cortex_stomp_a 1 127            # Toggle stomp A
- cortex_tap_tempo 1              # Tap tempo
```

**Helix:**

```markdown
- helix_preset 1 10               # Load preset 10
- helix_snapshot 1 2              # Snapshot 3
- helix_snapshot_1 1              # Snapshot 1 shortcut
- helix_expression 1 127          # Expression full
- helix_tap_tempo 1               # Tap tempo
```

**Kemper:**

```markdown
- kemper_rig 1 15                 # Load rig 15
- kemper_perf_slot_1 1            # Performance slot 1
- kemper_morph_pedal 1 64         # Morph 50%
- kemper_fx_delay 1 on            # Delay on
- kemper_tuner 1 on               # Tuner on
```

## Best Practices

### Naming Conventions

- Use descriptive, lowercase names with underscores
- Prefix with device name for device-specific aliases
- Use verbs for actions: `load_preset`, `switch_scene`
- Keep names concise but clear

**Good:**

```markdown
@alias cortex_scene_a {ch} "Scene A"
@alias helix_snapshot {ch} {num} "Snapshot select"
@alias toggle_reverb {ch} {state:bool} "Reverb on/off"
```

**Avoid:**

```markdown
@alias a {ch} {x} "?"                    # Too cryptic
@alias extremely_long_descriptive_name_for_scene_a {ch} "..."  # Too verbose
```

### Documentation

Always include descriptive strings:

```markdown
@alias cortex_load {ch} {setlist} {group} {preset} "Complete preset load sequence"
  - cc {ch}.32.{setlist}
  - cc {ch}.0.{group}
  - pc {ch}.{preset}
@end
```

### Organization

Group related aliases together with comments:

```markdown
# ============================================
# Scene Management
# ============================================

@alias cortex_scene {ch} {scene:0-7} "Switch to scene"
  - cc {ch}.34.{scene}
@end

@alias cortex_scene_a {ch} "Scene A shortcut"
  - cc {ch}.34.0
@end
```

### Parameter Validation

Use appropriate parameter types to catch errors early:

```markdown
# Good - validates range
@alias scene_switch {ch} {scene:0-7} "Scene 0-7"
  - cc {ch}.34.{scene}
@end

# Better - use enum for clarity
@alias scene_switch {ch} {scene=a:0,b:1,c:2,d:3,e:4,f:5,g:6,h:7} "Scene A-H"
  - cc {ch}.34.{scene}
@end
```

## Examples

### Example 1: Simple Live Setup

```markdown
---
title: Simple Live Song
tempo: 120
---

@alias verse_tone {ch} "Verse clean tone"
  - pc {ch}.0
  - cc {ch}.91.30
@end

@alias chorus_tone {ch} "Chorus with delay"
  - pc {ch}.1
  - cc {ch}.93.80
@end

@alias lead_tone {ch} "Lead with boost"
  - pc {ch}.2
  - cc {ch}.7.127
@end

# Intro
[00:00.000]
- verse_tone 1

# First chorus
[00:16.000]
- chorus_tone 1

# Solo
[00:32.000]
- lead_tone 1

# Final chorus
[01:00.000]
- chorus_tone 1

# Outro
[01:24.000]
- verse_tone 1
```

### Example 2: Multi-Device Setup

```markdown
---
title: Dual Processor Setup
---

@alias cortex_scene {ch} {scene:0-7} "Cortex scene"
  - cc {ch}.34.{scene}
@end

@alias helix_snapshot {ch} {snapshot:0-7} "Helix snapshot"
  - cc {ch}.69.{snapshot}
@end

@alias both_clean {ch1} {ch2} "Both clean"
  - cortex_scene {ch1} 0
  - helix_snapshot {ch2} 0
@end

@alias both_lead {ch1} {ch2} "Both lead"
  - cortex_scene {ch1} 3
  - helix_snapshot {ch2} 3
@end

# Intro - both clean
[00:00.000]
- both_clean 1 2

# Solo - both lead
[00:32.000]
- both_lead 1 2
```

### Example 3: Expression Automation

```markdown
---
title: Expression Automation
tempo: 120
---

@alias swell {ch} {level:percent} "Volume swell"
  - cc {ch}.11.{level}
@end

# Start silent
[00:00.000]
- swell 1 0

# Gradual swell over 4 bars
[00:02.000]
- swell 1 25

[00:04.000]
- swell 1 50

[00:06.000]
- swell 1 75

[00:08.000]
- swell 1 100
```

### Example 4: Conditional Device Handling

```markdown
---
title: Universal Song File
---

@alias device_scene {ch} {scene} {device=cortex:0,helix:1} "Device-agnostic scene"
  @if {device} == 0
    - cc {ch}.34.{scene}
  @elif {device} == 1
    - cc {ch}.69.{scene}
  @end
@end

# Works with either device
[00:00.000]
- device_scene 1 0 cortex    # Or use 'helix'

[00:08.000]
- device_scene 1 1 cortex
```

## Next Steps

- **Library Creation**: Learn to create your own device libraries in the [Device Library Author Guide](device-libraries.md)
- **API Reference**: See the complete alias syntax reference in [Alias API Reference](alias-api.md)
- **Examples**: Explore more examples in the `examples/` directory

## Troubleshooting

### Common Issues

**"Undefined alias" error:**
- Check spelling of alias name
- Ensure alias is defined before use
- Verify `@end` keyword closes the alias

**"Wrong number of arguments" error:**
- Count your arguments carefully
- Check for default parameters
- Review alias definition

**"Parameter out of range" error:**
- Check parameter type (e.g., `:0-127`)
- Verify your value is within bounds
- Use percent type for 0-100 values

**"Invalid enum value" error:**
- Check spelling of enum option
- Review available options in alias definition
- Enum values are case-sensitive

## Support

For more help:
- Check the [specification](../reference/specification.md) for complete syntax details
- Review [example files](https://github.com/cjgdev/midi-markdown/tree/main/examples) for working code
- Report issues at the project repository
