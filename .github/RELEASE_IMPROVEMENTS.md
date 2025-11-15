# Release Process Improvements - Summary Report

**Date**: 2025-11-15
**Status**: ✅ All improvements implemented

## Overview

This document summarizes all improvements made to the GitHub Actions release workflows and the manual configuration required on GitHub to enable them.

---

## 🔧 Changes Applied

### 1. Critical Fixes

#### ✅ UV Installation Consistency
- **File**: `.github/workflows/build-executables.yml`
- **Change**: Replaced `pip install uv` with `astral-sh/setup-uv@v6` action
- **Benefit**: Consistent UV installation with caching enabled
- **Impact**: Faster builds, more reliable

#### ✅ Windows SHA256 Extraction
- **File**: `.github/workflows/winget.yml`
- **Change**: Replaced `certutil` with PowerShell `Get-FileHash`
- **Benefit**: Reliable hash calculation in bash shell context
- **Impact**: Eliminates fragile certutil parsing

#### ✅ Python 3.12 for Ubuntu 20.04/22.04
- **File**: `.github/workflows/ppa.yml`
- **Change**: Added deadsnakes PPA for Python 3.12 on older Ubuntu
- **Benefit**: Ensures Python 3.12 available on all build targets
- **Impact**: Successful builds on Ubuntu 20.04 (focal)

#### ✅ Artifact Retention Standardization
- **Files**: All workflow files
- **Change**: Standardized to 7 days (CI builds are temporary)
- **Benefit**: Consistent retention policy, lower storage costs
- **Impact**: Release artifacts are permanent (attached to GitHub Release)

---

### 2. Security Enhancements

#### ✅ Artifact Attestation
- **File**: `.github/workflows/release.yml`
- **Change**: Added `actions/attest-build-provenance@v1`
- **Benefit**: Cryptographically signed build provenance
- **Impact**: Users can verify artifact authenticity
- **Verification**: `gh attestation verify <artifact> --owner cjgdev`

**Required Permissions** (added):
```yaml
permissions:
  id-token: write      # For OIDC token
  attestations: write  # For attestation creation
```

#### ✅ Normalized Checksum Format
- **File**: `.github/workflows/build-executables.yml`
- **Change**: PowerShell script to match Unix `shasum` format
- **Benefit**: Consistent checksum file format across all platforms
- **Impact**: Users can verify with `shasum -c` on all platforms

---

### 3. Quality Improvements

#### ✅ Improved Changelog Extraction
- **File Created**: `scripts/extract_changelog.py`
- **File**: `.github/workflows/release.yml`
- **Change**: Python script replaces fragile `sed` command
- **Benefit**: Robust parsing, better error messages
- **Impact**: Release notes accurately extracted even with formatting changes

#### ✅ Claude Skills Package Verification
- **File**: `.github/workflows/release.yml`
- **Change**: Added verification step after packaging
- **Benefit**: Ensures packages created successfully before release
- **Impact**: Prevents releases with missing/corrupted Claude Skills

#### ✅ Smoke Tests for Archives
- **File**: `.github/workflows/release.yml`
- **Change**: Extract and test archived executables before release
- **Benefit**: Catches packaging errors before public release
- **Impact**: Ensures users can actually extract and run the executables

---

### 4. Reliability Improvements

#### ✅ PyPI Availability Checks
- **File**: `.github/workflows/homebrew.yml`
- **Change**: Polls PyPI API before downloading package
- **Benefit**: Waits for package propagation instead of blind retries
- **Impact**: Eliminates random failures due to CDN propagation delays

#### ✅ Consolidated Build Logic
- **Files**: `.github/workflows/release.yml`, `.github/workflows/build-executables.yml`
- **Change**: Release workflow now calls build-executables as reusable workflow
- **Benefit**: Single source of truth for build logic, no duplication
- **Impact**: Easier maintenance, guaranteed consistency

---

## 📋 Manual GitHub Configuration Required

### Required: Repository Settings

#### 1. **Enable Artifact Attestations**

**Location**: Repository Settings → Actions → General

**Required Settings**:
- ✅ **Artifact and log retention**: 7 days (already standardized in workflows)
- ✅ **Allow GitHub Actions to create and approve pull requests**: YES (for Homebrew/Winget PRs)

**Steps**:
1. Go to: `https://github.com/cjgdev/midi-markdown/settings/actions`
2. Under "Workflow permissions":
   - Select: **Read and write permissions**
   - Check: **Allow GitHub Actions to create and approve pull requests**
3. Click **Save**

**Why**: Homebrew and Winget workflows create PRs automatically

---

#### 2. **PyPI Trusted Publishing** (Already Configured)

**Location**: PyPI Project Settings

**Status**: ✅ Already configured (workflow uses `pypa/gh-action-pypi-publish@release/v1`)

**Verification**:
```yaml
# In release.yml
publish-pypi:
  environment:
    name: pypi
    url: https://pypi.org/p/midi-markdown
  permissions:
    id-token: write  # Required for Trusted Publishing
```

**No action needed** - this is already set up correctly.

---

#### 3. **Workflow Permissions**

**Location**: Repository Settings → Actions → General → Workflow permissions

**Required**:
- ✅ **Read and write permissions** (for creating releases, uploading assets)
- ✅ **Allow GitHub Actions to create and approve pull requests** (for Homebrew/Winget)

**Current Status**:
```yaml
# release.yml already has correct permissions
permissions:
  contents: write       # Create releases
  id-token: write      # Attestation
  attestations: write  # Attestation
```

**Action Required**:
1. Verify repository-level permissions allow workflows to create PRs
2. Go to: `https://github.com/cjgdev/midi-markdown/settings/actions`
3. Ensure "Allow GitHub Actions to create and approve pull requests" is **checked**

---

### Optional: Enhanced Notifications

#### GitHub Discussions Announcements

**Setup** (optional):
1. Enable GitHub Discussions for the repository
2. Update release workflow to post announcement:

```yaml
- name: Create Discussion Announcement
  run: |
    gh api \
      --method POST \
      -H "Accept: application/vnd.github+json" \
      /repos/cjgdev/midi-markdown/discussions \
      -f title="Release v${{ steps.get_version.outputs.VERSION }}" \
      -f body="See release notes: https://github.com/cjgdev/midi-markdown/releases/tag/v${{ steps.get_version.outputs.VERSION }}" \
      -f category_id="<ANNOUNCEMENTS_CATEGORY_ID>"
```

---

## 🚀 Release Workflow

### Tag Format Requirements

**✅ CRITICAL**: Release tags MUST follow this format:

- **Git tag**: `v0.1.0` (with 'v' prefix)
- **pyproject.toml**: `version = "0.1.0"` (without 'v')

**Verification** built into workflow:
```yaml
- name: Verify version consistency
  run: |
    TAG_VERSION=${GITHUB_REF#refs/tags/v}
    PKG_VERSION=$(python -c "import tomli; print(tomli.load(open('pyproject.toml', 'rb'))['project']['version'])")
    if [ "$TAG_VERSION" != "$PKG_VERSION" ]; then
      echo "❌ Version mismatch!"
      exit 1
    fi
```

**Workflow will fail if versions don't match!**

---

### Complete Release Process

**1. Update CHANGELOG.md**
```markdown
## [Unreleased]

### Added
- New feature X

### Fixed
- Bug fix Y
```

**2. Bump Version**
```bash
# Script already exists and handles everything
python scripts/bump_version.py patch  # or minor, or major
```

**What it does**:
- Updates `pyproject.toml`
- Updates `src/midi_markdown/__init__.py`
- Moves [Unreleased] to new version in CHANGELOG.md
- Creates git commit
- Creates git tag

**3. Push Tag** (triggers release)
```bash
git push origin main
git push origin v0.1.0
```

**4. Monitor** (automatic from here)
```bash
gh run list --workflow=release.yml
```

**5. Verify** (after ~20 minutes)
- ✅ GitHub Release created with all artifacts
- ✅ PyPI package published
- ✅ Homebrew PR created (manual merge)
- ✅ Winget PR created (manual merge)
- ✅ PPA packages available

---

## 📦 Release Artifacts

### What Gets Published

**GitHub Release** (permanent):
- `mmdc-linux-x86_64.tar.gz` + `.sha256`
- `mmdc-windows-x86_64.zip` + `.sha256`
- `mmdc-macos-universal.zip` + `.sha256`
- `claude-skills-mmd-<version>.tar.gz` + `.zip`
- Attestation files (`.build` provenance)

**PyPI** (permanent):
- `midi-markdown-<version>-py3-none-any.whl`
- `midi-markdown-<version>.tar.gz`

**GitHub Actions Artifacts** (7 days):
- Build artifacts for CI/debugging

---

## 🔍 Testing & Verification

### Pre-Release Checks

```bash
# MUST pass before releasing
just pre-release
```

**What it checks**:
- ✅ Format (ruff format --check)
- ✅ Linting (ruff check)
- ✅ Type checking (mypy)
- ✅ All tests (1264 tests)
- ✅ Device library validation
- ✅ Example validation

### Smoke Tests (Automated)

**During Release**:
1. Extract Linux tarball → test `--version` and compile
2. Extract macOS zip → test `--version` and compile
3. Verify Windows zip structure (can't execute on Linux runner)

**Local Testing**:
```bash
# Test before pushing tag
just build-exe      # Build executable
just test-exe       # Test it works

# Test package
uv build
pip install dist/*.whl
mmdc --version
```

---

## 📊 Monitoring

### Workflow Status

```bash
# List recent runs
gh run list --workflow=release.yml --limit 5

# View specific run
gh run view <run-id>

# View in browser
gh run view <run-id> --web
```

### Expected Timeline

| Stage | Duration | Status Indicator |
|-------|----------|------------------|
| Tests | 3-5 min | ✅ All platforms pass |
| Build | 5-10 min | ✅ 3 executables created |
| Smoke Tests | 1-2 min | ✅ Archives extract & run |
| Attestation | 30 sec | ✅ Provenance generated |
| Release | 1 min | ✅ GitHub Release created |
| PyPI | 1-2 min | ✅ Package published |
| Homebrew | 5-10 min | ✅ PR created |
| Winget | 5-10 min | ✅ PR created |
| PPA | 10-15 min | ✅ 3 .deb packages |

**Total**: 15-25 minutes

---

## 🐛 Troubleshooting

### Common Issues

**Issue: "Version mismatch"**
```
❌ Version mismatch: tag=0.1.0, package=0.1.1
```
**Fix**: Update pyproject.toml version to match tag, or create new tag

---

**Issue: "PyPI package not found"**
```
❌ Package not available on PyPI after 10 attempts
```
**Fix**: Check PyPI publish step succeeded. Wait for CDN propagation (up to 5 minutes)

---

**Issue: "Smoke test failed - Linux executable failed"**
```
❌ Linux executable failed
```
**Fix**: Check build logs. Likely missing dependencies in PyInstaller spec

---

**Issue: "Homebrew workflow failed - download failed"**
```
❌ Download failed after 3 attempts
```
**Fix**: Wait for PyPI CDN propagation. Workflow has retry logic but may need manual re-run

---

## ✅ Verification Checklist

Before considering release complete:

- [ ] GitHub Release exists: `https://github.com/cjgdev/midi-markdown/releases/tag/v<version>`
- [ ] All artifacts attached to release (6 files: 3 archives + 3 checksums)
- [ ] Attestation files present
- [ ] PyPI package available: `https://pypi.org/project/midi-markdown/<version>/`
- [ ] `pip install midi-markdown==<version>` works
- [ ] Homebrew PR created (check: `https://github.com/cjgdev/midi-markdown/pulls`)
- [ ] Winget PR created (check: `https://github.com/cjgdev/midi-markdown/pulls`)
- [ ] PPA packages available (check artifacts)
- [ ] Version tag exists: `git tag -l v<version>`
- [ ] CHANGELOG.md updated with version section

---

## 📚 Reference

### Scripts Created/Updated

- ✅ `scripts/extract_changelog.py` - NEW: Robust changelog extraction
- ✅ `scripts/bump_version.py` - EXISTS: Version bumping (already working)
- ✅ `scripts/package_claude_skills.py` - EXISTS: Claude Skills packaging

### Workflows Modified

- ✅ `.github/workflows/release.yml` - Main release workflow
- ✅ `.github/workflows/build-executables.yml` - Reusable build workflow
- ✅ `.github/workflows/homebrew.yml` - Homebrew formula updates
- ✅ `.github/workflows/winget.yml` - Winget manifest updates
- ✅ `.github/workflows/ppa.yml` - PPA package builds

### Documentation Updated

- ✅ `.claude/agents/release-manager.md` - Release process documentation
- ✅ This file (`.github/RELEASE_IMPROVEMENTS.md`) - Summary report

---

## 🎯 Summary

### What's Improved

1. ✅ **Security**: Artifact attestation, normalized checksums
2. ✅ **Quality**: Smoke tests, version verification, package checks
3. ✅ **Reliability**: PyPI availability checks, retry logic, consolidated builds
4. ✅ **Automation**: All package managers update automatically
5. ✅ **Maintainability**: Reusable workflows, Python scripts vs shell

### What's Required

1. ⚠️ **Enable PR creation** in repository Actions settings
2. ⚠️ **Verify workflow permissions** allow read/write + attestations
3. ✅ PyPI Trusted Publishing (already configured)

### Next Release

```bash
# 1. Update CHANGELOG.md [Unreleased] section
# 2. Run pre-release checks
just pre-release

# 3. Bump version (creates commit + tag)
python scripts/bump_version.py patch  # or minor/major

# 4. Push (triggers automated release)
git push origin main
git push origin v0.1.0

# 5. Monitor (~20 minutes)
gh run list --workflow=release.yml

# 6. Verify release page has all artifacts
```

**All build artifacts will be available on the GitHub Release page when complete!**

---

**Report Generated**: 2025-11-15
**All Improvements**: ✅ Implemented and Ready
