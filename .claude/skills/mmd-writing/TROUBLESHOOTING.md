# MMD Troubleshooting Guide

Common errors, their causes, and solutions when writing MIDI Markdown files.

## Table of Contents

1. [Validation Errors](#validation-errors)
2. [Timing Issues](#timing-issues)
3. [Value Range Errors](#value-range-errors)
4. [Syntax Errors](#syntax-errors)
5. [Import and Alias Errors](#import-and-alias-errors)
6. [Compilation Issues](#compilation-issues)
7. [Debugging Workflow](#debugging-workflow)

## Validation Errors

### Error: "Missing frontmatter"

**Cause**: File doesn't start with YAML frontmatter.

**Solution**:
```mmd
---
title: "My Song"
ppq: 480
tempo: 120
---

[00:00.000]
- note_on 1.C4 100 1b
```

**Required fields**: At minimum, include `ppq` or `tempo`.

---

### Error: "No timing marker before first event"

**Cause**: Command appears before any timing marker.

**Wrong**:
```mmd
---
ppq: 480
---

- note_on 1.C4 100 1b    # Error: no timing!
```

**Correct**:
```mmd
---
ppq: 480
---

[00:00.000]              # Always start with timing
- note_on 1.C4 100 1b
```

---

### Error: "Time X is before previous event at time Y"

**Cause**: Timing goes backwards (not monotonically increasing).

**Wrong**:
```mmd
[00:10.000]
- note_on 1.C4 100 1b

[00:05.000]    # Error: 5 < 10
- note_on 1.D4 100 1b
```

**Correct**:
```mmd
[00:05.000]
- note_on 1.C4 100 1b

[00:10.000]    # Timing increases
- note_on 1.D4 100 1b
```

**Tip**: Use relative timing to avoid this:
```mmd
[00:05.000]
- note_on 1.C4 100 1b

[+5s]          # Relative to previous
- note_on 1.D4 100 1b
```

## Timing Issues

### Error: "Invalid timing marker format"

**Cause**: Timing marker doesn't match any valid format.

**Wrong**:
```mmd
[1:30]         # Missing milliseconds
[00.00.000]    # Wrong separator
[1-1-0]        # Wrong separator
```

**Correct**:
```mmd
[00:01.500]    # Absolute: mm:ss.ms
[1.1.0]        # Musical: bar.beat.tick
[+500ms]       # Relative: +value unit
[@]            # Simultaneous
```

---

### Error: "Musical timing requires tempo and time_signature"

**Cause**: Using musical timing `[bar.beat.tick]` without tempo/time signature.

**Wrong**:
```mmd
---
ppq: 480
---

[1.1.0]        # Error: no tempo!
- note_on 1.C4 100 1b
```

**Correct**:
```mmd
---
ppq: 480
tempo: 120
time_signature: [4, 4]
---

[1.1.0]        # Now it works
- note_on 1.C4 100 1b
```

---

### Issue: "Timing seems off after tempo change"

**Cause**: Using absolute timing after tempo change.

**Explanation**: Absolute timing `[mm:ss.ms]` is clock-based and doesn't adapt to tempo changes. Musical timing `[bar.beat.tick]` is tempo-aware.

**Solution**: Use musical timing for tempo-aware sequences:
```mmd
[00:00.000]
- tempo 120

[1.1.0]        # Use musical timing after this
- note_on 1.C4 100 1b

[2.1.0]        # Adapts to any tempo changes
- note_on 1.D4 100 1b
```

## Value Range Errors

### Error: "Value X exceeds maximum allowed (127)"

**Cause**: MIDI value out of range.

**Wrong**:
```mmd
- cc 1.7.255        # Max is 127
- note_on 1.C4 150  # Velocity max is 127
- pc 1.200          # Program max is 127
```

**Correct**:
```mmd
- cc 1.7.127        # 0-127
- note_on 1.C4 127  # 0-127
- pc 1.127          # 0-127
```

**MIDI Value Ranges**:
- Most values: 0-127
- Channels: 1-16
- Notes: 0-127 (C-1 to G9)
- Pitch bend: -8192 to +8191 or 0 to 16383

---

### Error: "Invalid channel X"

**Cause**: Channel number outside 1-16 range.

**Wrong**:
```mmd
- note_on 0.C4 100 1b     # Channels start at 1
- note_on 18.C4 100 1b    # Max is 16
```

**Correct**:
```mmd
- note_on 1.C4 100 1b     # 1-16
- note_on 16.C4 100 1b    # Max channel
```

---

### Error: "Invalid note name"

**Cause**: Malformed note name or out of range.

**Wrong**:
```mmd
- note_on 1.H4 100 1b     # No 'H' note
- note_on 1.C10 100 1b    # Octave too high (max 9)
- note_on 1.C-2 100 1b    # Octave too low (min -1)
```

**Correct**:
```mmd
- note_on 1.B4 100 1b     # B not H
- note_on 1.C9 100 1b     # Max octave
- note_on 1.C-1 100 1b    # Min octave
- note_on 1.60 100 1b     # Or use MIDI number directly
```

**Valid notes**: C, C#/Db, D, D#/Eb, E, F, F#/Gb, G, G#/Ab, A, A#/Bb, B
**Valid octaves**: -1 to 9

## Syntax Errors

### Error: "Unexpected token at line X"

**Cause**: Syntax doesn't match MMD grammar.

**Common causes**:

1. **Missing dash for commands**:
   ```mmd
   [00:00.000]
   note_on 1.C4 100 1b    # Missing '- '
   ```
   Fix: `- note_on 1.C4 100 1b`

2. **Wrong comment syntax**:
   ```mmd
   -- This is not a comment
   ```
   Fix: `# This is a comment`

3. **Missing @end**:
   ```mmd
   @loop 4 times at [1.1.0] every 1b
     - note_on 1.C4 100 1b
   # Missing @end!
   ```
   Fix: Add `@end` after loop body

---

### Error: "Invalid variable name"

**Cause**: Variable name doesn't follow naming conventions.

**Wrong**:
```mmd
@define myvar 100          # Should be UPPERCASE
@define 123VAR 100         # Can't start with number
@define MY-VAR 100         # Use underscores not hyphens
```

**Correct**:
```mmd
@define MY_VAR 100         # UPPERCASE_WITH_UNDERSCORES
@define MAIN_TEMPO 120
@define VERSE_PRESET_1 5
```

---

### Error: "random() not supported in this context"

**Cause**: Using `random()` where it's not allowed.

**NOT Supported**:
```mmd
[00:08.random(-10,10)]              # Timing
@define VEL random(40,60)           # @define
- note_on 10.42.random(80,100) 1b   # Numeric note ID
```

**Supported**:
```mmd
- note_on 1.C4 random(70,100) 0.5b  # Velocity
- note_on 1.random(C3,C5) 80 0.5b   # Note range
- cc 1.74.random(50,90)             # CC value
```

## Import and Alias Errors

### Error: "Import file not found"

**Cause**: Invalid import path.

**Wrong**:
```mmd
@import "quad_cortex.mmd"           # Missing devices/
@import devices/quad_cortex.mmd     # Missing quotes
```

**Correct**:
```mmd
@import "devices/quad_cortex.mmd"   # Relative to project root
```

**Available device libraries**:
- `devices/quad_cortex.mmd`
- `devices/eventide_h90.mmd`
- `devices/helix.mmd`
- `devices/hx_stomp.mmd`
- `devices/hx_effects.mmd`
- `devices/hx_stomp_xl.mmd`

---

### Error: "Undefined alias"

**Cause**: Using an alias that hasn't been defined or imported.

**Wrong**:
```mmd
---
ppq: 480
---

[00:00.000]
- cortex_load 1.1.0.5    # Alias not imported!
```

**Correct**:
```mmd
---
ppq: 480
---

@import "devices/quad_cortex.mmd"

[00:00.000]
- cortex_load 1.1.0.5    # Now it works
```

---

### Error: "Parameter count mismatch"

**Cause**: Wrong number of arguments to alias.

**Wrong**:
```mmd
@import "devices/quad_cortex.mmd"

[00:00.000]
- cortex_load 1.5        # Needs 4 params: ch.setlist.group.preset
```

**Correct**:
```mmd
@import "devices/quad_cortex.mmd"

[00:00.000]
- cortex_load 1.1.0.5    # ch=1, setlist=1, group=0, preset=5
```

**Tip**: Check device library documentation for parameter requirements.

## Compilation Issues

### Error: "Circular import detected"

**Cause**: Import chain creates a loop.

**Example**:
- `song.mmd` imports `shared/common.mmd`
- `shared/common.mmd` imports `song.mmd`

**Solution**: Reorganize imports to avoid cycles. Shared definitions should never import back to main files.

---

### Issue: "MIDI file is empty"

**Causes**:
1. No timing markers with commands
2. All events filtered out by validation
3. No `@end` after loops (events not expanded)

**Debug**:
```bash
# Check what events are generated
mmdc inspect song.mmd

# Validate first
mmdc validate song.mmd --verbose
```

---

### Issue: "Compilation very slow"

**Causes**:
1. Large loops (e.g., `@loop 10000 times`)
2. Very fine-grained sweeps (e.g., `every 1t`)
3. Deeply nested structures

**Solutions**:
```mmd
# Reduce loop iterations
@loop 100 times ...  # Instead of 10000

# Use coarser intervals
@sweep ... every 50ms  # Instead of every 1t

# Flatten nested structures
```

## Debugging Workflow

### Quick Debugging Checklist

1. **Syntax check**:
   ```bash
   mmdc check song.mmd
   ```

2. **Full validation**:
   ```bash
   mmdc validate song.mmd --verbose
   ```

3. **Inspect events**:
   ```bash
   mmdc inspect song.mmd
   ```

4. **Check specific section**:
   ```bash
   mmdc inspect song.mmd | grep "00:30"
   ```

5. **Export for analysis**:
   ```bash
   mmdc compile song.mmd --format json -o debug.json
   ```

### Common Debug Patterns

**Find timing issues**:
```bash
mmdc inspect song.mmd | awk '{print $1}' | sort -c
```

**Count event types**:
```bash
mmdc inspect song.mmd | grep "note_on" | wc -l
mmdc inspect song.mmd | grep "cc" | wc -l
```

**Filter by channel**:
```bash
mmdc inspect song.mmd | grep "ch:1"
```

**Check value ranges**:
```bash
# Find any value > 127
mmdc compile song.mmd --format csv -o - | awk -F',' '{print $5}' | sort -n | tail
```

### Validation Scripts

Use the quick validation script:
```bash
python .claude/skills/mmd-writing/scripts/validate_syntax.py song.mmd
```

This performs fast syntax checks without full compilation.

### Step-by-Step Debug Process

1. **Isolate the problem**:
   - Comment out sections until error disappears
   - Binary search: comment half, test, repeat

2. **Simplify**:
   - Remove loops and sweeps
   - Test with minimal frontmatter
   - Remove imports/aliases

3. **Add back incrementally**:
   - Re-enable features one at a time
   - Test after each change

4. **Compare with working examples**:
   ```bash
   # Look at similar patterns in examples
   cat examples/00_basics/01_hello_world.mmd
   cat examples/03_advanced/01_loops_and_patterns.mmd
   ```

## Error Message Reference

### E1xx - Syntax Errors

- **E101**: Missing frontmatter
- **E102**: Invalid timing marker
- **E103**: Invalid command syntax
- **E104**: Missing @end
- **E105**: Invalid variable name

### E2xx - Validation Errors

- **E201**: Value out of range
- **E202**: Invalid channel
- **E203**: Invalid note name
- **E204**: Timing not monotonic
- **E205**: Missing required field

### E3xx - Import/Alias Errors

- **E301**: Import file not found
- **E302**: Circular import
- **E303**: Undefined alias
- **E304**: Parameter count mismatch
- **E305**: Invalid parameter value

### E4xx - Compilation Errors

- **E401**: Variable not defined
- **E402**: Invalid expression
- **E403**: Loop overflow
- **E404**: Invalid computed value

## Getting Help

If you're still stuck:

1. **Check the examples**: `examples/` directory has 49 working files
2. **Read the spec**: `spec.md` for complete language reference
3. **Use the skills**: The mmd-debugging skill can help troubleshoot
4. **File an issue**: [GitHub Issues](https://github.com/cjgdev/midi-markdown/issues)

## Related Resources

- **SKILL.md** - Quick syntax reference
- **REFERENCE.md** - Complete syntax documentation
- **EXAMPLES.md** - Pattern library
- **mmd-debugging skill** - Specialized debugging assistance
- **spec.md** - Full language specification
- **examples/** - 49 working example files

---

**Tip**: When asking for help, include:
- Your MMD file (or minimal reproduction)
- Full error message
- Output of `mmdc validate --verbose`
- What you expected vs. what happened
