# Git Worktree Setup Summary

**Date**: 2025-11-15
**Status**: ✅ Complete and Ready

## What Was Configured

This setup enables Claude Code to work with git worktrees for parallel development across multiple feature branches.

## 1. Updated Configuration

### `.claude/settings.local.json`

Added the following auto-approved commands to the `permissions.allow` list:

**Git Worktree Operations**:
```json
"Bash(git worktree:*)",
"Bash(git checkout:*)",
"Bash(git switch:*)",
"Bash(git merge:*)",
"Bash(git rebase:*)",
"Bash(git pull:*)",
"Bash(git remote:*)",
"Bash(git add:*)",
"Bash(git commit:*)",
```

**Feature Branch Push** (auto-approved for `claude/*` branches):
```json
"Bash(git push -u origin claude/*)",
"Bash(git push origin claude/*)",
```

**GitHub CLI Operations**:
```json
"Bash(gh pr create:*)",
"Bash(gh pr view:*)",
"Bash(gh pr list:*)",
"Bash(gh pr status:*)",
"Bash(gh pr checks:*)",
"Bash(gh repo view:*)",
"Bash(gh auth status:*)",
"Bash(gh --version)",
```

## 2. Created Documentation

### `.claude/WORKTREE_WORKFLOW.md`
**Complete guide** covering:
- What git worktrees are and why use them
- Step-by-step workflow for creating and using worktrees
- Branch naming conventions
- Pull request creation with GitHub CLI
- Cleanup after merging
- Troubleshooting common issues
- Best practices
- FAQ

**Size**: ~800 lines with comprehensive examples

### `.claude/WORKTREE_QUICKREF.md`
**Quick reference card** with:
- Essential commands
- Common patterns
- Troubleshooting table
- Pre-PR checklist

**Size**: ~150 lines, designed for quick lookups

## 3. Created Helper Scripts

### `.claude/scripts/create-worktree.sh`
**Purpose**: Automate worktree creation

**Features**:
- Generates unique session IDs
- Creates properly named branches (`claude/<feature>-<sessionID>`)
- Creates worktree in sibling directory
- Provides next steps
- Shows current worktrees

**Usage**:
```bash
./.claude/scripts/create-worktree.sh add-feature-name
```

**Permissions**: Executable (`chmod +x`)

### `.claude/scripts/cleanup-worktrees.sh`
**Purpose**: Cleanup merged worktrees automatically

**Features**:
- Finds all `claude/*` branches
- Checks merge status against `origin/main`
- Removes merged worktrees and branches
- Dry run mode for safety
- Prunes stale references

**Usage**:
```bash
# Preview cleanup
./.claude/scripts/cleanup-worktrees.sh --dry-run

# Actually cleanup
./.claude/scripts/cleanup-worktrees.sh
```

**Permissions**: Executable (`chmod +x`)

### `.claude/scripts/README.md`
**Purpose**: Document the helper scripts

**Contents**:
- Detailed usage for each script
- Example outputs
- Troubleshooting
- Customization options
- Integration with workflow

## 4. Updated Summary Documentation

### `.claude/SUMMARY.md`
Added new section: "Parallel Development with Worktrees"

**Includes**:
- Quick start commands
- Benefits overview
- Links to full documentation

## How It Works

### Workflow Overview

```
┌─────────────────────────────────────────────┐
│  Main Repository                            │
│  /home/user/midi-markdown                   │
│  Branch: main                               │
└─────────────────────────────────────────────┘
                    │
                    │ create-worktree.sh
                    ↓
┌─────────────────────────────────────────────┐
│  Worktree 1                                 │
│  /home/user/midi-markdown-feature-a         │
│  Branch: claude/feature-a-01ABC123          │
│  ↳ Claude Code Instance 1                   │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  Worktree 2                                 │
│  /home/user/midi-markdown-feature-b         │
│  Branch: claude/feature-b-01DEF456          │
│  ↳ Claude Code Instance 2                   │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  Worktree 3                                 │
│  /home/user/midi-markdown-feature-c         │
│  Branch: claude/feature-c-01GHI789          │
│  ↳ Claude Code Instance 3                   │
└─────────────────────────────────────────────┘
                    │
                    │ git push + gh pr create
                    ↓
┌─────────────────────────────────────────────┐
│  GitHub Pull Requests                       │
│  - PR #123: Feature A                       │
│  - PR #124: Feature B                       │
│  - PR #125: Feature C                       │
└─────────────────────────────────────────────┘
                    │
                    │ After merge
                    ↓
┌─────────────────────────────────────────────┐
│  cleanup-worktrees.sh                       │
│  - Removes merged worktrees                 │
│  - Deletes local branches                   │
│  - Prunes stale references                  │
└─────────────────────────────────────────────┘
```

## Quick Start Guide

### Create Your First Worktree

```bash
# 1. Navigate to main repository
cd /home/user/midi-markdown

# 2. Create worktree using helper script
./.claude/scripts/create-worktree.sh add-new-feature

# 3. Navigate to worktree
cd ../midi-markdown-add-new-feature

# 4. Open Claude Code in this directory
# (Start your Claude Code session here)
```

### Develop in Worktree

Claude Code will now work in the isolated worktree. All git operations are auto-approved for `claude/*` branches:

```bash
# Claude Code can do these automatically:
git add src/new_feature.py
git commit -m "Add new feature"
git push -u origin claude/add-new-feature-sessionID
gh pr create --title "Add new feature" --body "Description..."
```

### After PR Is Merged

```bash
# Return to main repo
cd /home/user/midi-markdown

# Update main branch
git pull origin main

# Cleanup merged worktrees
./.claude/scripts/cleanup-worktrees.sh
```

## Benefits

### ✅ Parallel Development
- Work on multiple features simultaneously
- Each feature isolated in its own directory
- No conflicts between features

### ✅ Context Switching
- Switch between features by changing directories
- No need to stash or commit incomplete work
- Each worktree has independent state

### ✅ Automation
- Helper scripts automate common tasks
- Auto-approved git commands for `claude/*` branches
- GitHub CLI integration for easy PR creation

### ✅ Safety
- Cleanup script only removes merged branches
- Dry run mode to preview changes
- Maintains git history and integrity

## Requirements

### Prerequisites
1. **Git 2.5+** - For worktree support
2. **GitHub CLI (gh)** - For PR creation
   ```bash
   # Install on macOS
   brew install gh

   # Authenticate
   gh auth login
   ```
3. **Bash 4.0+** - For helper scripts

### Verification

```bash
# Check git version
git --version
# Should be 2.5 or higher

# Check GitHub CLI
gh --version
gh auth status

# Check worktree support
git worktree list
```

## Branch Naming Convention

**Format**: `claude/<feature-description>-<sessionID>`

**Examples**:
- ✅ `claude/add-looper-support-01ABC123`
- ✅ `claude/fix-timing-bug-01XYZ789`
- ✅ `claude/update-h90-library-01DEF456`

**Important**: The `claude/` prefix is **required** for auto-approved push commands.

## Integration with Existing Hooks

The worktree setup integrates seamlessly with existing Claude Code hooks:

### Auto-Format Hook
✅ Works in worktrees - Python files auto-formatted after Edit/Write

### Pre-Commit Hook
✅ Works in worktrees - All checks run before commit
- Format check
- Linting
- Type checking
- Smoke tests

### Shared Configuration
Worktrees share hooks and configuration from main repository:
- `.claude/settings.local.json`
- `.claude/hooks/`
- Git config

## File Structure

```
/home/user/midi-markdown/
├── .claude/
│   ├── settings.local.json        # ✅ Updated with permissions
│   ├── SUMMARY.md                 # ✅ Updated with worktree info
│   ├── WORKTREE_WORKFLOW.md       # ✅ New: Complete guide
│   ├── WORKTREE_QUICKREF.md       # ✅ New: Quick reference
│   ├── WORKTREE_SETUP_SUMMARY.md  # ✅ New: This file
│   └── scripts/
│       ├── README.md              # ✅ New: Scripts documentation
│       ├── create-worktree.sh     # ✅ New: Create worktree
│       └── cleanup-worktrees.sh   # ✅ New: Cleanup merged worktrees
│
├── /home/user/midi-markdown-feature-a/  # Example worktree 1
├── /home/user/midi-markdown-feature-b/  # Example worktree 2
└── /home/user/midi-markdown-feature-c/  # Example worktree 3
```

## Testing the Setup

### Test 1: Create a Worktree

```bash
cd /home/user/midi-markdown
./.claude/scripts/create-worktree.sh test-feature
cd ../midi-markdown-test-feature
git status
# Should show: On branch claude/test-feature-<sessionID>
```

### Test 2: Make a Commit

```bash
# In worktree
echo "# Test" > test.md
git add test.md
git commit -m "Test commit"
# Pre-commit hook should run
```

### Test 3: Push to Remote

```bash
# In worktree
git push -u origin $(git branch --show-current)
# Should succeed without asking permission (auto-approved)
```

### Test 4: Cleanup

```bash
# Return to main repo
cd /home/user/midi-markdown

# Dry run cleanup
./.claude/scripts/cleanup-worktrees.sh --dry-run

# Remove test worktree manually
git worktree remove ../midi-markdown-test-feature
git branch -D claude/test-feature-*
```

## Troubleshooting

### Issue: GitHub CLI Not Authenticated

```bash
gh auth status
# If not authenticated:
gh auth login
# Follow prompts
```

### Issue: Permission Denied on git push

**Cause**: Branch doesn't start with `claude/`

**Solution**: Ensure branch name follows convention:
```bash
git branch -m claude/feature-name-sessionID
```

### Issue: Worktree Creation Fails

**Cause**: Directory already exists

**Solution**:
```bash
rm -rf ../midi-markdown-feature-name
./.claude/scripts/create-worktree.sh feature-name
```

## Next Steps

### For Users

1. ✅ **Setup Complete** - All configurations in place
2. **Install GitHub CLI** - If not already installed
   ```bash
   brew install gh  # macOS
   gh auth login
   ```
3. **Test the workflow** - Create a test worktree
4. **Read the docs** - Review [WORKTREE_WORKFLOW.md](.claude/WORKTREE_WORKFLOW.md)

### For Development

1. Start using worktrees for new features
2. Create PRs using `gh pr create`
3. Cleanup merged worktrees regularly
4. Share feedback and improvements

## Additional Resources

- **[WORKTREE_WORKFLOW.md](.claude/WORKTREE_WORKFLOW.md)** - Complete workflow guide
- **[WORKTREE_QUICKREF.md](.claude/WORKTREE_QUICKREF.md)** - Quick reference
- **[scripts/README.md](.claude/scripts/README.md)** - Scripts documentation
- **[Git Worktree Docs](https://git-scm.com/docs/git-worktree)** - Official documentation
- **[GitHub CLI Manual](https://cli.github.com/manual/)** - gh command reference

## Success Criteria

All requirements met ✅:

- [x] `.claude/settings.local.json` updated with permissions
- [x] Git worktree commands auto-approved
- [x] Git push to `claude/*` branches auto-approved
- [x] GitHub CLI commands auto-approved
- [x] Helper script for creating worktrees
- [x] Helper script for cleanup
- [x] Comprehensive documentation
- [x] Quick reference guide
- [x] Integration with existing hooks
- [x] Scripts are executable
- [x] Examples and troubleshooting

---

**Status**: ✅ **READY FOR USE**

Claude Code can now use git worktrees for parallel development with automatic PR creation via GitHub CLI.

**Last Updated**: 2025-11-15
