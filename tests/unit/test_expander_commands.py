"""
Unit tests for CommandExpander MIDI command processing.

Phase 4: Tests MIDI command processing and event generation.
"""

from midi_markdown.parser.ast_nodes import MIDICommand


class TestCommandProcessing:
    """Test MIDI command processing."""

    def test_midi_command_object(self, expander):
        """Test processing MIDICommand objects."""
        cmd = MIDICommand(type="pc", channel=1, data1=10)
        nodes = [cmd]

        events = expander.process_ast(nodes)

        assert len(events) == 1
        assert events[0]["type"] == "pc"
        assert events[0]["channel"] == 1
        assert events[0]["data1"] == 10

    def test_command_dict(self, expander):
        """Test processing dict-based commands."""
        nodes = [{"type": "pc", "channel": 1, "data1": 5}]

        events = expander.process_ast(nodes)

        assert len(events) == 1
        assert events[0]["type"] == "pc"

    def test_timed_event_block(self, expander):
        """Test processing timed event with multiple commands."""
        nodes = [
            {
                "type": "timed_event",
                "timing": 480,  # 1 beat
                "commands": [
                    {"type": "pc", "channel": 1, "data1": 10},
                    {"type": "cc", "channel": 1, "data1": 7, "data2": 127},
                ],
            }
        ]

        events = expander.process_ast(nodes)

        assert len(events) == 2
        # Both should have time=480
        assert events[0]["time"] == 480
        assert events[1]["time"] == 480

    def test_command_time_assignment(self, expander):
        """Test that current_time is assigned to events."""
        expander.current_time = 1000
        nodes = [{"type": "pc", "channel": 1, "data1": 5}]

        events = expander.process_ast(nodes)

        assert events[0]["time"] == 1000

    def test_unknown_node_skipped(self, expander):
        """Test that unknown node types are skipped gracefully."""
        nodes = [
            {"type": "unknown_type", "data": "something"},
            {"type": "pc", "channel": 1, "data1": 5},  # This should process
        ]

        events = expander.process_ast(nodes)

        # Only the PC command should be processed
        assert len(events) == 1
        assert events[0]["type"] == "pc"
