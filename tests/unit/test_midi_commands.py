"""
Test Suite: MIDI Commands

Tests for all MIDI command types including channel voice messages,
meta events, and system messages, plus comprehensive edge cases.
"""

import pytest


class TestBasicMIDICommands:
    """Test basic MIDI command parsing"""

    # ========================================================================
    # Program Change Tests
    # ========================================================================

    def test_program_change(self, parser):
        """Test program change commands"""
        mml = """
[00:00.000]
- pc 1.0
- pc 2.127
- program_change 3.64
"""
        doc = parser.parse_string(mml)
        assert len(doc.events) == 1
        commands = doc.events[0]["commands"]
        assert len(commands) == 3
        assert commands[0].type == "pc"
        assert commands[0].channel == 1
        assert commands[0].data1 == 0

    # ========================================================================
    # Control Change Tests
    # ========================================================================

    def test_control_change(self, parser):
        """Test control change commands"""
        mml = """
[00:00.000]
- cc 1.7.100
- cc 2.10.64
- control_change 3.1.127
"""
        doc = parser.parse_string(mml)
        commands = doc.events[0]["commands"]
        assert len(commands) == 3
        assert commands[0].type == "cc"
        assert commands[0].channel == 1
        assert commands[0].data1 == 7
        assert commands[0].data2 == 100

    # ========================================================================
    # Note Commands Tests
    # ========================================================================

    def test_note_commands(self, parser):
        """Test note_on and note_off commands"""
        mml = """
[00:00.000]
- note_on 1.60 100
- note_off 1.60 64
- note_on 2.C4 127
"""
        doc = parser.parse_string(mml)
        commands = doc.events[0]["commands"]
        assert commands[0].type == "note_on"
        assert commands[0].data1 == 60
        assert commands[0].data2 == 100
        assert commands[1].type == "note_off"

    def test_note_with_duration(self, parser):
        """Test note_on with duration (auto note_off)"""
        mml = """[00:00.000]
- note_on 1.60 100 1b
"""
        doc = parser.parse_string(mml)
        cmd = doc.events[0]["commands"][0]
        assert cmd.type == "note_on"
        assert "duration" in cmd.params
        assert cmd.params["duration"] == (1.0, "b")

    # ========================================================================
    # Pitch Bend Tests
    # ========================================================================

    def test_pitch_bend(self, parser):
        """Test pitch bend commands"""
        mml = """
[00:00.000]
- pitch_bend 1.0
- pitch_bend 1.8191
- pitch_bend 1.-8192
"""
        doc = parser.parse_string(mml)
        commands = doc.events[0]["commands"]
        assert commands[0].type == "pitch_bend"
        assert commands[0].data1 == 0
        assert commands[1].data1 == 8191
        assert commands[2].data1 == -8192

    # ========================================================================
    # Pressure Commands Tests
    # ========================================================================

    def test_pressure_commands(self, parser):
        """Test channel and polyphonic pressure"""
        mml = """
[00:00.000]
- channel_pressure 1.64
- cp 1.64
- poly_pressure 1.C4.80
- pp 1.60.100
"""
        doc = parser.parse_string(mml)
        commands = doc.events[0]["commands"]
        assert commands[0].type == "channel_pressure"
        assert commands[0].data1 == 64
        assert commands[2].type == "poly_pressure"
        assert commands[2].data1 == 60
        assert commands[2].data2 == 80

    # ========================================================================
    # Meta Events Tests
    # ========================================================================

    def test_meta_events(self, parser):
        """Test meta events (tempo, marker, text)"""
        mml = """
[00:00.000]
- tempo 120
- marker "Intro"
- text "Performance notes"
"""
        doc = parser.parse_string(mml)
        commands = doc.events[0]["commands"]
        assert commands[0].type == "tempo"
        assert commands[0].data1 == 120
        assert commands[1].type == "marker"
        assert commands[2].type == "text"

    # ========================================================================
    # SysEx Tests
    # ========================================================================

    def test_sysex(self, parser):
        """Test SysEx message"""
        mml = """
[00:00.000]
- sysex F0 43 12 00 F7
"""
        doc = parser.parse_string(mml)
        cmd = doc.events[0]["commands"][0]
        assert cmd.type == "sysex"

    def test_multiline_sysex(self, parser):
        """Test multi-line SysEx message"""
        mml = """
[00:00.000]
- sysex F0 00 01 06
        02 03 04 05
        F7
"""
        doc = parser.parse_string(mml)
        cmd = doc.events[0]["commands"][0]
        assert cmd.type == "sysex"
        # Verify all hex bytes are captured
        assert len(cmd.params["bytes"]) == 9
        expected_bytes = ["F0", "00", "01", "06", "02", "03", "04", "05", "F7"]
        assert cmd.params["bytes"] == expected_bytes

    def test_multiline_sysex_long(self, parser):
        """Test multi-line SysEx with many lines"""
        mml = """
[00:00.000]
- sysex F0 41 10 00 11
        12 40 00 7F
        00 41 01 02
        03 04 05 06
        F7
"""
        doc = parser.parse_string(mml)
        cmd = doc.events[0]["commands"][0]
        assert cmd.type == "sysex"
        # Verify all 18 hex bytes are captured
        assert len(cmd.params["bytes"]) == 18
        # F0 + 16 data bytes + F7
        expected = [
            "F0",
            "41",
            "10",
            "00",
            "11",
            "12",
            "40",
            "00",
            "7F",
            "00",
            "41",
            "01",
            "02",
            "03",
            "04",
            "05",
            "06",
            "F7",
        ]
        assert cmd.params["bytes"] == expected


class TestMIDICommandEdgeCases:
    """Test MIDI command edge cases and boundary values"""

    # ========================================================================
    # Value Range Edge Cases
    # ========================================================================

    @pytest.mark.parametrize(
        ("mml", "expected_type", "expected_data"),
        [
            ("- cc 1.7.0", "cc", {"data2": 0}),  # CC value minimum
            ("- cc 1.7.127", "cc", {"data2": 127}),  # CC value maximum
            ("- note_on 1.60 0", "note_on", {"data2": 0}),  # Velocity minimum
            ("- note_on 1.60 127", "note_on", {"data2": 127}),  # Velocity maximum
            ("- pc 1.0", "pc", {"data1": 0}),  # Program change minimum
            ("- pc 1.127", "pc", {"data1": 127}),  # Program change maximum
        ],
    )
    def test_value_boundaries(self, parser, mml, expected_type, expected_data):
        """Test MIDI command value boundaries (0-127 range)"""
        doc = parser.parse_string(f"[00:00.000]\n{mml}\n")
        cmd = doc.events[0]["commands"][0]
        assert cmd.type == expected_type
        for key, value in expected_data.items():
            assert getattr(cmd, key) == value

    # ========================================================================
    # Channel Boundary Tests
    # ========================================================================

    @pytest.mark.parametrize("channel", [1, 16])
    def test_channel_boundaries(self, parser, channel):
        """Test channel boundaries (1-16 range)"""
        mml = f"[00:00.000]\n- pc {channel}.0\n"
        doc = parser.parse_string(mml)
        cmd = doc.events[0]["commands"][0]
        assert cmd.channel == channel

    # ========================================================================
    # Note Range Tests
    # ========================================================================

    @pytest.mark.parametrize(
        ("note", "expected"),
        [
            ("0", 0),  # Note number minimum (C-1)
            ("127", 127),  # Note number maximum (G9)
            ("C-1", 0),  # Note name lowest
            ("G9", 127),  # Note name highest
            ("C4", 60),  # Middle C
            ("C#4", 61),  # Note with sharp
            ("Db4", 61),  # Note with flat
        ],
    )
    def test_note_ranges(self, parser, note, expected):
        """Test note number and name ranges (0-127, C-1 to G9)"""
        mml = f"[00:00.000]\n- note_on 1.{note} 100\n"
        doc = parser.parse_string(mml)
        cmd = doc.events[0]["commands"][0]
        assert cmd.data1 == expected

    # ========================================================================
    # Pitch Bend Range Tests
    # ========================================================================

    @pytest.mark.parametrize("value", [-8192, 0, 8191])
    def test_pitch_bend_ranges(self, parser, value):
        """Test pitch bend range (-8192 to 8191)"""
        mml = f"[00:00.000]\n- pitch_bend 1.{value}\n"
        doc = parser.parse_string(mml)
        cmd = doc.events[0]["commands"][0]
        assert cmd.type == "pitch_bend"
        assert cmd.data1 == value

    # ========================================================================
    # Pressure Value Tests
    # ========================================================================

    @pytest.mark.parametrize(
        ("mml", "cmd_type", "data_field", "expected"),
        [
            ("- channel_pressure 1.0", "channel_pressure", "data1", 0),  # Channel min
            ("- channel_pressure 1.127", "channel_pressure", "data1", 127),  # Channel max
            ("- poly_pressure 1.60.0", "poly_pressure", "data2", 0),  # Poly min
            ("- poly_pressure 1.60.127", "poly_pressure", "data2", 127),  # Poly max
        ],
    )
    def test_pressure_ranges(self, parser, mml, cmd_type, data_field, expected):
        """Test channel and polyphonic pressure ranges (0-127)"""
        doc = parser.parse_string(f"[00:00.000]\n{mml}\n")
        cmd = doc.events[0]["commands"][0]
        assert cmd.type == cmd_type
        assert getattr(cmd, data_field) == expected

    # ========================================================================
    # Tempo Range Tests
    # ========================================================================

    @pytest.mark.parametrize("tempo", [1, 120, 300])
    def test_tempo_ranges(self, parser, tempo):
        """Test tempo range (1-300 BPM)"""
        mml = f"[00:00.000]\n- tempo {tempo}\n"
        doc = parser.parse_string(mml)
        cmd = doc.events[0]["commands"][0]
        assert cmd.type == "tempo"
        assert cmd.data1 == tempo

    # ========================================================================
    # Note Name Variations
    # ========================================================================

    def test_note_name_variations(self, parser):
        """Test various note name formats"""
        mml = """
[00:00.000]
- note_on 1.C4 100
- note_on 1.C#4 100
- note_on 1.Db4 100
- note_on 1.G9 100
- note_on 1.C-1 100
"""
        doc = parser.parse_string(mml)
        commands = doc.events[0]["commands"]
        assert commands[0].data1 == 60  # C4
        assert commands[1].data1 == 61  # C#4
        assert commands[2].data1 == 61  # Db4 (enharmonic equivalent)
        assert commands[3].data1 == 127  # G9
        assert commands[4].data1 == 0  # C-1

    # ========================================================================
    # Percent Values
    # ========================================================================

    def test_percent_values(self, parser):
        """Test percent value notation"""
        mml = """
[00:00.000]
- cc 1.7.100%
- cc 1.11.50%
- cc 1.1.0%
"""
        doc = parser.parse_string(mml)
        commands = doc.events[0]["commands"]
        # Note: percent conversion might need to be implemented
        # For now, just check that they parse
        assert len(commands) == 3


class TestModulationExpressions:
    """Test modulation expressions (curve, wave, envelope) in various MIDI contexts.

    These tests verify that modulation expressions parse correctly in pitch_bend
    and pressure parameter contexts (added in Phase 6 modulation grammar extension).
    """

    # ========================================================================
    # Pitch Bend Modulation Tests
    # ========================================================================

    def test_pitch_bend_with_curve(self, parser):
        """Test pitch bend with curve expression"""
        mml = """
[00:00.000]
- pitch_bend 1.curve(-4096, 4096, ease-in-out)
"""
        doc = parser.parse_string(mml)
        cmd = doc.events[0]["commands"][0]
        assert cmd.type == "pitch_bend"
        assert cmd.channel == 1
        # data1 should be a CurveExpression object
        from midi_markdown.parser.ast_nodes import CurveExpression

        assert isinstance(cmd.data1, CurveExpression)
        assert cmd.data1.start_value == -4096
        assert cmd.data1.end_value == 4096
        assert cmd.data1.curve_type == "ease-in-out"

    def test_pitch_bend_with_wave(self, parser):
        """Test pitch bend with wave expression"""
        mml = """
[00:00.000]
- pitch_bend 1.wave(sine, 8192, freq=7.0, depth=5)
"""
        doc = parser.parse_string(mml)
        cmd = doc.events[0]["commands"][0]
        assert cmd.type == "pitch_bend"
        assert cmd.channel == 1
        # data1 should be a WaveExpression object
        from midi_markdown.parser.ast_nodes import WaveExpression

        assert isinstance(cmd.data1, WaveExpression)
        assert cmd.data1.wave_type == "sine"
        assert cmd.data1.base_value == 8192
        assert cmd.data1.frequency == 7.0
        assert cmd.data1.depth == 5

    def test_pitch_bend_with_envelope(self, parser):
        """Test pitch bend with envelope expression"""
        mml = """
[00:00.000]
- pitch_bend 1.envelope(ar, attack=0.1, release=0.4)
"""
        doc = parser.parse_string(mml)
        cmd = doc.events[0]["commands"][0]
        assert cmd.type == "pitch_bend"
        # data1 should be an EnvelopeExpression object
        from midi_markdown.parser.ast_nodes import EnvelopeExpression

        assert isinstance(cmd.data1, EnvelopeExpression)
        assert cmd.data1.envelope_type == "ar"
        assert cmd.data1.attack == 0.1
        assert cmd.data1.release == 0.4

    # ========================================================================
    # Channel Pressure Modulation Tests
    # ========================================================================

    def test_channel_pressure_with_curve(self, parser):
        """Test channel pressure with curve expression"""
        mml = """
[00:00.000]
- channel_pressure 1.curve(0, 127, ease-in-out)
"""
        doc = parser.parse_string(mml)
        cmd = doc.events[0]["commands"][0]
        assert cmd.type == "channel_pressure"
        assert cmd.channel == 1
        # data1 should be a CurveExpression object
        from midi_markdown.parser.ast_nodes import CurveExpression

        assert isinstance(cmd.data1, CurveExpression)
        assert cmd.data1.start_value == 0
        assert cmd.data1.end_value == 127
        assert cmd.data1.curve_type == "ease-in-out"

    def test_channel_pressure_with_wave(self, parser):
        """Test channel pressure with wave expression"""
        mml = """
[00:00.000]
- cp 1.wave(triangle, 64, freq=2.0, depth=20)
"""
        doc = parser.parse_string(mml)
        cmd = doc.events[0]["commands"][0]
        assert cmd.type == "channel_pressure"
        # data1 should be a WaveExpression object
        from midi_markdown.parser.ast_nodes import WaveExpression

        assert isinstance(cmd.data1, WaveExpression)
        assert cmd.data1.wave_type == "triangle"
        assert cmd.data1.base_value == 64
        assert cmd.data1.frequency == 2.0
        assert cmd.data1.depth == 20

    def test_channel_pressure_with_envelope(self, parser):
        """Test channel pressure with envelope expression"""
        mml = """
[00:00.000]
- channel_pressure 1.envelope(ar, attack=2.0, release=1.0)
"""
        doc = parser.parse_string(mml)
        cmd = doc.events[0]["commands"][0]
        assert cmd.type == "channel_pressure"
        # data1 should be an EnvelopeExpression object
        from midi_markdown.parser.ast_nodes import EnvelopeExpression

        assert isinstance(cmd.data1, EnvelopeExpression)
        assert cmd.data1.envelope_type == "ar"
        assert cmd.data1.attack == 2.0
        assert cmd.data1.release == 1.0

    # ========================================================================
    # Poly Pressure Modulation Tests
    # ========================================================================

    def test_poly_pressure_with_curve(self, parser):
        """Test polyphonic pressure with curve expression"""
        mml = """
[00:00.000]
- poly_pressure 1.60.curve(30, 110, ease-out)
"""
        doc = parser.parse_string(mml)
        cmd = doc.events[0]["commands"][0]
        assert cmd.type == "poly_pressure"
        assert cmd.channel == 1
        assert cmd.data1 == 60  # Note number
        # data2 should be a CurveExpression object
        from midi_markdown.parser.ast_nodes import CurveExpression

        assert isinstance(cmd.data2, CurveExpression)
        assert cmd.data2.start_value == 30
        assert cmd.data2.end_value == 110
        assert cmd.data2.curve_type == "ease-out"

    def test_poly_pressure_with_wave(self, parser):
        """Test polyphonic pressure with wave expression"""
        mml = """
[00:00.000]
- pp 1.C4.wave(sine, 64, freq=6.0, depth=5)
"""
        doc = parser.parse_string(mml)
        cmd = doc.events[0]["commands"][0]
        assert cmd.type == "poly_pressure"
        assert cmd.data1 == 60  # C4 = 60
        # data2 should be a WaveExpression object
        from midi_markdown.parser.ast_nodes import WaveExpression

        assert isinstance(cmd.data2, WaveExpression)
        assert cmd.data2.wave_type == "sine"
        assert cmd.data2.base_value == 64
        assert cmd.data2.frequency == 6.0
        assert cmd.data2.depth == 5

    def test_poly_pressure_with_envelope(self, parser):
        """Test polyphonic pressure with envelope expression"""
        mml = """
[00:00.000]
- poly_pressure 1.60.envelope(adsr, attack=0.05, decay=0.1, sustain=0.8, release=0.2)
"""
        doc = parser.parse_string(mml)
        cmd = doc.events[0]["commands"][0]
        assert cmd.type == "poly_pressure"
        assert cmd.data1 == 60
        # data2 should be an EnvelopeExpression object
        from midi_markdown.parser.ast_nodes import EnvelopeExpression

        assert isinstance(cmd.data2, EnvelopeExpression)
        assert cmd.data2.envelope_type == "adsr"
        assert cmd.data2.attack == 0.05
        assert cmd.data2.decay == 0.1
        assert cmd.data2.sustain == 0.8
        assert cmd.data2.release == 0.2

    # ========================================================================
    # Control Change Modulation Tests (for comparison)
    # ========================================================================

    def test_cc_with_curve(self, parser):
        """Test CC with curve expression (existing feature)"""
        mml = """
[00:00.000]
- cc 1.74.curve(0, 127, ease-in)
"""
        doc = parser.parse_string(mml)
        cmd = doc.events[0]["commands"][0]
        assert cmd.type == "cc"
        assert cmd.data1 == 74  # Filter cutoff
        # data2 should be a CurveExpression object
        from midi_markdown.parser.ast_nodes import CurveExpression

        assert isinstance(cmd.data2, CurveExpression)
        assert cmd.data2.start_value == 0
        assert cmd.data2.end_value == 127
        assert cmd.data2.curve_type == "ease-in"

    # ========================================================================
    # Multiple Modulation Types Test
    # ========================================================================

    def test_mixed_modulation_types(self, parser):
        """Test multiple modulation types in one timing block"""
        mml = """
[00:00.000]
- pitch_bend 1.wave(sine, 8192, freq=7.0, depth=5)
- cc 1.74.curve(20, 120, ease-in-out)
- poly_pressure 1.60.envelope(adsr, attack=0.1, decay=0.2, sustain=0.6, release=0.3)
"""
        doc = parser.parse_string(mml)
        commands = doc.events[0]["commands"]
        assert len(commands) == 3

        from midi_markdown.parser.ast_nodes import (
            CurveExpression,
            EnvelopeExpression,
            WaveExpression,
        )

        # Verify each command has the correct modulation type
        assert isinstance(commands[0].data1, WaveExpression)
        assert isinstance(commands[1].data2, CurveExpression)
        assert isinstance(commands[2].data2, EnvelopeExpression)
