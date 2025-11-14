"""
MIDI Markup Language (MML) Parser Class

Provides the main MMDParser class that uses Lark and MMDTransformer
to parse MML files into structured MMDDocument objects.
"""

from __future__ import annotations

from pathlib import Path

from lark import Lark

from .ast_nodes import MMDDocument
from .transformer import MMDTransformer

# ============================================================================
# Parser Class
# ============================================================================


class MMDParser:
    """
    Main parser class for MIDI Markup Language.

    Usage:
        parser = MMDParser()
        document = parser.parse_file('song.mmd')
        # or
        document = parser.parse_string(mml_content)
    """

    def __init__(self, grammar_file: str | None = None):
        """
        Initialize the parser with the grammar.

        Args:
            grammar_file: Path to the .lark grammar file.
                         If None, uses the grammar from the parser package.
        """
        if grammar_file:
            with open(grammar_file) as f:
                grammar = f.read()
        else:
            # Use grammar from the parser package
            grammar_path = Path(__file__).parent / "mmd.lark"
            with open(grammar_path) as f:
                grammar = f.read()

        self.parser = Lark(
            grammar,
            parser="lalr",  # LALR parser for speed
            transformer=MMDTransformer(),
            start="document",
            propagate_positions=True,  # Track line/column numbers
            maybe_placeholders=False,
        )

    def parse_file(self, filepath: str | Path) -> MMDDocument:
        """
        Parse an MMD file.

        Args:
            filepath: Path to the .mmd file

        Returns:
            MMDDocument object containing the parsed content
        """
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        return self.parse_string(content, str(filepath))

    def parse_string(self, content: str, filename: str = "<string>") -> MMDDocument:
        """
        Parse MML content from a string.

        Args:
            content: MMD markup content
            filename: Name for error reporting

        Returns:
            MMDDocument object
        """
        try:
            result = self.parser.parse(content)
            # The transformer should return an MMDDocument
            if isinstance(result, MMDDocument):
                return result
            msg = f"Parser did not return MMDDocument, got {type(result)}"
            raise ValueError(msg)
        except Exception as e:
            self._format_parse_error(e, content, filename)
            raise

    def parse_interactive(self, text: str) -> tuple[bool, MMDDocument | Exception | None]:
        """Parse MML text for REPL, handling incomplete input.

        This method supports interactive parsing where input may be incomplete
        (e.g., user is still typing). It distinguishes between:
        - Incomplete input: Need more text (returns False, None)
        - Invalid but complete: Syntax error (returns True, Exception)
        - Valid and complete: Success (returns True, MMDDocument)

        Args:
            text: MML source text (may be incomplete)

        Returns:
            Tuple of (complete, result):
            - (False, None): Input incomplete, need more
            - (True, Exception): Input complete but invalid
            - (True, MMDDocument): Input complete and valid

        Example:
            >>> parser = MMDParser()
            >>> complete, result = parser.parse_interactive("[00:01.0")
            >>> assert not complete  # Incomplete timing marker
            >>> complete, result = parser.parse_interactive("[00:01.000]\\n- cc 1.7.64")
            >>> assert complete and isinstance(result, MMDDocument)
        """
        from lark import UnexpectedEOF, UnexpectedInput, UnexpectedToken

        try:
            doc = self.parse_string(text)
            return True, doc
        except UnexpectedEOF:
            # Need more input
            return False, None
        except UnexpectedToken as e:
            # Check if this is incomplete input (unexpected end of input)
            # Lark signals end-of-input with token type '$END' or empty token
            if e.token is None or e.token.type in {"$END", ""}:
                return False, None
            # Otherwise it's a complete but invalid input
            return True, e
        except UnexpectedInput as e:
            # Complete but invalid (other Lark parse errors)
            return True, e
        except Exception as e:
            # Other errors (file not found, etc.)
            return True, e

    def _format_parse_error(self, error, content: str, filename: str):
        """Format a parse error with context"""
        # Extract line information if available
        if hasattr(error, "line") and hasattr(error, "column"):
            lines = content.split("\n")
            lines[error.line - 1] if error.line <= len(lines) else ""


# ============================================================================
# Public API
# ============================================================================


def parse_mmd_file(filepath: str | Path) -> MMDDocument:
    """
    Convenience function to parse an MML file.

    Args:
        filepath: Path to the .mmd file

    Returns:
        MMDDocument object
    """
    parser = MMDParser()
    return parser.parse_file(filepath)


def parse_mmd_string(content: str) -> MMDDocument:
    """
    Convenience function to parse MML content from a string.

    Args:
        content: MMD markup content

    Returns:
        MMDDocument object
    """
    parser = MMDParser()
    return parser.parse_string(content)
