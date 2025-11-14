"""REPL session management for interactive MML execution.

This module provides the MMLRepl class which manages the interactive Read-Eval-Print
Loop, including multi-line input handling, completion detection, and state management.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from lark.exceptions import UnexpectedCharacters, UnexpectedInput, UnexpectedToken
from rich.console import Console

from midi_markdown.alias.imports import ImportManager
from midi_markdown.core.compiler import compile_ast_to_ir
from midi_markdown.diagnostics.formatter import display_events_table
from midi_markdown.expansion.errors import ExpansionError
from midi_markdown.parser.parser import MMDParser
from midi_markdown.utils.validation import ValidationError

from .repl_state import REPLState

if TYPE_CHECKING:
    from midi_markdown.parser.ast_nodes import MMDDocument


class MMLRepl:
    """Interactive REPL for MIDI Markup Language.

    The MMLRepl class manages an interactive session, providing:
    - Multi-line input buffering and completion detection
    - State management (variables, aliases, imports)
    - Parser integration with error handling
    - Context-aware autocompletion via MusicCompleter

    The REPL uses Lark's UnexpectedEOF exception to detect incomplete input,
    allowing natural multi-line editing of complex MML constructs like @alias
    blocks, @loop statements, and @sweep definitions.

    Example:
        >>> repl = MMLRepl()
        >>> complete, result = repl.try_parse("@alias test {val}")
        >>> assert complete is False  # Incomplete - needs @end
        >>> complete, result = repl.try_parse("@alias test {val}\\n  - cc 1.10.{val}\\n@end")
        >>> assert complete is True   # Complete block
        >>> isinstance(result, MMDDocument)
        True
    """

    def __init__(self) -> None:
        """Initialize the REPL with parser and state.

        Creates a new MMDParser instance for parsing input and a REPLState
        instance for tracking session state (variables, aliases, imports, etc.).
        """
        self.parser = MMDParser()
        self.state = REPLState()
        self.buffer: list[str] = []

    def try_parse(self, text: str) -> tuple[bool, MMDDocument | Exception | None]:
        """Attempt to parse input text and determine if it's complete.

        This method delegates to MMDParser.parse_interactive() which uses Lark's
        exception handling to distinguish three cases:

        1. Incomplete input (UnexpectedEOF): User hasn't finished typing a multi-line
           construct like @alias...@end. Returns (False, None).

        2. Complete and valid: Input is syntactically complete and parses successfully.
           Returns (True, MMDDocument).

        3. Complete but invalid: Input is complete but has syntax errors. Returns
           (True, Exception) so the error can be displayed without blocking further input.

        Args:
            text: MML source text to parse (may be multi-line)

        Returns:
            Tuple of (is_complete, result):
            - (False, None): Input is incomplete, need more lines
            - (True, MMDDocument): Input is complete and valid
            - (True, Exception): Input is complete but has syntax errors

        Example:
            >>> repl = MMLRepl()
            >>> # Incomplete alias block
            >>> complete, result = repl.try_parse("@alias test {val}")
            >>> assert complete is False
            >>> assert result is None
            >>>
            >>> # Complete single-line command
            >>> complete, result = repl.try_parse("- cc 1.7.64")
            >>> assert complete is True
            >>> assert isinstance(result, MMDDocument)
            >>>
            >>> # Complete but invalid syntax
            >>> complete, result = repl.try_parse("- invalid_command")
            >>> assert complete is True
            >>> assert isinstance(result, Exception)
        """
        return self.parser.parse_interactive(text)

    def is_complete(self, text: str) -> bool:
        """Check if input text is grammatically complete.

        This is a convenience method that returns just the completion status,
        discarding the parse result. Useful for prompt_toolkit integration where
        you only need to know whether to show a continuation prompt.

        Args:
            text: MML source text to check

        Returns:
            True if input is complete (valid or invalid), False if incomplete

        Example:
            >>> repl = MMLRepl()
            >>> repl.is_complete("- cc 1.7.64")
            True
            >>> repl.is_complete("@alias test {val}")
            False
            >>> repl.is_complete("@alias test {val}\\n@end")
            True
        """
        complete, _ = self.try_parse(text)
        return complete

    def reset(self) -> None:
        """Reset REPL state to initial values.

        Clears all variables, aliases, imports, and resets tempo/resolution
        to defaults. Does not affect the parser instance.

        Example:
            >>> repl = MMLRepl()
            >>> repl.state.variables["foo"] = 42
            >>> repl.reset()
            >>> assert repl.state.variables == {}
        """
        self.state.reset()
        self.buffer.clear()

    def evaluate(self, doc: MMDDocument) -> None:
        """Evaluate parsed MML document in REPL context.

        This method processes a parsed MML document and updates the REPL state
        accordingly. It handles:
        1. Frontmatter (tempo, ppq, time_signature)
        2. @define statements (variables)
        3. @alias definitions
        4. @import statements (device libraries)
        5. MIDI events (compile to IR)

        The state persists across multiple evaluate() calls, allowing
        incremental definition and usage of variables/aliases.

        Args:
            doc: Parsed MML document to evaluate

        Example:
            >>> repl = MMLRepl()
            >>> # Define a variable
            >>> doc1 = repl.parser.parse_string("@define VELOCITY 80")
            >>> repl.evaluate(doc1)
            >>> # Use the variable
            >>> doc2 = repl.parser.parse_string("[00:00.000]\\n- cc 1.7.${VELOCITY}")
            >>> repl.evaluate(doc2)
            >>> assert repl.state.variables["VELOCITY"] == 80
            >>> assert repl.state.last_ir is not None
        """
        console = Console()

        # 1. Update state from frontmatter (tempo, ppq, time_signature)
        if doc.frontmatter:
            self.state.update_from_frontmatter(doc.frontmatter)
            # Show compact frontmatter update
            updates = []
            if "tempo" in doc.frontmatter:
                updates.append(f"tempo={doc.frontmatter['tempo']}")
            if "ppq" in doc.frontmatter:
                updates.append(f"ppq={doc.frontmatter['ppq']}")
            if "time_signature" in doc.frontmatter:
                updates.append(f"time_signature={doc.frontmatter['time_signature']}")
            if updates:
                console.print(f"[green]✓[/green] Frontmatter: {', '.join(updates)}")

        # 2. Register @define variables (doc.defines is a dict)
        if doc.defines:
            for var_name, var_value in doc.defines.items():
                self.state.variables[var_name] = var_value
                console.print(f"[green]✓[/green] Defined: [cyan]{var_name}[/cyan] = {var_value}")

        # 3. Register @alias definitions (doc.aliases is a dict)
        if doc.aliases:
            for alias_name, alias in doc.aliases.items():
                self.state.aliases[alias_name] = alias
                param_count = len(alias.parameters)
                param_str = f"{param_count} param{'s' if param_count != 1 else ''}"
                console.print(
                    f"[green]✓[/green] Alias: [magenta]{alias_name}[/magenta] ({param_str})"
                )

        # 4. Load @import device libraries
        if doc.imports:
            import_manager = ImportManager(self.parser)
            for import_stmt in doc.imports:
                import_path = import_stmt.path
                if import_path not in self.state.imports:
                    # Load and parse imported file
                    try:
                        imported_aliases = import_manager.load_import(import_path)
                        # Merge imported aliases into state
                        self.state.aliases.update(imported_aliases)
                        self.state.imports.append(import_path)
                        alias_count = len(imported_aliases)
                        console.print(
                            f"[green]✓[/green] Imported: [blue]{import_path}[/blue] "
                            f"({alias_count} alias{'es' if alias_count != 1 else ''})"
                        )
                    except Exception as e:
                        console.print(f"[yellow]![/yellow] Import error: {e}")

        # 5. Compile MIDI events to IR
        if doc.events or doc.tracks:
            try:
                ir_program = compile_ast_to_ir(doc, ppq=self.state.resolution)
                self.state.last_ir = ir_program

                # Display summary
                console.print()
                console.print(f"[bold cyan]Compiled {ir_program.event_count} events[/]")
                console.print(f"Duration: [cyan]{ir_program.duration_seconds:.2f}s[/]")

                # Show first few events (limit to 10 for REPL)
                if ir_program.event_count > 0:
                    display_events_table(
                        ir_program, max_events=10, show_stats=False, console=console
                    )

            except Exception:
                # Let exceptions bubble up to REPL loop for error handling (Stage 2.6)
                raise

    def handle_error(self, error: Exception, source_text: str = "") -> None:
        """Display error without crashing REPL.

        This method provides graceful error handling by catching all exception types,
        formatting them beautifully with Rich console, and displaying helpful context
        and suggestions without terminating the REPL session.

        The method preserves REPL state - variables, aliases, and imports remain
        intact after error display, allowing the user to continue working.

        Args:
            error: Exception to display (parse, validation, expansion, import, etc.)
            source_text: Source text that caused the error (for context display)

        Example:
            >>> repl = MMLRepl()
            >>> try:
            ...     doc = repl.parser.parse_string("- invalid_cmd")
            ... except Exception as e:
            ...     repl.handle_error(e, "- invalid_cmd")
            # Displays formatted error without crashing

        Note:
            This method never raises exceptions - it's the final error handler.
            All errors are caught, formatted, and displayed gracefully.
        """
        console = Console()

        try:
            # 1. Parse/Syntax Errors (Lark exceptions)
            if isinstance(error, UnexpectedToken | UnexpectedCharacters | UnexpectedInput):
                self._handle_parse_error(error, source_text, console)

            # 2. Validation Errors (MIDI value range, channel, etc.)
            elif isinstance(error, ValidationError):
                self._handle_validation_error(error, source_text, console)

            # 3. Expansion Errors (undefined variables, invalid loops/sweeps)
            elif isinstance(error, ExpansionError):
                self._handle_expansion_error(error, console)

            # 4. File/Import Errors
            elif isinstance(error, FileNotFoundError):
                self._handle_file_error(error, console)

            # 5. Generic Fallback (any other exception)
            else:
                self._handle_generic_error(error, console)

        except Exception as display_error:
            # Ultimate fallback - even error display failed
            console.print(f"[red]Error displaying error: {display_error}[/red]")
            console.print(f"[red]Original error: {error}[/red]")

        # Always show reassurance message
        console.print("[dim]REPL state preserved - continue working[/dim]")

    def _handle_parse_error(
        self,
        error: UnexpectedToken | UnexpectedCharacters | UnexpectedInput,
        source_text: str,
        console: Console,
    ) -> None:
        """Handle parse/syntax errors with formatted code context."""
        # Determine error details
        if isinstance(error, UnexpectedToken):
            error_code = "E101"
            message = f"Unexpected token: {error.token.type}"
            line = getattr(error, "line", 1)
            column = getattr(error, "column", 1) - 1  # Convert to 0-indexed

            # Generate expected tokens message
            suggestion = None
            if hasattr(error, "expected") and error.expected:
                # Format expected tokens nicely
                expected = list(error.expected)[:5]  # Limit to first 5
                expected_str = ", ".join(expected)
                suggestion = f"Expected: {expected_str}"

        elif isinstance(error, UnexpectedCharacters):
            error_code = "E102"
            char = getattr(error, "char", "?")
            message = f"Unexpected character: '{char}'"
            line = getattr(error, "line", 1)
            column = getattr(error, "column", 1) - 1
            suggestion = None

        else:  # UnexpectedInput
            error_code = "E103"
            message = "Unexpected input"
            line = getattr(error, "line", 1)
            column = getattr(error, "column", 1) - 1
            suggestion = None

        # Format header
        header = f"[red bold]❌ error[{error_code}][/red bold]: {message}"
        location = f"  → <repl>:{line}:{column + 1}"

        # Format code context if we have source text
        parts = [header, location]
        if source_text:
            source_lines = source_text.splitlines()
            if 0 < line <= len(source_lines):
                parts.append("")
                # Show the error line with line number
                error_line = source_lines[line - 1]
                parts.append(f"   {line} │ {error_line}")
                # Show caret pointing to error column
                caret_line = " " * (len(str(line)) + 3) + "│ " + " " * column + "^^^"
                parts.append(f"[red]{caret_line}[/red]")

        # Add suggestion if available
        if suggestion:
            parts.append(f"\n  [cyan]💡 {suggestion}[/cyan]")

        console.print("\n".join(parts))

    def _handle_validation_error(
        self, error: ValidationError, source_text: str, console: Console
    ) -> None:
        """Handle validation errors with helpful context."""
        error_code = getattr(error, "error_code", "E201")
        header = f"[red bold]❌ error[{error_code}][/red bold]: {error}"

        parts = [header]

        # Add line/column context if available
        if hasattr(error, "line") and error.line:
            column = getattr(error, "column", 1)
            parts.append(f"  → <repl>:{error.line}:{column}")

            # Show code context if we have source
            if source_text:
                source_lines = source_text.splitlines()
                if 0 < error.line <= len(source_lines):
                    parts.append("")
                    error_line = source_lines[error.line - 1]
                    parts.append(f"   {error.line} │ {error_line}")
                    # Show caret
                    caret_line = " " * (len(str(error.line)) + 3) + "│ " + " " * (column - 1) + "^"
                    parts.append(f"[red]{caret_line}[/red]")

        # Add suggestion if available
        if hasattr(error, "suggestion") and error.suggestion:
            parts.append(f"\n  [cyan]💡 {error.suggestion}[/cyan]")

        console.print("\n".join(parts))

    def _handle_expansion_error(self, error: ExpansionError, console: Console) -> None:
        """Handle expansion errors (undefined variables, invalid loops, etc.)."""
        # Determine error code from error type
        error_type_map = {
            "UndefinedVariableError": "E301",
            "InvalidLoopConfigError": "E302",
            "InvalidSweepConfigError": "E303",
            "ValueRangeError": "E304",
        }
        error_code = error_type_map.get(type(error).__name__, "E300")

        header = f"[red bold]❌ error[{error_code}][/red bold]: {error}"
        parts = [header]

        # Add file/line context if available
        if hasattr(error, "source_file") and error.source_file:
            line = getattr(error, "line", None)
            if line:
                parts.append(f"  → {error.source_file}:{line}")

        # Add suggestion if available
        if hasattr(error, "suggestion") and error.suggestion:
            parts.append(f"\n  [cyan]💡 {error.suggestion}[/cyan]")

        console.print("\n".join(parts))

    def _handle_file_error(self, error: FileNotFoundError, console: Console) -> None:
        """Handle file not found errors."""
        filename = str(error).split("'")[1] if "'" in str(error) else "unknown"
        console.print(f"[red]❌ error[E401][/red]: File not found: {filename}")

    def _handle_generic_error(self, error: Exception, console: Console) -> None:
        """Handle any other unexpected errors."""
        error_type = type(error).__name__
        console.print(f"[red]❌ Error[/red]: {error_type}: {error}")

    def handle_meta_command(self, line: str) -> bool:
        """Handle REPL meta-commands (starting with .).

        Meta-commands provide REPL session control and state inspection without
        executing MML code. They start with a dot (.) and are processed before
        MML parsing.

        Args:
            line: Input line starting with '.'

        Returns:
            True if should exit REPL (for .quit/.exit), False otherwise

        Supported commands:
            .help         - Show help message with available commands
            .quit/.exit   - Exit REPL session
            .reset        - Clear all state (variables, aliases, imports)
            .list         - Show current state (variables, aliases, imports)
            .inspect      - Show last compiled IR program
            .tempo <bpm>  - Set current tempo (BPM)
            .ppq <value>  - Set pulses per quarter note (resolution)

        Example:
            >>> repl = MMLRepl()
            >>> should_exit = repl.handle_meta_command(".quit")
            >>> assert should_exit is True
        """
        console = Console()
        parts = line.strip().split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        # Help command
        if command == ".help":
            console.print("[bold cyan]MMD REPL Commands:[/bold cyan]")
            console.print("  [cyan].help[/cyan]         - Show this help message")
            console.print("  [cyan].quit[/cyan]/.exit   - Exit REPL")
            console.print("  [cyan].reset[/cyan]        - Clear all state")
            console.print("  [cyan].list[/cyan]         - Show variables, aliases, imports")
            console.print("  [cyan].inspect[/cyan]      - Show last compiled IR")
            console.print("  [cyan].tempo <bpm>[/cyan]  - Set tempo (e.g., .tempo 140)")
            console.print("  [cyan].ppq <value>[/cyan]  - Set resolution (e.g., .ppq 960)")
            console.print()
            console.print("[dim]Press Ctrl+C to cancel input, Ctrl+D to exit[/dim]")
            return False

        # Exit commands
        if command in (".quit", ".exit"):
            return True

        # Reset state
        if command == ".reset":
            self.reset()
            console.print("[green]✓[/green] State reset")
            return False

        # List current state
        if command == ".list":
            console.print("[bold cyan]Current State:[/bold cyan]")

            # Variables
            if self.state.variables:
                console.print(f"  [cyan]Variables ({len(self.state.variables)}):[/cyan]")
                for name, value in self.state.variables.items():
                    console.print(f"    {name} = {value}")
            else:
                console.print("  [dim]Variables: (none)[/dim]")

            # Aliases
            if self.state.aliases:
                console.print(f"  [cyan]Aliases ({len(self.state.aliases)}):[/cyan]")
                for name in self.state.aliases:
                    console.print(f"    {name}")
            else:
                console.print("  [dim]Aliases: (none)[/dim]")

            # Imports
            if self.state.imports:
                console.print(f"  [cyan]Imports ({len(self.state.imports)}):[/cyan]")
                for path in self.state.imports:
                    console.print(f"    {path}")
            else:
                console.print("  [dim]Imports: (none)[/dim]")

            # Settings
            console.print("  [cyan]Settings:[/cyan]")
            console.print(f"    Tempo: {self.state.tempo} BPM")
            console.print(f"    PPQ: {self.state.resolution}")
            console.print(f"    Time Signature: {self.state.time_signature}")

            return False

        # Inspect last IR
        if command == ".inspect":
            if self.state.last_ir is None:
                console.print("[yellow]No IR to inspect[/yellow]")
                console.print("[dim]Compile some MIDI events first[/dim]")
            else:
                console.print("[bold cyan]Last Compiled IR:[/bold cyan]")
                console.print(f"  Events: {self.state.last_ir.event_count}")
                console.print(f"  Duration: {self.state.last_ir.duration_seconds:.2f}s")
                console.print()
                display_events_table(
                    self.state.last_ir, max_events=20, show_stats=True, console=console
                )
            return False

        # Set tempo
        if command == ".tempo":
            if not args:
                console.print("[red]✗[/red] Usage: .tempo <bpm>")
                console.print("[dim]Example: .tempo 140[/dim]")
            else:
                try:
                    tempo = int(args)
                    if tempo <= 0 or tempo > 500:
                        console.print("[red]✗[/red] Tempo must be between 1 and 500 BPM")
                    else:
                        self.state.tempo = tempo
                        console.print(f"[green]✓[/green] Tempo set to {tempo} BPM")
                except ValueError:
                    console.print(f"[red]✗[/red] Invalid tempo: {args}")
                    console.print("[dim]Tempo must be an integer[/dim]")
            return False

        # Set PPQ
        if command == ".ppq":
            if not args:
                console.print("[red]✗[/red] Usage: .ppq <value>")
                console.print("[dim]Example: .ppq 960[/dim]")
            else:
                try:
                    ppq = int(args)
                    if ppq <= 0 or ppq > 9600:
                        console.print("[red]✗[/red] PPQ must be between 1 and 9600")
                    else:
                        self.state.resolution = ppq
                        console.print(f"[green]✓[/green] PPQ set to {ppq}")
                except ValueError:
                    console.print(f"[red]✗[/red] Invalid PPQ: {args}")
                    console.print("[dim]PPQ must be an integer[/dim]")
            return False

        # Unknown command
        console.print(f"[red]✗[/red] Unknown command: {command}")
        console.print("[dim]Type .help for available commands[/dim]")
        return False
