"""
Unit tests for CommandExpander variable substitution.

Phase 4: Tests variable substitution in commands.
"""

import pytest

from midi_markdown.expansion.errors import UndefinedVariableError


class TestVariableSubstitution:
    """Test variable substitution in commands."""

    def test_substitute_single_variable(self, expander):
        """Test replacing single variable reference."""
        nodes = [
            {"type": "define", "name": "PRESET", "value": 42, "line": 1},
            {"type": "pc", "channel": 1, "data1": ("var", "PRESET")},
        ]

        events = expander.process_ast(nodes)

        assert events[0]["data1"] == 42
        assert expander.stats.variables_substituted == 1

    def test_substitute_multiple_variables(self, expander):
        """Test multiple variables in one command."""
        nodes = [
            {"type": "define", "name": "CH", "value": 2, "line": 1},
            {"type": "define", "name": "VAL", "value": 100, "line": 2},
            {"type": "cc", "channel": ("var", "CH"), "data1": 7, "data2": ("var", "VAL")},
        ]

        events = expander.process_ast(nodes)

        assert events[0]["channel"] == 2
        assert events[0]["data2"] == 100
        assert expander.stats.variables_substituted == 2

    def test_substitute_nested_dict(self, expander):
        """Test recursive substitution in nested dicts."""
        nodes = [
            {"type": "define", "name": "VALUE", "value": 99, "line": 1},
            {
                "type": "cc",
                "channel": 1,
                "data1": 7,
                "data2": ("var", "VALUE"),
                "metadata": {"nested_value": ("var", "VALUE")},
            },
        ]

        events = expander.process_ast(nodes)

        # Check both direct and nested substitution
        assert events[0]["data2"] == 99
        assert events[0]["metadata"]["nested_value"] == 99

    def test_substitute_in_list(self, expander):
        """Test substitution in list values."""
        nodes = [
            {"type": "define", "name": "A", "value": 10, "line": 1},
            {"type": "define", "name": "B", "value": 20, "line": 2},
            {
                "type": "cc",
                "channel": 1,
                "data1": 7,
                "data2": 100,
                "test_list": [("var", "A"), 5, ("var", "B")],
            },
        ]

        events = expander.process_ast(nodes)

        assert events[0]["test_list"] == [10, 5, 20]

    def test_undefined_variable_error(self, expander):
        """Test UndefinedVariableError with suggestions."""
        nodes = [
            {"type": "define", "name": "PRESET", "value": 10, "line": 1},
            {"type": "pc", "channel": 1, "data1": ("var", "PRSET")},  # Typo!
        ]

        with pytest.raises(UndefinedVariableError) as exc_info:
            expander.process_ast(nodes)

        # Should suggest similar name
        assert "PRSET" in str(exc_info.value)

    def test_substitution_stats(self, expander):
        """Test variables_substituted counter."""
        nodes = [
            {"type": "define", "name": "A", "value": 1, "line": 1},
            {"type": "define", "name": "B", "value": 2, "line": 2},
            {"type": "pc", "channel": ("var", "A"), "data1": ("var", "B")},
            {"type": "cc", "channel": ("var", "A"), "data1": 7, "data2": ("var", "B")},
        ]

        expander.process_ast(nodes)

        # 2 in first command, 2 in second = 4 total
        assert expander.stats.variables_substituted == 4
