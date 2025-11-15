"""Unit tests for validation utilities."""

import pytest

from midi_markdown.utils.validation import ValidationError, Validator


class TestValidator:
    """Test the Validator class methods."""

    # ============================================
    # validate_midi_value tests
    # ============================================

    @pytest.mark.parametrize(
        ("value", "min_val", "max_val"),
        [
            (0, 0, 127),  # Default range min
            (64, 0, 127),  # Default range mid
            (127, 0, 127),  # Default range max
            (5, 0, 10),  # Custom range mid
            (0, 0, 10),  # Custom range min
            (10, 0, 10),  # Custom range max
        ],
    )
    def test_validate_midi_value_valid(self, value, min_val, max_val):
        """Test valid MIDI values pass validation."""
        Validator.validate_midi_value(value, min_val=min_val, max_val=max_val)
        # Should not raise

    @pytest.mark.parametrize(
        ("value", "min_val", "max_val", "error_match"),
        [
            (-1, 0, 127, "out of range"),  # Below default range
            (128, 0, 127, "out of range"),  # Above default range
            (255, 0, 127, "out of range"),  # Way above default range
            (11, 0, 10, "out of range"),  # Above custom range
            (-1, 0, 10, "out of range"),  # Below custom range
            (64.5, 0, 127, "must be an integer"),  # Float value
            ("64", 0, 127, "must be an integer"),  # String value
        ],
    )
    def test_validate_midi_value_invalid(self, value, min_val, max_val, error_match):
        """Test invalid MIDI values raise ValidationError."""
        with pytest.raises(ValidationError, match=error_match):
            Validator.validate_midi_value(value, min_val=min_val, max_val=max_val)

    # ============================================
    # validate_channel tests
    # ============================================

    @pytest.mark.parametrize(
        "value",
        [
            1,  # Min valid channel
            8,  # Mid channel
            16,  # Max valid channel
        ],
    )
    def test_validate_channel_valid(self, value):
        """Test valid channels pass validation."""
        Validator.validate_channel(value)
        # Should not raise

    @pytest.mark.parametrize(
        ("value", "error_match"),
        [
            (0, "out of range"),  # Below range
            (17, "out of range"),  # Above range
            (-1, "out of range"),  # Negative
            (1.5, "must be an integer"),  # Float
            ("1", "must be an integer"),  # String
        ],
    )
    def test_validate_channel_invalid(self, value, error_match):
        """Test invalid channels raise ValidationError."""
        with pytest.raises(ValidationError, match=error_match):
            Validator.validate_channel(value)

    # ============================================
    # validate_note tests
    # ============================================

    @pytest.mark.parametrize(
        ("note", "expected"),
        [
            (0, 0),  # Min note number
            (60, 60),  # Middle C
            (127, 127),  # Max note number
            ("C4", 60),  # Note name natural
            ("C#4", 61),  # Note name sharp
            ("Db4", 61),  # Note name flat
            ("A0", 21),  # Low note
            ("G9", 127),  # High note
        ],
    )
    def test_validate_note_valid(self, note, expected):
        """Test valid note numbers and names pass validation."""
        assert Validator.validate_note(note) == expected

    @pytest.mark.parametrize(
        ("note", "error_match"),
        [
            (-1, "out of range"),  # Below range
            (128, "out of range"),  # Above range
            ("H4", "Invalid note name"),  # Invalid note letter
            ("C10", "Invalid note name"),  # Invalid octave
            (60.5, "must be string or integer"),  # Float
            ([60], "must be string or integer"),  # List
        ],
    )
    def test_validate_note_invalid(self, note, error_match):
        """Test invalid notes raise ValidationError."""
        with pytest.raises(ValidationError, match=error_match):
            Validator.validate_note(note)

    # ============================================
    # validate_velocity tests
    # ============================================

    @pytest.mark.parametrize(
        "value",
        [
            0,  # Min velocity
            64,  # Mid velocity
            127,  # Max velocity
        ],
    )
    def test_validate_velocity_valid(self, value):
        """Test valid velocities pass validation."""
        Validator.validate_velocity(value)
        # Should not raise

    @pytest.mark.parametrize(
        ("value", "error_match"),
        [
            (-1, "out of range"),  # Below range
            (128, "out of range"),  # Above range
            (255, "out of range"),  # Way above range
            (64.5, "must be an integer"),  # Float
        ],
    )
    def test_validate_velocity_invalid(self, value, error_match):
        """Test invalid velocities raise ValidationError."""
        with pytest.raises(ValidationError, match=error_match):
            Validator.validate_velocity(value)

    # ============================================
    # validate_cc_controller tests
    # ============================================

    @pytest.mark.parametrize(
        "value",
        [
            0,  # Min controller
            7,  # Volume controller
            127,  # Max controller
        ],
    )
    def test_validate_cc_controller_valid(self, value):
        """Test valid CC controller numbers pass validation."""
        Validator.validate_cc_controller(value)
        # Should not raise

    @pytest.mark.parametrize(
        ("value", "error_match"),
        [
            (-1, "out of range"),  # Below range
            (128, "out of range"),  # Above range
        ],
    )
    def test_validate_cc_controller_invalid(self, value, error_match):
        """Test out of range CC controllers raise ValidationError."""
        with pytest.raises(ValidationError, match=error_match):
            Validator.validate_cc_controller(value)

    # ============================================
    # validate_cc_value tests
    # ============================================

    @pytest.mark.parametrize(
        "value",
        [
            0,  # Min value
            64,  # Mid value
            127,  # Max value
        ],
    )
    def test_validate_cc_value_valid(self, value):
        """Test valid CC values pass validation."""
        Validator.validate_cc_value(value)
        # Should not raise

    @pytest.mark.parametrize(
        ("value", "error_match"),
        [
            (-1, "out of range"),  # Below range
            (128, "out of range"),  # Above range
            (255, "out of range"),  # Way above range
            (64.5, "must be an integer"),  # Float
        ],
    )
    def test_validate_cc_value_invalid(self, value, error_match):
        """Test non-integer CC values raise ValidationError."""
        with pytest.raises(ValidationError, match=error_match):
            Validator.validate_cc_value(value)

    # ============================================
    # validate_program tests
    # ============================================

    @pytest.mark.parametrize(
        "value",
        [
            0,  # Min program
            64,  # Mid program
            127,  # Max program
        ],
    )
    def test_validate_program_valid(self, value):
        """Test valid program numbers pass validation."""
        Validator.validate_program(value)
        # Should not raise

    @pytest.mark.parametrize(
        ("value", "error_match"),
        [
            (-1, "out of range"),  # Below range
            (128, "out of range"),  # Above range
        ],
    )
    def test_validate_program_invalid(self, value, error_match):
        """Test out of range program numbers raise ValidationError."""
        with pytest.raises(ValidationError, match=error_match):
            Validator.validate_program(value)

    # ============================================
    # validate_pitch_bend tests
    # ============================================

    @pytest.mark.parametrize(
        "value",
        [
            -8192,  # Min pitch bend (signed notation)
            0,  # Center (signed notation)
            8191,  # Max pitch bend (signed notation)
            8192,  # Center (unsigned notation)
            16383,  # Max pitch bend (unsigned notation)
        ],
    )
    def test_validate_pitch_bend_valid(self, value):
        """Test valid pitch bend values pass validation."""
        Validator.validate_pitch_bend(value)
        # Should not raise

    @pytest.mark.parametrize(
        ("value", "error_match"),
        [
            (-8193, "out of range"),  # Below range
            (
                16384,
                "out of range",
            ),  # Above range (was 8192, but that's valid now in unsigned notation)
            (0.5, "must be an integer"),  # Float
        ],
    )
    def test_validate_pitch_bend_invalid(self, value, error_match):
        """Test invalid pitch bend values raise ValidationError."""
        with pytest.raises(ValidationError, match=error_match):
            Validator.validate_pitch_bend(value)

    # ============================================
    # validate_tempo tests
    # ============================================

    @pytest.mark.parametrize(
        "value",
        [
            1,  # Min tempo
            120,  # Standard tempo
            300,  # Max tempo
            120.5,  # Float is allowed
        ],
    )
    def test_validate_tempo_valid(self, value):
        """Test valid tempos pass validation."""
        Validator.validate_tempo(value)
        # Should not raise

    @pytest.mark.parametrize(
        ("value", "error_match"),
        [
            (0, "out of range"),  # Zero
            (301, "out of range"),  # Above max
            (-10, "out of range"),  # Negative
            ("120", "must be a number"),  # String
        ],
    )
    def test_validate_tempo_invalid(self, value, error_match):
        """Test invalid tempos raise ValidationError."""
        with pytest.raises(ValidationError, match=error_match):
            Validator.validate_tempo(value)


class TestValidationError:
    """Test the ValidationError class."""

    def test_error_message_only(self):
        """Test error with message only."""
        error = ValidationError("Test error")
        assert str(error) == "Test error"
        assert error.message == "Test error"
        assert error.line is None
        assert error.column is None

    def test_error_with_line(self):
        """Test error with line number."""
        error = ValidationError("Test error", line=10)
        assert str(error) == "Line 10: Test error"
        assert error.message == "Test error"
        assert error.line == 10
        assert error.column is None

    def test_error_with_line_and_column(self):
        """Test error with line and column."""
        error = ValidationError("Test error", line=10, column=5)
        assert str(error) == "Line 10:5: Test error"
        assert error.message == "Test error"
        assert error.line == 10
        assert error.column == 5
