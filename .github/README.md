# GitHub Configuration

This directory contains GitHub-specific configuration and automation scripts.

## Contents

### Pull Request Template

**File**: `PULL_REQUEST_TEMPLATE.md`

Comprehensive PR template that ensures all pull requests include:
- Description and motivation
- Type of change classification
- Test coverage details
- Documentation updates
- Code quality checklist
- Breaking changes documentation
- Performance impact assessment

This template is automatically loaded when creating PRs via GitHub web UI or can be filled programmatically using the scripts below.

### Automation Scripts

**Directory**: `scripts/`

Helper scripts for automating GitHub workflows:

1. **`fill-pr-template.sh`** - Auto-fills PR template based on git changes
2. **`create-pr-with-template.sh`** - Interactive PR creation with filled template

See [scripts/README.md](scripts/README.md) for detailed usage.

### Issue Templates

**Directory**: `ISSUE_TEMPLATE/`

Templates for bug reports, feature requests, and other issue types.

## Quick Start

### Creating a Pull Request

**Option 1: Using justfile** (Recommended)
```bash
# Interactive mode - reviews template before creating
just pr

# With custom title
just pr "feat: Add awesome feature"

# Auto mode (no prompts)
just pr-auto "fix: Quick fix"

# Preview what the template will contain
just pr-preview
```

**Option 2: Using scripts directly**
```bash
# Interactive mode
.github/scripts/create-pr-with-template.sh

# With custom title
.github/scripts/create-pr-with-template.sh "feat: Add feature"

# Auto mode
.github/scripts/create-pr-with-template.sh "fix: Bug fix" --auto
```

**Option 3: Using Claude Code**
```
/create-pr
```

**Option 4: Manual**
```bash
# Generate filled template
.github/scripts/fill-pr-template.sh > pr-body.md

# Edit as needed
$EDITOR pr-body.md

# Create PR with gh CLI
gh pr create --title "Your PR Title" --body-file pr-body.md
```

## Features

### Auto-Detection

The PR template scripts automatically detect and mark checkboxes based on:

**Change Type Detection**:
- Branch name patterns (`feature/*`, `fix/*`, `docs/*`, etc.)
- File change patterns
- Commit message analysis

**File Change Detection**:
- Documentation changes (`docs/*`)
- Test changes (`tests/*`)
- CI/CD changes (`.github/workflows/*`)
- Build/tooling changes (`justfile`, `pyproject.toml`, etc.)

**Commit Analysis**:
- Lists all commits since branch diverged
- Shows file statistics and changes
- Auto-generates description from commits

### Branch Naming Conventions

For best auto-detection results, use these branch naming patterns:

```
feature/descriptive-name    → Marks as "New feature"
fix/bug-description         → Marks as "Bug fix"
docs/what-you-updated       → Marks as "Documentation"
refactor/what-you-refactored → Marks as "Code refactoring"
perf/optimization-name      → Marks as "Performance improvement"
test/test-description       → Marks as "Test improvements"
chore/task-name             → Marks as "Build/tooling changes"
```

Branch names following this pattern will:
1. Auto-generate PR titles (e.g., `feature/add-loops` → "Feature: Add Loops")
2. Auto-check the appropriate "Type of Change" checkbox
3. Provide better context in the PR description

## Workflow

### Recommended PR Creation Flow

1. **Develop on a feature branch**:
   ```bash
   git checkout -b feature/your-feature
   # Make changes, commit often
   ```

2. **Before creating PR**:
   ```bash
   # Run quality checks
   just check       # Format, lint, typecheck
   just test        # Run all tests
   just test-cov    # Check coverage

   # Update CHANGELOG.md if needed
   ```

3. **Create PR**:
   ```bash
   # Interactive mode (recommended for first-time)
   just pr

   # Or auto mode if you're confident
   just pr-auto "feat: Your feature description"
   ```

4. **Review and customize**:
   - Script shows filled template
   - Customize any sections as needed
   - Confirm to create PR

5. **After PR created**:
   - Monitor CI checks
   - Address review comments
   - Keep branch updated with main if needed

### Claude Code Integration

When using Claude Code, it will automatically:
1. Detect when you're ready to create a PR
2. Run the fill-pr-template script
3. Analyze your changes
4. Present the filled template for review
5. Create the PR after confirmation

Use the `/create-pr` slash command to trigger this flow.

## Customization

### Modifying the Template

To change what's included in PRs:

1. Edit `.github/PULL_REQUEST_TEMPLATE.md` for structure
2. Edit `.github/scripts/fill-pr-template.sh` for auto-fill logic
3. Test changes: `just pr-preview`

### Adding New Auto-Detections

To add new auto-detection patterns, edit `fill-pr-template.sh`:

```bash
# Example: Detect performance changes
if echo "$changed_files" | grep -q "performance/"; then
    performance="- [x]"
fi
```

## Troubleshooting

### "gh: command not found"
Install GitHub CLI from https://cli.github.com/

### "Not in a git repository"
Ensure you're in the repository root directory

### "Current branch has no upstream"
The script will automatically push and set upstream for you

### Template not filled correctly
The scripts do their best to detect changes, but you can always:
- Use interactive mode (option 2) to edit before creating
- Use `just pr-preview` to see what would be generated
- Manually edit the template after generation

### PR created without template
If using `gh pr create` directly without the scripts, the template won't be auto-filled. Always use:
- `just pr` (recommended)
- `.github/scripts/create-pr-with-template.sh`
- `/create-pr` (in Claude Code)

## Best Practices

1. **Always run quality checks** before creating PR:
   ```bash
   just check test
   ```

2. **Write descriptive commit messages** - they're used in PR description

3. **Use conventional branch names** for better auto-detection

4. **Update CHANGELOG.md** for notable changes (required in template)

5. **Link related issues** in the Motivation section:
   ```markdown
   Closes #123
   Fixes #456
   Resolves #789
   ```

6. **Add test coverage** for new features and bug fixes

7. **Update documentation** when adding features or changing behavior

8. **Review the generated template** before creating - customize as needed

## Integration with CI/CD

GitHub Actions workflows (`.github/workflows/`) automatically:
- Run tests on PR creation
- Check code formatting and linting
- Validate type hints
- Check test coverage
- Validate device libraries and examples

Ensure all checks pass before requesting review.

## Contributing

To improve the PR automation:

1. **Test your changes**: Try with different branch types and change patterns
2. **Update documentation**: Keep this README and `scripts/README.md` in sync
3. **Add examples**: Show how new features work
4. **Get feedback**: Try it yourself before recommending to others

## See Also

- [scripts/README.md](scripts/README.md) - Detailed script documentation
- [PULL_REQUEST_TEMPLATE.md](PULL_REQUEST_TEMPLATE.md) - The actual template
- [Contributing Guide](../CONTRIBUTING.md) - General contribution guidelines
- [Development Guide](../docs/developer-guide/) - Architecture and patterns
