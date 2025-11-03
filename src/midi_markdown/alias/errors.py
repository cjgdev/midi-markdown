"""Exception classes for alias system errors.

This module defines specialized exceptions for alias resolution failures,
including recursion errors, depth limit violations, and computation errors.
"""

from __future__ import annotations

from typing import Any


class AliasError(Exception):
    """Base class for alias-related errors."""


class ComputationError(AliasError):
    """Raised when computation evaluation fails.

    This error is raised when evaluating computed value expressions fails,
    including syntax errors, security violations, operation limits, or
    runtime errors like division by zero.
    """


class AliasRecursionError(AliasError):
    """Raised when circular alias dependency is detected.

    This error is raised when an alias attempts to call itself either
    directly (A calls A) or indirectly (A calls B, B calls A).

    Attributes:
        alias_name: Name of the alias where cycle was detected
        call_chain: List of (alias_name, args) tuples showing the call path
        message: Human-readable error message
    """

    def __init__(
        self, alias_name: str, call_chain: list[tuple[str, list[Any]]], message: str | None = None
    ):
        """Initialize recursion error.

        Args:
            alias_name: Name of alias where cycle was detected
            call_chain: Full call chain leading to cycle
            message: Optional custom message
        """
        self.alias_name = alias_name
        self.call_chain = call_chain

        if message is None:
            # Format call chain for display
            chain_str = " → ".join(
                f"{name}({', '.join(map(str, args))})" for name, args in call_chain
            )
            # Add the cyclic call
            chain_str += f" → {alias_name}"

            message = (
                f"Circular alias dependency detected: {alias_name}\n\n"
                f"Call chain: {chain_str}\n\n"
                f"Suggestion: Remove circular dependency between aliases."
            )

        super().__init__(message)


class AliasMaxDepthError(AliasError):
    """Raised when alias expansion exceeds maximum depth limit.

    This error prevents runaway expansion even when there's no cycle,
    such as very long chains of aliases calling aliases.

    Attributes:
        alias_name: Name of the alias where limit was exceeded
        current_depth: Depth at which limit was exceeded
        max_depth: Maximum allowed depth
        call_chain: List of (alias_name, args) tuples showing the call path
        message: Human-readable error message
    """

    def __init__(
        self,
        alias_name: str,
        current_depth: int,
        max_depth: int,
        call_chain: list[tuple[str, list[Any]]],
        message: str | None = None,
    ):
        """Initialize max depth error.

        Args:
            alias_name: Name of alias where limit exceeded
            current_depth: Current expansion depth
            max_depth: Maximum allowed depth
            call_chain: Full call chain leading to error
            message: Optional custom message
        """
        self.alias_name = alias_name
        self.current_depth = current_depth
        self.max_depth = max_depth
        self.call_chain = call_chain

        if message is None:
            # Format call chain for display
            chain_str = " → ".join(
                f"{name}({', '.join(map(str, args))})" for name, args in call_chain
            )

            message = (
                f"Alias expansion exceeded maximum depth of {max_depth}\n\n"
                f"Call chain ({current_depth} levels): {chain_str} → {alias_name}\n\n"
                f"Suggestion: Simplify alias chain or increase max_depth parameter."
            )

        super().__init__(message)
