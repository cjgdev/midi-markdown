# PR Template Automation - Setup Complete ✅

This document summarizes the PR template automation setup for the MIDI Markdown project.

## Overview

Pull requests can now be created with **automatically filled templates** that include:
- Auto-detected change types
- List of commits and file changes
- Smart checkbox marking based on changed files
- Pre-filled sections for tests, documentation, and code quality

## What Was Created

### 1. Scripts

**`.github/scripts/fill-pr-template.sh`**
- Auto-fills the PR template based on git changes
- Detects change types from branch names and file patterns
- Lists commits, changed files, and statistics
- Marks checkboxes automatically

**`.github/scripts/create-pr-with-template.sh`**
- Interactive wrapper for PR creation
- Options to edit template before creating
- Auto mode for quick PR creation
- Integrated with gh CLI

### 2. Justfile Recipes

Added to `justfile`:
```just
# Create PR with filled template (interactive)
just pr [TITLE]

# Create PR automatically (no prompts)
just pr-auto [TITLE]

# Generate template to file
just pr-template [OUTPUT]

# Preview template content
just pr-preview
```

### 3. Claude Code Integration

**Slash Command**: `/create-pr`
- Location: `.claude/commands/create-pr.md`
- Guides Claude through PR creation with filled template
- Interactive workflow with user confirmation

### 4. Documentation

**`.github/README.md`**
- Complete guide to GitHub automation
- Workflow recommendations
- Troubleshooting section

**`.github/scripts/README.md`**
- Detailed script usage
- Examples and tips
- Auto-detection feature list

**`.github/PR_AUTOMATION_SETUP.md`** (this file)
- Setup summary
- Quick reference

## Usage

### Method 1: Justfile (Recommended)

```bash
# Interactive mode - review before creating
just pr

# With custom title
just pr "feat: Add awesome feature"

# Auto mode (no interaction)
just pr-auto "fix: Quick bug fix"

# Just preview the template
just pr-preview
```

### Method 2: Direct Script

```bash
# Interactive
.github/scripts/create-pr-with-template.sh

# With title
.github/scripts/create-pr-with-template.sh "feat: New feature"

# Auto mode
.github/scripts/create-pr-with-template.sh "fix: Bug fix" --auto
```

### Method 3: Claude Code

```
/create-pr
```

### Method 4: Manual

```bash
# Generate template
.github/scripts/fill-pr-template.sh > pr-body.md

# Edit as needed
$EDITOR pr-body.md

# Create PR
gh pr create --title "Your Title" --body-file pr-body.md
```

## Auto-Detection Features

### Branch Name Patterns

The scripts detect change types from branch names:

| Branch Pattern | Detected Type |
|----------------|---------------|
| `feature/*` or `feat/*` | New feature |
| `fix/*` | Bug fix |
| `docs/*` | Documentation |
| `refactor/*` | Code refactoring |
| `perf/*` | Performance improvement |
| `test/*` | Test improvements |
| `chore/*` | Build/tooling changes |

**Example**: Branch `feature/add-loops` → PR title "Feature: Add Loops"

### File Change Detection

Automatically marks checkboxes based on changed files:

| File Pattern | Checkbox Marked |
|--------------|-----------------|
| `docs/*` | Documentation update |
| `tests/*` | Test improvements |
| `tests/integration/*` | Integration tests |
| `tests/e2e/*` | E2E tests |
| `.github/workflows/*` | CI/CD improvements |
| `justfile`, `pyproject.toml` | Build/tooling changes |
| `src/**/*.py` | Docstrings, type hints |
| `CHANGELOG.md` | Changelog updated |
| `README.md` | README updated |

### Content Analysis

The scripts also analyze:
- All commits since branch diverged
- File statistics (additions/deletions)
- Changed file list with status (Modified, Added, Deleted)

## Workflow

### Recommended PR Creation Flow

1. **Develop on feature branch**:
   ```bash
   git checkout -b feature/your-feature
   # Make changes, commit often with clear messages
   ```

2. **Before creating PR**:
   ```bash
   # Run quality checks
   just check       # Format, lint, typecheck
   just test        # All tests
   just test-cov    # Check coverage

   # Update CHANGELOG.md for notable changes
   ```

3. **Create PR with auto-filled template**:
   ```bash
   just pr          # Interactive mode
   # or
   just pr-auto "feat: Your feature"  # Auto mode
   ```

4. **Review and customize**:
   - Script shows filled template
   - Customize specific sections
   - Confirm to create PR

5. **Monitor CI**:
   - GitHub Actions run automatically
   - Address any failures
   - Respond to review comments

## Examples

### Example 1: Bug Fix

```bash
# On branch: fix/parser-timing-bug
git checkout -b fix/parser-timing-bug

# Make changes, commit
git commit -m "Fix timing calculation for musical time"

# Create PR (interactive mode)
just pr
# → Auto-generates title: "Fix: Parser Timing Bug"
# → Marks "Bug fix" checkbox
# → Lists commit "Fix timing calculation for musical time"
```

### Example 2: New Feature

```bash
# On branch: feature/add-random-expressions
git checkout -b feature/add-random-expressions

# Make changes with multiple commits
git commit -m "Add random() function parser support"
git commit -m "Add random value expansion"
git commit -m "Add tests and documentation"

# Run checks
just check test

# Create PR with custom title
just pr "feat: Add random() expressions for generative music"
# → Marks "New feature" checkbox
# → Marks "Test improvements" (tests/ changed)
# → Marks "Documentation" (docs/ changed)
# → Lists all 3 commits
```

### Example 3: Documentation Update

```bash
# On branch: docs/update-quickstart
git checkout -b docs/update-quickstart

# Update docs
git commit -m "Update quickstart guide with new examples"
git commit -m "Add troubleshooting section"

# Quick PR creation (auto mode)
just pr-auto "docs: Improve quickstart guide"
# → Marks "Documentation update" checkbox
# → Skips interactive prompts
# → Creates PR immediately
```

## Customization

### Adding New Auto-Detection Patterns

Edit `.github/scripts/fill-pr-template.sh`:

```bash
# Example: Detect security changes
if echo "$changed_files" | grep -q "security/"; then
    security="- [x]"
fi
```

### Modifying Template Structure

1. Edit `.github/PULL_REQUEST_TEMPLATE.md` for structure
2. Edit `.github/scripts/fill-pr-template.sh` for auto-fill logic
3. Test: `just pr-preview`

## Troubleshooting

### "gh: command not found"
**Solution**: Install GitHub CLI from https://cli.github.com/

### "Not in a git repository"
**Solution**: Run from repository root directory

### "Current branch has no upstream"
**Solution**: Script automatically pushes and sets upstream

### Template not detecting changes correctly
**Cause**: Unusual branch name or file patterns
**Solution**: Use interactive mode (option 2) to edit before creating

### Want to see what will be generated
**Solution**: Run `just pr-preview` to see the template without creating PR

## Testing

### Test the Scripts

```bash
# Preview what will be generated
just pr-preview

# Save to file for inspection
just pr-template test-pr.md
cat test-pr.md
```

### Test End-to-End (without creating PR)

```bash
# Run in interactive mode, choose option 3 (Show and exit)
just pr
# Choose: 3
# → Shows filled template
# → Doesn't create PR
```

## Benefits

✅ **Saves Time**: No manual template filling
✅ **Consistency**: All PRs follow same structure
✅ **Completeness**: Reminds you of all required sections
✅ **Quality**: Encourages tests, docs, and quality checks
✅ **Traceability**: Links commits and changes clearly
✅ **Review-Friendly**: Reviewers get context immediately

## Integration with CI/CD

GitHub Actions automatically:
- Run tests on every PR
- Check formatting and linting
- Validate type hints
- Check test coverage
- Run example validation

The filled template helps ensure:
- You've run checks locally first
- Test coverage is documented
- Breaking changes are noted
- Documentation is updated

## Next Steps

1. **Try it out**: Create a test PR on a feature branch
2. **Customize**: Add project-specific auto-detections
3. **Share**: Teach team members about the new workflow
4. **Iterate**: Improve based on usage patterns

## Resources

- **Template**: `.github/PULL_REQUEST_TEMPLATE.md`
- **Scripts**: `.github/scripts/`
- **Documentation**: `.github/README.md`
- **Examples**: `.github/scripts/README.md`

## Feedback

If you have suggestions for improving the PR automation:
1. Test the changes
2. Update the scripts
3. Update documentation
4. Create a PR (using these scripts! 😄)

---

**Setup Date**: 2025-11-15
**Version**: 1.0
**Status**: ✅ Ready to Use
