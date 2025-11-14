"""Unit tests for safe computation engine (Stage 6).

Tests secure evaluation of mathematical expressions in computed value blocks.
"""

import pytest

from midi_markdown.alias.computation import (
    ComputationError,
    SafeComputationEngine,
)


class TestSafeComputationEngine:
    """Test safe computation engine."""

    @pytest.fixture
    def engine(self):
        """Create computation engine instance."""
        return SafeComputationEngine()

    # ============================================
    # Basic Arithmetic Tests
    # ============================================

    @pytest.mark.parametrize(
        ("expression", "expected"),
        [
            ("10 + 5", 15),
            ("20 - 8", 12),
            ("4 * 7", 28),
            ("100 / 4", 25.0),
            ("17 // 5", 3),
            ("17 % 5", 2),
            ("2 ** 8", 256),
        ],
    )
    def test_basic_arithmetic(self, engine, expression, expected):
        """Test basic arithmetic operators (+, -, *, /, //, %, **)."""
        result = engine.evaluate_expression(expression, {})
        assert result == expected

    def test_complex_expression(self, engine):
        """Test complex arithmetic expression."""
        result = engine.evaluate_expression("(120 - 40) * 127 / 260", {})
        assert pytest.approx(result, 0.01) == 39.07

    def test_order_of_operations(self, engine):
        """Test order of operations (PEMDAS)."""
        result = engine.evaluate_expression("2 + 3 * 4", {})
        assert result == 14  # Not 20

    def test_parentheses(self, engine):
        """Test parentheses override order of operations."""
        result = engine.evaluate_expression("(2 + 3) * 4", {})
        assert result == 20

    def test_unary_operators(self, engine):
        """Test unary plus and minus."""
        assert engine.evaluate_expression("+5", {}) == 5
        assert engine.evaluate_expression("-5", {}) == -5
        assert engine.evaluate_expression("-(10 + 5)", {}) == -15

    # ============================================
    # Parameter Substitution Tests
    # ============================================

    def test_single_parameter(self, engine):
        """Test expression with single parameter."""
        result = engine.evaluate_expression("val * 2", {"val": 10})
        assert result == 20

    def test_multiple_parameters(self, engine):
        """Test expression with multiple parameters."""
        result = engine.evaluate_expression("a + b * c", {"a": 5, "b": 3, "c": 4})
        assert result == 17

    def test_parameter_in_complex_expression(self, engine):
        """Test parameter in complex expression (BPM to MIDI)."""
        # Convert BPM 40-300 to MIDI 0-127
        result = engine.evaluate_expression("int((bpm - 40) * 127 / 260)", {"bpm": 120})
        assert result == 39

    # ============================================
    # Built-in Function Tests
    # ============================================

    @pytest.mark.parametrize(
        ("expression", "expected"),
        [
            ("int(3.7)", 3),
            ("int(-2.5)", -2),
            ("float(5)", 5.0),
            ("float(10)", 10.0),
            ("abs(-10)", 10),
            ("abs(10)", 10),
            ("abs(-5.5)", 5.5),
            ("round(3.7)", 4),
            ("round(3.2)", 3),
            ("round(2.5)", 2),
            ("min(5, 10, 3)", 3),
            ("min(100, 50)", 50),
            ("max(5, 10, 3)", 10),
            ("max(100, 50)", 100),
        ],
    )
    def test_builtin_functions(self, engine, expression, expected):
        """Test Python built-in functions (int, float, abs, round, min, max)."""
        result = engine.evaluate_expression(expression, {})
        assert result == expected

    # ============================================
    # MIDI Helper Function Tests
    # ============================================

    def test_clamp_function(self, engine):
        """Test clamp() helper function."""
        assert engine.evaluate_expression("clamp(50, 0, 127)", {}) == 50
        assert engine.evaluate_expression("clamp(-10, 0, 127)", {}) == 0
        assert engine.evaluate_expression("clamp(200, 0, 127)", {}) == 127

    def test_scale_range_function(self, engine):
        """Test scale_range() helper function."""
        # Scale 0-100 to 0-127
        result = engine.evaluate_expression("scale_range(50, 0, 100, 0, 127)", {})
        assert pytest.approx(result, 0.1) == 63.5

        # Scale BPM 40-300 to MIDI 0-127
        result = engine.evaluate_expression("scale_range(120, 40, 300, 0, 127)", {})
        assert pytest.approx(result, 0.1) == 39.07

    def test_scale_range_zero_input_range(self, engine):
        """Test scale_range with zero input range (edge case)."""
        result = engine.evaluate_expression("scale_range(50, 50, 50, 0, 127)", {})
        assert result == 0  # Returns out_min when input range is zero

    def test_msb_function(self, engine):
        """Test msb() helper function for 14-bit MIDI."""
        result = engine.evaluate_expression("msb(8192)", {})
        assert result == 64  # 8192 >> 7 = 64

    def test_lsb_function(self, engine):
        """Test lsb() helper function for 14-bit MIDI."""
        result = engine.evaluate_expression("lsb(8192)", {})
        assert result == 0  # 8192 & 0x7F = 0

    def test_msb_lsb_roundtrip(self, engine):
        """Test MSB/LSB can represent 14-bit values."""
        value = 10000
        msb = engine.evaluate_expression("msb(val)", {"val": value})
        lsb = engine.evaluate_expression("lsb(val)", {"val": value})

        # Reconstruct value
        reconstructed = (msb << 7) | lsb
        assert reconstructed == value

    # ============================================
    # Lark Tree Conversion Tests
    # ============================================

    def test_lark_tree_tuple_addition(self, engine):
        """Test converting Lark tuple tree for addition."""
        tree = ("add", 10, 5)
        result = engine.lark_tree_to_python(tree)
        assert result == "10 + 5"

    def test_lark_tree_tuple_multiplication(self, engine):
        """Test converting Lark tuple tree for multiplication."""
        tree = ("mul", 4, 7)
        result = engine.lark_tree_to_python(tree)
        assert result == "4 * 7"

    def test_lark_tree_tuple_negation(self, engine):
        """Test converting Lark tuple tree for unary negation."""
        tree = ("neg", 5)
        result = engine.lark_tree_to_python(tree)
        assert result == "-5"

    def test_lark_tree_tuple_variable(self, engine):
        """Test converting Lark tuple tree for variable reference."""
        tree = ("var", "val")
        result = engine.lark_tree_to_python(tree)
        assert result == "val"

    def test_lark_tree_complex_expression(self, engine):
        """Test converting complex nested Lark tree."""
        # Represents: (val + 10) * 2
        from lark import Tree

        tree = ("mul", Tree("paren", [("add", Tree("var_ref", [("var", "val")]), 10.0)]), 2.0)
        result = engine.lark_tree_to_python(tree)
        assert result == "(val + 10.0) * 2.0"

    def test_lark_tree_evaluation(self, engine):
        """Test full pipeline: Lark tree -> Python -> evaluation."""
        from lark import Tree

        tree = ("mul", Tree("paren", [("add", Tree("var_ref", [("var", "val")]), 10.0)]), 2.0)
        expr_str = engine.lark_tree_to_python(tree)
        result = engine.evaluate_expression(expr_str, {"val": 50})
        assert result == 120.0

    # ============================================
    # Security Tests
    # ============================================

    def test_block_import(self, engine):
        """Test that import statements are blocked."""
        with pytest.raises(ComputationError) as exc_info:
            engine.evaluate_expression("__import__('os')", {})
        assert "not allowed" in str(exc_info.value).lower()

    def test_block_attribute_access(self, engine):
        """Test that attribute access is blocked."""
        with pytest.raises(ComputationError) as exc_info:
            engine.evaluate_expression("(10).__class__", {})
        assert "attribute" in str(exc_info.value).lower()

    def test_block_dangerous_function(self, engine):
        """Test that dangerous functions are blocked."""
        with pytest.raises(ComputationError) as exc_info:
            engine.evaluate_expression("eval('1+1')", {})
        assert "not allowed" in str(exc_info.value).lower()

    def test_block_exec(self, engine):
        """Test that exec is blocked."""
        with pytest.raises(ComputationError) as exc_info:
            engine.evaluate_expression("exec('print(1)')", {})
        assert "not allowed" in str(exc_info.value).lower()

    def test_allowed_functions_only(self, engine):
        """Test that only whitelisted functions are allowed."""
        # These should work
        engine.evaluate_expression("int(5)", {})
        engine.evaluate_expression("abs(-5)", {})
        engine.evaluate_expression("clamp(10, 0, 127)", {})

        # This should fail
        with pytest.raises(ComputationError):
            engine.evaluate_expression("len([1,2,3])", {})

    # ============================================
    # Error Handling Tests
    # ============================================

    def test_syntax_error(self, engine):
        """Test handling of syntax errors."""
        with pytest.raises(ComputationError) as exc_info:
            engine.evaluate_expression("10 +* 5", {})
        assert "syntax error" in str(exc_info.value).lower()

    def test_division_by_zero(self, engine):
        """Test handling of division by zero."""
        with pytest.raises(ComputationError) as exc_info:
            engine.evaluate_expression("10 / 0", {})
        assert "division by zero" in str(exc_info.value).lower()

    def test_undefined_variable(self, engine):
        """Test handling of undefined variable."""
        with pytest.raises(ComputationError) as exc_info:
            engine.evaluate_expression("x + 10", {})
        assert "undefined variable" in str(exc_info.value).lower()

    def test_type_error_in_function(self, engine):
        """Test handling of type errors in function calls."""
        with pytest.raises(ComputationError) as exc_info:
            engine.evaluate_expression("clamp(10)", {})  # Missing required arguments
        assert "error calling" in str(exc_info.value).lower()

    def test_operation_limit(self, engine):
        """Test that operation limit is enforced."""
        # Note: Python's recursion limit (~1000) prevents us from reaching 10k operations
        # via deeply nested expressions. In practice, the operation counter protects against
        # computationally expensive operations that don't necessarily hit recursion limits.
        # For testing, we verify the counter mechanism works by checking it increments.

        # Test that operation counting works
        engine.operation_count = 0
        engine.evaluate_expression("1 + 2 + 3", {})
        # Should have counted: 3x Constant, 2x BinOp = 5 nodes
        assert engine.operation_count >= 5

        # Test that exceeding the limit raises an error
        # We'll temporarily lower the limit to trigger it without deep recursion
        original_limit = engine.MAX_OPERATIONS
        engine.MAX_OPERATIONS = 5
        try:
            with pytest.raises(ComputationError) as exc_info:
                engine.evaluate_expression("1 + 2 + 3 + 4 + 5 + 6", {})
            assert "operation limit exceeded" in str(exc_info.value).lower()
        finally:
            engine.MAX_OPERATIONS = original_limit

    # ============================================
    # Real-World Use Case Tests
    # ============================================

    def test_bpm_to_midi_conversion(self, engine):
        """Test BPM to MIDI value conversion (real-world use case)."""
        # Convert BPM 40-300 to MIDI 0-127
        test_cases = [
            (40, 0),  # Min BPM
            (120, 39),  # Mid BPM
            (170, 63),  # Mid-high BPM
            (300, 127),  # Max BPM
        ]

        for bpm, expected_midi in test_cases:
            result = engine.evaluate_expression("int((bpm - 40) * 127 / 260)", {"bpm": bpm})
            assert result == expected_midi, f"BPM {bpm} should map to MIDI {expected_midi}"

    def test_percentage_to_midi(self, engine):
        """Test percentage to MIDI value conversion."""
        # Scale 0-100% to 0-127
        test_cases = [
            (0, 0),
            (50, 63),
            (100, 127),
        ]

        for percent, expected in test_cases:
            result = engine.evaluate_expression("int(percent * 127 / 100)", {"percent": percent})
            assert result == expected

    def test_expression_preset_number(self, engine):
        """Test computed preset number (setlist * 100 + preset)."""
        result = engine.evaluate_expression("setlist * 100 + preset", {"setlist": 2, "preset": 35})
        assert result == 235

    def test_velocity_curve(self, engine):
        """Test velocity curve application."""
        # Apply exponential curve: vel^2 / 127
        result = engine.evaluate_expression("int(vel * vel / 127)", {"vel": 90})
        assert result == 63  # 90^2 / 127 = 63.78 -> 63

    def test_14bit_midi_split(self, engine):
        """Test splitting 14-bit value into MSB/LSB."""
        value = 10000
        msb = engine.evaluate_expression("msb(val)", {"val": value})
        lsb = engine.evaluate_expression("lsb(val)", {"val": value})

        assert msb == 78  # (10000 >> 7) & 0x7F
        assert lsb == 16  # 10000 & 0x7F

        # Verify reconstruction
        assert (msb << 7) | lsb == value
