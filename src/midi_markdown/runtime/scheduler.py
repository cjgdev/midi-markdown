"""Event scheduler for precise real-time MIDI playback.

This module provides the EventScheduler class for scheduling and playing MIDI events
with sub-5ms timing precision using a hybrid sleep/busy-wait strategy.
"""

from __future__ import annotations

import queue
import threading
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from midi_markdown.runtime.midi_io import MIDIOutputManager


@dataclass
class ScheduledEvent:
    """Event with absolute playback time in milliseconds.

    Attributes:
        time_ms: Absolute playback time in milliseconds from start
        midi_message: MIDI message as list of bytes [status, data1, data2]
        metadata: Additional event metadata (for callbacks/UI)
    """

    time_ms: float
    midi_message: list[int]
    metadata: dict

    def __lt__(self, other: ScheduledEvent) -> bool:
        """Compare by time for priority queue ordering.

        Args:
            other: Another ScheduledEvent to compare with

        Returns:
            True if this event should be scheduled before the other
        """
        return self.time_ms < other.time_ms


class EventScheduler:
    """Schedules and plays MIDI events with precise timing.

    The EventScheduler uses a hybrid sleep/busy-wait strategy to achieve sub-5ms
    timing precision:
    - For delays > 10ms: Use time.sleep() (OS scheduler)
    - For delays < 10ms: Use busy-wait loop (tight loop)

    Example:
        >>> from midi_markdown.runtime.midi_io import MIDIOutputManager
        >>> midi = MIDIOutputManager()
        >>> midi.open_port(0)
        >>> scheduler = EventScheduler(midi)
        >>> events = [
        ...     ScheduledEvent(0.0, [0x90, 60, 80], {}),
        ...     ScheduledEvent(1000.0, [0x80, 60, 0], {}),
        ... ]
        >>> scheduler.load_events(events)
        >>> scheduler.start()
        >>> # ... wait for completion ...
        >>> scheduler.stop()
        >>> midi.close_port()
    """

    BUSY_WAIT_THRESHOLD_MS = 10.0  # Switch to busy-wait below this threshold

    def __init__(self, midi_output: MIDIOutputManager) -> None:
        """Initialize event scheduler.

        Args:
            midi_output: MIDIOutputManager instance for sending MIDI messages
        """
        self.midi_output = midi_output
        self.event_queue: queue.PriorityQueue[ScheduledEvent] = queue.PriorityQueue()
        self.state = "stopped"  # stopped, playing, paused
        self.scheduler_thread: threading.Thread | None = None
        self.start_time: float | None = None
        self.pause_time: float | None = None
        self.time_offset: float = 0.0
        self.on_event_sent: Callable[[dict], None] | None = None
        self.on_complete: Callable[[], None] | None = None
        self._stop_flag = threading.Event()

    def load_events(self, events: list[ScheduledEvent]) -> None:
        """Load events into scheduler queue.

        Clears any existing events and loads the new event list into the
        internal PriorityQueue.

        Args:
            events: List of ScheduledEvent objects (will be sorted by time_ms)

        Example:
            >>> scheduler.load_events([
            ...     ScheduledEvent(0.0, [0x90, 60, 80], {}),
            ...     ScheduledEvent(500.0, [0x80, 60, 0], {}),
            ... ])
        """
        # Clear existing queue
        self.event_queue = queue.PriorityQueue()

        # Add all events to queue (PriorityQueue sorts by __lt__)
        for event in events:
            self.event_queue.put(event)

    def start(self) -> None:
        """Start playback in separate thread.

        Creates and starts a daemon thread that processes events from the queue.
        If already playing, this is a no-op.

        Example:
            >>> scheduler.load_events(events)
            >>> scheduler.start()
            >>> # Playback begins immediately in background thread
        """
        if self.state == "playing":
            return  # Already playing

        self.state = "playing"
        self.start_time = time.perf_counter()
        self._stop_flag.clear()

        # Start scheduler thread
        self.scheduler_thread = threading.Thread(
            target=self._scheduler_loop,
            daemon=True,
        )
        self.scheduler_thread.start()

    def pause(self) -> None:
        """Pause playback (preserves position).

        Records the current time so that resume() can adjust the time offset
        to account for the pause duration.

        Example:
            >>> scheduler.start()
            >>> # ... playback running ...
            >>> scheduler.pause()
            >>> # Playback paused, position preserved
        """
        if self.state != "playing":
            return

        self.state = "paused"
        self.pause_time = time.perf_counter()

    def resume(self) -> None:
        """Resume from paused position.

        Calculates the duration of the pause and adjusts the time offset so that
        playback continues from where it left off.

        Example:
            >>> scheduler.pause()
            >>> time.sleep(2.0)  # Paused for 2 seconds
            >>> scheduler.resume()
            >>> # Playback resumes, no timing drift
        """
        if self.state != "paused":
            return

        # Calculate time spent paused and adjust offset
        if self.pause_time is not None:
            paused_duration = time.perf_counter() - self.pause_time
            self.time_offset += paused_duration
        self.state = "playing"

    def stop(self) -> None:
        """Stop playback and reset position.

        Sets the stop flag and waits for the scheduler thread to finish
        (with 1-second timeout). Resets all timing state.

        Example:
            >>> scheduler.start()
            >>> # ... playback running ...
            >>> scheduler.stop()
            >>> # Playback stopped, thread cleaned up
        """
        self.state = "stopped"
        self._stop_flag.set()

        # Wait for scheduler thread to finish
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=1.0)

        self.start_time = None
        self.pause_time = None
        self.time_offset = 0.0

    def seek(self, target_time_ms: float, all_events: list[ScheduledEvent]) -> None:
        """Seek to a specific time position.

        Stops current playback, reloads events from target time onward, and
        adjusts timing state to resume from the new position.

        Args:
            target_time_ms: Target time in milliseconds from start
            all_events: Complete list of all events (needed to reload from target time)

        Example:
            >>> scheduler.seek(5000.0, all_events)  # Seek to 5 seconds
        """
        # Store current state
        was_playing = self.state == "playing"

        # Stop current playback
        self._stop_flag.set()
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=0.5)

        # Clamp target time to valid range
        if target_time_ms < 0:
            target_time_ms = 0.0

        # Reload only events at or after target time
        future_events = [e for e in all_events if e.time_ms >= target_time_ms]
        self.load_events(future_events)

        # Adjust timing offset to account for seek
        # We want elapsed time to match target_time_ms when playback resumes
        self.time_offset = target_time_ms / 1000  # Convert to seconds

        # Resume if was playing, otherwise stay paused/stopped
        if was_playing:
            self.start()
        else:
            self.state = "stopped"

    def _scheduler_loop(self) -> None:
        """Main scheduler loop (runs in separate thread).

        This is the core playback engine that:
        1. Retrieves events from the priority queue
        2. Waits until the event's target time
        3. Sends the MIDI message
        4. Calls callbacks if registered
        5. Repeats until queue is empty or stopped
        """
        while not self._stop_flag.is_set():
            # Check if paused
            if self.state == "paused":
                time.sleep(0.01)  # Sleep 10ms while paused
                continue

            # Get next event (non-blocking)
            try:
                event = self.event_queue.get_nowait()
            except queue.Empty:
                # No more events - playback complete
                self.state = "stopped"
                if self.on_complete:
                    self.on_complete()
                break

            # Calculate target time
            if self.start_time is not None:
                elapsed_ms = (time.perf_counter() - self.start_time - self.time_offset) * 1000
                wait_ms = event.time_ms - elapsed_ms

                # Wait until event time
                if wait_ms > 0:
                    target_time = time.perf_counter() + (wait_ms / 1000)
                    self._precise_wait(target_time)

            # Send MIDI message
            if self.state == "playing":  # Check state again (could have stopped during wait)
                self.midi_output.send_message(event.midi_message)

                # Call callback if registered
                if self.on_event_sent:
                    self.on_event_sent(event.metadata)

    def _precise_wait(self, target_time: float) -> None:
        """Hybrid sleep/busy-wait for precise timing with pause support.

        This method achieves sub-5ms timing precision by:
        1. Using time.sleep() for coarse delays > 10ms (efficient, low CPU)
        2. Using busy-wait loop for fine delays < 10ms (precise, higher CPU)
        3. Adjusting target_time when resuming from pause to account for pause duration

        Args:
            target_time: Target time from perf_counter()

        Example (internal use):
            >>> # Wait until 1.5 seconds from now
            >>> target = time.perf_counter() + 1.5
            >>> self._precise_wait(target)
        """
        was_paused = False
        pause_start = None

        # Sleep in small chunks to allow stop flag and pause checks
        while True:
            if self._stop_flag.is_set():
                break

            # Check for pause state - if paused, wait until resumed
            if self.state == "paused":
                if not was_paused:
                    # Just entered pause state - record when we paused
                    pause_start = time.perf_counter()
                    was_paused = True
                time.sleep(0.01)  # Sleep 10ms while paused
                continue

            if was_paused:
                # Just resumed from pause - adjust target_time for pause duration
                if pause_start is not None:
                    pause_duration = time.perf_counter() - pause_start
                    target_time += pause_duration
                was_paused = False
                pause_start = None

            # Check if we've reached the target time
            if time.perf_counter() >= target_time:
                break

            remaining = target_time - time.perf_counter()

            # Use sleep for coarse delay (> 10ms), but sleep in max 50ms chunks
            # to allow responsive stop flag checking
            if remaining > self.BUSY_WAIT_THRESHOLD_MS / 1000:
                sleep_time = min(0.05, remaining - (self.BUSY_WAIT_THRESHOLD_MS / 1000))
                time.sleep(sleep_time)
            else:
                # Busy-wait for final precision (< 10ms)
                break

        # Final busy-wait for sub-ms precision
        while time.perf_counter() < target_time:
            if self._stop_flag.is_set():
                break
            # Check pause in busy-wait loop too
            if self.state == "paused":
                time.sleep(0.001)  # Brief sleep if paused
                continue
