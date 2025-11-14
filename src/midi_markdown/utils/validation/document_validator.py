"""Document structure and command validation."""

from __future__ import annotations

from .errors import ValidationError
from .value_validator import Validator


class DocumentValidator:
    """Validates an entire MML document.

    Orchestrates validation of all document elements including:
    - MIDI command values (channels, velocities, CC values, etc.)
    - Track configuration (unique names, valid channels)
    - Document-level constraints
    """

    def __init__(self):
        """Initialize document validator."""
        self.errors: list[ValidationError] = []

    def validate(self, doc) -> list[ValidationError]:
        """Validate an entire MML document.

        Args:
            doc: MMDDocument instance to validate

        Returns:
            List of ValidationErrors (empty if valid)
        """
        self.errors = []

        # Validate all events/commands
        self._validate_events(doc.events)

        # Validate tracks
        if doc.tracks:
            self._validate_tracks(doc.tracks)

        return self.errors

    def _validate_events(self, events: list) -> None:
        """Validate all MIDI events/commands in a list.

        Args:
            events: List of events (can be dicts with 'commands' or MIDICommand objects)
        """
        for event in events:
            # Skip section headers and other non-command tokens
            if not isinstance(event, dict | object) or not hasattr(event, "__dict__"):
                if not isinstance(event, dict):
                    continue

            # Events from parser are dicts with 'commands' and 'timing'
            if isinstance(event, dict) and "commands" in event:
                for cmd in event["commands"]:
                    # Skip non-command objects (like Lark Tree objects)
                    if not hasattr(cmd, "type"):
                        continue
                    self._validate_command(cmd)
            elif hasattr(event, "type"):
                # Direct MIDICommand object
                self._validate_command(event)

    def _validate_command(self, cmd) -> None:
        """Validate a single MIDI command.

        Args:
            cmd: MIDICommand instance
        """
        try:
            cmd_type = cmd.type

            # Skip meta commands that don't need MIDI value validation
            # These include: time_signature, marker, sysex, etc.
            meta_commands = (
                "time_signature",
                "marker",
                "sysex",
                "text",
                "copyright",
                "track_name",
                "instrument_name",
            )
            if cmd_type in meta_commands:
                return

            # Validate channel if present
            if cmd.channel is not None:
                try:
                    Validator.validate_channel(cmd.channel)
                except ValidationError as e:
                    self.errors.append(
                        ValidationError(f"{e.message} in {cmd_type} command", line=cmd.source_line)
                    )

            # Validate based on command type
            if cmd_type in ("note_on", "note", "note_off"):
                self._validate_note_command(cmd)
            elif cmd_type == "cc":  # Parser uses "cc" not "control_change"
                self._validate_cc_command(cmd)
            elif cmd_type == "pc":  # Parser uses "pc" not "program_change"
                self._validate_pc_command(cmd)
            elif cmd_type == "pitch_bend":
                self._validate_pitch_bend_command(cmd)
            elif cmd_type == "channel_pressure":
                self._validate_pressure_command(cmd)
            elif cmd_type == "poly_pressure":
                self._validate_poly_pressure_command(cmd)
            elif cmd_type == "tempo":
                self._validate_tempo_command(cmd)

        except Exception as e:
            # Catch any unexpected errors
            self.errors.append(
                ValidationError(f"Error validating {cmd.type} command: {e}", line=cmd.source_line)
            )

    def _validate_note_command(self, cmd) -> None:
        """Validate note_on/note_off command."""
        # Validate note number (data1)
        if cmd.data1 is not None:
            try:
                Validator.validate_note(cmd.data1)
            except ValidationError as e:
                self.errors.append(
                    ValidationError(f"{e.message} in {cmd.type} command", line=cmd.source_line)
                )

        # Validate velocity (data2)
        if cmd.data2 is not None:
            try:
                Validator.validate_velocity(cmd.data2)
            except ValidationError as e:
                self.errors.append(
                    ValidationError(f"{e.message} in {cmd.type} command", line=cmd.source_line)
                )

    def _validate_cc_command(self, cmd) -> None:
        """Validate control_change command."""
        # Validate CC controller number (data1)
        if cmd.data1 is not None:
            try:
                Validator.validate_cc_controller(cmd.data1)
            except ValidationError as e:
                self.errors.append(
                    ValidationError(f"{e.message} in control_change command", line=cmd.source_line)
                )

        # Validate CC value (data2)
        if cmd.data2 is not None:
            try:
                Validator.validate_cc_value(cmd.data2)
            except ValidationError as e:
                self.errors.append(
                    ValidationError(f"{e.message} in control_change command", line=cmd.source_line)
                )

    def _validate_pc_command(self, cmd) -> None:
        """Validate program_change command."""
        # Validate program number (data1)
        if cmd.data1 is not None:
            try:
                Validator.validate_program(cmd.data1)
            except ValidationError as e:
                self.errors.append(
                    ValidationError(f"{e.message} in program_change command", line=cmd.source_line)
                )

    def _validate_pitch_bend_command(self, cmd) -> None:
        """Validate pitch_bend command."""
        # Pitch bend value is in data1
        if cmd.data1 is not None:
            try:
                Validator.validate_pitch_bend(cmd.data1)
            except ValidationError as e:
                self.errors.append(
                    ValidationError(f"{e.message} in pitch_bend command", line=cmd.source_line)
                )

    def _validate_pressure_command(self, cmd) -> None:
        """Validate channel_pressure command."""
        # Validate pressure value (data1)
        if cmd.data1 is not None:
            try:
                Validator.validate_midi_value(cmd.data1)
            except ValidationError as e:
                self.errors.append(
                    ValidationError(
                        f"{e.message} in channel_pressure command", line=cmd.source_line
                    )
                )

    def _validate_poly_pressure_command(self, cmd) -> None:
        """Validate poly_pressure command."""
        # Validate note number (data1)
        if cmd.data1 is not None:
            try:
                Validator.validate_note(cmd.data1)
            except ValidationError as e:
                self.errors.append(
                    ValidationError(f"{e.message} in poly_pressure command", line=cmd.source_line)
                )

        # Validate pressure value (data2)
        if cmd.data2 is not None:
            try:
                Validator.validate_midi_value(cmd.data2)
            except ValidationError as e:
                self.errors.append(
                    ValidationError(f"{e.message} in poly_pressure command", line=cmd.source_line)
                )

    def _validate_tempo_command(self, cmd) -> None:
        """Validate tempo command."""
        # Tempo value is in params
        if "bpm" in cmd.params:
            try:
                Validator.validate_tempo(cmd.params["bpm"])
            except ValidationError as e:
                self.errors.append(
                    ValidationError(f"{e.message} in tempo command", line=cmd.source_line)
                )

    def _validate_tracks(self, tracks: list) -> None:
        """Validate track configuration.

        Args:
            tracks: List of Track objects
        """
        # Check for duplicate track names
        track_names = [track.name for track in tracks if hasattr(track, "name")]
        duplicates = [name for name in track_names if track_names.count(name) > 1]
        if duplicates:
            unique_dups = list(set(duplicates))
            self.errors.append(
                ValidationError(f"Duplicate track names found: {', '.join(unique_dups)}")
            )

        # Validate each track's channel assignment
        for track in tracks:
            if hasattr(track, "channel") and track.channel is not None:
                try:
                    Validator.validate_channel(track.channel)
                except ValidationError as e:
                    track_name = track.name if hasattr(track, "name") else "unnamed"
                    self.errors.append(ValidationError(f"{e.message} in track '{track_name}'"))
