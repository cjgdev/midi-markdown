"""
Tests for float range parameters in alias system.

Tests that aliases can have float range parameters like {freq:0.5-8.0}.
"""

import pytest

from midi_markdown.alias.resolver import AliasError, AliasResolver
from midi_markdown.parser.ast_nodes import AliasDefinition
from midi_markdown.parser.parser import MMDParser


class TestFloatRangeParameters:
    """Tests for float range parameters in aliases."""

    @pytest.mark.unit
    def test_float_range_parameter_parsing(self):
        """Test that float ranges are correctly parsed from alias definitions."""
        mml = """@alias vibrato {ch} {freq:0.5-8.0} "Apply vibrato with frequency"
  - cc {ch}.1.wave(sine, 64, freq={freq}, depth=10)
@end

[00:00.000]
- vibrato 1 5.5
"""
        parser = MMDParser()
        doc = parser.parse_string(mml)

        # Check that the alias was parsed with float min/max
        assert len(doc.aliases) == 1
        alias_def = doc.aliases["vibrato"]
        assert alias_def.name == "vibrato"
        assert len(alias_def.parameters) == 2

        # Check the freq parameter has float range
        freq_param = alias_def.parameters[1]
        assert freq_param["name"] == "freq"
        assert freq_param["type"] == "range"
        assert freq_param["min"] == 0.5
        assert freq_param["max"] == 8.0

    @pytest.mark.unit
    def test_float_parameter_validation_within_range(self):
        """Test that float values within range are accepted."""
        alias_def = AliasDefinition(
            name="vibrato",
            parameters=[
                {
                    "name": "ch",
                    "type": "generic",
                    "min": 1,
                    "max": 16,
                    "default": None,
                    "enum_values": None,
                },
                {
                    "name": "freq",
                    "type": "range",
                    "min": 0.5,
                    "max": 8.0,
                    "default": None,
                    "enum_values": None,
                },
            ],
            commands=["cc.{ch}.1.wave(sine, 64, freq={freq}, depth=10)"],
            description="Apply vibrato",
        )

        resolver = AliasResolver({"vibrato": alias_def})

        # Test various float values within range
        resolver.resolve("vibrato", [1, 0.5], source_line=10)  # Min
        resolver.resolve("vibrato", [1, 5.5], source_line=10)  # Middle
        resolver.resolve("vibrato", [1, 8.0], source_line=10)  # Max
        resolver.resolve("vibrato", [1, 3.75], source_line=10)  # Arbitrary

    @pytest.mark.unit
    def test_float_parameter_validation_out_of_range(self):
        """Test that float values outside range are rejected."""
        alias_def = AliasDefinition(
            name="vibrato",
            parameters=[
                {
                    "name": "ch",
                    "type": "generic",
                    "min": 1,
                    "max": 16,
                    "default": None,
                    "enum_values": None,
                },
                {
                    "name": "freq",
                    "type": "range",
                    "min": 0.5,
                    "max": 8.0,
                    "default": None,
                    "enum_values": None,
                },
            ],
            commands=["cc.{ch}.1.wave(sine, 64, freq={freq}, depth=10)"],
            description="Apply vibrato",
        )

        resolver = AliasResolver({"vibrato": alias_def})

        # Test values outside range
        with pytest.raises(AliasError, match="out of range"):
            resolver.resolve("vibrato", [1, 0.4], source_line=10)  # Below min

        with pytest.raises(AliasError, match="out of range"):
            resolver.resolve("vibrato", [1, 8.1], source_line=10)  # Above max

        with pytest.raises(AliasError, match="out of range"):
            resolver.resolve("vibrato", [1, 10.0], source_line=10)  # Way above

    @pytest.mark.unit
    def test_float_parameter_integer_values(self):
        """Test that integer values work for float range parameters."""
        alias_def = AliasDefinition(
            name="vibrato",
            parameters=[
                {
                    "name": "ch",
                    "type": "generic",
                    "min": 1,
                    "max": 16,
                    "default": None,
                    "enum_values": None,
                },
                {
                    "name": "freq",
                    "type": "range",
                    "min": 0.5,
                    "max": 8.0,
                    "default": None,
                    "enum_values": None,
                },
            ],
            commands=["cc.{ch}.1.wave(sine, 64, freq={freq}, depth=10)"],
            description="Apply vibrato",
        )

        resolver = AliasResolver({"vibrato": alias_def})

        # Integer values should work for float ranges
        resolver.resolve("vibrato", [1, 1], source_line=10)
        resolver.resolve("vibrato", [1, 5], source_line=10)
        resolver.resolve("vibrato", [1, 8], source_line=10)

    @pytest.mark.unit
    def test_mixed_int_and_float_ranges(self):
        """Test alias with both int and float range parameters."""
        mml = """@alias complex_effect {ch} {depth:10-50} {freq:0.5-8.0} "Complex effect"
  - cc {ch}.74.{depth}
  - cc {ch}.1.wave(sine, 64, freq={freq})
@end

[00:00.000]
- complex_effect 1 30 5.5
"""
        parser = MMDParser()
        doc = parser.parse_string(mml)

        # Verify both parameters are parsed correctly
        alias_def = doc.aliases["complex_effect"]
        assert len(alias_def.parameters) == 3

        depth_param = alias_def.parameters[1]
        assert depth_param["name"] == "depth"
        assert depth_param["min"] == 10
        assert depth_param["max"] == 50
        assert isinstance(depth_param["min"], int)
        assert isinstance(depth_param["max"], int)

        freq_param = alias_def.parameters[2]
        assert freq_param["name"] == "freq"
        assert freq_param["min"] == 0.5
        assert freq_param["max"] == 8.0
        assert isinstance(freq_param["min"], float)
        assert isinstance(freq_param["max"], float)

    @pytest.mark.unit
    def test_h90_expression_vibrato_example(self):
        """Test the real H90 expression vibrato alias from the device library."""
        mml = """@alias h90_expression_vibrato {ch} {center:0-127} {freq:0.5-8.0} {depth:10-50} "Expression vibrato with sine wave"
  - cc {ch}.11.wave(sine, {center}, freq={freq}, depth={depth})
@end

[00:00.000]
- h90_expression_vibrato 2 64 5.5 30
"""
        parser = MMDParser()
        doc = parser.parse_string(mml)

        # Verify the alias parses correctly
        alias_def = doc.aliases["h90_expression_vibrato"]
        assert alias_def.name == "h90_expression_vibrato"
        assert len(alias_def.parameters) == 4

        # Check channel parameter
        ch_param = alias_def.parameters[0]
        assert ch_param["name"] == "ch"

        # Check center parameter (int range)
        center_param = alias_def.parameters[1]
        assert center_param["name"] == "center"
        assert center_param["min"] == 0
        assert center_param["max"] == 127
        assert isinstance(center_param["min"], int)

        # Check freq parameter (float range)
        freq_param = alias_def.parameters[2]
        assert freq_param["name"] == "freq"
        assert freq_param["min"] == 0.5
        assert freq_param["max"] == 8.0
        assert isinstance(freq_param["min"], float)

        # Check depth parameter (int range)
        depth_param = alias_def.parameters[3]
        assert depth_param["name"] == "depth"
        assert depth_param["min"] == 10
        assert depth_param["max"] == 50
        assert isinstance(depth_param["min"], int)
