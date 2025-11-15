"""Integration tests for document validation."""

from pathlib import Path

import pytest

from midi_markdown.utils.validation import DocumentValidator


class TestDocumentValidation:
    """Test document-level validation."""

    @pytest.fixture
    def validator(self):
        """Create document validator instance."""
        return DocumentValidator()

    @pytest.fixture
    def fixtures_dir(self):
        """Get fixtures directory."""
        return Path(__file__).parent.parent / "fixtures"

    # ============================================
    # Valid Document Tests
    # ============================================

    def test_valid_document_no_errors(self, parser, validator, fixtures_dir):
        """Test that a valid document produces no validation errors."""
        fixture = fixtures_dir / "valid" / "basic.mmd"
        doc = parser.parse_file(fixture)

        errors = validator.validate(doc)

        assert len(errors) == 0, f"Expected no errors, got: {[str(e) for e in errors]}"

    # ============================================
    # Invalid Channel Tests
    # ============================================

    def test_invalid_channel_detected(self, parser, validator, fixtures_dir):
        """Test that invalid channel (17) is detected."""
        fixture = fixtures_dir / "invalid" / "invalid_channel.mmd"
        doc = parser.parse_file(fixture)

        errors = validator.validate(doc)

        assert len(errors) > 0, "Expected validation errors for invalid channel"
        assert any("Channel" in str(e) and "out of range" in str(e) for e in errors), (
            f"Expected channel range error, got: {[str(e) for e in errors]}"
        )

    def test_channel_zero_detected(self, parser, validator):
        """Test that channel 0 is detected as invalid."""
        source = """---
title: Test
---

[00:00.000]
- note_on 0.C4 100 500ms
"""
        doc = parser.parse_string(source)
        errors = validator.validate(doc)

        assert len(errors) > 0
        assert any("Channel" in str(e) and "out of range" in str(e) for e in errors)

    # ============================================
    # Invalid Velocity Tests
    # ============================================

    def test_invalid_velocity_detected(self, parser, validator, fixtures_dir):
        """Test that invalid velocity (200) is detected."""
        fixture = fixtures_dir / "invalid" / "invalid_velocity.mmd"
        doc = parser.parse_file(fixture)

        errors = validator.validate(doc)

        assert len(errors) > 0, "Expected validation errors for invalid velocity"
        assert any("Velocity" in str(e) and "out of range" in str(e) for e in errors), (
            f"Expected velocity range error, got: {[str(e) for e in errors]}"
        )

    def test_velocity_negative_detected(self, parser, validator):
        """Test that negative velocity is detected."""
        source = """---
title: Test
---

[00:00.000]
- note_on 1.C4 -10 500ms
"""
        doc = parser.parse_string(source)
        errors = validator.validate(doc)

        assert len(errors) > 0
        assert any("Velocity" in str(e) and "out of range" in str(e) for e in errors)

    # ============================================
    # Invalid CC Value Tests
    # ============================================

    def test_invalid_cc_value_detected(self, parser, validator, fixtures_dir):
        """Test that invalid CC value (255) is detected."""
        fixture = fixtures_dir / "invalid" / "invalid_cc_value.mmd"
        doc = parser.parse_file(fixture)

        errors = validator.validate(doc)

        assert len(errors) > 0, "Expected validation errors for invalid CC value"
        assert any("CC value" in str(e) and "out of range" in str(e) for e in errors), (
            f"Expected CC value range error, got: {[str(e) for e in errors]}"
        )

    def test_invalid_cc_controller_detected(self, parser, validator):
        """Test that invalid CC controller number is detected."""
        source = """---
title: Test
---

[00:00.000]
- cc 1.128.64
"""
        doc = parser.parse_string(source)
        errors = validator.validate(doc)

        assert len(errors) > 0
        assert any("CC controller" in str(e) and "out of range" in str(e) for e in errors)

    # ============================================
    # Invalid Program Change Tests
    # ============================================

    def test_invalid_program_detected(self, parser, validator):
        """Test that invalid program number is detected."""
        source = """---
title: Test
---

[00:00.000]
- pc 1.128
"""
        doc = parser.parse_string(source)
        errors = validator.validate(doc)

        assert len(errors) > 0
        assert any("Program" in str(e) and "out of range" in str(e) for e in errors)

    # ============================================
    # Invalid Note Tests
    # ============================================

    def test_invalid_note_number_detected(self, parser, validator):
        """Test that invalid note number is detected."""
        source = """---
title: Test
---

[00:00.000]
- note_on 1.128 100 500ms
"""
        doc = parser.parse_string(source)
        errors = validator.validate(doc)

        assert len(errors) > 0
        assert any("Note" in str(e) and "out of range" in str(e) for e in errors)

    # ============================================
    # Invalid Pitch Bend Tests
    # ============================================

    def test_invalid_pitch_bend_detected(self, parser, validator):
        """Test that invalid pitch bend value is detected."""
        source = """---
title: Test
---

[00:00.000]
- pb 1.20000
"""
        doc = parser.parse_string(source)
        errors = validator.validate(doc)

        assert len(errors) > 0
        assert any("Pitch bend" in str(e) and "out of range" in str(e) for e in errors)

    # ============================================
    # Multiple Errors Tests
    # ============================================

    def test_multiple_errors_collected(self, parser, validator):
        """Test that multiple validation errors are collected."""
        source = """---
title: Test
---

[00:00.000]
- note_on 17.C4 200 500ms
- cc 1.128.255
- pc 1.130
"""
        doc = parser.parse_string(source)
        errors = validator.validate(doc)

        # Should have at least 4 errors:
        # 1. Invalid channel (17)
        # 2. Invalid velocity (200)
        # 3. Invalid CC controller (128)
        # 4. Invalid CC value (255)
        # 5. Invalid program (130)
        assert len(errors) >= 4, (
            f"Expected at least 4 errors, got {len(errors)}: {[str(e) for e in errors]}"
        )

    # ============================================
    # Line Number Tests
    # ============================================

    def test_error_includes_line_number(self, parser, validator):
        """Test that validation errors include line numbers."""
        source = """---
title: Test
---

[00:00.000]
- note_on 17.C4 100 500ms
"""
        doc = parser.parse_string(source)
        errors = validator.validate(doc)

        assert len(errors) > 0
        # At least one error should have a line number
        assert any(e.line is not None for e in errors), (
            "Expected at least one error with line number"
        )

    # ============================================
    # Track Validation Tests
    # ============================================

    def test_duplicate_track_names_detected(self, parser, validator):
        """Test that duplicate track names are detected."""
        source = """---
title: Test
---

@track Lead channel=1
[00:00.000]
- note_on 1.C4 100 500ms

@track Lead channel=1
[00:01.000]
- note_on 1.D4 100 500ms
"""
        doc = parser.parse_string(source)
        errors = validator.validate(doc)

        assert len(errors) > 0
        assert any("Duplicate track names" in str(e) for e in errors)

    # ============================================
    # Edge Cases
    # ============================================

    def test_empty_document_valid(self, parser, validator):
        """Test that an empty document is valid."""
        source = """---
title: Empty
---
"""
        doc = parser.parse_string(source)
        errors = validator.validate(doc)

        assert len(errors) == 0

    def test_document_with_only_aliases_valid(self, parser, validator):
        """Test that a document with only aliases (no events) is valid."""
        source = """---
title: Aliases Only
---

@alias test {ch} {value} "Test"
  - cc {ch}.7.{value}
@end
"""
        doc = parser.parse_string(source)
        errors = validator.validate(doc)

        assert len(errors) == 0

    def test_valid_edge_values(self, parser, validator):
        """Test that valid edge values (0, 127, etc.) pass validation."""
        source = """---
title: Edge Values
---

[00:00.000]
- note_on 1.0 0 500ms
- note_on 16.127 127 500ms
- cc 1.0.0
- cc 16.127.127
- pc 1.0
- pc 16.127
"""
        doc = parser.parse_string(source)
        errors = validator.validate(doc)

        assert len(errors) == 0, (
            f"Edge values should be valid, got errors: {[str(e) for e in errors]}"
        )
