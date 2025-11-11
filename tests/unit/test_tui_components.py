"""Unit tests for TUI components."""

from __future__ import annotations

import pytest
from rich.panel import Panel
from rich.progress import Progress
from rich.text import Text

from midi_markdown.runtime.tui.components import (
    render_controls,
    render_event_list,
    render_header,
    render_progress_bar,
    render_status_bar,
)
from midi_markdown.runtime.tui.state import EventInfo


@pytest.mark.unit
class TestTUIComponents:
    """Tests for TUI rendering components."""

    def test_render_header(self) -> None:
        """Test render_header returns Panel with correct content."""
        result = render_header("test.mmd", "IAC Driver Bus 1", "Test Song")

        assert isinstance(result, Panel)
        # Panel should contain file name, port name, and title

    def test_render_header_no_title(self) -> None:
        """Test render_header with no title uses 'Untitled'."""
        result = render_header("test.mmd", "IAC Driver Bus 1", None)

        assert isinstance(result, Panel)
        # Should default to "Untitled"

    def test_render_progress_bar(self) -> None:
        """Test render_progress_bar returns Progress with correct values."""
        result = render_progress_bar(30000.0, 60000.0)

        assert isinstance(result, Progress)
        # Progress should be at 50% (30s / 60s)

    def test_render_progress_bar_zero(self) -> None:
        """Test render_progress_bar at start (0ms)."""
        result = render_progress_bar(0.0, 60000.0)

        assert isinstance(result, Progress)

    def test_render_progress_bar_complete(self) -> None:
        """Test render_progress_bar at completion."""
        result = render_progress_bar(60000.0, 60000.0)

        assert isinstance(result, Progress)

    def test_render_status_bar_playing(self) -> None:
        """Test render_status_bar with 'playing' state."""
        result = render_status_bar("playing", 120.0, 480)

        assert isinstance(result, Text)
        # Should contain "PLAYING", tempo "120.0", tick "480"

    def test_render_status_bar_paused(self) -> None:
        """Test render_status_bar with 'paused' state."""
        result = render_status_bar("paused", 120.0, 480)

        assert isinstance(result, Text)
        # Should contain "PAUSED"

    def test_render_status_bar_stopped(self) -> None:
        """Test render_status_bar with 'stopped' state."""
        result = render_status_bar("stopped", 120.0, 0)

        assert isinstance(result, Text)
        # Should contain "STOPPED"

    def test_render_event_list_empty(self) -> None:
        """Test render_event_list with no events."""
        result = render_event_list([])

        assert isinstance(result, Panel)
        # Should return panel with table but no rows

    def test_render_event_list_with_events(self) -> None:
        """Test render_event_list with events."""
        events = [
            EventInfo(time_ms=0.0, type="NOTE_ON", channel=1, data="C4, Vel: 80"),
            EventInfo(time_ms=500.0, type="NOTE_OFF", channel=1, data="C4, Vel: 0"),
            EventInfo(time_ms=1000.0, type="CONTROL_CHANGE", channel=1, data="CC7: 100"),
        ]

        result = render_event_list(events)

        assert isinstance(result, Panel)
        # Should contain all 3 events

    def test_render_event_list_max_rows(self) -> None:
        """Test render_event_list with more than max events."""
        # Create 25 events (more than typical display)
        events = [
            EventInfo(time_ms=i * 100.0, type="NOTE_ON", channel=1, data=f"Event {i}")
            for i in range(25)
        ]

        result = render_event_list(events, max_rows=10)

        assert isinstance(result, Panel)
        # Should only display last 10 events

    def test_render_controls(self) -> None:
        """Test render_controls returns Panel."""
        result = render_controls()

        assert isinstance(result, Panel)
        # Should contain keyboard shortcuts (Space, Q, R)
