# Skipped Tests Analysis

**Date**: 2025-11-11
**Branch**: claude/review-skipped-tests-011CV2uNRKoCLLonrkJpjGzw

## Executive Summary

This document reviews all skipped tests in the MIDI Markdown codebase and provides recommendations on which can be fixed or re-enabled.

**Total Skipped Tests Identified**: 11

**Categories**:
- ✅ **Can be fixed now** (4 tests) - Already implemented or easy fixes
- ⚠️ **Requires implementation** (4 tests) - Features not yet implemented
- 🔧 **Platform-specific** (3 tests) - Inherent platform limitations

---

## Category 1: ✅ Can Be Fixed Now (High Priority)

### 1.1 Alias Timing Error Handling Tests

**Location**: `tests/unit/test_alias_timing.py:200-208`

**Tests**:
- `test_beat_timing_not_supported()` (line 200)
- `test_tick_timing_not_supported()` (line 205)

**Skip Reason**: "Beat/tick timing error handling not yet implemented"

**Analysis**:
These tests have empty bodies with TODO comments. The alias resolver should validate that beat-based and tick-based timing are not used inside alias definitions.

**Recommendation**: ✅ **CAN BE FIXED**

**Action Items**:
1. Check if beat/tick timing in aliases is actually unsupported (verify in `alias/resolver.py`)
2. If unsupported, implement validation that raises appropriate error
3. Write test bodies that verify error is raised
4. If supported, remove skip markers and write tests for the feature

**Estimated Effort**: 2-4 hours (implement validation + write tests)

**Impact**: Improves alias validation and prevents confusing user errors

---

### 1.2 CLI Integration Tests - Device Library Exploration

**Location**: `tests/integration/test_cli_helpers_integration.py:119-132`

**Test**: `test_library_exploration_workflow()`

**Skip Condition**: Conditional skip if no device libraries found
```python
if not devices_dir.exists() or not list(devices_dir.glob("*.mmd")):
    pytest.skip("No device libraries found")
```

**Analysis**:
This is a conditional skip, not a decorator-based skip. The test runs if device libraries exist (which they do - we have 6 device libraries in `devices/`).

**Recommendation**: ✅ **NO ACTION NEEDED**

This test should already be running in CI. Verify it's not being skipped in practice:
- `devices/quad_cortex.mmd` exists ✓
- `devices/eventide_h90.mmd` exists ✓
- `devices/helix.mmd` exists ✓

**Action Items**:
1. Verify test runs successfully in current test suite
2. If skipping in CI, check CI environment has device files

**Estimated Effort**: 30 minutes (verification only)

---

### 1.3 Lark Exception Tests

**Location**: `tests/unit/test_error_handler.py:72-208`

**Tests**:
- `test_parse_error_exit_code()` (line 72)
- `test_no_source_file_fallback()` (line 201)
- `test_accessibility_flags_passed()` (line 206)

**Skip Reason**: "Lark exception mocking is complex, covered by integration tests"

**Analysis**:
These unit tests were skipped because mocking Lark's exception hierarchy is complex. The functionality IS covered by integration tests (e.g., `tests/integration/test_cli.py`).

**Recommendation**: ⚠️ **OPTIONAL - LOW PRIORITY**

**Options**:
1. **Keep skipped** - Integration tests provide adequate coverage
2. **Remove tests** - Clean up test suite by removing redundant tests
3. **Implement with real Lark** - Don't mock, use actual invalid MML to trigger Lark errors

**Action Items** (if implementing):
1. Replace mocking approach with real invalid MML parsing
2. Use `parser.parse_string("invalid mml")` to trigger Lark exceptions
3. Verify error handler correctly catches and formats Lark errors

**Estimated Effort**: 3-4 hours (requires understanding Lark exception types)

**Recommendation**: **REMOVE** these tests - integration tests already cover this

---

## Category 2: ⚠️ Requires Implementation (Features Not Ready)

### 2.1 Multi-line SysEx

**Location**: `tests/integration/test_complex_documents.py:80-92`

**Test**: `test_multiline_sysex()`

**Skip Reason**: "Multi-line SysEx not yet implemented"

**Analysis**:
The test expects this syntax:
```mml
- sysex F0 43 12 00
         11 22 33 44
         55 66 77 F7
```

Current parser only supports single-line SysEx. Grammar would need to be updated to support continuation lines.

**Recommendation**: ⚠️ **FEATURE REQUEST - IMPLEMENT LATER**

**Action Items** (when implementing):
1. Update `parser/mml.lark` grammar to support multi-line SysEx
2. Update transformer to handle line continuations
3. Add whitespace normalization for hex bytes
4. Enable this test

**Estimated Effort**: 4-6 hours (grammar changes, transformer updates, tests)

**Priority**: Low (single-line SysEx works fine for most use cases)

---

### 2.2 Advanced Features - Conditionals and Sections

**Location**: `tests/unit/test_advanced_features.py:41-73`

**Tests**:
- `test_conditional_statement()` (line 41) - @if/@else conditionals
- `test_section_definition()` (line 58) - @section blocks

**Skip Reason**: "Conditional statements not yet implemented" / "Section definitions not yet implemented"

**Analysis**:
These are Phase 4+ features that were not part of MVP:
- **Conditionals**: `@if/@elif/@else` statements for conditional MIDI generation
- **Sections**: `@section` blocks for organizing timing ranges

**Recommendation**: ⚠️ **FUTURE FEATURE - KEEP SKIPPED**

These tests document future feature requirements. They should remain skipped until these features are implemented.

**Action Items**:
1. Keep tests as documentation of intended behavior
2. Update spec.md to clarify if these features are planned
3. When implementing, use these tests as acceptance criteria

**Priority**: Low (not critical for core functionality)

---

### 2.3 Advanced Features - Ramp and Random Expressions in @define

**Location**: `tests/unit/test_advanced_features.py:105-121`

**Tests**:
- `test_ramp_expression()` (line 105) - `@define VAL ramp(0, 127, linear)`
- `test_random_expression()` (line 114) - `@define VAL random(0, 127)`

**Skip Reason**: "Ramp expressions not yet implemented" / "Random expressions not yet implemented"

**Analysis**:
The tests expect `ramp()` and `random()` to work in `@define` statements. Currently:
- ✅ `random()` works in command parameters (velocity, notes, CC values)
- ❌ `random()` does NOT work in `@define` (by design - variables are resolved once)
- ❌ `ramp()` is used in `@sweep` blocks, not as standalone function

**Recommendation**: ✅ **CAN BE REMOVED OR UPDATED**

**Options**:
1. **Remove tests** - These don't match current design philosophy
   - `random()` in `@define` would only evaluate once (not useful)
   - `ramp()` is not a valid expression type for variables

2. **Update tests** - Test current behavior:
   - `random()` works in commands: `- note_on 1.60 random(80,100) 1b`
   - `ramp()` works in sweeps: `@sweep ... ramp(0, 127)`

**Action Items**:
1. Review design: Should variables support runtime expressions?
2. If not, remove these tests or convert to negative tests (verify they fail appropriately)
3. Update `examples/04_generative/` documentation to clarify `random()` limitations

**Estimated Effort**: 1-2 hours (decision + test updates)

**Recommendation**: **REMOVE** or convert to negative tests verifying intended behavior

---

## Category 3: 🔧 Platform-Specific (Cannot Be Fixed)

### 3.1 REPL Multiline Input Tests

**Location**: `tests/integration/test_repl_end_to_end.py:95-183`

**Tests**:
- `test_repl_multiline_alias()` (line 95)
- `test_repl_multiline_loop()` (line 129)
- `test_repl_continuation_prompt()` (line 157)

**Skip Reason**: "Flaky pexpect EOF handling with prompt_toolkit - REPL .quit doesn't exit cleanly in pexpect context"

**Analysis**:
These tests use `pexpect` to test interactive REPL behavior. The tests are flaky because:
- `prompt_toolkit` (used for REPL) has complex EOF handling
- `.quit` command doesn't always exit cleanly in pexpect subprocess
- Race conditions between expect() and prompt rendering

The REPL functionality WORKS in practice - the tests are just unreliable in automated testing.

**Recommendation**: 🔧 **KEEP SKIPPED - FLAKY TESTS**

**Options**:
1. **Keep skipped** - REPL works, tests are unreliable
2. **Rewrite with different approach** - Use pytest-subprocess or similar
3. **Manual testing only** - Remove automated tests, rely on manual QA

**Action Items**:
1. Document that REPL tests require manual verification
2. Add manual test checklist to CONTRIBUTING.md
3. Consider pytest-subprocess for more reliable subprocess testing

**Priority**: Low (REPL works, just hard to test automatically)

---

### 3.2 REPL Platform Compatibility

**Location**: `tests/integration/test_repl_end_to_end.py:27-30`

**Module-Level Skip**:
```python
pytestmark = pytest.mark.skipif(
    sys.platform == "win32",
    reason="pexpect doesn't work on Windows (uses Unix pty)",
)
```

**Analysis**:
All REPL end-to-end tests are skipped on Windows because `pexpect` uses Unix pseudo-terminals (pty) which don't exist on Windows.

**Recommendation**: 🔧 **PLATFORM LIMITATION - KEEP SKIPPED ON WINDOWS**

**Options**:
1. **Accept limitation** - REPL tests only run on Unix/macOS
2. **Use alternative library** - `wexpect` (Windows expect) for Windows testing
3. **Skip on Windows** - Current approach (tests still run on Linux/macOS in CI)

**Action Items**:
1. Verify CI runs on Linux (tests should pass there)
2. Document Windows testing limitations in CONTRIBUTING.md
3. Consider wexpect for Windows compatibility (low priority)

**Priority**: Very Low (Windows users can still use REPL, just not test it automatically)

---

## Summary and Recommendations

### Immediate Actions (Can Fix Now)

| Test | Action | Priority | Effort |
|------|--------|----------|--------|
| `test_beat_timing_not_supported()` | Implement validation + write test | HIGH | 2-4h |
| `test_tick_timing_not_supported()` | Implement validation + write test | HIGH | 2-4h |
| `test_ramp_expression()` | Remove or convert to negative test | MEDIUM | 1-2h |
| `test_random_expression()` | Remove or convert to negative test | MEDIUM | 1-2h |
| Lark exception tests (3 tests) | Remove redundant tests | LOW | 1h |

### Future Implementation

| Test | Feature | Priority | Complexity |
|------|---------|----------|------------|
| `test_multiline_sysex()` | Multi-line SysEx syntax | LOW | Medium |
| `test_conditional_statement()` | @if/@elif/@else | LOW | High |
| `test_section_definition()` | @section blocks | LOW | Medium |

### Keep Skipped (By Design)

| Test | Reason | Action |
|------|--------|--------|
| REPL multiline tests (3) | Flaky pexpect behavior | Document manual test procedure |
| Windows REPL tests | pexpect platform limitation | Document in CI/CONTRIBUTING.md |
| Device library exploration | Conditional skip (should pass) | Verify runs in CI |

---

## Proposed Plan

### Phase 1: Quick Wins (1-2 days)

1. ✅ **Fix alias timing tests**
   - Implement beat/tick validation in alias resolver
   - Write test bodies for both tests
   - Verify coverage improves

2. ✅ **Clean up redundant tests**
   - Remove 3 Lark exception unit tests (already covered by integration tests)
   - Remove or update ramp/random expression tests
   - Update coverage reports

### Phase 2: Documentation (1 day)

3. 📝 **Document test limitations**
   - Add CONTRIBUTING.md section on REPL testing
   - Document Windows testing limitations
   - Add manual test checklist for REPL features

### Phase 3: Future Features (As Needed)

4. 🚀 **Implement skipped features** (when prioritized)
   - Multi-line SysEx support
   - Conditional statements (@if/@else)
   - Section blocks (@section)

---

## Coverage Impact

**Current Status**: 72.53% coverage

**After Phase 1 Fixes**:
- +2 tests enabled (alias timing validation)
- +4 tests removed (redundant/wrong design)
- Estimated coverage: **73-74%** (slight improvement from alias validation)

**After Phase 3** (if all features implemented):
- +6 additional tests enabled
- Estimated coverage: **75-76%**

---

## Recommendations for Each Test

### ✅ High Priority - Fix Now

1. **`test_beat_timing_not_supported()`** - Write test body, implement validation
2. **`test_tick_timing_not_supported()`** - Write test body, implement validation

### ⚠️ Medium Priority - Clean Up

3. **`test_ramp_expression()`** - Remove (doesn't match design)
4. **`test_random_expression()`** - Remove (doesn't match design)
5. **Lark exception tests (3)** - Remove (redundant with integration tests)

### 🔧 Low Priority - Keep Skipped

6. **`test_multiline_sysex()`** - Keep skipped until feature implemented
7. **`test_conditional_statement()`** - Keep skipped until feature implemented
8. **`test_section_definition()`** - Keep skipped until feature implemented
9. **REPL multiline tests (3)** - Keep skipped (flaky by nature)
10. **Windows REPL tests** - Keep platform skip (pexpect limitation)

---

## Next Steps

1. **Review this analysis** with project maintainer
2. **Prioritize** which tests to address first
3. **Create issues** for feature implementations
4. **Update tests** based on recommendations

**Document Version**: 1.0
**Last Updated**: 2025-11-11
