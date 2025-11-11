# MIDI Markup Language (MML) Grammar Documentation

## Overview

This document describes the Lark grammar implementation for the MIDI Markup Language (MML) specification version 1.0.0. The grammar is designed to parse human-readable MIDI markup into a structured Abstract Syntax Tree (AST) that can be converted to MIDI files.

## Table of Contents

1. [Grammar Architecture](#grammar-architecture)
2. [Design Decisions](#design-decisions)
3. [Grammar Structure](#grammar-structure)
4. [Parser Implementation](#parser-implementation)
5. [Usage Guide](#usage-guide)
6. [Extension Guide](#extension-guide)

---

## Grammar Architecture

### Parser Type: LALR(1)

The grammar uses Lark's LALR (Look-Ahead Left-to-Right) parser for optimal performance:

**Advantages:**
- Fast parsing speed (linear time complexity)
- Low memory footprint
- Deterministic parsing behavior
- Suitable for large files

**Trade-offs:**
- Less flexible than Earley parser
- Requires more careful grammar design to avoid conflicts
- Limited error recovery capabilities

### Transformation Strategy

The grammar uses a **Transformer pattern** to convert the parse tree into Python objects:

```
Raw Text → Tokens → Parse Tree → AST → Python Objects
```

This approach provides:
- Clean separation between parsing and semantic analysis
- Type-safe data structures
- Easy validation and error reporting
- Extensible architecture

---

## Design Decisions

### 1. Timing Specification Hierarchy

```lark
timing: absolute_time
      | musical_time
      | relative_time
      | simultaneous
```

**Decision:** Use union type (|) for timing alternatives rather than optional components.

**Rationale:**
- Clear, unambiguous parsing
- Easy to validate timing format
- Allows for format-specific validation rules
- Better error messages

### 2. Command Structure

```lark
?command: note_command
        | program_change
        | control_change
        ...
```

**Decision:** Use inline rule (?) to flatten command types in the parse tree.

**Rationale:**
- Reduces tree depth
- Simplifies transformer logic
- Maintains clear command categorization
- Better performance

### 3. Parameter System

```lark
param_spec: IDENTIFIER param_type? param_default? param_enum?
```

**Decision:** Make all parameter modifiers optional with specific ordering.

**Rationale:**
- Flexible parameter definitions
- Natural reading order (name → type → default → options)
- Easy to extend with new modifiers
- Backward compatible

### 4. Expression Handling

```lark
?expression: expr_add

?expr_add: expr_mul
         | expr_add "+" expr_mul   -> add
         | expr_add "-" expr_mul   -> sub

?expr_mul: expr_atom
         | expr_mul "*" expr_atom  -> mul
         | expr_mul "/" expr_atom  -> div
```

**Decision:** Left-recursive grammar with standard operator precedence.

**Rationale:**
- Standard mathematical precedence (*, / before +, -)
- Efficient left-recursive parsing with LALR
- Matches user expectations
- Easy to extend with new operators

### 5. Comment Handling

```lark
COMMENT: /#[^\n]*/
comment_block: /\/\*[\s\S]*?\*\//
```

**Decision:** Multiple comment styles supported (Python, C-style).

**Rationale:**
- Familiar syntax for diverse users
- Different styles for different purposes
- Regex-based for performance
- Ignored during parsing (not in AST)

### 6. Whitespace Strategy

```lark
%ignore WHITESPACE
_NL: /\r?\n/
```

**Decision:** Ignore horizontal whitespace but track newlines explicitly.

**Rationale:**
- Whitespace-insensitive for readability
- Newlines significant for structure
- Cross-platform compatibility (handles \r\n and \n)
- Clean AST without whitespace nodes

### 7. String Handling

```lark
STRING: /"[^"]*"/
      | /'[^']*'/
```

**Decision:** Support both single and double quotes.

**Rationale:**
- Flexibility for users
- Avoid escaping in common cases
- Standard in most languages
- Simple implementation

---

## Grammar Structure

### Document-Level Organization

```
document
├── frontmatter (YAML)
└── statements*
    ├── imports
    ├── defines
    ├── aliases
    ├── tracks
    └── timed_events
```

### Statement Types

#### 1. Import Statement
```lark
import_stmt: "@import" STRING
```
- Simple, unambiguous syntax
- String allows for path flexibility
- No circular dependency checking in grammar (handled in semantic analysis)

#### 2. Define Statement
```lark
define_stmt: "@define" IDENTIFIER (expression | NUMBER | STRING)
```
- Supports multiple value types
- Expression evaluation deferred to transformer
- Variable references resolved during transformation

#### 3. Alias Definition

**Simple Alias:**
```lark
simple_alias: "@alias" IDENTIFIER alias_template STRING?
```

**Macro Alias:**
```lark
macro_alias: "@alias" IDENTIFIER alias_params STRING? 
             _NL* (command _NL*)+ "@end"
```

Key features:
- Template-based parameter substitution
- Optional description string
- Multi-command macros with @end delimiter
- Computed values for complex mappings

#### 4. Track Definition
```lark
track_def: "##" "Track" /[^\n]+/ _NL* track_attributes?
         | "@track" IDENTIFIER track_attributes?
```

Design choice: Support both Markdown-style (##) and @ directive syntax for compatibility.

#### 5. Control Flow

**Loops:**
```lark
loop_stmt: "@loop" INT "times" ("at" timing)? ("every" duration)? 
           _NL* (statement _NL*)* "@end"
```

**Sweeps:**
```lark
sweep_stmt: "@sweep" "from" timing "to" timing "every" duration 
            _NL* (command _NL*)+ "@end"
```

**Conditionals:**
```lark
conditional_stmt: if_clause elif_clause* else_clause? "@end"
```

### MIDI Command Grammar

#### Note Commands
```lark
note_command: "-" ("note_on" | "note_off") channel_note velocity duration?

channel_note: INT "." note_value
note_value: NOTE_NAME | INT
```

**Design choice:** Allow both note names (C4) and numbers (60) for flexibility.

#### Control Change
```lark
control_change: "-" ("control_change" | "cc") INT "." INT "." cc_value
cc_value: INT | percent | ramp_expr | random_expr
```

**Key feature:** CC values support static numbers, percentages, ramps, and random values.

#### Timing Integration
```lark
timed_event: timing _NL* command_list
```

**Design choice:** Timing precedes commands, allowing multiple commands at same time.

---

## Parser Implementation

### Core Classes

#### 1. MMLDocument
Represents the complete parsed document:
```python
@dataclass
class MMLDocument:
    frontmatter: Dict[str, Any]
    imports: List[str]
    defines: Dict[str, Any]
    aliases: Dict[str, AliasDefinition]
    tracks: List[Track]
    events: List[Any]
    metadata: Dict[str, Any]
```

#### 2. MIDICommand
Represents a single MIDI command:
```python
@dataclass
class MIDICommand:
    type: str
    channel: Optional[int]
    data1: Optional[int]
    data2: Optional[int]
    params: Dict[str, Any]
    timing: Optional[Timing]
    source_line: int
```

#### 3. Timing
Represents timing specifications:
```python
@dataclass
class Timing:
    type: str  # 'absolute', 'musical', 'relative', 'simultaneous'
    value: Any
    raw: str
```

### Transformer Methods

Key transformation methods in `MMLTransformer`:

```python
def note_command(self, cmd_type, channel_note, velocity, duration=None):
    """Transform note command to MIDICommand object"""
    channel, note = self._parse_channel_note(channel_note)
    return MIDICommand(
        type=str(cmd_type),
        channel=channel,
        data1=note,
        data2=int(velocity),
        params={'duration': duration} if duration else {}
    )

def absolute_time(self, *parts):
    """Transform absolute time to Timing object"""
    time_str = ''.join(str(p) for p in parts)
    return Timing('absolute', self._parse_absolute_time(time_str), time_str)
```

### Error Handling

The parser provides detailed error messages:

```python
def _format_parse_error(self, error, content: str, filename: str):
    """Format a parse error with context"""
    if hasattr(error, 'line') and hasattr(error, 'column'):
        lines = content.split('\n')
        error_line = lines[error.line - 1]
        
        print(f"\nError: Parse error at line {error.line}:{error.column}")
        print(f"  {error_line}")
        print(f"  {' ' * (error.column - 1)}^")
```

---

## Usage Guide

### Basic Usage

```python
from mml_parser import MMLParser

# Create parser
parser = MMLParser()

# Parse file
document = parser.parse_file('song.mml')

# Parse string
mml_content = """
[00:00.000]
- tempo 120
- pc 1.5
"""
document = parser.parse_string(mml_content)

# Access parsed data
print(f"Title: {document.frontmatter.get('title')}")
print(f"Events: {len(document.events)}")
print(f"Defines: {document.defines}")
```

### Working with Parsed Data

```python
# Iterate through events
for event in document.events:
    if isinstance(event, MIDICommand):
        print(f"Command: {event.type} on channel {event.channel}")
    elif isinstance(event, dict) and event.get('type') == 'loop':
        print(f"Loop: {event['count']} times")

# Access aliases
for name, alias_def in document.aliases.items():
    print(f"Alias: {name}")
    print(f"  Parameters: {[p['name'] for p in alias_def.parameters]}")
    print(f"  Is macro: {alias_def.is_macro}")

# Process tracks
for track in document.tracks:
    print(f"Track: {track.name} (channel {track.channel})")
```

### Converting to MIDI

```python
from mml_to_midi import MMLToMIDI

# Create converter
converter = MMLToMIDI(document)

# Generate MIDI file
midi_file = converter.to_midi()
midi_file.save('output.mid')
```

### Validation

```python
from mml_validator import MMLValidator

validator = MMLValidator(document)

# Validate timing
errors = validator.validate_timing()

# Validate MIDI values
errors.extend(validator.validate_midi_values())

# Validate aliases
errors.extend(validator.validate_aliases())

if errors:
    for error in errors:
        print(f"Error: {error}")
else:
    print("Document is valid!")
```

---

## Extension Guide

### Adding New MIDI Commands

1. **Add grammar rule:**
```lark
new_command: "-" "new_cmd" INT "." INT
```

2. **Add to command union:**
```lark
?command: note_command
        | program_change
        | new_command  # Add here
        ...
```

3. **Add transformer method:**
```python
def new_command(self, param1, param2):
    return MIDICommand(
        type='new_command',
        data1=int(param1),
        data2=int(param2)
    )
```

### Adding New Timing Formats

1. **Add grammar rule:**
```lark
frame_time: "[" INT "f" "]"  # Frame-based timing
```

2. **Add to timing union:**
```lark
timing: absolute_time
      | musical_time
      | frame_time  # Add here
      ...
```

3. **Add transformer method:**
```python
def frame_time(self, frames):
    return Timing('frame', int(frames), f"{frames}f")
```

### Adding New Expression Types

1. **Add to expression grammar:**
```lark
?expr_atom: NUMBER
          | variable_ref
          | function_call  # New expression type
          
function_call: IDENTIFIER "(" expression ("," expression)* ")"
```

2. **Add transformer:**
```python
def function_call(self, name, *args):
    return {
        'type': 'function',
        'name': str(name),
        'args': list(args)
    }
```

### Custom Validation Rules

```python
class CustomValidator(MMLValidator):
    def validate_custom_rule(self):
        errors = []
        for event in self.document.events:
            if self._violates_custom_rule(event):
                errors.append(f"Custom rule violation: {event}")
        return errors
```

### Plugin System Example

```python
class MMLPlugin:
    """Base class for MML plugins"""
    
    def extend_grammar(self, grammar: str) -> str:
        """Add grammar rules"""
        return grammar
    
    def extend_transformer(self, transformer: MMLTransformer):
        """Add transformer methods"""
        pass
    
    def post_parse(self, document: MMLDocument):
        """Process document after parsing"""
        pass

# Usage
parser = MMLParser()
parser.register_plugin(MyCustomPlugin())
```

---

## Performance Considerations

### Parser Performance

- **LALR parser:** O(n) parsing time
- **Transformer:** O(n) transformation time
- **Memory:** O(n) for AST storage

### Optimization Tips

1. **Use streaming for large files:**
```python
def parse_stream(self, file_handle):
    # Parse in chunks for very large files
    pass
```

2. **Cache parsed device libraries:**
```python
library_cache = {}

def load_library(self, path):
    if path not in library_cache:
        library_cache[path] = self.parse_file(path)
    return library_cache[path]
```

3. **Lazy evaluation of expressions:**
```python
class LazyExpression:
    def __init__(self, expr):
        self._expr = expr
        self._value = None
    
    def evaluate(self, context):
        if self._value is None:
            self._value = self._compute(context)
        return self._value
```

---

## Testing Strategy

### Unit Tests
- Test each grammar rule independently
- Test transformer methods
- Test edge cases and error conditions

### Integration Tests
- Test complete documents
- Test multi-file imports
- Test complex nested structures

### Performance Tests
- Large file handling (1000+ events)
- Many aliases (100+ definitions)
- Deep nesting (nested loops/conditionals)

### Validation Tests
- MIDI value ranges
- Timing consistency
- Alias parameter matching
- Reference resolution

---

## Common Issues and Solutions

### Issue: Ambiguous Grammar

**Problem:** Multiple parse trees for the same input.

**Solution:** Use inline rules (?) to flatten ambiguity:
```lark
?command: note_command | control_change  # Flattens the tree
```

### Issue: Left Recursion Performance

**Problem:** Slow parsing with deeply nested expressions.

**Solution:** LALR handles left recursion efficiently. For very deep nesting, consider:
```python
import sys
sys.setrecursionlimit(10000)  # Increase if needed
```

### Issue: Token Conflicts

**Problem:** Lexer can't distinguish between similar patterns.

**Solution:** Order terminals from most to least specific:
```lark
NOTE_NAME: /[A-G][#b]?-?[0-9]/  # More specific
IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9_]*/  # Less specific
```

### Issue: Error Recovery

**Problem:** Parser stops at first error.

**Solution:** Implement error recovery in transformer:
```python
def note_command(self, *args):
    try:
        return self._parse_note(*args)
    except ValueError as e:
        self.errors.append(f"Note parse error: {e}")
        return None  # Continue parsing
```

---

## Future Enhancements

### Planned Grammar Extensions

1. **MIDI 2.0 Support:**
```lark
midi2_command: "-" "cc2" INT "." INT "." INT  # 32-bit CC
```

2. **Pattern Generation:**
```lark
pattern_def: "@pattern" IDENTIFIER pattern_spec
           | "@end"
```

3. **Function Definitions:**
```lark
function_def: "@function" IDENTIFIER "(" params ")" 
              _NL* statements* "@end"
```

4. **Include with Variables:**
```lark
include_stmt: "@include" STRING "with" define_list
```

---

## References

- [Lark Parser Documentation](https://lark-parser.readthedocs.io/)
- [MIDI Specification](https://www.midi.org/specifications)
- [MML Specification v1.0.0](./MIDI_Markup_Language__MML__Specification_-_1_0_0.md)

---

## License

This grammar and implementation are part of the MIDI Markup Language project.
See LICENSE file for details.

## Contributing

To contribute to the grammar:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Update documentation
5. Submit pull request

For grammar changes, please include:
- Grammar rule additions/modifications
- Transformer method implementations
- Unit tests
- Documentation updates
- Example usage

---

**Version:** 1.0.0  
**Last Updated:** 2025-10-29  
**Maintainer:** MML Development Team
