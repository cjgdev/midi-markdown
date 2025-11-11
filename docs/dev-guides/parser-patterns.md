# Parser/Transformer Patterns

This guide documents the established patterns for extending the MIDI Markdown parser and transformer.

## Overview

The parser follows a three-stage pipeline:
1. **Lark Grammar** → Defines syntax rules
2. **AST Nodes** → Python dataclasses representing parsed structure
3. **Transformer** → Converts Lark tree to AST nodes

## Adding a New MIDI Command

Follow this exact sequence when adding new MIDI command types:

### Step 1: Add Grammar Rule

**File:** `src/midi_markdown/parser/mmd.lark`

```lark
your_command: "-" ("your_command" | "yc") param "." param
```

**Pattern Rules:**
- Start with `-` (bullet point)
- Provide full name AND abbreviated form (`"your_command" | "yc"`)
- Use `param` for parameters (handles variables/literals)
- Separate parameters with `.` for MIDI channel/value syntax

### Step 2: Add AST Node (if needed)

**File:** `src/midi_markdown/parser/ast_nodes.py`

Most MIDI commands use the existing `MIDICommand` dataclass:

```python
@dataclass
class MIDICommand:
    type: str  # CRITICAL: Use abbreviated form ("pc", "cc", "yc")
    channel: int | None = None
    data1: int | None = None
    data2: int | None = None
    timing: TimingMarker | None = None
    source_line: int | None = None
```

**Only create new AST node if:**
- Command requires unique fields not in `MIDICommand`
- Command is a meta-construct (like `@loop`, `@alias`)

### Step 3: Add Transformer Method

**File:** `src/midi_markdown/parser/transformer.py`

```python
def your_command(self, param1, param2):
    """Transform your command to AST node.

    Args:
        param1: First parameter (from grammar rule)
        param2: Second parameter (from grammar rule)

    Returns:
        MIDICommand with type="yc" (abbreviated!)
    """
    # CRITICAL: Always resolve parameters first
    param1_val = self._resolve_param(param1)
    param2_val = self._resolve_param(param2)

    # CRITICAL: Check isinstance before int() conversion
    # Tuples indicate forward references (unresolved variables)
    param1_int = int(param1_val) if not isinstance(param1_val, tuple) else param1_val
    param2_int = int(param2_val) if not isinstance(param2_val, tuple) else param2_val

    # CRITICAL: Use abbreviated type ("yc", NOT "your_command")
    return MIDICommand(
        type="yc",  # Abbreviated form!
        channel=param1_int,
        data1=param2_int,
    )
```

**Required Pattern Checks:**

1. ✅ **Resolve parameters**: `self._resolve_param()` handles variables
2. ✅ **Check tuple type**: Forward references are tuples, not ints
3. ✅ **Use abbreviated type**: "pc" not "program_change"
4. ✅ **Add docstring**: Explain what the command does

### Step 4: Add Validation

**File:** `src/midi_markdown/utils/validation/value_validator.py`

```python
def validate_your_command(channel: int, value: int) -> None:
    """Validate your command parameters.

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

### Step 5: Add IR Support (if needed)

**File:** `src/midi_markdown/core/ir.py`

If this is a new event category (not just another CC/PC variant):

```python
class EventType(str, Enum):
    NOTE_ON = "note_on"
    NOTE_OFF = "note_off"
    CC = "cc"
    PC = "pc"
    YOUR_TYPE = "your_command"  # Add new enum value
```

### Step 6: Add MIDI Codegen

**File:** `src/midi_markdown/codegen/midi_file.py`

In the `_event_to_midi()` function:

```python
def _event_to_midi(self, event: MIDIEvent) -> mido.Message:
    """Convert IR event to Mido MIDI message."""

    # ... existing cases ...

    elif event.type == EventType.YOUR_TYPE:
        return mido.Message(
            'your_midi_type',
            channel=event.channel - 1,  # MIDI channels are 0-indexed in Mido
            value=event.data1,
        )
```

### Step 7: Write Tests

**File:** `tests/unit/test_midi_commands.py`

```python
class TestYourCommand:
    """Test your_command MIDI command."""

    @pytest.mark.unit
    def test_basic_your_command(self, parser):
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
    def test_your_command_with_variable(self, parser):
        """Test your_command with variable substitution."""
        mml = """
@define MY_VAL 99

[00:00.000]
- yc 1.${MY_VAL}
"""
        doc = parser.parse_string(mml)

        assert doc.events[0]["data1"] == 99

    @pytest.mark.unit
    def test_your_command_validation(self, parser):
        """Test your_command parameter validation."""
        mml = """
[00:00.000]
- yc 1.255
"""
        with pytest.raises(ValueError, match="out of range"):
            parser.parse_string(mml)
```

## Critical Patterns

### Always Resolve Parameters

```python
# ❌ WRONG - doesn't handle variables
def program_change(self, channel, program):
    return MIDICommand(type="pc", channel=int(channel), data1=int(program))

# ✅ CORRECT - resolves variables first
def program_change(self, channel, program):
    channel_val = self._resolve_param(channel)
    program_val = self._resolve_param(program)

    channel_int = int(channel_val) if not isinstance(channel_val, tuple) else channel_val
    program_int = int(program_val) if not isinstance(program_val, tuple) else program_int

    return MIDICommand(type="pc", channel=channel_int, data1=program_int)
```

### Check isinstance Before int()

```python
# ❌ WRONG - crashes on forward references
channel = int(channel_param)  # TypeError if channel_param is ('var', 'MY_CHANNEL')

# ✅ CORRECT - preserves forward references
channel = int(channel_param) if not isinstance(channel_param, tuple) else channel_param
```

### Use Abbreviated Command Types

```python
# ❌ WRONG - validation won't match
MIDICommand(type="program_change", ...)

# ✅ CORRECT - matches validation logic
MIDICommand(type="pc", ...)
```

## Example: Program Change Command

**Complete implementation from actual codebase:**

```python
# Grammar (mml.lark:97)
program_change: "-" ("program_change" | "pc") param "." param

# AST Node (ast_nodes.py:32-48)
@dataclass
class MIDICommand:
    type: str  # "pc" for program change
    channel: int | None = None
    data1: int | None = None  # Program number
    # ... other fields

# Transformer (transformer.py:295-313)
def program_change(self, channel, program):
    """Transform program change (PC) MIDI command.

    Syntax: - pc 1.42  (load program 42 on channel 1)

    Args:
        channel: MIDI channel (1-16)
        program: Program number (0-127)

    Returns:
        MIDICommand with type="pc"
    """
    channel_val = self._resolve_param(channel)
    program_val = self._resolve_param(program)

    channel_int = int(channel_val) if not isinstance(channel_val, tuple) else channel_val
    program_int = int(program_val) if not isinstance(program_val, tuple) else program_val

    return MIDICommand(type="pc", channel=channel_int, data1=program_int)

# Validation (value_validator.py)
def validate_program_change(channel: int, program: int) -> None:
    """Validate program change parameters."""
    if not (1 <= channel <= 16):
        raise ValueError(f"Channel {channel} out of range (1-16)")
    if not (0 <= program <= 127):
        raise ValueError(f"Program {program} out of range (0-127)")

# Codegen (midi_file.py)
elif event.type == EventType.PC:
    return mido.Message(
        'program_change',
        channel=event.channel - 1,  # 0-indexed
        program=event.data1,
    )
```

## Testing Patterns

### Test Matrix

Every new command should have these tests:

1. **Basic parsing** - Command with literal values
2. **Variable substitution** - Command with `${VAR}`
3. **Validation** - Out-of-range values
4. **Edge cases** - Min/max values, channel boundaries
5. **Integration** - Command in loops/aliases

### Minimal Test Example

```python
@pytest.mark.unit
def test_your_command(self, parser):
    mml = "[00:00.000]\n- yc 1.42"
    doc = parser.parse_string(mml)

    assert len(doc.events) == 1
    assert doc.events[0]["type"] == "yc"
    assert doc.events[0]["channel"] == 1
    assert doc.events[0]["data1"] == 42
```

## Reference

**See also:**
- [specification.md](../reference/specification.md) - Full MIDI command reference
- [anti-patterns.md](./anti-patterns.md) - Common mistakes to avoid
- [timing-system.md](./timing-system.md) - Timing calculation patterns
