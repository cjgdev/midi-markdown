"""Keyboard input handler for TUI transport controls.

This module provides the KeyboardInputHandler class for capturing keyboard
input in a separate thread to control playback without blocking.
"""

from __future__ import annotations

import sys
import threading
from collections.abc import Callable


class KeyboardInputHandler:
    """Non-blocking keyboard input handler for transport controls.

    This class runs a keyboard listener in a separate daemon thread that
    captures key presses and triggers callbacks for playback control.

    Supported keys:
    - Space: Play/Pause toggle
    - Q: Quit
    - R: Restart (future)
    """

    def __init__(
        self,
        on_play_pause: Callable[[], None] | None = None,
        on_quit: Callable[[], None] | None = None,
        on_restart: Callable[[], None] | None = None,
    ):
        """Initialize keyboard input handler.

        Args:
            on_play_pause: Callback for Space key (play/pause toggle)
            on_quit: Callback for Q key (quit)
            on_restart: Callback for R key (restart, future)
        """
        self.on_play_pause = on_play_pause
        self.on_quit = on_quit
        self.on_restart = on_restart

        self._listener_thread: threading.Thread | None = None
        self._stop_flag = threading.Event()

    def start(self) -> None:
        """Start keyboard listener in background thread."""
        self._stop_flag.clear()
        self._listener_thread = threading.Thread(
            target=self._listen_loop, daemon=True, name="KeyboardListener"
        )
        self._listener_thread.start()

    def stop(self) -> None:
        """Stop keyboard listener thread."""
        self._stop_flag.set()

        if self._listener_thread and self._listener_thread.is_alive():
            # Give thread 100ms to finish
            self._listener_thread.join(timeout=0.1)

    def _listen_loop(self) -> None:
        """Main keyboard listening loop (runs in background thread).

        Uses readchar for cross-platform keyboard input. Falls back to
        input() if readchar is not available.
        """
        try:
            import readchar  # type: ignore
        except ImportError:
            # Readchar not available, use simple input() fallback
            self._listen_loop_fallback()
            return

        while not self._stop_flag.is_set():
            try:
                # Non-blocking read with timeout
                # Note: readchar doesn't have a built-in timeout, so we
                # check the stop flag between reads
                if sys.stdin.isatty():
                    key = readchar.readkey()
                    self._handle_key(key)
            except (KeyboardInterrupt, EOFError):
                # User pressed Ctrl+C or EOF
                if self.on_quit:
                    self.on_quit()
                break
            except Exception:
                # Ignore other errors (e.g., terminal not available)
                break

    def _listen_loop_fallback(self) -> None:
        """Fallback keyboard loop using input() when readchar unavailable.

        This is less responsive but works without dependencies.
        """
        while not self._stop_flag.is_set():
            try:
                # This blocks until Enter is pressed
                line = input()
                if line:
                    self._handle_key(line[0])
            except (KeyboardInterrupt, EOFError):
                if self.on_quit:
                    self.on_quit()
                break
            except Exception:
                break

    def _handle_key(self, key: str) -> None:
        """Handle key press by triggering appropriate callback.

        Args:
            key: Key character pressed
        """
        key_lower = key.lower() if len(key) == 1 else key

        if key == " " or key_lower == "space":
            # Space bar - play/pause toggle
            if self.on_play_pause:
                self.on_play_pause()

        elif key_lower == "q":
            # Q - quit
            if self.on_quit:
                self.on_quit()

        elif key_lower == "r":
            # R - restart (future feature)
            if self.on_restart:
                self.on_restart()
