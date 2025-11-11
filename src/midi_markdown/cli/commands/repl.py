"""REPL command for interactive MML session."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
from rich.console import Console

from midi_markdown.runtime.repl import MMLRepl


def run_repl(
    debug: bool = False,
    history_file: Path | None = None,
) -> None:
    """Start interactive REPL session.

    Args:
        debug: Enable debug mode (crashes on errors instead of handling gracefully)
        history_file: Path to history file (defaults to .mmd_history in current dir)
    """
    console = Console()

    # 1. Print welcome banner
    console.print("[bold cyan]╭─────────────────────────────────────────╮[/bold cyan]")
    console.print("[bold cyan]│  MMD REPL - Interactive MIDI Session   │[/bold cyan]")
    console.print("[bold cyan]╰─────────────────────────────────────────╯[/bold cyan]")
    console.print()
    console.print("[dim]Type .help for commands, Ctrl+D to exit[/dim]")
    console.print()

    # 2. Create MMLRepl instance
    repl = MMLRepl()

    # 3. Create PromptSession with history and completion
    history_path = history_file or Path(".mmd_history")

    # Basic command completer (will be enhanced later with MusicCompleter)
    completer = WordCompleter(
        [
            ".help",
            ".quit",
            ".exit",
            ".reset",
            ".list",
            ".inspect",
            ".tempo",
            ".ppq",
            "note_on",
            "note_off",
            "cc",
            "pc",
            "pitch_bend",
            "@define",
            "@import",
            "@alias",
            "@loop",
            "@sweep",
        ],
        ignore_case=True,
    )

    session: PromptSession[str] = PromptSession(
        history=FileHistory(str(history_path)),
        completer=completer,
        enable_history_search=True,
    )

    # 4. Main REPL loop
    buffer: list[str] = []

    try:
        while True:
            # 4a. Determine prompt
            prompt = "...  " if buffer else "mml> "

            # 4b. Get user input
            try:
                line = session.prompt(prompt)
            except KeyboardInterrupt:
                # Ctrl+C: clear buffer and continue
                if buffer:
                    console.print("[dim]Input cancelled[/dim]")
                    buffer.clear()
                continue
            except EOFError:
                # Ctrl+D: exit gracefully
                console.print()
                console.print("[cyan]Goodbye![/cyan]")
                break

            # 4c. Handle empty lines
            if not line.strip():
                if buffer:
                    # Empty line with buffer: try to process
                    pass
                else:
                    # Empty line without buffer: skip
                    continue

            # 4d. Handle meta-commands (only if buffer is empty)
            if not buffer and line.strip().startswith("."):
                should_exit = repl.handle_meta_command(line.strip())
                if should_exit:
                    console.print()
                    console.print("[cyan]Goodbye![/cyan]")
                    break
                continue

            # 4e. Append to buffer
            buffer.append(line)

            # 4f-i. Try to parse and evaluate accumulated input
            accumulated_input = "\n".join(buffer)

            # Parse the input string first using try_parse
            complete, result = repl.try_parse(accumulated_input)

            if not complete:
                # 4i. Incomplete input: continue with continuation prompt
                continue

            if isinstance(result, Exception):
                # 4h. Complete but has parse errors
                if debug:
                    raise result

                repl.handle_error(result, accumulated_input)
                buffer.clear()
            else:
                # 4g. Complete and valid: evaluate the parsed MMDDocument
                try:
                    repl.evaluate(result)
                    buffer.clear()
                except Exception as e:
                    # Error during evaluation (not parsing)
                    if debug:
                        raise

                    repl.handle_error(e, accumulated_input)
                    buffer.clear()

    except Exception as e:
        # 5. Handle unexpected exceptions
        if debug:
            raise

        console.print(f"[red]Fatal error: {e}[/red]")
        console.print("[dim]REPL session terminated[/dim]")


def create_repl_command(app):
    """Add REPL command to Typer app.

    This is called from cli/main.py to register the command.
    """

    @app.command(name="repl")
    def repl_command(
        debug: Annotated[
            bool,
            typer.Option("--debug", help="Enable debug mode (show full tracebacks)"),
        ] = False,
    ) -> None:
        """Start interactive REPL session for live MIDI composition.

        The REPL (Read-Eval-Print Loop) allows you to:
        - Write MML commands interactively
        - Define variables and aliases on the fly
        - Import device libraries
        - Inspect compiled MIDI events
        - Control tempo and resolution

        Meta-commands (start with .):
          .help         - Show available commands
          .quit/.exit   - Exit REPL
          .reset        - Clear all state
          .list         - Show variables, aliases, imports
          .inspect      - Show last compiled IR
          .tempo <bpm>  - Set tempo
          .ppq <value>  - Set resolution

        Keyboard shortcuts:
          Ctrl+C        - Cancel current input
          Ctrl+D        - Exit REPL
          Up/Down       - Navigate history
          Ctrl+R        - Search history
        """
        run_repl(debug=debug)
