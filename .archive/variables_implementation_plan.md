# MML Compiler Enhancement: Phased Implementation Plan
## Adding Variables, Loops, and Sweeps

---

## Project Structure

```
mml_compiler/
├── src/
│   ├── __init__.py
│   ├── parser.py           # Main parser (existing)
│   ├── grammar/
│   │   └── mml.lark        # Lark grammar (existing)
│   ├── ast_nodes.py        # AST node definitions (existing)
│   ├── timing.py           # Timing utilities (existing)
│   ├── midi_generator.py   # MIDI file generator (existing)
│   │
│   ├── symbols.py          # NEW: Symbol table (Phase 1)
│   ├── expressions.py      # NEW: Expression evaluator (Phase 2)
│   ├── loops.py            # NEW: Loop expansion (Phase 3)
│   ├── sweeps.py           # NEW: Sweep expansion (Phase 4)
│   └── expander.py         # NEW: Command expander (Phase 3-4)
│
├── tests/
│   ├── test_symbols.py     # Phase 1 tests
│   ├── test_expressions.py # Phase 2 tests
│   ├── test_loops.py       # Phase 3 tests
│   ├── test_sweeps.py      # Phase 4 tests
│   ├── test_integration.py # Phase 5 tests
│   └── fixtures/           # Test MML files
│
├── examples/
│   ├── variables.mml
│   ├── loops.mml
│   ├── sweeps.mml
│   └── complete.mml
│
└── requirements.txt
```

---

## Phase 1: Variables and Symbol Table

### Goals
- Add `@define` directive support
- Create symbol table for variable storage
- Enable variable lookups
- Support basic integer and float types
- NO expression evaluation yet (just literal values)

### Deliverables

#### File: `src/symbols.py`

```python
"""
Symbol table implementation for MML variables.
Handles variable definition, lookup, and scoping.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional, Union


@dataclass
class Variable:
    """Represents a defined variable."""
    name: str
    value: Union[int, float, str]
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
        'PI': 3.14159265359,
        'E': 2.71828182846,
    }
    
    def __init__(self, parent: Optional['SymbolTable'] = None):
        """
        Initialize symbol table.
        
        Args:
            parent: Parent symbol table for nested scopes
        """
        self.parent = parent
        self.symbols: Dict[str, Variable] = {}
    
    def define(self, name: str, value: Any, var_type: str = None, line: int = 0):
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
            raise ValueError(f"Cannot redefine built-in constant: {name}")
        
        # Validate name format
        if not name.isupper() or not name.replace('_', '').isalnum():
            raise ValueError(
                f"Invalid variable name '{name}'. "
                "Variables must be uppercase alphanumeric with underscores."
            )
        
        # Auto-detect type if not provided
        if var_type is None:
            if isinstance(value, int):
                var_type = 'int'
            elif isinstance(value, float):
                var_type = 'float'
            elif isinstance(value, str):
                var_type = 'string'
            else:
                raise ValueError(f"Unsupported value type: {type(value)}")
        
        # Type conversion
        if var_type == 'int':
            value = int(value)
        elif var_type == 'float':
            value = float(value)
        elif var_type == 'string':
            value = str(value)
        
        self.symbols[name] = Variable(name, value, var_type, line)
    
    def lookup(self, name: str) -> Optional[Variable]:
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
            return Variable(name, self.CONSTANTS[name], 'float', 0)
        
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
            raise ValueError(f"Undefined variable: {name}")
        return var.value
    
    def exists(self, name: str) -> bool:
        """Check if a variable is defined."""
        return self.lookup(name) is not None
    
    def get_all(self) -> Dict[str, Variable]:
        """Get all variables in current scope (not including parent)."""
        return self.symbols.copy()
    
    def __repr__(self):
        vars_repr = ', '.join(f"{k}={v.value}" for k, v in self.symbols.items())
        return f"SymbolTable({vars_repr})"
```

#### File: `tests/test_symbols.py`

```python
"""
Unit tests for symbol table implementation.
"""

import pytest
from src.symbols import SymbolTable, Variable


class TestSymbolTable:
    """Test SymbolTable class."""
    
    def test_define_integer(self):
        """Test defining an integer variable."""
        table = SymbolTable()
        table.define('MY_VAR', 42)
        
        var = table.lookup('MY_VAR')
        assert var is not None
        assert var.value == 42
        assert var.var_type == 'int'
    
    def test_define_float(self):
        """Test defining a float variable."""
        table = SymbolTable()
        table.define('TEMPO', 120.5)
        
        var = table.lookup('TEMPO')
        assert var is not None
        assert var.value == 120.5
        assert var.var_type == 'float'
    
    def test_define_string(self):
        """Test defining a string variable."""
        table = SymbolTable()
        table.define('NAME', 'Test Song')
        
        var = table.lookup('NAME')
        assert var is not None
        assert var.value == 'Test Song'
        assert var.var_type == 'string'
    
    def test_define_with_explicit_type(self):
        """Test defining variable with explicit type conversion."""
        table = SymbolTable()
        table.define('VALUE', '42', var_type='int')
        
        var = table.lookup('VALUE')
        assert var is not None
        assert var.value == 42
        assert var.var_type == 'int'
        assert isinstance(var.value, int)
    
    def test_resolve_variable(self):
        """Test resolving variable to value."""
        table = SymbolTable()
        table.define('PRESET', 5)
        
        value = table.resolve('PRESET')
        assert value == 5
    
    def test_undefined_variable_raises(self):
        """Test that resolving undefined variable raises error."""
        table = SymbolTable()
        
        with pytest.raises(ValueError, match="Undefined variable: UNKNOWN"):
            table.resolve('UNKNOWN')
    
    def test_constant_pi(self):
        """Test built-in PI constant."""
        table = SymbolTable()
        
        pi = table.resolve('PI')
        assert abs(pi - 3.14159) < 0.0001
    
    def test_constant_e(self):
        """Test built-in E constant."""
        table = SymbolTable()
        
        e = table.resolve('E')
        assert abs(e - 2.71828) < 0.0001
    
    def test_cannot_redefine_constant(self):
        """Test that constants cannot be redefined."""
        table = SymbolTable()
        
        with pytest.raises(ValueError, match="Cannot redefine built-in constant: PI"):
            table.define('PI', 3.14)
    
    def test_invalid_variable_name(self):
        """Test that invalid variable names are rejected."""
        table = SymbolTable()
        
        # Lowercase not allowed
        with pytest.raises(ValueError, match="Invalid variable name"):
            table.define('lowercase', 42)
        
        # Mixed case not allowed
        with pytest.raises(ValueError, match="Invalid variable name"):
            table.define('MixedCase', 42)
    
    def test_valid_variable_names(self):
        """Test valid variable name patterns."""
        table = SymbolTable()
        
        # These should all work
        table.define('VAR', 1)
        table.define('MY_VAR', 2)
        table.define('VAR_2', 3)
        table.define('MAIN_PRESET_123', 4)
        
        assert table.resolve('VAR') == 1
        assert table.resolve('MY_VAR') == 2
        assert table.resolve('VAR_2') == 3
        assert table.resolve('MAIN_PRESET_123') == 4
    
    def test_exists_method(self):
        """Test exists() method."""
        table = SymbolTable()
        table.define('VAR', 42)
        
        assert table.exists('VAR')
        assert not table.exists('UNKNOWN')
        assert table.exists('PI')  # Constants also exist
    
    def test_parent_scope_lookup(self):
        """Test variable lookup in parent scope."""
        parent = SymbolTable()
        parent.define('GLOBAL_VAR', 100)
        
        child = SymbolTable(parent=parent)
        child.define('LOCAL_VAR', 200)
        
        # Child can see both
        assert child.resolve('LOCAL_VAR') == 200
        assert child.resolve('GLOBAL_VAR') == 100
        
        # Parent cannot see child
        assert parent.resolve('GLOBAL_VAR') == 100
        with pytest.raises(ValueError):
            parent.resolve('LOCAL_VAR')
    
    def test_child_shadows_parent(self):
        """Test that child scope can shadow parent variables."""
        parent = SymbolTable()
        parent.define('VAR', 100)
        
        child = SymbolTable(parent=parent)
        child.define('VAR', 200)
        
        # Child sees its own value
        assert child.resolve('VAR') == 200
        
        # Parent unchanged
        assert parent.resolve('VAR') == 100
    
    def test_get_all(self):
        """Test get_all() returns only current scope."""
        parent = SymbolTable()
        parent.define('PARENT_VAR', 100)
        
        child = SymbolTable(parent=parent)
        child.define('CHILD_VAR', 200)
        
        child_vars = child.get_all()
        assert 'CHILD_VAR' in child_vars
        assert 'PARENT_VAR' not in child_vars  # Parent not included
    
    def test_variable_repr(self):
        """Test Variable string representation."""
        var = Variable('TEST', 42, 'int', 10)
        repr_str = repr(var)
        
        assert 'TEST' in repr_str
        assert '42' in repr_str
        assert 'int' in repr_str


class TestVariableClass:
    """Test Variable dataclass."""
    
    def test_create_variable(self):
        """Test creating a Variable instance."""
        var = Variable('MY_VAR', 42, 'int', 10)
        
        assert var.name == 'MY_VAR'
        assert var.value == 42
        assert var.var_type == 'int'
        assert var.source_line == 10
    
    def test_variable_equality(self):
        """Test variable equality."""
        var1 = Variable('VAR', 42, 'int', 10)
        var2 = Variable('VAR', 42, 'int', 10)
        
        assert var1 == var2
```

#### Grammar Extension (Lark)

**Instructions for Claude Code Agent:**

Add to `src/grammar/mml.lark`:

```lark
// Variable definition directive
define_stmt: "@define" VARIABLE_NAME value

// Variable reference (simple, no expressions yet)
variable_ref: "${" VARIABLE_NAME "}"

// Variable name token
VARIABLE_NAME: /[A-Z][A-Z0-9_]*/

// Value types
value: NUMBER | FLOAT | STRING

// Update command parameters to accept variable references
// Example: command parameters can now be: "1" or "${MY_VAR}"
parameter: NUMBER | variable_ref | STRING
```

#### Integration Point: `src/parser.py`

**Instructions for Claude Code Agent:**

Modify existing parser to:
1. Instantiate `SymbolTable` at parse start
2. Process `@define` statements and populate symbol table
3. Replace variable references with values during command parsing
4. Pass symbol table to downstream components

```python
# Add to parser.py
from src.symbols import SymbolTable

class MMLParser:
    def __init__(self):
        # ... existing code ...
        self.symbol_table = SymbolTable()
    
    def process_define(self, tree):
        """Process @define directive."""
        var_name = str(tree.children[0])
        value = self.extract_value(tree.children[1])
        
        self.symbol_table.define(var_name, value, line=tree.meta.line)
    
    def resolve_parameter(self, param_tree):
        """Resolve parameter, handling variable references."""
        if param_tree.data == 'variable_ref':
            var_name = str(param_tree.children[0])
            return self.symbol_table.resolve(var_name)
        else:
            return self.extract_value(param_tree)
```

### Test Files

Create `tests/fixtures/variables_basic.mml`:

```markdown
@define MAIN_CHANNEL 1
@define VERSE_PRESET 10
@define CHORUS_PRESET 15

[00:00.000]
- pc ${MAIN_CHANNEL}.${VERSE_PRESET}

[00:10.000]
- pc ${MAIN_CHANNEL}.${CHORUS_PRESET}
```

### Acceptance Criteria

- [ ] `SymbolTable` class implemented with all methods
- [ ] All unit tests pass (>95% coverage)
- [ ] Grammar accepts `@define` statements
- [ ] Grammar accepts `${VAR_NAME}` references
- [ ] Parser populates symbol table from `@define`
- [ ] Parser substitutes variable values in commands
- [ ] Example file `variables_basic.mml` compiles successfully
- [ ] Error messages include line numbers for undefined variables
- [ ] Documentation updated with variable syntax

---

## Phase 2: Expression Evaluation

### Goals
- Add mathematical expression support in `${...}`
- Support operators: `+`, `-`, `*`, `/`, `%`, `(`, `)`
- Enable computed variable definitions
- Maintain safety (no arbitrary code execution)

### Deliverables

#### File: `src/expressions.py`

```python
"""
Safe expression evaluator for MML variables.
Supports mathematical expressions with variables.
"""

import ast
import operator
from typing import Union
from src.symbols import SymbolTable


class ExpressionError(Exception):
    """Exception raised for expression evaluation errors."""
    pass


class ExpressionEvaluator:
    """
    Safely evaluates mathematical expressions with variables.
    
    Supported:
    - Arithmetic: +, -, *, /, %, **
    - Parentheses for grouping
    - Variable references
    - Integer and float literals
    
    NOT supported (security):
    - Function calls
    - Attribute access
    - List/dict literals
    - String operations
    """
    
    # Allowed AST node types for security
    ALLOWED_OPS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }
    
    def __init__(self, symbol_table: SymbolTable):
        """
        Initialize evaluator with symbol table.
        
        Args:
            symbol_table: Symbol table for variable lookup
        """
        self.symbol_table = symbol_table
    
    def evaluate(self, expr: str) -> Union[int, float]:
        """
        Evaluate a mathematical expression.
        
        Args:
            expr: Expression string, with or without ${ } wrapper
            
        Returns:
            Evaluated result as int or float
            
        Raises:
            ExpressionError: If expression is invalid or unsafe
            
        Examples:
            >>> eval.evaluate("10 + 5")
            15
            >>> eval.evaluate("${MY_VAR * 2}")
            20  # if MY_VAR = 10
        """
        # Remove ${ } wrapper if present
        expr = expr.strip()
        if expr.startswith('${') and expr.endswith('}'):
            expr = expr[2:-1].strip()
        
        # Replace variable references with values
        expr = self._substitute_variables(expr)
        
        # Parse and evaluate safely
        try:
            tree = ast.parse(expr, mode='eval')
            result = self._eval_node(tree.body)
            
            # Return int if possible, else float
            if isinstance(result, float) and result.is_integer():
                return int(result)
            return result
            
        except (SyntaxError, ValueError, KeyError) as e:
            raise ExpressionError(f"Invalid expression '{expr}': {e}")
    
    def _substitute_variables(self, expr: str) -> str:
        """
        Replace variable names with their values.
        
        Args:
            expr: Expression with variable names
            
        Returns:
            Expression with values substituted
        """
        import re
        
        # Match variable names (uppercase with underscores)
        var_pattern = r'\b([A-Z][A-Z0-9_]*)\b'
        
        def replace_var(match):
            var_name = match.group(1)
            try:
                value = self.symbol_table.resolve(var_name)
                return str(value)
            except ValueError:
                # Re-raise with original expression context
                raise ExpressionError(f"Undefined variable '{var_name}' in expression")
        
        return re.sub(var_pattern, replace_var, expr)
    
    def _eval_node(self, node: ast.AST) -> Union[int, float]:
        """
        Recursively evaluate an AST node.
        
        Args:
            node: AST node to evaluate
            
        Returns:
            Evaluated value
            
        Raises:
            ExpressionError: If node type is not allowed
        """
        # Literal number
        if isinstance(node, ast.Num):
            return node.n
        
        # Python 3.8+ uses ast.Constant for literals
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ExpressionError(f"Unsupported constant type: {type(node.value)}")
        
        # Binary operation (e.g., a + b)
        if isinstance(node, ast.BinOp):
            if type(node.op) not in self.ALLOWED_OPS:
                raise ExpressionError(f"Unsupported operation: {type(node.op).__name__}")
            
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            op_func = self.ALLOWED_OPS[type(node.op)]
            
            try:
                return op_func(left, right)
            except ZeroDivisionError:
                raise ExpressionError("Division by zero")
        
        # Unary operation (e.g., -a)
        if isinstance(node, ast.UnaryOp):
            if type(node.op) not in self.ALLOWED_OPS:
                raise ExpressionError(f"Unsupported operation: {type(node.op).__name__}")
            
            operand = self._eval_node(node.operand)
            op_func = self.ALLOWED_OPS[type(node.op)]
            return op_func(operand)
        
        # Anything else is not allowed
        raise ExpressionError(f"Unsupported expression type: {type(node).__name__}")


def evaluate_expression(expr: str, symbol_table: SymbolTable) -> Union[int, float]:
    """
    Convenience function to evaluate an expression.
    
    Args:
        expr: Expression to evaluate
        symbol_table: Symbol table for variable lookup
        
    Returns:
        Evaluated result
    """
    evaluator = ExpressionEvaluator(symbol_table)
    return evaluator.evaluate(expr)
```

#### File: `tests/test_expressions.py`

```python
"""
Unit tests for expression evaluator.
"""

import pytest
from src.expressions import ExpressionEvaluator, ExpressionError, evaluate_expression
from src.symbols import SymbolTable


class TestExpressionEvaluator:
    """Test ExpressionEvaluator class."""
    
    @pytest.fixture
    def symbol_table(self):
        """Create a symbol table with test variables."""
        table = SymbolTable()
        table.define('A', 10)
        table.define('B', 5)
        table.define('C', 2)
        table.define('TEMPO', 120)
        return table
    
    @pytest.fixture
    def evaluator(self, symbol_table):
        """Create an evaluator with test symbol table."""
        return ExpressionEvaluator(symbol_table)
    
    # Basic arithmetic
    
    def test_addition(self, evaluator):
        """Test addition."""
        assert evaluator.evaluate("10 + 5") == 15
        assert evaluator.evaluate("1 + 2 + 3") == 6
    
    def test_subtraction(self, evaluator):
        """Test subtraction."""
        assert evaluator.evaluate("10 - 5") == 5
        assert evaluator.evaluate("20 - 5 - 3") == 12
    
    def test_multiplication(self, evaluator):
        """Test multiplication."""
        assert evaluator.evaluate("10 * 5") == 50
        assert evaluator.evaluate("2 * 3 * 4") == 24
    
    def test_division(self, evaluator):
        """Test division."""
        assert evaluator.evaluate("10 / 2") == 5
        assert evaluator.evaluate("15 / 3") == 5
        assert evaluator.evaluate("10 / 4") == 2.5
    
    def test_floor_division(self, evaluator):
        """Test floor division."""
        assert evaluator.evaluate("10 // 3") == 3
        assert evaluator.evaluate("15 // 4") == 3
    
    def test_modulo(self, evaluator):
        """Test modulo."""
        assert evaluator.evaluate("10 % 3") == 1
        assert evaluator.evaluate("15 % 4") == 3
    
    def test_power(self, evaluator):
        """Test exponentiation."""
        assert evaluator.evaluate("2 ** 3") == 8
        assert evaluator.evaluate("10 ** 2") == 100
    
    # Operator precedence
    
    def test_precedence_mult_add(self, evaluator):
        """Test multiplication before addition."""
        assert evaluator.evaluate("2 + 3 * 4") == 14
        assert evaluator.evaluate("3 * 4 + 2") == 14
    
    def test_precedence_div_sub(self, evaluator):
        """Test division before subtraction."""
        assert evaluator.evaluate("10 - 8 / 4") == 8
        assert evaluator.evaluate("8 / 4 - 1") == 1
    
    def test_precedence_power(self, evaluator):
        """Test power has highest precedence."""
        assert evaluator.evaluate("2 ** 3 * 4") == 32
        assert evaluator.evaluate("2 * 3 ** 2") == 18
    
    # Parentheses
    
    def test_parentheses_override_precedence(self, evaluator):
        """Test parentheses override normal precedence."""
        assert evaluator.evaluate("(2 + 3) * 4") == 20
        assert evaluator.evaluate("2 * (3 + 4)") == 14
    
    def test_nested_parentheses(self, evaluator):
        """Test nested parentheses."""
        assert evaluator.evaluate("((2 + 3) * 4) - 5") == 15
        assert evaluator.evaluate("2 * ((3 + 4) / 7)") == 2
    
    # Unary operators
    
    def test_unary_minus(self, evaluator):
        """Test unary minus."""
        assert evaluator.evaluate("-5") == -5
        assert evaluator.evaluate("10 + -5") == 5
        assert evaluator.evaluate("-(-5)") == 5
    
    def test_unary_plus(self, evaluator):
        """Test unary plus."""
        assert evaluator.evaluate("+5") == 5
        assert evaluator.evaluate("10 + +5") == 15
    
    # Variables
    
    def test_variable_simple(self, evaluator):
        """Test simple variable reference."""
        assert evaluator.evaluate("A") == 10
        assert evaluator.evaluate("B") == 5
    
    def test_variable_in_expression(self, evaluator):
        """Test variable in arithmetic expression."""
        assert evaluator.evaluate("A + B") == 15
        assert evaluator.evaluate("A * C") == 20
        assert evaluator.evaluate("TEMPO / 2") == 60
    
    def test_variable_complex_expression(self, evaluator):
        """Test variables in complex expression."""
        assert evaluator.evaluate("A + B * C") == 20
        assert evaluator.evaluate("(A + B) * C") == 30
        assert evaluator.evaluate("A * B - C") == 48
    
    def test_all_variables(self, evaluator):
        """Test expression with only variables."""
        assert evaluator.evaluate("A + B + C") == 17
    
    def test_undefined_variable(self, evaluator):
        """Test undefined variable raises error."""
        with pytest.raises(ExpressionError, match="Undefined variable 'UNKNOWN'"):
            evaluator.evaluate("UNKNOWN + 5")
    
    # Expression wrapper
    
    def test_with_wrapper(self, evaluator):
        """Test expression with ${ } wrapper."""
        assert evaluator.evaluate("${10 + 5}") == 15
        assert evaluator.evaluate("${A + B}") == 15
    
    def test_wrapper_whitespace(self, evaluator):
        """Test wrapper with whitespace."""
        assert evaluator.evaluate("${ 10 + 5 }") == 15
        assert evaluator.evaluate("${  A + B  }") == 15
    
    # Float handling
    
    def test_float_result(self, evaluator):
        """Test expressions returning floats."""
        result = evaluator.evaluate("10 / 3")
        assert isinstance(result, float)
        assert abs(result - 3.333) < 0.001
    
    def test_integer_result_from_float(self, evaluator):
        """Test that whole number floats return as int."""
        result = evaluator.evaluate("10.0 / 2.0")
        assert isinstance(result, int)
        assert result == 5
    
    # Constants
    
    def test_pi_constant(self, evaluator):
        """Test PI constant in expression."""
        result = evaluator.evaluate("PI * 2")
        assert abs(result - 6.283) < 0.001
    
    def test_e_constant(self, evaluator):
        """Test E constant in expression."""
        result = evaluator.evaluate("E * 2")
        assert abs(result - 5.436) < 0.001
    
    # Error cases
    
    def test_division_by_zero(self, evaluator):
        """Test division by zero raises error."""
        with pytest.raises(ExpressionError, match="Division by zero"):
            evaluator.evaluate("10 / 0")
    
    def test_invalid_syntax(self, evaluator):
        """Test invalid syntax raises error."""
        with pytest.raises(ExpressionError):
            evaluator.evaluate("10 +")
        
        with pytest.raises(ExpressionError):
            evaluator.evaluate("* 10")
    
    def test_unsupported_operation(self, evaluator):
        """Test that unsupported operations are rejected."""
        # Function calls not allowed
        with pytest.raises(ExpressionError):
            evaluator.evaluate("abs(-5)")
        
        # String literals not allowed
        with pytest.raises(ExpressionError):
            evaluator.evaluate("'hello'")
    
    # Complex real-world examples
    
    def test_tempo_calculation(self, evaluator):
        """Test realistic tempo calculation."""
        # Double tempo
        assert evaluator.evaluate("TEMPO * 2") == 240
        
        # Half tempo
        assert evaluator.evaluate("TEMPO / 2") == 60
        
        # Increase by 10%
        assert evaluator.evaluate("TEMPO + TEMPO / 10") == 132
    
    def test_preset_calculation(self):
        """Test realistic preset calculations."""
        table = SymbolTable()
        table.define('BASE_PRESET', 10)
        table.define('OFFSET', 5)
        
        evaluator = ExpressionEvaluator(table)
        
        # Next preset
        assert evaluator.evaluate("BASE_PRESET + 1") == 11
        
        # Offset preset
        assert evaluator.evaluate("BASE_PRESET + OFFSET") == 15
        
        # Scene calculation
        assert evaluator.evaluate("BASE_PRESET * 8 + OFFSET") == 85


class TestConvenienceFunction:
    """Test the evaluate_expression convenience function."""
    
    def test_evaluate_expression(self):
        """Test convenience function."""
        table = SymbolTable()
        table.define('X', 10)
        
        result = evaluate_expression("X * 2", table)
        assert result == 20
```

#### Integration with Parser

**Instructions for Claude Code Agent:**

Modify `src/parser.py` to:
1. Detect expressions (strings containing operators or multiple variables)
2. Use `ExpressionEvaluator` for `@define` with expressions
3. Use `ExpressionEvaluator` for command parameters with expressions

```python
# Add to parser.py
from src.expressions import ExpressionEvaluator

class MMLParser:
    def __init__(self):
        # ... existing code ...
        self.symbol_table = SymbolTable()
        self.evaluator = ExpressionEvaluator(self.symbol_table)
    
    def process_define(self, tree):
        """Process @define with expression support."""
        var_name = str(tree.children[0])
        value_node = tree.children[1]
        
        # Check if value is an expression
        value_str = self.node_to_string(value_node)
        if self._is_expression(value_str):
            value = self.evaluator.evaluate(value_str)
        else:
            value = self.extract_value(value_node)
        
        self.symbol_table.define(var_name, value, line=tree.meta.line)
    
    def _is_expression(self, value_str: str) -> bool:
        """Check if string is an expression."""
        operators = ['+', '-', '*', '/', '%', '(', ')']
        return any(op in value_str for op in operators)
    
    def resolve_parameter(self, param_tree):
        """Resolve parameter with expression support."""
        param_str = self.node_to_string(param_tree)
        
        if '${' in param_str or self._is_expression(param_str):
            return self.evaluator.evaluate(param_str)
        else:
            return self.extract_value(param_tree)
```

### Test Files

Create `tests/fixtures/expressions.mml`:

```markdown
@define BASE_TEMPO 120
@define TEMPO_OFFSET 10
@define FAST_TEMPO ${BASE_TEMPO + TEMPO_OFFSET}
@define SLOW_TEMPO ${BASE_TEMPO - 20}

@define BASE_PRESET 10
@define VERSE_PRESET ${BASE_PRESET + 0}
@define CHORUS_PRESET ${BASE_PRESET + 5}
@define BRIDGE_PRESET ${BASE_PRESET * 2}

@define SCENE_OFFSET ${CHORUS_PRESET / 5}

[00:00.000]
- tempo ${BASE_TEMPO}
- pc 1.${VERSE_PRESET}

[00:10.000]
- tempo ${FAST_TEMPO}
- pc 1.${CHORUS_PRESET}

[00:20.000]
- tempo ${SLOW_TEMPO}
- pc 1.${BRIDGE_PRESET}
```

### Acceptance Criteria

- [ ] `ExpressionEvaluator` class implemented
- [ ] All unit tests pass (>95% coverage)
- [ ] All arithmetic operators supported
- [ ] Parentheses grouping works correctly
- [ ] Variables resolved in expressions
- [ ] Constants (PI, E) work in expressions
- [ ] Security: Function calls rejected
- [ ] Security: String operations rejected
- [ ] `@define` accepts expressions
- [ ] Command parameters accept expressions
- [ ] Example file `expressions.mml` compiles successfully
- [ ] Error messages distinguish syntax vs. undefined variable errors

---

## Phase 3: Loops

### Goals
- Implement `@loop` directive
- Support repetition with timing intervals
- Enable loop iteration variables
- Generate expanded event sequences

### Deliverables

#### File: `src/loops.py`

```python
"""
Loop expansion for MML compiler.
Handles @loop directive and generates repeated event sequences.
"""

from dataclasses import dataclass
from typing import List, Any
from src.symbols import SymbolTable
from src.timing import TimeSpec, TimingContext


@dataclass
class LoopCommand:
    """Represents a command inside a loop."""
    command_type: str  # 'pc', 'cc', 'note_on', etc.
    parameters: dict
    source_line: int = 0


@dataclass
class LoopDefinition:
    """
    Represents a @loop directive.
    
    Example:
        @loop 4 times at [1.1.0] every 1b
          - note_on 1.C4 100 1b
        @end
    """
    count: int
    start_time: TimeSpec
    interval: TimeSpec
    commands: List[LoopCommand]
    source_line: int = 0


class LoopExpander:
    """
    Expands loops into concrete event sequences.
    """
    
    def __init__(self, timing_context: TimingContext, symbol_table: SymbolTable):
        """
        Initialize loop expander.
        
        Args:
            timing_context: Timing context for tick calculations
            symbol_table: Symbol table for variable lookup
        """
        self.timing_context = timing_context
        self.symbol_table = symbol_table
    
    def expand_loop(self, loop_def: LoopDefinition) -> List[dict]:
        """
        Expand a loop into a list of events.
        
        Args:
            loop_def: Loop definition to expand
            
        Returns:
            List of event dictionaries with timing
            
        Example:
            Input: Loop 4 times every 1 beat
            Output: 4 events at sequential beat positions
        """
        events = []
        
        # Calculate start tick
        start_tick = loop_def.start_time.to_ticks(self.timing_context)
        
        # Calculate interval in ticks
        interval_ticks = self._calculate_interval_ticks(loop_def.interval)
        
        # Generate events for each iteration
        for iteration in range(loop_def.count):
            current_tick = start_tick + (iteration * interval_ticks)
            
            # Create loop-specific symbol table with iteration variables
            loop_symbols = SymbolTable(parent=self.symbol_table)
            loop_symbols.define('LOOP_INDEX', iteration, 'int')
            loop_symbols.define('LOOP_COUNT', loop_def.count, 'int')
            loop_symbols.define('LOOP_ITERATION', iteration + 1, 'int')  # 1-based
            
            # Expand each command in the loop
            for command in loop_def.commands:
                event = self._create_event(
                    command,
                    current_tick,
                    loop_symbols
                )
                events.append(event)
        
        return events
    
    def _calculate_interval_ticks(self, interval: TimeSpec) -> int:
        """
        Calculate interval in ticks.
        
        Args:
            interval: Time specification for interval
            
        Returns:
            Number of ticks
            
        Supports:
            - Beats: '1b', '2b'
            - Bars: '1.0.0', '2.0.0'
            - Milliseconds: '500ms'
            - Ticks: '120t'
        """
        if isinstance(interval, str):
            interval_str = interval.strip()
            
            # Beats
            if interval_str.endswith('b'):
                beats = float(interval_str[:-1])
                return int(beats * self.timing_context.ppq)
            
            # Milliseconds
            if interval_str.endswith('ms'):
                ms = float(interval_str[:-2])
                return self._ms_to_ticks(ms)
            
            # Ticks
            if interval_str.endswith('t'):
                return int(interval_str[:-1])
            
            # BBT format (bars.beats.ticks)
            if '.' in interval_str:
                parts = interval_str.split('.')
                if len(parts) == 3:
                    bars = int(parts[0])
                    beats = int(parts[1])
                    ticks = int(parts[2])
                    return self._bbt_to_ticks(bars, beats, ticks)
        
        raise ValueError(f"Unsupported interval format: {interval}")
    
    def _ms_to_ticks(self, milliseconds: float) -> int:
        """Convert milliseconds to ticks."""
        # ticks = (ms * ppq * tempo) / 60000
        tempo = self.timing_context.tempo
        ppq = self.timing_context.ppq
        return int(milliseconds * ppq * tempo / 60000)
    
    def _bbt_to_ticks(self, bars: int, beats: int, ticks: int) -> int:
        """Convert bars/beats/ticks to absolute ticks."""
        ticks_per_beat = self.timing_context.ppq
        beats_per_bar = self.timing_context.time_signature[0]
        ticks_per_bar = ticks_per_beat * beats_per_bar
        
        return bars * ticks_per_bar + beats * ticks_per_beat + ticks
    
    def _create_event(self, command: LoopCommand, tick: int,
                     loop_symbols: SymbolTable) -> dict:
        """
        Create an event from a command.
        
        Args:
            command: Loop command to convert
            tick: Absolute tick position
            loop_symbols: Symbol table with loop variables
            
        Returns:
            Event dictionary
        """
        from src.expressions import ExpressionEvaluator
        evaluator = ExpressionEvaluator(loop_symbols)
        
        # Resolve parameters (may contain loop variables)
        resolved_params = {}
        for key, value in command.parameters.items():
            if isinstance(value, str) and ('${' in value or self._has_loop_var(value)):
                resolved_params[key] = evaluator.evaluate(value)
            else:
                resolved_params[key] = value
        
        return {
            'tick': tick,
            'type': command.command_type,
            'parameters': resolved_params,
            'metadata': {
                'source_line': command.source_line,
                'from_loop': True
            }
        }
    
    def _has_loop_var(self, value: str) -> bool:
        """Check if value contains loop variable."""
        loop_vars = ['LOOP_INDEX', 'LOOP_COUNT', 'LOOP_ITERATION']
        return any(var in value for var in loop_vars)


def create_loop_definition(count: int, start_time: str, interval: str,
                          commands: List[dict], line: int = 0) -> LoopDefinition:
    """
    Convenience function to create a loop definition.
    
    Args:
        count: Number of iterations
        start_time: Start time as string (e.g., '1.1.0', '00:00.000')
        interval: Interval as string (e.g., '1b', '500ms')
        commands: List of command dictionaries
        line: Source line number
        
    Returns:
        LoopDefinition instance
    """
    from src.timing import parse_time_spec
    
    start_spec = parse_time_spec(start_time)
    
    loop_commands = [
        LoopCommand(
            command_type=cmd['type'],
            parameters=cmd['parameters'],
            source_line=cmd.get('line', 0)
        )
        for cmd in commands
    ]
    
    return LoopDefinition(
        count=count,
        start_time=start_spec,
        interval=interval,
        commands=loop_commands,
        source_line=line
    )
```

#### File: `tests/test_loops.py`

```python
"""
Unit tests for loop expansion.
"""

import pytest
from src.loops import LoopExpander, LoopDefinition, LoopCommand, create_loop_definition
from src.symbols import SymbolTable
from src.timing import TimingContext, TimeSpec, TimeUnit


class TestLoopExpander:
    """Test LoopExpander class."""
    
    @pytest.fixture
    def timing_context(self):
        """Create a standard timing context."""
        return TimingContext(ppq=480, tempo=120.0, time_signature=(4, 4))
    
    @pytest.fixture
    def symbol_table(self):
        """Create a symbol table."""
        return SymbolTable()
    
    @pytest.fixture
    def expander(self, timing_context, symbol_table):
        """Create a loop expander."""
        return LoopExpander(timing_context, symbol_table)
    
    def test_simple_loop(self, expander, timing_context):
        """Test simple loop expansion."""
        # @loop 3 times at [1.1.0] every 1b
        loop_def = LoopDefinition(
            count=3,
            start_time=TimeSpec(TimeUnit.MUSICAL_BBT, (1, 1, 0)),
            interval='1b',
            commands=[
                LoopCommand('pc', {'channel': 1, 'program': 5}, 10)
            ],
            source_line=10
        )
        
        events = expander.expand_loop(loop_def)
        
        assert len(events) == 3
        
        # Check timing - each beat is 480 ticks apart (ppq=480)
        assert events[0]['tick'] == 0  # Bar 1, beat 1
        assert events[1]['tick'] == 480  # Bar 1, beat 2
        assert events[2]['tick'] == 960  # Bar 1, beat 3
        
        # Check all events have same type
        for event in events:
            assert event['type'] == 'pc'
            assert event['parameters']['program'] == 5
    
    def test_loop_with_multiple_commands(self, expander):
        """Test loop with multiple commands per iteration."""
        loop_def = LoopDefinition(
            count=2,
            start_time=TimeSpec(TimeUnit.MUSICAL_BBT, (1, 1, 0)),
            interval='1b',
            commands=[
                LoopCommand('pc', {'channel': 1, 'program': 5}, 10),
                LoopCommand('cc', {'channel': 1, 'controller': 7, 'value': 100}, 11),
            ],
            source_line=10
        )
        
        events = expander.expand_loop(loop_def)
        
        # 2 iterations * 2 commands = 4 events
        assert len(events) == 4
        
        # First iteration
        assert events[0]['type'] == 'pc'
        assert events[0]['tick'] == 0
        assert events[1]['type'] == 'cc'
        assert events[1]['tick'] == 0
        
        # Second iteration
        assert events[2]['type'] == 'pc'
        assert events[2]['tick'] == 480
        assert events[3]['type'] == 'cc'
        assert events[3]['tick'] == 480
    
    def test_loop_with_loop_index(self, expander):
        """Test LOOP_INDEX variable in loop."""
        loop_def = LoopDefinition(
            count=3,
            start_time=TimeSpec(TimeUnit.MUSICAL_BBT, (1, 1, 0)),
            interval='1b',
            commands=[
                LoopCommand('pc', {'channel': 1, 'program': '${10 + LOOP_INDEX}'}, 10)
            ],
            source_line=10
        )
        
        events = expander.expand_loop(loop_def)
        
        assert len(events) == 3
        
        # Check programs increment
        assert events[0]['parameters']['program'] == 10  # 10 + 0
        assert events[1]['parameters']['program'] == 11  # 10 + 1
        assert events[2]['parameters']['program'] == 12  # 10 + 2
    
    def test_loop_iteration_variable(self, expander):
        """Test LOOP_ITERATION variable (1-based)."""
        loop_def = LoopDefinition(
            count=3,
            start_time=TimeSpec(TimeUnit.MUSICAL_BBT, (1, 1, 0)),
            interval='1b',
            commands=[
                LoopCommand('cc', {'channel': 1, 'controller': 7, 'value': '${LOOP_ITERATION * 10}'}, 10)
            ],
            source_line=10
        )
        
        events = expander.expand_loop(loop_def)
        
        # LOOP_ITERATION is 1-based
        assert events[0]['parameters']['value'] == 10  # 1 * 10
        assert events[1]['parameters']['value'] == 20  # 2 * 10
        assert events[2]['parameters']['value'] == 30  # 3 * 10
    
    def test_loop_count_variable(self, expander):
        """Test LOOP_COUNT variable."""
        loop_def = LoopDefinition(
            count=5,
            start_time=TimeSpec(TimeUnit.MUSICAL_BBT, (1, 1, 0)),
            interval='1b',
            commands=[
                LoopCommand('cc', {'channel': 1, 'controller': 7, 'value': '${LOOP_COUNT * 2}'}, 10)
            ],
            source_line=10
        )
        
        events = expander.expand_loop(loop_def)
        
        # All iterations see LOOP_COUNT = 5
        for event in events:
            assert event['parameters']['value'] == 10  # 5 * 2
    
    def test_interval_beats(self, expander):
        """Test different beat intervals."""
        # Every 2 beats
        loop_def = LoopDefinition(
            count=3,
            start_time=TimeSpec(TimeUnit.MUSICAL_BBT, (1, 1, 0)),
            interval='2b',
            commands=[LoopCommand('pc', {'channel': 1, 'program': 5}, 10)],
        )
        
        events = expander.expand_loop(loop_def)
        
        assert events[0]['tick'] == 0
        assert events[1]['tick'] == 960  # 2 beats = 960 ticks
        assert events[2]['tick'] == 1920
    
    def test_interval_milliseconds(self, expander, timing_context):
        """Test millisecond interval."""
        # Every 500ms at 120 BPM
        # 500ms = 480 ticks (at 120 BPM, 480 PPQ)
        loop_def = LoopDefinition(
            count=2,
            start_time=TimeSpec(TimeUnit.MUSICAL_BBT, (1, 1, 0)),
            interval='500ms',
            commands=[LoopCommand('pc', {'channel': 1, 'program': 5}, 10)],
        )
        
        events = expander.expand_loop(loop_def)
        
        # At 120 BPM, 500ms = 480 ticks
        assert abs(events[1]['tick'] - events[0]['tick'] - 480) < 10
    
    def test_interval_ticks(self, expander):
        """Test tick interval."""
        loop_def = LoopDefinition(
            count=3,
            start_time=TimeSpec(TimeUnit.MUSICAL_BBT, (1, 1, 0)),
            interval='240t',
            commands=[LoopCommand('pc', {'channel': 1, 'program': 5}, 10)],
        )
        
        events = expander.expand_loop(loop_def)
        
        assert events[0]['tick'] == 0
        assert events[1]['tick'] == 240
        assert events[2]['tick'] == 480
    
    def test_interval_bbt(self, expander):
        """Test BBT interval."""
        # Every 1 bar
        loop_def = LoopDefinition(
            count=3,
            start_time=TimeSpec(TimeUnit.MUSICAL_BBT, (1, 1, 0)),
            interval='1.0.0',
            commands=[LoopCommand('pc', {'channel': 1, 'program': 5}, 10)],
        )
        
        events = expander.expand_loop(loop_def)
        
        # 1 bar = 4 beats = 1920 ticks (at 4/4, ppq=480)
        assert events[0]['tick'] == 0
        assert events[1]['tick'] == 1920
        assert events[2]['tick'] == 3840
    
    def test_loop_with_user_variables(self):
        """Test loop using user-defined variables."""
        table = SymbolTable()
        table.define('BASE_PROGRAM', 20)
        
        context = TimingContext(ppq=480, tempo=120.0)
        expander = LoopExpander(context, table)
        
        loop_def = LoopDefinition(
            count=3,
            start_time=TimeSpec(TimeUnit.MUSICAL_BBT, (1, 1, 0)),
            interval='1b',
            commands=[
                LoopCommand('pc', {'channel': 1, 'program': '${BASE_PROGRAM + LOOP_INDEX}'}, 10)
            ],
        )
        
        events = expander.expand_loop(loop_def)
        
        # Programs should be 20, 21, 22
        assert events[0]['parameters']['program'] == 20
        assert events[1]['parameters']['program'] == 21
        assert events[2]['parameters']['program'] == 22
    
    def test_empty_loop(self, expander):
        """Test loop with no commands."""
        loop_def = LoopDefinition(
            count=3,
            start_time=TimeSpec(TimeUnit.MUSICAL_BBT, (1, 1, 0)),
            interval='1b',
            commands=[],
        )
        
        events = expander.expand_loop(loop_def)
        
        assert len(events) == 0
    
    def test_single_iteration_loop(self, expander):
        """Test loop with count=1."""
        loop_def = LoopDefinition(
            count=1,
            start_time=TimeSpec(TimeUnit.MUSICAL_BBT, (1, 1, 0)),
            interval='1b',
            commands=[LoopCommand('pc', {'channel': 1, 'program': 5}, 10)],
        )
        
        events = expander.expand_loop(loop_def)
        
        assert len(events) == 1
        assert events[0]['tick'] == 0


class TestCreateLoopDefinition:
    """Test convenience function for creating loop definitions."""
    
    def test_create_simple_loop(self):
        """Test creating a simple loop definition."""
        loop_def = create_loop_definition(
            count=3,
            start_time='1.1.0',
            interval='1b',
            commands=[
                {'type': 'pc', 'parameters': {'channel': 1, 'program': 5}, 'line': 10}
            ],
            line=10
        )
        
        assert loop_def.count == 3
        assert loop_def.interval == '1b'
        assert len(loop_def.commands) == 1
        assert loop_def.commands[0].command_type == 'pc'
```

#### Grammar Extension

**Instructions for Claude Code Agent:**

Add to `src/grammar/mml.lark`:

```lark
// Loop directive
loop_stmt: "@loop" loop_count "times" "at" time_spec "every" interval loop_body "@end"

loop_count: NUMBER | variable_ref
loop_body: command_list
interval: INTERVAL_SPEC

INTERVAL_SPEC: /\d+(\.\d+)?[bmt]/ | /\d+\.\d+\.\d+/ | /\d+ms/
// Examples: "1b", "2.5b", "120t", "500ms", "1.0.0"
```

### Test Files

Create `tests/fixtures/loops_basic.mml`:

```markdown
@define KICK_NOTE 36
@define SNARE_NOTE 38

# Simple 4-beat drum pattern
@loop 4 times at [1.1.0] every 1b
  - note_on 10.${KICK_NOTE} 100 250ms
@end

# Preset progression
@loop 8 times at [1.1.0] every 1.0.0
  - pc 1.${10 + LOOP_INDEX}
@end
```

### Acceptance Criteria

- [ ] `LoopExpander` class implemented
- [ ] All unit tests pass (>95% coverage)
- [ ] Grammar accepts `@loop` directive
- [ ] Loop variables (LOOP_INDEX, LOOP_COUNT, LOOP_ITERATION) work
- [ ] Interval formats supported: beats, bars, ticks, milliseconds
- [ ] Multiple commands per iteration work
- [ ] User variables accessible inside loops
- [ ] Nested scoping works (loop vars don't leak)
- [ ] Example file `loops_basic.mml` compiles successfully
- [ ] Generated events have correct timing

---

## Phase 4: Sweeps and Ramps

### Goals
- Implement `@sweep` directive
- Support value interpolation (ramps)
- Multiple curve types (linear, exponential, etc.)
- Generate smooth parameter automation

### Deliverables

#### File: `src/sweeps.py`

```python
"""
Sweep/ramp expansion for MML compiler.
Handles @sweep directive and generates smooth value transitions.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Union
import math

from src.symbols import SymbolTable
from src.timing import TimeSpec, TimingContext


class RampType(Enum):
    """Types of interpolation curves."""
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    LOGARITHMIC = "logarithmic"
    EASE_IN = "ease_in"
    EASE_OUT = "ease_out"
    EASE_IN_OUT = "ease_in_out"


@dataclass
class RampSpec:
    """
    Specification for value interpolation.
    
    Examples:
        ramp(0, 127)                    # Linear from 0 to 127
        ramp(0, 127, exponential)       # Exponential curve
        ramp(${START}, ${END}, ease_in) # With variables
    """
    start_value: Union[int, float]
    end_value: Union[int, float]
    ramp_type: RampType = RampType.LINEAR
    
    def interpolate(self, progress: float) -> int:
        """
        Calculate interpolated value at given progress.
        
        Args:
            progress: Progress from 0.0 to 1.0
            
        Returns:
            Interpolated value as MIDI value (0-127)
        """
        # Clamp progress
        progress = max(0.0, min(1.0, progress))
        
        # Apply curve function
        if self.ramp_type == RampType.LINEAR:
            factor = progress
        
        elif self.ramp_type == RampType.EXPONENTIAL:
            # Exponential ease: factor = progress^2
            # For smooth start-to-finish, use progress^2 for 0-start values
            if self.start_value == 0:
                factor = progress ** 2
            else:
                # For non-zero start, use exponential ratio
                ratio = self.end_value / self.start_value if self.start_value != 0 else 1
                factor = (ratio ** progress - 1) / (ratio - 1) if ratio != 1 else progress
        
        elif self.ramp_type == RampType.LOGARITHMIC:
            # Logarithmic curve: fast at start, slow at end
            if progress == 0:
                factor = 0
            else:
                # Scale log(1) to log(10) to 0-1 range
                factor = math.log10(progress * 9 + 1)
        
        elif self.ramp_type == RampType.EASE_IN:
            # Cubic ease-in: slow start, fast end
            factor = progress ** 3
        
        elif self.ramp_type == RampType.EASE_OUT:
            # Cubic ease-out: fast start, slow end
            factor = 1 - (1 - progress) ** 3
        
        elif self.ramp_type == RampType.EASE_IN_OUT:
            # Cubic ease-in-out: slow at both ends
            if progress < 0.5:
                factor = 4 * progress ** 3
            else:
                factor = 1 - ((-2 * progress + 2) ** 3) / 2
        
        else:
            factor = progress
        
        # Calculate value
        value = self.start_value + (self.end_value - self.start_value) * factor
        
        # Clamp to MIDI range
        return max(0, min(127, int(round(value))))


@dataclass
class SweepCommand:
    """Command template for sweep with ramp placeholder."""
    command_type: str
    parameters: dict
    ramp_parameter: str  # Which parameter has the ramp
    source_line: int = 0


@dataclass
class SweepDefinition:
    """
    Represents a @sweep directive.
    
    Example:
        @sweep from [1.1.0] to [5.1.0] every 8t
          - cc 1.7 ramp(0, 127)
        @end
    """
    start_time: TimeSpec
    end_time: TimeSpec
    interval: TimeSpec
    command: SweepCommand
    ramp_spec: RampSpec
    source_line: int = 0


class SweepExpander:
    """
    Expands sweeps into series of events with interpolated values.
    """
    
    def __init__(self, timing_context: TimingContext, symbol_table: SymbolTable):
        """
        Initialize sweep expander.
        
        Args:
            timing_context: Timing context for calculations
            symbol_table: Symbol table for variable lookup
        """
        self.timing_context = timing_context
        self.symbol_table = symbol_table
    
    def expand_sweep(self, sweep_def: SweepDefinition) -> List[dict]:
        """
        Expand sweep into series of events.
        
        Args:
            sweep_def: Sweep definition to expand
            
        Returns:
            List of event dictionaries with interpolated values
        """
        events = []
        
        # Calculate time range
        start_tick = sweep_def.start_time.to_ticks(self.timing_context)
        end_tick = sweep_def.end_time.to_ticks(self.timing_context)
        interval_ticks = self._calculate_interval_ticks(sweep_def.interval)
        
        total_duration = end_tick - start_tick
        
        if total_duration <= 0:
            raise ValueError("Sweep end time must be after start time")
        
        # Generate events at each interval
        current_tick = start_tick
        
        while current_tick <= end_tick:
            # Calculate progress (0.0 to 1.0)
            progress = (current_tick - start_tick) / total_duration
            
            # Interpolate value
            interpolated_value = sweep_def.ramp_spec.interpolate(progress)
            
            # Create event with interpolated value
            event = self._create_event(
                sweep_def.command,
                current_tick,
                interpolated_value
            )
            events.append(event)
            
            current_tick += interval_ticks
        
        return events
    
    def _calculate_interval_ticks(self, interval: TimeSpec) -> int:
        """
        Calculate interval in ticks.
        
        Args:
            interval: Time specification for interval
            
        Returns:
            Number of ticks
        """
        if isinstance(interval, str):
            interval_str = interval.strip()
            
            # Ticks
            if interval_str.endswith('t'):
                return int(interval_str[:-1])
            
            # Beats
            if interval_str.endswith('b'):
                beats = float(interval_str[:-1])
                return int(beats * self.timing_context.ppq)
            
            # Milliseconds
            if interval_str.endswith('ms'):
                ms = float(interval_str[:-2])
                tempo = self.timing_context.tempo
                ppq = self.timing_context.ppq
                return int(ms * ppq * tempo / 60000)
            
            # BBT format
            if '.' in interval_str:
                parts = interval_str.split('.')
                if len(parts) == 3:
                    bars = int(parts[0])
                    beats = int(parts[1])
                    ticks = int(parts[2])
                    return self._bbt_to_ticks(bars, beats, ticks)
        
        raise ValueError(f"Unsupported interval format: {interval}")
    
    def _bbt_to_ticks(self, bars: int, beats: int, ticks: int) -> int:
        """Convert BBT to ticks."""
        ticks_per_beat = self.timing_context.ppq
        beats_per_bar = self.timing_context.time_signature[0]
        ticks_per_bar = ticks_per_beat * beats_per_bar
        
        return bars * ticks_per_bar + beats * ticks_per_beat + ticks
    
    def _create_event(self, command: SweepCommand, tick: int, value: int) -> dict:
        """
        Create event with interpolated value.
        
        Args:
            command: Command template
            tick: Tick position
            value: Interpolated value
            
        Returns:
            Event dictionary
        """
        # Copy parameters and insert interpolated value
        params = command.parameters.copy()
        params[command.ramp_parameter] = value
        
        return {
            'tick': tick,
            'type': command.command_type,
            'parameters': params,
            'metadata': {
                'source_line': command.source_line,
                'from_sweep': True,
                'interpolated_value': value
            }
        }


def parse_ramp_spec(ramp_str: str, symbol_table: SymbolTable) -> RampSpec:
    """
    Parse ramp specification from string.
    
    Args:
        ramp_str: Ramp string like "ramp(0, 127)" or "ramp(0, 127, exponential)"
        symbol_table: Symbol table for variable resolution
        
    Returns:
        RampSpec instance
        
    Raises:
        ValueError: If ramp format is invalid
    """
    import re
    from src.expressions import ExpressionEvaluator
    
    # Match ramp(start, end) or ramp(start, end, type)
    pattern = r'ramp\s*\(\s*([^,]+?)\s*,\s*([^,)]+?)(?:\s*,\s*(\w+))?\s*\)'
    match = re.match(pattern, ramp_str.strip())
    
    if not match:
        raise ValueError(f"Invalid ramp specification: {ramp_str}")
    
    start_str = match.group(1)
    end_str = match.group(2)
    type_str = match.group(3) or 'linear'
    
    # Evaluate start and end (may be expressions or variables)
    evaluator = ExpressionEvaluator(symbol_table)
    
    if '${' in start_str or start_str.strip().isupper():
        start_val = evaluator.evaluate(start_str)
    else:
        start_val = int(start_str)
    
    if '${' in end_str or end_str.strip().isupper():
        end_val = evaluator.evaluate(end_str)
    else:
        end_val = int(end_str)
    
    # Parse ramp type
    try:
        ramp_type = RampType(type_str.lower())
    except ValueError:
        raise ValueError(f"Unknown ramp type: {type_str}")
    
    return RampSpec(
        start_value=start_val,
        end_value=end_val,
        ramp_type=ramp_type
    )
```

#### File: `tests/test_sweeps.py`

```python
"""
Unit tests for sweep expansion.
"""

import pytest
import math
from src.sweeps import (
    SweepExpander, SweepDefinition, SweepCommand, RampSpec, RampType,
    parse_ramp_spec
)
from src.symbols import SymbolTable
from src.timing import TimingContext, TimeSpec, TimeUnit


class TestRampSpec:
    """Test RampSpec interpolation."""
    
    def test_linear_ramp(self):
        """Test linear interpolation."""
        ramp = RampSpec(0, 127, RampType.LINEAR)
        
        assert ramp.interpolate(0.0) == 0
        assert ramp.interpolate(0.5) == 64
        assert ramp.interpolate(1.0) == 127
    
    def test_linear_ramp_partial_range(self):
        """Test linear interpolation with partial range."""
        ramp = RampSpec(20, 100, RampType.LINEAR)
        
        assert ramp.interpolate(0.0) == 20
        assert ramp.interpolate(0.5) == 60
        assert ramp.interpolate(1.0) == 100
    
    def test_exponential_ramp(self):
        """Test exponential curve."""
        ramp = RampSpec(0, 127, RampType.EXPONENTIAL)
        
        assert ramp.interpolate(0.0) == 0
        mid = ramp.interpolate(0.5)
        assert mid < 64  # Should be less than linear
        assert ramp.interpolate(1.0) == 127
    
    def test_logarithmic_ramp(self):
        """Test logarithmic curve."""
        ramp = RampSpec(0, 127, RampType.LOGARITHMIC)
        
        assert ramp.interpolate(0.0) == 0
        mid = ramp.interpolate(0.5)
        assert mid > 64  # Should be more than linear
        assert ramp.interpolate(1.0) == 127
    
    def test_ease_in_ramp(self):
        """Test ease-in curve."""
        ramp = RampSpec(0, 127, RampType.EASE_IN)
        
        assert ramp.interpolate(0.0) == 0
        # Ease-in starts slow
        early = ramp.interpolate(0.3)
        assert early < 0.3 * 127
        assert ramp.interpolate(1.0) == 127
    
    def test_ease_out_ramp(self):
        """Test ease-out curve."""
        ramp = RampSpec(0, 127, RampType.EASE_OUT)
        
        assert ramp.interpolate(0.0) == 0
        # Ease-out ends slow
        late = ramp.interpolate(0.7)
        assert late > 0.7 * 127
        assert ramp.interpolate(1.0) == 127
    
    def test_ease_in_out_ramp(self):
        """Test ease-in-out curve."""
        ramp = RampSpec(0, 127, RampType.EASE_IN_OUT)
        
        assert ramp.interpolate(0.0) == 0
        assert ramp.interpolate(0.5) == 64  # Should be near middle
        assert ramp.interpolate(1.0) == 127
    
    def test_ramp_clamping(self):
        """Test values are clamped to MIDI range."""
        ramp = RampSpec(0, 200, RampType.LINEAR)  # Exceeds MIDI max
        
        # Should clamp to 127
        assert ramp.interpolate(1.0) == 127
    
    def test_ramp_negative_values(self):
        """Test negative values are clamped to 0."""
        ramp = RampSpec(-50, 50, RampType.LINEAR)
        
        # Negative values clamped to 0
        assert ramp.interpolate(0.0) == 0
        assert ramp.interpolate(0.5) == 0
        assert ramp.interpolate(1.0) == 50
    
    def test_reverse_ramp(self):
        """Test ramp from high to low."""
        ramp = RampSpec(127, 0, RampType.LINEAR)
        
        assert ramp.interpolate(0.0) == 127
        assert ramp.interpolate(0.5) == 64
        assert ramp.interpolate(1.0) == 0


class TestSweepExpander:
    """Test SweepExpander class."""
    
    @pytest.fixture
    def timing_context(self):
        """Create timing context."""
        return TimingContext(ppq=480, tempo=120.0, time_signature=(4, 4))
    
    @pytest.fixture
    def symbol_table(self):
        """Create symbol table."""
        return SymbolTable()
    
    @pytest.fixture
    def expander(self, timing_context, symbol_table):
        """Create sweep expander."""
        return SweepExpander(timing_context, symbol_table)
    
    def test_simple_sweep(self, expander):
        """Test basic sweep expansion."""
        # Sweep from bar 1 to bar 2, every 240 ticks
        sweep_def = SweepDefinition(
            start_time=TimeSpec(TimeUnit.MUSICAL_BBT, (1, 1, 0)),
            end_time=TimeSpec(TimeUnit.MUSICAL_BBT, (2, 1, 0)),
            interval='240t',
            command=SweepCommand('cc', {'channel': 1, 'controller': 7}, 'value', 10),
            ramp_spec=RampSpec(0, 127, RampType.LINEAR),
            source_line=10
        )
        
        events = expander.expand_sweep(sweep_def)
        
        # 1 bar = 1920 ticks, every 240 ticks = 9 events (including start and end)
        assert len(events) >= 8
        
        # Check first and last values
        assert events[0]['parameters']['value'] == 0
        assert events[-1]['parameters']['value'] == 127
        
        # Check values are increasing
        for i in range(1, len(events)):
            assert events[i]['parameters']['value'] >= events[i-1]['parameters']['value']
    
    def test_sweep_timing(self, expander):
        """Test sweep event timing."""
        sweep_def = SweepDefinition(
            start_time=TimeSpec(TimeUnit.MUSICAL_BBT, (1, 1, 0)),
            end_time=TimeSpec(TimeUnit.MUSICAL_BBT, (1, 3, 0)),  # 2 beats
            interval='240t',
            command=SweepCommand('cc', {'channel': 1, 'controller': 7}, 'value'),
            ramp_spec=RampSpec(0, 127, RampType.LINEAR),
        )
        
        events = expander.expand_sweep(sweep_def)
        
        # Check timing increments
        for i in range(1, len(events)):
            tick_diff = events[i]['tick'] - events[i-1]['tick']
            assert tick_diff == 240
    
    def test_sweep_with_beats_interval(self, expander):
        """Test sweep with beat interval."""
        sweep_def = SweepDefinition(
            start_time=TimeSpec(TimeUnit.MUSICAL_BBT, (1, 1, 0)),
            end_time=TimeSpec(TimeUnit.MUSICAL_BBT, (5, 1, 0)),  # 4 bars
            interval='1b',
            command=SweepCommand('cc', {'channel': 1, 'controller': 7}, 'value'),
            ramp_spec=RampSpec(0, 100, RampType.LINEAR),
        )
        
        events = expander.expand_sweep(sweep_def)
        
        # 4 bars * 4 beats + 1 = 17 events
        assert len(events) == 17
        
        # Check beat spacing (480 ticks per beat at ppq=480)
        assert events[1]['tick'] - events[0]['tick'] == 480
    
    def test_sweep_exponential_curve(self, expander):
        """Test sweep with exponential curve."""
        sweep_def = SweepDefinition(
            start_time=TimeSpec(TimeUnit.MUSICAL_BBT, (1, 1, 0)),
            end_time=TimeSpec(TimeUnit.MUSICAL_BBT, (3, 1, 0)),
            interval='240t',
            command=SweepCommand('cc', {'channel': 1, 'controller': 7}, 'value'),
            ramp_spec=RampSpec(0, 127, RampType.EXPONENTIAL),
        )
        
        events = expander.expand_sweep(sweep_def)
        
        # Exponential curve should have values less than linear in middle
        mid_idx = len(events) // 2
        mid_value = events[mid_idx]['parameters']['value']
        
        # Mid value should be less than 64 (linear midpoint)
        assert mid_value < 64
    
    def test_sweep_metadata(self, expander):
        """Test sweep events have correct metadata."""
        sweep_def = SweepDefinition(
            start_time=TimeSpec(TimeUnit.MUSICAL_BBT, (1, 1, 0)),
            end_time=TimeSpec(TimeUnit.MUSICAL_BBT, (2, 1, 0)),
            interval='480t',
            command=SweepCommand('cc', {'channel': 1, 'controller': 7}, 'value', 42),
            ramp_spec=RampSpec(0, 127, RampType.LINEAR),
            source_line=42
        )
        
        events = expander.expand_sweep(sweep_def)
        
        for event in events:
            assert event['metadata']['from_sweep'] is True
            assert event['metadata']['source_line'] == 42
            assert 'interpolated_value' in event['metadata']


class TestParseRampSpec:
    """Test ramp specification parsing."""
    
    @pytest.fixture
    def symbol_table(self):
        """Create symbol table with test variables."""
        table = SymbolTable()
        table.define('START_VOL', 20)
        table.define('END_VOL', 100)
        return table
    
    def test_parse_simple_ramp(self, symbol_table):
        """Test parsing simple ramp."""
        ramp = parse_ramp_spec("ramp(0, 127)", symbol_table)
        
        assert ramp.start_value == 0
        assert ramp.end_value == 127
        assert ramp.ramp_type == RampType.LINEAR
    
    def test_parse_ramp_with_type(self, symbol_table):
        """Test parsing ramp with type specification."""
        ramp = parse_ramp_spec("ramp(0, 127, exponential)", symbol_table)
        
        assert ramp.start_value == 0
        assert ramp.end_value == 127
        assert ramp.ramp_type == RampType.EXPONENTIAL
    
    def test_parse_ramp_all_types(self, symbol_table):
        """Test parsing all ramp types."""
        types = ['linear', 'exponential', 'logarithmic', 'ease_in', 'ease_out', 'ease_in_out']
        
        for ramp_type in types:
            ramp = parse_ramp_spec(f"ramp(0, 127, {ramp_type})", symbol_table)
            assert ramp.ramp_type == RampType(ramp_type)
    
    def test_parse_ramp_with_variables(self, symbol_table):
        """Test parsing ramp with variables."""
        ramp = parse_ramp_spec("ramp(${START_VOL}, ${END_VOL})", symbol_table)
        
        assert ramp.start_value == 20
        assert ramp.end_value == 100
    
    def test_parse_ramp_with_expressions(self, symbol_table):
        """Test parsing ramp with expressions."""
        ramp = parse_ramp_spec("ramp(${START_VOL * 2}, ${END_VOL + 27})", symbol_table)
        
        assert ramp.start_value == 40
        assert ramp.end_value == 127
    
    def test_parse_ramp_whitespace(self, symbol_table):
        """Test parsing handles whitespace."""
        ramp = parse_ramp_spec("ramp( 0 , 127 , linear )", symbol_table)
        
        assert ramp.start_value == 0
        assert ramp.end_value == 127
    
    def test_parse_invalid_ramp(self, symbol_table):
        """Test invalid ramp raises error."""
        with pytest.raises(ValueError, match="Invalid ramp specification"):
            parse_ramp_spec("notaramp(0, 127)", symbol_table)
        
        with pytest.raises(ValueError, match="Invalid ramp specification"):
            parse_ramp_spec("ramp(0)", symbol_table)
    
    def test_parse_invalid_ramp_type(self, symbol_table):
        """Test invalid ramp type raises error."""
        with pytest.raises(ValueError, match="Unknown ramp type"):
            parse_ramp_spec("ramp(0, 127, invalid_type)", symbol_table)
```

### Grammar Extension

**Instructions for Claude Code Agent:**

Add to `src/grammar/mml.lark`:

```lark
// Sweep directive
sweep_stmt: "@sweep" "from" time_spec "to" time_spec "every" interval sweep_body "@end"

sweep_body: sweep_command

sweep_command: "-" command_type parameters_with_ramp

parameters_with_ramp: // Parameters that may contain ramp() function
    RAMP_SPEC | parameter

RAMP_SPEC: /ramp\s*\([^)]+\)/
// Examples: "ramp(0, 127)", "ramp(0, 127, exponential)"
```

### Test Files

Create `tests/fixtures/sweeps_basic.mml`:

```markdown
@define START_VOLUME 0
@define END_VOLUME 127

# Volume fade-in (linear)
@sweep from [1.1.0] to [5.1.0] every 16t
  - cc 1.7 ramp(${START_VOLUME}, ${END_VOLUME})
@end

# Expression swell (exponential)
@sweep from [8.1.0] to [12.1.0] every 8t
  - cc 1.11 ramp(0, 127, exponential)
@end
```

### Acceptance Criteria

- [ ] `SweepExpander` class implemented
- [ ] `RampSpec` with all curve types implemented
- [ ] All unit tests pass (>95% coverage)
- [ ] Grammar accepts `@sweep` directive
- [ ] `ramp()` function parsed correctly
- [ ] All curve types work (linear, exponential, logarithmic, ease_in, ease_out, ease_in_out)
- [ ] Variables and expressions work in ramp parameters
- [ ] Interval formats supported
- [ ] Example file `sweeps_basic.mml` compiles successfully
- [ ] Generated values are smooth and correct

---

## Phase 5: Integration and Polish

### Goals
- Integrate all features into main compiler
- Add comprehensive error handling
- Performance optimization
- Documentation and examples
- Full end-to-end testing

### Deliverables

#### File: `src/expander.py`

```python
"""
Main expander that coordinates loops, sweeps, and variable substitution.
"""

from typing import List, Dict, Any
from src.symbols import SymbolTable
from src.expressions import ExpressionEvaluator
from src.loops import LoopExpander
from src.sweeps import SweepExpander
from src.timing import TimingContext


class CommandExpander:
    """
    Coordinates expansion of all advanced features.
    
    Responsibilities:
    - Manage symbol table
    - Expand loops and sweeps
    - Substitute variables in regular commands
    - Generate sorted event list
    """
    
    def __init__(self, timing_context: TimingContext):
        """
        Initialize expander.
        
        Args:
            timing_context: Global timing context
        """
        self.timing_context = timing_context
        self.symbol_table = SymbolTable()
        self.evaluator = ExpressionEvaluator(self.symbol_table)
        self.loop_expander = LoopExpander(timing_context, self.symbol_table)
        self.sweep_expander = SweepExpander(timing_context, self.symbol_table)
        
        self.events: List[Dict[str, Any]] = []
    
    def process_ast(self, ast_nodes: List[Any]) -> List[Dict[str, Any]]:
        """
        Process AST and generate events.
        
        Args:
            ast_nodes: List of AST nodes from parser
            
        Returns:
            Sorted list of MIDI events
        """
        # Phase 1: Process all definitions first
        for node in ast_nodes:
            if node.type == 'define':
                self._process_define(node)
        
        # Phase 2: Expand loops, sweeps, and regular commands
        for node in ast_nodes:
            if node.type == 'loop':
                events = self.loop_expander.expand_loop(node)
                self.events.extend(events)
            
            elif node.type == 'sweep':
                events = self.sweep_expander.expand_sweep(node)
                self.events.extend(events)
            
            elif node.type == 'command':
                event = self._process_command(node)
                self.events.append(event)
            
            elif node.type == 'tempo':
                self._process_tempo(node)
                event = self._create_tempo_event(node)
                self.events.append(event)
        
        # Phase 3: Sort events by time
        self.events.sort(key=lambda e: (e['tick'], self._event_priority(e)))
        
        # Phase 4: Validate
        self._validate_events()
        
        return self.events
    
    def _process_define(self, node):
        """Process @define directive."""
        var_name = node.name
        value_expr = node.value
        
        # Evaluate if expression
        if self._is_expression(value_expr):
            value = self.evaluator.evaluate(value_expr)
        else:
            value = value_expr
        
        self.symbol_table.define(var_name, value, line=node.line)
    
    def _process_command(self, node) -> Dict[str, Any]:
        """Process regular command with variable substitution."""
        params = {}
        
        for key, value in node.parameters.items():
            if isinstance(value, str) and ('${' in value or value.isupper()):
                params[key] = self.evaluator.evaluate(value)
            else:
                params[key] = value
        
        tick = self._calculate_tick(node.time)
        
        return {
            'tick': tick,
            'type': node.type,
            'parameters': params,
            'metadata': {'source_line': node.line}
        }
    
    def _process_tempo(self, node):
        """Process tempo change and update context."""
        tempo = node.tempo
        if isinstance(tempo, str):
            tempo = self.evaluator.evaluate(tempo)
        
        self.timing_context.tempo = float(tempo)
    
    def _calculate_tick(self, time_spec) -> int:
        """Calculate absolute tick from time specification."""
        return time_spec.to_ticks(self.timing_context)
    
    def _is_expression(self, value: str) -> bool:
        """Check if value is an expression."""
        if not isinstance(value, str):
            return False
        operators = ['+', '-', '*', '/', '%', '(', ')']
        return any(op in value for op in operators)
    
    def _event_priority(self, event: Dict[str, Any]) -> int:
        """Determine event priority for sorting."""
        priority_map = {
            'tempo': 0,
            'time_signature': 1,
            'cc': 2,
            'pc': 3,
            'note_on': 4,
            'note_off': 5,
        }
        return priority_map.get(event['type'], 10)
    
    def _validate_events(self):
        """Validate expanded events."""
        # Check timing is monotonic
        for i in range(1, len(self.events)):
            if self.events[i]['tick'] < self.events[i-1]['tick']:
                raise ValueError(
                    f"Non-monotonic timing at line {self.events[i]['metadata'].get('source_line')}"
                )
        
        # Check MIDI value ranges
        for event in self.events:
            if 'channel' in event['parameters']:
                ch = event['parameters']['channel']
                if not 1 <= ch <= 16:
                    raise ValueError(f"Invalid channel {ch} at tick {event['tick']}")
    
    def _create_tempo_event(self, node) -> Dict[str, Any]:
        """Create tempo meta event."""
        tempo = node.tempo
        if isinstance(tempo, str):
            tempo = self.evaluator.evaluate(tempo)
        
        return {
            'tick': self._calculate_tick(node.time),
            'type': 'tempo',
            'parameters': {'tempo': float(tempo)},
            'metadata': {'source_line': node.line}
        }
```

#### File: `tests/test_integration.py`

```python
"""
Integration tests for complete MML compilation.
"""

import pytest
from src.expander import CommandExpander
from src.timing import TimingContext


class TestIntegration:
    """End-to-end integration tests."""
    
    @pytest.fixture
    def expander(self):
        """Create command expander."""
        context = TimingContext(ppq=480, tempo=120.0)
        return CommandExpander(context)
    
    def test_variables_in_loop(self, expander):
        """Test variables used inside loop."""
        # Simulate AST
        ast = [
            {'type': 'define', 'name': 'BASE', 'value': 10, 'line': 1},
            {
                'type': 'loop',
                'count': 3,
                'start_time': '1.1.0',
                'interval': '1b',
                'commands': [
                    {'type': 'pc', 'parameters': {'channel': 1, 'program': '${BASE + LOOP_INDEX}'}}
                ],
                'line': 2
            }
        ]
        
        events = expander.process_ast(ast)
        
        # Should have 3 events with programs 10, 11, 12
        assert len(events) == 3
        assert events[0]['parameters']['program'] == 10
        assert events[1]['parameters']['program'] == 11
        assert events[2]['parameters']['program'] == 12
    
    def test_variables_in_sweep(self, expander):
        """Test variables in sweep ramp."""
        ast = [
            {'type': 'define', 'name': 'START', 'value': 0, 'line': 1},
            {'type': 'define', 'name': 'END', 'value': 100, 'line': 2},
            {
                'type': 'sweep',
                'start_time': '1.1.0',
                'end_time': '2.1.0',
                'interval': '480t',
                'command': {
                    'type': 'cc',
                    'parameters': {'channel': 1, 'controller': 7},
                    'ramp_parameter': 'value'
                },
                'ramp_spec': 'ramp(${START}, ${END})',
                'line': 3
            }
        ]
        
        events = expander.process_ast(ast)
        
        # Check first and last values
        assert events[0]['parameters']['value'] == 0
        assert events[-1]['parameters']['value'] == 100
    
    def test_mixed_commands(self, expander):
        """Test mixing regular commands, loops, and sweeps."""
        ast = [
            {'type': 'define', 'name': 'TEMPO', 'value': 120, 'line': 1},
            {
                'type': 'tempo',
                'time': '0.0.0',
                'tempo': '${TEMPO}',
                'line': 2
            },
            {
                'type': 'command',
                'time': '1.1.0',
                'type': 'pc',
                'parameters': {'channel': 1, 'program': 5},
                'line': 3
            },
            {
                'type': 'loop',
                'count': 2,
                'start_time': '2.1.0',
                'interval': '1b',
                'commands': [
                    {'type': 'note_on', 'parameters': {'channel': 1, 'note': 60, 'velocity': 100}}
                ],
                'line': 4
            },
            {
                'type': 'sweep',
                'start_time': '4.1.0',
                'end_time': '5.1.0',
                'interval': '240t',
                'command': {
                    'type': 'cc',
                    'parameters': {'channel': 1, 'controller': 7},
                    'ramp_parameter': 'value'
                },
                'ramp_spec': 'ramp(0, 127)',
                'line': 5
            }
        ]
        
        events = expander.process_ast(ast)
        
        # Should have multiple event types
        event_types = set(e['type'] for e in events)
        assert 'tempo' in event_types
        assert 'pc' in event_types
        assert 'note_on' in event_types
        assert 'cc' in event_types
        
        # Events should be sorted by time
        for i in range(1, len(events)):
            assert events[i]['tick'] >= events[i-1]['tick']


# More comprehensive integration tests would go here
```

#### Error Handling Enhancement

```python
# src/errors.py

class MMLError(Exception):
    """Base exception for MML errors."""
    
    def __init__(self, message: str, line: int = 0, column: int = 0, filename: str = None):
        self.message = message
        self.line = line
        self.column = column
        self.filename = filename
        super().__init__(self.format_error())
    
    def format_error(self) -> str:
        """Format error with context."""
        location = f"line {self.line}"
        if self.column:
            location += f":{self.column}"
        if self.filename:
            location = f"{self.filename}:{location}"
        
        return f"Error at {location}: {self.message}"


class UndefinedVariableError(MMLError):
    """Variable not defined."""
    pass


class InvalidExpressionError(MMLError):
    """Expression cannot be evaluated."""
    pass


class InvalidLoopError(MMLError):
    """Loop specification invalid."""
    pass


class InvalidSweepError(MMLError):
    """Sweep specification invalid."""
    pass


class TimingError(MMLError):
    """Timing specification invalid."""
    pass
```

### Documentation

Create comprehensive documentation:

1. `docs/VARIABLES.md` - Variable system guide
2. `docs/LOOPS.md` - Loop directive guide
3. `docs/SWEEPS.md` - Sweep directive guide
4. `docs/EXAMPLES.md` - Complete examples

### Performance Benchmarks

Create `tests/test_performance.py` for benchmarking large files.

### Acceptance Criteria

- [ ] `CommandExpander` integrates all features
- [ ] All integration tests pass
- [ ] Error handling comprehensive with good messages
- [ ] Performance acceptable (1000+ events in <1s)
- [ ] Complete documentation written
- [ ] Example files work end-to-end
- [ ] Code coverage >95% across all modules
- [ ] CLI updated to use new expander
- [ ] All existing tests still pass (no regressions)

---

## Implementation Checklist

### Phase 1: Variables ✓
- [ ] Implement `SymbolTable` class
- [ ] Write unit tests for `SymbolTable`
- [ ] Extend Lark grammar for `@define`
- [ ] Integrate with parser
- [ ] Create test fixtures
- [ ] Verify acceptance criteria

### Phase 2: Expressions ✓
- [ ] Implement `ExpressionEvaluator` class
- [ ] Write unit tests for expressions
- [ ] Support all operators
- [ ] Security validation
- [ ] Integrate with parser and symbol table
- [ ] Create test fixtures
- [ ] Verify acceptance criteria

### Phase 3: Loops ✓
- [ ] Implement `LoopExpander` class
- [ ] Write unit tests for loops
- [ ] Support loop variables
- [ ] Handle multiple interval formats
- [ ] Extend grammar for `@loop`
- [ ] Create test fixtures
- [ ] Verify acceptance criteria

### Phase 4: Sweeps ✓
- [ ] Implement `RampSpec` and interpolation
- [ ] Implement `SweepExpander` class
- [ ] Write unit tests for sweeps
- [ ] Support all curve types
- [ ] Extend grammar for `@sweep`
- [ ] Create test fixtures
- [ ] Verify acceptance criteria

### Phase 5: Integration ✓
- [ ] Implement `CommandExpander`
- [ ] Write integration tests
- [ ] Add comprehensive error handling
- [ ] Performance optimization
- [ ] Complete documentation
- [ ] End-to-end testing
- [ ] Final acceptance criteria

---

## Notes for Claude Code Agent

### General Guidelines

1. **Follow existing patterns**: Match the coding style and patterns in the existing codebase
2. **Test-driven**: Write tests before or alongside implementation
3. **Type hints**: Use Python type hints throughout
4. **Docstrings**: Every class and public method needs a docstring
5. **Error handling**: Always provide helpful error messages with line numbers
6. **Performance**: Keep performance in mind, but prioritize correctness first

### When Implementing Grammar Changes

1. Add new rules incrementally
2. Test each grammar change in isolation
3. Provide examples in comments
4. Update parser to handle new node types

### Testing Strategy

1. Unit tests for each class independently
2. Integration tests for feature combinations
3. Error case testing (invalid input)
4. Edge case testing (empty loops, single iterations, etc.)
5. Performance tests for large files

### Common Pitfalls to Avoid

1. **Off-by-one errors** in loop counts and tick calculations
2. **Integer overflow** in tick calculations
3. **Division by zero** in interpolation
4. **Scope leakage** of loop variables
5. **Non-monotonic timing** after expansion

### Success Metrics

- All tests pass
- Code coverage >95%
- Documentation complete
- Examples compile successfully
- Performance acceptable
- No regressions in existing functionality