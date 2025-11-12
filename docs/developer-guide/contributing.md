# Contributing to MIDI Markdown

**Date**: 2025-11-08
**Version**: 0.1.0

Thank you for your interest in contributing to MIDI Markdown (MMD)! This document provides guidelines for developers who want to contribute to the codebase.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Setup](#development-setup)
3. [Project Structure](#project-structure)
4. [Development Workflow](#development-workflow)
5. [Code Style Guidelines](#code-style-guidelines)
6. [Testing Guidelines](#testing-guidelines)
7. [Pull Request Process](#pull-request-process)
8. [Issue Guidelines](#issue-guidelines)
9. [Documentation Guidelines](#documentation-guidelines)
10. [Release Process](#release-process)

---

## Getting Started

### Prerequisites

- **Python 3.12+** (required for modern type hints)
- **UV** (modern Python package manager) or `pip`
- **Git** for version control
- **Just** (optional but recommended for convenient commands)

### Quick Start

```bash
# Clone repository
git clone https://github.com/cjgdev/midi-markdown.git
cd midi-markdown

# Install dependencies with UV
uv sync

# Or with pip
pip install -e ".[dev]"

# Run tests to verify setup
uv run pytest

# Or with justfile (recommended)
just test
```

### First Contribution Ideas

Good first issues for new contributors:

- Fix typos or improve documentation
- Add more device libraries (devices/)
- Add more example MMD files (examples/)
- Improve error messages
- Add unit tests for uncovered code
- Fix "good first issue" labeled GitHub issues

---

## Development Setup

### Installing UV (Recommended)

UV is a fast, modern Python package manager:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv
```

### Installing Just (Optional)

Just is a command runner for convenient development tasks:

```bash
# macOS
brew install just

# Linux
cargo install just

# Windows
scoop install just
```

See [justfile](../../justfile) for all available commands.

### Virtual Environment

UV automatically manages virtual environments in `.venv/`:

```bash
# Activate manually (optional - uv run handles this)
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Install dependencies
uv sync

# Install with dev dependencies
uv sync --all-extras
```

### IDE Setup

**VS Code** (recommended):
- Install Python extension
- Configure interpreter: `.venv/bin/python`
- Enable format on save (Ruff)
- Enable type checking (mypy)

**PyCharm**:
- Configure interpreter: `.venv/bin/python`
- Enable Ruff as external formatter
- Enable mypy type checking

### Verifying Setup

```bash
# Run all tests
just test

# Run code quality checks
just check

# Format and lint
just fix

# Full CI pipeline
just ci
```

---

## Project Structure

```
midi-markdown/
├── src/midi_markdown/          # Source code (8,405 lines)
│   ├── parser/                 # Lark-based parser
│   ├── alias/                  # Alias resolution
│   ├── expansion/              # Loop/sweep/variable expansion
│   ├── core/                   # IR layer (Phase 0)
│   ├── codegen/                # Output generation
│   ├── runtime/                # Real-time playback (Phase 3)
│   ├── diagnostics/            # Event display (Phase 1)
│   ├── cli/                    # Typer CLI
│   └── utils/                  # Validation and utilities
├── tests/                      # Test suite (10,681 lines)
│   ├── unit/                   # Unit tests (598 tests)
│   ├── integration/            # Integration tests (242 tests)
│   └── fixtures/               # Test MMD files
├── examples/                   # 16 example MMD files
├── devices/                    # 6 MIDI device libraries
├── docs/                       # Documentation
│   ├── developer-guide/        # Developer docs (you are here)
│   ├── user-guide/             # User documentation
│   ├── reference/              # API reference
│   └── tutorials/              # Step-by-step tutorials
├── pyproject.toml              # Project configuration
├── justfile                    # Development commands
├── README.md                   # Project README
├── CLAUDE.md                   # AI assistant instructions
└── spec.md                     # Complete MMD specification
```

### Key Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | Dependencies, build config, tool settings |
| `justfile` | Development command shortcuts |
| `src/midi_markdown/__init__.py` | Package version, public API |
| `src/midi_markdown/parser/mml.lark` | Lark grammar definition |
| `src/midi_markdown/core/ir.py` | IR data structures |
| `tests/conftest.py` | Pytest fixtures and configuration |

---

## Development Workflow

### Using Justfile (Recommended)

The project includes a comprehensive `justfile` with convenient shortcuts:

```bash
# Quick reference
just                    # Show all available commands
just --list             # Same as above

# Testing
just test               # Run all tests
just test-cov           # Run tests with coverage report
just test-unit          # Unit tests only (598 tests)
just test-integration   # Integration tests only (242 tests)
just smoke              # Quick smoke test (fastest tests)

# Code quality
just fmt                # Format code with Ruff
just lint               # Lint code with Ruff
just lint-fix           # Auto-fix linting issues
just typecheck          # Run mypy type checking
just check              # Run all checks (fmt + lint + typecheck)
just fix                # Auto-fix all issues (fmt + lint-fix)
just qa                 # Quality assurance (fmt + lint-fix + test)
just ci                 # CI pipeline (check + test-cov)

# CLI commands
just run [ARGS]         # Run mmdc CLI
just compile INPUT OUTPUT  # Compile MMD file
just validate FILE      # Validate MMD file

# Validation
just validate-devices   # Validate all device libraries
just validate-examples  # Validate all examples
just validate-all       # Validate everything

# Utilities
just clean              # Clean build artifacts
just examples           # Compile all examples
just stats              # Show code statistics
just info               # Show project info
```

### Manual Commands

If not using `just`, use these commands directly:

```bash
# Run tests
uv run pytest                              # All tests
uv run pytest -m unit                      # Unit tests only
uv run pytest -m integration               # Integration tests only
uv run pytest tests/unit/test_parser.py    # Specific file
uv run pytest -x                           # Stop on first failure
uv run pytest --lf                         # Rerun last failed tests

# Code quality
uv run ruff format .             # Format code
uv run ruff check .              # Lint code
uv run ruff check --fix .        # Auto-fix issues
uv run mypy src                  # Type check

# Run CLI
uv run mmdc --help
uv run mmdc compile examples/00_basics/00_hello_world.mmd
```

### Git Workflow

We follow a standard Git workflow:

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes
# ... edit files ...

# Run tests and checks
just qa

# Commit changes
git add .
git commit -m "feat: add new feature"

# Push to GitHub
git push origin feature/my-feature

# Create pull request on GitHub
```

### Commit Message Format

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring (no behavior change)
- `test`: Adding or updating tests
- `chore`: Build, tooling, dependencies

**Examples**:
```
feat(parser): add support for MIDI 2.0 messages

Implements parsing for MIDI 2.0 channel voice messages including
per-note pitch bend and per-note controllers.

Closes #123

---

fix(cli): correct timing display in inspect command

The inspect command was displaying milliseconds as seconds.
Fixed unit conversion.

---

docs(contributing): add section on commit message format
```

---

## Code Style Guidelines

### Python Style

We follow **PEP 8** with Ruff enforcement:

- **Line length**: 120 characters (not 79)
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Double quotes for strings
- **Imports**: Sorted alphabetically, grouped (stdlib, third-party, local)
- **Type hints**: Required for all public functions/methods

### Modern Python Patterns

We use **Python 3.12+ features**:

```python
# Modern type hints (NOT Optional[T])
def parse_file(path: str | None = None) -> MMLDocument | None:
    ...

# Future annotations (at top of every file)
from __future__ import annotations

# Dataclasses for data structures
from dataclasses import dataclass

@dataclass
class MIDIEvent:
    time: int
    type: EventType
    channel: int

# Match statements (Python 3.10+)
match event_type:
    case "note_on":
        ...
    case "cc":
        ...

# Type aliases
EventList = list[MIDIEvent]
```

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `MMLParser`, `CommandExpander`)
- **Functions/methods**: `snake_case` (e.g., `parse_file`, `expand_loops`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_PPQ`, `MAX_MIDI_VALUE`)
- **Private**: `_leading_underscore` (e.g., `_internal_helper`)
- **Type vars**: `T`, `K`, `V` (single letter uppercase)

### Docstrings

Use **Google-style docstrings**:

```python
def compile_ast_to_ir(document: MMLDocument, ppq: int = 480) -> IRProgram:
    """Compile MMD document AST to IR program.

    This is the main entry point for compilation. It orchestrates:
    1. Event generation from AST commands
    2. Timing resolution (absolute, musical, relative)
    3. Expansion (loops, sweeps, variables)
    4. Validation (ranges, monotonicity)
    5. Time computation (ticks → seconds using tempo map)

    Args:
        document: Parsed MMD document AST
        ppq: Pulses per quarter note (MIDI resolution)

    Returns:
        IRProgram ready for output or execution

    Raises:
        ValidationError: If MIDI values are out of range
        ExpansionError: If loops/sweeps/variables fail to expand

    Example:
        >>> from midi_markdown.parser.parser import MMLParser
        >>> parser = MMLParser()
        >>> doc = parser.parse_file("song.mmd")
        >>> ir = compile_ast_to_ir(doc, ppq=480)
        >>> print(f"Duration: {ir.duration_seconds}s")
    """
    ...
```

### Type Hints

Type hints are **required** for:
- All public functions and methods
- All class attributes (use dataclasses)
- Function return values

Type hints are **optional** for:
- Private functions (encouraged but not required)
- Local variables (inferred by mypy)

### Error Handling

Use custom exceptions with helpful messages:

```python
# Good
raise ValidationError(
    f"MIDI note {note} out of range (0-127)",
    location=SourceLocation(line=12, column=5, file="song.mmd")
)

# Bad
raise ValueError("Invalid note")
```

### Comments

- **Why, not what**: Explain reasoning, not obvious code
- **TODOs**: Use `# TODO(username): description` format
- **FIXMEs**: Use `# FIXME(username): description` format

```python
# Good
# Use binary search for O(log n) lookup instead of linear O(n)
index = bisect.bisect_left(sorted_events, target_time)

# Bad
# Find the index
index = bisect.bisect_left(sorted_events, target_time)
```

---

## Testing Guidelines

### Test Organization

Tests are organized by type:

```
tests/
├── unit/                   # Unit tests (598 tests)
│   ├── test_parser.py
│   ├── test_timing.py
│   ├── test_midi_commands.py
│   ├── test_aliases.py
│   └── ...
├── integration/            # Integration tests (242 tests)
│   ├── test_cli.py
│   ├── test_end_to_end.py
│   ├── test_device_libraries.py
│   └── ...
└── fixtures/               # Test data
    ├── valid/              # Valid MMD files
    └── invalid/            # Invalid MMD files
```

### Test Markers

Use pytest markers to categorize tests:

```python
import pytest

@pytest.mark.unit
def test_parse_absolute_timing():
    """Test absolute timing parsing."""
    ...

@pytest.mark.integration
@pytest.mark.slow
def test_compile_large_file():
    """Test compilation of 1000+ event file."""
    ...

@pytest.mark.cli
def test_compile_command():
    """Test compile CLI command."""
    ...
```

**Run specific markers**:
```bash
pytest -m unit              # Unit tests only
pytest -m integration       # Integration tests only
pytest -m "not slow"        # Skip slow tests
```

### Test Fixtures

Use pytest fixtures for common setup:

```python
@pytest.fixture
def parser():
    """Provide MMLParser instance."""
    return MMLParser()

@pytest.fixture
def sample_mml():
    """Provide sample MMD source code."""
    return """---
title: "Test Song"
---

[00:00.000]
- tempo 120
- pc 1.0
"""

def test_parse_frontmatter(parser, sample_mml):
    """Test frontmatter parsing."""
    doc = parser.parse_string(sample_mml)
    assert doc.frontmatter["title"] == "Test Song"
```

### Writing Good Tests

**Good test characteristics**:
- **Descriptive names**: `test_parse_absolute_timing_with_milliseconds()`
- **Single assertion focus**: Test one thing per test
- **Clear arrange/act/assert**: Separate setup, execution, verification
- **No external dependencies**: Use mocks for file I/O, network
- **Fast**: Unit tests should run in < 100ms

**Test template**:
```python
def test_feature_name():
    """Brief description of what is being tested."""
    # Arrange - set up test data
    input_data = create_test_input()

    # Act - execute the code under test
    result = function_under_test(input_data)

    # Assert - verify the result
    assert result == expected_output
```

### Coverage Goals

- **Overall**: 80%+ code coverage
- **Critical paths**: 90%+ (parser, IR compiler, codegen)
- **New code**: 100% coverage required for PRs

**Check coverage**:
```bash
just test-cov                # Run tests with coverage
open htmlcov/index.html      # View HTML coverage report
```

---

## Pull Request Process

### Before Opening PR

1. **Run full test suite**: `just test`
2. **Run code quality checks**: `just check`
3. **Fix any issues**: `just fix`
4. **Update documentation** if needed
5. **Add tests** for new features
6. **Update CHANGELOG.md** (if applicable)

### PR Guidelines

**Good PR characteristics**:
- **Small and focused**: One feature/fix per PR
- **Clear description**: What, why, how
- **Tests included**: 100% coverage for new code
- **Documentation updated**: User-facing changes documented
- **Commit history clean**: Squash WIP commits
- **CI passing**: All checks green

**PR template**:
```markdown
## Description
Brief description of changes.

## Motivation
Why is this change needed?

## Changes
- Added X feature
- Fixed Y bug
- Refactored Z component

## Testing
- Added unit tests for X
- Added integration test for Y
- Manual testing: compiled 10 example files

## Checklist
- [ ] Tests pass (`just test`)
- [ ] Code formatted (`just fmt`)
- [ ] Type checking passes (`just typecheck`)
- [ ] Documentation updated
- [ ] CHANGELOG.md updated (if applicable)
```

### Review Process

1. **Automated checks**: CI must pass (tests, linting, type checking)
2. **Code review**: At least one maintainer approval required
3. **Discussion**: Address reviewer feedback
4. **Approval**: Maintainer approves PR
5. **Merge**: Squash and merge to main

### After Merge

- **Delete branch**: GitHub will prompt to delete feature branch
- **Release**: Maintainer will tag release if needed
- **Close issues**: Link to PR in issue comments

---

## Issue Guidelines

### Reporting Bugs

Use the bug report template:

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1. Create MMD file with...
2. Run `mmdc compile ...`
3. See error

**Expected behavior**
What should happen instead.

**Actual behavior**
What actually happened (error message, incorrect output, etc.)

**Environment**
- OS: macOS 14.0
- Python: 3.12.0
- MMD version: 0.1.0

**MML source code**
```mml
[00:00.000]
- cc 1.999.100  # Invalid CC number
```

**Error message** (if applicable)
```
ValidationError: CC controller 999 out of range (0-127)
  → song.mmd:2:5
```
```

### Feature Requests

Use the feature request template:

```markdown
**Feature description**
Clear description of the proposed feature.

**Motivation**
Why is this feature needed? What problem does it solve?

**Proposed syntax** (for language features)
```mml
# Example of how the feature would be used
@loop 4 [00:00.000] +500ms
  - note_on 1.60 100 500ms
@end
```

**Alternatives considered**
Other ways to achieve the same goal.

**Additional context**
Any other context, screenshots, examples.
```

### Issue Labels

| Label | Description |
|-------|-------------|
| `bug` | Something isn't working |
| `enhancement` | New feature or request |
| `documentation` | Documentation improvements |
| `good first issue` | Good for new contributors |
| `help wanted` | Extra attention needed |
| `question` | Further information requested |
| `wontfix` | This will not be worked on |

---

## Documentation Guidelines

### User Documentation

User-facing documentation lives in `docs/`:

- **Getting Started**: Installation, quickstart, first song
- **User Guide**: MMD syntax, timing, commands, aliases
- **Tutorials**: Step-by-step examples
- **Reference**: CLI commands, error codes, FAQ
- **Device Libraries**: Available device libraries

### Developer Documentation

Developer documentation lives in `docs/developer-guide/`:

- **Architecture**: System design, pipeline, components
- **IR Specification**: IR layer details
- **Contributing**: This document
- **Parser Design**: Parser internals
- **Lexer Design**: Lexer internals

### Markdown Style

- **Headers**: Use ATX style (`# Header`)
- **Code blocks**: Specify language (```python, ```bash, ```mml)
- **Links**: Use reference-style for readability
- **Tables**: Use GitHub-flavored markdown tables
- **Line length**: 120 characters for prose

### Code Examples

Include working code examples:

```python
# Good - complete, runnable example
from midi_markdown.parser.parser import MMLParser

parser = MMLParser()
doc = parser.parse_file("song.mmd")
print(f"Title: {doc.frontmatter['title']}")

# Bad - incomplete snippet
parser = MMLParser()
doc = parser.parse_file(...)  # What file?
```

---

## Release Process

### Versioning

We use **Semantic Versioning** (semver):

- **MAJOR**: Breaking changes (1.0.0 → 2.0.0)
- **MINOR**: New features, backward compatible (0.1.0 → 0.2.0)
- **PATCH**: Bug fixes, backward compatible (0.1.0 → 0.1.1)

### Release Checklist

1. **Update version** in `pyproject.toml` and `src/midi_markdown/__init__.py`
2. **Update CHANGELOG.md** with release notes
3. **Run full test suite**: `just ci`
4. **Build package**: `uv build`
5. **Tag release**: `git tag v0.1.0`
6. **Push tag**: `git push origin v0.1.0`
7. **Create GitHub release** with notes
8. **Publish to PyPI**: `uv publish`

### CHANGELOG Format

Use [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
## [0.2.0] - 2025-11-08

### Added
- Real-time MIDI playback with TUI
- Event scheduler with sub-5ms precision
- Keyboard controls (Space, Q, R)

### Changed
- Improved error messages with source context
- Updated IR layer with query methods

### Fixed
- Timing validation now handles simultaneous events
- CLI inspect command displays correct units

### Deprecated
- Old MIDI generator API (use codegen/midi_file.py)

## [0.1.0] - 2025-10-29

Initial release.
```

---

## Getting Help

### Resources

- **Documentation**: [docs/index.md](../index.md)
- **Specification**: [specification.md](../reference/specification.md)
- **Examples**: [examples/](https://github.com/cjgdev/midi-markdown/tree/main/examples)
- **GitHub Issues**: https://github.com/cjgdev/midi-markdown/issues
- **GitHub Discussions**: https://github.com/cjgdev/midi-markdown/discussions

### Communication

- **Bug reports**: Open GitHub issue
- **Feature requests**: Open GitHub discussion
- **Questions**: GitHub discussions or issues
- **Security issues**: Email maintainer directly

### Maintainers

- **Chris Gilbert** (@cjgdev) - Project creator and maintainer

---

## Code of Conduct

We are committed to providing a welcoming and inclusive environment:

- **Be respectful**: Treat everyone with respect and kindness
- **Be collaborative**: Work together constructively
- **Be inclusive**: Welcome diverse perspectives
- **Be professional**: Focus on what's best for the project

Unacceptable behavior will not be tolerated. Report issues to the maintainers.

---

## License

By contributing to MIDI Markdown, you agree that your contributions will be licensed under the **MIT License**.

---

## Acknowledgments

Thank you for contributing to MIDI Markdown! Your contributions help make MMD better for everyone.

---

**Document Version**: 1.0
**Last Updated**: 2025-11-08
