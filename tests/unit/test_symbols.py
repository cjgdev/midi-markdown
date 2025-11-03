"""
Unit tests for symbol table implementation.
"""

import pytest

from midi_markdown.expansion.variables import SymbolTable, Variable


class TestVariableClass:
    """Test Variable dataclass."""

    def test_create_variable(self):
        """Test creating a Variable instance."""
        var = Variable("MY_VAR", 42, "int", 10)

        assert var.name == "MY_VAR"
        assert var.value == 42
        assert var.var_type == "int"
        assert var.source_line == 10

    def test_variable_equality(self):
        """Test variable equality."""
        var1 = Variable("VAR", 42, "int", 10)
        var2 = Variable("VAR", 42, "int", 10)

        assert var1 == var2

    def test_variable_repr(self):
        """Test Variable string representation."""
        var = Variable("TEST", 42, "int", 10)
        repr_str = repr(var)

        assert "TEST" in repr_str
        assert "42" in repr_str
        assert "int" in repr_str


class TestSymbolTable:
    """Test SymbolTable class."""

    def test_define_integer(self):
        """Test defining an integer variable."""
        table = SymbolTable()
        table.define("MY_VAR", 42)

        var = table.lookup("MY_VAR")
        assert var is not None
        assert var.value == 42
        assert var.var_type == "int"

    def test_define_float(self):
        """Test defining a float variable."""
        table = SymbolTable()
        table.define("TEMPO", 120.5)

        var = table.lookup("TEMPO")
        assert var is not None
        assert var.value == 120.5
        assert var.var_type == "float"

    def test_define_string(self):
        """Test defining a string variable."""
        table = SymbolTable()
        table.define("NAME", "Test Song")

        var = table.lookup("NAME")
        assert var is not None
        assert var.value == "Test Song"
        assert var.var_type == "string"

    def test_define_with_explicit_type(self):
        """Test defining variable with explicit type conversion."""
        table = SymbolTable()
        table.define("VALUE", "42", var_type="int")

        var = table.lookup("VALUE")
        assert var is not None
        assert var.value == 42
        assert var.var_type == "int"
        assert isinstance(var.value, int)

    def test_define_float_from_string(self):
        """Test converting string to float."""
        table = SymbolTable()
        table.define("TEMPO", "120.5", var_type="float")

        var = table.lookup("TEMPO")
        assert var.value == 120.5
        assert isinstance(var.value, float)

    def test_resolve_variable(self):
        """Test resolving variable to value."""
        table = SymbolTable()
        table.define("PRESET", 5)

        value = table.resolve("PRESET")
        assert value == 5

    def test_undefined_variable_raises(self):
        """Test that resolving undefined variable raises error."""
        table = SymbolTable()

        with pytest.raises(ValueError, match="Undefined variable: UNKNOWN"):
            table.resolve("UNKNOWN")

    def test_constant_pi(self):
        """Test built-in PI constant."""
        table = SymbolTable()

        pi = table.resolve("PI")
        assert abs(pi - 3.14159) < 0.0001

    def test_constant_e(self):
        """Test built-in E constant."""
        table = SymbolTable()

        e = table.resolve("E")
        assert abs(e - 2.71828) < 0.0001

    def test_cannot_redefine_constant(self):
        """Test that constants cannot be redefined."""
        table = SymbolTable()

        with pytest.raises(ValueError, match="Cannot redefine built-in constant: PI"):
            table.define("PI", 3.14)

    def test_cannot_redefine_e(self):
        """Test that E constant cannot be redefined."""
        table = SymbolTable()

        with pytest.raises(ValueError, match="Cannot redefine built-in constant: E"):
            table.define("E", 2.71)

    def test_invalid_variable_name_lowercase(self):
        """Test that lowercase variable names are rejected."""
        table = SymbolTable()

        with pytest.raises(ValueError, match="Invalid variable name"):
            table.define("lowercase", 42)

    def test_invalid_variable_name_mixed_case(self):
        """Test that mixed case variable names are rejected."""
        table = SymbolTable()

        with pytest.raises(ValueError, match="Invalid variable name"):
            table.define("MixedCase", 42)

    def test_invalid_variable_name_special_chars(self):
        """Test that variable names with special characters are rejected."""
        table = SymbolTable()

        with pytest.raises(ValueError, match="Invalid variable name"):
            table.define("VAR-NAME", 42)

        with pytest.raises(ValueError, match="Invalid variable name"):
            table.define("VAR.NAME", 42)

    def test_valid_variable_names(self):
        """Test valid variable name patterns."""
        table = SymbolTable()

        # These should all work
        table.define("VAR", 1)
        table.define("MY_VAR", 2)
        table.define("VAR_2", 3)
        table.define("MAIN_PRESET_123", 4)

        assert table.resolve("VAR") == 1
        assert table.resolve("MY_VAR") == 2
        assert table.resolve("VAR_2") == 3
        assert table.resolve("MAIN_PRESET_123") == 4

    def test_exists_method(self):
        """Test exists() method."""
        table = SymbolTable()
        table.define("VAR", 42)

        assert table.exists("VAR")
        assert not table.exists("UNKNOWN")
        assert table.exists("PI")  # Constants also exist

    def test_parent_scope_lookup(self):
        """Test variable lookup in parent scope."""
        parent = SymbolTable()
        parent.define("GLOBAL_VAR", 100)

        child = SymbolTable(parent=parent)
        child.define("LOCAL_VAR", 200)

        # Child can see both
        assert child.resolve("LOCAL_VAR") == 200
        assert child.resolve("GLOBAL_VAR") == 100

        # Parent cannot see child
        assert parent.resolve("GLOBAL_VAR") == 100
        with pytest.raises(ValueError):
            parent.resolve("LOCAL_VAR")

    def test_child_shadows_parent(self):
        """Test that child scope can shadow parent variables."""
        parent = SymbolTable()
        parent.define("VAR", 100)

        child = SymbolTable(parent=parent)
        child.define("VAR", 200)

        # Child sees its own value
        assert child.resolve("VAR") == 200

        # Parent unchanged
        assert parent.resolve("VAR") == 100

    def test_get_all(self):
        """Test get_all() returns only current scope."""
        parent = SymbolTable()
        parent.define("PARENT_VAR", 100)

        child = SymbolTable(parent=parent)
        child.define("CHILD_VAR", 200)

        child_vars = child.get_all()
        assert "CHILD_VAR" in child_vars
        assert "PARENT_VAR" not in child_vars  # Parent not included

    def test_table_repr(self):
        """Test SymbolTable string representation."""
        table = SymbolTable()
        table.define("VAR1", 10)
        table.define("VAR2", 20)

        repr_str = repr(table)
        assert "SymbolTable" in repr_str
        assert "VAR1=10" in repr_str or "VAR2=20" in repr_str

    def test_variable_redefinition_allowed(self):
        """Test that variables can be redefined (unlike constants)."""
        table = SymbolTable()
        table.define("VAR", 10)
        table.define("VAR", 20)  # Should work

        assert table.resolve("VAR") == 20

    def test_source_line_tracking(self):
        """Test that source line numbers are tracked."""
        table = SymbolTable()
        table.define("VAR", 42, line=123)

        var = table.lookup("VAR")
        assert var.source_line == 123

    def test_type_coercion_int_to_float(self):
        """Test type coercion when explicitly requested."""
        table = SymbolTable()
        table.define("VAR", 42, var_type="float")

        var = table.lookup("VAR")
        assert var.value == 42.0
        assert isinstance(var.value, float)

    def test_type_coercion_string_to_int(self):
        """Test converting string to int."""
        table = SymbolTable()
        table.define("VAR", "100", var_type="int")

        var = table.lookup("VAR")
        assert var.value == 100
        assert isinstance(var.value, int)

    def test_unsupported_value_type(self):
        """Test that unsupported value types are rejected."""
        table = SymbolTable()

        with pytest.raises(ValueError, match="Unsupported value type"):
            table.define("VAR", [1, 2, 3])  # Lists not supported

    def test_empty_table(self):
        """Test operations on empty symbol table."""
        table = SymbolTable()

        assert not table.exists("ANYTHING")
        assert table.get_all() == {}

        # Constants should still work
        assert table.exists("PI")

    def test_constants_in_child_scope(self):
        """Test that constants are accessible in child scopes."""
        parent = SymbolTable()
        child = SymbolTable(parent=parent)

        assert child.resolve("PI") == parent.resolve("PI")
        assert child.resolve("E") == parent.resolve("E")
