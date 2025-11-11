"""Unit tests for import system (Stage 4).

Tests for ImportManager, path resolution, circular import detection,
and device library loading.
"""

from pathlib import Path

import pytest

from midi_markdown.alias.imports import CircularImportError, ImportError, ImportManager


class TestImportManager:
    """Test ImportManager core functionality."""

    @pytest.fixture
    def manager(self, parser):
        """Create ImportManager instance for tests."""
        return ImportManager(parser)

    def test_resolve_path_absolute(self, manager):
        """Test absolute path resolution."""
        abs_path = "/usr/local/share/mml/device.mmd"
        resolved = manager.resolve_path(abs_path, current_file="/home/user/song.mmd")
        assert resolved == Path(abs_path).resolve()

    def test_resolve_path_relative(self, manager):
        """Test relative path resolution."""
        import_path = "devices/quad_cortex.mmd"
        current_file = "/home/user/songs/main.mmd"
        resolved = manager.resolve_path(import_path, current_file)
        expected = Path("/home/user/songs/devices/quad_cortex.mmd").resolve()
        assert resolved == expected

    def test_resolve_path_no_current_file(self, manager):
        """Test path resolution when current_file is None (stdin case)."""
        import_path = "devices/test.mmd"
        resolved = manager.resolve_path(import_path, current_file=None)
        # Should resolve relative to cwd
        expected = (Path.cwd() / import_path).resolve()
        assert resolved == expected

    def test_check_circular_import_no_cycle(self, manager):
        """Test circular import detection with no cycle."""
        # Should not raise
        manager.check_circular_import(Path("/a.mmd"), ["/b.mmd", "/c.mmd"])

    def test_check_circular_import_direct_cycle(self, manager):
        """Test detection of direct circular import (A imports A)."""
        with pytest.raises(CircularImportError) as exc_info:
            manager.check_circular_import(Path("/a.mmd"), ["/a.mmd"])
        assert "Circular import detected" in str(exc_info.value)
        assert "/a.mmd → /a.mmd" in str(exc_info.value)

    def test_check_circular_import_indirect_cycle(self, manager):
        """Test detection of indirect circular import (A → B → C → A)."""
        with pytest.raises(CircularImportError) as exc_info:
            manager.check_circular_import(Path("/a.mmd"), ["/a.mmd", "/b.mmd", "/c.mmd"])
        assert "Circular import detected" in str(exc_info.value)
        assert "/a.mmd → /b.mmd → /c.mmd → /a.mmd" in str(exc_info.value)


class TestImportLibraryLoading:
    """Test library loading functionality."""

    @pytest.fixture
    def manager(self, parser):
        """Create ImportManager instance for tests."""
        return ImportManager(parser)

    def test_load_nonexistent_file(self, manager):
        """Test error when loading nonexistent file."""
        with pytest.raises(ImportError) as exc_info:
            manager.load_library(Path("/nonexistent/file.mmd"))
        assert "File not found" in str(exc_info.value)

    def test_load_device_library(self, manager, tmp_path):
        """Test loading a basic device library."""
        # Create a simple device library
        lib_file = tmp_path / "test_device.mmd"
        lib_file.write_text("""---
device: Test Device
---

@alias test_cmd {ch} {val} "Test command"
  - cc {ch}.7.{val}
@end
""")

        # Load the library
        aliases = manager.load_library(lib_file)

        # Verify alias was loaded
        assert "test_cmd" in aliases
        assert aliases["test_cmd"].name == "test_cmd"
        assert len(aliases["test_cmd"].parameters) == 2

    def test_resolve_imports_multiple(self, manager, tmp_path):
        """Test resolving multiple imports."""
        # Create two device libraries
        lib1 = tmp_path / "device1.mmd"
        lib1.write_text("""---
device: Device 1
---

@alias cmd1 {ch} "Command 1"
  - cc {ch}.1.0
@end
""")

        lib2 = tmp_path / "device2.mmd"
        lib2.write_text("""---
device: Device 2
---

@alias cmd2 {ch} "Command 2"
  - cc {ch}.2.0
@end
""")

        # Resolve imports
        aliases = manager.resolve_imports(
            imports=["device1.mmd", "device2.mmd"], current_file=str(tmp_path / "main.mmd")
        )

        # Both aliases should be present
        assert "cmd1" in aliases
        assert "cmd2" in aliases

    def test_import_conflict_detection(self, manager, tmp_path):
        """Test detection of alias name conflicts between imports."""
        # Create two libraries with conflicting alias names
        lib1 = tmp_path / "device1.mmd"
        lib1.write_text("""---
device: Device 1
---

@alias duplicate {ch} "Command from device 1"
  - cc {ch}.1.0
@end
""")

        lib2 = tmp_path / "device2.mmd"
        lib2.write_text("""---
device: Device 2
---

@alias duplicate {ch} "Command from device 2"
  - cc {ch}.2.0
@end
""")

        # Should raise ImportError
        with pytest.raises(ImportError) as exc_info:
            manager.resolve_imports(
                imports=["device1.mmd", "device2.mmd"], current_file=str(tmp_path / "main.mmd")
            )
        assert "Alias name conflict" in str(exc_info.value)
        assert "duplicate" in str(exc_info.value)

    def test_recursive_imports(self, manager, tmp_path):
        """Test recursive import resolution (A imports B, B imports C)."""
        # Create C (leaf)
        lib_c = tmp_path / "c.mmd"
        lib_c.write_text("""---
device: Device C
---

@alias cmd_c {ch} "Command from C"
  - cc {ch}.3.0
@end
""")

        # Create B (imports C)
        lib_b = tmp_path / "b.mmd"
        lib_b.write_text("""---
device: Device B
---

@import "c.mmd"

@alias cmd_b {ch} "Command from B"
  - cc {ch}.2.0
@end
""")

        # Create A (imports B)
        lib_a = tmp_path / "a.mmd"
        lib_a.write_text("""---
device: Device A
---

@import "b.mmd"

@alias cmd_a {ch} "Command from A"
  - cc {ch}.1.0
@end
""")

        # Load A (should recursively load B and C)
        aliases = manager.load_library(lib_a)

        # All three aliases should be present
        assert "cmd_a" in aliases
        assert "cmd_b" in aliases
        assert "cmd_c" in aliases

    def test_circular_import_detection_in_loading(self, manager, tmp_path):
        """Test circular import detection during library loading."""
        # Create A (imports B)
        lib_a = tmp_path / "a.mmd"
        lib_a.write_text("""---
device: Device A
---

@import "b.mmd"

@alias cmd_a {ch} "Command from A"
  - cc {ch}.1.0
@end
""")

        # Create B (imports A - circular!)
        lib_b = tmp_path / "b.mmd"
        lib_b.write_text("""---
device: Device B
---

@import "a.mmd"

@alias cmd_b {ch} "Command from B"
  - cc {ch}.2.0
@end
""")

        # Should detect circular import
        with pytest.raises(CircularImportError) as exc_info:
            manager.load_library(lib_a)
        assert "Circular import detected" in str(exc_info.value)

    def test_cache_functionality(self, manager, tmp_path):
        """Test that import cache works correctly."""
        # Create a device library
        lib_file = tmp_path / "test.mmd"
        lib_file.write_text("""---
device: Test Device
---

@alias test {ch} "Test"
  - cc {ch}.1.0
@end
""")

        # Load twice
        aliases1 = manager.load_library(lib_file)
        aliases2 = manager.load_library(lib_file)

        # Should be same dict (from cache)
        assert aliases1 is aliases2

        # Clear cache and load again
        manager.clear_cache()
        aliases3 = manager.load_library(lib_file)

        # Should be different dict (fresh load)
        assert aliases1 is not aliases3
        # But same content
        assert aliases1.keys() == aliases3.keys()


class TestImportTypedParameters:
    """Test importing libraries with typed parameters (note, percent, etc.)."""

    @pytest.fixture
    def manager(self, parser):
        """Create ImportManager instance for tests."""
        return ImportManager(parser)

    def test_import_with_types(self, manager, tmp_path):
        """Test importing library with typed parameters."""
        lib_file = tmp_path / "typed.mmd"
        lib_file.write_text("""---
device: Typed Device
---

@alias chord {ch} {root:note} {vel} "Play chord"
  - note_on {ch}.{root}.{vel}
  - note_on {ch}.64.{vel}
@end

@alias mixer {ch} {level:percent} "Set mixer level"
  - cc {ch}.7.{level}
@end
""")

        # Load the library
        aliases = manager.load_library(lib_file)

        # Check aliases loaded with type info
        assert "chord" in aliases
        assert "mixer" in aliases

        # Verify parameter types
        chord_params = aliases["chord"].parameters
        assert chord_params[1]["name"] == "root"
        assert chord_params[1]["type"] == "note"

        mixer_params = aliases["mixer"].parameters
        assert mixer_params[1]["name"] == "level"
        assert mixer_params[1]["type"] == "percent"
