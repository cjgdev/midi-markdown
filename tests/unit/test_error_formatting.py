"""Unit tests for enhanced error formatting (Phase 4, Stage 2)."""

from __future__ import annotations

from unittest.mock import Mock

import pytest
from rich.console import Console

from midi_markdown.cli.errors import _create_range_table, show_validation_error
from midi_markdown.utils.validation import ValidationError


class TestRangeTableCreation:
    """Test the range table creation for validation errors."""

    def test_channel_range_table(self):
        """Test range table for channel validation errors."""
        table = _create_range_table("E204", no_color=False)
        assert table is not None
        # Table structure is tested visually via integration tests

    def test_note_range_table(self):
        """Test range table for note validation errors."""
        table = _create_range_table("E205", no_color=False)
        assert table is not None

    def test_velocity_range_table(self):
        """Test range table for velocity validation errors."""
        table = _create_range_table("E206", no_color=False)
        assert table is not None

    def test_cc_controller_range_table(self):
        """Test range table for CC controller validation errors."""
        table = _create_range_table("E207", no_color=False)
        assert table is not None

    def test_cc_value_range_table(self):
        """Test range table for CC value validation errors."""
        table = _create_range_table("E208", no_color=False)
        assert table is not None

    def test_program_range_table(self):
        """Test range table for program change validation errors."""
        table = _create_range_table("E209", no_color=False)
        assert table is not None

    def test_pitch_bend_range_table(self):
        """Test range table for pitch bend validation errors."""
        table = _create_range_table("E210", no_color=False)
        assert table is not None

    def test_tempo_range_table(self):
        """Test range table for tempo validation errors."""
        table = _create_range_table("E211", no_color=False)
        assert table is not None

    def test_no_table_for_non_range_error(self):
        """Test that non-range error codes return None."""
        table = _create_range_table("E101", no_color=False)
        assert table is None

    def test_no_color_mode(self):
        """Test range table creation with no_color=True."""
        table = _create_range_table("E204", no_color=True)
        assert table is not None


class TestValidationErrorFormatting:
    """Test enhanced validation error display."""

    def test_error_with_code_and_suggestion(self):
        """Test validation error displays code and suggestion."""
        error = ValidationError(
            "Channel 99 out of range [1-16]",
            line=10,
            column=5,
            error_code="E204",
            suggestion="Valid MIDI channel range: 1-16. Did you mean 16?",
        )

        console = Mock(spec=Console)
        show_validation_error(error, None, console, no_color=False, no_emoji=False)

        # Verify console.print was called with error message
        assert console.print.called

    def test_error_displays_range_table(self):
        """Test that range errors display the range table."""
        error = ValidationError(
            "Note 200 out of range [0-127]",
            error_code="E205",
            suggestion="Valid note range: 0-127. Did you mean 127?",
        )

        console = Mock(spec=Console)
        show_validation_error(error, None, console, no_color=False, no_emoji=False)

        # Verify console.print was called multiple times (error + table + suggestion)
        assert console.print.call_count >= 2

    def test_error_with_no_color(self):
        """Test validation error with no_color flag."""
        error = ValidationError(
            "Invalid value",
            error_code="E204",
            suggestion="Use values 1-16",
        )

        console = Mock(spec=Console)
        show_validation_error(error, None, console, no_color=True, no_emoji=False)

        assert console.print.called

    def test_error_with_no_emoji(self):
        """Test validation error with no_emoji flag."""
        error = ValidationError(
            "Invalid value",
            error_code="E204",
            suggestion="Use values 1-16",
        )

        console = Mock(spec=Console)
        show_validation_error(error, None, console, no_color=False, no_emoji=True)

        assert console.print.called

    def test_error_without_suggestion(self):
        """Test validation error without suggestion field."""
        error = ValidationError("Generic validation error", error_code="E200")

        console = Mock(spec=Console)
        show_validation_error(error, None, console, no_color=False, no_emoji=False)

        assert console.print.called


class TestValidationErrorWithSuggestions:
    """Test that validators populate suggestion field correctly."""

    def test_channel_validator_suggestion(self):
        """Test channel validator provides helpful suggestion."""
        from midi_markdown.utils.validation import Validator

        with pytest.raises(ValidationError) as exc_info:
            Validator.validate_channel(99)

        error = exc_info.value
        assert error.error_code == "E204"
        assert error.suggestion is not None
        assert "1-16" in error.suggestion

    def test_note_validator_suggestion(self):
        """Test note validator provides helpful suggestion."""
        from midi_markdown.utils.validation import Validator

        with pytest.raises(ValidationError) as exc_info:
            Validator.validate_note(200)

        error = exc_info.value
        assert error.error_code == "E205"
        assert error.suggestion is not None
        assert "0-127" in error.suggestion

    def test_velocity_validator_suggestion(self):
        """Test velocity validator provides helpful suggestion."""
        from midi_markdown.utils.validation import Validator

        with pytest.raises(ValidationError) as exc_info:
            Validator.validate_velocity(200)

        error = exc_info.value
        assert error.error_code == "E206"
        assert error.suggestion is not None

    def test_cc_controller_validator_suggestion(self):
        """Test CC controller validator provides helpful suggestion."""
        from midi_markdown.utils.validation import Validator

        with pytest.raises(ValidationError) as exc_info:
            Validator.validate_cc_controller(200)

        error = exc_info.value
        assert error.error_code == "E207"
        assert error.suggestion is not None

    def test_program_validator_suggestion(self):
        """Test program validator provides helpful suggestion."""
        from midi_markdown.utils.validation import Validator

        with pytest.raises(ValidationError) as exc_info:
            Validator.validate_program(200)

        error = exc_info.value
        assert error.error_code == "E209"
        assert error.suggestion is not None

    def test_pitch_bend_validator_suggestion(self):
        """Test pitch bend validator provides helpful suggestion."""
        from midi_markdown.utils.validation import Validator

        with pytest.raises(ValidationError) as exc_info:
            Validator.validate_pitch_bend(20000)  # Beyond max of 16383

        error = exc_info.value
        assert error.error_code == "E210"
        assert error.suggestion is not None

    def test_tempo_validator_suggestion(self):
        """Test tempo validator provides helpful suggestion."""
        from midi_markdown.utils.validation import Validator

        with pytest.raises(ValidationError) as exc_info:
            Validator.validate_tempo(999)

        error = exc_info.value
        assert error.error_code == "E211"
        assert error.suggestion is not None


class TestSuggestInRange:
    """Test the _suggest_in_range helper function."""

    def test_suggest_in_range_clamps_low(self):
        """Test suggestion clamps values below range."""
        from midi_markdown.utils.validation.value_validator import _suggest_in_range

        suggestion = _suggest_in_range(-5, 1, 16, "channel")
        assert "1-16" in suggestion
        assert "1" in suggestion  # Clamped value

    def test_suggest_in_range_clamps_high(self):
        """Test suggestion clamps values above range."""
        from midi_markdown.utils.validation.value_validator import _suggest_in_range

        suggestion = _suggest_in_range(200, 0, 127, "note")
        assert "0-127" in suggestion
        assert "127" in suggestion  # Clamped value

    def test_suggest_in_range_custom_label(self):
        """Test suggestion uses custom label."""
        from midi_markdown.utils.validation.value_validator import _suggest_in_range

        suggestion = _suggest_in_range(99, 1, 16, "MIDI channel")
        assert "MIDI channel" in suggestion
