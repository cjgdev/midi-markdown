# Scripts Directory

Utility scripts for MIDI Markdown development and release management.

## Available Scripts

### bump_version.py

Automated version bumping script for releases.

**Purpose**: Updates version numbers across the project and creates git tags.

**Usage**:
```bash
# Patch release (0.1.0 -> 0.1.1)
python scripts/bump_version.py patch

# Minor release (0.1.0 -> 0.2.0)
python scripts/bump_version.py minor

# Major release (0.1.0 -> 1.0.0)
python scripts/bump_version.py major

# Set specific version
python scripts/bump_version.py 1.2.3

# Dry run (preview changes)
python scripts/bump_version.py patch --dry-run

# Skip git operations
python scripts/bump_version.py patch --no-git
```

**What it does**:
1. Updates version in `pyproject.toml`
2. Updates version in `src/midi_markdown/__init__.py`
3. Moves `[Unreleased]` changes to new version section in `CHANGELOG.md`
4. Creates git commit: "Release version X.Y.Z"
5. Creates git tag: "vX.Y.Z"

**Requirements**: Python 3.12+, git

**Via justfile**:
```bash
just release-patch    # Patch release
just release-minor    # Minor release
just release-major    # Major release
just release-version 1.2.3  # Specific version
```

## Adding New Scripts

When adding new scripts to this directory:

1. **Make them executable**: `chmod +x scripts/new_script.py`
2. **Add shebang**: `#!/usr/bin/env python3`
3. **Document usage**: Add docstring and help text
4. **Update this README**: Add section describing the script
5. **Add justfile command** (if appropriate): Add convenience command to `justfile`
6. **Test thoroughly**: Ensure script works on all platforms

## Best Practices

- **Keep scripts focused**: One responsibility per script
- **Use argparse**: For CLI argument parsing
- **Add --dry-run**: Preview changes before making them
- **Return proper exit codes**: 0 for success, non-zero for failure
- **Log operations**: Print what the script is doing
- **Handle errors gracefully**: Catch exceptions and show helpful messages

## See Also

- [Release Guide](../docs/developer-guide/releasing.md) - Complete release process documentation
- [CHANGELOG.md](../CHANGELOG.md) - Version history
- [justfile](../justfile) - Task runner commands
