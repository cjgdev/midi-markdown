# Anti-Patterns (From Our Mistakes)

This document catalogs **actual bugs and issues** we've encountered in this codebase. Learning from these mistakes will help you avoid repeating them.

## Overview

These are not theoretical "bad practices" - these are real bugs that made it into commits and had to be fixed. Each entry includes:
- **The Bug:** What the broken code looked like
- **Root Cause:** Why it was wrong
- **Impact:** What broke because of it
- **The Fix:** Corrected implementation
- **Lesson:** Key takeaway

---

## ❌ DON'T: Use Full Command Names in Code

### The Bug

```python
# BROKEN - validation was checking full names
if cmd_type == "control_change":  # Never matches!
    validate_cc_range(...)

# Parser/transformer uses abbreviated types
MIDICommand(type="cc", ...)  # NOT "control_change"
```

### Root Cause

**Type mismatch between parser and validator:**
- Transformer creates `MIDICommand(type="cc", ...)`
- Validation checked `if cmd_type == "control_change"`
- Condition never matched, validation silently skipped

### Impact

- CC and PC validation was **completely bypassed**
- Invalid values (>127) passed validation
- MIDI files generated with invalid data
- No test coverage caught this (tests only checked parsing, not validation)

### The Fix

```python
# CORRECT - use abbreviated types everywhere
if cmd_type == "cc":  # Matches transformer output
    validate_cc_range(...)

# Accept both forms for robustness
COMMAND_TYPE_MAP = {
    "cc": "cc",
    "control_change": "cc",  # Compatibility fallback
    "pc": "pc",
    "program_change": "pc",
}

canonical_type = COMMAND_TYPE_MAP.get(cmd_type, cmd_type)
```

### Lesson

**Always use abbreviated command types** (`"cc"`, `"pc"`, `"note_on"`, `"pitch_bend"`). This is the canonical form throughout the codebase. If you need to accept both forms, normalize to abbreviated immediately.

**Reference:** Fixed in `expansion/expander.py:888-896`

---

## ❌ DON'T: Modify AST Nodes After Parsing

### The Bug

```python
# BROKEN - mutating AST breaks validation
for event in ast.events:
    event.time = new_time  # Mutation!
    event.timing = new_timing_marker
```

### Root Cause

**AST immutability assumption violated:**
- Parser creates frozen AST structure
- Validation assumes AST hasn't changed
- Timing calculations depend on original timing markers

### Impact

- Validation errors with incorrect line numbers
- Timing calculations wrong on second pass
- Debugging impossible (AST doesn't match source)

### The Fix

```python
# CORRECT - create new events in expansion phase
new_events = []
for original in ast.events:
    new_event = MIDICommand(
        type=original.type,
        channel=original.channel,
        timing=new_timing,  # New timing, don't mutate original
        data1=original.data1,
        data2=original.data2,
        source_line=original.source_line,
    )
    new_events.append(new_event)
```

### Lesson

**Never modify AST nodes after parsing.** Create new nodes with updated fields instead. The AST is the source of truth - keep it immutable.

**Reference:** See `expansion/variables.py` and `expansion/loops.py` for correct patterns

---

## ❌ DON'T: Forget to Check `isinstance(value, tuple)`

### The Bug

```python
# BROKEN - crashes on forward references
def program_change(self, channel, program):
    channel_val = self._resolve_param(channel)
    # TypeError if channel_val is ('var', 'VAR_NAME')!
    channel = int(channel_val)
```

### Root Cause

**Forward references stored as tuples:**
- Variables can be used before definition (forward references)
- Unresolved variables stored as `('var', 'VAR_NAME')` tuples
- Direct `int()` conversion fails on tuples

### Impact

```python
# This code crashes:
@define MY_CHANNEL 5

[00:00.000]
- pc ${MY_CHANNEL}.10  # Works - variable resolved

- pc ${FUTURE_VAR}.10  # Crashes - forward reference is tuple
@define FUTURE_VAR 3
```

### The Fix

```python
# CORRECT - check type before converting
def program_change(self, channel, program):
    channel_val = self._resolve_param(channel)
    program_val = self._resolve_param(program)

    # Check isinstance before int() conversion
    channel_int = int(channel_val) if not isinstance(channel_val, tuple) else channel_val
    program_int = int(program_val) if not isinstance(program_val, tuple) else program_val

    return MIDICommand(type="pc", channel=channel_int, data1=program_int)
```

### Lesson

**Always check `isinstance(value, tuple)` before converting to int.** Forward references are tuples and must be preserved until variable resolution phase.

**Reference:** See `parser/transformer.py` - every transformer method does this check

---

## ❌ DON'T: Add Timing Statements Inside Alias Definitions

### The Bug

```python
# BROKEN - absolute timing in alias definition
@alias my_preset_load {ch}.{preset}
  [00:05.000]  # Don't do this!
  - pc {ch}.{preset}
@end

# Usage - timing is hardcoded!
- my_preset_load 1 42  # Always loads at 5 seconds
```

### Root Cause

**Aliases should be timing-agnostic:**
- Absolute timing in alias breaks reusability
- Caller should control when alias executes
- Timing must be computed during expansion, not definition

### Impact

```python
# This doesn't work as expected:
[00:10.000]
- my_preset_load 1 10  # Expands to [00:05.000] not [00:10.000]!

[00:20.000]
- my_preset_load 1 20  # Also expands to [00:05.000]!
```

### The Fix

```python
# CORRECT - use relative timing in aliases
@alias my_preset_load {ch}.{preset}
  [+50ms]  # Relative timing is OK - adds to caller's time
  - pc {ch}.{preset}
@end

# Usage - caller controls timing
[00:10.000]
- my_preset_load 1 42  # Loads at 10.05 seconds

# OR: Let caller control timing entirely
@alias my_preset_load {ch}.{preset}
  - pc {ch}.{preset}  # No timing - inherits from caller
@end

[00:10.000]
- my_preset_load 1 42  # Loads at 10 seconds
```

### Lesson

**Never use absolute timing in aliases.** Use relative timing (`[+duration]`) if you need delays, or let the caller control timing entirely.

**Reference:** Relative timing in aliases implemented in `alias/resolver.py`

---

## ❌ DON'T: Skip IR Layer for Output

### The Bug

```python
# BROKEN - direct AST to MIDI
def compile_to_midi(ast: Document) -> bytes:
    mido_track = []
    for event in ast.events:
        # Bypasses validation!
        # Bypasses timing calculations!
        # Bypasses IR query capabilities!
        mido_track.append(create_midi_message(event))

    return save_midi_file(mido_track)
```

### Root Cause

**IR layer exists for a reason:**
- Validation happens during IR compilation
- Timing calculations happen during IR compilation
- IR enables diagnostics (inspect, JSON export, CSV export)
- IR enables real-time playback

### Impact

- Validation silently skipped
- Timing calculations wrong (no expansion)
- No diagnostic output available
- Can't implement real-time playback

### The Fix

```python
# CORRECT - always compile to IR first
def compile_to_midi(ast: Document, ppq: int = 480) -> bytes:
    # Step 1: Compile AST to IR (includes validation and timing)
    ir_program = compile_ast_to_ir(ast, ppq=ppq)
    # IR includes:
    # - Validated events
    # - Computed absolute timing
    # - Metadata for diagnostics

    # Step 2: Generate output from IR
    midi_bytes = generate_midi_file(ir_program)
    return midi_bytes
```

### Lesson

**Always use the IR layer.** Never go directly from AST to output. The IR layer is the validated, expanded, timing-resolved representation.

**Reference:** See `core/compiler.py` and `codegen/midi_file.py`

---

## ❌ DON'T: Hardcode Time Signature for Musical Timing

### The Bug

```python
# BROKEN - assumes 4/4 time
def compute_musical_time(bar, beat, tick):
    beats_per_bar = 4  # Hardcoded!
    ticks_per_beat = 480

    absolute_ticks = (
        (bar - 1) * beats_per_bar * ticks_per_beat
        + (beat - 1) * ticks_per_beat
        + tick
    )
    return absolute_ticks
```

### Root Cause

**Time signatures vary:**
- Different meters: 3/4, 6/8, 5/4, 7/8, 12/8, etc.
- Musical timing `[8.4.120]` depends on time signature
- Hardcoding breaks non-4/4 songs

### Impact

```python
# This breaks in 3/4 time:
---
time_signature: 3/4
---

[1.1.0]  # Bar 1, beat 1
[2.1.0]  # Bar 2, beat 1 - should be 3 beats later
         # But code calculates 4 beats (assumes 4/4)!
```

### The Fix

```python
# CORRECT - extract from frontmatter or state
def compute_musical_time(bar, beat, tick, time_signature):
    beats_per_bar = time_signature[0]  # Numerator
    ticks_per_beat = self.ppq

    absolute_ticks = (
        (bar - 1) * beats_per_bar * ticks_per_beat
        + (beat - 1) * ticks_per_beat
        + tick
    )
    return absolute_ticks

# In expander:
self.time_signature = document.frontmatter.get("time_signature", (4, 4))
```

### Lesson

**Always get time signature from frontmatter or state.** Never hardcode beats_per_bar. Default to 4/4 if missing, but support all time signatures.

**Reference:** Parser defaults to 4/4 but validation catches missing declarations

---

## ❌ DON'T: Forget 1-Indexed Bar/Beat Conversion

### The Bug

```python
# BROKEN - treats bars/beats as 0-indexed
def compute_musical_time(bar, beat, tick):
    absolute_ticks = (
        bar * beats_per_bar * ticks_per_beat  # Missing -1!
        + beat * ticks_per_beat               # Missing -1!
        + tick
    )
```

### Root Cause

**Musical notation is 1-indexed:**
- Musicians think "bar 1, beat 1" (not "bar 0, beat 0")
- MIDI ticks are 0-indexed (start at tick 0)
- Must subtract 1 to convert

### Impact

```python
# This produces wrong timing:
[1.1.0]  # Bar 1, beat 1
# With bug: 1 * 4 * 480 + 1 * 480 + 0 = 2400 ticks
# Correct:  (1-1) * 4 * 480 + (1-1) * 480 + 0 = 0 ticks

[2.1.0]  # Bar 2, beat 1
# With bug: 2 * 4 * 480 + 1 * 480 + 0 = 4320 ticks
# Correct:  (2-1) * 4 * 480 + (1-1) * 480 + 0 = 1920 ticks
```

### The Fix

```python
# CORRECT - subtract 1 from bars and beats
def compute_musical_time(bar, beat, tick):
    absolute_ticks = (
        (bar - 1) * beats_per_bar * ticks_per_beat  # 1-indexed!
        + (beat - 1) * ticks_per_beat               # 1-indexed!
        + tick  # Already 0-indexed
    )
    return absolute_ticks
```

### Lesson

**Always subtract 1 from bars and beats in musical timing calculations.** They're 1-indexed in user syntax, 0-indexed in MIDI ticks.

**Reference:** See `expansion/expander.py:_compute_absolute_time()`

---

## ❌ DON'T: Use subprocess for CLI Testing

### The Bug

```python
# BROKEN - brittle subprocess testing
def test_compile_command():
    result = subprocess.run(
        ["mmdc", "compile", "input.mmd", "-o", "output.mid"],
        capture_output=True,
    )
    assert result.returncode == 0
```

### Root Cause

**subprocess is fragile:**
- Requires CLI to be installed in PATH
- Doesn't work in CI without extra setup
- Can't test before installation
- Slower than in-process testing

### Impact

- Tests fail in development environment
- CI requires complex setup
- Can't test work-in-progress code
- Debugging harder (separate process)

### The Fix

```python
# CORRECT - use CliRunner for in-process testing
from typer.testing import CliRunner

def test_compile_command(tmp_path: Path):
    runner = CliRunner()

    input_file = tmp_path / "input.mmd"
    input_file.write_text("[00:00.000]\n- pc 1.0")
    output_file = tmp_path / "output.mid"

    result = runner.invoke(
        app,
        ["compile", str(input_file), "-o", str(output_file)],
    )

    assert result.exit_code == 0
    assert output_file.exists()
    assert "Compilation successful" in result.stdout
```

### Lesson

**Always use `CliRunner` for CLI testing, NOT `subprocess`.** It's faster, more reliable, and works in all environments.

**Reference:** See `tests/integration/test_cli.py` for examples

---

## ❌ DON'T: Ignore Tempo Changes for Absolute Timing

### The Bug

```python
# BROKEN - uses initial tempo for all conversions
def __init__(self):
    self.tempo = 120  # Set once

def compute_absolute_time(self, seconds):
    # Always uses 120 BPM, even if tempo changed!
    ticks_per_second = (self.ppq * self.tempo) / 60.0
    return int(seconds * ticks_per_second)
```

### Root Cause

**Tempo affects tick rate:**
- At 120 BPM: 1 second = 960 ticks (at PPQ 480)
- At 140 BPM: 1 second = 1120 ticks (at PPQ 480)
- Absolute timing `[mm:ss.ms]` depends on current tempo

### Impact

```python
# This produces wrong timing:
[00:00.000]
- tempo 120

[00:10.000]  # 10 seconds = 9600 ticks at 120 BPM ✓
- tempo 140

[00:20.000]  # Next 10 seconds should be 11200 ticks at 140 BPM
             # But code uses 9600 ticks (still using 120 BPM)!
```

### The Fix

```python
# CORRECT - track tempo state and use current value
def process_event(self, event):
    # Update tempo state when tempo command encountered
    if event.type == "tempo":
        self.tempo = event.data1

def compute_absolute_time(self, seconds):
    # Use current tempo (may have changed)
    ticks_per_second = (self.ppq * self.tempo) / 60.0
    return int(seconds * ticks_per_second)
```

### Lesson

**Tempo is stateful.** Update `self.tempo` when tempo commands are processed, and always use the current value for absolute timing calculations.

**Reference:** See `expansion/expander.py:process_ast()`

---

## ❌ DON'T: Create Aliases Without Description

### The Bug

```python
# BROKEN - no description
@alias cortex_preset pc.{ch}.{preset}
```

### Root Cause

**Descriptions enable:**
- Auto-generated documentation
- CLI help text
- IDE autocomplete hints
- Maintainability for future developers

### Impact

```bash
# This produces unhelpful output:
$ mmdc library info quad_cortex

Aliases:
  cortex_preset  # No description!
  cortex_scene   # No description!
```

### The Fix

```python
# CORRECT - always include description
@alias cortex_preset pc.{ch}.{preset} "Load preset (0-127)"
@alias cortex_scene pc.{ch}.{scene:0-7} "Switch to scene (0=A, 1=B, ..., 7=H)"
```

### Lesson

**Always add descriptions to aliases.** They're used for documentation, help text, and maintainability. Treat them as required.

**Reference:** See `devices/quad_cortex.mmd` for examples

---

## Summary: Key Lessons

1. ✅ **Use abbreviated command types** (`"cc"`, `"pc"`, not `"control_change"`)
2. ✅ **Never mutate AST nodes** - create new ones instead
3. ✅ **Check `isinstance(value, tuple)`** before `int()` conversion
4. ✅ **No absolute timing in aliases** - use relative or let caller control
5. ✅ **Always compile through IR layer** - never skip validation
6. ✅ **Extract time signature from frontmatter** - don't hardcode 4/4
7. ✅ **Subtract 1 from bars/beats** - they're 1-indexed in syntax
8. ✅ **Use `CliRunner` not `subprocess`** for CLI tests
9. ✅ **Track tempo state** - it changes during processing
10. ✅ **Add descriptions to aliases** - enables documentation

## Reference

**See also:**
- [parser-patterns.md](./parser-patterns.md) - Correct implementation patterns
- [timing-system.md](./timing-system.md) - Timing calculation details
- [common-tasks.md](./common-tasks.md) - Step-by-step workflows
