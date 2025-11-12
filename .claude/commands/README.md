# Claude Slash Commands for MMD Development

This directory contains custom slash commands for Claude Code to assist with MIDI Markdown development.

## Available Commands

### 🆕 `/new-example` - Create New Example File
Creates a new MMD example with proper template, frontmatter, and inline comments.

**Usage:** `/new-example`

**Interactive prompts:**
- Example name
- Category (basics, timing, midi_features, advanced, device_libraries, generative, tutorials)
- Description
- Difficulty level

**Auto-completes:**
- Validates and compiles the example
- Updates examples/README.md

---

### 🎸 `/new-device` - Create Device Library
Creates a new device library file with proper structure and alias templates.

**Usage:** `/new-device`

**Interactive prompts:**
- Device name
- Manufacturer
- Default MIDI channel
- Documentation URL
- Key commands to implement

**Auto-completes:**
- Validates device library
- Creates test example
- Updates documentation

---

### ➕ `/add-midi-command` - Add New MIDI Command
Step-by-step guide for adding a new MIDI command type to the language.

**Usage:** `/add-midi-command`

**Guides through:**
1. Grammar updates (mml.lark)
2. Transformer changes (parser/transformer.py)
3. Validation logic (utils/validation/)
4. IR compiler updates (core/compiler.py)
5. Codegen implementation (codegen/midi_file.py)
6. Test creation
7. Documentation updates

**Critical:** Follows anti-patterns doc to avoid common mistakes

---

### 🐛 `/debug-timing` - Debug Timing Issues
Analyzes timing calculations and helps fix timing problems.

**Usage:** `/debug-timing`

**Analyzes:**
- Timing paradigm used (absolute, musical, relative, simultaneous)
- Calculation formulas
- Common timing issues (off-by-one, tempo changes, etc.)
- Non-monotonic event ordering

**Provides:**
- Step-by-step calculation breakdowns
- Event timeline inspection
- Specific recommendations

---

### 🔍 `/review-code` - Code Review Assistant
Reviews code changes against MMD coding standards and anti-patterns.

**Usage:** `/review-code`

**Checks:**
- Anti-patterns (10 common mistakes)
- Code quality standards (type hints, tests, formatting)
- Architecture patterns (pure functions, immutability)
- Parser patterns (grammar conventions)
- Testing coverage

**Output:**
- ✅ Passes
- ⚠️ Warnings
- ❌ Blockers

---

### 📖 `/explain-pipeline` - Pipeline Architecture
Explains the compilation pipeline and component responsibilities.

**Usage:** `/explain-pipeline`

**Covers:**
- 9-stage compilation pipeline
- Component responsibilities
- Feature → component mapping
- Where to find specific functionality

**Great for:** Understanding codebase architecture, finding where to make changes

---

### 🧪 `/test-feature` - Smart Test Runner
Finds and runs tests for a specific feature or component.

**Usage:** `/test-feature`

**Capabilities:**
- Searches for related tests (unit, integration, e2e)
- Runs tests in priority order
- Shows coverage for the feature
- Suggests missing test cases
- Maps features to test files

**Examples:**
- Test loops: finds test_loops.py, test_end_to_end.py
- Test aliases: finds test_alias_resolver.py, test_device_libraries.py

---

### 🎯 `/create-alias` - Alias Creation Guide
Interactive guide for creating device library aliases with proper syntax.

**Usage:** `/create-alias`

**Guides through:**
- Simple aliases (single command)
- Multi-command aliases (macros)
- Parameter types (basic, default, enum, special)
- Computed values
- Best practices

**Provides:**
- Syntax templates
- Parameter type reference
- Testing workflow
- Real examples from device libraries

---

## Usage Tips

1. **Invoke commands** by typing `/command-name` in your conversation with Claude
2. **Commands are interactive** - Claude will ask follow-up questions
3. **Commands understand context** - Reference files from CLAUDE.md and project docs
4. **Use frequently** - Designed to save time on repetitive development tasks

## Command Categories

| Category | Commands |
|----------|----------|
| **Creation** | `/new-example`, `/new-device`, `/add-midi-command` |
| **Debugging** | `/debug-timing`, `/review-code` |
| **Learning** | `/explain-pipeline`, `/test-feature` |
| **Guidance** | `/create-alias`, `/add-midi-command` |

## When to Use Each Command

### Starting New Work
- Creating example → `/new-example`
- Adding device support → `/new-device`
- Adding language feature → `/add-midi-command`

### During Development
- Code review → `/review-code`
- Understanding architecture → `/explain-pipeline`
- Running tests → `/test-feature`

### Debugging
- Timing problems → `/debug-timing`
- Architecture questions → `/explain-pipeline`

### Device Library Development
- Creating aliases → `/create-alias`
- New device → `/new-device`

## Integration with Existing Tools

These slash commands complement existing `just` commands:

| Just Command | Slash Command | Purpose |
|--------------|---------------|---------|
| `just test` | `/test-feature` | More targeted test execution |
| `just validate FILE` | `/debug-timing` | Deep timing analysis |
| `just examples` | `/new-example` | Create new examples |
| N/A | `/review-code` | Automated code review |
| N/A | `/explain-pipeline` | Architecture guidance |
| N/A | `/add-midi-command` | Feature development guide |

## Contributing

To add new slash commands:

1. Create `{command-name}.md` in `.claude/commands/`
2. Add frontmatter with description
3. Write clear instructions for Claude
4. Update this README
5. Test the command with Claude Code

**Format:**
```markdown
---
description: Brief description of what the command does
---

Detailed instructions for Claude on how to execute this command...
```

## References

- **[CLAUDE.md](../../CLAUDE.md)** - Project context for Claude
- **[spec.md](../../spec.md)** - Language specification
- **[docs/dev-guides/](../../docs/dev-guides/)** - Developer guides
- **[examples/README.md](../../examples/README.md)** - Example library

## See Also

- Claude Code documentation: https://docs.claude.com/claude-code
- Custom slash commands guide: https://docs.claude.com/claude-code/custom-commands
