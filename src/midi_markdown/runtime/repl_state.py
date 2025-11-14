"""REPL state management for interactive MML sessions.

This module provides the REPLState class which maintains all stateful information
during an interactive REPL session, including variables, aliases, imports, and
compilation results.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path

    from midi_markdown.core.ir import IRProgram


@dataclass
class REPLState:
    """Encapsulated REPL state - no global variables.

    This class maintains all state for an interactive REPL session, including:
    - User-defined variables from @define statements
    - Alias definitions from @alias blocks and @import statements
    - Loaded device library paths
    - Global settings (tempo, resolution, time signature)
    - Last compiled IR program for inspection

    The state can be persisted to JSON and restored later, enabling session save/load.

    Example:
        >>> state = REPLState()
        >>> state.tempo = 140
        >>> state.variables["velocity"] = 80
        >>> state.save_session(Path("my_session.json"))
        >>> # Later...
        >>> new_state = REPLState()
        >>> new_state.load_session(Path("my_session.json"))
        >>> assert new_state.tempo == 140
    """

    variables: dict[str, Any] = field(default_factory=dict)
    """User-defined variables from @define statements."""

    aliases: dict[str, Any] = field(default_factory=dict)
    """Alias definitions from @alias blocks and @import statements."""

    imports: list[str] = field(default_factory=list)
    """List of loaded device library file paths."""

    tempo: int = 120
    """Current tempo in beats per minute (BPM)."""

    resolution: int = 480
    """Pulses per quarter note (PPQ) resolution."""

    time_signature: tuple[int, int] = (4, 4)
    """Time signature as (numerator, denominator) tuple."""

    last_ir: IRProgram | None = None
    """Last compiled IR program, used by .inspect command (not serialized)."""

    def reset(self) -> None:
        """Clear all state back to default values.

        This reinitializes the entire state object, clearing all variables,
        aliases, imports, and resetting tempo/resolution to defaults.

        Example:
            >>> state = REPLState()
            >>> state.variables["foo"] = 42
            >>> state.tempo = 140
            >>> state.reset()
            >>> assert state.variables == {}
            >>> assert state.tempo == 120
        """
        self.__init__()

    def save_session(self, path: Path) -> None:
        """Persist state to JSON file.

        Serializes the current state (excluding last_ir) to a JSON file.
        The file can later be loaded with load_session() to restore the state.

        Args:
            path: File path to save the session to

        Raises:
            OSError: If file cannot be written

        Example:
            >>> state = REPLState()
            >>> state.tempo = 140
            >>> state.save_session(Path("session.json"))
        """
        # Create serializable dict (exclude last_ir which is not serializable)
        session_data = {
            "variables": self.variables,
            "aliases": self.aliases,
            "imports": self.imports,
            "tempo": self.tempo,
            "resolution": self.resolution,
            "time_signature": self.time_signature,
        }

        # Write to file with pretty formatting
        with path.open("w") as f:
            json.dump(session_data, f, indent=2)

    def load_session(self, path: Path) -> None:
        """Restore state from JSON file.

        Loads a previously saved session from a JSON file and updates the
        current state. Note that last_ir is not restored (it's not serialized).

        Args:
            path: File path to load the session from

        Raises:
            FileNotFoundError: If file does not exist
            json.JSONDecodeError: If file is not valid JSON
            KeyError: If required fields are missing

        Example:
            >>> state = REPLState()
            >>> state.load_session(Path("session.json"))
            >>> assert state.tempo > 0  # Loaded from file
        """
        with path.open("r") as f:
            session_data = json.load(f)

        # Update state from loaded data
        self.variables = session_data["variables"]
        self.aliases = session_data["aliases"]
        self.imports = session_data["imports"]
        self.tempo = session_data["tempo"]
        self.resolution = session_data["resolution"]
        self.time_signature = tuple(session_data["time_signature"])

    def update_from_frontmatter(self, frontmatter: dict[str, Any]) -> None:
        """Update state from MML frontmatter.

        Extracts tempo, ppq, and time_signature from frontmatter dictionary
        and updates the corresponding state fields.

        Args:
            frontmatter: Parsed YAML frontmatter from MML document

        Example:
            >>> state = REPLState()
            >>> frontmatter = {"tempo": 140, "ppq": 960, "time_signature": "3/4"}
            >>> state.update_from_frontmatter(frontmatter)
            >>> assert state.tempo == 140
            >>> assert state.resolution == 960
            >>> assert state.time_signature == (3, 4)
        """
        if "tempo" in frontmatter:
            self.tempo = int(frontmatter["tempo"])

        if "ppq" in frontmatter:
            self.resolution = int(frontmatter["ppq"])

        if "time_signature" in frontmatter:
            # Parse time signature string like "4/4" or "3/4"
            ts = frontmatter["time_signature"]
            if isinstance(ts, str) and "/" in ts:
                numerator, denominator = ts.split("/")
                self.time_signature = (int(numerator), int(denominator))
            elif isinstance(ts, list | tuple):
                # Expect time signature as [numerator, denominator]
                if len(ts) >= 2:
                    self.time_signature = (int(ts[0]), int(ts[1]))
