# Claude Code Hooks for MIDI Markdown

This directory contains hook scripts that help ensure code quality and prevent CI failures when Claude contributes changes.

## Available Hooks

### 1. `post-edit.sh` - Auto-format after edits
**When it runs**: After Claude edits any Python file
**What it does**:
- Automatically formats Python files with `ruff format`
- Ensures consistent code style

**Configuration**:
```json
{
  "hooks": {
    "post-edit": ".claude/hooks/post-edit.sh {file}"
  }
}
```

### 2. `pre-commit.sh` - Quality gate before commits
**When it runs**: Before creating git commits
**What it does**:
- ✅ Checks code formatting (`ruff format --check`)
- ✅ Runs linter (`ruff check src tests`)
- ✅ Runs type checker (`mypy src`)
- ✅ Runs smoke tests (parser + CLI)

This ensures **all GitHub Actions checks will pass**.

**Configuration**:
```json
{
  "hooks": {
    "pre-commit": ".claude/hooks/pre-commit.sh"
  }
}
```

### 3. `quick-check.sh` - Fast validation after changes
**When it runs**: After writing files (alternative to post-edit)
**What it does**:
- Formats the file
- Lints the file with auto-fix
- Fast feedback (file-level, not project-level)

**Configuration**:
```json
{
  "hooks": {
    "post-write": ".claude/hooks/quick-check.sh {file}"
  }
}
```

## Recommended Configuration

### Option A: Maximum Safety (Recommended for CI)
Add to `.claude/settings.local.json`:

```json
{
  "hooks": {
    "post-edit": ".claude/hooks/post-edit.sh {file}",
    "pre-commit": ".claude/hooks/pre-commit.sh"
  },
  "permissions": {
    // ... existing permissions
  }
}
```

**Benefits**:
- ✅ Code always formatted correctly
- ✅ Commits always pass CI checks
- ✅ Early detection of type errors
- ⚠️  Slower (runs full test suite before commits)

### Option B: Fast Development
Add to `.claude/settings.local.json`:

```json
{
  "hooks": {
    "post-write": ".claude/hooks/quick-check.sh {file}"
  },
  "permissions": {
    // ... existing permissions
  }
}
```

**Benefits**:
- ✅ Fast feedback
- ✅ Auto-formatting and auto-fix
- ⚠️  Less comprehensive (no type checking or tests)

### Option C: Hybrid (Best Balance)
Add to `.claude/settings.local.json`:

```json
{
  "hooks": {
    "post-edit": ".claude/hooks/post-edit.sh {file}",
    "pre-commit": ".claude/hooks/pre-commit.sh"
  },
  "permissions": {
    // ... existing permissions
  }
}
```

**Benefits**:
- ✅ Immediate formatting after edits
- ✅ Comprehensive checks before commits
- ✅ Best of both worlds

## GitHub Actions Equivalence

The `pre-commit.sh` hook runs the **exact same checks** as GitHub Actions:

| GitHub Actions | Pre-commit Hook | Just Command |
|----------------|-----------------|--------------|
| `uv run ruff check src tests` | Step 2/4 | `just lint` |
| `uv run mypy src` | Step 3/4 | `just typecheck` |
| `uv run pytest tests/` | Step 4/4 (smoke) | `just test` |
| `uv run ruff format --check` | Step 1/4 | `just fmt-check` |

## Manual Testing

You can run the hooks manually to test them:

```bash
# Test post-edit hook
./.claude/hooks/post-edit.sh src/midi_markdown/parser/parser.py

# Test pre-commit hook (comprehensive)
./.claude/hooks/pre-commit.sh

# Test quick-check hook
./.claude/hooks/quick-check.sh src/midi_markdown/core/compiler.py
```

## Troubleshooting

### Hook fails with "permission denied"
```bash
chmod +x .claude/hooks/*.sh
```

### Hook fails with "uv: command not found"
Ensure `uv` is installed and in your PATH:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Pre-commit hook is too slow
Use Option B (quick-check only) or run manually:
```bash
# Before committing, run manually:
just check && just smoke
```

### Want to skip pre-commit hook once
Set environment variable:
```bash
SKIP_HOOKS=1 git commit -m "message"
```

Then update `pre-commit.sh` to check for this variable:
```bash
if [[ "$SKIP_HOOKS" == "1" ]]; then
    echo "⚠️  Skipping pre-commit checks (SKIP_HOOKS=1)"
    exit 0
fi
```

## Integration with Just

All hooks use the same commands as `justfile` recipes:

| Hook Check | Just Recipe | Description |
|------------|-------------|-------------|
| `ruff format --check` | `just fmt-check` | Format check |
| `ruff format` | `just fmt` | Auto-format |
| `ruff check` | `just lint` | Linting |
| `ruff check --fix` | `just lint-fix` | Auto-fix lint |
| `mypy src` | `just typecheck` | Type checking |
| `pytest tests/unit/...` | `just smoke` | Smoke tests |
| All of above | `just check` | All checks |

## Customization

### Adding Coverage Check
Edit `pre-commit.sh`, replace the test step with:
```bash
if ! uv run pytest tests/ --cov=midi_markdown --cov-fail-under=72; then
    echo "❌ Tests or coverage failed!"
    exit 1
fi
```

### Adding Example Validation
Add to `pre-commit.sh`:
```bash
echo "📚 Step 5/5: Validating examples..."
if ! just validate-examples; then
    echo "❌ Example validation failed!"
    exit 1
fi
```

### Running Full Test Suite
Replace smoke tests with:
```bash
if ! uv run pytest tests/ -v; then
    echo "❌ Full test suite failed!"
    exit 1
fi
```

## See Also

- [CLAUDE.md](../../CLAUDE.md) - Claude Code project instructions
- [justfile](../../justfile) - Development task runner
- [.github/workflows/test.yml](../../.github/workflows/test.yml) - CI configuration
- [docs/dev-guides/anti-patterns.md](../../docs/dev-guides/anti-patterns.md) - Common mistakes to avoid
