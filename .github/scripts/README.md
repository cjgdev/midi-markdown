# GitHub Scripts

Helper scripts for GitHub workflows, PR creation, and automation.

## PR Template Scripts

### `fill-pr-template.sh`

Automatically fills in the PR template based on git changes.

**Usage:**
```bash
.github/scripts/fill-pr-template.sh ["Custom PR Title"]
```

**Features:**
- Auto-detects change type from branch name and files
- Lists all commits and changed files
- Marks checkboxes based on detected changes
- Generates test coverage section
- Detects documentation changes

**Example:**
```bash
# Generate filled template
.github/scripts/fill-pr-template.sh > pr-body.md

# Use with gh CLI
gh pr create --title "feat: Add new feature" --body-file pr-body.md
```

### `create-pr-with-template.sh`

Interactive wrapper for creating PRs with filled templates.

**Usage:**
```bash
.github/scripts/create-pr-with-template.sh ["PR Title"] [--auto]
```

**Options:**
- No arguments: Auto-generate title from branch name, interactive mode
- First argument: Custom PR title
- `--auto` flag: Skip interactive prompt and create PR immediately

**Interactive Options:**
1. Create PR with auto-filled template
2. Edit template before creating PR
3. Show template and exit (for manual editing)

**Examples:**
```bash
# Interactive mode with auto-generated title
.github/scripts/create-pr-with-template.sh

# Custom title, interactive mode
.github/scripts/create-pr-with-template.sh "feat: Add awesome feature"

# Auto mode (no prompts)
.github/scripts/create-pr-with-template.sh "fix: Bug fix" --auto

# Just show the template
.github/scripts/create-pr-with-template.sh
# Then choose option 3
```

## Using with Just

Add to your `justfile` for easy access:

```just
# Create PR with filled template
pr title="":
    .github/scripts/create-pr-with-template.sh "{{title}}"

# Create PR automatically (no prompts)
pr-auto title="":
    .github/scripts/create-pr-with-template.sh "{{title}}" --auto
```

**Usage:**
```bash
# Interactive mode
just pr

# With custom title
just pr "feat: Add new feature"

# Auto mode
just pr-auto "fix: Quick fix"
```

## Using with Claude Code

Claude Code can use these scripts via the `/create-pr` slash command:

```
/create-pr
```

This will:
1. Analyze your changes
2. Generate a filled PR template
3. Show you the template for review
4. Create the PR after confirmation

## PR Template Structure

The PR template (`.github/PULL_REQUEST_TEMPLATE.md`) includes:

- **Description**: Summary of changes
- **Motivation**: Why the change is needed
- **Type of Change**: Bug fix, feature, docs, etc.
- **Changes Made**: List of modifications
- **Testing**: Test coverage and manual testing
- **Documentation**: Docs updates
- **Code Quality**: Linting, formatting, type checking
- **Pre-submission Checklist**: Final checks
- **Breaking Changes**: If applicable
- **Performance Impact**: If applicable
- **Additional Context**: Links, notes, etc.

## Auto-Detection Features

The scripts automatically detect and mark:

### Change Type
- `fix/*` branch → Bug fix
- `feature/*` or `feat/*` branch → New feature
- `docs/*` branch → Documentation
- `refactor/*` branch → Refactoring
- `perf/*` branch → Performance
- `test/*` branch → Test improvements

### File Changes
- `docs/*` files → Documentation checkbox
- `tests/*` files → Test improvements checkbox
- `.github/workflows/*` files → CI/CD checkbox
- `justfile`, `pyproject.toml` → Build/tooling checkbox

### Test Coverage
- Changes in `tests/` → Unit/integration tests checkbox
- Changes in `tests/integration/` → Integration tests checkbox
- Changes in `tests/e2e/` → E2E tests checkbox

### Documentation
- Changes in `src/**/*.py` → Docstrings and type hints
- Changes in `src/midi_markdown/cli/` → CLI help text
- Changes in `docs/` → User documentation
- Changes in `examples/` → Examples
- Changes in `CHANGELOG.md` → Changelog
- Changes in `README.md` → README

## Tips

1. **Branch Naming**: Use conventional branch names for auto-detection:
   ```
   feature/add-awesome-feature
   fix/bug-in-parser
   docs/update-readme
   refactor/cleanup-code
   perf/optimize-timing
   test/add-unit-tests
   ```

2. **Commit Messages**: Write clear commit messages - they're included in the PR description

3. **Before Creating PR**:
   - Run `just check` (format + lint + typecheck)
   - Run `just test` (all tests)
   - Update CHANGELOG.md if needed

4. **Customization**: The scripts generate a baseline - always review and customize sections specific to your changes

## Troubleshooting

**"gh: command not found"**
- Install GitHub CLI: https://cli.github.com/

**"Not in a git repository"**
- Run from the repository root directory

**"Current branch has no upstream"**
- The script will automatically push and set upstream

**Template not auto-filled correctly**
- The script does its best to detect changes, but you can always edit before creating the PR
- Use option 2 (Edit template) in interactive mode

## Contributing

If you have ideas for improving the auto-detection or template filling, please:
1. Update the scripts
2. Test with various change types
3. Update this README
4. Submit a PR (using these scripts! 😄)
