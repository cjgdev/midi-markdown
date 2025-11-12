---
description: Explain MMD compilation pipeline and which components handle what
---

Explain the MMD compilation pipeline and help locate which component handles a specific feature.

## Pipeline Overview:

```
.mmd file (text)
    ↓
1. Parser (parser/parser.py) → AST
    ↓
2. Import Resolver (alias/imports.py) → Load device libraries
    ↓
3. Alias Resolver (alias/resolver.py) → Expand aliases
    ↓
4. Command Expander (expansion/expander.py) → Variables, loops, sweeps
    ↓
5. Validator (utils/validation/) → Check ranges, timing
    ↓
6. IR Compiler (core/compiler.py) → Intermediate representation
    ↓
7. Codegen (codegen/midi_file.py) → MIDI bytes
    ↓
.mid file (binary)
```

## Component Responsibilities:

### 1. Parser Layer (src/midi_markdown/parser/)
**What it does:**
- Lexical analysis (tokenization)
- Syntactic analysis (grammar rules)
- AST generation
- Position tracking for errors

**Key files:**
- `mml.lark` - Grammar definition (EBNF)
- `parser.py` - MMLParser class
- `transformer.py` - Parse tree → AST
- `ast_nodes.py` - AST data structures

**Handles:** Basic syntax, frontmatter, timing markers, MIDI commands

---

### 2. Import Resolver (src/midi_markdown/alias/imports.py)
**What it does:**
- Loads device library files
- Resolves @import statements
- Detects circular imports
- Merges alias definitions

**Handles:** @import directives, device library loading

---

### 3. Alias Resolver (src/midi_markdown/alias/resolver.py)
**What it does:**
- Expands alias calls to MIDI commands
- Parameter substitution
- Default values and enums
- Conditional logic (@if/@elif/@else)
- Computed values

**Related files:**
- `conditionals.py` - Conditional expansion
- `computation.py` - Expression evaluation

**Handles:** @alias definitions, alias calls, computed values

---

### 4. Command Expander (src/midi_markdown/expansion/)
**What it does:**
- Variable resolution (@define)
- Loop expansion (@loop)
- Sweep expansion (@sweep)
- Timing calculations (absolute, musical, relative)
- Expression evaluation

**Key files:**
- `expander.py` - Main orchestrator
- `variables.py` - Symbol table
- `loops.py` - Loop expansion
- `sweeps.py` - Sweep/ramp expansion

**Handles:** @define, @loop, @sweep, ${variables}, timing conversion

---

### 5. Validator (src/midi_markdown/utils/validation/)
**What it does:**
- MIDI value range checking
- Timing monotonicity verification
- Document structure validation
- Type checking

**Key files:**
- `value_validator.py` - Range checks
- `timing_validator.py` - Timing checks
- `document_validator.py` - Structure checks

**Handles:** Value ranges, timing order, required fields

---

### 6. IR Compiler (src/midi_markdown/core/)
**What it does:**
- Converts AST events to MIDIEvent objects
- Builds tempo map
- Computes time_seconds for all events
- Creates IRProgram structure

**Key files:**
- `compiler.py` - AST → IR conversion
- `ir.py` - IR data structures

**Handles:** Final event list, tempo calculations, IR queries

---

### 7. Codegen Layer (src/midi_markdown/codegen/)
**What it does:**
- Generate MIDI file bytes (mido)
- Export to JSON
- Export to CSV
- Diagnostic output

**Key files:**
- `midi_file.py` - MIDI file generation
- `json_export.py` - JSON export
- `csv_export.py` - CSV export

**Handles:** Output format generation

---

### 8. Runtime Layer (src/midi_markdown/runtime/)
**What it does:**
- Real-time MIDI playback
- Event scheduling (sub-5ms precision)
- TUI display
- MIDI I/O

**Key files:**
- `player.py` - High-level playback API
- `scheduler.py` - Event timing
- `midi_io.py` - Hardware I/O
- `tui/` - Terminal interface

**Handles:** Live playback, real-time sending

---

### 9. CLI Layer (src/midi_markdown/cli/)
**What it does:**
- User-facing commands
- Error formatting
- Command-line interface

**Key files:**
- `commands/compile.py` - Compile command
- `commands/validate.py` - Validate command
- `commands/play.py` - Play command
- `errors.py` - Error formatting

**Handles:** User interaction, CLI arguments

---

## Finding What You Need:

Ask me: "Where does X happen?" and I'll tell you which component handles it.

Examples:
- "Where are timing calculations?" → `expansion/expander.py`
- "Where is validation?" → `utils/validation/`
- "Where are aliases expanded?" → `alias/resolver.py`
- "Where is MIDI file generation?" → `codegen/midi_file.py`
- "Where are loops expanded?" → `expansion/loops.py`

For detailed architecture documentation, see:
- `docs/developer-guide/architecture.md` - Complete architecture overview
- `docs/dev-guides/parser-patterns.md` - Parser internals
- `docs/dev-guides/timing-system.md` - Timing calculations
