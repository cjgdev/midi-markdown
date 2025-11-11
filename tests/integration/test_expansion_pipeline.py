"""
Integration tests for the complete expansion pipeline.

Tests the full flow: Parse → Expand → Generate → Write MIDI
"""

import pytest

from midi_markdown.codegen import generate_midi_file
from midi_markdown.core.ir import MIDIEvent, create_ir_program, string_to_event_type
from midi_markdown.expansion.expander import CommandExpander
from midi_markdown.parser.parser import MMDParser


class TestVariablesExpansion:
    """Test variable expansion through the full pipeline."""

    def test_simple_variable_substitution(self, tmp_path):
        """Test basic variable definition and substitution."""
        mml_code = """---
title: "Variable Test"
tempo: 120
ppq: 480
---

@define CHANNEL 1
@define PRESET 10

[00:00.000]
- pc ${CHANNEL}.${PRESET}
"""
        # Parse
        parser = MMDParser()
        doc = parser.parse_string(mml_code)

        assert len(doc.defines) == 2
        assert doc.defines["CHANNEL"] == 1.0
        assert doc.defines["PRESET"] == 10.0

        # Expand
        expander = CommandExpander(ppq=480, tempo=120.0)
        for name, value in doc.defines.items():
            expander.symbol_table.define(name, value)

        expanded_events = expander.process_ast(doc.events)

        # Verify expansion
        assert len(expanded_events) == 1
        assert expanded_events[0]["type"] == "pc"
        assert expanded_events[0]["channel"] == 1
        assert expanded_events[0]["data1"] == 10

        # Generate MIDI events
        events = []
        for event_dict in expanded_events:
            midi_event = MIDIEvent(
                time=event_dict["time"],
                type=string_to_event_type(event_dict["type"]),
                channel=event_dict.get("channel", 0),
                data1=event_dict.get("data1", 0),
                data2=event_dict.get("data2", 0),
            )
            events.append(midi_event)

        assert len(events) == 1

        # Write MIDI file
        output_file = tmp_path / "test_variables.mid"
        ir_program = create_ir_program(events=events, ppq=480, initial_tempo=120)
        midi_bytes = generate_midi_file(ir_program, midi_format=1)
        output_file.write_bytes(midi_bytes)

        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_tempo_events_with_high_values(self, tmp_path):
        """Test that tempo events with values > 127 work correctly."""
        mml_code = """---
title: "Tempo Test"
tempo: 120
ppq: 480
---

@define TEMPO_FAST 140
@define TEMPO_SLOW 80

[00:00.000]
- tempo ${TEMPO_FAST}

[00:01.000]
- tempo ${TEMPO_SLOW}
"""
        parser = MMDParser()
        doc = parser.parse_string(mml_code)

        expander = CommandExpander(ppq=480, tempo=120.0)
        for name, value in doc.defines.items():
            expander.symbol_table.define(name, value)

        # Should not raise validation error for tempo > 127
        expanded_events = expander.process_ast(doc.events)

        assert len(expanded_events) == 2
        assert expanded_events[0]["type"] == "tempo"
        assert expanded_events[0]["data1"] == 140
        assert expanded_events[1]["type"] == "tempo"
        assert expanded_events[1]["data1"] == 80


class TestLoopsExpansion:
    """Test loop expansion through the full pipeline."""

    def test_simple_loop_expansion(self, tmp_path):
        """Test basic loop expansion with beat intervals."""
        mml_code = """---
title: "Loop Test"
tempo: 120
ppq: 480
---

@loop 3 times every 1b
- pc 1.10
@end
"""
        parser = MMDParser()
        doc = parser.parse_string(mml_code)

        expander = CommandExpander(ppq=480, tempo=120.0)
        expanded_events = expander.process_ast(doc.events)

        # Should expand to 3 events (3 iterations)
        assert len(expanded_events) == 3

        # Check timing - 1 beat = 480 ticks at 480 PPQ
        assert expanded_events[0]["time"] == 0
        assert expanded_events[1]["time"] == 480
        assert expanded_events[2]["time"] == 960

        # All should be PC commands
        for event in expanded_events:
            assert event["type"] == "pc"
            assert event["channel"] == 1
            assert event["data1"] == 10

        # Verify stats
        stats = expander.get_stats()
        assert stats.loops_expanded == 1
        assert stats.events_generated == 3

    def test_loop_with_variables(self, tmp_path):
        """Test loop expansion with variable substitution."""
        mml_code = """---
title: "Loop with Variables"
tempo: 120
ppq: 480
---

@define CHANNEL 2
@define PRESET 15

@loop 2 times every 1b
- pc ${CHANNEL}.${PRESET}
@end
"""
        parser = MMDParser()
        doc = parser.parse_string(mml_code)

        expander = CommandExpander(ppq=480, tempo=120.0)
        for name, value in doc.defines.items():
            expander.symbol_table.define(name, value)

        expanded_events = expander.process_ast(doc.events)

        assert len(expanded_events) == 2
        for event in expanded_events:
            assert event["channel"] == 2
            assert event["data1"] == 15

    def test_loop_with_timing(self, tmp_path):
        """Test loop with explicit start timing."""
        mml_code = """---
title: "Loop with Timing"
tempo: 120
ppq: 480
---

@loop 2 times at [00:05.000] every 2b
- cc 1.7.100
@end
"""
        parser = MMDParser()
        doc = parser.parse_string(mml_code)

        expander = CommandExpander(ppq=480, tempo=120.0)
        expanded_events = expander.process_ast(doc.events)

        assert len(expanded_events) == 2

        # 5 seconds = 5 * (480 * 120 / 60) = 5 * 960 = 4800 ticks
        # 2 beats = 2 * 480 = 960 ticks
        assert expanded_events[0]["time"] == 4800
        assert expanded_events[1]["time"] == 4800 + 960


class TestSweepsExpansion:
    """Test sweep expansion through the full pipeline."""

    def test_simple_sweep_expansion(self, tmp_path):
        """Test basic sweep expansion with linear ramp."""
        mml_code = """---
title: "Sweep Test"
tempo: 120
ppq: 480
---

@sweep from [00:00.000] to [00:01.000] every 500ms
- cc 1.7.64
@end
"""
        parser = MMDParser()
        doc = parser.parse_string(mml_code)

        expander = CommandExpander(ppq=480, tempo=120.0)
        expanded_events = expander.process_ast(doc.events)

        # Should generate multiple events for the sweep
        assert len(expanded_events) >= 2

        # First event at start time
        assert expanded_events[0]["time"] == 0

        # Events should be CC type
        for event in expanded_events:
            assert event["type"] == "cc"
            assert event["channel"] == 1
            assert event["data1"] == 7

        # Verify stats
        stats = expander.get_stats()
        assert stats.sweeps_expanded == 1
        assert stats.events_generated >= 2


class TestCombinedFeatures:
    """Test combinations of variables, loops, and sweeps."""

    def test_variables_and_loops_combined(self, tmp_path):
        """Test document with both variables and loops."""
        mml_code = """---
title: "Combined Test"
tempo: 120
ppq: 480
---

@define CHANNEL 1
@define BASE_PRESET 10

[00:00.000]
- pc ${CHANNEL}.${BASE_PRESET}

@loop 3 times every 1b
- cc ${CHANNEL}.7.64
@end
"""
        parser = MMDParser()
        doc = parser.parse_string(mml_code)

        expander = CommandExpander(ppq=480, tempo=120.0)
        for name, value in doc.defines.items():
            expander.symbol_table.define(name, value)

        expanded_events = expander.process_ast(doc.events)

        # Should have 1 timed event (PC) + 3 loop events (CC) = 4 total
        assert len(expanded_events) == 4

        # Count event types (sorting may reorder them)
        pc_events = [e for e in expanded_events if e["type"] == "pc"]
        cc_events = [e for e in expanded_events if e["type"] == "cc"]

        assert len(pc_events) == 1
        assert len(cc_events) == 3

        # PC event should have correct data
        assert pc_events[0]["channel"] == 1
        assert pc_events[0]["data1"] == 10

        # All CC events should be from the loop
        for cc_event in cc_events:
            assert cc_event["channel"] == 1
            assert cc_event["data1"] == 7

        stats = expander.get_stats()
        assert stats.loops_expanded == 1
        assert stats.events_generated == 4

    def test_full_pipeline_to_midi_file(self, tmp_path):
        """Test complete pipeline from MML string to MIDI file."""
        mml_code = """---
title: "Full Pipeline Test"
author: "Test Suite"
tempo: 120
time_signature: 4/4
ppq: 480
---

@define MAIN_CHANNEL 1
@define VERSE_PRESET 10

[00:00.000]
- pc ${MAIN_CHANNEL}.${VERSE_PRESET}

@loop 2 times every 1b
- cc ${MAIN_CHANNEL}.7.64
@end
"""
        # 1. Parse
        parser = MMDParser()
        doc = parser.parse_string(mml_code)

        assert doc.frontmatter is not None
        assert doc.frontmatter["title"] == "Full Pipeline Test"
        assert len(doc.defines) == 2

        # 2. Expand
        ppq = doc.frontmatter.get("ppq", 480)
        tempo = float(doc.frontmatter.get("tempo", 120.0))

        expander = CommandExpander(ppq=ppq, tempo=tempo)
        for name, value in doc.defines.items():
            expander.symbol_table.define(name, value)

        expanded_events = expander.process_ast(doc.events)
        assert len(expanded_events) == 3  # 1 PC + 2 CC from loop

        # 3. Convert to MIDIEvent objects
        events = []
        for event_dict in expanded_events:
            midi_event = MIDIEvent(
                time=event_dict["time"],
                type=string_to_event_type(event_dict["type"]),
                channel=event_dict.get("channel", 0),
                data1=event_dict.get("data1", 0),
                data2=event_dict.get("data2", 0),
            )
            events.append(midi_event)

        assert len(events) == 3

        # 4. Write MIDI file
        output_file = tmp_path / "full_pipeline_test.mid"
        ir_program = create_ir_program(events=events, ppq=ppq, initial_tempo=int(tempo))
        midi_bytes = generate_midi_file(ir_program, midi_format=1)
        output_file.write_bytes(midi_bytes)

        # Verify file was created
        assert output_file.exists()
        assert output_file.stat().st_size > 0

        # Verify we can read it back (basic sanity check)
        assert output_file.read_bytes()[:4] == b"MThd"  # MIDI file header


class TestErrorHandling:
    """Test error handling in the expansion pipeline."""

    def test_undefined_variable_error(self):
        """Test that undefined variables raise appropriate errors."""
        mml_code = """---
title: "Error Test"
---

[00:00.000]
- pc 1.${UNDEFINED_VAR}
"""
        parser = MMDParser()
        doc = parser.parse_string(mml_code)

        expander = CommandExpander(ppq=480, tempo=120.0)

        # Should raise UndefinedVariableError
        from midi_markdown.expansion.errors import UndefinedVariableError

        with pytest.raises(UndefinedVariableError):
            expander.process_ast(doc.events)

    def test_invalid_loop_config_error(self):
        """Test that invalid loop configurations raise errors."""
        mml_code = """---
title: "Error Test"
---

@loop 0 times every 1b
- pc 1.10
@end
"""
        parser = MMDParser()
        doc = parser.parse_string(mml_code)

        expander = CommandExpander(ppq=480, tempo=120.0)

        # Should raise InvalidLoopConfigError for count <= 0
        from midi_markdown.expansion.errors import InvalidLoopConfigError

        with pytest.raises(InvalidLoopConfigError):
            expander.process_ast(doc.events)
