# Test Fixtures

This directory contains focused test fixtures for unit and integration testing.

## Directory Structure

```
fixtures/
├── valid/          # Valid MMD files for testing specific features
├── invalid/        # Invalid MMD files that should fail parsing
└── README.md       # This file
```

## Valid Fixtures

Small, focused examples testing specific features:

| File | Purpose |
|------|---------|
| **basic.mmd** | Original basic test fixture |
| **single_note.mmd** | Simplest valid MMD (one note) |
| **cc_commands.mmd** | Control Change messages |
| **pitch_bend.mmd** | Pitch bend commands |
| **pressure_commands.mmd** | Channel and poly pressure |
| **meta_events.mmd** | Meta events (tempo, time sig, markers, etc.) |
| **timing_types.mmd** | All timing types (absolute, musical, relative, simultaneous) |
| **defines.mmd** | @define statements |
| **sysex.mmd** | SysEx messages |
| **comments.mmd** | Comment syntax (single-line, multi-line, C++ style) |

## Invalid Fixtures

Examples that should fail parsing or validation:

| File | Error Type | Status |
|------|-----------|---------|
| **syntax_error.mmd** | Invalid syntax | ✅ Fails as expected |
| **missing_frontmatter.mmd** | No frontmatter | ⚠️  Actually optional |
| **invalid_channel.mmd** | Channel > 16 | ⏳ Validation pending |
| **invalid_velocity.mmd** | Velocity > 127 | ⏳ Validation pending |
| **invalid_cc_value.mmd** | CC value > 127 | ⏳ Validation pending |
| **missing_timing.mmd** | Command without timing | ✅ Fails as expected |
| **non_monotonic_timing.mmd** | Time goes backward | ⏳ Validation pending |

## Usage

### In Tests

```python
from pathlib import Path

VALID_DIR = Path(__file__).parent / "fixtures" / "valid"
fixture = VALID_DIR / "single_note.mmd"
doc = parser.parse_file(fixture)
```

### Creating New Fixtures

1. **Valid fixtures** should be minimal and focus on ONE feature
2. **Invalid fixtures** should clearly demonstrate ONE type of error
3. Name files descriptively (e.g., `multi_channel.mmd`, `invalid_note_range.mmd`)
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
- [Specification](../../spec.md) - Complete MMD language spec
