"""
Unit tests for CommandExpander initialization.

Phase 4: Tests expander initialization and component creation.
"""

from midi_markdown.expansion.expander import CommandExpander
from midi_markdown.expansion.variables import SymbolTable


class TestCommandExpanderInit:
    """Test CommandExpander initialization."""

    def test_default_initialization(self):
        """Test expander with default parameters."""
        expander = CommandExpander()

        assert expander.ppq == 480
        assert expander.tempo == 120.0
        assert expander.source_file == "<unknown>"
        assert expander.current_time == 0
        assert len(expander.events) == 0

    def test_custom_initialization(self):
        """Test expander with custom parameters."""
        expander = CommandExpander(ppq=960, tempo=140.0, source_file="test.mmd")

        assert expander.ppq == 960
        assert expander.tempo == 140.0
        assert expander.source_file == "test.mmd"

    def test_component_creation(self):
        """Test that sub-components are created."""
        expander = CommandExpander()

        assert isinstance(expander.symbol_table, SymbolTable)
        assert expander.loop_expander is not None
        assert expander.sweep_expander is not None
        assert expander.computation_engine is not None
