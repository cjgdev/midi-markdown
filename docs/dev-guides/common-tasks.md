# Common Development Tasks

This guide provides step-by-step workflows for frequent development tasks in the MIDI Markdown project.

## Quick Reference

| Task | Files to Modify | Estimated Time |
|------|----------------|----------------|
| Add MIDI command | Grammar, Transformer, Validation, Tests | 30-45 min |
| Add device library | `devices/your_device.mmd`, Tests | 1-2 hours |
| Debug timing issue | Use `inspect` command, check `expander.py` | 15-30 min |
| Add alias to device | Device library file | 5-10 min |
| Performance profiling | Install pytest-profiling, analyze | 30 min |

---

## Task 1: Adding a New MIDI Command Type

**Use case:** Adding support for a new MIDI command (e.g., custom SysEx, new meta event)

### Prerequisites
- Understanding of MIDI specification for the command
- Knowledge of parameter ranges

### Step-by-Step

#### 1. Add Grammar Rule

**File:** `src/midi_markdown/parser/mmd.lark`

```lark
// Add after existing MIDI commands
your_command: "-" ("your_command" | "yc") param "." param
```

**Naming convention:**
- Full name in snake_case: `your_command`
- Abbreviated form (2-3 chars): `yc`
- Parameters: use `param` token (handles variables)

#### 2. Add Transformer Method

**File:** `src/midi_markdown/parser/transformer.py`

```python
def your_command(self, param1, param2):
    """Transform your_command to AST node.

    Syntax: - yc 1.42

    Args:
        param1: First parameter (channel or value)
        param2: Second parameter

    Returns:
        MIDICommand with type="yc"
    """
    # Resolve parameters (handles variables)
    param1_val = self._resolve_param(param1)
    param2_val = self._resolve_param(param2)

    # Check for forward references (tuples)
    param1_int = int(param1_val) if not isinstance(param1_val, tuple) else param1_val
    param2_int = int(param2_val) if not isinstance(param2_val, tuple) else param2_val

    return MIDICommand(
        type="yc",  # CRITICAL: Use abbreviated form!
        channel=param1_int,
        data1=param2_int,
    )
```

#### 3. Add Validation

**File:** `src/midi_markdown/utils/validation/value_validator.py`

```python
def validate_your_command(channel: int, value: int) -> None:
    """Validate your_command parameters.

    Args:
        channel: MIDI channel (1-16)
        value: Command value

    Raises:
        ValueError: If parameters are out of range
    """
    if not (1 <= channel <= 16):
        raise ValueError(f"Channel {channel} out of range (1-16)")

    if not (0 <= value <= 127):
        raise ValueError(f"Value {value} out of range (0-127)")
```

**Register validator in expansion phase:**

**File:** `src/midi_markdown/expansion/expander.py`

```python
# In validate_event() method
elif event.type == "yc":
    validate_your_command(event.channel, event.data1)
```

#### 4. Add IR Support (if needed)

**File:** `src/midi_markdown/core/ir.py`

```python
# Only if this is a new event category
class EventType(str, Enum):
    # ... existing types ...
    YOUR_COMMAND = "yc"
```

#### 5. Add MIDI Codegen

**File:** `src/midi_markdown/codegen/midi_file.py`

```python
# In _event_to_midi() function
elif event.type == EventType.YOUR_COMMAND:
    return mido.Message(
        'your_midi_type',  # Mido message type
        channel=event.channel - 1,  # 0-indexed in Mido
        value=event.data1,
    )
```

#### 6. Write Tests

**File:** `tests/unit/test_midi_commands.py`

```python
class TestYourCommand:
    """Test your_command MIDI command."""

    @pytest.mark.unit
    def test_basic_parsing(self, parser):
        """Test basic your_command parsing."""
        mml = """
[00:00.000]
- yc 1.42
"""
        doc = parser.parse_string(mml)

        assert len(doc.events) == 1
        assert doc.events[0]["type"] == "yc"
        assert doc.events[0]["channel"] == 1
        assert doc.events[0]["data1"] == 42

    @pytest.mark.unit
    def test_with_variable(self, parser):
        """Test your_command with variable substitution."""
        mml = """
@define MY_VAL 99

[00:00.000]
- yc 1.${MY_VAL}
"""
        doc = parser.parse_string(mml)
        assert doc.events[0]["data1"] == 99

    @pytest.mark.unit
    def test_validation(self, parser):
        """Test your_command parameter validation."""
        mml = """
[00:00.000]
- yc 1.255
"""
        with pytest.raises(ValueError, match="out of range"):
            parser.parse_string(mml)

    @pytest.mark.integration
    def test_end_to_end(self, parser):
        """Test complete compilation pipeline."""
        from midi_markdown.core.compiler import compile_ast_to_ir

        mml = """
[00:00.000]
- yc 1.42
"""
        doc = parser.parse_string(mml)
        ir = compile_ast_to_ir(doc, ppq=480)

        assert len(ir.events) == 1
        assert ir.events[0].type == EventType.YOUR_COMMAND
```

#### 7. Run Tests

```bash
# Run your new tests
pytest tests/unit/test_midi_commands.py::TestYourCommand -v

# Run full test suite
just test

# Check coverage
just test-cov
```

#### 8. Update Documentation

**File:** `spec.md`

Add command to MIDI Command Coverage section:

```markdown
#### Your Command
\`\`\`markdown
- your_command <channel>.<value>
- yc <channel>.<value>     # Shorthand alias

# Examples
- yc 1.42                  # Your command on channel 1
\`\`\`
```

---

## Task 2: Adding a Device Library

**Use case:** Creating a device library for a new MIDI device (e.g., Strymon BigSky, Boss GT-1000)

### Prerequisites
- MIDI implementation chart for the device
- List of CC numbers and their functions
- Understanding of device's program change behavior

### Step-by-Step

#### 1. Research Device MIDI Implementation

**Gather this information:**
- MIDI channel(s) used
- Program change behavior (patches, banks, etc.)
- CC numbers and their functions
- SysEx messages (if any)
- Timing requirements (delays between messages)
- Firmware version compatibility

**Sources:**
- Manufacturer's MIDI implementation PDF
- Device manual appendix
- Community forums/documentation

#### 2. Create Device Library File

**File:** `devices/your_device.mmd`

```yaml
---
device: Your Device Name
manufacturer: Manufacturer Name
firmware_version: 1.0.0
version: 1.0.0
default_channel: 1
documentation: https://manufacturer.com/docs
---
```

#### 3. Add Important Notes

```markdown
/*
 * IMPORTANT NOTES:
 * 1. Preset loading requires 100ms delay between bank select and PC
 * 2. Scene switching has ~50ms latency on firmware 1.x
 * 3. Expression pedals use CC#4 and CC#11
 * 4. Tap tempo is CC#80 (value ignored, any value triggers tap)
 */
```

#### 4. Define Basic Aliases

**Pattern: Start with core functionality**

```markdown
# ============================================
# Preset Selection
# ============================================

@alias device_preset pc.{ch}.{preset:0-127} "Load preset (0-127)"
@alias device_preset_up cc.{ch}.71.127 "Next preset"
@alias device_preset_down cc.{ch}.71.0 "Previous preset"

# ============================================
# Parameter Control
# ============================================

@alias device_mix cc.{ch}.7.{value:0-127} "Wet/dry mix"
@alias device_decay cc.{ch}.92.{value:0-127} "Decay/feedback time"
@alias device_tone cc.{ch}.74.{value:0-127} "Tone/filter control"
```

#### 5. Define Multi-Command Macros

**Pattern: Common operation sequences**

```markdown
@alias device_load_with_bank {ch}.{bank}.{preset} "Load preset with bank select"
  - cc {ch}.0.{bank}        # Bank select MSB
  [+100ms]                  # Device requires delay!
  - pc {ch}.{preset}        # Program change
@end

@alias device_tap_tempo {ch} "Send tap tempo pulse"
  - cc {ch}.80.127
@end
```

#### 6. Add Parameter Enums (if applicable)

```markdown
@alias device_mode {ch}.{mode=normal:0,freeze:1,hold:2} "Set operating mode"
  - cc {ch}.68.{mode}
@end
```

#### 7. Write Device Library Tests

**File:** `tests/integration/test_device_libraries.py`

```python
class TestYourDeviceLibrary:
    """Test your_device.mmd device library."""

    @pytest.mark.integration
    def test_device_library_loads(self, parser):
        """Test device library can be imported."""
        mml = """
@import "devices/your_device.mmd"

[00:00.000]
- device_preset 1.42
"""
        doc = parser.parse_string(mml)
        assert len(doc.events) == 1

    @pytest.mark.integration
    def test_preset_load_macro(self, parser):
        """Test multi-command preset load macro."""
        mml = """
@import "devices/your_device.mmd"

[00:00.000]
- device_load_with_bank 1 2 10
"""
        doc = parser.parse_string(mml)

        # Should expand to 2 commands (bank select + PC)
        assert len(doc.events) == 2
        assert doc.events[0]["type"] == "cc"
        assert doc.events[1]["type"] == "pc"
```

#### 8. Create Example File

**File:** `examples/04_device_libraries/your_device_example.mmd`

```markdown
---
title: "Your Device Example"
---

@import "devices/your_device.mmd"

# Basic preset loading
[00:00.000]
- device_preset 1.0

# Using macro for bank selection
[00:05.000]
- device_load_with_bank 1 2 10

# Parameter automation
[00:10.000]
- device_mix 1.0

[00:15.000]
- device_mix 1.127
```

#### 9. Validate Device Library

```bash
# Validate device library syntax
just run validate devices/your_device.mmd

# Compile example
just compile examples/04_device_libraries/your_device_example.mmd output/your_device.mid

# Run device library tests
pytest tests/integration/test_device_libraries.py::TestYourDeviceLibrary -v
```

#### 10. Document in README

**File:** `devices/README.md`

Add entry to device library list:

```markdown
## Your Device Name

**File:** `your_device.mmd`
**Manufacturer:** Manufacturer Name
**Firmware:** 1.0.0+

### Key Features
- Preset loading with bank support
- Parameter control (mix, decay, tone)
- Tap tempo

### Usage
\`\`\`markdown
@import "devices/your_device.mmd"

[00:00.000]
- device_load_with_bank 1 2 10
\`\`\`

### Notes
- Requires 100ms delay between bank select and program change
- See MIDI implementation chart for CC mappings
```

---

## Task 3: Debugging Timing Issues

**Use case:** Events are happening at wrong times in generated MIDI file

### Diagnostic Commands

```bash
# Visual timeline view (Rich table)
just run inspect song.mmd

# Export to CSV for spreadsheet analysis
just run compile song.mmd --format csv -o events.csv
# Import into Excel/Google Sheets

# Export to JSON for programmatic analysis
just run compile song.mmd --format json > events.json
jq '.events[] | select(.type=="note_on")' events.json

# Verbose compilation (see timing calculations)
just run compile song.mmd -v
```

### Common Timing Bugs

#### Bug 1: Musical Time Off by One Bar/Beat

**Symptom:** Events are 1 bar or 1 beat early/late

**Cause:** Forgot to subtract 1 from bars/beats (they're 1-indexed)

**Check:** `src/midi_markdown/expansion/expander.py:_compute_absolute_time()`

```python
# WRONG:
absolute_ticks = bar * beats_per_bar * ticks_per_beat

# CORRECT:
absolute_ticks = (bar - 1) * beats_per_bar * ticks_per_beat
```

#### Bug 2: Relative Timing Not Accumulating

**Symptom:** All relative times computed from beginning, not previous event

**Cause:** `current_time` not updated after each event

**Check:** `src/midi_markdown/expansion/expander.py:process_ast()`

```python
# WRONG:
for event in events:
    time = compute_absolute_time(event.timing)
    # Missing: self.current_time = time

# CORRECT:
for event in events:
    time = compute_absolute_time(event.timing)
    self.current_time = time  # Update for next relative timing
```

#### Bug 3: Loops Starting at Wrong Time

**Symptom:** Loop starts at unexpected time

**Cause:** Misunderstanding `at [time]` clause semantics

**Check:** Loop timing is absolute by default:

```markdown
# This ignores previous timing context:
[00:10.000]
@loop 4 times at [00:05.000] every 1b  # Starts at 5 seconds, NOT 10!
  - note_on 10.C1 100 1b
@end

# Use relative timing to add to previous:
[00:10.000]
@loop 4 times at [+2s] every 1b  # Starts at 12 seconds (10 + 2)
  - note_on 10.C1 100 1b
@end
```

#### Bug 4: Time Signature Mismatch

**Symptom:** Musical timing wrong in non-4/4 time

**Cause:** Assumed 4/4 time signature

**Check:** Frontmatter has correct time signature:

```yaml
---
time_signature: 3/4  # NOT 4/4!
---
```

### Debugging Workflow

1. **Export to CSV** - See all event times in spreadsheet
2. **Check frontmatter** - Verify PPQ, tempo, time_signature
3. **Isolate problem** - Reduce to minimal failing example
4. **Add unit test** - Test specific timing scenario
5. **Fix and verify** - Run tests, re-export CSV

---

## Task 4: Performance Profiling

**Use case:** Compilation is slow for large files

### Setup

```bash
# Install profiling plugin
uv add pytest-profiling --dev
```

### Profile Specific Test

```bash
# Profile single test
uv run pytest --profile tests/integration/test_end_to_end.py::test_large_file

# Results saved to prof/ directory
ls prof/
# combined.prof
```

### Analyze Profile

```bash
# Install snakeviz for visual analysis
uv add snakeviz --dev

# Open visual profiler
uv run snakeviz prof/combined.prof

# Or use cProfile stats
uv run python -m pstats prof/combined.prof
```

### Common Bottlenecks

#### 1. Lark Grammar Parsing

**Symptom:** `lark.parse()` taking >50% of time

**Solutions:**
- Simplify grammar rules (fewer alternatives)
- Use `@lark.v_args(inline=True)` for simple rules
- Cache parser instance (don't recreate each time)

#### 2. Alias Resolution

**Symptom:** `resolve_alias_call()` slow in nested aliases

**Solutions:**
- Check max_depth setting (default: 10)
- Optimize cycle detection (use set instead of list)
- Cache alias lookups

#### 3. Timing Calculations in Loops

**Symptom:** `_compute_absolute_time()` called repeatedly

**Solutions:**
- Cache timing conversions within loop iterations
- Pre-compute loop boundaries
- Use lower PPQ resolution (480 instead of 960)

### Optimization Pattern

```python
# BEFORE (slow):
for i in range(1000):
    time = compute_absolute_time(timing)  # Re-computes each iteration
    emit_event(time, ...)

# AFTER (fast):
base_time = compute_absolute_time(timing)  # Compute once
for i in range(1000):
    time = base_time + (i * interval_ticks)  # Simple arithmetic
    emit_event(time, ...)
```

---

## Task 5: Adding a Test

**Use case:** Need to add test coverage for new feature or bug fix

### Choose Test Type

| Test Type | When to Use | Location | Marker |
|-----------|-------------|----------|--------|
| Unit | Single function/method | `tests/unit/` | `@pytest.mark.unit` |
| Integration | Multi-component | `tests/integration/` | `@pytest.mark.integration` |
| E2E | Full pipeline | `tests/integration/` | `@pytest.mark.e2e` |
| CLI | Command-line interface | `tests/integration/` | `@pytest.mark.cli` |

### Test Pattern

```python
class TestFeatureName:
    """Test feature description."""

    @pytest.mark.unit
    def test_basic_case(self, parser):
        """Test basic functionality."""
        mml = """
[00:00.000]
- pc 1.0
"""
        doc = parser.parse_string(mml)
        assert len(doc.events) == 1

    @pytest.mark.unit
    def test_edge_case(self, parser):
        """Test boundary condition."""
        # ... test implementation

    @pytest.mark.unit
    def test_error_handling(self, parser):
        """Test error is raised for invalid input."""
        mml = """
[00:00.000]
- invalid_command
"""
        with pytest.raises(ValueError, match="expected pattern"):
            parser.parse_string(mml)
```

### Run Tests

```bash
# Run specific test class
pytest tests/unit/test_feature.py::TestFeatureName -v

# Run with coverage
pytest tests/unit/test_feature.py --cov=src/midi_markdown --cov-report=html

# Run fast tests only
pytest -m unit
```

---

## Reference

**See also:**
- [parser-patterns.md](./parser-patterns.md) - Parser implementation details
- [timing-system.md](./timing-system.md) - Timing calculation deep-dive
- [anti-patterns.md](./anti-patterns.md) - Common mistakes to avoid
- [specification.md](../reference/specification.md) - Language specification
- [examples/](https://github.com/cjgdev/midi-markdown/tree/main/examples) - 51 working examples for all features
