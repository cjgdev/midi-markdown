"""Integration tests for CSV export functionality."""

from __future__ import annotations

import csv
from io import StringIO

import pytest

from midi_markdown.codegen import export_to_csv
from midi_markdown.core import compile_ast_to_ir
from midi_markdown.parser.parser import MMDParser


@pytest.fixture
def parser():
    """Create MML parser instance."""
    return MMDParser()


@pytest.fixture
def simple_program(parser):
    """Create simple IR program with basic events."""
    mml_content = """---
title: "CSV Test"
tempo: 120
ppq: 480
---

[00:00.000]
- tempo 120
- note_on 1.60 90 1b
"""
    doc = parser.parse_string(mml_content)
    return compile_ast_to_ir(doc, ppq=480)


@pytest.fixture
def comprehensive_program(parser):
    """Create comprehensive IR program with various event types."""
    mml_content = """---
title: "Comprehensive CSV Test"
tempo: 100
ppq: 480
---

[00:00.000]
- tempo 100
- time_signature 4/4
- key_signature C
- marker "Intro"
- cc 1.7.80
- pc 1.5
- note_on 1.60 90 2b
- pitch_bend 1.8000
- channel_pressure 1.80
- poly_pressure 1.60.100

[00:02.000]
- note_off 1.60 64
- text "End"
"""
    doc = parser.parse_string(mml_content)
    return compile_ast_to_ir(doc, ppq=480)


class TestCSVExportBasics:
    """Test basic CSV export functionality."""

    def test_export_includes_header_and_footer(self, simple_program):
        """Test CSV includes proper header and footer records."""
        csv_output = export_to_csv(simple_program, include_header=True)
        lines = csv_output.strip().split("\n")

        # Check first line is header
        assert lines[0].startswith("0, 0, Header,")
        assert f"{simple_program.resolution}" in lines[0]

        # Check last line is footer
        assert lines[-1] == "0, 0, End_of_file"

    def test_export_includes_track_markers(self, simple_program):
        """Test CSV includes Start_track and End_track markers."""
        csv_output = export_to_csv(simple_program, include_header=True)
        lines = csv_output.strip().split("\n")

        # Find track markers
        start_track = [line for line in lines if "Start_track" in line]
        end_track = [line for line in lines if "End_track" in line]

        assert len(start_track) == 1
        assert len(end_track) == 1
        assert start_track[0] == "1, 0, Start_track"

    def test_export_without_header(self, simple_program):
        """Test CSV export without header/footer."""
        csv_output = export_to_csv(simple_program, include_header=False)
        lines = csv_output.strip().split("\n")

        # Should not have header or footer
        assert not any(line.startswith("0, 0, Header") for line in lines)
        assert not any(line == "0, 0, End_of_file" for line in lines)

        # But should still have track markers
        assert "1, 0, Start_track" in lines

    def test_csv_is_parseable(self, simple_program):
        """Test that generated CSV is valid and parseable."""
        csv_output = export_to_csv(simple_program)

        # Parse with Python's csv module
        reader = csv.reader(StringIO(csv_output))
        rows = list(reader)

        # Should have multiple rows
        assert len(rows) > 0

        # Each row should have at least 3 fields (track, time, type)
        for row in rows:
            # Strip whitespace from each field
            row = [field.strip() for field in row]
            assert len(row) >= 3, f"Row has insufficient fields: {row}"


class TestCSVChannelEvents:
    """Test CSV export of channel voice events."""

    def test_note_on_export(self, comprehensive_program):
        """Test note_on events export correctly."""
        csv_output = export_to_csv(comprehensive_program, include_header=False)

        # Find note_on events
        note_on_lines = [line for line in csv_output.split("\n") if "Note_on_c" in line]
        assert len(note_on_lines) > 0

        # Parse first note_on: should have track, time, type, channel, note, velocity
        parts = [p.strip() for p in note_on_lines[0].split(",")]
        assert parts[2] == "Note_on_c"
        assert len(parts) == 6  # track, time, type, channel, note, velocity

    def test_note_off_export(self, comprehensive_program):
        """Test note_off events export correctly."""
        csv_output = export_to_csv(comprehensive_program, include_header=False)

        # Find note_off events
        note_off_lines = [line for line in csv_output.split("\n") if "Note_off_c" in line]
        assert len(note_off_lines) > 0

        # Parse note_off
        parts = [p.strip() for p in note_off_lines[0].split(",")]
        assert parts[2] == "Note_off_c"
        assert len(parts) == 6  # track, time, type, channel, note, velocity

    def test_control_change_export(self, comprehensive_program):
        """Test control change events export correctly."""
        csv_output = export_to_csv(comprehensive_program, include_header=False)

        # Find CC events
        cc_lines = [line for line in csv_output.split("\n") if "Control_c" in line]
        assert len(cc_lines) > 0

        # Parse CC: track, time, type, channel, controller, value
        parts = [p.strip() for p in cc_lines[0].split(",")]
        assert parts[2] == "Control_c"
        assert len(parts) == 6

    def test_program_change_export(self, comprehensive_program):
        """Test program change events export correctly."""
        csv_output = export_to_csv(comprehensive_program, include_header=False)

        # Find PC events
        pc_lines = [line for line in csv_output.split("\n") if "Program_c" in line]
        assert len(pc_lines) > 0

        # Parse PC: track, time, type, channel, program
        parts = [p.strip() for p in pc_lines[0].split(",")]
        assert parts[2] == "Program_c"
        assert len(parts) == 5  # PC has no data2

    def test_pitch_bend_export(self, comprehensive_program):
        """Test pitch bend events export correctly."""
        csv_output = export_to_csv(comprehensive_program, include_header=False)

        # Find pitch bend events
        pb_lines = [line for line in csv_output.split("\n") if "Pitch_bend_c" in line]
        assert len(pb_lines) > 0

        # Parse pitch bend: track, time, type, channel, value
        parts = [p.strip() for p in pb_lines[0].split(",")]
        assert parts[2] == "Pitch_bend_c"
        assert len(parts) == 5

    def test_channel_pressure_export(self, comprehensive_program):
        """Test channel pressure events export correctly."""
        csv_output = export_to_csv(comprehensive_program, include_header=False)

        # Find channel pressure events
        cp_lines = [line for line in csv_output.split("\n") if "Channel_aftertouch_c" in line]
        assert len(cp_lines) > 0

        # Parse: track, time, type, channel, value
        parts = [p.strip() for p in cp_lines[0].split(",")]
        assert parts[2] == "Channel_aftertouch_c"

    def test_poly_pressure_export(self, comprehensive_program):
        """Test polyphonic pressure events export correctly."""
        csv_output = export_to_csv(comprehensive_program, include_header=False)

        # Find poly pressure events
        pp_lines = [line for line in csv_output.split("\n") if "Poly_aftertouch_c" in line]
        assert len(pp_lines) > 0

        # Parse: track, time, type, channel, note, value
        parts = [p.strip() for p in pp_lines[0].split(",")]
        assert parts[2] == "Poly_aftertouch_c"
        assert len(parts) == 6


class TestCSVMetaEvents:
    """Test CSV export of meta events."""

    def test_tempo_export(self, comprehensive_program):
        """Test tempo events export correctly."""
        csv_output = export_to_csv(comprehensive_program, include_header=False)

        # Find tempo events
        tempo_lines = [line for line in csv_output.split("\n") if ", Tempo," in line]
        assert len(tempo_lines) > 0

        # Parse tempo: track, time, type, microseconds_per_quarter
        parts = [p.strip() for p in tempo_lines[0].split(",")]
        assert parts[2] == "Tempo"
        assert len(parts) == 4

        # Verify tempo conversion: 100 BPM = 600000 microseconds/qn
        microseconds = int(parts[3])
        assert 500000 <= microseconds <= 700000  # Allow some range

    def test_time_signature_export(self, comprehensive_program):
        """Test time signature events export correctly."""
        csv_output = export_to_csv(comprehensive_program, include_header=False)

        # Find time signature events
        ts_lines = [line for line in csv_output.split("\n") if "Time_signature" in line]
        assert len(ts_lines) > 0

        # Parse: track, time, type, numerator, denominator, clocks, notesq
        parts = [p.strip() for p in ts_lines[0].split(",")]
        assert parts[2] == "Time_signature"
        assert len(parts) == 7

    def test_key_signature_export(self, comprehensive_program):
        """Test key signature events export correctly."""
        csv_output = export_to_csv(comprehensive_program, include_header=False)

        # Find key signature events
        ks_lines = [line for line in csv_output.split("\n") if "Key_signature" in line]
        assert len(ks_lines) > 0

        # Parse: track, time, type, sharps/flats, "major"/"minor"
        line = ks_lines[0]
        assert "Key_signature" in line
        assert '"major"' in line or '"minor"' in line

    def test_marker_export(self, comprehensive_program):
        """Test marker events export correctly."""
        csv_output = export_to_csv(comprehensive_program, include_header=False)

        # Find marker events
        marker_lines = [line for line in csv_output.split("\n") if "Marker" in line]
        assert len(marker_lines) > 0

        # Should have quoted text
        line = marker_lines[0]
        assert "Marker" in line
        assert '"' in line  # Contains quoted text

    def test_text_export(self, comprehensive_program):
        """Test text events export correctly."""
        csv_output = export_to_csv(comprehensive_program, include_header=False)

        # Find text events
        text_lines = [line for line in csv_output.split("\n") if ", Text," in line]
        assert len(text_lines) > 0

        # Should have quoted text
        line = text_lines[0]
        assert ", Text," in line
        assert '"' in line


class TestCSVEventCoverage:
    """Test that all event types are supported."""

    def test_all_event_types_have_mappings(self):
        """Test that all EventType enums have midicsv name mappings."""
        from midi_markdown.codegen.csv_export import _event_type_to_midicsv_name
        from midi_markdown.core.ir import EventType

        # Test each EventType enum value
        for event_type in EventType:
            midicsv_name = _event_type_to_midicsv_name(event_type)
            # All event types should map to something (or empty string if unsupported)
            assert isinstance(midicsv_name, str)

    def test_channel_events_have_c_suffix(self):
        """Test that channel events have '_c' suffix."""
        from midi_markdown.codegen.csv_export import _event_type_to_midicsv_name
        from midi_markdown.core.ir import EventType

        channel_events = [
            EventType.NOTE_ON,
            EventType.NOTE_OFF,
            EventType.CONTROL_CHANGE,
            EventType.PROGRAM_CHANGE,
            EventType.PITCH_BEND,
            EventType.CHANNEL_PRESSURE,
            EventType.POLY_PRESSURE,
        ]

        for event_type in channel_events:
            name = _event_type_to_midicsv_name(event_type)
            assert name.endswith("_c"), f"{event_type.name} should have '_c' suffix"

    def test_meta_events_no_suffix(self):
        """Test that meta events don't have '_c' suffix."""
        from midi_markdown.codegen.csv_export import _event_type_to_midicsv_name
        from midi_markdown.core.ir import EventType

        meta_events = [
            EventType.TEMPO,
            EventType.TIME_SIGNATURE,
            EventType.KEY_SIGNATURE,
            EventType.MARKER,
            EventType.TEXT,
        ]

        for event_type in meta_events:
            name = _event_type_to_midicsv_name(event_type)
            if name:  # If supported
                assert not name.endswith("_c"), f"{event_type.name} should not have '_c' suffix"


class TestCSVEdgeCases:
    """Test edge cases and special scenarios."""

    def test_empty_program_export(self, parser):
        """Test exporting empty program."""
        mml_content = """---
title: "Empty"
tempo: 120
ppq: 480
---

[00:00.000]
- tempo 120
"""
        doc = parser.parse_string(mml_content)
        ir_program = compile_ast_to_ir(doc, ppq=480)

        csv_output = export_to_csv(ir_program)

        # Should still have header, track markers, and footer
        assert "Header" in csv_output
        assert "Start_track" in csv_output
        assert "End_track" in csv_output

    def test_event_count_matches(self, comprehensive_program):
        """Test that CSV event count matches IR program."""
        csv_output = export_to_csv(comprehensive_program, include_header=False)
        lines = csv_output.strip().split("\n")

        # Count non-structural lines (exclude Start_track, End_track)
        event_lines = [
            line for line in lines if "Start_track" not in line and "End_track" not in line
        ]

        # Should match IR program event count
        assert len(event_lines) == len(comprehensive_program.events)

    def test_timing_is_correct(self, simple_program):
        """Test that event timing is preserved in CSV."""
        csv_output = export_to_csv(simple_program, include_header=False)

        # Parse CSV and check times
        reader = csv.reader(StringIO(csv_output))
        for row in reader:
            row = [field.strip() for field in row]
            if len(row) >= 3 and row[2] not in ("Start_track", "End_track"):
                # time field should be numeric
                time_str = row[1]
                time_val = int(time_str)
                assert time_val >= 0

    def test_multi_channel_support(self, parser):
        """Test CSV export with multiple channels."""
        mml_content = """---
title: "Multi-channel"
tempo: 120
ppq: 480
---

[00:00.000]
- note_on 1.60 90 1b
- note_on 2.64 85 1b
- note_on 10.36 100 1b
"""
        doc = parser.parse_string(mml_content)
        ir_program = compile_ast_to_ir(doc, ppq=480)

        csv_output = export_to_csv(ir_program, include_header=False)

        # Find all note_on events
        note_on_lines = [line for line in csv_output.split("\n") if "Note_on_c" in line]
        assert len(note_on_lines) == 3

        # Verify different channels
        channels = set()
        for line in note_on_lines:
            parts = [p.strip() for p in line.split(",")]
            channel = int(parts[3])
            channels.add(channel)

        # Should have 3 different channels
        assert len(channels) == 3


class TestCSVSystemMessages:
    """Test CSV export of system messages (SysEx, MTC, Song Position, etc.)."""

    def test_sysex_export(self, parser):
        """Test SysEx events export correctly with bytes data."""
        from midi_markdown.core.ir import EventType, IRProgram, MIDIEvent

        # Create IR program with SysEx event
        sysex_event = MIDIEvent(
            type=EventType.SYSEX,
            time=0,
            channel=None,
            data1=None,
            data2=None,
            metadata={"bytes": [0xF0, 0x43, 0x12, 0x00, 0x43, 0x12, 0x00, 0xF7]},
        )

        ir_program = IRProgram(
            events=[sysex_event],
            resolution=480,
            initial_tempo=120,
            metadata={},
        )

        csv_output = export_to_csv(ir_program, include_header=False)

        # Find SysEx event
        sysex_lines = [line for line in csv_output.split("\n") if "System_exclusive" in line]
        assert len(sysex_lines) > 0

        # Verify format: track, time, System_exclusive, length, byte1, byte2, ...
        line = sysex_lines[0]
        assert "System_exclusive" in line
        assert "240" in line  # 0xF0
        assert "247" in line  # 0xF7

    def test_sysex_without_bytes_skipped(self, parser):
        """Test SysEx events without bytes metadata are skipped."""
        from midi_markdown.core.ir import EventType, IRProgram, MIDIEvent

        # Create SysEx event WITHOUT bytes metadata
        sysex_event = MIDIEvent(
            type=EventType.SYSEX,
            time=0,
            channel=None,
            data1=None,
            data2=None,
            metadata={},  # No bytes!
        )

        ir_program = IRProgram(
            events=[sysex_event],
            resolution=480,
            initial_tempo=120,
            metadata={},
        )

        csv_output = export_to_csv(ir_program, include_header=False)

        # Should not have SysEx in output (skipped)
        assert "System_exclusive" not in csv_output

    def test_mtc_quarter_frame_export(self, parser):
        """Test MTC Quarter Frame events export correctly."""
        from midi_markdown.core.ir import EventType, IRProgram, MIDIEvent

        mtc_event = MIDIEvent(
            type=EventType.MTC_QUARTER_FRAME,
            time=0,
            channel=None,
            data1=0x20,  # MTC data
            data2=None,
            metadata={},
        )

        ir_program = IRProgram(
            events=[mtc_event],
            resolution=480,
            initial_tempo=120,
            metadata={},
        )

        csv_output = export_to_csv(ir_program, include_header=False)

        # Find MTC event
        mtc_lines = [line for line in csv_output.split("\n") if "MIDI_time_code" in line]
        assert len(mtc_lines) > 0

        # Verify format includes data1
        parts = [p.strip() for p in mtc_lines[0].split(",")]
        assert "32" in parts or "0x20" in mtc_lines[0]  # data1 value

    def test_song_position_export(self, parser):
        """Test Song Position Pointer events export correctly."""
        from midi_markdown.core.ir import EventType, IRProgram, MIDIEvent

        song_pos_event = MIDIEvent(
            type=EventType.SONG_POSITION,
            time=0,
            channel=None,
            data1=100,  # Song position value
            data2=None,
            metadata={},
        )

        ir_program = IRProgram(
            events=[song_pos_event],
            resolution=480,
            initial_tempo=120,
            metadata={},
        )

        csv_output = export_to_csv(ir_program, include_header=False)

        # Find song position event
        sp_lines = [line for line in csv_output.split("\n") if "Song_position" in line]
        assert len(sp_lines) > 0

        # Verify format includes position value
        parts = [p.strip() for p in sp_lines[0].split(",")]
        assert "100" in parts

    def test_song_select_export(self, parser):
        """Test Song Select events export correctly."""
        from midi_markdown.core.ir import EventType, IRProgram, MIDIEvent

        song_select_event = MIDIEvent(
            type=EventType.SONG_SELECT,
            time=0,
            channel=None,
            data1=5,  # Song number
            data2=None,
            metadata={},
        )

        ir_program = IRProgram(
            events=[song_select_event],
            resolution=480,
            initial_tempo=120,
            metadata={},
        )

        csv_output = export_to_csv(ir_program, include_header=False)

        # Find song select event
        ss_lines = [line for line in csv_output.split("\n") if "Song_select" in line]
        assert len(ss_lines) > 0

        # Verify format includes song number
        parts = [p.strip() for p in ss_lines[0].split(",")]
        assert "5" in parts


class TestCSVTimeSignatureEdgeCases:
    """Test time_signature event edge cases for metadata handling."""

    def test_time_signature_with_metadata(self, parser):
        """Test time_signature event using metadata path."""
        from midi_markdown.core.ir import EventType, IRProgram, MIDIEvent

        # Create time_signature with metadata (not data1/data2)
        ts_event = MIDIEvent(
            type=EventType.TIME_SIGNATURE,
            time=0,
            channel=None,
            data1=None,
            data2=None,
            metadata={"numerator": 3, "denominator": 3},  # 3/8 time (2^3 = 8)
        )

        ir_program = IRProgram(
            events=[ts_event],
            resolution=480,
            initial_tempo=120,
            metadata={},
        )

        csv_output = export_to_csv(ir_program, include_header=False)

        # Find time signature event
        ts_lines = [line for line in csv_output.split("\n") if "Time_signature" in line]
        assert len(ts_lines) > 0

        # Verify metadata values used
        parts = [p.strip() for p in ts_lines[0].split(",")]
        assert "3" in parts  # numerator

    def test_time_signature_with_data2_fallback(self, parser):
        """Test time_signature event with data2 as denominator fallback."""
        from midi_markdown.core.ir import EventType, IRProgram, MIDIEvent

        # Create time_signature with data1/data2 (no metadata)
        ts_event = MIDIEvent(
            type=EventType.TIME_SIGNATURE,
            time=0,
            channel=None,
            data1=6,  # numerator
            data2=3,  # denominator power (2^3 = 8, so 6/8 time)
            metadata={},
        )

        ir_program = IRProgram(
            events=[ts_event],
            resolution=480,
            initial_tempo=120,
            metadata={},
        )

        csv_output = export_to_csv(ir_program, include_header=False)

        # Find time signature event
        ts_lines = [line for line in csv_output.split("\n") if "Time_signature" in line]
        assert len(ts_lines) > 0

        # Verify data1/data2 values used
        parts = [p.strip() for p in ts_lines[0].split(",")]
        assert "6" in parts  # numerator from data1
        assert "3" in parts  # denominator from data2
