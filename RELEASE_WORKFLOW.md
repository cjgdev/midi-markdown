# Release Workflow - Quick Reference

Complete guide to releasing new versions of MIDI Markdown.

## 🎯 Overview

The release workflow automates:
- Version bumping across all files
- CHANGELOG.md updates
- Git tagging
- GitHub Release creation
- Binary builds (Linux, Windows, macOS)
- PyPI publishing (optional)

## 🚀 Quick Start

### For a Patch Release (bug fixes):

```bash
# 1. Run pre-release checks
just pre-release

# 2. Bump version and create tag (0.1.0 -> 0.1.1)
just release-patch

# 3. Push to trigger release
just release-push
```

### For a Minor Release (new features):

```bash
just pre-release
just release-minor    # 0.1.0 -> 0.2.0
just release-push
```

### For a Major Release (breaking changes):

```bash
just pre-release
just release-major    # 0.1.0 -> 1.0.0
just release-push
```

## 📋 Pre-Release Checklist

Before releasing, ensure:

- [ ] All tests pass: `just test`
- [ ] Code quality checks pass: `just check`
- [ ] CHANGELOG.md has all changes under `[Unreleased]`
- [ ] All examples work: `just validate-examples`
- [ ] Device libraries validate: `just validate-devices`
- [ ] Documentation is up-to-date
- [ ] Git branch is clean: `git status`

**Or run all checks at once:**
```bash
just pre-release
```

## 🛠️ Tools and Files

### Scripts

| Script | Purpose | Location |
|--------|---------|----------|
| `bump_version.py` | Version management | `scripts/bump_version.py` |

### Configuration Files

| File | Purpose |
|------|---------|
| `CHANGELOG.md` | Version history (Keep a Changelog format) |
| `pyproject.toml` | Version number, package metadata |
| `src/midi_markdown/__init__.py` | Version constant |
| `.github/workflows/release.yml` | GitHub Actions release workflow |
| `.github/RELEASE_CHECKLIST.md` | Release checklist template |

### Documentation

| File | Purpose |
|------|---------|
| `docs/developer-guide/releasing.md` | Complete release guide |
| `RELEASE_WORKFLOW.md` | This file - quick reference |
| `scripts/README.md` | Script documentation |

## 📦 What Gets Released

When you push a version tag (e.g., `v0.1.1`), GitHub Actions automatically:

1. **Runs Tests** - Ensures everything passes
2. **Builds Executables** - For Linux, Windows, macOS
3. **Creates GitHub Release** - With release notes from CHANGELOG.md
4. **Uploads Assets** - Executables + SHA256 checksums
5. **Publishes to PyPI** - If `PYPI_API_TOKEN` secret is configured

### Release Assets

- `mmdc-linux-x86_64.tar.gz` + `.sha256`
- `mmdc-windows-x86_64.zip` + `.sha256`
- `mmdc-macos-universal.zip` + `.sha256`
- Source code (zip, tar.gz) - automatically by GitHub

## 🔄 Complete Workflow

### Step 1: Prepare Changes

```bash
# Ensure all changes are committed
git status

# Update CHANGELOG.md with changes under [Unreleased]
vim CHANGELOG.md
```

Example CHANGELOG.md entry:
```markdown
## [Unreleased]

### Added
- New feature X
- Support for Y command

### Fixed
- Bug in parser Z
- Issue with device library
```

### Step 2: Run Pre-Release Checks

```bash
# Comprehensive quality checks
just pre-release
```

This runs:
- Format checking (`ruff format --check`)
- Linting (`ruff check`)
- Type checking (`mypy`)
- Full test suite with coverage
- Device library validation
- Example validation

### Step 3: Bump Version

Choose the appropriate release type:

```bash
# Patch release (0.1.0 -> 0.1.1) - bug fixes only
just release-patch

# Minor release (0.1.0 -> 0.2.0) - new features
just release-minor

# Major release (0.1.0 -> 1.0.0) - breaking changes
just release-major

# Or set specific version
just release-version 1.2.3
```

**What this does:**
1. Updates `pyproject.toml`
2. Updates `src/midi_markdown/__init__.py`
3. Moves `[Unreleased]` to new version in `CHANGELOG.md`
4. Creates git commit: "Release version X.Y.Z"
5. Creates git tag: "vX.Y.Z"

**Preview changes first:**
```bash
just release-preview patch
```

### Step 4: Push Release

```bash
# Interactive push (asks for confirmation)
just release-push

# Or manually:
git push origin main
git push origin v0.1.1  # Replace with your version
```

### Step 5: Monitor Release

1. **Watch GitHub Actions:**
   - Go to: https://github.com/cjgdev/midi-markdown/actions
   - Find the "Release" workflow
   - Monitor build progress (typically 15-20 minutes)

2. **Check for failures:**
   - Linux build
   - Windows build
   - macOS build
   - PyPI upload (if configured)

### Step 6: Verify Release

Once CI completes:

1. **Visit GitHub Releases:**
   - https://github.com/cjgdev/midi-markdown/releases
   - Verify release notes look correct
   - Check all executables are attached

2. **Test an executable:**
   ```bash
   # Download for your platform
   # Extract archive
   ./mmdc --version
   ./mmdc compile examples/00_basics/00_hello_world.mmd -o test.mid
   ```

3. **Verify PyPI (if published):**
   - https://pypi.org/project/midi-markdown/
   - Test installation: `pip install midi-markdown==X.Y.Z`

## 🔧 Advanced Usage

### Dry Run (Preview Changes)

```bash
# Preview what will be changed
uv run python scripts/bump_version.py patch --dry-run
```

### Skip Git Operations

```bash
# Update files but don't commit/tag
uv run python scripts/bump_version.py patch --no-git
```

### Hotfix Release

For critical bug fixes:

```bash
# Create hotfix branch from previous tag
git checkout -b hotfix/v0.1.2 v0.1.1

# Fix the bug
git commit -m "Fix critical bug"

# Update CHANGELOG.md manually
# Then bump version
uv run python scripts/bump_version.py patch

# Merge back to main
git checkout main
git merge hotfix/v0.1.2
git push origin main v0.1.2
```

### Delete a Tag (If Needed)

```bash
# Delete local tag
git tag -d v0.1.1

# Delete remote tag
git push origin :refs/tags/v0.1.1
```

## 🐍 PyPI Publishing

### One-Time Setup

1. Create PyPI account at https://pypi.org
2. Generate API token at https://pypi.org/manage/account/token/
3. Add as GitHub secret:
   - Name: `PYPI_API_TOKEN`
   - Value: Your `pypi-` token

### Manual PyPI Publishing

If you prefer manual control:

```bash
# Build distributions
just build

# Upload to TestPyPI first (recommended)
uv pip install twine
uv run twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ midi-markdown

# Upload to real PyPI
uv run twine upload dist/*
```

## 📊 Version Numbering (SemVer)

Format: `MAJOR.MINOR.PATCH[-PRERELEASE]`

| Change Type | Version Bump | Example |
|-------------|--------------|---------|
| Bug fixes | Patch | 0.1.0 → 0.1.1 |
| New features (backward-compatible) | Minor | 0.1.0 → 0.2.0 |
| Breaking changes | Major | 0.9.0 → 1.0.0 |
| Pre-release | Suffix | 1.0.0-alpha.1, 1.0.0-beta.2, 1.0.0-rc.1 |

**Pre-1.0.0 Note:** During 0.x.y development, breaking changes can occur in minor versions.

## 🆘 Troubleshooting

### CI Build Fails

1. Check logs: https://github.com/cjgdev/midi-markdown/actions
2. Fix the issue in main branch
3. Delete and recreate tag:
   ```bash
   git tag -d v0.1.1
   git push origin :refs/tags/v0.1.1
   # Fix, commit, then recreate tag
   ```

### Version Mismatch

Always use `bump_version.py` script - it keeps all files in sync:
```bash
uv run python scripts/bump_version.py patch
```

### CHANGELOG Not Updated

If you forgot to update CHANGELOG before release:

```bash
# If tag not pushed yet:
git tag -d v0.1.1
# Edit CHANGELOG.md
git add CHANGELOG.md
git commit --amend
git tag -a v0.1.1 -m "Release 0.1.1"

# If tag already pushed:
git push origin :refs/tags/v0.1.1  # Delete remote tag
# Update CHANGELOG, commit, retag
```

## 🔗 Quick Links

- **Releases**: https://github.com/cjgdev/midi-markdown/releases
- **Actions**: https://github.com/cjgdev/midi-markdown/actions
- **Issues**: https://github.com/cjgdev/midi-markdown/issues
- **PyPI** (future): https://pypi.org/project/midi-markdown/

## 📚 Documentation

- **Complete Guide**: [docs/developer-guide/releasing.md](docs/developer-guide/releasing.md)
- **Release Checklist**: [.github/RELEASE_CHECKLIST.md](.github/RELEASE_CHECKLIST.md)
- **Script Docs**: [scripts/README.md](scripts/README.md)
- **CHANGELOG**: [CHANGELOG.md](CHANGELOG.md)

## ⚡ TL;DR

```bash
# One-liner for patch release
just pre-release && just release-patch && just release-push

# One-liner for minor release
just pre-release && just release-minor && just release-push

# One-liner for major release
just pre-release && just release-major && just release-push
```

---

**Last Updated**: 2025-11-11
**Maintainer**: Christopher Gilbert (@cjgdev)
