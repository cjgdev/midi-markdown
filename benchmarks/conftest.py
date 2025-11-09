"""Pytest configuration and fixtures for benchmarks."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def small_mml_file() -> Path:
    """Path to small MML file (<100 events)."""
    return Path("benchmarks/fixtures/small_file.mml")


@pytest.fixture
def medium_mml_file() -> Path:
    """Path to medium MML file (100-500 events)."""
    return Path("benchmarks/fixtures/medium_file.mml")


@pytest.fixture
def large_mml_file() -> Path:
    """Path to large MML file (>1000 events)."""
    return Path("benchmarks/fixtures/large_file.mml")


@pytest.fixture
def parsed_small_document(small_mml_file):
    """Parse small MML file and return AST."""
    from midi_markdown.parser.parser import MMLParser

    parser = MMLParser()
    return parser.parse_file(str(small_mml_file))


@pytest.fixture
def parsed_medium_document(medium_mml_file):
    """Parse medium MML file and return AST."""
    from midi_markdown.parser.parser import MMLParser

    parser = MMLParser()
    return parser.parse_file(str(medium_mml_file))


@pytest.fixture
def parsed_large_document(large_mml_file):
    """Parse large MML file and return AST."""
    from midi_markdown.parser.parser import MMLParser

    parser = MMLParser()
    return parser.parse_file(str(large_mml_file))


@pytest.fixture
def small_ir_program(parsed_small_document):
    """Compile small document to IR."""
    from midi_markdown.core.compiler import compile_ast_to_ir

    return compile_ast_to_ir(parsed_small_document, ppq=480)


@pytest.fixture
def medium_ir_program(parsed_medium_document):
    """Compile medium document to IR."""
    from midi_markdown.core.compiler import compile_ast_to_ir

    return compile_ast_to_ir(parsed_medium_document, ppq=480)


@pytest.fixture
def large_ir_program(parsed_large_document):
    """Compile large document to IR."""
    from midi_markdown.core.compiler import compile_ast_to_ir

    return compile_ast_to_ir(parsed_large_document, ppq=480)
