"""Unit tests for TUIState thread-safe state management."""

from __future__ import annotations

import threading
import time

import pytest

from midi_markdown.runtime.tui.state import EventInfo, TUIState


@pytest.mark.unit
class TestTUIState:
    """Tests for TUIState thread-safe operations."""

    def test_initialization(self) -> None:
        """Test TUIState initializes with correct defaults."""
        state = TUIState(total_duration_ms=60000.0, initial_tempo=120.0, max_events=20)

        snapshot = state.get_state_snapshot()
        assert snapshot["position_ms"] == 0.0
        assert snapshot["position_ticks"] == 0
        assert snapshot["tempo"] == 120.0
        assert snapshot["state"] == "stopped"
        assert snapshot["total_duration_ms"] == 60000.0
        assert snapshot["event_history"] == []

    def test_update_position(self) -> None:
        """Test position updates are reflected in snapshot."""
        state = TUIState(total_duration_ms=60000.0, initial_tempo=120.0)

        state.update_position(1000.0, 480)
        snapshot = state.get_state_snapshot()

        assert snapshot["position_ms"] == 1000.0
        assert snapshot["position_ticks"] == 480

    def test_update_tempo(self) -> None:
        """Test tempo updates are reflected in snapshot."""
        state = TUIState(total_duration_ms=60000.0, initial_tempo=120.0)

        state.update_tempo(140.0)
        snapshot = state.get_state_snapshot()

        assert snapshot["tempo"] == 140.0

    def test_set_state(self) -> None:
        """Test playback state changes."""
        state = TUIState(total_duration_ms=60000.0, initial_tempo=120.0)

        # Test playing state
        state.set_state("playing")
        assert state.get_state_snapshot()["state"] == "playing"

        # Test paused state
        state.set_state("paused")
        assert state.get_state_snapshot()["state"] == "paused"

        # Test stopped state
        state.set_state("stopped")
        assert state.get_state_snapshot()["state"] == "stopped"

    def test_add_event(self) -> None:
        """Test adding events to history."""
        state = TUIState(total_duration_ms=60000.0, initial_tempo=120.0, max_events=5)

        event1 = EventInfo(time_ms=0.0, type="NOTE_ON", channel=1, data="C4, Vel: 80")
        event2 = EventInfo(time_ms=500.0, type="NOTE_OFF", channel=1, data="C4, Vel: 0")

        state.add_event(event1)
        state.add_event(event2)

        snapshot = state.get_state_snapshot()
        events = snapshot["event_history"]

        assert len(events) == 2
        assert events[0] == event1
        assert events[1] == event2

    def test_event_history_max_size(self) -> None:
        """Test event history respects max_events circular buffer."""
        state = TUIState(total_duration_ms=60000.0, initial_tempo=120.0, max_events=3)

        # Add 5 events (more than max_events=3)
        for i in range(5):
            event = EventInfo(time_ms=i * 100.0, type="NOTE_ON", channel=1, data=f"Event {i}")
            state.add_event(event)

        snapshot = state.get_state_snapshot()
        events = snapshot["event_history"]

        # Should only have last 3 events (events 2, 3, 4)
        assert len(events) == 3
        assert events[0].data == "Event 2"
        assert events[1].data == "Event 3"
        assert events[2].data == "Event 4"

    def test_clear_events(self) -> None:
        """Test clearing event history."""
        state = TUIState(total_duration_ms=60000.0, initial_tempo=120.0)

        # Add some events
        event = EventInfo(time_ms=0.0, type="NOTE_ON", channel=1, data="C4, Vel: 80")
        state.add_event(event)
        assert len(state.get_state_snapshot()["event_history"]) == 1

        # Clear events
        state.clear_events()
        assert len(state.get_state_snapshot()["event_history"]) == 0

    def test_reset(self) -> None:
        """Test reset returns state to initial values."""
        state = TUIState(total_duration_ms=60000.0, initial_tempo=120.0)

        # Modify state
        state.update_position(5000.0, 2400)
        state.update_tempo(140.0)
        state.set_state("playing")
        state.add_event(EventInfo(time_ms=0.0, type="NOTE_ON", channel=1, data="C4"))

        # Reset
        state.reset()

        snapshot = state.get_state_snapshot()
        assert snapshot["position_ms"] == 0.0
        assert snapshot["position_ticks"] == 0
        assert snapshot["state"] == "stopped"
        assert snapshot["event_history"] == []
        # Note: tempo is not reset, only position and state

    def test_thread_safety_concurrent_updates(self) -> None:
        """Test thread safety with concurrent position updates."""
        state = TUIState(total_duration_ms=60000.0, initial_tempo=120.0)
        update_count = 100
        errors = []

        def updater() -> None:
            """Update position in a loop."""
            try:
                for i in range(update_count):
                    state.update_position(float(i), i)
                    time.sleep(0.0001)  # Small delay
            except Exception as e:
                errors.append(e)

        # Start multiple threads updating position
        threads = [threading.Thread(target=updater) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should complete without errors
        assert len(errors) == 0

        # Final snapshot should be atomic and consistent
        snapshot = state.get_state_snapshot()
        assert isinstance(snapshot["position_ms"], float)
        assert isinstance(snapshot["position_ticks"], int)

    def test_thread_safety_concurrent_snapshot_reads(self) -> None:
        """Test thread safety with concurrent snapshot reads."""
        state = TUIState(total_duration_ms=60000.0, initial_tempo=120.0)
        read_count = 50
        errors = []
        snapshots = []

        def reader() -> None:
            """Read snapshots in a loop."""
            try:
                for _ in range(read_count):
                    snapshot = state.get_state_snapshot()
                    snapshots.append(snapshot)
                    time.sleep(0.0001)
            except Exception as e:
                errors.append(e)

        def updater() -> None:
            """Update position while readers are active."""
            try:
                for i in range(read_count):
                    state.update_position(float(i * 10), i * 10)
                    time.sleep(0.0001)
            except Exception as e:
                errors.append(e)

        # Start readers and updater concurrently
        threads = [threading.Thread(target=reader) for _ in range(3)]
        threads.append(threading.Thread(target=updater))

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should complete without errors
        assert len(errors) == 0

        # All snapshots should be valid dicts
        assert len(snapshots) > 0
        for snapshot in snapshots:
            assert isinstance(snapshot, dict)
            assert "position_ms" in snapshot
            assert "position_ticks" in snapshot
            assert "tempo" in snapshot
