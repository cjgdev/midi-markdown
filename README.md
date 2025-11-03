# MIDI Markdown

> Human-readable MIDI markup language for creating and automating MIDI sequences

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Status: Beta** - Core MIDI compilation and alias system are functional. Advanced features (loops, variables, imports) are in development.

## What is MIDI Markdown?

MIDI Markdown (MML) is a human-readable, text-based format for creating and automating MIDI sequences. It's designed specifically for live performance automation (e.g., Neural DSP Quad Cortex, Eventide H90) but supports all MIDI commands and devices.

### Key Features

- **Human-readable syntax** inspired by Markdown
- **Device-agnostic core** with extensible device libraries
- **Multiple timing paradigms**: absolute timecode, musical time (bars.beats.ticks), relative delta
- **Powerful alias system** for device-specific commands
- **Advanced features**: loops, variables, expressions, multi-track support
- **Full MIDI coverage**: channel voice messages, system messages, meta events

## Quick Start

New to MML? Check out the [Getting Started Guide](docs/getting-started.md) for a 5-minute tutorial.

## Quick Example

```markdown
---
title: "Song Automation"
midi_format: 1
ppq: 480
devices:
  - cortex: channel 1
  - h90: channel 2
---

# Intro
[00:00.000]
- tempo 120
- pc 1.10              # Load preset 10 on channel 1
- cc 2.7.100           # Set volume on channel 2

# Verse
[00:16.000]
- marker "Verse 1"
- note_on 1.C4 100 1b  # Middle C, 1 beat duration

# Chorus with relative timing
[00:40.000]
- marker "Chorus"
- cc 1.7.127           # Max volume
[+500ms]               # 500ms after previous
- cc 2.84.64           # Effects mix at 50%
```

## Installation

### For Python Users (Recommended)

Install via pipx for isolated environment:

```bash
pipx install midimarkup
```

Or with pip:

```bash
pip install midimarkup
```

### Standalone Executables (No Python Required)

Download pre-built executables from [GitHub Releases](https://github.com/yourusername/midi-markdown/releases):

**Linux**:
```bash
wget https://github.com/yourusername/midi-markdown/releases/latest/download/midimarkup-linux-x86_64.tar.gz
tar -xzf midimarkup-linux-x86_64.tar.gz
./midimarkup/midimarkup --version
```

**macOS**:
```bash
# Download and extract
curl -LO https://github.com/yourusername/midi-markdown/releases/latest/download/midimarkup-macos-universal.zip
unzip midimarkup-macos-universal.zip

# Remove quarantine attribute (required for unsigned apps)
xattr -cr midimarkup

# Run
./midimarkup/midimarkup --version
```

**Windows**:
1. Download `midimarkup-windows-x86_64.zip` from [Releases](https://github.com/yourusername/midi-markdown/releases/latest)
2. Extract the archive
3. Run `midimarkup.exe`
4. If Windows SmartScreen appears, click "More info" → "Run anyway"

### Development Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/midi-markdown.git
cd midi-markdown

# Install with UV (recommended)
uv sync

# Or with pip
pip install -e ".[dev]"
```

## Usage

### CLI Commands

```bash
# Compile MML to MIDI
midimarkup compile song.mml -o song.mid

# Validate MML syntax
midimarkup validate song.mml

# Quick syntax check
midimarkup check song.mml

# Show version
midimarkup version

# Device library management
midimarkup library list
midimarkup library info quad_cortex
```

### Python API

```python
# TODO: API usage examples once implementation is complete
from midi_markdown import compile_mml

compile_mml("song.mml", "output.mid", ppq=480)
```

## Project Structure

```
midi-markdown/
├── src/midi_markdown/    # Main package
│   ├── cli/              # Command-line interface
│   ├── parser/           # Lexer and parser
│   ├── alias/            # Alias resolution system
│   ├── midi/             # MIDI event generation
│   └── utils/            # Shared utilities
├── tests/                # Test suite
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── fixtures/         # Test data
├── examples/             # Example MML files
├── devices/              # Device library definitions
├── docs/                 # Documentation
├── spec.md               # Complete specification
└── CLAUDE.md             # AI assistant context
```

## Development

### Prerequisites

- Python 3.12+
- [UV](https://github.com/astral-sh/uv) (recommended) or pip

### Setup Development Environment

```bash
# Install dependencies with UV
uv sync

# Or with pip
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov

# Format code
ruff format .

# Lint code
ruff check .

# Type check
mypy src
```

### Running Tests

```bash
# All tests
pytest

# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# With coverage report
pytest --cov --cov-report=html
```

## Specification

For the complete language specification, see [spec.md](spec.md). Key sections:

- **File Structure** (lines 47-82): YAML frontmatter and document organization
- **Timing** (lines 84-123): Multiple timing paradigms
- **MIDI Commands** (lines 125-292): Complete MIDI command coverage
- **Alias System** (lines 294-385): Device-specific command shortcuts
- **Advanced Features** (lines 387-531): Variables, loops, conditionals
- **Device Libraries** (lines 533-711): Example device definitions

## Examples

See the [examples/README.md](examples/README.md) for a complete guide with learning path and feature matrix.

**Quick Links:**
- [00_hello_world.mml](examples/00_hello_world.mml) - Simplest possible MML file
- [05_multi_channel_basic.mml](examples/05_multi_channel_basic.mml) - Multiple MIDI channels
- [09_comprehensive_song.mml](examples/09_comprehensive_song.mml) - All features combined
- [13_device_import.mml](examples/13_device_import.mml) - Device library imports

## Device Libraries

MIDI Markdown includes device libraries for common MIDI controllers:

- **Neural DSP Quad Cortex** - [devices/quad_cortex.mml](devices/quad_cortex.mml) (86 aliases)
- **Eventide H90** - [devices/eventide_h90.mml](devices/eventide_h90.mml) (61 aliases)
- **Line 6 Helix Floor/LT/Rack** - [devices/helix.mml](devices/helix.mml) (49 aliases)
- **Line 6 HX Effects** - [devices/hx_effects.mml](devices/hx_effects.mml) (40+ aliases)
- **Line 6 HX Stomp** - [devices/hx_stomp.mml](devices/hx_stomp.mml) (39 aliases)
- **Line 6 HX Stomp XL** - [devices/hx_stomp_xl.mml](devices/hx_stomp_xl.mml) (40+ aliases)

Device libraries provide convenient aliases for device-specific operations:

```markdown
# Define aliases inline or use device libraries
@alias cortex_scene {ch} {scene:0-7} "Switch to scene"
  - cc {ch}.34.{scene}
@end

# Use aliases for cleaner, more readable code
[00:00.000]
- cortex_scene 1 0       # Scene A
- cortex_scene 1 3       # Scene D (lead tone)

# Import system coming in Stage 8
# @import "devices/quad_cortex.mml"
```

## Documentation

Comprehensive documentation is available in the [docs/](docs/) directory:

- **[Documentation Hub](docs/index.md)** - Central documentation index with learning paths
- **[Getting Started](docs/getting-started.md)** - 5-minute tutorial for your first MML file
- **[Installation Guide](docs/installation.md)** - Detailed setup for all platforms
- **[CLI Reference](docs/reference/cli-commands.md)** - Complete command-line interface documentation
- **[Alias System Guide](docs/guides/alias-system.md)** - Learn to use aliases
- **[Device Library Creation Guide](docs/guides/device-libraries.md)** - Create your own libraries
- **[Alias API Reference](docs/reference/alias-api.md)** - Complete API documentation

## Contributing

Contributions are welcome! This project is in early development - see the TODO comments throughout the codebase for areas needing implementation.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`pytest && ruff check .`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Roadmap

**Completed:**
- [x] Lexer/parser (Lark-based)
- [x] AST builder
- [x] Frontmatter parsing
- [x] MIDI event generation
- [x] MIDI file writing
- [x] Basic alias system (Stages 1-5)
- [x] Computed values (Stage 6 - partial)
- [x] Conditional logic in aliases (Stage 7)
- [x] Parser integration (Stage 9)
- [x] Device libraries: Quad Cortex, H90, Kemper, Helix
- [x] Comprehensive documentation (3 guides)
- [x] 281+ passing tests, 40%+ coverage

**In Progress:**
- [ ] Import system for device libraries (Stage 8)
- [ ] Advanced computed value expressions (Stage 6 completion)
- [ ] Enhanced validation engine

**Planned:**
- [ ] Variables and @define statements
- [ ] Loops and patterns (@loop)
- [ ] Sweep statements
- [ ] Multi-track advanced features
- [ ] Live mode (real-time MIDI sending)
- [ ] MIDI learn functionality
- [ ] More device libraries (Fractal, Strymon, Boss, etc.)

## Architecture

The implementation follows a pipeline architecture:

```
Input (.mml) → Lexer → Parser → Import Resolver → Alias Resolver
→ Validator → Event Generator → MIDI Writer → Output (.mid)
```

See [CLAUDE.md](CLAUDE.md) for detailed architecture documentation.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by Markdown's human-readable syntax
- Built for musicians and live performers
- Powered by modern Python tooling: UV, Ruff, Typer, pytest

## Links

- **Documentation Hub**: [docs/index.md](docs/index.md)
- **Getting Started**: [docs/getting-started.md](docs/getting-started.md)
- **Specification**: [spec.md](spec.md)
- **Examples**: [examples/README.md](examples/README.md)
- **Issue Tracker**: [GitHub Issues](https://github.com/yourusername/midi-markdown/issues)

---

**Note**: This project is in active development. The specification is complete, but implementation is ongoing. Contributions and feedback are welcome!
