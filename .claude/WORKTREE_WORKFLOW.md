# Git Worktree Workflow for Claude Code

This guide explains how to use git worktrees with Claude Code to work on multiple features simultaneously with different Claude Code instances.

## Overview

Git worktrees allow you to have multiple working directories from a single repository, enabling you to:
- Work on multiple features in parallel with different Claude Code instances
- Switch contexts quickly without stashing or committing incomplete work
- Keep each feature isolated in its own directory

## Prerequisites

1. **GitHub CLI (gh)**: Required for creating pull requests
   ```bash
   # Install on macOS
   brew install gh

   # Install on Linux
   sudo apt install gh  # Debian/Ubuntu

   # Authenticate
   gh auth login
   ```

2. **Verify Configuration**: Ensure `.claude/settings.local.json` has the necessary permissions (already configured)

## Quick Start

### 1. Create a New Worktree for a Feature

```bash
# From the main repository directory
cd /home/user/midi-markdown

# Create a new worktree in a sibling directory
git worktree add ../midi-markdown-feature-name -b claude/feature-name-sessionID

# Example:
git worktree add ../midi-markdown-add-looper -b claude/add-looper-01XYZ123
```

### 2. Open Claude Code in the Worktree

```bash
# Navigate to the worktree directory
cd ../midi-markdown-add-looper

# Start Claude Code in this directory
claude-code
# Or if using VS Code with Claude extension
code .
```

### 3. Work on Your Feature

Claude Code will now work in the isolated worktree. All changes are independent of other worktrees.

### 4. Create a Pull Request

When ready, Claude Code can create a PR using GitHub CLI:

```bash
# Add and commit changes
git add .
git commit -m "Add looper functionality"

# Push to remote
git push -u origin claude/add-looper-01XYZ123

# Create pull request
gh pr create --title "Add looper functionality" --body "$(cat <<'EOF'
## Summary
- Implemented looper MIDI commands
- Added tests for looper functionality
- Updated documentation

## Test plan
- [x] Unit tests pass
- [x] Integration tests pass
- [x] Manual testing with hardware looper
EOF
)"
```

## Workflow Patterns

### Pattern 1: Multiple Features in Parallel

```bash
# Main repo (for reference and code review)
/home/user/midi-markdown

# Feature 1: Add looper support
/home/user/midi-markdown-add-looper
  └── Branch: claude/add-looper-01ABC

# Feature 2: Fix timing calculation bug
/home/user/midi-markdown-fix-timing
  └── Branch: claude/fix-timing-bug-01DEF

# Feature 3: Add new device library
/home/user/midi-markdown-add-h90-library
  └── Branch: claude/add-h90-library-01GHI
```

### Pattern 2: Branch Naming Convention

**Format**: `claude/<feature-description>-<sessionID>`

Examples:
- `claude/add-looper-support-01T6HrDpTLfH3pJiLmWpv36h`
- `claude/fix-timing-validation-01XYZ789ABC123`
- `claude/update-docs-architecture-01ABC456DEF789`

**Important**: The `claude/` prefix is required for auto-approval of git push commands.

### Pattern 3: Cleanup After Merge

```bash
# After PR is merged, clean up the worktree
cd /home/user/midi-markdown  # Return to main repo
git worktree remove ../midi-markdown-feature-name
git branch -d claude/feature-name-sessionID  # Delete local branch

# Or force removal if needed
git worktree remove --force ../midi-markdown-feature-name
```

## Claude Code Automation

### Auto-approved Commands

The following git and GitHub CLI commands are auto-approved in `.claude/settings.local.json`:

**Git Operations**:
- `git worktree add/list/remove`
- `git checkout/switch`
- `git add/commit`
- `git push -u origin claude/*` (feature branches only)
- `git pull/fetch/merge/rebase`
- `git status/diff/log/show/branch`

**GitHub CLI**:
- `gh pr create/view/list/status/checks`
- `gh repo view`
- `gh auth status`

### Commands Requiring Approval

These commands require user confirmation:
- `git push` (to non-claude/* branches)
- `rm -rf` (destructive operations)
- `sudo` commands
- Release commands (`just release-*`)

## Example Session

### Full End-to-End Example

```bash
# 1. Create worktree
cd /home/user/midi-markdown
git worktree add ../midi-markdown-add-waveforms -b claude/add-waveforms-01ABC123

# 2. Start Claude Code in worktree
cd ../midi-markdown-add-waveforms
# (Open Claude Code here)

# 3. Claude Code implements the feature
# (Makes edits, runs tests, etc.)

# 4. Claude Code commits changes
git add src/midi_markdown/utils/waveforms.py tests/unit/test_waveforms.py
git commit -m "Add waveform generation utilities"

# 5. Claude Code pushes to remote
git push -u origin claude/add-waveforms-01ABC123

# 6. Claude Code creates PR
gh pr create --title "Add waveform generation utilities" \
  --body "Implements sine, triangle, sawtooth, and square wave generators for LFO modulation"

# 7. After PR is merged
cd /home/user/midi-markdown
git pull origin main
git worktree remove ../midi-markdown-add-waveforms
git branch -d claude/add-waveforms-01ABC123
```

## Managing Multiple Worktrees

### List All Worktrees

```bash
git worktree list
```

Output example:
```
/home/user/midi-markdown              74cc8fd [main]
/home/user/midi-markdown-add-looper   a1b2c3d [claude/add-looper-01ABC]
/home/user/midi-markdown-fix-timing   e4f5g6h [claude/fix-timing-01DEF]
```

### Check Worktree Status

```bash
# From any worktree or main repo
git worktree list --porcelain
```

### Prune Stale Worktrees

```bash
# Remove worktree references for deleted directories
git worktree prune
```

## Troubleshooting

### Issue: "Branch already exists"

```bash
# If branch exists but worktree doesn't
git worktree add ../midi-markdown-feature -b claude/feature-name

# Error: branch 'claude/feature-name' already exists

# Solution: Use existing branch or delete it first
git branch -d claude/feature-name  # Safe delete (if merged)
git branch -D claude/feature-name  # Force delete (if not merged)

# Then create worktree
git worktree add ../midi-markdown-feature -b claude/feature-name
```

### Issue: "Directory not empty"

```bash
# Error: destination path '...' already exists and is not an empty directory

# Solution: Remove directory first
rm -rf ../midi-markdown-feature
git worktree add ../midi-markdown-feature -b claude/feature-name
```

### Issue: GitHub CLI not authenticated

```bash
# Check authentication
gh auth status

# If not authenticated
gh auth login
# Follow prompts to authenticate
```

### Issue: Worktree locked

```bash
# If worktree is locked (after crash or force kill)
git worktree unlock ../midi-markdown-feature

# Or remove and recreate
git worktree remove --force ../midi-markdown-feature
git worktree add ../midi-markdown-feature -b claude/feature-name
```

## Best Practices

### 1. Naming Consistency

✅ **Good**: `claude/add-looper-support-01ABC123`
❌ **Bad**: `feature/looper` or `my-branch`

### 2. One Feature Per Worktree

Each worktree should focus on a single, well-defined feature or bugfix.

### 3. Regular Cleanup

Remove worktrees after PRs are merged to avoid clutter:

```bash
# Weekly cleanup routine
git worktree list  # Review active worktrees
git worktree prune  # Remove stale references
```

### 4. Sync with Main Branch

Before creating a PR, ensure your branch is up-to-date:

```bash
# In worktree directory
git fetch origin
git rebase origin/main

# Or merge if you prefer
git merge origin/main
```

### 5. Test Before PR

Always run the full test suite before creating a PR:

```bash
# In worktree directory
just qa  # Runs format, lint, typecheck, and tests
```

## Integration with GitHub Actions

All PRs created from `claude/*` branches will trigger GitHub Actions CI:

1. **Format Check** (ruff format --check)
2. **Lint** (ruff check)
3. **Type Check** (mypy)
4. **Tests** (pytest with coverage)

PRs can only be merged if all checks pass.

## Advanced: Worktree Hooks

The pre-commit hooks in `.claude/hooks/pre-commit.sh` work seamlessly with worktrees. Each worktree shares the same hooks from the main repository.

## FAQ

**Q: Can I have multiple Claude Code instances running in different worktrees?**
A: Yes! That's the primary use case. Each instance operates independently.

**Q: Do worktrees share the git configuration?**
A: Yes, they share `.git/config`, hooks, and refs, but have independent working directories.

**Q: What happens to my worktree if I delete the main repository?**
A: Worktrees depend on the main repository. Don't delete the main `.git` directory.

**Q: Can I create a worktree from a worktree?**
A: No, worktrees must be created from the main repository directory.

**Q: How do I switch between worktrees?**
A: Simply `cd` to the worktree directory. Each is a fully independent working directory.

## See Also

- [Git Worktree Documentation](https://git-scm.com/docs/git-worktree)
- [GitHub CLI Documentation](https://cli.github.com/manual/)
- [Claude Code Settings Documentation](.claude/SUMMARY.md)
- [Contributing Guide](../docs/developer-guide/contributing.md)

---

**Last Updated**: 2025-11-15
**Maintained by**: Claude Code automation setup
