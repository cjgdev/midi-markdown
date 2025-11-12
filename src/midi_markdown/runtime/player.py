"""Real-time MIDI playback engine.

This module provides the RealtimePlayer class for playing compiled MML programs
in real-time through MIDI output ports.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from midi_markdown.core.ir import EventType
from midi_markdown.runtime.midi_io import MIDIOutputManager
from midi_markdown.runtime.scheduler import EventScheduler, ScheduledEvent
from midi_markdown.runtime.tempo_tracker import TempoTracker

if TYPE_CHECKING:
    from midi_markdown.core.ir import IRProgram, MIDIEvent


class RealtimePlayer:
    """High-level real-time MIDI playback from IRProgram.

    The RealtimePlayer orchestrates MIDI I/O, tempo tracking, and event scheduling
    to play compiled MML programs in real-time through MIDI output devices.

    Example:
        >>> from midi_markdown.core.compiler import compile_mml
        >>> from midi_markdown.runtime.player import RealtimePlayer
        >>> ir = compile_mml("examples/00_basics/00_hello_world.mmd")
        >>> player = RealtimePlayer(ir, "IAC Driver Bus 1")
        >>> player.play()
        >>> # ... wait for completion ...
        >>> player.stop()
    """

    def __init__(self, ir_program: IRProgram, port_name: str | int) -> None:
        """Initialize real-time player.

        Args:
            ir_program: Compiled IR program to play
            port_name: MIDI output port name or index

        Raises:
            MIDIIOError: If MIDI port cannot be opened
        """
        self.ir_program = ir_program
        self.midi_output = MIDIOutputManager()
        self.port_name = port_name

        # Build tempo tracker from IR
        self.tempo_tracker = TempoTracker(
            ppq=ir_program.resolution, default_tempo=float(ir_program.initial_tempo)
        )
        self._build_tempo_map()

        # Get time signature for musical navigation
        self.time_signature = ir_program.metadata.get("time_signature", (4, 4))
        self.ppq = ir_program.resolution

        # Create scheduler and store all scheduled events for seeking
        self.scheduler = EventScheduler(self.midi_output)
        self._all_scheduled_events: list[ScheduledEvent] = []
        self._load_events()

        # Open MIDI port
        self.midi_output.open_port(port_name)

    def play(self) -> None:
        """Start playback from beginning.

        If already playing, this is a no-op.
        """
        self.scheduler.start()

    def pause(self) -> None:
        """Pause playback.

        Position is preserved for resume(). If not playing, this is a no-op.
        """
        self.scheduler.pause()

    def resume(self) -> None:
        """Resume from paused position.

        If not paused, this is a no-op. Time offset is adjusted to account
        for pause duration.
        """
        self.scheduler.resume()

    def stop(self) -> None:
        """Stop playback and send All Notes Off.

        Stops the scheduler, sends CC 123 (All Notes Off) on all 16 channels
        to prevent stuck notes, and resets playback position.
        """
        self.scheduler.stop()
        self._all_notes_off()

    def seek(self, target_time_ms: float) -> None:
        """Seek to a specific time position.

        Stops current playback, sends All Notes Off to prevent stuck notes,
        and resumes playback from the target time.

        Args:
            target_time_ms: Target time in milliseconds from start

        Example:
            >>> player.seek(5000.0)  # Seek to 5 seconds
        """
        # Send All Notes Off before seeking to prevent stuck notes
        self._all_notes_off()

        # Delegate to scheduler
        self.scheduler.seek(target_time_ms, self._all_scheduled_events)

    def seek_bars(self, bar_offset: int, current_position_ms: float) -> float:
        """Seek forward or backward by a number of bars.

        Args:
            bar_offset: Number of bars to seek (positive=forward, negative=backward)
            current_position_ms: Current playback position in milliseconds

        Returns:
            New position in milliseconds after seeking

        Example:
            >>> new_pos = player.seek_bars(1, 5000.0)  # Seek forward 1 bar
            >>> new_pos = player.seek_bars(-2, 10000.0)  # Seek backward 2 bars
        """
        # Calculate ticks per bar
        beats_per_bar = self.time_signature[0]
        ticks_per_bar = beats_per_bar * self.ppq

        # Convert current position to ticks
        current_ticks = self.tempo_tracker.ms_to_ticks(current_position_ms)

        # Calculate new position in ticks
        new_ticks = current_ticks + (bar_offset * ticks_per_bar)
        new_ticks = max(0, new_ticks)  # Clamp to valid range

        # Convert back to milliseconds
        new_position_ms = self.tempo_tracker.ticks_to_ms(new_ticks)

        # Perform the seek
        self.seek(new_position_ms)

        return new_position_ms

    def seek_beats(self, beat_offset: int, current_position_ms: float) -> float:
        """Seek forward or backward by a number of beats.

        Args:
            beat_offset: Number of beats to seek (positive=forward, negative=backward)
            current_position_ms: Current playback position in milliseconds

        Returns:
            New position in milliseconds after seeking

        Example:
            >>> new_pos = player.seek_beats(4, 5000.0)  # Seek forward 4 beats
            >>> new_pos = player.seek_beats(-1, 10000.0)  # Seek backward 1 beat
        """
        # Calculate ticks per beat
        ticks_per_beat = self.ppq

        # Convert current position to ticks
        current_ticks = self.tempo_tracker.ms_to_ticks(current_position_ms)

        # Calculate new position in ticks
        new_ticks = current_ticks + (beat_offset * ticks_per_beat)
        new_ticks = max(0, new_ticks)  # Clamp to valid range

        # Convert back to milliseconds
        new_position_ms = self.tempo_tracker.ticks_to_ms(new_ticks)

        # Perform the seek
        self.seek(new_position_ms)

        return new_position_ms

    def get_duration_ms(self) -> float:
        """Get total duration in milliseconds.

        Returns:
            Duration in milliseconds, or 0.0 if no events
        """
        if not self.ir_program.events:
            return 0.0

        # Get last event time
        last_tick = max(event.time for event in self.ir_program.events)
        return self.tempo_tracker.ticks_to_ms(last_tick)

    def is_complete(self) -> bool:
        """Check if playback is complete.

        Returns:
            True if scheduler is stopped, False otherwise
        """
        return self.scheduler.state == "stopped"

    def _build_tempo_map(self) -> None:
        """Extract tempo changes from IRProgram and build tempo map.

        Scans all events for TEMPO events and adds them to the tempo tracker.
        """
        # Find all tempo events
        for event in self.ir_program.events:
            if event.type == EventType.TEMPO:
                self.tempo_tracker.add_tempo_change(event.time, float(event.data1))

        self.tempo_tracker.build_tempo_map()

    def _load_events(self) -> None:
        """Convert IR events to scheduled events.

        Converts all IR events (with tick timing) to ScheduledEvents (with
        millisecond timing) and loads them into the scheduler. Tempo events
        are skipped as they're already in the tempo map.
        """
        scheduled_events = []

        for event in self.ir_program.events:
            # Skip tempo events (already in tempo map)
            if event.type == EventType.TEMPO:
                continue

            # Convert tick to milliseconds
            time_ms = self.tempo_tracker.ticks_to_ms(event.time)

            # Convert IR event to MIDI message
            midi_message = self._event_to_midi_message(event)
            if midi_message:
                scheduled_events.append(
                    ScheduledEvent(
                        time_ms=time_ms,
                        midi_message=midi_message,
                        metadata={
                            "type": event.type.name,
                            "tick": event.time,
                            "channel": event.channel,
                        },
                    )
                )

        # Store all events for seeking
        self._all_scheduled_events = scheduled_events
        self.scheduler.load_events(scheduled_events)

    def _event_to_midi_message(self, event: MIDIEvent) -> list[int] | None:
        """Convert IR event to MIDI message bytes.

        Args:
            event: IR event to convert

        Returns:
            MIDI message as list of bytes, or None if event type is not
            supported for MIDI output (e.g., markers, text events)
        """
        if event.type == EventType.NOTE_ON:
            return [0x90 + event.channel - 1, event.data1, event.data2]
        if event.type == EventType.NOTE_OFF:
            return [0x80 + event.channel - 1, event.data1, event.data2]
        if event.type == EventType.CONTROL_CHANGE:
            return [0xB0 + event.channel - 1, event.data1, event.data2]
        if event.type == EventType.PROGRAM_CHANGE:
            return [0xC0 + event.channel - 1, event.data1]
        if event.type == EventType.PITCH_BEND:
            # Pitch bend is 14-bit value (0-16383)
            # data1 contains the full value, split into LSB and MSB
            lsb = event.data1 & 0x7F
            msb = (event.data1 >> 7) & 0x7F
            return [0xE0 + event.channel - 1, lsb, msb]
        if event.type == EventType.CHANNEL_PRESSURE:
            return [0xD0 + event.channel - 1, event.data1]
        if event.type == EventType.POLY_PRESSURE:
            return [0xA0 + event.channel - 1, event.data1, event.data2]
        # Unsupported event type for MIDI output (markers, text, sysex, etc.)
        return None

    def _all_notes_off(self) -> None:
        """Send CC 123 (All Notes Off) on all channels.

        Sends All Notes Off message on all 16 MIDI channels to prevent
        stuck notes when playback is stopped.
        """
        for channel in range(1, 17):
            self.midi_output.send_message([0xB0 + channel - 1, 123, 0])

    def __del__(self) -> None:
        """Cleanup - close MIDI port."""
        if hasattr(self, "midi_output"):
            self.midi_output.close_port()
