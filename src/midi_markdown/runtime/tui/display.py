"""TUI Display Manager with Rich Live integration.

This module provides the TUIDisplayManager class that manages the live terminal
display using Rich's Live context for flicker-free updates at 30 FPS.
"""

from __future__ import annotations

import threading
import time
from typing import TYPE_CHECKING

from rich.console import Console, Group
from rich.live import Live

from .components import (
    render_controls,
    render_event_list,
    render_header,
    render_progress_bar,
    render_status_bar,
)

if TYPE_CHECKING:
    from .state import TUIState


class TUIDisplayManager:
    """Manages live terminal display with Rich Live.

    This class coordinates the display of all TUI components and manages
    the refresh loop at a target rate of 30 FPS (every ~33ms).

    The display runs in the main thread while playback happens in a background
    thread, with state synchronized through TUIState.
    """

    def __init__(
        self,
        state: TUIState,
        file_name: str,
        port_name: str,
        title: str | None = None,
        refresh_rate: int = 30,
    ):
        """Initialize TUI display manager.

        Args:
            state: TUIState instance for reading display data
            file_name: Name of the MML file being played
            port_name: MIDI output port name
            title: Optional song title
            refresh_rate: Target refresh rate in FPS (default: 30)
        """
        self.state = state
        self.file_name = file_name
        self.port_name = port_name
        self.title = title
        self.refresh_rate = refresh_rate
        self.refresh_interval = 1.0 / refresh_rate  # ~33ms for 30 FPS

        self.console = Console()
        self.live: Live | None = None
        self._stop_flag = threading.Event()

    def start(self) -> None:
        """Start the live display.

        This should be called before starting playback. The display will
        run until stop() is called.
        """
        self._stop_flag.clear()

        # Create Live context with auto-refresh disabled (we control refresh rate)
        self.live = Live(
            self._render_layout(),
            console=self.console,
            refresh_per_second=self.refresh_rate,
            screen=False,  # Don't use alternate screen
        )
        self.live.start()

    def stop(self) -> None:
        """Stop the live display and cleanup."""
        self._stop_flag.set()

        if self.live:
            self.live.stop()
            self.live = None

    def update_display(self) -> None:
        """Update the display with current state.

        This should be called periodically (e.g., every 33ms for 30 FPS).
        """
        if self.live and not self._stop_flag.is_set():
            self.live.update(self._render_layout())

    def run_loop(self) -> None:
        """Run the display update loop until stopped.

        This is a blocking call that continuously updates the display
        at the target refresh rate. Call this in the main thread while
        playback runs in a background thread.
        """
        while not self._stop_flag.is_set():
            self.update_display()
            time.sleep(self.refresh_interval)

    def _render_layout(self) -> Group:
        """Render the complete TUI layout.

        Returns:
            Rich Group containing all UI components
        """
        # Get atomic snapshot of state
        snapshot = self.state.get_state_snapshot()

        # Render all components
        header = render_header(self.file_name, self.port_name, self.title)

        progress = render_progress_bar(snapshot["position_ms"], snapshot["total_duration_ms"])

        status = render_status_bar(snapshot["state"], snapshot["tempo"], snapshot["position_ticks"])

        events = render_event_list(snapshot["event_history"])

        controls = render_controls()

        # Combine into layout
        return Group(header, progress, status, events, controls)
