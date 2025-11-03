"""Validation error types."""

from __future__ import annotations


class ValidationError(Exception):
    """Raised when validation fails."""

    def __init__(
        self,
        message: str,
        line: int | None = None,
        column: int | None = None,
        error_code: str | None = None,
        suggestion: str | None = None,
    ) -> None:
        """Initialize validation error.

        Args:
            message: Error message
            line: Line number where error occurred
            column: Column number where error occurred
            error_code: Error code (e.g., E201, E202)
            suggestion: Helpful suggestion for fixing the error
        """
        self.message = message
        self.line = line
        self.column = column
        self.error_code = error_code or "E200"  # Default validation error code
        self.suggestion = suggestion
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format error message with location."""
        if self.line is not None and self.column is not None:
            return f"Line {self.line}:{self.column}: {self.message}"
        if self.line is not None:
            return f"Line {self.line}: {self.message}"
        return self.message
