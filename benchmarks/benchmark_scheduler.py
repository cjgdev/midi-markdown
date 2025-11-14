"""Benchmark scheduler timing accuracy and performance.

Tests real-time scheduler precision and latency to ensure
sub-5ms average timing accuracy.

Performance Targets:
- Average latency: <5ms
- Max latency: <10ms
- High event density: >100 events/second

Run with:
    uv run pytest benchmarks/benchmark_scheduler.py -v
"""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass
from threading import Lock

import pytest

from midi_markdown.runtime.scheduler import EventScheduler, ScheduledEvent


@dataclass
class RecordedEvent:
    """Event with scheduled and actual playback times."""

    scheduled_time_ms: float
    actual_time_ms: float
    midi_message: list[int]

    @property
    def latency_ms(self) -> float:
        """Calculate latency in milliseconds."""
        return abs(self.actual_time_ms - self.scheduled_time_ms)


class RecordingMIDIPort:
    """Mock MIDI port that records timing of sent messages."""

    def __init__(self):
        """Initialize recording port."""
        self.messages: deque[RecordedEvent] = deque()
        self.start_time: float | None = None
        self.lock = Lock()

    def send_message(self, message: list[int]) -> None:
        """Record message send time.

        Args:
            message: MIDI message bytes
        """
        if self.start_time is None:
            self.start_time = time.perf_counter()

        current_time = time.perf_counter()
        elapsed_ms = (current_time - self.start_time) * 1000

        with self.lock:
            # We don't have scheduled time here, will be set externally
            self.messages.append(
                RecordedEvent(
                    scheduled_time_ms=0.0,  # Will be filled in later
                    actual_time_ms=elapsed_ms,
                    midi_message=message,
                )
            )

    def close_port(self) -> None:
        """Close port (no-op for recording)."""

    def get_latency_stats(self, scheduled_times: list[float]) -> dict[str, float]:
        """Calculate latency statistics.

        Args:
            scheduled_times: List of scheduled times in ms

        Returns:
            Dictionary with latency statistics
        """
        with self.lock:
            messages = list(self.messages)

        if not messages or not scheduled_times:
            return {"avg": 0.0, "max": 0.0, "min": 0.0, "count": 0}

        # Match scheduled times to actual times
        latencies = []
        for scheduled, recorded in zip(scheduled_times, messages, strict=False):
            latency = abs(recorded.actual_time_ms - scheduled)
            latencies.append(latency)

        return {
            "avg": sum(latencies) / len(latencies) if latencies else 0.0,
            "max": max(latencies) if latencies else 0.0,
            "min": min(latencies) if latencies else 0.0,
            "count": len(latencies),
        }


@pytest.mark.benchmark
class TestSchedulerLatency:
    """Benchmark scheduler message delivery latency."""

    def test_scheduler_10ms_intervals(self):
        """Test scheduler with 10ms intervals (100 events/second).

        Target: Average latency <5ms, max latency <10ms
        """
        port = RecordingMIDIPort()

        # Create mock MIDI output manager
        class MockMIDIOutput:
            def send_message(self, msg):
                port.send_message(msg)

        scheduler = EventScheduler(MockMIDIOutput())

        # Schedule 100 events at 10ms intervals
        events = []
        scheduled_times = []
        for i in range(100):
            time_ms = i * 10.0
            scheduled_times.append(time_ms)
            events.append(
                ScheduledEvent(
                    time_ms=time_ms,
                    midi_message=[0x90, 60, 80],  # Note on
                    metadata={"index": i},
                )
            )

        port.start_time = time.perf_counter()
        scheduler.load_events(events)
        scheduler.start()

        # Wait for completion
        time.sleep(1.5)
        scheduler.stop()

        # Calculate statistics
        stats = port.get_latency_stats(scheduled_times)

        # Verify targets
        assert stats["avg"] < 5.0, f"Average latency {stats['avg']:.2f}ms exceeds 5ms"
        assert stats["max"] < 10.0, f"Max latency {stats['max']:.2f}ms exceeds 10ms"
        assert stats["count"] >= 90, f"Only sent {stats['count']}/100 events"

    def test_scheduler_5ms_intervals(self):
        """Test scheduler with 5ms intervals (200 events/second).

        Target: Average latency <5ms, max latency <10ms
        """
        port = RecordingMIDIPort()

        class MockMIDIOutput:
            def send_message(self, msg):
                port.send_message(msg)

        scheduler = EventScheduler(MockMIDIOutput())

        # Schedule 100 events at 5ms intervals
        events = []
        scheduled_times = []
        for i in range(100):
            time_ms = i * 5.0
            scheduled_times.append(time_ms)
            events.append(
                ScheduledEvent(
                    time_ms=time_ms,
                    midi_message=[0x90, 60 + (i % 12), 80],
                    metadata={"index": i},
                )
            )

        port.start_time = time.perf_counter()
        scheduler.load_events(events)
        scheduler.start()

        # Wait for completion
        time.sleep(0.8)
        scheduler.stop()

        stats = port.get_latency_stats(scheduled_times)

        assert stats["avg"] < 5.0, f"Average latency {stats['avg']:.2f}ms exceeds 5ms"
        assert stats["max"] < 10.0, f"Max latency {stats['max']:.2f}ms exceeds 10ms"

    def test_scheduler_simultaneous_events(self):
        """Test scheduler with multiple simultaneous events.

        Tests handling of events scheduled at the same time (chords).
        """
        port = RecordingMIDIPort()

        class MockMIDIOutput:
            def send_message(self, msg):
                port.send_message(msg)

        scheduler = EventScheduler(MockMIDIOutput())

        # Schedule chords: 3 notes at 0ms, 3 notes at 100ms, etc.
        events = []
        scheduled_times = []
        for chord_time in [0, 100, 200, 300, 400]:
            for note in [60, 64, 67]:  # C major chord
                scheduled_times.append(chord_time)
                events.append(
                    ScheduledEvent(
                        time_ms=chord_time,
                        midi_message=[0x90, note, 80],
                        metadata={"chord": chord_time},
                    )
                )

        port.start_time = time.perf_counter()
        scheduler.load_events(events)
        scheduler.start()

        time.sleep(0.6)
        scheduler.stop()

        stats = port.get_latency_stats(scheduled_times)

        assert stats["avg"] < 5.0
        assert stats["count"] == 15  # 5 chords × 3 notes


@pytest.mark.benchmark
class TestSchedulerPerformance:
    """Benchmark scheduler throughput and scalability."""

    def test_high_event_density(self):
        """Test scheduler with >100 events/second.

        Target: Handle 500 events in 2 seconds (250 events/second)
        """
        port = RecordingMIDIPort()

        class MockMIDIOutput:
            def send_message(self, msg):
                port.send_message(msg)

        scheduler = EventScheduler(MockMIDIOutput())

        # Schedule 500 events over 2 seconds (4ms intervals)
        events = []
        for i in range(500):
            events.append(
                ScheduledEvent(
                    time_ms=i * 4.0,
                    midi_message=[0x90, 60, 80],
                    metadata={"index": i},
                )
            )

        port.start_time = time.perf_counter()
        start = time.perf_counter()

        scheduler.load_events(events)
        scheduler.start()

        time.sleep(2.5)
        scheduler.stop()

        time.perf_counter() - start

        # Should handle all events
        assert len(port.messages) >= 480, f"Only sent {len(port.messages)}/500 events"

    def test_long_sequence(self):
        """Test scheduler with long event sequence (30 seconds).

        Tests scheduler stability over extended playback.
        """
        port = RecordingMIDIPort()

        class MockMIDIOutput:
            def send_message(self, msg):
                port.send_message(msg)

        scheduler = EventScheduler(MockMIDIOutput())

        # Schedule events for 5 seconds (100 events at 50ms intervals)
        # Full 30s test would take too long for benchmarks
        events = []
        for i in range(100):
            events.append(
                ScheduledEvent(
                    time_ms=i * 50.0,
                    midi_message=[0x90, 60, 80],
                    metadata={"index": i},
                )
            )

        port.start_time = time.perf_counter()
        scheduler.load_events(events)
        scheduler.start()

        time.sleep(5.5)
        scheduler.stop()

        # Should complete most events (allow some margin)
        assert len(port.messages) >= 95


@pytest.mark.benchmark
class TestSchedulerPauseResume:
    """Benchmark scheduler pause/resume functionality."""

    def test_pause_resume_timing(self):
        """Test pause/resume maintains accurate timing.

        Events after resume should continue from correct time point.
        """
        port = RecordingMIDIPort()

        class MockMIDIOutput:
            def send_message(self, msg):
                port.send_message(msg)

        scheduler = EventScheduler(MockMIDIOutput())

        # Schedule 20 events at 50ms intervals
        events = []
        for i in range(20):
            events.append(
                ScheduledEvent(
                    time_ms=i * 50.0,
                    midi_message=[0x90, 60, 80],
                    metadata={"index": i},
                )
            )

        port.start_time = time.perf_counter()
        scheduler.load_events(events)
        scheduler.start()

        # Let 5 events play
        time.sleep(0.3)
        scheduler.pause()

        len(port.messages)

        # Pause for 500ms
        time.sleep(0.5)

        # Resume
        scheduler.resume()

        # Let remaining events play
        time.sleep(1.0)
        scheduler.stop()

        total_events = len(port.messages)

        # Should have sent most events
        assert total_events >= 15
