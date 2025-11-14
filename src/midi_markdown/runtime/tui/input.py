"""Keyboard input handler for TUI transport controls.

This module provides the KeyboardInputHandler class for capturing keyboard
input in a separate thread to control playback without blocking.
"""

from __future__ import annotations

import sys
import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable


class KeyboardInputHandler:
    """Non-blocking keyboard input handler for transport controls.

    This class runs a keyboard listener in a separate daemon thread that
    captures key presses and triggers callbacks for playback control.

    Supported keys:
    - Space: Play/Pause toggle
    - Q: Quit
    - R: Restart (future)
    - Left Arrow: Seek backward 5s
    - Right Arrow: Seek forward 5s
    - Shift+Left Arrow: Seek backward 1 beat
    - Shift+Right Arrow: Seek forward 1 beat
    - Ctrl+Left Arrow: Seek backward 1 bar
    - Ctrl+Right Arrow: Seek forward 1 bar
    """

    def __init__(
        self,
        on_play_pause: Callable[[], None] | None = None,
        on_quit: Callable[[], None] | None = None,
        on_restart: Callable[[], None] | None = None,
        on_seek_forward: Callable[[], None] | None = None,
        on_seek_backward: Callable[[], None] | None = None,
        on_seek_beat_forward: Callable[[], None] | None = None,
        on_seek_beat_backward: Callable[[], None] | None = None,
        on_seek_bar_forward: Callable[[], None] | None = None,
        on_seek_bar_backward: Callable[[], None] | None = None,
    ):
        """Initialize keyboard input handler.

        Args:
            on_play_pause: Callback for Space key (play/pause toggle)
            on_quit: Callback for Q key (quit)
            on_restart: Callback for R key (restart, future)
            on_seek_forward: Callback for Right Arrow key (seek forward 5s)
            on_seek_backward: Callback for Left Arrow key (seek backward 5s)
            on_seek_beat_forward: Callback for Shift+Right Arrow (seek forward 1 beat)
            on_seek_beat_backward: Callback for Shift+Left Arrow (seek backward 1 beat)
            on_seek_bar_forward: Callback for Ctrl+Right Arrow (seek forward 1 bar)
            on_seek_bar_backward: Callback for Ctrl+Left Arrow (seek backward 1 bar)
        """
        self.on_play_pause = on_play_pause
        self.on_quit = on_quit
        self.on_restart = on_restart
        self.on_seek_forward = on_seek_forward
        self.on_seek_backward = on_seek_backward
        self.on_seek_beat_forward = on_seek_beat_forward
        self.on_seek_beat_backward = on_seek_beat_backward
        self.on_seek_bar_forward = on_seek_bar_forward
        self.on_seek_bar_backward = on_seek_bar_backward

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

        # Handle standard keys
        if key == " " or key_lower == "space":
            if self.on_play_pause:
                self.on_play_pause()
        elif key_lower == "q" and self.on_quit:
            self.on_quit()
        elif key_lower == "r" and self.on_restart:
            self.on_restart()
        else:
            # Handle arrow keys
            self._handle_arrow_key(key, key_lower)

    def _handle_arrow_key(self, key: str, key_lower: str) -> None:
        """Handle arrow key presses for seeking.

        Supports modifier keys:
        - Arrow: Seek 5 seconds
        - Shift+Arrow: Seek 1 beat
        - Ctrl+Arrow: Seek 1 bar

        Args:
            key: Original key character
            key_lower: Lowercased key character
        """
        # Check for readchar key constants
        try:
            import readchar  # type: ignore

            if hasattr(readchar, "key"):
                # Ctrl+Arrow (bar seeking)
                if hasattr(readchar.key, "CTRL_LEFT") and key == readchar.key.CTRL_LEFT:
                    if self.on_seek_bar_backward:
                        self.on_seek_bar_backward()
                    return
                if hasattr(readchar.key, "CTRL_RIGHT") and key == readchar.key.CTRL_RIGHT:
                    if self.on_seek_bar_forward:
                        self.on_seek_bar_forward()
                    return

                # Shift+Arrow (beat seeking)
                if hasattr(readchar.key, "SHIFT_LEFT") and key == readchar.key.SHIFT_LEFT:
                    if self.on_seek_beat_backward:
                        self.on_seek_beat_backward()
                    return
                if hasattr(readchar.key, "SHIFT_RIGHT") and key == readchar.key.SHIFT_RIGHT:
                    if self.on_seek_beat_forward:
                        self.on_seek_beat_forward()
                    return

                # Plain arrow keys (time seeking)
                if key == readchar.key.LEFT and self.on_seek_backward:
                    self.on_seek_backward()
                    return
                if key == readchar.key.RIGHT and self.on_seek_forward:
                    self.on_seek_forward()
                    return
        except (ImportError, AttributeError):
            pass

        # Fallback: check for ANSI escape sequences
        # Ctrl+Arrow sequences
        if key == "\x1b[1;5D" and self.on_seek_bar_backward:  # Ctrl+Left
            self.on_seek_bar_backward()
        elif key == "\x1b[1;5C" and self.on_seek_bar_forward:  # Ctrl+Right
            self.on_seek_bar_forward()
        # Shift+Arrow sequences
        elif key == "\x1b[1;2D" and self.on_seek_beat_backward:  # Shift+Left
            self.on_seek_beat_backward()
        elif key == "\x1b[1;2C" and self.on_seek_beat_forward:  # Shift+Right
            self.on_seek_beat_forward()
        # Plain arrow sequences
        elif (key == "\x1b[D" or key_lower == "left") and self.on_seek_backward:
            self.on_seek_backward()
        elif (key == "\x1b[C" or key_lower == "right") and self.on_seek_forward:
            self.on_seek_forward()
