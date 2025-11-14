"""
Test Suite: Integration

Complex integration tests for complete MML documents including performance tests
and multi-feature scenarios.
"""


class TestComplexDocuments:
    """Test complex, complete MML documents"""

    def test_complete_song_structure(self, parser):
        """Test complete song with multiple features"""
        mml = """---
title: "Complete Song"
author: "Test"
ppq: 480
---
@import "devices/common.mmd"

@define MAIN_CHANNEL 1
@define MAIN_TEMPO 120
@define VERSE_PRESET 5

[00:00.000]
- tempo ${MAIN_TEMPO}
- marker "Intro"
- pc 1.${VERSE_PRESET}

[00:04.000]
- cc 1.7.100

[00:08.000]
- note_on 1.C4 100 1b
"""
        doc = parser.parse_string(mml)
        assert doc.frontmatter["title"] == "Complete Song"
        assert len(doc.imports) >= 1
        assert len(doc.defines) >= 3
        assert len(doc.events) >= 3

    def test_multi_track_with_automation(self, parser):
        """Test multi-track document with automation"""
        mml = """---
title: "Multi-Track"
---
@track drums channel=10
[00:00.000]
- note_on 10.36 100 1b

@track bass channel=2
[00:00.000]
- note_on 2.40 100 4b
[00:04.000]
- cc 2.7.64
"""
        doc = parser.parse_string(mml)
        # Parser should successfully parse track definitions
        assert doc is not None

    def test_device_library_pattern(self, parser):
        """Test device library usage pattern"""
        mml = """
@import "devices/quad_cortex.mmd"

@alias cortex_load {ch} {preset} "Load preset"
  - cc {ch}.32.0
  - pc {ch}.{preset}
@end

[00:00.000]
- cortex_load 1 5
"""
        doc = parser.parse_string(mml)
        assert "devices/quad_cortex.mmd" in doc.imports
        assert "cortex_load" in doc.aliases

    def test_multiline_sysex(self, parser):
        """Test multi-line SysEx message"""
        mml = """
[00:00.000]
- sysex F0 43 12 00
         11 22 33 44
         55 66 77 F7
"""
        doc = parser.parse_string(mml)
        cmd = doc.events[0]["commands"][0]
        assert cmd.type == "sysex"


class TestPerformance:
    """Performance tests for parser"""

    def test_many_events(self, parser):
        """Test parsing many events (performance)"""
        # Generate MML with 1000 events
        events = ["[00:00.000]"]
        for i in range(1000):
            events.append(f"- pc 1.{i % 128}")
            if i % 10 == 0:
                events.append(f"[+{i}ms]")

        mml = "\n".join(events)
        doc = parser.parse_string(mml)
        assert len(doc.events) >= 100

    def test_many_aliases(self, parser):
        """Test document with many alias definitions"""
        aliases = []
        for i in range(50):
            aliases.append(
                f'@alias test_{i} {{ch}} {{preset}} "Alias {i}"\n  - pc {{ch}}.{{preset}}\n@end'
            )

        mml = "\n".join(aliases)
        doc = parser.parse_string(mml)
        assert len(doc.aliases) >= 50
