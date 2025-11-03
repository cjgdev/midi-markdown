# Test Fixtures

This directory contains focused test fixtures for unit and integration testing.

## Directory Structure

```
fixtures/
├── valid/          # Valid MML files for testing specific features
├── invalid/        # Invalid MML files that should fail parsing
└── README.md       # This file
```

## Valid Fixtures

Small, focused examples testing specific features:

| File | Purpose |
|------|---------|
| **basic.mml** | Original basic test fixture |
| **single_note.mml** | Simplest valid MML (one note) |
| **cc_commands.mml** | Control Change messages |
| **pitch_bend.mml** | Pitch bend commands |
| **pressure_commands.mml** | Channel and poly pressure |
| **meta_events.mml** | Meta events (tempo, time sig, markers, etc.) |
| **timing_types.mml** | All timing types (absolute, musical, relative, simultaneous) |
| **defines.mml** | @define statements |
| **sysex.mml** | SysEx messages |
| **comments.mml** | Comment syntax (single-line, multi-line, C++ style) |

## Invalid Fixtures

Examples that should fail parsing or validation:

| File | Error Type | Status |
|------|-----------|---------|
| **syntax_error.mml** | Invalid syntax | ✅ Fails as expected |
| **missing_frontmatter.mml** | No frontmatter | ⚠️  Actually optional |
| **invalid_channel.mml** | Channel > 16 | ⏳ Validation pending |
| **invalid_velocity.mml** | Velocity > 127 | ⏳ Validation pending |
| **invalid_cc_value.mml** | CC value > 127 | ⏳ Validation pending |
| **missing_timing.mml** | Command without timing | ✅ Fails as expected |
| **non_monotonic_timing.mml** | Time goes backward | ⏳ Validation pending |

## Usage

### In Tests

```python
from pathlib import Path

VALID_DIR = Path(__file__).parent / "fixtures" / "valid"
fixture = VALID_DIR / "single_note.mml"
doc = parser.parse_file(fixture)
```

### Creating New Fixtures

1. **Valid fixtures** should be minimal and focus on ONE feature
2. **Invalid fixtures** should clearly demonstrate ONE type of error
3. Name files descriptively (e.g., `multi_channel.mml`, `invalid_note_range.mml`)
4. Add comprehensive comments explaining what's being tested
5. Update this README with the new fixture

### Guidelines

**Valid Fixtures:**
- Minimal - only what's needed to test the feature
- Well-commented - explain what's being tested
- Self-contained - no external dependencies
- Parser-compatible - must parse successfully

**Invalid Fixtures:**
- Single error - don't mix multiple problems
- Clear intent - comment explaining why it should fail
- Realistic - based on actual user errors
- Documented - note whether validation is implemented

## Test Coverage

Current test coverage for fixtures:

- ✅ **Valid**: All fixtures have dedicated tests in [test_fixtures.py](../integration/test_fixtures.py)
- ✅ **Invalid**: Tests exist but some are skipped pending validation implementation

## Examples vs Fixtures

**Examples** ([examples/](../../examples/)):
- User-facing documentation
- Complete, realistic use cases
- Well-commented for learning
- Can be complex/multi-feature

**Fixtures** (this directory):
- Internal test data
- Focused, minimal test cases
- Quick to parse and verify
- Single-feature focused

## See Also

- [Integration Tests](../integration/test_fixtures.py) - Tests using these fixtures
- [Examples](../../examples/) - User-facing example files
- [Specification](../../spec.md) - Complete MML language spec
