"""Unified error handling for all CLI commands.

This module provides a centralized error handling system that ensures consistent
behavior across all CLI commands. It uses a context manager pattern to catch and
route exceptions to appropriate handlers with mode-specific cleanup.
"""

from __future__ import annotations

import sys
from contextlib import contextmanager
from dataclasses import dataclass
from typing import TYPE_CHECKING

from lark.exceptions import UnexpectedCharacters, UnexpectedInput, UnexpectedToken
from rich.console import Console

from midi_markdown.alias.errors import AliasError
from midi_markdown.expansion.errors import ExpansionError
from midi_markdown.utils.validation.errors import ValidationError

if TYPE_CHECKING:
    from pathlib import Path

    from midi_markdown.runtime.player import RealtimePlayer


@dataclass
class ErrorContext:
    """Context for error handling behavior.

    Attributes:
        mode: Command mode (compile/play/repl/validate/check/inspect)
        debug: Whether to show full tracebacks
        source_file: Optional source file path for error context
        no_color: Disable color output
        no_emoji: Disable emoji output
        player: Optional RealtimePlayer instance for cleanup in play mode
        console: Optional Rich Console instance (created if not provided)
    """

    mode: str
    debug: bool = False
    source_file: Path | None = None
    no_color: bool = False
    no_emoji: bool = False
    player: RealtimePlayer | None = None
    console: Console | None = None


@contextmanager
def cli_error_handler(ctx: ErrorContext):
    """Mode-aware error handling context manager.

    This context manager provides unified error handling across all CLI commands.
    It catches common exception types, routes them to appropriate formatters, and
    ensures proper cleanup based on the command mode.

    Exit codes:
        0: Success (when no exception raised)
        1: General error
        2: Parse error (syntax errors from Lark parser)
        3: Validation error (semantic validation failures)
        4: File not found
        5: Runtime error (MIDI I/O, player errors)
        130: Keyboard interrupt (standard Unix convention)

    Error handling:
        - Parse errors: Show source context with structured formatting
        - Validation errors: Show validation failures with helpful suggestions
        - Expansion errors: Show variable/loop/sweep errors with context
        - Alias errors: Show alias resolution errors with suggestions
        - File errors: Show missing file with helpful hints
        - Runtime errors: Show MIDI/player errors with troubleshooting
        - Keyboard interrupt: Clean cleanup with user-friendly message
        - Generic errors: Show error type with optional traceback

    Mode-specific cleanup:
        - play: Stop player and send MIDI all-notes-off
        - Other modes: Standard cleanup only

    Args:
        ctx: ErrorContext with mode, debug flag, and optional player/console

    Yields:
        None (context manager for use with `with` statement)

    Examples:
        >>> ctx = ErrorContext(mode="compile", debug=True)
        >>> with cli_error_handler(ctx):
        ...     # Compile logic here
        ...     pass
    """
    from midi_markdown.cli.errors import (
        show_expansion_error,
        show_parse_error,
        show_validation_error,
    )

    console = ctx.console or Console()

    try:
        yield

    except KeyboardInterrupt:
        console.print("\n[yellow]⚠[/yellow] Cancelled by user")

        # Mode-specific cleanup
        if ctx.mode == "play" and ctx.player:
            console.print("[dim]Sending all-notes-off...[/dim]")
            try:
                ctx.player.stop()  # Sends MIDI panic
            except Exception:
                pass  # Ignore cleanup errors

        sys.exit(130)

    except (UnexpectedToken, UnexpectedCharacters, UnexpectedInput) as e:
        # Parse errors from Lark parser
        if ctx.source_file:
            show_parse_error(
                e, ctx.source_file, console, no_color=ctx.no_color, no_emoji=ctx.no_emoji
            )
        else:
            console.print(f"[red]Parse Error:[/red] {e}")
            if ctx.debug:
                console.print_exception()
        sys.exit(2)

    except ValidationError as e:
        # Semantic validation errors
        if ctx.source_file:
            show_validation_error(
                e, ctx.source_file, console, no_color=ctx.no_color, no_emoji=ctx.no_emoji
            )
        else:
            console.print(f"[red]Validation Error:[/red] {e}")
            if ctx.debug:
                console.print_exception()
        sys.exit(3)

    except ExpansionError as e:
        # Variable, loop, sweep expansion errors
        show_expansion_error(e, console, no_color=ctx.no_color, no_emoji=ctx.no_emoji)
        sys.exit(1)

    except AliasError as e:
        # Alias resolution errors
        from midi_markdown.cli.errors import show_alias_error

        show_alias_error(e, console, no_color=ctx.no_color, no_emoji=ctx.no_emoji)
        sys.exit(1)

    except FileNotFoundError as e:
        # Missing input files
        from midi_markdown.cli.errors import show_file_not_found_error

        show_file_not_found_error(e, console, no_color=ctx.no_color, no_emoji=ctx.no_emoji)
        sys.exit(4)

    except RuntimeError as e:
        # MIDI port errors, player errors, etc.
        from midi_markdown.cli.errors import show_runtime_error

        show_runtime_error(e, console, mode=ctx.mode, no_color=ctx.no_color, no_emoji=ctx.no_emoji)
        sys.exit(5)

    except Exception as e:
        # Unexpected errors
        console.print(f"[red]Unexpected Error:[/red] {type(e).__name__}: {e}")
        if ctx.debug:
            console.print_exception(show_locals=True)
        else:
            console.print("[dim]Run with --debug for full traceback[/dim]")
        sys.exit(1)
