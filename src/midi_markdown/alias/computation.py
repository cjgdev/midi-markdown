"""Safe computation engine for evaluating expressions in alias definitions.

This module provides secure evaluation of mathematical expressions in computed
value blocks, with strict security controls to prevent code injection.
"""

from __future__ import annotations

import ast
import operator
import signal
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any

from .errors import ComputationError

if TYPE_CHECKING:
    from collections.abc import Callable


class ComputationTimeoutError(ComputationError):
    """Raised when computation exceeds time limit."""


class SafeComputationEngine:
    """Safely evaluate computation expressions in aliases.

    This engine provides secure evaluation of mathematical expressions with:
    - Whitelisted operations (arithmetic only)
    - Operation counting to prevent runaway computations
    - Execution timeout (1 second max)
    - Read-only input parameters
    - No access to imports, attributes, or dangerous functions

    Example:
        >>> engine = SafeComputationEngine()
        >>> result = engine.evaluate_expression(
        ...     "int((bpm - 40) * 127 / 260)",
        ...     {'bpm': 120}
        ... )
        >>> result
        39
    """

    # Security limits
    MAX_OPERATIONS = 10000
    MAX_EXECUTION_TIME = 1.0  # seconds

    # Whitelisted AST node types for security
    ALLOWED_NODES = {
        ast.Expression,  # Top-level expression wrapper
        ast.BinOp,  # Binary operations (a + b)
        ast.UnaryOp,  # Unary operations (-a, +a)
        ast.Constant,  # Python 3.8+ literal values (numbers, strings, etc.)
        ast.Name,  # Variable references
        ast.Load,  # Load context for variables
        ast.Call,  # Function calls (only whitelisted functions)
        # Operators
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.FloorDiv,
        ast.Mod,
        ast.Pow,
        ast.UAdd,
        ast.USub,
    }

    # Whitelisted function names
    ALLOWED_FUNCTIONS = {
        "int",
        "float",
        "abs",
        "round",
        "min",
        "max",
        "clamp",
        "scale_range",
        "msb",
        "lsb",
    }

    def __init__(self):
        """Initialize the computation engine."""
        self.operation_count = 0
        self.midi_functions = self._create_midi_functions()

        # Binary operators mapping
        self.binary_ops = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.FloorDiv: operator.floordiv,
            ast.Mod: operator.mod,
            ast.Pow: operator.pow,
        }

        # Unary operators mapping
        self.unary_ops = {
            ast.UAdd: operator.pos,
            ast.USub: operator.neg,
        }

    def lark_tree_to_python(self, expr: Any) -> str:
        """Convert Lark expression tree to Python expression string.

        Args:
            expr: Lark Tree or tuple representing an expression

        Returns:
            Python expression string

        Example:
            >>> # Lark tree for: (${val} + 10) * 2
            >>> # converts to: (val + 10) * 2
        """
        # Handle tuples (operators with operands)
        if isinstance(expr, tuple):
            op_name = expr[0]

            # Binary operators
            if op_name in ("add", "sub", "mul", "div", "mod"):
                op_map = {
                    "add": "+",
                    "sub": "-",
                    "mul": "*",
                    "div": "/",
                    "mod": "%",
                }
                left = self.lark_tree_to_python(expr[1])
                right = self.lark_tree_to_python(expr[2])
                return f"{left} {op_map[op_name]} {right}"

            # Unary minus
            if op_name == "neg":
                operand = self.lark_tree_to_python(expr[1])
                return f"-{operand}"

            # Variable reference
            if op_name == "var":
                return str(expr[1])

            # Function call
            if op_name == "func_call":
                func_name = expr[1]
                args = expr[2] if len(expr) > 2 else []
                arg_strs = [self.lark_tree_to_python(arg) for arg in args]
                return f"{func_name}({', '.join(arg_strs)})"

        # Handle Lark Tree objects
        elif hasattr(expr, "data"):
            tree_type = expr.data

            if tree_type == "paren":
                # Parenthesized expression
                inner = self.lark_tree_to_python(expr.children[0])
                return f"({inner})"

            if tree_type == "var_ref":
                # Variable reference: ${var}
                if expr.children:
                    return self.lark_tree_to_python(expr.children[0])
                return ""

            if tree_type in ("add", "sub", "mul", "div", "mod"):
                # Binary operation stored as Tree
                if len(expr.children) >= 2:
                    op_map = {
                        "add": "+",
                        "sub": "-",
                        "mul": "*",
                        "div": "/",
                        "mod": "%",
                    }
                    left = self.lark_tree_to_python(expr.children[0])
                    right = self.lark_tree_to_python(expr.children[1])
                    return f"{left} {op_map[tree_type]} {right}"

            elif tree_type == "neg":
                # Unary negation
                if expr.children:
                    operand = self.lark_tree_to_python(expr.children[0])
                    return f"-{operand}"

            elif tree_type in ("number", "integer"):
                # Numeric literal
                if expr.children:
                    return str(expr.children[0])

            elif tree_type == "func_call":
                # Function call stored as Tree
                if expr.children and len(expr.children) >= 1:
                    # First child is typically a tuple or token for the function
                    # Extract function details from children
                    # The Lark tree structure is: Tree('func_call', [('func_call', 'fname', [args])])
                    # or could be simpler depending on grammar
                    func_info = expr.children[0]
                    if isinstance(func_info, tuple) and func_info[0] == "func_call":
                        func_name = func_info[1]
                        args = func_info[2] if len(func_info) > 2 else []
                        arg_strs = [self.lark_tree_to_python(arg) for arg in args]
                        return f"{func_name}({', '.join(arg_strs)})"

        # Handle raw numbers/strings
        elif isinstance(expr, int | float):
            return str(expr)
        elif isinstance(expr, str):
            return expr

        # Unknown type
        msg = f"Cannot convert Lark expression to Python: {type(expr)} {expr}"
        raise ComputationError(msg)

    def evaluate_expression(self, expr_str: str, input_params: dict[str, Any]) -> Any:
        """Evaluate a single expression safely.

        Args:
            expr_str: Python expression string (e.g., "(bpm - 40) * 127 / 260")
            input_params: Input parameters (read-only)

        Returns:
            Evaluated result

        Raises:
            ComputationError: If evaluation fails or security check fails
            ComputationTimeoutError: If execution exceeds time limit

        Example:
            >>> engine.evaluate_expression("(120 - 40) * 127 / 260", {})
            39.0
        """
        # Reset operation counter
        self.operation_count = 0

        # Parse expression to AST
        try:
            tree = ast.parse(expr_str, mode="eval")
        except SyntaxError as e:
            msg = f"Syntax error in expression '{expr_str}': {e}"
            raise ComputationError(msg)

        # Validate AST for security
        self._validate_ast(tree)

        # Create namespace (read-only params + MIDI functions + builtins)
        namespace = {
            **input_params,
            **self.midi_functions,
            "int": int,
            "float": float,
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
        }

        # Evaluate with timeout
        try:
            with self._timeout(self.MAX_EXECUTION_TIME):
                return self._eval_node(tree.body, namespace)
        except ComputationTimeoutError:
            raise
        except ZeroDivisionError:
            msg = f"Division by zero in expression: {expr_str}"
            raise ComputationError(msg)
        except KeyError as e:
            available_vars = ", ".join(sorted(namespace.keys()))
            msg = (
                f"Undefined variable {e} in expression: {expr_str}\n"
                f"Available variables: {available_vars}"
            )
            raise ComputationError(msg)
        except Exception as e:
            msg = f"Error evaluating expression '{expr_str}': {e}"
            raise ComputationError(msg)

    def _validate_ast(self, tree: ast.AST) -> None:
        """Validate AST contains only safe operations.

        Args:
            tree: AST tree to validate

        Raises:
            ComputationError: If forbidden operation detected
        """
        for node in ast.walk(tree):
            node_type = type(node)

            # Check if node type is allowed
            if node_type not in self.ALLOWED_NODES:
                msg = (
                    f"Forbidden operation: {node_type.__name__}. "
                    f"Only basic arithmetic operations are allowed."
                )
                raise ComputationError(msg)

            # Special check for function calls - only whitelisted functions
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    if func_name not in self.ALLOWED_FUNCTIONS:
                        msg = (
                            f"Function '{func_name}' is not allowed. "
                            f"Allowed functions: {', '.join(sorted(self.ALLOWED_FUNCTIONS))}"
                        )
                        raise ComputationError(msg)
                else:
                    # Function call that's not a simple name (e.g., obj.method())
                    msg = "Only simple function calls are allowed (no attribute access)"
                    raise ComputationError(msg)

            # Block attribute access (prevents obj.__class__, etc.)
            if isinstance(node, ast.Attribute):
                msg = "Attribute access is not allowed for security reasons"
                raise ComputationError(msg)

            # Block imports
            if isinstance(node, ast.Import | ast.ImportFrom):
                msg = "Import statements are not allowed"
                raise ComputationError(msg)

    def _eval_node(self, node: ast.AST, namespace: dict[str, Any]) -> Any:
        """Evaluate AST node recursively.

        Args:
            node: AST node to evaluate
            namespace: Variable namespace

        Returns:
            Evaluated result

        Raises:
            ComputationError: If operation limit exceeded
        """
        # Increment operation counter
        self.operation_count += 1
        if self.operation_count > self.MAX_OPERATIONS:
            msg = (
                f"Operation limit exceeded ({self.MAX_OPERATIONS} operations). "
                f"Expression is too complex."
            )
            raise ComputationError(msg)

        # Handle different node types
        if isinstance(node, ast.Constant):  # Python 3.8+ literal values
            return node.value
        if isinstance(node, ast.Name):
            # Variable reference
            if node.id not in namespace:
                raise KeyError(node.id)
            return namespace[node.id]
        if isinstance(node, ast.BinOp):
            # Binary operation
            left = self._eval_node(node.left, namespace)
            right = self._eval_node(node.right, namespace)
            op_func = self.binary_ops.get(type(node.op))
            if op_func is None:
                msg = f"Unsupported operator: {type(node.op).__name__}"
                raise ComputationError(msg)
            return op_func(left, right)
        if isinstance(node, ast.UnaryOp):
            # Unary operation
            operand = self._eval_node(node.operand, namespace)
            op_func = self.unary_ops.get(type(node.op))
            if op_func is None:
                msg = f"Unsupported operator: {type(node.op).__name__}"
                raise ComputationError(msg)
            return op_func(operand)
        if isinstance(node, ast.Call):
            # Function call
            func_name = node.func.id
            func = namespace.get(func_name)
            if func is None:
                msg = f"Unknown function: {func_name}"
                raise ComputationError(msg)

            # Evaluate arguments
            args = [self._eval_node(arg, namespace) for arg in node.args]

            # Call function
            try:
                return func(*args)
            except TypeError as e:
                msg = f"Error calling {func_name}: {e}"
                raise ComputationError(msg)
        else:
            msg = f"Unsupported AST node type: {type(node).__name__}"
            raise ComputationError(msg)

    def _create_midi_functions(self) -> dict[str, Callable]:
        """Create MIDI helper functions.

        Returns:
            Dictionary of function name -> function
        """

        def clamp(value: float, min_val: float, max_val: float) -> float:
            """Constrain value to range [min_val, max_val]."""
            return max(min_val, min(max_val, value))

        def scale_range(
            value: float, in_min: float, in_max: float, out_min: float, out_max: float
        ) -> float:
            """Scale value from input range to output range (linear)."""
            # Avoid division by zero
            if in_max == in_min:
                return out_min

            # Linear interpolation
            normalized = (value - in_min) / (in_max - in_min)
            return out_min + normalized * (out_max - out_min)

        def msb(value: int) -> int:
            """Get most significant byte (7-bit) for 14-bit MIDI values."""
            return (value >> 7) & 0x7F

        def lsb(value: int) -> int:
            """Get least significant byte (7-bit) for 14-bit MIDI values."""
            return value & 0x7F

        return {
            "clamp": clamp,
            "scale_range": scale_range,
            "msb": msb,
            "lsb": lsb,
        }

    @contextmanager
    def _timeout(self, seconds: float):
        """Context manager for execution timeout.

        Args:
            seconds: Timeout in seconds

        Raises:
            ComputationTimeoutError: If execution exceeds timeout

        Note:
            Uses signal.alarm() on Unix, which has limitations:
            - Only works on Unix/Linux/Mac (not Windows)
            - Only one alarm can be active at a time
            On Windows, timeout is not enforced (limitation accepted for now)
        """

        def timeout_handler(signum, frame):
            msg = f"Computation exceeded time limit of {seconds} seconds"
            raise ComputationTimeoutError(msg)

        # Check if signal.alarm is available (Unix-like systems)
        if hasattr(signal, "alarm"):
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(int(seconds + 0.5))  # Round up
            try:
                yield
            finally:
                signal.alarm(0)  # Cancel alarm
                signal.signal(signal.SIGALRM, old_handler)
        else:
            # Windows or other platforms without signal.alarm
            # Timeout not enforced (limitation accepted)
            yield
