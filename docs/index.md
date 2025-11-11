# MIDI Markdown Documentation

Welcome to the MIDI Markdown (MML) documentation. MMD is a human-readable, text-based format for creating MIDI sequences, designed for live performance automation and compositional workflows.

---

## Quick Start

- **[Getting Started](getting-started.md)** - Create your first MIDI file in 5 minutes
- **[Installation Guide](installation.md)** - Detailed setup instructions for all platforms

---

## User Guides

Learn how to use MMD effectively:

- **[Basic Syntax](user-guide/mml-syntax.md)** - Fundamentals: frontmatter, timing, commands
- **[Timing Systems](user-guide/timing-system.md)** - Absolute, musical, relative, and simultaneous timing
- **[Alias System](user-guide/alias-system.md)** - Create reusable command shortcuts
- **[Device Libraries](user-guide/device-libraries.md)** - Control MIDI hardware with high-level commands
- **[Real-time Playback](user-guide/realtime-playback.md)** - Live MIDI playback with interactive Terminal UI
- **[Computed Values](user-guide/computed_values.md)** - Variables, expressions, and computed parameters
- **[Modulation](user-guide/modulation.md)** - Curves, waveforms, and envelopes
- **[Generative Music](user-guide/generative-music.md)** - Random values and algorithmic composition

---

## Reference Documentation

Complete API and command references:

- **[Language Specification](../spec.md)** - Complete MMD specification (1,600+ lines)
- **[CLI Commands](cli-reference/overview.md)** - Command-line interface reference
- **[Alias API](user-guide/alias-api.md)** - Alias definition and parameter syntax
- **[MIDI Commands](user-guide/midi-commands.md)** - Quick MIDI command reference
- **[Modulation Reference](reference/modulation-reference.md)** - Curves, waveforms, and envelopes
- **[Random Expressions](reference/random-expressions.md)** - Random value generation
- **[FAQ](reference/faq.md)** - Frequently asked questions
- **[Troubleshooting](reference/troubleshooting.md)** - Common issues and solutions

---

## Examples

Progressive learning path with 16 examples:

- **[Examples README](../examples/README.md)** - Complete guide with learning path and feature matrix

**Quick Links:**
- [00_hello_world.mmd](../examples/00_basics/00_hello_world.mmd) - Simplest possible MMD file
- [05_multi_channel_basic.mmd](../examples/02_midi_features/05_multi_channel_basic.mmd) - Multiple MIDI channels
- [09_comprehensive_song.mmd](../examples/03_advanced/09_comprehensive_song.mmd) - All features combined
- [13_device_import.mmd](../examples/04_device_libraries/13_device_import.mmd) - Device library imports

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

- **[Neural DSP Quad Cortex](../devices/quad_cortex.mmd)** - 86 aliases for Quad Cortex control
- **[Eventide H90](../devices/eventide_h90.mmd)** - 61 aliases for H90 harmonizer/effects
- **[Kemper Profiler](../devices/kemper_profiler.mmd)** - 51 aliases for Kemper control
- **[Line 6 Helix](../devices/line6_helix.mmd)** - 49 aliases for Helix control

See the [Device Library Creation Guide](guides/device-libraries.md) to create your own.

---

## Additional Resources

- **[spec.md](../spec.md)** - Authoritative language specification
- **[CLAUDE.md](../CLAUDE.md)** - Developer context and architecture (for AI assistants)
- **[README.md](../README.md)** - Project overview and quick start
- **[Tests](../tests/)** - Test suite with 1090+ tests (840+ unit + 250+ integration)

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
| Real-time Playback Guide | ✅ Complete |
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
- **CLI Help**: Run `uv run mmdc --help`
- **Issues**: Report bugs on [GitHub](https://github.com/cjgdev/midi-markdown/issues)
- **Specification**: See [spec.md](../spec.md) for complete reference

---

**Version**: 0.1.0
**Last Updated**: 2025-11-05
