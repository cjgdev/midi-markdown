# Contributing to MIDI Markdown

Thank you for your interest in contributing to MIDI Markdown! Whether you're a musician, developer, MIDI enthusiast, or device owner, there are many ways to help improve the project. We welcome all contributions, from bug reports and documentation to device libraries and code improvements.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Help](#getting-help)
- [Development Setup](#development-setup)
- [Ways to Contribute](#ways-to-contribute)
- [Device Library Creation](#device-library-creation)
- [Reporting Issues](#reporting-issues)
- [Pull Request Process](#pull-request-process)
- [Code Style & Standards](#code-style--standards)
- [Testing Guidelines](#testing-guidelines)

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers via [GitHub Issues](https://github.com/cjgdev/midi-markdown/issues).

## Getting Help

- **Documentation**: Start with [docs/index.md](docs/index.md) for comprehensive guides
- **Getting Started**: [docs/getting-started.md](docs/getting-started.md) for first steps
- **Device Library Guide**: [docs/guides/device-libraries.md](docs/guides/device-libraries.md)
- **Examples**: [examples/README.md](examples/README.md) with runnable examples
- **Specification**: [spec.md](spec.md) for detailed technical details
- **Issues**: [GitHub Issues](https://github.com/cjgdev/midi-markdown/issues) for questions

## Development Setup

### Prerequisites

- **Python 3.12+** (check with `python --version`)
- **Git** for version control
- **UV** package manager (recommended) or pip

### Step 1: Clone the Repository

```bash
git clone https://github.com/cjgdev/midi-markdown.git
cd midi-markdown
```

### Step 2: Set Up Virtual Environment

**Using UV (recommended - fast!):**
```bash
uv sync  # Creates virtual environment and installs all dependencies
```

**Using pip:**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### Step 3: Verify Installation

```bash
# Check that the CLI works
uv run mmdc --version

# Run the test suite
just test  # or: uv run pytest

# Run code quality checks
just check  # or: uv run ruff check . && mypy src
```

## Ways to Contribute

### Device Libraries (Great First Contribution!)

Creating device libraries is the easiest way to contribute—no complex coding required. If you have a MIDI device with documented CC/PC mappings, you can create a library. See [Device Library Creation](#device-library-creation) below.

### Bug Reports

Found a bug? Help us fix it:

1. **Check existing issues** to avoid duplicates
2. **Create a detailed issue** with:
   - Clear title describing the problem
   - Steps to reproduce (MML example preferred)
   - Expected vs actual behavior
   - Python version and OS
   - Error message and stack trace (if applicable)

**Example bug report:**
```
Title: Pitch bend range validation fails for negative values

Description:
When using negative pitch bend values, the compiler crashes with a
validation error instead of properly handling the range.

Steps to reproduce:
1. Create file with: `- pitch_bend 1.-5000`
2. Run: `mmdc compile test.mmd -o test.mid`

Expected: Compiles successfully (pitch bend range is -8192 to +8191)
Actual: ValidationError: pitch_bend value -5000 out of range

Environment:
- Python 3.12.1
- MIDI Markdown 0.1.0
- macOS 14.2
```

### Feature Requests

Have an idea? Share it:

1. **Check existing discussions** in GitHub Issues
2. **Create a feature request** with:
   - Clear title and description
   - Use case (why you need this feature)
   - Example of how it would be used
   - Alternatives considered

**Example feature request:**
```
Title: Add @repeat directive for shorter loop syntax

Description:
The @loop directive is powerful but verbose for simple repetitions.
A shorter @repeat syntax would improve readability.

Current syntax:
@loop 4 "repeat 4 times"
  - note_on 1.60 80
@end

Proposed syntax:
@repeat 4
  - note_on 1.60 80
@end

Use case: Live performance files with many repeated patterns
```

### Code Contributions

Focus areas for development:

- **Parser improvements**: Better error messages, recovery, performance
- **New MIDI features**: MPE support, MIDI 2.0, system messages
- **CLI enhancements**: Interactive mode, better diagnostics, configuration
- **Documentation**: Tutorials, examples, guides, API docs
- **Testing**: Additional test coverage for edge cases
- **Runtime features**: Phase 2 (REPL), advanced scheduler features

### Documentation

Documentation improvements are always welcome:

- Tutorial improvements and clarifications
- Missing use case examples
- API documentation
- Architecture diagrams
- Translation to other languages

## Device Library Creation

Device libraries enable users to write semantic commands instead of raw MIDI. See [Device Library Creation Guide](docs/guides/device-libraries.md) for complete details.

### Quick Checklist

- [ ] Device has MIDI documentation (manual or website)
- [ ] You have access to test the library
- [ ] You've created the file in `devices/device_name.mmd`
- [ ] You've defined YAML frontmatter with metadata
- [ ] You've tested at least one alias
- [ ] You've run validation: `just validate-devices`

### File Structure

Create `devices/your_device.mmd`:

```markdown
---
title: Device Name
device: Full Device Model Name
manufacturer: Manufacturer Name
version: 1.0
description: Brief description of the device
url: https://device-documentation-url.com
channels: 16
note: Any additional notes
---

@alias load_preset {ch:1-16} {preset:0-127} "Load preset by number"
  - cc {ch}.0.0      # Bank LSB
  - pc {ch}.{preset} # Program Change
@end

@alias cc_param {ch:1-16} {param:0-127} {value:0-127} "Generic CC parameter"
  - cc {ch}.{param}.{value}
@end

# Add more aliases here
```

### Testing Your Library

```bash
# Validate the library file
just validate FILE=devices/your_device.mmd

# Or manually test compilation
uv run mmdc compile test_file.mmd -o test.mid
```

## Reporting Issues

Use [GitHub Issues](https://github.com/cjgdev/midi-markdown/issues) for:

- Bug reports
- Feature requests
- Documentation suggestions
- Questions or clarifications

**Before filing an issue:**
1. Search existing issues to avoid duplicates
2. Check the documentation and examples
3. Test with the latest version
4. Include a minimal reproducible example

## Pull Request Process

### Branch Naming

Use descriptive branch names:

- `feature/add-repl-mode` for new features
- `fix/validate-pitch-bend-range` for bug fixes
- `docs/improve-tutorial` for documentation
- `test/add-sweep-edge-cases` for test additions
- `refactor/simplify-parser-logic` for refactoring

### Before Submitting

1. **Create a branch** from `main`
   ```bash
   git checkout -b feature/your-feature
   ```

2. **Make your changes** following [Code Style & Standards](#code-style--standards)

3. **Run tests and checks**
   ```bash
   just check  # Ruff format, lint, mypy
   just test   # Run full test suite
   ```

4. **Commit with clear messages**
   ```bash
   git commit -m "Add feature: brief description of change"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature
   ```

6. **Open a Pull Request** with:
   - Clear title describing changes
   - Description of what changed and why
   - Link to related issues (e.g., `Fixes #123`)
   - Any relevant testing notes

### PR Title and Description Format

**Title:** Follow convention
- `Add: feature description`
- `Fix: bug description`
- `Docs: documentation improvement`
- `Refactor: code improvement`

**Description:** Include
```markdown
## Summary
Brief description of the changes

## Changes
- List of specific changes
- Another change
- Testing modifications

## Related Issues
Fixes #123
Relates to #456

## Testing
How this was tested (manual steps, test cases added, etc.)
```

### Review Process

- Code maintainers will review your PR
- Feedback and suggestions may be requested
- All automated checks (tests, linting) must pass
- Changes should align with project goals and architecture

## Code Style & Standards

### Python Version

- **Minimum**: Python 3.12
- **Style**: Modern Python features encouraged
- **Type hints**: Required for all public functions and methods

### Type Hints

All public APIs must have type hints:

```python
from typing import Optional
from pathlib import Path

def compile_file(input_path: Path, output_path: Optional[Path] = None) -> bytes:
    """Compile MMD file and return MIDI bytes."""
    pass
```

### Imports

```python
from __future__ import annotations

from typing import Optional
from pathlib import Path

import typer
from rich.console import Console

from midi_markdown.core import compile_ast_to_ir
```

### Formatting

Automatically format code with Ruff:

```bash
just fmt        # Format code
just lint-fix   # Auto-fix linting issues
just fix        # Both: format + lint-fix
```

**Manual checks:**
```bash
just fmt-check  # Check if code is formatted
just lint       # Show linting issues
just typecheck  # Run mypy type checking
```

### Docstrings

Use comprehensive docstrings:

```python
def load_device_library(library_name: str) -> dict[str, Any]:
    """Load a device library and return its aliases.

    Args:
        library_name: Name of the device (e.g., 'quad_cortex')

    Returns:
        Dictionary mapping alias names to alias definitions

    Raises:
        FileNotFoundError: If library file doesn't exist
        ParseError: If library file is malformed

    Example:
        >>> aliases = load_device_library('quad_cortex')
        >>> aliases['qc_load_preset']
    """
```

## Testing Guidelines

### Test Organization

- **Unit tests** (1000+ tests): Test individual components in isolation
- **Integration tests** (200+ tests): Test component interactions and workflows
- **Fixtures**: Reusable test files in `tests/fixtures/`

### Where to Add Tests

**Unit tests** (`tests/unit/`): Test a single function/class
- Test behavior in isolation
- Mock external dependencies
- Fast execution

**Integration tests** (`tests/integration/`): Test workflows
- Test multiple components together
- CLI command testing
- Full compilation pipeline tests

### Test File Naming

```
tests/unit/test_component.py        # Unit test file
tests/integration/test_feature.py   # Integration test file
tests/fixtures/valid/file.mmd       # Valid test file
tests/fixtures/invalid/file.mmd     # Invalid test file
```

### Test Class and Function Naming

```python
class TestParser:
    """Tests for MMLParser class."""

    def test_parse_absolute_timing(self):
        """Test parsing absolute timecode [mm:ss.ms]."""
        pass

    def test_parse_invalid_timing_raises_error(self):
        """Test that invalid timing raises ParseError."""
        pass
```

### Using pytest Markers

Tests should have appropriate markers:

```python
import pytest

@pytest.mark.unit
class TestParser:
    @pytest.mark.parser
    def test_parse_note_command(self):
        pass

@pytest.mark.integration
class TestEndToEnd:
    @pytest.mark.e2e
    def test_full_compilation_pipeline(self):
        pass
```

**Available markers:**
- `@pytest.mark.unit` - Unit tests (561 tests)
- `@pytest.mark.integration` - Integration tests (188 tests)
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.parser` - Parser tests
- `@pytest.mark.alias` - Alias system tests
- `@pytest.mark.expansion` - Variable/loop/sweep tests
- `@pytest.mark.validation` - Validation tests
- `@pytest.mark.cli` - CLI command tests
- `@pytest.mark.slow` - Slow/long-running tests

### Running Tests

```bash
# All tests
just test
just test-cov    # With coverage report

# By type
just test-unit
just test-integration

# By file or pattern
just test-file tests/unit/test_parser.py
just test-k "timing"  # Keyword expression

# Quick smoke test
just smoke

# Specific test markers
uv run pytest -m unit
uv run pytest -m integration
uv run pytest -m "parser and not slow"

# Stop on first failure
just test-x
just test-xvs    # Extra verbose + stop first failure
```

### Test Coverage

Current coverage: **72.53%**

Target: **80%+**

Check coverage:
```bash
just test-cov      # Show coverage summary
just coverage      # Generate HTML report
```

Critical paths to keep well-tested:
- Parser (grammar, transformer, timing)
- Validation (ranges, timing, values)
- MIDI generation (all command types)
- Alias resolution
- Command expansion (variables, loops, sweeps)

### Example Test Structure

```python
import pytest
from midi_markdown.parser import MMLParser
from midi_markdown.utils.validation import ValidationError

@pytest.mark.unit
@pytest.mark.parser
class TestAbsoluteTiming:
    @pytest.fixture
    def parser(self):
        return MMLParser()

    def test_parse_absolute_timecode(self, parser):
        """Test parsing [mm:ss.ms] format."""
        mml = "[00:01.500]\n- note_on 1.60 80"
        doc = parser.parse_string(mml)
        assert doc.events[0].timing.value == 1500

    def test_invalid_timing_format_raises_error(self, parser):
        """Test that malformed timing raises ParseError."""
        mml = "[25:90.000]\n- note_on 1.60 80"
        with pytest.raises(Exception):  # ParseError
            parser.parse_string(mml)

@pytest.mark.integration
class TestCompileWithTiming:
    def test_compile_preserves_timing_accuracy(self):
        """Test that compiled MIDI has correct absolute timing."""
        mml = """
        [00:00.000]
        - note_on 1.60 80
        [00:01.000]
        - note_off 1.60 0
        """
        # Test compilation and verify timing
        pass
```

## Questions or Need Help?

- Check [docs/index.md](docs/index.md) for documentation
- Review [examples/](examples/) for working examples
- Open an [issue](https://github.com/cjgdev/midi-markdown/issues) for questions
- Look at [existing PRs](https://github.com/cjgdev/midi-markdown/pulls) for patterns

## Recognition

Contributors are recognized in:
- Release notes for significant contributions
- GitHub contributors page
- Project documentation (for device libraries)

Thank you for making MIDI Markdown better!
