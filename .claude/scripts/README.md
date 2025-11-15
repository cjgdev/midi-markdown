# Claude Code Helper Scripts

Automation scripts for git worktree management and development workflow.

## Scripts

### create-worktree.sh

**Purpose**: Create a new git worktree for parallel feature development

**Usage**:
```bash
./.claude/scripts/create-worktree.sh <feature-name>
```

**Example**:
```bash
./.claude/scripts/create-worktree.sh add-looper-support
```

**What it does**:
1. Generates a unique session ID
2. Creates branch: `claude/<feature-name>-<sessionID>`
3. Creates worktree in: `../midi-markdown-<feature-name>/`
4. Displays next steps

**Output**:
```
Creating worktree for feature: add-looper-support

  Branch: claude/add-looper-support-Tm90IGEgbWFsaWNpb3Vz
  Directory: /home/user/midi-markdown-add-looper-support

✓ Worktree created successfully!

Next steps:
  1. cd /home/user/midi-markdown-add-looper-support
  2. Start Claude Code
  3. Push: git push -u origin claude/add-looper-support-...
  4. Create PR: gh pr create --title "..." --body "..."
```

---

### cleanup-worktrees.sh

**Purpose**: Cleanup merged worktrees and their branches

**Usage**:
```bash
# Dry run (preview what would be cleaned)
./.claude/scripts/cleanup-worktrees.sh --dry-run

# Actually cleanup
./.claude/scripts/cleanup-worktrees.sh
```

**What it does**:
1. Finds all worktrees with `claude/*` branches
2. Checks if branches are merged into `origin/main`
3. Removes merged worktrees and deletes their local branches
4. Prunes stale worktree references

**Safety**:
- Only processes `claude/*` branches
- Only removes if merged into main
- Dry run mode available
- Skips unmerged branches

**Output**:
```
Checking for worktrees to cleanup...

Found worktrees:
  /home/user/midi-markdown                     74cc8fd [main]
  /home/user/midi-markdown-add-looper         a1b2c3d [claude/add-looper-01ABC]

Fetching latest changes from origin...

✓ Branch claude/add-looper-01ABC is merged
  Worktree: /home/user/midi-markdown-add-looper
  Removing worktree...
  ✓ Worktree removed
  Deleting local branch...
  ✓ Branch deleted

Cleanup Summary:
  Cleaned: 1
  Skipped: 0
```

---

## Workflow Integration

These scripts integrate with the git worktree workflow documented in:
- [.claude/WORKTREE_WORKFLOW.md](../WORKTREE_WORKFLOW.md) - Complete guide
- [.claude/WORKTREE_QUICKREF.md](../WORKTREE_QUICKREF.md) - Quick reference

## Prerequisites

Both scripts require:
- Git 2.5+ (for worktree support)
- Bash 4.0+
- Being run from within the git repository

The cleanup script additionally requires:
- Network access to fetch from origin
- Write permissions to remove worktrees

## Common Usage Patterns

### Daily Development

```bash
# Morning: Create worktree for new feature
./.claude/scripts/create-worktree.sh implement-feature-x
cd ../midi-markdown-implement-feature-x
# Work on feature...

# Evening: After PR is merged
cd /home/user/midi-markdown
git pull origin main
./.claude/scripts/cleanup-worktrees.sh
```

### Weekly Cleanup

```bash
# Check what would be cleaned
./.claude/scripts/cleanup-worktrees.sh --dry-run

# If looks good, cleanup
./.claude/scripts/cleanup-worktrees.sh
```

### Multiple Parallel Features

```bash
# Create multiple worktrees for different features
./.claude/scripts/create-worktree.sh add-feature-a
./.claude/scripts/create-worktree.sh fix-bug-b
./.claude/scripts/create-worktree.sh update-docs-c

# Work in each independently
# Cleanup as PRs are merged
```

## Troubleshooting

### create-worktree.sh Issues

**Error: Directory already exists**
```bash
# Remove existing directory
rm -rf ../midi-markdown-feature-name
# Try again
./.claude/scripts/create-worktree.sh feature-name
```

**Error: Branch already exists**
```bash
# Delete existing branch (if safe)
git branch -d claude/feature-name-sessionID
# Try again with different feature name
```

### cleanup-worktrees.sh Issues

**Branch not detected as merged**
```bash
# Verify merge status manually
git branch --merged origin/main | grep claude/branch-name

# If merged but not detected, force cleanup
git worktree remove ../midi-markdown-feature
git branch -D claude/branch-name-sessionID
```

**Worktree locked**
```bash
# Unlock worktree
git worktree unlock ../midi-markdown-feature
# Then cleanup
./.claude/scripts/cleanup-worktrees.sh
```

## Customization

### Change Worktree Location

Edit `create-worktree.sh` line 32:
```bash
# Default (sibling directory):
WORKTREE_DIR="${REPO_ROOT}/../${REPO_NAME}-${FEATURE_NAME}"

# Alternative (subdirectory):
WORKTREE_DIR="${REPO_ROOT}/worktrees/${FEATURE_NAME}"

# Alternative (fixed location):
WORKTREE_DIR="${HOME}/worktrees/midi-markdown-${FEATURE_NAME}"
```

### Change Branch Prefix

Edit `create-worktree.sh` line 26:
```bash
# Default:
BRANCH_NAME="claude/${FEATURE_NAME}-${SESSION_ID}"

# Alternative (your initials):
BRANCH_NAME="jd/${FEATURE_NAME}-${SESSION_ID}"
```

**Note**: If you change the prefix, update `.claude/settings.local.json` permissions:
```json
"Bash(git push -u origin your-prefix/*)",
"Bash(git push origin your-prefix/*)",
```

## See Also

- [Git Worktree Documentation](https://git-scm.com/docs/git-worktree)
- [GitHub CLI Documentation](https://cli.github.com/manual/)
- [WORKTREE_WORKFLOW.md](../WORKTREE_WORKFLOW.md)
- [WORKTREE_QUICKREF.md](../WORKTREE_QUICKREF.md)

---

**Maintained by**: MIDI Markdown project
**Last Updated**: 2025-11-15
