"""
MIDI Markup Language (MML) Parser Implementation

This module provides the complete parser for MML files using the Lark parsing library.
It transforms MML text into an Abstract Syntax Tree (AST) and provides utilities
for working with parsed MML documents.
"""

from __future__ import annotations

from typing import Any

import yaml
from lark import Token, Transformer, v_args

from midi_markdown.alias.computation import ComputationError, SafeComputationEngine
from midi_markdown.expansion.variables import SymbolTable
from midi_markdown.utils.parameter_types import note_to_midi, percent_to_midi

from .ast_nodes import AliasDefinition, MIDICommand, MMDDocument, Timing, Track

# ============================================================================
# Lark Transformer
# ============================================================================


@v_args(inline=True)
class MMDTransformer(Transformer):
    """
    Transforms the Lark parse tree into structured Python objects.
    Each method corresponds to a grammar rule and transforms it into
    a meaningful data structure.
    """

    def __init__(self):
        super().__init__()
        self.current_track: Track | None = None
        self.line_number = 0
        self.symbol_table = SymbolTable()
        self.computation_engine = SafeComputationEngine()

    # Document Structure
    def document(self, *args):
        """Handle document with optional frontmatter"""
        doc = MMDDocument()

        # Handle empty document
        if not args:
            return doc

        # Parse arguments - frontmatter may or may not be present
        # First arg is either frontmatter (dict without 'type') or a statement
        first_arg = args[0]
        statements_start = 0

        if first_arg and isinstance(first_arg, dict) and "type" not in first_arg:
            # It's actual YAML frontmatter
            doc.frontmatter = first_arg
            statements_start = 1

        # Track the current track context for multi-track files
        current_track: Track | None = None

        # Process statements
        for stmt in args[statements_start:]:
            if stmt is None:
                continue
            if isinstance(stmt, tuple) and len(stmt) >= 2:
                if stmt[0] == "import":
                    doc.imports.append(stmt[1])
                elif stmt[0] == "define":
                    doc.defines[stmt[1]] = stmt[2]
            elif isinstance(stmt, AliasDefinition):
                doc.aliases[stmt.name] = stmt
            elif isinstance(stmt, Track):
                # Switch to this track - subsequent events go to this track
                doc.tracks.append(stmt)
                current_track = stmt
            # Add events to current track if in track context, else to top-level
            elif current_track is not None:
                current_track.events.append(stmt)
            else:
                doc.events.append(stmt)

        return doc

    def yaml_content(self, content):
        """Extract YAML content from token"""
        return str(content)

    def frontmatter(self, yaml_text):
        """Parse YAML frontmatter"""
        try:
            return yaml.safe_load(yaml_text)
        except yaml.YAMLError:
            return {}

    # Imports and Definitions
    def import_stmt(self, path):
        """Transform @import statement into tuple format.

        Args:
            path: Path string with quotes (e.g., '"devices/quad_cortex.mmd"')

        Returns:
            Tuple of ("import", path_without_quotes)
        """
        return ("import", str(path).strip("\"'"))

    def define_stmt(self, name, value):
        """Handle @define statement - store in symbol table and return tuple."""
        var_name = str(name)

        # Resolve the value - could be literal, string, or expression tree
        resolved_value = self._resolve_define_value(value)

        # Store in symbol table
        try:
            self.symbol_table.define(var_name, resolved_value)
        except ValueError as e:
            # Re-raise with line number if available
            msg = f"Error in @define {var_name}: {e}"
            raise ValueError(msg)

        # Still return tuple for doc.defines
        return ("define", var_name, resolved_value)

    # Timing (now terminals)
    def ABSOLUTE_TIME(self, token):
        """Handle terminal ABSOLUTE_TIME"""
        time_str = str(token).strip("[]")
        return Timing("absolute", self._parse_absolute_time(time_str), str(token))

    def MUSICAL_TIME(self, token):
        """Handle terminal MUSICAL_TIME"""
        time_str = str(token).strip("[]")
        parts = time_str.split(".")
        return Timing("musical", (int(parts[0]), int(parts[1]), int(parts[2])), str(token))

    def RELATIVE_TIME(self, token):
        """Handle terminal RELATIVE_TIME

        Supports two formats:
        - Relative musical time: [+bars.beats.ticks] e.g., [+2.1.0]
        - Relative time with unit: [+value(unit)] e.g., [+1b], [+500ms], [+2.5s]
        """
        time_str = str(token).strip("[+]")
        import re

        # Try matching as relative musical time first (bars.beats.ticks)
        musical_match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", time_str)
        if musical_match:
            bars, beats, ticks = musical_match.groups()
            return Timing("relative", (int(bars), int(beats), int(ticks)), str(token))

        # Fall back to relative time with unit (value + unit)
        # ms must be checked before s in the pattern
        unit_match = re.match(r"^([\d.]+)(ms|[smbt])$", time_str)
        if unit_match:
            value, unit = unit_match.groups()
            return Timing("relative", (float(value), unit), str(token))

        # Default fallback (should not reach here with correct grammar)
        return Timing("relative", (0, "s"), str(token))

    @v_args(inline=False)
    def relative_time(self, items):
        """Handle relative_time parser rule.

        Grammar:
            relative_time: RELATIVE_MUSICAL_TIME | "[+" duration "]"

        Args:
            items: List containing either:
                - RELATIVE_MUSICAL_TIME token (like "[+2.1.0]")
                - duration tuple (number, unit)
                - variable_ref tuple ('var', name)
                - param_ref tuple ('param_ref', {...})

        Returns:
            Timing object with type="relative"
        """
        value = items[0]

        # Check if it's a RELATIVE_MUSICAL_TIME terminal (includes brackets)
        if isinstance(value, Token) and value.type == "RELATIVE_MUSICAL_TIME":
            # Extract the time value from the token (remove [+ and ])
            time_str = str(value)[2:-1]  # Remove "[+" and "]"
            parts = time_str.split(".")
            raw = str(value)
            return Timing("relative", (int(parts[0]), int(parts[1]), int(parts[2])), raw)

        # Otherwise it's a duration (could be literal, variable_ref, or param_ref)
        # Duration can be:
        # - A tuple (number, unit) from the duration transformer
        # - A variable_ref tuple like ('var', 'VAR_NAME')
        # - A param_ref tuple like ('param_ref', {...})
        if isinstance(value, tuple):
            if value[0] == "var":
                # Variable reference - store as-is for later resolution
                raw = f"[+${{{value[1]}}}]"
                return Timing("relative", value, raw)
            if value[0] == "param_ref":
                # Parameter reference (in alias body) - store as-is
                param_name = value[1].get("name", "unknown")
                raw = f"[+{{{param_name}}}]"
                return Timing("relative", value, raw)
            if len(value) == 2 and isinstance(value[0], int | float) and isinstance(value[1], str):
                # Duration tuple (number, unit) from duration transformer
                num, unit = value
                raw = f"[+{int(num) if num == int(num) else num}{unit}]"
                return Timing("relative", value, raw)
        elif isinstance(value, str):
            # String duration like "2b" - parse the value and unit (legacy path)
            import re

            match = re.match(r"^([\d.]+)(ms|[smbt])$", value)
            if match:
                num_str, unit = match.groups()
                # Convert to float first, then to int if it's a whole number
                num = float(num_str)
                if num.is_integer():
                    num = int(num)
                raw = f"[+{value}]"
                return Timing("relative", (num, unit), raw)

        # Fallback for unexpected format
        raw = f"[+{value}]"
        return Timing("relative", value, raw)

    def simultaneous(self):
        """Transform [@] simultaneous timing marker.

        Returns:
            Timing object with type="simultaneous" indicating event occurs
            at same time as previous event
        """
        return Timing("simultaneous", None, "[@]")

    def timing(self, time_spec):
        """Handle timing rule - just return the timing object"""
        return time_spec

    # Terminal transformers
    def STRING(self, token):
        """Strip quotes from STRING tokens"""
        return str(token).strip("\"'")

    def INT(self, token):
        """Convert INT tokens to int"""
        return int(token)

    def FLOAT(self, token):
        """Convert FLOAT tokens to float"""
        return float(token)

    def NUMBER(self, token):
        """Convert NUMBER tokens - preserve int vs float.

        This is important because integer values (like 60) should remain
        as int (60) not float (60.0), especially for note numbers and
        other MIDI values that require integers.
        """
        value = float(token)
        if value.is_integer():
            return int(value)
        return value

    def cc_value(self, value):
        """Extract CC value from rule"""
        return value

    def modulated_value(self, value):
        """Handle modulated_value rule - pass through for later resolution.

        Grammar: modulated_value: param | ramp_expr | random_expr | curve_expr | wave_expr | envelope_expr

        Value can be:
        - int (from param → INT)
        - tuple (from param → variable_ref)
        - RandomExpression (from random_expr)
        - CurveExpression (from curve_expr)
        - WaveExpression (from wave_expr)
        - EnvelopeExpression (from envelope_expr)
        - RampExpression (from ramp_expr)
        """
        return value  # Preserve type for later handling

    def timed_event(self, timing, command_list=None):
        """Handle timed events with optional commands"""
        if command_list is None:
            # Just timing, no commands
            return {"type": "timed_event", "timing": timing, "commands": []}
        # Timing with commands
        return {"type": "timed_event", "timing": timing, "commands": command_list}

    def command_list(self, *commands):
        """Handle command list"""
        return list(commands)

    # MIDI Commands
    def velocity(self, value):
        """Handle velocity rule - pass through for later resolution.

        Value can be:
        - int (from INT token)
        - tuple (from variable_ref)
        - RandomExpression (from random_expr)
        """
        return value  # Preserve type for later handling

    def pb_value(self, value):
        """Handle pitch bend value rule"""
        return self._parse_pitch_bend(value)

    def channel_note(self, channel, note):
        """Handle channel_note rule - return as tuple to preserve RandomExpression.

        Returns tuple (channel, note) where note can be:
        - int (MIDI note number)
        - str (note name like "C4")
        - tuple (variable reference)
        - RandomExpression (random note selection)
        """
        return (int(channel), note)  # Return tuple instead of string

    def note_value(self, value):
        """Handle note_value rule - pass through for later resolution.

        Value can be:
        - NOTE_NAME token (e.g., "C4")
        - int (from param)
        - tuple (from variable_ref via param)
        - RandomExpression (from random_expr)
        """
        return value  # Preserve type for later handling

    @v_args(inline=False)
    def duration(self, children):
        """Handle duration rule.

        Grammar: duration: FLOAT (TIME_UNIT_S | TIME_UNIT_MS | TIME_UNIT_B | TIME_UNIT_T)
                        | INT (TIME_UNIT_S | TIME_UNIT_MS | TIME_UNIT_B | TIME_UNIT_T)
                        | random_expr (TIME_UNIT_S | TIME_UNIT_MS | TIME_UNIT_B | TIME_UNIT_T)
                        | variable_ref
                        | param_ref

        Note: This method uses @v_args(inline=False) to handle multiple alternatives
        with different numbers of children.

        Args:
            children: List of matched children, can be:
                - [number, unit] for FLOAT/INT/random_expr with TIME_UNIT alternatives
                - [ref] for variable_ref or param_ref alternatives

        Returns:
            - Tuple (number, unit) for duration values to avoid string unpacking
            - Tuple ('var', name) or ('param_ref', {...}) for variables/params

        Examples:
        - "1.25b" → [1.25, Token('TIME_UNIT_B', 'b')] → (1.25, "b")
        - "500ms" → [500, Token('TIME_UNIT_MS', 'ms')] → (500, "ms")
        - "2b" → [2, Token('TIME_UNIT_B', 'b')] → (2, "b")
        - "${VAR}" → [('var', 'VAR')] → ('var', 'VAR')
        """
        if len(children) >= 2:
            number = children[0]
            # Convert float to int if it's a whole number
            if isinstance(number, float) and number.is_integer():
                number = int(number)
            # Extract unit from Token
            unit = str(children[1]) if isinstance(children[1], Token) else str(children[1])
            # Return tuple to avoid string unpacking by @v_args(inline=True)
            return (float(number) if isinstance(number, int | float) else number, unit)
        if len(children) == 1:
            # variable_ref or param_ref - return as-is
            return children[0]
        return (1.0, "b")  # Default

    @v_args(inline=False)
    def note_command(self, args):
        """Handle note_command - extract note type from grammar alternative"""
        # Grammar: "-" NOTE_ON channel_note velocity duration?
        # args will be [note_type_token, channel_note_tuple, velocity, duration?]
        note_type_token = args[0]
        note_type = str(note_type_token).lower()  # "note_on" or "note_off"

        channel_note = args[1]
        velocity = args[2]
        duration = args[3] if len(args) > 3 else None

        channel, note = self._parse_channel_note(channel_note)

        # Resolve velocity (can be int, variable reference, or RandomExpression)
        from midi_markdown.parser.ast_nodes import RandomExpression

        velocity_val = self._resolve_param(velocity)
        # Only convert to int if it's not a tuple (variable) or RandomExpression
        velocity_int = (
            int(velocity_val)
            if not isinstance(velocity_val, tuple | RandomExpression)
            else velocity_val
        )

        return MIDICommand(
            type=note_type,
            channel=channel,
            data1=note,
            data2=velocity_int,
            params={"duration": duration} if duration else {},
        )

    def program_change(self, channel, program):
        """Transform program change (PC) MIDI command.

        Args:
            channel: MIDI channel (1-16) or variable reference
            program: Program number (0-127) or variable reference

        Returns:
            MIDICommand object with type="pc"
        """
        # Resolve variables if present
        channel_val = self._resolve_param(channel)
        program_val = self._resolve_param(program)

        # Only convert to int if not a tuple (forward reference)
        channel_int = int(channel_val) if not isinstance(channel_val, tuple) else channel_val
        program_int = int(program_val) if not isinstance(program_val, tuple) else program_val

        return MIDICommand(type="pc", channel=channel_int, data1=program_int)

    def control_change(self, channel, controller, value):
        """Transform control change (CC) MIDI command.

        Args:
            channel: MIDI channel (1-16) or variable reference
            controller: CC number (0-127) or variable reference
            value: CC value (0-127), can be integer or percent

        Returns:
            MIDICommand object with type="cc"
        """
        # Resolve variables if present
        channel_val = self._resolve_param(channel)
        controller_val = self._resolve_param(controller)

        # Only convert to int if not a tuple (forward reference)
        channel_int = int(channel_val) if not isinstance(channel_val, tuple) else channel_val
        controller_int = (
            int(controller_val) if not isinstance(controller_val, tuple) else controller_val
        )

        return MIDICommand(
            type="cc", channel=channel_int, data1=controller_int, data2=self._parse_cc_value(value)
        )

    def pitch_bend(self, channel, value):
        """Transform pitch bend MIDI command.

        Args:
            channel: MIDI channel (1-16)
            value: Pitch bend value (-8192 to +8191)

        Returns:
            MIDICommand object with type="pitch_bend"
        """
        return MIDICommand(
            type="pitch_bend", channel=int(channel), data1=self._parse_pitch_bend(value)
        )

    def pressure_value(self, value):
        """Handle pressure_value rule - pass through for later resolution.

        Grammar: pressure_value: param | random_expr

        Value can be:
        - int (from param → INT)
        - tuple (from param → variable_ref)
        - RandomExpression (from random_expr)
        """
        return value  # Preserve type for later handling

    def pressure_command(self, *args):
        """Handle pressure commands (channel_pressure or poly_pressure)"""
        from midi_markdown.parser.ast_nodes import (
            CurveExpression,
            EnvelopeExpression,
            RandomExpression,
            WaveExpression,
        )

        # Distinguish by number of arguments:
        # channel_pressure: 2 args (channel, pressure_value)
        # poly_pressure: 3 args (channel, note, pressure_value)
        if len(args) == 2:
            # channel_pressure 1.64 → args = (1, 64)
            # Pressure value may be modulation expression, tuple (variable), or int
            pressure_val = args[1]
            if not isinstance(
                pressure_val,
                RandomExpression | CurveExpression | WaveExpression | EnvelopeExpression | tuple,
            ):
                pressure_val = int(pressure_val)
            return MIDICommand(type="channel_pressure", channel=int(args[0]), data1=pressure_val)
        # len(args) == 3
        # poly_pressure 1.C4.80 → args = (1, 'C4', 80)
        channel = int(args[0])
        note = self._note_to_midi(args[1]) if not str(args[1]).isdigit() else int(args[1])
        # Pressure value may be modulation expression, tuple (variable), or int
        pressure_val = args[2]
        if not isinstance(
            pressure_val,
            RandomExpression | CurveExpression | WaveExpression | EnvelopeExpression | tuple,
        ):
            pressure_val = int(pressure_val)
        return MIDICommand(type="poly_pressure", channel=channel, data1=note, data2=pressure_val)

    @v_args(inline=False)
    def meta_event(self, args):
        """Handle meta_event - extract event type from grammar alternative"""
        # args will be [meta_type_token, value?]
        # The first arg is the META_* terminal (META_TEMPO, META_MARKER, etc.)
        meta_type_token = args[0]
        meta_type_str = str(meta_type_token).lower()  # e.g., "tempo", "marker", "text"

        # Strip META_ prefix if present
        if meta_type_str.startswith("meta_"):
            meta_type_str = meta_type_str[5:]  # Remove "META_"

        # Handle different meta event types
        if meta_type_str in ("tempo", "META_TEMPO"):
            # tempo event: args = [META_TEMPO, NUMBER]
            return MIDICommand(type="tempo", data1=int(args[1]))
        if meta_type_str in (
            "text",
            "marker",
            "lyric",
            "cue_point",
            "copyright",
            "track_name",
            "instrument_name",
            "device_name",
            "META_TEXT",
            "META_MARKER",
            "META_LYRIC",
            "META_CUE_POINT",
            "META_COPYRIGHT",
            "META_TRACK_NAME",
            "META_INSTRUMENT_NAME",
            "META_DEVICE_NAME",
        ):
            # String-based meta events: args = [META_TYPE, STRING]
            # Extract the base type (e.g., "text" from "META_TEXT")
            base_type = meta_type_str.replace("meta_", "").replace("_", "")
            text_value = str(args[1]).strip("\"'")
            return MIDICommand(type=base_type, params={"text": text_value})
        if meta_type_str in ("time_signature", "META_TIME_SIG"):
            # time_signature event: args = [META_TIME_SIG, time_sig_tree]
            return MIDICommand(type="time_signature", params={"time_sig": args[1]})
        if meta_type_str in ("key_signature", "META_KEY_SIG"):
            # key_signature event: args = [META_KEY_SIG, key_sig_tree]
            return MIDICommand(type="key_signature", params={"key_sig": args[1]})
        if meta_type_str in ("end_of_track", "META_END_OF_TRACK"):
            # end_of_track event: args = [META_END_OF_TRACK]
            return MIDICommand(type="end_of_track")
        # Unknown meta event type
        return MIDICommand(type="meta_event", params={"args": args})

    def sysex_bytes(self, *items):
        """Extract hex bytes from sysex_bytes tree, filtering out newlines.

        Args:
            *items: Mix of hex byte tokens and potentially newline separators

        Returns:
            List of hex byte tokens (strings)
        """
        # Filter out any non-hex-byte items (like newlines if they leaked through)
        # In practice, items should be HEX_BYTE tokens due to grammar structure
        hex_bytes = []
        for item in items:
            # HEX_BYTE tokens are Token objects with .value attribute
            if hasattr(item, "value") or isinstance(item, str):
                hex_bytes.append(item)
        return hex_bytes

    def sysex_command(self, *args):
        """Transform SysEx (System Exclusive) MIDI command.

        Args:
            *args: Either a list of hex bytes (from sysex_bytes) or a string (from sysex_file)

        Returns:
            MIDICommand object with type="sysex" and bytes in params
        """
        # If we get a list (from sysex_bytes), it's already been processed
        # If we get individual tokens, collect them
        hex_bytes = args[0] if len(args) == 1 and isinstance(args[0], list) else args
        return MIDICommand(type="sysex", params={"bytes": [str(b) for b in hex_bytes]})

    def channel_reset(self, *args):
        """Handle channel mode/reset messages"""
        # First arg is the command type terminal (CHAN_*)
        # Remaining args are the parameters
        # args is a list of tokens
        cmd_token = args[0][0] if isinstance(args[0], list) else args[0]
        cmd_type = cmd_token.type if hasattr(cmd_token, "type") else str(cmd_token)
        channel = int(args[0][1] if isinstance(args[0], list) else args[1])

        # Map terminal name to MIDI command type
        type_map = {
            "CHAN_ALL_NOTES_OFF": "all_notes_off",
            "CHAN_ALL_SOUND_OFF": "all_sound_off",
            "CHAN_RESET_CONTROLLERS": "reset_all_controllers",
            "CHAN_LOCAL_CONTROL": "local_control",
            "CHAN_MONO_MODE": "mono_mode",
            "CHAN_POLY_MODE": "poly_mode",
        }

        midi_type = type_map.get(cmd_type, "channel_reset")

        # Handle special cases with extra parameters
        token_list = args[0] if isinstance(args[0], list) else args
        if cmd_type == "CHAN_LOCAL_CONTROL" and len(token_list) > 2:
            # local_control has on/off parameter
            on_off = str(token_list[2]).lower()
            return MIDICommand(type=midi_type, channel=channel, data1=127 if on_off == "on" else 0)
        if cmd_type == "CHAN_MONO_MODE" and len(token_list) > 2:
            # mono_mode has channel count parameter
            return MIDICommand(type=midi_type, channel=channel, data1=int(token_list[2]))
        # Simple channel reset command
        return MIDICommand(type=midi_type, channel=channel)

    def system_common(self, *args):
        """Handle system common messages"""
        # args is a list of tokens
        token_list = args[0] if isinstance(args[0], list) else args
        cmd_token = token_list[0]
        cmd_type = cmd_token.type if hasattr(cmd_token, "type") else str(cmd_token)

        # Map terminal name to MIDI command type
        type_map = {
            "SYS_MTC_QUARTER_FRAME": "mtc_quarter_frame",
            "SYS_SONG_POSITION": "song_position",
            "SYS_SONG_SELECT": "song_select",
            "SYS_TUNE_REQUEST": "tune_request",
        }

        midi_type = type_map.get(cmd_type, "system_common")

        # tune_request has no parameters
        if cmd_type == "SYS_TUNE_REQUEST":
            return MIDICommand(type=midi_type)

        # Other commands have an integer parameter
        if len(token_list) > 1:
            value = int(token_list[1])
            return MIDICommand(type=midi_type, data1=value)

        # Fallback
        return MIDICommand(type=midi_type)

    def system_realtime(self, *args):
        """Handle system real-time messages"""
        # args is a list of tokens
        # All system realtime commands have no parameters
        token_list = args[0] if isinstance(args[0], list) else args
        cmd_token = token_list[0]
        cmd_type = cmd_token.type if hasattr(cmd_token, "type") else str(cmd_token)

        # Map terminal name to MIDI command type
        type_map = {
            "SYS_CLOCK_START": "clock_start",
            "SYS_CLOCK_STOP": "clock_stop",
            "SYS_CLOCK_CONTINUE": "clock_continue",
            "SYS_CLOCK_TICK": "timing_clock",
            "SYS_ACTIVE_SENSING": "active_sensing",
            "SYS_SYSTEM_RESET": "system_reset",
        }

        midi_type = type_map.get(cmd_type, "system_realtime")
        return MIDICommand(type=midi_type)

    # Alias System
    def simple_alias(self, *args):
        """Handle all simple_alias variants"""
        name = str(args[0])

        # Extract template string - might be a Tree or Token
        template_arg = args[1]
        if hasattr(template_arg, "children") and len(template_arg.children) > 0:
            # It's a Tree, extract the token value
            template = str(template_arg.children[0])
        else:
            template = str(template_arg)

        description = None
        computed = {}

        # Parse remaining arguments
        for arg in args[2:]:
            if isinstance(arg, str) and (arg.startswith(('"', "'"))):
                description = arg.strip("\"'")
            elif isinstance(arg, dict):
                computed = arg

        params = self._extract_params(template)
        return AliasDefinition(
            name=name,
            parameters=params,
            commands=[template],  # Store as string, not Tree
            description=description,
            computed_values=computed,
            is_macro=False,
        )

    def command_template(self, *args):
        """Handle command template - capture as string for later parsing with params"""
        # Lark passes the regex match as multiple args (one per character)
        # Rejoin them to get the full command string
        # The args tuple contains the matched text from the regex: /[^\n]+/
        return "".join(str(arg) for arg in args).strip()

    def alias_body_content(self, *items):
        """Handle alias_body_content - unwrap the single child.

        This rule exists to allow mixing commands and conditionals in alias bodies.
        Just pass through the single child (either alias_body_item or conditional_stmt).
        """
        return items[0]

    def alias_body_item(self, *items):
        """Handle alias_body_item - timing, define, sweep, or command_template.

        Returns:
            Timing, DefineStatement, SweepStatement, or command template string
        """
        # Lark passes transformed children as args
        # Should be exactly one item
        item = items[0]

        # If it's a tuple from define_stmt, convert to DefineStatement
        if isinstance(item, tuple) and len(item) >= 2 and item[0] == "define":
            from .ast_nodes import DefineStatement

            return DefineStatement(name=item[1], value=item[2] if len(item) > 2 else None)

        # If it's a dict from sweep_stmt, convert to SweepStatement
        if isinstance(item, dict) and item.get("type") == "sweep":
            from .ast_nodes import SweepStatement

            return SweepStatement(
                start_time=item["start_time"],
                end_time=item["end_time"],
                interval=item["interval"],
                commands=item["commands"],
                source_line=item.get("source_line", 0),
            )

        # Otherwise it's Timing or command template string
        return item

    def macro_alias(self, *args):
        """Handle macro_alias - description is now required.

        Structure changed in Stage 7:
        args[0]: name
        args[1]: params
        args[2]: description
        args[3+]: computed_values (dict objects) and alias_body (list or conditional dict)
        """
        from .ast_nodes import ConditionalBranch

        name = str(args[0])
        params = args[1]
        description = args[2].strip("\"'") if args[2] else None

        # Separate computed values from the body
        computed_values = {}
        alias_body = None

        for item in args[3:]:
            if (
                isinstance(item, dict)
                and len(item) == 1
                and not any(k in item for k in ["type", "branches"])
            ):
                # It's a computed value (single key-value pair from computed_value())
                computed_values.update(item)
            elif isinstance(item, dict) and item.get("type") == "alias_conditional":
                # It's a conditional structure (Stage 7)
                alias_body = item
            elif isinstance(item, list):
                # It's a list of commands (non-conditional)
                alias_body = item
            elif isinstance(item, str):
                # Single command string
                if alias_body is None:
                    alias_body = []
                if isinstance(alias_body, list):
                    alias_body.append(item)

        # Build the AliasDefinition
        if (
            alias_body is not None
            and isinstance(alias_body, dict)
            and alias_body.get("type") == "alias_conditional"
        ):
            # Conditional alias (Stage 7)
            branches = []
            for branch_dict in alias_body["branches"]:
                branches.append(
                    ConditionalBranch(
                        condition=branch_dict.get("condition"),
                        commands=branch_dict["commands"],
                        branch_type=branch_dict["type"],
                    )
                )

            return AliasDefinition(
                name=name,
                parameters=self._parse_params(params),
                commands=[],  # Empty for conditional aliases
                description=description,
                computed_values=computed_values,
                conditional_branches=branches,
                is_macro=True,
                has_conditionals=True,
            )
        # Non-conditional alias
        commands = alias_body if isinstance(alias_body, list) else []
        return AliasDefinition(
            name=name,
            parameters=self._parse_params(params),
            commands=commands,
            description=description,
            computed_values=computed_values,
            is_macro=True,
            has_conditionals=False,
        )

    def computed_value(self, name, expr):
        """Parse computed value from braces"""
        return {str(name): expr}

    # Stage 7: Conditional transformation methods
    def alias_body(self, *items):
        """Handle alias body - either commands or conditionals.

        Returns either a list of command strings or a conditional dict.
        """
        # If there's only one item and it's a dict with 'type'='alias_conditional', return it
        if (
            len(items) == 1
            and isinstance(items[0], dict)
            and items[0].get("type") == "alias_conditional"
        ):
            return items[0]
        # Otherwise, return list of commands
        return list(items)

    def alias_conditional_stmt(self, if_clause, *other_clauses):
        """Handle conditional statement within alias (Stage 7).

        Args:
            if_clause: The @if clause (dict)
            other_clauses: Zero or more @elif or @else clauses

        Returns:
            Dict with type='alias_conditional' and list of branches
        """
        branches = [if_clause]
        for clause in other_clauses:
            branches.append(clause)

        return {"type": "alias_conditional", "branches": branches}

    def alias_if_clause(self, condition, *commands):
        """Handle @if clause in alias conditional."""
        return {"type": "if", "condition": condition, "commands": list(commands)}

    def alias_elif_clause(self, condition, *commands):
        """Handle @elif clause in alias conditional."""
        return {"type": "elif", "condition": condition, "commands": list(commands)}

    def alias_else_clause(self, *commands):
        """Handle @else clause in alias conditional."""
        return {
            "type": "else",
            "condition": None,  # No condition for else
            "commands": list(commands),
        }

    def alias_condition(self, *args):
        """Parse condition expression for alias conditional.

        Args can be:
        - param_ref, operator, value
        - IDENTIFIER, operator, value

        Returns:
            Dict with 'left', 'operator', 'right' keys
        """
        if len(args) != 3:
            msg = f"Expected 3 args for alias_condition, got {len(args)}: {args}"
            raise ValueError(msg)

        left_arg = args[0]
        operator_arg = args[1]
        right_arg = args[2]

        # Extract left value (parameter name)
        if hasattr(left_arg, "data") and left_arg.data == "param_ref":
            # It's a {param} reference - extract the parameter name
            left = self._extract_param_name(left_arg)
        else:
            # It's an IDENTIFIER
            left = str(left_arg)

        # Extract operator - should be a Token now (COMPARE_OP terminal)
        operator = str(operator_arg)

        # Extract right value
        right = self._extract_condition_value(right_arg)

        return {"left": left, "operator": operator, "right": right}

    def alias_cond_value(self, value):
        """Extract value from alias_cond_value node."""
        return self._extract_condition_value(value)

    def _extract_param_name(self, param_ref_tree):
        """Extract parameter name from param_ref tree."""
        # param_ref contains param_spec which contains IDENTIFIER
        for child in param_ref_tree.children:
            if hasattr(child, "data") and child.data == "param_spec":
                # First child of param_spec is the IDENTIFIER
                return str(child.children[0])
            if isinstance(child, str):
                return str(child)
        # Fallback
        return str(param_ref_tree.children[0])

    def _extract_condition_value(self, value_node):
        """Extract value from condition value node (string, int, param, etc)."""
        if hasattr(value_node, "data"):
            # It's a tree node
            if value_node.data == "param_ref":
                return self._extract_param_name(value_node)
            if value_node.data == "STRING":
                # STRING node - extract and strip quotes
                return str(value_node.children[0]).strip("\"'")
            if value_node.data in ("INT", "FLOAT"):
                # Numeric value
                return value_node.children[0]
            # Other nodes - try first child
            return value_node.children[0] if value_node.children else str(value_node)
        if hasattr(value_node, "type"):
            # It's a Token
            if value_node.type == "STRING":
                return str(value_node).strip("\"'")
            if value_node.type in ("INT", "FLOAT"):
                return int(value_node) if value_node.type == "INT" else float(value_node)
            return str(value_node)
        # Plain value
        return value_node

    def alias_call(self, name, *args):
        """Parse alias invocation"""
        # Flatten args if they come wrapped in alias_args tree
        flat_args = []
        for arg in args:
            if hasattr(arg, "children"):
                # It's a Tree node (alias_args), extract children
                for child in arg.children:
                    if hasattr(child, "children") and len(child.children) == 1:
                        # alias_arg wrapper
                        flat_args.append(child.children[0])
                    else:
                        flat_args.append(child)
            else:
                flat_args.append(arg)

        return MIDICommand(type="alias_call", params={"alias_name": str(name), "args": flat_args})

    def alias_def(self, alias):
        """Unwrap alias definition (simple_alias or macro_alias)"""
        return alias

    # Advanced Features
    def track_def(self, *args):
        """Handle both track definition formats"""
        if len(args) == 1:
            # Just identifier or markdown style string
            return Track(name=str(args[0]))
        if len(args) == 2:
            # identifier + channel number
            # (keywords "channel" and "=" are consumed by grammar)
            return Track(name=str(args[0]), channel=int(args[1]))
        return Track(name=str(args[0]))

    def loop_body(self, *items):
        """Handle loop_body - returns list of loop items.

        Grammar: loop_body: (loop_item _NL*)*

        Returns:
            List of loop items (commands, timings, or nested loops)
        """
        # Filter out None values (from optional items)
        return [item for item in items if item is not None]

    def loop_item(self, item):
        """Handle loop_item - returns the single item.

        Grammar: loop_item: timing | command | loop_stmt

        Returns:
            Single item (Timing, MIDICommand, or loop dict)
        """
        return item

    def loop_stmt(self, *args):
        """
        Handle all loop_stmt variants.

        Phase 3: Returns a loop dictionary that will be expanded by LoopExpander
        in the EventGenerator.

        Grammar variants:
        - @loop INT times at timing every duration ... @end
        - @loop INT times every duration ... @end
        - @loop INT times at timing ... @end
        - @loop INT times ... @end
        """
        count = int(args[0])
        timing = None
        interval = None
        statements = []

        i = 1
        # Check for timing
        if i < len(args) and isinstance(args[i], Timing):
            timing = args[i]
            i += 1

        # Check for interval (duration) - can be string or Duration object
        if i < len(args) and not isinstance(args[i], dict | MIDICommand | Track | list):
            interval = args[i]
            i += 1

        # Rest are statements (now properly transformed via loop_body)
        # If we have a list (from loop_body), use it; otherwise collect remaining args
        statements = args[i] if i < len(args) and isinstance(args[i], list) else list(args[i:])

        return {
            "type": "loop",
            "count": count,
            "start_time": timing,  # Can be None
            "interval": interval,  # Can be None - default to 1 beat
            "statements": statements,
            "source_line": self.line_number,
        }

    def sweep_stmt(self, start_time, end_time, interval, *commands):
        """
        Handle sweep statement.

        Phase 3: Returns a sweep dictionary that will be expanded by SweepExpander
        in the EventGenerator.

        Grammar:
        - @sweep from timing to timing every duration ... @end

        Note: The actual sweep expansion (ramp type, CC controller, etc.) will be
        extracted from the commands during EventGenerator processing.
        """
        return {
            "type": "sweep",
            "start_time": start_time,
            "end_time": end_time,
            "interval": interval,
            "commands": list(commands),
            "source_line": self.line_number,
        }

    def conditional_stmt(self, if_clause, *other_clauses):
        """Transform @if/@elif/@else conditional statement.

        Args:
            if_clause: Tuple with condition and commands for @if branch
            *other_clauses: Variable number of @elif or @else clauses

        Returns:
            Dictionary representing conditional statement with all branches
        """
        return {
            "type": "conditional",
            "if": if_clause,
            "elif": [c for c in other_clauses if c[0] == "elif"],
            "else": next((c for c in other_clauses if c[0] == "else"), None),
        }

    # Expressions
    def add(self, left, right):
        """Transform addition expression (left + right).

        Args:
            left: Left operand (number or expression)
            right: Right operand (number or expression)

        Returns:
            Tuple ("add", left, right) representing addition operation
        """
        return ("add", left, right)

    def sub(self, left, right):
        """Transform subtraction expression (left - right).

        Args:
            left: Left operand (number or expression)
            right: Right operand (number or expression)

        Returns:
            Tuple ("sub", left, right) representing subtraction operation
        """
        return ("sub", left, right)

    def mul(self, left, right):
        """Transform multiplication expression (left * right).

        Args:
            left: Left operand (number or expression)
            right: Right operand (number or expression)

        Returns:
            Tuple ("mul", left, right) representing multiplication operation
        """
        return ("mul", left, right)

    def div(self, left, right):
        """Transform division expression (left / right).

        Args:
            left: Left operand (number or expression)
            right: Right operand (number or expression)

        Returns:
            Tuple ("div", left, right) representing division operation
        """
        return ("div", left, right)

    def mod(self, left, right):
        """Transform modulo expression (left % right).

        Args:
            left: Left operand (number or expression)
            right: Right operand (number or expression)

        Returns:
            Tuple ("mod", left, right) representing modulo operation
        """
        return ("mod", left, right)

    def variable_ref(self, name):
        """Resolve variable reference ${VAR} to its value."""
        var_name = str(name)
        try:
            return self.symbol_table.resolve(var_name)
        except ValueError:
            # If variable not found, return tuple for later resolution
            # This handles forward references where variable is defined after use
            return ("var", var_name)

    def param(self, value):
        """Handle parameter - can be INT or variable_ref."""
        # Value is already transformed by child rule (INT or variable_ref)
        return value

    def tempo_value(self, value):
        """Handle tempo value - can be NUMBER or param."""
        # Value is already transformed by child rule
        return value

    def function_call(self, func_name, *args):
        """Transform function call in expression."""
        return ("func_call", str(func_name), list(args))

    def number(self, n):
        """Transform NUMBER token - preserve int vs float.

        The NUMBER terminal has already determined whether this should be
        an int or float. Just return the value as-is.

        Args:
            n: Numeric value (int or float from NUMBER terminal)

        Returns:
            Original value with type preserved
        """
        return n

    def integer(self, n):
        """Transform INT token to integer.

        Args:
            n: Integer token

        Returns:
            Integer value
        """
        return int(n)

    def param_ref_expr(self, param_ref):
        """Transform param_ref in expression context.

        Returns a tuple marking this as a parameter reference.
        """
        # param_ref is already transformed (dict with 'name', 'type', etc.)
        return ("param_ref", param_ref)

    def percent(self, value):
        """Transform percent value (e.g., 50%) to internal representation.

        Args:
            value: Percentage value (0-100)

        Returns:
            Tuple ("percent", value) for later conversion to 0-127 MIDI range
        """
        return ("percent", int(value))

    def ramp_expr(self, start, end, ramp_type="linear"):
        """Transform ramp/sweep expression (e.g., ramp(0, 127, "linear")).

        Args:
            start: Starting value for ramp
            end: Ending value for ramp
            ramp_type: Type of ramp curve ("linear", "exponential", etc.)

        Returns:
            Dictionary with ramp parameters for sweep expansion
        """
        return {
            "type": "ramp",
            "start": int(start),
            "end": int(end),
            "ramp_type": str(ramp_type) if ramp_type else "linear",
        }

    def random_expr(self, *args):
        """Transform random() expression to RandomExpression AST node.

        Args:
            *args: Variable arguments [min_val, max_val] or [min_val, max_val, seed]

        Returns:
            RandomExpression AST node
        """
        from midi_markdown.parser.ast_nodes import RandomExpression

        min_val = args[0]
        max_val = args[1]
        seed = int(args[2]) if len(args) > 2 else None

        return RandomExpression(min_value=min_val, max_value=max_val, seed=seed)

    def curve_expr(self, start, end, curve_type_arg):
        """Transform curve() expression to CurveExpression AST node.

        Grammar: curve "(" number "," number "," curve_type ")"
        curve_type: "ease-in" | "ease-out" | "ease-in-out" | "linear"
                  | ("bezier" "(" number "," number "," number "," number ")")

        Args:
            start: Start value
            end: End value
            curve_type_arg: Either a Token/Tree with single Token child (preset curves)
                           or a Tree with 4 number children (bezier)

        Returns:
            CurveExpression AST node
        """
        from lark import Token, Tree

        from midi_markdown.parser.ast_nodes import CurveExpression

        start_value = float(start)
        end_value = float(end)

        # Determine curve type and control points
        # curve_type_arg can be a Tree (for bezier) or Token (for preset curves)
        if isinstance(curve_type_arg, Tree):
            # Check if it has 4 children (bezier with control points)
            if len(curve_type_arg.children) == 4:
                # It's a bezier curve with 4 control points
                curve_type = "bezier"
                control_points = (
                    float(curve_type_arg.children[0]),
                    float(curve_type_arg.children[1]),
                    float(curve_type_arg.children[2]),
                    float(curve_type_arg.children[3]),
                )
            elif len(curve_type_arg.children) == 1:
                # It's a Tree with a single Token child (CURVE_TYPE_NAME)
                curve_type = str(curve_type_arg.children[0])
                control_points = None
            elif len(curve_type_arg.children) == 0:
                # Empty tree - shouldn't happen with updated grammar
                msg = f"Unexpected empty curve_type tree: {curve_type_arg}"
                raise ValueError(msg)
            else:
                # Shouldn't happen, but handle gracefully
                msg = f"Unexpected curve_type structure: {curve_type_arg}"
                raise ValueError(msg)
        elif isinstance(curve_type_arg, Token):
            # Direct Token (CURVE_TYPE_NAME from updated grammar)
            curve_type = str(curve_type_arg)
            control_points = None
        else:
            # Unknown type
            msg = f"Unexpected curve_type type: {type(curve_type_arg)}"
            raise ValueError(msg)

        return CurveExpression(
            start_value=start_value,
            end_value=end_value,
            curve_type=curve_type,
            control_points=control_points,
        )

    def wave_expr(self, wave_type, base_value, *params):
        """Transform wave() expression to WaveExpression AST node.

        Grammar: wave "(" wave_type "," number ("," wave_params)? ")"
        wave_params: "freq" "=" number ("," "phase" "=" number)? ("," "depth" "=" number)?

        Args:
            wave_type: Token containing wave type ('sine', 'triangle', 'square', 'sawtooth')
            base_value: Base/center value
            *params: Optional wave_params dict (if wave_params transformer is called)

        Returns:
            WaveExpression AST node
        """
        from lark import Token

        from midi_markdown.parser.ast_nodes import WaveExpression

        # Extract wave type from Token or Tree
        if isinstance(wave_type, Token):
            wave_type_str = str(wave_type)
        elif hasattr(wave_type, "children") and len(wave_type.children) == 1:
            wave_type_str = str(wave_type.children[0])
        else:
            wave_type_str = str(wave_type)

        # Extract wave parameters from dict (returned by wave_params transformer)
        if params and isinstance(params[0], dict):
            wave_params_dict = params[0]
            frequency = wave_params_dict.get("freq")
            phase = wave_params_dict.get("phase")
            depth = wave_params_dict.get("depth")
        else:
            frequency = None
            phase = None
            depth = None

        return WaveExpression(
            wave_type=wave_type_str,
            base_value=float(base_value),
            frequency=frequency,
            phase=phase,
            depth=depth,
        )

    def wave_params(self, *wave_param_list):
        """Transform wave parameters.

        Grammar: wave_param ("," wave_param)*
        wave_param: "freq" "=" number | "phase" "=" number | "depth" "=" number

        Returns dict with wave parameters.
        """
        result = {}
        for param_dict in wave_param_list:
            if isinstance(param_dict, dict):
                result.update(param_dict)
        return result

    def wave_freq(self, value):
        """Transform freq= wave parameter"""
        return {"freq": float(value)}

    def wave_phase(self, value):
        """Transform phase= wave parameter"""
        return {"phase": float(value)}

    def wave_depth(self, value):
        """Transform depth= wave parameter"""
        return {"depth": float(value)}

    def envelope_expr(self, envelope_type, envelope_params):
        """Transform envelope() expression to EnvelopeExpression AST node.

        Grammar: envelope "(" envelope_type "," envelope_params ")"
        envelope_params: adsr_params | ar_params | ad_params

        Args:
            envelope_type: Token containing envelope type ('adsr', 'ar', 'ad')
            envelope_params: Dict with parsed envelope parameters from adsr_params/ar_params/ad_params

        Returns:
            EnvelopeExpression AST node
        """
        from lark import Token

        from midi_markdown.parser.ast_nodes import EnvelopeExpression

        # Extract envelope type from Token or Tree
        if isinstance(envelope_type, Token):
            envelope_type_str = str(envelope_type)
        elif hasattr(envelope_type, "children") and len(envelope_type.children) == 1:
            envelope_type_str = str(envelope_type.children[0])
        else:
            envelope_type_str = str(envelope_type)

        # envelope_params is now a dict returned by adsr_params/ar_params/ad_params transformers
        if isinstance(envelope_params, dict):
            attack = envelope_params.get("attack")
            decay = envelope_params.get("decay")
            sustain = envelope_params.get("sustain")
            release = envelope_params.get("release")
            curve = envelope_params.get("curve", "linear")
        else:
            # Fallback for unexpected format
            attack = decay = sustain = release = None
            curve = "linear"

        return EnvelopeExpression(
            envelope_type=envelope_type_str,
            attack=attack,
            decay=decay,
            sustain=sustain,
            release=release,
            curve=curve,
        )

    def adsr_params(self, attack, decay, sustain, release, *curve_args):
        """Transform ADSR envelope parameters.

        Grammar: "attack" "=" number "," "decay" "=" number "," "sustain" "=" number "," "release" "=" number ("," envelope_curve)?

        Returns dict with envelope parameters.
        """
        result = {
            "attack": float(attack),
            "decay": float(decay),
            "sustain": float(sustain),
            "release": float(release),
        }
        if curve_args:
            result["curve"] = str(curve_args[0])
        return result

    def ar_params(self, attack, release, *curve_args):
        """Transform AR envelope parameters.

        Grammar: "attack" "=" number "," "release" "=" number ("," envelope_curve)?

        Returns dict with envelope parameters.
        """
        result = {
            "attack": float(attack),
            "release": float(release),
        }
        if curve_args:
            result["curve"] = str(curve_args[0])
        return result

    def ad_params(self, attack, decay, *curve_args):
        """Transform AD envelope parameters.

        Grammar: "attack" "=" number "," "decay" "=" number ("," envelope_curve)?

        Returns dict with envelope parameters.
        """
        result = {
            "attack": float(attack),
            "decay": float(decay),
        }
        if curve_args:
            result["curve"] = str(curve_args[0])
        return result

    def envelope_curve(self, curve_type):
        """Transform envelope_curve parameter.

        Grammar: "curve" "=" ("linear" | "exponential")

        Returns the curve type string.
        """
        return str(curve_type)

    # Helper Methods
    def _resolve_define_value(self, value):
        """Resolve a value for @define - handles literals, strings, and expressions.

        Phase 2: Now uses SafeComputationEngine for full expression evaluation.

        Args:
            value: Can be a literal (int/float/string), Lark Tree, or tuple

        Returns:
            Resolved value (int, float, or string)

        Raises:
            ValueError: If expression evaluation fails
        """
        # If it's a string literal, strip quotes
        if isinstance(value, str):
            return value.strip("\"'")

        # If it's a simple number, return it
        if isinstance(value, int | float):
            return value

        # Handle Lark Tree objects (expressions from grammar)
        if hasattr(value, "data"):
            from lark import Tree

            if isinstance(value, Tree):
                # Check if it's an expression tree that needs evaluation
                if self._is_expression_tree(value):
                    return self._evaluate_expression_tree(value)
                # Simple value tree (like a plain number or string)
                return self._eval_tree(value)

        # If it's an expression tuple (from Phase 1)
        if isinstance(value, tuple):
            # Variable reference
            if value[0] == "var":
                return self.symbol_table.resolve(value[1])
            # Expression tuple - evaluate it
            return self._simple_eval(value)

        # Default: return as-is
        return value

    def _simple_eval(self, expr_tree):
        """Simple expression evaluator for Phase 1."""
        # Handle Lark Tree objects
        if hasattr(expr_tree, "data"):
            from lark import Tree

            if isinstance(expr_tree, Tree):
                return self._eval_tree(expr_tree)

        if isinstance(expr_tree, int | float):
            return expr_tree

        if not isinstance(expr_tree, tuple) or len(expr_tree) == 0:
            return expr_tree

        op = expr_tree[0]

        # Variable reference
        if op == "var":
            return self.symbol_table.resolve(expr_tree[1])

        # Binary operations
        if op == "add" and len(expr_tree) == 3:
            left = self._simple_eval(expr_tree[1])
            right = self._simple_eval(expr_tree[2])
            return left + right
        if op == "sub" and len(expr_tree) == 3:
            left = self._simple_eval(expr_tree[1])
            right = self._simple_eval(expr_tree[2])
            return left - right
        if op == "mul" and len(expr_tree) == 3:
            left = self._simple_eval(expr_tree[1])
            right = self._simple_eval(expr_tree[2])
            return left * right
        if op == "div" and len(expr_tree) == 3:
            left = self._simple_eval(expr_tree[1])
            right = self._simple_eval(expr_tree[2])
            return left / right
        if op == "mod" and len(expr_tree) == 3:
            left = self._simple_eval(expr_tree[1])
            right = self._simple_eval(expr_tree[2])
            return left % right

        # Unrecognized - return as is
        return expr_tree

    def _resolve_param(self, value):
        """Resolve a parameter value which may be an int, variable reference tuple, or Tree object.

        Phase 2: Enhanced to use SafeComputationEngine for expression evaluation.

        Args:
            value: Can be int, ('var', name) tuple, or Lark Tree object

        Returns:
            Resolved value (int or tuple for forward references)

        Note:
            Forward references (undefined variables) are preserved as tuples
            to be resolved later during MIDI generation.
        """
        # Handle Lark Tree objects
        if hasattr(value, "data"):
            # It's a Lark Tree - could be from expression
            from lark import Tree

            if isinstance(value, Tree):
                # Check if it's an expression that needs evaluation
                if self._is_expression_tree(value):
                    try:
                        return self._evaluate_expression_tree(value)
                    except ValueError:
                        # If evaluation fails (e.g., undefined variable), preserve as tuple
                        # This allows forward references
                        return value
                else:
                    # Simple value tree
                    try:
                        return self._eval_tree(value)
                    except ValueError:
                        return value

        # If it's already an int, return it
        if isinstance(value, int):
            return value

        # If it's a tuple, it could be a variable reference or expression
        if isinstance(value, tuple):
            # Preserve tuples as-is for now - they will be resolved later
            # This includes both ('var', name) and expression tuples
            return value

        # Try to convert to int
        try:
            return int(value)
        except (ValueError, TypeError):
            # If conversion fails, return as-is
            return value

    def _eval_tree(self, tree):
        """Evaluate a Lark Tree object to a numeric value."""
        from lark import Token, Tree

        if isinstance(tree, Token):
            return int(tree)

        if not isinstance(tree, Tree):
            return tree

        # Handle expression trees
        if tree.data in ("add", "sub", "mul", "div", "mod"):
            left = self._eval_tree(tree.children[0])
            right = self._eval_tree(tree.children[1])

            if tree.data == "add":
                return left + right
            if tree.data == "sub":
                return left - right
            if tree.data == "mul":
                return left * right
            if tree.data == "div":
                return left / right
            if tree.data == "mod":
                return left % right

        # Handle variable references
        if tree.data == "variable_ref":
            # Extract variable name and resolve
            var_name = str(tree.children[0])
            return self.symbol_table.resolve(var_name)

        # Handle numeric values
        if tree.data in ("integer", "number"):
            return self._eval_tree(tree.children[0])

        # If we can't handle it, try the first child
        if tree.children:
            return self._eval_tree(tree.children[0])

        return 0

    def _is_expression_tree(self, tree) -> bool:
        """Check if a Lark Tree represents an expression that needs computation.

        Args:
            tree: Lark Tree object

        Returns:
            True if tree contains operators that need evaluation
        """
        from lark import Tree

        if not isinstance(tree, Tree):
            return False

        # Expression operators that require SafeComputationEngine
        expression_types = {
            "add",
            "sub",
            "mul",
            "div",
            "mod",
            "pow",
            "floordiv",
            "neg",
            "pos",  # Unary operators
            "var_ref",  # Variable references might be in expressions (aliased from variable_ref in grammar)
        }

        # Check if this tree or any child contains expression operators
        if tree.data in expression_types:
            return True

        # Recursively check children
        for child in tree.children:
            if isinstance(child, Tree) and self._is_expression_tree(child):
                return True

        return False

    def _evaluate_expression_tree(self, tree):
        """Evaluate a Lark expression tree using SafeComputationEngine.

        Phase 2: Full expression evaluation with security and proper error handling.

        Args:
            tree: Lark Tree object representing an expression

        Returns:
            Evaluated result (int or float)

        Raises:
            ValueError: If expression evaluation fails
        """
        try:
            # Convert Lark tree to Python expression string
            python_expr = self.computation_engine.lark_tree_to_python(tree)

            # Prepare input parameters: all defined variables + constants
            input_params = {}

            # Add all defined variables
            for name, var in self.symbol_table.symbols.items():
                input_params[name] = var.value

            # Add built-in constants
            input_params.update(self.symbol_table.CONSTANTS)

            # Evaluate the expression
            return self.computation_engine.evaluate_expression(python_expr, input_params)

            # Return the result (SafeComputationEngine handles int/float conversion)

        except ComputationError as e:
            # Enhance error message with context
            msg = f"Expression evaluation error: {e}"
            raise ValueError(msg) from e
        except Exception as e:
            # Catch any other errors and provide helpful message
            msg = f"Failed to evaluate expression: {e}"
            raise ValueError(msg) from e

    def _parse_absolute_time(self, time_str: str) -> float:
        """Parse mm:ss.mmm format to seconds"""
        parts = time_str.strip("[]").split(":")
        minutes = int(parts[0])
        seconds = float(parts[1])
        return minutes * 60 + seconds

    def _parse_channel_note(self, channel_note) -> tuple:
        """Parse channel.note format or tuple from channel_note() transformer.

        Args:
            channel_note: Either a tuple (channel, note) from new transformer,
                         or a string "channel.note" for backward compatibility

        Returns:
            Tuple of (channel: int, note: int|str|tuple|RandomExpression)
        """
        from midi_markdown.parser.ast_nodes import RandomExpression

        # New format: tuple from channel_note() transformer
        if isinstance(channel_note, tuple):
            channel, note_val = channel_note
            # Note is already processed by note_value() transformer
            # It can be: int, str (note name), tuple (variable), or RandomExpression
            if isinstance(note_val, RandomExpression):
                return channel, note_val  # Preserve RandomExpression
            if isinstance(note_val, tuple):
                return channel, note_val  # Preserve variable reference
            if isinstance(note_val, int):
                return channel, note_val  # Already a MIDI number
            if isinstance(note_val, str):
                # Could be note name or numeric string
                if note_val.isdigit():
                    return channel, int(note_val)
                # Try to parse as note name
                try:
                    return channel, self._note_to_midi(note_val)
                except (ValueError, KeyError):
                    return channel, note_val  # Literal string
            else:
                return channel, note_val

        # Old format: string "channel.note" (for backward compatibility)
        parts = str(channel_note).split(".")
        channel = int(parts[0])

        note_str = parts[1]
        if "${" in note_str:
            var_name = note_str.strip()[2:-1]
            note = ("var", var_name)
        elif note_str.isdigit():
            note = int(note_str)
        else:
            try:
                note = self._note_to_midi(note_str)
            except (ValueError, KeyError):
                note = note_str
        return channel, note

    def _parse_note_value(self, note_value):
        """Parse note_value - can be NOTE_NAME, INT, or variable_ref.

        Args:
            note_value: Can be:
                - str: NOTE_NAME token (e.g., "C4", "D#5")
                - int: MIDI note number
                - tuple: variable reference ("var", "VAR_NAME")

        Returns:
            int or tuple: MIDI note number or variable reference tuple
        """
        if isinstance(note_value, tuple):
            # Variable reference
            return note_value
        if isinstance(note_value, int):
            # Already a MIDI note number
            return note_value
        if isinstance(note_value, str):
            # Could be NOTE_NAME
            if note_value.isdigit():
                return int(note_value)
            # Try to parse as note name (C4, D#5, etc.)
            try:
                return self._note_to_midi(note_value)
            except (ValueError, KeyError):
                # If it fails, return as-is (might be resolved later)
                return note_value
        else:
            # Unknown type, return as-is
            return note_value

    def _note_to_midi(self, note_name: str) -> int:
        """Convert note name (e.g., 'C4') to MIDI number.

        This method now delegates to the shared utility function.
        """
        return note_to_midi(note_name)

    def _parse_cc_value(self, value) -> int | dict:
        """Parse CC value (can be int, percent, ramp, etc.)"""
        # Handle Token objects and strings
        if isinstance(value, int | float):
            return int(value)
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                pass
        if isinstance(value, tuple) and value[0] == "percent":
            # Use shared utility for percent conversion
            return percent_to_midi(value[1])
        # Handle all modulation expressions (AST nodes or old dict format)
        from midi_markdown.parser.ast_nodes import (
            CurveExpression,
            EnvelopeExpression,
            RandomExpression,
            WaveExpression,
        )

        # Pass through modulation expression objects unchanged
        if isinstance(
            value, RandomExpression | CurveExpression | WaveExpression | EnvelopeExpression
        ):
            return value
        if isinstance(value, dict) and value.get("type") in ("ramp", "random"):
            return value
        # Try converting to string then int as fallback
        try:
            return int(str(value))
        except (ValueError, TypeError):
            # For unknown types, return a placeholder
            return 0

    def _parse_pitch_bend(self, value):
        """Parse pitch bend value.

        Pitch bend values can be:
        - Absolute: -8192 to +8191 (full range)
        - String offsets: "+2000", "-2000" (offset from center 8192)
        - Integer offsets: 2000, -2000 (offset from center 8192)
        - Center: 0 (maps to 8192)
        - RandomExpression: Passed through for expansion
        - Modulation expressions (curve, wave, envelope): Passed through for expansion

        Returns:
            int or Expression: Pitch bend value (validation happens later)
        """
        from midi_markdown.parser.ast_nodes import (
            CurveExpression,
            EnvelopeExpression,
            RandomExpression,
            WaveExpression,
        )

        # Check for modulation expressions - pass through for later expansion
        if isinstance(
            value, RandomExpression | CurveExpression | WaveExpression | EnvelopeExpression
        ):
            return value

        if isinstance(value, str) and (value.startswith(("+", "-"))):
            # String with explicit sign: treat as offset from center
            return int(value)

        # Convert to int and return as-is (let validator check range)
        return int(value)

    def _extract_params(self, template) -> list[dict[str, Any]]:
        """
        Extract parameter definitions from alias template string.

        Parses {param} placeholders with specifications like:
        - {name} - basic parameter
        - {name:0-127} - parameter with range
        - {name:note} - typed parameter
        - {name=64} - parameter with default
        - {name=opt1:0,opt2:1} - enum parameter
        """
        import re

        params = []
        seen_names = set()

        # Match {param_spec} patterns
        for match in re.finditer(r"\{([^}]+)\}", str(template)):
            param_spec = match.group(1)
            param_dict = self._parse_single_param_spec(param_spec)

            # Only add each parameter once (may appear multiple times in template)
            if param_dict["name"] not in seen_names:
                params.append(param_dict)
                seen_names.add(param_dict["name"])

        return params

    def _parse_single_param_spec(self, spec: str) -> dict[str, Any]:
        """
        Parse a single parameter specification string.

        Format: name[:type|range][=default|enum_options]
        Examples:
          - velocity
          - velocity:0-127
          - velocity:velocity
          - velocity=100
          - mode=series:0,parallel:1
        """

        param = {
            "name": "",
            "type": "generic",
            "min": 0,
            "max": 127,
            "default": None,
            "enum_values": None,
        }

        # Split on = to separate name/type from default/enum
        if "=" in spec:
            name_part, value_part = spec.split("=", 1)

            # Check if value_part contains enums (has : and ,)
            if ":" in value_part and "," in value_part:
                # Parse enum: opt1:val1,opt2:val2
                param["enum_values"] = {}
                for enum_option in value_part.split(","):
                    if ":" in enum_option:
                        opt_name, opt_val = enum_option.split(":", 1)
                        param["enum_values"][opt_name.strip()] = int(opt_val.strip())
                param["type"] = "enum"
            else:
                # Simple default value
                param["default"] = value_part.strip()
                # Try to convert to int if possible
                try:
                    param["default"] = int(param["default"])
                except ValueError:
                    pass  # Keep as string
        else:
            name_part = spec

        # Parse name and optional type/range
        if ":" in name_part:
            name, type_spec = name_part.split(":", 1)
            param["name"] = name.strip()

            # Check if type_spec is a range (INT-INT)
            # Use regex to properly handle negative numbers
            import re

            range_match = re.match(r"^(-?\d+)\s*-\s*(-?\d+)$", type_spec.strip())
            if range_match:
                # Parse range: 0-127, -24-24, etc.
                min_val, max_val = range_match.groups()
                param["type"] = "range"
                param["min"] = int(min_val)
                param["max"] = int(max_val)
            else:
                # Named type: note, channel, bool, percent, velocity
                param["type"] = type_spec.strip()
                # Set appropriate ranges for known types
                if param["type"] == "channel":
                    param["min"] = 1
                    param["max"] = 16
                elif param["type"] == "bool":
                    param["min"] = 0
                    param["max"] = 1
                elif param["type"] == "percent":
                    param["min"] = 0
                    param["max"] = 100
                elif param["type"] in ("note", "velocity"):
                    param["min"] = 0
                    param["max"] = 127
        else:
            param["name"] = name_part.strip()

        return param

    def _parse_params(self, params_tree) -> list[dict[str, Any]]:
        """
        Parse parameter specifications from Lark tree (for macro aliases).

        The params_tree contains param_ref nodes, each with a param_spec child.
        """
        params = []

        # params_tree is an alias_params node containing param_ref children
        for param_ref in params_tree.find_data("param_ref"):
            # Get the param_spec child
            param_spec = param_ref.children[0]
            param_dict = self._parse_param_spec_tree(param_spec)
            params.append(param_dict)

        return params

    def _parse_param_spec_tree(self, param_spec_tree) -> dict[str, Any]:
        """
        Parse a param_spec tree node into a parameter dictionary.

        param_spec: IDENTIFIER param_type? param_default? param_enum?
        """
        param = {
            "name": "",
            "type": "generic",
            "min": 0,
            "max": 127,
            "default": None,
            "enum_values": None,
        }

        children = list(param_spec_tree.children)

        # First child is always the parameter name
        param["name"] = str(children[0])

        # Process optional children
        for child in children[1:]:
            if child.data == "param_type":
                # param_type: ":" PARAM_RANGE | ":" param_type_name
                type_children = list(child.children)
                child_value = str(type_children[0])

                # Check if it's a range (contains hyphen)
                # Use regex to properly handle negative numbers
                import re

                range_match = re.match(
                    r"^(-?\d+(?:\.\d+)?)\s*-\s*(-?\d+(?:\.\d+)?)$", child_value.strip()
                )
                if range_match:
                    # PARAM_RANGE: "min-max" (e.g., "0-127", "0.5-8.0", "-24-24")
                    param["type"] = "range"
                    min_str, max_str = range_match.groups()

                    # Try to parse as int first, then as float
                    try:
                        param["min"] = int(min_str)
                        param["max"] = int(max_str)
                    except ValueError:
                        # If int conversion fails, must be float
                        param["min"] = float(min_str)
                        param["max"] = float(max_str)
                else:
                    # Named type (PARAM_TYPE_NAME)
                    param["type"] = child_value
                    # Set appropriate ranges
                    if param["type"] == "channel":
                        param["min"] = 1
                        param["max"] = 16
                    elif param["type"] == "bool":
                        param["min"] = 0
                        param["max"] = 1
                    elif param["type"] == "percent":
                        param["min"] = 0
                        param["max"] = 100
                    elif param["type"] in ("note", "velocity"):
                        param["min"] = 0
                        param["max"] = 127

            elif child.data == "param_default":
                # param_default: "=" (INT | IDENTIFIER)
                default_val = child.children[0]
                try:
                    param["default"] = int(default_val)
                except (ValueError, TypeError):
                    param["default"] = str(default_val)

            elif child.data == "param_enum":
                # param_enum: "=" enum_option ("," enum_option)*
                param["type"] = "enum"
                param["enum_values"] = {}
                for enum_option in child.find_data("enum_option"):
                    # enum_option: IDENTIFIER ":" INT
                    opt_name = str(enum_option.children[0])
                    opt_value = int(enum_option.children[1])
                    param["enum_values"][opt_name] = opt_value

        return param
