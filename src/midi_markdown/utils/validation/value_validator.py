"""MIDI value range validation."""

from __future__ import annotations

from midi_markdown.constants import (
    MIDI_CHANNEL_MAX,
    MIDI_CHANNEL_MIN,
    MIDI_MAX,
    MIDI_MIN,
    MIDI_NOTE_MAX,
    MIDI_NOTE_MIN,
    PITCH_BEND_MAX,
    PITCH_BEND_MIN,
    TEMPO_MAX,
    TEMPO_MIN,
)
from midi_markdown.utils.parameter_types import note_to_midi

from .errors import ValidationError


def _suggest_in_range(value: int, min_val: int, max_val: int, label: str = "value") -> str:
    """Generate a helpful suggestion for an out-of-range value.

    Args:
        value: The invalid value
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        label: Human-readable name for the value type

    Returns:
        Suggestion string with clamped value
    """
    clamped = min(max(min_val, value), max_val)
    return f"Valid {label} range: {min_val}-{max_val}. Did you mean {clamped}?"


class Validator:
    """Validates MIDI values and constraints.

    Provides static methods for validating MIDI values, channels, notes, tempo, and other constraints.
    All methods raise ValidationError if validation fails.
    """

    @staticmethod
    def validate_midi_value(value: int, min_val: int = 0, max_val: int = 127) -> None:
        """Validate a MIDI value is in range.

        Args:
            value: Value to validate
            min_val: Minimum allowed value
            max_val: Maximum allowed value

        Raises:
            ValidationError: If value is out of range
        """
        from midi_markdown.parser.ast_nodes import (
            CurveExpression,
            EnvelopeExpression,
            RandomExpression,
            WaveExpression,
        )

        # Allow modulation expressions - validation happens during expansion
        if isinstance(
            value, RandomExpression | CurveExpression | WaveExpression | EnvelopeExpression
        ):
            return

        if not isinstance(value, int):
            msg = f"MIDI value must be an integer, got {type(value).__name__}"
            raise ValidationError(
                msg,
                error_code="E201",
                suggestion="MIDI values must be integers. Most MIDI values range from 0 to 127.",
            )

        if not (min_val <= value <= max_val):
            msg = f"MIDI value {value} out of range [{min_val}-{max_val}]"
            raise ValidationError(
                msg,
                error_code="E200",
                suggestion=_suggest_in_range(value, min_val, max_val, "MIDI value"),
            )

    @staticmethod
    def validate_channel(channel: int) -> None:
        """Validate MIDI channel is in range 1-16.

        Args:
            channel: Channel number to validate

        Raises:
            ValidationError: If channel is invalid
        """
        if not isinstance(channel, int):
            msg = f"Channel must be an integer, got {type(channel).__name__}"
            raise ValidationError(
                msg,
                error_code="E201",
                suggestion="MIDI channels must be specified as integers from 1 to 16.",
            )

        if not (MIDI_CHANNEL_MIN <= channel <= MIDI_CHANNEL_MAX):
            msg = f"Channel {channel} out of range [{MIDI_CHANNEL_MIN}-{MIDI_CHANNEL_MAX}]"
            raise ValidationError(
                msg,
                error_code="E204",
                suggestion=_suggest_in_range(
                    channel, MIDI_CHANNEL_MIN, MIDI_CHANNEL_MAX, "MIDI channel"
                ),
            )

    @staticmethod
    def validate_note(note: int | str) -> int:
        """Validate and convert note to MIDI note number.

        Args:
            note: Note number (0-127) or name (e.g., "C4", "D#5")

        Returns:
            MIDI note number (0-127)

        Raises:
            ValidationError: If note is invalid
        """
        from midi_markdown.parser.ast_nodes import RandomExpression

        # Allow RandomExpression - validation happens during expansion
        if isinstance(note, RandomExpression):
            return note

        if isinstance(note, str):
            try:
                return note_to_midi(note)
            except ValueError as e:
                msg = f"Invalid note name '{note}': {e}"
                raise ValidationError(
                    msg,
                    error_code="E202",
                    suggestion="Use note names like C4, D#5, Eb3, or MIDI note numbers (0-127). "
                    "Middle C is C4 (MIDI note 60).",
                )

        if isinstance(note, int):
            if not (MIDI_NOTE_MIN <= note <= MIDI_NOTE_MAX):
                msg = f"Note number {note} out of range [{MIDI_NOTE_MIN}-{MIDI_NOTE_MAX}]"
                raise ValidationError(
                    msg,
                    error_code="E205",
                    suggestion=_suggest_in_range(note, MIDI_NOTE_MIN, MIDI_NOTE_MAX, "note"),
                )
            return note

        msg = f"Note must be string or integer, got {type(note).__name__}"
        raise ValidationError(
            msg,
            error_code="E201",
            suggestion="Notes can be specified as note names (C4, D#5) or MIDI note numbers (0-127).",
        )

    @staticmethod
    def validate_velocity(velocity: int) -> None:
        """Validate MIDI velocity is in range 0-127.

        Args:
            velocity: Velocity value to validate

        Raises:
            ValidationError: If velocity is invalid
        """
        from midi_markdown.parser.ast_nodes import (
            CurveExpression,
            EnvelopeExpression,
            RandomExpression,
            WaveExpression,
        )

        # Allow modulation expressions - validation happens during expansion
        if isinstance(
            velocity, RandomExpression | CurveExpression | WaveExpression | EnvelopeExpression
        ):
            return

        if not isinstance(velocity, int):
            msg = f"Velocity must be an integer, got {type(velocity).__name__}"
            raise ValidationError(
                msg,
                error_code="E201",
                suggestion="Velocity must be a whole number from 0 (silent) to 127 (maximum).",
            )

        if not (MIDI_MIN <= velocity <= MIDI_MAX):
            msg = f"Velocity {velocity} out of range [{MIDI_MIN}-{MIDI_MAX}]"
            raise ValidationError(
                msg,
                error_code="E206",
                suggestion=_suggest_in_range(velocity, MIDI_MIN, MIDI_MAX, "velocity"),
            )

    @staticmethod
    def validate_cc_controller(controller: int) -> None:
        """Validate CC controller number is in range 0-127.

        Args:
            controller: Controller number to validate

        Raises:
            ValidationError: If controller is invalid
        """
        if not isinstance(controller, int):
            msg = f"CC controller must be an integer, got {type(controller).__name__}"
            raise ValidationError(
                msg,
                error_code="E201",
                suggestion="CC controller numbers must be integers from 0 to 127. "
                "Common controllers: 7=Volume, 10=Pan, 64=Sustain, 74=Brightness.",
            )

        if not (MIDI_MIN <= controller <= MIDI_MAX):
            msg = f"CC controller {controller} out of range [{MIDI_MIN}-{MIDI_MAX}]"
            raise ValidationError(
                msg,
                error_code="E207",
                suggestion=_suggest_in_range(controller, MIDI_MIN, MIDI_MAX, "CC controller"),
            )

    @staticmethod
    def validate_cc_value(value: int | dict) -> None:
        """Validate CC value is in range 0-127 or a valid expression (ramp/random).

        Args:
            value: CC value to validate (int or dict for ramp/random expressions)

        Raises:
            ValidationError: If value is invalid
        """
        # Import modulation expression types for type checking
        from midi_markdown.parser.ast_nodes import (
            CurveExpression,
            EnvelopeExpression,
            RandomExpression,
            WaveExpression,
        )

        # Allow modulation expression AST nodes (will be expanded later)
        if isinstance(
            value, RandomExpression | CurveExpression | WaveExpression | EnvelopeExpression
        ):
            # Validation happens during expansion - just accept it here
            return

        # Allow dict values for ramp and random expressions
        if isinstance(value, dict):
            if value.get("type") in ("ramp", "random"):
                # Validate ramp/random expression values
                if value.get("type") == "ramp":
                    start = value.get("start", 0)
                    end = value.get("end", 127)
                    if not (MIDI_MIN <= start <= MIDI_MAX):
                        msg = f"Ramp start value {start} out of range [{MIDI_MIN}-{MIDI_MAX}]"
                        raise ValidationError(
                            msg,
                            error_code="E208",
                            suggestion=_suggest_in_range(start, MIDI_MIN, MIDI_MAX, "ramp start"),
                        )
                    if not (MIDI_MIN <= end <= MIDI_MAX):
                        msg = f"Ramp end value {end} out of range [{MIDI_MIN}-{MIDI_MAX}]"
                        raise ValidationError(
                            msg,
                            error_code="E208",
                            suggestion=_suggest_in_range(end, MIDI_MIN, MIDI_MAX, "ramp end"),
                        )
                return
            msg = f"Unknown CC expression type: {value.get('type')}"
            raise ValidationError(
                msg,
                error_code="E203",
                suggestion="Supported CC expression types: ramp, random.",
            )

        if not isinstance(value, int):
            msg = (
                f"CC value must be an integer or ramp/random expression, got {type(value).__name__}"
            )
            raise ValidationError(
                msg,
                error_code="E201",
                suggestion="CC values must be integers (0-127) or expressions like ramp(0, 127).",
            )

        if not (MIDI_MIN <= value <= MIDI_MAX):
            msg = f"CC value {value} out of range [{MIDI_MIN}-{MIDI_MAX}]"
            raise ValidationError(
                msg,
                error_code="E208",
                suggestion=_suggest_in_range(value, MIDI_MIN, MIDI_MAX, "CC value"),
            )

    @staticmethod
    def validate_program(program: int) -> None:
        """Validate program change number is in range 0-127.

        Args:
            program: Program number to validate

        Raises:
            ValidationError: If program is invalid
        """
        if not isinstance(program, int):
            msg = f"Program must be an integer, got {type(program).__name__}"
            raise ValidationError(
                msg,
                error_code="E201",
                suggestion="Program change numbers must be integers from 0 to 127. "
                "0 = Acoustic Grand Piano (GM), 32 = Acoustic Bass, etc.",
            )

        if not (MIDI_MIN <= program <= MIDI_MAX):
            msg = f"Program {program} out of range [{MIDI_MIN}-{MIDI_MAX}]"
            raise ValidationError(
                msg,
                error_code="E209",
                suggestion=_suggest_in_range(program, MIDI_MIN, MIDI_MAX, "program"),
            )

    @staticmethod
    def validate_pitch_bend(value: int) -> None:
        """Validate pitch bend value is in range -8192 to +8191.

        Args:
            value: Pitch bend value to validate

        Raises:
            ValidationError: If value is invalid
        """
        from midi_markdown.parser.ast_nodes import (
            CurveExpression,
            EnvelopeExpression,
            RandomExpression,
            WaveExpression,
        )

        # Allow modulation expressions - validation happens during expansion
        if isinstance(
            value, RandomExpression | CurveExpression | WaveExpression | EnvelopeExpression
        ):
            return

        if not isinstance(value, int):
            msg = f"Pitch bend must be an integer, got {type(value).__name__}"
            raise ValidationError(
                msg,
                error_code="E201",
                suggestion="Pitch bend values must be integers. Range: -8192 (down 2 semitones) "
                "to +8191 (up 2 semitones). 0 = no bend.",
            )

        if not (PITCH_BEND_MIN <= value <= PITCH_BEND_MAX):
            msg = f"Pitch bend {value} out of range [{PITCH_BEND_MIN}-{PITCH_BEND_MAX}]"
            raise ValidationError(
                msg,
                error_code="E210",
                suggestion=_suggest_in_range(value, PITCH_BEND_MIN, PITCH_BEND_MAX, "pitch bend"),
            )

    @staticmethod
    def validate_tempo(bpm: int | float) -> None:
        """Validate tempo is in reasonable range.

        Args:
            bpm: Tempo in beats per minute

        Raises:
            ValidationError: If tempo is invalid
        """
        if not isinstance(bpm, int | float):
            msg = f"Tempo must be a number, got {type(bpm).__name__}"
            raise ValidationError(
                msg,
                error_code="E201",
                suggestion="Tempo must be a number (can be decimal). Common values: 60 (Largo), "
                "120 (Moderato), 140 (Allegro), 180 (Presto).",
            )

        if not (TEMPO_MIN <= bpm <= TEMPO_MAX):
            clamped = min(max(TEMPO_MIN, bpm), TEMPO_MAX)
            msg = f"Tempo {bpm} BPM out of range [{TEMPO_MIN}-{TEMPO_MAX}]"
            raise ValidationError(
                msg,
                error_code="E211",
                suggestion=f"Valid tempo range: {TEMPO_MIN}-{TEMPO_MAX} BPM. Did you mean {clamped}?",
            )
