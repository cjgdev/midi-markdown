"""Tests for Bezier curve interpolation.

This module tests the BezierCurve class and related utility functions
for creating smooth parameter transitions in MIDI automation.
"""

from __future__ import annotations

from midi_markdown.utils.curves import (
    BezierCurve,
    create_ease_in_bezier,
    create_ease_in_out_bezier,
    create_ease_out_bezier,
    create_linear_bezier,
    scale_bezier_to_range,
)


class TestBezierCurveBasics:
    """Test basic Bezier curve functionality."""

    def test_create_bezier_curve(self):
        """Test creating a Bezier curve with 4 control points."""
        curve = BezierCurve(0, 40, 90, 127)
        assert curve.p0 == 0.0
        assert curve.p1 == 40.0
        assert curve.p2 == 90.0
        assert curve.p3 == 127.0

    def test_interpolate_at_start(self):
        """Test interpolation at t=0 returns start point."""
        curve = BezierCurve(0, 40, 90, 127)
        assert curve.interpolate(0.0) == 0.0

    def test_interpolate_at_end(self):
        """Test interpolation at t=1 returns end point."""
        curve = BezierCurve(0, 40, 90, 127)
        assert curve.interpolate(1.0) == 127.0

    def test_interpolate_at_midpoint(self):
        """Test interpolation at t=0.5 gives expected midpoint value."""
        # Symmetric control points should give midpoint at t=0.5
        curve = BezierCurve(0, 42.333, 84.667, 127)
        midpoint = curve.interpolate(0.5)
        # For symmetric curves, midpoint should be close to average
        assert 62.0 < midpoint < 65.0

    def test_linear_curve(self):
        """Test that a linear curve gives linear interpolation."""
        # Control points on a straight line
        curve = BezierCurve(0, 42.333, 84.667, 127)

        # Check several points for linearity
        assert abs(curve.interpolate(0.25) - 31.75) < 1.0
        assert abs(curve.interpolate(0.5) - 63.5) < 1.0
        assert abs(curve.interpolate(0.75) - 95.25) < 1.0

    def test_repr(self):
        """Test string representation of Bezier curve."""
        curve = BezierCurve(0, 40, 90, 127)
        repr_str = repr(curve)
        assert "BezierCurve" in repr_str
        assert "p0=0.0" in repr_str
        assert "p3=127.0" in repr_str

    def test_equality(self):
        """Test Bezier curve equality comparison."""
        curve1 = BezierCurve(0, 40, 90, 127)
        curve2 = BezierCurve(0, 40, 90, 127)
        curve3 = BezierCurve(0, 30, 90, 127)

        assert curve1 == curve2
        assert curve1 != curve3
        assert curve1 != "not a curve"


class TestBezierCurveInterpolation:
    """Test Bezier curve interpolation accuracy."""

    def test_interpolate_quarter_points(self):
        """Test interpolation at t=0.25, 0.5, 0.75."""
        curve = BezierCurve(0, 40, 90, 127)

        # Values should be monotonically increasing for this curve
        v0 = curve.interpolate(0.0)
        v25 = curve.interpolate(0.25)
        v50 = curve.interpolate(0.5)
        v75 = curve.interpolate(0.75)
        v100 = curve.interpolate(1.0)

        assert v0 < v25 < v50 < v75 < v100

    def test_interpolate_many_points(self):
        """Test interpolation at many points for smoothness."""
        curve = BezierCurve(0, 40, 90, 127)

        previous = curve.interpolate(0.0)
        for i in range(1, 101):
            t = i / 100.0
            current = curve.interpolate(t)
            # Curve should be monotonically increasing
            assert current >= previous
            previous = current

    def test_interpolate_reverse_curve(self):
        """Test interpolation for a curve that goes backward (end < start)."""
        curve = BezierCurve(127, 90, 40, 0)

        assert curve.interpolate(0.0) == 127.0
        assert curve.interpolate(1.0) == 0.0

        # Values should decrease monotonically
        v0 = curve.interpolate(0.0)
        v50 = curve.interpolate(0.5)
        v100 = curve.interpolate(1.0)
        assert v0 > v50 > v100

    def test_interpolate_with_overshoot(self):
        """Test curve with control points creating overshoot."""
        # Control points create an overshoot beyond the end value
        curve = BezierCurve(0, 100, 150, 127)

        # Some intermediate values might exceed the end point
        values = [curve.interpolate(t / 10.0) for t in range(11)]
        max_value = max(values)

        # With these control points, we should see some overshoot
        # (not all intermediate values will be between 0 and 127)
        assert max_value > 127 or any(v < 0 for v in values)

    def test_interpolate_negative_values(self):
        """Test curve with negative control points."""
        curve = BezierCurve(-50, 0, 50, 100)

        assert curve.interpolate(0.0) == -50.0
        assert curve.interpolate(1.0) == 100.0


class TestBezierCurveClamping:
    """Test parameter clamping behavior."""

    def test_clamp_t_below_zero(self):
        """Test that t < 0 is clamped to 0."""
        curve = BezierCurve(0, 40, 90, 127)
        assert curve.interpolate(-0.5) == curve.interpolate(0.0)
        assert curve.interpolate(-1.0) == 0.0

    def test_clamp_t_above_one(self):
        """Test that t > 1 is clamped to 1."""
        curve = BezierCurve(0, 40, 90, 127)
        assert curve.interpolate(1.5) == curve.interpolate(1.0)
        assert curve.interpolate(2.0) == 127.0

    def test_clamp_extreme_t_values(self):
        """Test clamping with extreme t values."""
        curve = BezierCurve(0, 40, 90, 127)
        assert curve.interpolate(-1000.0) == 0.0
        assert curve.interpolate(1000.0) == 127.0


class TestPresetBezierCurves:
    """Test preset Bezier curve generators."""

    def test_create_ease_in(self):
        """Test ease-in curve creation."""
        curve = create_ease_in_bezier()

        # Should start at 0, end at 1
        assert curve.interpolate(0.0) == 0.0
        assert curve.interpolate(1.0) == 1.0

        # Should be slow at start (value < t)
        assert curve.interpolate(0.25) < 0.25
        assert curve.interpolate(0.5) < 0.5

    def test_create_ease_out(self):
        """Test ease-out curve creation."""
        curve = create_ease_out_bezier()

        # Should start at 0, end at 1
        assert curve.interpolate(0.0) == 0.0
        assert curve.interpolate(1.0) == 1.0

        # Should be fast at start (value > t)
        assert curve.interpolate(0.5) > 0.5
        assert curve.interpolate(0.75) > 0.75

    def test_create_ease_in_out(self):
        """Test ease-in-out curve creation."""
        curve = create_ease_in_out_bezier()

        # Should start at 0, end at 1
        assert curve.interpolate(0.0) == 0.0
        assert curve.interpolate(1.0) == 1.0

        # Should be symmetric around midpoint
        assert abs(curve.interpolate(0.5) - 0.5) < 0.01

    def test_create_linear(self):
        """Test linear curve creation."""
        curve = create_linear_bezier()

        # Should be exactly linear (t == value)
        for t in [0.0, 0.25, 0.5, 0.75, 1.0]:
            assert abs(curve.interpolate(t) - t) < 0.001


class TestBezierCurveScaling:
    """Test Bezier curve scaling to different ranges."""

    def test_scale_to_midi_range(self):
        """Test scaling a normalized curve to MIDI 0-127 range."""
        normalized = create_ease_in_bezier()
        scaled = scale_bezier_to_range(normalized, 0, 127)

        assert scaled.interpolate(0.0) == 0.0
        assert scaled.interpolate(1.0) == 127.0

        # Mid-values should be scaled proportionally
        normalized_mid = normalized.interpolate(0.5)
        scaled_mid = scaled.interpolate(0.5)
        assert abs(scaled_mid - normalized_mid * 127) < 0.1

    def test_scale_to_custom_range(self):
        """Test scaling to a custom value range."""
        normalized = create_linear_bezier()
        scaled = scale_bezier_to_range(normalized, 50, 100)

        assert abs(scaled.interpolate(0.0) - 50.0) < 0.01
        assert abs(scaled.interpolate(0.5) - 75.0) < 0.01
        assert abs(scaled.interpolate(1.0) - 100.0) < 0.01

    def test_scale_negative_range(self):
        """Test scaling to a range with negative values."""
        normalized = create_linear_bezier()
        scaled = scale_bezier_to_range(normalized, -50, 50)

        assert abs(scaled.interpolate(0.0) - (-50.0)) < 0.01
        assert abs(scaled.interpolate(0.5) - 0.0) < 0.01
        assert abs(scaled.interpolate(1.0) - 50.0) < 0.01

    def test_scale_reverse_range(self):
        """Test scaling to a reversed range (max < min)."""
        normalized = create_linear_bezier()
        scaled = scale_bezier_to_range(normalized, 100, 0)

        assert abs(scaled.interpolate(0.0) - 100.0) < 0.01
        assert abs(scaled.interpolate(0.5) - 50.0) < 0.01
        assert abs(scaled.interpolate(1.0) - 0.0) < 0.01


class TestBezierCurveEdgeCases:
    """Test edge cases and error conditions."""

    def test_zero_range_curve(self):
        """Test curve where start == end."""
        curve = BezierCurve(64, 64, 64, 64)

        # All interpolated values should be 64
        assert curve.interpolate(0.0) == 64.0
        assert curve.interpolate(0.5) == 64.0
        assert curve.interpolate(1.0) == 64.0

    def test_control_points_equal_endpoints(self):
        """Test curve where control points equal endpoints."""
        curve = BezierCurve(0, 0, 127, 127)

        # Should create a specific curve shape
        assert curve.interpolate(0.0) == 0.0
        assert curve.interpolate(1.0) == 127.0

    def test_extreme_control_points(self):
        """Test curve with extreme control point values."""
        curve = BezierCurve(0, 1000, -1000, 127)

        # Should still return start and end points correctly
        assert curve.interpolate(0.0) == 0.0
        assert curve.interpolate(1.0) == 127.0

        # Middle values might be wild, but should be finite
        mid = curve.interpolate(0.5)
        assert mid == mid  # Check not NaN

    def test_float_control_points(self):
        """Test curve with floating-point control points."""
        curve = BezierCurve(0.5, 42.7, 84.3, 126.9)

        # Should accept and convert to float
        assert isinstance(curve.p0, float)
        assert isinstance(curve.p1, float)
        assert isinstance(curve.p2, float)
        assert isinstance(curve.p3, float)


class TestBezierCurveRealWorld:
    """Test real-world use cases for MIDI automation."""

    def test_filter_sweep(self):
        """Test Bezier curve for smooth filter cutoff sweep."""
        # Simulate a filter sweep from closed (0) to open (127)
        # with ease-in characteristic (slow start, fast end)
        curve = BezierCurve(0, 10, 80, 127)

        # Generate 10 points for automation
        values = [curve.interpolate(i / 9.0) for i in range(10)]

        # Should be monotonically increasing
        for i in range(len(values) - 1):
            assert values[i] <= values[i + 1]

        # Should start at 0 and end at 127
        assert values[0] == 0.0
        assert values[-1] == 127.0

    def test_expression_curve(self):
        """Test Bezier curve for expression pedal response."""
        # Create a curve that makes expression feel more natural
        # (slow at bottom, fast in middle, slow at top)
        curve = create_ease_in_out_bezier()
        scaled = scale_bezier_to_range(curve, 0, 127)

        # Generate automation points
        values = [scaled.interpolate(i / 20.0) for i in range(21)]

        # Should be smooth and monotonic
        for i in range(len(values) - 1):
            assert values[i] <= values[i + 1]

    def test_volume_fade(self):
        """Test Bezier curve for volume fade-out."""
        # Fade from full volume (127) to silence (0)
        curve = BezierCurve(127, 100, 40, 0)

        # Generate fade curve over 1 second (10 points at 100ms)
        values = [curve.interpolate(i / 9.0) for i in range(10)]

        # Should decrease monotonically
        for i in range(len(values) - 1):
            assert values[i] >= values[i + 1]

        assert values[0] == 127.0
        assert values[-1] == 0.0

    def test_pitch_bend_glide(self):
        """Test Bezier curve for smooth pitch bend glide."""
        # Center position is 8192 (14-bit)
        # Glide from center to +2 semitones (10192)
        curve = BezierCurve(8192, 8500, 9800, 10192)

        # Generate smooth glide
        values = [curve.interpolate(i / 19.0) for i in range(20)]

        # Should be smooth and monotonic
        for i in range(len(values) - 1):
            assert values[i] <= values[i + 1]
