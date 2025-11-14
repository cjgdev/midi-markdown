"""
Symbol table implementation for MML variables.
Handles variable definition, lookup, and scoping.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Variable:
    """Represents a defined variable."""

    name: str
    value: int | float | str
    var_type: str  # 'int', 'float', 'string'
    source_line: int = 0

    def __repr__(self):
        return f"Variable({self.name}={self.value}, type={self.var_type})"


class SymbolTable:
    """
    Manages variable definitions and lookups with scoping support.

    Features:
    - Define variables with type checking
    - Lookup with parent scope chain
    - Built-in constants (PI, E)
    - Prevent constant redefinition
    """

    # Built-in constants
    CONSTANTS = {
        "PI": 3.14159265359,
        "E": 2.71828182846,
    }

    def __init__(self, parent: SymbolTable | None = None):
        """
        Initialize symbol table.

        Args:
            parent: Parent symbol table for nested scopes
        """
        self.parent = parent
        self.symbols: dict[str, Variable] = {}

    def define(self, name: str, value: Any, var_type: str | None = None, line: int = 0):
        """
        Define a new variable.

        Args:
            name: Variable name (must be uppercase)
            value: Variable value
            var_type: Type hint ('int', 'float', 'string'), auto-detected if None
            line: Source line number for error reporting

        Raises:
            ValueError: If name is a constant or invalid
        """
        # Check if constant
        if name in self.CONSTANTS:
            msg = f"Cannot redefine built-in constant: {name}"
            raise ValueError(msg)

        # Validate name format
        if not name.isupper() or not name.replace("_", "").isalnum():
            msg = (
                f"Invalid variable name '{name}'. "
                "Variables must be uppercase alphanumeric with underscores."
            )
            raise ValueError(msg)

        # Auto-detect type if not provided
        if var_type is None:
            if isinstance(value, int):
                var_type = "int"
            elif isinstance(value, float):
                var_type = "float"
            elif isinstance(value, str):
                var_type = "string"
            else:
                msg = f"Unsupported value type: {type(value)}"
                raise ValueError(msg)

        # Type conversion
        if var_type == "int":
            value = int(value)
        elif var_type == "float":
            value = float(value)
        elif var_type == "string":
            value = str(value)

        self.symbols[name] = Variable(name, value, var_type, line)

    def lookup(self, name: str) -> Variable | None:
        """
        Look up a variable, checking parent scopes.

        Args:
            name: Variable name

        Returns:
            Variable if found, None otherwise
        """
        # Check current scope
        if name in self.symbols:
            return self.symbols[name]

        # Check constants
        if name in self.CONSTANTS:
            return Variable(name, self.CONSTANTS[name], "float", 0)

        # Check parent scope
        if self.parent:
            return self.parent.lookup(name)

        return None

    def resolve(self, name: str) -> Any:
        """
        Resolve variable name to its value.

        Args:
            name: Variable name

        Returns:
            Variable value

        Raises:
            ValueError: If variable is undefined
        """
        var = self.lookup(name)
        if var is None:
            msg = f"Undefined variable: {name}"
            raise ValueError(msg)
        return var.value

    def exists(self, name: str) -> bool:
        """Check if a variable is defined."""
        return self.lookup(name) is not None

    def get_all(self) -> dict[str, Variable]:
        """Get all variables in current scope (not including parent)."""
        return self.symbols.copy()

    def __repr__(self):
        vars_repr = ", ".join(f"{k}={v.value}" for k, v in self.symbols.items())
        return f"SymbolTable({vars_repr})"
