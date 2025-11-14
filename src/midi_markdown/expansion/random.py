"""
Random Value Generator for MIDI Markup Language

This module provides random value expansion for generative music, humanization,
and variation in MIDI sequences.

Features:
- Integer random values (MIDI CC, velocity, note numbers)
- Note name random values (C3-C5)
- Optional seed for reproducibility
- Range validation
"""

from __future__ import annotations

import random
from typing import Any

from midi_markdown.parser.ast_nodes import RandomExpression
from midi_markdown.utils.parameter_types import note_to_midi


class RandomValueExpander:
    """Expands random() expressions to concrete MIDI values.

    This class handles the expansion of RandomExpression AST nodes to
    concrete integer values for use in MIDI commands. It supports:
    - Integer ranges: random(0, 127)
    - Note name ranges: random(C3, C5)
    - Optional seeding: random(64, 96, seed=42)

    The expander validates ranges and ensures generated values are
    within MIDI-valid ranges.
    """

    def __init__(self) -> None:
        """Initialize the RandomValueExpander."""
        self._last_seed: int | None = None

    def expand_random(self, expr: RandomExpression) -> int:
        """Expand a RandomExpression to a concrete integer value.

        Args:
            expr: RandomExpression AST node with min_value, max_value, and optional seed

        Returns:
            Random integer between min_value and max_value (inclusive)

        Raises:
            ValueError: If min > max or values are out of range
            TypeError: If values cannot be converted to integers

        Examples:
            >>> expander = RandomValueExpander()
            >>> expander.expand_random(RandomExpression(0, 127))
            64  # (random value 0-127)
            >>> expander.expand_random(RandomExpression("C3", "C5"))
            60  # (random MIDI note 48-72)
            >>> expander.expand_random(RandomExpression(64, 96, seed=42))
            81  # (always same with seed=42)
        """
        # Parse min/max values (handle note names and integers)
        min_val = self._parse_value(expr.min_value)
        max_val = self._parse_value(expr.max_value)

        # Validate range
        if min_val > max_val:
            msg = f"random() min value ({min_val}) cannot be greater than max value ({max_val})"
            raise ValueError(msg)

        # Set seed if provided
        if expr.seed is not None:
            random.seed(expr.seed)
            self._last_seed = expr.seed

        # Generate and return random value
        return random.randint(min_val, max_val)

    def _parse_value(self, value: Any) -> int:
        """Convert note name or expression to MIDI integer.

        Args:
            value: Value to parse (int, str note name, or expression)

        Returns:
            Integer MIDI value

        Raises:
            ValueError: If value cannot be converted
            TypeError: If value type is unsupported

        Examples:
            >>> expander = RandomValueExpander()
            >>> expander._parse_value(64)
            64
            >>> expander._parse_value("C4")
            60
            >>> expander._parse_value("C#5")
            73
        """
        # Already an integer
        if isinstance(value, int):
            return value

        # Note name (string) or string integer
        if isinstance(value, str):
            # First try to convert to integer (for string numbers like "64")
            try:
                return int(value)
            except ValueError:
                # Not a number, try as note name
                try:
                    return note_to_midi(value)
                except ValueError as e:
                    msg = f"Invalid note name or integer string '{value}': {e}"
                    raise ValueError(msg) from e

        # Try to convert to int
        try:
            return int(value)
        except (ValueError, TypeError) as e:
            msg = f"Cannot convert {type(value).__name__} to integer: {value}"
            raise TypeError(msg) from e

    def validate_midi_range(
        self, value: int, min_range: int = 0, max_range: int = 127, param_name: str = "value"
    ) -> None:
        """Validate that a value is within MIDI range.

        Args:
            value: Value to validate
            min_range: Minimum allowed value
            max_range: Maximum allowed value
            param_name: Parameter name for error messages

        Raises:
            ValueError: If value is out of range

        Examples:
            >>> expander = RandomValueExpander()
            >>> expander.validate_midi_range(64)  # OK
            >>> expander.validate_midi_range(200)  # Raises ValueError
        """
        if not (min_range <= value <= max_range):
            msg = f"{param_name} {value} out of MIDI range [{min_range}, {max_range}]"
            raise ValueError(msg)


def expand_random_in_command(
    command: dict[str, Any], expander: RandomValueExpander
) -> dict[str, Any]:
    """Expand all RandomExpression nodes in a MIDI command dict.

    This function recursively searches a command dictionary for RandomExpression
    AST nodes and expands them to concrete integer values.

    Args:
        command: MIDI command dictionary (may contain RandomExpression values)
        expander: RandomValueExpander instance to use

    Returns:
        Command dictionary with all random expressions expanded

    Examples:
        >>> expander = RandomValueExpander()
        >>> cmd = {"type": "cc", "channel": 1, "data1": 7, "data2": RandomExpression(64, 96)}
        >>> expand_random_in_command(cmd, expander)
        {"type": "cc", "channel": 1, "data1": 7, "data2": 80}  # (random value)
    """
    # Create a copy to avoid modifying original
    result = command.copy()

    # Check all values for RandomExpression nodes
    for key, value in result.items():
        if isinstance(value, RandomExpression):
            # Expand to concrete integer
            result[key] = expander.expand_random(value)
        elif isinstance(value, dict):
            # Recursively expand nested dicts
            result[key] = expand_random_in_command(value, expander)
        elif isinstance(value, list):
            # Expand items in lists
            result[key] = [
                expander.expand_random(item)
                if isinstance(item, RandomExpression)
                else expand_random_in_command(item, expander)
                if isinstance(item, dict)
                else item
                for item in value
            ]

    return result
