"""End-to-end integration tests for MIDI Markdown compilation."""

import mido

from midi_markdown.codegen import generate_midi_file
from midi_markdown.core.ir import MIDIEvent, create_ir_program, string_to_event_type
from midi_markdown.expansion.expander import CommandExpander
from midi_markdown.parser.parser import MMDParser


class TestEndToEndCompilation:
    """Test complete pipeline: MML → Parse → Events → MIDI file."""

    def test_basic_compilation(self, tmp_path):
        """Test basic compilation with tempo, program change, and control changes."""
        mml_content = """---
title: "Test"
ppq: 480
---

[00:00.000]
- tempo 120
- pc 1.10

[00:01.000]
- cc 1.7.100

[+1b]
- cc 1.7.80
"""
        # Parse
        parser = MMDParser()
        doc = parser.parse_string(mml_content)

        assert len(doc.events) > 0

        # Expand and generate events
        expander = CommandExpander(ppq=480, tempo=120)
        expanded_dicts = expander.process_ast(doc.events)
        events = [
            MIDIEvent(
                time=d["time"],
                type=string_to_event_type(d["type"]),
                channel=d.get("channel", 0),
                data1=d.get("data1", 0),
                data2=d.get("data2", 0),
            )
            for d in expanded_dicts
        ]

        assert len(events) == 4  # tempo, pc, 2x cc
        assert events[0].type.name == "TEMPO"
        assert events[1].type.name == "PROGRAM_CHANGE"
        assert events[2].type.name == "CONTROL_CHANGE"
        assert events[3].type.name == "CONTROL_CHANGE"

        # Write MIDI file
        output_file = tmp_path / "test.mid"
        ir_program = create_ir_program(events=events, ppq=480, initial_tempo=120)
        midi_bytes = generate_midi_file(ir_program)
        output_file.write_bytes(midi_bytes)

        # Verify file exists
        assert output_file.exists()

        # Load and inspect MIDI file
        mid = mido.MidiFile(str(output_file))
        assert mid.ticks_per_beat == 480
        assert len(mid.tracks) == 1

        # Check messages
        track = mid.tracks[0]
        messages = [
            msg for msg in track if not isinstance(msg, mido.MetaMessage) or msg.type == "set_tempo"
        ]

        # Should have: tempo, pc, 2x cc, end_of_track
        assert len(messages) >= 4

        # Check tempo
        tempo_msgs = [
            msg for msg in messages if isinstance(msg, mido.MetaMessage) and msg.type == "set_tempo"
        ]
        assert len(tempo_msgs) == 1
        assert tempo_msgs[0].tempo == 500000  # 120 BPM

        # Check PC
        pc_msgs = [msg for msg in track if hasattr(msg, "type") and msg.type == "program_change"]
        assert len(pc_msgs) == 1
        assert pc_msgs[0].program == 10

        # Check CC
        cc_msgs = [msg for msg in track if hasattr(msg, "type") and msg.type == "control_change"]
        assert len(cc_msgs) == 2
        assert cc_msgs[0].control == 7
        assert cc_msgs[0].value == 100
        assert cc_msgs[1].value == 80

    def test_note_on_with_duration(self, tmp_path):
        """Test note_on with duration auto-generates note_off."""
        mml_content = """[00:00.000]
- note_on 1.C4 100 1b
"""
        parser = MMDParser()
        doc = parser.parse_string(mml_content)

        expander = CommandExpander(ppq=480, tempo=120)
        expanded_dicts = expander.process_ast(doc.events)
        events = [
            MIDIEvent(
                time=d["time"],
                type=string_to_event_type(d["type"]),
                channel=d.get("channel", 0),
                data1=d.get("data1", 0),
                data2=d.get("data2", 0),
            )
            for d in expanded_dicts
        ]

        # Should have note_on and auto-generated note_off
        assert len(events) == 2
        assert events[0].type.name == "NOTE_ON"
        assert events[1].type.name == "NOTE_OFF"

        # Check timing
        assert events[0].time == 0
        assert events[1].time == 480  # 1 beat = 480 ticks at ppq=480

        # Check note number (C4 = 60)
        assert events[0].data1 == 60
        assert events[1].data1 == 60

    def test_musical_timing(self, tmp_path):
        """Test musical time format (bar.beat.tick)."""
        mml_content = """[1.1.0]
- pc 1.10

[2.1.0]
- pc 1.11

[2.3.0]
- pc 1.12
"""
        parser = MMDParser()
        doc = parser.parse_string(mml_content)

        expander = CommandExpander(ppq=480, tempo=120)
        expanded_dicts = expander.process_ast(doc.events)
        events = [
            MIDIEvent(
                time=d["time"],
                type=string_to_event_type(d["type"]),
                channel=d.get("channel", 0),
                data1=d.get("data1", 0),
                data2=d.get("data2", 0),
            )
            for d in expanded_dicts
        ]

        assert len(events) == 3

        # Bar 1, beat 1 = 0 ticks
        assert events[0].time == 0

        # Bar 2, beat 1 = (2-1) * 4 beats * 480 ppq = 1920 ticks
        assert events[1].time == 1920

        # Bar 2, beat 3 = (2-1) * 4 beats * 480 + (3-1) * 480 = 2880 ticks
        assert events[2].time == 2880

    def test_relative_timing(self, tmp_path):
        """Test relative timing formats."""
        mml_content = """[00:00.000]
- pc 1.10
[+1b]
- pc 1.11
[+500ms]
- pc 1.12
"""
        parser = MMDParser()
        doc = parser.parse_string(mml_content)

        expander = CommandExpander(ppq=480, tempo=120)
        expanded_dicts = expander.process_ast(doc.events)
        events = [
            MIDIEvent(
                time=d["time"],
                type=string_to_event_type(d["type"]),
                channel=d.get("channel", 0),
                data1=d.get("data1", 0),
                data2=d.get("data2", 0),
            )
            for d in expanded_dicts
        ]

        assert len(events) == 3

        # First event at time 0
        assert events[0].time == 0

        # Second event +1 beat = +480 ticks
        assert events[1].time == 480

        # Third event +500ms at 120 BPM = +240 ticks (500ms * 120/60 * 480/1000)
        # Actually: 500ms = 0.5s, at 120 BPM = 2 beats/sec, so 0.5s = 1 beat = 480 ticks
        assert events[2].time == 960  # 480 + 480

    def test_simultaneous_timing(self, tmp_path):
        """Test simultaneous timing [@]."""
        mml_content = """[00:00.000]
- pc 1.10

[@]
- cc 1.7.100
"""
        parser = MMDParser()
        doc = parser.parse_string(mml_content)

        expander = CommandExpander(ppq=480, tempo=120)
        expanded_dicts = expander.process_ast(doc.events)
        events = [
            MIDIEvent(
                time=d["time"],
                type=string_to_event_type(d["type"]),
                channel=d.get("channel", 0),
                data1=d.get("data1", 0),
                data2=d.get("data2", 0),
            )
            for d in expanded_dicts
        ]

        assert len(events) == 2

        # Both events at same time
        assert events[0].time == events[1].time == 0

    def test_format_0_single_track_compilation(self, tmp_path):
        """Test Format 0 (single-track) MIDI file generation."""
        mml_content = """---
title: Format 0 Test
---
[00:00.000]
- tempo 120
- pc 1.5
- cc 1.7.100
[00:01.000]
- note_on 1.C4 100 500ms
"""
        # Parse
        parser = MMDParser()
        doc = parser.parse_string(mml_content)

        # Generate events
        expander = CommandExpander(ppq=480, tempo=120)
        expanded_dicts = expander.process_ast(doc.events)
        events = [
            MIDIEvent(
                time=d["time"],
                type=string_to_event_type(d["type"]),
                channel=d.get("channel", 0),
                data1=d.get("data1", 0),
                data2=d.get("data2", 0),
            )
            for d in expanded_dicts
        ]

        # Write MIDI file with format 0
        output_file = tmp_path / "format0.mid"
        ir_program = create_ir_program(events=events, ppq=480, initial_tempo=120)
        midi_bytes = generate_midi_file(ir_program, midi_format=0)
        output_file.write_bytes(midi_bytes)

        # Verify file exists
        assert output_file.exists()

        # Load and inspect MIDI file
        mid = mido.MidiFile(str(output_file))
        assert mid.type == 0  # Format 0
        assert mid.ticks_per_beat == 480
        assert len(mid.tracks) == 1  # Single track only

        # Verify all messages in single track
        track = mid.tracks[0]
        pc_msgs = [msg for msg in track if hasattr(msg, "type") and msg.type == "program_change"]
        cc_msgs = [msg for msg in track if hasattr(msg, "type") and msg.type == "control_change"]
        note_msgs = [
            msg for msg in track if hasattr(msg, "type") and msg.type in ["note_on", "note_off"]
        ]

        assert len(pc_msgs) == 1
        assert len(cc_msgs) == 1
        assert len(note_msgs) == 2  # note_on + note_off

    def test_format_2_independent_sequences(self, tmp_path):
        """Test Format 2 (independent sequences) MIDI file generation.

        Note: Current implementation creates single track for all formats.
        This test verifies the format type is set correctly.
        """
        mml_content = """---
title: Format 2 Test
---
[00:00.000]
- pc 1.0
- pc 2.0
[00:01.000]
- note_on 1.C4 100 1b
- note_on 2.D4 100 1b
"""
        # Parse
        parser = MMDParser()
        doc = parser.parse_string(mml_content)

        # Generate events
        expander = CommandExpander(ppq=480, tempo=120)
        expanded_dicts = expander.process_ast(doc.events)
        events = [
            MIDIEvent(
                time=d["time"],
                type=string_to_event_type(d["type"]),
                channel=d.get("channel", 0),
                data1=d.get("data1", 0),
                data2=d.get("data2", 0),
            )
            for d in expanded_dicts
        ]

        # Write MIDI file with format 2
        output_file = tmp_path / "format2.mid"
        ir_program = create_ir_program(events=events, ppq=480, initial_tempo=120)
        midi_bytes = generate_midi_file(ir_program, midi_format=2)
        output_file.write_bytes(midi_bytes)

        # Verify file exists
        assert output_file.exists()

        # Load and inspect MIDI file
        mid = mido.MidiFile(str(output_file))
        assert mid.type == 2  # Format 2
        assert mid.ticks_per_beat == 480

        # Note: Current implementation creates single track
        # In a full Format 2 implementation, there would be multiple independent tracks
        assert len(mid.tracks) >= 1


class TestTimingAccuracy:
    """Test timing accuracy in generated MIDI files."""

    def test_absolute_timing_accuracy(self, tmp_path):
        """Test absolute timing is converted to correct ticks."""
        mml_content = """---
ppq: 480
---
[00:00.000]
- pc 1.0
[00:01.500]
- pc 1.1
[00:03.250]
- pc 1.2
"""
        parser = MMDParser()
        doc = parser.parse_string(mml_content)

        expander = CommandExpander(ppq=480, tempo=120)
        expanded_dicts = expander.process_ast(doc.events)
        events = [
            MIDIEvent(
                time=d["time"],
                type=string_to_event_type(d["type"]),
                channel=d.get("channel", 0),
                data1=d.get("data1", 0),
                data2=d.get("data2", 0),
            )
            for d in expanded_dicts
        ]

        # Verify tick values
        # 00:00.000 = 0 ticks
        # 00:01.500 = 1.5 seconds * 480 ticks/beat * 2 beats/sec = 1440 ticks
        # 00:03.250 = 3.25 seconds * 480 * 2 = 3120 ticks
        assert events[0].time == 0
        assert events[1].time == 1440
        assert events[2].time == 3120

    def test_simultaneous_timing_accuracy(self, tmp_path):
        """Test simultaneous events have identical ticks."""
        mml_content = """[00:00.000]
- pc 1.0
[@]
- cc 1.7.100
[@]
- note_on 1.C4 100
"""
        parser = MMDParser()
        doc = parser.parse_string(mml_content)

        expander = CommandExpander(ppq=480, tempo=120)
        expanded_dicts = expander.process_ast(doc.events)
        events = [
            MIDIEvent(
                time=d["time"],
                type=string_to_event_type(d["type"]),
                channel=d.get("channel", 0),
                data1=d.get("data1", 0),
                data2=d.get("data2", 0),
            )
            for d in expanded_dicts
        ]

        # All three events should have same time
        assert events[0].time == events[1].time == events[2].time == 0


class TestMIDIMessageVerification:
    """Test various MIDI message types in generated .mid files."""

    def test_complete_midi_command_coverage(self, tmp_path):
        """Test all major MIDI message types in generated .mid file."""
        mml_content = """---
ppq: 480
---
[00:00.000]
- tempo 120
- pc 1.5
- cc 1.7.100
- note_on 1.C4 100 500ms
- pitch_bend 1.2000
- poly_pressure 1.C4.80
- channel_pressure 1.90
"""
        parser = MMDParser()
        doc = parser.parse_string(mml_content)

        expander = CommandExpander(ppq=480, tempo=120)
        expanded_dicts = expander.process_ast(doc.events)
        events = [
            MIDIEvent(
                time=d["time"],
                type=string_to_event_type(d["type"]),
                channel=d.get("channel", 0),
                data1=d.get("data1", 0),
                data2=d.get("data2", 0),
            )
            for d in expanded_dicts
        ]

        # Write MIDI file
        output_file = tmp_path / "complete.mid"
        ir_program = create_ir_program(events=events, ppq=480, initial_tempo=120)
        midi_bytes = generate_midi_file(ir_program)
        output_file.write_bytes(midi_bytes)

        # Verify file and messages
        mid = mido.MidiFile(str(output_file))
        track = mid.tracks[0]

        # Check tempo
        tempo_msgs = [
            msg for msg in track if isinstance(msg, mido.MetaMessage) and msg.type == "set_tempo"
        ]
        assert len(tempo_msgs) == 1
        assert tempo_msgs[0].tempo == 500000  # 120 BPM

        # Check PC
        pc_msgs = [msg for msg in track if hasattr(msg, "type") and msg.type == "program_change"]
        assert len(pc_msgs) == 1
        assert pc_msgs[0].program == 5

        # Check CC
        cc_msgs = [msg for msg in track if hasattr(msg, "type") and msg.type == "control_change"]
        assert len(cc_msgs) == 1
        assert cc_msgs[0].control == 7
        assert cc_msgs[0].value == 100

        # Check notes (note_on + note_off)
        note_msgs = [
            msg for msg in track if hasattr(msg, "type") and msg.type in ["note_on", "note_off"]
        ]
        assert len(note_msgs) == 2

        # Check pitch bend
        pb_msgs = [msg for msg in track if hasattr(msg, "type") and msg.type == "pitchwheel"]
        assert len(pb_msgs) == 1
        assert pb_msgs[0].pitch == 2000

        # Check polyphonic aftertouch
        poly_at_msgs = [msg for msg in track if hasattr(msg, "type") and msg.type == "polytouch"]
        assert len(poly_at_msgs) == 1
        assert poly_at_msgs[0].value == 80

        # Check channel aftertouch
        chan_at_msgs = [msg for msg in track if hasattr(msg, "type") and msg.type == "aftertouch"]
        assert len(chan_at_msgs) == 1
        assert chan_at_msgs[0].value == 90
