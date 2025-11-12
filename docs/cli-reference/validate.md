# Command: validate

> **Audience**: Users
> **Level**: Beginner to Intermediate

Validate MMD file syntax and semantics without generating output files.

---

## Synopsis

```bash
mmdc validate [OPTIONS] INPUT_FILE
mml validate [OPTIONS] INPUT_FILE       # Shorter alias
```

---

## Description

The `validate` command performs **comprehensive validation** of MMD files without generating MIDI output. It's faster than full compilation and useful for:

- Quick error checking during development
- Pre-commit hooks and CI/CD pipelines
- Batch validation of multiple files
- Learning MMD syntax (immediate feedback)

**What validate checks**:

1. **Syntax** - Parse errors, unexpected tokens, malformed commands
2. **MIDI Values** - Note numbers (0-127), velocities (0-127), CC numbers (0-127)
3. **Channels** - Channel numbers (1-16)
4. **Pitch Bend** - Range (-8192 to +8191)
5. **Timing** - Monotonic ordering, musical time requirements
6. **Aliases** - Undefined references, parameter count mismatches
7. **Imports** - File existence, circular dependencies
8. **Variables** - Undefined variable references
9. **Loops** - Valid iteration counts and ranges
10. **Sweeps** - Valid ramp parameters

**What validate does NOT do**:
- Generate MIDI files
- Compile to IR (Intermediate Representation)
- Expand all features (some expansion happens for validation)
- Create any output files

**Comparison with other commands**:

| Command | Speed | Checks | Output |
|---------|-------|--------|--------|
| `check` | Fastest | Syntax only | None |
| `validate` | Fast | Syntax + semantics | None |
| `compile` | Slower | Everything + generates | MIDI file |

---

## Options

### Input

#### `INPUT_FILE` (required)
Path to `.mmd` file to validate.

```bash
mmdc validate song.mmd
mmdc validate path/to/performance.mmd
```

---

### Output Control

#### `-v, --verbose`
Show detailed validation steps.

```bash
mmdc validate song.mmd --verbose
```

**Verbose output shows**:
- Parsing progress
- Event count
- Import loading
- Alias resolution
- Each validation phase

**Example verbose output**:
```
Validating: song.mmd
  Parsing file...
  Parsed: 38 event(s)
  Validating MIDI values...
  Validating timing...
✓ Validation passed
  File is valid and ready for compilation
```

---

#### `--no-progress`
Disable progress indicators (for scripting/CI).

```bash
mmdc validate large_file.mmd --no-progress
```

**Progress appears for**:
- Files >50KB
- Files with >500 events
- Verbose mode (`-v`)

---

### Debugging

#### `--debug`
Show full error tracebacks instead of formatted errors.

```bash
mmdc validate broken.mmd --debug
```

**Useful for**: Bug reports, understanding internal errors.

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0    | Validation passed - file is valid |
| 1    | Validation failed - errors found |
| 2    | Parse error - syntax mistakes |
| 3    | Validation error - invalid values/structure |
| 4    | File not found or not readable |

**Script usage**:
```bash
if mmdc validate song.mmd; then
  echo "File is valid"
else
  echo "Validation failed with code $?"
fi
```

---

## Examples

### Basic Validation

```bash
# Simplest usage
mmdc validate song.mmd
```

**Success output**:
```
Validating: song.mmd
✓ Validation passed
  File is valid and ready for compilation
```

**Error output**:
```
Validating: song.mmd

✗ Validation failed with 2 error(s):

  • MIDI value out of range: Note 128 exceeds maximum (127) at line 15
  • Channel number must be 1-16, got 17 at line 23

```

---

### Verbose Validation

```bash
# See all validation steps
mmdc validate song.mmd --verbose
```

**Output**:
```
Validating: song.mmd
  Parsing file...
  Parsed: 38 event(s)
  Validating MIDI values...
  Validating timing...
✓ Validation passed
  File is valid and ready for compilation
```

---

### Batch Validation

```bash
# Validate all MMD files in directory
for file in *.mmd; do
  if mmdc validate "$file"; then
    echo "✓ $file"
  else
    echo "✗ $file"
  fi
done
```

**Advanced batch validation**:
```bash
# Parallel validation with xargs
find . -name "*.mmd" | xargs -P 4 -I {} mmdc validate {}
```

---

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Validate all staged .mmd files
staged_files=$(git diff --cached --name-only --diff-filter=ACM | grep '\.mmd$')

if [ -n "$staged_files" ]; then
  echo "Validating MMD files..."

  for file in $staged_files; do
    if ! mmdc validate "$file" --no-progress; then
      echo "Validation failed: $file"
      echo "Commit aborted."
      exit 1
    fi
  done

  echo "All MMD files valid ✓"
fi

exit 0
```

**Make executable**:
```bash
chmod +x .git/hooks/pre-commit
```

---

### CI/CD Pipeline

```yaml
# .github/workflows/validate-mml.yml
name: Validate MMD Files

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install mmdc
        run: pipx install mmdc

      - name: Validate all MMD files
        run: |
          find . -name "*.mmd" -exec mmdc validate {} --no-progress \;
```

**GitLab CI**:
```yaml
# .gitlab-ci.yml
validate-mml:
  stage: test
  script:
    - pipx install mmdc
    - find . -name "*.mmd" | xargs mmdc validate --no-progress
  only:
    - merge_requests
    - main
```

---

### Development Workflow

```bash
# 1. Quick syntax check (fastest)
mmdc check song.mmd

# 2. Full validation
mmdc validate song.mmd

# 3. Compile to MIDI
mmdc compile song.mmd
```

**Watch mode** (with `entr`):
```bash
# Auto-validate on file change
ls *.mmd | entr mmdc validate song.mmd
```

---

### Large File Validation

```bash
# Validate with progress indicator
mmdc validate large_composition.mmd --verbose
```

**Output**:
```
Validating: large_composition.mmd
  Parsing file...
  Parsed: 1247 event(s)
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% Validating...
✓ Validation passed
  File is valid and ready for compilation
```

---

### Debug Mode

```bash
# Show full traceback on error
mmdc validate broken.mmd --debug
```

**Normal error**:
```
✗ Validation failed with 1 error(s):

  • Unexpected token 'foo' at line 12
```

**Debug error** (with `--debug`):
```
✗ Validation failed with 1 error(s):

  • Unexpected token 'foo' at line 12

Traceback (most recent call last):
  File ".../parser.py", line 86, in parse_string
    result = self.parser.parse(content)
  ...
lark.exceptions.UnexpectedToken: ...
```

---

## Validation Details

### Syntax Validation

**Checks**:
- Command spelling (note_on, cc, pc, etc.)
- Timing marker format ([mm:ss.ms], [bars.beats.ticks])
- Frontmatter YAML syntax
- Comment syntax
- Directive structure (@alias, @loop, @import)

**Example errors**:
```yaml
# ❌ Wrong
[00:01.0]  # Missing digit
- note_onn 1.60 80 1b  # Typo

# ✅ Correct
[00:01.000]
- note_on 1.60 80 1b
```

---

### Value Validation

**MIDI value ranges**:
- Notes: 0-127 (C-1 to G9)
- Velocities: 0-127
- CC numbers: 0-127
- CC values: 0-127
- Program numbers: 0-127
- Channels: 1-16
- Pitch bend: -8192 to +8191

**Example errors**:
```yaml
# ❌ Wrong
- note_on 1.128 80 1b  # Note > 127
- cc 17.7.64            # Channel > 16
- pc 1.200              # Program > 127

# ✅ Correct
- note_on 1.127 80 1b  # Max note
- cc 16.7.64            # Max channel
- pc 1.127              # Max program
```

---

### Timing Validation

**Rules**:
1. Timing must be **monotonically increasing** (no going backwards)
2. Musical time requires **tempo** and **time_signature** in frontmatter
3. Relative timing (`[@]`) requires a previous event
4. Delta timing (`[+1s]`) accumulates correctly

**Example errors**:
```yaml
# ❌ Wrong - timing goes backwards
[00:02.000]
- note_on 1.60 80 1b
[00:01.000]  # ERROR: Earlier than previous
- note_off 1.60

# ✅ Correct - monotonically increasing
[00:01.000]
- note_on 1.60 80 1b
[00:02.000]
- note_off 1.60
```

**Musical time requirements**:
```yaml
# ❌ Wrong - no tempo/time_signature
[1.1.0]  # ERROR: Musical time needs frontmatter
- note_on 1.60 80 1b

# ✅ Correct
---
tempo: 120
time_signature: "4/4"
---

[1.1.0]  # Now valid
- note_on 1.60 80 1b
```

---

### Alias Validation

**Checks**:
- All referenced aliases are defined or imported
- Parameter count matches definition
- Parameter types match (note, percent, enum, int)
- Parameter values in range

**Example errors**:
```yaml
# ❌ Wrong - undefined alias
- cortex_load 1.2.3.5  # ERROR: cortex_load not defined

# ✅ Correct - import first
@import "devices/quad_cortex.mmd"
- cortex_load 1.2.3.5
```

---

### Import Validation

**Checks**:
- Imported files exist
- No circular imports (A imports B, B imports A)
- Imported files are valid MML
- Relative paths resolve correctly

**Example errors**:
```yaml
# ❌ Wrong - file not found
@import "devices/nonexistent.mmd"  # ERROR

# ✅ Correct
@import "devices/quad_cortex.mmd"
```

---

## Performance

### Validation Speed

**Benchmarks** (typical hardware):

| File Size | Events | Validation Time |
|-----------|--------|-----------------|
| Small     | <100   | <20ms           |
| Medium    | 100-500 | <100ms         |
| Large     | 1000+  | <500ms          |

**Comparison**:
- `check` (syntax only): 5-10x faster than validate
- `validate` (full checks): 2-3x faster than compile
- `compile` (everything): Slowest but generates output

---

### Tips for Faster Validation

1. **Use `check` for quick feedback**:
   ```bash
   mmdc check song.mmd  # 5-10x faster
   ```

2. **Disable progress for small files**:
   ```bash
   mmdc validate song.mmd --no-progress
   ```

3. **Batch validate in parallel**:
   ```bash
   find . -name "*.mmd" | xargs -P 4 -I {} mmdc validate {}
   ```

---

## Common Issues

### "Timing must be monotonically increasing"

**Problem**: Events are out of chronological order.

**Solution**: Sort timing markers in ascending order:
```yaml
# ❌ Wrong
[00:03.000]
[00:02.000]  # Goes backwards!

# ✅ Correct
[00:02.000]
[00:03.000]
```

**See**: [Troubleshooting Guide - Timing Errors](../reference/troubleshooting.md#timing-errors)

---

### "Musical time requires tempo and time_signature"

**Problem**: Using musical timing without required frontmatter.

**Solution**: Add frontmatter:
```yaml
# ❌ Wrong
[1.1.0]  # Musical time needs context

# ✅ Correct
---
tempo: 120
time_signature: "4/4"
---

[1.1.0]  # Now valid
```

---

### "Undefined alias"

**Problem**: Using alias that isn't defined or imported.

**Solution**: Define alias or import device library:
```yaml
# ❌ Wrong
- cortex_load 1.2.3.5  # Not defined

# ✅ Correct - Option 1: Import
@import "devices/quad_cortex.mmd"
- cortex_load 1.2.3.5

# ✅ Correct - Option 2: Define locally
@alias cortex_load {ch}.{setlist}.{group}.{preset}
  - cc {ch}.32.{setlist}
  - cc {ch}.0.{group}
  - pc {ch}.{preset}
@end

- cortex_load 1.2.3.5
```

---

### "MIDI value out of range"

**Problem**: Value exceeds MIDI limits (0-127 for most values).

**Solution**: Fix the value:
```yaml
# ❌ Wrong
- cc 1.7.200  # Value > 127
- note_on 1.200 80 1b  # Note > 127

# ✅ Correct
- cc 1.7.127  # Max value
- note_on 1.127 80 1b  # Max note (G9)
```

---

### "Channel must be 1-16"

**Problem**: Channel number outside valid range.

**Solution**: Use channels 1-16:
```yaml
# ❌ Wrong
- note_on 17.60 80 1b  # Channel > 16

# ✅ Correct
- note_on 16.60 80 1b  # Max channel
```

---

### Validation passes but compile fails

**Problem**: File validates but compilation has errors.

**Explanation**: Validation doesn't expand all features (some expansion is deferred to compile).

**Solution**: Always test with `compile` before performance:
```bash
# 1. Validate (quick check)
mmdc validate song.mmd

# 2. Compile (full check)
mmdc compile song.mmd --format table
```

---

## Tips & Tricks

### Editor Integration

**VS Code** (with task):
```json
// .vscode/tasks.json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Validate MML",
      "type": "shell",
      "command": "mmdc validate ${file}",
      "group": "build",
      "presentation": {
        "reveal": "always",
        "panel": "new"
      },
      "problemMatcher": []
    }
  ]
}
```

**Usage**: Cmd+Shift+P → "Run Task" → "Validate MML"

---

### Watch Mode

```bash
# Install entr (file watcher)
brew install entr  # macOS
apt-get install entr  # Linux

# Auto-validate on save
ls *.mmd | entr mmdc validate /_
```

**Alternative** (with `fswatch`):
```bash
fswatch -o song.mmd | xargs -n1 -I{} mmdc validate song.mmd
```

---

### Validation in Make

```makefile
# Makefile
.PHONY: validate validate-all

validate:
	mmdc validate song.mmd

validate-all:
	@for file in *.mmd; do \
		echo "Validating $$file..."; \
		mmdc validate "$$file" || exit 1; \
	done
	@echo "All files valid ✓"
```

**Usage**:
```bash
make validate       # Single file
make validate-all   # All files
```

---

### Continuous Validation

```bash
# Validate before every commit
# .git/hooks/pre-commit
#!/bin/bash
git diff --cached --name-only --diff-filter=ACM | grep '\.mmd$' | \
  xargs -I {} mmdc validate {} --no-progress
```

---

### Validate Before Playback

```bash
# Safe playback script
#!/bin/bash
FILE=$1
PORT=${2:-"IAC Driver Bus 1"}

if mmdc validate "$FILE"; then
  echo "Validation passed, starting playback..."
  mmdc play "$FILE" --port "$PORT"
else
  echo "Validation failed, aborting playback"
  exit 1
fi
```

---

## Validation vs. Check vs. Compile

### When to use `check`

**Use for**: Rapid syntax checking during editing
- Fastest (syntax only)
- No semantic validation
- No value range checks
- Perfect for editor integration

```bash
mmdc check song.mmd  # <20ms
```

---

### When to use `validate`

**Use for**: Pre-commit, CI/CD, development workflow
- Fast (2-3x faster than compile)
- Full semantic validation
- No output file generation
- Catches most issues

```bash
mmdc validate song.mmd  # <100ms
```

---

### When to use `compile`

**Use for**: Final verification before performance
- Slowest (generates output)
- 100% complete validation
- Tests entire pipeline
- Creates output file

```bash
mmdc compile song.mmd  # <200ms
```

---

### Recommended Workflow

```bash
# 1. During editing: check (fastest)
mmdc check song.mmd

# 2. Before commit: validate (comprehensive)
mmdc validate song.mmd

# 3. Before performance: compile (complete)
mmdc compile song.mmd --format table
```

---

## See Also

- [check command](check.md) - Faster syntax-only checking
- [compile command](compile.md) - Full compilation with output
- [inspect command](inspect.md) - Analyze compiled events
- [Troubleshooting Guide](../reference/troubleshooting.md) - Common validation errors
- [MML Syntax Reference](../user-guide/mmd-syntax.md) - Complete syntax guide
- [First Song Tutorial](../getting-started/first-song.md) - Learn MMD basics

---

**Next Steps**: Learn about [syntax checking](check.md) or [compilation](compile.md).
