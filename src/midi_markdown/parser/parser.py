"""
MIDI Markup Language (MML) Parser Class

Provides the main MMLParser class that uses Lark and MMLTransformer
to parse MML files into structured MMLDocument objects.
"""

from __future__ import annotations

from pathlib import Path

from lark import Lark

from .ast_nodes import MMLDocument
from .transformer import MMLTransformer

# ============================================================================
# Parser Class
# ============================================================================


class MMLParser:
    """
    Main parser class for MIDI Markup Language.

    Usage:
        parser = MMLParser()
        document = parser.parse_file('song.mml')
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
            grammar_path = Path(__file__).parent / "mml.lark"
            with open(grammar_path) as f:
                grammar = f.read()

        self.parser = Lark(
            grammar,
            parser="lalr",  # LALR parser for speed
            transformer=MMLTransformer(),
            start="document",
            propagate_positions=True,  # Track line/column numbers
            maybe_placeholders=False,
        )

    def parse_file(self, filepath: str | Path) -> MMLDocument:
        """
        Parse an MML file.

        Args:
            filepath: Path to the .mml file

        Returns:
            MMLDocument object containing the parsed content
        """
        with open(filepath, encoding="utf-8") as f:
            content = f.read()

        return self.parse_string(content, str(filepath))

    def parse_string(self, content: str, filename: str = "<string>") -> MMLDocument:
        """
        Parse MML content from a string.

        Args:
            content: MML markup content
            filename: Name for error reporting

        Returns:
            MMLDocument object
        """
        try:
            result = self.parser.parse(content)
            # The transformer should return an MMLDocument
            if isinstance(result, MMLDocument):
                return result
            raise ValueError(f"Parser did not return MMLDocument, got {type(result)}")
        except Exception as e:
            self._format_parse_error(e, content, filename)
            raise

    def _format_parse_error(self, error, content: str, filename: str):
        """Format a parse error with context"""
        # Extract line information if available
        if hasattr(error, "line") and hasattr(error, "column"):
            lines = content.split("\n")
            error_line = lines[error.line - 1] if error.line <= len(lines) else ""

            print(f"\nError: Parse error at line {error.line}:{error.column} in {filename}")
            print(f"  {error_line}")
            print(f"  {' ' * (error.column - 1)}^")
            print(f"\n{error}")


# ============================================================================
# Public API
# ============================================================================


def parse_mml_file(filepath: str | Path) -> MMLDocument:
    """
    Convenience function to parse an MML file.

    Args:
        filepath: Path to the .mml file

    Returns:
        MMLDocument object
    """
    parser = MMLParser()
    return parser.parse_file(filepath)


def parse_mml_string(content: str) -> MMLDocument:
    """
    Convenience function to parse MML content from a string.

    Args:
        content: MML markup content

    Returns:
        MMLDocument object
    """
    parser = MMLParser()
    return parser.parse_string(content)
