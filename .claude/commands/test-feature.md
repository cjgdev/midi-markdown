---
description: Find and run tests related to a specific feature or component
---

Smart test runner that finds and executes tests for a specific feature or component.

Ask the user what they want to test (e.g., "loops", "pitch_bend", "aliases", "timing").

Then:

## 1. Identify Relevant Tests

Search for tests related to the feature:
- Use `grep` to find test files mentioning the feature
- Look in `tests/unit/` for unit tests
- Look in `tests/integration/` for integration tests
- Check `tests/fixtures/` for test data

## 2. Categorize Test Types

**Unit tests** (fast, isolated):
- `tests/unit/test_parser.py` - Parsing tests
- `tests/unit/test_transformer.py` - AST transformation
- `tests/unit/test_loops.py` - Loop expansion
- `tests/unit/test_sweeps.py` - Sweep expansion
- `tests/unit/test_variables.py` - Variable resolution
- `tests/unit/test_alias_resolver.py` - Alias expansion

**Integration tests** (multi-component):
- `tests/integration/test_cli.py` - CLI commands
- `tests/integration/test_end_to_end.py` - Full compilation
- `tests/integration/test_device_libraries.py` - Device libraries
- `tests/integration/test_complex_documents.py` - Complex features

**E2E tests** (complete pipeline):
- `tests/integration/test_end_to_end.py` - Full examples

## 3. Run Tests

Execute tests in priority order:

```bash
# Run unit tests first (fastest)
just test-k {feature_name}

# Run specific test file
just test-file tests/unit/test_{feature}.py

# Run integration tests
just test-integration

# Run with verbose output
pytest tests/ -k {feature_name} -v
```

## 4. Show Coverage

After running tests, show coverage for the feature:

```bash
pytest tests/ -k {feature_name} --cov=src/midi_markdown --cov-report=term
```

## 5. Suggest Additional Tests

Based on the feature, suggest test cases that might be missing:
- Edge cases (min/max values)
- Error conditions (invalid input)
- Integration tests (full pipeline)
- Examples that use the feature

## Feature → Test Mapping:

| Feature | Unit Tests | Integration Tests | Examples |
|---------|------------|-------------------|----------|
| **Loops** | test_loops.py | test_end_to_end.py | 03_advanced/01_loops_and_patterns.mmd |
| **Sweeps** | test_sweeps.py | test_end_to_end.py | 03_advanced/02_sweep_automation.mmd |
| **Aliases** | test_alias_resolver.py | test_device_libraries.py | 03_advanced/03_alias_showcase.mmd |
| **Timing** | test_parser.py, test_expander.py | test_timing_calculations.py | 01_timing/* |
| **Variables** | test_variables.py | test_end_to_end.py | 03_advanced/09_generative_pattern.mmd |
| **Notes** | test_parser.py, test_transformer.py | test_end_to_end.py | 00_basics/01_hello_world.mmd |
| **CC** | test_transformer.py | test_cli.py | 02_midi_features/02_cc_automation.mmd |
| **Pitch Bend** | test_transformer.py | test_end_to_end.py | 02_midi_features/03_pitch_bend_pressure.mmd |

## Common Test Commands:

```bash
# Run all tests for a feature
pytest -k "loop" -v

# Run tests and stop on first failure
pytest -k "loop" -x

# Run tests with detailed output
pytest -k "loop" -vv --tb=long

# Run specific test method
pytest tests/unit/test_loops.py::TestLoops::test_basic_loop -v

# Run all unit tests
just test-unit

# Run smoke tests (fastest)
just smoke
```

After running tests, show:
- ✅ Passed count
- ❌ Failed count
- ⚠️ Skipped count
- 📊 Coverage percentage
- 💡 Suggestions for additional test coverage
