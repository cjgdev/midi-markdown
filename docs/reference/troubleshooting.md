# Troubleshooting Guide

> **Audience**: Users
> **Level**: Beginner to Intermediate

Common issues and solutions when working with MIDI Markdown.

---

## Parse Errors

### "Unexpected token" Error

**Symptom**:
```
❌ error[E101]: Unexpected token 'DOT'
  → example.mmd:15:16

13 | # Simple drum pattern
14 | [00:01.000]
15 | - note_on 10.36.100 0.25b
   |                ^
```

**Causes**:
1. **Decimal note durations** - MMD doesn't support decimal beat durations like `0.25b`
2. **Invalid syntax** - Using unsupported features

**Solutions**:
```yaml
# ❌ WRONG: Decimal beat duration
- note_on 10.36.100 0.25b

# ✅ CORRECT: Use milliseconds or whole beats
- note_on 10.36.100 250ms
- note_on 10.36.100 1b

# ✅ CORRECT: Use musical timing
[1.1.0]          # Bar 1, Beat 1
- note_on 10.36.100 480t  # 480 ticks (quarter note at PPQ=480)
```

---

### "End of file while parsing" Error

**Symptom**:
```
Parse error: Unexpected end of file while parsing block
```

**Causes**:
- Missing `@end` for `@alias`, `@loop`, or `@track` block
- Unclosed string literal
- Missing closing bracket

**Solutions**:
```yaml
# ❌ WRONG: Missing @end
@alias test {note}
  - note_on 1.{note}.80 1b
# Missing @end here!

# ✅ CORRECT: Proper closing
@alias test {note}
  - note_on 1.{note}.80 1b
@end
```

---

## Timing Errors

### "Timing must be monotonically increasing"

**Symptom**:
```
❌ Validation error: Timing must be monotonically increasing
   Found: 00:02.000 after 00:03.000
```

**Cause**:
- Events are out of chronological order
- Time goes backwards

**Solution**:
```yaml
# ❌ WRONG: Time goes backwards
[00:03.000]
- note_on 1.60.80 1b
[00:02.000]  # ← Error: Earlier than previous
- note_on 1.64.80 1b

# ✅ CORRECT: Chronological order
[00:02.000]
- note_on 1.64.80 1b
[00:03.000]
- note_on 1.60.80 1b
```

---

### "Musical time requires tempo"

**Symptom**:
```
❌ Validation error: Musical time requires tempo to be set
```

**Cause**:
- Using musical timing (`[1.1.0]`) without setting tempo
- Missing `time_signature` in frontmatter

**Solution**:
```yaml
# ❌ WRONG: Musical timing without tempo
---
title: "Song"
ppq: 480
---

[1.1.0]  # ← Error: No tempo set
- note_on 1.60.80 1b

# ✅ CORRECT: Set tempo first
---
title: "Song"
tempo: 120
time_signature: "4/4"
ppq: 480
---

[00:00.000]
- tempo 120  # Or set it here

[1.1.0]  # Now this works
- note_on 1.60.80 1b
```

---

## Alias Errors

### "Undefined alias"

**Symptom**:
```
❌ Alias error: Undefined alias 'my_chord'
```

**Cause**:
- Calling an alias that hasn't been defined
- Typo in alias name
- Alias defined after it's used

**Solution**:
```yaml
# ❌ WRONG: Alias used before definition
[00:00.000]
- my_chord 1.60.80  # ← Error: Not defined yet

@alias my_chord {ch}.{note}.{vel}
  - note_on {ch}.{note}.{vel} 1b
@end

# ✅ CORRECT: Define before use
@alias my_chord {ch}.{note}.{vel}
  - note_on {ch}.{note}.{vel} 1b
@end

[00:00.000]
- my_chord 1.60.80  # Now this works
```

---

### "Wrong number of parameters"

**Symptom**:
```
❌ Alias error: Expected 3 parameters, got 2
```

**Cause**:
- Calling alias with incorrect number of arguments

**Solution**:
```yaml
@alias chord {ch}.{root}.{vel}
  - note_on {ch}.{root}.{vel} 1b
  - note_on {ch}.{root+4}.{vel} 1b
  - note_on {ch}.{root+7}.{vel} 1b
@end

# ❌ WRONG: Missing velocity parameter
[00:00.000]
- chord 1.60  # Only 2 args, needs 3

# ✅ CORRECT: All 3 parameters
[00:00.000]
- chord 1.60.80  # ch=1, root=60, vel=80
```

---

## MIDI Playback Issues

### "No MIDI ports found"

**Symptom**:
```
❌ Error: No MIDI output ports available
```

**Platform-Specific Solutions**:

#### macOS:
```bash
# 1. Enable IAC Driver
# - Open "Audio MIDI Setup" app
# - Window → Show MIDI Studio
# - Double-click "IAC Driver"
# - Check "Device is online"

# 2. Verify ports
mmdc play --list-ports

# Should show: IAC Driver Bus 1
```

#### Linux:
```bash
# 1. Install ALSA MIDI
sudo apt-get install libasound2-dev

# 2. Load virtual MIDI module
sudo modprobe snd-virmidi

# 3. Verify
aconnect -l

# 4. Play with specific port
mmdc play song.mmd --port 0
```

#### Windows:
```bash
# 1. Install loopMIDI
# Download from: https://www.tobias-erichsen.de/software/loopmidi.html

# 2. Create virtual port in loopMIDI application

# 3. Verify
mmdc play --list-ports

# 4. Play
mmdc play song.mmd --port "loopMIDI Port"
```

---

### "Permission denied" on Linux

**Symptom**:
```
PermissionError: [Errno 13] Permission denied: '/dev/snd/seq'
```

**Solution**:
```bash
# Add your user to the audio group
sudo usermod -a -G audio $USER

# Log out and log back in, then verify
groups  # Should show "audio"

# Alternative: Run with sudo (not recommended)
sudo mmdc play song.mmd
```

---

## Validation Errors

### "Invalid MIDI value"

**Symptom**:
```
❌ Validation error: MIDI value 128 out of range (0-127)
```

**Cause**:
- MIDI values must be 0-127
- Note numbers, velocities, CC values are limited

**Solution**:
```yaml
# ❌ WRONG: Value too high
- note_on 1.60.128 1b  # Velocity > 127
- cc 1.7.200           # CC value > 127

# ✅ CORRECT: Valid range
- note_on 1.60.127 1b  # Max velocity
- cc 1.7.127           # Max CC value
```

---

### "Invalid channel"

**Symptom**:
```
❌ Validation error: MIDI channel 16 out of range (1-16)
```

**Note**: MIDI channels are 1-16, not 0-15 in MML!

**Solution**:
```yaml
# ❌ WRONG: Channel 0 or > 16
- note_on 0.60.80 1b   # Channel 0 invalid
- note_on 17.60.80 1b  # Channel 17 invalid

# ✅ CORRECT: Channels 1-16
- note_on 1.60.80 1b   # Channel 1
- note_on 10.36.100 1b # Channel 10 (drums)
- note_on 16.60.80 1b  # Channel 16
```

---

## REPL Issues

### REPL won't exit with `.quit`

**Symptom**:
- Typing `.quit` doesn't exit the REPL
- Have to use Ctrl+C

**Known Issue**:
- pexpect EOF handling with prompt_toolkit is flaky
- Some tests are skipped due to this

**Workarounds**:
```bash
# Use Ctrl+D (EOF) instead
# Or Ctrl+C to force quit
```

---

## Compilation Performance Issues

### "Compilation is slow for large files"

**Symptom**:
- Files with >1000 events take several seconds

**Expected Performance**:
- Small files (<100 events): <200ms
- Medium files (100-500 events): <500ms
- Large files (>1000 events): <2s

**Solutions**:
1. **Use `--dry-run` for syntax checking** (faster than full compile)
2. **Break large files into sections** with `@import`
3. **Reduce loop iterations** during development

```bash
# Fast syntax check
mmdc check large_file.mmd  # <1s

# Full compilation
mmdc compile large_file.mmd  # May take 2-3s for large files
```

---

## File Organization Issues

### "Import not found"

**Symptom**:
```
❌ Import error: File not found: devices/my_device.mmd
```

**Cause**:
- Import path is relative to current file
- File doesn't exist

**Solution**:
```yaml
# File structure:
# project/
#   song.mmd
#   devices/
#     quad_cortex.mmd

# In song.mmd:
# ❌ WRONG: Absolute path
@import "/devices/quad_cortex.mmd"

# ✅ CORRECT: Relative path
@import "devices/quad_cortex.mmd"
```

---

## Getting Help

### Still Stuck?

1. **Check the examples** - `examples/` directory has working code
2. **Run with verbose** - `mmdc compile -v` shows detailed output
3. **Use inspect** - `mmdc inspect file.mmd` shows parsed events
4. **File an issue** - [GitHub Issues](https://github.com/cjgdev/midi-markdown/issues)

### Useful Commands

```bash
# Syntax check only (fast)
mmdc check file.mmd

# Full validation
mmdc validate file.mmd

# Verbose output
mmdc compile file.mmd -v

# Inspect parsed events
mmdc inspect file.mmd

# Show version and dependencies
mmdc version
```

---

## See Also

- [FAQ](faq.md) - Frequently asked questions
- [CLI Reference](../cli-reference/overview.md) - Command documentation
- [MML Syntax Guide](../user-guide/mmd-syntax.md) - Complete syntax reference
