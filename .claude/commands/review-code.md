---
description: Review code changes against MMD coding standards and anti-patterns
---

Review code changes to ensure they follow MMD best practices.

## What to Check:

### 1. Anti-Patterns (docs/dev-guides/anti-patterns.md)

Verify the code DOES NOT contain these common mistakes:

❌ **Using full command names** (should be "cc" not "control_change")
❌ **Mutating AST nodes** after parsing (create new nodes instead)
❌ **Missing `isinstance(value, tuple)` check** before int() conversion
❌ **Absolute timing in aliases** (use relative or let caller control)
❌ **Skipping IR layer** (always compile through IR)
❌ **Hardcoded time signature** (extract from frontmatter)
❌ **Missing bar/beat -1 adjustment** (they're 1-indexed)
❌ **Using subprocess for CLI tests** (use CliRunner instead)
❌ **Ignoring tempo changes** (tempo is stateful)
❌ **Aliases without descriptions** (required for documentation)

### 2. Code Quality Standards (CLAUDE.md)

✅ **Type hints** - All functions have Python 3.12+ type annotations
✅ **Tests** - New features have unit + integration tests
✅ **Formatting** - Run `just fmt` (Ruff formatted)
✅ **Linting** - No Ruff errors (`just lint`)
✅ **Type checking** - No mypy errors (`just typecheck`)
✅ **Documentation** - User guides updated if syntax changes
✅ **Examples** - New features have working examples

### 3. Architecture Patterns

✅ **Pure functions for codegen** - Return bytes/strings, don't write files
✅ **Immutable data structures** - Use dataclasses, don't mutate
✅ **Error handling with context** - Include source location (file, line, column)
✅ **Separation of concerns** - Each layer has single responsibility
✅ **IR layer usage** - Don't bypass validation/compilation stages

### 4. Parser Patterns (docs/dev-guides/parser-patterns.md)

For parser/transformer changes:
✅ **Grammar follows conventions** - Use Lark best practices
✅ **Transformer creates correct AST** - Proper node types
✅ **Position tracking enabled** - For error messages
✅ **Forward reference handling** - Check tuples before conversion

### 5. Testing Coverage

✅ **Unit tests** - Test individual components in isolation
✅ **Integration tests** - Test full pipeline
✅ **Edge cases** - Test min/max values, empty inputs
✅ **Error cases** - Test validation failures
✅ **Examples compile** - Test examples actually work

## Review Process:

1. **Read the changes** - Understand what's being modified
2. **Check against anti-patterns** - Flag any violations
3. **Verify tests exist** - New code must have tests
4. **Run quality checks** - `just check` should pass
5. **Run test suite** - `just test` should pass
6. **Check documentation** - Is it updated?
7. **Provide feedback** - Specific, actionable suggestions

## Output Format:

✅ **Passes**: List what looks good
⚠️ **Warnings**: Non-critical issues to consider
❌ **Blockers**: Must fix before merging

Provide specific line numbers and file paths for all feedback.
