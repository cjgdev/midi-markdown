# MIDI Markup Language Documentation

Welcome to the MIDI Markup Language (MML) documentation. MML is a human-readable, text-based format for creating MIDI sequences, designed for live performance automation and compositional workflows.

---

## Quick Start

- **[Getting Started](getting-started.md)** - Create your first MIDI file in 5 minutes
- **[Installation Guide](installation.md)** - Detailed setup instructions for all platforms

---

## User Guides

Learn how to use MML effectively:

- **[Basic Syntax](guides/basic-syntax.md)** - Fundamentals: frontmatter, timing, commands *(Coming Soon)*
- **[Timing Systems](guides/timing-systems.md)** - Absolute, musical, relative, and simultaneous timing *(Coming Soon)*
- **[Alias System](guides/alias-system.md)** - Create reusable command shortcuts
- **[Device Libraries](guides/device-libraries.md)** - Control MIDI hardware with high-level commands
- **[Advanced Features](guides/variables-loops-sweeps.md)** - Variables, loops, and sweep automation *(Coming Soon)*

---

## Reference Documentation

Complete API and command references:

- **[Language Specification](../spec.md)** - Complete MML specification (1,300+ lines)
- **[CLI Commands](reference/cli-commands.md)** - Command-line interface reference
- **[Alias API](reference/alias-api.md)** - Alias definition and parameter syntax
- **[MIDI Commands](reference/midi-commands.md)** - Quick MIDI command reference *(Coming Soon)*
- **[Grammar](grammar/GRAMMAR_DOCUMENTATION.md)** - Lark grammar documentation

---

## Examples

Progressive learning path with 16 examples:

- **[Examples README](../examples/README.md)** - Complete guide with learning path and feature matrix

**Quick Links:**
- [00_hello_world.mml](../examples/00_hello_world.mml) - Simplest possible MML file
- [05_multi_channel_basic.mml](../examples/05_multi_channel_basic.mml) - Multiple MIDI channels
- [09_comprehensive_song.mml](../examples/09_comprehensive_song.mml) - All features combined
- [13_device_import.mml](../examples/13_device_import.mml) - Device library imports

---

## Developer Documentation

Architecture and implementation details:

- **[Architecture Overview](architecture/overview.md)** - System architecture *(Coming Soon)*
- **[Compilation Pipeline](architecture/compilation-pipeline.md)** - Stage-by-stage pipeline *(Coming Soon)*
- **[Parser Design](architecture/parser.md)** - Parser architecture and Lark grammar
- **[Lexer Design](architecture/lexer.md)** - Lexer implementation details
- **[Quick References](architecture/quick-reference/)** - Parser and lexer quick lookups
- **[Contributing Guide](contributing.md)** - How to contribute to the project *(Coming Soon)*

---

## Device Libraries

Pre-built libraries for controlling MIDI hardware:

- **[Neural DSP Quad Cortex](../devices/quad_cortex.mml)** - 86 aliases for Quad Cortex control
- **[Eventide H90](../devices/eventide_h90.mml)** - 61 aliases for H90 harmonizer/effects
- **[Kemper Profiler](../devices/kemper_profiler.mml)** - 51 aliases for Kemper control
- **[Line 6 Helix](../devices/line6_helix.mml)** - 49 aliases for Helix control

See the [Device Library Creation Guide](guides/device-libraries.md) to create your own.

---

## Additional Resources

- **[spec.md](../spec.md)** - Authoritative language specification
- **[CLAUDE.md](../CLAUDE.md)** - Developer context and architecture (for AI assistants)
- **[README.md](../README.md)** - Project overview and quick start
- **[Tests](../tests/)** - Test suite with 747 tests (561 unit + 186 integration)

---

## Documentation Status

✅ = Complete | 🚧 = Coming Soon

| Document | Status |
|----------|--------|
| Getting Started | ✅ Complete |
| Installation | ✅ Complete |
| Basic Syntax Guide | 🚧 Coming Soon |
| Timing Systems Guide | 🚧 Coming Soon |
| Alias System Guide | ✅ Complete |
| Device Libraries Guide | ✅ Complete |
| Advanced Features Guide | 🚧 Coming Soon |
| CLI Reference | ✅ Complete |
| Alias API Reference | ✅ Complete |
| MIDI Commands Reference | 🚧 Coming Soon |
| Architecture Overview | 🚧 Coming Soon |
| Compilation Pipeline | 🚧 Coming Soon |
| Parser Design | ✅ Complete |
| Lexer Design | ✅ Complete |
| Contributing Guide | 🚧 Coming Soon |

---

## Need Help?

- **Examples**: Start with [examples/README.md](../examples/README.md)
- **CLI Help**: Run `uv run midimarkup --help`
- **Issues**: Report bugs on [GitHub](https://github.com/anthropics/midi-markdown/issues)
- **Specification**: See [spec.md](../spec.md) for complete reference

---

**Version**: 0.1.0
**Last Updated**: 2025-11-01
