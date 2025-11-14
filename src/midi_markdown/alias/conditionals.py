"""Conditional evaluation for alias branching logic (Stage 7).

This module provides the ConditionalEvaluator class that evaluates conditional
expressions in alias definitions (@if/@elif/@else) and selects the appropriate
branch to execute based on parameter values.
"""

from __future__ import annotations

from typing import Any

from .errors import AliasError


class ConditionalEvaluator:
    """Evaluates conditional expressions in alias definitions.

    The evaluator supports comparison operators (==, !=, <, >, <=, >=) and
    can compare parameter values against literals or other parameters.

    Example:
        >>> evaluator = ConditionalEvaluator()
        >>> condition = {'left': 'device', 'operator': '==', 'right': 'cortex'}
        >>> params = {'device': 'cortex', 'channel': 1}
        >>> evaluator.evaluate_condition(condition, params)
        True
    """

    VALID_OPERATORS = {"==", "!=", "<", ">", "<=", ">="}

    def evaluate_condition(self, condition: dict[str, Any], param_values: dict[str, Any]) -> bool:
        """Evaluate a single condition with current parameter values.

        Args:
            condition: Condition dict with 'left', 'operator', 'right' keys
            param_values: Current bound parameter values

        Returns:
            True if condition evaluates to true, False otherwise

        Raises:
            AliasError: If operator is invalid or parameters are undefined

        Example:
            >>> evaluator.evaluate_condition(
            ...     {'left': 'mode', 'operator': '>', 'right': 0},
            ...     {'mode': 2}
            ... )
            True
        """
        if not isinstance(condition, dict):
            msg = f"Invalid condition format: {condition}"
            raise AliasError(msg)

        if "left" not in condition or "operator" not in condition or "right" not in condition:
            msg = f"Condition missing required keys (left/operator/right): {condition}"
            raise AliasError(msg)

        left = self._resolve_value(condition["left"], param_values)
        right = self._resolve_value(condition["right"], param_values)
        operator = condition["operator"]

        if operator not in self.VALID_OPERATORS:
            msg = (
                f"Invalid comparison operator '{operator}'. "
                f"Valid operators: {', '.join(sorted(self.VALID_OPERATORS))}"
            )
            raise AliasError(msg)

        return self._apply_operator(left, operator, right)

    def _resolve_value(self, value: Any, param_values: dict[str, Any]) -> Any:
        """Resolve parameter references or return literal values.

        If the value is a string that matches a parameter name, return the
        parameter's value. Otherwise, return the literal value.

        Args:
            value: Value to resolve (may be parameter name or literal)
            param_values: Available parameter values

        Returns:
            Resolved value (either from params or the literal value)

        Raises:
            AliasError: If parameter reference is undefined
        """
        # If it's a string that matches a parameter name, look it up
        if isinstance(value, str):
            # Check if it's a parameter reference
            if value in param_values:
                return param_values[value]
            # Otherwise it's a literal string value (e.g., "cortex", "h90")
            return value

        # For non-strings (int, float, bool), return as-is
        return value

    def _apply_operator(self, left: Any, operator: str, right: Any) -> bool:
        """Apply comparison operator to two values.

        Args:
            left: Left operand
            operator: Comparison operator (==, !=, <, >, <=, >=)
            right: Right operand

        Returns:
            Result of comparison

        Raises:
            AliasError: If comparison fails due to type incompatibility
        """
        try:
            if operator == "==":
                return left == right
            if operator == "!=":
                return left != right
            if operator == "<":
                return left < right
            if operator == ">":
                return left > right
            if operator == "<=":
                return left <= right
            if operator == ">=":
                return left >= right
            # Should never reach here due to validation above
            msg = f"Unknown operator: {operator}"
            raise AliasError(msg)

        except TypeError as e:
            msg = f"Type error comparing {left!r} {operator} {right!r}: {e}"
            raise AliasError(msg)

    def select_branch(self, branches: list, param_values: dict[str, Any]) -> list | None:
        """Select the first matching conditional branch.

        Evaluates branches in order (@if, @elif..., @else) and returns
        the commands from the first branch whose condition is true.

        Args:
            branches: List of ConditionalBranch objects
            param_values: Current parameter values

        Returns:
            Commands from first matching branch, or None if no match

        Example:
            >>> from midi_markdown.parser.ast_nodes import ConditionalBranch
            >>> branches = [
            ...     ConditionalBranch(
            ...         condition={'left': 'mode', 'operator': '==', 'right': 0},
            ...         commands=['pc 1.0'],
            ...         branch_type='if'
            ...     ),
            ...     ConditionalBranch(
            ...         condition=None,  # @else branch
            ...         commands=['pc 1.1'],
            ...         branch_type='else'
            ...     )
            ... ]
            >>> evaluator.select_branch(branches, {'mode': 0})
            ['pc 1.0']
        """
        for branch in branches:
            # @else branch (no condition) - always matches
            if branch.condition is None:
                return branch.commands

            # @if or @elif branch - evaluate condition
            try:
                if self.evaluate_condition(branch.condition, param_values):
                    return branch.commands
            except AliasError:
                # If condition evaluation fails, skip this branch
                # (e.g., undefined parameter, type error)
                continue

        # No branch matched
        return None
