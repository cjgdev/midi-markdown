"""Integration tests for device library parsing and usage."""

from pathlib import Path

import pytest

from midi_markdown.expansion.expander import CommandExpander
from midi_markdown.midi.events import MIDIEvent, string_to_event_type


class TestDeviceLibraries:
    """Test that device libraries parse correctly and can be used."""

    @pytest.fixture
    def devices_dir(self):
        """Get devices directory path."""
        return Path(__file__).parent.parent.parent / "devices"

    # ============================================
    # Library Parsing Tests
    # ============================================

    def test_quad_cortex_library_parses(self, parser, devices_dir):
        """Test that Quad Cortex library parses without errors."""
        library_path = devices_dir / "quad_cortex.mmd"
        assert library_path.exists(), "Quad Cortex library not found"

        with open(library_path, encoding="utf-8") as f:
            content = f.read()

        # Should parse without errors
        doc = parser.parse_string(content)

        # Check frontmatter
        assert doc.frontmatter.get("device") == "Neural DSP Quad Cortex"
        assert doc.frontmatter.get("manufacturer") == "Neural DSP"

        # Check that aliases are defined
        assert len(doc.aliases) > 0
        assert "qc_preset" in doc.aliases
        assert "qc_scene" in doc.aliases

    def test_eventide_h90_library_parses(self, parser, devices_dir):
        """Test that Eventide H90 library parses without errors."""
        library_path = devices_dir / "eventide_h90.mmd"
        assert library_path.exists(), "Eventide H90 library not found"

        with open(library_path, encoding="utf-8") as f:
            content = f.read()

        # Should parse without errors
        doc = parser.parse_string(content)

        # Check frontmatter
        assert doc.frontmatter.get("device") == "Eventide H90"
        assert doc.frontmatter.get("manufacturer") == "Eventide"

        # Check that aliases are defined
        assert len(doc.aliases) > 0

    def test_helix_library_parses(self, parser, devices_dir):
        """Test that Line 6 Helix Floor/LT/Rack library parses without errors."""
        library_path = devices_dir / "helix.mmd"
        assert library_path.exists(), "Line 6 Helix library not found"

        with open(library_path, encoding="utf-8") as f:
            content = f.read()

        # Should parse without errors
        doc = parser.parse_string(content)

        # Check frontmatter
        assert "Helix" in doc.frontmatter.get("device", "")
        assert doc.frontmatter.get("manufacturer") == "Line 6"

        # Check that aliases are defined
        assert len(doc.aliases) > 0
        assert "helix_load" in doc.aliases
        assert "helix_snap_1" in doc.aliases

    def test_hx_effects_library_parses(self, parser, devices_dir):
        """Test that HX Effects library parses without errors."""
        library_path = devices_dir / "hx_effects.mmd"
        assert library_path.exists(), "HX Effects library not found"

        with open(library_path, encoding="utf-8") as f:
            content = f.read()

        # Should parse without errors
        doc = parser.parse_string(content)

        # Check frontmatter
        assert "HX Effects" in doc.frontmatter.get("device", "")
        assert doc.frontmatter.get("manufacturer") == "Line 6"

        # Check that aliases are defined
        assert len(doc.aliases) > 0

    def test_hx_stomp_library_parses(self, parser, devices_dir):
        """Test that HX Stomp library parses without errors."""
        library_path = devices_dir / "hx_stomp.mmd"
        assert library_path.exists(), "HX Stomp library not found"

        with open(library_path, encoding="utf-8") as f:
            content = f.read()

        # Should parse without errors
        doc = parser.parse_string(content)

        # Check frontmatter
        assert "HX Stomp" in doc.frontmatter.get("device", "")
        assert doc.frontmatter.get("manufacturer") == "Line 6"

        # Check that aliases are defined
        assert len(doc.aliases) > 0

    def test_hx_stomp_xl_library_parses(self, parser, devices_dir):
        """Test that HX Stomp XL library parses without errors."""
        library_path = devices_dir / "hx_stomp_xl.mmd"
        assert library_path.exists(), "HX Stomp XL library not found"

        with open(library_path, encoding="utf-8") as f:
            content = f.read()

        # Should parse without errors
        doc = parser.parse_string(content)

        # Check frontmatter
        assert "HX Stomp XL" in doc.frontmatter.get("device", "")
        assert doc.frontmatter.get("manufacturer") == "Line 6"

        # Check that aliases are defined
        assert len(doc.aliases) > 0

    # ============================================
    # Alias Usage Tests (Quad Cortex)
    # ============================================

    def test_cortex_preset_change(self, parser, resolve_aliases):
        """Test Quad Cortex preset change alias."""
        source = """---
title: Cortex Preset Test
---

@alias cortex_preset {ch} {preset:0-127} "Load preset"
  - pc {ch}.{preset}
@end

[00:00.000]
- cortex_preset 1 42
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
        assert len(pc_events) == 1
        assert pc_events[0].channel == 1
        assert pc_events[0].data1 == 42

    def test_cortex_scene_switch(self, parser, resolve_aliases):
        """Test Quad Cortex scene switching."""
        source = """---
title: Cortex Scene Test
---

@alias cortex_scene {ch} {scene:0-7} "Switch to scene"
  - cc {ch}.34.{scene}
@end

[00:00.000]
- cortex_scene 1 3
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
        assert cc_events[0].channel == 1
        assert cc_events[0].data1 == 34  # CC number
        assert cc_events[0].data2 == 3  # Scene D

    def test_cortex_complete_load(self, parser, resolve_aliases):
        """Test Quad Cortex complete preset load sequence."""
        source = """---
title: Cortex Complete Load Test
---

@alias cortex_load {ch} {setlist} {group} {preset} "Complete preset load"
  - cc {ch}.32.{setlist}
  - cc {ch}.0.{group}
  - pc {ch}.{preset}
@end

[00:00.000]
- cortex_load 1 2 5 10
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

        # Should have 2 CC events and 1 PC event
        cc_events = [e for e in events if e.type.name == "CONTROL_CHANGE"]
        pc_events = [e for e in events if e.type.name == "PROGRAM_CHANGE"]

        assert len(cc_events) == 2
        assert len(pc_events) == 1

        # Check setlist CC
        assert cc_events[0].data1 == 32
        assert cc_events[0].data2 == 2

        # Check group CC
        assert cc_events[1].data1 == 0
        assert cc_events[1].data2 == 5

        # Check preset PC
        assert pc_events[0].data1 == 10

    # ============================================
    # Alias Usage Tests (Helix)
    # ============================================

    def test_helix_snapshot_change(self, parser, resolve_aliases):
        """Test Helix snapshot change."""
        source = """---
title: Helix Snapshot Test
---

@alias helix_snapshot {ch} {snapshot:0-7} "Select snapshot"
  - cc {ch}.69.{snapshot}
@end

[00:00.000]
- helix_snapshot 1 2
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
        assert cc_events[0].channel == 1
        assert cc_events[0].data1 == 69  # Snapshot CC
        assert cc_events[0].data2 == 2  # Snapshot 3

    def test_helix_bank_preset(self, parser, resolve_aliases):
        """Test Helix bank + preset change."""
        source = """---
title: Helix Bank Preset Test
---

@alias helix_bank_preset {ch} {bank:0-63} {preset:0-127} "Select bank and preset"
  - cc {ch}.0.{bank}
  - pc {ch}.{preset}
@end

[00:00.000]
- helix_bank_preset 1 5 20
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
        pc_events = [e for e in events if e.type.name == "PROGRAM_CHANGE"]

        assert len(cc_events) == 1
        assert len(pc_events) == 1

        # Bank MSB
        assert cc_events[0].data1 == 0
        assert cc_events[0].data2 == 5

        # Preset
        assert pc_events[0].data1 == 20

    # ============================================
    # Real-World Scenario Tests
    # ============================================

    def test_live_performance_multi_device(self, parser, resolve_aliases):
        """Test a realistic live performance scenario with multiple devices."""
        source = """---
title: Multi-Device Live Performance
tempo: 120
---

@alias cortex_scene {ch} {scene:0-7} "Cortex scene"
  - cc {ch}.34.{scene}
@end

@alias helix_snapshot {ch} {snapshot:0-7} "Helix snapshot"
  - cc {ch}.69.{snapshot}
@end

# Intro - Clean tones
[00:00.000]
- cortex_scene 1 0
- helix_snapshot 2 0

# Verse - Rhythm tones
[00:08.000]
- cortex_scene 1 1
- helix_snapshot 2 1

# Chorus - Full band
[00:16.000]
- cortex_scene 1 2
- helix_snapshot 2 2

# Solo - Lead tones
[00:24.000]
- cortex_scene 1 3
- helix_snapshot 2 3
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

        # Should have 8 CC events (4 cortex + 4 helix)
        cc_events = [e for e in events if e.type.name == "CONTROL_CHANGE"]
        assert len(cc_events) == 8

        # Verify channels (cortex on 1, helix on 2)
        cortex_events = [e for e in cc_events if e.channel == 1]
        helix_events = [e for e in cc_events if e.channel == 2]

        assert len(cortex_events) == 4
        assert len(helix_events) == 4

        # Verify CC numbers
        assert all(e.data1 == 34 for e in cortex_events)  # Cortex scene CC
        assert all(e.data1 == 69 for e in helix_events)  # Helix snapshot CC
