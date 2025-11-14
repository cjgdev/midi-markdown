#!/usr/bin/env python3
"""
MMD template generator.

Generates starter MMD files with common patterns and structures.

Usage:
    python generate_template.py --type basic
    python generate_template.py --type song --title "My Song" --tempo 120
    python generate_template.py --type live-set --device quad_cortex
    python generate_template.py --list
"""

import argparse
import sys
from datetime import datetime

TEMPLATES = {
    "basic": """---
title: "{title}"
author: "{author}"
midi_format: 1
ppq: 480
default_channel: 1
default_velocity: 100
tempo: {tempo}
time_signature: [4, 4]
---

[00:00.000]
- tempo {tempo}
- marker "Start"

[00:01.000]
- note_on 1.C4 100 1b
""",
    "song": """---
title: "{title}"
author: "{author}"
date: "{date}"
midi_format: 1
ppq: 480
default_channel: 1
default_velocity: 100
tempo: {tempo}
time_signature: [4, 4]
---

@define MAIN_TEMPO {tempo}
@define VERSE_PRESET 1
@define CHORUS_PRESET 2

# ============================================
# INTRO
# ============================================

[00:00.000]
- tempo ${{MAIN_TEMPO}}
- time_signature 4/4
- key_signature C
- marker "Intro"

# Add your intro commands here

# ============================================
# VERSE 1
# ============================================

[00:16.000]
- marker "Verse 1"

# Add verse 1 commands here

# ============================================
# CHORUS
# ============================================

[00:48.000]
- marker "Chorus"

# Add chorus commands here

# ============================================
# VERSE 2
# ============================================

[01:20.000]
- marker "Verse 2"

# Add verse 2 commands here

# ============================================
# BRIDGE
# ============================================

[01:52.000]
- marker "Bridge"

# Add bridge commands here

# ============================================
# FINAL CHORUS
# ============================================

[02:24.000]
- marker "Final Chorus"

# Add final chorus commands here

# ============================================
# OUTRO
# ============================================

[03:00.000]
- marker "Outro"

# Add outro commands here
""",
    "live-set": """---
title: "{title}"
author: "{author}"
date: "{date}"
midi_format: 1
ppq: 480
default_channel: 1
default_velocity: 100
devices:
  - {device}: channel 1
---

@import "devices/{device}.mmd"

@define MAIN_TEMPO {tempo}
@define INTRO_PRESET 1
@define VERSE_PRESET 2
@define CHORUS_PRESET 3

# ============================================
# Song: {title}
# Live Performance Automation
# ============================================

# --- INTRO ---
[00:00.000]
- marker "Intro"
- tempo ${{MAIN_TEMPO}}
# Add device preset loading here

# --- VERSE 1 ---
[00:16.000]
- marker "Verse 1"
# Add preset changes and automation here

# --- CHORUS ---
[00:48.000]
- marker "Chorus"
# Add preset changes and automation here

# --- OUTRO ---
[03:00.000]
- marker "Outro"
# Add final automation here
""",
    "drums": """---
title: "{title} - Drums"
author: "{author}"
midi_format: 1
ppq: 480
default_channel: 10  # GM drums on channel 10
tempo: {tempo}
time_signature: [4, 4]
---

# GM Drum Map Reference:
# C1  (36) - Kick
# D1  (38) - Snare
# F#2 (42) - Closed Hi-Hat
# A#2 (46) - Open Hi-Hat
# D2  (45) - Low Tom
# G2  (48) - High Tom
# C#3 (49) - Crash Cymbal
# D#3 (51) - Ride Cymbal

@define KICK 36
@define SNARE 38
@define HIHAT_CLOSED 42
@define HIHAT_OPEN 46

# ============================================
# Basic Rock Beat
# ============================================

[1.1.0]
- marker "Beat"

@loop 16 times at [1.1.0] every 1b
  # Kick on beats 1 and 3
  - note_on 10.${{KICK}} 110 0.1b
  [@]
  - note_on 10.${{HIHAT_CLOSED}} 70 0.1b

  [+1b]
  # Snare on beats 2 and 4
  - note_on 10.${{SNARE}} 90 0.1b
  [@]
  - note_on 10.${{HIHAT_CLOSED}} 65 0.1b
@end
""",
    "automation": """---
title: "{title} - Automation"
author: "{author}"
midi_format: 1
ppq: 480
default_channel: 1
tempo: {tempo}
---

# ============================================
# Volume Automation
# ============================================

[00:00.000]
- marker "Volume Fade In"

# Fade from silence to full
@sweep from [00:00.000] to [00:04.000] every 100ms
  - cc 1.7 ramp(0, 100, ease-out)
@end

# ============================================
# Filter Automation
# ============================================

[00:08.000]
- marker "Filter Sweep"

# Filter opening
@sweep from [00:08.000] to [00:12.000] every 50ms
  - cc 1.74 ramp(0, 127, exponential)
@end

# ============================================
# Expression Automation
# ============================================

[00:16.000]
- marker "Expression Swell"

# Expression curve
- cc 1.11.curve(0, 127, ease-in-out)

# ============================================
# Pan Automation
# ============================================

[00:24.000]
- marker "Auto-Pan"

# LFO panning
- cc 1.10.wave(sine, 64, freq=2.0, depth=80)
""",
    "minimal": """---
title: "{title}"
ppq: 480
tempo: {tempo}
---

[00:00.000]
- tempo {tempo}
- note_on 1.C4 100 1b
""",
}


def list_templates():
    """List available templates."""
    for name, template in TEMPLATES.items():
        template.strip().split("\n")
        desc = f"  {name:15} - "
        if name == "basic":
            desc += "Basic MMD file with frontmatter and one note"
        elif name == "song":
            desc += "Full song structure with sections and markers"
        elif name == "live-set":
            desc += "Live performance automation template"
        elif name == "drums":
            desc += "GM drum pattern template"
        elif name == "automation":
            desc += "Automation examples (volume, filter, pan)"
        elif name == "minimal":
            desc += "Absolute minimum MMD file"


def generate_template(template_type: str, **kwargs):
    """Generate a template with given parameters."""
    if template_type not in TEMPLATES:
        sys.exit(1)

    # Set defaults
    params = {
        "title": kwargs.get("title", "Untitled"),
        "author": kwargs.get("author", "Your Name"),
        "date": kwargs.get("date", datetime.now().strftime("%Y-%m-%d")),
        "tempo": kwargs.get("tempo", 120),
        "device": kwargs.get("device", "quad_cortex"),
    }

    template = TEMPLATES[template_type]
    return template.format(**params)


def main():
    parser = argparse.ArgumentParser(
        description="Generate MMD file templates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --list
  %(prog)s --type basic
  %(prog)s --type song --title "My Song" --tempo 140
  %(prog)s --type live-set --device eventide_h90
  %(prog)s --type drums --title "Rock Beat"
        """,
    )

    parser.add_argument("--list", action="store_true", help="List available templates")
    parser.add_argument("--type", choices=TEMPLATES.keys(), help="Template type")
    parser.add_argument("--title", default="Untitled", help="Song/file title")
    parser.add_argument("--author", default="Your Name", help="Author name")
    parser.add_argument("--tempo", type=int, default=120, help="Default tempo (BPM)")
    parser.add_argument(
        "--device",
        default="quad_cortex",
        choices=["quad_cortex", "eventide_h90", "helix", "hx_stomp", "hx_effects", "hx_stomp_xl"],
        help="Device for live-set template",
    )
    parser.add_argument("-o", "--output", help="Output file (default: stdout)")

    args = parser.parse_args()

    if args.list:
        list_templates()
        sys.exit(0)

    if not args.type:
        parser.print_help()
        sys.exit(1)

    # Generate template
    output = generate_template(
        args.type, title=args.title, author=args.author, tempo=args.tempo, device=args.device
    )

    # Write output
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
    else:
        pass


if __name__ == "__main__":
    main()
