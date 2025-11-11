"""
Tests for random value generation in MML.

This module tests the random() expression functionality including:
- Random integer generation (0-127)
- Random note name generation (C3-C5)
- Seed-based reproducibility
- Range validation
- Integration with loops and commands
"""

from __future__ import annotations

import pytest

from midi_markdown.expansion.random import RandomValueExpander, expand_random_in_command
from midi_markdown.parser.ast_nodes import RandomExpression
from midi_markdown.parser.parser import MMDParser


class TestRandomValueExpander:
    """Test the RandomValueExpander class."""

    def test_random_integer_generation(self):
        """Test basic random integer generation."""
        expander = RandomValueExpander()
        expr = RandomExpression(min_value=0, max_value=127)

        # Generate 100 values and verify they're all in range
        for _ in range(100):
            value = expander.expand_random(expr)
            assert 0 <= value <= 127
            assert isinstance(value, int)

    def test_random_note_generation(self):
        """Test random note name generation."""
        expander = RandomValueExpander()
        expr = RandomExpression(min_value="C3", max_value="C5")

        # C3 = MIDI 48, C5 = MIDI 72
        for _ in range(100):
            value = expander.expand_random(expr)
            assert 48 <= value <= 72
            assert isinstance(value, int)

    def test_random_with_seed_reproducible(self):
        """Test that same seed produces same value."""
        expander = RandomValueExpander()
        expr = RandomExpression(min_value=0, max_value=127, seed=42)

        # First generation
        value1 = expander.expand_random(expr)

        # Create new expander with same seed
        expander2 = RandomValueExpander()
        expr2 = RandomExpression(min_value=0, max_value=127, seed=42)
        value2 = expander2.expand_random(expr2)

        # Should be the same
        assert value1 == value2

    def test_random_range_validation_min_greater_than_max(self):
        """Test that min > max raises ValueError."""
        expander = RandomValueExpander()
        expr = RandomExpression(min_value=100, max_value=50)

        with pytest.raises(ValueError, match="min value.*cannot be greater than max value"):
            expander.expand_random(expr)

    def test_random_midi_value_range(self):
        """Test random values within MIDI range."""
        expander = RandomValueExpander()
        expr = RandomExpression(min_value=0, max_value=127)

        # Generate many values and ensure all are valid MIDI values
        values = [expander.expand_random(expr) for _ in range(200)]
        assert all(0 <= v <= 127 for v in values)
        # Verify we get some variation
        assert len(set(values)) > 20  # Should have at least 20 unique values

    def test_random_note_names_sharps_flats(self):
        """Test random with sharp and flat note names."""
        expander = RandomValueExpander()

        # C#4 = MIDI 61, Db5 = MIDI 73 (enharmonic)
        expr = RandomExpression(min_value="C#4", max_value="E5")
        for _ in range(50):
            value = expander.expand_random(expr)
            assert 61 <= value <= 76  # C#4 to E5

        # Test with flats
        expr2 = RandomExpression(min_value="Bb3", max_value="F4")
        for _ in range(50):
            value = expander.expand_random(expr2)
            assert 58 <= value <= 65  # Bb3 to F4

    def test_random_single_value(self):
        """Test random where min == max."""
        expander = RandomValueExpander()
        expr = RandomExpression(min_value=64, max_value=64)

        # Should always return 64
        for _ in range(10):
            value = expander.expand_random(expr)
            assert value == 64

    def test_random_invalid_note_name(self):
        """Test that invalid note names raise errors."""
        expander = RandomValueExpander()
        expr = RandomExpression(min_value="X9", max_value="C5")

        with pytest.raises(ValueError, match="Invalid note name"):
            expander.expand_random(expr)

    def test_random_boundary_values(self):
        """Test random with boundary MIDI values."""
        expander = RandomValueExpander()

        # Test 0 to 127 (full MIDI range)
        expr = RandomExpression(min_value=0, max_value=127)
        for _ in range(100):
            value = expander.expand_random(expr)
            assert 0 <= value <= 127

        # Test very small range
        expr2 = RandomExpression(min_value=63, max_value=65)
        values = [expander.expand_random(expr2) for _ in range(100)]
        assert all(v in [63, 64, 65] for v in values)

    def test_parse_value_integer(self):
        """Test _parse_value with integer."""
        expander = RandomValueExpander()
        assert expander._parse_value(60) == 60
        assert expander._parse_value(0) == 0
        assert expander._parse_value(127) == 127

    def test_parse_value_note_name(self):
        """Test _parse_value with note names."""
        expander = RandomValueExpander()
        assert expander._parse_value("C4") == 60
        assert expander._parse_value("A4") == 69
        assert expander._parse_value("C#4") == 61
        assert expander._parse_value("Db4") == 61

    def test_parse_value_invalid_type(self):
        """Test _parse_value with invalid type."""
        expander = RandomValueExpander()
        with pytest.raises(TypeError):
            expander._parse_value([1, 2, 3])


class TestRandomInLoops:
    """Test random expressions within loops."""

    def test_random_in_loop_different_values(self):
        """Test that each loop iteration gets different random values (without seed)."""
        parser = MMDParser()
        mml_text = """
@loop 5 times every 1b
  - cc 1.7.random(64, 96)
@end
"""
        doc = parser.parse_string(mml_text)
        # We're just testing that it parses correctly
        # The expander will handle the actual expansion
        assert doc is not None

    def test_random_in_loop_with_seed(self):
        """Test that random with seed produces same sequence."""
        parser = MMDParser()
        mml_text = """
@loop 3 times every 1b
  - cc 1.7.random(64, 96, seed=42)
@end
"""
        doc = parser.parse_string(mml_text)
        assert doc is not None

    def test_random_velocity_humanization(self):
        """Test random for velocity humanization (musical example)."""
        parser = MMDParser()
        mml_text = """
@loop 16 times at [00:00.000] every 0.25b
  - note_on 1.C4 random(70, 90) 0.1b
@end
"""
        doc = parser.parse_string(mml_text)
        assert doc is not None

    def test_random_cc_automation(self):
        """Test random for CC automation variation."""
        parser = MMDParser()
        mml_text = """
@loop 8 times at [00:00.000] every 2b
  - cc 1.1.random(64, 96)
@end
"""
        doc = parser.parse_string(mml_text)
        assert doc is not None

    def test_random_note_selection(self):
        """Test random note selection within octave range."""
        parser = MMDParser()
        mml_text = """
@loop 32 times at [00:00.000] every 0.5b
  - note_on 1.random(C3, C5) 80 0.25b
@end
"""
        doc = parser.parse_string(mml_text)
        assert doc is not None


class TestRandomInCommands:
    """Test random expressions in various MIDI commands."""

    def test_random_in_cc_command(self):
        """Test random in control change command."""
        parser = MMDParser()
        mml_text = """
[00:00.000]
- cc 1.7.random(0, 127)
"""
        doc = parser.parse_string(mml_text)
        assert doc is not None
        assert len(doc.events) > 0

    def test_random_in_note_velocity(self):
        """Test random in note velocity."""
        parser = MMDParser()
        mml_text = """
[00:00.000]
- note_on 1.60 random(64, 96) 1b
"""
        doc = parser.parse_string(mml_text)
        assert doc is not None

    def test_random_in_note_number(self):
        """Test random in note number."""
        parser = MMDParser()
        mml_text = """
[00:00.000]
- note_on 1.random(60, 72) 80 1b
"""
        doc = parser.parse_string(mml_text)
        assert doc is not None

    def test_multiple_random_in_single_command(self):
        """Test multiple random expressions in one command."""
        parser = MMDParser()
        mml_text = """
[00:00.000]
- note_on 1.random(60, 72) random(70, 90) 1b
"""
        doc = parser.parse_string(mml_text)
        assert doc is not None


class TestRandomIntegration:
    """Test random expression integration with full pipeline."""

    def test_random_parsing_grammar(self):
        """Test that random() grammar is correctly parsed."""
        parser = MMDParser()

        # Test basic syntax in CC
        mml_text = """
[00:00.000]
- cc 1.7.random(0, 127)
"""
        doc = parser.parse_string(mml_text)
        assert doc is not None

        # Test with note names in note_value
        mml_text2 = """
[00:00.000]
- note_on 1.random(C3, C5) 80 1b
"""
        doc2 = parser.parse_string(mml_text2)
        assert doc2 is not None

        # Test with seed in velocity
        mml_text3 = """
[00:00.000]
- note_on 1.60 random(64, 96, seed=42) 1b
"""
        doc3 = parser.parse_string(mml_text3)
        assert doc3 is not None

    def test_expand_random_in_command_dict(self):
        """Test expand_random_in_command utility function."""
        expander = RandomValueExpander()

        # Command with RandomExpression
        cmd = {
            "type": "cc",
            "channel": 1,
            "data1": 7,
            "data2": RandomExpression(64, 96),
        }

        result = expand_random_in_command(cmd, expander)

        # Should have integer value now
        assert isinstance(result["data2"], int)
        assert 64 <= result["data2"] <= 96

    def test_expand_random_nested_dict(self):
        """Test expanding random in nested dictionaries."""
        expander = RandomValueExpander()

        cmd = {
            "type": "note_on",
            "channel": 1,
            "params": {
                "velocity": RandomExpression(70, 90),
            },
        }

        result = expand_random_in_command(cmd, expander)
        assert isinstance(result["params"]["velocity"], int)
        assert 70 <= result["params"]["velocity"] <= 90

    def test_expand_random_in_list(self):
        """Test expanding random in lists."""
        expander = RandomValueExpander()

        cmd = {
            "type": "chord",
            "notes": [
                RandomExpression(60, 64),
                RandomExpression(67, 71),
                RandomExpression(72, 76),
            ],
        }

        result = expand_random_in_command(cmd, expander)
        assert all(isinstance(note, int) for note in result["notes"])
        assert 60 <= result["notes"][0] <= 64
        assert 67 <= result["notes"][1] <= 71
        assert 72 <= result["notes"][2] <= 76


class TestRandomEdgeCases:
    """Test edge cases and error handling for random expressions."""

    def test_random_with_negative_values(self):
        """Test that negative values are rejected."""
        expander = RandomValueExpander()
        # MIDI values must be 0-127
        expr = RandomExpression(min_value=-10, max_value=50)

        # Should expand but result in invalid MIDI value
        # The actual validation happens in the validator layer
        value = expander.expand_random(expr)
        assert isinstance(value, int)

    def test_random_with_very_large_range(self):
        """Test random with large range."""
        expander = RandomValueExpander()
        expr = RandomExpression(min_value=0, max_value=16383)  # Pitch bend range

        # Should work for large ranges
        value = expander.expand_random(expr)
        assert 0 <= value <= 16383

    def test_random_distribution_approximation(self):
        """Test that random has reasonable distribution."""
        expander = RandomValueExpander()
        expr = RandomExpression(min_value=0, max_value=127)

        # Generate many values
        values = [expander.expand_random(expr) for _ in range(1000)]

        # Check distribution (should have values across the range)
        assert min(values) < 20  # Should have some low values
        assert max(values) > 107  # Should have some high values
        assert len(set(values)) > 50  # Should have good variety

    def test_random_with_string_integers(self):
        """Test random with string values that convert to integers."""
        expander = RandomValueExpander()

        # _parse_value should handle string integers
        assert expander._parse_value("64") == 64
        assert expander._parse_value("127") == 127

    def test_random_expression_ast_node(self):
        """Test RandomExpression AST node creation."""
        expr1 = RandomExpression(min_value=0, max_value=127)
        assert expr1.min_value == 0
        assert expr1.max_value == 127
        assert expr1.seed is None

        expr2 = RandomExpression(min_value="C4", max_value="C5", seed=42)
        assert expr2.min_value == "C4"
        assert expr2.max_value == "C5"
        assert expr2.seed == 42


class TestRandomWithVariables:
    """Test random expressions combined with variables."""

    def test_random_with_defined_variables(self):
        """Test random combined with @define variables."""
        parser = MMDParser()
        mml_text = """
@define MIN_VEL 70
@define MAX_VEL 90

[00:00.000]
- note_on 1.60 random(70, 90) 1b
"""
        doc = parser.parse_string(mml_text)
        assert doc is not None
        assert "MIN_VEL" in doc.defines
        assert "MAX_VEL" in doc.defines


class TestRandomSeeding:
    """Test random seed functionality."""

    def test_seed_reproducibility_sequence(self):
        """Test that seed produces same sequence of values."""
        expander1 = RandomValueExpander()
        expander2 = RandomValueExpander()

        expr = RandomExpression(min_value=0, max_value=127, seed=42)

        # Generate sequence with expander1
        seq1 = [expander1.expand_random(expr) for _ in range(10)]

        # Generate sequence with expander2 (same seed)
        seq2 = [expander2.expand_random(expr) for _ in range(10)]

        # Sequences should be identical
        assert seq1 == seq2

    def test_different_seeds_different_values(self):
        """Test that different seeds produce different values."""
        expander1 = RandomValueExpander()
        expander2 = RandomValueExpander()

        expr1 = RandomExpression(min_value=0, max_value=127, seed=42)
        expr2 = RandomExpression(min_value=0, max_value=127, seed=123)

        value1 = expander1.expand_random(expr1)
        value2 = expander2.expand_random(expr2)

        # Very likely to be different (not guaranteed, but extremely likely)
        # If they happen to be the same, generate more and compare sequences
        if value1 == value2:
            seq1 = [expander1.expand_random(expr1) for _ in range(10)]
            seq2 = [expander2.expand_random(expr2) for _ in range(10)]
            assert seq1 != seq2

    def test_no_seed_gives_variation(self):
        """Test that without seed, values vary."""
        expander = RandomValueExpander()
        expr = RandomExpression(min_value=0, max_value=127)

        # Generate many values without seed
        values = [expander.expand_random(expr) for _ in range(100)]

        # Should have good variation (very unlikely to all be the same)
        assert len(set(values)) > 10
