"""Tempo tracking for tick-to-millisecond conversion.

This module provides the TempoTracker class for converting between MIDI tick times
and real-world millisecond times, accounting for tempo changes throughout a sequence.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TempoSegment:
    """Tempo segment with start tick and cumulative time.

    Attributes:
        start_tick: Absolute tick time where this tempo begins
        tempo: Tempo in BPM (beats per minute)
        cumulative_ms: Milliseconds elapsed from start to this segment
    """

    start_tick: int
    tempo: float  # BPM
    cumulative_ms: float  # Milliseconds elapsed at start of this segment


class TempoTracker:
    """Converts tick times to milliseconds using tempo map.

    The TempoTracker maintains a tempo map that allows accurate conversion between
    MIDI tick times and real-world millisecond times, accounting for tempo changes
    throughout a sequence.

    Example:
        >>> tracker = TempoTracker(ppq=480, default_tempo=120.0)
        >>> tracker.add_tempo_change(960, 140.0)  # Change to 140 BPM at tick 960
        >>> tracker.build_tempo_map()
        >>> print(tracker.ticks_to_ms(1440))  # Convert tick 1440 to milliseconds
        1428.57...
    """

    def __init__(self, ppq: int, default_tempo: float = 120.0) -> None:
        """Initialize tempo tracker.

        Args:
            ppq: Pulses per quarter note (ticks per beat)
            default_tempo: Initial tempo in BPM
        """
        self.ppq = ppq
        self.default_tempo = default_tempo
        self.segments: list[TempoSegment] = []
        self._built = False

    def add_tempo_change(self, tick: int, tempo: float) -> None:
        """Register a tempo change at specified tick.

        Tempo changes can be added in any order - they will be sorted when
        build_tempo_map() is called.

        Args:
            tick: Absolute tick time where tempo changes
            tempo: New tempo in BPM

        Example:
            >>> tracker = TempoTracker(ppq=480)
            >>> tracker.add_tempo_change(480, 90.0)
            >>> tracker.add_tempo_change(960, 140.0)
        """
        self.segments.append(TempoSegment(tick, tempo, 0.0))
        self._built = False  # Mark as needing rebuild

    def build_tempo_map(self) -> None:
        """Calculate cumulative milliseconds for each tempo segment.

        This method must be called after all tempo changes are added and before
        ticks_to_ms() or ms_to_ticks() are used. It:
        1. Sorts segments by tick
        2. Ensures a segment exists at tick 0 (uses default_tempo if needed)
        3. Calculates cumulative milliseconds for each segment

        Example:
            >>> tracker = TempoTracker(ppq=480, default_tempo=120.0)
            >>> tracker.add_tempo_change(960, 140.0)
            >>> tracker.build_tempo_map()
        """
        # Sort segments by tick
        self.segments.sort(key=lambda s: s.start_tick)

        # Ensure segment at tick 0 exists
        if not self.segments or self.segments[0].start_tick > 0:
            self.segments.insert(0, TempoSegment(0, self.default_tempo, 0.0))

        # Calculate cumulative milliseconds for each segment
        for i in range(1, len(self.segments)):
            prev = self.segments[i - 1]
            curr = self.segments[i]

            # Calculate duration of previous segment
            tick_delta = curr.start_tick - prev.start_tick
            ms_delta = self._ticks_to_ms_simple(tick_delta, prev.tempo)

            # Set cumulative time for current segment
            curr.cumulative_ms = prev.cumulative_ms + ms_delta

        self._built = True

    def ticks_to_ms(self, ticks: int) -> float:
        """Convert absolute tick time to milliseconds.

        Args:
            ticks: Absolute tick time

        Returns:
            Time in milliseconds

        Raises:
            RuntimeError: If tempo map not built (call build_tempo_map() first)

        Example:
            >>> tracker = TempoTracker(ppq=480, default_tempo=120.0)
            >>> tracker.build_tempo_map()
            >>> tracker.ticks_to_ms(480)  # 1 beat at 120 BPM = 500ms
            500.0
        """
        if not self._built:
            msg = "Tempo map not built - call build_tempo_map() first"
            raise RuntimeError(msg)

        # Find the segment containing this tick
        segment = self._find_segment(ticks)

        # Calculate time within this segment
        tick_offset = ticks - segment.start_tick
        ms_offset = self._ticks_to_ms_simple(tick_offset, segment.tempo)

        return segment.cumulative_ms + ms_offset

    def ms_to_ticks(self, ms: float) -> int:
        """Convert milliseconds to absolute tick time.

        Args:
            ms: Time in milliseconds

        Returns:
            Absolute tick time

        Raises:
            RuntimeError: If tempo map not built (call build_tempo_map() first)

        Example:
            >>> tracker = TempoTracker(ppq=480, default_tempo=120.0)
            >>> tracker.build_tempo_map()
            >>> tracker.ms_to_ticks(500.0)  # 500ms at 120 BPM = 1 beat = 480 ticks
            480
        """
        if not self._built:
            msg = "Tempo map not built - call build_tempo_map() first"
            raise RuntimeError(msg)

        # Find the segment containing this time
        segment = self._find_segment_by_ms(ms)

        # Calculate ticks within this segment
        ms_offset = ms - segment.cumulative_ms
        tick_offset = self._ms_to_ticks_simple(ms_offset, segment.tempo)

        return segment.start_tick + tick_offset

    def _find_segment(self, ticks: int) -> TempoSegment:
        """Find the tempo segment containing the given tick.

        Uses reverse iteration (most recent tempo is often needed).

        Args:
            ticks: Absolute tick time

        Returns:
            TempoSegment containing this tick
        """
        # Binary search for correct segment (reverse iteration)
        for i in range(len(self.segments) - 1, -1, -1):
            if ticks >= self.segments[i].start_tick:
                return self.segments[i]
        return self.segments[0]  # Shouldn't happen if built correctly

    def _find_segment_by_ms(self, ms: float) -> TempoSegment:
        """Find the tempo segment containing the given time.

        Uses reverse iteration (most recent tempo is often needed).

        Args:
            ms: Time in milliseconds

        Returns:
            TempoSegment containing this time
        """
        for i in range(len(self.segments) - 1, -1, -1):
            if ms >= self.segments[i].cumulative_ms:
                return self.segments[i]
        return self.segments[0]

    def _ticks_to_ms_simple(self, ticks: int, tempo: float) -> float:
        """Convert tick duration to milliseconds at constant tempo.

        Formula: ms = (ticks / ppq) * (60000 / tempo)

        Args:
            ticks: Tick duration (not absolute time)
            tempo: Tempo in BPM

        Returns:
            Duration in milliseconds

        Example:
            At 120 BPM with ppq=480:
            - 480 ticks = 1 beat = 500ms
            - Formula: (480 / 480) * (60000 / 120) = 1 * 500 = 500ms
        """
        return (ticks / self.ppq) * (60000.0 / tempo)

    def _ms_to_ticks_simple(self, ms: float, tempo: float) -> int:
        """Convert millisecond duration to ticks at constant tempo.

        Formula: ticks = (ms * tempo * ppq) / 60000

        Args:
            ms: Duration in milliseconds
            tempo: Tempo in BPM

        Returns:
            Tick duration (not absolute time)

        Example:
            At 120 BPM with ppq=480:
            - 500ms = 1 beat = 480 ticks
            - Formula: (500 * 120 * 480) / 60000 = 480
        """
        return int((ms * tempo * self.ppq) / 60000.0)
