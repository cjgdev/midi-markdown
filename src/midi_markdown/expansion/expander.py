"""
Command Expander - Unified orchestrator for variable expansion, loops, and sweeps.

Phase 4: Coordinates all expansion operations and provides a clean interface
for the compilation pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from midi_markdown.alias.computation import ComputationError, SafeComputationEngine

from .errors import (
    ExpansionError,
    InvalidLoopConfigError,
    InvalidSweepConfigError,
    TimingConflictError,
    UndefinedVariableError,
    ValueRangeError,
)
from .loops import (
    IntervalType,
    LoopCommand,
    LoopDefinition,
    LoopExpander,
    LoopInterval,
    parse_interval,
)
from .random import RandomValueExpander
from .sweeps import (
    RampSpec,
    RampType,
    SweepDefinition,
    SweepExpander,
    parse_sweep_interval,
)
from .variables import SymbolTable


@dataclass
class ExpansionStats:
    """Statistics about expansion operations."""

    defines_processed: int = 0
    loops_expanded: int = 0
    sweeps_expanded: int = 0
    events_generated: int = 0
    variables_substituted: int = 0


class CommandExpander:
    """
    Unified orchestrator for command expansion.

    Coordinates:
    - Variable definitions (@define) via SymbolTable
    - Loop expansion via LoopExpander
    - Sweep expansion via SweepExpander
    - Variable substitution in commands
    - Event sorting and validation

    Usage:
        expander = CommandExpander(ppq=480, tempo=120.0)
        expanded_events = expander.process_ast(ast_nodes)
    """

    def __init__(
        self,
        ppq: int = 480,
        tempo: float = 120.0,
        time_signature: tuple[int, int] = (4, 4),
        source_file: str = "<unknown>",
    ):
        """
        Initialize command expander.

        Args:
            ppq: Pulses per quarter note (MIDI resolution)
            tempo: Default tempo in BPM
            time_signature: Time signature as (numerator, denominator) tuple, e.g., (4, 4) for 4/4 time
            source_file: Source filename for error reporting
        """
        self.ppq = ppq
        self.tempo = tempo
        self.time_signature = time_signature
        self.source_file = source_file

        # Core components
        self.symbol_table = SymbolTable()
        self.computation_engine = SafeComputationEngine()
        self.loop_expander = LoopExpander(
            parent_symbols=self.symbol_table, ppq=ppq, tempo=tempo, time_signature=time_signature
        )
        self.sweep_expander = SweepExpander(ppq=ppq)
        self.random_expander = RandomValueExpander()

        # State
        self.current_time = 0  # Track current time in ticks
        self.events: list[dict] = []
        self.stats = ExpansionStats()

    def process_ast(self, ast_nodes: list[Any]) -> list[dict]:
        """
        Process AST nodes and return expanded events.

        Uses two-pass processing:
        1. Pass 1: Collect all @define statements
        2. Pass 2: Expand loops, sweeps, and commands with variable substitution

        Args:
            ast_nodes: List of AST nodes from parser

        Returns:
            List of expanded event dictionaries sorted by time

        Raises:
            ExpansionError: If expansion fails
        """
        self.events = []
        self.stats = ExpansionStats()

        # Pass 1: Process all @define statements
        for node in ast_nodes:
            if self._is_define_node(node):
                self._process_define(node)

        # Pass 2: Expand loops, sweeps, and commands
        for node in ast_nodes:
            if self._is_define_node(node):
                continue  # Already processed in pass 1

            if self._is_loop_node(node):
                self._process_loop(node)
            elif self._is_sweep_node(node):
                self._process_sweep(node)
            elif self._is_timed_event_node(node):
                self._process_timed_event(node)
            elif self._is_command_node(node):
                self._process_command(node)

        # Sort events by time
        self.events = self._sort_events(self.events)

        # Validate events
        self._validate_events(self.events)

        self.stats.events_generated = len(self.events)
        return self.events

    def get_stats(self) -> ExpansionStats:
        """Get expansion statistics."""
        return self.stats

    def get_symbol_table(self) -> SymbolTable:
        """Get symbol table for inspection."""
        return self.symbol_table

    # ========================================================================
    # Node Type Detection
    # ========================================================================

    def _is_define_node(self, node: Any) -> bool:
        """Check if node is a @define statement."""
        return bool(isinstance(node, dict) and node.get("type") == "define")

    def _is_loop_node(self, node: Any) -> bool:
        """Check if node is a @loop statement."""
        return bool(isinstance(node, dict) and node.get("type") == "loop")

    def _is_sweep_node(self, node: Any) -> bool:
        """Check if node is a @sweep statement."""
        return bool(isinstance(node, dict) and node.get("type") == "sweep")

    def _is_timed_event_node(self, node: Any) -> bool:
        """Check if node is a timed event block."""
        return bool(isinstance(node, dict) and node.get("type") == "timed_event")

    def _is_command_node(self, node: Any) -> bool:
        """Check if node is a MIDI command."""
        from midi_markdown.parser.ast_nodes import MIDICommand

        if isinstance(node, MIDICommand):
            return True
        if isinstance(node, dict) and "type" in node:
            # Check for known command types
            cmd_types = {
                "pc",
                "cc",
                "note",
                "note_on",
                "note_off",
                "pitch_bend",
                "pressure",
                "sysex",
            }
            if node["type"] in cmd_types:
                return True
        return False

    # ========================================================================
    # Pass 1: Define Processing
    # ========================================================================

    def _process_define(self, node: dict) -> None:
        """
        Process a @define statement.

        Args:
            node: Define node with 'name' and 'value'

        Raises:
            ExpansionError: If define processing fails
        """
        name = node.get("name")
        value = node.get("value")
        line = node.get("line", 0)

        if not name:
            msg = "Define statement missing variable name"
            raise ExpansionError(msg, line=line, file=self.source_file)

        try:
            # Resolve value (may be expression, variable reference, or literal)
            resolved_value = self._resolve_value(value)

            # Define in symbol table
            self.symbol_table.define(name, resolved_value, line=line)
            self.stats.defines_processed += 1

        except Exception as e:
            msg = f"Failed to process @define {name}: {e}"
            raise ExpansionError(msg, line=line, file=self.source_file) from e

    def _resolve_value(self, value: Any) -> Any:
        """
        Resolve a value (may be literal, variable reference, or expression).

        Args:
            value: Value to resolve

        Returns:
            Resolved value (int, float, or string)
        """
        # Literal values
        if isinstance(value, int | float | str):
            return value

        # Variable reference tuple: ('var', 'NAME')
        if isinstance(value, tuple) and len(value) == 2 and value[0] == "var":
            return self.symbol_table.resolve(value[1])

        # Expression tuple: ('add', left, right), etc.
        if isinstance(value, tuple):
            return self._evaluate_expression_tuple(value)

        # Tree object (from parser)
        if hasattr(value, "data"):
            # Use computation engine to evaluate
            return self._evaluate_tree(value)

        # Default: return as-is
        return value

    def _evaluate_expression_tuple(self, expr: tuple) -> Any:
        """
        Evaluate an expression tuple.

        Args:
            expr: Expression tuple like ('add', left, right)

        Returns:
            Evaluated result
        """
        if len(expr) < 2:
            return expr

        op = expr[0]

        # Unary operators
        if op in ("neg", "pos"):
            operand = self._resolve_value(expr[1])
            if op == "neg":
                return -operand
            return operand

        # Binary operators
        if len(expr) >= 3:
            left = self._resolve_value(expr[1])
            right = self._resolve_value(expr[2])

            if op == "add":
                return left + right
            if op == "sub":
                return left - right
            if op == "mul":
                return left * right
            if op == "div":
                if right == 0:
                    msg = "Division by zero"
                    raise ExpansionError(msg)
                return left / right
            if op == "mod":
                return left % right
            if op == "pow":
                return left**right
            if op == "floordiv":
                return left // right

        return expr

    def _evaluate_tree(self, tree: Any) -> Any:
        """
        Evaluate a Lark tree object.

        Args:
            tree: Lark Tree object

        Returns:
            Evaluated result
        """
        try:
            # Convert tree to Python expression
            python_expr = self.computation_engine.lark_tree_to_python(tree)

            # Prepare variables
            input_params = {}
            for name, var in self.symbol_table.symbols.items():
                input_params[name] = var.value
            input_params.update(self.symbol_table.CONSTANTS)

            # Evaluate
            return self.computation_engine.evaluate_expression(python_expr, input_params)

        except ComputationError as e:
            msg = f"Expression evaluation failed: {e}"
            raise ExpansionError(msg) from e

    # ========================================================================
    # Pass 2: Loop Processing
    # ========================================================================

    def _process_loop(self, node: dict) -> None:
        """
        Process a @loop statement.

        Args:
            node: Loop node with 'count', 'interval', 'statements'

        Raises:
            InvalidLoopConfigError: If loop configuration is invalid
        """
        count = node.get("count", 1)
        interval_spec = node.get("interval")
        start_time_spec = node.get("start_time")
        statements = node.get("statements", [])
        line = node.get("source_line", 0)

        # Validate count
        if count <= 0:
            msg = f"Loop count must be positive, got {count}"
            raise InvalidLoopConfigError(
                msg,
                line=line,
                file=self.source_file,
                suggestion="Use a positive integer for loop count",
            )

        # Parse interval
        if interval_spec is None:
            interval = LoopInterval(value=1.0, interval_type=IntervalType.BEATS)
        else:
            # interval_spec can be a tuple (from parser) or string
            # parse_interval handles both
            try:
                interval = parse_interval(interval_spec)
            except ValueError as e:
                msg = f"Invalid loop interval: {e}"
                raise InvalidLoopConfigError(msg, line=line, file=self.source_file) from e

        # Determine start time
        start_time = self._resolve_timing(start_time_spec) if start_time_spec else self.current_time

        # Convert statements to LoopCommand objects
        from midi_markdown.parser.ast_nodes import MIDICommand

        loop_commands = []
        for stmt in statements:
            # Convert MIDICommand to dict if needed
            if isinstance(stmt, MIDICommand):
                cmd_dict = {
                    "type": stmt.type,
                    "channel": stmt.channel,
                }
                if hasattr(stmt, "data1") and stmt.data1 is not None:
                    cmd_dict["data1"] = stmt.data1
                if hasattr(stmt, "data2") and stmt.data2 is not None:
                    cmd_dict["data2"] = stmt.data2
                if hasattr(stmt, "note") and stmt.note is not None:
                    cmd_dict["note"] = stmt.note
                if hasattr(stmt, "velocity") and stmt.velocity is not None:
                    cmd_dict["velocity"] = stmt.velocity
                if hasattr(stmt, "duration") and stmt.duration is not None:
                    cmd_dict["duration"] = stmt.duration
                loop_cmd = LoopCommand(command=cmd_dict, relative_time=0)
            elif isinstance(stmt, dict):
                loop_cmd = LoopCommand(command=stmt, relative_time=0)
            else:
                continue  # Skip unknown types

            loop_commands.append(loop_cmd)

        # Create LoopDefinition
        loop_def = LoopDefinition(
            count=count,
            interval=interval,
            commands=loop_commands,
            start_time=start_time,
            source_line=line,
        )

        # Expand loop
        try:
            expanded_events = self.loop_expander.expand(loop_def)

            # Substitute variables in expanded events
            for event in expanded_events:
                substituted_event = self._substitute_variables(event)
                self.events.append(substituted_event)

            self.stats.loops_expanded += 1

            # Update current time
            interval_ticks = interval.to_ticks(self.ppq, self.tempo, self.time_signature)
            self.current_time = start_time + (count * interval_ticks)

        except Exception as e:
            msg = f"Loop expansion failed: {e}"
            raise InvalidLoopConfigError(msg, line=line, file=self.source_file) from e

    # ========================================================================
    # Pass 2: Sweep Processing
    # ========================================================================

    def _process_sweep(self, node: dict) -> None:
        """
        Process a @sweep statement.

        Args:
            node: Sweep node with 'start_time', 'end_time', 'interval', 'commands'

        Raises:
            InvalidSweepConfigError: If sweep configuration is invalid
        """
        start_time_spec = node.get("start_time")
        end_time_spec = node.get("end_time")
        interval_spec = node.get("interval")
        commands = node.get("commands", [])
        line = node.get("source_line", 0)

        # Resolve times
        start_time = self._resolve_timing(start_time_spec) if start_time_spec else self.current_time
        end_time = (
            self._resolve_timing(end_time_spec) if end_time_spec else start_time + (4 * self.ppq)
        )

        # Validate times
        if end_time <= start_time:
            msg = f"Sweep end time ({end_time}) must be after start time ({start_time})"
            raise InvalidSweepConfigError(
                msg,
                line=line,
                file=self.source_file,
                suggestion="Ensure sweep times are in chronological order",
            )

        # Parse interval (can be tuple from parser or string)
        # parse_sweep_interval handles both
        try:
            interval_ticks = parse_sweep_interval(
                interval_spec, ppq=self.ppq, tempo=self.tempo, time_signature=self.time_signature
            )
        except ValueError as e:
            msg = f"Invalid sweep interval: {e}"
            raise InvalidSweepConfigError(msg, line=line, file=self.source_file) from e

        # Calculate steps
        total_duration = end_time - start_time
        steps = max(1, int(total_duration / interval_ticks))

        # Parse sweep parameters from commands
        # Expected format: - cc CHANNEL.CONTROLLER.ramp(START, END, TYPE)
        # If no commands, nothing to sweep - return early (allows testing timing logic)
        if not commands:
            self.current_time = end_time_spec
            self.stats.sweeps_expanded += 1
            return

        # Extract first command (sweeps typically have one command)
        first_cmd = commands[0]

        # Handle MIDICommand objects
        if hasattr(first_cmd, "type"):
            command_type = first_cmd.type
            channel = first_cmd.channel if first_cmd.channel is not None else 1
            data1 = first_cmd.data1 if first_cmd.data1 is not None else 7
            data2 = first_cmd.data2
        else:
            # Handle dict-based commands
            command_type = first_cmd.get("type", "cc")
            channel = first_cmd.get("channel", 1)
            data1 = first_cmd.get("data1", 7)
            data2 = first_cmd.get("data2", 0)

        # Extract ramp specification from data2
        if isinstance(data2, dict) and data2.get("type") == "ramp":
            start_val = float(data2.get("start", 0))
            end_val = float(data2.get("end", 127))
            ramp_type_str = data2.get("ramp_type", "linear")

            # Convert string to RampType enum
            ramp_type_map = {
                "linear": RampType.LINEAR,
                "exponential": RampType.EXPONENTIAL,
                "logarithmic": RampType.LOGARITHMIC,
                "ease-in": RampType.EASE_IN,
                "ease-out": RampType.EASE_OUT,
                "ease-in-out": RampType.EASE_IN_OUT,
            }
            ramp_type = ramp_type_map.get(ramp_type_str, RampType.LINEAR)
            ramp = RampSpec(ramp_type, start_val, end_val)
        else:
            # Default: linear sweep from current value to data2
            ramp = RampSpec(
                RampType.LINEAR, 0.0, float(data2) if isinstance(data2, int | float) else 127.0
            )

        sweep_def = SweepDefinition(
            command_type=command_type,
            channel=channel,
            data1=data1,
            ramp=ramp,
            steps=steps,
            interval_ticks=interval_ticks,
            start_time=start_time,
            source_line=line,
        )

        # Expand sweep
        try:
            expanded_events = self.sweep_expander.expand(sweep_def)

            # Substitute variables in expanded events
            for event in expanded_events:
                substituted_event = self._substitute_variables(event)
                self.events.append(substituted_event)

            self.stats.sweeps_expanded += 1

            # Update current time
            self.current_time = end_time

        except Exception as e:
            msg = f"Sweep expansion failed: {e}"
            raise InvalidSweepConfigError(msg, line=line, file=self.source_file) from e

    # ========================================================================
    # Pass 2: Command Processing
    # ========================================================================

    def _process_timed_event(self, node: dict) -> None:
        """Process a timed event block."""
        timing = node.get("timing")
        commands = node.get("commands", [])

        # Update current time from timing
        if timing:
            self.current_time = self._resolve_timing(timing)

        # Process each command
        for cmd in commands:
            self._process_command(cmd)

    def _process_command(self, node: Any) -> None:
        """
        Process a single MIDI command with variable substitution.

        Args:
            node: Command node (MIDICommand or dict)
        """
        from midi_markdown.parser.ast_nodes import MIDICommand

        # Convert to dict if MIDICommand
        if isinstance(node, MIDICommand):
            cmd_dict = {"type": node.type, "channel": node.channel, "time": self.current_time}
            if hasattr(node, "data1"):
                cmd_dict["data1"] = node.data1
            if hasattr(node, "data2"):
                cmd_dict["data2"] = node.data2
            if hasattr(node, "note"):
                cmd_dict["note"] = node.note
            if hasattr(node, "velocity"):
                cmd_dict["velocity"] = node.velocity
            # Extract duration from params if present
            duration_value = None
            if hasattr(node, "params") and node.params:
                duration_value = node.params.get("duration")
        elif isinstance(node, dict):
            cmd_dict = node.copy()
            cmd_dict["time"] = self.current_time
            # Extract duration from dict params if present
            duration_value = cmd_dict.get("params", {}).get("duration")
        else:
            return  # Skip unknown node types

        # Substitute variables
        cmd_dict = self._substitute_variables(cmd_dict)

        # Add to events
        self.events.append(cmd_dict)

        # Handle note_on with duration: auto-generate note_off
        if cmd_dict.get("type") == "note_on" and duration_value is not None:
            # Parse duration to ticks
            from midi_markdown.expansion.loops import parse_interval

            try:
                interval = parse_interval(duration_value)
                duration_ticks = interval.to_ticks(self.ppq, self.tempo, self.time_signature)
            except (ValueError, AttributeError):
                # If parsing fails, skip note_off generation
                return

            # Create note_off event
            note_off_dict = {
                "type": "note_off",
                "channel": cmd_dict["channel"],
                "data1": cmd_dict["data1"],  # Same note number
                "data2": 0,  # Note off velocity typically 0
                "time": self.current_time + duration_ticks,
            }
            self.events.append(note_off_dict)

    def _substitute_variables(self, event: dict) -> dict:
        """
        Recursively substitute variables and expand random expressions in an event dictionary.

        Args:
            event: Event dictionary with potential variable references and random expressions

        Returns:
            Event with all variables resolved and random expressions expanded
        """
        from midi_markdown.parser.ast_nodes import RandomExpression

        resolved = {}

        for key, value in event.items():
            if isinstance(value, tuple) and len(value) == 2 and value[0] == "var":
                # Variable reference
                try:
                    resolved[key] = self.symbol_table.resolve(value[1])
                    self.stats.variables_substituted += 1
                except (KeyError, ValueError) as e:
                    # Collect similar names for suggestion
                    similar = self._find_similar_names(value[1])
                    raise UndefinedVariableError(
                        value[1],
                        line=event.get("line", 0),
                        file=self.source_file,
                        similar_names=similar,
                    ) from e
            elif isinstance(value, RandomExpression):
                # Random expression - expand to concrete value
                try:
                    resolved[key] = self.random_expander.expand_random(value)
                except (ValueError, TypeError) as e:
                    msg = f"Failed to expand random expression: {e}"
                    raise ExpansionError(
                        msg,
                        line=event.get("line", 0),
                        file=self.source_file,
                    ) from e
            elif isinstance(value, dict):
                resolved[key] = self._substitute_variables(value)
            elif isinstance(value, list):
                resolved[key] = self._substitute_list(value)
            else:
                resolved[key] = value

        return resolved

    def _substitute_list(self, items: list) -> list:
        """
        Substitute variables and expand random expressions in a list.

        Args:
            items: List potentially containing variable references and random expressions

        Returns:
            List with all variables resolved and random expressions expanded
        """
        from midi_markdown.parser.ast_nodes import RandomExpression

        resolved = []
        for item in items:
            if isinstance(item, dict):
                resolved.append(self._substitute_variables(item))
            elif isinstance(item, RandomExpression):
                try:
                    resolved.append(self.random_expander.expand_random(item))
                except (ValueError, TypeError) as e:
                    msg = f"Failed to expand random expression in list: {e}"
                    raise ExpansionError(
                        msg,
                        line=0,
                        file=self.source_file,
                    ) from e
            elif isinstance(item, tuple) and len(item) == 2 and item[0] == "var":
                try:
                    resolved.append(self.symbol_table.resolve(item[1]))
                    self.stats.variables_substituted += 1
                except (KeyError, ValueError) as e:
                    similar = self._find_similar_names(item[1])
                    raise UndefinedVariableError(
                        item[1], line=0, file=self.source_file, similar_names=similar
                    ) from e
            else:
                resolved.append(item)
        return resolved

    def _find_similar_names(self, name: str) -> list[str]:
        """Find similar variable names for suggestions."""
        similar = []
        name_lower = name.lower()

        for var_name in self.symbol_table.symbols:
            if (
                var_name.lower() == name_lower
                or name_lower in var_name.lower()
                or var_name.lower() in name_lower
            ):
                similar.append(var_name)

        return similar[:3]  # Return up to 3 suggestions

    # ========================================================================
    # Utilities
    # ========================================================================

    def _resolve_timing(self, timing: Any) -> int:
        """
        Resolve a timing specification to ticks.

        Args:
            timing: Timing object from parser

        Returns:
            Absolute time in ticks
        """
        from midi_markdown.parser.ast_nodes import Timing

        if isinstance(timing, Timing):
            # Use timing object's calculated ticks if available
            if hasattr(timing, "ticks"):
                return timing.ticks

            # Calculate ticks based on timing type
            if timing.type == "absolute":
                # Absolute time in seconds - convert to ticks
                # ticks = seconds * (ppq * tempo / 60)
                seconds = (
                    float(timing.value) if isinstance(timing.value, str | int) else timing.value
                )
                ticks_per_second = (self.ppq * self.tempo) / 60.0
                return int(seconds * ticks_per_second)

            if timing.type == "musical":
                # Musical time format: bars.beats.ticks
                # timing.value is a tuple (bar, beat, tick) where:
                # - bar: Bar number (starts at 1)
                # - beat: Beat within the bar (starts at 1)
                # - tick: MIDI tick within the beat (0 to PPQ-1)
                if isinstance(timing.value, tuple) and len(timing.value) == 3:
                    bar, beat, tick = timing.value
                    beats_per_bar = self.time_signature[0]  # Time signature numerator
                    ticks_per_beat = self.ppq

                    # Convert to absolute ticks
                    # Formula: (bars - 1) * beats_per_bar * ticks_per_beat +
                    #          (beats - 1) * ticks_per_beat +
                    #          ticks
                    absolute_ticks = (
                        (bar - 1) * beats_per_bar * ticks_per_beat  # Full bars before this one
                        + (beat - 1) * ticks_per_beat  # Beats within current bar
                        + tick  # Ticks within current beat
                    )
                    return int(absolute_ticks)
                # Fallback for backwards compatibility or malformed input
                value = float(timing.value) if isinstance(timing.value, str | int) else timing.value
                return int(value * self.ppq)

            if timing.type == "relative":
                # Relative timing - add to current time
                # value is a tuple (delta_value, unit) where unit is 'ms', 's', 'b', 'm', or 't'
                if isinstance(timing.value, tuple):
                    delta_value, unit = timing.value
                    if unit == "ms":
                        # Milliseconds to seconds
                        delta_seconds = delta_value / 1000.0
                    elif unit == "s":
                        # Already in seconds
                        delta_seconds = delta_value
                    elif unit == "b":
                        # Beats to seconds
                        delta_seconds = (delta_value * 60.0) / self.tempo
                    elif unit == "m":
                        # Measures/bars to seconds
                        beats_per_measure = self.time_signature[0]  # Use time signature numerator
                        delta_beats = delta_value * beats_per_measure
                        delta_seconds = (delta_beats * 60.0) / self.tempo
                    elif unit == "t":
                        # Ticks - return directly
                        return self.current_time + int(delta_value)
                    else:
                        delta_seconds = delta_value
                else:
                    # Fallback for backwards compatibility
                    delta_seconds = (
                        float(timing.value) if isinstance(timing.value, str | int) else timing.value
                    )

                ticks_per_second = (self.ppq * self.tempo) / 60.0
                return self.current_time + int(delta_seconds * ticks_per_second)

            if timing.type == "simultaneous":
                # Simultaneous - use current time
                return self.current_time

            # Unknown type - return 0
            return 0

        if isinstance(timing, int):
            return timing

        return self.current_time

    def _sort_events(self, events: list[dict]) -> list[dict]:
        """
        Sort events by time with priority ordering.

        Priority order (for events at same time):
        1. Tempo changes
        2. Time signature changes
        3. Control changes
        4. Program changes
        5. Note events

        Args:
            events: Unsorted events

        Returns:
            Events sorted by (time, priority)
        """

        def event_priority(event: dict) -> tuple:
            time = event.get("time", 0)
            event_type = event.get("type", "")

            # Assign priority
            priority_map = {
                "tempo": 0,
                "time_signature": 1,
                "cc": 2,
                "control_change": 2,
                "pc": 3,
                "program_change": 3,
                "note": 4,
                "note_on": 4,
                "note_off": 5,
            }
            priority = priority_map.get(event_type, 10)

            return (time, priority)

        return sorted(events, key=event_priority)

    def _validate_events(self, events: list[dict]) -> None:
        """
        Validate expanded events.

        Args:
            events: Events to validate

        Raises:
            EventValidationError: If validation fails
            ValueRangeError: If values are out of range
        """
        # Sort events by time to handle multi-channel compositions
        # where events from different channels can be created in any order
        # but need to be validated in chronological order
        sorted_events = sorted(events, key=lambda e: e.get("time", 0))

        for i, event in enumerate(sorted_events):
            event_type = event.get("type", "unknown")
            line = event.get("line", 0)

            # Validate channel
            channel = event.get("channel")
            if channel is not None and (channel < 1 or channel > 16):
                msg = "channel"
                raise ValueRangeError(msg, channel, 1, 16, line=line, file=self.source_file)

            # Validate MIDI values (0-127)
            # Skip validation for event types with different ranges
            if event_type == "pitch_bend":
                # Pitch bend has special range: -8192 to +8191
                value = event.get("data1")
                if value is not None and (value < -8192 or value > 8191):
                    msg = "data1"
                    raise ValueRangeError(msg, value, -8192, 8191, line=line, file=self.source_file)
            elif event_type not in ["tempo", "marker", "text", "lyric", "time_signature"]:
                for key in ["data1", "data2", "velocity", "note"]:
                    value = event.get(key)
                    if value is not None and (value < 0 or value > 127):
                        raise ValueRangeError(key, value, 0, 127, line=line, file=self.source_file)

            # Check timing monotonicity (optional - can be disabled)
            if i > 0:
                prev_time = sorted_events[i - 1].get("time", 0)
                curr_time = event.get("time", 0)
                if curr_time < prev_time:
                    msg = f"Event time {curr_time} is before previous event time {prev_time}"
                    raise TimingConflictError(
                        msg,
                        event_time=curr_time,
                        line=line,
                        file=self.source_file,
                    )
