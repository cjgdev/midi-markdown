"""
Test Suite: Aliases

Tests for the MML alias system including simple aliases, enum parameters,
macros, and alias calls.
"""

import pytest

from midi_markdown.alias.resolver import AliasError, AliasResolver
from midi_markdown.expansion.expander import CommandExpander
from midi_markdown.midi.events import MIDIEvent, string_to_event_type


class TestAliases:
    """Test alias system"""

    def test_simple_alias(self, parser):
        """Test simple alias definition"""
        mml = '@alias cortex_preset pc.{channel}.{preset} "Load preset"'
        doc = parser.parse_string(mml)
        assert "cortex_preset" in doc.aliases
        assert doc.aliases["cortex_preset"].name == "cortex_preset"
        assert len(doc.aliases["cortex_preset"].parameters) == 2
        assert doc.aliases["cortex_preset"].parameters[0]["name"] == "channel"
        assert doc.aliases["cortex_preset"].parameters[1]["name"] == "preset"

    def test_alias_with_enum(self, parser):
        """Test alias with enumerated values"""
        mml = '@alias h90_routing cc.{ch}.85.{mode=series:0,parallel:1} "Routing"'
        doc = parser.parse_string(mml)
        assert "h90_routing" in doc.aliases
        alias = doc.aliases["h90_routing"]
        assert len(alias.parameters) == 2
        # Check enum parameter
        mode_param = alias.parameters[1]
        assert mode_param["name"] == "mode"
        assert mode_param["type"] == "enum"
        assert mode_param["enum_values"] == {"series": 0, "parallel": 1}

    def test_macro_alias(self, parser):
        """Test multi-command macro alias"""
        mml = """
@alias cortex_load {ch=1} {preset=0} "Load Quad Cortex preset"
  - cc {ch}.32.0
  - pc {ch}.{preset}
@end
"""
        doc = parser.parse_string(mml)
        assert "cortex_load" in doc.aliases
        alias = doc.aliases["cortex_load"]
        assert alias.is_macro
        assert len(alias.commands) == 2

    def test_alias_call(self, parser):
        """Test calling a defined alias"""
        mml = """
@alias test_alias cc.{ch}.{cc}.{val}
[00:00.000]
- test_alias 1 7 100
"""
        doc = parser.parse_string(mml)
        assert "test_alias" in doc.aliases
        assert len(doc.events) == 1
        # Check that the event contains an alias_call command
        event = doc.events[0]
        assert isinstance(event, dict)
        assert event["type"] == "timed_event"
        assert len(event["commands"]) == 1
        cmd = event["commands"][0]
        assert cmd.type == "alias_call"
        assert cmd.params["alias_name"] == "test_alias"
        assert cmd.params["args"] == [1, 7, 100]

    def test_parameter_with_range(self, parser):
        """Test parameter with explicit range"""
        mml = "@alias test_cmd cc.{ch}.{val:0-100}"
        doc = parser.parse_string(mml)
        alias = doc.aliases["test_cmd"]
        val_param = alias.parameters[1]
        assert val_param["name"] == "val"
        assert val_param["type"] == "range"
        assert val_param["min"] == 0
        assert val_param["max"] == 100

    def test_parameter_with_default(self, parser):
        """Test parameter with default value"""
        mml = "@alias test_cmd cc.{ch}.{val=64}"
        doc = parser.parse_string(mml)
        alias = doc.aliases["test_cmd"]
        val_param = alias.parameters[1]
        assert val_param["name"] == "val"
        assert val_param["default"] == 64

    def test_alias_resolver_undefined_alias(self):
        """Test error when referencing undefined alias"""
        resolver = AliasResolver({})
        with pytest.raises(AliasError) as exc_info:
            resolver.resolve("nonexistent", [1, 2], source_line=10)
        assert "Undefined alias" in str(exc_info.value)
        assert "nonexistent" in str(exc_info.value)

    def test_alias_resolver_parameter_count_mismatch(self, parser):
        """Test error when argument count doesn't match"""
        mml = "@alias test_cmd cc.{ch}.{cc}.{val}"
        doc = parser.parse_string(mml)
        resolver = AliasResolver(doc.aliases)

        # Too few arguments
        with pytest.raises(AliasError) as exc_info:
            resolver.resolve("test_cmd", [1, 2], source_line=10)
        assert "at least 3 arguments" in str(exc_info.value)

        # Too many arguments
        with pytest.raises(AliasError) as exc_info:
            resolver.resolve("test_cmd", [1, 2, 3, 4, 5], source_line=10)
        assert "at most 3 arguments" in str(exc_info.value)

    def test_alias_resolver_parameter_out_of_range(self, parser):
        """Test error when parameter value out of range"""
        mml = "@alias test_cmd cc.{ch:1-16}.{val:0-100}"
        doc = parser.parse_string(mml)
        resolver = AliasResolver(doc.aliases)

        # Channel out of range
        with pytest.raises(AliasError) as exc_info:
            resolver.resolve("test_cmd", [20, 50], source_line=10)
        assert "out of range" in str(exc_info.value)

        # Value out of range
        with pytest.raises(AliasError) as exc_info:
            resolver.resolve("test_cmd", [1, 150], source_line=10)
        assert "out of range" in str(exc_info.value)

    def test_alias_expansion_simple(self, parser):
        """Test expanding a simple alias to MIDI commands"""
        mml = "@alias test_alias cc.{ch}.{cc}.{val}"
        doc = parser.parse_string(mml)
        resolver = AliasResolver(doc.aliases)

        expanded = resolver.resolve("test_alias", [1, 7, 100])
        assert len(expanded) == 1
        assert expanded[0].type == "control_change"
        assert expanded[0].channel == 1
        assert expanded[0].data1 == 7
        assert expanded[0].data2 == 100

    def test_alias_expansion_with_default(self, parser):
        """Test expanding alias with default parameter"""
        mml = "@alias test_alias cc.{ch}.{cc}.{val=64}"
        doc = parser.parse_string(mml)
        resolver = AliasResolver(doc.aliases)

        # Without optional parameter
        expanded = resolver.resolve("test_alias", [1, 7])
        assert len(expanded) == 1
        assert expanded[0].data2 == 64

        # With optional parameter
        expanded = resolver.resolve("test_alias", [1, 7, 100])
        assert expanded[0].data2 == 100

    def test_alias_expansion_enum(self, parser):
        """Test expanding alias with enum parameter"""
        mml = "@alias test_cmd cc.{ch}.85.{mode=series:0,parallel:1}"
        doc = parser.parse_string(mml)
        resolver = AliasResolver(doc.aliases)

        # Using enum name
        expanded = resolver.resolve("test_cmd", [1, "parallel"])
        assert expanded[0].data2 == 1

        # Using numeric value
        expanded = resolver.resolve("test_cmd", [1, 0])
        assert expanded[0].data2 == 0

    def test_end_to_end_compilation_with_aliases(self, parser, resolve_aliases):
        """Test complete compilation with alias expansion"""
        mml = """
@alias cortex_pc pc.{ch}.{preset}
[00:00.000]
- cortex_pc 1 5
"""
        doc = parser.parse_string(mml)

        # Resolve aliases before generating events
        resolved_events = resolve_aliases(doc)
        doc.events = resolved_events

        # Generate MIDI events
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
        assert len(events) == 1
        assert events[0].type.name == "PROGRAM_CHANGE"
        assert events[0].channel == 1
        assert events[0].data1 == 5

    def test_macro_alias_expansion(self, parser):
        """Test expanding multi-command macro alias"""
        mml = """
@alias cortex_load {ch=1} {preset=0} "Load Quad Cortex preset"
  - cc {ch}.32.0
  - pc {ch}.{preset}
@end
"""
        doc = parser.parse_string(mml)
        resolver = AliasResolver(doc.aliases)

        expanded = resolver.resolve("cortex_load", [1, 5])
        assert len(expanded) == 2
        # First command: cc 1.32.0
        assert expanded[0].type == "control_change"
        assert expanded[0].channel == 1
        assert expanded[0].data1 == 32
        assert expanded[0].data2 == 0
        # Second command: pc 1.5
        assert expanded[1].type == "program_change"
        assert expanded[1].channel == 1
        assert expanded[1].data1 == 5

    def test_macro_with_three_commands(self, parser):
        """Test macro alias with 3+ commands"""
        mml = """
@alias full_init {ch} "Initialize device to defaults"
  - cc {ch}.0.0
  - cc {ch}.32.0
  - pc {ch}.0
@end
"""
        doc = parser.parse_string(mml)
        resolver = AliasResolver(doc.aliases)

        expanded = resolver.resolve("full_init", [1])
        assert len(expanded) == 3
        assert expanded[0].type == "control_change"
        assert expanded[1].type == "control_change"
        assert expanded[2].type == "program_change"

    def test_macro_with_note_parameter(self, parser):
        """Test macro with note parameter type"""
        mml = """
@alias chord {ch} {root:note} {vel} "Play a chord with note name"
  - note_on {ch}.{root}.{vel}
  - note_on {ch}.64.{vel}
  - note_on {ch}.67.{vel}
@end
"""
        doc = parser.parse_string(mml)
        resolver = AliasResolver(doc.aliases)

        # Use note name
        expanded = resolver.resolve("chord", [1, "C4", 100])
        assert len(expanded) == 3
        assert expanded[0].data1 == 60  # C4
        assert expanded[1].data1 == 64  # E4
        assert expanded[2].data1 == 67  # G4

    def test_macro_with_percent_parameter(self, parser):
        """Test macro with percent parameter type"""
        mml = """
@alias mixer {ch} {dry:percent} {wet:percent} "Set mixer dry/wet levels"
  - cc {ch}.90.{dry}
  - cc {ch}.91.{wet}
@end
"""
        doc = parser.parse_string(mml)
        resolver = AliasResolver(doc.aliases)

        expanded = resolver.resolve("mixer", [1, 50, 75])
        assert len(expanded) == 2
        assert expanded[0].data2 == 63  # 50% -> 63
        assert expanded[1].data2 == 95  # 75% -> 95

    def test_macro_with_bool_parameter(self, parser):
        """Test macro with bool parameter type"""
        mml = """
@alias toggle_fx {ch} {enabled:bool} "Toggle FX on/off"
  - cc {ch}.80.{enabled}
  - cc {ch}.81.{enabled}
@end
"""
        doc = parser.parse_string(mml)
        resolver = AliasResolver(doc.aliases)

        expanded = resolver.resolve("toggle_fx", [1, "true"])
        assert len(expanded) == 2
        assert expanded[0].data2 == 127
        assert expanded[1].data2 == 127

    def test_macro_with_enum_parameter(self, parser):
        """Test macro with enum parameter type"""
        mml = """
@alias set_mode {ch} {mode=series:0,parallel:1,bypass:127} "Set routing mode"
  - cc {ch}.85.{mode}
@end
"""
        doc = parser.parse_string(mml)
        resolver = AliasResolver(doc.aliases)

        expanded = resolver.resolve("set_mode", [1, "parallel"])
        assert len(expanded) == 1
        assert expanded[0].data2 == 1

    def test_macro_with_mixed_defaults(self, parser):
        """Test macro with mix of required and default parameters"""
        mml = """
@alias load {ch} {preset} {bank=0} "Load preset with optional bank"
  - cc {ch}.0.{bank}
  - pc {ch}.{preset}
@end
"""
        doc = parser.parse_string(mml)
        resolver = AliasResolver(doc.aliases)

        # Use default for bank
        expanded = resolver.resolve("load", [1, 5])
        assert len(expanded) == 2
        assert expanded[0].data2 == 0  # default bank
        assert expanded[1].data1 == 5  # preset

        # Override default
        expanded = resolver.resolve("load", [1, 10, 2])
        assert expanded[0].data2 == 2  # override bank
        assert expanded[1].data1 == 10  # preset

    def test_macro_command_order_preserved(self, parser):
        """Test that macro commands execute in order"""
        mml = """
@alias sequence {ch} "Execute preset sequence"
  - pc {ch}.1
  - pc {ch}.2
  - pc {ch}.3
  - pc {ch}.4
@end
"""
        doc = parser.parse_string(mml)
        resolver = AliasResolver(doc.aliases)

        expanded = resolver.resolve("sequence", [1])
        assert len(expanded) == 4
        for i, cmd in enumerate(expanded, 1):
            assert cmd.data1 == i

    def test_macro_with_description(self, parser):
        """Test macro with description string"""
        mml = """
@alias init {ch} "Initialize device settings"
  - cc {ch}.0.0
  - cc {ch}.32.0
@end
"""
        doc = parser.parse_string(mml)
        assert "init" in doc.aliases
        assert doc.aliases["init"].description == "Initialize device settings"
