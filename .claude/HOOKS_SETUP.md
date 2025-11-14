# Claude Code Hooks Setup Guide

## Overview

This project has configured Claude Code hooks to ensure all GitHub Actions CI checks pass automatically. The hooks provide immediate feedback and prevent broken commits.

## Configured Hooks

### 1. Post-Edit Auto-Format (PostToolUse → Edit)
**Trigger**: After Claude edits a Python file
**Action**: Runs `uv run ruff format <file>`
**Purpose**: Ensures all Python code is properly formatted immediately after editing

### 2. Post-Write Auto-Format (PostToolUse → Write)
**Trigger**: After Claude writes a new Python file
**Action**: Runs `uv run ruff format <file>`
**Purpose**: Ensures new Python files follow project formatting standards

### 3. Pre-Commit Quality Gate (PreToolUse → Bash git commit)
**Trigger**: Before executing `git commit` commands
**Action**: Runs `.claude/hooks/pre-commit.sh`
**Purpose**: Prevents commits that would fail CI

The pre-commit hook runs:
1. ✅ Format check (`ruff format --check`)
2. ✅ Linting (`ruff check src tests`)
3. ✅ Type checking (`mypy src`)
4. ✅ Smoke tests (parser + CLI tests)

## How It Works

### Auto-Formatting Flow
```
Claude edits file.py
    ↓
PostToolUse hook triggers
    ↓
ruff format file.py runs automatically
    ↓
File is now properly formatted
```

### Pre-Commit Flow
```
Claude runs: git commit -m "message"
    ↓
PreToolUse hook intercepts
    ↓
.claude/hooks/pre-commit.sh executes
    ↓
All checks pass? → Commit proceeds
Any check fails? → Commit blocked with error message
```

## Alignment with GitHub Actions

The hooks mirror the exact checks run in `.github/workflows/test.yml`:

| GitHub Actions Check | Local Hook | Time |
|---------------------|------------|------|
| `uv run ruff check src tests` | pre-commit.sh step 2/4 | ~3s |
| `uv run mypy src` | pre-commit.sh step 3/4 | ~5s |
| `uv run pytest tests/` | pre-commit.sh step 4/4 (smoke) | ~10s |

**Total pre-commit time**: ~18 seconds (vs 3-5 minutes in GitHub Actions)

## Testing the Hooks

### Test Auto-Format Hook
```bash
# Make a poorly formatted file
cat > /tmp/test.py << 'EOF'
def    badly_formatted(  x,y  ):
    return x+y
EOF

# Simulate Claude editing it
uv run python -c "
from pathlib import Path
content = Path('/tmp/test.py').read_text()
# Hook would run here automatically
"

# Manually test the hook command
uv run ruff format /tmp/test.py
cat /tmp/test.py  # Should be nicely formatted
```

### Test Pre-Commit Hook
```bash
# Run the hook manually
./.claude/hooks/pre-commit.sh

# Expected output:
# 🔍 Running pre-commit quality checks...
#
# 📝 Step 1/4: Checking code formatting...
# ✅ Formatting OK
#
# 🔎 Step 2/4: Running linter...
# ✅ Linting OK
#
# 🔬 Step 3/4: Running type checker...
# ✅ Type checking OK
#
# 🧪 Step 4/4: Running smoke tests...
# ✅ Tests OK
#
# ✅ All pre-commit checks passed! Ready to commit.
```

## Customization

### Disable Hooks Temporarily
Set environment variable before commands:
```bash
# Not currently supported in hooks config, but can modify scripts
```

### Modify Pre-Commit Checks
Edit `.claude/hooks/pre-commit.sh` to:
- Add more tests: Change `tests/unit/test_parser.py` to `tests/`
- Add coverage requirement: Add `--cov --cov-fail-under=72`
- Add example validation: Add `just validate-examples`

### Change Formatting Style
Hooks use `ruff format` which reads configuration from `pyproject.toml`.
To change formatting, edit `pyproject.toml`:
```toml
[tool.ruff.format]
quote-style = "double"  # or "single"
line-length = 100       # or any value
```

## Troubleshooting

### Hook Not Running
1. Check `.claude/settings.local.json` has `hooks` section
2. Verify hook scripts are executable: `chmod +x .claude/hooks/*.sh`
3. Check Claude Code version supports hooks

### Hook Fails
View full error output:
```bash
# Run hook manually to see detailed errors
./.claude/hooks/pre-commit.sh
```

Common failures:
- **Linting errors**: Run `just lint-fix` to auto-fix
- **Type errors**: Fix type annotations manually
- **Test failures**: Run `just test-unit -v` to see details

### Hook Too Slow
Options to speed up:
1. Replace full smoke tests with just parser tests
2. Skip type checking (not recommended)
3. Use quick-check.sh instead of pre-commit.sh

## Benefits

### For Claude
- ✅ No need to manually run `just fmt` after edits
- ✅ Immediate feedback on code quality
- ✅ Prevents creating commits that fail CI
- ✅ Confidence that changes will pass GitHub Actions

### For Developers
- ✅ Consistent code quality from Claude contributions
- ✅ Fewer failed CI builds
- ✅ Less time reviewing Claude PRs
- ✅ Automated enforcement of project standards

## Alternative Configurations

### Minimal (Fast, Less Safe)
Remove pre-commit hook, keep only auto-formatting:
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit",
        "hooks": [{"type": "command", "command": "if [[ \"$TOOL_ARGS\" == *\".py\"* ]]; then uv run ruff format \"$(echo \"$TOOL_ARGS\" | grep -oP 'file_path[^,}]+'  | cut -d'\"' -f4)\"; fi"}]
      }
    ]
  }
}
```

### Maximum (Slow, Very Safe)
Add full test suite to pre-commit:
```bash
# Edit .claude/hooks/pre-commit.sh, replace step 4 with:
echo "🧪 Step 4/4: Running full test suite..."
if ! uv run pytest tests/ -v --cov=midi_markdown --cov-fail-under=72; then
    echo "❌ Tests failed or coverage below 72%!"
    exit 1
fi
```

### Custom Hook Events
Add hooks for other events:
```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Review the user's request and ensure it follows project coding standards from CLAUDE.md"
          }
        ]
      }
    ],
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "echo '🚀 Starting Claude session. Remember to run tests!' && git status --short"
          }
        ]
      }
    ]
  }
}
```

## See Also

- [.claude/hooks/README.md](.claude/hooks/README.md) - Detailed hook documentation
- [.claude/hooks/pre-commit.sh](.claude/hooks/pre-commit.sh) - Pre-commit script
- [.github/workflows/test.yml](../.github/workflows/test.yml) - GitHub Actions CI config
- [CLAUDE.md](../CLAUDE.md) - Project instructions for Claude
- [justfile](../justfile) - Development task runner

## Quick Reference

| Want to... | Command |
|-----------|---------|
| Test pre-commit hook | `./.claude/hooks/pre-commit.sh` |
| Format all code | `just fmt` |
| Run all checks | `just check` |
| Run smoke tests | `just smoke` |
| Run full tests | `just test` |
| Skip a hook | Edit hook script to add condition |
| Disable all hooks | Set `"disableAllHooks": true` in settings |
