# Timing System Deep Dive

This guide documents the complete timing system implementation for MIDI Markdown.

## Overview

MIDI Markdown supports 4 timing paradigms:
1. **Absolute** - `[mm:ss.milliseconds]`
2. **Musical** - `[bars.beats.ticks]`
3. **Relative** - `[+value unit]`
4. **Simultaneous** - `[@]`

All timing is ultimately converted to **absolute ticks** for MIDI file generation.

## Core Formula Reference

### Absolute Timing → Ticks

```python
# [mm:ss.milliseconds] → ticks
seconds = float(timing.value)
ticks_per_second = (ppq * tempo) / 60.0
absolute_ticks = int(seconds * ticks_per_second)
```

**Example:**
- Time: `[00:02.500]` (2.5 seconds)
- Tempo: 120 BPM
- PPQ: 480
- Result: `2.5 * (480 * 120 / 60) = 2.5 * 960 = 2400 ticks`

### Musical Timing → Ticks

```python
# [bars.beats.ticks] → absolute ticks
bar, beat, tick = timing.value  # All 1-indexed!

beats_per_bar = time_signature[0]  # Numerator (e.g., 4 for 4/4)
ticks_per_beat = ppq

absolute_ticks = (
    (bar - 1) * beats_per_bar * ticks_per_beat  # Full bars
    + (beat - 1) * ticks_per_beat                # Beats in current bar
    + tick                                        # Ticks in current beat
)
```

**Example:**
- Time: `[2.3.240]` (bar 2, beat 3, tick 240)
- Time signature: 4/4
- PPQ: 480
- Calculation:
  - Bars: `(2-1) * 4 * 480 = 1920 ticks`
  - Beats: `(3-1) * 480 = 960 ticks`
  - Ticks: `240 ticks`
  - **Total: 3120 ticks**

**CRITICAL:** Bars and beats are **1-indexed** (subtract 1 in calculations)!

### Relative Timing → Ticks

```python
# [+value unit] → current_time + delta
delta_value, unit = timing.value

# Supported units:
# t = ticks (direct)
# b = beats
# m = measures (bars)
# s = seconds
# ms = milliseconds

if unit == "t":
    return current_time + int(delta_value)

elif unit == "b":
    ticks_per_beat = ppq
    return current_time + int(delta_value * ticks_per_beat)

elif unit == "m":
    beats_per_bar = time_signature[0]
    ticks_per_bar = ppq * beats_per_bar
    return current_time + int(delta_value * ticks_per_bar)

elif unit == "s":
    ticks_per_second = (ppq * tempo) / 60.0
    return current_time + int(delta_value * ticks_per_second)

elif unit == "ms":
    ticks_per_second = (ppq * tempo) / 60.0
    return current_time + int((delta_value / 1000.0) * ticks_per_second)
```

**Example:**
- Current time: `1920 ticks`
- Relative: `[+2b]` (2 beats)
- PPQ: 480
- Result: `1920 + (2 * 480) = 2880 ticks`

### Simultaneous Timing

```python
# [@] → use current_time without advancing
return current_time
```

**Use case:** Multiple commands at same moment:
```
[00:05.000]
- note_on 1.C4 100 1b
[@]
- cc 1.7.127  # Happens simultaneously with note
```

## Implementation Reference

**File:** `src/midi_markdown/expansion/expander.py`

**Function:** `_compute_absolute_time(timing: TimingMarker) -> int`

**Lines:** 761-860

```python
def _compute_absolute_time(self, timing: TimingMarker) -> int:
    """Convert any timing format to absolute ticks.

    Args:
        timing: TimingMarker AST node

    Returns:
        Absolute time in ticks

    Raises:
        ValueError: If timing format is invalid or references are missing
    """

    # 1. ABSOLUTE TIMING: [mm:ss.milliseconds]
    if timing.type == "absolute":
        seconds = float(timing.value)
        ticks_per_second = (self.ppq * self.tempo) / 60.0
        return int(seconds * ticks_per_second)

    # 2. MUSICAL TIMING: [bars.beats.ticks]
    if timing.type == "musical":
        bar, beat, tick = timing.value  # 1-indexed!

        beats_per_bar = self.time_signature[0]
        ticks_per_beat = self.ppq

        # CRITICAL: Subtract 1 from bars and beats (1-indexed)
        absolute_ticks = (
            (bar - 1) * beats_per_bar * ticks_per_beat
            + (beat - 1) * ticks_per_beat
            + tick
        )
        return int(absolute_ticks)

    # 3. RELATIVE TIMING: [+value unit]
    if timing.type == "relative":
        delta_value, unit = timing.value

        if unit == "t":  # Ticks
            return self.current_time + int(delta_value)

        elif unit == "b":  # Beats
            ticks_per_beat = self.ppq
            return self.current_time + int(delta_value * ticks_per_beat)

        elif unit == "m":  # Measures (bars)
            beats_per_bar = self.time_signature[0]
            ticks_per_bar = self.ppq * beats_per_bar
            return self.current_time + int(delta_value * ticks_per_bar)

        elif unit == "s":  # Seconds
            ticks_per_second = (self.ppq * self.tempo) / 60.0
            return self.current_time + int(delta_value * ticks_per_second)

        elif unit == "ms":  # Milliseconds
            ticks_per_second = (self.ppq * self.tempo) / 60.0
            delta_seconds = delta_value / 1000.0
            return self.current_time + int(delta_seconds * ticks_per_second)

        else:
            raise ValueError(f"Unknown relative timing unit: {unit}")

    # 4. SIMULTANEOUS TIMING: [@]
    if timing.type == "simultaneous":
        return self.current_time

    raise ValueError(f"Unknown timing type: {timing.type}")
```

## Required State

The timing system depends on these expander state variables:

```python
class CommandExpander:
    def __init__(self, document: Document, ppq: int = 480):
        self.ppq = ppq  # Pulses Per Quarter note (resolution)
        self.tempo = 120  # BPM (default, overridden by tempo commands)
        self.time_signature = (4, 4)  # (numerator, denominator)
        self.current_time = 0  # Accumulated ticks
```

**Where these come from:**
- `ppq`: Frontmatter `ppq: 480` or CLI flag `--ppq`
- `tempo`: Initial from frontmatter, updated by `- tempo 140` commands
- `time_signature`: Frontmatter `time_signature: 3/4` (defaults to 4/4)
- `current_time`: Tracked as events are processed

## Edge Cases

### 1. Missing Time Signature for Musical Time

```python
# ❌ WRONG - assumes 4/4
beats_per_bar = 4  # Hardcoded!

# ✅ CORRECT - extract from frontmatter
beats_per_bar = self.time_signature[0]
```

**Test case:**
```
---
time_signature: 7/8
---

[1.1.0]  # Bar 1, beat 1
[2.1.0]  # Should be 7 beats later, not 4!
```

### 2. Relative Timing Without Previous Event

```python
# First event can't use relative timing
[+1b]  # ERROR - no previous event to reference

# Fix: Use absolute or musical time first
[00:00.000]  # Establish baseline
[+1b]        # Now OK
```

### 3. Fractional Ticks

```python
# Timing calculations may produce floats
delta_ticks = delta_value * ticks_per_beat  # Could be 480.75

# Always cast to int (MIDI ticks are integers)
return int(delta_ticks)  # Truncates, doesn't round
```

### 4. Tempo Changes Mid-Song

```python
# Tempo affects absolute timing calculations
[00:00.000]
- tempo 120  # 960 ticks/second (at PPQ=480)

[00:10.000]  # 10 seconds = 9600 ticks
- tempo 140  # NOW 1120 ticks/second

[00:20.000]  # Next 10 seconds = 11200 ticks
# Total: 9600 + 11200 = 20800 ticks
```

**CRITICAL:** Tempo changes affect subsequent absolute timing!

## Loop and Sweep Timing

### Loop Timing Semantics

```python
@loop 4 times at [start_time] every 1b
  - note_on 10.C1 100 1b
@end
```

**Key rules:**
1. `at [start_time]` is **independent** of preceding timing markers
2. `at [00:00.000]` means "start at beginning" NOT "start at current time"
3. For relative to previous marker, use `at [+duration]` or omit `at` clause

**Examples:**

```
# Absolute timing - ignores previous context
[00:10.000]
@loop 4 times at [00:05.000] every 1b  # Starts at 5 seconds, NOT 10!
  - note_on 10.C1 100 1b
@end

# Relative timing - adds to previous
[00:10.000]
@loop 4 times at [+2s] every 1b  # Starts at 12 seconds (10 + 2)
  - note_on 10.C1 100 1b
@end

# Implicit timing - uses previous marker
[00:10.000]
@loop 4 times every 1b  # Starts at 10 seconds
  - note_on 10.C1 100 1b
@end
```

**Implementation:** See `expansion/loops.py:expand_loop()`

### Sweep Timing

```python
@sweep from [start] to [end] every interval
  - cc 1.7 ramp(0, 127)
@end
```

**Calculation:**
```python
start_ticks = compute_absolute_time(start_timing)
end_ticks = compute_absolute_time(end_timing)
interval_ticks = compute_absolute_time(interval_timing)

num_steps = (end_ticks - start_ticks) // interval_ticks
current_tick = start_ticks

for i in range(num_steps):
    value = start_val + (end_val - start_val) * (i / num_steps)
    # Emit event at current_tick
    current_tick += interval_ticks
```

**Implementation:** See `expansion/sweeps.py:expand_sweep()`

## Debugging Timing Issues

### Diagnostic Commands

```bash
# Visual timeline view
just run inspect song.mmd

# CSV export for spreadsheet analysis
just run compile song.mmd --format csv -o events.csv

# JSON export for programmatic querying
just run compile song.mmd --format json > events.json
jq '.events[] | select(.time > 5000)' events.json
```

### Common Bugs

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Events 4 beats too early/late | Forgot to subtract 1 from bars/beats | Check 1-indexed conversion |
| Relative timing not accumulating | `current_time` not updated | Update after each event |
| Musical time incorrect | Wrong time signature assumed | Check frontmatter `time_signature` |
| Tempo change ignored | Using old tempo in calculation | Re-fetch tempo before conversion |

### Test Pattern

```python
def test_timing_conversion(self, parser):
    """Test all timing paradigms produce correct ticks."""
    mml = """
---
ppq: 480
time_signature: 4/4
---

[00:00.000]
- tempo 120

[00:01.000]  # Should be 960 ticks (1 sec * 960 ticks/sec)
- pc 1.0

[1.1.0]      # Should be 0 ticks (bar 1, beat 1)
- pc 1.1

[2.1.0]      # Should be 1920 ticks (4 beats * 480)
- pc 1.2

[+1b]        # Should be 2400 ticks (1920 + 480)
- pc 1.3

[@]          # Should be 2400 ticks (same as previous)
- pc 1.4
"""
    doc = parser.parse_string(mml)
    ir = compile_ast_to_ir(doc, ppq=480)

    assert ir.events[0].time == 960   # [00:01.000]
    assert ir.events[1].time == 0     # [1.1.0]
    assert ir.events[2].time == 1920  # [2.1.0]
    assert ir.events[3].time == 2400  # [+1b]
    assert ir.events[4].time == 2400  # [@]
```

## Reference

**See also:**
- [specification.md](../reference/specification.md#timing-specification) - User-facing timing documentation
- [parser-patterns.md](./parser-patterns.md) - Parsing timing markers
- [examples/01_timing/](https://github.com/cjgdev/midi-markdown/tree/main/examples/01_timing) - Working timing examples
