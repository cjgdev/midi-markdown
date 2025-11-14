"""
Specialized tests for multi-track timing calculations across MIDI formats 0, 1, and 2.

These tests verify that timing calculations remain correct when multi-track projects
are compiled to different MIDI file formats:
- Format 0: Single track (all events merged)
- Format 1: Multi-track synchronous (tracks play simultaneously)
- Format 2: Multi-track asynchronous (independent sequences)

Tests cover:
- Absolute timing across tracks
- Musical timing (bars.beats.ticks)
- Relative timing (deltas)
- Mixed timing paradigms
- Tempo changes
- Simultaneous events (@)
- Overlapping events
"""

import pytest
from mido import MidiFile

from midi_markdown.codegen.midi_file import generate_midi_file
from midi_markdown.core.compiler import compile_ast_to_ir
from midi_markdown.parser.parser import MMDParser


class TestMultiTrackAbsoluteTiming:
    """Test absolute timing (mm:ss.ms) across tracks in different MIDI formats."""

    @pytest.mark.integration
    def test_absolute_timing_format_0(self, parser: MMDParser):
        """Format 0: Verify absolute timing is preserved in single-track output."""
        mmd = """---
title: "Absolute Timing Test"
midi_format: 0
---

## Track 1: Control
@track control channel=1
[00:00.000]
- cc 1.7.100

[00:01.000]
- cc 1.7.80

## Track 2: Notes
@track notes channel=2
[00:00.500]
- note_on 2.60 100 500ms

[00:01.500]
- note_on 2.64 90 500ms
"""
        doc = parser.parse_string(mmd)
        ir_program = compile_ast_to_ir(doc, ppq=480)
        midi_bytes = generate_midi_file(ir_program, midi_format=0)

        # Parse generated MIDI to verify timing
        import io

        mid = MidiFile(file=io.BytesIO(midi_bytes))

        assert mid.type == 0  # Format 0
        assert mid.ticks_per_beat == 480

        # Collect all MIDI events with timing
        events = []
        current_tick = 0
        for msg in mid.tracks[0]:
            current_tick += msg.time
            if msg.type in ["control_change", "note_on", "note_off"]:
                events.append({"type": msg.type, "time": current_tick, "channel": msg.channel})

        # Verify timing (at 120 BPM, 480 PPQ)
        # 00:00.000 = 0 ticks
        # 00:00.500 = 480 ticks (0.5 seconds * 960 ticks/sec)
        # 00:01.000 = 960 ticks
        # 00:01.500 = 1440 ticks
        cc_events = [e for e in events if e["type"] == "control_change"]
        note_events = [e for e in events if e["type"] == "note_on"]

        assert len(cc_events) == 2
        assert cc_events[0]["time"] == 0  # 00:00.000
        assert cc_events[1]["time"] == 960  # 00:01.000

        assert len(note_events) == 2
        assert note_events[0]["time"] == 480  # 00:00.500
        assert note_events[1]["time"] == 1440  # 00:01.500

    @pytest.mark.integration
    def test_absolute_timing_format_1(self, parser: MMDParser):
        """Format 1: Verify absolute timing in multi-track synchronous output."""
        mmd = """---
title: "Absolute Timing Test"
midi_format: 1
---

## Track 1: Control
@track control channel=1
[00:00.000]
- cc 1.7.100

[00:02.000]
- cc 1.7.80

## Track 2: Notes
@track notes channel=2
[00:01.000]
- note_on 2.60 100 500ms

[00:03.000]
- note_on 2.64 90 500ms
"""
        doc = parser.parse_string(mmd)
        ir_program = compile_ast_to_ir(doc, ppq=480)
        midi_bytes = generate_midi_file(ir_program, midi_format=1)

        import io

        mid = MidiFile(file=io.BytesIO(midi_bytes))

        assert mid.type == 1  # Format 1

        # Verify timing is correct in the merged track
        events = []
        current_tick = 0
        for msg in mid.tracks[0]:
            current_tick += msg.time
            if msg.type in ["control_change", "note_on", "note_off"]:
                events.append({"type": msg.type, "time": current_tick, "channel": msg.channel})

        # At 120 BPM: 1 second = 960 ticks
        # 00:00.000 = 0
        # 00:01.000 = 960 (note_on)
        # 00:01.500 = 1440 (note_off after 500ms)
        # 00:02.000 = 1920
        # 00:03.000 = 2880 (note_on)
        # 00:03.500 = 3360 (note_off after 500ms)
        assert len(events) == 6
        assert events[0]["time"] == 0  # Track 1: 00:00.000 CC
        assert events[1]["time"] == 960  # Track 2: 00:01.000 note_on
        assert events[2]["time"] == 1440  # Track 2: 00:01.500 note_off (500ms duration)
        assert events[3]["time"] == 1920  # Track 1: 00:02.000 CC
        assert events[4]["time"] == 2880  # Track 2: 00:03.000 note_on
        assert events[5]["time"] == 3360  # Track 2: 00:03.500 note_off (500ms duration)

    @pytest.mark.integration
    def test_absolute_timing_format_2(self, parser: MMDParser):
        """Format 2: Verify absolute timing in multi-track asynchronous output."""
        mmd = """---
title: "Absolute Timing Test"
midi_format: 2
---

## Track 1: Control
@track control channel=1
[00:00.000]
- cc 1.7.100

[00:01.000]
- cc 1.7.80

## Track 2: Notes
@track notes channel=2
[00:00.000]
- note_on 2.60 100 1s

[00:02.000]
- note_on 2.64 90 1s
"""
        doc = parser.parse_string(mmd)
        ir_program = compile_ast_to_ir(doc, ppq=480)
        midi_bytes = generate_midi_file(ir_program, midi_format=2)

        import io

        mid = MidiFile(file=io.BytesIO(midi_bytes))

        assert mid.type == 2  # Format 2

        # Verify events are correctly timed
        events = []
        current_tick = 0
        for msg in mid.tracks[0]:
            current_tick += msg.time
            if msg.type in ["control_change", "note_on", "note_off"]:
                events.append({"type": msg.type, "time": current_tick, "channel": msg.channel})

        # Both tracks start at 00:00.000
        assert events[0]["time"] == 0  # Both channels at 0
        assert events[0]["channel"] in [0, 1]  # Either channel 1 or 2 (0-indexed)


class TestMultiTrackMusicalTiming:
    """Test musical timing (bars.beats.ticks) across tracks."""

    @pytest.mark.integration
    def test_musical_timing_format_0(self, parser: MMDParser):
        """Format 0: Verify musical timing is preserved."""
        mmd = """---
title: "Musical Timing Test"
midi_format: 0
tempo: 120
time_signature: [4, 4]
---

## Track 1: Bass
@track bass channel=2
[1.1.0]
- note_on 2.40 100 1b

[2.1.0]
- note_on 2.40 100 1b

## Track 2: Drums
@track drums channel=10
[1.1.0]
- note_on 10.36 100 100ms

[1.3.0]
- note_on 10.38 80 100ms
"""
        doc = parser.parse_string(mmd)
        ir_program = compile_ast_to_ir(doc, ppq=480)
        midi_bytes = generate_midi_file(ir_program, midi_format=0)

        import io

        mid = MidiFile(file=io.BytesIO(midi_bytes))

        # Collect events
        events = []
        current_tick = 0
        for msg in mid.tracks[0]:
            current_tick += msg.time
            if msg.type == "note_on" and msg.velocity > 0:
                events.append({"time": current_tick, "note": msg.note, "channel": msg.channel})

        # Musical timing at 4/4, 480 PPQ:
        # [1.1.0] = bar 1, beat 1 = 0 ticks
        # [1.3.0] = bar 1, beat 3 = 2 * 480 = 960 ticks
        # [2.1.0] = bar 2, beat 1 = 4 * 480 = 1920 ticks

        # Find bass and drum events
        bass_events = [e for e in events if e["channel"] == 1]  # Channel 2 = index 1
        drum_events = [e for e in events if e["channel"] == 9]  # Channel 10 = index 9

        assert len(bass_events) == 2
        assert bass_events[0]["time"] == 0  # [1.1.0]
        assert bass_events[1]["time"] == 1920  # [2.1.0]

        assert len(drum_events) == 2
        assert drum_events[0]["time"] == 0  # [1.1.0]
        assert drum_events[1]["time"] == 960  # [1.3.0]

    @pytest.mark.integration
    def test_musical_timing_format_1(self, parser: MMDParser):
        """Format 1: Verify musical timing with multiple tracks."""
        mmd = """---
title: "Musical Timing Format 1"
midi_format: 1
tempo: 140
time_signature: [4, 4]
---

## Track 1: Chords
@track chords channel=1
[1.1.0]
- note_on 1.60 80 2b
- note_on 1.64 80 2b
- note_on 1.67 80 2b

[3.1.0]
- note_on 1.62 80 2b
- note_on 1.65 80 2b
- note_on 1.69 80 2b

## Track 2: Melody
@track melody channel=3
[2.1.0]
- note_on 3.72 100 1b

[2.3.0]
- note_on 3.74 100 1b
"""
        doc = parser.parse_string(mmd)
        ir_program = compile_ast_to_ir(doc, ppq=480)
        midi_bytes = generate_midi_file(ir_program, midi_format=1)

        import io

        mid = MidiFile(file=io.BytesIO(midi_bytes))

        assert mid.type == 1

        # Verify musical timing is correct
        events = []
        current_tick = 0
        for msg in mid.tracks[0]:
            current_tick += msg.time
            if msg.type == "note_on" and msg.velocity > 0:
                events.append({"time": current_tick, "channel": msg.channel})

        # [1.1.0] = 0 ticks
        # [2.1.0] = 4 beats * 480 = 1920 ticks
        # [2.3.0] = 6 beats * 480 = 2880 ticks
        # [3.1.0] = 8 beats * 480 = 3840 ticks

        # First three events should be at tick 0 (simultaneous chord)
        assert events[0]["time"] == 0
        assert events[1]["time"] == 0
        assert events[2]["time"] == 0

        # Melody starts at bar 2
        melody_events = [e for e in events if e["channel"] == 2]  # Channel 3 = index 2
        assert len(melody_events) == 2
        assert melody_events[0]["time"] == 1920  # [2.1.0]
        assert melody_events[1]["time"] == 2880  # [2.3.0]

    @pytest.mark.integration
    def test_musical_timing_format_2(self, parser: MMDParser):
        """Format 2: Verify musical timing in asynchronous format."""
        mmd = """---
title: "Musical Timing Format 2"
midi_format: 2
tempo: 120
time_signature: [3, 4]
---

## Track 1: Waltz Bass
@track bass channel=2
[1.1.0]
- note_on 2.40 100 1b

[1.2.0]
- note_on 2.40 80 1b

[1.3.0]
- note_on 2.40 80 1b

## Track 2: Melody
@track melody channel=1
[1.1.0]
- note_on 1.60 90 3b
"""
        doc = parser.parse_string(mmd)
        ir_program = compile_ast_to_ir(doc, ppq=480)
        midi_bytes = generate_midi_file(ir_program, midi_format=2)

        import io

        mid = MidiFile(file=io.BytesIO(midi_bytes))

        assert mid.type == 2

        # In 3/4 time: each beat is 480 ticks
        # [1.1.0] = 0
        # [1.2.0] = 480
        # [1.3.0] = 960
        events = []
        current_tick = 0
        for msg in mid.tracks[0]:
            current_tick += msg.time
            if msg.type == "note_on" and msg.velocity > 0:
                events.append({"time": current_tick, "note": msg.note, "channel": msg.channel})

        # Verify 3/4 timing
        bass_events = [e for e in events if e["note"] == 40]
        assert len(bass_events) == 3
        assert bass_events[0]["time"] == 0  # [1.1.0]
        assert bass_events[1]["time"] == 480  # [1.2.0]
        assert bass_events[2]["time"] == 960  # [1.3.0]


class TestMultiTrackRelativeTiming:
    """Test relative timing (+duration) across tracks."""

    @pytest.mark.integration
    def test_relative_timing_format_0(self, parser: MMDParser):
        """Format 0: Verify relative timing is independent per track."""
        mmd = """---
title: "Relative Timing Test"
midi_format: 0
---

## Track 1
@track track1 channel=1
[00:00.000]
- cc 1.7.100
[+500ms]
- cc 1.7.80
[+500ms]
- cc 1.7.60

## Track 2
@track track2 channel=2
[00:00.000]
- cc 2.10.64
[+1s]
- cc 2.10.32
[+1s]
- cc 2.10.0
"""
        doc = parser.parse_string(mmd)
        ir_program = compile_ast_to_ir(doc, ppq=480)
        midi_bytes = generate_midi_file(ir_program, midi_format=0)

        import io

        mid = MidiFile(file=io.BytesIO(midi_bytes))

        events = []
        current_tick = 0
        for msg in mid.tracks[0]:
            current_tick += msg.time
            if msg.type == "control_change":
                events.append({"time": current_tick, "channel": msg.channel, "value": msg.value})

        # Track 1: 0, 500ms (480 ticks), 1000ms (960 ticks)
        # Track 2: 0, 1s (960 ticks), 2s (1920 ticks)
        track1_events = [e for e in events if e["channel"] == 0]
        track2_events = [e for e in events if e["channel"] == 1]

        assert len(track1_events) == 3
        assert track1_events[0]["time"] == 0
        assert track1_events[1]["time"] == 480  # +500ms
        assert track1_events[2]["time"] == 960  # +500ms

        assert len(track2_events) == 3
        assert track2_events[0]["time"] == 0
        assert track2_events[1]["time"] == 960  # +1s
        assert track2_events[2]["time"] == 1920  # +1s

    @pytest.mark.integration
    def test_relative_timing_format_1(self, parser: MMDParser):
        """Format 1: Verify relative timing with beats."""
        mmd = """---
title: "Relative Timing Beats"
midi_format: 1
tempo: 120
---

## Track 1
@track track1 channel=1
[00:00.000]
- note_on 1.60 100 1b
[+1b]
- note_on 1.62 100 1b
[+1b]
- note_on 1.64 100 1b

## Track 2
@track track2 channel=2
[00:00.000]
- note_on 2.48 80 2b
[+2b]
- note_on 2.50 80 2b
"""
        doc = parser.parse_string(mmd)
        ir_program = compile_ast_to_ir(doc, ppq=480)
        midi_bytes = generate_midi_file(ir_program, midi_format=1)

        import io

        mid = MidiFile(file=io.BytesIO(midi_bytes))

        events = []
        current_tick = 0
        for msg in mid.tracks[0]:
            current_tick += msg.time
            if msg.type == "note_on" and msg.velocity > 0:
                events.append({"time": current_tick, "note": msg.note, "channel": msg.channel})

        # Track 1: 0, +480 (1b), +480 (1b) = 0, 480, 960
        # Track 2: 0, +960 (2b) = 0, 960
        track1_events = [e for e in events if e["channel"] == 0]
        track2_events = [e for e in events if e["channel"] == 1]

        assert len(track1_events) == 3
        assert track1_events[0]["time"] == 0
        assert track1_events[1]["time"] == 480
        assert track1_events[2]["time"] == 960

        assert len(track2_events) == 2
        assert track2_events[0]["time"] == 0
        assert track2_events[1]["time"] == 960


class TestMultiTrackSimultaneousTiming:
    """Test simultaneous timing (@) across tracks."""

    @pytest.mark.integration
    def test_simultaneous_events_format_0(self, parser: MMDParser):
        """Format 0: Verify @ timing works across tracks."""
        mmd = """---
title: "Simultaneous Events"
midi_format: 0
---

## Track 1: Chords
@track chords channel=1
[00:00.000]
- note_on 1.60 80 2s
[@]
- note_on 1.64 80 2s
[@]
- note_on 1.67 80 2s

## Track 2: Bass
@track bass channel=2
[00:00.000]
- note_on 2.36 100 2s
"""
        doc = parser.parse_string(mmd)
        ir_program = compile_ast_to_ir(doc, ppq=480)
        midi_bytes = generate_midi_file(ir_program, midi_format=0)

        import io

        mid = MidiFile(file=io.BytesIO(midi_bytes))

        events = []
        current_tick = 0
        for msg in mid.tracks[0]:
            current_tick += msg.time
            if msg.type == "note_on" and msg.velocity > 0:
                events.append({"time": current_tick, "note": msg.note, "channel": msg.channel})

        # All note_on events should be at tick 0
        assert len(events) == 4
        for event in events:
            assert event["time"] == 0

    @pytest.mark.integration
    def test_simultaneous_events_format_1(self, parser: MMDParser):
        """Format 1: Verify @ timing in multi-track format."""
        mmd = """---
title: "Simultaneous Multi-Track"
midi_format: 1
tempo: 120
---

## Track 1
@track track1 channel=1
[00:02.000]
- cc 1.7.100
[@]
- cc 1.10.64
[@]
- cc 1.11.127

## Track 2
@track track2 channel=2
[00:02.000]
- cc 2.7.80
[@]
- cc 2.10.32
"""
        doc = parser.parse_string(mmd)
        ir_program = compile_ast_to_ir(doc, ppq=480)
        midi_bytes = generate_midi_file(ir_program, midi_format=1)

        import io

        mid = MidiFile(file=io.BytesIO(midi_bytes))

        events = []
        current_tick = 0
        for msg in mid.tracks[0]:
            current_tick += msg.time
            if msg.type == "control_change":
                events.append(
                    {"time": current_tick, "channel": msg.channel, "control": msg.control}
                )

        # All CC events should be at 00:02.000 = 1920 ticks
        assert len(events) == 5
        for event in events:
            assert event["time"] == 1920


class TestMultiTrackTempoChanges:
    """Test tempo changes affect timing correctly across all formats."""

    @pytest.mark.integration
    def test_tempo_changes_format_0(self, parser: MMDParser):
        """Format 0: Verify tempo changes affect all tracks."""
        mmd = """---
title: "Tempo Changes"
midi_format: 0
---

## Track 1: Control
@track control channel=1
[00:00.000]
- tempo 120
- cc 1.7.100

[00:02.000]
- tempo 60
- cc 1.7.80

[00:04.000]
- cc 1.7.60

## Track 2: Notes
@track notes channel=2
[00:00.000]
- note_on 2.60 100 500ms

[00:02.000]
- note_on 2.64 90 500ms

[00:04.000]
- note_on 2.67 80 500ms
"""
        doc = parser.parse_string(mmd)
        ir_program = compile_ast_to_ir(doc, ppq=480)
        midi_bytes = generate_midi_file(ir_program, midi_format=0)

        import io

        mid = MidiFile(file=io.BytesIO(midi_bytes))

        # Find tempo messages
        tempo_changes = []
        current_tick = 0
        for msg in mid.tracks[0]:
            current_tick += msg.time
            if msg.type == "set_tempo":
                tempo_changes.append({"time": current_tick, "tempo": msg.tempo})

        # Verify tempo changes are present
        assert len(tempo_changes) >= 2

        # First tempo at 00:00.000
        assert tempo_changes[0]["time"] == 0

        # Second tempo at 00:02.000 (1920 ticks at 120 BPM)
        assert tempo_changes[1]["time"] == 1920

    @pytest.mark.integration
    def test_tempo_changes_format_1(self, parser: MMDParser):
        """Format 1: Verify tempo changes in multi-track."""
        mmd = """---
title: "Tempo Changes Multi-Track"
midi_format: 1
tempo: 100
---

## Track 1
@track track1 channel=1
[00:00.000]
- note_on 1.60 100 1b

[00:02.000]
- tempo 140
- note_on 1.62 100 1b

[00:04.000]
- note_on 1.64 100 1b

## Track 2
@track track2 channel=2
[00:01.000]
- note_on 2.48 80 1b

[00:03.000]
- note_on 2.50 80 1b
"""
        doc = parser.parse_string(mmd)
        ir_program = compile_ast_to_ir(doc, ppq=480)
        midi_bytes = generate_midi_file(ir_program, midi_format=1)

        import io

        mid = MidiFile(file=io.BytesIO(midi_bytes))

        # Collect events
        events = []
        current_tick = 0
        for msg in mid.tracks[0]:
            current_tick += msg.time
            if msg.type in ["note_on", "set_tempo"]:
                events.append({"type": msg.type, "time": current_tick})

        # Verify tempo change is in the timeline
        tempo_events = [e for e in events if e["type"] == "set_tempo"]
        assert len(tempo_events) >= 1


class TestMultiTrackOverlappingEvents:
    """Test overlapping events across tracks."""

    @pytest.mark.integration
    def test_overlapping_notes_format_0(self, parser: MMDParser):
        """Format 0: Verify overlapping notes across tracks."""
        mmd = """---
title: "Overlapping Notes"
midi_format: 0
---

## Track 1: Long note
@track sustain channel=1
[00:00.000]
- note_on 1.60 100 4s

## Track 2: Short notes
@track melody channel=2
[00:00.000]
- note_on 2.72 90 500ms

[00:01.000]
- note_on 2.74 90 500ms

[00:02.000]
- note_on 2.76 90 500ms
"""
        doc = parser.parse_string(mmd)
        ir_program = compile_ast_to_ir(doc, ppq=480)
        midi_bytes = generate_midi_file(ir_program, midi_format=0)

        import io

        mid = MidiFile(file=io.BytesIO(midi_bytes))

        # Collect all note_on events
        # Note: Current implementation does not generate note_off events
        events = []
        current_tick = 0
        for msg in mid.tracks[0]:
            current_tick += msg.time
            if msg.type == "note_on":
                events.append({"time": current_tick, "note": msg.note, "channel": msg.channel})

        # Verify we have 4 note_on events
        assert len(events) == 4

        # Find sustained note (note 60 on channel 1)
        sustain_events = [e for e in events if e["note"] == 60]
        assert len(sustain_events) == 1
        assert sustain_events[0]["time"] == 0

        # Verify melody notes (channel 2)
        melody_events = [e for e in events if e["channel"] == 1]  # Channel 2 = index 1
        assert len(melody_events) == 3
        assert melody_events[0]["time"] == 0
        assert melody_events[1]["time"] == 960
        assert melody_events[2]["time"] == 1920

    @pytest.mark.integration
    def test_overlapping_notes_format_1(self, parser: MMDParser):
        """Format 1: Verify overlapping in multi-track format."""
        mmd = """---
title: "Overlapping Multi-Track"
midi_format: 1
---

## Track 1: Pad
@track pad channel=1
[00:00.000]
- note_on 1.48 70 8s

## Track 2: Bass
@track bass channel=2
[00:00.000]
- note_on 2.36 100 1s
[+1s]
- note_on 2.36 100 1s
[+1s]
- note_on 2.36 100 1s

## Track 3: Melody
@track melody channel=3
[00:02.000]
- note_on 3.72 90 500ms
[+500ms]
- note_on 3.74 90 500ms
"""
        doc = parser.parse_string(mmd)
        ir_program = compile_ast_to_ir(doc, ppq=480)
        midi_bytes = generate_midi_file(ir_program, midi_format=1)

        import io

        mid = MidiFile(file=io.BytesIO(midi_bytes))

        # Verify all three channels have events
        events = []
        current_tick = 0
        for msg in mid.tracks[0]:
            current_tick += msg.time
            if msg.type == "note_on" and msg.velocity > 0:
                events.append({"time": current_tick, "channel": msg.channel})

        # Verify we have events from all three channels
        channels = {e["channel"] for e in events}
        assert len(channels) == 3
        assert 0 in channels  # Channel 1
        assert 1 in channels  # Channel 2
        assert 2 in channels  # Channel 3


class TestMultiTrackMixedTimingParadigms:
    """Test mixed timing paradigms across tracks."""

    @pytest.mark.integration
    def test_mixed_timing_format_0(self, parser: MMDParser):
        """Format 0: Mix absolute, musical, and relative timing."""
        mmd = """---
title: "Mixed Timing"
midi_format: 0
tempo: 120
time_signature: [4, 4]
---

## Track 1: Absolute timing
@track absolute channel=1
[00:00.000]
- cc 1.7.100
[00:02.000]
- cc 1.7.80

## Track 2: Musical timing
@track musical channel=2
[1.1.0]
- note_on 2.60 100 1b
[2.1.0]
- note_on 2.62 100 1b

## Track 3: Relative timing
@track relative channel=3
[00:00.000]
- note_on 3.72 90 500ms
[+500ms]
- note_on 3.74 90 500ms
[+500ms]
- note_on 3.76 90 500ms
"""
        doc = parser.parse_string(mmd)
        ir_program = compile_ast_to_ir(doc, ppq=480)
        midi_bytes = generate_midi_file(ir_program, midi_format=0)

        import io

        mid = MidiFile(file=io.BytesIO(midi_bytes))

        # Verify events from all three timing paradigms
        events = []
        current_tick = 0
        for msg in mid.tracks[0]:
            current_tick += msg.time
            if msg.type in ["control_change", "note_on"]:
                events.append({"type": msg.type, "time": current_tick, "channel": msg.channel})

        # Track 1 (absolute): 0, 1920 ticks
        track1_events = [e for e in events if e["channel"] == 0]
        assert len(track1_events) == 2
        assert track1_events[0]["time"] == 0
        assert track1_events[1]["time"] == 1920

        # Track 2 (musical): 0 ([1.1.0]), 1920 ([2.1.0])
        track2_events = [e for e in events if e["channel"] == 1]
        assert len(track2_events) == 2
        assert track2_events[0]["time"] == 0
        assert track2_events[1]["time"] == 1920

        # Track 3 (relative): 0, 480, 960
        track3_events = [e for e in events if e["channel"] == 2]
        assert len(track3_events) == 3
        assert track3_events[0]["time"] == 0
        assert track3_events[1]["time"] == 480
        assert track3_events[2]["time"] == 960

    @pytest.mark.integration
    def test_mixed_timing_format_1(self, parser: MMDParser):
        """Format 1: Mix all timing paradigms in multi-track."""
        mmd = """---
title: "Mixed Timing Multi-Track"
midi_format: 1
tempo: 140
time_signature: [3, 4]
---

## Track 1: Absolute
@track absolute channel=1
[00:00.000]
- note_on 1.60 80 1s
[00:01.500]
- note_on 1.62 80 1s

## Track 2: Musical
@track musical channel=2
[1.1.0]
- note_on 2.48 100 1b
[2.1.0]
- note_on 2.50 100 1b

## Track 3: Relative
@track relative channel=3
[00:00.000]
- note_on 3.72 90 500ms
[+250ms]
- note_on 3.74 90 500ms
[+250ms]
- note_on 3.76 90 500ms

## Track 4: Simultaneous
@track simultaneous channel=4
[00:00.000]
- cc 4.7.100
[@]
- cc 4.10.64
[@]
- cc 4.11.127
"""
        doc = parser.parse_string(mmd)
        ir_program = compile_ast_to_ir(doc, ppq=480)
        midi_bytes = generate_midi_file(ir_program, midi_format=1)

        import io

        mid = MidiFile(file=io.BytesIO(midi_bytes))

        assert mid.type == 1

        # Verify all channels have events
        events = []
        current_tick = 0
        for msg in mid.tracks[0]:
            current_tick += msg.time
            if msg.type in ["note_on", "control_change"]:
                if msg.type == "note_on" and msg.velocity == 0:
                    continue  # Skip note_off as note_on velocity 0
                events.append({"type": msg.type, "time": current_tick, "channel": msg.channel})

        # Verify we have events from all 4 channels
        channels = {e["channel"] for e in events}
        assert 0 in channels  # Channel 1
        assert 1 in channels  # Channel 2
        assert 2 in channels  # Channel 3
        assert 3 in channels  # Channel 4

        # Verify simultaneous events are at time 0
        simultaneous_events = [
            e for e in events if e["channel"] == 3 and e["type"] == "control_change"
        ]
        assert len(simultaneous_events) == 3
        for event in simultaneous_events:
            assert event["time"] == 0


class TestMultiTrackEdgeCases:
    """Test edge cases for multi-track timing."""

    @pytest.mark.integration
    def test_empty_track_format_0(self, parser: MMDParser):
        """Format 0: Handle empty tracks gracefully."""
        mmd = """---
title: "Empty Track"
midi_format: 0
---

## Track 1: Has events
@track active channel=1
[00:00.000]
- cc 1.7.100

## Track 2: Empty
@track empty channel=2

## Track 3: Has events
@track active2 channel=3
[00:01.000]
- cc 3.10.64
"""
        doc = parser.parse_string(mmd)
        ir_program = compile_ast_to_ir(doc, ppq=480)
        midi_bytes = generate_midi_file(ir_program, midi_format=0)

        import io

        mid = MidiFile(file=io.BytesIO(midi_bytes))

        # Should only have events from tracks 1 and 3
        events = []
        for msg in mid.tracks[0]:
            if msg.type == "control_change":
                events.append({"channel": msg.channel})

        assert len(events) == 2
        channels = {e["channel"] for e in events}
        assert 0 in channels  # Channel 1
        assert 2 in channels  # Channel 3
        assert 1 not in channels  # Channel 2 (empty)

    @pytest.mark.integration
    def test_single_event_per_track_format_1(self, parser: MMDParser):
        """Format 1: Single event per track."""
        mmd = """---
title: "Single Events"
midi_format: 1
---

@track track1 channel=1
[00:00.000]
- cc 1.7.127

@track track2 channel=2
[00:01.000]
- cc 2.10.64

@track track3 channel=3
[00:02.000]
- cc 3.11.100
"""
        doc = parser.parse_string(mmd)
        ir_program = compile_ast_to_ir(doc, ppq=480)
        midi_bytes = generate_midi_file(ir_program, midi_format=1)

        import io

        mid = MidiFile(file=io.BytesIO(midi_bytes))

        # Verify three events at different times
        events = []
        current_tick = 0
        for msg in mid.tracks[0]:
            current_tick += msg.time
            if msg.type == "control_change":
                events.append({"time": current_tick, "channel": msg.channel})

        assert len(events) == 3
        assert events[0]["time"] == 0  # 00:00.000
        assert events[1]["time"] == 960  # 00:01.000
        assert events[2]["time"] == 1920  # 00:02.000

    @pytest.mark.integration
    def test_many_tracks_format_2(self, parser: MMDParser):
        """Format 2: Handle many tracks."""
        # Create MMD with 8 tracks
        tracks = []
        for i in range(1, 9):
            tracks.append(f"""
@track track{i} channel={i}
[00:00.000]
- cc {i}.7.{i * 10}
[00:0{i}.000]
- cc {i}.10.{i * 10}
""")

        mmd = f"""---
title: "Many Tracks"
midi_format: 2
---

{"".join(tracks)}
"""
        doc = parser.parse_string(mmd)
        ir_program = compile_ast_to_ir(doc, ppq=480)
        midi_bytes = generate_midi_file(ir_program, midi_format=2)

        import io

        mid = MidiFile(file=io.BytesIO(midi_bytes))

        assert mid.type == 2

        # Verify events from all 8 channels
        events = []
        for msg in mid.tracks[0]:
            if msg.type == "control_change":
                events.append({"channel": msg.channel})

        channels = {e["channel"] for e in events}
        assert len(channels) == 8
        for i in range(8):
            assert i in channels  # Channels 0-7 (1-8 in MMD)
