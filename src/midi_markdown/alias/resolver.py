"""Alias resolver for expanding device-specific commands.

The alias system is a core feature of MML that allows device-specific shortcuts.
"""

from __future__ import annotations

import re
from typing import Any

from midi_markdown.parser.ast_nodes import AliasDefinition, MIDICommand
from midi_markdown.utils.parameter_types import bool_to_midi, note_to_midi, percent_to_midi

from .computation import ComputationError, SafeComputationEngine
from .conditionals import ConditionalEvaluator
from .errors import AliasError, AliasMaxDepthError, AliasRecursionError


class AliasResolver:
    """Resolves and expands aliases to MIDI commands.

    The resolver:
    1. Validates alias usage
    2. Binds arguments to parameters
    3. Validates parameter ranges and types
    4. Evaluates computed values (mathematical expressions)
    5. Evaluates conditional branches (if/elif/else)
    6. Expands aliases to base MIDI commands

    Stage 1: Basic expansion (no nesting, no imports, no computation)
    Stage 2: Enhanced parameter types (note names, percentages, booleans)
    Stage 3: Nested aliases (aliases calling other aliases)
    Stage 6: Computed values (mathematical expressions in parameters)
    Stage 7: Conditional logic (@if/@elif/@else branches)
    """

    def __init__(
        self, aliases: dict[str, AliasDefinition] | None = None, max_depth: int = 10
    ) -> None:
        """Initialize the alias resolver.

        Args:
            aliases: Dictionary of alias definitions (name -> AliasDefinition)
            max_depth: Maximum allowed nesting depth (default: 10)
        """
        self.aliases = aliases or {}
        self.max_depth = max_depth
        self.computation_engine = SafeComputationEngine()

    def resolve(
        self,
        alias_name: str,
        arguments: list[Any],
        timing: Any = None,
        source_line: int = 0,
        _expansion_stack: list[tuple[str, list[Any]]] | None = None,
        _depth: int = 0,
    ) -> list[MIDICommand]:
        """Resolve an alias to MIDI commands with nesting support.

        This method now supports nested aliases (aliases calling other aliases)
        with cycle detection and depth limiting.

        Args:
            alias_name: The alias name to expand
            arguments: Arguments passed to the alias
            timing: Timing information to apply to expanded commands
            source_line: Source line number for error reporting
            _expansion_stack: Internal - tracks current expansion path for cycle detection
            _depth: Internal - current expansion depth for depth limiting

        Returns:
            List of expanded MIDI commands (fully resolved, no nested alias calls)

        Raises:
            AliasError: If alias not found or parameters invalid
            AliasRecursionError: If circular dependency detected
            AliasMaxDepthError: If expansion exceeds max_depth

        Note:
            The _expansion_stack and _depth parameters are for internal use only
            and should not be passed by external callers.
        """
        # Initialize tracking on first call
        if _expansion_stack is None:
            _expansion_stack = []

        # Check for max depth exceeded
        if _depth >= self.max_depth:
            raise AliasMaxDepthError(
                alias_name=alias_name,
                current_depth=_depth,
                max_depth=self.max_depth,
                call_chain=_expansion_stack,
            )

        # Check for circular dependency (cycle detection)
        if any(name == alias_name for name, _ in _expansion_stack):
            raise AliasRecursionError(alias_name=alias_name, call_chain=_expansion_stack)

        # Add current alias to stack
        _expansion_stack.append((alias_name, arguments))

        try:
            # Look up alias definition
            if alias_name not in self.aliases:
                msg = (
                    f"Undefined alias '{alias_name}' at line {source_line}. "
                    f"Available aliases: {', '.join(self.aliases.keys()) or 'none'}"
                )
                raise AliasError(msg)

            alias_def = self.aliases[alias_name]

            # Bind and validate parameters
            param_values = self._bind_parameters(alias_def, arguments, source_line)

            # Evaluate computed values (Stage 6)
            if alias_def.computed_values:
                try:
                    for var_name, expr_tree in alias_def.computed_values.items():
                        # Convert Lark tree to Python expression
                        expr_str = self.computation_engine.lark_tree_to_python(expr_tree)

                        # Evaluate expression with current parameter values (read-only)
                        computed_value = self.computation_engine.evaluate_expression(
                            expr_str, param_values
                        )

                        # Add computed value to parameter namespace
                        param_values[var_name] = computed_value

                except ComputationError as e:
                    msg = f"Computation error in alias '{alias_name}' at line {source_line}: {e}"
                    raise AliasError(msg)

            # Select commands based on conditionals (Stage 7)
            if alias_def.has_conditionals and alias_def.conditional_branches:
                # Conditional alias - evaluate conditions and select branch
                evaluator = ConditionalEvaluator()
                selected_commands = evaluator.select_branch(
                    alias_def.conditional_branches, param_values
                )

                if selected_commands is None:
                    msg = (
                        f"No conditional branch matched in alias '{alias_name}' "
                        f"at line {source_line}. Parameter values: {param_values}"
                    )
                    raise AliasError(msg)

                # Use selected commands
                commands_to_expand = selected_commands
            else:
                # Non-conditional alias - use all commands
                commands_to_expand = alias_def.commands

            # Expand commands - track timing for relative offsets
            from midi_markdown.parser.ast_nodes import Timing

            expanded_commands = []
            accumulated_timing = None  # Track relative timing to apply to next command
            current_timing = timing  # Start with timing from call site

            for item in commands_to_expand:
                # Check if this is a timing statement
                if isinstance(item, Timing):
                    if item.type == "relative":
                        # Accumulate relative timing for next command
                        if accumulated_timing is None:
                            accumulated_timing = item
                        else:
                            # Combine relative timings (add them)
                            accumulated_timing = self._combine_relative_timing(
                                accumulated_timing, item
                            )
                    elif item.type == "simultaneous":
                        # Simultaneous timing means same time as previous command
                        # Store it to apply to next command
                        accumulated_timing = item
                    elif item.type == "absolute":
                        # Absolute timing not allowed in aliases
                        msg = (
                            f"Absolute timing (e.g., [mm:ss.mmm]) is not supported in alias '{alias_name}'. "
                            f"Use relative timing (e.g., [+100ms], [+1b]) instead to preserve reusability. "
                            f"See docs/dev-guides/anti-patterns.md for details."
                        )
                        raise AliasError(msg)
                    elif item.type == "musical":
                        # Musical timing not allowed in aliases
                        msg = (
                            f"Musical timing (e.g., [bars.beats.ticks]) is not supported in alias '{alias_name}'. "
                            f"Use relative timing (e.g., [+100ms], [+1b]) instead to preserve reusability. "
                            f"See docs/dev-guides/anti-patterns.md for details."
                        )
                        raise AliasError(msg)
                    else:
                        # Unknown timing type
                        msg = f"Unknown timing type '{item.type}' in alias '{alias_name}'"
                        raise AliasError(msg)
                    continue

                # It's a command (str or MIDICommand)
                command_template = item

                # Determine what timing to apply to this command
                command_timing = accumulated_timing or current_timing

                if isinstance(command_template, str):
                    # String template - substitute parameters and parse
                    expanded_str = self._substitute_parameters(command_template, param_values)

                    # Check if this might be a nested alias call
                    # Format: "alias_name arg1 arg2 ..." or "alias_name arg1.arg2.arg3"
                    nested_commands = self._try_resolve_nested_alias(
                        expanded_str, command_timing, source_line, _expansion_stack, _depth
                    )

                    if nested_commands is not None:
                        # Was a nested alias - add all expanded commands
                        expanded_commands.extend(nested_commands)
                    else:
                        # Not a nested alias - parse as MIDI command
                        expanded_cmd = self._parse_command_string(
                            expanded_str, command_timing, source_line
                        )
                        expanded_commands.append(expanded_cmd)

                    # Reset accumulated timing after applying to command
                    accumulated_timing = None

                elif isinstance(command_template, MIDICommand):
                    # Already parsed command - substitute in params dict
                    expanded_cmd = self._substitute_in_command(
                        command_template, param_values, command_timing, source_line
                    )

                    # Check if this is an alias_call type that needs recursive resolution
                    if expanded_cmd.type == "alias_call":
                        # Extract alias name and args from command
                        nested_alias_name = expanded_cmd.params.get("alias_name")
                        nested_args = expanded_cmd.params.get("arguments", [])

                        if nested_alias_name is None:
                            msg = f"alias_call command missing alias_name at line {source_line}"
                            raise AliasError(msg)

                        # Recursively resolve the nested alias
                        nested_commands = self.resolve(
                            alias_name=str(nested_alias_name),
                            arguments=nested_args,
                            timing=command_timing or expanded_cmd.timing,
                            source_line=expanded_cmd.source_line,
                            _expansion_stack=_expansion_stack,
                            _depth=_depth + 1,
                        )
                        expanded_commands.extend(nested_commands)
                    else:
                        expanded_commands.append(expanded_cmd)

                    # Reset accumulated timing after applying to command
                    accumulated_timing = None

            return expanded_commands

        finally:
            # Always remove from stack, even if error occurred
            _expansion_stack.pop()

    def _try_resolve_nested_alias(
        self,
        command_str: str,
        timing: Any,
        source_line: int,
        expansion_stack: list[tuple[str, list[Any]]],
        depth: int,
    ) -> list[MIDICommand] | None:
        """Try to resolve a command string as a nested alias call.

        Args:
            command_str: The command string to check
            timing: Timing to apply
            source_line: Source line number
            expansion_stack: Current expansion stack
            depth: Current expansion depth

        Returns:
            List of resolved MIDI commands if this was an alias call,
            None if this is not an alias call (should be parsed as MIDI command)
        """
        # Remove leading dash and whitespace
        command_str = command_str.strip().lstrip("-").strip()

        if not command_str:
            return None

        # Parse as potential alias call: "alias_name arg1 arg2 ..." or "alias_name arg1.arg2"
        # Split on first space or period to get potential alias name
        if " " in command_str:
            parts = command_str.split(None, 1)  # Split on whitespace
            potential_name = parts[0]
            args_str = parts[1] if len(parts) > 1 else ""
        elif "." in command_str and command_str.split(".")[0] not in (
            "cc",
            "pc",
            "note",
            "note_on",
            "pb",
            "cp",
            "pp",
        ):
            # Has dots but doesn't start with known MIDI command
            parts = command_str.split(".", 1)
            potential_name = parts[0]
            args_str = parts[1] if len(parts) > 1 else ""
        else:
            # Just a potential alias name with no args, or a MIDI command
            potential_name = command_str.split(".")[0].split()[0]
            args_str = ""

        # Check if this name exists in our alias registry
        if potential_name not in self.aliases:
            return None  # Not an alias, let it be parsed as MIDI command

        # Parse arguments
        arguments = []
        if args_str:
            # Try space-separated first, then dot-separated
            arguments = args_str.split() if " " in args_str else args_str.split(".")

        # Recursively resolve the nested alias
        try:
            return self.resolve(
                alias_name=potential_name,
                arguments=arguments,
                timing=timing,
                source_line=source_line,
                _expansion_stack=expansion_stack,
                _depth=depth + 1,
            )
        except (AliasRecursionError, AliasMaxDepthError):
            # Re-raise recursion and depth errors - these are real problems
            raise
        except AliasError:
            # Other alias errors - maybe it wasn't an alias after all
            return None

    def _bind_parameters(
        self, alias_def: AliasDefinition, arguments: list[Any], source_line: int
    ) -> dict[str, Any]:
        """Bind arguments to parameters and validate.

        Args:
            alias_def: Alias definition with parameter specs
            arguments: Provided arguments
            source_line: Source line for error reporting

        Returns:
            Dictionary mapping parameter names to values

        Raises:
            AliasError: If parameter count mismatch or validation fails
        """
        params = alias_def.parameters
        param_values = {}

        # Count required vs optional parameters
        required_count = sum(1 for p in params if p.get("default") is None)
        total_count = len(params)

        # Check argument count
        if len(arguments) < required_count:
            msg = (
                f"Alias '{alias_def.name}' requires at least {required_count} arguments, "
                f"got {len(arguments)} at line {source_line}"
            )
            raise AliasError(msg)

        if len(arguments) > total_count:
            msg = (
                f"Alias '{alias_def.name}' accepts at most {total_count} arguments, "
                f"got {len(arguments)} at line {source_line}"
            )
            raise AliasError(msg)

        # Bind each parameter
        for i, param_def in enumerate(params):
            param_name = param_def["name"]

            # Get value (from arguments or default)
            if i < len(arguments):
                value = arguments[i]
            elif param_def.get("default") is not None:
                value = param_def["default"]
            else:
                msg = (
                    f"Missing required parameter '{param_name}' for alias '{alias_def.name}' "
                    f"at line {source_line}"
                )
                raise AliasError(msg)

            # Validate and convert value
            validated_value = self._validate_parameter(
                param_def, value, alias_def.name, source_line
            )
            param_values[param_name] = validated_value

        return param_values

    def _validate_parameter(
        self, param_def: dict[str, Any], value: Any, alias_name: str, source_line: int
    ) -> int | float:
        """Validate a parameter value against its definition.

        Args:
            param_def: Parameter definition dict
            value: Value to validate
            alias_name: Alias name for error messages
            source_line: Source line for error reporting

        Returns:
            Validated integer or float value

        Raises:
            AliasError: If validation fails
        """
        param_name = param_def["name"]
        param_type = param_def.get("type", "generic")

        # Handle enum parameters
        if param_type == "enum" and param_def.get("enum_values"):
            if isinstance(value, str):
                if value not in param_def["enum_values"]:
                    valid_options = ", ".join(param_def["enum_values"].keys())
                    msg = (
                        f"Invalid value '{value}' for enum parameter '{param_name}' "
                        f"in alias '{alias_name}'. Valid options: {valid_options} "
                        f"at line {source_line}"
                    )
                    raise AliasError(msg)
                return param_def["enum_values"][value]
            # Numeric value for enum - validate it's in the enum values
            if value not in param_def["enum_values"].values():
                msg = (
                    f"Invalid numeric value {value} for enum parameter '{param_name}' "
                    f"in alias '{alias_name}' at line {source_line}"
                )
                raise AliasError(msg)
            return int(value)

        # Handle note parameter - convert note names to MIDI numbers
        if param_type == "note" and isinstance(value, str):
            try:
                return note_to_midi(value)
            except ValueError as e:
                msg = (
                    f"Invalid note name '{value}' for parameter '{param_name}' "
                    f"in alias '{alias_name}': {e} at line {source_line}"
                )
                raise AliasError(msg)
            # If numeric, fall through to validate as MIDI note number

        # Handle percent parameter - scale 0-100 to 0-127
        if param_type == "percent":
            try:
                percent_value = int(value)
            except (ValueError, TypeError):
                msg = (
                    f"Invalid percent value '{value}' for parameter '{param_name}' "
                    f"in alias '{alias_name}' - expected integer 0-100 at line {source_line}"
                )
                raise AliasError(msg)

            try:
                return percent_to_midi(percent_value)
            except ValueError as e:
                msg = (
                    f"Invalid percent value for parameter '{param_name}' "
                    f"in alias '{alias_name}': {e} at line {source_line}"
                )
                raise AliasError(msg)

        # Handle bool parameter - accept various boolean formats
        if param_type == "bool":
            try:
                return bool_to_midi(value)
            except ValueError as e:
                msg = (
                    f"Invalid boolean value '{value}' for parameter '{param_name}' "
                    f"in alias '{alias_name}': {e} at line {source_line}"
                )
                raise AliasError(msg)

        # Convert to numeric value (int or float) for generic and other typed parameters
        # Try float if value is already float or string contains decimal point
        numeric_value: int | float

        # Check if value is already a float or looks like one
        if isinstance(value, float):
            numeric_value = value
        elif isinstance(value, str) and "." in value:
            try:
                numeric_value = float(value)
            except (ValueError, TypeError):
                msg = (
                    f"Invalid value '{value}' for parameter '{param_name}' in alias '{alias_name}' "
                    f"- expected numeric value at line {source_line}"
                )
                raise AliasError(msg)
        else:
            # Try int first, then float
            try:
                numeric_value = int(value)
            except (ValueError, TypeError):
                try:
                    numeric_value = float(value)
                except (ValueError, TypeError):
                    msg = (
                        f"Invalid value '{value}' for parameter '{param_name}' in alias '{alias_name}' "
                        f"- expected numeric value at line {source_line}"
                    )
                    raise AliasError(msg)

        # Validate range
        min_val = param_def.get("min", 0)
        max_val = param_def.get("max", 127)

        if not (min_val <= numeric_value <= max_val):
            msg = (
                f"Parameter '{param_name}' value {numeric_value} out of range [{min_val}-{max_val}] "
                f"in alias '{alias_name}' at line {source_line}"
            )
            raise AliasError(msg)

        return numeric_value

    def _substitute_parameters(self, template: str, param_values: dict[str, Any]) -> str:
        """Substitute parameter placeholders in a template string.

        Args:
            template: Template string with {param} placeholders
            param_values: Dictionary of parameter values

        Returns:
            String with parameters substituted
        """
        result = template
        for param_name, param_value in param_values.items():
            # Replace all occurrences of {param_name} with the value
            # Match {name}, {name:...}, or {name=...} but not partial matches like {name_longer}
            pattern = r"\{" + re.escape(param_name) + r"(?:[=:][^}]*)?\}"
            # Convert float values to int to avoid decimal points in command strings
            # (e.g., "127.0" would break "cc 1.14.127.0" parsing which splits on dots)
            if isinstance(param_value, float) and param_value.is_integer():
                value_str = str(int(param_value))
            else:
                value_str = str(param_value)
            result = re.sub(pattern, value_str, result)
        return result

    def _parse_command_string(self, command_str: str, timing: Any, source_line: int) -> MIDICommand:
        """Parse an expanded command string into a MIDICommand.

        This is a simplified parser for basic MIDI commands.

        Args:
            command_str: Command string (e.g., "cc.1.7.100", "pc.1.5", or "cc 1.7.100")
            timing: Timing to apply
            source_line: Source line number

        Returns:
            Parsed MIDICommand object
        """
        # Remove leading dash if present
        command_str = command_str.strip().lstrip("-").strip()

        if not command_str:
            msg = f"Empty command after alias expansion at line {source_line}"
            raise AliasError(msg)

        # Check if command has the format "cmd.args" (no space) or "cmd args" (with space)
        if " " in command_str:
            # Space-separated format: "cc 1.7.100"
            parts = command_str.split(None, 1)  # Split on first whitespace only
            cmd_type = parts[0]
            args_str = parts[1] if len(parts) > 1 else ""
        elif "." in command_str:
            # Dot-separated format: "cc.1.7.100"
            parts = command_str.split(".", 1)
            cmd_type = parts[0]
            args_str = parts[1] if len(parts) > 1 else ""
        else:
            # Just command, no args
            cmd_type = command_str
            args_str = ""

        # Parse based on command type
        if cmd_type in ("cc", "control_change"):
            # Format: cc.channel.controller.value or cc channel.controller.value
            if not args_str:
                msg = f"Invalid cc command: {command_str} at line {source_line}"
                raise AliasError(msg)
            values = args_str.split(".")
            if len(values) != 3:
                msg = f"Invalid cc format: {command_str} - expected channel.cc.value at line {source_line}"
                raise AliasError(msg)
            return MIDICommand(
                type="control_change",
                channel=int(values[0]),
                data1=int(values[1]),
                data2=int(values[2]),
                timing=timing,
                source_line=source_line,
            )

        if cmd_type in ("pc", "program_change"):
            # Format: pc.channel.program or pc channel.program
            if not args_str:
                msg = f"Invalid pc command: {command_str} at line {source_line}"
                raise AliasError(msg)
            values = args_str.split(".")
            if len(values) != 2:
                msg = f"Invalid pc format: {command_str} - expected channel.program at line {source_line}"
                raise AliasError(msg)
            return MIDICommand(
                type="program_change",
                channel=int(values[0]),
                data1=int(values[1]),
                timing=timing,
                source_line=source_line,
            )

        if cmd_type in ("note", "note_on"):
            # Format: note.channel.note.velocity [duration]
            if not args_str:
                msg = f"Invalid note command: {command_str} at line {source_line}"
                raise AliasError(msg)
            # Check if duration is specified (space-separated after values)
            duration = None
            if " " in args_str:
                args_str, duration = args_str.split(None, 1)

            values = args_str.split(".")
            if len(values) < 3:
                msg = f"Invalid note format: {command_str} - expected channel.note.velocity at line {source_line}"
                raise AliasError(msg)

            params = {}
            if duration:
                params["duration"] = duration

            return MIDICommand(
                type="note_on",
                channel=int(values[0]),
                data1=int(values[1]),
                data2=int(values[2]),
                params=params,
                timing=timing,
                source_line=source_line,
            )

        # Generic command - store as params
        return MIDICommand(
            type=cmd_type, params={"raw": command_str}, timing=timing, source_line=source_line
        )

    def _combine_relative_timing(self, timing1: Any, timing2: Any) -> Any:
        """Combine two relative timing values by adding them.

        Args:
            timing1: First relative timing
            timing2: Second relative timing (must also be relative)

        Returns:
            New Timing object with combined offset

        Raises:
            AliasError: If timing2 is not relative type or uses unsupported units
        """
        from midi_markdown.parser.ast_nodes import Timing

        if timing2.type != "relative":
            msg = f"Cannot combine non-relative timing with accumulated relative timing: {timing2.raw}"
            raise AliasError(msg)

        # Both timings are relative: (value, unit)
        val1, unit1 = timing1.value
        val2, unit2 = timing2.value

        # Convert to common unit (milliseconds) for addition
        ms1 = self._to_milliseconds(val1, unit1)
        ms2 = self._to_milliseconds(val2, unit2)
        combined_ms = ms1 + ms2

        # Return as milliseconds
        return Timing(type="relative", value=(combined_ms, "ms"), raw=f"[+{combined_ms}ms]")

    def _to_milliseconds(self, value: float, unit: str) -> float:
        """Convert timing value to milliseconds.

        Args:
            value: Numeric timing value
            unit: Unit string ('ms', 's', 'b', 't')

        Returns:
            Value converted to milliseconds

        Raises:
            AliasError: If unit is beats or ticks (not supported in aliases)
        """
        if unit == "ms":
            return value
        if unit == "s":
            return value * 1000
        if unit == "b":
            # Beats to ms: depends on tempo
            msg = (
                "Cannot use beat-based relative timing in aliases "
                "(no tempo context available). Use 'ms' or 's' units instead."
            )
            raise AliasError(msg)
        if unit == "t":
            # Ticks to ms: depends on PPQ and tempo
            msg = (
                "Cannot use tick-based relative timing in aliases "
                "(no PPQ/tempo context available). Use 'ms' or 's' units instead."
            )
            raise AliasError(msg)
        msg = f"Unknown timing unit: {unit}"
        raise AliasError(msg)

    def _substitute_in_command(
        self, command: MIDICommand, param_values: dict[str, Any], timing: Any, source_line: int
    ) -> MIDICommand:
        """Substitute parameters in a MIDICommand object.

        Args:
            command: Command template with parameter placeholders
            param_values: Parameter values
            timing: Timing to apply
            source_line: Source line number

        Returns:
            New MIDICommand with substituted values
        """
        # Create a copy of the command with timing applied
        return MIDICommand(
            type=command.type,
            channel=command.channel,
            data1=command.data1,
            data2=command.data2,
            params=command.params.copy() if command.params else {},
            timing=timing or command.timing,
            source_line=source_line,
        )
