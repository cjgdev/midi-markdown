# Release Guide

This guide covers the complete release process for MIDI Markdown, from version bumping to publishing releases.

## Table of Contents

1. [Version Numbering](#version-numbering)
2. [Pre-Release Checklist](#pre-release-checklist)
3. [Release Process](#release-process)
4. [Post-Release Tasks](#post-release-tasks)
5. [Hotfix Releases](#hotfix-releases)
6. [Troubleshooting](#troubleshooting)

---

## Version Numbering

MIDI Markdown follows [Semantic Versioning 2.0.0](https://semver.org/):

```
MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]
```

### Version Components

- **MAJOR**: Incompatible API/syntax changes (breaking changes)
- **MINOR**: New features (backwards-compatible)
- **PATCH**: Bug fixes (backwards-compatible)

### Examples

- `0.1.0` → `0.1.1` - Patch (bug fix)
- `0.1.0` → `0.2.0` - Minor (new feature)
- `0.1.0` → `1.0.0` - Major (breaking change)
- `1.0.0-alpha.1` - Pre-release version
- `1.0.0-beta.2` - Beta release

### Pre-1.0.0 Releases

During initial development (0.x.y):
- Breaking changes can occur in minor versions
- The API is not yet stable
- Production use is not recommended

### Release Types

| Type | When to Use | Example |
|------|-------------|---------|
| **Patch** | Bug fixes, documentation, internal refactoring | 0.1.0 → 0.1.1 |
| **Minor** | New features, deprecations (with warnings) | 0.1.0 → 0.2.0 |
| **Major** | Breaking changes, API redesign | 0.9.0 → 1.0.0 |
| **Alpha** | Early testing, incomplete features | 1.0.0-alpha.1 |
| **Beta** | Feature-complete, testing phase | 1.0.0-beta.1 |
| **RC** | Release candidate, final testing | 1.0.0-rc.1 |

---

## Pre-Release Checklist

Before starting a release, ensure all these items are complete:

### 1. Code Quality

- [ ] All tests pass: `just test`
- [ ] Code is formatted: `just fmt-check`
- [ ] No linting errors: `just lint`
- [ ] Type checking passes: `just typecheck`
- [ ] Coverage is maintained or improved: `just test-cov`

```bash
# Run all checks at once
just check
just test-cov
```

### 2. Documentation

- [ ] CHANGELOG.md updated with all changes in [Unreleased] section
- [ ] README.md is up-to-date
- [ ] All examples compile successfully: `just validate-examples`
- [ ] Device libraries validate: `just validate-devices`
- [ ] Documentation builds: `just docs-build`
- [ ] User guides reflect new features
- [ ] Developer guides updated if architecture changed

### 3. Examples and Devices

- [ ] All example files work: `just validate-examples`
- [ ] Device libraries are valid: `just validate-devices`
- [ ] New features have example files
- [ ] Example README.md is updated

### 4. Git Repository

- [ ] All changes committed to main branch
- [ ] Branch is up-to-date with origin: `git pull origin main`
- [ ] No uncommitted changes: `git status`
- [ ] CI/CD passes on GitHub Actions

### 5. Version Planning

- [ ] Decide version number (major/minor/patch)
- [ ] Review all changes since last release
- [ ] Ensure CHANGELOG.md categorizes changes correctly:
  - Added (new features)
  - Changed (changes in existing functionality)
  - Deprecated (features marked for removal)
  - Removed (removed features)
  - Fixed (bug fixes)
  - Security (security fixes)

---

## Release Process

### Step 1: Update Unreleased Changes

Ensure CHANGELOG.md has all changes documented under `[Unreleased]`:

```markdown
## [Unreleased]

### Added
- New feature X
- Support for Y

### Fixed
- Bug Z in parser
```

### Step 2: Run Pre-Release Checks

```bash
# Run comprehensive checks
just check
just test-cov
just validate-all

# Verify executables build (optional, CI will do this)
just build-exe
just test-exe
```

### Step 3: Bump Version

Use the version bump script to update versions across the project:

```bash
# For patch release (0.1.0 -> 0.1.1)
python scripts/bump_version.py patch

# For minor release (0.1.0 -> 0.2.0)
python scripts/bump_version.py minor

# For major release (0.1.0 -> 1.0.0)
python scripts/bump_version.py major

# Or specify exact version
python scripts/bump_version.py 1.2.3
```

**What this script does:**
1. Updates `pyproject.toml` with new version
2. Updates `src/midi_markdown/__init__.py` with new version
3. Moves [Unreleased] changes to new version section in CHANGELOG.md
4. Creates git commit: "Release version X.Y.Z"
5. Creates git tag: "vX.Y.Z"

**Preview changes first:**
```bash
python scripts/bump_version.py patch --dry-run
```

### Step 4: Push Changes

Push the commit and tag to GitHub:

```bash
# Push commits
git push origin main

# Push tag (this triggers the release workflow)
git push origin v0.1.1  # Replace with your version
```

**Alternative: Push everything at once**
```bash
git push origin main --tags
```

### Step 5: Monitor CI/CD

Once you push the tag, GitHub Actions will automatically:

1. **Run Tests** - Verify everything passes
2. **Build Executables** - Create binaries for Linux, Windows, macOS
3. **Create GitHub Release** - Generate release with notes
4. **Upload Assets** - Attach executables and checksums

Monitor progress:
- Go to: https://github.com/cjgdev/midi-markdown/actions
- Find the "Release" workflow run
- Check for any failures

**Typical build time:** 15-20 minutes for all platforms

### Step 6: Verify Release

Once CI completes:

1. **Check GitHub Release:**
   - Go to: https://github.com/cjgdev/midi-markdown/releases
   - Verify release notes look correct
   - Verify all executables are attached:
     - `mmdc-linux-x86_64.tar.gz` + `.sha256`
     - `mmdc-windows-x86_64.zip` + `.sha256`
     - `mmdc-macos-universal.zip` + `.sha256`

2. **Test Executables:**
   - Download one executable for your platform
   - Verify checksum matches
   - Run `./mmdc --version`
   - Test with a simple example

3. **Verify Documentation:**
   - Check that docs site is updated (if auto-deployed)
   - Verify links work

### Step 7: Publish to PyPI (Optional)

To publish the package to PyPI for `pip install midi-markdown`:

```bash
# Build distributions
just build

# Upload to TestPyPI first (recommended)
uv run twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ midi-markdown

# If everything works, upload to real PyPI
uv run twine upload dist/*
```

**Note:** You need PyPI credentials configured. See [PyPI Publishing](#pypi-publishing) section.

### Step 8: Announce Release

- [ ] Update project README.md if needed
- [ ] Post announcement in GitHub Discussions (if enabled)
- [ ] Notify users in relevant channels (Discord, Twitter, etc.)
- [ ] Update documentation site

---

## Post-Release Tasks

After a successful release:

### 1. Verify Installation

Test that users can install the new version:

```bash
# Via pip (if published to PyPI)
pip install midi-markdown==0.1.1

# Via pipx
pipx install midi-markdown==0.1.1

# Test it works
mmdc --version
```

### 2. Monitor Issues

Watch for bug reports related to the new release:
- Check GitHub Issues: https://github.com/cjgdev/midi-markdown/issues
- Monitor for installation problems
- Respond quickly to critical bugs

### 3. Update Development Branch

Start work on the next version:

```bash
# Add [Unreleased] section back to CHANGELOG.md
# (This should already be there from bump_version.py)

# Start tracking new changes
git checkout -b feature/next-feature
```

### 4. Update Project Status

- [ ] Update README badges if needed
- [ ] Update project status (Alpha → Beta → Stable)
- [ ] Update roadmap/milestones

---

## Hotfix Releases

For critical bug fixes that need immediate release:

### Process

1. **Create hotfix branch from tag:**
   ```bash
   git checkout -b hotfix/v0.1.2 v0.1.1
   ```

2. **Fix the bug:**
   ```bash
   # Make changes
   git commit -m "Fix critical bug in parser"
   ```

3. **Update CHANGELOG.md:**
   ```markdown
   ## [0.1.2] - 2025-11-12

   ### Fixed
   - Critical bug in parser causing crashes
   ```

4. **Bump version:**
   ```bash
   python scripts/bump_version.py patch --no-git
   git add .
   git commit -m "Release version 0.1.2 (hotfix)"
   git tag -a v0.1.2 -m "Hotfix release 0.1.2"
   ```

5. **Merge back to main:**
   ```bash
   git checkout main
   git merge hotfix/v0.1.2
   git push origin main v0.1.2
   ```

---

## PyPI Publishing

To enable automatic PyPI publishing, add PyPI credentials to GitHub Secrets:

### One-Time Setup

1. **Create PyPI Account:**
   - Go to https://pypi.org/account/register/
   - Verify email

2. **Generate API Token:**
   - Go to https://pypi.org/manage/account/token/
   - Create token with name "github-actions-midi-markdown"
   - Scope: Project (midi-markdown) or Account
   - **Save the token securely** (starts with `pypi-`)

3. **Add to GitHub Secrets:**
   - Go to: https://github.com/cjgdev/midi-markdown/settings/secrets/actions
   - Click "New repository secret"
   - Name: `PYPI_API_TOKEN`
   - Value: Paste your `pypi-` token
   - Click "Add secret"

4. **Update release.yml workflow:**

Add this job to `.github/workflows/release.yml`:

```yaml
publish-pypi:
  name: Publish to PyPI
  needs: create-release
  runs-on: ubuntu-latest

  steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.12'

    - name: Install uv
      run: pip install uv

    - name: Build distributions
      run: uv build

    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: |
        uv pip install twine
        uv run twine upload dist/*
```

### Manual PyPI Publishing

If you prefer to publish manually:

```bash
# Install twine
uv pip install twine

# Build distributions
just build

# Upload to PyPI
uv run twine upload dist/*
```

---

## Troubleshooting

### Tag Already Exists

**Problem:** You created a tag but need to update it.

**Solution:**
```bash
# Delete local tag
git tag -d v0.1.1

# Delete remote tag
git push origin :refs/tags/v0.1.1

# Recreate tag
git tag -a v0.1.1 -m "Release 0.1.1"
git push origin v0.1.1
```

### CI Build Fails

**Problem:** GitHub Actions workflow fails during release.

**Solution:**
1. Check the workflow logs: https://github.com/cjgdev/midi-markdown/actions
2. Fix the issue in main branch
3. Delete the tag and recreate:
   ```bash
   git tag -d v0.1.1
   git push origin :refs/tags/v0.1.1
   # Fix issues, commit, then retag
   ```

### Version Mismatch

**Problem:** Versions in pyproject.toml and __init__.py don't match.

**Solution:**
```bash
# Use the bump script (it keeps them in sync)
python scripts/bump_version.py patch

# Or manually fix:
# 1. Edit pyproject.toml
# 2. Edit src/midi_markdown/__init__.py
# 3. Commit changes
```

### CHANGELOG Not Updated

**Problem:** Forgot to update CHANGELOG before release.

**Solution:**
```bash
# If tag not pushed yet:
git tag -d v0.1.1
# Edit CHANGELOG.md
git add CHANGELOG.md
git commit --amend
git tag -a v0.1.1 -m "Release 0.1.1"

# If tag already pushed:
# 1. Delete remote tag: git push origin :refs/tags/v0.1.1
# 2. Update CHANGELOG
# 3. Commit and retag
```

### Executable Doesn't Work

**Problem:** Built executable fails to run.

**Solution:**
1. Check PyInstaller spec file: `mmdc.spec`
2. Test locally: `just build-exe && just test-exe`
3. Check for missing dependencies
4. Verify hidden imports in spec file

### PyPI Upload Fails

**Problem:** Twine fails to upload to PyPI.

**Solution:**
1. Verify API token is correct
2. Check package name isn't taken
3. Verify version number is unique (can't reupload same version)
4. Try TestPyPI first: `twine upload --repository testpypi dist/*`

---

## Release Workflow Summary

**Quick Reference:**

```bash
# 1. Prepare
just check && just test-cov && just validate-all

# 2. Bump version
python scripts/bump_version.py minor  # or patch/major

# 3. Push (triggers release)
git push origin main --tags

# 4. Monitor CI
# Visit: https://github.com/cjgdev/midi-markdown/actions

# 5. Verify release
# Visit: https://github.com/cjgdev/midi-markdown/releases

# 6. (Optional) Publish to PyPI
just build
uv run twine upload dist/*
```

---

## Reference

### Files Modified by Release

- `pyproject.toml` - Version number
- `src/midi_markdown/__init__.py` - __version__ string
- `CHANGELOG.md` - Move [Unreleased] to version section
- Git tag - `vX.Y.Z`

### Tools Used

- `scripts/bump_version.py` - Version management
- `just` - Task runner
- `uv` - Package manager
- `pytest` - Testing
- `ruff` - Linting/formatting
- `mypy` - Type checking
- `twine` - PyPI publishing
- `pyinstaller` - Executable building
- GitHub Actions - CI/CD

### Links

- **Releases**: https://github.com/cjgdev/midi-markdown/releases
- **Actions**: https://github.com/cjgdev/midi-markdown/actions
- **PyPI** (future): https://pypi.org/project/midi-markdown/
- **Semantic Versioning**: https://semver.org/
- **Keep a Changelog**: https://keepachangelog.com/

---

**Last Updated**: 2025-11-11
**Maintainer**: Christopher Gilbert (@cjgdev)
