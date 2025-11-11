# Device Library Creation Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Library Structure](#library-structure)
3. [Frontmatter Requirements](#frontmatter-requirements)
4. [Writing Effective Aliases](#writing-effective-aliases)
5. [Organization Strategies](#organization-strategies)
6. [Testing Your Library](#testing-your-library)
7. [Best Practices](#best-practices)
8. [Complete Example](#complete-example)
9. [Publishing Guidelines](#publishing-guidelines)

## Introduction

Device libraries are MMD files that define reusable aliases for specific MIDI hardware. They encapsulate device-specific MIDI implementation details behind human-readable command names, making it easier for users to control their gear.

### Why Create a Device Library?

- **Abstraction**: Hide complex MIDI mappings behind simple names
- **Reusability**: Share your work with the community
- **Documentation**: Serve as reference for device MIDI implementation
- **Consistency**: Establish naming conventions for a device
- **Productivity**: Save others time learning MIDI specs

### What You'll Need

- Device MIDI implementation chart (from manufacturer)
- Understanding of the device's features and organization
- MMD alias syntax knowledge
- Test device (or MIDI monitor) for validation

## Library Structure

A device library is an `.mmd` file with three main sections:

```markdown
---
# Frontmatter (required metadata)
---

# Documentation comments

# Alias definitions
```

###  File Naming

Use lowercase with underscores, matching manufacturer/device naming:

- `neural_dsp_quad_cortex.mmd` or `quad_cortex.mmd`
- `helix.mmd` (Line 6 Helix Floor/LT/Rack)
- `hx_effects.mmd` (Line 6 HX Effects)
- `hx_stomp.mmd` (Line 6 HX Stomp)
- `hx_stomp_xl.mmd` (Line 6 HX Stomp XL)
- `eventide_h90.mmd`
- `fractal_axe_fx_iii.mmd`

### Directory Structure

Place libraries in the `devices/` directory:

```
midi-markdown/
├── devices/
│   ├── quad_cortex.mmd
│   ├── eventide_h90.mmd
│   ├── helix.mmd
│   ├── hx_effects.mmd
│   ├── hx_stomp.mmd
│   ├── hx_stomp_xl.mmd
│   └── your_device.mmd
```

## Frontmatter Requirements

Every device library must include YAML frontmatter with these fields:

```yaml
---
device: Device Full Name           # Required: Official device name
manufacturer: Manufacturer Name    # Required: Company name
version: 1.0.0                     # Required: Library version (semver)
default_channel: 1                 # Optional: Common MIDI channel
documentation: https://...         # Optional: Link to MIDI docs
notes: Additional info             # Optional: Special notes
---
```

### Example Frontmatter

```yaml
---
device: Neural DSP Quad Cortex
manufacturer: Neural DSP
version: 3.0.0
default_channel: 1
documentation: https://neuraldsp.com/quad-cortex
notes: Firmware 3.0.0+. Scene changes via CC 34.
---
```

### Version Numbering

Use semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes to alias names or parameters
- **MINOR**: New aliases added (backward compatible)
- **PATCH**: Bug fixes, documentation updates

## Writing Effective Aliases

### Research the Device

Before writing aliases, thoroughly research the device's MIDI implementation:

1. **Get the MIDI implementation chart** from the manufacturer
2. **Identify key functions**: Preset changes, effect toggles, expression controls
3. **Note CC mappings**: Which CC numbers control what
4. **Understand ranges**: Value ranges for parameters (0-127, boolean, etc.)
5. **Test with device**: Verify commands work as documented

### Alias Naming Conventions

**Format**: `device_function[_detail]`

- **Prefix with device abbreviation**: `cortex_`, `helix_`, `kemper_`
- **Use action verbs**: `load`, `switch`, `toggle`, `set`
- **Be specific but concise**: `cortex_scene` not `cortex_s` or `cortex_switch_to_scene`
- **Group related functions**: `cortex_scene`, `cortex_scene_a`, `cortex_scene_b`

**Examples:**

```markdown
# Good names
@alias cortex_preset {ch} {preset} "Load preset"
@alias helix_snapshot {ch} {num} "Snapshot select"
@alias kemper_morph_pedal {ch} {amount} "Morph via pedal"

# Avoid
@alias cp {ch} {p} "?"                          # Too cryptic
@alias quad_cortex_load_preset {ch} {p} "..."  # Too verbose
@alias change_scene {ch} {s} "..."             # Missing device prefix
```

### Parameter Design

Choose appropriate parameter types:

**Generic (0-127):**
```markdown
@alias device_cc {ch} {value} "Generic CC"
  - cc {ch}.20.{value}
@end
```

**Range constrained:**
```markdown
@alias device_scene {ch} {scene:0-7} "Scene A-H"
  - cc {ch}.34.{scene}
@end
```

**Enum (named values):**
```markdown
@alias amp_channel {ch} {mode=clean:0,crunch:1,lead:2,ultra:3} "Amp channel"
  - cc {ch}.12.{mode}
@end
```

**Boolean:**
```markdown
@alias toggle_effect {ch} {enabled:bool} "Effect on/off"
  - cc {ch}.82.{enabled}
@end
```

**Percent:**
```markdown
@alias expression {ch} {level:percent} "Expression 0-100%"
  - cc {ch}.11.{level}
@end
```

**Note:**
```markdown
@alias play_note {ch} {note:note} {vel} "Play note by name"
  - note {ch}.{note}.{vel} 500ms
@end
```

### Documentation Strings

Every alias should have a clear, concise description:

```markdown
@alias cortex_load {ch} {setlist} {group} {preset} "Complete preset load sequence"
  - cc {ch}.32.{setlist}
  - cc {ch}.0.{group}
  - pc {ch}.{preset}
@end
```

**Good descriptions:**
- State what it does, not how
- Mention key parameters if not obvious
- Note special requirements

## Organization Strategies

### Group by Function

Organize aliases into logical sections with clear headers:

```markdown
# ============================================
# Preset/Bank Management
# ============================================

@alias device_preset {ch} {preset} "..."
@end

@alias device_bank_up {ch} "..."
@end

# ============================================
# Scene Management
# ============================================

@alias device_scene {ch} {scene} "..."
@end

# ============================================
# Expression Pedals
# ============================================

@alias device_exp1 {ch} {value} "..."
@end
```

### Common Organizational Sections

Use consistent section headers across libraries:

1. **Preset/Bank Management**: Load presets, navigate banks
2. **Scene/Snapshot Management**: Scene/snapshot switching
3. **Expression Pedals**: Expression control
4. **Effect Controls**: Effect on/off, parameters
5. **Tempo/Timing**: Tap tempo, BPM control
6. **Looper**: Looper commands (if applicable)
7. **Tuner**: Tuner on/off
8. **Advanced/Utility**: Special functions
9. **Performance Macros**: Higher-level combined commands

### Provide Shortcut Aliases

For frequently used values, create convenience aliases:

```markdown
@alias device_scene {ch} {scene:0-7} "Scene 0-7"
  - cc {ch}.34.{scene}
@end

# Convenient shortcuts
@alias device_scene_a {ch} "Scene A"
  - device_scene {ch} 0
@end

@alias device_scene_b {ch} "Scene B"
  - device_scene {ch} 1
@end
```

### Create Composite Aliases

Build higher-level aliases from lower-level ones:

```markdown
# Basic building blocks
@alias device_preset {ch} {preset} "Load preset"
  - pc {ch}.{preset}
@end

@alias device_reverb {ch} {level} "Reverb level"
  - cc {ch}.91.{level}
@end

# Composite alias
@alias device_ambient_preset {ch} {preset} {reverb} "Preset with reverb"
  - device_preset {ch} {preset}
  - device_reverb {ch} {reverb}
@end
```

## Testing Your Library

### Create Test File

Create a test document that uses every alias:

```markdown
---
title: Device Library Test
---

# Copy all aliases from your library here
# ...

# Test each alias
[00:00.000]
- device_preset 1 0

[00:01.000]
- device_scene 1 0

# ... test all aliases
```

### Validation Checklist

- [ ] All aliases parse without errors
- [ ] Parameter types are correct
- [ ] Parameter ranges match device specs
- [ ] CC numbers are correct
- [ ] Descriptions are clear and accurate
- [ ] Nested aliases work correctly
- [ ] Enum values are spelled correctly
- [ ] Bool parameters work
- [ ] Frontmatter is complete
- [ ] Comments are helpful

### Test with Device

If you have the physical device:

1. Compile test MMD to MIDI file
2. Play MIDI file to device
3. Verify each command does what's expected
4. Adjust aliases if behavior differs
5. Document any firmware version dependencies

### Automated Testing

Create integration tests (see `tests/integration/test_device_libraries.py`):

```python
def test_your_device_library_parses(parser, devices_dir):
    """Test that your device library parses."""
    library_path = devices_dir / "your_device.mmd"
    with open(library_path) as f:
        content = f.read()

    doc = parser.parse_string(content)
    assert doc.frontmatter.get('device') == 'Your Device Name'
    assert 'your_device_preset' in doc.aliases
```

## Best Practices

### 1. Start with Common Commands

Focus on the most-used 20% of features first:

- Preset/patch selection
- Scene/snapshot switching
- Expression pedal control
- Common effect toggles

### 2. Match User Mental Model

Use names that match how users think about the device:

```markdown
# Good - matches Helix terminology
@alias helix_snapshot {ch} {num} "Snapshot"

# Confusing - doesn't match user expectations
@alias helix_preset_variant {ch} {num} "..."
```

### 3. Provide Multiple Access Patterns

Offer both generic and specific aliases:

```markdown
# Generic (flexible)
@alias device_scene {ch} {scene:0-7} "Scene 0-7"
  - cc {ch}.34.{scene}
@end

# Specific shortcuts (convenient)
@alias device_clean {ch} "Clean scene"
  - device_scene {ch} 0
@end

@alias device_lead {ch} "Lead scene"
  - device_scene {ch} 3
@end
```

### 4. Document Limitations

Note any firmware version requirements or limitations:

```markdown
# ============================================
# IMPORTANT: Firmware Version Requirements
# ============================================
#
# These aliases require firmware 3.0.0 or higher:
# - device_advanced_feature
#
# CC 34 behavior changed in firmware 2.5.0

@alias device_feature {ch} {value} "Requires FW 3.0.0+"
  - cc {ch}.99.{value}
@end
```

### 5. Include Usage Examples

Add comment blocks with usage examples:

```markdown
@alias cortex_load {ch} {setlist} {group} {preset} "Complete preset load"
  - cc {ch}.32.{setlist}
  - cc {ch}.0.{group}
  - pc {ch}.{preset}
@end

# Usage examples:
# - cortex_load 1 2 0 5    # Setlist 2, Group 0, Preset 5
# - cortex_load 1 0 3 10   # Setlist 0, Group 3, Preset 10
```

### 6. Avoid Magic Numbers

Use named enum values instead of raw numbers:

```markdown
# Poor - magic numbers
@alias device_mode {ch} {mode:0-3} "Set mode"
  - cc {ch}.50.{mode}
@end

# Better - named values
@alias device_mode {ch} {mode=stomp:0,scene:1,preset:2,snapshot:3} "Set mode"
  - cc {ch}.50.{mode}
@end
```

## Complete Example

Here's a complete minimal device library:

```yaml
---
device: Example Processor
manufacturer: Example Audio
version: 1.0.0
default_channel: 1
documentation: https://example.com/midi-spec
---

# ============================================
# Example Audio Processor MIDI Library
# ============================================
#
# This library defines common MIDI commands for the Example Processor.
# Compatible with firmware 2.0.0+.
#
# MIDI Implementation:
# - PC 0-127: Preset selection
# - CC 10: Scene select (0-3)
# - CC 11: Expression pedal
# - CC 80: Tap tempo
# - CC 81-84: Effect A-D toggle (0=off, 127=on)

# ============================================
# Preset Management
# ============================================

@alias example_preset {ch} {preset:0-127} "Select preset"
  - pc {ch}.{preset}
@end

@alias example_next_preset {ch} "Next preset"
  - cc {ch}.20.127
@end

@alias example_prev_preset {ch} "Previous preset"
  - cc {ch}.20.0
@end

# ============================================
# Scene Management
# ============================================

@alias example_scene {ch} {scene:0-3} "Select scene A-D"
  - cc {ch}.10.{scene}
@end

@alias example_scene_a {ch} "Scene A"
  - example_scene {ch} 0
@end

@alias example_scene_b {ch} "Scene B"
  - example_scene {ch} 1
@end

@alias example_scene_c {ch} "Scene C"
  - example_scene {ch} 2
@end

@alias example_scene_d {ch} "Scene D"
  - example_scene {ch} 3
@end

# ============================================
# Expression Control
# ============================================

@alias example_expression {ch} {value:0-127} "Expression pedal"
  - cc {ch}.11.{value}
@end

@alias example_exp_percent {ch} {value:percent} "Expression as percent"
  - cc {ch}.11.{value}
@end

# ============================================
# Effects
# ============================================

@alias example_fx_a {ch} {state:bool} "Effect A toggle"
  - cc {ch}.81.{state}
@end

@alias example_fx_b {ch} {state:bool} "Effect B toggle"
  - cc {ch}.82.{state}
@end

@alias example_fx_c {ch} {state:bool} "Effect C toggle"
  - cc {ch}.83.{state}
@end

@alias example_fx_d {ch} {state:bool} "Effect D toggle"
  - cc {ch}.84.{state}
@end

# ============================================
# Tempo
# ============================================

@alias example_tap_tempo {ch} "Tap tempo"
  - cc {ch}.80.127
@end

# ============================================
# Performance Macros
# ============================================

@alias example_clean_with_reverb {ch} "Clean preset with reverb"
  - example_preset {ch} 0
  - example_fx_c {ch} on
@end

@alias example_lead_with_delay {ch} "Lead preset with delay"
  - example_preset {ch} 10
  - example_fx_b {ch} on
@end
```

## Publishing Guidelines

### Documentation

Include a README section in your library:

```markdown
# ============================================
# README
# ============================================
#
# Example Audio Processor MIDI Library
#
# Author: Your Name
# Version: 1.0.0
# Last Updated: 2025-01-30
#
# This library provides aliases for the Example Audio Processor.
#
# Quick Start:
# @import "devices/example_processor.mmd"
# - example_preset 1 10
#
# Requirements:
# - Firmware 2.0.0+
# - MIDI channel 1 (default)
#
# Resources:
# - MIDI spec: https://example.com/midi
# - Manual: https://example.com/manual
```

### Contribution Process

1. Fork the MMD repository
2. Create your device library in `devices/`
3. Add integration tests in `tests/integration/test_device_libraries.py`
4. Update `devices/README.md` with your device
5. Submit pull request

### License

Device libraries should use the same license as the main project (MIT).

## Next Steps

- **User Guide**: Learn to use aliases in the [Alias System User Guide](alias-system.md)
- **API Reference**: See complete syntax in [Alias API Reference](alias-api.md)
- **Examples**: Study existing libraries in `devices/`

## Resources

### Manufacturer MIDI Documentation

- Neural DSP: https://neuraldsp.com/quad-cortex
- Line 6: https://line6.com/support/manuals/helix
- Kemper: https://www.kemper.digital/profiler
- Eventide: https://www.eventideaudio.com/support
- Fractal Audio: https://wiki.fractalaudio.com

### MIDI Reference

- MIDI Association: https://www.midi.org
- MIDI Implementation Chart template: https://www.midi.org/specifications

### Community

- Share your library with the community
- Request libraries for devices you own
- Contribute improvements to existing libraries
