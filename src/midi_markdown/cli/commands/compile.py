"""Compile command implementation - MML to MIDI compilation."""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Annotated

import typer
from lark.exceptions import UnexpectedCharacters, UnexpectedToken
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from midi_markdown.cli.errors import (
    show_expansion_error,
    show_parse_error,
    show_success,
    show_validation_error,
)
from midi_markdown.cli.progress import (
    CompilationProgress,
    create_compilation_progress,
    should_show_progress,
)
from midi_markdown.constants import DEFAULT_TIME_SIGNATURE
from midi_markdown.expansion.expander import CommandExpander


def compile(
    input_file: Annotated[
        Path,
        typer.Argument(
            help="Input .mmd file to compile",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
        ),
    ],
    output: Annotated[
        Path | None,
        typer.Option(
            "-o",
            "--output",
            help="Output .mid file (default: same as input with .mid extension)",
        ),
    ] = None,
    ppq: Annotated[
        int,
        typer.Option(help="Pulses per quarter note / resolution (default: 480)"),
    ] = 480,
    output_format: Annotated[
        str,
        typer.Option(
            "--format",
            "-f",
            help="Output format: midi, table, csv, json, json-simple (default: midi)",
        ),
    ] = "midi",
    midi_format: Annotated[
        int,
        typer.Option(
            "--midi-format", help="MIDI file format: 0=single track, 1=multi-track, 2=async"
        ),
    ] = 1,
    validate: Annotated[
        bool,
        typer.Option("--validate/--no-validate", help="Validate before compiling"),
    ] = True,
    verbose: Annotated[
        bool,
        typer.Option("-v", "--verbose", help="Verbose output"),
    ] = False,
    no_color: Annotated[
        bool,
        typer.Option("--no-color", help="Disable colored output (accessibility)"),
    ] = False,
    no_emoji: Annotated[
        bool,
        typer.Option("--no-emoji", help="Disable emoji in output (accessibility)"),
    ] = False,
    debug: Annotated[
        bool,
        typer.Option("--debug", help="Show full error tracebacks"),
    ] = False,
    no_progress: Annotated[
        bool,
        typer.Option("--no-progress", help="Disable progress indicators"),
    ] = False,
) -> None:
    """Compile MML file to MIDI or other output formats.

    Parses an MML source file, resolves aliases and imports, expands advanced
    features (loops, variables, sweeps), validates MIDI commands, and generates
    output in the specified format.

    The default output is a Standard MIDI File (.mid), but you can also export
    to human-readable formats (table, CSV, JSON) for analysis and debugging.

    Examples:
        # Basic compilation to MIDI file
        midimarkup compile song.mmd

        # Specify custom output path
        midimarkup compile song.mmd -o output/performance.mid

        # High-resolution MIDI (960 PPQ for precise timing)
        midimarkup compile song.mmd --ppq 960

        # Export to CSV for spreadsheet analysis
        midimarkup compile song.mmd --format csv -o events.csv

        # Export to JSON for programmatic processing
        midimarkup compile song.mmd --format json -o data.json

        # Display events as formatted table (no file output)
        midimarkup compile song.mmd --format table

        # Verbose output showing compilation steps
        midimarkup compile song.mmd -v

        # Compile with progress bars for large files
        midimarkup compile large_song.mmd --verbose

        # Skip validation for faster compilation (not recommended)
        midimarkup compile song.mmd --no-validate

    Output Formats:
        midi         Standard MIDI File (.mid) - default format
        table        Pretty-printed table in terminal (for quick inspection)
        csv          midicsv-compatible CSV format (for spreadsheet tools)
        json         Complete MIDI event data with metadata
        json-simple  Simplified JSON for music analysis tools

    MIDI File Formats:
        0  Single-track format (all events in one track)
        1  Multi-track format (separate tracks) - default
        2  Async multi-track (independent sequences)

    Notes:
        - Validation is enabled by default and highly recommended
        - Progress indicators appear automatically for large files (>50KB or >500 events)
        - Use --no-color and --no-emoji for accessibility or scripting
        - Exit code 0 on success, non-zero on errors
    """
    # Detect accessibility settings from environment
    if os.getenv("NO_COLOR") or os.getenv("CI"):
        no_color = True

    # Auto-detect limited console encodings (e.g., Windows charmap)
    # and disable emoji to prevent UnicodeEncodeError
    from midi_markdown.cli.encoding_utils import should_disable_emoji

    no_emoji = should_disable_emoji(no_emoji)

    # Create console with appropriate settings
    output_console = Console(no_color=no_color, force_terminal=not no_color)

    # For MIDI format, default output file; for other formats, output to stdout
    if output is None and output_format == "midi":
        output = input_file.with_suffix(".mid")

    # Print compilation info (but not for non-MIDI formats that go to stdout)
    if output_format == "midi" or output is not None:
        if not no_color:
            output_console.print(f"[cyan]Compiling:[/cyan] {input_file}")
            if output:
                output_console.print(f"[cyan]Output:[/cyan] {output}")
        else:
            output_console.print(f"Compiling: {input_file}")
            if output:
                output_console.print(f"Output: {output}")

    try:
        # Start compilation timer
        start_time = time.time()

        # Parse the file first to check if we should show progress
        if verbose:
            output_console.print("  [dim]Parsing MML file...[/dim]")

        from midi_markdown.parser.parser import MMDParser

        try:
            parser = MMDParser()
            doc = parser.parse_file(input_file)
        except (UnexpectedToken, UnexpectedCharacters) as parse_error:
            # Use structured parse error display
            show_parse_error(
                parse_error, input_file, output_console, no_color=no_color, no_emoji=no_emoji
            )
            raise typer.Exit(code=1)

        if verbose:
            output_console.print(
                f"  [dim]Parsed: {len(doc.events)} events, {len(doc.tracks)} tracks[/dim]"
            )

        # Determine if we should show progress (for large files or verbose mode)
        outputs_to_stdout = output_format != "midi" and output is None
        use_progress = (
            should_show_progress(input_file, doc, verbose, no_progress)
            and not no_color
            and not outputs_to_stdout
        )

        # Use new progress indicator for large files
        if use_progress:
            progress_bar = create_compilation_progress(output_console)
            progress_ctx = CompilationProgress(progress_bar)
        else:
            # Use simple spinner for small files in non-verbose mode
            progress_ctx = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=output_console,
                disable=verbose or no_color or outputs_to_stdout,
            )

        with progress_ctx as progress:
            # Note: parsing already completed above
            if isinstance(progress, CompilationProgress):
                progress.parsing_complete()
            elif not verbose and hasattr(progress, "add_task"):
                progress.add_task("Processing...", total=None)

            # 2. Process imports (load device libraries)
            if doc.imports:
                if verbose:
                    output_console.print(f"  [dim]Loading {len(doc.imports)} import(s)...[/dim]")

                from midi_markdown.alias.imports import ImportManager

                import_manager = ImportManager(parser)

                try:
                    imported_aliases = import_manager.resolve_imports(
                        imports=doc.imports, current_file=str(input_file)
                    )

                    # Merge imported aliases into document
                    # Check for conflicts with document's own aliases
                    for alias_name, alias_def in imported_aliases.items():
                        if alias_name in doc.aliases:
                            msg = (
                                f"Alias name conflict: '{alias_name}' is defined both in imported library "
                                f"and in {input_file}\n\n"
                                f"Suggestion: Rename the alias in your file or use a different device library."
                            )
                            raise Exception(msg)
                        doc.aliases[alias_name] = alias_def

                    if verbose:
                        output_console.print(
                            f"  [dim]Loaded {len(imported_aliases)} alias(es) from imports[/dim]"
                        )

                except Exception as import_error:
                    output_console.print(f"[red]✗ Import Error:[/red] {import_error}")
                    if verbose:
                        import traceback

                        output_console.print(f"[dim]{traceback.format_exc()}[/dim]")
                    raise typer.Exit(code=1)

            # 3. Resolve aliases (expand alias calls to MIDI commands)
            if doc.aliases or any(
                isinstance(e, dict) and e.get("type") == "alias_call" for e in doc.events
            ):
                if isinstance(progress, CompilationProgress):
                    progress.aliases_complete()

                if verbose:
                    output_console.print("  [dim]Resolving aliases...[/dim]")

                from midi_markdown.alias.errors import AliasError
                from midi_markdown.alias.resolver import AliasResolver

                try:
                    alias_resolver = AliasResolver(doc.aliases)

                    # Resolve all alias calls in events
                    # Handle nested structure: timed_event -> commands -> MIDICommand objects
                    resolved_events = []
                    alias_count = 0

                    for event in doc.events:
                        # Handle timed_event blocks with commands list
                        if isinstance(event, dict) and event.get("type") == "timed_event":
                            commands = event.get("commands", [])
                            resolved_commands = []

                            for cmd in commands:
                                # Check if it's an alias_call MIDICommand object
                                if hasattr(cmd, "type") and cmd.type == "alias_call":
                                    # Extract alias call details from params
                                    alias_name = cmd.params.get("alias_name", "")
                                    args = cmd.params.get("args", [])
                                    timing = event.get(
                                        "timing"
                                    )  # Get timing from parent timed_event
                                    source_line = cmd.source_line

                                    # Resolve alias to MIDI commands
                                    expanded_commands = alias_resolver.resolve(
                                        alias_name=alias_name,
                                        arguments=args,
                                        timing=timing,
                                        source_line=source_line,
                                    )

                                    # Add all expanded commands
                                    resolved_commands.extend(expanded_commands)
                                    alias_count += 1
                                else:
                                    # Keep non-alias commands as-is
                                    resolved_commands.append(cmd)

                            # Update event with resolved commands
                            event["commands"] = resolved_commands
                            resolved_events.append(event)

                        # Handle direct alias_call events (if they exist)
                        elif isinstance(event, dict) and event.get("type") == "alias_call":
                            alias_name = event.get("alias_name", "")
                            args = event.get("args", [])
                            timing = event.get("timing")
                            source_line = event.get("source_line", 0)

                            # Resolve alias and add as separate timed events
                            expanded_commands = alias_resolver.resolve(
                                alias_name=alias_name,
                                arguments=args,
                                timing=timing,
                                source_line=source_line,
                            )

                            # Wrap each in a timed_event structure
                            for cmd in expanded_commands:
                                resolved_events.append(
                                    {"type": "timed_event", "timing": timing, "commands": [cmd]}
                                )
                            alias_count += 1
                        else:
                            # Keep other events as-is
                            resolved_events.append(event)

                    doc.events = resolved_events

                    if verbose and alias_count > 0:
                        output_console.print(f"  [dim]Resolved {alias_count} alias call(s)[/dim]")

                except AliasError as alias_error:
                    emoji = "" if no_emoji else "✗ "
                    if no_color:
                        output_console.print(f"{emoji}Alias Error: {alias_error}")
                    else:
                        output_console.print(f"[red]{emoji}Alias Error:[/red] {alias_error}")
                    if verbose:
                        import traceback

                        output_console.print(f"[dim]{traceback.format_exc()}[/dim]")
                    raise typer.Exit(code=1)

            # 4. Validate (if enabled)
            if validate:
                if isinstance(progress, CompilationProgress):
                    progress.validation_complete()

                if verbose:
                    output_console.print("  [dim]Validating...[/dim]")

                from midi_markdown.utils import DocumentValidator, TimingValidator

                # Run value validation
                doc_validator = DocumentValidator()
                value_errors = doc_validator.validate(doc)

                # Run timing validation
                timing_validator = TimingValidator()
                timing_errors = timing_validator.validate(doc)

                all_errors = value_errors + timing_errors

                if all_errors:
                    # Display validation errors with rich formatting
                    for error in all_errors:
                        show_validation_error(error, input_file, output_console, no_color, no_emoji)
                    raise typer.Exit(code=1)

                if verbose:
                    emoji = "" if no_emoji else "✓ "
                    if no_color:
                        output_console.print(f"  {emoji}Validation passed")
                    else:
                        output_console.print(f"  [green]{emoji}Validation passed[/green]")

            # 5. Expand commands (variables, loops, sweeps)
            if verbose:
                output_console.print("  [dim]Expanding commands...[/dim]")

            # Extract config values from frontmatter
            ppq_value = doc.frontmatter.get("ppq", ppq)
            tempo_value = float(doc.frontmatter.get("tempo", 120.0)) if doc.frontmatter else 120.0

            # Extract time signature from frontmatter (default to 4/4)
            time_sig_value = DEFAULT_TIME_SIGNATURE
            if doc.frontmatter and "time_signature" in doc.frontmatter:
                ts = doc.frontmatter["time_signature"]
                if isinstance(ts, list | tuple) and len(ts) == 2:
                    time_sig_value = tuple(ts)

            from midi_markdown.expansion.errors import ExpansionError

            try:
                expander = CommandExpander(
                    ppq=ppq_value,
                    tempo=tempo_value,
                    time_signature=time_sig_value,
                    source_file=str(input_file),
                )

                # Populate symbol table from parser defines
                for name, value in (doc.defines or {}).items():
                    expander.symbol_table.define(name, value)

                # Expand loops, sweeps, and substitute variables
                expanded_events = expander.process_ast(doc.events)

                # Get expansion statistics
                stats = expander.get_stats()

                if verbose:
                    output_console.print(f"  [dim]Expanded: {stats.events_generated} events[/dim]")
                    if (
                        stats.defines_processed > 0
                        or stats.loops_expanded > 0
                        or stats.sweeps_expanded > 0
                    ):
                        output_console.print(f"  [dim]  - Defines: {stats.defines_processed}[/dim]")
                        output_console.print(f"  [dim]  - Loops: {stats.loops_expanded}[/dim]")
                        output_console.print(f"  [dim]  - Sweeps: {stats.sweeps_expanded}[/dim]")

            except ExpansionError as exp_error:
                # Use structured expansion error display
                show_expansion_error(
                    exp_error, output_console, no_color=no_color, no_emoji=no_emoji
                )
                if verbose:
                    import traceback

                    output_console.print(f"[dim]{traceback.format_exc()}[/dim]")
                raise typer.Exit(code=1)

            # 6. Compile to IR program
            if verbose:
                output_console.print("  [dim]Compiling to IR...[/dim]")

            from midi_markdown.core.ir import MIDIEvent, create_ir_program, string_to_event_type

            # Convert expanded dicts to MIDIEvent objects
            # Filter out end_of_track commands (automatically added by MIDI writer)
            events = []
            for event_dict in expanded_events:
                # Skip end_of_track - it's automatically added
                if event_dict["type"] == "end_of_track":
                    continue

                midi_event = MIDIEvent(
                    time=event_dict["time"],
                    type=string_to_event_type(event_dict["type"]),
                    channel=event_dict.get("channel", 0),
                    data1=event_dict.get("data1", 0),
                    data2=event_dict.get("data2", 0),
                    metadata=event_dict.get("metadata"),
                )
                events.append(midi_event)

            if verbose:
                output_console.print(f"  [dim]Generated: {len(events)} MIDI events[/dim]")

            # Create IR program (adds time_seconds and metadata)
            ir_program = create_ir_program(
                events=events,
                ppq=ppq_value,
                initial_tempo=int(tempo_value),
                frontmatter=doc.frontmatter,
            )

            if verbose:
                output_console.print(f"  [dim]Duration: {ir_program.duration_seconds:.2f}s[/dim]")
                output_console.print(f"  [dim]Tracks: {ir_program.track_count}[/dim]")

            # 7. Generate output based on format
            if output_format == "midi":
                # Write MIDI file
                if isinstance(progress, CompilationProgress):
                    progress.generation_complete()

                if verbose:
                    output_console.print("  [dim]Writing MIDI file...[/dim]")

                from midi_markdown.codegen import generate_midi_file

                # Generate MIDI file bytes
                midi_bytes = generate_midi_file(ir_program, midi_format=midi_format)

                # Write to disk
                output.write_bytes(midi_bytes)

            elif output_format == "table":
                # Display as Rich table
                if isinstance(progress, CompilationProgress):
                    progress.generation_complete()

                from midi_markdown.diagnostics import display_events_table

                output_console.print()  # Blank line
                display_events_table(
                    ir_program, max_events=100, show_stats=True, console=output_console
                )

            elif output_format == "csv":
                # Export to CSV
                if isinstance(progress, CompilationProgress):
                    progress.generation_complete()

                from midi_markdown.codegen import export_to_csv

                csv_output = export_to_csv(ir_program, include_header=True)

                if output is None:
                    # Write to stdout (plain print, no formatting)
                    print(csv_output)
                else:
                    # Write to file
                    output.write_text(csv_output)

            elif output_format == "json":
                # Export to JSON (complete format)
                if isinstance(progress, CompilationProgress):
                    progress.generation_complete()

                from midi_markdown.codegen import export_to_json

                json_output = export_to_json(ir_program, format="complete", pretty=True)

                if output is None:
                    # Write to stdout (plain print, no formatting)
                    print(json_output)
                else:
                    # Write to file
                    output.write_text(json_output)

            elif output_format == "json-simple":
                # Export to JSON (simplified format)
                if isinstance(progress, CompilationProgress):
                    progress.generation_complete()

                from midi_markdown.codegen import export_to_json

                json_output = export_to_json(ir_program, format="simplified", pretty=True)

                if output is None:
                    # Write to stdout (plain print, no formatting)
                    print(json_output)
                else:
                    # Write to file
                    output.write_text(json_output)

            else:
                output_console.print(f"[red]Error:[/] Unknown format: {output_format}")
                raise typer.Exit(1)

            # Calculate compilation time
            elapsed = time.time() - start_time

            # Extract track names
            track_names = []
            if doc.tracks:
                track_names = [t.get("name", f"Track {i + 1}") for i, t in enumerate(doc.tracks)]
            elif ir_program.event_count > 0:
                track_names = ["Main"]

            # Get duration from IR program
            duration_seconds = ir_program.duration_seconds
            duration_formatted = f"{int(duration_seconds // 60)}:{int(duration_seconds % 60):02d}"

            # Get file sizes (only if output file exists)
            input_size = input_file.stat().st_size
            output_size = output.stat().st_size if output else 0

            # Build stats dictionary for success display
            success_stats = {
                "events": ir_program.event_count,
                "tracks": ir_program.track_count,
                "track_names": track_names,
                "ppq": ppq_value,
                "format": midi_format,
                "elapsed": elapsed,
                "duration_seconds": int(duration_seconds),
                "duration_formatted": duration_formatted,
                "input_size_bytes": input_size,
                "output_size_bytes": output_size,
            }

            if stats.defines_processed > 0:
                success_stats["variables_defined"] = stats.defines_processed
            if stats.loops_expanded > 0:
                success_stats["loops_expanded"] = stats.loops_expanded
            if stats.sweeps_expanded > 0:
                success_stats["sweeps_expanded"] = stats.sweeps_expanded
            if stats.variables_substituted > 0:
                success_stats["variables_substituted"] = stats.variables_substituted

        # Use structured success display (only for MIDI format)
        if output_format == "midi":
            show_success(
                output, success_stats, output_console, no_color=no_color, no_emoji=no_emoji
            )

    except typer.Exit:
        # Re-raise typer.Exit to preserve exit codes
        raise
    except Exception as e:
        # Catch-all for unexpected errors
        emoji = "" if no_emoji else "✗ "
        if no_color:
            output_console.print(f"{emoji}Error: {e}")
        else:
            output_console.print(f"[red]{emoji}Error:[/red] {e}")
        if verbose:
            import traceback

            output_console.print(f"[dim]{traceback.format_exc()}[/dim]")
        raise typer.Exit(code=1)
