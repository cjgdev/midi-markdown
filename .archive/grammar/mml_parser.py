"""
MIDI Markup Language (MML) Parser Implementation
Version 1.0.0

This module provides a complete parser for MML files using the Lark parsing library.
It transforms MML text into an Abstract Syntax Tree (AST) and provides utilities
for working with parsed MML documents.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from lark import Lark, Transformer, v_args

# ============================================================================
# Data Classes for AST Nodes
# ============================================================================


@dataclass
class Timing:
    """Represents a timing specification"""

    type: str  # 'absolute', 'musical', 'relative', 'simultaneous'
    value: Any
    raw: str


@dataclass
class MIDICommand:
    """Represents a MIDI command"""

    type: str
    channel: int | None = None
    data1: int | None = None
    data2: int | None = None
    params: dict[str, Any] = field(default_factory=dict)
    timing: Timing | None = None
    source_line: int = 0


@dataclass
class AliasDefinition:
    """Represents an alias definition"""

    name: str
    parameters: list[dict[str, Any]]
    commands: list[str | MIDICommand]
    description: str | None = None
    computed_values: dict[str, str] = field(default_factory=dict)
    is_macro: bool = False


@dataclass
class Track:
    """Represents a track in multi-track mode"""

    name: str
    channel: int | None = None
    events: list[Any] = field(default_factory=list)


@dataclass
class MMLDocument:
    """Represents a complete MML document"""

    frontmatter: dict[str, Any] = field(default_factory=dict)
    imports: list[str] = field(default_factory=list)
    defines: dict[str, Any] = field(default_factory=dict)
    aliases: dict[str, AliasDefinition] = field(default_factory=dict)
    tracks: list[Track] = field(default_factory=list)
    events: list[Any] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


# ============================================================================
# Lark Transformer
# ============================================================================


@v_args(inline=True)
class MMLTransformer(Transformer):
    """
    Transforms the Lark parse tree into structured Python objects.
    Each method corresponds to a grammar rule and transforms it into
    a meaningful data structure.
    """

    def __init__(self):
        super().__init__()
        self.current_track: Track | None = None
        self.line_number = 0

    # Document Structure
    def document(self, frontmatter, *statements):
        doc = MMLDocument()
        if frontmatter:
            doc.frontmatter = frontmatter

        for stmt in statements:
            if stmt is None:
                continue
            if isinstance(stmt, tuple) and stmt[0] == "import":
                doc.imports.append(stmt[1])
            elif isinstance(stmt, tuple) and stmt[0] == "define":
                doc.defines[stmt[1]] = stmt[2]
            elif isinstance(stmt, AliasDefinition):
                doc.aliases[stmt.name] = stmt
            elif isinstance(stmt, Track):
                doc.tracks.append(stmt)
            else:
                doc.events.append(stmt)

        return doc

    def frontmatter(self, content):
        """Parse YAML frontmatter"""
        try:
            return yaml.safe_load(str(content))
        except yaml.YAMLError:
            return {}

    # Imports and Definitions
    def import_stmt(self, path):
        return ("import", str(path).strip("\"'"))

    def define_stmt(self, name, value):
        return ("define", str(name), value)

    # Timing
    def absolute_time(self, *parts):
        time_str = "".join(str(p) for p in parts)
        return Timing("absolute", self._parse_absolute_time(time_str), time_str)

    def musical_time(self, bar, beat, tick):
        return Timing("musical", (int(bar), int(beat), int(tick)), f"{bar}.{beat}.{tick}")

    def relative_time(self, value, unit):
        return Timing("relative", (float(value), str(unit)), f"+{value}{unit}")

    def simultaneous(self):
        return Timing("simultaneous", None, "[@]")

    # MIDI Commands
    def note_command(self, cmd_type, channel_note, velocity, duration=None):
        channel, note = self._parse_channel_note(channel_note)
        return MIDICommand(
            type=str(cmd_type),
            channel=channel,
            data1=note,
            data2=int(velocity),
            params={"duration": duration} if duration else {},
        )

    def program_change(self, channel, program):
        return MIDICommand(type="program_change", channel=int(channel), data1=int(program))

    def control_change(self, channel, controller, value):
        return MIDICommand(
            type="control_change",
            channel=int(channel),
            data1=int(controller),
            data2=self._parse_cc_value(value),
        )

    def pitch_bend(self, channel, value):
        return MIDICommand(
            type="pitch_bend", channel=int(channel), data1=self._parse_pitch_bend(value)
        )

    def pressure_command(self, cmd_type, *args):
        if str(cmd_type) in ["channel_pressure", "cp"]:
            return MIDICommand(type="channel_pressure", channel=int(args[0]), data1=int(args[1]))
        # poly_pressure
        channel, note = self._parse_channel_note(args[0])
        return MIDICommand(type="poly_pressure", channel=channel, data1=note, data2=int(args[1]))

    def meta_event(self, event_type, *args):
        return MIDICommand(type=str(event_type), params={"args": args})

    def sysex_command(self, *hex_bytes):
        return MIDICommand(type="sysex", params={"bytes": [str(b) for b in hex_bytes]})

    # Alias System
    def simple_alias(self, name, template, description=None, computed=None):
        params = self._extract_params(template)
        return AliasDefinition(
            name=str(name),
            parameters=params,
            commands=[str(template)],
            description=str(description).strip("\"'") if description else None,
            computed_values=computed or {},
            is_macro=False,
        )

    def macro_alias(self, name, params, description, *commands):
        return AliasDefinition(
            name=str(name),
            parameters=self._parse_params(params),
            commands=list(commands),
            description=str(description).strip("\"'") if description else None,
            is_macro=True,
        )

    def alias_call(self, name, *args):
        return MIDICommand(type="alias_call", params={"alias_name": str(name), "args": list(args)})

    # Advanced Features
    def track_def(self, name, attributes=None):
        track = Track(name=str(name))
        if attributes and "channel" in attributes:
            track.channel = attributes["channel"]
        return track

    def loop_stmt(self, count, timing, interval, *statements):
        return {
            "type": "loop",
            "count": int(count),
            "start_time": timing,
            "interval": interval,
            "statements": list(statements),
        }

    def sweep_stmt(self, start_time, end_time, interval, *commands):
        return {
            "type": "sweep",
            "start_time": start_time,
            "end_time": end_time,
            "interval": interval,
            "commands": list(commands),
        }

    def conditional_stmt(self, if_clause, *other_clauses):
        return {
            "type": "conditional",
            "if": if_clause,
            "elif": [c for c in other_clauses if c[0] == "elif"],
            "else": next((c for c in other_clauses if c[0] == "else"), None),
        }

    # Expressions
    def add(self, left, right):
        return ("add", left, right)

    def sub(self, left, right):
        return ("sub", left, right)

    def mul(self, left, right):
        return ("mul", left, right)

    def div(self, left, right):
        return ("div", left, right)

    def mod(self, left, right):
        return ("mod", left, right)

    def variable_ref(self, name):
        return ("var", str(name))

    def number(self, n):
        return float(n)

    def integer(self, n):
        return int(n)

    def percent(self, value):
        return ("percent", int(value))

    def ramp_expr(self, start, end, ramp_type="linear"):
        return {
            "type": "ramp",
            "start": int(start),
            "end": int(end),
            "ramp_type": str(ramp_type) if ramp_type else "linear",
        }

    def random_expr(self, min_val, max_val):
        return {"type": "random", "min": min_val, "max": max_val}

    # Helper Methods
    def _parse_absolute_time(self, time_str: str) -> float:
        """Parse mm:ss.mmm format to seconds"""
        parts = time_str.strip("[]").split(":")
        minutes = int(parts[0])
        seconds = float(parts[1])
        return minutes * 60 + seconds

    def _parse_channel_note(self, channel_note) -> tuple:
        """Parse channel.note format"""
        # This is simplified - actual implementation would handle
        # note names (C4, D#5, etc.) and convert to MIDI numbers
        parts = str(channel_note).split(".")
        channel = int(parts[0])
        note = self._note_to_midi(parts[1]) if not parts[1].isdigit() else int(parts[1])
        return channel, note

    def _note_to_midi(self, note_name: str) -> int:
        """Convert note name (e.g., 'C4') to MIDI number"""
        note_map = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}

        # Parse note name
        base_note = note_name[0].upper()
        octave_start = 1

        # Handle sharps/flats
        if len(note_name) > 1 and note_name[1] in "#b":
            octave_start = 2
            if note_name[1] == "#":
                modifier = 1
            else:  # flat
                modifier = -1
        else:
            modifier = 0

        # Get octave
        octave = int(note_name[octave_start:])

        # Calculate MIDI number (C4 = 60)
        midi_num = note_map[base_note] + modifier + (octave + 1) * 12
        return midi_num

    def _parse_cc_value(self, value) -> int:
        """Parse CC value (can be int, percent, ramp, etc.)"""
        if isinstance(value, int):
            return value
        if isinstance(value, tuple) and value[0] == "percent":
            return int(value[1] * 127 / 100)
        # For ramp and random, return a placeholder
        # Actual implementation would handle these during event generation
        return 0

    def _parse_pitch_bend(self, value) -> int:
        """Parse pitch bend value"""
        if isinstance(value, str):
            if value.startswith("+") or value.startswith("-"):
                return 8192 + int(value)
        return int(value)

    def _extract_params(self, template) -> list[dict[str, Any]]:
        """Extract parameter definitions from alias template"""
        # Simplified - actual implementation would parse {param:type:range}
        import re

        params = []
        for match in re.finditer(r"\{([^}]+)\}", str(template)):
            param_str = match.group(1)
            params.append({"name": param_str.split(":")[0]})
        return params

    def _parse_params(self, params_tree) -> list[dict[str, Any]]:
        """Parse parameter specifications"""
        # Simplified implementation
        return []


# ============================================================================
# Parser Class
# ============================================================================


class MMLParser:
    """
    Main parser class for MIDI Markup Language.

    Usage:
        parser = MMLParser()
        document = parser.parse_file('song.mml')
        # or
        document = parser.parse_string(mml_content)
    """

    def __init__(self, grammar_file: str | None = None):
        """
        Initialize the parser with the grammar.

        Args:
            grammar_file: Path to the .lark grammar file.
                         If None, uses the embedded grammar.
        """
        if grammar_file:
            with open(grammar_file) as f:
                grammar = f.read()
        else:
            # Use embedded grammar (for production, load from file)
            grammar_file = Path(__file__).parent / "mml_grammar.lark"
            with open(grammar_file) as f:
                grammar = f.read()

        self.parser = Lark(
            grammar,
            parser="lalr",  # LALR parser for speed
            transformer=MMLTransformer(),
            start="document",
            propagate_positions=True,  # Track line/column numbers
            maybe_placeholders=False,
        )

    def parse_file(self, filepath: str | Path) -> MMLDocument:
        """
        Parse an MML file.

        Args:
            filepath: Path to the .mml file

        Returns:
            MMLDocument object containing the parsed content
        """
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        return self.parse_string(content, str(filepath))

    def parse_string(self, content: str, filename: str = "<string>") -> MMLDocument:
        """
        Parse MML content from a string.

        Args:
            content: MML markup content
            filename: Name for error reporting

        Returns:
            MMLDocument object
        """
        try:
            tree = self.parser.parse(content)
            return tree
        except Exception as e:
            self._format_parse_error(e, content, filename)
            raise

    def _format_parse_error(self, error, content: str, filename: str):
        """Format a parse error with context"""
        # Extract line information if available
        if hasattr(error, "line") and hasattr(error, "column"):
            lines = content.split("\n")
            error_line = lines[error.line - 1] if error.line <= len(lines) else ""

            print(f"\nError: Parse error at line {error.line}:{error.column} in {filename}")
            print(f"  {error_line}")
            print(f"  {' ' * (error.column - 1)}^")
            print(f"\n{error}")


# ============================================================================
# Utility Functions
# ============================================================================


def validate_midi_value(
    value: int, min_val: int = 0, max_val: int = 127, param_name: str = "value"
) -> bool:
    """Validate a MIDI value is in range"""
    if not isinstance(value, int):
        raise ValueError(f"{param_name} must be an integer")
    if not (min_val <= value <= max_val):
        raise ValueError(f"{param_name} {value} out of range [{min_val}, {max_val}]")
    return True


def timing_to_ticks(timing: Timing, ppq: int = 480, tempo: int = 120) -> int:
    """
    Convert a Timing object to absolute ticks.

    Args:
        timing: Timing object to convert
        ppq: Pulses per quarter note (resolution)
        tempo: Current tempo in BPM

    Returns:
        Absolute tick value
    """
    if timing.type == "absolute":
        # Convert seconds to ticks
        seconds = timing.value
        microseconds_per_quarter = 60_000_000 / tempo
        ticks = int((seconds * 1_000_000) / microseconds_per_quarter * ppq)
        return ticks

    if timing.type == "musical":
        bar, beat, tick = timing.value
        # Assuming 4/4 time signature
        ticks = ((bar - 1) * 4 + (beat - 1)) * ppq + tick
        return ticks

    if timing.type == "relative":
        # Relative timing needs previous event context
        return 0  # Placeholder

    if timing.type == "simultaneous":
        return 0  # Same as previous

    return 0


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    # Example MML content
    example_mml = """---
title: "Test Song"
midi_format: 1
ppq: 480
default_channel: 1
---

@import "devices/quad_cortex.mml"

@define MAIN_TEMPO 120
@define VERSE_PRESET 2

## Track 1: Control
@track control channel=1

[00:00.000]
- tempo ${MAIN_TEMPO}
- marker "Intro"
- pc 1.${VERSE_PRESET}

[00:04.000]
- cc 1.7.100

[00:08.000]
- note_on 1.C4 100 1b
"""

    # Create parser and parse
    parser = MMLParser()

    try:
        doc = parser.parse_string(example_mml)

        print("Parsed MML Document:")
        print(f"Title: {doc.frontmatter.get('title', 'Untitled')}")
        print(f"Imports: {doc.imports}")
        print(f"Defines: {doc.defines}")
        print(f"Tracks: {len(doc.tracks)}")
        print(f"Events: {len(doc.events)}")

    except Exception as e:
        print(f"Parse error: {e}")
