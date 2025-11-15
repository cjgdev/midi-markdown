"""
Test Suite: Multi-Track Compilation

Tests for multi-track MMD file compilation, event generation, and timing validation.
This test suite exposes and validates fixes for multi-track timing bugs.
"""

from midi_markdown.core.compiler import compile_ast_to_ir
from midi_markdown.parser.parser import MMDParser


class TestMultiTrackBasics:
    """Test basic multi-track compilation."""

    def test_single_track_compilation(self):
        """Test that a single @track block compiles correctly."""
        parser = MMDParser()
        mml = """---
title: "Single Track Test"
---

@track drums channel=10
[00:00.000]
- note_on 10.36 100 1b

[00:01.000]
- note_on 10.38 90 1b
"""
        doc = parser.parse_string(mml)
        ir = compile_ast_to_ir(doc, ppq=480)

        # Should have 4 events: 2 note_on + 2 note_off
        note_events = [e for e in ir.events if e.type.name in ("NOTE_ON", "NOTE_OFF")]
        assert len(note_events) == 4, f"Expected 4 note events, got {len(note_events)}"

        # Verify timing
        note_on_events = [e for e in note_events if e.type.name == "NOTE_ON"]
        assert len(note_on_events) == 2

        # First note should be at time 0
        assert note_on_events[0].time == 0, f"First note at {note_on_events[0].time}, expected 0"

        # Second note should be at 1 second (120 BPM default, 480 PPQ)
        # 1 second = 960 ticks at 120 BPM
        expected_time = 960
        assert note_on_events[1].time == expected_time, (
            f"Second note at {note_on_events[1].time}, expected {expected_time}"
        )

    def test_two_tracks_compilation(self):
        """Test that two @track blocks compile with correct timing."""
        parser = MMDParser()
        mml = """---
title: "Two Track Test"
---

@track drums channel=10
[00:00.000]
- note_on 10.36 100 500ms

@track bass channel=2
[00:00.000]
- note_on 2.40 90 500ms
"""
        doc = parser.parse_string(mml)
        ir = compile_ast_to_ir(doc, ppq=480)

        # Should have 4 events total: 2 note_on + 2 note_off
        note_events = [e for e in ir.events if e.type.name in ("NOTE_ON", "NOTE_OFF")]
        assert len(note_events) == 4, f"Expected 4 note events, got {len(note_events)}"

        # Verify channels
        note_on_events = [e for e in note_events if e.type.name == "NOTE_ON"]
        channels = {e.channel for e in note_on_events}
        assert channels == {10, 2}, f"Expected channels {{10, 2}}, got {channels}"

        # Both should start at time 0
        for event in note_on_events:
            assert event.time == 0, f"Event on channel {event.channel} at {event.time}, expected 0"

    def test_three_tracks_with_staggered_timing(self):
        """Test three tracks with staggered start times."""
        parser = MMDParser()
        mml = """---
title: "Staggered Tracks"
---

@track drums channel=10
[00:00.000]
- note_on 10.36 100 100ms

@track bass channel=2
[00:01.000]
- note_on 2.40 90 100ms

@track lead channel=1
[00:02.000]
- note_on 1.60 85 100ms
"""
        doc = parser.parse_string(mml)
        ir = compile_ast_to_ir(doc, ppq=480)

        note_on_events = sorted(
            [e for e in ir.events if e.type.name == "NOTE_ON"], key=lambda e: e.time
        )

        assert len(note_on_events) == 3, f"Expected 3 note_on events, got {len(note_on_events)}"

        # At 120 BPM, 480 PPQ: 1 second = 960 ticks
        assert note_on_events[0].time == 0, f"First event at {note_on_events[0].time}, expected 0"
        assert note_on_events[0].channel == 10

        assert note_on_events[1].time == 960, (
            f"Second event at {note_on_events[1].time}, expected 960"
        )
        assert note_on_events[1].channel == 2

        assert note_on_events[2].time == 1920, (
            f"Third event at {note_on_events[2].time}, expected 1920"
        )
        assert note_on_events[2].channel == 1


class TestMultiTrackTiming:
    """Test multi-track timing scenarios."""

    def test_overlapping_events_different_tracks(self):
        """Test that events in different tracks can overlap in time."""
        parser = MMDParser()
        mml = """---
title: "Overlapping Events"
---

@track track1 channel=1
[00:00.000]
- cc 1.7.100
[00:01.000]
- cc 1.7.80

@track track2 channel=2
[00:00.500]
- cc 2.10.64
[00:01.500]
- cc 2.10.32
"""
        doc = parser.parse_string(mml)
        ir = compile_ast_to_ir(doc, ppq=480)

        cc_events = sorted(
            [e for e in ir.events if e.type.name == "CONTROL_CHANGE"],
            key=lambda e: (e.time, e.channel),
        )

        assert len(cc_events) == 4, f"Expected 4 CC events, got {len(cc_events)}"

        # At 120 BPM: 0.5s = 480 ticks, 1s = 960 ticks, 1.5s = 1440 ticks
        assert cc_events[0].time == 0
        assert cc_events[0].channel == 1

        assert cc_events[1].time == 480
        assert cc_events[1].channel == 2

        assert cc_events[2].time == 960
        assert cc_events[2].channel == 1

        assert cc_events[3].time == 1440
        assert cc_events[3].channel == 2

    def test_musical_timing_in_tracks(self):
        """Test musical timing (bars.beats.ticks) in multi-track files."""
        parser = MMDParser()
        mml = """---
title: "Musical Timing Multi-Track"
tempo: 120
time_signature: [4, 4]
---

@track track1 channel=1
[1.1.0]
- note_on 1.60 100 1b

[2.1.0]
- note_on 1.62 100 1b

@track track2 channel=2
[1.3.0]
- note_on 2.40 90 1b

[2.3.0]
- note_on 2.42 90 1b
"""
        doc = parser.parse_string(mml)
        ir = compile_ast_to_ir(doc, ppq=480)

        note_on_events = sorted(
            [e for e in ir.events if e.type.name == "NOTE_ON"], key=lambda e: e.time
        )

        assert len(note_on_events) == 4

        # Bar 1, Beat 1 = 0 ticks
        assert note_on_events[0].time == 0
        assert note_on_events[0].channel == 1

        # Bar 1, Beat 3 = 2 beats = 960 ticks
        assert note_on_events[1].time == 960
        assert note_on_events[1].channel == 2

        # Bar 2, Beat 1 = 4 beats = 1920 ticks
        assert note_on_events[2].time == 1920
        assert note_on_events[2].channel == 1

        # Bar 2, Beat 3 = 6 beats = 2880 ticks
        assert note_on_events[3].time == 2880
        assert note_on_events[3].channel == 2

    def test_relative_timing_in_tracks(self):
        """Test relative timing within tracks."""
        parser = MMDParser()
        mml = """---
title: "Relative Timing in Tracks"
---

@track track1 channel=1
[00:00.000]
- cc 1.7.100
[+500ms]
- cc 1.7.80
[+500ms]
- cc 1.7.60

@track track2 channel=2
[00:00.000]
- cc 2.10.64
[+1s]
- cc 2.10.32
"""
        doc = parser.parse_string(mml)
        ir = compile_ast_to_ir(doc, ppq=480)

        cc_events = sorted(
            [e for e in ir.events if e.type.name == "CONTROL_CHANGE"],
            key=lambda e: (e.time, e.channel),
        )

        assert len(cc_events) == 5

        # Track 1: 0ms, 500ms, 1000ms
        # Track 2: 0ms, 1000ms
        # Sorted: 0 (ch1), 0 (ch2), 500 (ch1), 1000 (ch1), 1000 (ch2)

        # At 120 BPM: 500ms = 480 ticks, 1s = 960 ticks
        assert cc_events[0].time == 0
        assert cc_events[0].channel == 1
        assert cc_events[1].time == 0
        assert cc_events[1].channel == 2
        assert cc_events[2].time == 480
        assert cc_events[2].channel == 1
        assert cc_events[3].time == 960
        assert cc_events[3].channel == 1
        assert cc_events[4].time == 960
        assert cc_events[4].channel == 2


class TestMultiTrackWithTopLevelEvents:
    """Test multi-track files that also have top-level events."""

    def test_tracks_and_top_level_events(self):
        """Test that both @track events and top-level events are included."""
        parser = MMDParser()
        mml = """---
title: "Mixed Events"
---

# Top-level tempo event
[00:00.000]
- tempo 140

@track drums channel=10
[00:00.000]
- note_on 10.36 100 1b

@track bass channel=2
[00:00.000]
- note_on 2.40 90 1b
"""
        doc = parser.parse_string(mml)
        ir = compile_ast_to_ir(doc, ppq=480)

        # Should have tempo event + note events
        tempo_events = [e for e in ir.events if e.type.name == "TEMPO"]
        note_events = [e for e in ir.events if e.type.name in ("NOTE_ON", "NOTE_OFF")]

        assert len(tempo_events) == 1, f"Expected 1 tempo event, got {len(tempo_events)}"
        assert len(note_events) == 4, f"Expected 4 note events, got {len(note_events)}"

        # Tempo should be at time 0
        assert tempo_events[0].time == 0


class TestMultiTrackEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_track(self):
        """Test that empty tracks don't cause errors."""
        parser = MMDParser()
        mml = """---
title: "Empty Track"
---

@track empty channel=1

@track filled channel=2
[00:00.000]
- note_on 2.40 90 1b
"""
        doc = parser.parse_string(mml)
        ir = compile_ast_to_ir(doc, ppq=480)

        note_events = [e for e in ir.events if e.type.name in ("NOTE_ON", "NOTE_OFF")]
        assert len(note_events) == 2  # Only events from filled track

    def test_track_with_loops(self):
        """Test @loop directives within tracks."""
        parser = MMDParser()
        mml = """---
title: "Track with Loop"
---

@track drums channel=10
@loop 4 times at [00:00.000] every 1b
  - note_on 10.36 100 100ms
@end
"""
        doc = parser.parse_string(mml)
        ir = compile_ast_to_ir(doc, ppq=480)

        note_on_events = [e for e in ir.events if e.type.name == "NOTE_ON"]
        # Should have 4 note_on events from the loop
        assert len(note_on_events) == 4

        # Verify spacing (1 beat = 480 ticks at 120 BPM)
        for i, event in enumerate(sorted(note_on_events, key=lambda e: e.time)):
            expected_time = i * 480
            assert event.time == expected_time, (
                f"Event {i} at {event.time}, expected {expected_time}"
            )

    def test_simultaneous_timing_in_tracks(self):
        """Test simultaneous [@] timing marker in tracks."""
        parser = MMDParser()
        mml = """---
title: "Simultaneous Events in Tracks"
---

@track track1 channel=1
[00:00.000]
- cc 1.7.100
[@]
- cc 1.10.64

@track track2 channel=2
[00:01.000]
- cc 2.7.80
[@]
- cc 2.10.32
"""
        doc = parser.parse_string(mml)
        ir = compile_ast_to_ir(doc, ppq=480)

        cc_events = sorted(
            [e for e in ir.events if e.type.name == "CONTROL_CHANGE"],
            key=lambda e: (e.time, e.channel, e.data1),
        )

        assert len(cc_events) == 4

        # Track 1: both at time 0
        assert cc_events[0].time == 0
        assert cc_events[0].channel == 1
        assert cc_events[0].data1 == 7
        assert cc_events[1].time == 0
        assert cc_events[1].channel == 1
        assert cc_events[1].data1 == 10

        # Track 2: both at time 960 (1 second)
        assert cc_events[2].time == 960
        assert cc_events[2].channel == 2
        assert cc_events[2].data1 == 7
        assert cc_events[3].time == 960
        assert cc_events[3].channel == 2
        assert cc_events[3].data1 == 10
