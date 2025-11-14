"""MIDI I/O management for real-time MIDI output.

This module provides the MIDIOutputManager class for managing MIDI output port
connections and sending MIDI messages using python-rtmidi.
"""

from __future__ import annotations

import rtmidi


class MIDIIOError(Exception):
    """Raised when MIDI I/O operation fails."""


class MIDIOutputManager:
    """Manages MIDI output port connections and message sending.

    This class provides a high-level interface to python-rtmidi for:
    - Listing available MIDI output ports
    - Opening ports by name or index
    - Sending MIDI messages
    - Proper resource cleanup

    Example:
        >>> manager = MIDIOutputManager()
        >>> ports = manager.list_ports()
        >>> print(ports)
        ['IAC Driver Bus 1', 'Network Session 1']
        >>> manager.open_port('IAC Driver Bus 1')
        >>> manager.send_message([0x90, 60, 100])  # Note On, C4, velocity 100
        >>> manager.close_port()
    """

    def __init__(self) -> None:
        """Initialize MIDI output manager.

        Creates rtmidi.MidiOut instance. No port is opened by default.

        Raises:
            SystemError: If MIDI backend initialization fails (e.g., ALSA sequencer unavailable)
        """
        # Initialize attributes first in case __init__ raises exception
        self.current_port: int | None = None
        self.port_name: str | None = None

        try:
            self.midiout = rtmidi.MidiOut()
        except SystemError:
            # Re-raise SystemError to let callers know initialization failed
            # This can happen in headless CI environments without ALSA/CoreMIDI/etc
            raise

    def list_ports(self) -> list[str]:
        """Get list of available MIDI output ports.

        Returns:
            List of port names (e.g., ['IAC Driver Bus 1', 'Network Session 1'])
            Returns empty list if no ports available.

        Example:
            >>> manager = MIDIOutputManager()
            >>> ports = manager.list_ports()
            >>> for i, port in enumerate(ports):
            ...     print(f"{i}: {port}")
        """
        return self.midiout.get_ports()

    def open_port(self, port_name_or_index: str | int) -> None:
        """Open MIDI output port by name or index.

        Args:
            port_name_or_index: Either port index (0-based int) or exact port name (str)

        Raises:
            MIDIIOError: If port index out of range or port name not found
            MIDIIOError: If port is already open (must close first)

        Example:
            >>> manager = MIDIOutputManager()
            >>> manager.open_port(0)  # Open by index
            >>> manager.close_port()
            >>> manager.open_port('IAC Driver Bus 1')  # Open by name
        """
        # Check if port already open
        if self.current_port is not None:
            msg = f"Port '{self.port_name}' is already open. Close it first."
            raise MIDIIOError(msg)

        ports = self.list_ports()

        # Handle port index
        if isinstance(port_name_or_index, int):
            port_index = port_name_or_index
            if port_index < 0 or port_index >= len(ports):
                msg = f"Port index {port_index} out of range (0-{len(ports) - 1})"
                raise MIDIIOError(msg)
            port_name = ports[port_index]

        # Handle port name
        else:
            port_name = port_name_or_index
            try:
                port_index = ports.index(port_name)
            except ValueError as e:
                available = ", ".join(f"'{p}'" for p in ports)
                msg = f"Port '{port_name}' not found. Available ports: {available}"
                raise MIDIIOError(msg) from e

        # Open the port
        try:
            self.midiout.open_port(port_index)
            self.current_port = port_index
            self.port_name = port_name
        except Exception as e:
            msg = f"Failed to open port '{port_name}': {e}"
            raise MIDIIOError(msg) from e

    def close_port(self) -> None:
        """Close current MIDI port.

        Safe to call even if no port is open (does nothing).
        Resets current_port and port_name to None.

        Example:
            >>> manager = MIDIOutputManager()
            >>> manager.open_port(0)
            >>> manager.close_port()
            >>> manager.close_port()  # Safe to call again
        """
        if self.current_port is not None:
            self.midiout.close_port()
            self.current_port = None
            self.port_name = None

    def send_message(self, message: list[int]) -> None:
        """Send MIDI message to current port.

        Args:
            message: MIDI message as list of bytes
                     - 2 bytes: [status, data1] (e.g., Program Change)
                     - 3 bytes: [status, data1, data2] (e.g., Note On, CC)

        Raises:
            MIDIIOError: If no port is open
            MIDIIOError: If message format is invalid

        Example:
            >>> manager = MIDIOutputManager()
            >>> manager.open_port(0)
            >>> manager.send_message([0x90, 60, 100])  # Note On
            >>> manager.send_message([0xB0, 7, 127])   # CC 7 (Volume)
            >>> manager.send_message([0xC0, 42])       # Program Change 42
        """
        if self.current_port is None:
            msg = "No MIDI port open. Call open_port() first."
            raise MIDIIOError(msg)

        # Validate message format
        if not isinstance(message, list):
            msg = f"Message must be a list, got {type(message).__name__}"
            raise MIDIIOError(msg)

        if len(message) < 2 or len(message) > 3:
            msg = f"Message must be 2-3 bytes, got {len(message)} bytes"
            raise MIDIIOError(msg)

        # Validate byte values (0-255)
        for i, byte in enumerate(message):
            if not isinstance(byte, int) or byte < 0 or byte > 255:
                msg = f"Message byte {i} must be 0-255, got {byte}"
                raise MIDIIOError(msg)

        # Send the message
        try:
            self.midiout.send_message(message)
        except Exception as e:
            msg = f"Failed to send MIDI message: {e}"
            raise MIDIIOError(msg) from e

    def __del__(self) -> None:
        """Cleanup - close port on deletion.

        Ensures MIDI port is properly closed when object is garbage collected.
        Safe to call even if port is already closed.
        """
        self.close_port()
