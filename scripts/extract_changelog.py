#!/usr/bin/env python3
"""Extract changelog section for a specific version from CHANGELOG.md."""

import argparse
import re
import sys
from pathlib import Path


def extract_changelog_section(changelog_path: Path, version: str) -> str:
    """
    Extract the changelog section for a specific version.

    Args:
        changelog_path: Path to CHANGELOG.md file
        version: Version number (e.g., "0.1.0")

    Returns:
        Changelog section content for the specified version

    Raises:
        ValueError: If version section is not found
    """
    if not changelog_path.exists():
        msg = f"Changelog file not found: {changelog_path}"
        raise FileNotFoundError(msg)

    content = changelog_path.read_text(encoding="utf-8")

    # Pattern to match version headers: ## [0.1.0] or ## [0.1.0] - 2025-11-08
    version_pattern = rf"^## \[{re.escape(version)}\].*$"

    lines = content.split("\n")
    section_lines = []
    in_section = False
    found = False

    for line in lines:
        # Check if this is the start of our version section
        if re.match(version_pattern, line):
            in_section = True
            found = True
            continue  # Skip the version header itself

        # Check if we've hit the next version section
        if in_section and re.match(r"^## \[", line):
            break

        # Collect lines in our section
        if in_section:
            section_lines.append(line)

    if not found:
        available = find_available_versions(content)
        msg = f"Version [{version}] not found in {changelog_path}\nAvailable versions: {available}"
        raise ValueError(msg)

    # Strip leading/trailing whitespace
    result = "\n".join(section_lines).strip()

    if not result:
        msg = f"Version [{version}] section is empty in {changelog_path}"
        raise ValueError(msg)

    return result


def find_available_versions(content: str) -> list[str]:
    """Find all version numbers in the changelog."""
    versions = []
    for line in content.split("\n"):
        match = re.match(r"^## \[([^\]]+)\]", line)
        if match:
            version = match.group(1)
            if version.lower() != "unreleased":
                versions.append(version)
    return versions


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Extract changelog section for a specific version")
    parser.add_argument("--version", required=True, help="Version number (e.g., 0.1.0)")
    parser.add_argument(
        "--changelog",
        default="CHANGELOG.md",
        help="Path to CHANGELOG.md (default: CHANGELOG.md)",
    )
    parser.add_argument("--output", help="Output file (default: stdout)")

    args = parser.parse_args()

    try:
        changelog_path = Path(args.changelog)
        section = extract_changelog_section(changelog_path, args.version)

        if args.output:
            Path(args.output).write_text(section, encoding="utf-8")
            print(f"✅ Extracted changelog for v{args.version} to {args.output}")
        else:
            print(section)

    except (FileNotFoundError, ValueError) as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
