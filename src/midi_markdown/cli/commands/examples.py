"""Show example MML snippets command."""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from midi_markdown.cli.encoding_utils import safe_emoji

# Example MML snippets
EXAMPLES = {
    "hello": {
        "title": "Hello World - Simple Note",
        "description": "Simplest possible MML file with one note",
        "code": """---
title: "Hello MIDI"
tempo: 120
ppq: 480
---

[00:00.000]
- note_on 1.60 80 1b  # Middle C for 1 beat
""",
    },
    "timing": {
        "title": "Timing Paradigms",
        "description": "Three timing modes: absolute, relative, and musical",
        "code": """---
title: "Timing Examples"
tempo: 120
time_signature: [4, 4]
ppq: 480
---

# Absolute time (mm:ss.milliseconds)
[00:00.000]
- note_on 1.60 80 1b

# Relative time (delta from previous)
[+1b]
- note_on 1.64 80 1b

# Musical time (bars.beats.ticks)
[2.1.0]
- note_on 1.67 80 1b

# Simultaneous events
[@]
- note_on 1.72 80 1b
""",
    },
    "cc": {
        "title": "Control Changes",
        "description": "Common MIDI CC messages for automation",
        "code": """---
title: "CC Automation"
tempo: 120
ppq: 480
---

[00:00.000]
- cc 1.7.100   # Channel volume to 100
- cc 1.10.64   # Pan to center
- cc 1.11.127  # Expression maximum
- cc 1.1.64    # Modulation wheel center

# Automate volume over time
[00:01.000]
- cc 1.7.100

[00:02.000]
- cc 1.7.80

[00:03.000]
- cc 1.7.60

[00:04.000]
- cc 1.7.40
""",
    },
    "loop": {
        "title": "Loop Pattern",
        "description": "Repeat a pattern over a time range",
        "code": """---
title: "Loop Example"
tempo: 120
time_signature: [4, 4]
ppq: 480
---

# Simple hi-hat pattern repeated 8 times
@loop from [00:00.000] to [00:08.000] every 0.5b
  - note_on 10.42 80 0.25b  # Closed hi-hat
@end

# Kick drum on beats 1 and 3
@loop from [00:00.000] to [00:08.000] every 1b
  - note_on 10.36 127 0.25b  # Kick
@end
""",
    },
    "alias": {
        "title": "Alias Definition",
        "description": "Create reusable command shortcuts with aliases",
        "code": """---
title: "Alias Example"
tempo: 120
ppq: 480
---

# Define an alias for common chord
@alias cmajor {ch}.{vel} "C major chord"
  - note_on {ch}.60.{vel} 1b
  - note_on {ch}.64.{vel} 1b
  - note_on {ch}.67.{vel} 1b
@end

# Use the alias
[00:00.000]
- cmajor 1.80

[00:02.000]
- cmajor 1.60
""",
    },
}


def examples(
    name: Annotated[str | None, typer.Argument(help="Example name to display")] = None,
) -> None:
    """Show example MML snippets and usage patterns.

    Run without arguments to list all available examples.
    Run with an example name to see the full code with syntax highlighting.

    Examples:
        midimarkup examples          # List all available examples
        midimarkup examples hello    # Show hello world example
        midimarkup examples timing   # Show timing paradigms
        midimarkup examples loop     # Show loop pattern example
    """
    console = Console()

    if name is None:
        # List all examples
        console.print()
        console.print("[bold cyan]Available MML Examples:[/bold cyan]")
        console.print()

        for key in sorted(EXAMPLES.keys()):
            example = EXAMPLES[key]
            console.print(f"  [green bold]{key:12}[/green bold] - {example['title']}")
            console.print(f"               [dim]{example['description']}[/dim]")
            console.print()

        lightbulb = safe_emoji("💡", "[i]")
        console.print(
            f"[dim]{lightbulb} View full code:[/dim] [cyan]midimarkup examples <name>[/cyan]"
        )
        console.print()
        return

    # Show specific example
    if name not in EXAMPLES:
        console.print()
        cross = safe_emoji("✗", "[X]")
        console.print(f"[red]{cross} Unknown example:[/red] [bold]{name}[/bold]")
        console.print()
        console.print("[dim]Available examples:[/dim]")
        for key in sorted(EXAMPLES.keys()):
            console.print(f"  - [green]{key}[/green]")
        console.print()
        console.print(
            "[dim]Run[/dim] [cyan]midimarkup examples[/cyan] [dim]to see all examples[/dim]"
        )
        raise typer.Exit(1)

    example = EXAMPLES[name]

    # Display example with syntax highlighting
    console.print()
    console.print(f"[bold cyan]{example['title']}[/bold cyan]")
    console.print(f"[dim]{example['description']}[/dim]")
    console.print()

    syntax = Syntax(
        example["code"].strip(),
        "yaml",
        theme="monokai",
        line_numbers=True,
        word_wrap=False,
    )
    console.print(Panel(syntax, title=f"[cyan]{name}.mmd[/cyan]", border_style="cyan"))

    console.print()
    console.print("[dim]💡 Try it out:[/dim]")
    console.print(f"   1. Copy the code above to [cyan]{name}.mmd[/cyan]")
    console.print(f"   2. Compile: [cyan]midimarkup compile {name}.mmd[/cyan]")
    console.print(f"   3. Play: [cyan]midimarkup play {name}.mmd --port 0[/cyan]")
    console.print()
