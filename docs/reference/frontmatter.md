# YAML Frontmatter Reference

**MIDI Markdown (MMD) Frontmatter Specification**

## Overview

MMD files use YAML-style frontmatter to define document-level properties and metadata. Frontmatter is enclosed between triple-dash delimiters (`---`) at the beginning of the file and parsed as YAML.

**Basic Structure:**

```yaml
---
title: "My Song"
ppq: 480
tempo: 120
time_signature: 4/4
---

# Your MMD content follows here
```

Frontmatter is **optional** but recommended for proper MIDI file generation. When omitted, sensible defaults are used.

---

## Required Fields

While technically optional (defaults exist for all fields), these fields are strongly recommended for proper MIDI compilation:

### `ppq` - Pulses Per Quarter Note

**Type:** Integer
**Default:** 480
**Valid Range:** 96-960 (common values)

Defines MIDI timing resolution. Higher values provide more precise timing.

**Common Values:**
- `96` - Low resolution (older hardware)
- `192` - Standard resolution
- `480` - **High resolution (recommended)**
- `960` - Very high resolution (for precise automation)

**Example:**
```yaml
ppq: 480
```

**Impact:**
- Affects timing precision for all events
- Higher PPQ = smoother CC automation and note timing
- Used for musical timing calculations (bars.beats.ticks)

---

### `tempo` - Initial Tempo

**Type:** Integer or Float
**Default:** 120
**Valid Range:** 20-999 BPM (practical range)

Sets the starting tempo in beats per minute. Can be changed dynamically using `- tempo` commands.

**Example:**
```yaml
tempo: 128
```

**With Fractional BPM:**
```yaml
tempo: 132.5
```

**Notes:**
- Affects conversion of absolute time `[mm:ss.ms]` to MIDI ticks
- Affects musical time `[bars.beats.ticks]` calculations
- Can be overridden with `- tempo` commands in the timeline

---

### `time_signature` - Time Signature

**Type:** String or Tuple
**Default:** 4/4
**Format:** `numerator/denominator`

Defines the musical meter for bars and beats calculations.

**String Format (YAML):**
```yaml
time_signature: 4/4
```

**Common Time Signatures:**
```yaml
time_signature: 4/4    # Common time (4 beats per bar)
time_signature: 3/4    # Waltz time
time_signature: 6/8    # Compound meter
time_signature: 5/4    # Unusual meter (e.g., "Take Five")
time_signature: 7/8    # Complex meter
```

**Impact:**
- Used for musical timing `[bars.beats.ticks]` calculations
- Determines beats per bar for bar/beat positioning
- Affects loop and sweep timing when using beat notation

---

## Optional Metadata Fields

These fields provide documentation and organization but don't affect MIDI compilation:

### `title` - Song/Document Title

**Type:** String
**Default:** None

Human-readable title for the composition or automation sequence.

**Example:**
```yaml
title: "Electric Dreams - Live Performance"
```

### `author` - Creator Name

**Type:** String
**Default:** None

Name of the person who created the MMD file.

**Example:**
```yaml
author: "John Doe"
```

### `description` - Document Description

**Type:** String
**Default:** None

Brief description of the file's purpose or contents.

**Example:**
```yaml
description: "Complete live automation for 3-song medley"
```

### `date` - Creation/Modification Date

**Type:** String (ISO 8601 format recommended)
**Default:** None

**Example:**
```yaml
date: "2025-11-11"
```

---

## Optional Configuration Fields

### `midi_format` - MIDI File Format

**Type:** Integer
**Default:** 1
**Valid Values:** 0, 1, 2

Specifies the Standard MIDI File (SMF) format type.

**Format Types:**
- `0` - Single track (all events merged into one track)
- `1` - Multi-track synchronous (tracks play simultaneously) **[recommended]**
- `2` - Multi-track asynchronous (independent sequences)

**Example:**
```yaml
midi_format: 1
```

**When to Use:**
- **Format 0:** Simple single-instrument sequences
- **Format 1:** Multi-instrument songs, DAW import
- **Format 2:** Rarely used (independent MIDI sequences)

---

### `default_channel` - Default MIDI Channel

**Type:** Integer
**Default:** 1
**Valid Range:** 1-16

Sets the default MIDI channel when not specified in commands.

**Example:**
```yaml
default_channel: 1
```

**Usage:**
```yaml
default_channel: 2
---

# This note goes to channel 2 (default)
- note_on C4 100 1b

# This note goes to channel 5 (explicit)
- note_on 5.C4 100 1b
```

---

### `default_velocity` - Default Note Velocity

**Type:** Integer
**Default:** 100
**Valid Range:** 0-127

Sets the default velocity for note commands when not specified.

**Example:**
```yaml
default_velocity: 80
```

**Usage:**
```yaml
default_velocity: 90
---

# Uses default velocity (90)
- note_on 1.C4 1b

# Explicit velocity overrides default
- note_on 1.C4 127 1b
```

---

### `devices` - Device Mapping (Future)

**Type:** YAML Map/List
**Default:** None
**Status:** Reserved for future use

Intended for mapping MIDI channels to device names in multi-device setups.

**Proposed Format:**
```yaml
devices:
  - cortex: channel 1
  - h90: channel 2
  - helix: channel 3
```

**Current Status:** Parsed but not yet used by compiler. Reserved for future device library enhancements.

---

## Complete Examples

### Minimal Frontmatter (Recommended)

```yaml
---
ppq: 480
tempo: 120
time_signature: 4/4
---
```

### Basic Song Metadata

```yaml
---
title: "Verse 1 Automation"
author: "Studio Engineer"
ppq: 480
tempo: 132
time_signature: 4/4
midi_format: 1
---
```

### Live Performance Setup

```yaml
---
title: "Live Set - Song 3"
author: "Touring Band"
description: "Quad Cortex + H90 preset automation"
date: "2025-11-11"
ppq: 480
tempo: 128
time_signature: 4/4
midi_format: 1
default_channel: 1
devices:
  - cortex: channel 1
  - h90: channel 2
---
```

### High-Resolution MIDI

```yaml
---
title: "Studio Recording Automation"
ppq: 960
tempo: 120.5
time_signature: 4/4
midi_format: 1
default_velocity: 95
---
```

### Unusual Time Signature

```yaml
---
title: "Progressive Rock Section"
ppq: 480
tempo: 145
time_signature: 7/8
---
```

---

## Field Processing

### Precedence and Overrides

1. **Frontmatter values** are read first during parsing
2. **CLI arguments** can override frontmatter (e.g., `--ppq 960`)
3. **Timeline commands** can override tempo dynamically:
   ```mmd
   [00:00.000]
   - tempo 120

   [00:30.000]
   - tempo 140  # Changes tempo mid-song
   ```

### Default Values Summary

| Field | Default | Type | Required |
|-------|---------|------|----------|
| `ppq` | 480 | Integer | Recommended |
| `tempo` | 120 | Integer/Float | Recommended |
| `time_signature` | 4/4 | String | Recommended |
| `midi_format` | 1 | Integer | Optional |
| `default_channel` | 1 | Integer | Optional |
| `default_velocity` | 100 | Integer | Optional |
| `title` | None | String | Optional |
| `author` | None | String | Optional |
| `description` | None | String | Optional |
| `date` | None | String | Optional |
| `devices` | None | Map/List | Future |

---

## YAML Syntax Notes

### Strings
```yaml
# Quotes optional for simple strings
title: My Song

# Quotes required for strings with special characters
title: "Song: Part 1"

# Multi-line strings
description: |
  This is a multi-line
  description of the file.
```

### Numbers
```yaml
# Integers
ppq: 480
tempo: 120

# Floats
tempo: 132.5
```

### Lists (for future device mapping)
```yaml
devices:
  - cortex: channel 1
  - h90: channel 2
```

### Maps
```yaml
# Inline map
time_signature: {numerator: 4, denominator: 4}

# Block map
metadata:
  genre: Rock
  key: Dm
```

---

## Validation Rules

### PPQ Validation
- Must be positive integer
- Recommended range: 96-960
- Warning if outside common range (96, 192, 480, 960)

### Tempo Validation
- Must be positive number (integer or float)
- Practical range: 20-999 BPM
- Values outside range will trigger warning

### Time Signature Validation
- Numerator: typically 2-16
- Denominator: must be power of 2 (2, 4, 8, 16, 32)
- Common meters: 2/4, 3/4, 4/4, 5/4, 6/8, 7/8, 9/8, 12/8

### MIDI Format Validation
- Must be 0, 1, or 2
- Invalid values default to 1

### Channel Validation
- Must be 1-16 (MIDI channel range)
- Values outside range cause validation error

### Velocity Validation
- Must be 0-127 (MIDI value range)
- 0 = note off, 1-127 = note on with velocity

---

## Common Patterns

### Studio Production
```yaml
---
title: "Studio Session - Lead Guitar"
author: "Producer Name"
ppq: 960           # High resolution for smooth automation
tempo: 120.0
time_signature: 4/4
midi_format: 1
default_velocity: 95
---
```

### Live Performance
```yaml
---
title: "Live Set - Song 2"
ppq: 480           # Standard resolution (lower CPU)
tempo: 128
time_signature: 4/4
default_channel: 1
---
```

### Click Track / Metronome
```yaml
---
title: "Click Track - 7/8"
ppq: 192           # Lower resolution sufficient for clicks
tempo: 160
time_signature: 7/8
default_channel: 10  # GM drums
default_velocity: 80
---
```

---

## Best Practices

1. **Always specify PPQ, tempo, and time_signature** for predictable behavior
2. **Use PPQ 480** for most use cases (good balance of precision and file size)
3. **Use PPQ 960** for studio work with heavy automation
4. **Document your files** with title, author, and description
5. **Use midi_format: 1** for multi-track songs (DAW-compatible)
6. **Set default_channel** when working with single device
7. **Use ISO 8601 dates** (YYYY-MM-DD) for consistency

---

## See Also

- [MMD Specification](https://github.com/cjgdev/midi-markdown/blob/main/spec.md) - Complete language specification
- [Timing System](../user-guide/timing-system.md) - Timing paradigms and calculations
- [Quick Start Guide](../getting-started/quickstart.md) - Getting started with MMD
- [Examples](https://github.com/cjgdev/midi-markdown/blob/main/examples/README.md) - Example MMD files with frontmatter

---

**Document Version:** 1.0
**Last Updated:** 2025-11-11
