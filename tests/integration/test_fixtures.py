"""
Integration tests for focused MML fixtures.

Tests small, focused examples for specific features.
"""

from pathlib import Path

import pytest

# Paths to fixture directories
VALID_DIR = Path(__file__).parent.parent / "fixtures" / "valid"
INVALID_DIR = Path(__file__).parent.parent / "fixtures" / "invalid"


class TestValidFixtures:
    """Test that all valid fixtures parse successfully"""

    def test_single_note(self, parser):
        """Test single note fixture"""
        fixture = VALID_DIR / "single_note.mmd"
        doc = parser.parse_file(fixture)

        assert len(doc.events) >= 1
        # Should have a note_on command
        note_commands = [
            cmd
            for event in doc.events
            if event["type"] == "timed_event"
            for cmd in event["commands"]
            if cmd.type == "note_on"
        ]
        assert len(note_commands) >= 1

    def test_cc_commands(self, parser):
        """Test CC commands fixture"""
        fixture = VALID_DIR / "cc_commands.mmd"
        doc = parser.parse_file(fixture)

        # Should have multiple CC commands
        # Parser outputs 'cc' for control_change commands
        cc_commands = [
            cmd
            for event in doc.events
            if event["type"] == "timed_event"
            for cmd in event["commands"]
            if cmd.type == "cc"
        ]
        assert len(cc_commands) >= 3

    def test_pitch_bend(self, parser):
        """Test pitch bend fixture"""
        fixture = VALID_DIR / "pitch_bend.mmd"
        doc = parser.parse_file(fixture)

        # Should have pitch bend commands
        pb_commands = [
            cmd
            for event in doc.events
            if event["type"] == "timed_event"
            for cmd in event["commands"]
            if cmd.type == "pitch_bend"
        ]
        assert len(pb_commands) >= 4

    def test_pressure_commands(self, parser):
        """Test pressure commands fixture"""
        fixture = VALID_DIR / "pressure_commands.mmd"
        doc = parser.parse_file(fixture)

        # Should have channel and poly pressure
        has_cp = False
        has_pp = False
        for event in doc.events:
            if event["type"] == "timed_event":
                for cmd in event["commands"]:
                    if cmd.type == "channel_pressure":
                        has_cp = True
                    if cmd.type == "poly_pressure":
                        has_pp = True

        assert has_cp, "Should have channel pressure"
        assert has_pp, "Should have poly pressure"

    def test_meta_events(self, parser):
        """Test meta events fixture"""
        fixture = VALID_DIR / "meta_events.mmd"
        doc = parser.parse_file(fixture)

        # Extract message types
        types = set()
        for event in doc.events:
            if event["type"] == "timed_event":
                for cmd in event["commands"]:
                    types.add(cmd.type)

        assert "tempo" in types
        assert "time_signature" in types
        assert "key_signature" in types
        assert "marker" in types
        assert "text" in types

    def test_timing_types(self, parser):
        """Test different timing types fixture"""
        fixture = VALID_DIR / "timing_types.mmd"
        doc = parser.parse_file(fixture)

        # Extract timing types
        timing_types = set()
        for event in doc.events:
            if event["type"] == "timed_event":
                timing_types.add(event["timing"].type)

        assert "absolute" in timing_types
        assert "musical" in timing_types
        assert "relative" in timing_types
        assert "simultaneous" in timing_types

    def test_defines(self, parser):
        """Test defines fixture"""
        fixture = VALID_DIR / "defines.mmd"
        doc = parser.parse_file(fixture)

        # Should have defines
        assert len(doc.defines) >= 3
        assert "MAIN_CHANNEL" in doc.defines
        assert "DEFAULT_VELOCITY" in doc.defines
        assert "TEMPO_FAST" in doc.defines

    def test_sysex(self, parser):
        """Test SysEx fixture"""
        fixture = VALID_DIR / "sysex.mmd"
        doc = parser.parse_file(fixture)

        # Should have SysEx commands
        sysex_commands = [
            cmd
            for event in doc.events
            if event["type"] == "timed_event"
            for cmd in event["commands"]
            if cmd.type == "sysex"
        ]
        assert len(sysex_commands) >= 2

    def test_comments(self, parser):
        """Test comments fixture"""
        fixture = VALID_DIR / "comments.mmd"
        doc = parser.parse_file(fixture)

        # Should parse successfully despite comments
        assert len(doc.events) >= 1

    def test_all_valid_fixtures_parse(self, parser):
        """Test that all valid fixtures parse without errors"""
        for fixture_file in VALID_DIR.glob("*.mmd"):
            try:
                doc = parser.parse_file(fixture_file)
                assert doc is not None, f"Failed to parse {fixture_file.name}"
            except Exception as e:
                pytest.fail(f"Failed to parse {fixture_file.name}: {e}")


class TestInvalidFixtures:
    """Test that invalid fixtures fail parsing appropriately"""

    def test_syntax_error(self, parser):
        """Test that syntax error fixture fails"""
        fixture = INVALID_DIR / "syntax_error.mmd"
        with pytest.raises(Exception):
            parser.parse_file(fixture)

    # Note: Parser validates syntax only. MIDI value validation happens during compilation.
    # See tests/integration/test_document_validation.py for validation tests.
    # See tests/integration/test_timing_validation_integration.py for timing tests.

    def test_missing_timing(self, parser):
        """Test that missing timing fails"""
        fixture = INVALID_DIR / "missing_timing.mmd"
        with pytest.raises(Exception):
            parser.parse_file(fixture)
