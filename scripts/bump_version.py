#!/usr/bin/env python3
"""Version bumping script for MIDI Markdown.

This script automates version updates across the project:
- Updates version in pyproject.toml
- Updates version in src/midi_markdown/__init__.py
- Updates CHANGELOG.md with new version section
- Creates a git tag

Usage:
    python scripts/bump_version.py major    # 0.1.0 -> 1.0.0
    python scripts/bump_version.py minor    # 0.1.0 -> 0.2.0
    python scripts/bump_version.py patch    # 0.1.0 -> 0.1.1
    python scripts/bump_version.py 1.2.3    # Set specific version
"""

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


class VersionBumper:
    """Handle version updates across the project."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.pyproject_path = project_root / "pyproject.toml"
        self.init_path = project_root / "src" / "midi_markdown" / "__init__.py"
        self.changelog_path = project_root / "CHANGELOG.md"

    def get_current_version(self) -> str:
        """Extract current version from pyproject.toml."""
        content = self.pyproject_path.read_text()
        match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
        if not match:
            msg = "Could not find version in pyproject.toml"
            raise ValueError(msg)
        return match.group(1)

    def parse_version(self, version: str) -> tuple[int, int, int]:
        """Parse semantic version string into tuple."""
        match = re.match(r"^(\d+)\.(\d+)\.(\d+)(?:-.*)?$", version)
        if not match:
            msg = f"Invalid semantic version: {version}"
            raise ValueError(msg)
        return int(match.group(1)), int(match.group(2)), int(match.group(3))

    def bump_version(self, current: str, bump_type: str) -> str:
        """Calculate new version based on bump type."""
        if bump_type not in ["major", "minor", "patch"]:
            # Assume it's a specific version
            self.parse_version(bump_type)  # Validate format
            return bump_type

        major, minor, patch = self.parse_version(current)

        if bump_type == "major":
            return f"{major + 1}.0.0"
        if bump_type == "minor":
            return f"{major}.{minor + 1}.0"
        # patch
        return f"{major}.{minor}.{patch + 1}"

    def update_pyproject(self, new_version: str) -> None:
        """Update version in pyproject.toml."""
        content = self.pyproject_path.read_text()
        updated = re.sub(
            r'^version\s*=\s*"[^"]+"',
            f'version = "{new_version}"',
            content,
            count=1,
            flags=re.MULTILINE,
        )
        self.pyproject_path.write_text(updated)

    def update_init(self, new_version: str) -> None:
        """Update version in __init__.py."""
        content = self.init_path.read_text()
        updated = re.sub(
            r'^__version__\s*=\s*"[^"]+"',
            f'__version__ = "{new_version}"',
            content,
            count=1,
            flags=re.MULTILINE,
        )
        self.init_path.write_text(updated)

    def update_changelog(self, new_version: str) -> None:
        """Update CHANGELOG.md with new version section."""
        content = self.changelog_path.read_text()
        today = datetime.now().strftime("%Y-%m-%d")

        # Check if version already exists
        if f"## [{new_version}]" in content:
            return

        # Replace [Unreleased] with new version section
        unreleased_pattern = r"## \[Unreleased\]\n\n(.*?)(?=\n## \[)"
        match = re.search(unreleased_pattern, content, re.DOTALL)

        if match:
            unreleased_content = match.group(1).strip()
            if not unreleased_content or unreleased_content == "":
                unreleased_content = "### Changed\n- Version bump"

            new_section = f"""## [Unreleased]

## [{new_version}] - {today}

{unreleased_content}"""

            updated = re.sub(
                r"## \[Unreleased\]\n\n.*?(?=\n## \[)",
                new_section + "\n",
                content,
                count=1,
                flags=re.DOTALL,
            )

            # Update comparison links at bottom
            updated = self._update_changelog_links(updated, new_version)

            self.changelog_path.write_text(updated)
        else:
            pass

    def _update_changelog_links(self, content: str, new_version: str) -> str:
        """Update version comparison links in CHANGELOG.md."""
        # Find the repository URL from existing links
        repo_match = re.search(
            r"\[Unreleased\]: (https://github\.com/[^/]+/[^/]+)/compare", content
        )
        if not repo_match:
            return content

        repo_url = repo_match.group(1)

        # Update [Unreleased] link
        updated = re.sub(
            r"\[Unreleased\]: .*",
            f"[Unreleased]: {repo_url}/compare/v{new_version}...HEAD",
            content,
        )

        # Add new version link if it doesn't exist
        version_link = f"[{new_version}]: {repo_url}/releases/tag/v{new_version}"
        if version_link not in updated:
            # Insert before the last existing version link
            updated = re.sub(
                r"(\[\d+\.\d+\.\d+\]: .*\n)$", f"{version_link}\n\\1", updated, flags=re.MULTILINE
            )

        return updated

    def git_commit_and_tag(self, version: str, dry_run: bool = False) -> None:
        """Create git commit and tag for the version."""
        files = [
            str(self.pyproject_path.relative_to(self.project_root)),
            str(self.init_path.relative_to(self.project_root)),
            str(self.changelog_path.relative_to(self.project_root)),
        ]

        commands = [
            ["git", "add", *files],
            ["git", "commit", "-m", f"Release version {version}"],
            ["git", "tag", "-a", f"v{version}", "-m", f"Release {version}"],
        ]

        if dry_run:
            for cmd in commands:
                pass
            return

        for cmd in commands:
            try:
                subprocess.run(
                    cmd, cwd=self.project_root, capture_output=True, text=True, check=True
                )
            except subprocess.CalledProcessError:
                sys.exit(1)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Bump version for MIDI Markdown project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/bump_version.py patch       # 0.1.0 -> 0.1.1
  python scripts/bump_version.py minor       # 0.1.0 -> 0.2.0
  python scripts/bump_version.py major       # 0.1.0 -> 1.0.0
  python scripts/bump_version.py 1.2.3       # Set to 1.2.3
  python scripts/bump_version.py patch --dry-run  # Preview changes
        """,
    )
    parser.add_argument(
        "bump_type",
        choices=["major", "minor", "patch"],
        nargs="?",
        default=None,
        help="Type of version bump (or specific version like 1.2.3)",
    )
    parser.add_argument("version", nargs="?", help="Specific version to set (e.g., 1.2.3)")
    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Preview changes without modifying files",
    )
    parser.add_argument(
        "--no-git",
        action="store_true",
        help="Don't create git commit and tag",
    )

    args = parser.parse_args()

    # Determine version argument
    if args.version:
        version_arg = args.version
    elif args.bump_type:
        version_arg = args.bump_type
    else:
        parser.print_help()
        sys.exit(1)

    # Initialize bumper
    project_root = Path(__file__).parent.parent
    bumper = VersionBumper(project_root)

    try:
        # Get current version
        current = bumper.get_current_version()

        # Calculate new version
        new_version = bumper.bump_version(current, version_arg)

        if args.dry_run:
            return

        # Confirm
        response = input(f"\nBump version {current} -> {new_version}? [y/N] ")
        if response.lower() not in ["y", "yes"]:
            sys.exit(0)

        # Update files
        bumper.update_pyproject(new_version)
        bumper.update_init(new_version)
        bumper.update_changelog(new_version)

        # Git operations
        if not args.no_git:
            bumper.git_commit_and_tag(new_version, dry_run=args.dry_run)
        else:
            pass

    except Exception:
        sys.exit(1)


if __name__ == "__main__":
    main()
