"""Unit tests for event scheduler."""

from __future__ import annotations

import time
from unittest.mock import MagicMock

import pytest

from midi_markdown.runtime.scheduler import EventScheduler, ScheduledEvent


@pytest.fixture
def mock_midi_output():
    """Mock MIDI output."""
    mock = MagicMock()
    mock.send_message = MagicMock()
    return mock


@pytest.mark.unit
class TestScheduledEvent:
    """Tests for ScheduledEvent dataclass."""

    def test_scheduled_event_creation(self):
        """Test ScheduledEvent dataclass initialization."""
        event = ScheduledEvent(100.0, [0x90, 60, 80], {"note": "C4"})

        assert event.time_ms == 100.0
        assert event.midi_message == [0x90, 60, 80]
        assert event.metadata == {"note": "C4"}

    def test_scheduled_event_ordering(self):
        """Test ScheduledEvent comparison for PriorityQueue."""
        event1 = ScheduledEvent(100.0, [0x90, 60, 80], {})
        event2 = ScheduledEvent(200.0, [0x80, 60, 0], {})
        event3 = ScheduledEvent(50.0, [0xB0, 7, 127], {})

        # Test __lt__ for priority queue ordering
        assert event3 < event1  # 50ms < 100ms
        assert event1 < event2  # 100ms < 200ms
        assert not event2 < event1  # 200ms not < 100ms

    def test_scheduled_event_equality_time(self):
        """Test events with same time."""
        event1 = ScheduledEvent(100.0, [0x90, 60, 80], {})
        event2 = ScheduledEvent(100.0, [0xB0, 7, 127], {})

        # Neither should be less than the other
        assert not event1 < event2
        assert not event2 < event1


@pytest.mark.unit
class TestEventScheduler:
    """Tests for EventScheduler class."""

    def test_init(self, mock_midi_output):
        """Test EventScheduler initialization."""
        scheduler = EventScheduler(mock_midi_output)

        assert scheduler.midi_output == mock_midi_output
        assert scheduler.state == "stopped"
        assert scheduler.event_queue.qsize() == 0
        assert scheduler.scheduler_thread is None
        assert scheduler.start_time is None
        assert scheduler.pause_time is None
        assert scheduler.time_offset == 0.0
        assert scheduler.on_event_sent is None
        assert scheduler.on_complete is None

    def test_load_events(self, mock_midi_output):
        """Test loading events into scheduler."""
        scheduler = EventScheduler(mock_midi_output)

        events = [
            ScheduledEvent(0.0, [0x90, 60, 80], {}),
            ScheduledEvent(100.0, [0x80, 60, 0], {}),
            ScheduledEvent(50.0, [0xB0, 7, 127], {}),
        ]

        scheduler.load_events(events)
        assert scheduler.event_queue.qsize() == 3

    def test_load_events_clears_existing(self, mock_midi_output):
        """Test load_events clears existing queue."""
        scheduler = EventScheduler(mock_midi_output)

        # Load first set
        events1 = [
            ScheduledEvent(0.0, [0x90, 60, 80], {}),
            ScheduledEvent(100.0, [0x80, 60, 0], {}),
        ]
        scheduler.load_events(events1)
        assert scheduler.event_queue.qsize() == 2

        # Load second set (should clear first)
        events2 = [ScheduledEvent(50.0, [0xB0, 7, 127], {})]
        scheduler.load_events(events2)
        assert scheduler.event_queue.qsize() == 1

    def test_start_stop(self, mock_midi_output):
        """Test starting and stopping scheduler."""
        scheduler = EventScheduler(mock_midi_output)

        # Use events with delays so scheduler doesn't complete immediately
        events = [
            ScheduledEvent(0.0, [0x90, 60, 80], {}),
            ScheduledEvent(500.0, [0x80, 60, 0], {}),  # 500ms delay
        ]
        scheduler.load_events(events)

        scheduler.start()
        assert scheduler.state == "playing"
        assert scheduler.start_time is not None
        assert scheduler.scheduler_thread is not None

        time.sleep(0.05)  # Let thread start

        scheduler.stop()
        assert scheduler.state == "stopped"
        assert scheduler.start_time is None
        time.sleep(0.1)  # Let thread finish
        if scheduler.scheduler_thread:
            assert not scheduler.scheduler_thread.is_alive()

    def test_start_already_playing(self, mock_midi_output):
        """Test starting when already playing is no-op."""
        scheduler = EventScheduler(mock_midi_output)

        # Use events with delays so state stays "playing"
        events = [ScheduledEvent(500.0, [0x90, 60, 80], {})]
        scheduler.load_events(events)

        scheduler.start()
        first_state = scheduler.state

        time.sleep(0.05)

        # Try to start again - should be no-op
        scheduler.start()
        # State should still be "playing" (not restarted)
        assert scheduler.state == first_state

        scheduler.stop()

    def test_pause_resume(self, mock_midi_output):
        """Test pausing and resuming scheduler."""
        scheduler = EventScheduler(mock_midi_output)

        # Use events with delays so state stays "playing"
        events = [ScheduledEvent(500.0, [0x90, 60, 80], {})]
        scheduler.load_events(events)

        scheduler.start()
        assert scheduler.state == "playing"

        time.sleep(0.05)

        scheduler.pause()
        assert scheduler.state == "paused"
        assert scheduler.pause_time is not None

        time.sleep(0.1)  # Paused for 100ms

        scheduler.resume()
        assert scheduler.state == "playing"
        # Time offset should account for pause duration
        assert scheduler.time_offset > 0

        scheduler.stop()

    def test_pause_when_not_playing(self, mock_midi_output):
        """Test pause when not playing is no-op."""
        scheduler = EventScheduler(mock_midi_output)

        scheduler.pause()
        assert scheduler.state == "stopped"
        assert scheduler.pause_time is None

    def test_resume_when_not_paused(self, mock_midi_output):
        """Test resume when not paused is no-op."""
        scheduler = EventScheduler(mock_midi_output)

        initial_offset = scheduler.time_offset
        scheduler.resume()
        assert scheduler.time_offset == initial_offset

    def test_event_playback(self, mock_midi_output):
        """Test events are sent to MIDI output."""
        scheduler = EventScheduler(mock_midi_output)

        events = [
            ScheduledEvent(0.0, [0x90, 60, 80], {}),
            ScheduledEvent(50.0, [0x80, 60, 0], {}),
        ]

        scheduler.load_events(events)
        scheduler.start()

        time.sleep(0.2)  # Let scheduler run
        scheduler.stop()

        # Verify MIDI messages were sent
        assert mock_midi_output.send_message.call_count >= 2

    def test_on_event_sent_callback(self, mock_midi_output):
        """Test on_event_sent callback fires."""
        scheduler = EventScheduler(mock_midi_output)

        events_sent = []
        scheduler.on_event_sent = lambda metadata: events_sent.append(metadata)

        events = [
            ScheduledEvent(0.0, [0x90, 60, 80], {"note": "C4"}),
            ScheduledEvent(50.0, [0x80, 60, 0], {"note": "C4 off"}),
        ]

        scheduler.load_events(events)
        scheduler.start()

        time.sleep(0.2)
        scheduler.stop()

        assert len(events_sent) >= 2
        assert events_sent[0]["note"] == "C4"

    def test_on_complete_callback(self, mock_midi_output):
        """Test on_complete callback fires when queue empty."""
        scheduler = EventScheduler(mock_midi_output)

        complete_called = []
        scheduler.on_complete = lambda: complete_called.append(True)

        events = [ScheduledEvent(0.0, [0x90, 60, 80], {})]

        scheduler.load_events(events)
        scheduler.start()

        time.sleep(0.15)  # Wait for completion

        assert len(complete_called) == 1
        assert scheduler.state == "stopped"

    def test_stop_during_playback(self, mock_midi_output):
        """Test stop during active playback."""
        scheduler = EventScheduler(mock_midi_output)

        # Create events with delays
        events = [
            ScheduledEvent(0.0, [0x90, 60, 80], {}),
            ScheduledEvent(500.0, [0x80, 60, 0], {}),  # 500ms delay
        ]

        scheduler.load_events(events)
        scheduler.start()

        time.sleep(0.1)  # Stop before second event

        scheduler.stop()
        assert scheduler.state == "stopped"

        # Verify thread terminated
        time.sleep(0.1)
        assert not scheduler.scheduler_thread.is_alive()

    def test_multiple_events_sequential(self, mock_midi_output):
        """Test multiple events processed in order."""
        scheduler = EventScheduler(mock_midi_output)

        events = [
            ScheduledEvent(0.0, [0x90, 60, 80], {"order": 1}),
            ScheduledEvent(30.0, [0x90, 62, 80], {"order": 2}),
            ScheduledEvent(60.0, [0x90, 64, 80], {"order": 3}),
        ]

        events_sent = []
        scheduler.on_event_sent = lambda metadata: events_sent.append(metadata)

        scheduler.load_events(events)
        scheduler.start()

        time.sleep(0.2)
        scheduler.stop()

        # Verify events sent in correct order
        assert len(events_sent) >= 3
        for i, event_meta in enumerate(events_sent[:3]):
            assert event_meta["order"] == i + 1

    def test_busy_wait_threshold(self, mock_midi_output):
        """Test BUSY_WAIT_THRESHOLD_MS constant."""
        scheduler = EventScheduler(mock_midi_output)

        assert scheduler.BUSY_WAIT_THRESHOLD_MS == 10.0

    def test_stop_flag_interrupts_wait(self, mock_midi_output):
        """Test stop flag interrupts busy-wait loop."""
        scheduler = EventScheduler(mock_midi_output)

        # Event with long delay
        events = [ScheduledEvent(1000.0, [0x90, 60, 80], {})]

        scheduler.load_events(events)
        scheduler.start()

        time.sleep(0.05)  # Let scheduler start waiting

        # Stop should interrupt the wait
        stop_time = time.perf_counter()
        scheduler.stop()
        elapsed = time.perf_counter() - stop_time

        # Stop should be nearly instant (< 100ms), not wait for full 1000ms
        assert elapsed < 0.2

    def test_pause_during_event_wait(self, mock_midi_output):
        """Test pause while waiting for event."""
        scheduler = EventScheduler(mock_midi_output)

        # Use longer event time to ensure we have time to pause before it's sent
        events = [ScheduledEvent(1000.0, [0x90, 60, 80], {})]  # 1 second instead of 200ms

        scheduler.load_events(events)
        scheduler.start()

        time.sleep(0.1)  # Let scheduler start

        scheduler.pause()
        assert scheduler.state == "paused"

        time.sleep(0.2)  # Paused time

        scheduler.resume()
        assert scheduler.state == "playing"

        # Wait for event to be sent (should be ~900ms after resume: 1000ms - 100ms elapsed)
        # Add extra margin for CI
        time.sleep(1.2)
        scheduler.stop()

        # Event should still have been sent
        assert mock_midi_output.send_message.call_count >= 1

    def test_empty_queue_completes_immediately(self, mock_midi_output):
        """Test empty event queue completes immediately."""
        scheduler = EventScheduler(mock_midi_output)

        complete_called = []
        scheduler.on_complete = lambda: complete_called.append(True)

        scheduler.load_events([])  # Empty queue
        scheduler.start()

        time.sleep(0.1)

        assert len(complete_called) == 1
        assert scheduler.state == "stopped"
