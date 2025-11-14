"""
Tests for Stage 2: Enhanced Parameter Types in Alias System

Tests note name resolution, percent scaling, and boolean parameter handling.
"""

import pytest

from midi_markdown.alias.resolver import AliasError, AliasResolver
from midi_markdown.utils.parameter_types import bool_to_midi, note_to_midi, percent_to_midi

# ============================================================================
# Utility Function Tests
# ============================================================================


class TestNoteToMidi:
    """Tests for note name to MIDI conversion utility."""

    @pytest.mark.parametrize(
        ("note", "expected"),
        [
            # Natural notes
            ("C4", 60),
            ("D4", 62),
            ("E4", 64),
            ("F4", 65),
            ("G4", 67),
            ("A4", 69),
            ("B4", 71),
            # Sharps
            ("C#4", 61),
            ("D#4", 63),
            ("F#4", 66),
            ("G#4", 68),
            ("A#4", 70),
            # Flats
            ("Db4", 61),
            ("Eb4", 63),
            ("Gb4", 66),
            ("Ab4", 68),
            ("Bb3", 58),
            # Octave ranges
            ("C-1", 0),  # Lowest MIDI note
            ("C0", 12),
            ("C1", 24),
            ("C2", 36),
            ("C3", 48),  # Middle C
            ("C5", 72),
            ("C6", 84),
            ("C7", 96),
            ("C8", 108),
            ("G9", 127),  # Highest MIDI note
        ],
    )
    def test_note_conversions(self, note, expected):
        """Test note name to MIDI number conversion."""
        assert note_to_midi(note) == expected

    @pytest.mark.parametrize(
        ("note", "error_match"),
        [
            ("H4", "base note must be A-G"),
            ("C10", "out of valid MIDI range"),
            ("C-2", "out of valid MIDI range"),
            ("invalid", "Invalid note name"),
            ("", "cannot be empty"),
        ],
    )
    def test_invalid_notes(self, note, error_match):
        """Test error handling for invalid note names."""
        with pytest.raises(ValueError, match=error_match):
            note_to_midi(note)


class TestPercentToMidi:
    """Tests for percent to MIDI conversion utility."""

    @pytest.mark.parametrize(
        ("percent", "expected"),
        [
            (0, 0),  # Minimum
            (1, 1),  # Edge case low
            (25, 31),  # Quarter
            (50, 63),  # Half (50 * 127/100 = 63.5 -> 63)
            (75, 95),  # Three quarters (75 * 127/100 = 95.25 -> 95)
            (99, 125),  # Edge case high
            (100, 127),  # Maximum
        ],
    )
    def test_percent_scaling(self, percent, expected):
        """Test percent to MIDI scaling (0-100 -> 0-127)."""
        assert percent_to_midi(percent) == expected

    @pytest.mark.parametrize(
        ("value", "error_match"),
        [
            (-1, "out of valid range"),
            (101, "out of valid range"),
            (200, "out of valid range"),
            ("invalid", "must be a number"),
        ],
    )
    def test_invalid_percent(self, value, error_match):
        """Test error handling for invalid percent values."""
        with pytest.raises(ValueError, match=error_match):
            percent_to_midi(value)


class TestBoolToMidi:
    """Tests for boolean to MIDI conversion utility."""

    @pytest.mark.parametrize(
        "value",
        [
            # Boolean type
            True,
            # String variations (case insensitive)
            "true",
            "True",
            "TRUE",
            "TrUe",
            "on",
            "ON",
            "oN",
            "yes",
            "YES",
            # Numeric
            "1",
            1,
        ],
    )
    def test_true_variations(self, value):
        """Test various representations of true (127)."""
        assert bool_to_midi(value) == 127

    @pytest.mark.parametrize(
        "value",
        [
            # Boolean type
            False,
            # String variations (case insensitive)
            "false",
            "False",
            "FALSE",
            "FaLsE",
            "off",
            "OFF",
            "OfF",
            "no",
            "NO",
            # Numeric
            "0",
            0,
        ],
    )
    def test_false_variations(self, value):
        """Test various representations of false (0)."""
        assert bool_to_midi(value) == 0

    @pytest.mark.parametrize(
        ("value", "error_match"),
        [
            ("maybe", "Invalid boolean"),
            (2, "Invalid boolean"),
            ("invalid", "Invalid boolean"),
        ],
    )
    def test_invalid_bool(self, value, error_match):
        """Test error handling for invalid boolean values."""
        with pytest.raises(ValueError, match=error_match):
            bool_to_midi(value)


# ============================================================================
# Alias Resolver Tests with Parameter Types
# ============================================================================


class TestNoteParameterInAliases:
    """Tests for note parameter type in aliases."""

    def test_note_parameter_with_note_name(self):
        """Test alias with note parameter accepting note name."""
        from midi_markdown.parser.ast_nodes import AliasDefinition

        # Create alias definition directly
        alias_def = AliasDefinition(
            name="play_note",
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
                    "name": "note",
                    "type": "note",
                    "min": 0,
                    "max": 127,
                    "default": None,
                    "enum_values": None,
                },
                {
                    "name": "vel",
                    "type": "generic",
                    "min": 0,
                    "max": 127,
                    "default": None,
                    "enum_values": None,
                },
            ],
            commands=["note_on.{ch}.{note}.{vel}"],
            description="Play note",
        )

        resolver = AliasResolver({"play_note": alias_def})

        # Expand alias with note name
        commands = resolver.resolve("play_note", [1, "C4", 100], source_line=10)

        assert len(commands) == 1
        assert commands[0].type == "note_on"
        assert commands[0].channel == 1
        assert commands[0].data1 == 60  # C4 = 60
        assert commands[0].data2 == 100

    def test_note_parameter_with_sharps(self):
        """Test note parameter with sharp notes."""
        from midi_markdown.parser.ast_nodes import AliasDefinition

        alias_def = AliasDefinition(
            name="play_note",
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
                    "name": "note",
                    "type": "note",
                    "min": 0,
                    "max": 127,
                    "default": None,
                    "enum_values": None,
                },
                {
                    "name": "vel",
                    "type": "generic",
                    "min": 0,
                    "max": 127,
                    "default": None,
                    "enum_values": None,
                },
            ],
            commands=["note_on.{ch}.{note}.{vel}"],
            description="",
        )

        resolver = AliasResolver({"play_note": alias_def})
        commands = resolver.resolve("play_note", [1, "C#4", 80], source_line=10)

        assert commands[0].data1 == 61  # C#4 = 61

    def test_note_parameter_with_flats(self):
        """Test note parameter with flat notes."""
        from midi_markdown.parser.ast_nodes import AliasDefinition

        alias_def = AliasDefinition(
            name="play_note",
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
                    "name": "note",
                    "type": "note",
                    "min": 0,
                    "max": 127,
                    "default": None,
                    "enum_values": None,
                },
                {
                    "name": "vel",
                    "type": "generic",
                    "min": 0,
                    "max": 127,
                    "default": None,
                    "enum_values": None,
                },
            ],
            commands=["note_on.{ch}.{note}.{vel}"],
            description="",
        )

        resolver = AliasResolver({"play_note": alias_def})
        commands = resolver.resolve("play_note", [1, "Bb3", 90], source_line=10)

        assert commands[0].data1 == 58  # Bb3 = 58

    def test_note_parameter_invalid_note_name(self):
        """Test error for invalid note name."""
        from midi_markdown.parser.ast_nodes import AliasDefinition

        alias_def = AliasDefinition(
            name="play_note",
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
                    "name": "note",
                    "type": "note",
                    "min": 0,
                    "max": 127,
                    "default": None,
                    "enum_values": None,
                },
                {
                    "name": "vel",
                    "type": "generic",
                    "min": 0,
                    "max": 127,
                    "default": None,
                    "enum_values": None,
                },
            ],
            commands=["note_on.{ch}.{note}.{vel}"],
            description="",
        )

        resolver = AliasResolver({"play_note": alias_def})

        with pytest.raises(AliasError, match="Invalid note name"):
            resolver.resolve("play_note", [1, "H4", 100], source_line=10)


class TestPercentParameterInAliases:
    """Tests for percent parameter type in aliases."""

    def test_percent_parameter_scaling(self):
        """Test percent parameter scales correctly."""
        from midi_markdown.parser.ast_nodes import AliasDefinition

        alias_def = AliasDefinition(
            name="reverb",
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
                    "name": "mix",
                    "type": "percent",
                    "min": 0,
                    "max": 100,
                    "default": None,
                    "enum_values": None,
                },
            ],
            commands=["cc.{ch}.91.{mix}"],
            description="Reverb mix",
        )

        resolver = AliasResolver({"reverb": alias_def})

        # 75% should scale to 95 (75 * 127/100)
        commands = resolver.resolve("reverb", [1, 75], source_line=10)

        assert len(commands) == 1
        assert commands[0].type == "control_change"
        assert commands[0].channel == 1
        assert commands[0].data1 == 91
        assert commands[0].data2 == 95

    def test_percent_parameter_edge_cases(self):
        """Test percent parameter edge cases."""
        from midi_markdown.parser.ast_nodes import AliasDefinition

        alias_def = AliasDefinition(
            name="reverb",
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
                    "name": "mix",
                    "type": "percent",
                    "min": 0,
                    "max": 100,
                    "default": None,
                    "enum_values": None,
                },
            ],
            commands=["cc.{ch}.91.{mix}"],
            description="",
        )

        resolver = AliasResolver({"reverb": alias_def})

        # Test 0%
        commands = resolver.resolve("reverb", [1, 0], source_line=10)
        assert commands[0].data2 == 0

        # Test 100%
        commands = resolver.resolve("reverb", [1, 100], source_line=10)
        assert commands[0].data2 == 127

        # Test 50%
        commands = resolver.resolve("reverb", [1, 50], source_line=10)
        assert commands[0].data2 == 63

    def test_percent_parameter_out_of_range(self):
        """Test error for percent out of range."""
        from midi_markdown.parser.ast_nodes import AliasDefinition

        alias_def = AliasDefinition(
            name="reverb",
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
                    "name": "mix",
                    "type": "percent",
                    "min": 0,
                    "max": 100,
                    "default": None,
                    "enum_values": None,
                },
            ],
            commands=["cc.{ch}.91.{mix}"],
            description="",
        )

        resolver = AliasResolver({"reverb": alias_def})

        with pytest.raises(AliasError, match="out of valid range"):
            resolver.resolve("reverb", [1, 101], source_line=10)

        with pytest.raises(AliasError, match="out of valid range"):
            resolver.resolve("reverb", [1, -1], source_line=10)


class TestBoolParameterInAliases:
    """Tests for bool parameter type in aliases."""

    def test_bool_parameter_true_variations(self):
        """Test bool parameter accepts various true formats."""
        from midi_markdown.parser.ast_nodes import AliasDefinition

        alias_def = AliasDefinition(
            name="stomp_toggle",
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
                    "name": "enabled",
                    "type": "bool",
                    "min": 0,
                    "max": 1,
                    "default": None,
                    "enum_values": None,
                },
            ],
            commands=["cc.{ch}.81.{enabled}"],
            description="Toggle stomp",
        )

        resolver = AliasResolver({"stomp_toggle": alias_def})

        # Test "true"
        commands = resolver.resolve("stomp_toggle", [1, "true"], source_line=10)
        assert commands[0].data2 == 127

        # Test "on"
        commands = resolver.resolve("stomp_toggle", [1, "on"], source_line=10)
        assert commands[0].data2 == 127

        # Test 1
        commands = resolver.resolve("stomp_toggle", [1, 1], source_line=10)
        assert commands[0].data2 == 127

    def test_bool_parameter_false_variations(self):
        """Test bool parameter accepts various false formats."""
        from midi_markdown.parser.ast_nodes import AliasDefinition

        alias_def = AliasDefinition(
            name="stomp_toggle",
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
                    "name": "enabled",
                    "type": "bool",
                    "min": 0,
                    "max": 1,
                    "default": None,
                    "enum_values": None,
                },
            ],
            commands=["cc.{ch}.81.{enabled}"],
            description="",
        )

        resolver = AliasResolver({"stomp_toggle": alias_def})

        # Test "false"
        commands = resolver.resolve("stomp_toggle", [1, "false"], source_line=10)
        assert commands[0].data2 == 0

        # Test "off"
        commands = resolver.resolve("stomp_toggle", [1, "off"], source_line=10)
        assert commands[0].data2 == 0

        # Test 0
        commands = resolver.resolve("stomp_toggle", [1, 0], source_line=10)
        assert commands[0].data2 == 0

    def test_bool_parameter_case_insensitive(self):
        """Test bool parameter is case insensitive."""
        from midi_markdown.parser.ast_nodes import AliasDefinition

        alias_def = AliasDefinition(
            name="stomp_toggle",
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
                    "name": "enabled",
                    "type": "bool",
                    "min": 0,
                    "max": 1,
                    "default": None,
                    "enum_values": None,
                },
            ],
            commands=["cc.{ch}.81.{enabled}"],
            description="",
        )

        resolver = AliasResolver({"stomp_toggle": alias_def})

        commands = resolver.resolve("stomp_toggle", [1, "TRUE"], source_line=10)
        assert commands[0].data2 == 127

        commands = resolver.resolve("stomp_toggle", [1, "FaLsE"], source_line=10)
        assert commands[0].data2 == 0

    def test_bool_parameter_invalid_value(self):
        """Test error for invalid boolean value."""
        from midi_markdown.parser.ast_nodes import AliasDefinition

        alias_def = AliasDefinition(
            name="stomp_toggle",
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
                    "name": "enabled",
                    "type": "bool",
                    "min": 0,
                    "max": 1,
                    "default": None,
                    "enum_values": None,
                },
            ],
            commands=["cc.{ch}.81.{enabled}"],
            description="",
        )

        resolver = AliasResolver({"stomp_toggle": alias_def})

        with pytest.raises(AliasError, match="Invalid boolean"):
            resolver.resolve("stomp_toggle", [1, "maybe"], source_line=10)

        with pytest.raises(AliasError, match="Invalid boolean"):
            resolver.resolve("stomp_toggle", [1, 2], source_line=10)


# ============================================================================
# Integration Tests
# ============================================================================


class TestParameterTypesIntegration:
    """Integration tests for parameter types working together."""

    def test_all_parameter_types_together(self):
        """Test all parameter types can be used together."""
        from midi_markdown.parser.ast_nodes import AliasDefinition

        # Create aliases with different parameter types
        aliases = {
            "play_note": AliasDefinition(
                name="play_note",
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
                        "name": "note",
                        "type": "note",
                        "min": 0,
                        "max": 127,
                        "default": None,
                        "enum_values": None,
                    },
                    {
                        "name": "vel",
                        "type": "generic",
                        "min": 0,
                        "max": 127,
                        "default": None,
                        "enum_values": None,
                    },
                ],
                commands=["note_on.{ch}.{note}.{vel}"],
                description="Play note with name",
            ),
            "reverb": AliasDefinition(
                name="reverb",
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
                        "name": "mix",
                        "type": "percent",
                        "min": 0,
                        "max": 100,
                        "default": None,
                        "enum_values": None,
                    },
                ],
                commands=["cc.{ch}.91.{mix}"],
                description="Reverb mix as percent",
            ),
            "stomp": AliasDefinition(
                name="stomp",
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
                        "name": "enabled",
                        "type": "bool",
                        "min": 0,
                        "max": 1,
                        "default": None,
                        "enum_values": None,
                    },
                ],
                commands=["cc.{ch}.81.{enabled}"],
                description="Toggle stomp",
            ),
        }

        resolver = AliasResolver(aliases)

        # Test note parameter
        cmds = resolver.resolve("play_note", [1, "C4", 100], source_line=11)
        assert cmds[0].data1 == 60  # Note number

        # Test percent parameter
        cmds = resolver.resolve("reverb", [1, 75], source_line=12)
        assert cmds[0].data2 == 95  # CC value

        # Test bool parameter
        cmds = resolver.resolve("stomp", [1, "true"], source_line=13)
        assert cmds[0].data2 == 127  # CC value
