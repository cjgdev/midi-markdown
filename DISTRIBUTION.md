# Distribution Guide - MIDI Markdown Compiler

This document describes how the MIDI Markdown compiler is packaged and distributed as standalone executables for Windows, macOS, and Linux.

## Overview

The project supports two distribution methods:

1. **Python Package (PyPI)** - For Python developers, installable via `pipx` or `pip`
2. **Standalone Executables** - For end-users (musicians) without Python installed

## Building Executables

### Prerequisites

- Python 3.12+
- uv package manager (`pip install uv`)
- Just command runner (`brew install just` or see https://github.com/casey/just)

### Quick Build

```bash
# Install build dependencies
uv sync --group build

# Build executable for current platform
just build-exe

# Test the built executable
just test-exe
```

The executable will be built in `dist/mmdc/`.

### Build Modes

**Onedir Mode** (Default - Faster startup):
```bash
just build-exe
# Output: dist/mmdc/ directory
# Startup: ~0.3-0.5 seconds
# Size: ~50-100 MB
```

**Onefile Mode** (Single portable file):
```bash
just build-exe-onefile
# Output: Single executable file
# Startup: ~1-1.5 seconds (extraction overhead)
# Size: ~40-80 MB compressed
```

**Recommendation**: Use onedir mode for distribution. Research shows 3x faster startup time with minimal size trade-off.

## PyInstaller Configuration

The `mmdc.spec` file controls the build process:

### Critical Data Files

- **Lark Grammar**: `src/midi_markdown/parser/mml.lark` - Required for parser
- **Device Libraries**: `devices/*.mmd` - Optional, can bundle or keep external
- **Examples**: `examples/*.mmd` - Optional reference files

### Hidden Imports

The spec file explicitly includes:

- `shellingham.posix` / `shellingham.nt` - Typer shell completion
- `rtmidi` modules - MIDI real-time support
- `rich` / `pygments` - Terminal formatting
- All `midi_markdown` submodules

### Package Metadata

Rich and Typer require metadata collection:

```python
datas += copy_metadata('rich')
datas += copy_metadata('typer')
```

## Platform-Specific Builds

### Linux

**Output**: AppImage portable executable

- No installation required
- Works across Ubuntu, Debian, Fedora, Arch, etc.
- Fastest startup among containerized formats
- Distribution: Single `.AppImage` file

**Build**:
```bash
# On Linux system
just build-exe
# Manually create AppImage (future: automated script)
```

### Windows

**Output**: Standalone `.exe` + dependencies in directory

- Archive as `.zip` for distribution
- Optional: Inno Setup installer for Start Menu integration
- **Unsigned**: Windows SmartScreen will show warnings

**Security Warning Workaround**:
Users must click "More info" → "Run anyway" for unsigned executables.

**Future**: Apply for SignPath Foundation free signing or use Sigstore.

### macOS

**Output**: `.app` bundle (future) or directory executable

- **Unsigned**: Gatekeeper will block execution
- Workaround: Right-click → "Open" or `xattr -cr mmdc`
- **Future**: Apply for Apple Developer Program ($99/year) for code signing

## GitHub Actions CI/CD

### Automated Builds

The `.github/workflows/build-executables.yml` workflow:

- Triggers on push to `main`/`develop` or pull requests
- Builds executables for Linux, Windows, macOS in parallel
- Tests each executable with sample files
- Uploads artifacts with SHA-256 checksums
- Retention: 30 days

**Matrix Build Strategy**:
```yaml
matrix:
  os: [ubuntu-latest, windows-latest, macos-latest]
```

### Release Workflow

The `.github/workflows/release.yml` workflow:

- Triggers on version tags (`v*`, e.g., `v0.1.0`)
- Builds executables for all platforms
- Creates GitHub Release with auto-generated notes
- Uploads platform-specific archives:
  - `mmdc-linux-x86_64.tar.gz`
  - `mmdc-windows-x86_64.zip`
  - `mmdc-macos-universal.zip`
- Includes SHA-256 checksums for verification

**Triggering a Release**:
```bash
git tag v0.1.0
git push origin v0.1.0
```

## Testing Executables

### Automated Testing

```bash
just test-exe
```

Runs:
1. `mmdc --version` - Verify executable starts
2. `mmdc compile examples/basic_usage.mmd` - Test compilation
3. Verify output MIDI file created

### Manual Testing Checklist

Test on clean systems (VMs/Docker containers without Python):

- [ ] Executable runs without Python installed
- [ ] `--help` displays correctly
- [ ] `--version` shows correct version
- [ ] Compilation produces valid MIDI files
- [ ] File paths with spaces/special characters work
- [ ] Error messages are helpful (not cryptic PyInstaller internals)
- [ ] MIDI playback works (use DAW or MIDI player)

### Platform-Specific Testing

**Linux**:
- Test on Ubuntu, Debian, Fedora
- Verify no missing library errors

**Windows**:
- Test on Windows 10/11
- Verify SmartScreen workaround documented
- Check antivirus false positives (VirusTotal scan)

**macOS**:
- Test on macOS 10.13+ (High Sierra and later)
- Verify Gatekeeper workaround works
- Test on both Intel and Apple Silicon (if universal build)

## Distribution Checklist

Before releasing a new version:

1. **Version Bump**
   - Update version in `src/midi_markdown/__init__.py`
   - Update changelog/release notes

2. **Build & Test**
   ```bash
   just clean
   just build-exe
   just test-exe
   ```

3. **Create Release**
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```

4. **Verify GitHub Actions**
   - Check workflow runs successfully
   - Download and test artifacts from GitHub

5. **Update Documentation**
   - README installation instructions
   - Release notes in GitHub Release
   - Update CLAUDE.md if distribution process changed

## Dual Distribution Strategy

### For Python Developers (Primary)

**PyPI + pipx**:
```bash
pipx install mmdc
```

Benefits:
- Isolated environment (no dependency conflicts)
- Easy updates (`pipx upgrade mmdc`)
- Standard Python ecosystem integration

### For Musicians/End-Users

**GitHub Releases**:
1. Navigate to https://github.com/youruser/midi-markdown/releases
2. Download platform-specific archive
3. Extract and run executable

Benefits:
- No Python installation required
- Single download, immediate use
- Portable (can run from USB drive)

## File Size Optimization

Current executable sizes:
- Linux: ~50-70 MB (onedir), ~30-40 MB (onefile)
- Windows: ~60-80 MB (onedir), ~35-45 MB (onefile)
- macOS: ~70-100 MB (onedir), ~40-50 MB (onefile)

**Optimization strategies** (if size becomes an issue):

1. **Exclude unnecessary packages** (already configured):
   - matplotlib, numpy, pandas, scipy
   - GUI frameworks (tkinter, PyQt, wx)

2. **UPX compression** (enabled):
   - Compresses binaries without runtime overhead
   - Can reduce size by 30-50%

3. **Strip debug symbols**:
   - Already configured with `strip=False` (minimal impact)

4. **Lazy imports**:
   - Import heavy libraries only when needed
   - Not applicable for this project (all imports essential)

## Troubleshooting

### "ModuleNotFoundError" at runtime

**Cause**: Missing hidden import

**Solution**: Add to `hiddenimports` in `mmdc.spec`

### "No module named 'lark.lark'"

**Cause**: Lark grammar file not bundled

**Solution**: Verify `mml.lark` in `datas` section of spec file

### "Permission denied" on macOS

**Cause**: Gatekeeper blocking unsigned executable

**Solution**: Right-click → "Open" or run `xattr -cr mmdc`

### Windows SmartScreen blocks executable

**Cause**: Executable is unsigned

**Solution**: Click "More info" → "Run anyway"

**Long-term**: Apply for free signing via SignPath Foundation

### Antivirus false positives

**Cause**: PyInstaller executables commonly flagged

**Solution**:
1. Submit to VirusTotal
2. Report false positives to antivirus vendors
3. Consider code signing (reduces but doesn't eliminate false positives)

## Code Signing (Future)

### Current Status

**Not implemented** - Project uses unsigned executables

### Free Options

1. **SignPath Foundation** (Windows)
   - Free for qualifying open-source projects
   - Requires verification of OSS status
   - HSM-based signing

2. **Sigstore** (All platforms)
   - Keyless signing using OIDC identity
   - Growing adoption in Python ecosystem
   - PyPI integration underway

### Paid Options

**Windows**:
- Organization Validation (OV) Certificate: $129-$340/year
- ~~Extended Validation (EV) Certificate~~: No longer provides SmartScreen advantage (as of March 2024)

**macOS**:
- Apple Developer Program: $99/year (required for notarization)
- Enables code signing + notarization for Gatekeeper

### Recommendation

Start with unsigned builds, document workarounds clearly. Once project gains traction, apply for SignPath Foundation (free) or invest in Apple Developer Program for macOS users.

## References

- PyInstaller Documentation: https://pyinstaller.org/
- GitHub Actions: https://docs.github.com/en/actions
- SignPath Foundation: https://about.signpath.io/product/open-source
- Sigstore: https://www.sigstore.dev/
- cli-research.md - Detailed research findings on Python CLI distribution
