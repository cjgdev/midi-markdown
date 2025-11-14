"""Context-aware autocompletion for MMD REPL.

This module provides the MusicCompleter class which offers intelligent,
context-sensitive completion suggestions for MIDI commands, aliases, variables,
note names, and meta-commands.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from prompt_toolkit.completion import Completer, Completion

if TYPE_CHECKING:
    from collections.abc import Iterable

    from prompt_toolkit.completion import CompleteEvent
    from prompt_toolkit.document import Document

    from .repl_state import REPLState


class MusicCompleter(Completer):
    """Context-aware completer for MML syntax.

    Provides intelligent autocompletion based on what the user is typing:
    - MIDI commands (note_on, cc, pc, etc.)
    - Meta-commands (.help, .quit, .reset, etc.)
    - Directives (@define, @alias, @import, etc.)
    - Alias names from loaded device libraries
    - Variable names from @define statements
    - Note names (C-1 through G9, with sharps/flats)

    The completer is context-aware and only suggests relevant completions
    based on the current input position.

    Example:
        >>> from midi_markdown.runtime import REPLState, MusicCompleter
        >>> state = REPLState()
        >>> completer = MusicCompleter(state)
        >>> # Use with PromptSession:
        >>> # session = PromptSession(completer=completer)
    """

    def __init__(self, state: REPLState) -> None:
        """Initialize the completer with REPL state.

        Args:
            state: REPLState instance containing aliases and variables
        """
        self.state = state

        # MIDI commands (channel voice messages)
        self.midi_commands = [
            "note_on",
            "note_off",
            "cc",
            "pc",
            "pitch_bend",
            "poly_pressure",
            "channel_pressure",
            "sysex",
        ]

        # Meta-commands (REPL control commands)
        self.meta_commands = [
            ".help",
            ".quit",
            ".exit",
            ".reset",
            ".list",
            ".inspect",
            ".load",
            ".save",
            ".tempo",
            ".ppq",
        ]

        # Directives (MML document structures)
        self.directives = [
            "@define",
            "@alias",
            "@import",
            "@loop",
            "@sweep",
            "@if",
            "@elif",
            "@else",
            "@end",
        ]

        # Generate all valid note names
        self.note_names = self._generate_note_names()

    def _generate_note_names(self) -> list[str]:
        """Generate all valid MIDI note names.

        Creates note names from C-1 (MIDI 0) through G9 (MIDI 127),
        including both sharps and flats for applicable notes.

        Returns:
            List of all 120+ valid note name strings

        Example:
            >>> completer = MusicCompleter(REPLState())
            >>> "C4" in completer.note_names
            True
            >>> "C#4" in completer.note_names
            True
            >>> "Db4" in completer.note_names
            True
        """
        notes = []
        note_letters = ["C", "D", "E", "F", "G", "A", "B"]

        for octave in range(-1, 10):  # -1 to 9 (MIDI 0-127)
            for letter in note_letters:
                # Natural note
                notes.append(f"{letter}{octave}")

                # Sharp (C#, D#, F#, G#, A#) - no B# or E#
                if letter in ["C", "D", "F", "G", "A"]:
                    notes.append(f"{letter}#{octave}")

                # Flat (Db, Eb, Gb, Ab, Bb) - no Cb or Fb
                if letter in ["D", "E", "G", "A", "B"]:
                    notes.append(f"{letter}b{octave}")

        return notes

    def get_completions(
        self,
        document: Document,
        complete_event: CompleteEvent,
    ) -> Iterable[Completion]:
        """Provide context-sensitive completions.

        Analyzes the current input and returns appropriate completions based on:
        - Line content (meta-commands, directives, MIDI commands)
        - Cursor position (current word being typed)
        - REPL state (available aliases and variables)

        Args:
            document: Current document/input state
            complete_event: Completion trigger event

        Yields:
            Completion objects for valid suggestions

        Example:
            >>> from prompt_toolkit.document import Document
            >>> doc = Document("- no", cursor_position=4)
            >>> completions = list(completer.get_completions(doc, None))
            >>> any(c.text == "note_on" for c in completions)
            True
        """
        # Get current word and line context
        word = document.get_word_before_cursor()
        line = document.current_line_before_cursor.strip()

        # Context-based routing
        if line.startswith("."):
            # Meta-commands (REPL control)
            yield from self._complete_meta_commands(word)

        elif line.startswith("@"):
            # Directives (@define, @alias, etc.)
            yield from self._complete_directives(word)

        elif "${" in line and "}" not in line.split("${")[-1]:
            # Variable reference (inside ${...})
            yield from self._complete_variables(word)

        elif line.startswith("-") or (line.startswith("[") and "]" in line):
            # After dash or timing marker - could be command or alias
            yield from self._complete_midi_commands(word)
            yield from self._complete_aliases(word)

        else:
            # Default: MIDI commands
            yield from self._complete_midi_commands(word)

    def _complete_meta_commands(self, word: str) -> Iterable[Completion]:
        """Complete meta-commands starting with dot.

        Args:
            word: Current word being typed

        Yields:
            Completion objects for matching meta-commands
        """
        word_lower = word.lstrip(".").lower()
        for cmd in self.meta_commands:
            if cmd.lstrip(".").lower().startswith(word_lower):
                # Determine description based on command
                descriptions = {
                    ".help": "Show available commands",
                    ".quit": "Exit REPL",
                    ".exit": "Exit REPL",
                    ".reset": "Clear all state",
                    ".list": "Show variables/aliases",
                    ".inspect": "Show last compiled IR",
                    ".load": "Load MML file",
                    ".save": "Save session",
                    ".tempo": "Get/set tempo",
                    ".ppq": "Get/set resolution",
                }
                yield Completion(
                    text=cmd,
                    start_position=-len(word),
                    display_meta=descriptions.get(cmd, "Meta-command"),
                )

    def _complete_directives(self, word: str) -> Iterable[Completion]:
        """Complete MML directives starting with @.

        Args:
            word: Current word being typed

        Yields:
            Completion objects for matching directives
        """
        word_lower = word.lstrip("@").lower()
        for directive in self.directives:
            if directive.lstrip("@").lower().startswith(word_lower):
                # Determine description based on directive
                descriptions = {
                    "@define": "Define variable",
                    "@alias": "Define alias",
                    "@import": "Import device library",
                    "@loop": "Repeat commands",
                    "@sweep": "Ramp parameter",
                    "@if": "Conditional branch",
                    "@elif": "Else-if branch",
                    "@else": "Else branch",
                    "@end": "End block",
                }
                yield Completion(
                    text=directive,
                    start_position=-len(word),
                    display_meta=descriptions.get(directive, "Directive"),
                )

    def _complete_midi_commands(self, word: str) -> Iterable[Completion]:
        """Complete MIDI command names.

        Args:
            word: Current word being typed

        Yields:
            Completion objects for matching MIDI commands
        """
        word_lower = word.lower()
        for cmd in self.midi_commands:
            if cmd.lower().startswith(word_lower):
                # Provide helpful descriptions
                descriptions = {
                    "note_on": "Note On message",
                    "note_off": "Note Off message",
                    "cc": "Control Change",
                    "pc": "Program Change",
                    "pitch_bend": "Pitch Bend",
                    "poly_pressure": "Polyphonic Aftertouch",
                    "channel_pressure": "Channel Aftertouch",
                    "sysex": "System Exclusive",
                }
                yield Completion(
                    text=cmd,
                    start_position=-len(word),
                    display_meta=descriptions.get(cmd, "MIDI command"),
                )

    def _complete_aliases(self, word: str) -> Iterable[Completion]:
        """Complete alias names from REPL state.

        Args:
            word: Current word being typed

        Yields:
            Completion objects for matching aliases
        """
        word_lower = word.lower()
        for alias_name in self.state.aliases:
            if alias_name.lower().startswith(word_lower):
                yield Completion(
                    text=alias_name,
                    start_position=-len(word),
                    display_meta="Alias",
                )

    def _complete_variables(self, word: str) -> Iterable[Completion]:
        """Complete variable names from REPL state.

        Args:
            word: Current word being typed

        Yields:
            Completion objects for matching variables
        """
        word_lower = word.lower()
        for var_name in self.state.variables:
            if var_name.lower().startswith(word_lower):
                # Show variable value in meta
                value = self.state.variables[var_name]
                yield Completion(
                    text=var_name,
                    start_position=-len(word),
                    display_meta=f"= {value}",
                )

    def _complete_note_names(self, word: str) -> Iterable[Completion]:
        """Complete note names (for use in note parameters).

        Args:
            word: Current word being typed

        Yields:
            Completion objects for matching note names
        """
        word_upper = word.upper()
        # Limit to prevent overwhelming completion list
        count = 0
        max_completions = 50

        for note in self.note_names:
            if note.upper().startswith(word_upper):
                yield Completion(
                    text=note,
                    start_position=-len(word),
                    display_meta="Note name",
                )
                count += 1
                if count >= max_completions:
                    break
