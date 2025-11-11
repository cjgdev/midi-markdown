"""Pytest configuration and fixtures for benchmarks."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def small_mmd_file() -> Path:
    """Path to small MMD file (<100 events)."""
    return Path("benchmarks/fixtures/small_file.mmd")


@pytest.fixture
def medium_mmd_file() -> Path:
    """Path to medium MMD file (100-500 events)."""
    return Path("benchmarks/fixtures/medium_file.mmd")


@pytest.fixture
def large_mmd_file() -> Path:
    """Path to large MMD file (>1000 events)."""
    return Path("benchmarks/fixtures/large_file.mmd")


@pytest.fixture
def parsed_small_document(small_mmd_file):
    """Parse small MMD file and return AST."""
    from midi_markdown.parser.parser import MMDParser

    parser = MMDParser()
    return parser.parse_file(str(small_mmd_file))


@pytest.fixture
def parsed_medium_document(medium_mmd_file):
    """Parse medium MMD file and return AST."""
    from midi_markdown.parser.parser import MMDParser

    parser = MMDParser()
    return parser.parse_file(str(medium_mmd_file))


@pytest.fixture
def parsed_large_document(large_mmd_file):
    """Parse large MMD file and return AST."""
    from midi_markdown.parser.parser import MMDParser

    parser = MMDParser()
    return parser.parse_file(str(large_mmd_file))


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
