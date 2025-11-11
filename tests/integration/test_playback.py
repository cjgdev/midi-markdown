"""Integration tests for real-time MIDI playback."""

from __future__ import annotations

import time
from typing import Any
from unittest.mock import MagicMock

import pytest

from midi_markdown.core.ir import EventType, IRProgram, MIDIEvent
from midi_markdown.runtime.player import RealtimePlayer


@pytest.fixture
def simple_ir_program() -> IRProgram:
    """Create simple IR program for testing.

    Creates a program with 2 events: note on at tick 0, note off at tick 480.
    At 120 BPM with ppq=480, this equals 500ms duration.
    """
    return IRProgram(
        resolution=480,
        initial_tempo=120,
        events=[
            MIDIEvent(time=0, type=EventType.NOTE_ON, channel=1, data1=60, data2=80),
            MIDIEvent(time=480, type=EventType.NOTE_OFF, channel=1, data1=60, data2=0),
        ],
        metadata={"title": "Test Song", "author": "Test Author"},
    )


@pytest.fixture
def tempo_change_ir_program() -> IRProgram:
    """Create IR program with tempo change.

    Creates a program with tempo change from 120 to 140 BPM at tick 480.
    """
    return IRProgram(
        resolution=480,
        initial_tempo=120,
        events=[
            MIDIEvent(time=0, type=EventType.NOTE_ON, channel=1, data1=60, data2=80),
            MIDIEvent(time=480, type=EventType.TEMPO, channel=0, data1=140, data2=0),
            MIDIEvent(time=480, type=EventType.NOTE_OFF, channel=1, data1=60, data2=0),
            MIDIEvent(time=960, type=EventType.NOTE_ON, channel=1, data1=62, data2=80),
        ],
        metadata={"title": "Tempo Change Test"},
    )


@pytest.fixture
def mock_midi_port(monkeypatch: Any) -> MagicMock:
    """Mock MIDI port opening.

    Patches MIDIOutputManager to avoid needing real MIDI hardware.
    """
    mock_send = MagicMock()

    def mock_init(self: Any) -> None:
        self.midiout = MagicMock()
        self.current_port = None
        self.port_name = None

    def mock_open_port(self: Any, port: str | int) -> None:
        self.current_port = 0
        self.port_name = "Test Port"

    def mock_close_port(self: Any) -> None:
        self.current_port = None
        self.port_name = None

    def mock_send_message(self: Any, message: list[int]) -> None:
        mock_send(message)

    monkeypatch.setattr("midi_markdown.runtime.midi_io.MIDIOutputManager.__init__", mock_init)
    monkeypatch.setattr("midi_markdown.runtime.midi_io.MIDIOutputManager.open_port", mock_open_port)
    monkeypatch.setattr(
        "midi_markdown.runtime.midi_io.MIDIOutputManager.close_port", mock_close_port
    )
    monkeypatch.setattr(
        "midi_markdown.runtime.midi_io.MIDIOutputManager.send_message", mock_send_message
    )

    return mock_send


@pytest.mark.integration
class TestRealtimePlayer:
    """Integration tests for RealtimePlayer class."""

    def test_player_initialization(
        self, simple_ir_program: IRProgram, mock_midi_port: MagicMock
    ) -> None:
        """Test player initializes correctly."""
        player = RealtimePlayer(simple_ir_program, "Test Port")

        assert player.port_name == "Test Port"
        assert player.tempo_tracker.ppq == 480
        # 2 note events (tempo events are skipped)
        assert player.scheduler.event_queue.qsize() == 2

    def test_player_play_stop(
        self, simple_ir_program: IRProgram, mock_midi_port: MagicMock
    ) -> None:
        """Test basic play/stop functionality."""
        player = RealtimePlayer(simple_ir_program, "Test Port")

        player.play()
        assert player.scheduler.state == "playing"

        time.sleep(0.1)

        player.stop()
        assert player.scheduler.state == "stopped"

    def test_player_pause_resume(
        self, simple_ir_program: IRProgram, mock_midi_port: MagicMock
    ) -> None:
        """Test pause/resume functionality."""
        player = RealtimePlayer(simple_ir_program, "Test Port")

        player.play()
        player.pause()
        assert player.scheduler.state == "paused"

        player.resume()
        assert player.scheduler.state == "playing"

        player.stop()

    def test_player_duration(self, simple_ir_program: IRProgram, mock_midi_port: MagicMock) -> None:
        """Test duration calculation."""
        player = RealtimePlayer(simple_ir_program, "Test Port")

        # At 120 BPM with ppq=480, 480 ticks = 1 beat = 500ms
        assert player.get_duration_ms() == pytest.approx(500.0)

    def test_player_all_notes_off(
        self, simple_ir_program: IRProgram, mock_midi_port: MagicMock
    ) -> None:
        """Test All Notes Off sent on stop."""
        player = RealtimePlayer(simple_ir_program, "Test Port")

        player.play()
        time.sleep(0.1)

        # Clear previous calls
        mock_midi_port.reset_mock()

        player.stop()

        # Verify CC 123 sent on all 16 channels
        calls = mock_midi_port.call_args_list
        all_notes_off_calls = [call for call in calls if call[0][0][1] == 123]
        assert len(all_notes_off_calls) == 16  # One per channel

    def test_player_event_conversion_note_on(
        self, simple_ir_program: IRProgram, mock_midi_port: MagicMock
    ) -> None:
        """Test NOTE_ON event conversion."""
        event = MIDIEvent(time=0, type=EventType.NOTE_ON, channel=1, data1=60, data2=80)
        player = RealtimePlayer(simple_ir_program, "Test Port")

        message = player._event_to_midi_message(event)
        assert message == [0x90, 60, 80]  # Note On, channel 1, note 60, velocity 80

    def test_player_event_conversion_note_off(
        self, simple_ir_program: IRProgram, mock_midi_port: MagicMock
    ) -> None:
        """Test NOTE_OFF event conversion."""
        event = MIDIEvent(time=0, type=EventType.NOTE_OFF, channel=1, data1=60, data2=0)
        player = RealtimePlayer(simple_ir_program, "Test Port")

        message = player._event_to_midi_message(event)
        assert message == [0x80, 60, 0]  # Note Off, channel 1, note 60

    def test_player_event_conversion_cc(
        self, simple_ir_program: IRProgram, mock_midi_port: MagicMock
    ) -> None:
        """Test CONTROL_CHANGE event conversion."""
        event = MIDIEvent(time=0, type=EventType.CONTROL_CHANGE, channel=1, data1=7, data2=127)
        player = RealtimePlayer(simple_ir_program, "Test Port")

        message = player._event_to_midi_message(event)
        assert message == [0xB0, 7, 127]  # CC 7 (volume), value 127, channel 1

    def test_player_event_conversion_pc(
        self, simple_ir_program: IRProgram, mock_midi_port: MagicMock
    ) -> None:
        """Test PROGRAM_CHANGE event conversion."""
        event = MIDIEvent(time=0, type=EventType.PROGRAM_CHANGE, channel=1, data1=42, data2=0)
        player = RealtimePlayer(simple_ir_program, "Test Port")

        message = player._event_to_midi_message(event)
        assert message == [0xC0, 42]  # Program change 42, channel 1

    def test_player_event_conversion_pitch_bend(
        self, simple_ir_program: IRProgram, mock_midi_port: MagicMock
    ) -> None:
        """Test PITCH_BEND event conversion."""
        # Pitch bend value 8192 (center) = 0x2000
        # LSB = 0x00, MSB = 0x40
        event = MIDIEvent(time=0, type=EventType.PITCH_BEND, channel=1, data1=8192, data2=0)
        player = RealtimePlayer(simple_ir_program, "Test Port")

        message = player._event_to_midi_message(event)
        assert message == [0xE0, 0x00, 0x40]  # Pitch bend, channel 1, center position

    def test_player_event_conversion_channel_pressure(
        self, simple_ir_program: IRProgram, mock_midi_port: MagicMock
    ) -> None:
        """Test CHANNEL_PRESSURE event conversion."""
        event = MIDIEvent(time=0, type=EventType.CHANNEL_PRESSURE, channel=1, data1=64, data2=0)
        player = RealtimePlayer(simple_ir_program, "Test Port")

        message = player._event_to_midi_message(event)
        assert message == [0xD0, 64]  # Channel pressure 64, channel 1

    def test_player_event_conversion_poly_pressure(
        self, simple_ir_program: IRProgram, mock_midi_port: MagicMock
    ) -> None:
        """Test POLY_PRESSURE event conversion."""
        event = MIDIEvent(time=0, type=EventType.POLY_PRESSURE, channel=1, data1=60, data2=80)
        player = RealtimePlayer(simple_ir_program, "Test Port")

        message = player._event_to_midi_message(event)
        assert message == [0xA0, 60, 80]  # Poly pressure, channel 1, note 60, value 80

    def test_player_event_conversion_marker_skipped(
        self, simple_ir_program: IRProgram, mock_midi_port: MagicMock
    ) -> None:
        """Test MARKER event returns None (not sent to MIDI)."""
        event = MIDIEvent(time=0, type=EventType.MARKER, channel=0, data1=0, data2=0)
        player = RealtimePlayer(simple_ir_program, "Test Port")

        message = player._event_to_midi_message(event)
        assert message is None  # Markers not sent to MIDI output

    def test_player_tempo_change(
        self, tempo_change_ir_program: IRProgram, mock_midi_port: MagicMock
    ) -> None:
        """Test tempo changes are handled correctly."""
        player = RealtimePlayer(tempo_change_ir_program, "Test Port")

        # Should have 3 events (tempo event skipped)
        assert player.scheduler.event_queue.qsize() == 3

        # Duration calculation should account for tempo change
        # First 480 ticks at 120 BPM = 500ms
        # Next 480 ticks at 140 BPM = ~428.57ms
        # Total = ~928.57ms
        assert player.get_duration_ms() == pytest.approx(928.57, rel=0.01)

    def test_player_is_complete(
        self, simple_ir_program: IRProgram, mock_midi_port: MagicMock
    ) -> None:
        """Test is_complete checks scheduler state."""
        player = RealtimePlayer(simple_ir_program, "Test Port")

        # Initially stopped
        assert player.is_complete()

        player.play()
        # Should be playing (not complete)
        # Note: Might complete immediately if events are very fast
        time.sleep(0.05)

        player.stop()
        # Should be complete after stop
        assert player.is_complete()

    def test_player_empty_program(self, mock_midi_port: MagicMock) -> None:
        """Test player with empty event list."""
        empty_program = IRProgram(
            resolution=480, initial_tempo=120, events=[], metadata={"title": "Empty"}
        )

        player = RealtimePlayer(empty_program, "Test Port")

        assert player.get_duration_ms() == 0.0
        assert player.scheduler.event_queue.qsize() == 0
