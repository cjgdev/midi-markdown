# Installation Guide

Detailed installation instructions for MIDI Markdown.

## System Requirements

- **Python**: 3.12 or higher
- **Operating System**: macOS, Linux, or Windows
- **Disk Space**: ~50 MB for project and dependencies
- **Optional**: Git for cloning the repository

## Installation Methods

### Method 1: UV Package Manager (Recommended)

UV is a fast, modern Python package manager that handles virtual environments automatically.

**1. Install UV**

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with Homebrew (macOS)
brew install uv

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**2. Clone Repository**

```bash
git clone https://github.com/cjgdev/midi-markdown.git
cd midi-markdown
```

**3. Install Dependencies**

```bash
# UV automatically creates venv and installs dependencies
uv sync
```

**4. Verify Installation**

```bash
uv run mmdc version
# Output: MIDI Markdown (MMD) Compiler
#         Version: 0.1.0
```

### Method 2: pip and venv (Traditional)

If you prefer traditional Python tools:

**1. Clone Repository**

```bash
git clone https://github.com/cjgdev/midi-markdown.git
cd midi-markdown
```

**2. Create Virtual Environment**

```bash
# Create venv
python3.12 -m venv .venv

# Activate (macOS/Linux)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate
```

**3. Install Dependencies**

```bash
pip install -e .
```

**4. Verify Installation**

```bash
mmdc version
```

## Post-Installation Setup

### Create Output Directory

```bash
# Create directory for compiled MIDI files
mkdir -p output
```

### Test with Examples

```bash
# Compile a simple example
uv run mmdc compile examples/00_basics/01_hello_world.mmd -o output/test.mid

# Should output:
# ✅ Compilation successful
```

### Optional: Shell Completion

Enable tab completion for your shell:

```bash
# Bash
uv run mmdc --install-completion bash

# Zsh
uv run mmdc --install-completion zsh

# Fish
uv run mmdc --install-completion fish
```

## Development Setup

If you plan to contribute or modify the code:

### 1. Install Development Dependencies

```bash
uv sync --all-extras
```

### 2. Install Development Tools

```bash
# Ruff (linter and formatter) - included in uv
# mypy (type checker) - included in uv
# pytest (test framework) - included in uv
```

### 3. Verify Development Environment

```bash
# Run tests
uv run pytest

# Check code style
uv run ruff check .

# Type check
uv run mypy src
```

### 4. Pre-commit Setup (Optional)

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install
```

## IDE Setup

### Visual Studio Code

**1. Install Python Extension**

Install the official Python extension from Microsoft.

**2. Configure Interpreter**

1. Press `Cmd/Ctrl + Shift + P`
2. Type "Python: Select Interpreter"
3. Choose `.venv/bin/python`

**3. Recommended Extensions**

- Python (Microsoft) - Python language support
- Pylance - Fast Python language server
- YAML - YAML language support (for frontmatter)

**4. Settings (`.vscode/settings.json`)**

```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.linting.enabled": true,
  "python.formatting.provider": "none",
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true
  }
}
```

### PyCharm

**1. Open Project**

Open the `midi-markdown` directory.

**2. Configure Interpreter**

1. Go to Settings/Preferences → Project → Python Interpreter
2. Click gear icon → Add
3. Select "Existing environment"
4. Choose `.venv/bin/python`

**3. Enable Ruff**

1. Install Ruff plugin from JetBrains Marketplace
2. Enable in Settings → Tools → Ruff

## Troubleshooting

### Python Version Issues

**Q: "Python 3.12 not found"**

```bash
# Check your Python version
python3 --version

# Install Python 3.12 via pyenv (recommended)
brew install pyenv
pyenv install 3.12.9
pyenv local 3.12.9
```

### UV Installation Issues

**Q: "uv: command not found"**

```bash
# Add UV to PATH (macOS/Linux)
export PATH="$HOME/.cargo/bin:$PATH"

# Add to your shell profile (~/.zshrc or ~/.bashrc)
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.zshrc
```

### Dependency Issues

**Q: "Failed to install dependencies"**

```bash
# Clear UV cache
uv cache clean

# Retry installation
uv sync --reinstall
```

### Permission Issues

**Q: "Permission denied"**

```bash
# Don't use sudo with UV - it manages its own environment
# If you see permission errors, check file ownership:
ls -la

# Fix ownership if needed
sudo chown -R $USER:$USER .
```

### Virtual Environment Issues

**Q: "Wrong Python version in venv"**

```bash
# Remove existing venv
rm -rf .venv

# Recreate with correct Python version
uv sync --python 3.12
```

## Platform-Specific Notes

### macOS

- UV installs to `~/.cargo/bin/`
- Virtual environment created in `.venv/`
- MIDI playback: Use QuickTime Player or GarageBand

**Required:**
```bash
# Xcode Command Line Tools (for some dependencies)
xcode-select --install
```

### Linux

- UV installs to `~/.cargo/bin/`
- May need to install additional MIDI tools:

```bash
# Ubuntu/Debian
sudo apt-get install timidity fluidsynth

# Fedora
sudo dnf install timidity++ fluid-soundfont-gm

# Arch
sudo pacman -S timidity++ soundfont-fluid
```

### Windows

- UV installs to `%USERPROFILE%\.cargo\bin\`
- Use PowerShell or Windows Terminal (recommended)
- MIDI playback: Built into Windows Media Player

**Path Setup:**
Add UV to PATH via System Environment Variables if not done automatically.

## Verification Checklist

After installation, verify everything works:

```bash
# ✓ UV installed and in PATH
uv --version

# ✓ Python 3.12+ available
python3 --version

# ✓ Project dependencies installed
uv run mmdc version

# ✓ Can compile examples
uv run mmdc compile examples/00_basics/01_hello_world.mmd -o output/test.mid

# ✓ Tests pass
uv run pytest -m unit

# ✓ Code formatting works
uv run ruff format . --check
```

If all commands succeed, your installation is complete!

## Updating

To update to the latest version:

```bash
# Pull latest changes
git pull origin main

# Update dependencies
uv sync

# Verify update
uv run mmdc version
```

## Uninstalling

To completely remove the project:

```bash
# Remove project directory
cd ..
rm -rf midi-markdown

# Remove UV (optional)
rm -rf ~/.cargo/bin/uv
```

## Next Steps

- **[Getting Started Guide](quickstart.md)** - Create your first MIDI file
- **[CLI Command Reference](../cli-reference/overview.md)** - Learn all commands
- **[Examples](examples-guide.md)** - Work through progressive examples

## Getting Help

- Check [Troubleshooting](#troubleshooting) section above
- Review [GitHub Issues](https://github.com/cjgdev/midi-markdown/issues)
- Read the [FAQ](../reference/faq.md) (if available)
- Ask for help by creating a new issue
