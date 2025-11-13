# Alias System API Reference

## Table of Contents

1. [Syntax Overview](#syntax-overview)
2. [Alias Definition](#alias-definition)
3. [Parameter Specification](#parameter-specification)
4. [Parameter Types](#parameter-types)
5. [Computed Values](#computed-values)
6. [Conditional Logic](#conditional-logic)
7. [Alias Invocation](#alias-invocation)
8. [Import System](#import-system)
9. [Error Handling](#error-handling)
10. [Grammar Reference](#grammar-reference)

## Syntax Overview

The alias system uses a declarative syntax inspired by Markdown and YAML:

```markdown
@alias name {param1} {param2} "Description"
  {computed_var = expression}
  @if {param} == value
    - command template
  @end
@end
```

### Keywords

- `@alias` - Begin alias definition
- `@end` - End alias definition or conditional block
- `@if` - Begin conditional branch
- `@elif` - Else-if branch
- `@else` - Else branch
- `@import` - Import device library (Stage 8)

## Alias Definition

### Basic Syntax

```markdown
@alias alias_name parameters "description"
  command_templates
@end
```

### Components

**`alias_name`** (required)
- Type: Identifier
- Pattern: `[a-zA-Z_][a-zA-Z0-9_]*`
- Convention: `device_function` (lowercase with underscores)
- Example: `cortex_scene`, `helix_snapshot`

**`parameters`** (optional)
- Zero or more parameter specifications
- Format: `{param_name}` or `{param_name:type}` or `{param_name=default}`
- Must be unique within alias
- Order matters for invocation

**`description`** (required)
- Type: String (single or double quotes)
- Purpose: Human-readable description
- Displayed in help/documentation
- Should explain what (not how)

**`command_templates`** (required)
- One or more command lines starting with `-`
- Can reference parameters: `{param_name}`
- Can reference computed values: `{var_name}`
- Can invoke other aliases
- Can include conditional blocks

### Examples

```markdown
# Simple alias
@alias preset_change {ch} {preset} "Change preset"
  - pc {ch}.{preset}
@end

# Multi-command alias
@alias scene_with_fx {ch} {scene} {fx_level} "Scene with effects"
  - cc {ch}.34.{scene}
  - cc {ch}.91.{fx_level}
@end

# Alias calling another alias
@alias quick_scene_a {ch} "Quick scene A"
  - cortex_scene {ch} 0
@end
```

## Parameter Specification

### Parameter Syntax

Parameters are enclosed in braces: `{parameter_spec}`

```
{name}                    # Generic parameter
{name:type}              # Typed parameter
{name:min-max}          # Range parameter
{name=default}          # Default value
{name:type=default}     # Type + default
{name=opt1:val1,opt2:val2}  # Enum parameter
```

### Parameter Components

**Name**
- Required
- Must be valid identifier: `[a-zA-Z_][a-zA-Z0-9_]*`
- Case-sensitive
- Should be descriptive: `preset`, `scene`, `velocity`

**Type** (optional)
- Specifies parameter type and validation
- See [Parameter Types](#parameter-types) for full list
- Format: `:type` or `:min-max`

**Default Value** (optional)
- Provides default if argument omitted
- Format: `=value`
- Must be valid for parameter type
- Allows optional parameters

**Enum Values** (optional)
- Named options mapping to numbers
- Format: `=name1:value1,name2:value2,...`
- Names must be identifiers
- Values must be integers

### Parameter Examples

```markdown
# Generic (0-127)
{channel}
{value}

# Range constrained
{scene:0-7}
{bpm:40-300}
{velocity:1-127}

# Typed
{note:note}          # Note name or number
{level:percent}      # 0-100 → 0-127
{enabled:bool}       # true/false, on/off, etc.
{channel:channel}    # 1-16

# Default values
{channel=1}          # Channel defaults to 1
{velocity=100}       # Velocity defaults to 100

# Enum
{mode=clean:0,crunch:1,lead:2}
{device=cortex:0,helix:1,kemper:2}

# Combined
{bpm:40-300=120}     # Range with default
{level:percent=50}   # Type with default
```

## Parameter Types

### Generic (default)

**Type**: `generic` (implicit)
**Range**: 0-127
**Input**: Integer
**Output**: Integer (0-127)

```markdown
{value}              # Any MIDI value
{cc_num}            # CC number
```

### Range

**Type**: `:min-max`
**Range**: Custom (specified)
**Input**: Integer in range
**Output**: Integer (validated)

```markdown
{scene:0-7}         # 0-7 only
{bpm:40-300}        # 40-300 only
{channel:1-16}      # MIDI channels
```

### Note

**Type**: `:note`
**Range**: 0-127 (MIDI note numbers)
**Input**: Note name (C4, D#5, Bb3) or MIDI number
**Output**: MIDI note number (0-127)

```markdown
{note:note}         # Accepts C4 or 60
```

**Note Name Format**:
- Base note: A-G
- Accidental: `#` (sharp) or `b` (flat)
- Octave: 0-9 (MIDI octaves, C4 = middle C = 60)

**Examples**:
- `C4` → 60
- `C#4` → 61
- `Db4` → 61
- `A0` → 21
- `G9` → 127

### Percent

**Type**: `:percent`
**Range**: 0-100
**Input**: Percentage (0-100)
**Output**: MIDI value (0-127)

```markdown
{level:percent}     # 0-100% → 0-127
```

**Conversion**: `midi_value = round(percent * 127 / 100)`

**Examples**:
- `0%` → 0
- `50%` → 64
- `100%` → 127

### Bool

**Type**: `:bool`
**Range**: 0 or 127
**Input**: Boolean value
**Output**: 0 (false) or 127 (true)

```markdown
{enabled:bool}      # true/false → 0/127
```

**Accepted Values**:
- **True**: `true`, `on`, `yes`, `1`, `127`
- **False**: `false`, `off`, `no`, `0`

**Output**:
- True → 127
- False → 0

### Channel

**Type**: `:channel`
**Range**: 1-16
**Input**: MIDI channel (1-16)
**Output**: Channel number (1-16)

```markdown
{ch:channel}        # MIDI channels 1-16
```

### Velocity

**Type**: `:velocity`
**Range**: 1-127 (0 reserved for note-off)
**Input**: Velocity (1-127)
**Output**: Velocity (1-127)

```markdown
{vel:velocity}      # Note velocity 1-127
```

### Enum

**Type**: Implicit (defined by options)
**Range**: Defined by enum values
**Input**: Name or value
**Output**: Corresponding integer value

```markdown
{mode=clean:0,crunch:1,lead:2}
```

**Invocation**:
- By name: `device_mode 1 clean` → 0
- By value: `device_mode 1 0` → 0

## Computed Values

**Status**: ✅ Complete (Phase 6)

Computed values allow defining variables with calculated values based on parameters.

### Syntax

```markdown
@alias name {params} "description"
  {var_name = expression}
  - command using {var_name}
@end
```

### Expressions

**Variables**: Reference parameters with `${param_name}`

**Operators**:
- Arithmetic: `+`, `-`, `*`, `/`, `%`, `**` (power)
- Parentheses: `(`, `)`

**Functions**:
- `int(x)` - Convert to integer
- `round(x)` - Round to nearest integer
- `floor(x)` - Round down
- `ceil(x)` - Round up
- `abs(x)` - Absolute value
- `min(a, b)` - Minimum
- `max(a, b)` - Maximum
- `clamp(x, min, max)` - Constrain value

### Example

```markdown
@alias bpm_to_midi {ch} {bpm:40-300} "Convert BPM to MIDI"
  {midi_val = int((${bpm} - 40) * 127 / 260)}
  - cc {ch}.81.{midi_val}
@end
```

### Evaluation Order

1. Parameter binding
2. Computed value evaluation (in definition order)
3. Conditional branch selection
4. Command expansion

## Conditional Logic

**Status**: Stage 7 (Complete)

Conditionals allow different command sequences based on parameter values.

### Syntax

```markdown
@alias name {params} "description"
  @if condition
    - commands
  @elif condition
    - commands
  @else
    - commands
  @end
@end
```

### Condition Syntax

```
{param} operator value
```

**Operators**:
- `==` - Equal
- `!=` - Not equal
- `<` - Less than
- `>` - Greater than
- `<=` - Less than or equal
- `>=` - Greater than or equal

**Values**:
- Numbers: `0`, `127`, `42`
- Strings: `"text"` (for future string params)
- Parameter references: `{other_param}`

### Rules

1. At least one `@if` branch required
2. Zero or more `@elif` branches
3. Zero or one `@else` branch
4. Conditions evaluated in order (first match wins)
5. `@else` matches if no other branch matches
6. Conditional block closed with `@end` before alias `@end`

### Examples

```markdown
# Simple conditional
@alias device_load {ch} {preset} {device=cortex:0,helix:1} "Device-aware load"
  @if {device} == 0
    - pc {ch}.{preset}
  @elif {device} == 1
    - cc {ch}.69.{preset}
  @end
@end

# With else
@alias smart_velocity {ch} {note:note} {level:0-2} "Dynamic velocity"
  @if {level} == 0
    - note {ch}.{note}.50 500ms
  @elif {level} == 1
    - note {ch}.{note}.80 500ms
  @else
    - note {ch}.{note}.127 500ms
  @end
@end

# Multiple conditions
@alias scene_selector {ch} {scene} {mode} "Scene with mode check"
  @if {mode} == 0
    - cc {ch}.34.{scene}
  @elif {mode} == 1
    - cc {ch}.69.{scene}
  @else
    - pc {ch}.{scene}
  @end
@end
```

## Alias Invocation

### Syntax

```markdown
[timing]
- alias_name arg1 arg2 arg3
```

### Argument Passing

**Positional Arguments**:
- Arguments matched to parameters by position
- Must provide arguments for all required parameters
- Optional parameters (with defaults) can be omitted
- Excess arguments cause error

**Examples**:

```markdown
@alias test {a} {b=10} {c=20} "Test defaults"
  - cc {a}.{b}.{c}
@end

# Valid invocations:
- test 1              # a=1, b=10, c=20
- test 1 5            # a=1, b=5, c=20
- test 1 5 15         # a=1, b=5, c=15

# Invalid:
- test                # Error: missing required 'a'
- test 1 2 3 4        # Error: too many arguments
```

### Expansion Process

1. **Parse**: Parse alias call and arguments
2. **Resolve**: Look up alias definition
3. **Bind**: Match arguments to parameters
4. **Validate**: Check types and ranges
5. **Compute**: Evaluate computed values (if any)
6. **Select**: Choose conditional branch (if any)
7. **Expand**: Replace parameter placeholders
8. **Recurse**: Expand nested alias calls
9. **Generate**: Create MIDI events

### Timing

Alias invocations use the same timing as MIDI commands:

```markdown
[00:00.000]           # Absolute time
- alias_name args

[1.1.0]              # Musical time
- alias_name args

[+500ms]             # Relative time
- alias_name args

[@]                  # Simultaneous
- alias_name args
```

All commands expanded from an alias inherit the timing of the alias call.

## Import System

**Status**: ✅ Complete

The import system allows loading aliases from external files.

### Syntax

```markdown
@import "path/to/library.mmd"
```

### Path Resolution

- Relative to current file
- Searched in `devices/` directory
- `.mmd` extension optional

### Examples

```markdown
@import "devices/quad_cortex.mmd"
@import "quad_cortex"                # .mmd assumed
@import "../shared/common_aliases.mmd"
```

### Import Behavior

- Aliases merged into current namespace
- Name conflicts cause error
- Circular imports detected and prevented
- Imports processed before alias definitions

## Error Handling

### Compile-Time Errors

**Undefined Alias**:
```
Error: Undefined alias 'cortex_scne' at line 10
Did you mean 'cortex_scene'?
```

**Wrong Argument Count**:
```
Error: Alias 'cortex_load' expects 4 arguments, got 3 at line 15
Usage: cortex_load {ch} {setlist} {group} {preset}
```

**Parameter Out of Range**:
```
Error: Parameter 'scene' value 9 out of range [0-7] in alias 'cortex_scene' at line 20
```

**Invalid Parameter Type**:
```
Error: Invalid note name 'H4' for parameter 'note' in alias 'play_note' at line 25
Valid note names: A-G with optional # or b, plus octave 0-9
```

**Invalid Enum Value**:
```
Error: Invalid value 'lead' for enum parameter 'mode' in alias 'amp_channel'
Valid options: clean, crunch, rhythm
```

**Circular Dependency**:
```
Error: Circular alias dependency detected: alias_a → alias_b → alias_a
```

**Max Depth Exceeded**:
```
Error: Alias expansion max depth (10) exceeded in 'recursive_alias'
Call chain: recursive_alias → recursive_alias → ...
```

### Runtime Errors

**Computation Error**:
```
Error: Computation error in alias 'bpm_to_midi': Division by zero
```

**No Conditional Match**:
```
Error: No conditional branch matched in alias 'device_load' at line 30
Parameter values: {device: 5}
```

## Grammar Reference

### Complete Alias Grammar (Lark)

```lark
// Alias definition
macro_alias: "@alias" IDENTIFIER alias_params STRING _NL*
             (computed_value _NL*)*
             alias_body
             "@end"

// Parameters
alias_params: param_ref*

param_ref: "{" param_spec "}"

param_spec: IDENTIFIER                    // Simple
          | IDENTIFIER param_type         // Typed
          | IDENTIFIER param_default      // Default
          | IDENTIFIER param_enum         // Enum
          | IDENTIFIER param_type param_default  // Type + default

param_type: ":" INT "-" INT              // Range
          | ":" PARAM_TYPE_NAME          // Named type

param_default: "=" (INT | IDENTIFIER)

param_enum: "=" enum_option ("," enum_option)*

enum_option: IDENTIFIER ":" INT

PARAM_TYPE_NAME: "note" | "channel" | "bool" | "percent" | "velocity"

// Computed values (Stage 6)
computed_value: "{" IDENTIFIER "=" expression "}"

// Alias body - commands or conditionals
alias_body: (command_template _NL*)+              // Non-conditional
          | alias_conditional_stmt                // Conditional

// Conditionals (Stage 7)
alias_conditional_stmt: alias_if_clause
                       alias_elif_clause*
                       alias_else_clause?
                       "@end" _NL*

alias_if_clause: "@if" alias_condition _NL*
                (command_template _NL*)+

alias_elif_clause: "@elif" alias_condition _NL*
                  (command_template _NL*)+

alias_else_clause: "@else" _NL*
                  (command_template _NL*)+

alias_condition: param_ref COMPARE_OP alias_cond_value
               | IDENTIFIER COMPARE_OP alias_cond_value

alias_cond_value: STRING | NUMBER | param_ref | IDENTIFIER

COMPARE_OP: "==" | "!=" | "<=" | ">=" | "<" | ">"

// Command template
command_template: "-" /[^\n]+/

// Alias invocation
alias_call: IDENTIFIER (INT | FLOAT | STRING | IDENTIFIER)*
```

### Type Hierarchy

```
Parameter Types:
├── generic (0-127)
├── range (min-max)
├── note (note names or 0-127)
├── percent (0-100 → 0-127)
├── bool (true/false → 0/127)
├── channel (1-16)
├── velocity (1-127)
└── enum (named → integer)

Expression Types:
├── number (int or float)
├── variable (parameter reference)
├── binary_op (arithmetic)
├── unary_op (negation)
├── function_call
└── parenthesized
```

## Versioning

The alias system follows semantic versioning:

**Current**: v1.0.0 (Stage 7 complete)

**Version History**:
- v0.1.0: Basic aliases (Stage 1)
- v0.2.0: Enhanced parameters (Stage 2)
- v0.3.0: Nested aliases (Stage 5)
- v0.6.0: Computed values (Stage 6, in progress)
- v0.7.0: Conditional logic (Stage 7, complete)
- v0.9.0: Integration (Stage 9, complete)
- v1.0.0: Full release

## See Also

- [Alias System User Guide](alias-system.md) - Tutorials and examples
- [Device Library Creation Guide](device-libraries.md) - Library authoring
- [MML Specification](../reference/specification.md) - Complete language spec
- [Examples](https://github.com/cjgdev/midi-markdown/tree/main/examples) - Working code samples
