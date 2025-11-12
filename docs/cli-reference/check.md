# Command: check

> **Audience**: Users
> **Level**: Beginner

Fast syntax-only validation for rapid development feedback.

---

## Synopsis

```bash
mmdc check [OPTIONS] INPUT_FILE
mml check [OPTIONS] INPUT_FILE         # Shorter alias
```

---

## Description

The `check` command performs **syntax-only validation** of MMD files - the fastest way to catch typos and syntax errors without full semantic validation.

**Key Difference**: `check` only verifies that your file can be **parsed**, not that it's valid MIDI.

**What check does**:
1. Parse MMD file with Lark grammar
2. Verify syntax structure (brackets, commands, timing format)
3. Report parse errors immediately

**What check does NOT do**:
- Validate MIDI value ranges (0-127)
- Check channel numbers (1-16)
- Verify timing monotonicity
- Resolve or validate aliases
- Expand variables, loops, sweeps
- Verify imports exist
- Check semantic correctness

**Speed**: Typically **5-10x faster** than `validate` and **10-20x faster** than `compile`.

**Use cases**:
- Editor save hooks for instant feedback
- Watch mode during development
- Quick syntax verification
- Learning MMD syntax

---

## Options

### Input

#### `INPUT_FILE` (required)
Path to `.mmd` file to check.

```bash
mmdc check song.mmd
mmdc check path/to/draft.mmd
```

---

### Output Control

#### `-v, --verbose`
Show verbose output with event count.

```bash
mmdc check song.mmd --verbose
```

**Verbose output**:
```
Checking syntax: song.mmd
  Parsing file...
✓ Syntax is valid
  Parsed: 38 event(s)
  Note: Use 'validate' command for full validation
```

---

### Debugging

#### `--debug`
Show full error tracebacks instead of formatted errors.

```bash
mmdc check broken.mmd --debug
```

**Useful for**: Bug reports, understanding parser behavior.

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0    | Syntax is valid - file can be parsed |
| 2    | Parse error - syntax mistakes found |
| 4    | File not found or not readable |

**Script usage**:
```bash
if mmdc check song.mmd; then
  echo "Syntax OK"
else
  echo "Syntax error, code $?"
fi
```

---

## Examples

### Basic Syntax Check

```bash
# Simplest usage
mmdc check song.mmd
```

**Success output**:
```
Checking syntax: song.mmd
✓ Syntax is valid
```

**Error output**:
```
Checking syntax: song.mmd
❌ error[E101]: Unexpected token 'foo'
  → song.mmd:12:5

   10 │ [00:01.000]
   11 │ - note_on 1.60 80 1b
   12 │ - foo
       │   ^^^ unexpected token
   13 │ [00:02.000]

💡 Expected: note_on, note_off, cc, pc, pitch_bend, etc.
```

---

### Verbose Check

```bash
# See parsing details
mmdc check song.mmd --verbose
```

**Output**:
```
Checking syntax: song.mmd
  Parsing file...
✓ Syntax is valid
  Parsed: 38 event(s)
  Note: Use 'validate' command for full validation
```

---

### Batch Syntax Check

```bash
# Check all MMD files quickly
for file in *.mmd; do
  if mmdc check "$file"; then
    echo "✓ $file"
  else
    echo "✗ $file"
  fi
done
```

**Output**:
```
✓ song1.mmd
✓ song2.mmd
✗ broken.mmd
✓ song3.mmd
```

---

### Watch Mode (Auto-check on Save)

```bash
# Install entr (file watcher)
brew install entr  # macOS
apt-get install entr  # Linux

# Auto-check on file change
ls *.mmd | entr mmdc check /_
```

**Alternative with `fswatch`**:
```bash
fswatch -o song.mmd | xargs -n1 -I{} mmdc check song.mmd
```

---

### Editor Integration

**VS Code Task** (`.vscode/tasks.json`):
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Check MMD Syntax",
      "type": "shell",
      "command": "mmdc check ${file}",
      "group": "build",
      "presentation": {
        "reveal": "always",
        "panel": "dedicated"
      },
      "problemMatcher": []
    }
  ]
}
```

**Keyboard shortcut**: Cmd+Shift+B (macOS) / Ctrl+Shift+B (Windows/Linux)

---

### Quick Development Cycle

```bash
# 1. Check syntax (fastest - <20ms)
mmdc check song.mmd

# Edit file...

# 2. Check again
mmdc check song.mmd

# When syntax is correct, validate semantics
# 3. Full validation (~100ms)
mmdc validate song.mmd
```

---

### Multiple Files

```bash
# Check multiple files
mmdc check song1.mmd song2.mmd song3.mmd

# Check all files in directory
mmdc check *.mmd

# Check files matching pattern
mmdc check setlist_*.mmd
```

---

## What Check Catches

### Syntax Errors

**Command typos**:
```yaml
# ❌ Wrong
- note_onn 1.60 80 1b  # Typo caught by check

# ✅ Correct
- note_on 1.60 80 1b
```

**Timing format errors**:
```yaml
# ❌ Wrong
[00:01.0]  # Missing digit - caught by check

# ✅ Correct
[00:01.000]
```

**Missing brackets**:
```yaml
# ❌ Wrong
00:01.000  # Missing brackets - caught by check
- note_on 1.60 80 1b

# ✅ Correct
[00:01.000]
- note_on 1.60 80 1b
```

**Malformed frontmatter**:
```yaml
# ❌ Wrong
---
title: "Song  # Missing closing quote - caught by check
---

# ✅ Correct
---
title: "Song"
---
```

**Incomplete blocks**:
```yaml
# ❌ Wrong
@alias test {val}
  - cc 1.7.{val}
# Missing @end - caught by check

# ✅ Correct
@alias test {val}
  - cc 1.7.{val}
@end
```

---

## What Check Misses

### Value Range Errors (Use `validate`)

```yaml
# ✓ Passes check (valid syntax)
# ✗ Fails validate (value > 127)
- cc 1.7.200  # Check won't catch this!

# Need validate to catch:
mmdc validate song.mmd
```

---

### Channel Validation (Use `validate`)

```yaml
# ✓ Passes check (valid syntax)
# ✗ Fails validate (channel > 16)
- note_on 17.60 80 1b  # Check won't catch this!

# Need validate to catch:
mmdc validate song.mmd
```

---

### Timing Order (Use `validate`)

```yaml
# ✓ Passes check (valid syntax)
# ✗ Fails validate (time goes backwards)
[00:02.000]
- note_on 1.60 80 1b
[00:01.000]  # Check won't catch this!
- note_off 1.60

# Need validate to catch:
mmdc validate song.mmd
```

---

### Undefined Aliases (Use `validate`)

```yaml
# ✓ Passes check (valid syntax)
# ✗ Fails validate (undefined alias)
- cortex_load 1.2.3.5  # Check won't catch this!

# Need validate to catch:
mmdc validate song.mmd
```

---

### Missing Imports (Use `validate`)

```yaml
# ✓ Passes check (valid syntax)
# ✗ Fails validate (file not found)
@import "devices/nonexistent.mmd"  # Check won't catch this!

# Need validate to catch:
mmdc validate song.mmd
```

---

## Performance

### Speed Comparison

**Benchmarks** (typical hardware):

| Command | Small File | Large File | What it Checks |
|---------|------------|------------|----------------|
| `check` | <10ms | <50ms | Syntax only |
| `validate` | <50ms | <500ms | Syntax + semantics |
| `compile` | <100ms | <1000ms | Everything + output |

**File size reference**:
- Small: <100 events
- Large: 1000+ events

---

### Best Practices

**During editing**: Use `check` for instant feedback
```bash
# Fast enough for save hooks
mmdc check song.mmd  # <10ms
```

**Before commit**: Use `validate` for comprehensive checking
```bash
# Catches semantic errors
mmdc validate song.mmd  # <100ms
```

**Before performance**: Use `compile` to verify everything
```bash
# Full pipeline test
mmdc compile song.mmd  # <200ms
```

---

## Common Issues

### "Syntax is valid" but validation fails

**Problem**: File passes `check` but fails `validate`.

**Explanation**: `check` only verifies syntax, not semantics.

**Example**:
```yaml
# This passes check (valid syntax)
[00:01.000]
- cc 1.7.200  # But value > 127!

# Check says OK:
mmdc check song.mmd
# ✓ Syntax is valid

# Validate catches the error:
mmdc validate song.mmd
# ✗ MIDI value out of range: 200 exceeds maximum (127)
```

**Solution**: Always validate before important use:
```bash
mmdc check song.mmd     # Quick syntax check
mmdc validate song.mmd  # Full validation
```

---

### Parse error on valid-looking code

**Problem**: Code looks correct but check fails.

**Common causes**:
1. Invisible characters (copy-paste from web)
2. Wrong quote types (curly quotes instead of straight)
3. Mixed tabs/spaces in indentation
4. Hidden Unicode characters

**Debugging**:
```bash
# Show hidden characters
cat -A song.mmd

# Check file encoding
file song.mmd  # Should be "UTF-8 Unicode text"

# Fix encoding
iconv -f ISO-8859-1 -t UTF-8 song.mmd > song_fixed.mmd
```

---

### Check passes but compile fails

**Problem**: Syntax valid, validation passes, but compilation fails.

**Explanation**: Some errors only appear during expansion (loops, variables, sweeps).

**Solution**: Always test full compilation:
```bash
mmdc check song.mmd      # Syntax OK
mmdc validate song.mmd   # Validation OK
mmdc compile song.mmd    # May still have expansion errors
```

---

## Tips & Tricks

### Vim Integration

```vim
" .vimrc
" Quick syntax check on save
autocmd BufWritePost *.mmd :!mmdc check %
```

**Or with statusline**:
```vim
function! CheckMMLSyntax()
  let l:output = system('mmdc check ' . shellescape(expand('%')))
  if v:shell_error == 0
    echo "✓ Syntax OK"
  else
    echo "✗ Syntax error"
  endif
endfunction

nnoremap <leader>c :call CheckMMLSyntax()<CR>
```

---

### Emacs Integration

```elisp
;; .emacs or init.el
(defun mml-check-syntax ()
  "Check MMD file syntax"
  (interactive)
  (compile (concat "mmdc check " (buffer-file-name))))

(add-hook 'mml-mode-hook
  (lambda ()
    (local-set-key (kbd "C-c C-c") 'mml-check-syntax)))
```

---

### Shell Alias

```bash
# .bashrc or .zshrc
alias mmlc='mmdc check'

# Usage
mmlc song.mmd
```

---

### Makefile Integration

```makefile
.PHONY: check-syntax

check-syntax:
	@for file in *.mmd; do \
		echo "Checking $$file..."; \
		mmdc check "$$file" || exit 1; \
	done
	@echo "All files have valid syntax ✓"
```

**Usage**:
```bash
make check-syntax
```

---

### Pre-commit Hook (Lightweight)

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Quick syntax check only (fast enough for pre-commit)
git diff --cached --name-only --diff-filter=ACM | grep '\.mmd$' | \
  xargs -I {} mmdc check {}

if [ $? -ne 0 ]; then
  echo "Syntax errors found. Commit aborted."
  exit 1
fi
```

---

### CI/CD Fast Check

```yaml
# .github/workflows/syntax-check.yml
name: Fast Syntax Check

on: [push]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install mmdc
        run: pipx install mmdc
      - name: Check syntax
        run: find . -name "*.mmd" -exec mmdc check {} \;
```

**Note**: For production, add full validation:
```yaml
      - name: Full validation
        run: find . -name "*.mmd" -exec mmdc validate {} \;
```

---

### Parallel Checking

```bash
# Check all files in parallel (4 workers)
find . -name "*.mmd" | xargs -P 4 -I {} mmdc check {}

# With progress indicator
find . -name "*.mmd" | parallel --progress mmdc check {}
```

---

## Development Workflow

### Recommended 3-Stage Process

**Stage 1: Rapid Editing** (use `check`)
```bash
# Edit file...
# Save
mmdc check song.mmd  # <10ms - instant feedback

# Edit more...
# Save
mmdc check song.mmd  # <10ms
```

**Stage 2: Pre-Commit** (use `validate`)
```bash
# Before committing changes
mmdc validate song.mmd  # <100ms - full validation
```

**Stage 3: Pre-Performance** (use `compile`)
```bash
# Before live performance or recording
mmdc compile song.mmd  # <200ms - complete test
mmdc play song.mmd --port 0  # Test playback
```

---

### Watch Mode for Live Coding

```bash
# Terminal 1: Edit file in vim/emacs/nano
vim song.mmd

# Terminal 2: Auto-check on save
ls song.mmd | entr mmdc check /_
```

**Output refreshes on every save**:
```
Checking syntax: song.mmd
✓ Syntax is valid

# (Refreshes when you save)
```

---

## When to Use Each Command

### Use `check` when:
- ✅ Editing files (need instant feedback)
- ✅ Learning MMD syntax
- ✅ Testing parser changes (development)
- ✅ Batch syntax checking many files
- ✅ CI/CD first pass (fast)

### Use `validate` when:
- ✅ Before committing to version control
- ✅ CI/CD comprehensive check
- ✅ Need to verify MIDI values
- ✅ Checking timing order
- ✅ Verifying aliases/imports

### Use `compile` when:
- ✅ Before live performance
- ✅ Testing complete pipeline
- ✅ Need MIDI output
- ✅ Final verification
- ✅ Integration testing

---

## See Also

- [validate command](validate.md) - Full validation with semantic checks
- [compile command](compile.md) - Complete compilation with output
- [Troubleshooting Guide](../reference/troubleshooting.md) - Common parse errors
- [MML Syntax Reference](../user-guide/mmd-syntax.md) - Complete syntax guide
- [First Song Tutorial](../getting-started/first-song.md) - Learn MMD basics

---

**Next Steps**: Learn about [full validation](validate.md) or [compilation](compile.md).
