"""Unit tests for tempo tracking."""

from __future__ import annotations

import pytest

from midi_markdown.runtime.tempo_tracker import TempoSegment, TempoTracker


@pytest.mark.unit
class TestTempoSegment:
    """Tests for TempoSegment dataclass."""

    def test_tempo_segment_creation(self):
        """Test TempoSegment dataclass initialization."""
        segment = TempoSegment(start_tick=0, tempo=120.0, cumulative_ms=0.0)

        assert segment.start_tick == 0
        assert segment.tempo == 120.0
        assert segment.cumulative_ms == 0.0

    def test_tempo_segment_with_values(self):
        """Test TempoSegment with non-zero values."""
        segment = TempoSegment(start_tick=960, tempo=140.0, cumulative_ms=1000.0)

        assert segment.start_tick == 960
        assert segment.tempo == 140.0
        assert segment.cumulative_ms == 1000.0


@pytest.mark.unit
class TestTempoTracker:
    """Tests for TempoTracker class."""

    def test_init(self):
        """Test TempoTracker initialization."""
        tracker = TempoTracker(ppq=480, default_tempo=120.0)

        assert tracker.ppq == 480
        assert tracker.default_tempo == 120.0
        assert tracker.segments == []
        assert tracker._built is False

    def test_init_with_different_values(self):
        """Test initialization with different PPQ and tempo."""
        tracker = TempoTracker(ppq=960, default_tempo=90.0)

        assert tracker.ppq == 960
        assert tracker.default_tempo == 90.0

    def test_add_tempo_change(self):
        """Test adding tempo changes."""
        tracker = TempoTracker(ppq=480)

        tracker.add_tempo_change(480, 90.0)
        tracker.add_tempo_change(960, 140.0)

        assert len(tracker.segments) == 2
        assert tracker.segments[0].start_tick == 480
        assert tracker.segments[0].tempo == 90.0
        assert tracker.segments[1].start_tick == 960
        assert tracker.segments[1].tempo == 140.0
        assert tracker._built is False  # Not built yet

    def test_build_tempo_map_no_changes(self):
        """Test building tempo map with no tempo changes."""
        tracker = TempoTracker(ppq=480, default_tempo=120.0)
        tracker.build_tempo_map()

        assert tracker._built is True
        assert len(tracker.segments) == 1
        assert tracker.segments[0].start_tick == 0
        assert tracker.segments[0].tempo == 120.0
        assert tracker.segments[0].cumulative_ms == 0.0

    def test_build_tempo_map_single_change(self):
        """Test building tempo map with one tempo change."""
        tracker = TempoTracker(ppq=480, default_tempo=120.0)
        tracker.add_tempo_change(960, 140.0)
        tracker.build_tempo_map()

        assert tracker._built is True
        assert len(tracker.segments) == 2

        # First segment: tick 0-959 at 120 BPM
        assert tracker.segments[0].start_tick == 0
        assert tracker.segments[0].tempo == 120.0
        assert tracker.segments[0].cumulative_ms == 0.0

        # Second segment: tick 960+ at 140 BPM
        # 960 ticks at 120 BPM = 2 beats = 1000ms
        assert tracker.segments[1].start_tick == 960
        assert tracker.segments[1].tempo == 140.0
        assert tracker.segments[1].cumulative_ms == pytest.approx(1000.0)

    def test_build_tempo_map_multiple_changes(self):
        """Test building tempo map with multiple tempo changes."""
        tracker = TempoTracker(ppq=480, default_tempo=120.0)
        tracker.add_tempo_change(480, 90.0)
        tracker.add_tempo_change(960, 140.0)
        tracker.build_tempo_map()

        assert len(tracker.segments) == 3

        # First segment: 0-479 at 120 BPM, 480 ticks = 500ms
        assert tracker.segments[0].cumulative_ms == 0.0

        # Second segment: 480-959 at 90 BPM, 480 ticks = 666.67ms
        assert tracker.segments[1].cumulative_ms == pytest.approx(500.0)

        # Third segment: 960+ at 140 BPM, cumulative = 500 + 666.67 = 1166.67ms
        assert tracker.segments[2].cumulative_ms == pytest.approx(1166.67, rel=0.01)

    def test_build_tempo_map_out_of_order(self):
        """Test tempo changes are sorted correctly."""
        tracker = TempoTracker(ppq=480, default_tempo=120.0)

        # Add out of order
        tracker.add_tempo_change(960, 140.0)
        tracker.add_tempo_change(480, 90.0)
        tracker.build_tempo_map()

        # Should be sorted by tick
        assert tracker.segments[0].start_tick == 0
        assert tracker.segments[1].start_tick == 480
        assert tracker.segments[2].start_tick == 960

    def test_ticks_to_ms_constant_tempo(self):
        """Test tick-to-ms conversion with constant tempo."""
        tracker = TempoTracker(ppq=480, default_tempo=120.0)
        tracker.build_tempo_map()

        # At 120 BPM, 480 ticks = 1 beat = 500ms
        assert tracker.ticks_to_ms(0) == 0.0
        assert tracker.ticks_to_ms(480) == pytest.approx(500.0)
        assert tracker.ticks_to_ms(960) == pytest.approx(1000.0)
        assert tracker.ticks_to_ms(1920) == pytest.approx(2000.0)

    def test_ticks_to_ms_single_tempo_change(self):
        """Test conversion with one tempo change."""
        tracker = TempoTracker(ppq=480, default_tempo=120.0)
        tracker.add_tempo_change(960, 140.0)
        tracker.build_tempo_map()

        # First 960 ticks at 120 BPM = 1000ms
        assert tracker.ticks_to_ms(960) == pytest.approx(1000.0)

        # Next 480 ticks at 140 BPM = ~428.57ms
        # Formula: (480 / 480) * (60000 / 140) = 428.57
        assert tracker.ticks_to_ms(1440) == pytest.approx(1428.57, rel=0.01)

    def test_ticks_to_ms_multiple_tempo_changes(self):
        """Test conversion with multiple tempo changes."""
        tracker = TempoTracker(ppq=480, default_tempo=120.0)
        tracker.add_tempo_change(480, 90.0)
        tracker.add_tempo_change(960, 140.0)
        tracker.build_tempo_map()

        # First 480 ticks at 120 BPM = 500ms
        assert tracker.ticks_to_ms(480) == pytest.approx(500.0)

        # Next 480 ticks at 90 BPM = 666.67ms, total = 1166.67ms
        assert tracker.ticks_to_ms(960) == pytest.approx(1166.67, rel=0.01)

        # Next 480 ticks at 140 BPM = ~428.57ms, total = 1595.24ms
        assert tracker.ticks_to_ms(1440) == pytest.approx(1595.24, rel=0.01)

    def test_ticks_to_ms_not_built_error(self):
        """Test error when tempo map not built."""
        tracker = TempoTracker(ppq=480, default_tempo=120.0)

        with pytest.raises(RuntimeError, match="Tempo map not built"):
            tracker.ticks_to_ms(100)

    def test_ms_to_ticks_constant_tempo(self):
        """Test reverse conversion (ms to ticks)."""
        tracker = TempoTracker(ppq=480, default_tempo=120.0)
        tracker.build_tempo_map()

        assert tracker.ms_to_ticks(0.0) == 0
        assert tracker.ms_to_ticks(500.0) == 480
        assert tracker.ms_to_ticks(1000.0) == 960
        assert tracker.ms_to_ticks(2000.0) == 1920

    def test_ms_to_ticks_with_tempo_change(self):
        """Test reverse conversion with tempo change."""
        tracker = TempoTracker(ppq=480, default_tempo=120.0)
        tracker.add_tempo_change(960, 140.0)
        tracker.build_tempo_map()

        # 1000ms should be at tick 960 (boundary)
        assert tracker.ms_to_ticks(1000.0) == 960

        # 1428.57ms should be close to tick 1440 (allow ±1 for rounding)
        result = tracker.ms_to_ticks(1428.57)
        assert 1439 <= result <= 1441

    def test_ms_to_ticks_not_built_error(self):
        """Test error when tempo map not built."""
        tracker = TempoTracker(ppq=480, default_tempo=120.0)

        with pytest.raises(RuntimeError, match="Tempo map not built"):
            tracker.ms_to_ticks(100.0)

    def test_round_trip_conversion(self):
        """Test converting ticks→ms→ticks returns original value."""
        tracker = TempoTracker(ppq=480, default_tempo=120.0)
        tracker.add_tempo_change(960, 140.0)
        tracker.build_tempo_map()

        # Test several tick values (allow ±1 tick for rounding)
        for ticks in [0, 480, 960, 1440, 1920]:
            ms = tracker.ticks_to_ms(ticks)
            result_ticks = tracker.ms_to_ticks(ms)
            assert result_ticks == ticks or abs(result_ticks - ticks) <= 1

    def test_different_ppq(self):
        """Test with different PPQ value."""
        tracker = TempoTracker(ppq=960, default_tempo=120.0)
        tracker.build_tempo_map()

        # At 120 BPM with ppq=960, 960 ticks = 1 beat = 500ms
        assert tracker.ticks_to_ms(960) == pytest.approx(500.0)
        assert tracker.ticks_to_ms(1920) == pytest.approx(1000.0)

    def test_different_default_tempo(self):
        """Test with different default tempo."""
        tracker = TempoTracker(ppq=480, default_tempo=90.0)
        tracker.build_tempo_map()

        # At 90 BPM, 480 ticks = 1 beat = 666.67ms
        # Formula: (480 / 480) * (60000 / 90) = 666.67
        assert tracker.ticks_to_ms(480) == pytest.approx(666.67, rel=0.01)

    def test_tempo_at_tick_zero(self):
        """Test adding tempo change at tick 0."""
        tracker = TempoTracker(ppq=480, default_tempo=120.0)
        tracker.add_tempo_change(0, 140.0)  # Override default at tick 0
        tracker.build_tempo_map()

        # Should use 140 BPM from start
        # 480 ticks at 140 BPM = ~428.57ms
        assert tracker.ticks_to_ms(480) == pytest.approx(428.57, rel=0.01)

    def test_very_small_values(self):
        """Test with very small tick values."""
        tracker = TempoTracker(ppq=480, default_tempo=120.0)
        tracker.build_tempo_map()

        # 1 tick at 120 BPM ≈ 1.04ms
        assert tracker.ticks_to_ms(1) == pytest.approx(1.04, rel=0.01)

    def test_very_large_values(self):
        """Test with large tick values."""
        tracker = TempoTracker(ppq=480, default_tempo=120.0)
        tracker.build_tempo_map()

        # 48000 ticks = 100 beats = 50 seconds = 50000ms
        assert tracker.ticks_to_ms(48000) == pytest.approx(50000.0)

    def test_fractional_ms(self):
        """Test ms_to_ticks with fractional milliseconds."""
        tracker = TempoTracker(ppq=480, default_tempo=120.0)
        tracker.build_tempo_map()

        # 250.5ms should convert to approximately 240 ticks
        result = tracker.ms_to_ticks(250.5)
        assert 239 <= result <= 241  # Allow small rounding error

    def test_rebuild_tempo_map(self):
        """Test rebuilding tempo map after adding more changes."""
        tracker = TempoTracker(ppq=480, default_tempo=120.0)
        tracker.add_tempo_change(960, 140.0)
        tracker.build_tempo_map()

        # Get initial conversion
        ms1 = tracker.ticks_to_ms(1440)

        # Add another tempo change and rebuild
        tracker.add_tempo_change(1200, 100.0)
        tracker.build_tempo_map()

        # Result should be different now
        ms2 = tracker.ticks_to_ms(1440)
        assert ms1 != ms2
