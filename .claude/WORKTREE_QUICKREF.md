# Git Worktree Quick Reference

**One-page cheat sheet for using worktrees with Claude Code**

## Create New Worktree

```bash
# Using helper script (recommended)
./.claude/scripts/create-worktree.sh add-feature-name

# Manual creation
git worktree add ../midi-markdown-feature-name -b claude/feature-name-sessionID
```

## Work in Worktree

```bash
# Navigate to worktree
cd ../midi-markdown-feature-name

# Start Claude Code here
# Make changes, run tests, etc.
```

## Commit and Push

```bash
# Add and commit
git add .
git commit -m "Add feature description"

# Push (auto-approved for claude/* branches)
git push -u origin claude/feature-name-sessionID
```

## Create Pull Request

```bash
# Simple PR
gh pr create --title "Feature title" --body "Feature description"

# PR with detailed body
gh pr create --title "Add looper support" --body "$(cat <<'EOF'
## Summary
- Implemented looper MIDI commands
- Added comprehensive tests
- Updated documentation

## Test plan
- [x] Unit tests pass
- [x] Integration tests pass
- [x] Manual testing complete
EOF
)"
```

## Cleanup After Merge

```bash
# Return to main repo
cd /home/user/midi-markdown

# Update main branch
git pull origin main

# Remove worktree
git worktree remove ../midi-markdown-feature-name

# Delete local branch
git branch -d claude/feature-name-sessionID
```

## Useful Commands

```bash
# List all worktrees
git worktree list

# Check PR status
gh pr status

# View worktree details
git worktree list --porcelain

# Prune stale worktree references
git worktree prune
```

## Branch Naming Convention

**Format**: `claude/<description>-<sessionID>`

**Examples**:
- `claude/add-looper-01ABC123`
- `claude/fix-timing-bug-01XYZ789`
- `claude/update-docs-01DEF456`

**Important**: Must start with `claude/` for auto-approved push

## Parallel Development Example

```bash
# Main repo
/home/user/midi-markdown [main]

# Feature 1
/home/user/midi-markdown-add-looper [claude/add-looper-01ABC]

# Feature 2
/home/user/midi-markdown-fix-bug [claude/fix-bug-01DEF]

# Feature 3
/home/user/midi-markdown-update-docs [claude/update-docs-01GHI]
```

## Common Issues

| Issue | Solution |
|-------|----------|
| Branch exists | `git branch -d claude/branch-name` |
| Directory not empty | `rm -rf ../directory` |
| Worktree locked | `git worktree unlock ../directory` |
| GH CLI not auth'd | `gh auth login` |

## Pre-PR Checklist

- [ ] All tests pass (`just qa`)
- [ ] Code formatted (`just fmt`)
- [ ] Branch up-to-date with main
- [ ] Commit messages are clear
- [ ] PR title and description are descriptive

## See Full Documentation

[.claude/WORKTREE_WORKFLOW.md](.claude/WORKTREE_WORKFLOW.md)
