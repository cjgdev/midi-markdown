"""
Test Suite for MIDI Markup Language (MML) Parser
Tests all major features of the grammar and parser implementation
"""

import pytest
from mml_parser import MMLDocument, MMLParser


class TestMMLParser:
    """Test suite for the MML parser"""

    @pytest.fixture
    def parser(self):
        """Create a parser instance for testing"""
        return MMLParser()

    # ========================================================================
    # Basic Structure Tests
    # ========================================================================

    def test_empty_document(self, parser):
        """Test parsing an empty document"""
        doc = parser.parse_string("")
        assert isinstance(doc, MMLDocument)
        assert len(doc.events) == 0

    def test_frontmatter(self, parser):
        """Test parsing YAML frontmatter"""
        mml = """---
title: "Test Song"
author: "Test Author"
ppq: 480
---
"""
        doc = parser.parse_string(mml)
        assert doc.frontmatter["title"] == "Test Song"
        assert doc.frontmatter["author"] == "Test Author"
        assert doc.frontmatter["ppq"] == 480

    def test_imports(self, parser):
        """Test import statements"""
        mml = """
@import "devices/quad_cortex.mml"
@import "devices/eventide_h90.mml"
"""
        doc = parser.parse_string(mml)
        assert len(doc.imports) == 2
        assert "devices/quad_cortex.mml" in doc.imports

    def test_defines(self, parser):
        """Test define statements"""
        mml = """
@define TEMPO 120
@define PRESET 5
@define NAME "Test"
"""
        doc = parser.parse_string(mml)
        assert doc.defines["TEMPO"] == 120
        assert doc.defines["PRESET"] == 5
        assert doc.defines["NAME"] == "Test"

    # ========================================================================
    # Timing Tests
    # ========================================================================

    def test_absolute_timing(self, parser):
        """Test absolute time format [mm:ss.mmm]"""
        mml = "[00:00.000]\n- pc 1.0"
        doc = parser.parse_string(mml)
        # Should have at least one event with timing
        assert len(doc.events) > 0

    def test_musical_timing(self, parser):
        """Test musical time format [bar.beat.tick]"""
        mml = "[1.1.000]\n- pc 1.0\n[2.3.240]\n- pc 1.1"
        doc = parser.parse_string(mml)
        assert len(doc.events) >= 2

    def test_relative_timing(self, parser):
        """Test relative time format [+value unit]"""
        mml = """
[00:00.000]
- pc 1.0
[+1.0s]
- pc 1.1
[+500ms]
- pc 1.2
[+2b]
- pc 1.3
"""
        doc = parser.parse_string(mml)
        assert len(doc.events) >= 4

    def test_simultaneous_timing(self, parser):
        """Test simultaneous execution [@]"""
        mml = """
[00:00.000]
- pc 1.0
[@]
- cc 1.7.100
"""
        doc = parser.parse_string(mml)
        # Both commands should be present
        assert len(doc.events) >= 2

    # ========================================================================
    # MIDI Command Tests
    # ========================================================================

    def test_program_change(self, parser):
        """Test program change commands"""
        test_cases = ["- program_change 1.42", "- pc 1.42", "- pc 2.0"]
        for mml in test_cases:
            doc = parser.parse_string(mml)
            assert len(doc.events) > 0

    def test_control_change(self, parser):
        """Test control change commands"""
        test_cases = ["- control_change 1.7.127", "- cc 1.7.127", "- cc 1.10.64", "- cc 2.1.0"]
        for mml in test_cases:
            doc = parser.parse_string(mml)
            assert len(doc.events) > 0

    def test_note_commands(self, parser):
        """Test note on/off commands"""
        mml = """
- note_on 1.C4 100 1b
- note_on 1.60 127 500ms
- note_on 2.D#5 80 2b
- note_off 1.C4 64
"""
        doc = parser.parse_string(mml)
        assert len(doc.events) >= 4

    def test_pitch_bend(self, parser):
        """Test pitch bend commands"""
        test_cases = ["- pitch_bend 1.0", "- pb 1.8192", "- pb 1.+2000", "- pb 1.-4096"]
        for mml in test_cases:
            doc = parser.parse_string(mml)
            assert len(doc.events) > 0

    def test_pressure_commands(self, parser):
        """Test aftertouch/pressure commands"""
        mml = """
- channel_pressure 1.64
- cp 1.64
- poly_pressure 1.C4.80
- pp 1.60.100
"""
        doc = parser.parse_string(mml)
        assert len(doc.events) >= 4

    def test_meta_events(self, parser):
        """Test meta events"""
        mml = """
- tempo 120
- time_signature 4/4
- key_signature Am
- marker "Intro"
- text "Some text"
"""
        doc = parser.parse_string(mml)
        assert len(doc.events) >= 5

    def test_sysex(self, parser):
        """Test SysEx commands"""
        mml = "- sysex F0 00 01 06 02 F7"
        doc = parser.parse_string(mml)
        assert len(doc.events) > 0

    # ========================================================================
    # Alias System Tests
    # ========================================================================

    def test_simple_alias(self, parser):
        """Test simple alias definition"""
        mml = '@alias cortex_preset pc.{channel}.{preset} "Load preset"'
        doc = parser.parse_string(mml)
        assert "cortex_preset" in doc.aliases
        assert doc.aliases["cortex_preset"].name == "cortex_preset"

    def test_alias_with_enum(self, parser):
        """Test alias with enumerated values"""
        mml = '@alias h90_routing cc.{ch}.85.{mode=series:0,parallel:1} "Routing"'
        doc = parser.parse_string(mml)
        assert "h90_routing" in doc.aliases

    def test_macro_alias(self, parser):
        """Test multi-command macro alias"""
        mml = """
@alias cortex_load {ch}.{preset} "Load preset"
  - cc {ch}.32.0
  - pc {ch}.{preset}
@end
"""
        doc = parser.parse_string(mml)
        assert "cortex_load" in doc.aliases
        assert doc.aliases["cortex_load"].is_macro == True

    def test_alias_call(self, parser):
        """Test calling an alias"""
        mml = """
@alias test_alias pc.{ch}.{preset} "Test"

[00:00.000]
- test_alias 1 5
"""
        doc = parser.parse_string(mml)
        assert "test_alias" in doc.aliases
        # Should have an alias call in events

    # ========================================================================
    # Advanced Features Tests
    # ========================================================================

    def test_track_definition(self, parser):
        """Test track definitions"""
        mml = """
## Track 1: Control
@track control channel=1

[00:00.000]
- pc 1.0
"""
        doc = parser.parse_string(mml)
        assert len(doc.tracks) > 0 or "control" in str(doc.events)

    def test_loop_statement(self, parser):
        """Test loop statements"""
        mml = """
@loop 4 times at [1.1.0] every 1b
  - note_on 10.C1 100 1b
@end
"""
        doc = parser.parse_string(mml)
        # Should have a loop structure in events
        assert len(doc.events) > 0

    def test_sweep_statement(self, parser):
        """Test sweep/ramp statements"""
        mml = """
@sweep from [1.1.0] to [5.1.0] every 8t
  - cc 1.7 ramp(0, 127)
@end
"""
        doc = parser.parse_string(mml)
        assert len(doc.events) > 0

    def test_conditional_statement(self, parser):
        """Test conditional statements"""
        mml = """
@if ${DEVICE_TYPE} == "cortex"
  - pc 1.10
@elif ${DEVICE_TYPE} == "h90"
  - pc 2.5
@else
  - pc 1.0
@end
"""
        doc = parser.parse_string(mml)
        assert len(doc.events) > 0

    def test_section_definition(self, parser):
        """Test section definitions"""
        mml = """
@section "Intro" from [0.0.0] to [8.1.0]
  - tempo 120
  - marker "Intro Start"
@end
"""
        doc = parser.parse_string(mml)
        assert len(doc.events) > 0

    # ========================================================================
    # Expression Tests
    # ========================================================================

    def test_variable_reference(self, parser):
        """Test variable references in expressions"""
        mml = """
@define TEMPO 120

[00:00.000]
- tempo ${TEMPO}
"""
        doc = parser.parse_string(mml)
        assert "TEMPO" in doc.defines

    def test_expressions(self, parser):
        """Test mathematical expressions"""
        mml = """
@define BASE 100
@define DOUBLE ${BASE * 2}
@define HALF ${BASE / 2}
"""
        doc = parser.parse_string(mml)
        assert "BASE" in doc.defines
        assert "DOUBLE" in doc.defines

    def test_percent_values(self, parser):
        """Test percentage values"""
        mml = "- cc 1.7.50%"
        doc = parser.parse_string(mml)
        assert len(doc.events) > 0

    def test_ramp_expression(self, parser):
        """Test ramp expressions"""
        mml = "- cc 1.7 ramp(0, 127, linear)"
        doc = parser.parse_string(mml)
        assert len(doc.events) > 0

    def test_random_expression(self, parser):
        """Test random expressions"""
        mml = "- cc 1.7 random(0, 127)"
        doc = parser.parse_string(mml)
        assert len(doc.events) > 0

    # ========================================================================
    # Comment Tests
    # ========================================================================

    def test_single_line_comments(self, parser):
        """Test single-line comments"""
        mml = """
# This is a comment
- pc 1.0  # Inline comment
// C-style comment
"""
        doc = parser.parse_string(mml)
        assert len(doc.events) > 0

    def test_multi_line_comments(self, parser):
        """Test multi-line comment blocks"""
        mml = """
/*
  Multi-line comment
  spanning several lines
*/
- pc 1.0
"""
        doc = parser.parse_string(mml)
        assert len(doc.events) > 0

    # ========================================================================
    # Complex Integration Tests
    # ========================================================================

    def test_complete_song_structure(self, parser):
        """Test a complete song structure"""
        mml = """---
title: "Test Song"
midi_format: 1
ppq: 480
---

@import "devices/quad_cortex.mml"

@define MAIN_TEMPO 120
@define VERSE_PRESET 2

## Track 1: Control
@track control channel=1

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
        assert doc.frontmatter["title"] == "Test Song"
        assert len(doc.imports) > 0
        assert len(doc.defines) >= 2

    def test_multi_track_with_automation(self, parser):
        """Test multi-track setup with automation"""
        mml = """
## Track 1: Main
@track main channel=1

[00:00.000]
- pc 1.0

## Track 2: Automation
@track automation channel=2

@sweep from [0.1.0] to [8.1.0] every 16t
  - cc 2.7 ramp(0, 127)
@end
"""
        doc = parser.parse_string(mml)
        # Should have multiple tracks or automation structures
        assert len(doc.events) > 0 or len(doc.tracks) > 0

    def test_device_library_pattern(self, parser):
        """Test device library alias patterns"""
        mml = """
@alias cortex_load {ch}.{setlist}.{group}.{preset} "Complete load"
  - cc {ch}.32.{setlist}
  - cc {ch}.0.{group}
  - pc {ch}.{preset}
@end

[00:00.000]
- cortex_load 1 2 0 5
"""
        doc = parser.parse_string(mml)
        assert "cortex_load" in doc.aliases
        assert doc.aliases["cortex_load"].is_macro


# ============================================================================
# Grammar Validation Tests
# ============================================================================


class TestGrammarEdgeCases:
    """Test edge cases and error handling"""

    @pytest.fixture
    def parser(self):
        return MMLParser()

    def test_note_name_variations(self, parser):
        """Test various note name formats"""
        test_cases = [
            "- note_on 1.C4 100 1b",
            "- note_on 1.C#4 100 1b",
            "- note_on 1.Db5 100 1b",
            "- note_on 1.G9 100 1b",  # Highest MIDI note
            "- note_on 1.C-1 100 1b",  # Lowest MIDI note
        ]
        for mml in test_cases:
            doc = parser.parse_string(mml)
            assert len(doc.events) > 0

    def test_nested_expressions(self, parser):
        """Test nested mathematical expressions"""
        mml = "@define RESULT ${(10 + 5) * 2 / 3}"
        doc = parser.parse_string(mml)
        assert "RESULT" in doc.defines

    def test_multiline_sysex(self, parser):
        """Test multi-line SysEx data"""
        mml = """
- sysex F0 00 01 06
        02 03 04 05
        F7
"""
        doc = parser.parse_string(mml)
        assert len(doc.events) > 0

    def test_empty_tracks(self, parser):
        """Test tracks with no content"""
        mml = """
## Track 1: Empty
@track empty channel=1
"""
        doc = parser.parse_string(mml)
        # Should not error


# ============================================================================
# Performance and Stress Tests
# ============================================================================


class TestPerformance:
    """Test parser performance with large files"""

    @pytest.fixture
    def parser(self):
        return MMLParser()

    def test_many_events(self, parser):
        """Test parsing many sequential events"""
        events = "\n".join([f"[00:00.{i:03d}]\n- pc 1.{i % 128}" for i in range(100)])
        doc = parser.parse_string(events)
        assert len(doc.events) >= 100

    def test_many_aliases(self, parser):
        """Test many alias definitions"""
        aliases = "\n".join([f'@alias test_{i} pc.{{ch}}.{{preset}} "Test {i}"' for i in range(50)])
        doc = parser.parse_string(aliases)
        assert len(doc.aliases) >= 50


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
