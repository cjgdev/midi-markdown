"""
Test Suite: Timing

Tests for all MML timing paradigms including absolute, musical, relative,
and simultaneous timing, plus comprehensive edge cases.
"""

import pytest


class TestTimingBasics:
    """Test basic timing functionality"""

    # ========================================================================
    # Absolute Timing Tests
    # ========================================================================

    def test_absolute_timing(self, parser):
        """Test absolute timing format [mm:ss.mmm]"""
        mml = """
[00:00.000]
- pc 1.0
[00:01.500]
- pc 1.1
[01:30.250]
- pc 1.2
"""
        doc = parser.parse_string(mml)
        assert len(doc.events) == 3
        assert doc.events[0]["timing"].type == "absolute"
        assert doc.events[0]["timing"].value == 0.0
        assert doc.events[1]["timing"].value == 1.5
        assert abs(doc.events[2]["timing"].value - 90.25) < 0.01

    # ========================================================================
    # Musical Timing Tests
    # ========================================================================

    def test_musical_timing(self, parser):
        """Test musical timing format [bars.beats.ticks]"""
        mml = """
[1.1.0]
- pc 1.0
[2.3.120]
- pc 1.1
[4.4.0]
- pc 1.2
"""
        doc = parser.parse_string(mml)
        assert len(doc.events) == 3
        assert doc.events[0]["timing"].type == "musical"
        assert doc.events[0]["timing"].value == (1, 1, 0)
        assert doc.events[1]["timing"].value == (2, 3, 120)
        assert doc.events[2]["timing"].value == (4, 4, 0)

    # ========================================================================
    # Relative Timing Tests
    # ========================================================================

    def test_relative_timing(self, parser):
        """Test relative timing with various units"""
        mml = """
[00:00.000]
- pc 1.0
[+1b]
- pc 1.1
[+500ms]
- pc 1.2
[+0.5s]
- pc 1.3
"""
        doc = parser.parse_string(mml)
        assert len(doc.events) == 4
        assert doc.events[1]["timing"].type == "relative"
        assert doc.events[1]["timing"].value == (1, "b")
        assert doc.events[2]["timing"].value == (500, "ms")
        assert doc.events[3]["timing"].value == (0.5, "s")

    # ========================================================================
    # Simultaneous Timing Tests
    # ========================================================================

    def test_simultaneous_timing(self, parser):
        """Test simultaneous timing [@]"""
        mml = """
[00:00.000]
- pc 1.0
[@]
- cc 1.7.100
[@]
- note_on 1.60 100
"""
        doc = parser.parse_string(mml)
        assert len(doc.events) == 3
        assert doc.events[0]["timing"].type == "absolute"
        assert doc.events[1]["timing"].type == "simultaneous"
        assert doc.events[2]["timing"].type == "simultaneous"


class TestTimingEdgeCases:
    """Test timing edge cases and boundary values"""

    # ========================================================================
    # Absolute Timing Edge Cases
    # ========================================================================

    @pytest.mark.parametrize(
        ("time_str", "expected"),
        [
            ("00:00.000", 0.0),  # Minimum time value
            ("00:00.001", 0.001),  # Minimum fractional
            ("00:00.500", 0.500),  # Mid fractional
            ("00:00.999", 0.999),  # Max fractional
            ("99:59.999", 99 * 60 + 59.999),  # Very large time
        ],
    )
    def test_absolute_edge_cases(self, parser, time_str, expected):
        """Test absolute timing edge cases and boundary values"""
        mml = f"[{time_str}]\n- pc 1.0\n"
        doc = parser.parse_string(mml)
        assert len(doc.events) == 1
        assert abs(doc.events[0]["timing"].value - expected) < 0.001

    # ========================================================================
    # Musical Timing Edge Cases
    # ========================================================================

    @pytest.mark.parametrize(
        ("time_str", "expected"),
        [
            ("1.1.0", (1, 1, 0)),  # First bar, first beat
            ("1.1.479", (1, 1, 479)),  # Max tick boundary-1
            ("1.1.480", (1, 1, 480)),  # Max tick boundary
            ("100.4.480", (100, 4, 480)),  # Large bar number
        ],
    )
    def test_musical_edge_cases(self, parser, time_str, expected):
        """Test musical timing edge cases and boundary values"""
        mml = f"[{time_str}]\n- pc 1.0\n"
        doc = parser.parse_string(mml)
        assert len(doc.events) == 1
        assert doc.events[0]["timing"].value == expected

    # ========================================================================
    # Relative Timing Edge Cases
    # ========================================================================

    @pytest.mark.parametrize(
        ("offset", "expected"),
        [
            ("0b", (0, "b")),  # Zero beat offset
            ("0s", (0, "s")),  # Zero second offset
            ("0ms", (0, "ms")),  # Zero millisecond offset
            ("1000b", (1000, "b")),  # Large beat offset
            ("9999s", (9999, "s")),  # Large second offset
            ("0.5s", (0.5, "s")),  # Fractional second offset
        ],
    )
    def test_relative_edge_cases(self, parser, offset, expected):
        """Test relative timing edge cases and boundary values"""
        mml = f"[00:00.000]\n- pc 1.0\n[+{offset}]\n- pc 1.1\n"
        doc = parser.parse_string(mml)
        assert len(doc.events) == 2
        assert doc.events[1]["timing"].value == expected

    def test_relative_musical_time(self, parser):
        """Test [+2.1.0] - relative musical time offset

        Relative musical time uses [+bars.beats.ticks] format.
        This is now properly supported in both grammar and transformer.
        """
        mml = """[1.1.0]
- pc 1.0
[+2.1.0]
- pc 1.1
"""
        doc = parser.parse_string(mml)
        assert len(doc.events) == 2
        assert doc.events[1]["timing"].value == (2, 1, 0)

    # ========================================================================
    # Simultaneous Timing Edge Cases
    # ========================================================================

    def test_multiple_simultaneous_events(self, parser):
        """Test multiple [@] events in sequence"""
        mml = """[00:00.000]
- pc 1.0
[@]
- cc 1.7.100
[@]
- cc 1.11.127
[@]
- note_on 1.60 100
"""
        doc = parser.parse_string(mml)
        assert len(doc.events) == 4
        assert doc.events[1]["timing"].type == "simultaneous"
        assert doc.events[2]["timing"].type == "simultaneous"
        assert doc.events[3]["timing"].type == "simultaneous"


class TestTimingMixedUsage:
    """Test mixed usage of different timing paradigms"""

    def test_mixed_timing_paradigms(self, parser):
        """Test using all timing types in one document"""
        mml = """[00:00.000]
- pc 1.0
[1.1.0]
- pc 1.1
[+1b]
- pc 1.2
[@]
- cc 1.7.100
[00:05.000]
- pc 1.3
"""
        doc = parser.parse_string(mml)
        assert len(doc.events) == 5
        assert doc.events[0]["timing"].type == "absolute"
        assert doc.events[1]["timing"].type == "musical"
        assert doc.events[2]["timing"].type == "relative"
        assert doc.events[3]["timing"].type == "simultaneous"
        assert doc.events[4]["timing"].type == "absolute"
