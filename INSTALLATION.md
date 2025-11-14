# Installation Guide

MIDI Markdown (MMD) provides multiple installation methods to suit different user preferences and platforms. Choose the method that works best for your workflow.

## Quick Installation

### For Python Users (Recommended)

```bash
# Using pipx (isolated environment, recommended)
pipx install midi-markdown

# Or using pip
pip install midi-markdown
```

### For macOS Users

```bash
# Using Homebrew (easiest for macOS)
brew tap cjgdev/midi-markdown https://github.com/cjgdev/midi-markdown
brew install midi-markdown
```

### For Windows Users

```bash
# Using winget (Windows Package Manager)
winget install CJGDev.MIDIMarkdown

# Or download standalone executable from releases
# https://github.com/cjgdev/midi-markdown/releases
```

### For Ubuntu/Debian Users

```bash
# Using PPA
sudo add-apt-repository ppa:cjgdev/midi-markdown
sudo apt update
sudo apt install midi-markdown
```

---

## Detailed Installation Instructions

### 1. Python Package Managers (All Platforms)

**Requirements:** Python 3.12 or higher

#### Option A: pipx (Recommended)

[pipx](https://github.com/pypa/pipx) installs Python CLI tools in isolated environments:

```bash
# Install pipx if not already installed
python3 -m pip install --user pipx
python3 -m pipx ensurepath

# Install midi-markdown
pipx install midi-markdown

# Verify installation
mmdc --version
```

**Benefits:**
- ✅ Isolated from system Python
- ✅ No dependency conflicts
- ✅ Automatic PATH management
- ✅ Easy upgrades: `pipx upgrade midi-markdown`

#### Option B: pip

```bash
# Install midi-markdown
pip install midi-markdown

# Verify installation
mmdc --version
```

#### Option C: uv (Fastest)

[uv](https://github.com/astral-sh/uv) is an extremely fast Python package installer:

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install midi-markdown
uv pip install midi-markdown

# Verify installation
mmdc --version
```

**Upgrading:**
```bash
# pipx
pipx upgrade midi-markdown

# pip
pip install --upgrade midi-markdown

# uv
uv pip install --upgrade midi-markdown
```

---

### 2. Homebrew (macOS and Linux)

**Requirements:** [Homebrew](https://brew.sh/) package manager

```bash
# Add the MIDI Markdown tap
brew tap cjgdev/midi-markdown https://github.com/cjgdev/midi-markdown

# Install midi-markdown
brew install midi-markdown

# Verify installation
mmdc --version

# Test with an example
mmdc compile examples/00_basics/01_hello_world.mmd -o test.mid
```

**Benefits:**
- ✅ Native package manager experience
- ✅ Automatic dependency management
- ✅ Shell completions included (bash, zsh, fish)
- ✅ Examples and device libraries included in `/opt/homebrew/share/midi-markdown/`

**Upgrading:**
```bash
brew update
brew upgrade midi-markdown
```

**Uninstalling:**
```bash
brew uninstall midi-markdown
brew untap cjgdev/midi-markdown
```

---

### 3. Windows Package Managers

#### Option A: Winget (Recommended for Windows 10/11)

**Requirements:** Windows 10 1809+ or Windows 11

```bash
# Install midi-markdown
winget install CJGDev.MIDIMarkdown

# Verify installation
mmdc --version
```

**Benefits:**
- ✅ Official Microsoft package manager
- ✅ Integrated with Windows 10/11
- ✅ Automatic updates available
- ✅ No admin rights required

**Upgrading:**
```bash
winget upgrade CJGDev.MIDIMarkdown
```

#### Option B: Chocolatey

**Requirements:** [Chocolatey](https://chocolatey.org/install) package manager

```bash
# Install midi-markdown
choco install midi-markdown

# Verify installation
mmdc --version
```

**Upgrading:**
```bash
choco upgrade midi-markdown
```

#### Option C: Standalone Executable

Download the standalone Windows executable from [GitHub Releases](https://github.com/cjgdev/midi-markdown/releases):

1. Download `mmdc-windows-x86_64.zip`
2. Extract the ZIP file
3. Add the extracted folder to your PATH, or run `mmdc.exe` directly

**Benefits:**
- ✅ No Python installation required
- ✅ No dependencies needed
- ✅ Works offline
- ❌ Must manually update for new versions

---

### 4. Ubuntu/Debian PPA

**Requirements:** Ubuntu 20.04+, Debian 11+, or derivatives

```bash
# Add the MIDI Markdown PPA
sudo add-apt-repository ppa:cjgdev/midi-markdown

# Update package list
sudo apt update

# Install midi-markdown
sudo apt install midi-markdown

# Verify installation
mmdc --version
```

**Supported Ubuntu versions:**
- Ubuntu 24.04 LTS (Noble)
- Ubuntu 22.04 LTS (Jammy)
- Ubuntu 20.04 LTS (Focal)

**Benefits:**
- ✅ Native package manager experience
- ✅ Automatic security updates
- ✅ System-wide installation
- ✅ Examples included in `/usr/share/doc/midi-markdown/examples/`

**Upgrading:**
```bash
sudo apt update
sudo apt upgrade midi-markdown
```

**Uninstalling:**
```bash
sudo apt remove midi-markdown
sudo add-apt-repository --remove ppa:cjgdev/midi-markdown
```

---

### 5. Standalone Executables (All Platforms)

Download pre-built executables from [GitHub Releases](https://github.com/cjgdev/midi-markdown/releases).

#### Linux (x86_64)

```bash
# Download and extract
wget https://github.com/cjgdev/midi-markdown/releases/download/v0.1.0/mmdc-linux-x86_64.tar.gz
tar -xzf mmdc-linux-x86_64.tar.gz

# Run directly or add to PATH
./mmdc/mmdc --version

# Optional: Install to /usr/local/bin
sudo cp mmdc/mmdc /usr/local/bin/
```

#### macOS (Universal)

```bash
# Download and extract
curl -L -o mmdc-macos-universal.zip https://github.com/cjgdev/midi-markdown/releases/download/v0.1.0/mmdc-macos-universal.zip
unzip mmdc-macos-universal.zip

# Bypass Gatekeeper (one-time)
xattr -cr mmdc

# Run directly or add to PATH
./mmdc/mmdc --version

# Optional: Install to /usr/local/bin
sudo cp mmdc/mmdc /usr/local/bin/
```

#### Windows (x86_64)

1. Download `mmdc-windows-x86_64.zip` from releases
2. Extract the ZIP file
3. Run `mmdc\mmdc.exe` directly or add to PATH

**Windows Security Warning:** Windows SmartScreen may show a warning for unsigned executables. Click "More info" then "Run anyway".

**Benefits:**
- ✅ No Python installation required
- ✅ No dependencies needed
- ✅ Works offline
- ✅ Single binary distribution
- ❌ Larger file size (~50-80 MB)
- ❌ Must manually update for new versions

**Verify checksums:**
```bash
# Linux/macOS
sha256sum mmdc-linux-x86_64.tar.gz
# Compare with .sha256 file

# Windows
certutil -hashfile mmdc-windows-x86_64.zip SHA256
# Compare with .sha256 file
```

---

### 6. From Source (Developers)

**Requirements:** Python 3.12+, [uv](https://github.com/astral-sh/uv) package manager

```bash
# Clone repository
git clone https://github.com/cjgdev/midi-markdown.git
cd midi-markdown

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync --all-extras

# Run from source
uv run mmdc --version

# Run tests
uv run pytest tests/

# Build standalone executable (optional)
uv sync --group build
uv run pyinstaller mmdc.spec
./dist/mmdc/mmdc --version
```

**Benefits:**
- ✅ Latest development version
- ✅ Contribute to development
- ✅ Modify and customize
- ✅ Run tests locally

---

## Verification

After installation, verify MIDI Markdown is working correctly:

```bash
# Check version
mmdc --version

# View help
mmdc --help

# Compile a test file
echo '---
title: "Test"
---

[00:00.000]
- note_on 1.60 100 1000ms' > test.mmd

mmdc compile test.mmd -o test.mid

# Should output: "✅ Compilation successful: test.mid"
```

---

## Troubleshooting

### Command Not Found

**Problem:** `mmdc: command not found` after installation

**Solution:**
- **pipx:** Run `pipx ensurepath` and restart terminal
- **pip:** Add `~/.local/bin` to PATH (Linux/macOS) or `%APPDATA%\Python\Python312\Scripts` (Windows)
- **Homebrew:** Run `eval "$(brew shellenv)"` or restart terminal
- **Standalone:** Add extracted folder to PATH

### Python Version Issues

**Problem:** `requires Python >=3.12` error

**Solution:**
```bash
# Check Python version
python3 --version

# Install Python 3.12+ from:
# - https://www.python.org/downloads/
# - Homebrew: brew install python@3.12
# - Windows: winget install Python.Python.3.12
```

### Permission Errors (Linux/macOS)

**Problem:** Permission denied when installing

**Solution:**
```bash
# Use --user flag with pip
pip install --user midi-markdown

# Or use pipx (recommended)
pipx install midi-markdown
```

### Windows SmartScreen Warning

**Problem:** "Windows protected your PC" message

**Solution:**
1. Click "More info"
2. Click "Run anyway"
3. This is normal for open-source software without code signing certificates

### macOS Gatekeeper Block

**Problem:** "cannot be opened because the developer cannot be verified"

**Solution:**
```bash
# Remove quarantine attribute
xattr -cr mmdc

# Or right-click the app and select "Open"
```

---

## Next Steps

After installation:

1. **Read the Quickstart:** [docs/getting-started/quickstart.md](docs/getting-started/quickstart.md)
2. **Try Examples:** Explore the [examples/](examples/) directory
3. **Read the Spec:** Comprehensive language reference in [spec.md](spec.md)
4. **Join Community:** Report issues on [GitHub](https://github.com/cjgdev/midi-markdown/issues)

---

## Platform Comparison

| Method | Platforms | Size | Updates | Python Required | Pros |
|--------|-----------|------|---------|-----------------|------|
| **pipx** | All | Small | Manual | Yes (3.12+) | ✅ Isolated, clean |
| **pip** | All | Small | Manual | Yes (3.12+) | ✅ Simple, familiar |
| **Homebrew** | macOS, Linux | Medium | Auto | No | ✅ Native, completions |
| **Winget** | Windows | Medium | Auto | No | ✅ Native, official |
| **PPA** | Ubuntu/Debian | Medium | Auto | No | ✅ Native, trusted |
| **Standalone** | All | Large | Manual | No | ✅ Self-contained |
| **From Source** | All | Small | Manual | Yes (3.12+) | ✅ Latest, dev-friendly |

**Recommendations:**
- **Beginners:** Use Homebrew (macOS), Winget (Windows), or PPA (Ubuntu)
- **Python developers:** Use pipx for isolated environment
- **Power users:** Use standalone executables for portability
- **Contributors:** Install from source

---

## Support

- **Documentation:** https://github.com/cjgdev/midi-markdown#readme
- **Issues:** https://github.com/cjgdev/midi-markdown/issues
- **Discussions:** https://github.com/cjgdev/midi-markdown/discussions
- **License:** MIT License
