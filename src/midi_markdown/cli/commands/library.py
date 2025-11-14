"""Library management commands."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from midi_markdown.cli.encoding_utils import safe_emoji
from midi_markdown.parser.parser import MMDParser


def library_list() -> None:
    """List installed device libraries.

    Shows all available device libraries with their alias counts.
    Device libraries are located in the devices/ directory.

    Examples:
        midimarkup library list
    """
    console = Console()

    # Find devices directory relative to this file
    # src/midi_markdown/cli/commands/library.py -> ../../../../devices/
    # (library.py -> commands -> cli -> midi_markdown -> src -> project_root -> devices)
    devices_dir = Path(__file__).parent.parent.parent.parent.parent / "devices"

    if not devices_dir.exists():
        console.print()
        console.print("[yellow]⚠ Device libraries directory not found[/yellow]")
        console.print(f"[dim]Expected location: {devices_dir}[/dim]")
        console.print()
        return

    # Find all .mmd files (excluding README files)
    libraries = sorted([f for f in devices_dir.glob("*.mmd") if not f.stem.startswith("README")])

    if not libraries:
        console.print()
        console.print("[yellow]⚠ No device libraries found[/yellow]")
        console.print(f"[dim]Search path: {devices_dir}[/dim]")
        console.print()
        return

    # Create table
    table = Table(title="Device Libraries", show_header=True, header_style="bold cyan")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("File", style="dim")
    table.add_column("Aliases", style="green", justify="right")
    table.add_column("Description", style="white")

    # Parse each library to count aliases and get info
    parser = MMDParser()
    for lib_file in libraries:
        name = lib_file.stem
        try:
            doc = parser.parse_file(lib_file)
            alias_count = len(doc.aliases) if doc.aliases else 0
            title = doc.frontmatter.get("title", "") if doc.frontmatter else ""
            table.add_row(name, lib_file.name, str(alias_count), title)
        except Exception:
            # If parsing fails, still show the file
            table.add_row(name, lib_file.name, "?", "[dim]Parse error[/dim]")

    console.print()
    console.print(table)
    console.print()
    console.print("[dim]💡 View library details:[/dim] [cyan]midimarkup library info <name>[/cyan]")
    console.print('[dim]💡 Import in MML:[/dim] [cyan]@import "devices/<name>.mmd"[/cyan]')
    console.print()


def library_info(
    name: Annotated[str, typer.Argument(help="Library name to show info for")],
) -> None:
    """Show information about a device library.

    Displays details about a specific device library including metadata
    and a list of all available aliases with their signatures.

    Examples:
        midimarkup library info quad_cortex
        midimarkup library info eventide_h90
    """
    console = Console()

    # Find devices directory
    devices_dir = Path(__file__).parent.parent.parent.parent.parent / "devices"
    lib_file = devices_dir / f"{name}.mmd"

    if not lib_file.exists():
        console.print()
        cross = safe_emoji("✗", "[X]")
        console.print(f"[red]{cross} Library not found:[/red] [bold]{name}[/bold]")
        console.print()
        console.print("[dim]Available libraries:[/dim]")
        libraries = sorted(
            [
                f.stem
                for f in devices_dir.glob("*.mmd")
                if f.exists() and not f.stem.startswith("README")
            ]
        )
        for lib in libraries:
            console.print(f"  - [cyan]{lib}[/cyan]")
        console.print()
        console.print(
            "[dim]Use[/dim] [cyan]midimarkup library list[/cyan] [dim]to see all libraries[/dim]"
        )
        raise typer.Exit(1)

    # Parse library
    try:
        parser = MMDParser()
        doc = parser.parse_file(lib_file)
    except Exception as e:
        console.print()
        cross = safe_emoji("✗", "[X]")
        console.print(f"[red]{cross} Failed to parse library:[/red] {e}")
        console.print()
        raise typer.Exit(1)

    # Display library info
    console.print()
    console.print(f"[bold cyan]Library:[/bold cyan] {name}")
    console.print()

    # Show frontmatter metadata
    if doc.frontmatter:
        if "title" in doc.frontmatter:
            console.print(f"[bold]Title:[/bold] {doc.frontmatter['title']}")
        if "description" in doc.frontmatter:
            console.print(f"[bold]Description:[/bold] {doc.frontmatter['description']}")
        if "version" in doc.frontmatter:
            console.print(f"[bold]Version:[/bold] {doc.frontmatter['version']}")
        console.print()

    # Show aliases
    if doc.aliases:
        console.print(f"[bold]Aliases:[/bold] [green]{len(doc.aliases)}[/green] defined")
        console.print()

        # Create aliases table
        table = Table(show_header=True, header_style="bold")
        table.add_column("Alias", style="cyan", no_wrap=True)
        table.add_column("Parameters", style="yellow")
        table.add_column("Description", style="dim")

        for alias_name, alias_def in sorted(doc.aliases.items()):
            # Build parameter signature
            params = alias_def.parameters if alias_def.parameters else []
            param_str = ", ".join([p["name"] for p in params]) if params else "[dim]none[/dim]"

            # Get description
            description = alias_def.description if alias_def.description else ""

            table.add_row(alias_name, param_str, description)

        console.print(table)
        console.print()
    else:
        console.print("[yellow]No aliases defined in this library[/yellow]")
        console.print()

    console.print(f'[dim]💡 Use in MML:[/dim] [cyan]@import "devices/{name}.mmd"[/cyan]')
    console.print()


def library_validate(
    library_file: Annotated[
        Path,
        typer.Argument(
            help="Device library file to validate",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
        ),
    ],
) -> None:
    """Validate a device library file.

    Checks that a device library file has correct syntax and valid alias
    definitions. Reports any parsing errors or structural issues.

    Examples:
        midimarkup library validate devices/quad_cortex.mmd
        midimarkup library validate my_custom_library.mmd
    """
    console = Console()

    console.print()
    console.print(f"[cyan]Validating library:[/cyan] {library_file}")
    console.print()

    # Parse the library file
    try:
        parser = MMDParser()
        doc = parser.parse_file(library_file)
    except Exception as e:
        cross = safe_emoji("✗", "[X]")
        console.print(f"[red]{cross} Parse error:[/red] {e}")
        console.print()
        console.print("[dim]The library file has syntax errors and cannot be parsed.[/dim]")
        raise typer.Exit(1)

    # Check for aliases
    if not doc.aliases:
        warning = safe_emoji("⚠", "[!]")
        console.print(f"[yellow]{warning} Warning: No aliases defined in this library[/yellow]")
        console.print()
        console.print("[dim]Device libraries should define at least one alias.[/dim]")
        console.print()
        raise typer.Exit(1)

    # Validate alias structure
    errors = []
    for alias_name, alias_def in doc.aliases.items():
        # Check for required fields
        if not alias_def.commands:
            errors.append(f"Alias '{alias_name}' has no commands defined")

        # Check parameters structure
        params = alias_def.parameters if alias_def.parameters else []
        for param in params:
            if "name" not in param:
                errors.append(f"Alias '{alias_name}' has parameter without 'name' field")

    if errors:
        cross = safe_emoji("✗", "[X]")
        console.print(f"[red]{cross} Validation failed with {len(errors)} error(s):[/red]")
        console.print()
        for error in errors:
            console.print(f"  [red]-[/red] {error}")
        console.print()
        raise typer.Exit(1)

    # Success!
    alias_count = len(doc.aliases)
    check = safe_emoji("✓", "[OK]")
    console.print(f"[green]{check} Validation passed[/green]")
    console.print()
    console.print(f"  - [green]{alias_count}[/green] alias(es) defined")
    if doc.frontmatter:
        if "title" in doc.frontmatter:
            console.print(f"  - Title: {doc.frontmatter['title']}")
        if "version" in doc.frontmatter:
            console.print(f"  - Version: {doc.frontmatter['version']}")
    console.print()
    console.print("[dim]The library is valid and ready to use.[/dim]")
    console.print()


def library_search(
    query: Annotated[str, typer.Argument(help="Search query (name, manufacturer, or description)")],
) -> None:
    """Search for device libraries.

    Searches through available device libraries by name, manufacturer,
    or description. Results are displayed with match highlighting.

    Examples:
        midimarkup library search "eventide"
        midimarkup library search "neural"
        midimarkup library search "helix"
    """
    console = Console()

    # Find devices directory
    devices_dir = Path(__file__).parent.parent.parent.parent.parent / "devices"

    if not devices_dir.exists():
        console.print()
        console.print("[yellow]⚠ Device libraries directory not found[/yellow]")
        console.print(f"[dim]Expected location: {devices_dir}[/dim]")
        console.print()
        return

    # Find all .mmd files
    libraries = sorted([f for f in devices_dir.glob("*.mmd") if not f.stem.startswith("README")])

    if not libraries:
        console.print()
        console.print("[yellow]⚠ No device libraries found[/yellow]")
        console.print()
        return

    # Search through libraries
    query_lower = query.lower()
    matches = []
    parser = MMDParser()

    for lib_file in libraries:
        name = lib_file.stem
        try:
            doc = parser.parse_file(lib_file)

            # Search in name
            name_match = query_lower in name.lower()

            # Search in frontmatter
            manufacturer_match = False
            device_match = False
            desc_match = False

            if doc.frontmatter:
                manufacturer = doc.frontmatter.get("manufacturer", "")
                manufacturer_match = query_lower in manufacturer.lower() if manufacturer else False

                device = doc.frontmatter.get("device", "")
                device_match = query_lower in device.lower() if device else False

                description = doc.frontmatter.get("description", "")
                desc_match = query_lower in description.lower() if description else False

            if name_match or manufacturer_match or device_match or desc_match:
                matches.append(
                    {
                        "name": name,
                        "file": lib_file.name,
                        "doc": doc,
                        "match_type": (
                            "name"
                            if name_match
                            else "manufacturer"
                            if manufacturer_match
                            else "device"
                            if device_match
                            else "description"
                        ),
                    }
                )
        except Exception:
            # If parsing fails, still search by name
            if query_lower in name.lower():
                matches.append(
                    {
                        "name": name,
                        "file": lib_file.name,
                        "doc": None,
                        "match_type": "name",
                    }
                )

    # Display results
    console.print()
    if not matches:
        console.print(f"[yellow]No libraries found matching:[/yellow] [bold]{query}[/bold]")
        console.print()
        console.print(
            "[dim]💡 Try different search terms or use[/dim] [cyan]midimarkup library list[/cyan]"
        )
        console.print()
        return

    console.print(
        f"[green]Found {len(matches)} matching librar{'y' if len(matches) == 1 else 'ies'}:[/green]"
    )
    console.print()

    # Create results table
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Device", style="white")
    table.add_column("Manufacturer", style="dim")
    table.add_column("Aliases", style="green", justify="right")
    table.add_column("Match", style="yellow")

    for match in matches:
        name = match["name"]
        doc = match["doc"]

        if doc and doc.frontmatter:
            device = doc.frontmatter.get("device", "")
            manufacturer = doc.frontmatter.get("manufacturer", "")
            alias_count = str(len(doc.aliases)) if doc.aliases else "0"
        else:
            device = ""
            manufacturer = ""
            alias_count = "?"

        match_type = match["match_type"]

        table.add_row(name, device, manufacturer, alias_count, match_type)

    console.print(table)
    console.print()
    console.print("[dim]💡 View details:[/dim] [cyan]midimarkup library info <name>[/cyan]")
    console.print()


def library_create(
    name: Annotated[str, typer.Argument(help="Library name (e.g., my_device)")],
    output_file: Annotated[
        Path | None,
        typer.Option(
            "--output",
            "-o",
            help="Output file path (default: devices/<name>.mmd)",
        ),
    ] = None,
    manufacturer: Annotated[
        str | None,
        typer.Option(
            "--manufacturer",
            "-m",
            help="Device manufacturer name",
        ),
    ] = None,
    device: Annotated[
        str | None,
        typer.Option(
            "--device",
            "-d",
            help="Device full name",
        ),
    ] = None,
    channel: Annotated[
        int,
        typer.Option(
            "--channel",
            "-c",
            help="Default MIDI channel (1-16)",
            min=1,
            max=16,
        ),
    ] = 1,
) -> None:
    """Create a new device library template.

    Creates a new device library file with proper frontmatter structure
    and example alias definitions. This provides a starting point for
    building custom device libraries.

    Examples:
        midimarkup library create my_synth
        midimarkup library create my_synth --manufacturer "Acme" --device "Acme Synth Pro"
        midimarkup library create my_fx --output my_library.mmd --channel 5
    """
    console = Console()

    # Determine output file path
    if output_file is None:
        devices_dir = Path(__file__).parent.parent.parent.parent.parent / "devices"
        output_file = devices_dir / f"{name}.mmd"

    # Check if file exists
    if output_file.exists():
        console.print()
        cross = safe_emoji("✗", "[X]")
        console.print(f"[red]{cross} File already exists:[/red] {output_file}")
        console.print()
        console.print("[dim]Use a different name or delete the existing file first.[/dim]")
        raise typer.Exit(1)

    # Use provided values or defaults
    manufacturer_name = manufacturer or "Unknown Manufacturer"
    device_name = device or name.replace("_", " ").title()

    # Create library template
    template = f"""---
device: {device_name}
manufacturer: {manufacturer_name}
version: 1.0.0
default_channel: {channel}
midi_din: true
midi_usb: true
documentation: https://example.com/midi-spec
---

/*
 * ============================================================================
 * {device_name.upper()} - MMD DEVICE LIBRARY
 * ============================================================================
 *
 * This is a template device library for {device_name}.
 * Edit this file to add device-specific MIDI aliases and commands.
 *
 * IMPORTANT NOTES:
 *
 * 1. Always test aliases with your actual hardware before using in production
 * 2. Add timing delays between messages if device requires them
 * 3. Document any known issues or quirks in this header comment
 * 4. Use descriptive alias names and add descriptions for documentation
 *
 * ============================================================================
 */


# ============================================================================
# PRESET MANAGEMENT
# ============================================================================

/*
 * Basic preset loading aliases.
 * Customize these based on your device's MIDI implementation.
 */

@alias {name}_preset {{ch}} {{preset:0-127}} "Load preset (0-127)"
  - pc {{ch}}.{{preset}}
@end

@alias {name}_preset_next {{ch}} "Next preset"
  - cc {{ch}}.71.127
@end

@alias {name}_preset_prev {{ch}} "Previous preset"
  - cc {{ch}}.71.0
@end


# ============================================================================
# PARAMETER CONTROL
# ============================================================================

/*
 * Common CC parameter controls.
 * Add device-specific parameters here.
 */

@alias {name}_volume {{ch}} {{value:0-127}} "Set volume (CC#7)"
  - cc {{ch}}.7.{{value}}
@end

@alias {name}_expression {{ch}} {{value:0-127}} "Set expression (CC#11)"
  - cc {{ch}}.11.{{value}}
@end

@alias {name}_modulation {{ch}} {{value:0-127}} "Set modulation wheel (CC#1)"
  - cc {{ch}}.1.{{value}}
@end


# ============================================================================
# CUSTOM CONTROLS
# ============================================================================

/*
 * Add device-specific aliases below.
 * Examples:
 *
 * @alias {name}_reverb_mix {{ch}} {{value:0-127}} "Set reverb mix (CC#91)"
 *   - cc {{ch}}.91.{{value}}
 * @end
 *
 * @alias {name}_tap_tempo {{ch}} "Tap tempo"
 *   - cc {{ch}}.80.127
 * @end
 *
 * @alias {name}_bypass {{ch}} {{state=active:127,bypassed:0}} "Bypass toggle"
 *   - cc {{ch}}.102.{{state}}
 * @end
 */


# ============================================================================
# MULTI-COMMAND MACROS
# ============================================================================

/*
 * Complex preset loading or state changes can use multi-command aliases.
 * Example:
 *
 * @alias {name}_load_scene {{ch}} {{bank}} {{preset}} "Load bank and preset"
 *   - cc {{ch}}.0.{{bank}}
 *   [+100ms]
 *   - pc {{ch}}.{{preset}}
 * @end
 */
"""

    # Write template to file
    try:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(template)
    except Exception as e:
        console.print()
        cross = safe_emoji("✗", "[X]")
        console.print(f"[red]{cross} Failed to create library:[/red] {e}")
        console.print()
        raise typer.Exit(1)

    # Success!
    console.print()
    check = safe_emoji("✓", "[OK]")
    console.print(f"[green]{check} Created device library:[/green] {output_file}")
    console.print()
    console.print(f"  - Device: {device_name}")
    console.print(f"  - Manufacturer: {manufacturer_name}")
    console.print(f"  - Default channel: {channel}")
    console.print()
    console.print("[dim]💡 Next steps:[/dim]")
    console.print(f"  1. Edit the file: [cyan]{output_file}[/cyan]")
    console.print("  2. Add device-specific aliases and MIDI commands")
    console.print(f"  3. Validate: [cyan]midimarkup library validate {output_file}[/cyan]")
    console.print(f'  4. Use in MML: [cyan]@import "{output_file.name}"[/cyan]')
    console.print()


def library_install(
    source: Annotated[str, typer.Argument(help="Library source (name or URL)")],
    output_dir: Annotated[
        Path | None,
        typer.Option(
            "--output",
            "-o",
            help="Output directory (default: devices/)",
        ),
    ] = None,
) -> None:
    """Install device library from repository or URL.

    This command is currently a placeholder for future implementation.
    It will allow installing libraries from:
    - A central repository of community-maintained libraries
    - Direct URLs to .mmd files
    - GitHub repositories

    For now, manually download libraries and place them in devices/

    Examples (planned):
        midimarkup library install eventide-h90
        midimarkup library install https://example.com/my_device.mmd
        midimarkup library install github:user/repo/device.mmd
    """
    console = Console()

    console.print()
    console.print("[yellow]⚠ Library installation is not yet implemented[/yellow]")
    console.print()
    console.print("[dim]This feature is planned for a future release.[/dim]")
    console.print()
    console.print("[bold]Current workaround:[/bold]")
    console.print("  1. Download the .mmd library file manually")
    console.print("  2. Place it in the [cyan]devices/[/cyan] directory")
    console.print("  3. Validate it: [cyan]midimarkup library validate devices/<name>.mmd[/cyan]")
    console.print()
    console.print("[bold]Planned features:[/bold]")
    console.print("  - Central repository of community libraries")
    console.print("  - Install from URLs or GitHub")
    console.print("  - Automatic dependency resolution")
    console.print("  - Version management")
    console.print()
    console.print(
        "[dim]Follow progress at:[/dim] [cyan]https://github.com/cjgdev/midi-markdown/issues[/cyan]"
    )
    console.print()
