# Claude Code Agents for MIDI Markdown

This directory contains specialized Claude Code agents for the MIDI Markdown (MMD) project.

## Available Agents

### 1. test-runner ⚡

**Purpose**: Automated test execution and failure resolution

**Triggers**:
- After code changes to `src/` files
- When tests fail
- After implementing new features

**Capabilities**:
- Runs appropriate test suite based on changes (smoke, unit, integration, full)
- Analyzes test failures systematically
- Fixes bugs while preserving test intent
- Checks anti-patterns before implementing fixes
- Reports coverage changes

**Tools**: Bash, Read, Edit, Grep, Glob

**Use case**: "Run tests for these parser changes and fix any failures"

---

### 2. parser-expert 🎯

**Purpose**: Lark grammar and AST transformation specialist

**Triggers**:
- Adding new MIDI command types
- Modifying grammar rules
- Working with AST transformation
- Debugging parser issues

**Capabilities**:
- Guides through complete workflow for adding MIDI commands
- Ensures critical transformer patterns (abbreviated types, isinstance checks)
- Updates grammar, transformer, validation, and codegen
- Creates comprehensive tests

**Tools**: Read, Edit, Grep, Glob, Bash

**Use case**: "Add support for MIDI polyphonic aftertouch command"

---

### 3. timing-debugger ⏱️

**Purpose**: Timing calculation debugging and validation

**Triggers**:
- Off-by-one timing errors
- Musical time (bars.beats.ticks) bugs
- Tempo change handling issues
- Timing validation failures

**Capabilities**:
- Debugs all 4 timing paradigms (absolute, musical, relative, simultaneous)
- Enforces critical timing rules (1-indexed bars/beats, tempo state, time signature)
- Validates calculations against reference formulas
- Provides detailed diagnostic output

**Tools**: Read, Edit, Bash, Grep, Glob

**Use case**: "Debug why musical timing is off by one bar in 3/4 time"

---

### 4. code-quality-guardian 🛡️

**Purpose**: Enforce critical implementation rules and prevent anti-patterns

**Triggers**:
- After significant code changes
- Before committing
- During code review

**Capabilities**:
- Checks for 5 critical implementation rules (command types, forward refs, timing, AST immutability, IR layer)
- Detects known anti-patterns from production bugs
- Performs systematic code review with checklist
- Reports issues by severity (critical, warning, suggestion)

**Tools**: Read, Edit, Grep, Glob, Bash

**Use case**: "Review my changes and check for anti-patterns"

---

### 5. device-library-expert 🎸

**Purpose**: Device library creation and documentation

**Triggers**:
- Creating new device libraries
- Documenting MIDI implementations
- Building reusable command sets

**Capabilities**:
- Guides through complete device library creation workflow
- Ensures proper structure (frontmatter, sections, naming)
- Documents all parameter types (enum, range, computed, conditional)
- Creates comprehensive aliases for hardware devices
- Validates library syntax and completeness

**Tools**: Read, Write, Edit, Grep, Glob, Bash

**Use case**: "Create a device library for the Strymon BigSky reverb pedal"

---

### 6. release-manager 🚀

**Purpose**: Release management and version publishing

**Triggers**:
- Creating new releases (patch, minor, major)
- Version bumping and changelog updates
- Publishing to package repositories
- Managing GitHub releases

**Capabilities**:
- Guides through complete release workflow
- Runs pre-release quality checks (tests, linting, validation)
- Manages version bumping across project files
- Updates CHANGELOG.md with release notes
- Creates git tags and manages GitHub releases
- Monitors release workflows and package publishing
- Handles rollbacks and hotfixes

**Tools**: Bash, Read, Edit, Grep, Glob

**Use case**: "Create a new patch release with bug fixes"

---

## Agent Selection Guide

| Task | Recommended Agent |
|------|------------------|
| Run tests after code changes | `test-runner` |
| Add new MIDI command | `parser-expert` |
| Fix timing calculation bug | `timing-debugger` |
| Review code before commit | `code-quality-guardian` |
| Create device library | `device-library-expert` |
| Create new release | `release-manager` |
| Debug off-by-one timing | `timing-debugger` |
| Fix test failures | `test-runner` |
| Ensure code quality | `code-quality-guardian` |
| Update grammar rules | `parser-expert` |
| Bump version | `release-manager` |
| Update changelog | `release-manager` |
| Publish to PyPI | `release-manager` |

## Usage

Claude Code will automatically invoke these agents when appropriate based on task descriptions. You can also explicitly request an agent:

```
> Use the test-runner agent to run tests for my parser changes
> Have the code-quality-guardian review my recent commits
> Ask the timing-debugger to investigate this musical timing issue
> Use the release-manager to create a new patch release
```

## Agent Workflow Example

### Scenario: Adding a new MIDI command

1. **parser-expert**: Guides through grammar, transformer, validation, codegen updates
2. **test-runner**: Runs tests and fixes any failures
3. **code-quality-guardian**: Reviews changes for anti-patterns
4. **test-runner**: Final smoke test before commit

### Scenario: Creating device library

1. **device-library-expert**: Creates device library with proper structure
2. **test-runner**: Validates library syntax with `mmdc library validate`
3. **code-quality-guardian**: Reviews for completeness and consistency

### Scenario: Creating a release

1. **release-manager**: Runs pre-release checks (tests, linting, validation)
2. **release-manager**: Updates CHANGELOG.md and bumps version
3. **release-manager**: Creates git tag and pushes to GitHub
4. **release-manager**: Monitors GitHub Actions workflows
5. **release-manager**: Verifies package publishing (PyPI, Homebrew, etc.)

## Design Principles

These agents follow Anthropic's best practices:

- ✅ **Focused expertise**: Each agent has a single, clear responsibility
- ✅ **Detailed prompts**: Include specific instructions, examples, and checklists
- ✅ **Limited tool access**: Only grant tools necessary for the agent's purpose
- ✅ **Context preservation**: Separate context windows prevent main thread pollution
- ✅ **Proactive invocation**: Descriptions include triggers for automatic use
- ✅ **Project-specific**: Tailored to MMD codebase patterns and workflows

## Maintenance

Update agents when:
- New anti-patterns are discovered
- New features require specialized handling
- Test workflows change
- New common tasks emerge

## Related Documentation

- **[Anthropic Agents Documentation](https://docs.anthropic.com/claude-code/agents)** - Official agent guide
- **[CLAUDE.md](../CLAUDE.md)** - Project context and critical rules
- **[docs/dev-guides/anti-patterns.md](../../docs/dev-guides/anti-patterns.md)** - Known bugs and fixes
- **[docs/dev-guides/parser-patterns.md](../../docs/dev-guides/parser-patterns.md)** - Parser implementation patterns
- **[docs/dev-guides/timing-system.md](../../docs/dev-guides/timing-system.md)** - Timing calculations

---

**Total Agents**: 6
**Total Size**: ~71KB
**Created**: 2025-11-15
**Last Updated**: 2025-11-15 (added release-manager)
