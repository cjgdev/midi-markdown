"""Integration tests for JSON export functionality."""

from __future__ import annotations

import json

import pytest

from midi_markdown.codegen import export_to_json
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
title: "JSON Test"
author: "Test Author"
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
title: "Comprehensive JSON Test"
author: "Test Author"
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


class TestJSONExportBasics:
    """Test basic JSON export functionality."""

    def test_json_is_valid(self, simple_program):
        """Test that generated JSON is valid."""
        json_output = export_to_json(simple_program, format="complete")

        # Should be parseable
        data = json.loads(json_output)
        assert isinstance(data, dict)
        assert "metadata" in data
        assert "events" in data

    def test_pretty_print_vs_compact(self, simple_program):
        """Test pretty-print vs compact JSON output."""
        json_pretty = export_to_json(simple_program, pretty=True)
        json_compact = export_to_json(simple_program, pretty=False)

        # Pretty should have newlines and indentation
        assert "\n" in json_pretty
        assert "  " in json_pretty

        # Compact should be single line (or fewer lines)
        assert len(json_compact.split("\n")) < len(json_pretty.split("\n"))

        # Both should parse to same data
        data_pretty = json.loads(json_pretty)
        data_compact = json.loads(json_compact)
        assert data_pretty == data_compact

    def test_round_trip_parsing(self, comprehensive_program):
        """Test that JSON can be parsed back into Python."""
        json_output = export_to_json(comprehensive_program, format="complete")

        # Parse JSON
        data = json.loads(json_output)

        # Verify structure
        assert "metadata" in data
        assert "events" in data
        assert isinstance(data["metadata"], dict)
        assert isinstance(data["events"], list)


class TestCompleteFormat:
    """Test complete JSON format."""

    def test_complete_format_has_all_fields(self, comprehensive_program):
        """Test complete format includes all MIDI data."""
        json_output = export_to_json(comprehensive_program, format="complete")
        data = json.loads(json_output)

        # Check metadata fields
        metadata = data["metadata"]
        assert "title" in metadata
        assert "duration_ticks" in metadata
        assert "duration_seconds" in metadata
        assert "resolution" in metadata
        assert "initial_tempo" in metadata
        assert "event_count" in metadata

        # Check event fields
        for event in data["events"]:
            assert "time" in event
            assert "time_seconds" in event
            assert "type" in event
            # channel, data1, data2 may be None for meta events

    def test_complete_format_preserves_exact_values(self, simple_program):
        """Test complete format preserves exact MIDI values."""
        json_output = export_to_json(simple_program, format="complete")
        data = json.loads(json_output)

        # Find note_on event
        note_events = [e for e in data["events"] if e["type"] == "note_on"]
        assert len(note_events) > 0

        note = note_events[0]
        assert note["data1"] == 60  # Note number
        assert note["data2"] == 90  # Velocity
        assert note["channel"] == 1

    def test_complete_format_metadata_accuracy(self, comprehensive_program):
        """Test metadata is accurate."""
        json_output = export_to_json(comprehensive_program, format="complete")
        data = json.loads(json_output)

        metadata = data["metadata"]
        assert metadata["title"] == "Comprehensive JSON Test"
        assert metadata["author"] == "Test Author"
        assert metadata["resolution"] == 480
        assert metadata["initial_tempo"] == 100
        assert metadata["event_count"] == len(comprehensive_program.events)

    def test_complete_format_all_event_types(self, comprehensive_program):
        """Test complete format handles all event types."""
        json_output = export_to_json(comprehensive_program, format="complete")
        data = json.loads(json_output)

        # Find different event types
        event_types = {e["type"] for e in data["events"]}

        # Should have various types
        assert "tempo" in event_types
        assert "note_on" in event_types
        assert "control_change" in event_types
        assert "program_change" in event_types


class TestSimplifiedFormat:
    """Test simplified JSON format."""

    def test_simplified_format_is_readable(self, comprehensive_program):
        """Test simplified format is human-readable."""
        json_output = export_to_json(comprehensive_program, format="simplified")
        data = json.loads(json_output)

        # Check that times are readable strings
        for event in data["events"]:
            assert "time" in event
            assert isinstance(event["time"], str)
            assert event["time"].endswith("s")

            assert "musical_time" in event
            assert isinstance(event["musical_time"], str)
            assert "." in event["musical_time"]  # Should have bars.beats.ticks format

    def test_simplified_format_note_names(self, comprehensive_program):
        """Test simplified format converts note numbers to names."""
        json_output = export_to_json(comprehensive_program, format="simplified")
        data = json.loads(json_output)

        # Find note events
        note_events = [e for e in data["events"] if e["type"] in ("note_on", "note_off")]
        assert len(note_events) > 0

        for note in note_events:
            assert "note" in note
            assert isinstance(note["note"], str)
            assert "note_number" in note
            assert isinstance(note["note_number"], int)

    def test_simplified_format_controller_names(self, comprehensive_program):
        """Test simplified format includes controller names."""
        json_output = export_to_json(comprehensive_program, format="simplified")
        data = json.loads(json_output)

        # Find CC events
        cc_events = [e for e in data["events"] if e["type"] == "control_change"]
        assert len(cc_events) > 0

        for cc in cc_events:
            assert "controller" in cc
            assert isinstance(cc["controller"], str)
            assert "controller_number" in cc
            assert "value" in cc

    def test_simplified_format_tempo_events(self, comprehensive_program):
        """Test simplified format handles tempo events."""
        json_output = export_to_json(comprehensive_program, format="simplified")
        data = json.loads(json_output)

        # Find tempo events
        tempo_events = [e for e in data["events"] if e["type"] == "tempo"]
        assert len(tempo_events) > 0

        tempo = tempo_events[0]
        assert "bpm" in tempo
        assert tempo["bpm"] == 100

    def test_simplified_format_time_signature(self, comprehensive_program):
        """Test simplified format handles time signature."""
        json_output = export_to_json(comprehensive_program, format="simplified")
        data = json.loads(json_output)

        # Find time signature events
        ts_events = [e for e in data["events"] if e["type"] == "time_signature"]
        assert len(ts_events) > 0

        ts = ts_events[0]
        assert "numerator" in ts
        assert "denominator" in ts
        assert ts["numerator"] == 4
        assert ts["denominator"] == 4  # 2^2 = 4

    def test_simplified_format_pitch_bend(self, comprehensive_program):
        """Test simplified format handles pitch bend."""
        json_output = export_to_json(comprehensive_program, format="simplified")
        data = json.loads(json_output)

        # Find pitch bend events
        pb_events = [e for e in data["events"] if e["type"] == "pitch_bend"]
        assert len(pb_events) > 0

        pb = pb_events[0]
        assert "value" in pb
        # Value should be signed (-8192 to +8191)
        assert isinstance(pb["value"], int)

    def test_simplified_format_markers(self, comprehensive_program):
        """Test simplified format handles markers."""
        json_output = export_to_json(comprehensive_program, format="simplified")
        data = json.loads(json_output)

        # Find marker events
        marker_events = [e for e in data["events"] if e["type"] == "marker"]
        assert len(marker_events) > 0

        marker = marker_events[0]
        assert "text" in marker


class TestJSONEdgeCases:
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

        json_output = export_to_json(ir_program, format="complete")
        data = json.loads(json_output)

        assert "metadata" in data
        assert "events" in data
        assert isinstance(data["events"], list)

    def test_event_count_matches(self, comprehensive_program):
        """Test that JSON event count matches IR program."""
        json_output = export_to_json(comprehensive_program, format="complete")
        data = json.loads(json_output)

        assert len(data["events"]) == len(comprehensive_program.events)
        assert data["metadata"]["event_count"] == len(comprehensive_program.events)

    def test_multi_channel_support(self, parser):
        """Test JSON export with multiple channels."""
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

        json_output = export_to_json(ir_program, format="simplified")
        data = json.loads(json_output)

        # Find all note_on events
        note_events = [e for e in data["events"] if e["type"] == "note_on"]
        assert len(note_events) == 3

        # Verify different channels
        channels = {e["channel"] for e in note_events}
        assert len(channels) == 3

    def test_musical_time_formatting(self, simple_program):
        """Test musical time is formatted correctly."""
        json_output = export_to_json(simple_program, format="simplified")
        data = json.loads(json_output)

        # All events should have musical_time
        for event in data["events"]:
            assert "musical_time" in event
            # Should be in format "bar.beat.tick"
            parts = event["musical_time"].split(".")
            assert len(parts) == 3


class TestFormatComparison:
    """Test differences between complete and simplified formats."""

    def test_format_differences(self, comprehensive_program):
        """Test that complete and simplified formats differ appropriately."""
        json_complete = export_to_json(comprehensive_program, format="complete")
        json_simplified = export_to_json(comprehensive_program, format="simplified")

        data_complete = json.loads(json_complete)
        data_simplified = json.loads(json_simplified)

        # Both should have same number of events
        assert len(data_complete["events"]) == len(data_simplified["events"])

        # But event structures should differ
        if len(data_complete["events"]) > 0:
            complete_event = data_complete["events"][0]
            simplified_event = data_simplified["events"][0]

            # Complete has data1/data2, simplified has readable fields
            assert set(complete_event.keys()) != set(simplified_event.keys())

    def test_both_formats_have_metadata(self, comprehensive_program):
        """Test both formats include metadata."""
        json_complete = export_to_json(comprehensive_program, format="complete")
        json_simplified = export_to_json(comprehensive_program, format="simplified")

        data_complete = json.loads(json_complete)
        data_simplified = json.loads(json_simplified)

        # Both should have same metadata
        assert data_complete["metadata"]["title"] == data_simplified["metadata"]["title"]
        assert (
            data_complete["metadata"]["event_count"] == data_simplified["metadata"]["event_count"]
        )
