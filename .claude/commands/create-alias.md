---
description: Interactive guide for creating device library aliases
---

Guide the user through creating a properly formatted device library alias.

Ask the user:

1. **Alias name** (e.g., "cortex_preset", "h90_mix")
2. **What MIDI commands** it should send (e.g., "cc 1.7.value", "pc 1.preset")
3. **Parameters needed** (e.g., channel, preset, value)
4. **Parameter constraints** (ranges, defaults, enums)
5. **Description** of what the alias does

Then create a properly formatted @alias definition:

## Simple Alias (Single Command)

For simple one-line aliases:

```mml
@alias {device}_{function} {params} "Description"
```

**Example:**
```mml
@alias cortex_preset pc.{ch}.{preset:0-127} "Load preset (0-127)"
```

## Parameter Types Guide:

### Basic Parameters
```mml
{name}              # Any value (0-127 default)
{name:0-127}        # Explicit range
{name:40-300}       # Custom range (e.g., BPM)
```

### Default Values
```mml
{name=default}      # Optional with default
{channel=1}         # Defaults to channel 1
{velocity=100}      # Defaults to velocity 100
```

### Special Types
```mml
{note}              # Note name or number
{channel:1-16}      # MIDI channel
{percent:0-100}     # Percentage (auto-scaled to 0-127)
{velocity:0-127}    # Note velocity
{bool:0-1}          # Boolean as 0/1
```

### Enum Parameters
```mml
{param=opt1:val1,opt2:val2,opt3:val3}
```

**Example:**
```mml
@alias h90_routing cc.{ch}.85.{mode=series:0,parallel:1,a_only:2,b_only:3}
```

## Multi-Command Alias (Macro)

For sequences of commands:

```mml
@alias {name} {params} "Description"
  - command1 {param1}
  - command2 {param2}
  - command3 {param3}
@end
```

**Example:**
```mml
@alias cortex_load {ch}.{setlist}.{group}.{preset} "Load complete preset"
  - cc {ch}.32.{setlist}
  - cc {ch}.0.{group}
  - pc {ch}.{preset}
@end
```

## Computed Values

For value transformations:

```mml
@alias {name} {params} "Description"
  {computed_var = expression}
  - command {ch}.{value}.{computed_var}
@end
```

**Example:**
```mml
@alias cortex_tempo {ch} {bpm:40-300} "Set tempo"
  {midi_val = int((${bpm} - 40) * 127 / 260)}
  - cc {ch}.14.{midi_val}
@end
```

## Best Practices:

✅ **Use device prefix** - `cortex_preset` not just `preset`
✅ **Include descriptions** - Required for documentation
✅ **Document ranges** - Show min/max values in description
✅ **Use meaningful names** - `mix_ab` not `m1`
✅ **Group by category** - Organize aliases logically
✅ **No absolute timing** - Let caller control when it executes

❌ **Don't hardcode channels** - Use parameter instead
❌ **Don't use absolute timing** - Use relative timing or none
❌ **Don't create redundant aliases** - Keep it simple

## Testing the Alias

After creating the alias:

1. **Add to device library file** (devices/{device}.mmd)
2. **Validate the file**: `mmdc validate devices/{device}.mmd`
3. **Create test example**:
```mml
@import "devices/{device}.mmd"

[00:00.000]
- {your_alias_name} {params}
```
4. **Compile the example**: `mmdc compile test.mmd -o test.mid`
5. **Verify MIDI output** matches expectations

## Reference Examples:

See these device libraries for patterns:
- `devices/quad_cortex.mmd` - Comprehensive example
- `devices/eventide_h90.mmd` - Enum parameters
- `devices/helix.mmd` - Multi-command macros

For detailed alias documentation, see:
- `docs/user-guide/alias-system.md` - Complete alias guide
- `spec.md` - Alias syntax specification
