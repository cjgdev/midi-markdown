"""Unit tests for conditional alias evaluation (Stage 7).

Tests the ConditionalEvaluator class that handles @if/@elif/@else logic
in alias definitions.
"""

import pytest

from midi_markdown.alias.conditionals import ConditionalEvaluator
from midi_markdown.alias.errors import AliasError
from midi_markdown.parser.ast_nodes import ConditionalBranch


class TestConditionalEvaluator:
    """Test conditional expression evaluation."""

    @pytest.fixture
    def evaluator(self):
        """Create ConditionalEvaluator instance."""
        return ConditionalEvaluator()

    # ============================================
    # Basic Operator Tests
    # ============================================

    def test_equality_operator_true(self, evaluator):
        """Test == operator when condition is true."""
        condition = {"left": "device", "operator": "==", "right": "cortex"}
        params = {"device": "cortex"}
        assert evaluator.evaluate_condition(condition, params) is True

    def test_equality_operator_false(self, evaluator):
        """Test == operator when condition is false."""
        condition = {"left": "device", "operator": "==", "right": "cortex"}
        params = {"device": "h90"}
        assert evaluator.evaluate_condition(condition, params) is False

    def test_inequality_operator_true(self, evaluator):
        """Test != operator when condition is true."""
        condition = {"left": "mode", "operator": "!=", "right": 0}
        params = {"mode": 1}
        assert evaluator.evaluate_condition(condition, params) is True

    def test_inequality_operator_false(self, evaluator):
        """Test != operator when condition is false."""
        condition = {"left": "mode", "operator": "!=", "right": 1}
        params = {"mode": 1}
        assert evaluator.evaluate_condition(condition, params) is False

    def test_less_than_operator_true(self, evaluator):
        """Test < operator when condition is true."""
        condition = {"left": "value", "operator": "<", "right": 10}
        params = {"value": 5}
        assert evaluator.evaluate_condition(condition, params) is True

    def test_less_than_operator_false(self, evaluator):
        """Test < operator when condition is false."""
        condition = {"left": "value", "operator": "<", "right": 10}
        params = {"value": 15}
        assert evaluator.evaluate_condition(condition, params) is False

    def test_greater_than_operator_true(self, evaluator):
        """Test > operator when condition is true."""
        condition = {"left": "intensity", "operator": ">", "right": 50}
        params = {"intensity": 75}
        assert evaluator.evaluate_condition(condition, params) is True

    def test_greater_than_operator_false(self, evaluator):
        """Test > operator when condition is false."""
        condition = {"left": "intensity", "operator": ">", "right": 50}
        params = {"intensity": 25}
        assert evaluator.evaluate_condition(condition, params) is False

    def test_less_equal_operator_true(self, evaluator):
        """Test <= operator when condition is true."""
        condition = {"left": "value", "operator": "<=", "right": 10}
        params = {"value": 10}
        assert evaluator.evaluate_condition(condition, params) is True

    def test_less_equal_operator_false(self, evaluator):
        """Test <= operator when condition is false."""
        condition = {"left": "value", "operator": "<=", "right": 10}
        params = {"value": 11}
        assert evaluator.evaluate_condition(condition, params) is False

    def test_greater_equal_operator_true(self, evaluator):
        """Test >= operator when condition is true."""
        condition = {"left": "value", "operator": ">=", "right": 10}
        params = {"value": 10}
        assert evaluator.evaluate_condition(condition, params) is True

    def test_greater_equal_operator_false(self, evaluator):
        """Test >= operator when condition is false."""
        condition = {"left": "value", "operator": ">=", "right": 10}
        params = {"value": 9}
        assert evaluator.evaluate_condition(condition, params) is False

    # ============================================
    # Parameter Type Tests
    # ============================================

    def test_string_parameter_comparison(self, evaluator):
        """Test comparing string parameter values."""
        condition = {"left": "device", "operator": "==", "right": "cortex"}
        params = {"device": "cortex"}
        assert evaluator.evaluate_condition(condition, params) is True

    def test_numeric_parameter_comparison(self, evaluator):
        """Test comparing numeric parameter values."""
        condition = {"left": "mode", "operator": "==", "right": 0}
        params = {"mode": 0}
        assert evaluator.evaluate_condition(condition, params) is True

    def test_parameter_to_parameter_comparison(self, evaluator):
        """Test comparing two parameters."""
        condition = {"left": "value1", "operator": "==", "right": "value2"}
        params = {"value1": 10, "value2": 10}
        assert evaluator.evaluate_condition(condition, params) is True

    def test_parameter_to_literal_string(self, evaluator):
        """Test comparing parameter to literal string."""
        condition = {"left": "name", "operator": "==", "right": "test"}
        params = {"name": "test"}
        assert evaluator.evaluate_condition(condition, params) is True

    def test_parameter_to_literal_number(self, evaluator):
        """Test comparing parameter to literal number."""
        condition = {"left": "count", "operator": ">", "right": 5}
        params = {"count": 10}
        assert evaluator.evaluate_condition(condition, params) is True

    # ============================================
    # Branch Selection Tests
    # ============================================

    def test_select_if_branch(self, evaluator):
        """Test selecting the @if branch when condition is true."""
        branches = [
            ConditionalBranch(
                condition={"left": "mode", "operator": "==", "right": 0},
                commands=["pc 1.0"],
                branch_type="if",
            ),
            ConditionalBranch(condition=None, commands=["pc 1.1"], branch_type="else"),
        ]

        result = evaluator.select_branch(branches, {"mode": 0})
        assert result == ["pc 1.0"]

    def test_select_elif_branch(self, evaluator):
        """Test selecting an @elif branch when it matches."""
        branches = [
            ConditionalBranch(
                condition={"left": "mode", "operator": "==", "right": 0},
                commands=["pc 1.0"],
                branch_type="if",
            ),
            ConditionalBranch(
                condition={"left": "mode", "operator": "==", "right": 1},
                commands=["pc 1.1"],
                branch_type="elif",
            ),
            ConditionalBranch(condition=None, commands=["pc 1.2"], branch_type="else"),
        ]

        result = evaluator.select_branch(branches, {"mode": 1})
        assert result == ["pc 1.1"]

    def test_select_else_branch(self, evaluator):
        """Test selecting @else branch when no other matches."""
        branches = [
            ConditionalBranch(
                condition={"left": "mode", "operator": "==", "right": 0},
                commands=["pc 1.0"],
                branch_type="if",
            ),
            ConditionalBranch(
                condition={"left": "mode", "operator": "==", "right": 1},
                commands=["pc 1.1"],
                branch_type="elif",
            ),
            ConditionalBranch(condition=None, commands=["pc 1.9"], branch_type="else"),
        ]

        result = evaluator.select_branch(branches, {"mode": 5})
        assert result == ["pc 1.9"]

    def test_select_no_branch_matches(self, evaluator):
        """Test when no branch matches and no @else exists."""
        branches = [
            ConditionalBranch(
                condition={"left": "mode", "operator": "==", "right": 0},
                commands=["pc 1.0"],
                branch_type="if",
            ),
            ConditionalBranch(
                condition={"left": "mode", "operator": "==", "right": 1},
                commands=["pc 1.1"],
                branch_type="elif",
            ),
        ]

        result = evaluator.select_branch(branches, {"mode": 5})
        assert result is None

    def test_select_first_matching_branch(self, evaluator):
        """Test that first matching branch is selected (not last)."""
        branches = [
            ConditionalBranch(
                condition={"left": "value", "operator": ">", "right": 0},
                commands=["command1"],
                branch_type="if",
            ),
            ConditionalBranch(
                condition={"left": "value", "operator": ">", "right": 5},
                commands=["command2"],
                branch_type="elif",
            ),
        ]

        # value=10 matches both, should select first
        result = evaluator.select_branch(branches, {"value": 10})
        assert result == ["command1"]

    def test_select_multiple_elif_branches(self, evaluator):
        """Test selecting from multiple @elif branches."""
        branches = [
            ConditionalBranch(
                condition={"left": "mode", "operator": "==", "right": 0},
                commands=["mode0"],
                branch_type="if",
            ),
            ConditionalBranch(
                condition={"left": "mode", "operator": "==", "right": 1},
                commands=["mode1"],
                branch_type="elif",
            ),
            ConditionalBranch(
                condition={"left": "mode", "operator": "==", "right": 2},
                commands=["mode2"],
                branch_type="elif",
            ),
            ConditionalBranch(
                condition={"left": "mode", "operator": "==", "right": 3},
                commands=["mode3"],
                branch_type="elif",
            ),
        ]

        assert evaluator.select_branch(branches, {"mode": 2}) == ["mode2"]
        assert evaluator.select_branch(branches, {"mode": 3}) == ["mode3"]

    # ============================================
    # Error Handling Tests
    # ============================================

    def test_invalid_operator_error(self, evaluator):
        """Test error on invalid comparison operator."""
        condition = {"left": "value", "operator": "===", "right": 10}
        params = {"value": 10}

        with pytest.raises(AliasError) as exc_info:
            evaluator.evaluate_condition(condition, params)
        assert "invalid" in str(exc_info.value).lower()
        assert "operator" in str(exc_info.value).lower()

    def test_missing_condition_keys(self, evaluator):
        """Test error when condition dict is missing keys."""
        condition = {"left": "value", "operator": "=="}  # Missing 'right'
        params = {"value": 10}

        with pytest.raises(AliasError) as exc_info:
            evaluator.evaluate_condition(condition, params)
        assert "missing required keys" in str(exc_info.value).lower()

    def test_invalid_condition_format(self, evaluator):
        """Test error when condition is not a dict."""
        condition = "invalid"
        params = {"value": 10}

        with pytest.raises(AliasError) as exc_info:
            evaluator.evaluate_condition(condition, params)
        assert "invalid condition format" in str(exc_info.value).lower()

    def test_type_error_in_comparison(self, evaluator):
        """Test error when comparing incompatible types."""
        condition = {"left": "value", "operator": "<", "right": "string"}
        params = {"value": 10}

        with pytest.raises(AliasError) as exc_info:
            evaluator.evaluate_condition(condition, params)
        assert "type error" in str(exc_info.value).lower()

    # ============================================
    # Real-World Scenario Tests
    # ============================================

    def test_device_specific_routing(self, evaluator):
        """Test device-specific routing scenario."""
        branches = [
            ConditionalBranch(
                condition={"left": "device", "operator": "==", "right": "cortex"},
                commands=["pc 1.{preset}"],
                branch_type="if",
            ),
            ConditionalBranch(
                condition={"left": "device", "operator": "==", "right": "h90"},
                commands=["cc 1.71.{preset}"],
                branch_type="elif",
            ),
            ConditionalBranch(condition=None, commands=["pc 1.{preset}"], branch_type="else"),
        ]

        # Test cortex device
        assert evaluator.select_branch(branches, {"device": "cortex", "preset": 5}) == [
            "pc 1.{preset}"
        ]

        # Test h90 device
        assert evaluator.select_branch(branches, {"device": "h90", "preset": 10}) == [
            "cc 1.71.{preset}"
        ]

        # Test unknown device (uses else)
        assert evaluator.select_branch(branches, {"device": "other", "preset": 15}) == [
            "pc 1.{preset}"
        ]

    def test_range_based_velocity(self, evaluator):
        """Test range-based velocity curve selection."""
        branches = [
            ConditionalBranch(
                condition={"left": "velocity", "operator": "<", "right": 60},
                commands=["note {ch}.{note}.{velocity}", "cc {ch}.11.40"],
                branch_type="if",
            ),
            ConditionalBranch(
                condition={"left": "velocity", "operator": "<", "right": 100},
                commands=["note {ch}.{note}.{velocity}", "cc {ch}.11.80"],
                branch_type="elif",
            ),
            ConditionalBranch(
                condition=None,
                commands=["note {ch}.{note}.{velocity}", "cc {ch}.11.127"],
                branch_type="else",
            ),
        ]

        # Low velocity
        result = evaluator.select_branch(branches, {"velocity": 40, "ch": 1, "note": 60})
        assert len(result) == 2
        assert "cc {ch}.11.40" in result

        # Medium velocity
        result = evaluator.select_branch(branches, {"velocity": 80, "ch": 1, "note": 60})
        assert "cc {ch}.11.80" in result

        # High velocity
        result = evaluator.select_branch(branches, {"velocity": 120, "ch": 1, "note": 60})
        assert "cc {ch}.11.127" in result

    def test_enum_based_routing(self, evaluator):
        """Test enum-based routing mode selection."""
        # Enums resolved to numeric values by parameter binding
        branches = [
            ConditionalBranch(
                condition={"left": "mode", "operator": "==", "right": 0},
                commands=["cc {ch}.85.0", "cc {ch}.84.64"],  # Series
                branch_type="if",
            ),
            ConditionalBranch(
                condition={"left": "mode", "operator": "==", "right": 1},
                commands=["cc {ch}.85.1", "cc {ch}.84.64"],  # Parallel
                branch_type="elif",
            ),
            ConditionalBranch(
                condition={"left": "mode", "operator": "==", "right": 2},
                commands=["cc {ch}.85.2", "cc {ch}.84.0"],  # A only
                branch_type="elif",
            ),
            ConditionalBranch(
                condition=None,
                commands=["cc {ch}.85.3", "cc {ch}.84.127"],  # B only
                branch_type="else",
            ),
        ]

        # Test series mode (enum value 0)
        result = evaluator.select_branch(branches, {"mode": 0, "ch": 2})
        assert "cc {ch}.85.0" in result

        # Test parallel mode (enum value 1)
        result = evaluator.select_branch(branches, {"mode": 1, "ch": 2})
        assert "cc {ch}.85.1" in result

        # Test A only mode (enum value 2)
        result = evaluator.select_branch(branches, {"mode": 2, "ch": 2})
        assert "cc {ch}.85.2" in result

        # Test else (any other value)
        result = evaluator.select_branch(branches, {"mode": 99, "ch": 2})
        assert "cc {ch}.85.3" in result
