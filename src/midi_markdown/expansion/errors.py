"""
Error types for command expansion.

Phase 4: Provides specific error types for variable expansion, loop processing,
sweep processing, and event validation with helpful context and suggestions.
"""

from __future__ import annotations


class ExpansionError(Exception):
    """
    Base class for all expansion-related errors.

    Provides context about where the error occurred (file, line) and
    helpful suggestions for fixing the issue.
    """

    def __init__(
        self, message: str, line: int = 0, file: str = "<unknown>", suggestion: str | None = None
    ):
        """
        Initialize expansion error.

        Args:
            message: Error description
            line: Source line number where error occurred
            file: Source file name
            suggestion: Optional suggestion for fixing the error
        """
        self.message = message
        self.line = line
        self.file = file
        self.suggestion = suggestion
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format error message with context."""
        parts = [f"Error at {self.file}:{self.line}"]
        parts.append(f"  {self.message}")
        if self.suggestion:
            parts.append(f"  Suggestion: {self.suggestion}")
        return "\n".join(parts)


class UndefinedVariableError(ExpansionError):
    """Variable referenced but not defined."""

    def __init__(
        self,
        variable_name: str,
        line: int = 0,
        file: str = "<unknown>",
        similar_names: list[str] | None = None,
    ):
        """
        Initialize undefined variable error.

        Args:
            variable_name: Name of undefined variable
            line: Source line number
            file: Source file name
            similar_names: List of similar variable names (for suggestions)
        """
        message = f"Undefined variable: ${{{variable_name}}}"

        suggestion = None
        if similar_names:
            suggestion = f"Did you mean: {', '.join(similar_names)}?"

        super().__init__(message, line, file, suggestion)
        self.variable_name = variable_name


class VariableTypeError(ExpansionError):
    """Variable has wrong type for operation."""

    def __init__(
        self,
        variable_name: str,
        expected_type: str,
        actual_type: str,
        line: int = 0,
        file: str = "<unknown>",
    ):
        """
        Initialize variable type error.

        Args:
            variable_name: Name of variable
            expected_type: Expected type (e.g., "int", "float")
            actual_type: Actual type
            line: Source line number
            file: Source file name
        """
        message = f"Variable ${{{variable_name}}} has type {actual_type}, expected {expected_type}"
        super().__init__(message, line, file)
        self.variable_name = variable_name
        self.expected_type = expected_type
        self.actual_type = actual_type


class InvalidLoopConfigError(ExpansionError):
    """Loop configuration is invalid."""

    def __init__(
        self, reason: str, line: int = 0, file: str = "<unknown>", suggestion: str | None = None
    ):
        """
        Initialize invalid loop config error.

        Args:
            reason: Why the loop config is invalid
            line: Source line number
            file: Source file name
            suggestion: Optional fix suggestion
        """
        message = f"Invalid loop configuration: {reason}"
        super().__init__(message, line, file, suggestion)


class InvalidSweepConfigError(ExpansionError):
    """Sweep configuration is invalid."""

    def __init__(
        self, reason: str, line: int = 0, file: str = "<unknown>", suggestion: str | None = None
    ):
        """
        Initialize invalid sweep config error.

        Args:
            reason: Why the sweep config is invalid
            line: Source line number
            file: Source file name
            suggestion: Optional fix suggestion
        """
        message = f"Invalid sweep configuration: {reason}"
        super().__init__(message, line, file, suggestion)


class TimingConflictError(ExpansionError):
    """Events have conflicting or invalid timing."""

    def __init__(self, reason: str, event_time: int, line: int = 0, file: str = "<unknown>"):
        """
        Initialize timing conflict error.

        Args:
            reason: Description of timing conflict
            event_time: Time (in ticks) where conflict occurred
            line: Source line number
            file: Source file name
        """
        message = f"Timing conflict at tick {event_time}: {reason}"
        suggestion = "Ensure events are in chronological order"
        super().__init__(message, line, file, suggestion)
        self.event_time = event_time


class EventValidationError(ExpansionError):
    """Event data is invalid."""

    def __init__(self, reason: str, event_type: str, line: int = 0, file: str = "<unknown>"):
        """
        Initialize event validation error.

        Args:
            reason: Why the event is invalid
            event_type: Type of event (e.g., "note_on", "cc")
            line: Source line number
            file: Source file name
        """
        message = f"Invalid {event_type} event: {reason}"
        super().__init__(message, line, file)
        self.event_type = event_type


class ValueRangeError(ExpansionError):
    """MIDI value out of valid range."""

    def __init__(
        self,
        value_name: str,
        value: int,
        min_value: int,
        max_value: int,
        line: int = 0,
        file: str = "<unknown>",
    ):
        """
        Initialize value range error.

        Args:
            value_name: Name of the value (e.g., "velocity", "controller")
            value: Actual value
            min_value: Minimum valid value
            max_value: Maximum valid value
            line: Source line number
            file: Source file name
        """
        message = f"{value_name} value {value} out of range [{min_value}-{max_value}]"
        suggestion = f"Use a value between {min_value} and {max_value}"
        super().__init__(message, line, file, suggestion)
        self.value_name = value_name
        self.value = value
        self.min_value = min_value
        self.max_value = max_value
