"""
Integration Tests: Timing Validation

Tests for timing validation integrated with the MML parser,
validating real MML documents for timing constraints.
"""


class TestTimingValidationIntegration:
    """Integration tests for timing validation with parser."""

    # ============================================
    # Absolute Timing Tests
    # ============================================

    def test_valid_absolute_timing(self, parser, validator):
        """Test that valid absolute timing passes validation."""
        source = """---
title: Test
---

[00:00.000]
- pc 1.0

[00:01.500]
- pc 1.1

[00:05.000]
- pc 1.2
"""
        doc = parser.parse_string(source)
        errors = validator.validate(doc)
        assert len(errors) == 0

    def test_non_monotonic_absolute_timing_detected(self, parser, validator):
        """Test that non-monotonic absolute timing is detected."""
        source = """---
title: Test
---

[00:10.000]
- pc 1.0

[00:05.000]
- pc 1.1
"""
        doc = parser.parse_string(source)
        errors = validator.validate(doc)

        assert len(errors) > 0
        assert any("before previous event" in str(e) for e in errors)
        assert any("monotonically increasing" in str(e) for e in errors)

    def test_same_absolute_time_valid(self, parser, validator):
        """Test that events at same absolute time are valid."""
        source = """---
title: Test
---

[00:01.000]
- pc 1.0

[00:01.000]
- cc 1.7.100
"""
        doc = parser.parse_string(source)
        errors = validator.validate(doc)
        assert len(errors) == 0

    # ============================================
    # Musical Timing Tests
    # ============================================

    def test_musical_timing_with_metadata_valid(self, parser, validator):
        """Test that musical timing with tempo and time_signature is valid."""
        source = """---
title: Test
tempo: 120
time_signature: 4/4
---

[1.1.0]
- pc 1.0

[2.1.0]
- pc 1.1

[4.3.240]
- pc 1.2
"""
        doc = parser.parse_string(source)
        errors = validator.validate(doc)
        assert len(errors) == 0

    def test_musical_timing_without_tempo_detected(self, parser, validator):
        """Test that musical timing without tempo is detected."""
        source = """---
title: Test
time_signature: 4/4
---

[1.1.0]
- pc 1.0
"""
        doc = parser.parse_string(source)
        errors = validator.validate(doc)

        assert len(errors) > 0
        assert any("tempo" in str(e).lower() for e in errors)

    def test_musical_timing_without_time_signature_detected(self, parser, validator):
        """Test that musical timing without time_signature is detected."""
        source = """---
title: Test
tempo: 120
---

[1.1.0]
- pc 1.0
"""
        doc = parser.parse_string(source)
        errors = validator.validate(doc)

        assert len(errors) > 0
        assert any("time_signature" in str(e).lower() for e in errors)

    def test_musical_timing_without_metadata_detected(self, parser, validator):
        """Test that musical timing without metadata produces multiple errors."""
        source = """---
title: Test
---

[1.1.0]
- pc 1.0

[2.1.0]
- pc 1.1
"""
        doc = parser.parse_string(source)
        errors = validator.validate(doc)

        # Should have 2 errors per musical time event (tempo + time_sig)
        assert len(errors) == 4
        assert sum(1 for e in errors if "tempo" in str(e).lower()) == 2
        assert sum(1 for e in errors if "time_signature" in str(e).lower()) == 2

    # ============================================
    # Relative Timing Tests
    # ============================================

    def test_relative_timing_after_absolute_valid(self, parser, validator):
        """Test that relative timing after absolute timing is valid."""
        source = """---
title: Test
---

[00:00.000]
- pc 1.0

[+1b]
- pc 1.1

[+500ms]
- pc 1.2

[+0.5s]
- pc 1.3
"""
        doc = parser.parse_string(source)
        errors = validator.validate(doc)
        assert len(errors) == 0

    def test_relative_timing_at_start_detected(self, parser, validator):
        """Test that relative timing at start of document is detected."""
        source = """---
title: Test
---

[+1b]
- pc 1.0
"""
        doc = parser.parse_string(source)
        errors = validator.validate(doc)

        assert len(errors) > 0
        assert any("requires a previous event" in str(e) for e in errors)

    def test_consecutive_relative_timing_valid(self, parser, validator):
        """Test that consecutive relative timings are valid."""
        source = """---
title: Test
---

[00:00.000]
- pc 1.0

[+1b]
- pc 1.1

[+1b]
- pc 1.2

[+1b]
- pc 1.3
"""
        doc = parser.parse_string(source)
        errors = validator.validate(doc)
        assert len(errors) == 0

    # ============================================
    # Simultaneous Timing Tests
    # ============================================

    def test_simultaneous_timing_valid(self, parser, validator):
        """Test that simultaneous timing after event is valid."""
        source = """---
title: Test
---

[00:00.000]
- pc 1.0

[@]
- cc 1.7.100

[@]
- note_on 1.C4 100
"""
        doc = parser.parse_string(source)
        errors = validator.validate(doc)
        assert len(errors) == 0

    def test_simultaneous_timing_at_start_detected(self, parser, validator):
        """Test that simultaneous timing at start is detected."""
        source = """---
title: Test
---

[@]
- pc 1.0
"""
        doc = parser.parse_string(source)
        errors = validator.validate(doc)

        assert len(errors) > 0
        assert any("requires a previous event" in str(e) for e in errors)

    # ============================================
    # Mixed Timing Tests
    # ============================================

    def test_mixed_timing_types_valid(self, parser, validator):
        """Test that mixing timing types works correctly."""
        source = """---
title: Test
tempo: 120
time_signature: 4/4
---

[00:00.000]
- pc 1.0

[+1b]
- pc 1.1

[@]
- cc 1.7.100

[00:05.000]
- pc 1.2

[1.1.0]
- pc 1.3

[+500ms]
- pc 1.4
"""
        doc = parser.parse_string(source)
        errors = validator.validate(doc)
        assert len(errors) == 0

    def test_multiple_timing_violations(self, parser, validator):
        """Test that multiple timing violations are all detected."""
        source = """---
title: Test
---

[@]
- pc 1.0

[+1b]
- pc 1.1

[1.1.0]
- pc 1.2

[00:10.000]
- pc 1.3

[00:05.000]
- pc 1.4
"""
        doc = parser.parse_string(source)
        errors = validator.validate(doc)

        # Should detect:
        # - Simultaneous at start
        # - Relative at start (after simultaneous which has no previous)
        # - Musical without tempo
        # - Musical without time_sig
        # - Non-monotonic (10s -> 5s)
        assert len(errors) >= 4

    # ============================================
    # Real-World Scenarios
    # ============================================

    def test_song_with_intro_and_verses(self, parser, validator):
        """Test realistic song structure with multiple sections."""
        source = """---
title: Song Structure Test
tempo: 128
time_signature: 4/4
---

# Intro
[00:00.000]
- pc 1.0

[@]
- cc 1.7.127

# Verse 1
[00:08.000]
- pc 1.1

[+4b]
- cc 1.11.100

# Chorus
[00:32.000]
- pc 1.2

[+8b]
- pc 1.3
"""
        doc = parser.parse_string(source)
        errors = validator.validate(doc)
        assert len(errors) == 0

    def test_live_performance_preset_changes(self, parser, validator):
        """Test realistic live performance preset changes."""
        source = """---
title: Live Performance
---

# Song 1
[00:00.000]
- pc 1.0

# Song 2
[03:45.000]
- pc 1.1

# Song 3
[07:30.000]
- pc 1.2

# Song 4
[11:15.000]
- pc 1.3
"""
        doc = parser.parse_string(source)
        errors = validator.validate(doc)
        assert len(errors) == 0

    # ============================================
    # Edge Cases
    # ============================================

    def test_empty_document_valid(self, parser, validator):
        """Test that empty document is valid."""
        source = """---
title: Empty
---
"""
        doc = parser.parse_string(source)
        errors = validator.validate(doc)
        assert len(errors) == 0

    def test_document_without_frontmatter_valid(self, parser, validator):
        """Test that document without frontmatter is valid (if using absolute time)."""
        source = """
[00:00.000]
- pc 1.0

[00:01.000]
- pc 1.1
"""
        doc = parser.parse_string(source)
        errors = validator.validate(doc)
        assert len(errors) == 0

    def test_zero_time_events_valid(self, parser, validator):
        """Test that multiple events at time zero are valid."""
        source = """---
title: Test
---

[00:00.000]
- pc 1.0

[00:00.000]
- cc 1.7.100

[00:00.000]
- note_on 1.C4 100
"""
        doc = parser.parse_string(source)
        errors = validator.validate(doc)
        assert len(errors) == 0
