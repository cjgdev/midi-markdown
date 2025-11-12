# Computed Values in Aliases

## Overview

Computed values allow you to perform calculations and transformations on alias parameters before they're used in MIDI commands. This powerful feature lets you create more intuitive aliases that hide complex MIDI details and let musicians think in natural units like BPM, percentages, decibels, or time values.

## Table of Contents

- [Basic Syntax](#basic-syntax)
- [Why Use Computed Values?](#why-use-computed-values)
- [Available Functions](#available-functions)
- [Real-World Examples](#real-world-examples)
- [Best Practices](#best-practices)
- [Security and Limitations](#security-and-limitations)
- [Troubleshooting](#troubleshooting)

---

## Basic Syntax

Computed values are defined using curly braces with an assignment expression:

```markdown
@alias alias_name {param1} {param2} "Description"
  {computed_var = expression}
  - command using {computed_var}
@end
```

### Simple Example

```markdown
@alias double_value {ch} {value:0-63} "Double a value"
  {doubled = ${value} * 2}
  - cc {ch}.7.{doubled}
@end

# Usage
- double_value 1 50  # Sends CC 1.7.100
```

### Key Points

1. **Variable Reference**: Use `${param}` to reference alias parameters in expressions
2. **Multiple Computed Values**: You can define multiple computed variables
3. **Order Matters**: Computed values are evaluated in the order they appear
4. **Dependency**: Later computed values can reference earlier ones

---

## Why Use Computed Values?

### 1. Hide MIDI Complexity

MIDI uses 0-127 values, but musicians think in different units:

```markdown
# Without computed values (confusing)
@alias set_tempo {ch} {midi_val:0-127} "Set tempo"
  - cc {ch}.14.{midi_val}
@end
- set_tempo 1 39  # What BPM is this?

# With computed values (intuitive)
@alias set_tempo {ch} {bpm:40-300} "Set tempo in BPM"
  {midi_val = int((${bpm} - 40) * 127 / 260)}
  - cc {ch}.14.{midi_val}
@end
- set_tempo 1 120  # Clear: 120 BPM
```

### 2. Automate Complex Calculations

```markdown
# 14-bit MIDI value splitting
@alias pitch_bend_14bit {ch} {value:0-16383} "High-res pitch"
  {msb_val = msb(${value})}
  {lsb_val = lsb(${value})}
  - cc {ch}.64.{msb_val}
  - cc {ch}.96.{lsb_val}
@end
```

### 3. Ensure Correctness

Computed values prevent manual calculation errors:

```markdown
# Complementary mix (A + B = 100%)
@alias mix_ab {ch} {a_percent:0-100} "A/B mix"
  {b_percent = 100 - ${a_percent}}
  {a_midi = int(${a_percent} * 127 / 100)}
  {b_midi = int(${b_percent} * 127 / 100)}
  - cc {ch}.84.{a_midi}
  - cc {ch}.85.{b_midi}
@end
```

### 4. Create Parameter Relationships

```markdown
# Linked cutoff and resonance
@alias filter_sweep {ch} {cutoff:0-127} "Filter with auto-resonance"
  {resonance = clamp(int(${cutoff} / 2), 0, 80)}
  - cc {ch}.74.{cutoff}      # Cutoff
  - cc {ch}.71.{resonance}   # Resonance (half of cutoff, max 80)
@end
```

---

## Available Functions

### Arithmetic Operators

- `+` - Addition
- `-` - Subtraction
- `*` - Multiplication
- `/` - Division (floating point)
- `//` - Integer division (floor division)
- `%` - Modulo (remainder)
- `**` - Exponentiation

### Built-in Functions

#### `int(value)`
Convert to integer (truncate decimals).

```markdown
{midi_val = int(${bpm} * 1.27)}  # 100 * 1.27 = 127
```

#### `float(value)`
Convert to floating point number.

```markdown
{normalized = float(${value}) / 127.0}
```

#### `round(value[, decimals])`
Round to nearest integer or specified decimal places.

```markdown
{rounded = round(${value} * 1.5)}      # Round to integer
{precise = round(${value} * 1.5, 2)}   # Round to 2 decimal places
```

#### `abs(value)`
Get absolute value (remove negative sign).

```markdown
{magnitude = abs(${offset} - 64)}
```

#### `min(a, b, ...)`
Return the smallest value.

```markdown
{lower = min(${val1}, ${val2}, 100)}
```

#### `max(a, b, ...)`
Return the largest value.

```markdown
{higher = max(${val1}, ${val2}, 20)}
```

### MIDI Helper Functions

#### `clamp(value, min, max)`
Constrain value to range [min, max].

```markdown
{safe_val = clamp(${raw_val}, 0, 127)}  # Ensure MIDI range
```

**Use Case**: Prevent values from exceeding MIDI limits after calculations.

#### `scale_range(value, from_min, from_max, to_min, to_max)`
Map value from one range to another (linear interpolation).

```markdown
# Map 0-100% to MIDI 0-127
{midi_val = int(scale_range(${percent}, 0, 100, 0, 127))}

# Map dB (-60 to +6) to MIDI (0-127)
{midi_val = int(scale_range(${db}, -60, 6, 0, 127))}
```

**Use Case**: Convert between different parameter scales.

#### `msb(value)`
Extract most significant byte (high 7 bits) from 14-bit value.

```markdown
{msb_val = msb(${full_value})}  # Get upper 7 bits
```

**Use Case**: Split 14-bit values for high-resolution MIDI control.

#### `lsb(value)`
Extract least significant byte (low 7 bits) from 14-bit value.

```markdown
{lsb_val = lsb(${full_value})}  # Get lower 7 bits
```

**Use Case**: Split 14-bit values for high-resolution MIDI control.

---

## Real-World Examples

### Example 1: BPM to MIDI Conversion

**Problem**: Device accepts tempo via MIDI CC, but musicians think in BPM.

**Solution**:
```markdown
@alias set_tempo {ch} {bpm:40-300} "Set tempo (40-300 BPM)"
  {midi_val = int((${bpm} - 40) * 127 / 260)}
  - cc {ch}.14.{midi_val}
@end

# Usage
- set_tempo 1 120  # 120 BPM → MIDI 39
- set_tempo 1 180  # 180 BPM → MIDI 68
```

**Math Explanation**:
- Range: 40-300 BPM → 260 BPM span
- MIDI: 0-127 → 127 value span
- Formula: `(BPM - 40) * 127 / 260`

### Example 2: Percentage to MIDI

**Problem**: Mixing percentages are more intuitive than 0-127 values.

**Solution**:
```markdown
@alias set_mix {ch} {percent:0-100} "Set mix level (0-100%)"
  {midi_val = int(${percent} * 127 / 100)}
  - cc {ch}.7.{midi_val}
@end

# Usage
- set_mix 1 75   # 75% → MIDI 95
- set_mix 1 50   # 50% → MIDI 63
```

### Example 3: Velocity Curve

**Problem**: Apply dynamic scaling to velocity for expression.

**Solution**:
```markdown
@alias vel_curve {ch} {note} {vel} {curve:50-150} "Velocity with curve"
  {scaled = int(${vel} * ${curve} / 100)}
  {safe_vel = clamp(${scaled}, 0, 127)}
  - note_on {ch}.{note}.{safe_vel} 1b
@end

# Usage
- vel_curve 1 60 90 150  # 90 * 150% = 135 → clamp to 127
- vel_curve 1 64 80 75   # 80 * 75% = 60
```

### Example 4: 14-bit MIDI Control

**Problem**: High-resolution parameter needs 14-bit precision.

**Solution**:
```markdown
@alias pitch_14bit {ch} {value:0-16383} "14-bit pitch control"
  {msb_val = msb(${value})}
  {lsb_val = lsb(${value})}
  - cc {ch}.64.{msb_val}  # Coarse
  - cc {ch}.96.{lsb_val}  # Fine
@end

# Usage
- pitch_14bit 1 8192   # Center: MSB=64, LSB=0
- pitch_14bit 1 12288  # 75% up: MSB=96, LSB=0
```

### Example 5: Multi-Step Computation

**Problem**: Create custom response curve for expression pedal.

**Solution**:
```markdown
@alias expr_curve {ch} {raw:0-127} "Logarithmic expression"
  {normalized = ${raw} / 127.0}
  {curved = ${normalized} * ${normalized}}  # Square
  {result = clamp(int(${curved} * 127), 0, 127)}
  - cc {ch}.11.{result}
@end

# Usage
- expr_curve 1 64   # 50% input → 25% output
- expr_curve 1 127  # 100% input → 100% output
```

---

## Best Practices

### 1. Use Descriptive Variable Names

```markdown
# Good
{bpm_midi = int((${bpm} - 40) * 127 / 260)}

# Bad
{x = int((${bpm} - 40) * 127 / 260)}
```

### 2. Always Clamp Calculated Values

MIDI values must be 0-127. Prevent overflow:

```markdown
{safe_value = clamp(${calculated}, 0, 127)}
```

### 3. Use `int()` for MIDI Values

MIDI doesn't support decimal values:

```markdown
{midi_val = int(${percent} * 1.27)}  # Good: integer
{midi_val = ${percent} * 1.27}       # Bad: might be decimal
```

### 4. Document Your Formulas

Add comments explaining complex calculations:

```markdown
@alias cortex_tempo {ch} {bpm:40-300} "Set tempo"
  # Quad Cortex maps BPM 40-300 to MIDI 0-127 linearly
  {midi_val = int((${bpm} - 40) * 127 / 260)}
  - cc {ch}.14.{midi_val}
@end
```

### 5. Order Dependencies Correctly

If one computed value depends on another, define it after:

```markdown
# Good
{step1 = ${value} * 2}
{step2 = ${step1} + 10}  # Uses step1

# Bad
{step2 = ${step1} + 10}  # Error: step1 not defined yet
{step1 = ${value} * 2}
```

### 6. Use Range Constraints on Parameters

```markdown
# Good: Range prevents invalid BPM
@alias set_tempo {ch} {bpm:40-300} "Set tempo"
  {midi_val = int((${bpm} - 40) * 127 / 260)}
  - cc {ch}.14.{midi_val}
@end

# Bad: User could pass 500 BPM
@alias set_tempo {ch} {bpm} "Set tempo"
  {midi_val = int((${bpm} - 40) * 127 / 260)}
  - cc {ch}.14.{midi_val}
@end
```

---

## Security and Limitations

### Security Features

Computed values are evaluated in a **sandboxed environment** with these safety features:

1. **Whitelisted Operations**: Only safe arithmetic operators and functions allowed
2. **Operation Limit**: Maximum 10,000 operations per expression
3. **Timeout**: 1-second execution limit (prevents infinite loops)
4. **No Imports**: Cannot import modules or access file system
5. **No Attributes**: Cannot access object attributes or methods
6. **Read-Only Parameters**: Input parameters cannot be modified

### Limitations

1. **No Loops**: Cannot use `for`, `while`, or recursion
2. **No Conditionals**: Cannot use `if/else` (use alias conditionals instead)
3. **No String Operations**: Only numeric calculations
4. **No Variable Assignment**: Cannot reassign computed values
5. **No Side Effects**: Cannot modify external state

### Performance

- **Fast**: Simple expressions evaluate in <1ms
- **Cached**: Computations are not cached between alias calls
- **Linear**: Performance scales linearly with expression complexity

---

## Troubleshooting

### Common Errors

#### Error: "Division by zero"

```markdown
# Bad
{result = ${value} / 0}

# Good
{result = ${value} / max(${divisor}, 1)}  # Prevent zero division
```

#### Error: "Undefined variable"

```markdown
# Bad
{result = ${typo_val} + 10}  # typo_val not defined

# Good
{result = ${value} + 10}
```

#### Error: "Exceeds operation limit"

```markdown
# Bad
{result = ${val} ** ${val} ** ${val}}  # Exponential explosion

# Good
{result = ${val} ** 3}  # Simple exponentiation
```

#### Error: "Invalid expression syntax"

```markdown
# Bad
{result = ${value} + }  # Missing operand

# Good
{result = ${value} + 10}
```

### Debugging Tips

1. **Test Incrementally**: Add computed values one at a time
2. **Use Simple Values**: Test with known inputs (e.g., 0, 64, 127)
3. **Check Math**: Verify calculations manually
4. **Add Clamp**: Use `clamp()` to catch out-of-range values
5. **Check Types**: Ensure `int()` conversion where needed

---

## Advanced Techniques

### Technique 1: Chained Transformations

```markdown
@alias complex_transform {ch} {raw:0-127} "Multi-step transform"
  {normalized = ${raw} / 127.0}
  {curved = ${normalized} ** 2}  # Square
  {scaled = ${curved} * 100}
  {result = clamp(int(${scaled}), 0, 127)}
  - cc {ch}.7.{result}
@end
```

### Technique 2: Parameter Validation

```markdown
@alias safe_cc {ch} {cc_num:0-127} {value} "CC with clamping"
  {safe_val = clamp(int(${value}), 0, 127)}
  - cc {ch}.{cc_num}.{safe_val}
@end
```

### Technique 3: Unit Conversion

```markdown
# Decibels to MIDI gain
@alias gain_db {ch} {db:-60-6} "Set gain in dB"
  {midi_val = int(scale_range(${db}, -60, 6, 0, 127))}
  - cc {ch}.7.{midi_val}
@end
```

### Technique 4: Custom Curves

```markdown
# Exponential curve (for faders)
@alias exp_fader {ch} {position:0-127} "Exponential fader"
  {norm = ${position} / 127.0}
  {exp_val = (${norm} ** 3) * 127}  # Cubic curve
  {result = clamp(int(${exp_val}), 0, 127)}
  - cc {ch}.7.{result}
@end
```

---

## See Also

- [Alias System Guide](alias-system.md)
- [Expression Syntax Reference](../reference/expressions.md)
- [Device Library Creation](device-libraries.md)
- [Examples: computed_values.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/03_advanced/04_computed_values.mmd)

---

**Last Updated**: November 2025
**Version**: 1.0
**Status**: Complete - Feature fully implemented and tested
