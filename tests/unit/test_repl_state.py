"""Tests for REPL state management."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from midi_markdown.runtime.repl_state import REPLState

if TYPE_CHECKING:
    from pathlib import Path


class TestREPLStateInitialization:
    """Test REPLState initialization and default values."""

    def test_default_values(self):
        """Test that state initializes with correct defaults."""
        state = REPLState()

        assert state.tempo == 120
        assert state.resolution == 480
        assert state.time_signature == (4, 4)
        assert state.last_ir is None

    def test_empty_collections(self):
        """Test that collections initialize as empty."""
        state = REPLState()

        assert state.variables == {}
        assert state.aliases == {}
        assert state.imports == []

    def test_mutable_defaults_independent(self):
        """Test that multiple instances don't share mutable defaults."""
        state1 = REPLState()
        state2 = REPLState()

        state1.variables["foo"] = 42
        state1.imports.append("device.mmd")

        assert "foo" not in state2.variables
        assert "device.mmd" not in state2.imports


@pytest.mark.unit
class TestREPLStateReset:
    """Test REPLState reset functionality."""

    def test_reset_clears_variables(self):
        """Test that reset clears all variables."""
        state = REPLState()
        state.variables["velocity"] = 80
        state.variables["channel"] = 1

        state.reset()

        assert state.variables == {}

    def test_reset_clears_aliases(self):
        """Test that reset clears all aliases."""
        state = REPLState()
        state.aliases["preset_load"] = {"name": "preset_load", "params": []}

        state.reset()

        assert state.aliases == {}

    def test_reset_clears_imports(self):
        """Test that reset clears all imports."""
        state = REPLState()
        state.imports.append("devices/quad_cortex.mmd")
        state.imports.append("devices/h90.mmd")

        state.reset()

        assert state.imports == []

    def test_reset_restores_defaults(self):
        """Test that reset restores default tempo and resolution."""
        state = REPLState()
        state.tempo = 140
        state.resolution = 960
        state.time_signature = (3, 4)

        state.reset()

        assert state.tempo == 120
        assert state.resolution == 480
        assert state.time_signature == (4, 4)

    def test_reset_clears_last_ir(self):
        """Test that reset clears last_ir."""
        state = REPLState()
        state.last_ir = "fake_ir_program"  # type: ignore

        state.reset()

        assert state.last_ir is None


@pytest.mark.unit
class TestREPLStateSessionPersistence:
    """Test REPLState session save/load functionality."""

    def test_save_session(self, tmp_path: Path):
        """Test that save_session creates a valid JSON file."""
        state = REPLState()
        state.variables["velocity"] = 80
        state.tempo = 140
        session_file = tmp_path / "session.json"

        state.save_session(session_file)

        assert session_file.exists()
        with session_file.open("r") as f:
            data = json.load(f)
        assert data["variables"]["velocity"] == 80
        assert data["tempo"] == 140

    def test_load_session(self, tmp_path: Path):
        """Test that load_session restores state from JSON."""
        session_file = tmp_path / "session.json"
        session_data = {
            "variables": {"velocity": 80, "channel": 1},
            "aliases": {},
            "imports": ["devices/quad_cortex.mmd"],
            "tempo": 140,
            "resolution": 960,
            "time_signature": [3, 4],
        }
        with session_file.open("w") as f:
            json.dump(session_data, f)

        state = REPLState()
        state.load_session(session_file)

        assert state.variables == {"velocity": 80, "channel": 1}
        assert state.imports == ["devices/quad_cortex.mmd"]
        assert state.tempo == 140
        assert state.resolution == 960
        assert state.time_signature == (3, 4)

    def test_save_load_roundtrip(self, tmp_path: Path):
        """Test that save then load yields the same state."""
        state1 = REPLState()
        state1.variables["velocity"] = 80
        state1.variables["channel"] = 1
        state1.aliases["test_alias"] = {"name": "test", "params": []}
        state1.imports.append("devices/quad_cortex.mmd")
        state1.tempo = 140
        state1.resolution = 960
        state1.time_signature = (3, 4)

        session_file = tmp_path / "session.json"
        state1.save_session(session_file)

        state2 = REPLState()
        state2.load_session(session_file)

        assert state2.variables == state1.variables
        assert state2.aliases == state1.aliases
        assert state2.imports == state1.imports
        assert state2.tempo == state1.tempo
        assert state2.resolution == state1.resolution
        assert state2.time_signature == state1.time_signature

    def test_save_excludes_last_ir(self, tmp_path: Path):
        """Test that last_ir is not included in saved JSON."""
        state = REPLState()
        state.last_ir = "fake_ir_program"  # type: ignore
        session_file = tmp_path / "session.json"

        state.save_session(session_file)

        with session_file.open("r") as f:
            data = json.load(f)
        assert "last_ir" not in data

    def test_load_missing_file(self, tmp_path: Path):
        """Test that loading a missing file raises FileNotFoundError."""
        state = REPLState()
        missing_file = tmp_path / "missing.json"

        with pytest.raises(FileNotFoundError):
            state.load_session(missing_file)

    def test_load_invalid_json(self, tmp_path: Path):
        """Test that loading invalid JSON raises JSONDecodeError."""
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("not valid json {]")

        state = REPLState()
        with pytest.raises(json.JSONDecodeError):
            state.load_session(invalid_file)


@pytest.mark.unit
class TestREPLStateUpdateFromFrontmatter:
    """Test REPLState frontmatter update functionality."""

    def test_update_tempo(self):
        """Test that frontmatter with tempo updates state."""
        state = REPLState()
        frontmatter = {"tempo": 140}

        state.update_from_frontmatter(frontmatter)

        assert state.tempo == 140

    def test_update_ppq(self):
        """Test that frontmatter with ppq updates resolution."""
        state = REPLState()
        frontmatter = {"ppq": 960}

        state.update_from_frontmatter(frontmatter)

        assert state.resolution == 960

    def test_update_time_signature_string(self):
        """Test that frontmatter with time_signature string updates state."""
        state = REPLState()
        frontmatter = {"time_signature": "3/4"}

        state.update_from_frontmatter(frontmatter)

        assert state.time_signature == (3, 4)

    def test_update_time_signature_list(self):
        """Test that frontmatter with time_signature list updates state."""
        state = REPLState()
        frontmatter = {"time_signature": [6, 8]}

        state.update_from_frontmatter(frontmatter)

        assert state.time_signature == (6, 8)

    def test_update_multiple_fields(self):
        """Test that frontmatter with multiple fields updates all."""
        state = REPLState()
        frontmatter = {
            "tempo": 140,
            "ppq": 960,
            "time_signature": "5/4",
        }

        state.update_from_frontmatter(frontmatter)

        assert state.tempo == 140
        assert state.resolution == 960
        assert state.time_signature == (5, 4)

    def test_update_empty_frontmatter(self):
        """Test that empty frontmatter doesn't change state."""
        state = REPLState()
        original_tempo = state.tempo
        original_resolution = state.resolution
        frontmatter: dict[str, int] = {}

        state.update_from_frontmatter(frontmatter)

        assert state.tempo == original_tempo
        assert state.resolution == original_resolution

    def test_update_partial_frontmatter(self):
        """Test that partial frontmatter only updates specified fields."""
        state = REPLState()
        state.tempo = 100
        state.resolution = 240
        frontmatter = {"tempo": 140}  # Only tempo, not ppq

        state.update_from_frontmatter(frontmatter)

        assert state.tempo == 140
        assert state.resolution == 240  # Unchanged

    def test_update_with_extra_fields(self):
        """Test that extra frontmatter fields don't cause errors."""
        state = REPLState()
        frontmatter = {
            "tempo": 140,
            "title": "My Song",  # Extra field
            "artist": "Test Artist",  # Extra field
        }

        state.update_from_frontmatter(frontmatter)

        assert state.tempo == 140  # Should still work
