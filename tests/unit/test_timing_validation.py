"""
Unit Tests: Timing Validation

Tests for TimingValidator class that validates timing constraints
in MML documents including monotonicity, musical time requirements,
and relative timing constraints.
"""

from midi_markdown.parser.ast_nodes import Timing


class TestTimingValidatorBasics:
    """Test basic timing validator functionality."""

    def test_validator_initialization(self, validator):
        """Test TimingValidator initializes correctly."""
        assert validator.errors == []
        assert validator.last_absolute_time is None
        assert validator.has_tempo is False
        assert validator.has_time_signature is False

    def test_validate_resets_state(self, validator):
        """Test that validate() resets state between calls."""

        # Create a mock document with no events
        class MockDoc:
            events = []
            frontmatter = None

        # First validation
        validator.last_absolute_time = 100.0
        validator.has_tempo = True
        validator.validate(MockDoc())

        # State should be reset
        assert validator.last_absolute_time is None
        assert validator.has_tempo is False


class TestAbsoluteTimingValidation:
    """Test validation of absolute timing monotonicity."""

    def test_monotonic_increasing_valid(self, validator):
        """Test that monotonically increasing absolute times are valid."""

        class MockDoc:
            events = [
                {"timing": Timing(type="absolute", value=0.0, raw="[00:00.000]")},
                {"timing": Timing(type="absolute", value=1.5, raw="[00:01.500]")},
                {"timing": Timing(type="absolute", value=3.0, raw="[00:03.000]")},
            ]
            frontmatter = None

        errors = validator.validate(MockDoc())
        assert len(errors) == 0

    def test_same_time_valid(self, validator):
        """Test that same time (simultaneous but absolute) is valid."""

        class MockDoc:
            events = [
                {"timing": Timing(type="absolute", value=1.0, raw="[00:01.000]")},
                {"timing": Timing(type="absolute", value=1.0, raw="[00:01.000]")},
            ]
            frontmatter = None

        errors = validator.validate(MockDoc())
        assert len(errors) == 0

    def test_non_monotonic_detected(self, validator):
        """Test that non-monotonic timing is detected."""

        class MockDoc:
            events = [
                {"timing": Timing(type="absolute", value=10.0, raw="[00:10.000]")},
                {"timing": Timing(type="absolute", value=5.0, raw="[00:05.000]")},
            ]
            frontmatter = None

        errors = validator.validate(MockDoc())
        assert len(errors) == 1
        assert "before previous event" in str(errors[0])
        assert "monotonically increasing" in str(errors[0])

    def test_time_formatting(self, validator):
        """Test that time formatting works correctly."""
        formatted = validator._format_time(90.5)
        assert formatted == "01:30.500"

        formatted = validator._format_time(0.123)
        assert formatted == "00:00.123"

        formatted = validator._format_time(125.999)
        assert formatted == "02:05.999"


class TestMusicalTimingValidation:
    """Test validation of musical timing requirements."""

    def test_musical_time_without_tempo(self, validator):
        """Test that musical time without tempo is invalid."""

        class MockDoc:
            events = [
                {"timing": Timing(type="musical", value=(1, 1, 0), raw="[1.1.0]")},
            ]
            frontmatter = {"time_signature": "4/4"}

        errors = validator.validate(MockDoc())
        assert len(errors) == 1
        assert "tempo" in str(errors[0]).lower()

    def test_musical_time_without_time_signature(self, validator):
        """Test that musical time without time signature is invalid."""

        class MockDoc:
            events = [
                {"timing": Timing(type="musical", value=(1, 1, 0), raw="[1.1.0]")},
            ]
            frontmatter = {"tempo": 120}

        errors = validator.validate(MockDoc())
        assert len(errors) == 1
        assert "time_signature" in str(errors[0]).lower()

    def test_musical_time_without_either(self, validator):
        """Test that musical time without tempo or time_signature produces 2 errors."""

        class MockDoc:
            events = [
                {"timing": Timing(type="musical", value=(1, 1, 0), raw="[1.1.0]")},
            ]
            frontmatter = None

        errors = validator.validate(MockDoc())
        assert len(errors) == 2
        assert any("tempo" in str(e).lower() for e in errors)
        assert any("time_signature" in str(e).lower() for e in errors)

    def test_musical_time_with_both_valid(self, validator):
        """Test that musical time with tempo and time_signature is valid."""

        class MockDoc:
            events = [
                {"timing": Timing(type="musical", value=(1, 1, 0), raw="[1.1.0]")},
                {"timing": Timing(type="musical", value=(2, 1, 0), raw="[2.1.0]")},
            ]
            frontmatter = {"tempo": 120, "time_signature": "4/4"}

        errors = validator.validate(MockDoc())
        assert len(errors) == 0


class TestRelativeTimingValidation:
    """Test validation of relative timing requirements."""

    def test_relative_time_at_start_invalid(self, validator):
        """Test that relative timing at start of document is invalid."""

        class MockDoc:
            events = [
                {"timing": Timing(type="relative", value=(1, "b"), raw="[+1b]")},
            ]
            frontmatter = None

        errors = validator.validate(MockDoc())
        assert len(errors) == 1
        assert "requires a previous event" in str(errors[0])

    def test_relative_time_after_event_valid(self, validator):
        """Test that relative timing after an event is valid."""

        class MockDoc:
            events = [
                {"timing": Timing(type="absolute", value=0.0, raw="[00:00.000]")},
                {"timing": Timing(type="relative", value=(1, "b"), raw="[+1b]")},
            ]
            frontmatter = None

        errors = validator.validate(MockDoc())
        assert len(errors) == 0

    def test_multiple_relative_times_valid(self, validator):
        """Test that multiple consecutive relative times are valid."""

        class MockDoc:
            events = [
                {"timing": Timing(type="absolute", value=0.0, raw="[00:00.000]")},
                {"timing": Timing(type="relative", value=(500, "ms"), raw="[+500ms]")},
                {"timing": Timing(type="relative", value=(1, "b"), raw="[+1b]")},
            ]
            frontmatter = None

        errors = validator.validate(MockDoc())
        assert len(errors) == 0


class TestSimultaneousTimingValidation:
    """Test validation of simultaneous timing requirements."""

    def test_simultaneous_at_start_invalid(self, validator):
        """Test that simultaneous timing at start is invalid."""

        class MockDoc:
            events = [
                {"timing": Timing(type="simultaneous", value=None, raw="[@]")},
            ]
            frontmatter = None

        errors = validator.validate(MockDoc())
        assert len(errors) == 1
        assert "requires a previous event" in str(errors[0])

    def test_simultaneous_after_event_valid(self, validator):
        """Test that simultaneous timing after event is valid."""

        class MockDoc:
            events = [
                {"timing": Timing(type="absolute", value=0.0, raw="[00:00.000]")},
                {"timing": Timing(type="simultaneous", value=None, raw="[@]")},
            ]
            frontmatter = None

        errors = validator.validate(MockDoc())
        assert len(errors) == 0

    def test_multiple_simultaneous_valid(self, validator):
        """Test that multiple simultaneous timings are valid."""

        class MockDoc:
            events = [
                {"timing": Timing(type="absolute", value=1.0, raw="[00:01.000]")},
                {"timing": Timing(type="simultaneous", value=None, raw="[@]")},
                {"timing": Timing(type="simultaneous", value=None, raw="[@]")},
                {"timing": Timing(type="simultaneous", value=None, raw="[@]")},
            ]
            frontmatter = None

        errors = validator.validate(MockDoc())
        assert len(errors) == 0


class TestMixedTimingValidation:
    """Test validation with mixed timing types."""

    def test_mixed_timing_types_valid(self, validator):
        """Test that mixing timing types works correctly."""

        class MockDoc:
            events = [
                {"timing": Timing(type="absolute", value=0.0, raw="[00:00.000]")},
                {"timing": Timing(type="relative", value=(1, "b"), raw="[+1b]")},
                {"timing": Timing(type="simultaneous", value=None, raw="[@]")},
                {"timing": Timing(type="absolute", value=5.0, raw="[00:05.000]")},
            ]
            frontmatter = None

        errors = validator.validate(MockDoc())
        assert len(errors) == 0

    def test_multiple_violations(self, validator):
        """Test that multiple violations are all collected."""

        class MockDoc:
            events = [
                {"timing": Timing(type="relative", value=(1, "b"), raw="[+1b]")},  # No previous
                {"timing": Timing(type="musical", value=(1, 1, 0), raw="[1.1.0]")},  # No tempo/sig
                {"timing": Timing(type="absolute", value=10.0, raw="[00:10.000]")},
                {"timing": Timing(type="absolute", value=5.0, raw="[00:05.000]")},  # Goes back
            ]
            frontmatter = None

        errors = validator.validate(MockDoc())
        # Should have: 1 relative, 2 musical (tempo + time_sig), 1 monotonic = 4 errors
        assert len(errors) == 4

    def test_events_without_timing_skipped(self, validator):
        """Test that events without timing are safely skipped."""

        class MockDoc:
            events = [
                {"timing": Timing(type="absolute", value=0.0, raw="[00:00.000]")},
                {"commands": []},  # Event without timing
                {"timing": Timing(type="absolute", value=1.0, raw="[00:01.000]")},
            ]
            frontmatter = None

        errors = validator.validate(MockDoc())
        assert len(errors) == 0


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_document(self, validator):
        """Test that empty document is valid."""

        class MockDoc:
            events = []
            frontmatter = None

        errors = validator.validate(MockDoc())
        assert len(errors) == 0

    def test_single_event_always_valid(self, validator):
        """Test that single event is always valid."""

        class MockDoc:
            events = [
                {"timing": Timing(type="absolute", value=99.9, raw="[01:39.900]")},
            ]
            frontmatter = None

        errors = validator.validate(MockDoc())
        assert len(errors) == 0

    def test_section_headers_skipped(self, validator):
        """Test that non-event tokens like section headers are skipped."""
        from lark import Token

        class MockDoc:
            events = [
                Token("SECTION_HEADER", "## Track: Lead"),
                {"timing": Timing(type="absolute", value=0.0, raw="[00:00.000]")},
                Token("SECTION_HEADER", "## Track: Bass"),
                {"timing": Timing(type="absolute", value=1.0, raw="[00:01.000]")},
            ]
            frontmatter = None

        errors = validator.validate(MockDoc())
        assert len(errors) == 0

    def test_zero_time_valid(self, validator):
        """Test that time zero is valid."""

        class MockDoc:
            events = [
                {"timing": Timing(type="absolute", value=0.0, raw="[00:00.000]")},
                {"timing": Timing(type="absolute", value=0.0, raw="[00:00.000]")},
            ]
            frontmatter = None

        errors = validator.validate(MockDoc())
        assert len(errors) == 0

    def test_very_large_time_valid(self, validator):
        """Test that very large times are valid."""

        class MockDoc:
            events = [
                {"timing": Timing(type="absolute", value=0.0, raw="[00:00.000]")},
                {"timing": Timing(type="absolute", value=999999.0, raw="[16666:39.000]")},
            ]
            frontmatter = None

        errors = validator.validate(MockDoc())
        assert len(errors) == 0
