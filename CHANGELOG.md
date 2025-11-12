# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Release workflow and version management system

## [0.1.0] - 2025-11-08

### Added
- Initial MVP release
- Complete MIDI Markdown parser with Lark-based LALR grammar
- Support for all MIDI 1.0 commands (note on/off, CC, PC, pitch bend, aftertouch, SysEx)
- Four timing paradigms: absolute, musical, relative, simultaneous
- Device library system with 6 device libraries (Quad Cortex, H90, Helix, HX Stomp, HX Effects, HX Stomp XL)
- Alias system for device-specific commands with parameter validation
- Advanced features: loops (@loop), sweeps (@sweep), variables (@define), expressions
- Generative music support with random() expressions
- Enhanced modulation: Bezier curves, waveforms (LFO), envelopes (ADSR/AR/AD)
- Real-time MIDI playback with TUI (sub-5ms timing precision)
- Multiple output formats: MIDI files, JSON, CSV, table display
- CLI with commands: compile, validate, check, play, inspect, version
- Comprehensive test suite: 1264 tests with 72.53% coverage
- 35 working examples across 7 categories
- Complete documentation: user guides, developer guides, tutorials
- MkDocs documentation site
- GitHub Actions CI/CD workflows
- PyInstaller-based standalone executables for Linux, Windows, macOS

### Documentation
- Complete language specification (spec.md)
- Architecture overview (docs/developer-guide/architecture.md)
- Developer guides: parser patterns, timing system, anti-patterns, common tasks
- User guides: quickstart, syntax reference, device libraries, tutorials
- CLAUDE.md for AI-assisted development
- 35 example files with learning paths
- API reference documentation

### Developer Experience
- Modern Python 3.12+ with type hints throughout
- UV package manager for fast dependency management
- Ruff for linting and formatting
- MyPy for type checking
- pytest with comprehensive test markers
- Justfile with 50+ development commands
- Pre-commit hooks ready (optional)

## Version History

### Version Numbering

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version for incompatible API/syntax changes
- **MINOR** version for new features (backwards-compatible)
- **PATCH** version for bug fixes (backwards-compatible)

### Release Types

- **Stable**: Production-ready releases (v1.0.0, v1.1.0, etc.)
- **Pre-release**: Alpha/beta releases (v0.1.0, v0.2.0-alpha.1, etc.)
- **Development**: Unreleased changes in main branch

[Unreleased]: https://github.com/cjgdev/midi-markdown/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/cjgdev/midi-markdown/releases/tag/v0.1.0
