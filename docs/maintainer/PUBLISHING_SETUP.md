# Publishing Setup Guide for Maintainers

This guide explains how to configure all the publishing methods for MIDI Markdown. Follow these one-time setup steps to enable automated publishing across all platforms.

## Table of Contents

1. [PyPI Trusted Publishing Setup](#1-pypi-trusted-publishing-setup)
2. [Homebrew Tap Setup](#2-homebrew-tap-setup)
3. [Windows Winget Setup](#3-windows-winget-setup)
4. [Ubuntu PPA Setup](#4-ubuntu-ppa-setup)
5. [Codecov Setup](#5-codecov-setup-optional)
6. [Release Workflow](#6-release-workflow)

---

## 1. PyPI Trusted Publishing Setup

Trusted Publishing uses OIDC to authenticate GitHub Actions with PyPI, eliminating the need for API tokens.

### Steps:

1. **Log in to PyPI**
   - Go to https://pypi.org/account/login/
   - Log in with your PyPI account

2. **Navigate to Publishing Settings**
   - Go to your project: https://pypi.org/project/midi-markdown/
   - Click "Manage project"
   - Click "Publishing" in the left sidebar

3. **Add Trusted Publisher**
   - Click "Add a new publisher"
   - Fill in the form:
     - **Owner:** `cjgdev`
     - **Repository name:** `midi-markdown`
     - **Workflow name:** `release.yml`
     - **Environment name:** `pypi`
   - Click "Add"

4. **Verify Configuration**
   - You should see the trusted publisher listed
   - No API token is needed in GitHub Secrets

### Testing:

```bash
# Create a test tag (will trigger release workflow)
git tag v0.1.1-test
git push origin v0.1.1-test

# Monitor workflow at: https://github.com/cjgdev/midi-markdown/actions
# Delete test release after verification
```

**Result:** PyPI publishing will work automatically on new version tags without any secrets.

---

## 2. Homebrew Tap Setup

Homebrew formulas can be served from your repository as a "tap."

### Steps:

1. **The formula is already created**
   - Located at `.github/homebrew/midi-markdown.rb`
   - Updated automatically by `.github/workflows/homebrew.yml`

2. **Users install with:**
   ```bash
   brew tap cjgdev/midi-markdown https://github.com/cjgdev/midi-markdown
   brew install midi-markdown
   ```

3. **Optional: Submit to homebrew-core**

   Once your package gains traction, consider submitting to the official Homebrew repository:

   **Requirements:**
   - Stable release (1.0.0+)
   - Significant user base
   - DFSG-compliant license (MIT ✅)
   - Meaningful test block (✅ already included)

   **Steps:**
   ```bash
   # Test formula locally first
   brew install --build-from-source .github/homebrew/midi-markdown.rb
   brew test midi-markdown
   brew audit --strict --online --new-formula midi-markdown

   # Fork homebrew-core and submit PR
   # https://github.com/Homebrew/homebrew-core/blob/master/CONTRIBUTING.md
   ```

### Testing:

```bash
# Test formula installation locally
brew install --build-from-source .github/homebrew/midi-markdown.rb
mmdc --version
brew test midi-markdown
brew uninstall midi-markdown
```

**Result:** Formula is automatically updated on each release.

---

## 3. Windows Winget Setup

Winget manifests are submitted to microsoft/winget-pkgs repository.

### Steps:

1. **Install wingetcreate** (one-time)
   ```powershell
   # On Windows machine
   winget install Microsoft.WingetCreate
   ```

2. **First-time submission:**

   After your first release (v0.1.0), submit manually:

   ```bash
   # Generate manifest
   wingetcreate new https://github.com/cjgdev/midi-markdown/releases/download/v0.1.0/mmdc-windows-x86_64.zip

   # Or use prepared manifest
   wingetcreate submit .github/winget/midi-markdown.yaml
   ```

3. **Automated updates:**

   After first approval, enable automated updates:

   ```bash
   # The .github/workflows/winget.yml workflow will:
   # 1. Update the manifest on each release
   # 2. Create a PR to your repo
   # 3. You can then submit to microsoft/winget-pkgs
   ```

4. **For each release:**

   ```bash
   # Use wingetcreate to submit update
   wingetcreate update CJGDev.MIDIMarkdown \
     --version 0.1.1 \
     --urls https://github.com/cjgdev/midi-markdown/releases/download/v0.1.1/mmdc-windows-x86_64.zip \
     --submit
   ```

### Testing:

```bash
# Test manifest locally before submitting
winget validate .github\winget\midi-markdown.yaml
winget install --manifest .github\winget\midi-markdown.yaml
mmdc --version
```

**Timeline:** 1-2 days for PR approval, then users can `winget install CJGDev.MIDIMarkdown`

---

## 4. Ubuntu PPA Setup

Launchpad Personal Package Archives (PPAs) provide apt packages for Ubuntu users.

### One-Time Setup:

1. **Create Launchpad Account**
   - Go to https://launchpad.net/
   - Create account or log in

2. **Generate GPG Key**
   ```bash
   # Generate key
   gpg --full-generate-key
   # Use: RSA and RSA, 4096 bits, name/email matching Launchpad

   # List keys to get key ID
   gpg --list-keys
   # Output shows: pub   rsa4096 2025-01-01 [SC] [expires: 2027-01-01]
   #               ABCD1234ABCD1234ABCD1234ABCD1234ABCD1234

   # Upload public key to Ubuntu keyserver
   gpg --send-keys YOUR_KEY_ID --keyserver keyserver.ubuntu.com

   # Also upload to Launchpad
   gpg --armor --export YOUR_KEY_ID
   # Copy output and paste at: https://launchpad.net/~/+editpgpkeys
   ```

3. **Sign Ubuntu Code of Conduct**
   - Go to https://launchpad.net/codeofconduct/2.0/+sign
   - Sign the code of conduct

4. **Create PPA**
   - Go to https://launchpad.net/~cjgdev/+activate-ppa
   - Create PPA named `midi-markdown`
   - URL will be: `ppa:cjgdev/midi-markdown`

### Publishing Process:

The GitHub Actions workflow (`.github/workflows/ppa.yml`) builds .deb packages for Ubuntu 20.04, 22.04, and 24.04.

**Manual upload to PPA:**

```bash
# Download source packages from GitHub Actions artifacts
# (after workflow runs on release)

# Sign the packages
debsign -k YOUR_KEY_ID midi-markdown_0.1.0-1~ppa1~ubuntu22.04.1_source.changes
debsign -k YOUR_KEY_ID midi-markdown_0.1.0-1~ppa1~ubuntu20.04.1_source.changes
debsign -k YOUR_KEY_ID midi-markdown_0.1.0-1~ppa1~ubuntu24.04.1_source.changes

# Upload to Launchpad PPA
dput ppa:cjgdev/midi-markdown midi-markdown_0.1.0-1~ppa1~ubuntu22.04.1_source.changes
dput ppa:cjgdev/midi-markdown midi-markdown_0.1.0-1~ppa1~ubuntu20.04.1_source.changes
dput ppa:cjgdev/midi-markdown midi-markdown_0.1.0-1~ppa1~ubuntu24.04.1_source.changes

# Launchpad builds packages automatically (10 min - 2 hours)
```

### Testing:

```bash
# On Ubuntu machine
sudo add-apt-repository ppa:cjgdev/midi-markdown
sudo apt update
sudo apt install midi-markdown
mmdc --version
```

**Timeline:** 10 minutes to 2 hours for Launchpad to build packages

---

## 5. Codecov Setup (Optional)

Codecov provides coverage reporting for your tests.

### Steps:

1. **Sign up for Codecov**
   - Go to https://about.codecov.io/
   - Sign in with GitHub

2. **Add Repository**
   - Add `cjgdev/midi-markdown` repository
   - Get upload token

3. **Add Secret to GitHub**
   - Go to https://github.com/cjgdev/midi-markdown/settings/secrets/actions
   - Add new secret: `CODECOV_TOKEN`
   - Value: paste token from Codecov

4. **Badge in README**
   ```markdown
   [![Coverage](https://codecov.io/gh/cjgdev/midi-markdown/branch/main/graph/badge.svg)](https://codecov.io/gh/cjgdev/midi-markdown)
   ```

**Result:** Coverage reports uploaded automatically on test runs.

---

## 6. Release Workflow

### Complete Release Process:

1. **Update Version**
   ```bash
   # Edit pyproject.toml
   vim pyproject.toml
   # Update version: version = "0.1.1"

   # Update CHANGELOG.md
   vim CHANGELOG.md
   # Add release notes under ## [0.1.1] - YYYY-MM-DD
   ```

2. **Commit Changes**
   ```bash
   git add pyproject.toml CHANGELOG.md
   git commit -m "Bump version to 0.1.1"
   git push origin main
   ```

3. **Create and Push Tag**
   ```bash
   git tag v0.1.1
   git push origin v0.1.1
   ```

4. **Automated Actions**
   - GitHub Actions automatically:
     ✅ Runs all tests
     ✅ Builds executables (Linux, macOS, Windows)
     ✅ Creates GitHub Release
     ✅ Publishes to PyPI (Trusted Publishing)
     ✅ Updates Homebrew formula
     ✅ Updates Winget manifest
     ✅ Builds Debian packages

5. **Manual Steps** (only these require manual action):

   **Winget submission:**
   ```bash
   wingetcreate update CJGDev.MIDIMarkdown --version 0.1.1 \
     --urls https://github.com/cjgdev/midi-markdown/releases/download/v0.1.1/mmdc-windows-x86_64.zip \
     --submit
   ```

   **PPA upload:**
   ```bash
   # Download source packages from GitHub Actions
   # Sign and upload to Launchpad (see section 4)
   ```

6. **Verify Release**
   - PyPI: https://pypi.org/project/midi-markdown/
   - GitHub: https://github.com/cjgdev/midi-markdown/releases
   - Homebrew: Test `brew install midi-markdown`
   - Winget: Test `winget install CJGDev.MIDIMarkdown` (after PR approval)
   - PPA: Test `apt install midi-markdown` (after build completes)

---

## Summary Checklist

Before first release:

- [ ] Configure PyPI Trusted Publishing
- [ ] Test Homebrew formula locally
- [ ] Submit first Winget manifest
- [ ] Create Launchpad PPA and upload GPG key
- [ ] (Optional) Set up Codecov

For each release:

- [ ] Update version in `pyproject.toml`
- [ ] Update `CHANGELOG.md`
- [ ] Commit and push changes
- [ ] Create and push version tag (`git tag v0.1.1 && git push origin v0.1.1`)
- [ ] Wait for CI to complete (~15 minutes)
- [ ] Submit Winget update (semi-automated)
- [ ] Upload PPA packages (semi-automated)
- [ ] Verify all distribution methods work

---

## Support and Documentation

- **GitHub Actions Workflows:** `.github/workflows/`
- **Homebrew Formula:** `.github/homebrew/midi-markdown.rb`
- **Winget Manifest:** `.github/winget/midi-markdown.yaml`
- **Debian Packaging:** `.github/debian/`
- **Installation Guide:** `INSTALLATION.md`

For questions or issues with the publishing setup:
- Open an issue: https://github.com/cjgdev/midi-markdown/issues
- Check workflow runs: https://github.com/cjgdev/midi-markdown/actions
