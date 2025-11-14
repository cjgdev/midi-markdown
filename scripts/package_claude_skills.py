#!/usr/bin/env python3
"""
Package Claude skills for distribution.

This script creates distributable packages of the Claude Code skills
for MIDI Markdown, including both individual skill files and a combined
archive for easy installation.
"""

import argparse
import json
import shutil
import sys
import tarfile
import zipfile
from pathlib import Path


def create_skill_archive(source_dir: Path, output_dir: Path, version: str) -> dict[str, Path]:
    """
    Create distributable archives of Claude skills.

    Args:
        source_dir: Source directory containing .claude/skills/
        output_dir: Output directory for archives
        version: Version string for naming

    Returns:
        Dictionary mapping archive type to file path
    """
    skills_dir = source_dir / ".claude" / "skills"

    if not skills_dir.exists():
        msg = f"Skills directory not found: {skills_dir}"
        raise FileNotFoundError(msg)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Get skill files
    skill_files = list(skills_dir.glob("*.md"))

    if not skill_files:
        msg = f"No skill files found in {skills_dir}"
        raise FileNotFoundError(msg)

    for skill_file in skill_files:
        pass

    archives = {}

    # Create README for skills package
    readme_content = f"""# MIDI Markdown Claude Skills

Version: {version}

This package contains Claude Code skills for working with MIDI Markdown (MMD) files.

## Included Skills

"""

    for skill_file in skill_files:
        skill_name = skill_file.stem
        readme_content += f"- **{skill_name}**: "

        # Extract purpose from skill file
        with open(skill_file) as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if line.strip().startswith("## Purpose") and i + 1 < len(lines):
                    purpose = lines[i + 1].strip()
                    readme_content += purpose + "\n"
                    break
            else:
                readme_content += "MMD skill\n"

    readme_content += f"""
## Installation

### Option 1: Automatic Installation (Recommended)

```bash
# Extract the archive
tar -xzf claude-skills-mmd-{version}.tar.gz  # Linux/macOS
# or
unzip claude-skills-mmd-{version}.zip  # Windows

# Run the installation script
cd claude-skills-mmd-{version}
./install.sh  # Linux/macOS
# or
install.bat  # Windows
```

### Option 2: Manual Installation

1. Extract this archive
2. Copy the skill files to your Claude Code skills directory:
   - **Linux/macOS**: `~/.config/claude/skills/`
   - **Windows**: `%APPDATA%\\Claude\\skills\\`

```bash
# Linux/macOS
mkdir -p ~/.config/claude/skills
cp *.md ~/.config/claude/skills/

# Windows (PowerShell)
New-Item -ItemType Directory -Force -Path "$env:APPDATA\\Claude\\skills"
Copy-Item *.md "$env:APPDATA\\Claude\\skills\\"
```

### Option 3: Project-Local Installation

Copy skills to your MMD project's `.claude/skills/` directory:

```bash
# From your MMD project directory
mkdir -p .claude/skills
cp /path/to/extracted/*.md .claude/skills/
```

## Usage

Once installed, Claude Code will automatically detect and use these skills when:

1. **MMD Writing Skill**: When creating or editing `.mmd` files
2. **MMDC CLI Usage Skill**: When working with `mmdc` CLI commands

You can also explicitly invoke skills by name in your prompts:
- "Use the mmd-writing skill to help me create a new song"
- "Use the mmdc-cli-usage skill to help me compile this file"

## Available Skills

### mmd-writing
Helps write MIDI Markdown files with correct syntax, timing, MIDI commands,
and advanced features like loops, sweeps, random expressions, and modulation.

**Use when:**
- Creating or editing MMD files
- Learning MMD syntax
- Implementing MIDI automation
- Troubleshooting MMD syntax errors

### mmdc-cli-usage
Helps use the MIDI Markdown Compiler CLI effectively for compiling, validating,
playing, and inspecting MMD files.

**Use when:**
- Compiling MMD to MIDI
- Validating MMD syntax
- Playing MMD files with real-time output
- Inspecting or exporting MMD in different formats
- Troubleshooting compilation errors

## Documentation

- **User Guide**: https://github.com/cjgdev/midi-markdown#readme
- **Examples**: https://github.com/cjgdev/midi-markdown/tree/main/examples
- **Language Spec**: https://github.com/cjgdev/midi-markdown/blob/main/spec.md
- **Docs Site**: https://cjgdev.github.io/midi-markdown/

## Support

- **GitHub Issues**: https://github.com/cjgdev/midi-markdown/issues
- **Discussions**: https://github.com/cjgdev/midi-markdown/discussions

## License

MIT License - Same as MIDI Markdown project
"""

    # Create installation scripts
    install_sh_content = """#!/bin/bash
# Install Claude skills for MIDI Markdown

set -e

echo "Installing MIDI Markdown Claude Skills..."

# Determine install location
if [ -n "$CLAUDE_SKILLS_DIR" ]; then
    SKILLS_DIR="$CLAUDE_SKILLS_DIR"
elif [ "$(uname)" = "Darwin" ] || [ "$(uname)" = "Linux" ]; then
    SKILLS_DIR="$HOME/.config/claude/skills"
else
    echo "Error: Unable to determine installation directory"
    echo "Please set CLAUDE_SKILLS_DIR environment variable"
    exit 1
fi

# Create directory if it doesn't exist
mkdir -p "$SKILLS_DIR"

# Copy skill files
echo "Installing skills to: $SKILLS_DIR"
for skill in *.md; do
    if [ -f "$skill" ]; then
        cp "$skill" "$SKILLS_DIR/"
        echo "  ✓ Installed $skill"
    fi
done

echo ""
echo "✅ Installation complete!"
echo ""
echo "Skills installed to: $SKILLS_DIR"
echo ""
echo "The skills will be automatically available in Claude Code."
echo "You can verify installation by checking: $SKILLS_DIR"
"""

    install_bat_content = """@echo off
REM Install Claude skills for MIDI Markdown

echo Installing MIDI Markdown Claude Skills...

REM Determine install location
if defined CLAUDE_SKILLS_DIR (
    set SKILLS_DIR=%CLAUDE_SKILLS_DIR%
) else (
    set SKILLS_DIR=%APPDATA%\\Claude\\skills
)

REM Create directory if it doesn't exist
if not exist "%SKILLS_DIR%" mkdir "%SKILLS_DIR%"

REM Copy skill files
echo Installing skills to: %SKILLS_DIR%
for %%f in (*.md) do (
    copy "%%f" "%SKILLS_DIR%\\" >nul
    echo   ✓ Installed %%f
)

echo.
echo ✅ Installation complete!
echo.
echo Skills installed to: %SKILLS_DIR%
echo.
echo The skills will be automatically available in Claude Code.
echo You can verify installation by checking: %SKILLS_DIR%
pause
"""

    # Create temporary directory for packaging
    temp_dir = output_dir / f"claude-skills-mmd-{version}"
    temp_dir.mkdir(exist_ok=True)

    # Copy skill files
    for skill_file in skill_files:
        shutil.copy2(skill_file, temp_dir / skill_file.name)

    # Write README
    (temp_dir / "README.md").write_text(readme_content)

    # Write installation scripts
    install_sh = temp_dir / "install.sh"
    install_sh.write_text(install_sh_content)
    install_sh.chmod(0o755)  # Make executable

    (temp_dir / "install.bat").write_text(install_bat_content)

    # Create tar.gz archive (for Linux/macOS)
    tar_path = output_dir / f"claude-skills-mmd-{version}.tar.gz"
    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(temp_dir, arcname=temp_dir.name)
    archives["tar.gz"] = tar_path

    # Create zip archive (for Windows)
    zip_path = output_dir / f"claude-skills-mmd-{version}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file_path in temp_dir.rglob("*"):
            if file_path.is_file():
                arcname = file_path.relative_to(output_dir)
                zipf.write(file_path, arcname)
    archives["zip"] = zip_path

    # Clean up temp directory
    shutil.rmtree(temp_dir)

    # Create manifest file
    manifest = {
        "version": version,
        "skills": [
            {
                "name": skill_file.stem,
                "filename": skill_file.name,
                "size": skill_file.stat().st_size,
            }
            for skill_file in skill_files
        ],
        "archives": {
            format_name: {"filename": archive_path.name, "size": archive_path.stat().st_size}
            for format_name, archive_path in archives.items()
        },
    }

    manifest_path = output_dir / f"claude-skills-mmd-{version}.manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    archives["manifest"] = manifest_path

    return archives


def main():
    parser = argparse.ArgumentParser(description="Package Claude Code skills for MIDI Markdown")
    parser.add_argument(
        "--source",
        type=Path,
        default=Path.cwd(),
        help="Source directory containing .claude/skills/ (default: current directory)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path.cwd() / "dist" / "claude-skills",
        help="Output directory for archives (default: dist/claude-skills)",
    )
    parser.add_argument(
        "--version", required=True, help="Version string for the skills package (e.g., 0.1.0)"
    )

    args = parser.parse_args()

    try:
        archives = create_skill_archive(args.source, args.output, args.version)

        for _format_name, _archive_path in archives.items():
            pass

    except Exception:
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
