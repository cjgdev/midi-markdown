"""Data models for alias expansion tracking.

This module provides data structures for tracking alias expansion state,
including call chains and expansion nodes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExpansionNode:
    """Represents a single node in the alias expansion tree.

    Each node tracks one alias call during expansion, maintaining
    a link to its parent for call chain reconstruction.

    Attributes:
        alias_name: Name of the alias being expanded
        arguments: Arguments passed to this alias call
        depth: Depth in expansion tree (0 = root)
        parent: Parent node in expansion tree (None for root)
        status: Current expansion status
    """

    alias_name: str
    arguments: list[Any]
    depth: int = 0
    parent: ExpansionNode | None = None
    status: str = "pending"  # pending, expanding, complete, error

    def get_call_chain(self) -> list[tuple[str, list[Any]]]:
        """Get the full call chain from root to this node.

        Returns:
            List of (alias_name, arguments) tuples representing the call path.

        Example:
            >>> root = ExpansionNode("alias_a", [1, 2])
            >>> child = ExpansionNode("alias_b", [3], parent=root, depth=1)
            >>> child.get_call_chain()
            [("alias_a", [1, 2]), ("alias_b", [3])]
        """
        chain: list[tuple[str, list[Any]]] = []
        node: ExpansionNode | None = self

        while node is not None:
            chain.insert(0, (node.alias_name, node.arguments))
            node = node.parent

        return chain

    def get_chain_display(self) -> str:
        """Get a human-readable display of the call chain.

        Returns:
            Formatted string showing the call chain with arguments.

        Example:
            >>> node.get_chain_display()
            'alias_a(1, 2) → alias_b(3) → alias_c(4, 5)'
        """
        chain = self.get_call_chain()
        return " → ".join(f"{name}({', '.join(map(str, args))})" for name, args in chain)


@dataclass
class ExpansionContext:
    """Context for tracking alias expansion state.

    Maintains the expansion stack and provides utilities for
    cycle detection and depth limiting.

    Attributes:
        max_depth: Maximum allowed expansion depth
        stack: Stack of currently expanding aliases
        root: Root expansion node (if tracking tree structure)
    """

    max_depth: int = 10
    stack: list[tuple[str, list[Any]]] = field(default_factory=list)
    root: ExpansionNode | None = None

    def push(self, alias_name: str, arguments: list[Any]) -> None:
        """Push alias call onto expansion stack.

        Args:
            alias_name: Name of alias being expanded
            arguments: Arguments to the alias
        """
        self.stack.append((alias_name, arguments))

    def pop(self) -> tuple[str, list[Any]]:
        """Pop alias call from expansion stack.

        Returns:
            Tuple of (alias_name, arguments) that was popped.

        Raises:
            IndexError: If stack is empty
        """
        return self.stack.pop()

    def is_in_stack(self, alias_name: str) -> bool:
        """Check if alias is currently being expanded.

        Args:
            alias_name: Alias name to check

        Returns:
            True if alias is in the expansion stack
        """
        return any(name == alias_name for name, _ in self.stack)

    def current_depth(self) -> int:
        """Get current expansion depth.

        Returns:
            Number of aliases currently in the stack
        """
        return len(self.stack)

    def get_call_chain(self) -> list[tuple[str, list[Any]]]:
        """Get the current call chain.

        Returns:
            Copy of the current stack
        """
        return self.stack.copy()

    def get_chain_display(self) -> str:
        """Get human-readable display of current call chain.

        Returns:
            Formatted string showing the call chain
        """
        return " → ".join(f"{name}({', '.join(map(str, args))})" for name, args in self.stack)
