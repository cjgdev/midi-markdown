# Command: repl

> **Audience**: Users
> **Level**: Intermediate to Advanced

Interactive REPL (Read-Eval-Print Loop) for live MIDI composition and testing.

---

## Synopsis

```bash
mmdc repl [OPTIONS]
mml repl [OPTIONS]                     # Shorter alias
```

---

## Description

The `repl` command starts an **interactive session** for live MMD composition, testing, and experimentation. It provides a REPL (Read-Eval-Print Loop) environment where you can:

- Write MMD commands interactively
- Define and test aliases on the fly
- Import device libraries dynamically
- Inspect compiled events immediately
- Control tempo and resolution
- Build sequences incrementally

**Key Features**:
- **Multi-line input** - Automatic continuation for @alias, @loop, @sweep blocks
- **History** - Up/Down arrows, Ctrl+R search, persistent history file
- **Auto-completion** - Tab completion for commands and directives
- **State management** - Variables, aliases, imports persist across commands
- **Event inspection** - See compiled IR after each command
- **Meta-commands** - `.help`, `.list`, `.reset`, `.tempo`, `.ppq`, `.quit`

**Typical use cases**:
- Testing alias definitions before adding to device libraries
- Experimenting with timing and commands
- Live coding MIDI sequences
- Learning MMD syntax interactively
- Quick prototyping before writing full files

---

## Options

#### `--debug`
Enable debug mode (show full tracebacks on errors).

```bash
mmdc repl --debug
```

**Use when**: Troubleshooting REPL issues, reporting bugs.

---

## REPL Interface

### Welcome Banner

```
╭─────────────────────────────────────────╮
│  MMD REPL - Interactive MIDI Session   │
╰─────────────────────────────────────────╯

Type .help for commands, Ctrl+D to exit

mml>
```

---

### Prompts

**Main prompt** (ready for input):
```
mml>
```

**Continuation prompt** (multi-line input):
```
...
```

**Example multi-line session**:
```
mml> @alias test {val}
...    - cc 1.7.{val}
...  @end
✓ Alias: test (1 param)
```

---

### Keyboard Shortcuts

| Shortcut | Action | Description |
|----------|--------|-------------|
| **Ctrl+C** | Cancel | Cancel current input (clear buffer) |
| **Ctrl+D** | Exit | Exit REPL gracefully |
| **Up/Down** | History | Navigate command history |
| **Ctrl+R** | Search | Search command history |
| **Tab** | Complete | Auto-complete commands (partial) |
| **Enter** | Submit | Submit line (or continue for multi-line) |

---

## Meta-Commands

Meta-commands start with `.` and control REPL behavior (not MMD code).

### `.help`
Show available meta-commands.

```
mml> .help
MMD REPL Commands:
  .help         - Show this help message
  .quit/.exit   - Exit REPL
  .reset        - Clear all state
  .list         - Show variables, aliases, imports
  .inspect      - Show last compiled IR
  .tempo <bpm>  - Set tempo (e.g., .tempo 140)
  .ppq <value>  - Set resolution (e.g., .ppq 960)

Press Ctrl+C to cancel input, Ctrl+D to exit
```

---

### `.quit` / `.exit`
Exit REPL session.

```
mml> .quit

Goodbye!
```

**Alternative**: Press **Ctrl+D**

---

### `.reset`
Clear all state (variables, aliases, imports, IR).

```
mml> .reset
✓ State reset
```

**Clears**:
- All defined variables
- All defined aliases
- All imported libraries
- Last compiled IR
- Resets tempo to 120 BPM
- Resets PPQ to 480

---

### `.list`
Show current session state.

```
mml> .list
Current State:
  Variables (2):
    VELOCITY = 80
    CHANNEL = 1
  Aliases (3):
    test
    fade_in
    cortex_load
  Imports (1):
    devices/quad_cortex.mmd
  Settings:
    Tempo: 120 BPM
    PPQ: 480
    Time Signature: 4/4
```

**Shows**:
- All variables and their values
- All alias names
- All imported file paths
- Current tempo, PPQ, time signature

---

### `.inspect`
Show last compiled IR program.

```
mml> .inspect
Last Compiled IR:
  Events: 24
  Duration: 5.00s

┌──────────┬──────────────┬─────────┬──────────────┐
│ Time     │ Event        │ Channel │ Data         │
├──────────┼──────────────┼─────────┼──────────────┤
│ 0:00.000 │ Tempo        │ -       │ 120 BPM      │
│ 0:00.000 │ Note On      │ 1       │ 60 / 80      │
│ 0:01.000 │ Note Off     │ 1       │ 60           │
└──────────┴──────────────┴─────────┴──────────────┘
```

**Shows**: Full event table with statistics (last 20 events if >20).

---

### `.tempo <bpm>`
Set current tempo (BPM).

```
mml> .tempo 140
✓ Tempo set to 140 BPM
```

**Range**: 1-500 BPM

**Affects**: Subsequent MIDI event compilation (tempo events).

---

### `.ppq <value>`
Set pulses per quarter note (resolution).

```
mml> .ppq 960
✓ PPQ set to 960
```

**Range**: 1-9600

**Affects**: Timing precision for subsequent events.

---

## Interactive Features

### Multi-line Input

The REPL automatically detects incomplete input and switches to continuation mode.

**Example - Alias definition**:
```
mml> @alias fade_in {ch}.{start}.{end}.{steps}
...    @sweep linear {start} {end} {steps}
...      - cc {ch}.7.{value}
...    @end
...  @end
✓ Alias: fade_in (4 params)
```

**Incomplete constructs**:
- `@alias ... @end` blocks
- `@loop ... @end` blocks
- `@sweep ... @end` blocks
- `@if/@elif/@else ... @end` blocks

---

### Variable Definitions

Define variables that persist across commands.

```
mml> @define VELOCITY 80
✓ Defined: VELOCITY = 80

mml> @define CHANNEL 1
✓ Defined: CHANNEL = 1

mml> [00:00.000]
...  - note_on ${CHANNEL}.60 ${VELOCITY} 1b
✓ Compiled 3 events
Duration: 1.00s
```

---

### Alias Definitions

Define aliases interactively.

```
mml> @alias test {val}
...    - cc 1.7.{val}
...  @end
✓ Alias: test (1 param)

mml> [00:00.000]
...  - test 100
✓ Compiled 2 events
```

---

### Import Device Libraries

Load device libraries dynamically.

```
mml> @import "devices/quad_cortex.mmd"
✓ Imported: devices/quad_cortex.mmd (86 aliases)

mml> [00:00.000]
...  - cortex_load 1.2.3.5
✓ Compiled 5 events
```

**Aliases persist** - Can use imported aliases in subsequent commands.

---

### Immediate Compilation

MIDI events compile immediately and show result.

```
mml> [00:00.000]
...  - note_on 1.60 80 1b

Compiled 3 events
Duration: 1.00s

┌──────────┬──────────────┬─────────┬──────────────┐
│ Time     │ Event        │ Channel │ Data         │
├──────────┼──────────────┼─────────┼──────────────┤
│ 0:00.000 │ Tempo        │ -       │ 120 BPM      │
│ 0:00.000 │ Note On      │ 1       │ 60 / 80      │
│ 0:01.000 │ Note Off     │ 1       │ 60           │
└──────────┴──────────────┴─────────┴──────────────┘
```

**Shows**: First 10 events + statistics.

---

### Error Handling

Errors are shown without crashing REPL.

```
mml> - invalid_command
❌ error[E101]: Unexpected token: 'invalid_command'
  → <repl>:1:3

   1 │ - invalid_command
       │   ^^^^^^^^^^^^^^^ unexpected token

💡 Expected: note_on, note_off, cc, pc, pitch_bend, etc.

REPL state preserved - continue working
```

**State preserved** - Variables, aliases, imports remain intact after errors.

---

### Command History

**Persistent history** saved to `.mmd_history` in current directory.

**Navigation**:
- **Up/Down arrows** - Navigate history
- **Ctrl+R** - Reverse search history

**Example search**:
```
(reverse-i-search)`alias': @alias fade_in ...
```

**History persists** across REPL sessions.

---

### Auto-completion

**Tab completion** for:
- Commands: `note_on`, `cc`, `pc`, etc.
- Directives: `@define`, `@alias`, `@import`, `@loop`, `@sweep`
- Meta-commands: `.help`, `.quit`, `.reset`, `.list`, `.inspect`, `.tempo`, `.ppq`

**Example**:
```
mml> note_<TAB>
note_on  note_off

mml> .te<TAB>
.tempo
```

---

## Examples

### Basic Session

```
mml> [00:00.000]
...  - note_on 1.60 80 1b

Compiled 3 events
Duration: 1.00s

mml> .list
Current State:
  Variables: (none)
  Aliases: (none)
  Imports: (none)
  Settings:
    Tempo: 120 BPM
    PPQ: 480

mml> .quit

Goodbye!
```

---

### Variable Workflow

```
mml> @define VEL 80
✓ Defined: VEL = 80

mml> @define CH 1
✓ Defined: CH = 1

mml> [00:00.000]
...  - note_on ${CH}.60 ${VEL} 1b
...  [00:01.000]
...  - note_on ${CH}.64 ${VEL} 1b

Compiled 5 events
Duration: 2.00s

mml> .list
Current State:
  Variables (2):
    VEL = 80
    CH = 1
```

---

### Alias Testing

```
mml> @alias chord {ch}.{root}.{vel}
...    - note_on {ch}.{root} {vel} 500ms
...    - note_on {ch}.{root+4} {vel} 500ms
...    - note_on {ch}.{root+7} {vel} 500ms
...  @end
✓ Alias: chord (3 params)

mml> [00:00.000]
...  - chord 1.60.80

Compiled 7 events
Duration: 0.50s

mml> .inspect
[Shows expanded chord events]
```

---

### Import and Use

```
mml> @import "devices/quad_cortex.mmd"
✓ Imported: devices/quad_cortex.mmd (86 aliases)

mml> [00:00.000]
...  - cortex_load 1.2.3.5

Compiled 5 events

mml> .inspect
[Shows expanded CC/PC sequence]
```

---

### Tempo Control

```
mml> .tempo 140
✓ Tempo set to 140 BPM

mml> [00:00.000]
...  - note_on 1.60 80 1b

Compiled 3 events
Duration: 0.86s  # Faster due to 140 BPM

mml> .list
Settings:
  Tempo: 140 BPM
  PPQ: 480
```

---

### Loop Testing

```
mml> @loop 4
...    [+0.250s]
...    - note_on 1.60 80 100ms
...  @end

Compiled 9 events
Duration: 1.00s

┌──────────┬──────────────┬─────────┬──────────────┐
│ Time     │ Event        │ Channel │ Data         │
├──────────┼──────────────┼─────────┼──────────────┤
│ 0:00.000 │ Tempo        │ -       │ 120 BPM      │
│ 0:00.000 │ Note On      │ 1       │ 60 / 80      │
│ 0:00.100 │ Note Off     │ 1       │ 60           │
│ 0:00.250 │ Note On      │ 1       │ 60 / 80      │
│ 0:00.350 │ Note Off     │ 1       │ 60           │
└──────────┴──────────────┴─────────┴──────────────┘
```

---

### Sweep Experimentation

```
mml> @sweep linear 0 127 8
...    [+0.125s]
...    - cc 1.7.{value}
...  @end

Compiled 9 events
Duration: 1.00s

mml> .inspect
[Shows gradual CC ramp from 0 to 127]
```

---

### Multi-line Frontmatter

```
mml> ---
...  tempo: 140
...  time_signature: "3/4"
...  ppq: 960
...  ---
✓ Frontmatter: tempo=140, time_signature=3/4, ppq=960

mml> .list
Settings:
  Tempo: 140 BPM
  PPQ: 960
  Time Signature: 3/4
```

---

### Error Recovery

```
mml> [00:00.000]
...  - note_on 1.200 80 1b
❌ error[E201]: MIDI value out of range: 200 exceeds maximum (127)

REPL state preserved - continue working

mml> [00:00.000]
...  - note_on 1.60 80 1b

Compiled 3 events
Duration: 1.00s
```

**State intact** - Can continue after errors.

---

### Reset Workflow

```
mml> @define VEL 80
✓ Defined: VEL = 80

mml> @alias test {val}
...    - cc 1.7.{val}
...  @end
✓ Alias: test (1 param)

mml> .list
Variables (1):
  VEL = 80
Aliases (1):
  test

mml> .reset
✓ State reset

mml> .list
Variables: (none)
Aliases: (none)
```

---

## Use Cases

### Learning MMD Syntax

**Interactive experimentation**:
```
mml> [00:00.000]
...  - note_on 1.60 80 1b
[See immediate result]

mml> [00:00.000]
...  - cc 1.7.100
[Test CC commands]

mml> @loop 3
...    [+0.5s]
...    - note_on 1.60 80 250ms
...  @end
[Test loops]
```

**Benefit**: Instant feedback, no file editing needed.

---

### Testing Alias Definitions

**Before adding to device library**:
```
mml> @alias preset_load {ch}.{bank}.{preset}
...    - cc {ch}.32.{bank}
...    [+50ms]
...    - pc {ch}.{preset}
...  @end
✓ Alias: preset_load (3 params)

mml> [00:00.000]
...  - preset_load 1.2.5

[Verify expansion is correct]

mml> .inspect
[Check timing and values]

# If good, copy to device library file
```

---

### Prototyping Sequences

**Build incrementally**:
```
mml> @define CH 1
mml> @define VEL 80

mml> [00:00.000]
...  - note_on ${CH}.60 ${VEL} 500ms
[Test first note]

mml> [@]
...  - note_on ${CH}.64 ${VEL} 500ms
[Add harmony]

mml> [+0.5s]
...  - note_on ${CH}.67 ${VEL} 500ms
[Add next note]
```

---

### Testing Imports

**Verify device library**:
```
mml> @import "devices/quad_cortex.mmd"
✓ Imported: devices/quad_cortex.mmd (86 aliases)

mml> .list
Aliases (86):
  cortex_load
  cortex_preset
  ...

mml> [00:00.000]
...  - cortex_load 1.2.3.5

[Verify alias works correctly]
```

---

### Debugging Timing

**Test timing calculations**:
```
mml> .tempo 120
mml> .ppq 480

mml> [00:00.000]
...  - note_on 1.60 80 1b

mml> .inspect
[Check if duration is exactly 1 second]

mml> .tempo 140
mml> [00:00.000]
...  - note_on 1.60 80 1b

[Compare timing at different tempos]
```

---

### Experimenting with Variables

**Test expressions**:
```
mml> @define BASE 60
mml> [00:00.000]
...  - note_on 1.${BASE} 80 250ms
...  [+0.25s]
...  - note_on 1.${BASE+2} 80 250ms
...  [+0.25s]
...  - note_on 1.${BASE+4} 80 250ms

[Build scale incrementally]
```

---

## Performance

### REPL Responsiveness

**Typical response times**:
- Single command: <10ms
- Multi-line block: <50ms
- Import loading: <200ms
- Large compilation (100+ events): <500ms

**Features**:
- Non-blocking input
- Immediate error feedback
- Fast auto-completion
- Efficient history search

---

## Common Issues

### Multi-line input stuck in continuation mode

**Problem**: Continuation prompt (`...`) won't exit.

**Cause**: Incomplete block (missing `@end`, closing bracket, etc.)

**Solution**: Complete the block or press **Ctrl+C** to cancel:
```
mml> @alias test {val}
...    - cc 1.7.{val}
...  # Missing @end - stuck!
...  ^C
Input cancelled

mml>  # Back to main prompt
```

---

### History not persisting

**Problem**: Command history lost between sessions.

**Cause**: `.mmd_history` file not writable or deleted.

**Solution**:
```bash
# Check if history file exists
ls -la .mmd_history

# Ensure it's writable
chmod 644 .mmd_history

# Or delete and let REPL recreate
rm .mmd_history
```

---

### Tab completion not working

**Problem**: Pressing Tab inserts literal tab character.

**Cause**: Terminal doesn't support readline/prompt_toolkit.

**Solution**: Use modern terminal emulator:
- iTerm2 (macOS)
- Windows Terminal (Windows)
- Alacritty (cross-platform)

---

### Variables not substituting

**Problem**: `${VAR}` shows literally instead of substituting.

**Cause**: Variable not defined or wrong syntax.

**Solution**:
```
mml> @define VAR 80
✓ Defined: VAR = 80

mml> - cc 1.7.${VAR}
[Now substitutes correctly]

# Wrong: $VAR (missing braces)
# Wrong: {VAR} (missing $)
# Correct: ${VAR}
```

---

### Imports not found

**Problem**: `@import` fails with file not found.

**Cause**: Relative path doesn't resolve from current directory.

**Solution**: Use paths relative to current working directory:
```bash
# Start REPL from project root
cd /path/to/project
mmdc repl

# Now imports work
mml> @import "devices/quad_cortex.mmd"
```

---

### Cannot exit REPL

**Problem**: `.quit` not working or unclear how to exit.

**Solutions**:
- Type `.quit` or `.exit`
- Press **Ctrl+D**
- Press **Ctrl+C** twice
- Type EOF (platform-specific)

---

## Tips & Tricks

### Quick Alias Library Testing

```bash
# Create test file
cat > test_alias.mmd << 'EOF'
@alias myalias {val}
  - cc 1.7.{val}
@end
EOF

# Test in REPL
mmdc repl
mml> @import "test_alias.mmd"
mml> - myalias 100
```

---

### Saving REPL Sessions

```
# Copy-paste from REPL into file
mml> @define VEL 80
mml> @alias test {val}
...    - cc 1.7.{val}
...  @end

# Later, copy to .mmd file:
cat > song.mmd << 'EOF'
@define VEL 80
@alias test {val}
  - cc 1.7.{val}
@end
EOF
```

---

### REPL as Calculator

```
mml> @define RESULT ${60 + 12}
✓ Defined: RESULT = 72

mml> .list
Variables (1):
  RESULT = 72
```

---

### Building Device Libraries Interactively

```
# Test each alias in REPL
mml> @alias cortex_load {ch}.{sl}.{gr}.{pr}
...    - cc {ch}.32.{sl}
...    [+50ms]
...    - cc {ch}.0.{gr}
...    [+50ms]
...    - pc {ch}.{pr}
...  @end

# Test it
mml> - cortex_load 1.2.3.5
mml> .inspect

# If correct, copy to devices/quad_cortex.mmd
```

---

### Sharing REPL Commands

```
# Export history to share with team
cp .mmd_history team_repl_examples.txt

# Or create cheatsheet
cat > repl_cheatsheet.md << 'EOF'
# Common REPL Commands

## Define velocity variable
@define VEL 80

## Create chord alias
@alias chord {ch}.{root}.{vel}
  - note_on {ch}.{root} {vel} 500ms
  - note_on {ch}.{root+4} {vel} 500ms
  - note_on {ch}.{root+7} {vel} 500ms
@end
EOF
```

---

### REPL in Scripts

```bash
#!/bin/bash
# Test alias definitions automatically

cat > test_commands.txt << 'EOF'
@define VEL 80
@alias test {val}
  - cc 1.7.{val}
@end
[00:00.000]
- test ${VEL}
.inspect
.quit
EOF

# Pipe to REPL
mmdc repl < test_commands.txt
```

---

### Learning Workflow

```
# 1. Start REPL
mmdc repl

# 2. Try simple commands
mml> [00:00.000]
...  - note_on 1.60 80 1b

# 3. Add complexity
mml> @define VEL 80
mml> [00:00.000]
...  - note_on 1.60 ${VEL} 1b

# 4. Test loops
mml> @loop 4
...    [+0.25s]
...    - note_on 1.60 ${VEL} 100ms
...  @end

# 5. Save working examples to file
```

---

## Advanced Usage

### Custom History File

```bash
# Use custom history location
export MML_HISTORY_FILE=~/.mmd_history_global
mmdc repl
```

---

### REPL + Editor Workflow

```bash
# Terminal 1: Editor
vim song.mmd

# Terminal 2: REPL for testing
mmdc repl

# Test snippets from editor in REPL
# Copy working code back to editor
```

---

### Automated Testing with REPL

```bash
# test_aliases.sh
#!/bin/bash

cat << 'EOF' | mmdc repl
@import "devices/quad_cortex.mmd"
[00:00.000]
- cortex_load 1.2.3.5
.inspect
.quit
EOF

# Verify output contains expected events
```

---

## See Also

- [compile command](compile.md) - Generate MIDI files from MML
- [inspect command](inspect.md) - Analyze compiled events
- [validate command](validate.md) - Validate MMD syntax
- [Alias System Guide](../user-guide/alias-system.md) - Complete alias documentation
- [MML Syntax Reference](../user-guide/mmd-syntax.md) - Complete syntax guide
- [First Song Tutorial](../getting-started/first-song.md) - Learn MMD basics

---

**Next Steps**: Try the REPL with `mmdc repl`, or learn about [aliases](../user-guide/alias-system.md).
