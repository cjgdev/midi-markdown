# Expression Syntax Reference

**Version**: 1.0
**Last Updated**: November 2025
**Status**: Production

## Overview

This document provides a complete reference for expression syntax used in MIDI Markdown computed values. Expressions enable mathematical calculations, unit conversions, and parameter transformations within alias definitions.

## Table of Contents

- [Basic Syntax](#basic-syntax)
- [Arithmetic Operators](#arithmetic-operators)
- [Built-in Functions](#built-in-functions)
- [MIDI Helper Functions](#midi-helper-functions)
- [Variable Substitution](#variable-substitution)
- [Expression Examples](#expression-examples)
- [Operator Precedence](#operator-precedence)
- [Security and Limitations](#security-and-limitations)

---

## Basic Syntax

Expressions are used within computed value definitions in alias blocks:

```markdown
@alias alias_name {param1} {param2} "Description"
  {computed_var = expression}
  - command using {computed_var}
@end
```

**Key Rules**:
- Expressions must be valid Python numeric expressions
- Only whitelisted operators and functions are allowed
- Results are evaluated at alias expansion time
- Expressions can reference alias parameters and previously computed values

---

## Arithmetic Operators

### Addition (`+`)

**Syntax**: `a + b`

**Description**: Add two values.

**Example**:
```markdown
{result = ${value} + 10}
{sum = ${a} + ${b} + ${c}}
```

### Subtraction (`-`)

**Syntax**: `a - b`

**Description**: Subtract b from a.

**Example**:
```markdown
{offset = ${value} - 64}
{range = ${max} - ${min}}
```

### Multiplication (`*`)

**Syntax**: `a * b`

**Description**: Multiply two values.

**Example**:
```markdown
{doubled = ${value} * 2}
{scaled = ${input} * 1.27}
```

### Division (`/`)

**Syntax**: `a / b`

**Description**: Divide a by b (floating point).

**Example**:
```markdown
{half = ${value} / 2}
{normalized = ${value} / 127.0}
```

**Note**: Returns float. Use `int()` for integer results.

### Integer Division (`//`)

**Syntax**: `a // b`

**Description**: Divide a by b, rounding down to nearest integer (floor division).

**Example**:
```markdown
{whole = ${value} // 2}      # 127 // 2 = 63
{quotient = ${total} // ${count}}
```

### Modulo (`%`)

**Syntax**: `a % b`

**Description**: Remainder after division.

**Example**:
```markdown
{remainder = ${value} % 10}   # Last digit
{is_even = ${value} % 2}      # 0 if even, 1 if odd
```

### Exponentiation (`**`)

**Syntax**: `a ** b`

**Description**: Raise a to the power of b.

**Example**:
```markdown
{squared = ${value} ** 2}
{cubed = ${input} ** 3}
```

**Warning**: Can cause exponential growth. Use with caution.

### Parentheses (`()`)

**Syntax**: `(expression)`

**Description**: Group expressions to control evaluation order.

**Example**:
```markdown
{result = (${a} + ${b}) * ${c}}
{complex = ((${x} - 40) * 127) / 260}
```

---

## Built-in Functions

### `int(value)`

**Signature**: `int(value) → integer`

**Description**: Convert value to integer, truncating decimal places.

**Examples**:
```markdown
{midi_val = int(${percent} * 1.27)}     # 100 * 1.27 = 127
{whole = int(${decimal})}                # 64.7 → 64
{computed = int((${bpm} - 40) * 127 / 260)}
```

**Use Cases**:
- Convert calculated floats to MIDI integers
- Truncate decimal results

### `float(value)`

**Signature**: `float(value) → float`

**Description**: Convert value to floating point number.

**Examples**:
```markdown
{normalized = float(${value}) / 127.0}
{precise = float(${int_val})}
```

**Use Cases**:
- Ensure floating point division
- Normalize values (0.0-1.0)

### `round(value[, decimals])`

**Signature**: `round(value, decimals=0) → number`

**Description**: Round to nearest integer or specified decimal places.

**Examples**:
```markdown
{rounded = round(${value} * 1.5)}        # Round to integer
{precise = round(${value} * 1.5, 2)}     # Round to 2 decimals
{midi_val = round(${percent} * 1.27)}    # 50 * 1.27 = 63.5 → 64
```

**Use Cases**:
- Round calculated values to nearest integer
- Control decimal precision

### `abs(value)`

**Signature**: `abs(value) → number`

**Description**: Return absolute value (remove negative sign).

**Examples**:
```markdown
{magnitude = abs(${offset} - 64)}        # Distance from center
{distance = abs(${a} - ${b})}
{positive = abs(${negative_val})}
```

**Use Cases**:
- Calculate distances/deltas
- Ensure positive values

### `min(a, b, ...)`

**Signature**: `min(a, b, c, ...) → number`

**Description**: Return smallest value from arguments.

**Examples**:
```markdown
{lower = min(${val1}, ${val2})}
{clamped_max = min(${value}, 127)}       # Cap at 127
{smallest = min(${a}, ${b}, ${c}, 100)}
```

**Use Cases**:
- Cap maximum values
- Find minimum of multiple inputs

### `max(a, b, ...)`

**Signature**: `max(a, b, c, ...) → number`

**Description**: Return largest value from arguments.

**Examples**:
```markdown
{higher = max(${val1}, ${val2})}
{clamped_min = max(${value}, 0)}         # Floor at 0
{largest = max(${a}, ${b}, ${c}, 20)}
```

**Use Cases**:
- Floor minimum values
- Find maximum of multiple inputs

---

## MIDI Helper Functions

### `clamp(value, min, max)`

**Signature**: `clamp(value, min, max) → number`

**Description**: Constrain value to range [min, max]. If value < min, returns min. If value > max, returns max.

**Examples**:
```markdown
{safe_val = clamp(${raw_val}, 0, 127)}   # Ensure MIDI range
{clamped = clamp(${calculated}, 20, 100)}
{velocity = clamp(int(${input} * 1.5), 1, 127)}
```

**Use Cases**:
- Prevent MIDI value overflow/underflow
- Enforce valid parameter ranges
- Safety checks after calculations

**Implementation**:
```python
def clamp(value, min_val, max_val):
    return max(min_val, min(value, max_val))
```

### `scale_range(value, from_min, from_max, to_min, to_max)`

**Signature**: `scale_range(value, from_min, from_max, to_min, to_max) → float`

**Description**: Map value from one range to another using linear interpolation.

**Formula**:
```
result = to_min + (value - from_min) * (to_max - to_min) / (from_max - from_min)
```

**Examples**:
```markdown
# Percentage to MIDI
{midi_val = int(scale_range(${percent}, 0, 100, 0, 127))}

# Decibels to MIDI
{gain = int(scale_range(${db}, -60, 6, 0, 127))}

# BPM to device-specific range
{tempo_cc = int(scale_range(${bpm}, 40, 300, 0, 127))}

# Invert range (127-0 instead of 0-127)
{inverted = int(scale_range(${value}, 0, 127, 127, 0))}
```

**Use Cases**:
- Unit conversion (%, dB, Hz, BPM → MIDI)
- Range remapping
- Scale transformations

### `msb(value)`

**Signature**: `msb(value) → integer`

**Description**: Extract most significant byte (upper 7 bits) from 14-bit value.

**Formula**:
```
msb = (value >> 7) & 0x7F
```

**Examples**:
```markdown
{msb_val = msb(${full_value})}           # Get upper 7 bits
{coarse = msb(8192)}                     # Returns 64 (center)
{high = msb(16383)}                      # Returns 127 (max)
```

**Use Cases**:
- Split 14-bit values for high-resolution MIDI
- Extract coarse parameter value

**14-bit MIDI Pattern**:
```markdown
@alias pitch_14bit {ch} {value:0-16383} "14-bit pitch"
  {msb_val = msb(${value})}
  {lsb_val = lsb(${value})}
  - cc {ch}.64.{msb_val}  # Coarse
  - cc {ch}.96.{lsb_val}  # Fine
@end
```

### `lsb(value)`

**Signature**: `lsb(value) → integer`

**Description**: Extract least significant byte (lower 7 bits) from 14-bit value.

**Formula**:
```
lsb = value & 0x7F
```

**Examples**:
```markdown
{lsb_val = lsb(${full_value})}           # Get lower 7 bits
{fine = lsb(8192)}                       # Returns 0
{low = lsb(8320)}                        # Returns 127
```

**Use Cases**:
- Split 14-bit values for high-resolution MIDI
- Extract fine parameter value

---

## Variable Substitution

### Syntax

**Alias Parameter Reference**: `${parameter_name}`

**Description**: Substitute alias parameter value into expression.

**Examples**:
```markdown
@alias example {ch} {value} {multiplier} "Example"
  {result = ${value} * ${multiplier}}
  {offset = ${result} + ${ch}}
  - cc {ch}.7.{offset}
@end
```

### Rules

1. **Must Reference Defined Parameters**: Variable must be an alias parameter or previously computed value
2. **Curly Braces Required**: Always use `${name}`, not `$name`
3. **Numeric Only**: Only numeric values supported (no strings)
4. **Read-Only**: Cannot reassign variable values
5. **Scope**: Variables scoped to alias definition

### Referencing Computed Values

Later computed values can reference earlier ones:

```markdown
@alias multi_step {value} "Multiple computations"
  {step1 = ${value} * 2}
  {step2 = ${step1} + 10}          # References step1
  {step3 = ${step2} / ${step1}}    # References both
  - cc 1.7.{step3}
@end
```

**Order Matters**: Define variables before referencing them.

---

## Expression Examples

### Unit Conversions

#### BPM to MIDI (40-300 BPM → 0-127)
```markdown
{midi_val = int((${bpm} - 40) * 127 / 260)}
```

#### Percentage to MIDI (0-100% → 0-127)
```markdown
{midi_val = int(${percent} * 127 / 100)}
```

#### Decibels to MIDI (-60dB to +6dB → 0-127)
```markdown
{midi_val = int(scale_range(${db}, -60, 6, 0, 127))}
```

#### Frequency to MIDI Note (Hz → MIDI note)
```markdown
{note = int(12 * log2(${freq} / 440) + 69)}
# Requires log2 support (future extension)
```

### Response Curves

#### Linear Scaling
```markdown
{output = int(${input} * 1.5)}
```

#### Exponential (Quadratic)
```markdown
{normalized = ${input} / 127.0}
{curved = ${normalized} ** 2}
{output = int(${curved} * 127)}
```

#### Logarithmic Approximation
```markdown
{normalized = ${input} / 127.0}
{curved = ${normalized} ** 0.5}  # Square root
{output = int(${curved} * 127)}
```

### MIDI Value Safety

#### Basic Clamping
```markdown
{safe = clamp(${value}, 0, 127)}
```

#### Safe Multiplication
```markdown
{result = clamp(int(${value} * ${factor}), 0, 127)}
```

#### Prevent Division by Zero
```markdown
{result = ${numerator} / max(${denominator}, 1)}
```

### Multi-Step Transformations

#### Velocity Curve with Safety
```markdown
{scaled = ${velocity} * ${curve_factor} / 100}
{rounded = round(${scaled})}
{safe = clamp(${rounded}, 1, 127)}
```

#### Complementary Mix (A + B = 100%)
```markdown
{a_percent = ${mix}}
{b_percent = 100 - ${mix}}
{a_midi = int(${a_percent} * 127 / 100)}
{b_midi = int(${b_percent} * 127 / 100)}
```

#### Linked Parameters
```markdown
{cutoff = ${input}}
{resonance = clamp(int(${cutoff} / 2), 0, 80)}
{drive = min(int(${cutoff} / 4), 50)}
```

---

## Operator Precedence

Expressions follow standard mathematical precedence rules:

1. **Parentheses**: `()`
2. **Exponentiation**: `**`
3. **Unary Minus**: `-x`
4. **Multiplication/Division/Modulo**: `*`, `/`, `//`, `%` (left-to-right)
5. **Addition/Subtraction**: `+`, `-` (left-to-right)

**Examples**:
```markdown
{a = 2 + 3 * 4}        # 14, not 20 (multiplication first)
{b = (2 + 3) * 4}      # 20 (parentheses override)
{c = 2 ** 3 ** 2}      # 512 (right-to-left: 2^(3^2))
{d = 10 / 2 * 5}       # 25 (left-to-right: (10/2)*5)
```

**Best Practice**: Use parentheses for clarity, even when not strictly necessary.

---

## Security and Limitations

### Security Features

Expressions execute in a **sandboxed environment** with strict safety controls:

1. **Whitelisted Operations**: Only documented operators and functions allowed
2. **Operation Limit**: Maximum 10,000 operations per expression
3. **Timeout**: 1-second execution limit
4. **No Imports**: Cannot import modules or access external code
5. **No Attribute Access**: Cannot call object methods or access attributes
6. **No Side Effects**: Cannot modify global state or perform I/O
7. **Read-Only Parameters**: Input parameters are immutable

### Limitations

**NOT Supported**:
- Control flow (`if`, `else`, `while`, `for`)
- String operations
- List/dictionary operations
- Variable reassignment
- Function definitions
- Lambda functions
- Recursion
- Import statements
- Attribute access (`.` operator on objects)
- File I/O
- Network access

**Why**: These restrictions ensure expressions are deterministic, safe, and performant.

### Performance

- **Fast Evaluation**: Simple expressions evaluate in <1ms
- **Linear Scaling**: Complexity scales linearly with expression length
- **No Caching**: Each alias call re-evaluates expressions
- **Operation Budget**: 10,000 operations prevents infinite loops

---

## Error Handling

### Common Expression Errors

#### Division by Zero
```markdown
# Error
{result = ${value} / 0}

# Fix
{result = ${value} / max(${divisor}, 1)}
```

#### Undefined Variable
```markdown
# Error
{result = ${typo} + 10}  # typo not defined

# Fix
{result = ${value} + 10}
```

#### Invalid Syntax
```markdown
# Error
{result = ${value} + }  # Missing operand

# Fix
{result = ${value} + 10}
```

#### Exceeds Operation Limit
```markdown
# Error
{result = ${val} ** ${val} ** ${val}}  # Exponential explosion

# Fix
{result = ${val} ** 3}
```

#### Type Mismatch
```markdown
# Error (if string parameters supported in future)
{result = int("abc")}

# Fix
{result = int(${numeric_param})}
```

### Debugging Tips

1. **Test Incrementally**: Add computed values one at a time
2. **Use Known Values**: Test with simple inputs (0, 64, 127)
3. **Verify Math**: Calculate by hand to confirm formula
4. **Add Safety**: Use `clamp()` to catch overflow/underflow
5. **Check Types**: Ensure `int()` where MIDI values expected

---

## See Also

- [Computed Values User Guide](../user-guide/computed_values.md) - Detailed guide with real-world examples
- [Alias System Guide](../user-guide/alias-system.md) - Alias definition syntax
- [MIDI Commands](../user-guide/midi-commands.md) - Valid MIDI value specifications
- [Examples: computed_values.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/03_advanced/04_computed_values.mmd) - Working code examples

---

**Document Version**: 1.0
**Last Updated**: November 2025
**Status**: Complete
