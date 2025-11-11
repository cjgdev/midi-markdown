# CLI Design Guidelines

**MIDI Markdown (MMD) Command-Line Interface Design Standards**

This document defines the conventions, patterns, and best practices for all CLI commands in the MIDI Markdown project. Follow these guidelines to ensure consistency, usability, and maintainability across all commands.

---

## Table of Contents

1. [Core Principles](#core-principles)
2. [Output Styling](#output-styling)
3. [Error Handling](#error-handling)
4. [Exit Codes](#exit-codes)
5. [Command Design](#command-design)
6. [Help Text](#help-text)
7. [Flags and Options](#flags-and-options)
8. [Console Configuration](#console-configuration)
9. [Progress Indicators](#progress-indicators)
10. [Examples](#examples)

---

## Core Principles

### 1. Consistency Above All
- Use the same symbols, colors, and formatting patterns across all commands
- Users should feel a unified experience whether using `compile`, `play`, or `validate`
- When in doubt, check existing commands for established patterns

### 2. Helpful by Default
- Provide clear error messages with context and suggestions
- Show helpful tips when appropriate (e.g., "No MIDI ports found" → show how to enable them)
- Include examples in every command's help text

### 3. Professional and Minimal
- Avoid unnecessary emoji (use sparingly for visual anchors only)
- Keep output concise but informative
- Respect `--no-color` and accessibility flags

### 4. Fail Fast, Recover Gracefully
- Validate inputs early (use Typer's built-in validators)
- Provide specific error messages about what went wrong
- Suggest fixes or alternatives when possible

---

## Output Styling

### Color Scheme

Use Rich markup consistently across all commands:

```python
# Success messages
console.print("[green]✓[/green] Operation successful")

# Errors
console.print("[red]✗[/red] Error message")
console.print("[red]Error:[/red] Detailed error description")

# Information
console.print("[cyan]Processing:[/cyan] filename.mmd")
console.print("[cyan]Output:[/cyan] output.mid")

# Warnings
console.print("[yellow]⚠ Warning message[/yellow]")

# Hints and tips
console.print("[dim]💡 Tip:[/dim] Helpful suggestion")
console.print("[dim]💡 Use:[/dim] command example")

# Contextual/secondary information
console.print("  [dim]Parsed: 42 events[/dim]")

# Values and emphasis
console.print(f"[bold cyan]{count}[/bold cyan] [dim]events[/dim]")
console.print(f"[green bold]{value}[/green bold]")
```

### Symbol Usage

Standard symbols for consistency:

- `✓` - Success (green)
- `✗` - Error (red)
- `⚠` - Warning (yellow)
- `💡` - Tip/hint (with dim styling)
- `•` - List items
- `→` - Directional indicator

### Typography

```python
# Headings and titles
console.print("[bold cyan]Section Title[/bold cyan]")

# Commands and code
console.print("[cyan]mmdc compile song.mmd[/cyan]")

# File paths
console.print(f"[cyan]{filename}[/cyan]")

# Emphasis
console.print("[bold]{important_text}[/bold]")

# De-emphasis
console.print("[dim]{secondary_info}[/dim]")
```

---

## Error Handling

### Unified Error Handler

All commands that perform file operations or complex processing MUST use the unified error handler:

```python
from midi_markdown.cli.error_handler import ErrorContext, cli_error_handler

def command_name(..., debug: bool = False) -> None:
    console = Console()

    # Create error context
    ctx = ErrorContext(
        mode="command_name",  # "compile", "validate", "play", etc.
        debug=debug,
        source_file=input_file,  # Optional: path to input file
        console=console,
    )

    with cli_error_handler(ctx):
        # Command implementation here
        pass
```

### Error Message Format

```python
# General errors
console.print("[red]Error:[/red] Clear description of what went wrong")

# Parse errors (let error_handler format these)
# Will show: line number, source context, pointer to error

# Validation errors
console.print(f"[red]✗ Validation failed with {count} error(s):[/red]\n")
for error in errors:
    console.print(f"  [red]•[/red] {error}")

# Runtime errors
console.print(f"[red]Runtime Error:[/red] {message}")
```

### Error Context and Suggestions

Always provide context and next steps:

```python
# Bad
console.print("[red]File not found[/red]")

# Good
console.print("[red]✗ File not found:[/red] song.mmd")
console.print("[dim]Make sure the file exists and the path is correct[/dim]")

# Best
console.print()
console.print("[red]✗ File not found:[/red] [bold]song.mmd[/bold]")
console.print()
console.print("[dim]💡 Tips:[/dim]")
console.print("  • Check the file path is correct")
console.print("  • Verify the file has [cyan].mmd[/cyan] extension")
console.print("  • Try: [cyan]mmdc examples[/cyan] to see example files")
console.print()
```

---

## Exit Codes

**Standard exit codes for all commands:**

```
0   - Success
1   - General error
2   - Parse error (syntax mistakes)
3   - Validation error (semantic issues)
4   - File not found / IO error
5   - MIDI/runtime error (port errors, playback issues)
130 - Keyboard interrupt (Ctrl+C)
```

Use `raise typer.Exit(code=N)` to exit with specific codes.

The `cli_error_handler` context manager automatically maps exceptions to appropriate exit codes:
- `ParseError` → exit code 2
- `ValidationError` → exit code 3
- `FileNotFoundError` → exit code 4
- `RuntimeError` → exit code 5
- `KeyboardInterrupt` → exit code 130

---

## Command Design

### Command Structure

```python
def command_name(
    # Positional arguments first
    input_file: Annotated[
        Path,
        typer.Argument(
            help="Description of argument",
            exists=True,  # For file inputs
            file_okay=True,
            dir_okay=False,
            readable=True,
        ),
    ],
    # Optional arguments
    optional_arg: Annotated[
        str | None,
        typer.Argument(help="Optional argument description"),
    ] = None,
    # Options/flags (in standard order)
    output: Annotated[
        Path | None,
        typer.Option("-o", "--output", help="Output file path"),
    ] = None,
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format"),
    ] = "midi",
    verbose: Annotated[
        bool,
        typer.Option("-v", "--verbose", help="Verbose output"),
    ] = False,
    debug: Annotated[
        bool,
        typer.Option("--debug", help="Show full error tracebacks"),
    ] = False,
    no_color: Annotated[
        bool,
        typer.Option("--no-color", help="Disable colored output"),
    ] = False,
) -> None:
    """Short one-line description.

    Longer description with details about what the command does,
    when to use it, and any important notes.

    Examples:
        # Basic usage
        mmdc command file.mmd

        # With options
        mmdc command file.mmd --option value

        # Advanced usage
        mmdc command file.mmd --flag -v
    """
    pass
```

### Standard Flag Order

When adding common flags, use this order:

1. Command-specific options (--format, --ppq, etc.)
2. `--verbose` / `-v` (more output)
3. `--debug` (full tracebacks)
4. `--no-progress` (disable progress indicators)
5. `--no-color` (disable colors)
6. `--no-emoji` (disable emoji)

---

## Help Text

### Docstring Format

Every command MUST have a comprehensive docstring following this template:

```python
def command(...) -> None:
    """Short one-line description of what command does.

    Detailed description explaining:
    - What the command does
    - When to use it vs. other commands
    - What it outputs or produces
    - Any important caveats or requirements

    Examples:
        # Example 1: Basic usage
        mmdc command file.mmd

        # Example 2: With common option
        mmdc command file.mmd --option value

        # Example 3: Advanced usage
        mmdc command file.mmd --flag1 --flag2

        # Include at least 3-5 examples covering:
        # - Basic usage
        # - Common workflows
        # - Advanced features
        # - Edge cases if relevant

    Output Formats:  # If applicable
        format1  Description of format
        format2  Description of format

    Exit Codes:  # Always include
        0  Success description
        2  Error type 1 description
        3  Error type 2 description

    Notes:  # Optional additional context
        - Important note 1
        - Important note 2
        - Reference to related commands
    """
```

### Help Text Best Practices

1. **One-line summary**: Clear, concise, describes the action
2. **Examples first**: Users scan for examples before reading descriptions
3. **Minimum 3 examples**: Cover basic → intermediate → advanced usage
4. **Real-world examples**: Use realistic file names and parameters
5. **Cross-references**: Mention related commands when relevant

---

## Flags and Options

### Boolean Flags

```python
# Standard boolean flags
verbose: bool = False          # -v, --verbose
debug: bool = False            # --debug
no_color: bool = False         # --no-color
no_progress: bool = False      # --no-progress
no_emoji: bool = False         # --no-emoji (if needed)
```

### File Path Options

```python
# Input files (required)
input_file: Annotated[
    Path,
    typer.Argument(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
]

# Output files (optional)
output: Annotated[
    Path | None,
    typer.Option("-o", "--output"),
] = None
```

### Choice Options

```python
# Enum-style choices
format: Annotated[
    str,
    typer.Option(help="Output format: midi, csv, json, table"),
] = "midi"

# Validate choices in command body:
valid_formats = ["midi", "csv", "json", "table"]
if format not in valid_formats:
    console.print(
        f"[red]Error:[/red] Invalid format '{format}'. "
        f"Valid formats: {', '.join(valid_formats)}"
    )
    raise typer.Exit(1)
```

---

## Console Configuration

### Standard Console Creation

```python
# Basic console (most commands)
console = Console()

# Console with color control (commands that support --no-color)
console = Console(
    no_color=no_color,
    force_terminal=not no_color,
)
```

### When to Use Which Console

```python
# Simple commands (version, ports, examples, etc.)
console = Console()

# Commands with --no-color support (compile, validate, inspect, play)
console = Console(no_color=no_color, force_terminal=not no_color)

# Commands that output to stdout (CSV/JSON export)
# Use print() directly to bypass Rich formatting
print(csv_output)  # Not console.print()
```

---

## Progress Indicators

### When to Show Progress

Show progress indicators for operations that:
- Take longer than 2 seconds for typical files
- Process large files (>50KB or >500 events)
- Have multiple distinct phases
- Are explicitly requested with `--verbose`

Do NOT show progress for:
- Quick operations (<1 second)
- Small files
- Commands with `--no-progress` flag
- Simple single-step operations

### Progress Bar Implementation

```python
from midi_markdown.cli.progress import (
    create_validation_progress,
    should_show_progress,
    ValidationProgress,
)

# Determine if progress should be shown
use_progress = should_show_progress(input_file, doc, verbose, no_progress)

if use_progress:
    progress_bar = create_validation_progress(console)
    progress_ctx = ValidationProgress(progress_bar)
else:
    from contextlib import nullcontext
    progress_ctx = nullcontext()

with progress_ctx as progress:
    # Phase 1
    do_work()
    if isinstance(progress, ValidationProgress):
        progress.parsing_complete()

    # Phase 2
    do_more_work()
    if isinstance(progress, ValidationProgress):
        progress.aliases_complete()
```

### Progress Phases

Standard phase names for consistency:
- **Parsing** - Reading and parsing MMD file
- **Resolving aliases** - Expanding device library aliases
- **Validating** - Running validation checks
- **Generating** - Creating output (MIDI/CSV/JSON)

---

## Examples

### Complete Command Example

```python
"""Example command following all guidelines."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from midi_markdown.cli.error_handler import ErrorContext, cli_error_handler


def example_command(
    input_file: Annotated[
        Path,
        typer.Argument(
            help="Input .mmd file to process",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
        ),
    ],
    output: Annotated[
        Path | None,
        typer.Option("-o", "--output", help="Output file path"),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("-v", "--verbose", help="Verbose output"),
    ] = False,
    debug: Annotated[
        bool,
        typer.Option("--debug", help="Show full error tracebacks"),
    ] = False,
) -> None:
    """Process MMD file and generate output.

    This command demonstrates all CLI design guidelines including proper
    error handling, consistent styling, and comprehensive help text.

    Examples:
        # Basic usage
        mmdc example input.mmd

        # With custom output
        mmdc example input.mmd -o output.txt

        # Verbose mode
        mmdc example input.mmd -v

        # Debug mode for troubleshooting
        mmdc example input.mmd --debug

    Exit Codes:
        0  Processing completed successfully
        2  Parse error in input file
        3  Validation error
        4  File not found

    Notes:
        - This is an example command
        - See other commands for real implementations
    """
    console = Console()

    # Create error context
    ctx = ErrorContext(
        mode="example",
        debug=debug,
        source_file=input_file,
        console=console,
    )

    with cli_error_handler(ctx):
        # Show what we're doing
        console.print(f"[cyan]Processing:[/cyan] {input_file}")
        if output:
            console.print(f"[cyan]Output:[/cyan] {output}")

        # Verbose information
        if verbose:
            console.print("  [dim]Running in verbose mode...[/dim]")

        # Do the work
        # ... implementation ...

        # Success!
        console.print("[green]✓[/green] Processing completed")
        if verbose:
            console.print("  [dim]42 items processed[/dim]")
```

---

## Testing CLI Commands

### Integration Test Template

```python
"""Integration test for CLI command."""

import pytest
from typer.testing import CliRunner
from pathlib import Path

from midi_markdown.cli.main import app

runner = CliRunner()


@pytest.mark.integration
def test_command_basic_usage(tmp_path: Path) -> None:
    """Test basic command usage."""
    # Create test file
    test_file = tmp_path / "test.mmd"
    test_file.write_text("# test content")

    # Run command
    result = runner.invoke(app, ["command-name", str(test_file)])

    # Assertions
    assert result.exit_code == 0
    assert "✓" in result.stdout  # Success indicator


@pytest.mark.integration
def test_command_error_handling(tmp_path: Path) -> None:
    """Test command handles errors correctly."""
    # Test with non-existent file
    result = runner.invoke(app, ["command-name", "/nonexistent/file.mmd"])

    # Should fail
    assert result.exit_code != 0


@pytest.mark.integration
def test_command_verbose_mode(tmp_path: Path) -> None:
    """Test verbose output."""
    test_file = tmp_path / "test.mmd"
    test_file.write_text("# test content")

    # Run with verbose
    result = runner.invoke(app, ["command-name", str(test_file), "-v"])

    assert result.exit_code == 0
    # Verbose should have more output
    assert len(result.stdout) > 100
```

---

## Shell Completion

### Enabling Completion

Typer provides built-in shell completion. Users can enable it with:

```bash
# Bash
mmdc --install-completion bash
source ~/.bashrc

# Zsh
mmdc --install-completion zsh
source ~/.zshrc

# Fish
mmdc --install-completion fish
```

### Testing Completion

```bash
# Test that completion is working
mmdc <TAB>       # Should show all commands
mmdc compile <TAB>  # Should show files in current directory
```

---

## Accessibility

### Supporting Diverse Environments

1. **Color blindness**: Use symbols (✓✗⚠) in addition to colors
2. **No TTY**: Commands work when piped or in CI/CD
3. **NO_COLOR env var**: Respect `NO_COLOR=1` environment variable
4. **Screen readers**: Don't rely solely on visual formatting

### Testing Accessibility

```bash
# Test without colors
mmdc command --no-color

# Test with NO_COLOR environment variable
NO_COLOR=1 mmdc command

# Test output piping
mmdc command | less
mmdc command > output.txt
```

---

## Summary Checklist

Before merging a new CLI command, verify:

- [ ] Follows standard command structure
- [ ] Uses unified error handler with ErrorContext
- [ ] Has comprehensive docstring with 3+ examples
- [ ] Uses consistent Rich styling (green ✓, red ✗, cyan info, yellow ⚠)
- [ ] Returns appropriate exit codes
- [ ] Includes --verbose and --debug flags
- [ ] Has integration tests (basic usage, errors, verbose)
- [ ] Handles KeyboardInterrupt gracefully
- [ ] Works with --no-color flag
- [ ] Help text is clear and actionable
- [ ] Cross-references related commands where appropriate

---

**Last Updated**: 2025-11-07
**Version**: 1.0
**Phase**: 4 Stage 7 (Polish & Cleanup)
