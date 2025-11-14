"""Integration tests for computed values (Stage 6).

Tests full pipeline: parsing → alias resolution → computation → event generation.
"""

import pytest

from midi_markdown.alias.resolver import AliasResolver


class TestComputedValuesIntegration:
    """Integration tests for computed values in aliases."""

    def test_bpm_to_midi_conversion(self, parser):
        """Test BPM to MIDI CC conversion with computed value."""
        source = """---
title: Test BPM Conversion
---

@alias tempo_cc {ch} {bpm:40-300} "Set tempo via CC"
  {midi_val = int((${bpm} - 40) * 127 / 260)}
  - cc {ch}.81.{midi_val}
@end

[00:00.000]
- tempo_cc 1 120
"""
        doc = parser.parse_string(source)
        resolver = AliasResolver(doc.aliases)

        # Find the tempo_cc call
        event = doc.events[0]
        event["commands"][0]

        # Resolve the alias
        expanded = resolver.resolve(
            alias_name="tempo_cc", arguments=[1, 120], timing=event["timing"]
        )

        # Should expand to a single CC command
        assert len(expanded) == 1
        assert expanded[0].type == "control_change"
        assert expanded[0].channel == 1
        assert expanded[0].data1 == 81  # CC#81
        assert expanded[0].data2 == 39  # (120-40)*127/260 = 39

    def test_percentage_mix_control(self, parser):
        """Test percentage-based mix control with computed complement."""
        source = """---
title: Test Mix Control
---

@alias mix_ab {ch} {a_percent:0-100} "Set A/B mix"
  {b_percent = 100 - ${a_percent}}
  {a_midi = int(${a_percent} * 127 / 100)}
  {b_midi = int(${b_percent} * 127 / 100)}
  - cc {ch}.84.{a_midi}
  - cc {ch}.85.{b_midi}
@end

[00:00.000]
- mix_ab 2 75
"""
        doc = parser.parse_string(source)
        resolver = AliasResolver(doc.aliases)

        # Resolve the alias
        event = doc.events[0]
        expanded = resolver.resolve(alias_name="mix_ab", arguments=[2, 75], timing=event["timing"])

        # Should expand to two CC commands
        assert len(expanded) == 2

        # First command: A mix = 75% → MIDI 95
        assert expanded[0].type == "control_change"
        assert expanded[0].channel == 2
        assert expanded[0].data1 == 84
        assert expanded[0].data2 == 95  # 75 * 127 / 100 = 95

        # Second command: B mix = 25% → MIDI 31
        assert expanded[1].type == "control_change"
        assert expanded[1].channel == 2
        assert expanded[1].data1 == 85
        assert expanded[1].data2 == 31  # 25 * 127 / 100 = 31

    def test_14bit_midi_conversion(self, parser):
        """Test 14-bit value split into MSB/LSB."""
        source = """---
title: Test 14-bit MIDI
---

@alias pitch_14bit {ch} {value:0-16383} "Send 14-bit pitch"
  {msb_val = msb(${value})}
  {lsb_val = lsb(${value})}
  - cc {ch}.96.{lsb_val}
  - cc {ch}.64.{msb_val}
@end

[00:00.000]
- pitch_14bit 3 8192
"""
        doc = parser.parse_string(source)
        resolver = AliasResolver(doc.aliases)

        # Resolve the alias
        event = doc.events[0]
        expanded = resolver.resolve(
            alias_name="pitch_14bit", arguments=[3, 8192], timing=event["timing"]
        )

        # Should expand to two CC commands (LSB, MSB)
        assert len(expanded) == 2

        # LSB command
        assert expanded[0].type == "control_change"
        assert expanded[0].channel == 3
        assert expanded[0].data1 == 96
        assert expanded[0].data2 == 0  # 8192 & 0x7F = 0

        # MSB command
        assert expanded[1].type == "control_change"
        assert expanded[1].channel == 3
        assert expanded[1].data1 == 64
        assert expanded[1].data2 == 64  # (8192 >> 7) & 0x7F = 64

    def test_velocity_curve(self, parser):
        """Test velocity curve application with clamp."""
        source = """---
title: Test Velocity Curve
---

@alias vel_curve {ch} {note:0-127} {vel:0-127} {curve:0-200} "Apply curve"
  {curved_vel = clamp(int(${vel} * ${curve} / 100), 0, 127)}
  - note {ch}.{note}.{curved_vel}
@end

[00:00.000]
- vel_curve 1 60 90 150
"""
        doc = parser.parse_string(source)
        resolver = AliasResolver(doc.aliases)

        # Resolve the alias
        event = doc.events[0]
        expanded = resolver.resolve(
            alias_name="vel_curve", arguments=[1, 60, 90, 150], timing=event["timing"]
        )

        # Should expand to one note command
        assert len(expanded) == 1
        assert expanded[0].type == "note_on"
        assert expanded[0].channel == 1
        assert expanded[0].data1 == 60  # Note
        # Velocity: clamp(90 * 150 / 100, 0, 127) = clamp(135, 0, 127) = 127
        assert expanded[0].data2 == 127

    def test_multiple_computed_values(self, parser):
        """Test multiple computed values in sequence."""
        source = """---
title: Test Multiple Computed
---

@alias complex {ch} {val:0-100} "Complex computation"
  {step1 = ${val} * 2}
  {step2 = ${step1} + 10}
  {step3 = int(${step2} * 127 / 200)}
  - cc {ch}.7.{step3}
@end

[00:00.000]
- complex 1 50
"""
        doc = parser.parse_string(source)
        resolver = AliasResolver(doc.aliases)

        # Resolve the alias
        event = doc.events[0]
        expanded = resolver.resolve(alias_name="complex", arguments=[1, 50], timing=event["timing"])

        # val=50 → step1=100 → step2=110 → step3=int(110*127/200)=int(69.85)=69
        assert len(expanded) == 1
        assert expanded[0].type == "control_change"
        assert expanded[0].data2 == 69

    def test_nested_function_calls(self, parser):
        """Test nested function calls in computed values."""
        source = """---
title: Test Nested Functions
---

@alias nested_calc {ch} {val:0-100} "Nested functions"
  {result = int(round(${val} * 1.27))}
  - cc {ch}.10.{result}
@end

[00:00.000]
- nested_calc 1 50
"""
        doc = parser.parse_string(source)
        resolver = AliasResolver(doc.aliases)

        # Resolve the alias
        event = doc.events[0]
        expanded = resolver.resolve(
            alias_name="nested_calc", arguments=[1, 50], timing=event["timing"]
        )

        # 50 * 1.27 = 63.5 → round(63.5) = 64 → int(64) = 64
        assert len(expanded) == 1
        assert expanded[0].data2 == 64

    def test_scale_range_helper(self, parser):
        """Test scale_range helper function."""
        source = """---
title: Test Scale Range
---

@alias scale_bpm {ch} {bpm:40-300} "Scale BPM to MIDI"
  {midi_val = int(scale_range(${bpm}, 40, 300, 0, 127))}
  - cc {ch}.81.{midi_val}
@end

[00:00.000]
- scale_bpm 1 170
"""
        doc = parser.parse_string(source)
        resolver = AliasResolver(doc.aliases)

        # Resolve the alias
        event = doc.events[0]
        expanded = resolver.resolve(
            alias_name="scale_bpm", arguments=[1, 170], timing=event["timing"]
        )

        # scale_range(170, 40, 300, 0, 127) = (170-40)/(300-40) * 127 = 130/260 * 127 = 63.5 → 63
        assert len(expanded) == 1
        assert expanded[0].data2 == 63

    def test_computation_error_handling(self, parser):
        """Test that computation errors are reported properly."""
        source = """---
title: Test Computation Error
---

@alias bad_calc {ch} {val:0-100} "Bad computation"
  {result = ${val} / 0}
  - cc {ch}.10.{result}
@end

[00:00.000]
- bad_calc 1 50
"""
        doc = parser.parse_string(source)
        resolver = AliasResolver(doc.aliases)

        # Should raise AliasError with computation error details
        from midi_markdown.alias.errors import AliasError

        event = doc.events[0]
        with pytest.raises(AliasError) as exc_info:
            resolver.resolve(alias_name="bad_calc", arguments=[1, 50], timing=event["timing"])

        assert "computation error" in str(exc_info.value).lower()
        assert "division by zero" in str(exc_info.value).lower()

    def test_undefined_variable_error(self, parser):
        """Test error when using undefined variable in computation."""
        source = """---
title: Test Undefined Variable
---

@alias undefined_var {ch} {val:0-100} "Use undefined var"
  {result = ${undefined} + 10}
  - cc {ch}.10.{result}
@end

[00:00.000]
- undefined_var 1 50
"""
        doc = parser.parse_string(source)
        resolver = AliasResolver(doc.aliases)

        # Should raise AliasError with undefined variable error
        from midi_markdown.alias.errors import AliasError

        event = doc.events[0]
        with pytest.raises(AliasError) as exc_info:
            resolver.resolve(alias_name="undefined_var", arguments=[1, 50], timing=event["timing"])

        assert "computation error" in str(exc_info.value).lower()
        assert "undefined variable" in str(exc_info.value).lower()
