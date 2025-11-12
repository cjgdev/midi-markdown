# MIDI Markdown

> Human-readable MIDI markup language for creating and automating MIDI sequences

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Tests: 1090+](https://img.shields.io/badge/tests-1090%2B_passing-brightgreen.svg)](tests/)
[![Coverage: 72.53%](https://img.shields.io/badge/coverage-72.53%25-yellowgreen.svg)](tests/)
[![Code Style: Ruff](https://img.shields.io/badge/code_style-ruff-black.svg)](https://github.com/astral-sh/ruff)
[![Type Checking: mypy](https://img.shields.io/badge/type_checked-mypy-blue.svg)](https://www.mypy-lang.org/)
[![CI: Passing](https://img.shields.io/badge/CI-passing-brightgreen.svg)](https://github.com/cjgdev/midi-markdown/actions)
[![PyPI Published](https://img.shields.io/badge/PyPI-published-blue.svg)](https://pypi.org/project/midi-markdown/)

**✅ Production-Ready** — 1090+ tests, 72.53% coverage | Real-time MIDI playback | 6 device libraries (300+ aliases)

## 🎹 Real-Time MIDI Playback (NEW)

![TUI Demo](docs/images/tui-demo.gif)

*Interactive Terminal UI with real-time MIDI playback, sub-5ms timing precision, and keyboard controls (Space/Q/R)*

## Table of Contents

- [What is MIDI Markdown?](#what-is-midi-markup-language)
- [Why MMD?](#why-mml)
- [Key Features](#key-features)
- [Quick Example](#quick-example)
- [Getting Started](#getting-started)
- [Installation](#installation)
- [Usage](#usage)
- [Device Libraries](#device-libraries)
- [Examples](#examples)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [Roadmap](#roadmap)
- [License](#license)

## What is MIDI Markdown?

**The Problem**: Musicians struggle with MIDI automation for live performances. A single preset change requires manually programming 3+ MIDI commands (Bank MSB, Bank LSB, Program Change). Traditional solutions—DAWs, raw MIDI files—are either not portable or completely unreadable.

**The Solution**: MIDI Markdown (MMD) provides human-readable, text-based MIDI automation designed specifically for live performance. Instead of cryptic hex values and binary files, you write semantic commands like `cortex_load 1.2.0.5` that compile to precise MIDI sequences.

**Why Choose MMD?**

- **Device aliases**: Write `cortex_load 1.2.0.5` instead of 3 cryptic MIDI commands (Bank MSB, LSB, PC)
- **Version control**: Commit your automation to Git alongside your setlists—see exactly what changed between gigs
- **Real-time playback**: Interactive TUI with sub-5ms timing precision, keyboard controls (Space/Q/R), no DAW overhead
- **300+ pre-built aliases**: 6 supported devices (Neural DSP Quad Cortex, Eventide H90, Line 6 Helix, HX Stomp, HX Effects, HX Stomp XL)
- **Flexible timing**: Absolute timecode `[mm:ss.ms]`, musical time `[bars.beats.ticks]`, relative `[+500ms]`, simultaneous `[@]`
- **Production-tested**: 1090+ tests, 72.53% code coverage—built for reliability

**Example: From Chaos to Clarity**

```markdown
# Without MMD: cryptic raw MIDI
- cc 1.32.2    # Bank MSB (what does this do?)
- cc 1.0.0     # Bank LSB (no idea!)
- pc 1.5       # Program Change (which preset?)

# With MMD: semantic, obvious
- cortex_load 1.2.0.5  # Load Setlist 2, Group A, Preset 5
```

## Why MMD?

If you're currently managing MIDI automation for live performance, you might be wondering why MMD is better than other approaches. Here's how it compares:

| Aspect | Manual MIDI Programming | DAW Session Files | Raw MIDI Files | **MIDI Markdown** |
|--------|------------------------|-------------------|----------------|------------------|
| **Readability** | Hex values, hard to scan | GUI-based, not portable | Binary, unreadable | Human-readable text ✓ |
| **Version Control** | Difficult to diff/merge | Large binary files | Binary diffs | Text-based, Git-friendly ✓ |
| **Device Portability** | Device-specific | Locked to DAW | Needs mapping tables | Device-agnostic core ✓ |
| **Performance Tweaking** | Manual editing tedious | Requires DAW open | Binary hex editing | Simple text editing ✓ |
| **Reusability** | Copy-paste error-prone | Project-locked | No structure | Aliases & imports ✓ |
| **Real-time Editing** | ❌ Not possible | Requires DAW running | ❌ Not possible | Interactive TUI ✓ |

**Why musicians choose MMD:**

- **Version control**: Commit your automation to Git alongside your setlists. See exactly what changed between gigs.
- **Portable**: Same automation works across any MIDI device. Use Quad Cortex one night, Helix the next—no rewiring needed.
- **Device libraries**: Pre-built aliases for 6+ devices (Quad Cortex, H90, Helix, HX effects). Create your own in minutes.
- **Live-friendly**: Edit and test automations on the fly with interactive playback. No DAW startup overhead.
- **Human-readable**: Comments, clear syntax, and intuitive timing make automation easy to understand and maintain.

**Example**: Switching from Neural DSP Quad Cortex to Eventide H90? Change one line (`@import "devices/h90.mmd"`) and your automation adapts automatically.

## Key Features

🎹 **Real-Time MIDI Playback** — Interactive TUI with play/pause/stop, sub-5ms timing precision, keyboard controls (Space/Q/R)

🎛️ **Device-Specific Aliases** — 300+ aliases for 6 devices (Quad Cortex, H90, Helix, HX Stomp, HX Effects, HX Stomp XL) — replace raw MIDI with semantic commands

📝 **Human-Readable Syntax** — Markdown-inspired format, version control friendly, designed for musicians not programmers

⚡ **Multiple Timing Systems** — Absolute `[00:16.250]`, musical `[8.2.240]`, relative `[+500ms]`, simultaneous `[@]`

🔄 **Advanced Automation** — Variables, loops, conditionals, sweeps, generative patterns with `random()`, Bezier curves, LFO modulation, envelopes

📊 **Comprehensive Output** — MIDI files (formats 0/1/2), JSON export, CSV export (midicsv-compatible), Rich table display for debugging

## Quick Example

Imagine you're setting up a live performance with your Neural DSP Quad Cortex and need to automate preset changes throughout your set. With traditional MIDI, you'd have to manually configure bank selects and program changes. With MML, you write human-readable code and let the compiler handle the complexity:

```markdown
---
title: "Live Performance - Quad Cortex Automation"
tempo: 120
ppq: 480
---

# Import device-specific aliases for Quad Cortex
@import "devices/quad_cortex.mmd"

# Define reusable scene transitions with timing
@alias switch_scene {ch} {scene} {name}
  - marker "{name}"
  - cc {ch}.34.{scene}    # CC#34 = scene select
  - [+100ms]              # Account for device latency
@end

# ============= INTRO (Clean Tones) =============
[00:00.000]
- tempo 120
- qc_load_preset 1 0 0 5  # Load preset 5 from Setlist 1

# Build tone with gain automation
[00:04.000]
- switch_scene 1 0 "Intro - Scene A (Clean)"

# ============= VERSE (Rhythm Tone) =============
[00:16.000]
- switch_scene 1 1 "Verse - Scene B (Light OD)"

# Boost volume for section
[00:20.000]
- cc 1.7.100  # Master volume to 100

# ============= CHORUS (Heavy Tone) =============
[00:32.000]
- switch_scene 1 2 "Chorus - Scene C (Heavy Distortion)"

# ============= SOLO (Lead Tone) =============
[00:48.000]
- qc_load_preset 1 0 0 12  # Switch to lead preset
- [+150ms]
- switch_scene 1 3 "Solo - Scene D (High Gain Lead)"

# ============= OUTRO =============
[01:04.000]
- switch_scene 1 0 "Outro - Back to Clean"
```

**Compile it:**
```bash
mmdc compile performance.mmd -o performance.mid
```

**Play it live:**
```bash
mmdc play performance.mmd --port "Quad Cortex MIDI"
```

**What just happened:**
- You imported Neural DSP's device library with 86+ pre-built aliases
- You wrote readable, structured code using `switch_scene` and `qc_load_preset` instead of cryptic CC/PC numbers
- Automatic delays are built in so your device has time to process messages
- The compiler generated precise MIDI timing (down to milliseconds)
- You can now sync your entire performance to your DAW or play it standalone in real-time

This is what makes MMD special: **device automation becomes readable, reusable, and reliable**.

## Getting Started

New to MMD? Check out the [Getting Started Guide](docs/getting-started.md) for a 5-minute tutorial.

## Installation

**Recommended (pipx):**
```bash
pipx install midi-markdown
mmdc --version
```

**Alternative (pip):**
```bash
pip install midi-markdown
```

**Development (from source):**
```bash
git clone https://github.com/cjgdev/midi-markdown.git
cd midi-markdown
uv sync  # or: pip install -e ".[dev]"
```

**Standalone executables** (no Python required): Download from [GitHub Releases](https://github.com/cjgdev/midi-markdown/releases) for Linux, macOS, and Windows.

See [Installation Guide](docs/installation.md) for detailed platform-specific instructions.

## Usage

### CLI Commands

```bash
# Compile MMD to MIDI
mmdc compile song.mmd -o song.mid

# Real-time playback (NEW - Phase 3)
mmdc play song.mmd --port "IAC Driver Bus 1"
mmdc play song.mmd --port 0 --no-ui
mmdc play --list-ports

# Validate MMD syntax
mmdc validate song.mmd

# Quick syntax check
mmdc check song.mmd

# Show version
mmdc version

# Device library management
mmdc library list
mmdc library info quad_cortex
```

### Python API

```python
# TODO: API usage examples once implementation is complete
from midi_markdown import compile_mml

compile_mml("song.mmd", "output.mid", ppq=480)
```

## Claude Code Skills

**For Claude Code users**: MIDI Markdown provides official Claude Code skills to enhance your development experience:

- **mmd-writing** - Help writing MMD files with correct syntax, timing, and commands
- **mmdc-cli-usage** - Help using the mmdc CLI effectively

**Installation**: Download the skills package from the [latest release](https://github.com/cjgdev/midi-markdown/releases) and run the included installation script. See the [Claude Skills documentation](https://cjgdev.github.io/midi-markdown/getting-started/claude-skills/) for detailed instructions.

**Benefits**:
- ✅ Automatic syntax help when editing `.mmd` files
- ✅ CLI command suggestions and best practices
- ✅ Error troubleshooting and debugging assistance
- ✅ Example code and common patterns

## Device Libraries

Device libraries enable semantic commands that replace raw MIDI sequences. Instead of manual CC/PC sequences, write `cortex_load 1.2.0.5` for "Load Setlist 2, Group A, Preset 5"—much clearer and easier to maintain. MIDI Markdown includes 300+ pre-built aliases across 6 device libraries:

| Device | Aliases | Key Features |
|--------|---------|--------------|
| [Neural DSP Quad Cortex](devices/quad_cortex.mmd) | 86 | Preset loading, scene switching, I/O routing |
| [Eventide H90](devices/eventide_h90.mmd) | 61 | Preset management, parameter control, MIDI mapping |
| [Line 6 Helix Floor/LT/Rack](devices/helix.mmd) | 49 | Snapshots, command center, routing |
| [Line 6 HX Effects](devices/hx_effects.mmd) | 40+ | Preset switching, bypass, parameters |
| [Line 6 HX Stomp](devices/hx_stomp.mmd) | 39 | Compact control, scene switching |
| [Line 6 HX Stomp XL](devices/hx_stomp_xl.mmd) | 40+ | Extended control, preset management |

Use device libraries to replace low-level MIDI with expressive, semantic commands:

```markdown
# Instead of cryptic raw MIDI
- cc 1.32.2               # Bank MSB (unclear!)
- cc 1.0.0                # Bank LSB
- pc 1.5                  # Program Change

# Write clear, semantic commands
- cortex_load 1.2.0.5     # Load Setlist 2, Group A, Preset 5 (obvious!)

# Import device libraries (Stage 8 coming soon)
# @import "devices/quad_cortex.mmd"
```

## Examples

See the [examples/README.md](examples/README.md) for a complete guide with learning path and feature matrix.

**Quick Links:**
- [00_hello_world.mmd](examples/00_basics/00_hello_world.mmd) - Simplest possible MMD file
- [05_multi_channel_basic.mmd](examples/02_midi_features/05_multi_channel_basic.mmd) - Multiple MIDI channels
- [09_comprehensive_song.mmd](examples/03_advanced/09_comprehensive_song.mmd) - All features combined
- [13_device_import.mmd](examples/04_device_libraries/13_device_import.mmd) - Device library imports

## Documentation

Comprehensive documentation is available in the [docs/](docs/) directory:

- **[Documentation Hub](docs/index.md)** - Central documentation index with learning paths
- **[Getting Started](docs/getting-started.md)** - 5-minute tutorial for your first MMD file
- **[Installation Guide](docs/installation.md)** - Detailed setup for all platforms
- **[CLI Reference](docs/reference/cli-commands.md)** - Complete command-line interface documentation
- **[Alias System Guide](docs/guides/alias-system.md)** - Learn to use aliases
- **[Device Library Creation Guide](docs/guides/device-libraries.md)** - Create your own libraries
- **[Alias API Reference](docs/reference/alias-api.md)** - Complete API documentation

## Contributing

Contributions are welcome! Whether you're a developer, musician, or device enthusiast, there are many ways to help improve MIDI Markdown.

### Quick Start for Contributors

```bash
# Clone and setup
git clone https://github.com/cjgdev/midi-markdown.git
cd midi-markdown

# Install dependencies (UV is fast!)
uv sync

# Run tests
just test  # or: pytest
```

### Ways to Contribute

#### 🎛️ Device Libraries (Great First Contribution!)

Creating device libraries is the easiest way to contribute—no complex coding required! If you have a MIDI device with documented CC/PC mappings:

1. Create a new file in `devices/` directory (e.g., `devices/axe_fx.mmd`)
2. Add YAML frontmatter with device metadata
3. Define aliases using the simple alias syntax (just MIDI CC/PC basics needed)
4. Submit a PR—we'll help with any questions!

See [Device Library Creation Guide](docs/guides/device-libraries.md) for step-by-step instructions.

#### 🐛 Bug Reports & Feature Requests

- Found a bug? [Open an issue](https://github.com/cjgdev/midi-markdown/issues)
- Have an idea? [Request a feature](https://github.com/cjgdev/midi-markdown/issues)
- Include MMD examples and expected vs actual behavior

#### 💻 Code Contributions

Focus areas for development:
- Parser improvements (better error messages, recovery)
- New MIDI features (MPE, MIDI 2.0 support)
- CLI enhancements (interactive mode, better diagnostics)
- Documentation (tutorials, examples, guides)

### Code Quality Tools

We use modern Python tooling for code quality:

```bash
# Run all quality checks
just check  # or: ruff check . && mypy src

# Auto-fix issues
just fix    # or: ruff format . && ruff check --fix .

# Run tests with coverage
just test-cov  # or: pytest --cov
```

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and quality checks (`just check && just test`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines (coming soon).

## Roadmap

### Recently Completed

✅ **Real-time MIDI playback with interactive TUI** (Phase 3, Nov 2025)

- Sub-5ms event scheduler, tempo tracking, keyboard controls (Space/Q/R)

✅ **Generative & modulation features** (Phase 6)

- Random pattern generation, Bezier curves, LFO, envelope modulation

✅ **Diagnostic output formats** (Phase 1)

- JSON, CSV, Rich table display for analysis and debugging

✅ **Core compilation pipeline** (MVP Complete)

- Lark parser, alias resolution, variables, loops, sweeps, validation
- 1090+ tests, 72.53% code coverage

### Planned Features

- REPL mode for interactive editing (Phase 2)
- MIDI Learn and device interrogation
- MIDI 2.0 support
- OSC integration
- Python/Lua scripting for advanced automation

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
- **Issue Tracker**: [GitHub Issues](https://github.com/cjgdev/midi-markdown/issues)

---

**Built with ❤️ for musicians by musicians** — If MMD helps your workflow, give us a ⭐ on GitHub!
