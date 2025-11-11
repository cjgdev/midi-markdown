"""Tests for diagnostics formatter module."""

from __future__ import annotations

from midi_markdown.core.ir import EventType, IRProgram, MIDIEvent
from midi_markdown.diagnostics.formatter import (
    display_events_table,
    format_event_details,
    format_musical_time,
    get_event_summary,
)


class TestFormatMusicalTime:
    """Test musical time formatting."""

    def test_format_musical_time_start(self):
        """Test formatting at start of song."""
        assert format_musical_time(0, 480) == "1.1.000"

    def test_format_musical_time_one_beat(self):
        """Test formatting after one beat."""
        assert format_musical_time(480, 480) == "1.2.000"

    def test_format_musical_time_one_bar(self):
        """Test formatting after one bar (4 beats)."""
        assert format_musical_time(1920, 480) == "2.1.000"

    def test_format_musical_time_with_ticks(self):
        """Test formatting with tick offset."""
        assert format_musical_time(600, 480) == "1.2.120"
        assert format_musical_time(1440, 480) == "1.4.000"

    def test_format_musical_time_multiple_bars(self):
        """Test formatting across multiple bars."""
        assert format_musical_time(3840, 480) == "3.1.000"  # 2 bars
        assert format_musical_time(7680, 480) == "5.1.000"  # 4 bars

    def test_format_musical_time_different_ppq(self):
        """Test formatting with different PPQ values."""
        assert format_musical_time(0, 960) == "1.1.000"
        assert format_musical_time(960, 960) == "1.2.000"
        assert format_musical_time(3840, 960) == "2.1.000"


class TestFormatEventDetails:
    """Test event detail formatting."""

    def test_format_note_on(self):
        """Test note_on event formatting."""
        event = MIDIEvent(
            time=0,
            type=EventType.NOTE_ON,
            channel=1,
            data1=60,  # Middle C
            data2=90,  # Velocity
        )
        details = format_event_details(event)
        assert "C4" in details
        assert "#60" in details
        assert "vel:90" in details

    def test_format_note_off(self):
        """Test note_off event formatting."""
        event = MIDIEvent(
            time=480,
            type=EventType.NOTE_OFF,
            channel=1,
            data1=60,
            data2=64,
        )
        details = format_event_details(event)
        assert "C4" in details
        assert "vel:64" in details

    def test_format_control_change(self):
        """Test control_change event formatting."""
        event = MIDIEvent(
            time=0,
            type=EventType.CONTROL_CHANGE,
            channel=1,
            data1=7,  # Volume
            data2=100,
        )
        details = format_event_details(event)
        assert "CC#7" in details
        assert "Volume" in details
        assert "val:100" in details

    def test_format_program_change(self):
        """Test program_change event formatting."""
        event = MIDIEvent(
            time=0,
            type=EventType.PROGRAM_CHANGE,
            channel=1,
            data1=0,  # Acoustic Grand Piano
            data2=0,
        )
        details = format_event_details(event)
        assert "Program 0" in details

    def test_format_pitch_bend(self):
        """Test pitch_bend event formatting."""
        event = MIDIEvent(
            time=0,
            type=EventType.PITCH_BEND,
            channel=1,
            data1=8192,  # Center (no bend)
            data2=0,
        )
        details = format_event_details(event)
        assert "Bend" in details
        assert "+0" in details

        # Positive bend
        event.data1 = 10000
        details = format_event_details(event)
        assert "+1808" in details

        # Negative bend
        event.data1 = 6000
        details = format_event_details(event)
        assert "-2192" in details

    def test_format_tempo(self):
        """Test tempo event formatting."""
        event = MIDIEvent(
            time=0,
            type=EventType.TEMPO,
            channel=0,
            data1=120,
            data2=0,
        )
        details = format_event_details(event)
        assert "120 BPM" in details

    def test_format_channel_pressure(self):
        """Test channel_pressure event formatting."""
        event = MIDIEvent(
            time=0,
            type=EventType.CHANNEL_PRESSURE,
            channel=1,
            data1=80,
            data2=0,
        )
        details = format_event_details(event)
        assert "Pressure: 80" in details

    def test_format_poly_pressure(self):
        """Test poly_pressure event formatting."""
        event = MIDIEvent(
            time=0,
            type=EventType.POLY_PRESSURE,
            channel=1,
            data1=60,  # Note
            data2=70,  # Pressure
        )
        details = format_event_details(event)
        assert "C4" in details
        assert "pressure: 70" in details

    def test_format_marker(self):
        """Test marker event formatting."""
        event = MIDIEvent(
            time=0,
            type=EventType.MARKER,
            channel=0,
            data1=0,
            data2=0,
            metadata={"text": "Verse 1"},
        )
        details = format_event_details(event)
        assert "Verse 1" in details

    def test_format_text(self):
        """Test text event formatting."""
        event = MIDIEvent(
            time=0,
            type=EventType.TEXT,
            channel=0,
            data1=0,
            data2=0,
            metadata={"text": "Composed by..."},
        )
        details = format_event_details(event)
        assert "Composed by..." in details

    def test_format_sysex_short(self):
        """Test sysex event formatting with short data."""
        event = MIDIEvent(
            time=0,
            type=EventType.SYSEX,
            channel=0,
            data1=0,
            data2=0,
            metadata={"bytes": [0xF0, 0x43, 0x10, 0xF7]},
        )
        details = format_event_details(event)
        assert "SysEx" in details
        assert "F0" in details
        assert "F7" in details

    def test_format_sysex_long(self):
        """Test sysex event formatting with long data."""
        event = MIDIEvent(
            time=0,
            type=EventType.SYSEX,
            channel=0,
            data1=0,
            data2=0,
            metadata={"bytes": [0xF0] + [0x00] * 20 + [0xF7]},
        )
        details = format_event_details(event)
        assert "SysEx: 22 bytes" in details


class TestGetEventSummary:
    """Test event summary generation."""

    def test_summary_empty_program(self):
        """Test summary for empty program."""
        ir_program = IRProgram(
            resolution=480,
            initial_tempo=120,
            events=[],
            metadata={},
        )
        summary = get_event_summary(ir_program)
        assert summary["total_events"] == 0
        assert summary["duration_ticks"] == 0
        assert summary["duration_seconds"] == 0.0
        assert summary["channels_used"] == []

    def test_summary_single_event(self):
        """Test summary for single event."""
        event = MIDIEvent(
            time=480,
            type=EventType.NOTE_ON,
            channel=1,
            data1=60,
            data2=90,
            time_seconds=0.5,
        )
        ir_program = IRProgram(
            resolution=480,
            initial_tempo=120,
            events=[event],
            metadata={},
        )
        summary = get_event_summary(ir_program)
        assert summary["total_events"] == 1
        assert summary["duration_ticks"] == 480
        assert summary["duration_seconds"] == 0.5
        assert summary["channels_used"] == [1]
        assert summary["resolution"] == 480
        assert summary["initial_tempo"] == 120

    def test_summary_multiple_channels(self):
        """Test summary with multiple channels."""
        events = [
            MIDIEvent(time=0, type=EventType.NOTE_ON, channel=1, data1=60, data2=90),
            MIDIEvent(time=480, type=EventType.NOTE_ON, channel=2, data1=64, data2=85),
            MIDIEvent(time=960, type=EventType.NOTE_ON, channel=1, data1=67, data2=80),
            MIDIEvent(time=1440, type=EventType.NOTE_ON, channel=3, data1=72, data2=75),
        ]
        ir_program = IRProgram(
            resolution=480,
            initial_tempo=120,
            events=events,
            metadata={},
        )
        summary = get_event_summary(ir_program)
        assert summary["total_events"] == 4
        assert summary["channels_used"] == [1, 2, 3]

    def test_summary_meta_events_no_channel(self):
        """Test summary with meta events (no channel)."""
        events = [
            MIDIEvent(time=0, type=EventType.TEMPO, channel=None, data1=120, data2=0),
            MIDIEvent(time=480, type=EventType.NOTE_ON, channel=1, data1=60, data2=90),
        ]
        ir_program = IRProgram(
            resolution=480,
            initial_tempo=120,
            events=events,
            metadata={},
        )
        summary = get_event_summary(ir_program)
        assert summary["total_events"] == 2
        assert summary["channels_used"] == [1]  # Only channel events counted


class TestDisplayEventsTable:
    """Test table display functionality."""

    def test_display_events_table_basic(self):
        """Test basic table display without crashing."""
        events = [
            MIDIEvent(
                time=0,
                type=EventType.TEMPO,
                channel=None,
                data1=120,
                data2=0,
                time_seconds=0.0,
            ),
            MIDIEvent(
                time=0,
                type=EventType.NOTE_ON,
                channel=1,
                data1=60,
                data2=90,
                time_seconds=0.0,
            ),
            MIDIEvent(
                time=480,
                type=EventType.NOTE_OFF,
                channel=1,
                data1=60,
                data2=64,
                time_seconds=0.5,
            ),
        ]
        ir_program = IRProgram(
            resolution=480,
            initial_tempo=120,
            events=events,
            metadata={"title": "Test Song"},
        )

        # Should not crash
        display_events_table(ir_program, max_events=10, show_stats=True)

    def test_display_events_table_empty(self):
        """Test table display with empty program."""
        ir_program = IRProgram(
            resolution=480,
            initial_tempo=120,
            events=[],
            metadata={},
        )

        # Should not crash
        display_events_table(ir_program, max_events=10, show_stats=True)

    def test_display_events_table_limit(self):
        """Test table display with event limit."""
        # Create many events
        events = [
            MIDIEvent(
                time=i * 100,
                type=EventType.NOTE_ON,
                channel=1,
                data1=60 + (i % 12),
                data2=90,
                time_seconds=i * 0.1,
            )
            for i in range(150)
        ]
        ir_program = IRProgram(
            resolution=480,
            initial_tempo=120,
            events=events,
            metadata={},
        )

        # Should not crash and should limit output
        display_events_table(ir_program, max_events=50, show_stats=False)

    def test_display_events_table_no_limit(self):
        """Test table display without limit."""
        events = [
            MIDIEvent(
                time=i * 100,
                type=EventType.NOTE_ON,
                channel=1,
                data1=60,
                data2=90,
                time_seconds=i * 0.1,
            )
            for i in range(10)
        ]
        ir_program = IRProgram(
            resolution=480,
            initial_tempo=120,
            events=events,
            metadata={},
        )

        # Should display all events
        display_events_table(ir_program, max_events=None, show_stats=True)
