"""Tests for REPL session management and multi-line input handling."""

from __future__ import annotations

import pytest

from midi_markdown.parser.ast_nodes import MMDDocument
from midi_markdown.runtime.repl import MMLRepl


@pytest.mark.unit
class TestMMLReplInitialization:
    """Test MMLRepl initialization and default values."""

    def test_default_initialization(self):
        """Test that REPL initializes with correct defaults."""
        repl = MMLRepl()

        assert repl.parser is not None
        assert repl.state is not None
        assert repl.buffer == []

    def test_state_defaults(self):
        """Test that REPL state has correct initial values."""
        repl = MMLRepl()

        assert repl.state.tempo == 120
        assert repl.state.resolution == 480
        assert repl.state.variables == {}
        assert repl.state.aliases == {}

    def test_multiple_instances_independent(self):
        """Test that multiple REPL instances don't share state."""
        repl1 = MMLRepl()
        repl2 = MMLRepl()

        repl1.state.variables["foo"] = 42
        repl1.buffer.append("test")

        assert "foo" not in repl2.state.variables
        assert "test" not in repl2.buffer


@pytest.mark.unit
class TestTryParseIncomplete:
    """Test try_parse() with incomplete input (unexpected $END token)."""

    def test_incomplete_loop_block(self):
        """Test that unclosed @loop block is detected as incomplete."""
        repl = MMLRepl()
        text = "@loop 3 times every 1b"

        complete, result = repl.try_parse(text)

        assert complete is False
        assert result is None

    def test_incomplete_loop_with_command(self):
        """Test that @loop with commands but no @end is incomplete."""
        repl = MMLRepl()
        text = "@loop 3 times every 1b\n- pc 1.10"

        complete, result = repl.try_parse(text)

        assert complete is False
        assert result is None


@pytest.mark.unit
class TestTryParseComplete:
    """Test try_parse() with complete and valid input."""

    def test_complete_define_statement(self):
        """Test that @define statement is complete and valid."""
        repl = MMLRepl()
        text = "@define VELOCITY 80"

        complete, result = repl.try_parse(text)

        assert complete is True
        assert isinstance(result, MMDDocument)

    def test_complete_alias_definition(self):
        """Test that single-line @alias definition is complete."""
        repl = MMLRepl()
        text = '@alias preset pc.{channel}.{num} "Load preset"'

        complete, result = repl.try_parse(text)

        assert complete is True
        assert isinstance(result, MMDDocument)

    def test_complete_import_statement(self):
        """Test that @import statement is complete and valid."""
        repl = MMLRepl()
        text = '@import "devices/quad_cortex.mmd"'

        complete, result = repl.try_parse(text)

        assert complete is True
        assert isinstance(result, MMDDocument)

    def test_complete_loop_block(self):
        """Test that complete @loop block parses successfully."""
        repl = MMLRepl()
        text = "@loop 3 times every 1b\n- pc 1.10\n@end"

        complete, result = repl.try_parse(text)

        assert complete is True
        assert isinstance(result, MMDDocument)

    def test_complete_empty_input(self):
        """Test that empty input is considered complete."""
        repl = MMLRepl()
        text = ""

        complete, result = repl.try_parse(text)

        assert complete is True
        assert isinstance(result, MMDDocument)


@pytest.mark.unit
class TestTryParseErrors:
    """Test try_parse() with complete but invalid input."""

    def test_invalid_define_variable_name(self):
        """Test that invalid variable name returns complete with exception."""
        repl = MMLRepl()
        text = "@define velocity 80"  # Variables must be uppercase

        complete, result = repl.try_parse(text)

        assert complete is True
        assert isinstance(result, Exception)

    def test_invalid_loop_syntax(self):
        """Test that invalid loop syntax returns complete with exception."""
        repl = MMLRepl()
        text = "@loop invalid\n@end"

        complete, result = repl.try_parse(text)

        assert complete is True
        assert isinstance(result, Exception)

    def test_missing_import_quotes(self):
        """Test that missing quotes in import returns exception."""
        repl = MMLRepl()
        text = "@import devices/test.mmd"  # Missing quotes

        complete, result = repl.try_parse(text)

        assert complete is True
        assert isinstance(result, Exception)


@pytest.mark.unit
class TestIsComplete:
    """Test is_complete() convenience method."""

    def test_is_complete_single_line(self):
        """Test that single-line statement returns True."""
        repl = MMLRepl()

        assert repl.is_complete("@define VELOCITY 80") is True

    def test_is_complete_incomplete_block(self):
        """Test that incomplete block returns False."""
        repl = MMLRepl()

        assert repl.is_complete("@loop 3 times every 1b") is False

    def test_is_complete_complete_block(self):
        """Test that complete block returns True."""
        repl = MMLRepl()

        assert repl.is_complete("@loop 3 times every 1b\n- pc 1.10\n@end") is True

    def test_is_complete_syntax_error(self):
        """Test that syntax error still returns True (complete but invalid)."""
        repl = MMLRepl()

        assert repl.is_complete("@loop invalid\n@end") is True

    def test_is_complete_empty_input(self):
        """Test that empty input is considered complete."""
        repl = MMLRepl()

        assert repl.is_complete("") is True


@pytest.mark.unit
class TestReset:
    """Test REPL reset functionality."""

    def test_reset_clears_state_variables(self):
        """Test that reset clears all state variables."""
        repl = MMLRepl()
        repl.state.variables["VELOCITY"] = 80
        repl.state.variables["CHANNEL"] = 1

        repl.reset()

        assert repl.state.variables == {}

    def test_reset_clears_state_aliases(self):
        """Test that reset clears all state aliases."""
        repl = MMLRepl()
        repl.state.aliases["test"] = {"name": "test"}

        repl.reset()

        assert repl.state.aliases == {}

    def test_reset_restores_state_defaults(self):
        """Test that reset restores default tempo and resolution."""
        repl = MMLRepl()
        repl.state.tempo = 140
        repl.state.resolution = 960

        repl.reset()

        assert repl.state.tempo == 120
        assert repl.state.resolution == 480

    def test_reset_clears_buffer(self):
        """Test that reset clears the input buffer."""
        repl = MMLRepl()
        repl.buffer.append("@loop 3 times every 1b")
        repl.buffer.append("- pc 1.10")

        repl.reset()

        assert repl.buffer == []

    def test_reset_preserves_parser(self):
        """Test that reset doesn't replace the parser instance."""
        repl = MMLRepl()
        parser_id = id(repl.parser)

        repl.reset()

        assert id(repl.parser) == parser_id


@pytest.mark.unit
class TestMultiLineWorkflow:
    """Test realistic multi-line input workflows."""

    def test_build_loop_incrementally(self):
        """Test building a loop block line by line."""
        repl = MMLRepl()

        # Start with loop declaration
        complete, _ = repl.try_parse("@loop 4 times every 1b")
        assert complete is False

        # Add command line
        complete, _ = repl.try_parse("@loop 4 times every 1b\n- pc 1.10")
        assert complete is False

        # Complete with @end
        complete, result = repl.try_parse("@loop 4 times every 1b\n- pc 1.10\n@end")
        assert complete is True
        assert isinstance(result, MMDDocument)

    def test_multiple_statements(self):
        """Test that multiple complete statements parse correctly."""
        repl = MMLRepl()

        text = """@define VELOCITY 80
@define CHANNEL 1
@alias preset pc.{ch}.{num} "Preset"
"""
        complete, result = repl.try_parse(text)
        assert complete is True
        assert isinstance(result, MMDDocument)


@pytest.mark.unit
class TestEvaluateDefine:
    """Test evaluate() method with @define statements."""

    def test_evaluate_single_define(self):
        """Test that @define updates state.variables."""
        repl = MMLRepl()
        doc = repl.parser.parse_string("@define VELOCITY 80")

        repl.evaluate(doc)

        assert repl.state.variables["VELOCITY"] == 80

    def test_evaluate_multiple_defines(self):
        """Test that multiple @define statements update state."""
        repl = MMLRepl()
        doc = repl.parser.parse_string("""
@define VELOCITY 80
@define CHANNEL 1
@define PRESET 10
""")

        repl.evaluate(doc)

        assert repl.state.variables["VELOCITY"] == 80
        assert repl.state.variables["CHANNEL"] == 1
        assert repl.state.variables["PRESET"] == 10

    def test_evaluate_define_overwrites_existing(self):
        """Test that @define overwrites existing variable."""
        repl = MMLRepl()
        repl.state.variables["VELOCITY"] = 50

        doc = repl.parser.parse_string("@define VELOCITY 100")
        repl.evaluate(doc)

        assert repl.state.variables["VELOCITY"] == 100


@pytest.mark.unit
class TestEvaluateAlias:
    """Test evaluate() method with @alias definitions."""

    def test_evaluate_single_line_alias(self):
        """Test that single-line alias is registered in state."""
        repl = MMLRepl()
        doc = repl.parser.parse_string('@alias preset pc.{ch}.{num} "Load preset"')

        repl.evaluate(doc)

        assert "preset" in repl.state.aliases
        assert repl.state.aliases["preset"].name == "preset"

    def test_evaluate_multi_command_alias(self):
        """Test that multi-command alias block is registered."""
        repl = MMLRepl()
        doc = repl.parser.parse_string("""
@alias cortex_load {ch} {setlist} {group} {preset} "Load preset"
  - cc {ch}.32.{setlist}
  - cc {ch}.0.{group}
  - pc {ch}.{preset}
@end
""")

        repl.evaluate(doc)

        assert "cortex_load" in repl.state.aliases
        alias = repl.state.aliases["cortex_load"]
        assert len(alias.parameters) == 4

    def test_evaluate_multiple_aliases(self):
        """Test that multiple aliases are all registered."""
        repl = MMLRepl()
        doc = repl.parser.parse_string("""
@alias preset pc.{ch}.{num} "Preset"
@alias volume cc.{ch}.7.{val} "Volume"
@alias mix cc.{ch}.84.{val} "Mix"
""")

        repl.evaluate(doc)

        assert "preset" in repl.state.aliases
        assert "volume" in repl.state.aliases
        assert "mix" in repl.state.aliases


@pytest.mark.unit
class TestEvaluateFrontmatter:
    """Test evaluate() method with frontmatter."""

    def test_evaluate_tempo_frontmatter(self):
        """Test that tempo in frontmatter updates state."""
        repl = MMLRepl()
        doc = repl.parser.parse_string("""---
tempo: 140
---
""")

        repl.evaluate(doc)

        assert repl.state.tempo == 140

    def test_evaluate_ppq_frontmatter(self):
        """Test that ppq in frontmatter updates state."""
        repl = MMLRepl()
        doc = repl.parser.parse_string("""---
ppq: 960
---
""")

        repl.evaluate(doc)

        assert repl.state.resolution == 960

    def test_evaluate_time_signature_frontmatter(self):
        """Test that time_signature in frontmatter updates state."""
        repl = MMLRepl()
        doc = repl.parser.parse_string("""---
time_signature: "3/4"
---
""")

        repl.evaluate(doc)

        assert repl.state.time_signature == (3, 4)

    def test_evaluate_all_frontmatter_fields(self):
        """Test that all frontmatter fields update state together."""
        repl = MMLRepl()
        doc = repl.parser.parse_string("""---
tempo: 90
ppq: 480
time_signature: "6/8"
---
""")

        repl.evaluate(doc)

        assert repl.state.tempo == 90
        assert repl.state.resolution == 480
        assert repl.state.time_signature == (6, 8)


@pytest.mark.unit
class TestEvaluateEvents:
    """Test evaluate() method with MIDI events."""

    def test_evaluate_single_event(self):
        """Test that single MIDI event compiles to IR."""
        repl = MMLRepl()
        doc = repl.parser.parse_string("""
[00:00.000]
- cc 1.7.64
""")

        repl.evaluate(doc)

        assert repl.state.last_ir is not None
        assert repl.state.last_ir.event_count > 0

    def test_evaluate_multiple_events(self):
        """Test that multiple events compile correctly."""
        repl = MMLRepl()
        doc = repl.parser.parse_string("""
[00:00.000]
- cc 1.7.64
- pc 1.10

[00:01.000]
- cc 1.7.127
""")

        repl.evaluate(doc)

        assert repl.state.last_ir is not None
        assert repl.state.last_ir.event_count >= 3

    def test_evaluate_events_with_ppq(self):
        """Test that events compile using state.resolution."""
        repl = MMLRepl()
        repl.state.resolution = 960

        doc = repl.parser.parse_string("""
[00:00.000]
- cc 1.7.64
""")

        repl.evaluate(doc)

        assert repl.state.last_ir is not None


@pytest.mark.unit
class TestEvaluatePersistence:
    """Test state persistence across multiple evaluate() calls."""

    def test_variables_persist_across_calls(self):
        """Test that variables defined in one call persist to next."""
        repl = MMLRepl()

        # First call: define variable
        doc1 = repl.parser.parse_string("@define VELOCITY 80")
        repl.evaluate(doc1)

        # Second call: define another variable
        doc2 = repl.parser.parse_string("@define CHANNEL 1")
        repl.evaluate(doc2)

        # Both should be present
        assert repl.state.variables["VELOCITY"] == 80
        assert repl.state.variables["CHANNEL"] == 1

    def test_aliases_persist_across_calls(self):
        """Test that aliases defined in one call persist to next."""
        repl = MMLRepl()

        # First call: define alias
        doc1 = repl.parser.parse_string('@alias preset pc.{ch}.{num} "Preset"')
        repl.evaluate(doc1)

        # Second call: define another alias
        doc2 = repl.parser.parse_string('@alias volume cc.{ch}.7.{val} "Volume"')
        repl.evaluate(doc2)

        # Both should be present
        assert "preset" in repl.state.aliases
        assert "volume" in repl.state.aliases

    def test_last_ir_updated_each_call(self):
        """Test that last_ir is replaced on each evaluate with events."""
        repl = MMLRepl()

        # First compilation
        doc1 = repl.parser.parse_string("[00:00.000]\n- cc 1.7.64")
        repl.evaluate(doc1)
        first_ir = repl.state.last_ir

        # Second compilation
        doc2 = repl.parser.parse_string("[00:00.000]\n- cc 1.7.127")
        repl.evaluate(doc2)
        second_ir = repl.state.last_ir

        # Should be different IR objects
        assert first_ir is not second_ir


@pytest.mark.unit
class TestEvaluateEmpty:
    """Test evaluate() method with empty or minimal documents."""

    def test_evaluate_empty_document(self):
        """Test that empty document doesn't crash."""
        repl = MMLRepl()
        doc = repl.parser.parse_string("")

        repl.evaluate(doc)

        # State should remain unchanged
        assert repl.state.variables == {}
        assert repl.state.aliases == {}
        assert repl.state.last_ir is None

    def test_evaluate_only_comments(self):
        """Test that document with only comments is handled."""
        repl = MMLRepl()
        doc = repl.parser.parse_string("""
# This is a comment
# Another comment
""")

        repl.evaluate(doc)

        assert repl.state.last_ir is None

    def test_evaluate_only_frontmatter(self):
        """Test that document with only frontmatter updates state."""
        repl = MMLRepl()
        doc = repl.parser.parse_string("""---
tempo: 100
---
""")

        repl.evaluate(doc)

        assert repl.state.tempo == 100
        assert repl.state.last_ir is None


@pytest.mark.unit
class TestErrorHandling:
    """Test handle_error() method and error display."""

    def test_handle_parse_error_unexpected_token(self, capsys):
        """Test that parse errors display formatted message without crashing."""
        from lark.exceptions import UnexpectedToken
        from lark.lexer import Token

        repl = MMLRepl()
        source_text = "- invalid_command"

        # Create a mock UnexpectedToken error by setting attributes
        token = Token("INVALID", "invalid_command")
        error = UnexpectedToken(token=token, expected={"CMD_CC", "CMD_PC", "CMD_NOTE_ON"})
        error.line = 1
        error.column = 3

        # Should not raise exception
        repl.handle_error(error, source_text)

        # Verify output contains error message
        captured = capsys.readouterr()
        assert "error[E101]" in captured.out
        assert "Unexpected token" in captured.out
        assert "REPL state preserved" in captured.out

    def test_handle_parse_error_unexpected_char(self, capsys):
        """Test that unexpected character errors are handled."""
        from lark.exceptions import UnexpectedCharacters

        repl = MMLRepl()
        source_text = "- cc 1.10.@"

        # Create a mock UnexpectedCharacters error
        error = UnexpectedCharacters(
            seq=source_text,
            lex_pos=10,
            line=1,
            column=11,
            allowed=None,
            considered_tokens=None,
        )
        error.char = "@"

        # Should not raise exception
        repl.handle_error(error, source_text)

        captured = capsys.readouterr()
        assert "error[E102]" in captured.out
        assert "Unexpected character" in captured.out
        assert "REPL state preserved" in captured.out

    def test_handle_validation_error(self, capsys):
        """Test that validation errors display formatted message."""
        from midi_markdown.utils.validation import ValidationError

        repl = MMLRepl()
        source_text = "- cc 17.10.64"

        # Create a mock ValidationError
        error = ValidationError("Invalid MIDI channel: 17")
        error.error_code = "E204"
        error.line = 1
        error.column = 6
        error.suggestion = "Channels must be 1-16"

        # Should not raise exception
        repl.handle_error(error, source_text)

        captured = capsys.readouterr()
        assert "error[E204]" in captured.out
        assert "Invalid MIDI channel" in captured.out
        assert "Channels must be 1-16" in captured.out
        assert "REPL state preserved" in captured.out

    def test_handle_expansion_error_undefined_variable(self, capsys):
        """Test that undefined variable errors are handled."""
        from midi_markdown.expansion.errors import UndefinedVariableError

        repl = MMLRepl()

        # Create a mock UndefinedVariableError (use correct signature)
        error = UndefinedVariableError("velocity", similar_names=["vel", "value"])

        # Should not raise exception
        repl.handle_error(error)

        captured = capsys.readouterr()
        assert "error[E301]" in captured.out
        assert "velocity" in captured.out
        assert "Did you mean" in captured.out
        assert "REPL state preserved" in captured.out

    def test_handle_import_error_file_not_found(self, capsys):
        """Test that file not found errors are handled gracefully."""
        repl = MMLRepl()

        # Create a FileNotFoundError
        error = FileNotFoundError("No such file or directory: 'devices/missing.mmd'")

        # Should not raise exception
        repl.handle_error(error)

        captured = capsys.readouterr()
        assert "error[E401]" in captured.out
        assert "File not found" in captured.out
        assert "REPL state preserved" in captured.out

    def test_handle_generic_error(self, capsys):
        """Test that unknown exceptions are caught and displayed."""
        repl = MMLRepl()

        # Create a generic exception
        error = RuntimeError("Something went wrong")

        # Should not raise exception
        repl.handle_error(error)

        captured = capsys.readouterr()
        assert "Error" in captured.out
        assert "RuntimeError" in captured.out
        assert "Something went wrong" in captured.out
        assert "REPL state preserved" in captured.out

    def test_error_preserves_repl_state(self):
        """Test that state is unchanged after error handling."""
        from lark.exceptions import UnexpectedToken
        from lark.lexer import Token

        repl = MMLRepl()

        # Set up REPL state
        repl.state.variables["VELOCITY"] = 80
        repl.state.variables["CHANNEL"] = 1
        repl.state.aliases["test"] = {"name": "test"}

        # Trigger error
        token = Token("INVALID", "invalid")
        error = UnexpectedToken(token=token, expected=set())
        error.line = 1
        error.column = 1

        repl.handle_error(error, "- invalid")

        # Verify state unchanged
        assert repl.state.variables["VELOCITY"] == 80
        assert repl.state.variables["CHANNEL"] == 1
        assert "test" in repl.state.aliases

    def test_handle_error_never_raises(self):
        """Test that handle_error() never raises exceptions."""
        from lark.exceptions import UnexpectedToken
        from lark.lexer import Token

        repl = MMLRepl()

        # Create various errors and verify none crash
        token_error = UnexpectedToken(token=Token("INVALID", "x"), expected=set())
        token_error.line = 1
        token_error.column = 1

        errors = [
            token_error,
            ValueError("Test error"),
            RuntimeError("Test runtime error"),
            Exception("Generic exception"),
        ]

        for error in errors:
            # Should not raise - wrap in try/except to be extra safe
            try:
                repl.handle_error(error, "test input")
            except Exception as e:
                pytest.fail(f"handle_error() raised {type(e).__name__}: {e}")

    def test_handle_error_with_multiline_source(self, capsys):
        """Test error display with multi-line source text."""
        from lark.exceptions import UnexpectedToken
        from lark.lexer import Token

        repl = MMLRepl()
        source_text = """@define VELOCITY 80
- cc 1.10.64
- invalid_cmd
"""

        # Error on line 3
        token = Token("INVALID", "invalid_cmd")
        error = UnexpectedToken(token=token, expected=set())
        error.line = 3
        error.column = 3

        repl.handle_error(error, source_text)

        captured = capsys.readouterr()
        assert "error[E101]" in captured.out
        assert "3 │" in captured.out  # Shows line 3
        assert "invalid_cmd" in captured.out
        assert "REPL state preserved" in captured.out

    def test_handle_error_without_source_text(self, capsys):
        """Test error display when no source text provided."""
        from midi_markdown.utils.validation import ValidationError

        repl = MMLRepl()

        # Error without source context
        error = ValidationError("Invalid value")
        error.error_code = "E201"

        repl.handle_error(error)  # No source_text

        captured = capsys.readouterr()
        assert "error[E201]" in captured.out
        assert "Invalid value" in captured.out
        assert "REPL state preserved" in captured.out
