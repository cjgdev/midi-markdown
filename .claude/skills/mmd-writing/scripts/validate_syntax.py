#!/usr/bin/env python3
"""
Quick MMD syntax validation script.

This script performs basic syntax validation on MMD files without full compilation.
Useful for rapid feedback during development.

Usage:
    python validate_syntax.py <file.mmd>
    python validate_syntax.py --stdin  # Read from stdin
"""

import re
import sys
from pathlib import Path


class SyntaxError:
    def __init__(self, line_num: int, message: str, line_content: str = ""):
        self.line_num = line_num
        self.message = message
        self.line_content = line_content

    def __str__(self):
        result = f"Line {self.line_num}: {self.message}"
        if self.line_content:
            result += f"\n  {self.line_content}"
        return result


def validate_frontmatter(lines: list[str]) -> tuple[bool, list[SyntaxError], int]:
    """Validate YAML frontmatter. Returns (valid, errors, end_line)."""
    errors = []

    if not lines or lines[0].strip() != "---":
        errors.append(SyntaxError(1, "Missing frontmatter start (---)", lines[0] if lines else ""))
        return False, errors, 0

    # Find end of frontmatter
    end_line = 0
    for i in range(1, min(len(lines), 50)):  # Check first 50 lines
        if lines[i].strip() == "---":
            end_line = i
            break

    if end_line == 0:
        errors.append(SyntaxError(1, "Missing frontmatter end (---)", ""))
        return False, errors, 0

    # Check for required fields
    frontmatter = "\n".join(lines[1:end_line])

    if "ppq:" not in frontmatter and "tempo:" not in frontmatter:
        errors.append(SyntaxError(1, "Missing required fields (ppq or tempo)", ""))

    return len(errors) == 0, errors, end_line


def validate_timing_marker(line: str, line_num: int) -> SyntaxError | None:
    """Validate timing marker syntax."""
    line = line.strip()

    # Absolute timing: [mm:ss.ms]
    absolute_pattern = r"^\[\d+:\d{2}\.\d{3}\]$"
    # Musical timing: [bar.beat.tick]
    musical_pattern = r"^\[\d+\.\d+\.\d+\]$"
    # Relative timing: [+value unit] or [+bar.beat.tick]
    relative_pattern = r"^\[\+(\d+(\.\d+)?[smbt]|\d+\.\d+\.\d+)\]$"
    # Simultaneous: [@]
    simultaneous_pattern = r"^\[@\]$"

    if not (
        re.match(absolute_pattern, line)
        or re.match(musical_pattern, line)
        or re.match(relative_pattern, line)
        or re.match(simultaneous_pattern, line)
    ):
        return SyntaxError(line_num, "Invalid timing marker format", line)

    return None


def validate_command(line: str, line_num: int) -> SyntaxError | None:
    """Validate MIDI command syntax."""
    line = line.strip()

    if not line.startswith("- "):
        return SyntaxError(line_num, "Commands must start with '- '", line)

    command = line[2:].strip()

    # Split command and arguments
    parts = command.split(None, 1)
    if not parts:
        return SyntaxError(line_num, "Empty command", line)

    cmd_type = parts[0].lower()

    # Valid command types
    valid_commands = [
        "note_on",
        "note_off",
        "pc",
        "program_change",
        "cc",
        "control_change",
        "pb",
        "pitch_bend",
        "cp",
        "channel_pressure",
        "pp",
        "poly_pressure",
        "tempo",
        "time_signature",
        "key_signature",
        "marker",
        "text",
        "track_name",
        "instrument_name",
        "lyric",
        "cue_point",
        "device_name",
        "all_notes_off",
        "all_sound_off",
        "reset_controllers",
    ]

    if cmd_type not in valid_commands and not cmd_type.replace("_", "").isalpha():
        # Might be an alias, check if it looks reasonable
        if not re.match(r"^[a-z_][a-z0-9_]*$", cmd_type):
            return SyntaxError(line_num, f"Invalid command type: {cmd_type}", line)

    return None


def validate_variable(line: str, line_num: int) -> SyntaxError | None:
    """Validate @define syntax."""
    line = line.strip()

    if not line.startswith("@define "):
        return SyntaxError(line_num, "@define requires space after keyword", line)

    parts = line[8:].split(None, 1)
    if len(parts) < 2:
        return SyntaxError(line_num, "@define requires NAME and value", line)

    var_name = parts[0]
    if not re.match(r"^[A-Z_][A-Z0-9_]*$", var_name):
        return SyntaxError(
            line_num, f"Variable name '{var_name}' should be UPPERCASE with underscores", line
        )

    return None


def validate_loop(line: str, line_num: int) -> SyntaxError | None:
    """Validate @loop syntax."""
    line = line.strip()

    if not re.match(r"^@loop\s+\d+\s+times", line):
        return SyntaxError(line_num, "@loop syntax: @loop N times [at [time]] every interval", line)

    if "every" not in line:
        return SyntaxError(line_num, "@loop requires 'every' clause", line)

    return None


def validate_file(content: str) -> tuple[bool, list[SyntaxError]]:
    """Validate entire MMD file."""
    lines = content.split("\n")
    errors = []

    # Validate frontmatter
    _valid_fm, fm_errors, fm_end = validate_frontmatter(lines)
    errors.extend(fm_errors)

    # Track state
    has_timing_marker = False
    in_loop = False
    in_alias = False
    in_multiline_comment = False

    for i, line in enumerate(lines[fm_end + 1 :], start=fm_end + 2):
        stripped = line.strip()

        # Skip empty lines
        if not stripped:
            continue

        # Handle multiline comments
        if "/*" in stripped:
            in_multiline_comment = True
        if "*/" in stripped:
            in_multiline_comment = False
            continue
        if in_multiline_comment:
            continue

        # Skip single-line comments
        if stripped.startswith(("#", "//")):
            continue

        # Track blocks
        if stripped.startswith("@loop"):
            err = validate_loop(stripped, i)
            if err:
                errors.append(err)
            in_loop = True
            continue

        if stripped.startswith("@alias"):
            in_alias = True
            continue

        if stripped == "@end":
            in_loop = False
            in_alias = False
            continue

        # Skip alias content
        if in_alias:
            continue

        # Validate @define
        if stripped.startswith("@define"):
            err = validate_variable(stripped, i)
            if err:
                errors.append(err)
            continue

        # Validate @import
        if stripped.startswith("@import"):
            if not re.match(r'^@import\s+"[^"]+"', stripped):
                errors.append(
                    SyntaxError(i, '@import requires quoted path: @import "path"', stripped)
                )
            continue

        # Validate timing markers
        if stripped.startswith("["):
            err = validate_timing_marker(stripped, i)
            if err:
                errors.append(err)
            else:
                has_timing_marker = True
            continue

        # Validate commands
        if stripped.startswith("- "):
            if not has_timing_marker and not in_loop:
                errors.append(SyntaxError(i, "Command before first timing marker", stripped))

            err = validate_command(stripped, i)
            if err:
                errors.append(err)
            continue

    return len(errors) == 0, errors


def main():
    if len(sys.argv) < 2:
        sys.exit(1)

    # Read input
    if sys.argv[1] == "--stdin":
        content = sys.stdin.read()
    else:
        file_path = Path(sys.argv[1])
        if not file_path.exists():
            sys.exit(1)
        content = file_path.read_text()

    # Validate
    valid, errors = validate_file(content)

    if valid:
        sys.exit(0)
    else:
        for _error in errors:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()
