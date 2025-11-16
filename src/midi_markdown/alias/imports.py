"""Import manager for loading device libraries and alias definitions.

This module handles:
- Resolving import paths (relative/absolute)
- Loading and parsing device library files
- Detecting circular imports
- Merging alias definitions from multiple sources
- Multi-path search (project-local → package data)
"""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from midi_markdown.parser.ast_nodes import AliasDefinition


class ImportError(Exception):
    """Raised when import operation fails."""


class CircularImportError(ImportError):
    """Raised when circular import is detected."""


def _get_package_data_paths() -> list[Path]:
    """Get search paths for package data (device libraries).

    Returns paths in priority order:
    1. Development mode: <repo_root>/devices/
    2. Editable install: <repo_root>/devices/
    3. Installed package: site-packages/midi_markdown/data/devices/

    Returns:
        List of Path objects to search for device libraries
    """
    search_paths: list[Path] = []

    # Try to get package data directory using importlib.resources
    try:
        package_files = files("midi_markdown")
        if package_files is not None:
            # For installed packages, device libraries are in data/devices/
            data_devices = package_files / "data" / "devices"
            if hasattr(data_devices, "joinpath"):
                # Convert Traversable to Path if possible
                try:
                    data_devices_path = Path(str(data_devices))
                    if data_devices_path.exists():
                        search_paths.append(data_devices_path)
                except (ValueError, OSError):
                    pass
    except (ImportError, AttributeError, TypeError):
        pass

    # Fallback: check if we're in development/editable mode
    # Find the package installation directory
    try:
        # Import here to avoid circular imports at module level
        import midi_markdown  # noqa: PLC0415

        package_init = Path(midi_markdown.__file__).parent
        # Check for repo root (editable install or development)
        # Go up from src/midi_markdown to find devices/
        repo_root = package_init.parent.parent
        devices_dir = repo_root / "devices"
        if devices_dir.exists() and devices_dir.is_dir():
            search_paths.insert(0, devices_dir)  # Prioritize development path
    except (ImportError, AttributeError):
        pass

    return search_paths


class ImportManager:
    """Manages loading and resolution of @import directives.

    The import manager:
    1. Resolves import paths relative to current file
    2. Loads and parses imported MML files
    3. Detects circular import chains
    4. Extracts alias definitions from imported files
    5. Merges aliases with conflict detection

    Example:
        >>> manager = ImportManager(parser)
        >>> aliases = manager.resolve_imports(
        ...     imports=["devices/quad_cortex.mmd"],
        ...     current_file="main.mmd"
        ... )
    """

    def __init__(self, parser: Any) -> None:
        """Initialize the import manager.

        Args:
            parser: MMDParser instance for parsing imported files
        """
        self.parser = parser
        self._import_cache: dict[str, dict[str, AliasDefinition]] = {}

    def resolve_path(self, import_path: str, current_file: str | None = None) -> Path:
        """Resolve import path to absolute path.

        Import paths can be:
        - Relative: "devices/quad_cortex.mmd" (searched in multiple locations)
        - Absolute: "/usr/local/share/mml/devices/h90.mmd"

        Search order for relative paths:
        1. Relative to current file's directory (if current_file provided)
        2. Package data directories (bundled device libraries)
        3. Relative to current working directory

        Note: This method returns the resolved path without checking existence.
        The actual existence check happens in load_library().

        Args:
            import_path: Path from @import directive
            current_file: Path to file containing the import

        Returns:
            Resolved absolute path (may not exist yet)

        Example:
            >>> manager.resolve_path("devices/quad_cortex.mmd", "/home/user/song.mmd")
            Path("/home/user/devices/quad_cortex.mmd")
        """
        path = Path(import_path)

        # If already absolute, use as-is (no existence check)
        if path.is_absolute():
            return path.resolve()

        # Relative path - prioritize project-local, then fall back to package data
        #
        # Strategy:
        # 1. Determine primary location (relative to current file or CWD)
        # 2. If file exists there, use it
        # 3. If not, search package data directories
        # 4. If still not found, return primary location (let load_library error)

        # 1. Determine primary location
        if current_file:
            # Relative to current file's directory
            primary_path = (Path(current_file).parent / path).resolve()
        else:
            # Relative to current working directory
            primary_path = path.resolve()

        # 2. If file exists at primary location, use it (project-local priority)
        if primary_path.exists():
            return primary_path

        # 3. File doesn't exist locally - search package data directories
        package_data_paths = _get_package_data_paths()
        for data_path in package_data_paths:
            # Try full path: data_path / devices/quad_cortex.mmd
            package_candidate = (data_path / path).resolve()
            if package_candidate.exists():
                return package_candidate

            # If path starts with "devices/", also try without that prefix
            # (since package data path already points to devices/ directory)
            path_str = str(path)
            if path_str.startswith(("devices/", "devices\\")):
                relative_to_devices = Path(path_str[8:])  # Strip "devices/" or "devices\"
                package_candidate_stripped = (data_path / relative_to_devices).resolve()
                if package_candidate_stripped.exists():
                    return package_candidate_stripped

        # 4. File doesn't exist anywhere - return primary location
        # (load_library() will handle the error with better context)
        return primary_path

    def check_circular_import(self, filepath: Path, import_chain: list[str]) -> None:
        """Check if importing this file would create a circular import.

        Args:
            filepath: Path to file being imported
            import_chain: List of file paths already in import chain

        Raises:
            CircularImportError: If circular import detected

        Example:
            >>> # A imports B, B imports C, C imports A
            >>> manager.check_circular_import(
            ...     Path("A.mmd"),
            ...     ["A.mmd", "B.mmd", "C.mmd"]
            ... )
            CircularImportError: Circular import detected: A.mmd → B.mmd → C.mmd → A.mmd
        """
        # Normalize filepath for comparison (resolve to absolute path)
        # This ensures consistent comparison across platforms (Windows vs Unix)
        filepath_normalized = str(filepath.resolve())

        # Normalize all paths in the chain for comparison
        # This handles path separator differences (/ vs \) and case sensitivity
        normalized_chain = [str(Path(p).resolve()) for p in import_chain]

        if filepath_normalized in normalized_chain:
            # Build the cycle string for error message using original chain
            # Use as_posix() to ensure forward slashes on all platforms (Windows uses \)
            filepath_str = filepath.as_posix()
            cycle_chain = [*import_chain, filepath_str]
            chain_str = " → ".join(cycle_chain)
            msg = (
                f"Circular import detected: {chain_str}\n\n"
                f"File '{filepath.name}' is already being imported in this chain."
            )
            raise CircularImportError(msg)

    def load_library(
        self, filepath: Path, import_chain: list[str] | None = None
    ) -> dict[str, AliasDefinition]:
        """Load a device library file and extract alias definitions.

        This method:
        1. Checks for circular imports
        2. Loads and parses the MML file
        3. Recursively loads any nested imports
        4. Extracts alias definitions
        5. Returns merged alias dict

        Args:
            filepath: Absolute path to library file
            import_chain: Current import chain for circular detection

        Returns:
            Dictionary mapping alias names to definitions

        Raises:
            ImportError: If file not found or parse error
            CircularImportError: If circular import detected
        """
        import_chain = import_chain or []
        filepath_str = str(filepath)

        # Check cache first
        if filepath_str in self._import_cache:
            return self._import_cache[filepath_str]

        # Check for circular imports
        self.check_circular_import(filepath, import_chain)

        # Check file exists
        if not filepath.exists():
            msg = (
                f"Import failed: File not found: {filepath}\n\n"
                f"Import chain: {' → '.join([*import_chain, filepath_str])}"
            )
            raise ImportError(msg)

        # Parse the file
        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()
            doc = self.parser.parse_string(content)
        except Exception as e:
            msg = (
                f"Import failed: Error parsing {filepath}\n"
                f"Error: {e}\n\n"
                f"Import chain: {' → '.join([*import_chain, filepath_str])}"
            )
            raise ImportError(msg)

        # Add to chain for nested imports
        new_chain = [*import_chain, filepath_str]

        # Start with aliases defined in this file
        merged_aliases = doc.aliases.copy()

        # Recursively load nested imports
        for nested_import in doc.imports:
            nested_path = self.resolve_path(nested_import, str(filepath))
            nested_aliases = self.load_library(nested_path, new_chain)

            # Merge with conflict detection
            for alias_name, alias_def in nested_aliases.items():
                if alias_name in merged_aliases:
                    # Conflict: same alias defined in multiple imports
                    merged_aliases[alias_name]
                    msg = (
                        f"Alias name conflict: '{alias_name}' is defined in multiple imports\n\n"
                        f"First definition: (from earlier import or current file)\n"
                        f"Second definition: {nested_path}\n\n"
                        f"Import chain: {' → '.join([*new_chain, str(nested_path)])}\n\n"
                        f"Suggestion: Rename one of the aliases or use different device libraries."
                    )
                    raise ImportError(msg)
                merged_aliases[alias_name] = alias_def

        # Cache the result
        self._import_cache[filepath_str] = merged_aliases

        return merged_aliases

    def resolve_imports(
        self, imports: list[str], current_file: str | None = None
    ) -> dict[str, AliasDefinition]:
        """Resolve all imports for a document.

        This is the main entry point for import resolution.

        Args:
            imports: List of import paths from @import directives
            current_file: Path to file containing the imports

        Returns:
            Dictionary of all imported aliases (merged)

        Raises:
            ImportError: If any import fails
            CircularImportError: If circular import detected
        """
        merged_aliases: dict[str, AliasDefinition] = {}

        for import_path in imports:
            # Resolve the path
            resolved_path = self.resolve_path(import_path, current_file)

            # Load the library and its nested imports
            library_aliases = self.load_library(resolved_path)

            # Merge with conflict detection at top level
            for alias_name, alias_def in library_aliases.items():
                if alias_name in merged_aliases:
                    msg = (
                        f"Alias name conflict: '{alias_name}' is defined in multiple imports\n\n"
                        f"First import: (earlier import)\n"
                        f"Second import: {import_path}\n\n"
                        f"Suggestion: Use different device libraries or rename aliases."
                    )
                    raise ImportError(msg)
                merged_aliases[alias_name] = alias_def

        return merged_aliases

    def clear_cache(self) -> None:
        """Clear the import cache.

        Useful for testing or when files have changed.
        """
        self._import_cache.clear()
