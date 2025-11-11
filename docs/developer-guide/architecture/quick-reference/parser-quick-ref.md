## MMD Parser Quick Reference

**Fast lookup guide for the MMD parser implementation**

---

### Parser Usage

```python
from midi_markdown.parser.ast_builder import Parser

# Initialize
parser = Parser()

# Parse string
doc = parser.parse(source, source_file="test.mmd")

# Parse file
doc = parser.parse_file(Path("file.mmd"))
```

---

### Key Files

| File | Purpose | Lines |
|------|---------|-------|
| `src/midi_markdown/parser/mml.lark` | Grammar definition | ~280 |
| `src/midi_markdown/parser/ast_nodes.py` | AST node classes | ~450 |
| `src/midi_markdown/parser/ast_builder.py` | Parser & transformer | ~720 |
| `tests/unit/test_parser.py` | Test suite | ~600 |

---

### AST Node Quick Ref

```python
# Document
Document(frontmatter, statements)
Frontmatter(content, parsed_data)

# Directives
ImportDirective(path)
DefineDirective(name, value)
AliasSimple(name, parameters, expansion, description)
AliasMacro(name, parameters, commands, description)
LoopDirective(count, start_timing, interval, body)
IfDirective(condition, body, elif_clauses, else_clause)
TrackDirective(name, parameters)

# Timing
Timing(timing_type, value, ...)
  timing_type: ABSOLUTE | MUSICAL | RELATIVE_UNIT | RELATIVE_MUSICAL | SIMULTANEOUS
TimingBlock(timing, commands)

# Commands
MIDICommand(command_name, arguments)
AliasCall(command_name, arguments)
MetaCommand(command_name, arguments)

# Expressions
BinaryOp(operator, left, right)
Literal(value)
VariableRef(name)
RampExpr(start_value, end_value, ramp_type)

# Values
DottedValue(components)  # [1, 5] for "1.5"
NoteSpec(note_name, octave)
  .to_midi_note() -> int
```

---

### Grammar Patterns

```ebnf
# Document
document: frontmatter? body

# Frontmatter
frontmatter: "---" frontmatter_content "---"

# Directives
import_directive: IMPORT STRING
define_directive: DEFINE IDENTIFIER value_expr
alias_simple: ALIAS IDENTIFIER parameter_list? command_expansion STRING?

# Timing
timing: "[" timecode "]" | "[" "@" "]"
timecode: TIMECODE

# Commands
midi_command: "-" command_name argument*
argument: NUMBER | note_spec | dotted_value | STRING | value_expr

# Expressions
expr: term | expr "+" term | expr "-" term
term: factor | term "*" factor | term "/" factor
factor: NUMBER | variable_ref | "(" expr ")"
```

---

### Timing Types

| Pattern | Type | Example | Fields |
|---------|------|---------|--------|
| `mm:ss.ms` | ABSOLUTE | `[00:30.500]` | minutes, seconds |
| `bars.beats.ticks` | MUSICAL | `[8.2.120]` | bars, beats, ticks |
| `+value(unit)` | RELATIVE_UNIT | `[+1b]`, `[+500ms]` | value, unit |
| `+bars.beats.ticks` | RELATIVE_MUSICAL | `[+2.1.0]` | bars, beats, ticks |
| `@` | SIMULTANEOUS | `[@]` | - |

---

### Testing Commands

```bash
# Run all parser tests
pytest tests/unit/test_parser.py -v

# Run specific test class
pytest tests/unit/test_parser.py::TestTimingParsing -v

# With coverage
pytest tests/unit/test_parser.py --cov=src/midi_markdown/parser

# Fast run (no output)
pytest tests/unit/test_parser.py -q

# Stop on first failure
pytest tests/unit/test_parser.py -x
```

---

### Test Structure (60+ tests)

```
TestParserBasics (3)
TestFrontmatterParsing (2)
TestDirectiveParsing (3)
TestAliasParsing (3)
TestTimingParsing (4)
TestCommandParsing (5)
TestTimingWithCommands (3)
TestTrackHeaders (2)
TestLoopParsing (2)
TestConditionalParsing (2)
TestExpressionParsing (4)
TestCommentParsing (3)
TestCompleteDocuments (2)
TestErrorHandling (2)
TestFileParsing (2)
TestASTNodeProperties (3)
```

---

### Common AST Traversal

```python
# Walk all statements
for stmt in doc.statements:
    if isinstance(stmt, TimingBlock):
        print(f"Timing: {stmt.timing.value}")
        for cmd in stmt.commands:
            print(f"  {cmd.command_name}")

    elif isinstance(stmt, ImportDirective):
        print(f"Import: {stmt.path}")

    elif isinstance(stmt, DefineDirective):
        print(f"Define: {stmt.name} = {stmt.value}")
```

---

### Error Handling

```python
from midi_markdown.parser.ast_builder import ParseError

try:
    doc = parser.parse(source)
except ParseError as e:
    print(f"{e.file}:{e.line}:{e.column}: {e.message}")
```

---

### Transformer Method Mapping

| Grammar Rule | Transformer Method | Returns |
|--------------|-------------------|---------|
| `document` | `document()` | `Document` |
| `frontmatter` | `frontmatter()` | `Frontmatter` |
| `import_directive` | `import_directive()` | `ImportDirective` |
| `define_directive` | `define_directive()` | `DefineDirective` |
| `alias_simple` | `alias_simple()` | `AliasSimple` |
| `alias_macro` | `alias_macro()` | `AliasMacro` |
| `timing` | `timing()` | `Timing` |
| `timing_block` | `timing_block()` | `TimingBlock` |
| `midi_command` | `midi_command()` | `MIDICommand` |
| `add` | `add()` | `BinaryOp` |
| `variable_ref` | `variable_ref()` | `VariableRef` |
| `note_spec` | `note_spec()` | `NoteSpec` |
| `NUMBER` | `NUMBER()` | `int` or `float` |
| `STRING` | `STRING()` | `str` |
| `IDENTIFIER` | `IDENTIFIER()` | `str` |

---

### Lark Configuration

```python
Lark(
    grammar,
    parser="lalr",              # Fast LALR parser
    propagate_positions=True,   # Track line/column
    maybe_placeholders=False,   # Strict parsing
)
```

---

### Note Name to MIDI Conversion

```python
note = NoteSpec(note_name="C", octave=4)
midi_note = note.to_midi_note()  # 60 (middle C)

# Mapping
C4 = 60 (middle C)
A4 = 69 (440 Hz)
C5 = 72
```

Note: C#4 and Db4 are enharmonic (both = 61)

---

### Dependencies

```toml
[project]
dependencies = [
    "lark>=1.3.1",      # Parser generator
    "pyyaml>=6.0",      # Frontmatter parsing
]
```

Install: `uv add lark pyyaml`

---

### Next Pipeline Steps

1. **Validation** (`utils/validation.py`)
   - Validate MIDI ranges
   - Check timing monotonicity
   - Validate frontmatter

2. **Alias Resolution** (`alias/resolver.py`)
   - Expand alias calls
   - Substitute parameters
   - Handle imports

3. **MIDI Generation** (`midi/generator.py`)
   - Convert AST to MIDI events
   - Calculate timing in ticks
   - Write MIDI file

---

### Quick Debug

```python
# Print AST structure
def print_ast(node, depth=0):
    print("  " * depth + node.__class__.__name__)
    for child in getattr(node, 'children', []):
        print_ast(child, depth + 1)
    for stmt in getattr(node, 'statements', []):
        print_ast(stmt, depth + 1)

print_ast(doc)
```

---

### Status

✅ Grammar complete (280 lines)
✅ AST nodes complete (30+ types)
✅ Parser & transformer complete (720 lines)
✅ Tests complete (60+ tests)
✅ Documentation complete

**Ready for next phase: Validation & MIDI Generation**
