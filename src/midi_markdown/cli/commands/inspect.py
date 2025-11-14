"""Inspect command for analyzing MML files without generating output."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from midi_markdown.cli.error_handler import ErrorContext, cli_error_handler
from midi_markdown.codegen import export_to_csv, export_to_json
from midi_markdown.core import compile_ast_to_ir
from midi_markdown.diagnostics import display_events_table
from midi_markdown.parser.parser import MMDParser


def inspect(
    input_file: Annotated[
        Path,
        typer.Argument(
            help="Input MML file to analyze",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
        ),
    ],
    format: Annotated[
        str,
        typer.Option(
            "--format",
            "-f",
            help="Output format: table, csv, json, json-simple (default: table)",
        ),
    ] = "table",
    limit: Annotated[
        int | None,
        typer.Option(
            "--limit",
            "-n",
            help="Maximum number of events to display (table format only)",
        ),
    ] = None,
    no_stats: Annotated[
        bool,
        typer.Option(
            "--no-stats",
            help="Hide statistics summary (table format only)",
        ),
    ] = False,
    verbose: Annotated[bool, typer.Option("-v", "--verbose")] = False,
    no_color: Annotated[bool, typer.Option("--no-color")] = False,
    debug: Annotated[
        bool,
        typer.Option("--debug", help="Show full error tracebacks"),
    ] = False,
) -> None:
    """Analyze MML file and display events without creating output files.

    The inspect command parses and compiles an MML file to show the resulting
    MIDI events in various formats. Unlike 'compile', it never writes MIDI files.

    Examples:
        midimarkup inspect song.mmd
        midimarkup inspect song.mmd --format json
        midimarkup inspect song.mmd --limit 50 --no-stats
        midimarkup inspect song.mmd -f csv > events.csv
    """
    console = Console(no_color=no_color, force_terminal=not no_color)

    # Create error context
    ctx = ErrorContext(
        mode="inspect",
        debug=debug,
        source_file=input_file,
        no_color=no_color,
        console=console,
    )

    with cli_error_handler(ctx):
        # Validate format
        valid_formats = ["table", "csv", "json", "json-simple"]
        if format not in valid_formats:
            console.print(
                f"[red]Error:[/red] Invalid format '{format}'. "
                f"Valid formats: {', '.join(valid_formats)}"
            )
            raise typer.Exit(1)

        if verbose:
            console.print(f"[cyan]Analyzing:[/cyan] {input_file}")
            console.print(f"[cyan]Format:[/cyan] {format}")

        # 1. Parse MML file
        if verbose:
            console.print("  [dim]Parsing MML file...[/dim]")

        parser = MMDParser()
        doc = parser.parse_file(str(input_file))

        if verbose:
            event_count = len(doc.events) if hasattr(doc, "events") else 0
            track_count = len(doc.tracks) if hasattr(doc, "tracks") else 0
            console.print(
                f"  [dim]Parsed:[/dim] [bold cyan]{event_count}[/bold cyan] "
                f"[dim]events,[/dim] [bold cyan]{track_count}[/bold cyan] [dim]tracks[/dim]"
            )

        # 2. Compile to IR
        if verbose:
            console.print("  [dim]Compiling to IR...[/dim]")

        ppq = doc.frontmatter.get("ppq", 480)
        ir_program = compile_ast_to_ir(doc, ppq=ppq)

        if verbose:
            console.print(
                f"  [dim]Compiled:[/dim] [bold cyan]{ir_program.event_count}[/bold cyan] "
                f"[dim]MIDI events[/dim]"
            )

        # 3. Display based on format
        if format == "table":
            # Display as Rich table
            max_events = limit if limit is not None else 100
            show_stats = not no_stats

            display_events_table(
                ir_program,
                max_events=max_events,
                show_stats=show_stats,
                console=console,
            )

        elif format == "csv":
            # Export to CSV and print to stdout
            csv_output = export_to_csv(ir_program, include_header=True)
            # Print directly to stdout (bypass Rich console for clean CSV)
            print(csv_output)

        elif format == "json":
            # Export to JSON (complete format)
            json_output = export_to_json(ir_program, format="complete", pretty=True)
            # Print directly to stdout
            print(json_output)

        elif format == "json-simple":
            # Export to JSON (simplified format)
            json_output = export_to_json(ir_program, format="simplified", pretty=True)
            # Print directly to stdout
            print(json_output)
