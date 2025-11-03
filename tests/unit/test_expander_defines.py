"""
Unit tests for CommandExpander @define processing.

Phase 4: Tests @define statement processing and variable definition.
"""

import pytest

from midi_markdown.expansion.errors import ExpansionError


class TestDefineProcessing:
    """Test @define statement processing."""

    def test_simple_define(self, expander):
        """Test defining a literal integer."""
        nodes = [{"type": "define", "name": "CHANNEL", "value": 1, "line": 1}]

        expander.process_ast(nodes)

        assert expander.symbol_table.resolve("CHANNEL") == 1
        assert expander.stats.defines_processed == 1

    def test_define_with_expression(self, expander):
        """Test defining with arithmetic expression."""
        nodes = [
            {"type": "define", "name": "BASE", "value": 10, "line": 1},
            {"type": "define", "name": "RESULT", "value": ("add", 10, 5), "line": 2},
        ]

        expander.process_ast(nodes)

        assert expander.symbol_table.resolve("RESULT") == 15

    def test_define_variable_reference(self, expander):
        """Test defining using another variable."""
        nodes = [
            {"type": "define", "name": "BASE", "value": 42, "line": 1},
            {"type": "define", "name": "COPY", "value": ("var", "BASE"), "line": 2},
        ]

        expander.process_ast(nodes)

        assert expander.symbol_table.resolve("COPY") == 42

    def test_define_updates_stats(self, expander):
        """Test that defines_processed counter increments."""
        nodes = [
            {"type": "define", "name": "A", "value": 1, "line": 1},
            {"type": "define", "name": "B", "value": 2, "line": 2},
            {"type": "define", "name": "C", "value": 3, "line": 3},
        ]

        expander.process_ast(nodes)

        assert expander.stats.defines_processed == 3

    def test_define_missing_name_error(self, expander):
        """Test error when define is missing variable name."""
        nodes = [
            {"type": "define", "value": 42, "line": 1}  # Missing 'name'
        ]

        with pytest.raises(ExpansionError, match="missing variable name"):
            expander.process_ast(nodes)

    def test_define_constant_redefinition_error(self, expander):
        """Test error when trying to redefine built-in constants."""
        nodes = [{"type": "define", "name": "PI", "value": 3, "line": 1}]

        with pytest.raises(Exception):  # SymbolTable raises ValueError
            expander.process_ast(nodes)
