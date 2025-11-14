"""Progress indicator helpers for long-running CLI operations.

This module provides utilities for displaying progress feedback during
compilation, validation, and other time-consuming operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn

if TYPE_CHECKING:
    from pathlib import Path

    from rich.console import Console

    from midi_markdown.parser.ast_nodes import MMDDocument


def should_show_progress(
    input_file: Path,
    doc: MMDDocument | None = None,
    verbose: bool = False,
    no_progress: bool = False,
) -> bool:
    """Determine whether to show progress indicators for a file.

    Progress is shown when:
    - --verbose flag is set, OR
    - File size is > 50 KB, OR
    - Estimated event count is > 500

    Progress is suppressed when:
    - --no-progress flag is set

    Args:
        input_file: Path to the input file
        doc: Parsed MML document (optional, for event count estimation)
        verbose: Whether verbose mode is enabled
        no_progress: Whether progress display is explicitly disabled

    Returns:
        True if progress indicators should be shown
    """
    if no_progress:
        return False

    if verbose:
        return True

    # Check file size
    try:
        file_size = input_file.stat().st_size
        if file_size > 50 * 1024:  # 50 KB
            return True
    except OSError:
        pass

    # Check estimated event count
    if doc is not None:
        event_count = estimate_event_count(doc)
        if event_count > 500:
            return True

    return False


def estimate_event_count(doc: MMDDocument) -> int:
    """Estimate the number of MIDI events in a document.

    This is a rough estimate that counts:
    - Direct events in the document
    - Events in tracks (if multi-track mode)
    - Does NOT account for expansion (loops, sweeps, etc.)

    Args:
        doc: Parsed MML document

    Returns:
        Estimated number of events
    """
    count = 0

    # Count events in single-track mode
    if doc.events:
        count += len(doc.events)

    # Count events in multi-track mode
    if doc.tracks:
        for track in doc.tracks:
            if hasattr(track, "events") and track.events:
                count += len(track.events)

    return count


def create_compilation_progress(console: Console) -> Progress:
    """Create a progress bar configured for compilation operations.

    The progress bar shows 4 phases:
    1. Parsing (25%)
    2. Alias Resolution (25%)
    3. Validation (25%)
    4. MIDI Generation (25%)

    Args:
        console: Rich console instance for output

    Returns:
        Configured Progress instance
    """
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
        transient=True,  # Remove progress bar when complete
    )


def create_validation_progress(console: Console) -> Progress:
    """Create a progress bar configured for validation operations.

    The progress bar shows 3 phases:
    1. Parsing (33%)
    2. Alias Resolution (33%)
    3. Validation (34%)

    Args:
        console: Rich console instance for output

    Returns:
        Configured Progress instance
    """
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
        transient=True,  # Remove progress bar when complete
    )


class CompilationProgress:
    """Context manager for compilation progress tracking.

    Provides a simple interface for updating progress through the 4 compilation phases.
    """

    def __init__(self, progress: Progress):
        """Initialize compilation progress tracker.

        Args:
            progress: Rich Progress instance
        """
        self.progress = progress
        self.task_id = None

    def __enter__(self) -> CompilationProgress:
        """Start the progress bar."""
        self.progress.__enter__()
        self.task_id = self.progress.add_task("Parsing MML file...", total=100)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop the progress bar."""
        self.progress.__exit__(exc_type, exc_val, exc_tb)

    def parsing_complete(self) -> None:
        """Update progress: parsing phase complete (25%)."""
        if self.task_id is not None:
            self.progress.update(self.task_id, advance=25, description="Resolving aliases...")

    def aliases_complete(self) -> None:
        """Update progress: alias resolution complete (50%)."""
        if self.task_id is not None:
            self.progress.update(self.task_id, advance=25, description="Validating...")

    def validation_complete(self) -> None:
        """Update progress: validation complete (75%)."""
        if self.task_id is not None:
            self.progress.update(self.task_id, advance=25, description="Generating MIDI...")

    def generation_complete(self) -> None:
        """Update progress: MIDI generation complete (100%)."""
        if self.task_id is not None:
            self.progress.update(self.task_id, advance=25, description="Complete")


class ValidationProgress:
    """Context manager for validation progress tracking.

    Provides a simple interface for updating progress through the 3 validation phases.
    """

    def __init__(self, progress: Progress):
        """Initialize validation progress tracker.

        Args:
            progress: Rich Progress instance
        """
        self.progress = progress
        self.task_id = None

    def __enter__(self) -> ValidationProgress:
        """Start the progress bar."""
        self.progress.__enter__()
        self.task_id = self.progress.add_task("Parsing MML file...", total=100)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop the progress bar."""
        self.progress.__exit__(exc_type, exc_val, exc_tb)

    def parsing_complete(self) -> None:
        """Update progress: parsing phase complete (33%)."""
        if self.task_id is not None:
            self.progress.update(self.task_id, advance=33, description="Resolving aliases...")

    def aliases_complete(self) -> None:
        """Update progress: alias resolution complete (66%)."""
        if self.task_id is not None:
            self.progress.update(self.task_id, advance=33, description="Validating...")

    def validation_complete(self) -> None:
        """Update progress: validation complete (100%)."""
        if self.task_id is not None:
            self.progress.update(self.task_id, advance=34, description="Complete")
