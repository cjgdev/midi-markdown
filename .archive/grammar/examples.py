#!/usr/bin/env python3
"""
Complete Example: MIDI Markup Language Parser Usage

This example demonstrates the full workflow of:
1. Loading the grammar
2. Parsing MML files
3. Validating the result
4. Converting to MIDI (conceptual)
5. Error handling
"""

# Import our MML parser
from mml_parser import (
    MIDICommand,
    MMLParser,
    timing_to_ticks,
    validate_midi_value,
)


def example_1_basic_parsing():
    """Example 1: Basic parsing of a simple MML document"""
    print("=" * 60)
    print("EXAMPLE 1: Basic Parsing")
    print("=" * 60)

    mml_content = """---
title: "Simple Example"
author: "Demo User"
ppq: 480
default_channel: 1
---

# Set initial tempo
[00:00.000]
- tempo 120
- marker "Start"

# Change to program 5
[00:01.000]
- program_change 1.5

# Fade in volume
[00:02.000]
- cc 1.7.0

[00:03.000]
- cc 1.7.64

[00:04.000]
- cc 1.7.127
"""

    # Parse the content
    parser = MMLParser()
    doc = parser.parse_string(mml_content, filename="example1.mml")

    # Display results
    print("\nParsed Document:")
    print(f"  Title: {doc.frontmatter.get('title')}")
    print(f"  Author: {doc.frontmatter.get('author')}")
    print(f"  PPQ: {doc.frontmatter.get('ppq')}")
    print(f"  Number of events: {len(doc.events)}")

    print("\nEvents:")
    for i, event in enumerate(doc.events, 1):
        if isinstance(event, MIDICommand):
            print(f"  {i}. {event.type} - Channel {event.channel}")

    print("\n✓ Example 1 complete\n")


def example_2_aliases_and_imports():
    """Example 2: Using aliases and imports"""
    print("=" * 60)
    print("EXAMPLE 2: Aliases and Device Libraries")
    print("=" * 60)

    # First, create a device library
    device_library = """---
device: Example Device
---

# Simple aliases
@alias dev_preset pc.{channel}.{preset} "Load preset"
@alias dev_volume cc.{channel}.7.{value} "Set volume"

# Macro alias
@alias dev_init {channel} "Initialize device"
  - cc {channel}.7.100
  - cc {channel}.10.64
  - pc {channel}.0
@end
"""

    # Main document that imports the library
    main_document = """---
title: "Alias Example"
---

@import "devices/example_device.mml"

@define MAIN_CHANNEL 1
@define PRESET_NUM 5

[00:00.000]
- dev_init ${MAIN_CHANNEL}

[00:01.000]
- dev_preset ${MAIN_CHANNEL} ${PRESET_NUM}
- dev_volume ${MAIN_CHANNEL} 80
"""

    parser = MMLParser()

    # In a real implementation, imports would be resolved automatically
    # For this example, we'll just parse the main document
    doc = parser.parse_string(main_document, filename="example2.mml")

    print("\nDocument parsed successfully")
    print(f"  Imports: {doc.imports}")
    print(f"  Defines: {doc.defines}")
    print(f"  Events: {len(doc.events)}")

    print("\n✓ Example 2 complete\n")


def example_3_timing_and_tracks():
    """Example 3: Multiple timing formats and tracks"""
    print("=" * 60)
    print("EXAMPLE 3: Timing Formats and Multi-Track")
    print("=" * 60)

    mml_content = """---
title: "Multi-Track Example"
midi_format: 1
---

## Track 1: Control
@track control channel=1

# Absolute time
[00:00.000]
- tempo 120
- time_signature 4/4

# Musical time
[1.1.000]
- marker "Bar 1"
- pc 1.0

# Relative time
[+1b]
- cc 1.7.100

## Track 2: Melody
@track melody channel=2

[1.1.000]
- note_on 2.C4 100 1b

[+1b]
- note_on 2.E4 100 1b

[@]  # Simultaneous with previous
- note_on 2.G4 80 1b
"""

    parser = MMLParser()
    doc = parser.parse_string(mml_content, filename="example3.mml")

    print("\nDocument structure:")
    print(f"  Format: {doc.frontmatter.get('midi_format')}")
    print(f"  Tracks: {len(doc.tracks)}")

    for track in doc.tracks:
        print(f"\n  Track: {track.name}")
        print(f"    Channel: {track.channel}")
        print(f"    Events: {len(track.events)}")

    print("\n✓ Example 3 complete\n")


def example_4_advanced_features():
    """Example 4: Loops, sweeps, and expressions"""
    print("=" * 60)
    print("EXAMPLE 4: Advanced Features")
    print("=" * 60)

    mml_content = """---
title: "Advanced Features"
---

@define BASE_TEMPO 120
@define FAST_TEMPO ${BASE_TEMPO * 1.5}

# Loop example
@loop 4 times at [1.1.0] every 1b
  - note_on 10.C1 100 250ms
@end

# Sweep example
@sweep from [2.1.0] to [6.1.0] every 16t
  - cc 1.7 ramp(0, 127)
@end

# Conditional example
@if ${BASE_TEMPO} > 100
  [00:10.000]
  - tempo ${FAST_TEMPO}
@else
  [00:10.000]
  - tempo ${BASE_TEMPO}
@end

# Random and percent values
[00:15.000]
- cc 1.11 random(60, 100)
- cc 1.10 50%
"""

    parser = MMLParser()
    doc = parser.parse_string(mml_content, filename="example4.mml")

    print("\nAdvanced features parsed:")
    print(f"  Defines: {doc.defines}")
    print(f"  Total events/structures: {len(doc.events)}")

    # Count different event types
    loops = sum(1 for e in doc.events if isinstance(e, dict) and e.get("type") == "loop")
    sweeps = sum(1 for e in doc.events if isinstance(e, dict) and e.get("type") == "sweep")
    conditionals = sum(
        1 for e in doc.events if isinstance(e, dict) and e.get("type") == "conditional"
    )

    print(f"\n  Loops: {loops}")
    print(f"  Sweeps: {sweeps}")
    print(f"  Conditionals: {conditionals}")

    print("\n✓ Example 4 complete\n")


def example_5_error_handling():
    """Example 5: Error handling and validation"""
    print("=" * 60)
    print("EXAMPLE 5: Error Handling")
    print("=" * 60)

    # Example with intentional errors
    invalid_mml = """
[00:00.000]
- cc 1.7.255  # Invalid: CC value must be 0-127

[invalid_time]  # Invalid: malformed timing
- pc 1.0

- note_on 1.C4 200 1b  # Invalid: velocity must be 0-127
"""

    parser = MMLParser()

    print("\nAttempting to parse invalid MML...")
    try:
        doc = parser.parse_string(invalid_mml, filename="invalid.mml")

        # Even if parsing succeeds, validate the values
        print("\nValidating MIDI values...")
        errors = []

        for event in doc.events:
            if isinstance(event, MIDICommand):
                try:
                    if event.channel:
                        validate_midi_value(event.channel, 1, 16, "Channel")
                    if event.data1 is not None:
                        validate_midi_value(event.data1, 0, 127, "Data1")
                    if event.data2 is not None:
                        validate_midi_value(event.data2, 0, 127, "Data2")
                except ValueError as e:
                    errors.append(f"Line {event.source_line}: {e}")

        if errors:
            print("\nValidation errors found:")
            for error in errors:
                print(f"  ✗ {error}")
        else:
            print("  ✓ All values valid")

    except Exception as e:
        print(f"\n✗ Parse error: {e}")
        print("\nThis is expected - the document contains intentional errors")

    # Now try valid MML
    valid_mml = """
[00:00.000]
- cc 1.7.127  # Valid
- note_on 1.C4 100 1b  # Valid
"""

    print("\n\nAttempting to parse valid MML...")
    try:
        doc = parser.parse_string(valid_mml, filename="valid.mml")
        print("  ✓ Parse successful")
        print(f"  ✓ {len(doc.events)} events parsed")
    except Exception as e:
        print(f"  ✗ Unexpected error: {e}")

    print("\n✓ Example 5 complete\n")


def example_6_complete_song():
    """Example 6: A complete song structure"""
    print("=" * 60)
    print("EXAMPLE 6: Complete Song Structure")
    print("=" * 60)

    complete_song = """---
title: "Demo Song"
author: "MML Parser Demo"
date: "2025-10-29"
midi_format: 1
ppq: 480
default_channel: 1
devices:
  - guitar: channel 1
  - bass: channel 2
  - drums: channel 10
---

@define INTRO_TEMPO 90
@define MAIN_TEMPO 120
@define VERSE_PRESET 1
@define CHORUS_PRESET 5

# ============================================
# Track 1: Master Control
# ============================================

## Track 1: Master
@track master

[00:00.000]
- tempo ${INTRO_TEMPO}
- time_signature 4/4
- key_signature Am
- marker "Intro"

[00:08.000]
- tempo ${MAIN_TEMPO}
- marker "Verse 1"
- text "Main section begins"

[00:24.000]
- marker "Chorus"

[00:40.000]
- marker "Verse 2"

[00:56.000]
- marker "Bridge"

[01:12.000]
- marker "Final Chorus"

[01:36.000]
- marker "Outro"

# ============================================
# Track 2: Guitar
# ============================================

## Track 2: Guitar
@track guitar channel=1

[00:00.000]
- pc 1.${VERSE_PRESET}

[00:08.000]
# Verse - clean tone
- cc 1.7.80

[00:24.000]
# Chorus - drive up
- pc 1.${CHORUS_PRESET}
- cc 1.7.110

@sweep from [24.1.0] to [28.1.0] every 16t
  - cc 1.11 ramp(0, 127)
@end

# ============================================
# Track 3: Bass
# ============================================

## Track 3: Bass
@track bass channel=2

[00:08.000]
# Bass pattern (simplified)
@loop 8 times at [8.1.0] every 2b
  - note_on 2.E2 100 500ms
  [+500ms]
  - note_on 2.G2 95 500ms
@end

# ============================================
# Track 4: Drums
# ============================================

## Track 4: Drums
@track drums channel=10

[00:08.000]
# Basic drum pattern
@loop 32 times at [8.1.0] every 1b
  - note_on 10.C1 100 100ms   # Kick
  [+500ms]
  - note_on 10.D1 90 100ms    # Snare
@end
"""

    parser = MMLParser()
    doc = parser.parse_string(complete_song, filename="demo_song.mml")

    print("\nSong Structure:")
    print(f"  Title: {doc.frontmatter.get('title')}")
    print(f"  Author: {doc.frontmatter.get('author')}")
    print(f"  Format: Type {doc.frontmatter.get('midi_format')}")
    print(f"  Resolution: {doc.frontmatter.get('ppq')} PPQ")

    print("\n  Devices:")
    for device in doc.frontmatter.get("devices", []):
        for name, config in device.items():
            print(f"    - {name}: {config}")

    print("\n  Definitions:")
    for name, value in doc.defines.items():
        print(f"    - {name} = {value}")

    print(f"\n  Tracks: {len(doc.tracks)}")
    for i, track in enumerate(doc.tracks, 1):
        print(f"    {i}. {track.name} (Channel {track.channel})")

    print(f"\n  Total events: {len(doc.events)}")

    print("\n✓ Example 6 complete\n")


def example_7_conversion_to_midi():
    """Example 7: Converting parsed MML to MIDI (conceptual)"""
    print("=" * 60)
    print("EXAMPLE 7: MIDI Conversion (Conceptual)")
    print("=" * 60)

    mml_content = """---
title: "Conversion Example"
ppq: 480
---

[00:00.000]
- tempo 120
- pc 1.0

[00:01.000]
- note_on 1.C4 100 1b
"""

    parser = MMLParser()
    doc = parser.parse_string(mml_content)

    print("\nStep 1: Parse MML")
    print(f"  ✓ Parsed {len(doc.events)} events")

    print("\nStep 2: Convert timing to ticks")
    ppq = doc.frontmatter.get("ppq", 480)
    tempo = 120

    # Conceptual conversion
    ticks_list = []
    for event in doc.events:
        if hasattr(event, "timing") and event.timing:
            ticks = timing_to_ticks(event.timing, ppq, tempo)
            ticks_list.append(ticks)
            print(f"  Event at {event.timing.raw} → {ticks} ticks")

    print("\nStep 3: Generate MIDI messages")
    print("  (In actual implementation, this would create MIDI file)")

    for event in doc.events:
        if isinstance(event, MIDICommand):
            if event.type == "program_change":
                print(f"  → Program Change: Ch{event.channel} Program{event.data1}")
            elif event.type == "note_on":
                print(f"  → Note On: Ch{event.channel} Note{event.data1} Vel{event.data2}")
            elif event.type == "tempo":
                print(f"  → Tempo: {event.params.get('args', [''])[0]} BPM")

    print("\nStep 4: Write MIDI file")
    print("  (Would save to output.mid)")

    print("\n✓ Example 7 complete\n")


def main():
    """Run all examples"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  MIDI Markup Language Parser - Complete Examples".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    print("\n")

    examples = [
        example_1_basic_parsing,
        example_2_aliases_and_imports,
        example_3_timing_and_tracks,
        example_4_advanced_features,
        example_5_error_handling,
        example_6_complete_song,
        example_7_conversion_to_midi,
    ]

    for i, example in enumerate(examples, 1):
        try:
            example()
        except Exception as e:
            print(f"\n✗ Example {i} failed with error: {e}\n")
            import traceback

            traceback.print_exc()

    print("=" * 60)
    print("ALL EXAMPLES COMPLETE")
    print("=" * 60)
    print("\nFor more information, see:")
    print("  - GRAMMAR_DOCUMENTATION.md")
    print("  - mml_grammar.lark")
    print("  - mml_parser.py")
    print("  - test_mml_parser.py")
    print("\n")


if __name__ == "__main__":
    main()
