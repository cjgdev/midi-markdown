"""Shared pytest fixtures for MIDI Markdown tests."""

from pathlib import Path

import pytest

from midi_markdown.alias.resolver import AliasResolver
from midi_markdown.expansion.expander import CommandExpander

# EventGenerator removed - tests now use CommandExpander directly
from midi_markdown.parser.parser import MMDParser
from midi_markdown.utils.validation.timing_validator import TimingValidator


def pytest_collection_modifyitems(items):
    """Automatically add markers to tests based on their location and name.

    This hook runs after test collection and adds appropriate markers:
    - @pytest.mark.unit for tests in tests/unit/
    - @pytest.mark.integration for tests in tests/integration/
    - Domain-specific markers based on filename patterns
    """
    for item in items:
        # Add unit/integration markers based on directory
        test_path = str(item.fspath)
        if "/unit/" in test_path:
            item.add_marker(pytest.mark.unit)
        elif "/integration/" in test_path:
            item.add_marker(pytest.mark.integration)

        # Add domain-specific markers based on filename
        node_id = item.nodeid
        if "test_alias" in node_id:
            item.add_marker(pytest.mark.alias)
        elif "test_parser" in node_id or "test_lexer" in node_id:
            item.add_marker(pytest.mark.parser)
        elif "test_expander" in node_id or "test_expansion" in node_id:
            item.add_marker(pytest.mark.expansion)
        elif "test_midi" in node_id or "test_generator" in node_id or "test_events" in node_id:
            item.add_marker(pytest.mark.midi)
        elif "test_validation" in node_id or "test_validator" in node_id:
            item.add_marker(pytest.mark.validation)
        elif "test_timing" in node_id:
            item.add_marker(pytest.mark.timing)
        elif "test_sweep" in node_id:
            item.add_marker(pytest.mark.sweeps)
        elif "test_loop" in node_id:
            item.add_marker(pytest.mark.loops)
        elif "test_variable" in node_id:
            item.add_marker(pytest.mark.variables)

        # Mark slow tests (can be extended as needed)
        if "test_performance" in node_id or "test_many" in node_id:
            item.add_marker(pytest.mark.slow)


@pytest.fixture
def fixtures_dir() -> Path:
    """Return path to test fixtures directory.

    Returns:
        Path to fixtures directory
    """
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def valid_fixtures_dir(fixtures_dir: Path) -> Path:
    """Return path to valid MML fixtures.

    Returns:
        Path to valid fixtures directory
    """
    return fixtures_dir / "valid"


@pytest.fixture
def invalid_fixtures_dir(fixtures_dir: Path) -> Path:
    """Return path to invalid MML fixtures.

    Returns:
        Path to invalid fixtures directory
    """
    return fixtures_dir / "invalid"


@pytest.fixture
def basic_mml(valid_fixtures_dir: Path) -> str:
    """Load basic valid MML file.

    Returns:
        Contents of basic.mmd
    """
    return (valid_fixtures_dir / "basic.mmd").read_text()


@pytest.fixture
def invalid_mml(invalid_fixtures_dir: Path) -> str:
    """Load invalid MML file for error testing.

    Returns:
        Contents of syntax_error.mmd
    """
    return (invalid_fixtures_dir / "syntax_error.mmd").read_text()


@pytest.fixture
def sample_tokens() -> list[dict[str, any]]:
    """Provide sample tokens for parser testing.

    Returns:
        List of sample token dictionaries
    """
    return [
        {"type": "DASH", "value": "-", "line": 1, "column": 1},
        {"type": "IDENTIFIER", "value": "pc", "line": 1, "column": 3},
        {"type": "NUMBER", "value": "1", "line": 1, "column": 6},
        {"type": "DOT", "value": ".", "line": 1, "column": 7},
        {"type": "NUMBER", "value": "5", "line": 1, "column": 8},
    ]


@pytest.fixture(scope="session")
def parser() -> MMDParser:
    """Provide MML parser instance.

    This is the most commonly used fixture across all tests.
    Previously duplicated in 43+ test files, now centralized here.

    Session-scoped for performance since MMDParser is stateless.
    Each test still gets isolated parsing results.

    Returns:
        Reusable MMDParser instance for entire test session
    """
    return MMDParser()


@pytest.fixture
def resolve_aliases():
    """Provide helper function to resolve alias calls in document events.

    This helper was previously duplicated in 7+ test files.
    Now centralized as a reusable fixture.

    Returns:
        Function that takes a document and resolves all alias calls
    """

    def _resolve_aliases(doc):
        """Resolve all alias calls in document events."""
        alias_resolver = AliasResolver(doc.aliases if doc.aliases else {})
        resolved_events = []

        for event in doc.events:
            if isinstance(event, dict) and event.get("type") == "timed_event":
                commands = event.get("commands", [])
                resolved_commands = []

                for cmd in commands:
                    if hasattr(cmd, "type") and cmd.type == "alias_call":
                        alias_name = cmd.params.get("alias_name", "")
                        args = cmd.params.get("args", [])
                        timing = event.get("timing")
                        source_line = cmd.source_line

                        expanded_commands = alias_resolver.resolve(
                            alias_name=alias_name,
                            arguments=args,
                            timing=timing,
                            source_line=source_line,
                        )
                        resolved_commands.extend(expanded_commands)
                    else:
                        resolved_commands.append(cmd)

                event["commands"] = resolved_commands
                resolved_events.append(event)
            else:
                resolved_events.append(event)

        return resolved_events

    return _resolve_aliases


@pytest.fixture
def expander() -> CommandExpander:
    """Provide CommandExpander instance.

    Commonly used fixture for expansion tests.
    Previously duplicated in 7+ test files.

    Function-scoped (not session) because CommandExpander has mutable state
    (current_time, events, stats, symbol_table).

    Returns:
        Fresh CommandExpander instance with default settings for each test
    """
    return CommandExpander(source_file="test.mmd")


@pytest.fixture
def validator() -> TimingValidator:
    """Provide TimingValidator instance.

    Commonly used fixture for timing validation tests.
    Previously duplicated in 9+ test files.

    Function-scoped (not session) because TimingValidator has mutable state
    (errors, last_absolute_time, has_tempo, has_time_signature).

    Returns:
        Fresh TimingValidator instance for each test
    """
    return TimingValidator()


# event_generator fixture removed - EventGenerator class deleted
# Tests now use CommandExpander directly for event generation
