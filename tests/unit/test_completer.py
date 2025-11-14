"""Tests for Music Completer autocompletion."""

from __future__ import annotations

import pytest
from prompt_toolkit.document import Document

from midi_markdown.runtime.completer import MusicCompleter
from midi_markdown.runtime.repl_state import REPLState


def get_display_text(formatted_text):
    """Extract text from FormattedText object."""
    if formatted_text is None:
        return None
    # FormattedText is a list of (style, text) tuples
    if hasattr(formatted_text, "__iter__"):
        return "".join(text for _, text in formatted_text)
    return str(formatted_text)


class TestMIDICommandCompletion:
    """Test MIDI command autocompletion."""

    def test_complete_midi_commands_from_empty(self):
        """Test that all MIDI commands are suggested from empty input."""
        state = REPLState()
        completer = MusicCompleter(state)
        doc = Document("", cursor_position=0)

        completions = list(completer.get_completions(doc, None))
        completion_texts = [c.text for c in completions]

        assert "note_on" in completion_texts
        assert "note_off" in completion_texts
        assert "cc" in completion_texts
        assert "pc" in completion_texts

    def test_complete_midi_commands_partial(self):
        """Test that MIDI commands are filtered by prefix."""
        state = REPLState()
        completer = MusicCompleter(state)
        doc = Document("not", cursor_position=3)

        completions = list(completer.get_completions(doc, None))
        completion_texts = [c.text for c in completions]

        assert "note_on" in completion_texts
        assert "note_off" in completion_texts
        assert "cc" not in completion_texts
        assert "pc" not in completion_texts

    def test_complete_midi_commands_case_insensitive(self):
        """Test that completion is case-insensitive."""
        state = REPLState()
        completer = MusicCompleter(state)
        doc = Document("PC", cursor_position=2)

        completions = list(completer.get_completions(doc, None))
        completion_texts = [c.text for c in completions]

        assert "pc" in completion_texts

    def test_complete_midi_commands_no_match(self):
        """Test that invalid prefix returns no completions."""
        state = REPLState()
        completer = MusicCompleter(state)
        doc = Document("xyz", cursor_position=3)

        completions = list(completer.get_completions(doc, None))

        assert len(completions) == 0

    def test_complete_midi_commands_exact(self):
        """Test that exact match is still suggested."""
        state = REPLState()
        completer = MusicCompleter(state)
        doc = Document("cc", cursor_position=2)

        completions = list(completer.get_completions(doc, None))
        completion_texts = [c.text for c in completions]

        assert "cc" in completion_texts

    def test_completion_start_position(self):
        """Test that completion start_position replaces current word."""
        state = REPLState()
        completer = MusicCompleter(state)
        doc = Document("not", cursor_position=3)

        completions = list(completer.get_completions(doc, None))
        note_on_completion = next(c for c in completions if c.text == "note_on")

        assert note_on_completion.start_position == -3  # Replace "not"


@pytest.mark.unit
class TestMetaCommandCompletion:
    """Test meta-command autocompletion."""

    def test_complete_meta_commands_dot(self):
        """Test that starting with dot shows all meta-commands."""
        state = REPLState()
        completer = MusicCompleter(state)
        doc = Document(".", cursor_position=1)

        completions = list(completer.get_completions(doc, None))
        completion_texts = [c.text for c in completions]

        assert ".help" in completion_texts
        assert ".quit" in completion_texts
        assert ".reset" in completion_texts
        assert ".list" in completion_texts

    def test_complete_meta_commands_partial(self):
        """Test that partial meta-command filters correctly."""
        state = REPLState()
        completer = MusicCompleter(state)
        doc = Document(".he", cursor_position=3)

        completions = list(completer.get_completions(doc, None))
        completion_texts = [c.text for c in completions]

        assert ".help" in completion_texts
        assert ".quit" not in completion_texts
        assert ".reset" not in completion_texts

    def test_complete_meta_commands_exact(self):
        """Test that exact meta-command match works."""
        state = REPLState()
        completer = MusicCompleter(state)
        doc = Document(".quit", cursor_position=5)

        completions = list(completer.get_completions(doc, None))
        completion_texts = [c.text for c in completions]

        assert ".quit" in completion_texts

    def test_meta_commands_display_meta(self):
        """Test that meta-commands have descriptions."""
        state = REPLState()
        completer = MusicCompleter(state)
        doc = Document(".help", cursor_position=5)

        completions = list(completer.get_completions(doc, None))
        help_completion = next(c for c in completions if c.text == ".help")

        assert help_completion.display_meta is not None
        assert "command" in get_display_text(help_completion.display_meta).lower()


@pytest.mark.unit
class TestDirectiveCompletion:
    """Test directive (@define, @alias, etc.) autocompletion."""

    def test_complete_directives_at_symbol(self):
        """Test that @ shows all directives."""
        state = REPLState()
        completer = MusicCompleter(state)
        doc = Document("@", cursor_position=1)

        completions = list(completer.get_completions(doc, None))
        completion_texts = [c.text for c in completions]

        assert "@define" in completion_texts
        assert "@alias" in completion_texts
        assert "@import" in completion_texts
        assert "@loop" in completion_texts

    def test_complete_directives_partial(self):
        """Test that partial directive filters correctly."""
        state = REPLState()
        completer = MusicCompleter(state)
        doc = Document("@def", cursor_position=4)

        completions = list(completer.get_completions(doc, None))
        completion_texts = [c.text for c in completions]

        assert "@define" in completion_texts
        assert "@alias" not in completion_texts
        assert "@import" not in completion_texts

    def test_complete_directives_if_elif_else(self):
        """Test that conditional directives are suggested."""
        state = REPLState()
        completer = MusicCompleter(state)
        doc = Document("@if", cursor_position=3)

        completions = list(completer.get_completions(doc, None))
        completion_texts = [c.text for c in completions]

        assert "@if" in completion_texts
        # Also suggest @elif, @else when typing @if
        doc2 = Document("@el", cursor_position=3)
        completions2 = list(completer.get_completions(doc2, None))
        completion_texts2 = [c.text for c in completions2]

        assert "@elif" in completion_texts2
        assert "@else" in completion_texts2


@pytest.mark.unit
class TestAliasCompletion:
    """Test alias name autocompletion from state."""

    def test_complete_aliases_from_state(self):
        """Test that aliases in state are suggested."""
        state = REPLState()
        state.aliases["preset_load"] = {"name": "preset_load"}
        state.aliases["scene_change"] = {"name": "scene_change"}

        completer = MusicCompleter(state)
        doc = Document("- ", cursor_position=2)

        completions = list(completer.get_completions(doc, None))
        completion_texts = [c.text for c in completions]

        assert "preset_load" in completion_texts
        assert "scene_change" in completion_texts

    def test_complete_aliases_empty_state(self):
        """Test that no aliases are suggested if state is empty."""
        state = REPLState()
        completer = MusicCompleter(state)
        doc = Document("- ", cursor_position=2)

        completions = list(completer.get_completions(doc, None))
        # Should still have MIDI commands, but no aliases
        completion_texts = [c.text for c in completions]

        assert "note_on" in completion_texts  # MIDI command
        assert len([c for c in completions if get_display_text(c.display_meta) == "Alias"]) == 0

    def test_complete_aliases_filter_by_prefix(self):
        """Test that aliases are filtered by prefix."""
        state = REPLState()
        state.aliases["preset_load"] = {"name": "preset_load"}
        state.aliases["scene_change"] = {"name": "scene_change"}
        state.aliases["preset_change"] = {"name": "preset_change"}

        completer = MusicCompleter(state)
        doc = Document("- pre", cursor_position=5)

        completions = list(completer.get_completions(doc, None))
        alias_completions = [c for c in completions if get_display_text(c.display_meta) == "Alias"]
        alias_texts = [c.text for c in alias_completions]

        assert "preset_load" in alias_texts
        assert "preset_change" in alias_texts
        assert "scene_change" not in alias_texts  # Doesn't start with "pre"

    def test_complete_aliases_case_insensitive(self):
        """Test that alias completion is case-insensitive."""
        state = REPLState()
        state.aliases["PresetLoad"] = {"name": "PresetLoad"}

        completer = MusicCompleter(state)
        doc = Document("- preset", cursor_position=8)

        completions = list(completer.get_completions(doc, None))
        alias_texts = [c.text for c in completions if get_display_text(c.display_meta) == "Alias"]

        assert "PresetLoad" in alias_texts


@pytest.mark.unit
class TestVariableCompletion:
    """Test variable name autocompletion from state."""

    def test_complete_variables_from_state(self):
        """Test that variables in state are suggested."""
        state = REPLState()
        state.variables["velocity"] = 80
        state.variables["channel"] = 1

        completer = MusicCompleter(state)
        # Start typing a variable name after ${
        doc = Document("${v", cursor_position=3)

        completions = list(completer.get_completions(doc, None))
        completion_texts = [c.text for c in completions]

        assert "velocity" in completion_texts
        # channel doesn't start with 'v', so not included

    def test_complete_variables_after_dollar_brace(self):
        """Test that variables are suggested after ${ context."""
        state = REPLState()
        state.variables["velocity"] = 80

        completer = MusicCompleter(state)
        doc = Document("- cc 1.10.${vel", cursor_position=15)

        completions = list(completer.get_completions(doc, None))
        completion_texts = [c.text for c in completions]

        assert "velocity" in completion_texts

    def test_complete_variables_empty_state(self):
        """Test that no variables are suggested if none defined."""
        state = REPLState()
        completer = MusicCompleter(state)
        doc = Document("${", cursor_position=2)

        completions = list(completer.get_completions(doc, None))

        assert len(completions) == 0

    def test_complete_variables_partial(self):
        """Test that variables are filtered by prefix."""
        state = REPLState()
        state.variables["velocity"] = 80
        state.variables["volume"] = 100
        state.variables["channel"] = 1

        completer = MusicCompleter(state)
        doc = Document("${v", cursor_position=3)

        completions = list(completer.get_completions(doc, None))
        completion_texts = [c.text for c in completions]

        assert "velocity" in completion_texts
        assert "volume" in completion_texts
        assert "channel" not in completion_texts

    def test_complete_variables_display_value(self):
        """Test that variable completions show their values."""
        state = REPLState()
        state.variables["velocity"] = 80

        completer = MusicCompleter(state)
        doc = Document("${vel", cursor_position=5)

        completions = list(completer.get_completions(doc, None))
        velocity_completion = next(c for c in completions if c.text == "velocity")

        assert velocity_completion.display_meta is not None
        assert "80" in str(velocity_completion.display_meta)


@pytest.mark.unit
class TestNoteNameCompletion:
    """Test note name generation and completion."""

    def test_note_names_generated(self):
        """Test that all note names are generated."""
        state = REPLState()
        completer = MusicCompleter(state)

        # Should have 120+ notes (C-1 to G9 with sharps/flats)
        assert len(completer.note_names) > 120

    def test_note_names_include_naturals(self):
        """Test that natural notes are included."""
        state = REPLState()
        completer = MusicCompleter(state)

        assert "C4" in completer.note_names
        assert "D4" in completer.note_names
        assert "E4" in completer.note_names
        assert "F4" in completer.note_names
        assert "G4" in completer.note_names
        assert "A4" in completer.note_names
        assert "B4" in completer.note_names

    def test_note_names_include_sharps(self):
        """Test that sharps are included (no B# or E#)."""
        state = REPLState()
        completer = MusicCompleter(state)

        assert "C#4" in completer.note_names
        assert "D#4" in completer.note_names
        assert "F#4" in completer.note_names
        assert "G#4" in completer.note_names
        assert "A#4" in completer.note_names
        # No B# or E#
        assert "B#4" not in completer.note_names
        assert "E#4" not in completer.note_names

    def test_note_names_include_flats(self):
        """Test that flats are included (no Cb or Fb)."""
        state = REPLState()
        completer = MusicCompleter(state)

        assert "Db4" in completer.note_names
        assert "Eb4" in completer.note_names
        assert "Gb4" in completer.note_names
        assert "Ab4" in completer.note_names
        assert "Bb4" in completer.note_names
        # No Cb or Fb
        assert "Cb4" not in completer.note_names
        assert "Fb4" not in completer.note_names

    def test_note_names_octave_range(self):
        """Test that octave range is correct (-1 to 9)."""
        state = REPLState()
        completer = MusicCompleter(state)

        # Lowest note (C-1)
        assert "C-1" in completer.note_names
        # Highest note (G9)
        assert "G9" in completer.note_names
        # Out of range
        assert "C10" not in completer.note_names
        assert "G-2" not in completer.note_names

    def test_complete_note_partial(self):
        """Test that note completion filters by prefix."""
        state = REPLState()
        completer = MusicCompleter(state)

        completions = list(completer._complete_note_names("C#"))
        completion_texts = [c.text for c in completions]

        # Should match C#-1, C#0, C#1, ..., C#9
        assert any("C#" in text for text in completion_texts)
        # Should not match other notes
        assert not any(text.startswith("D") for text in completion_texts)

    def test_complete_note_limit(self):
        """Test that note completion is limited to prevent overwhelming list."""
        state = REPLState()
        completer = MusicCompleter(state)

        # Completing just "C" would match C-1, C0, C1, ..., C9, C#-1, C#0, etc.
        completions = list(completer._complete_note_names("C"))

        # Should be limited to 50 completions
        assert len(completions) <= 50


@pytest.mark.unit
class TestContextAwareCompletion:
    """Test context-aware completion routing."""

    def test_context_switches_correctly(self):
        """Test that different contexts trigger different completions."""
        state = REPLState()
        state.variables["velocity"] = 80
        state.aliases["preset_load"] = {"name": "preset_load"}
        completer = MusicCompleter(state)

        # Meta-command context
        doc1 = Document(".he", cursor_position=3)
        completions1 = list(completer.get_completions(doc1, None))
        assert any(c.text == ".help" for c in completions1)

        # Directive context
        doc2 = Document("@def", cursor_position=4)
        completions2 = list(completer.get_completions(doc2, None))
        assert any(c.text == "@define" for c in completions2)

        # Variable context
        doc3 = Document("${vel", cursor_position=5)
        completions3 = list(completer.get_completions(doc3, None))
        assert any(c.text == "velocity" for c in completions3)

        # MIDI command context
        doc4 = Document("not", cursor_position=3)
        completions4 = list(completer.get_completions(doc4, None))
        assert any(c.text == "note_on" for c in completions4)

    def test_after_timing_marker(self):
        """Test that after timing marker, MIDI commands are suggested."""
        state = REPLState()
        completer = MusicCompleter(state)
        doc = Document("[00:00.000]\n- ", cursor_position=14)

        completions = list(completer.get_completions(doc, None))
        completion_texts = [c.text for c in completions]

        assert "note_on" in completion_texts
        assert "cc" in completion_texts

    def test_multi_word_line(self):
        """Test that only current word is completed."""
        state = REPLState()
        completer = MusicCompleter(state)
        # Typing "- note_on 1.60.80 " then starting a new command
        doc = Document("- note_on 1.60.80 n", cursor_position=19)

        # Should complete the word "n" (suggests note_on, note_off)
        completions = list(completer.get_completions(doc, None))
        completion_texts = [c.text for c in completions]

        # Should suggest MIDI commands starting with 'n'
        assert "note_on" in completion_texts or "note_off" in completion_texts

    def test_variable_reference_not_closed(self):
        """Test that variable context is detected when ${ not closed."""
        state = REPLState()
        state.variables["velocity"] = 80
        completer = MusicCompleter(state)

        # Variable reference not closed
        doc = Document("- cc 1.10.${vel", cursor_position=15)
        completions = list(completer.get_completions(doc, None))
        completion_texts = [c.text for c in completions]

        assert "velocity" in completion_texts

        # Variable reference closed - should not suggest variables
        doc2 = Document("- cc 1.10.${velocity} ", cursor_position=22)
        completions2 = list(completer.get_completions(doc2, None))
        [c.text for c in completions2]

        # After closing }, back to MIDI command context
        assert any(c.text in ["note_on", "cc", "pc"] for c in completions2)
