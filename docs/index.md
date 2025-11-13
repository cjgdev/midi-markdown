# MIDI Markdown Documentation

Welcome to the MIDI Markdown (MMD) documentation. MMD is a human-readable, text-based format for creating MIDI sequences, designed for live performance automation and compositional workflows.

---

## Quick Start

- **[Getting Started](getting-started/quickstart.md)** - Create your first MIDI file in 5 minutes
- **[Installation Guide](getting-started/installation.md)** - Detailed setup instructions for all platforms
- **[Claude Code Skills](getting-started/claude-skills.md)** - Optional AI assistant skills for enhanced development (Claude Code users)

---

## User Guides

Learn how to use MMD effectively:

- **[Basic Syntax](user-guide/mmd-syntax.md)** - Fundamentals: frontmatter, timing, commands
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

- **[Language Specification](reference/specification.md)** - Complete MMD specification (1,600+ lines)
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

- **[Examples Guide](getting-started/examples-guide.md)** - Complete guide with learning path and feature matrix

**Quick Links:**
- [01_hello_world.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/00_basics/01_hello_world.mmd) - Simplest possible MMD file
- [01_multi_channel_basic.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/02_midi_features/01_multi_channel_basic.mmd) - Multiple MIDI channels
- [10_comprehensive_song.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/03_advanced/10_comprehensive_song.mmd) - All features combined
- [01_device_import.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/04_device_libraries/01_device_import.mmd) - Device library imports
- [01_random_humanization.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/05_generative/01_random_humanization.mmd) - Random values for humanization
- [03_generative_ambient.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/05_generative/03_generative_ambient.mmd) - Generative music techniques

---

## Developer Documentation

Architecture and implementation details:

- **[Architecture Overview](developer-guide/architecture.md)** - System architecture and compilation pipeline
- **[Parser Design](developer-guide/architecture/parser.md)** - Parser architecture and Lark grammar
- **[Parser Design](developer-guide/architecture/parser.md)** - Parser and lexer implementation details
- **[IR Specification](developer-guide/ir-specification.md)** - Intermediate representation format
- **[Contributing Guide](developer-guide/contributing.md)** - How to contribute to the project

---

## Device Libraries

Pre-built libraries for controlling MIDI hardware:

- **[Neural DSP Quad Cortex](https://github.com/cjgdev/midi-markdown/blob/main/devices/quad_cortex.mmd)** - 86 aliases for Quad Cortex control
- **[Eventide H90](https://github.com/cjgdev/midi-markdown/blob/main/devices/eventide_h90.mmd)** - 61 aliases for H90 harmonizer/effects
- **[Line 6 Helix](https://github.com/cjgdev/midi-markdown/blob/main/devices/helix.mmd)** - 49 aliases for Helix control
- **[HX Stomp](https://github.com/cjgdev/midi-markdown/blob/main/devices/hx_stomp.mmd)** - HX Stomp control
- **[HX Effects](https://github.com/cjgdev/midi-markdown/blob/main/devices/hx_effects.mmd)** - HX Effects control
- **[HX Stomp XL](https://github.com/cjgdev/midi-markdown/blob/main/devices/hx_stomp_xl.mmd)** - HX Stomp XL control

See the [Device Library Guide](user-guide/device-libraries.md) to learn more.

---

## Additional Resources

- **[specification.md](reference/specification.md)** - Authoritative language specification
- **[CLAUDE.md](https://github.com/cjgdev/midi-markdown/blob/main/CLAUDE.md)** - Developer context and architecture (for AI assistants)
- **[README.md](https://github.com/cjgdev/midi-markdown/blob/main/README.md)** - Project overview and quick start
- **[Tests](https://github.com/cjgdev/midi-markdown/tree/main/tests)** - Test suite with 1264+ tests

---

## Documentation Status

✅ = Complete | 🚧 = Coming Soon

| Document | Status |
|----------|--------|
| Getting Started | ✅ Complete |
| Installation | ✅ Complete |
| Basic Syntax Guide | ✅ Complete |
| Timing Systems Guide | ✅ Complete |
| Alias System Guide | ✅ Complete |
| Device Libraries Guide | ✅ Complete |
| Real-time Playback Guide | ✅ Complete |
| Computed Values Guide | ✅ Complete |
| Modulation Guide | ✅ Complete |
| Generative Music Guide | ✅ Complete |
| CLI Reference | ✅ Complete |
| Alias API Reference | ✅ Complete |
| MIDI Commands Reference | ✅ Complete |
| Architecture Overview | ✅ Complete |
| IR Specification | ✅ Complete |
| Parser Design | ✅ Complete |
| Lexer Design | ✅ Complete |
| Contributing Guide | ✅ Complete |

---

## Need Help?

- **Examples**: Start with [getting-started/examples-guide.md](getting-started/examples-guide.md)
- **CLI Help**: Run `uv run mmdc --help`
- **Issues**: Report bugs on [GitHub](https://github.com/cjgdev/midi-markdown/issues)
- **Specification**: See [specification.md](reference/specification.md) for complete reference

---

**Version**: 0.1.0
**Last Updated**: 2025-11-05
