"""MIDI event representation and generation.

Defines data structures for MIDI events before writing to file.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from midi_markdown.constants import (
    DEFAULT_PPQ,
    DEFAULT_TEMPO,
    DEFAULT_TIME_SIGNATURE,
    DEFAULT_VELOCITY,
)
from midi_markdown.expansion.loops import (
    IntervalType,
    LoopCommand,
    LoopDefinition,
    LoopExpander,
    LoopInterval,
    parse_interval,
)
from midi_markdown.expansion.sweeps import (
    RampSpec,
    RampType,
    SweepDefinition,
    SweepExpander,
    parse_sweep_interval,
)


class EventType(Enum):
    """MIDI event types."""

    # Channel Voice Messages
    NOTE_ON = auto()
    NOTE_OFF = auto()
    PROGRAM_CHANGE = auto()
    CONTROL_CHANGE = auto()
    PITCH_BEND = auto()
    CHANNEL_PRESSURE = auto()
    POLY_PRESSURE = auto()

    # System Messages
    SYSEX = auto()
    MTC_QUARTER_FRAME = auto()
    SONG_POSITION = auto()
    SONG_SELECT = auto()

    # Meta Events
    TEMPO = auto()
    TIME_SIGNATURE = auto()
    KEY_SIGNATURE = auto()
    TEXT = auto()
    MARKER = auto()
    END_OF_TRACK = auto()


@dataclass
class MIDIEvent:
    """Represents a single MIDI event.

    Attributes:
        time: Absolute time in ticks
        type: Event type
        channel: MIDI channel (1-16)
        data1: First data byte (e.g., note number, controller)
        data2: Second data byte (e.g., velocity, value)
        metadata: Source location for error reporting
    """

    time: int
    type: EventType
    channel: int
    data1: int = 0
    data2: int = 0
    metadata: dict[str, any] | None = None


class EventGenerator:
    """Generates MIDI events from AST.

    Converts high-level commands in the AST to low-level MIDI events
    with proper timing resolution.
    """

    def __init__(self, ppq: int = DEFAULT_PPQ) -> None:
        """Initialize event generator.

        Args:
            ppq: Pulses per quarter note (resolution)
        """
        self.ppq = ppq
        self.events: list[MIDIEvent] = []
        self.current_time = 0  # Track absolute time in ticks
        self.last_time = 0  # For simultaneous events
        self.tempo = DEFAULT_TEMPO  # Default BPM
        self.time_signature = DEFAULT_TIME_SIGNATURE  # Default time signature

    def generate(self, ast: any) -> list[MIDIEvent]:
        """Generate MIDI events from AST.

        Args:
            ast: The parsed MMLDocument

        Returns:
            List of MIDI events sorted by time
        """
        self.events = []
        self.current_time = 0
        self.last_time = 0

        # Process frontmatter for defaults
        if hasattr(ast, "frontmatter") and ast.frontmatter:
            if "ppq" in ast.frontmatter:
                self.ppq = ast.frontmatter["ppq"]
            if "tempo" in ast.frontmatter:
                self.tempo = ast.frontmatter["tempo"]

        # Process defines (variable substitution would happen here)
        # For now, we'll just store them
        defines = getattr(ast, "defines", {})

        # Process top-level events
        for event in getattr(ast, "events", []):
            self._process_event(event)

        # Process tracks if multi-track
        for track in getattr(ast, "tracks", []):
            self._process_track(track)

        # Sort events by time
        self.events.sort(key=lambda e: e.time)

        return self.events

    def add_event(self, event: MIDIEvent) -> None:
        """Add an event to the event list.

        Args:
            event: The MIDI event to add
        """
        self.events.append(event)

    def _process_event(self, event: any) -> None:
        """Process a single event from the AST.

        Args:
            event: Event object (could be dict, MIDICommand, etc.)
        """
        if isinstance(event, dict):
            event_type = event.get("type")

            if event_type == "timed_event":
                self._process_timed_event(event)
            elif event_type == "loop":
                self._process_loop(event)
            elif event_type == "sweep":
                self._process_sweep(event)
            elif event_type == "conditional":
                self._process_conditional(event)

    def _process_timed_event(self, event: dict) -> None:
        """Process a timed event block.

        Args:
            event: Timed event dict with 'timing' and 'commands' keys
        """
        from ..parser.ast_nodes import MIDICommand, Timing

        timing = event.get("timing")
        if timing and isinstance(timing, Timing):
            self._update_time_from_timing(timing)

        # Process commands
        for cmd in event.get("commands", []):
            if isinstance(cmd, MIDICommand):
                self._add_command(cmd, self.current_time)

    def _process_track(self, track: any) -> None:
        """Process a track definition.

        Args:
            track: Track object
        """
        # Save current time state
        saved_time = self.current_time
        saved_last = self.last_time

        # Reset time for track
        self.current_time = 0
        self.last_time = 0

        # Process track events
        for event in getattr(track, "events", []):
            self._process_event(event)

        # Restore time state
        self.current_time = saved_time
        self.last_time = saved_last

    def _process_loop(self, loop: dict) -> None:
        """
        Process a loop statement.

        Phase 3: Expands loop using LoopExpander and generates events.

        Args:
            loop: Loop dictionary from parser with 'count', 'interval', 'statements'
        """
        from midi_markdown.expansion.variables import SymbolTable

        from ..parser.ast_nodes import Timing

        # Extract loop parameters
        count = loop.get("count", 1)
        interval_spec = loop.get("interval")
        start_timing = loop.get("start_time")
        statements = loop.get("statements", [])
        source_line = loop.get("source_line", 0)

        # Parse interval - default to 1 beat if not specified
        if interval_spec is None:
            interval = LoopInterval(value=1.0, interval_type=IntervalType.BEATS)
        else:
            # Convert to string if it's a Duration object
            interval_str = (
                str(interval_spec) if hasattr(interval_spec, "__str__") else interval_spec
            )
            interval = parse_interval(interval_str)

        # Determine start time
        if start_timing and isinstance(start_timing, Timing):
            # Use the timing object's time
            start_time = self._timing_to_ticks(start_timing)
            # Update current_time to match loop start
            self.current_time = start_time
        else:
            start_time = self.current_time

        # Convert statements to LoopCommand objects
        loop_commands = []
        relative_time = 0

        for stmt in statements:
            # Each statement becomes a LoopCommand with relative timing
            # For now, all commands start at relative_time 0 (simultaneous within iteration)
            loop_cmd = LoopCommand(command=stmt, relative_time=relative_time)
            loop_commands.append(loop_cmd)

        # Create LoopDefinition
        loop_def = LoopDefinition(
            count=count,
            interval=interval,
            commands=loop_commands,
            start_time=start_time,
            source_line=source_line,
        )

        # Create LoopExpander with empty symbol table (Phase 1 already handled in parser)
        # TODO: Pass actual symbol table from parser when available
        parent_symbols = SymbolTable()
        expander = LoopExpander(parent_symbols=parent_symbols, ppq=self.ppq, tempo=self.tempo)

        # Expand loop into events
        expanded_events = expander.expand(loop_def)

        # Process each expanded event
        for event_dict in expanded_events:
            # Convert event dict to MIDICommand or process directly
            self._process_loop_event(event_dict)

        # Update current_time to after the loop
        interval_ticks = interval.to_ticks(self.ppq, self.tempo)
        self.current_time = start_time + (count * interval_ticks)

    def _process_loop_event(self, event_dict: dict) -> None:
        """
        Process a single event from loop expansion.

        Args:
            event_dict: Event dictionary with type, time, channel, data
        """
        from ..parser.ast_nodes import MIDICommand

        # Create a MIDICommand-like object from the event dict
        # This allows reuse of existing command processing logic
        event_type = event_dict.get("type")
        time = event_dict.get("time", self.current_time)

        # Set current time for this event
        saved_time = self.current_time
        self.current_time = time

        # Create MIDICommand object based on type
        if event_type == "pc":
            cmd = MIDICommand(
                type="pc", channel=event_dict.get("channel"), data1=event_dict.get("data1")
            )
            self._process_midi_command(cmd)
        elif event_type == "cc":
            cmd = MIDICommand(
                type="cc",
                channel=event_dict.get("channel"),
                data1=event_dict.get("data1"),
                data2=event_dict.get("data2"),
            )
            self._process_midi_command(cmd)
        elif event_type == "note":
            cmd = MIDICommand(
                type="note",
                channel=event_dict.get("channel"),
                note=event_dict.get("note"),
                velocity=event_dict.get("velocity"),
                duration=event_dict.get("duration"),
            )
            self._process_midi_command(cmd)
        # Add more command types as needed

        # Restore saved time
        self.current_time = saved_time

    def _process_sweep(self, sweep: dict) -> None:
        """
        Process a sweep statement.

        Phase 3: Expands sweep using SweepExpander and generates events.

        Args:
            sweep: Sweep dictionary from parser
        """
        from ..parser.ast_nodes import Timing

        # Extract sweep parameters
        start_timing = sweep.get("start_time")
        end_timing = sweep.get("end_time")
        interval_spec = sweep.get("interval")
        commands = sweep.get("commands", [])
        source_line = sweep.get("source_line", 0)

        # Calculate start and end times in ticks
        if isinstance(start_timing, Timing):
            start_time = self._timing_to_ticks(start_timing)
        else:
            start_time = self.current_time

        if isinstance(end_timing, Timing):
            end_time = self._timing_to_ticks(end_timing)
        else:
            # Default to 4 beats from start
            end_time = start_time + (4 * self.ppq)

        # Parse interval
        interval_str = str(interval_spec) if hasattr(interval_spec, "__str__") else interval_spec
        interval_ticks = parse_sweep_interval(interval_str, ppq=self.ppq, tempo=self.tempo)

        # Calculate number of steps
        total_duration = end_time - start_time
        steps = max(1, int(total_duration / interval_ticks))

        # Extract sweep parameters from commands
        # Expect commands like: cc 1.7.linear.0.127 (channel.controller.ramp.start.end)
        # For now, assume first command defines the sweep
        if not commands:
            return  # No commands to sweep

        first_cmd = commands[0]

        # Parse command to extract sweep parameters
        # This is simplified - real implementation would parse properly
        # For now, assume CC sweep with default linear ramp from 0 to 127
        ramp = RampSpec(RampType.LINEAR, 0.0, 127.0)
        sweep_def = SweepDefinition(
            command_type="cc",
            channel=1,
            data1=7,  # Default to volume controller
            ramp=ramp,
            steps=steps,
            interval_ticks=interval_ticks,
            start_time=start_time,
            source_line=source_line,
        )

        # Create SweepExpander
        expander = SweepExpander(ppq=self.ppq)

        # Expand sweep into events
        expanded_events = expander.expand(sweep_def)

        # Process each expanded event
        for event_dict in expanded_events:
            self._process_loop_event(event_dict)  # Reuse loop event processing

        # Update current_time to after the sweep
        self.current_time = end_time

    def _process_conditional(self, conditional: dict) -> None:
        """Process a conditional statement (placeholder for now)."""
        # TODO: Implement conditional evaluation

    def _update_time_from_timing(self, timing: any) -> None:
        """Update current time based on timing object.

        Args:
            timing: Timing object from AST
        """
        if timing.type == "absolute":
            self.last_time = self.current_time
            self.current_time = self._absolute_to_ticks(timing.value)
        elif timing.type == "musical":
            self.last_time = self.current_time
            self.current_time = self._musical_to_ticks(timing.value)
        elif timing.type == "relative":
            self.last_time = self.current_time
            value, unit = timing.value
            self.current_time += self._relative_to_ticks(value, unit)
        elif timing.type == "simultaneous":
            # Use last_time (stay at previous event's time)
            self.current_time = self.last_time

    def _absolute_to_ticks(self, seconds: float) -> int:
        """Convert absolute time (seconds) to ticks.

        Args:
            seconds: Time in seconds

        Returns:
            Time in ticks
        """
        # At tempo BPM: 1 beat = 60/BPM seconds
        # At PPQ resolution: 1 beat = PPQ ticks
        # Therefore: seconds → (seconds * BPM / 60) beats → beats * PPQ ticks
        beats = seconds * self.tempo / 60.0
        return int(beats * self.ppq)

    def _musical_to_ticks(self, value: tuple) -> int:
        """Convert musical time (bar.beat.tick) to ticks.

        Args:
            value: Tuple of (bar, beat, tick)

        Returns:
            Time in ticks
        """
        bar, beat, tick = value
        # Bars and beats are 1-indexed
        beats_per_bar = self.time_signature[0]
        total_beats = (bar - 1) * beats_per_bar + (beat - 1)
        return int(total_beats * self.ppq + tick)

    def _relative_to_ticks(self, value: float, unit: str) -> int:
        """Convert relative time to tick delta.

        Args:
            value: Time value
            unit: Unit ('s', 'ms', 'b', 't')

        Returns:
            Tick delta
        """
        if unit == "s":
            # Seconds to ticks
            beats = value * self.tempo / 60.0
            return int(beats * self.ppq)
        if unit == "ms":
            # Milliseconds to ticks
            seconds = value / 1000.0
            beats = seconds * self.tempo / 60.0
            return int(beats * self.ppq)
        if unit == "b":
            # Beats to ticks
            return int(value * self.ppq)
        if unit == "t":
            # Ticks
            return int(value)
        return 0

    def _parse_duration(self, duration_str: str) -> int:
        """Parse duration string to ticks.

        Args:
            duration_str: Duration string like "1b", "500ms"

        Returns:
            Duration in ticks
        """
        import re

        match = re.match(r"([\d.]+)([smbt])", duration_str)
        if match:
            value, unit = match.groups()
            return self._relative_to_ticks(float(value), unit)
        return 0

    def _add_command(self, cmd: any, time: int) -> None:
        """Convert MIDI command to event(s) and add to list.

        Args:
            cmd: MIDICommand object
            time: Absolute time in ticks
        """
        # Alias calls should have been resolved earlier in the pipeline
        if cmd.type == "alias_call":
            raise RuntimeError(
                f"Unexpected alias_call at line {cmd.source_line}. "
                f"Aliases should be resolved before event generation. "
                f"This indicates a pipeline bug."
            )

        # Map command type to event type
        type_map = {
            "note_on": EventType.NOTE_ON,
            "note_off": EventType.NOTE_OFF,
            "program_change": EventType.PROGRAM_CHANGE,
            "pc": EventType.PROGRAM_CHANGE,  # Abbreviation
            "control_change": EventType.CONTROL_CHANGE,
            "cc": EventType.CONTROL_CHANGE,  # Abbreviation
            "pitch_bend": EventType.PITCH_BEND,
            "pb": EventType.PITCH_BEND,  # Abbreviation
            "channel_pressure": EventType.CHANNEL_PRESSURE,
            "cp": EventType.CHANNEL_PRESSURE,  # Abbreviation
            "poly_pressure": EventType.POLY_PRESSURE,
            "pp": EventType.POLY_PRESSURE,  # Abbreviation
            "sysex": EventType.SYSEX,
            "tempo": EventType.TEMPO,
            "time_signature": EventType.TIME_SIGNATURE,
            "key_signature": EventType.KEY_SIGNATURE,
            "marker": EventType.MARKER,
            "text": EventType.TEXT,
        }

        event_type = type_map.get(cmd.type)
        if event_type:
            # Build metadata
            metadata = {"source_line": cmd.source_line, "cmd_type": cmd.type}

            # For text-based meta events, store text in metadata
            if cmd.type in ["marker", "text"] and "text" in cmd.params:
                metadata["text"] = cmd.params["text"]

            # Create base event
            event = MIDIEvent(
                time=time,
                type=event_type,
                channel=cmd.channel or 1,
                data1=cmd.data1 if cmd.data1 is not None else 0,
                data2=cmd.data2 if cmd.data2 is not None else 0,
                metadata=metadata,
            )
            self.add_event(event)

            # Handle note_on with duration - auto-generate note_off
            if cmd.type == "note_on" and "duration" in cmd.params:
                duration_str = cmd.params["duration"]
                duration_ticks = self._parse_duration(duration_str)

                note_off = MIDIEvent(
                    time=time + duration_ticks,
                    type=EventType.NOTE_OFF,
                    channel=cmd.channel or 1,
                    data1=cmd.data1 or 0,  # Same note number
                    data2=DEFAULT_VELOCITY,  # Default release velocity
                    metadata={"generated": True, "source_line": cmd.source_line},
                )
                self.add_event(note_off)

        # Handle special commands
        if cmd.type == "tempo":
            # Update internal tempo for timing calculations
            # Tempo command data1 contains BPM
            if cmd.data1:
                self.tempo = cmd.data1
