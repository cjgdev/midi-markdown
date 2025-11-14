"""List available MIDI ports command."""

from __future__ import annotations

from rich.console import Console
from rich.table import Table

from midi_markdown.runtime.midi_io import MIDIOutputManager


def ports() -> None:
    """List available MIDI input and output ports.

    Displays all MIDI output ports available on the system. Useful for
    finding the correct port name or index to use with the play command.

    Examples:
        midimarkup ports
    """
    console = Console()

    # Try to initialize MIDI output manager
    try:
        manager = MIDIOutputManager()
    except (SystemError, Exception) as e:
        # Handle ALSA initialization errors in headless CI environments
        console.print()
        console.print("[yellow]⚠ No MIDI output ports found[/yellow]")
        console.print()
        console.print(f"[dim]Note: MIDI system initialization failed ({type(e).__name__})[/dim]")
        console.print()
        console.print("[dim]💡 To create virtual MIDI ports:[/dim]")
        console.print()
        console.print("  [bold]macOS:[/bold]")
        console.print("    1. Open [cyan]Audio MIDI Setup[/cyan] (in /Applications/Utilities)")
        console.print("    2. Window → Show MIDI Studio")
        console.print("    3. Double-click [cyan]IAC Driver[/cyan]")
        console.print("    4. Check [green]'Device is online'[/green]")
        console.print()
        console.print("  [bold]Linux:[/bold]")
        console.print("    Install virtual MIDI kernel module:")
        console.print("    [cyan]sudo modprobe snd-virmidi[/cyan]  # or snd-aloop")
        console.print()
        console.print("  [bold]Windows:[/bold]")
        console.print("    Install a virtual MIDI driver:")
        console.print(
            "    - [cyan]loopMIDI[/cyan] - https://www.tobias-erichsen.de/software/loopmidi.html"
        )
        console.print("    - [cyan]VirtualMIDI[/cyan] - Included with some DAWs")
        console.print()
        return

    # Get output ports
    try:
        output_ports = manager.list_ports()
    except Exception as e:
        console.print(f"[red]Error listing MIDI ports:[/red] {e}")
        console.print("[dim]Make sure MIDI drivers are properly installed[/dim]")
        return

    # Display ports
    if output_ports:
        table = Table(title="MIDI Output Ports", show_header=True, header_style="bold cyan")
        table.add_column("Index", style="cyan", justify="right", width=8)
        table.add_column("Port Name", style="green")

        for i, port_name in enumerate(output_ports):
            table.add_row(str(i), port_name)

        console.print()
        console.print(table)
        console.print()
        console.print("[dim]💡 Use port index or name with:[/dim]")
        console.print("   [cyan]midimarkup play song.mmd --port 0[/cyan]")
        console.print('   [cyan]midimarkup play song.mmd --port "IAC Driver Bus 1"[/cyan]')
    else:
        console.print()
        console.print("[yellow]⚠ No MIDI output ports found[/yellow]")
        console.print()
        console.print("[dim]💡 To create virtual MIDI ports:[/dim]")
        console.print()
        console.print("  [bold]macOS:[/bold]")
        console.print("    1. Open [cyan]Audio MIDI Setup[/cyan] (in /Applications/Utilities)")
        console.print("    2. Window → Show MIDI Studio")
        console.print("    3. Double-click [cyan]IAC Driver[/cyan]")
        console.print("    4. Check [green]'Device is online'[/green]")
        console.print()
        console.print("  [bold]Linux:[/bold]")
        console.print("    Install virtual MIDI kernel module:")
        console.print("    [cyan]sudo modprobe snd-virmidi[/cyan]  # or snd-aloop")
        console.print()
        console.print("  [bold]Windows:[/bold]")
        console.print("    Install a virtual MIDI driver:")
        console.print(
            "    - [cyan]loopMIDI[/cyan] - https://www.tobias-erichsen.de/software/loopmidi.html"
        )
        console.print("    - [cyan]VirtualMIDI[/cyan] - Included with some DAWs")
        console.print()
