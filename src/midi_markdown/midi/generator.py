"""MIDI file generator.

Writes MIDI events to standard MIDI files.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from mido import Message, MetaMessage, MidiFile, MidiTrack

from midi_markdown.constants import DEFAULT_PPQ, MIDI_FORMAT_MULTI_TRACK
from midi_markdown.core.ir import EventType, IRProgram, MIDIEvent

if TYPE_CHECKING:
    from pathlib import Path


class MIDIGenerator:
    """Generates MIDI files from events.

    Uses the mido library to write standard MIDI files with proper formatting.
    """

    def __init__(self, ppq: int = DEFAULT_PPQ, midi_format: int = MIDI_FORMAT_MULTI_TRACK) -> None:
        """Initialize MIDI generator.

        Args:
            ppq: Pulses per quarter note
            midi_format: MIDI file format (0, 1, or 2)
        """
        self.ppq = ppq
        self.midi_format = midi_format

    def generate(self, events_or_ir: list[MIDIEvent] | IRProgram, output_path: Path) -> None:
        """Generate MIDI file from events or IR program.

        Args:
            events_or_ir: List of MIDI events or IRProgram
            output_path: Path to write MIDI file

        Raises:
            Exception: If generation fails
        """
        # Extract events from IRProgram if needed (backward compatible)
        if isinstance(events_or_ir, IRProgram):
            events = events_or_ir.events
            # Use resolution from IRProgram if available
            if events_or_ir.resolution:
                self.ppq = events_or_ir.resolution
        else:
            events = events_or_ir

        # Create MIDI file
        mid = MidiFile(type=self.midi_format, ticks_per_beat=self.ppq)

        # Create a single track (for format 1)
        track = MidiTrack()
        mid.tracks.append(track)

        # Convert events to mido messages
        messages = self._events_to_messages(events)

        # Add messages to track
        for msg in messages:
            track.append(msg)

        # Add end of track meta message
        track.append(MetaMessage("end_of_track", time=0))

        # Save file
        mid.save(str(output_path))

    def write_track(self, track_events: list[MIDIEvent]) -> MidiTrack:
        """Write a single MIDI track.

        Args:
            track_events: Events for this track

        Returns:
            mido Track object
        """
        track = MidiTrack()

        # Convert events to messages
        messages = self._events_to_messages(track_events)

        # Add messages to track
        for msg in messages:
            track.append(msg)

        # Add end of track
        track.append(MetaMessage("end_of_track", time=0))

        return track

    def _events_to_messages(self, events: list[MIDIEvent]) -> list[Message | MetaMessage]:
        """Convert MIDIEvent objects to mido Messages with delta times.

        Args:
            events: List of MIDI events (must be sorted by time)

        Returns:
            List of mido Message/MetaMessage objects with delta times
        """
        messages = []
        last_time = 0

        for event in sorted(events, key=lambda e: e.time):
            # Calculate delta time
            delta_time = event.time - last_time

            # Convert event type to mido message
            msg = self._event_to_message(event, delta_time)
            if msg:
                messages.append(msg)

            last_time = event.time

        return messages

    def _event_to_message(self, event: MIDIEvent, delta_time: int) -> Message | MetaMessage | None:
        """Convert a single MIDIEvent to a mido Message.

        Args:
            event: MIDI event to convert
            delta_time: Delta time in ticks since last event

        Returns:
            mido Message or MetaMessage, or None if type not supported
        """
        # Note: mido uses 0-15 for channels, MML uses 1-16
        channel = (event.channel - 1) if event.channel else 0

        # Map event types to mido messages
        if event.type == EventType.NOTE_ON:
            return Message(
                "note_on", channel=channel, note=event.data1, velocity=event.data2, time=delta_time
            )

        if event.type == EventType.NOTE_OFF:
            return Message(
                "note_off", channel=channel, note=event.data1, velocity=event.data2, time=delta_time
            )

        if event.type == EventType.PROGRAM_CHANGE:
            return Message("program_change", channel=channel, program=event.data1, time=delta_time)

        if event.type == EventType.CONTROL_CHANGE:
            return Message(
                "control_change",
                channel=channel,
                control=event.data1,
                value=event.data2,
                time=delta_time,
            )

        if event.type == EventType.PITCH_BEND:
            # Pitch bend: mido expects 0-16383, center at 8192
            # MML stores the bend value directly
            return Message("pitchwheel", channel=channel, pitch=event.data1, time=delta_time)

        if event.type == EventType.CHANNEL_PRESSURE:
            return Message("aftertouch", channel=channel, value=event.data1, time=delta_time)

        if event.type == EventType.POLY_PRESSURE:
            return Message(
                "polytouch", channel=channel, note=event.data1, value=event.data2, time=delta_time
            )

        if event.type == EventType.TEMPO:
            # Convert BPM to microseconds per beat
            # event.data1 contains BPM
            bpm = event.data1
            tempo_us = int(60_000_000 / bpm)
            return MetaMessage("set_tempo", tempo=tempo_us, time=delta_time)

        if event.type == EventType.TIME_SIGNATURE:
            # event.metadata should contain numerator, denominator, etc.
            # For now, use defaults
            return MetaMessage(
                "time_signature",
                numerator=4,
                denominator=4,
                clocks_per_click=24,
                notated_32nd_notes_per_beat=8,
                time=delta_time,
            )

        if event.type == EventType.MARKER:
            # text comes from metadata
            text = event.metadata.get("text", "") if event.metadata else ""
            return MetaMessage("marker", text=text, time=delta_time)

        if event.type == EventType.TEXT:
            text = event.metadata.get("text", "") if event.metadata else ""
            return MetaMessage("text", text=text, time=delta_time)

        if event.type == EventType.SYSEX:
            # SysEx data comes from metadata
            data = event.metadata.get("bytes", []) if event.metadata else []
            return Message("sysex", data=data, time=delta_time)

        # Return None for unsupported types
        return None
