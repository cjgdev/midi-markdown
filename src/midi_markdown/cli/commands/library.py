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
            console.print(f"  • [cyan]{lib}[/cyan]")
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
            if params:
                param_str = ", ".join([p["name"] for p in params])
            else:
                param_str = "[dim]none[/dim]"

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
            console.print(f"  [red]•[/red] {error}")
        console.print()
        raise typer.Exit(1)

    # Success!
    alias_count = len(doc.aliases)
    check = safe_emoji("✓", "[OK]")
    console.print(f"[green]{check} Validation passed[/green]")
    console.print()
    console.print(f"  • [green]{alias_count}[/green] alias(es) defined")
    if doc.frontmatter:
        if "title" in doc.frontmatter:
            console.print(f"  • Title: {doc.frontmatter['title']}")
        if "version" in doc.frontmatter:
            console.print(f"  • Version: {doc.frontmatter['version']}")
    console.print()
    console.print("[dim]The library is valid and ready to use.[/dim]")
    console.print()
