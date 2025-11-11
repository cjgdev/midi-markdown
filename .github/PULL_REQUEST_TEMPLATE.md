## Description

<!-- Provide a clear and concise summary of what this PR does -->


## Motivation

<!-- Why is this change needed? What problem does it solve? -->
<!-- Link to related issues using: Closes #123, Fixes #456, Resolves #789 -->


## Type of Change

<!-- Mark all applicable options with an 'x' -->

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring (no functional changes)
- [ ] Test improvements
- [ ] CI/CD improvements
- [ ] Build/tooling changes

## Changes Made

<!-- List the key changes in this PR. Be specific and concise. -->

-
-
-

## Testing

<!-- Describe how you tested these changes -->

### Test Coverage

- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] E2E tests added/updated (if applicable)
- [ ] All tests pass locally (`just test` or `uv run pytest`)
- [ ] No test coverage decrease (or justified if decreased)

**Coverage change**: <!-- e.g., 72.53% → 75.20% (+2.67%) or "no change" -->

### Manual Testing

<!-- Describe what manual testing you performed -->

**Test commands run**:
```bash
# Example:
# just test
# just test-unit
# uv run mmdc compile examples/00_basics/00_hello_world.mmd
```

**Test scenarios**:
<!-- List specific scenarios you tested -->
-
-

## Documentation

<!-- Check all applicable items -->

- [ ] Code docstrings added/updated
- [ ] Type hints added for all new functions/methods
- [ ] CLI help text updated (if CLI changes made)
- [ ] User documentation updated in `docs/` (if applicable)
- [ ] Examples added/updated in `examples/` (if applicable)
- [ ] CHANGELOG.md updated (required for notable changes)
- [ ] README.md updated (if applicable)

## Code Quality

<!-- Ensure your code meets quality standards -->

- [ ] Code follows project style guidelines (`just fmt` or `uv run ruff format .`)
- [ ] Linting passes with no warnings (`just lint` or `uv run ruff check .`)
- [ ] Type checking passes (`just typecheck` or `uv run mypy src`)
- [ ] No new compiler warnings or errors
- [ ] Error messages are clear and actionable
- [ ] Performance impact assessed (if applicable)
- [ ] Security implications considered (if applicable)

**Style checks run**:
```bash
# just check  (runs fmt + lint + typecheck)
```

## Pre-submission Checklist

<!-- Complete all items before requesting review -->

- [ ] I have read [CONTRIBUTING.md](../CONTRIBUTING.md)
- [ ] My code follows the project's architecture and design patterns
- [ ] I have performed a self-review of my code
- [ ] I have commented complex/non-obvious code sections
- [ ] My changes generate no new warnings or errors
- [ ] I have added tests that prove my fix/feature works
- [ ] New and existing unit tests pass locally
- [ ] Any dependent changes have been merged and published
- [ ] I have checked my code for security vulnerabilities
- [ ] I have verified backwards compatibility (or documented breaking changes)

## Breaking Changes

<!-- If this PR includes breaking changes, describe them here -->
<!-- Update CHANGELOG.md with migration guide if needed -->

**Breaking changes**: None | Yes (describe below)

<!-- If yes, list breaking changes and migration path -->


## Performance Impact

<!-- If this PR affects performance, provide details -->

**Performance impact**: None | Positive | Negative | Unknown

<!-- If impactful, provide benchmarks or profiling results -->


## Screenshots / Output Examples

<!-- Add screenshots for UI changes or CLI output examples -->

### Before
```
<!-- Example output before changes -->
```

### After
```
<!-- Example output after changes -->
```

## Additional Context

<!-- Any additional information, links, design decisions, or context -->
<!-- Link to related PRs, external documentation, or discussion threads -->


## Dependencies

<!-- List any new dependencies added or dependency version changes -->

**New dependencies**: None | Yes (list below)

<!-- If yes, justify why each dependency is needed -->


## Deployment Notes

<!-- Any special deployment considerations? -->
<!-- Required database migrations, config changes, etc. -->

**Deployment notes**: None | Yes (describe below)


## Reviewer Notes

<!-- Anything specific you want reviewers to focus on? -->
<!-- Areas where you're unsure or want specific feedback? -->

**Focus areas for review**:
-
-

**Questions for reviewers**:
-
-

---

<!--
Thank you for contributing to MIDI Markdown!
Your effort helps make this project better for everyone.
-->
