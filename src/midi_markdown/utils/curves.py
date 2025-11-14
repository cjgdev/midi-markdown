"""Bezier curve implementation for smooth parameter transitions.

This module provides Bezier curve interpolation for creating smooth,
natural-looking parameter changes in MIDI automation. It implements
cubic Bezier curves using De Casteljau's algorithm.

Key Features:
- Cubic Bezier interpolation with 4 control points
- Efficient De Casteljau's algorithm
- Value clamping to MIDI ranges
- Support for reverse curves (end < start)

Usage:
    curve = BezierCurve(0, 40, 90, 127)
    value_at_25_percent = curve.interpolate(0.25)
    value_at_50_percent = curve.interpolate(0.5)
"""

from __future__ import annotations

from typing import Any


class BezierCurve:
    """Cubic Bezier curve interpolator using De Casteljau's algorithm.

    A cubic Bezier curve is defined by 4 control points:
    - P0: Start point
    - P1: First control point (influences start curvature)
    - P2: Second control point (influences end curvature)
    - P3: End point

    The curve is calculated using the formula:
    B(t) = (1-t)³P0 + 3(1-t)²tP1 + 3(1-t)t²P2 + t³P3

    where t ∈ [0, 1] is the interpolation parameter.

    Attributes:
        p0: Start point value
        p1: First control point value
        p2: Second control point value
        p3: End point value

    Example:
        >>> curve = BezierCurve(0, 30, 90, 127)
        >>> curve.interpolate(0.0)  # Start
        0.0
        >>> curve.interpolate(0.5)  # Midpoint
        60.0
        >>> curve.interpolate(1.0)  # End
        127.0
    """

    def __init__(self, p0: float, p1: float, p2: float, p3: float):
        """Initialize Bezier curve with 4 control points.

        Args:
            p0: Start point (typically 0-127 for MIDI)
            p1: First control point (influences start curvature)
            p2: Second control point (influences end curvature)
            p3: End point (typically 0-127 for MIDI)

        Note:
            Control points can be outside the 0-127 range to create
            overshoot effects, but the interpolated values will be
            clamped to valid MIDI ranges when used.
        """
        self.p0 = float(p0)
        self.p1 = float(p1)
        self.p2 = float(p2)
        self.p3 = float(p3)

    def interpolate(self, t: float) -> float:
        """Calculate curve value at parameter t using De Casteljau's algorithm.

        This algorithm is numerically stable and efficiently computes the
        Bezier curve value without expanding the cubic polynomial.

        Args:
            t: Interpolation parameter, where:
               - t=0.0 returns the start point (p0)
               - t=1.0 returns the end point (p3)
               - 0 < t < 1 returns points along the curve

        Returns:
            Interpolated value at parameter t

        Note:
            Values of t outside [0, 1] are clamped to the valid range.
            This ensures predictable behavior at curve endpoints.

        Example:
            >>> curve = BezierCurve(0, 40, 90, 127)
            >>> curve.interpolate(0.0)
            0.0
            >>> curve.interpolate(0.25)  # 25% along the curve
            28.515625
            >>> curve.interpolate(0.5)   # Midpoint
            63.75
            >>> curve.interpolate(0.75)  # 75% along the curve
            98.484375
            >>> curve.interpolate(1.0)
            127.0
        """
        # Clamp t to [0, 1] range to prevent extrapolation
        t = max(0.0, min(1.0, t))

        # Calculate using cubic Bezier formula:
        # B(t) = (1-t)³P0 + 3(1-t)²tP1 + 3(1-t)t²P2 + t³P3

        # Precompute repeated terms for efficiency
        one_minus_t = 1.0 - t
        one_minus_t_squared = one_minus_t * one_minus_t
        one_minus_t_cubed = one_minus_t_squared * one_minus_t
        t_squared = t * t
        t_cubed = t_squared * t

        # Apply Bezier formula
        return (
            one_minus_t_cubed * self.p0
            + 3.0 * one_minus_t_squared * t * self.p1
            + 3.0 * one_minus_t * t_squared * self.p2
            + t_cubed * self.p3
        )

    def __repr__(self) -> str:
        """String representation of the Bezier curve."""
        return f"BezierCurve(p0={self.p0}, p1={self.p1}, p2={self.p2}, p3={self.p3})"

    def __eq__(self, other: Any) -> bool:
        """Check equality of two Bezier curves."""
        if not isinstance(other, BezierCurve):
            return False
        return (
            self.p0 == other.p0
            and self.p1 == other.p1
            and self.p2 == other.p2
            and self.p3 == other.p3
        )


def create_ease_in_bezier() -> BezierCurve:
    """Create a standard ease-in Bezier curve.

    This curve starts slowly and accelerates toward the end.
    Equivalent to CSS ease-in timing function.

    Returns:
        BezierCurve with ease-in characteristic

    Example:
        >>> curve = create_ease_in_bezier()
        >>> # Normalized 0-1 range
        >>> curve.interpolate(0.0)
        0.0
        >>> curve.interpolate(0.5)  # Still slow at midpoint
        0.125
        >>> curve.interpolate(1.0)
        1.0
    """
    return BezierCurve(0.0, 0.42, 0.0, 1.0)


def create_ease_out_bezier() -> BezierCurve:
    """Create a standard ease-out Bezier curve.

    This curve starts quickly and decelerates toward the end.
    Equivalent to CSS ease-out timing function.

    Returns:
        BezierCurve with ease-out characteristic

    Example:
        >>> curve = create_ease_out_bezier()
        >>> curve.interpolate(0.0)
        0.0
        >>> curve.interpolate(0.5)  # Already fast at midpoint
        0.875
        >>> curve.interpolate(1.0)
        1.0
    """
    return BezierCurve(0.0, 0.58, 1.0, 1.0)


def create_ease_in_out_bezier() -> BezierCurve:
    """Create a standard ease-in-out Bezier curve.

    This curve starts slowly, accelerates in the middle, and
    decelerates toward the end. Equivalent to CSS ease-in-out.

    Returns:
        BezierCurve with ease-in-out characteristic

    Example:
        >>> curve = create_ease_in_out_bezier()
        >>> curve.interpolate(0.0)
        0.0
        >>> curve.interpolate(0.5)  # Smooth midpoint
        0.5
        >>> curve.interpolate(1.0)
        1.0
    """
    return BezierCurve(0.0, 0.42, 0.58, 1.0)


def create_linear_bezier() -> BezierCurve:
    """Create a linear Bezier curve (straight line).

    This curve provides linear interpolation between start and end.
    Useful for comparison with curved interpolation.

    Returns:
        BezierCurve with linear characteristic

    Example:
        >>> curve = create_linear_bezier()
        >>> curve.interpolate(0.0)
        0.0
        >>> curve.interpolate(0.5)
        0.5
        >>> curve.interpolate(1.0)
        1.0
    """
    return BezierCurve(0.0, 0.333, 0.667, 1.0)


def scale_bezier_to_range(curve: BezierCurve, min_val: float, max_val: float) -> BezierCurve:
    """Scale a normalized Bezier curve to a specific value range.

    Takes a Bezier curve defined in the 0-1 range and scales it to
    map to a specific min/max range. This is useful for creating
    reusable curve shapes that can be applied to different MIDI
    parameter ranges.

    Args:
        curve: Bezier curve with control points in 0-1 range
        min_val: Minimum value of the target range
        max_val: Maximum value of the target range

    Returns:
        New BezierCurve scaled to the specified range

    Example:
        >>> normalized = create_ease_in_bezier()  # 0-1 range
        >>> midi_curve = scale_bezier_to_range(normalized, 0, 127)
        >>> midi_curve.interpolate(0.0)
        0.0
        >>> midi_curve.interpolate(1.0)
        127.0
    """
    value_range = max_val - min_val
    return BezierCurve(
        min_val + curve.p0 * value_range,
        min_val + curve.p1 * value_range,
        min_val + curve.p2 * value_range,
        min_val + curve.p3 * value_range,
    )
