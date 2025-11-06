"""Unit tests for MIDI I/O management."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from midi_markdown.runtime.midi_io import MIDIIOError, MIDIOutputManager


@pytest.fixture
def mock_midiout():
    """Mock rtmidi.MidiOut for testing."""
    with patch("midi_markdown.runtime.midi_io.rtmidi.MidiOut") as mock:
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        yield mock_instance


@pytest.mark.unit
class TestMIDIOutputManager:
    """Tests for MIDIOutputManager class."""

    def test_init(self, mock_midiout):
        """Test MIDIOutputManager initialization."""
        manager = MIDIOutputManager()

        assert manager.midiout == mock_midiout
        assert manager.current_port is None
        assert manager.port_name is None

    def test_list_ports_empty(self, mock_midiout):
        """Test list_ports returns empty list when no ports available."""
        mock_midiout.get_ports.return_value = []

        manager = MIDIOutputManager()
        ports = manager.list_ports()

        assert ports == []
        mock_midiout.get_ports.assert_called_once()

    def test_list_ports_with_ports(self, mock_midiout):
        """Test list_ports returns available ports."""
        expected_ports = ["IAC Driver Bus 1", "Network Session 1", "Virtual Port"]
        mock_midiout.get_ports.return_value = expected_ports

        manager = MIDIOutputManager()
        ports = manager.list_ports()

        assert ports == expected_ports
        mock_midiout.get_ports.assert_called_once()

    def test_open_port_by_index(self, mock_midiout):
        """Test opening port by index."""
        mock_midiout.get_ports.return_value = ["Port 0", "Port 1", "Port 2"]

        manager = MIDIOutputManager()
        manager.open_port(1)

        mock_midiout.open_port.assert_called_once_with(1)
        assert manager.current_port == 1
        assert manager.port_name == "Port 1"

    def test_open_port_by_name(self, mock_midiout):
        """Test opening port by name."""
        mock_midiout.get_ports.return_value = ["IAC Driver", "Network", "Virtual"]

        manager = MIDIOutputManager()
        manager.open_port("Network")

        mock_midiout.open_port.assert_called_once_with(1)
        assert manager.current_port == 1
        assert manager.port_name == "Network"

    def test_open_port_invalid_index_negative(self, mock_midiout):
        """Test opening port with negative index raises error."""
        mock_midiout.get_ports.return_value = ["Port 0", "Port 1"]

        manager = MIDIOutputManager()

        with pytest.raises(MIDIIOError, match="Port index -1 out of range"):
            manager.open_port(-1)

        mock_midiout.open_port.assert_not_called()

    def test_open_port_invalid_index_too_high(self, mock_midiout):
        """Test opening port with index >= len(ports) raises error."""
        mock_midiout.get_ports.return_value = ["Port 0", "Port 1"]

        manager = MIDIOutputManager()

        with pytest.raises(MIDIIOError, match="Port index 5 out of range"):
            manager.open_port(5)

        mock_midiout.open_port.assert_not_called()

    def test_open_port_invalid_name(self, mock_midiout):
        """Test opening port with non-existent name raises error."""
        mock_midiout.get_ports.return_value = ["IAC Driver", "Network"]

        manager = MIDIOutputManager()

        with pytest.raises(MIDIIOError, match="Port 'NonExistent' not found"):
            manager.open_port("NonExistent")

        mock_midiout.open_port.assert_not_called()

    def test_open_port_already_open(self, mock_midiout):
        """Test opening port when one is already open raises error."""
        mock_midiout.get_ports.return_value = ["Port 0", "Port 1"]

        manager = MIDIOutputManager()
        manager.open_port(0)

        with pytest.raises(MIDIIOError, match="Port 'Port 0' is already open"):
            manager.open_port(1)

        # Should only be called once (first open)
        assert mock_midiout.open_port.call_count == 1

    def test_close_port(self, mock_midiout):
        """Test closing port."""
        mock_midiout.get_ports.return_value = ["Port 0"]

        manager = MIDIOutputManager()
        manager.open_port(0)
        manager.close_port()

        mock_midiout.close_port.assert_called_once()
        assert manager.current_port is None
        assert manager.port_name is None

    def test_close_port_when_not_open(self, mock_midiout):
        """Test closing port when no port is open (should be safe no-op)."""
        manager = MIDIOutputManager()
        manager.close_port()  # Should not raise

        mock_midiout.close_port.assert_not_called()

    def test_send_message_3_bytes(self, mock_midiout):
        """Test sending 3-byte MIDI message (Note On, CC, etc.)."""
        mock_midiout.get_ports.return_value = ["Port 0"]

        manager = MIDIOutputManager()
        manager.open_port(0)
        manager.send_message([0x90, 60, 100])

        mock_midiout.send_message.assert_called_once_with([0x90, 60, 100])

    def test_send_message_2_bytes(self, mock_midiout):
        """Test sending 2-byte MIDI message (Program Change)."""
        mock_midiout.get_ports.return_value = ["Port 0"]

        manager = MIDIOutputManager()
        manager.open_port(0)
        manager.send_message([0xC0, 42])

        mock_midiout.send_message.assert_called_once_with([0xC0, 42])

    def test_send_message_no_port_open(self, mock_midiout):
        """Test sending message without opening port raises error."""
        manager = MIDIOutputManager()

        with pytest.raises(MIDIIOError, match="No MIDI port open"):
            manager.send_message([0x90, 60, 100])

        mock_midiout.send_message.assert_not_called()

    def test_send_message_invalid_type(self, mock_midiout):
        """Test sending non-list message raises error."""
        mock_midiout.get_ports.return_value = ["Port 0"]

        manager = MIDIOutputManager()
        manager.open_port(0)

        with pytest.raises(MIDIIOError, match="Message must be a list"):
            manager.send_message((0x90, 60, 100))  # Tuple instead of list

    def test_send_message_invalid_length_too_short(self, mock_midiout):
        """Test sending message with < 2 bytes raises error."""
        mock_midiout.get_ports.return_value = ["Port 0"]

        manager = MIDIOutputManager()
        manager.open_port(0)

        with pytest.raises(MIDIIOError, match="Message must be 2-3 bytes"):
            manager.send_message([0x90])

    def test_send_message_invalid_length_too_long(self, mock_midiout):
        """Test sending message with > 3 bytes raises error."""
        mock_midiout.get_ports.return_value = ["Port 0"]

        manager = MIDIOutputManager()
        manager.open_port(0)

        with pytest.raises(MIDIIOError, match="Message must be 2-3 bytes"):
            manager.send_message([0x90, 60, 100, 0])

    def test_send_message_invalid_byte_value_negative(self, mock_midiout):
        """Test sending message with negative byte value raises error."""
        mock_midiout.get_ports.return_value = ["Port 0"]

        manager = MIDIOutputManager()
        manager.open_port(0)

        with pytest.raises(MIDIIOError, match="Message byte 1 must be 0-255"):
            manager.send_message([0x90, -1, 100])

    def test_send_message_invalid_byte_value_too_high(self, mock_midiout):
        """Test sending message with byte value > 255 raises error."""
        mock_midiout.get_ports.return_value = ["Port 0"]

        manager = MIDIOutputManager()
        manager.open_port(0)

        with pytest.raises(MIDIIOError, match="Message byte 2 must be 0-255"):
            manager.send_message([0x90, 60, 256])

    def test_send_message_invalid_byte_type(self, mock_midiout):
        """Test sending message with non-int byte raises error."""
        mock_midiout.get_ports.return_value = ["Port 0"]

        manager = MIDIOutputManager()
        manager.open_port(0)

        with pytest.raises(MIDIIOError, match="Message byte 1 must be 0-255"):
            manager.send_message([0x90, "60", 100])

    def test_del_closes_port(self, mock_midiout):
        """Test __del__ closes port on deletion."""
        mock_midiout.get_ports.return_value = ["Port 0"]

        manager = MIDIOutputManager()
        manager.open_port(0)
        manager.__del__()

        mock_midiout.close_port.assert_called_once()
        assert manager.current_port is None
        assert manager.port_name is None

    def test_del_when_no_port_open(self, mock_midiout):
        """Test __del__ is safe when no port is open."""
        manager = MIDIOutputManager()
        manager.__del__()  # Should not raise

        mock_midiout.close_port.assert_not_called()

    def test_multiple_messages(self, mock_midiout):
        """Test sending multiple messages in sequence."""
        mock_midiout.get_ports.return_value = ["Port 0"]

        manager = MIDIOutputManager()
        manager.open_port(0)

        # Send multiple messages
        manager.send_message([0x90, 60, 100])  # Note On
        manager.send_message([0xB0, 7, 127])  # CC 7 (Volume)
        manager.send_message([0xC0, 42])  # Program Change
        manager.send_message([0x80, 60, 0])  # Note Off

        assert mock_midiout.send_message.call_count == 4

    def test_open_close_reopen(self, mock_midiout):
        """Test opening, closing, and reopening port."""
        mock_midiout.get_ports.return_value = ["Port 0", "Port 1"]

        manager = MIDIOutputManager()

        # Open port 0
        manager.open_port(0)
        assert manager.current_port == 0
        assert manager.port_name == "Port 0"

        # Close it
        manager.close_port()
        assert manager.current_port is None

        # Reopen a different port
        manager.open_port("Port 1")
        assert manager.current_port == 1
        assert manager.port_name == "Port 1"
