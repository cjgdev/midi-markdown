"""Integration tests for import system (Stage 4).

Tests full compilation pipeline with device library imports.
"""

from pathlib import Path

import pytest

from midi_markdown.alias.imports import CircularImportError, ImportError, ImportManager
from midi_markdown.expansion.expander import CommandExpander
from midi_markdown.midi.events import MIDIEvent, string_to_event_type


class TestImportIntegration:
    """Integration tests for import system."""

    @pytest.fixture
    def import_manager(self, parser):
        """Create import manager instance."""
        return ImportManager(parser)

    def test_compile_with_single_import(self, parser, import_manager, resolve_aliases):
        """Test compiling a file with single device library import."""
        fixture_path = Path("tests/fixtures/valid/with_single_import.mmd")
        doc = parser.parse_file(fixture_path)

        # Process imports
        imported_aliases = import_manager.resolve_imports(
            imports=doc.imports, current_file=str(fixture_path)
        )

        # Merge into document
        doc.aliases.update(imported_aliases)

        # Resolve aliases before generating events
        resolved_events = resolve_aliases(doc)
        doc.events = resolved_events

        # Generate events
        expander = CommandExpander(ppq=480, tempo=120)
        expanded_dicts = expander.process_ast(doc.events)
        events = [
            MIDIEvent(
                time=d["time"],
                type=string_to_event_type(d["type"]),
                channel=d.get("channel", 0),
                data1=d.get("data1", 0),
                data2=d.get("data2", 0),
            )
            for d in expanded_dicts
        ]

        # Should have generated events from alias expansion
        assert len(events) > 0
        # Should have imported aliases
        assert len(imported_aliases) > 0
        assert "device_a_init" in imported_aliases

    def test_compile_with_multiple_imports(self, parser, import_manager, resolve_aliases):
        """Test compiling with multiple device library imports."""
        fixture_path = Path("tests/fixtures/valid/with_multiple_imports.mmd")
        doc = parser.parse_file(fixture_path)

        # Process imports
        imported_aliases = import_manager.resolve_imports(
            imports=doc.imports, current_file=str(fixture_path)
        )

        # Merge into document
        doc.aliases.update(imported_aliases)

        # Resolve aliases before generating events
        resolved_events = resolve_aliases(doc)
        doc.events = resolved_events

        # Generate events
        expander = CommandExpander(ppq=480, tempo=120)
        expanded_dicts = expander.process_ast(doc.events)
        events = [
            MIDIEvent(
                time=d["time"],
                type=string_to_event_type(d["type"]),
                channel=d.get("channel", 0),
                data1=d.get("data1", 0),
                data2=d.get("data2", 0),
            )
            for d in expanded_dicts
        ]

        # Should have imported from both libraries
        assert "device_a_init" in imported_aliases
        assert "device_b_init" in imported_aliases
        assert len(events) > 0

    def test_compile_with_nested_imports(self, parser, import_manager):
        """Test compiling with nested imports (library imports another library)."""
        fixture_path = Path("tests/fixtures/valid/with_nested_imports.mmd")
        doc = parser.parse_file(fixture_path)

        # Process imports
        imported_aliases = import_manager.resolve_imports(
            imports=doc.imports, current_file=str(fixture_path)
        )

        # Merge into document
        doc.aliases.update(imported_aliases)

        # Should have aliases from nested imports
        assert "nested_command" in imported_aliases
        assert "device_a_init" in imported_aliases  # From nested import
        assert "device_a_preset" in imported_aliases

    def test_import_nonexistent_file_error(self, parser, import_manager):
        """Test error when importing nonexistent file."""
        fixture_path = Path("tests/fixtures/invalid/imports/missing_import.mmd")
        doc = parser.parse_file(fixture_path)

        with pytest.raises(ImportError) as exc_info:
            import_manager.resolve_imports(imports=doc.imports, current_file=str(fixture_path))
        assert "File not found" in str(exc_info.value)

    def test_circular_import_error(self, parser, import_manager):
        """Test circular import detection."""
        fixture_path = Path("tests/fixtures/invalid/imports/circular_a.mmd")
        doc = parser.parse_file(fixture_path)

        with pytest.raises(CircularImportError) as exc_info:
            import_manager.resolve_imports(imports=doc.imports, current_file=str(fixture_path))
        assert "Circular import detected" in str(exc_info.value)

    def test_import_conflict_error(self, parser, import_manager, tmp_path):
        """Test error when imports have conflicting alias names."""
        # Create two libraries with same alias name
        lib1 = tmp_path / "lib1.mmd"
        lib1.write_text("""---
device: Library 1
---

@alias duplicate {ch} "From lib1"
  - cc {ch}.1.0
@end
""")

        lib2 = tmp_path / "lib2.mmd"
        lib2.write_text("""---
device: Library 2
---

@alias duplicate {ch} "From lib2"
  - cc {ch}.2.0
@end
""")

        # Create main file that imports both
        main_file = tmp_path / "main.mmd"
        main_file.write_text("""---
title: Test Conflict
---

@import "lib1.mmd"
@import "lib2.mmd"

[00:00.000]
- pc 1.0
""")

        doc = parser.parse_file(main_file)

        with pytest.raises(ImportError) as exc_info:
            import_manager.resolve_imports(imports=doc.imports, current_file=str(main_file))
        assert "Alias name conflict" in str(exc_info.value)
        assert "duplicate" in str(exc_info.value)


class TestRealDeviceLibraries:
    """Test real device libraries (Quad Cortex, H90)."""

    @pytest.fixture
    def import_manager(self, parser):
        """Create import manager instance."""
        return ImportManager(parser)

    def test_load_quad_cortex_library(self, import_manager, resolve_aliases):
        """Test loading Quad Cortex device library."""
        qc_path = Path("devices/quad_cortex.mmd")
        aliases = import_manager.load_library(qc_path)

        # Check expected aliases exist
        assert "qc_preset" in aliases
        assert "qc_scene" in aliases
        assert "qc_load_preset" in aliases  # Multi-command macro
        assert "qc_exp1" in aliases
        assert "qc_stomp_a" in aliases
        assert "qc_tempo" in aliases

        # Verify it's a reasonable number
        assert len(aliases) >= 20

    def test_load_h90_library(self, import_manager):
        """Test loading Eventide H90 device library."""
        h90_path = Path("devices/eventide_h90.mmd")
        aliases = import_manager.load_library(h90_path)

        # Check expected aliases exist
        assert "h90_program" in aliases
        assert "h90_mix" in aliases
        assert "h90_program_bypass" in aliases
        assert "h90_dual_reverb_setup" in aliases  # Multi-command macro

        # Verify it's a reasonable number
        assert len(aliases) >= 20

    def test_compile_with_quad_cortex(self, parser, import_manager, tmp_path, resolve_aliases):
        """Test compiling a song that uses Quad Cortex library."""
        # Use absolute path to device library
        qc_path = Path("devices/quad_cortex.mmd").resolve()

        song_file = tmp_path / "qc_song.mmd"
        song_file.write_text(f"""---
title: Quad Cortex Test Song
tempo: 120
---

@import "{qc_path}"

# Switch scenes during song
[00:00.000]
- qc_scene_a 1

[00:04.000]
- qc_scene_b 1

[00:08.000]
- qc_load_preset 1 0 0 5
""")

        doc = parser.parse_file(song_file)

        # Process imports
        imported_aliases = import_manager.resolve_imports(
            imports=doc.imports, current_file=str(song_file)
        )
        doc.aliases.update(imported_aliases)

        # Resolve aliases before generating events
        resolved_events = resolve_aliases(doc)
        doc.events = resolved_events

        # Generate events
        expander = CommandExpander(ppq=480, tempo=120)
        expanded_dicts = expander.process_ast(doc.events)
        events = [
            MIDIEvent(
                time=d["time"],
                type=string_to_event_type(d["type"]),
                channel=d.get("channel", 0),
                data1=d.get("data1", 0),
                data2=d.get("data2", 0),
            )
            for d in expanded_dicts
        ]

        # Should have generated MIDI events
        assert len(events) > 0
        # qc_load_preset is a macro, should expand to 3 commands (with timing)
        assert len(events) >= 5  # 2 scene commands + 3 from qc_load_preset macro

    def test_compile_with_h90(self, parser, import_manager, tmp_path, resolve_aliases):
        """Test compiling a song that uses H90 library."""
        # Use absolute path to device library
        h90_path = Path("devices/eventide_h90.mmd").resolve()

        song_file = tmp_path / "h90_song.mmd"
        song_file.write_text(f"""---
title: H90 Test Song
tempo: 120
---

@import "{h90_path}"

# Configure H90 settings
[00:00.000]
- h90_program 2 10
- h90_mix 2 50

[00:04.000]
- h90_program_bypass 2
""")

        doc = parser.parse_file(song_file)

        # Process imports
        imported_aliases = import_manager.resolve_imports(
            imports=doc.imports, current_file=str(song_file)
        )
        doc.aliases.update(imported_aliases)

        # Resolve aliases before generating events
        resolved_events = resolve_aliases(doc)
        doc.events = resolved_events

        # Generate events
        expander = CommandExpander(ppq=480, tempo=120)
        expanded_dicts = expander.process_ast(doc.events)
        events = [
            MIDIEvent(
                time=d["time"],
                type=string_to_event_type(d["type"]),
                channel=d.get("channel", 0),
                data1=d.get("data1", 0),
                data2=d.get("data2", 0),
            )
            for d in expanded_dicts
        ]

        # Should have generated MIDI events
        assert len(events) > 0
