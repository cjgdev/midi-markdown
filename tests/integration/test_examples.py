"""
Integration tests for MML examples.

Tests that all example files parse successfully and contain expected structure.
"""

from pathlib import Path

# Path to examples directory (now in root examples/)
EXAMPLES_DIR = Path(__file__).parent.parent.parent / "examples"


class TestExampleParsing:
    """Test that all examples parse successfully"""

    def test_00_hello_world(self, parser):
        """Test the simplest example"""
        example_file = EXAMPLES_DIR / "00_basics" / "01_hello_world.mmd"
        doc = parser.parse_file(example_file)

        # Verify frontmatter
        assert doc.frontmatter["title"] == "Hello World"
        assert doc.frontmatter["author"] == "First Time User"
        assert doc.frontmatter["midi_format"] == 0
        assert doc.frontmatter["ppq"] == 480

        # Verify has events
        assert len(doc.events) >= 2

        # First event should have tempo command
        first_event = doc.events[0]
        assert first_event["type"] == "timed_event"
        assert any(cmd.type == "tempo" for cmd in first_event["commands"])
        assert any(cmd.type == "note_on" for cmd in first_event["commands"])

        # Last event should have text
        last_event = doc.events[-1]
        assert any(cmd.type == "text" for cmd in last_event["commands"])

    def test_01_minimal_midi(self, parser):
        """Test minimal MIDI file with metadata"""
        example_file = EXAMPLES_DIR / "00_basics" / "02_minimal_midi.mmd"
        doc = parser.parse_file(example_file)

        assert doc.frontmatter["title"] == "My First MIDI File"
        assert len(doc.events) >= 2

        # Should have tempo, time_signature, key_signature
        first_event = doc.events[0]
        commands = first_event["commands"]
        assert any(cmd.type == "tempo" and cmd.data1 == 120 for cmd in commands)
        assert any(cmd.type == "time_signature" for cmd in commands)
        assert any(cmd.type == "key_signature" for cmd in commands)

    def test_02_simple_click_track(self, parser):
        """Test click track with repeated note patterns"""
        example_file = EXAMPLES_DIR / "00_basics" / "03_simple_click_track.mmd"
        doc = parser.parse_file(example_file)

        assert doc.frontmatter["title"] == "Practice Click Track"
        assert doc.frontmatter["default_channel"] == 10

        # Count note events (should have many)
        note_count = sum(
            1
            for event in doc.events
            if event["type"] == "timed_event"
            for cmd in event["commands"]
            if cmd.type == "note_on" and cmd.channel == 10
        )
        assert note_count >= 16, "Should have at least 16 click notes"

    def test_03_song_structure_markers(self, parser):
        """Test song with section markers"""
        example_file = EXAMPLES_DIR / "00_basics" / "04_song_structure_markers.mmd"
        doc = parser.parse_file(example_file)

        assert doc.frontmatter["title"] == "Basic Song Structure"

        # Extract all markers
        markers = []
        for event in doc.events:
            if event["type"] == "timed_event":
                for cmd in event["commands"]:
                    if cmd.type == "marker":
                        markers.append(cmd.params["text"])

        # Should have all major song sections
        expected_markers = ["Intro", "Verse 1", "Chorus", "Verse 2", "Bridge", "Outro"]
        for expected in expected_markers:
            assert any(expected in marker for marker in markers), f"Missing marker: {expected}"

    def test_04_tempo_changes(self, parser):
        """Test dynamic tempo changes"""
        example_file = EXAMPLES_DIR / "01_timing" / "01_tempo_changes.mmd"
        doc = parser.parse_file(example_file)

        assert doc.frontmatter["title"] == "Ballad with Tempo Changes"

        # Check defines were parsed
        assert "SLOW_TEMPO" in doc.defines
        assert "MODERATE_TEMPO" in doc.defines
        assert "FAST_TEMPO" in doc.defines

        # Extract all tempo changes
        tempos = []
        for event in doc.events:
            if event["type"] == "timed_event":
                for cmd in event["commands"]:
                    if cmd.type == "tempo":
                        tempos.append(cmd.data1)

        # Should have multiple different tempos
        assert len(tempos) >= 10, "Should have many tempo changes"
        assert len(set(tempos)) >= 5, "Should have at least 5 different tempos"

        # Check range
        assert min(tempos) <= 65, "Should have slow tempos"
        assert max(tempos) >= 120, "Should have fast tempos"

    def test_05_multi_channel_basic(self, parser):
        """Test multi-channel song"""
        example_file = EXAMPLES_DIR / "02_midi_features" / "01_multi_channel_basic.mmd"
        doc = parser.parse_file(example_file)

        assert doc.frontmatter["title"] == "Multi-Channel Song"

        # Check defines for channels
        assert "SYNTH_CHANNEL" in doc.defines
        assert "BASS_CHANNEL" in doc.defines
        assert "DRUMS_CHANNEL" in doc.defines

        # Extract all channels used
        channels_used = set()
        for event in doc.events:
            if event["type"] == "timed_event":
                for cmd in event["commands"]:
                    if cmd.channel is not None:
                        channels_used.add(cmd.channel)

        # Should use multiple channels
        assert len(channels_used) >= 2, "Should use at least 2 channels"

    def test_06_cc_automation(self, parser):
        """Test CC automation"""
        example_file = EXAMPLES_DIR / "02_midi_features" / "02_cc_automation.mmd"
        doc = parser.parse_file(example_file)

        assert doc.frontmatter["title"] == "Control Change Automation"

        # Extract CC messages
        cc_messages = []
        for event in doc.events:
            if event["type"] == "timed_event":
                for cmd in event["commands"]:
                    if cmd.type == "cc":
                        cc_messages.append((cmd.channel, cmd.data1, cmd.data2))

        # Should have many CC messages
        assert len(cc_messages) >= 20, "Should have substantial CC automation"

        # Check for different CC types (CC 7=volume, CC 10=pan, etc.)
        cc_types = {cc[1] for cc in cc_messages}
        assert 7 in cc_types, "Should have volume (CC 7) automation"
        assert 10 in cc_types, "Should have pan (CC 10) automation"

    def test_07_pitch_bend_pressure(self, parser):
        """Test pitch bend and pressure"""
        example_file = EXAMPLES_DIR / "02_midi_features" / "03_pitch_bend_pressure.mmd"
        doc = parser.parse_file(example_file)

        assert doc.frontmatter["title"] == "Pitch Bend and Pressure Demo"

        # Extract pitch bend messages
        pitch_bends = []
        for event in doc.events:
            if event["type"] == "timed_event":
                for cmd in event["commands"]:
                    if cmd.type == "pitch_bend":
                        pitch_bends.append(cmd.data1)

        assert len(pitch_bends) >= 5, "Should have pitch bend messages"

        # Check for positive and negative bends
        assert any(pb > 0 for pb in pitch_bends), "Should have upward bends"
        assert any(pb < 0 for pb in pitch_bends), "Should have downward bends"

        # Extract pressure messages
        has_channel_pressure = False
        has_poly_pressure = False
        for event in doc.events:
            if event["type"] == "timed_event":
                for cmd in event["commands"]:
                    if cmd.type == "channel_pressure":
                        has_channel_pressure = True
                    if cmd.type == "poly_pressure":
                        has_poly_pressure = True

        assert has_channel_pressure, "Should have channel pressure"
        assert has_poly_pressure, "Should have polyphonic pressure"

    def test_08_system_messages(self, parser):
        """Test system and SysEx messages"""
        example_file = EXAMPLES_DIR / "02_midi_features" / "04_system_messages.mmd"
        doc = parser.parse_file(example_file)

        assert doc.frontmatter["title"] == "System and SysEx Messages"

        # Extract message types
        message_types = set()
        for event in doc.events:
            if event["type"] == "timed_event":
                for cmd in event["commands"]:
                    message_types.add(cmd.type)

        # Should have SysEx
        assert "sysex" in message_types, "Should have SysEx messages"

        # Should have system common
        assert "mtc_quarter_frame" in message_types or "song_position" in message_types, (
            "Should have system common messages"
        )

        # Should have real-time
        assert (
            "clock_start" in message_types
            or "clock_stop" in message_types
            or "timing_clock" in message_types
        ), "Should have real-time messages"

    def test_09_comprehensive_song(self, parser):
        """Test comprehensive example combining many features"""
        example_file = EXAMPLES_DIR / "03_advanced" / "10_comprehensive_song.mmd"
        doc = parser.parse_file(example_file)

        assert doc.frontmatter["title"] == "Comprehensive Song Example"

        # Should have defines
        assert len(doc.defines) >= 3

        # Should have many events across all tracks
        total_events = sum(len(track.events) for track in doc.tracks)
        assert total_events >= 50, "Should be a substantial song"

        # Extract markers from all tracks
        markers = []
        for track in doc.tracks:
            for event in track.events:
                if isinstance(event, dict) and event.get("type") == "timed_event":
                    for cmd in event["commands"]:
                        if cmd.type == "marker":
                            markers.append(cmd.params["text"])

        # Should have song structure
        assert len(markers) >= 6, "Should have multiple sections"

        # Extract channels used from all tracks
        channels = set()
        for track in doc.tracks:
            for event in track.events:
                if isinstance(event, dict) and event.get("type") == "timed_event":
                    for cmd in event["commands"]:
                        if cmd.channel is not None:
                            channels.add(cmd.channel)

        # Should use multiple channels
        assert len(channels) >= 3, "Should use 3+ channels"

        # Should have various command types
        command_types = set()
        for track in doc.tracks:
            for event in track.events:
                if isinstance(event, dict) and event.get("type") == "timed_event":
                    for cmd in event["commands"]:
                        command_types.add(cmd.type)

        assert "note_on" in command_types
        assert "cc" in command_types  # Parser uses "cc" not "control_change"
        assert "pitch_bend" in command_types
        assert "tempo" in command_types


class TestExampleTiming:
    """Test timing aspects of examples"""

    def test_timing_monotonicity(self, parser):
        """Verify all examples have monotonically increasing timing"""
        # Examples organized by instrument/channel rather than chronologically
        skip_examples = ["01_multi_channel_basic", "05_multi_channel", "09_comprehensive"]

        for example_file in EXAMPLES_DIR.rglob("*.mmd"):
            # Skip examples with non-chronological organization
            # TODO: Reorganize these examples to be chronological
            if any(skip in example_file.name for skip in skip_examples):
                continue

            doc = parser.parse_file(example_file)

            # Extract timing values (absolute seconds)
            timings = []
            for event in doc.events:
                # Skip Token objects (SECTION_HEADER, etc.)
                if not isinstance(event, dict):
                    continue
                if event["type"] == "timed_event":
                    timing = event["timing"]
                    if timing.type == "absolute":
                        timings.append(timing.value)

            # Check monotonicity (allowing simultaneous events with same timestamp)
            for i in range(1, len(timings)):
                assert timings[i] >= timings[i - 1], (
                    f"Non-monotonic timing in {example_file.name}: {timings[i]} < {timings[i - 1]} at position {i}"
                )


class TestExampleContent:
    """Test content quality of examples"""

    def test_all_examples_have_frontmatter(self, parser):
        """All examples should have title and author"""
        for example_file in EXAMPLES_DIR.rglob("*.mmd"):
            doc = parser.parse_file(example_file)
            assert "title" in doc.frontmatter, f"{example_file.name} missing title"
            assert "author" in doc.frontmatter, f"{example_file.name} missing author"

    def test_all_examples_have_events(self, parser):
        """All examples should have at least one event"""
        for example_file in EXAMPLES_DIR.rglob("*.mmd"):
            # Skip library files (only contain alias definitions)
            if "shared" in example_file.parts:
                continue

            doc = parser.parse_file(example_file)
            # Check doc.events (single-track) or doc.tracks (multi-track)
            has_events = len(doc.events) > 0 or any(len(track.events) > 0 for track in doc.tracks)
            assert has_events, f"{example_file.name} has no events"

    def test_all_examples_have_tempo(self, parser):
        """All examples should set tempo (either in frontmatter or as command)"""
        for example_file in EXAMPLES_DIR.rglob("*.mmd"):
            # Skip library files (only contain alias definitions)
            if "shared" in example_file.parts:
                continue

            doc = parser.parse_file(example_file)

            # Check frontmatter first
            has_tempo = doc.frontmatter.get("tempo") is not None

            # If not in frontmatter, check for tempo command in events
            if not has_tempo:
                # Check doc.events (for single-track files)
                for event in doc.events:
                    # Skip Token objects (SECTION_HEADER, etc.)
                    if not isinstance(event, dict):
                        continue
                    if event["type"] == "timed_event":
                        for cmd in event["commands"]:
                            if cmd.type == "tempo":
                                has_tempo = True
                                break
                    if has_tempo:
                        break

                # Check doc.tracks (for multi-track files)
                if not has_tempo:
                    for track in doc.tracks:
                        for event in track.events:
                            if isinstance(event, dict) and event.get("type") == "timed_event":
                                for cmd in event["commands"]:
                                    if cmd.type == "tempo":
                                        has_tempo = True
                                        break
                            if has_tempo:
                                break
                        if has_tempo:
                            break

            assert has_tempo, f"{example_file.name} does not set tempo"
