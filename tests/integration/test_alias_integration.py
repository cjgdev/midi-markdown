"""Integration tests for alias system (Stage 9).

Tests end-to-end alias expansion in real MIDI compilation scenarios.
"""

import pytest

from midi_markdown.expansion.expander import CommandExpander
from midi_markdown.midi.events import MIDIEvent, string_to_event_type


class TestAliasIntegration:
    """Test complete alias expansion pipeline."""

    # ============================================
    # Basic Alias Expansion Tests
    # ============================================

    def test_simple_alias_expansion(self, parser, resolve_aliases):
        """Test simple alias expands to MIDI command."""
        source = """---
title: Simple Alias Test
---

@alias quick_pc {ch} {preset} "Quick program change"
  - pc {ch}.{preset}
@end

[00:00.000]
- quick_pc 1 10
"""
        doc = parser.parse_string(source)
        resolved_events = resolve_aliases(doc)
        doc.events = resolved_events
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

        # Should have one program change event
        pc_events = [e for e in events if e.type.name == "PROGRAM_CHANGE"]
        assert len(pc_events) == 1
        assert pc_events[0].channel == 1
        assert pc_events[0].data1 == 10

    def test_multi_command_alias(self, parser, resolve_aliases):
        """Test alias that expands to multiple commands."""
        source = """---
title: Multi-Command Alias
---

@alias setup {ch} "Setup channel"
  - cc {ch}.7.100
  - cc {ch}.10.64
  - pc {ch}.5
@end

[00:00.000]
- setup 2
"""
        doc = parser.parse_string(source)
        resolved_events = resolve_aliases(doc)
        doc.events = resolved_events
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

        # Should have 2 CC + 1 PC = 3 events
        cc_events = [e for e in events if e.type.name == "CONTROL_CHANGE"]
        pc_events = [e for e in events if e.type.name == "PROGRAM_CHANGE"]

        assert len(cc_events) == 2
        assert len(pc_events) == 1

        # Check first CC (volume)
        assert cc_events[0].channel == 2
        assert cc_events[0].data1 == 7
        assert cc_events[0].data2 == 100

        # Check second CC (pan)
        assert cc_events[1].channel == 2
        assert cc_events[1].data1 == 10
        assert cc_events[1].data2 == 64

        # Check PC
        assert pc_events[0].channel == 2
        assert pc_events[0].data1 == 5

    # ============================================
    # Timing Preservation Tests
    # ============================================

    def test_alias_preserves_timing(self, parser, resolve_aliases):
        """Test that alias expansion preserves timing."""
        source = """---
title: Timing Test
---

@alias dual_cc {ch} {cc1} {cc2} "Send two CCs"
  - cc {ch}.{cc1}.100
  - cc {ch}.{cc2}.50
@end

[00:00.000]
- dual_cc 1 7 10

[00:01.000]
- dual_cc 1 11 91
"""
        doc = parser.parse_string(source)
        resolved_events = resolve_aliases(doc)
        doc.events = resolved_events
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

        cc_events = [e for e in events if e.type.name == "CONTROL_CHANGE"]
        assert len(cc_events) == 4

        # First two CCs should be at time 0
        assert cc_events[0].time == 0
        assert cc_events[1].time == 0

        # Second two CCs should be at 1 second (480 ticks at 120 BPM, 480 PPQ)
        # Actually: 1 second = 60/120 * 2 = 1 beat... wait let me recalculate
        # At 120 BPM: 1 beat = 0.5 seconds, so 1 second = 2 beats = 2 * 480 = 960 ticks
        assert cc_events[2].time == 960
        assert cc_events[3].time == 960

    # ============================================
    # Nested Alias Tests
    # ============================================

    def test_nested_alias_expansion(self, parser, resolve_aliases):
        """Test nested alias (alias calling alias)."""
        source = """---
title: Nested Alias Test
---

@alias base_cc {ch} {cc} {val} "Base CC"
  - cc {ch}.{cc}.{val}
@end

@alias volume_pan {ch} {vol} {pan} "Set volume and pan"
  - base_cc {ch} 7 {vol}
  - base_cc {ch} 10 {pan}
@end

[00:00.000]
- volume_pan 1 100 64
"""
        doc = parser.parse_string(source)
        resolved_events = resolve_aliases(doc)
        doc.events = resolved_events
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

        cc_events = [e for e in events if e.type.name == "CONTROL_CHANGE"]
        assert len(cc_events) == 2

        # Volume CC
        assert cc_events[0].channel == 1
        assert cc_events[0].data1 == 7
        assert cc_events[0].data2 == 100

        # Pan CC
        assert cc_events[1].channel == 1
        assert cc_events[1].data1 == 10
        assert cc_events[1].data2 == 64

    # ============================================
    # Computed Value Tests
    # ============================================

    def test_alias_with_computed_values(self, parser, resolve_aliases):
        """Test alias with computed value (Stage 6 integration)."""
        source = """---
title: Computed Value Test
---

@alias bpm_cc {ch} {bpm:40-300} "Convert BPM to MIDI"
  {midi_val = int((${bpm} - 40) * 127 / 260)}
  - cc {ch}.81.{midi_val}
@end

[00:00.000]
- bpm_cc 1 120
"""
        doc = parser.parse_string(source)
        resolved_events = resolve_aliases(doc)
        doc.events = resolved_events
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

        cc_events = [e for e in events if e.type.name == "CONTROL_CHANGE"]
        assert len(cc_events) == 1

        # BPM 120 → (120-40)*127/260 = 80*127/260 = 39.07 → 39
        assert cc_events[0].data2 == 39

    # ============================================
    # Conditional Alias Tests
    # ============================================

    def test_alias_with_conditionals(self, parser, resolve_aliases):
        """Test alias with conditional logic (Stage 7 integration)."""
        source = """---
title: Conditional Alias Test
---

@alias device_load {ch} {preset} {device=cortex:0,h90:1,other:2} "Device-aware load"
  @if {device} == 0
    - pc {ch}.{preset}
  @elif {device} == 1
    - cc {ch}.71.{preset}
  @else
    - pc {ch}.{preset}
  @end
@end

[00:00.000]
- device_load 1 10 cortex

[00:01.000]
- device_load 2 20 h90

[00:02.000]
- device_load 3 30 other
"""
        doc = parser.parse_string(source)
        resolved_events = resolve_aliases(doc)
        doc.events = resolved_events
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

        pc_events = [e for e in events if e.type.name == "PROGRAM_CHANGE"]
        cc_events = [e for e in events if e.type.name == "CONTROL_CHANGE"]

        # Should have 2 PCs (cortex + other) and 1 CC (h90)
        assert len(pc_events) == 2
        assert len(cc_events) == 1

        # First event: cortex uses PC
        assert pc_events[0].channel == 1
        assert pc_events[0].data1 == 10

        # Second event: h90 uses CC
        assert cc_events[0].channel == 2
        assert cc_events[0].data1 == 71
        assert cc_events[0].data2 == 20

        # Third event: other uses PC (else branch)
        assert pc_events[1].channel == 3
        assert pc_events[1].data1 == 30

    # ============================================
    # Parameter Type Tests
    # ============================================

    def test_alias_with_note_parameter(self, parser, resolve_aliases):
        """Test alias with note name parameter (Stage 2 integration)."""
        source = """---
title: Note Parameter Test
---

@alias play_note {ch} {note:note} {vel} "Play note"
  - note {ch}.{note}.{vel} 500ms
@end

[00:00.000]
- play_note 1 C4 100
"""
        doc = parser.parse_string(source)
        resolved_events = resolve_aliases(doc)
        doc.events = resolved_events
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

        note_on_events = [e for e in events if e.type.name == "NOTE_ON"]
        note_off_events = [e for e in events if e.type.name == "NOTE_OFF"]

        assert len(note_on_events) == 1
        assert len(note_off_events) == 1

        # C4 = MIDI note 60
        assert note_on_events[0].data1 == 60
        assert note_on_events[0].data2 == 100

    def test_alias_with_percent_parameter(self, parser, resolve_aliases):
        """Test alias with percentage parameter (Stage 2 integration)."""
        source = """---
title: Percent Parameter Test
---

@alias volume_percent {ch} {vol:percent} "Set volume as percentage"
  - cc {ch}.7.{vol}
@end

[00:00.000]
- volume_percent 1 75
"""
        doc = parser.parse_string(source)
        resolved_events = resolve_aliases(doc)
        doc.events = resolved_events
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

        cc_events = [e for e in events if e.type.name == "CONTROL_CHANGE"]
        assert len(cc_events) == 1

        # 75% → 75 * 127 / 100 = 95.25 → 95
        assert cc_events[0].data2 == 95

    def test_alias_with_enum_parameter(self, parser, resolve_aliases):
        """Test alias with enum parameter (Stage 2 integration)."""
        source = """---
title: Enum Parameter Test
---

@alias routing {ch} {mode=series:0,parallel:1} "Set routing mode"
  - cc {ch}.85.{mode}
@end

[00:00.000]
- routing 2 series

[00:01.000]
- routing 2 parallel
"""
        doc = parser.parse_string(source)
        resolved_events = resolve_aliases(doc)
        doc.events = resolved_events
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

        cc_events = [e for e in events if e.type.name == "CONTROL_CHANGE"]
        assert len(cc_events) == 2

        # series = 0
        assert cc_events[0].data2 == 0

        # parallel = 1
        assert cc_events[1].data2 == 1

    # ============================================
    # Multi-Track Tests
    # ============================================

    def test_alias_in_multi_track(self, parser, resolve_aliases):
        """Test alias usage in multi-track document."""
        source = """---
title: Multi-Track Alias Test
---

@alias quick_note {ch} {note} {vel} "Quick note"
  - note {ch}.{note}.{vel} 250ms
@end

[00:00.000]
- quick_note 1 60 100

[00:01.000]
- quick_note 1 62 90

[00:00.000]
- quick_note 2 36 110

[00:01.000]
- quick_note 2 38 100
"""
        doc = parser.parse_string(source)
        resolved_events = resolve_aliases(doc)
        doc.events = resolved_events
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

        note_on_events = [e for e in events if e.type.name == "NOTE_ON"]

        # Should have 4 note_on events (2 per channel)
        assert len(note_on_events) == 4

        # Check channels
        lead_notes = [e for e in note_on_events if e.channel == 1]
        bass_notes = [e for e in note_on_events if e.channel == 2]

        assert len(lead_notes) == 2
        assert len(bass_notes) == 2

    # ============================================
    # Error Handling Tests
    # ============================================

    def test_undefined_alias_error(self, parser, resolve_aliases):
        """Test error when calling undefined alias."""
        source = """---
title: Error Test
---

[00:00.000]
- undefined_alias 1 2
"""
        doc = parser.parse_string(source)

        with pytest.raises(Exception) as exc_info:
            resolve_aliases(doc)

        assert "undefined_alias" in str(exc_info.value).lower()

    def test_wrong_argument_count_error(self, parser, resolve_aliases):
        """Test error when providing wrong number of arguments."""
        source = """---
title: Error Test
---

@alias needs_two {ch} {preset} "Needs two args"
  - pc {ch}.{preset}
@end

[00:00.000]
- needs_two 1
"""
        doc = parser.parse_string(source)

        with pytest.raises(Exception) as exc_info:
            resolve_aliases(doc)

        # Check that error mentions the alias name or argument count
        error_msg = str(exc_info.value).lower()
        assert "needs_two" in error_msg or "argument" in error_msg

    # ============================================
    # Real-World Scenario Tests
    # ============================================

    def test_quad_cortex_scene_change(self, parser, resolve_aliases):
        """Test real Quad Cortex scene change scenario."""
        source = """---
title: Quad Cortex Scene Test
---

@alias cortex_scene {ch} {scene:0-7} "Change to scene"
  - cc {ch}.43.{scene}
@end

[00:00.000]
- cortex_scene 1 0

[00:05.000]
- cortex_scene 1 1

[00:10.000]
- cortex_scene 1 2
"""
        doc = parser.parse_string(source)
        resolved_events = resolve_aliases(doc)
        doc.events = resolved_events
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

        cc_events = [e for e in events if e.type.name == "CONTROL_CHANGE"]
        assert len(cc_events) == 3

        # All should be CC43 (scene select)
        assert all(e.data1 == 43 for e in cc_events)

        # Scene numbers: 0, 1, 2
        assert cc_events[0].data2 == 0
        assert cc_events[1].data2 == 1
        assert cc_events[2].data2 == 2

    def test_h90_dual_algo_setup(self, parser, resolve_aliases):
        """Test Eventide H90 dual algorithm setup."""
        source = """---
title: H90 Dual Setup
---

@alias h90_algo_a {ch} {algo} "Set algorithm A"
  - cc {ch}.82.{algo}
@end

@alias h90_algo_b {ch} {algo} "Set algorithm B"
  - cc {ch}.83.{algo}
@end

@alias h90_mix {ch} {percent:percent} "Set A/B mix"
  - cc {ch}.84.{percent}
@end

[00:00.000]
- h90_algo_a 2 10
- h90_algo_b 2 25
- h90_mix 2 50
"""
        doc = parser.parse_string(source)
        resolved_events = resolve_aliases(doc)
        doc.events = resolved_events
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

        cc_events = [e for e in events if e.type.name == "CONTROL_CHANGE"]
        assert len(cc_events) == 3

        # Algo A (CC82)
        assert cc_events[0].data1 == 82
        assert cc_events[0].data2 == 10

        # Algo B (CC83)
        assert cc_events[1].data1 == 83
        assert cc_events[1].data2 == 25

        # Mix (CC84) - 50% → 63
        assert cc_events[2].data1 == 84
        assert cc_events[2].data2 == 63

    def test_complex_live_performance(self, parser, resolve_aliases):
        """Test complex live performance scenario with multiple features."""
        source = """---
title: Live Performance
ppq: 480
tempo: 120
---

@alias cortex_preset {ch} {preset} "Load Cortex preset"
  - pc {ch}.{preset}
@end

@alias expression {ch} {cc} {percent:percent} "Expression pedal"
  - cc {ch}.{cc}.{percent}
@end

@alias scene_with_exp {ch} {scene} {exp_val} "Scene + expression"
  - cc {ch}.43.{scene}
  - expression {ch} 100 {exp_val}
@end

[00:00.000]
- cortex_preset 1 5
- expression 1 100 0

[00:04.000]
- scene_with_exp 1 1 75

[00:08.000]
- scene_with_exp 1 2 50

[00:12.000]
- cortex_preset 1 10
- expression 1 100 100
"""
        doc = parser.parse_string(source)
        resolved_events = resolve_aliases(doc)
        doc.events = resolved_events
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

        pc_events = [e for e in events if e.type.name == "PROGRAM_CHANGE"]
        cc_events = [e for e in events if e.type.name == "CONTROL_CHANGE"]

        # Should have 2 PC events (preset changes)
        assert len(pc_events) == 2

        # Should have 6 CC events:
        # - 00:00.000: expression (1 CC)
        # - 00:04.000: scene_with_exp (2 CCs: scene + expression)
        # - 00:08.000: scene_with_exp (2 CCs: scene + expression)
        # - 00:12.000: expression (1 CC)
        assert len(cc_events) == 6

        # Verify timing is preserved and monotonic
        all_events = sorted(events, key=lambda e: e.time)
        times = [e.time for e in all_events]
        assert times == sorted(times), "Events should be in time order"
