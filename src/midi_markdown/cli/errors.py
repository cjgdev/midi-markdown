"""
Rich error display formatting for the MIDI Markup Language compiler.

This module provides structured error display with:
- Source code context with line numbers
- Visual indicators (carets, colors) pointing to error locations
- Error codes (E1xx parse, E2xx validation, E3xx type, E4xx file/import)
- Helpful suggestions and "did you mean?" hints
- Accessibility support (--no-color, --no-emoji flags)
"""

from __future__ import annotations

from pathlib import Path

from lark.exceptions import UnexpectedCharacters, UnexpectedToken
from rich.console import Console
from rich.panel import Panel

from ..expansion.errors import (
    ExpansionError,
    InvalidLoopConfigError,
    InvalidSweepConfigError,
    UndefinedVariableError,
    ValueRangeError,
)
from ..utils.validation import ValidationError

# Error code mapping
ERROR_CODES = {
    # E1xx: Parse errors
    "unexpected_token": "E101",
    "unexpected_char": "E102",
    "syntax_error": "E103",
    # E2xx: Validation errors
    "invalid_value": "E201",
    "invalid_range": "E202",
    "invalid_note": "E203",
    "invalid_channel": "E204",
    "timing_error": "E205",
    # E3xx: Expansion/type errors
    "undefined_variable": "E301",
    "invalid_loop": "E302",
    "invalid_sweep": "E303",
    "value_range": "E304",
    # E4xx: File/import errors
    "file_not_found": "E401",
    "import_error": "E402",
}

# Valid MML tokens for "did you mean?" suggestions
VALID_NOTES = [
    "C",
    "D",
    "E",
    "F",
    "G",
    "A",
    "B",
    "Cb",
    "Db",
    "Eb",
    "Fb",
    "Gb",
    "Ab",
    "Bb",
    "C#",
    "D#",
    "E#",
    "F#",
    "G#",
    "A#",
    "B#",
]

VALID_DURATIONS = ["w", "h", "q", "e", "s", "t", "whole", "half", "quarter", "eighth", "sixteenth"]

VALID_DIRECTIVES = [
    "@define",
    "@import",
    "@alias",
    "@loop",
    "@sweep",
    "@if",
    "@elif",
    "@else",
    "@end",
    "@track",
    "@section",
    "@group",
]

VALID_COMMANDS = [
    "pc",
    "cc",
    "note_on",
    "note_off",
    "note",
    "tempo",
    "time_signature",
    "marker",
    "text",
    "pitch_bend",
    "pressure",
    "all_notes_off",
]


def format_code_context(
    source_lines: list[str],
    error_line: int,
    error_column: int,
    context_lines: int = 2,
    no_color: bool = False,
) -> str:
    """
    Format source code context with line numbers and error indicator.

    Args:
        source_lines: List of source code lines
        error_line: Line number where error occurred (1-indexed)
        error_column: Column number where error occurred (0-indexed)
        context_lines: Number of lines to show before/after error
        no_color: Disable color output for accessibility

    Returns:
        Formatted string with line numbers and caret indicator
    """
    # Calculate line range
    start_line = max(1, error_line - context_lines)
    end_line = min(len(source_lines), error_line + context_lines)

    # Format line numbers with padding
    max_line_num = end_line
    line_num_width = len(str(max_line_num))

    lines = []
    for i in range(start_line - 1, end_line):
        line_num = i + 1
        line_content = source_lines[i].rstrip()

        # Format line number
        if no_color:
            prefix = f"{line_num:>{line_num_width}} | "
        else:
            prefix = f"[dim]{line_num:>{line_num_width}}[/dim] [dim]|[/dim] "

        lines.append(prefix + line_content)

        # Add caret indicator on error line
        if line_num == error_line:
            caret_padding = " " * line_num_width + " | " + " " * error_column
            if no_color:
                caret_line = caret_padding + "^"
            else:
                caret_line = caret_padding + "[red bold]^[/red bold]"
            lines.append(caret_line)

    return "\n".join(lines)


def format_expected_tokens(expected: list[str]) -> str:
    """
    Convert Lark token names to friendly descriptions.

    Args:
        expected: List of expected token names from Lark

    Returns:
        Human-readable description of expected tokens
    """
    # Map Lark token names to friendly names
    token_map = {
        # Basic tokens
        "TIMING": "timing marker (e.g., [00:00.000])",
        "ABSOLUTE_TIME": "absolute time [MM:SS.mmm]",
        "MUSICAL_TIME": "musical time [bars.beats.ticks]",
        "RELATIVE_TIME": "relative time [+duration]",
        "INT": "integer number",
        "FLOAT": "number",
        "NUMBER": "number",
        "STRING": "quoted string",
        # MML-specific tokens
        "NOTE_NAME": "note name (C, D, E, F, G, A, B)",
        "OCTAVE": "octave number (0-10)",
        "DURATION": "duration (w=whole, h=half, q=quarter, e=eighth, s=sixteenth)",
        "CHANNEL": "MIDI channel (1-16)",
        "VELOCITY": "velocity (0-127)",
        "CC_NUMBER": "CC controller number (0-127)",
        "PROGRAM_NUMBER": "program number (0-127)",
        "TEMPO_VALUE": "tempo in BPM (20-300)",
        # Commands
        "COMMAND": "command (e.g., pc, cc, note)",
        "CMD_PC": "program change (pc)",
        "CMD_CC": "control change (cc)",
        "CMD_NOTE_ON": "note on command",
        "CMD_NOTE_OFF": "note off command",
        "CMD_NOTE": "note with duration",
        "CMD_TEMPO": "tempo command",
        "CMD_MARKER": "marker command",
        "CMD_TEXT": "text command",
        # Directives (AT_ tokens)
        "AT_DEFINE": "@define directive",
        "AT_IMPORT": "@import directive",
        "AT_ALIAS": "@alias directive",
        "AT_LOOP": "@loop directive",
        "AT_SWEEP": "@sweep directive",
        "AT_IF": "@if directive",
        "AT_ELIF": "@elif directive",
        "AT_ELSE": "@else directive",
        "AT_END": "@end directive",
        "AT_TRACK": "@track directive",
        "AT_SECTION": "@section directive",
        "AT_GROUP": "@group directive",
        # Punctuation with context
        "DASH": "command prefix '-'",
        "DOT": "dot '.' (for channel.value notation)",
        "COLON": "colon ':' (for timing)",
        "PLUS": "plus '+' (for relative timing)",
        "EQUALS": "equals '=' (for assignment)",
        "DOLLAR": "'$' (for variable reference)",
        # Brackets and delimiters
        "LBRACKET": "opening bracket '[' (for timing or grouping)",
        "RBRACKET": "closing bracket ']'",
        "LBRACE": "opening brace '{' (for parameters)",
        "RBRACE": "closing brace '}'",
        "LPAREN": "opening parenthesis '('",
        "RPAREN": "closing parenthesis ')'",
        # Special
        "PIPE": "pipe '|' (measure separator)",
        "COMMA": "comma ','",
        "SEMICOLON": "semicolon ';'",
        "_NL": "newline (start new line)",
        "COMMENT": "comment",
        "IDENTIFIER": "identifier name",
        "VARIABLE": "variable reference",
    }

    friendly_names = []
    for token in expected[:5]:  # Limit to 5 suggestions
        friendly_names.append(token_map.get(token, token.lower()))

    if len(friendly_names) == 1:
        return friendly_names[0]
    if len(friendly_names) == 2:
        return f"{friendly_names[0]} or {friendly_names[1]}"
    return ", ".join(friendly_names[:-1]) + f", or {friendly_names[-1]}"


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calculate Levenshtein distance between two strings.

    Args:
        s1: First string
        s2: Second string

    Returns:
        Edit distance between the strings
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            # Cost of insertions, deletions, or substitutions
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def generate_suggestion(
    error_value: str, valid_values: list[str], threshold: int = 3
) -> str | None:
    """
    Generate "did you mean?" suggestion using Levenshtein distance.

    Args:
        error_value: The incorrect value
        valid_values: List of valid values
        threshold: Maximum edit distance to suggest

    Returns:
        Suggestion string or None if no close match
    """
    closest = None
    min_distance = threshold + 1

    for valid in valid_values:
        distance = levenshtein_distance(error_value.lower(), valid.lower())
        if distance < min_distance:
            min_distance = distance
            closest = valid

    if closest and min_distance <= threshold:
        return f"Did you mean '{closest}'?"
    return None


def show_parse_error(
    error: UnexpectedToken | UnexpectedCharacters,
    source_file: Path,
    console: Console,
    no_color: bool = False,
    no_emoji: bool = False,
) -> None:
    """
    Display a parse error with rich formatting.

    Args:
        error: Lark parse exception
        source_file: Path to source file
        console: Rich console for output
        no_color: Disable color output
        no_emoji: Disable emoji output
    """
    # Read source file
    source_lines = source_file.read_text().splitlines()

    # Determine error code and message
    if isinstance(error, UnexpectedToken):
        error_code = ERROR_CODES["unexpected_token"]
        message = f"Unexpected token: {error.token.type}"
        line = error.line
        column = error.column - 1  # Convert to 0-indexed

        # Generate expected tokens message
        if hasattr(error, "expected"):
            expected_msg = format_expected_tokens(list(error.expected))
            suggestion = f"Expected {expected_msg}"
        else:
            suggestion = None

        # Try to generate "did you mean?" suggestion for typos
        if hasattr(error, "token") and error.token.value:
            token_value = str(error.token.value)
            # Try to find similar tokens in our valid lists
            all_valid = VALID_NOTES + VALID_DURATIONS + VALID_DIRECTIVES + VALID_COMMANDS
            typo_suggestion = generate_suggestion(token_value, all_valid, threshold=2)
            if typo_suggestion:
                # Append typo suggestion to expected tokens message
                if suggestion:
                    suggestion = f"{suggestion}\n  {typo_suggestion}"
                else:
                    suggestion = typo_suggestion

    else:  # UnexpectedCharacters
        error_code = ERROR_CODES["unexpected_char"]
        char = error.char if hasattr(error, "char") else "unknown"
        message = f"Unexpected character: '{char}'"
        line = error.line
        column = error.column - 1
        suggestion = None

    # Format header
    emoji = "" if no_emoji else "❌ "
    if no_color:
        header = f"{emoji}error[{error_code}]: {message}"
    else:
        header = f"{emoji}[red bold]error[{error_code}][/red bold]: {message}"

    # Format file location
    location = f"  → {source_file}:{line}:{column + 1}"

    # Format code context
    context = format_code_context(source_lines, line, column, no_color=no_color)

    # Build full error message
    error_parts = [header, location, "", context]

    if suggestion:
        emoji = "" if no_emoji else "💡 "
        if no_color:
            error_parts.append(f"\n  {emoji}{suggestion}")
        else:
            error_parts.append(f"\n  {emoji}[cyan]{suggestion}[/cyan]")

    console.print("\n".join(error_parts))


def show_validation_error(
    error: ValidationError,
    source_file: Path | None,
    console: Console,
    no_color: bool = False,
    no_emoji: bool = False,
) -> None:
    """
    Display a validation error with rich formatting.

    Args:
        error: ValidationError exception
        source_file: Path to source file (if available)
        console: Rich console for output
        no_color: Disable color output
        no_emoji: Disable emoji output
    """
    # Use error code from ValidationError if available
    error_code = getattr(error, "error_code", ERROR_CODES.get("invalid_value", "E201"))

    # Format header
    emoji = "" if no_emoji else "❌ "
    if no_color:
        header = f"{emoji}error[{error_code}]: {error}"
    else:
        header = f"{emoji}[red bold]error[{error_code}][/red bold]: {error}"

    # Add file location if available
    parts = [header]
    if source_file and hasattr(error, "line") and error.line:
        column = getattr(error, "column", 1)
        parts.append(f"  → {source_file}:{error.line}:{column}")

        # Add code context if we have source
        try:
            source_lines = source_file.read_text().splitlines()
            context = format_code_context(source_lines, error.line, column - 1, no_color=no_color)
            parts.extend(["", context])
        except Exception:
            pass  # Source file not readable

    # Add suggestion if available
    if hasattr(error, "suggestion") and error.suggestion:
        emoji = "" if no_emoji else "💡 "
        if no_color:
            parts.append(f"\n  {emoji}{error.suggestion}")
        else:
            parts.append(f"\n  {emoji}[cyan]{error.suggestion}[/cyan]")

    console.print("\n".join(parts))


def show_expansion_error(
    error: ExpansionError,
    console: Console,
    no_color: bool = False,
    no_emoji: bool = False,
) -> None:
    """
    Display an expansion error with rich formatting.

    Args:
        error: ExpansionError exception
        console: Rich console for output
        no_color: Disable color output
        no_emoji: Disable emoji output
    """
    # Determine error code based on error type
    if isinstance(error, UndefinedVariableError):
        error_code = ERROR_CODES["undefined_variable"]
    elif isinstance(error, InvalidLoopConfigError):
        error_code = ERROR_CODES["invalid_loop"]
    elif isinstance(error, InvalidSweepConfigError):
        error_code = ERROR_CODES["invalid_sweep"]
    elif isinstance(error, ValueRangeError):
        error_code = ERROR_CODES["value_range"]
    else:
        error_code = "E3xx"

    # Format header
    emoji = "" if no_emoji else "❌ "
    if no_color:
        header = f"{emoji}error[{error_code}]: {error}"
    else:
        header = f"{emoji}[red bold]error[{error_code}][/red bold]: {error}"

    # Add file location
    parts = [header]
    if error.file and error.line:
        parts.append(f"  → {error.file}:{error.line}:1")

        # Add code context if source is readable
        try:
            source_path = Path(error.file)
            if source_path.exists():
                source_lines = source_path.read_text().splitlines()
                context = format_code_context(source_lines, error.line, 0, no_color=no_color)
                parts.extend(["", context])
        except Exception:
            pass

    # Add suggestion
    if error.suggestion:
        emoji = "" if no_emoji else "💡 "
        if no_color:
            parts.append(f"\n  {emoji}{error.suggestion}")
        else:
            parts.append(f"\n  {emoji}[cyan]{error.suggestion}[/cyan]")

    console.print("\n".join(parts))


def show_success(
    output_file: Path,
    stats: dict,
    console: Console,
    no_color: bool = False,
    no_emoji: bool = False,
) -> None:
    """
    Display compilation success message with statistics.

    Args:
        output_file: Path to generated MIDI file
        stats: Compilation statistics dictionary
        console: Rich console for output
        no_color: Disable color output
        no_emoji: Disable emoji output
    """
    emoji = "" if no_emoji else "✅ "

    # Build statistics text
    stats_lines = []

    # Basic composition stats
    if "events" in stats:
        stats_lines.append(f"Events: {stats['events']}")

    # Track information with names
    if stats.get("track_names"):
        names = ", ".join(stats["track_names"][:5])  # Limit to 5
        if len(stats["track_names"]) > 5:
            names += f", +{len(stats['track_names']) - 5} more"
        stats_lines.append(f"Tracks: {stats['tracks']} ({names})")
    elif "tracks" in stats:
        stats_lines.append(f"Tracks: {stats['tracks']}")

    # Duration
    if "duration_formatted" in stats:
        secs = stats.get("duration_seconds", 0)
        stats_lines.append(f"Duration: {stats['duration_formatted']} ({secs}s)")

    # File sizes
    if "input_size_bytes" in stats and "output_size_bytes" in stats:
        input_kb = stats["input_size_bytes"] / 1024
        output_kb = stats["output_size_bytes"] / 1024
        stats_lines.append(f"Input: {input_kb:.1f} KB → Output: {output_kb:.1f} KB")

    # Expansion statistics (if any)
    expansion_stats = []
    if "variables_defined" in stats and stats["variables_defined"] > 0:
        expansion_stats.append(f"Variables defined: {stats['variables_defined']}")
    if "variables_substituted" in stats and stats["variables_substituted"] > 0:
        expansion_stats.append(f"Variables substituted: {stats['variables_substituted']}")
    if "loops_expanded" in stats and stats["loops_expanded"] > 0:
        expansion_stats.append(f"Loops expanded: {stats['loops_expanded']}")
    if "sweeps_expanded" in stats and stats["sweeps_expanded"] > 0:
        expansion_stats.append(f"Sweeps expanded: {stats['sweeps_expanded']}")

    if expansion_stats:
        stats_lines.append("")  # Blank line before expansion stats
        stats_lines.extend(expansion_stats)

    stats_text = "\n".join(stats_lines)

    # Format title with elapsed time
    if "elapsed" in stats:
        elapsed_str = f" ({stats['elapsed']:.2f}s)"
    else:
        elapsed_str = ""

    # Format success message
    if no_color:
        title = f"{emoji}Compilation successful{elapsed_str}"
        message = f"Output: {output_file}\n\n{stats_text}"
        console.print(f"\n{title}\n{message}\n")
    else:
        panel = Panel(
            stats_text,
            title=f"{emoji}[green bold]Compilation successful{elapsed_str}[/green bold]",
            subtitle=f"[dim]{output_file!s}[/dim]",
            border_style="green",
        )
        console.print(panel)
