# CLAUDE.md

This file provides core context for Claude Code when working with this repository.

<project_context>

## Project Overview

**MIDI Markdown (MMD)** is a human-readable, text-based format for creating and automating MIDI sequences. Designed for live performance automation (Neural DSP Quad Cortex, Eventide H90, Line 6 Helix) but supports all MIDI devices.

**Status:** MVP Complete - Full compilation pipeline working with 1264 passing tests, 72.53% coverage.

**Recent:** Phase 6 (Generative & Modulation) complete. Random values, computed expressions, curve/wave/envelope modulation.

**Phase 3:** Real-time MIDI playback complete. TUI player with sub-5ms timing precision.

</project_context>

---

<when_to_use>

## When to Use This Context

**Auto-invoke when:**

- Working with parser/transformer code in `src/midi_markdown/parser/`
- Adding new MIDI command types
- Debugging timing calculations
- Writing tests in `tests/`
- Implementing device libraries in `devices/`
- Modifying alias resolution in `src/midi_markdown/alias/`
- Working with expansion logic (loops, sweeps, variables)

**Do NOT invoke for:**

- General MIDI theory questions (use web search)
- External tool documentation (python-rtmidi, mido)
- Generic Python best practices
- Questions about examples (read example files directly)

</when_to_use>

---

<quick_start>

## Quick Start

Essential commands for development:

```bash
# Testing
just test          # All tests (1264 passing)
just test-unit     # Unit tests only (598)
just test-e2e      # End-to-end compilation tests
just smoke         # Quick validation (fastest tests)

# Code quality
just fmt           # Format code (Ruff)
just lint          # Lint code
just check         # Format + lint + typecheck
just qa            # Format + lint + test

# CLI usage
just compile INPUT OUTPUT    # Compile MMD to MIDI
just validate FILE          # Full validation
just run play song.mmd      # Real-time playback with TUI
just run inspect song.mmd   # Diagnostic output (table format)

# Development
just repl          # Python REPL with project loaded
just clean         # Clean build artifacts
```

**Technology Stack:**

- Python 3.12+ with UV package manager
- Lark (parser), Mido (MIDI files), python-rtmidi (real-time I/O)
- Typer + Rich (CLI), pytest (testing), Ruff (linting/formatting)

</quick_start>

---

<file_structure>

## Codebase Structure

```
src/midi_markdown/
├── parser/          # Lark grammar + AST transformation
├── alias/           # Alias resolution + imports
├── expansion/       # Variables, loops, sweeps, modulation, random
├── core/            # IR (Intermediate Representation)
├── codegen/         # MIDI file generation (Mido)
├── runtime/         # Real-time playback + TUI
├── cli/             # Typer CLI commands
└── utils/           # Validation, constants, curves, waveforms

examples/            # 35 working examples (organized by category)
devices/             # 6 device libraries (Quad Cortex, H90, Helix, etc.)
docs/                # User guides, tutorials, references
  └── dev-guides/    # Developer guides
tests/               # 1264 tests (unit + integration + e2e)
```

</file_structure>

---

<critical_notes>

## Critical Implementation Rules

**ALWAYS follow these patterns** - violations cause bugs:

### 1. Command Type Convention

Use abbreviated command types in code:

- ✅ `"pc"` NOT `"program_change"`
- ✅ `"cc"` NOT `"control_change"`
- ✅ `"note_on"` NOT `"note_on_message"`
- ✅ `"pitch_bend"` NOT `"pitchbend"`

**Why:** Transformer creates abbreviated types. Validation/codegen must match.

### 2. Forward Reference Pattern

Always check `isinstance(value, tuple)` before `int()` conversion:

```python
# ✅ CORRECT
param_val = self._resolve_param(param)
param_int = int(param_val) if not isinstance(param_val, tuple) else param_val

# ❌ WRONG - crashes on forward references
param_int = int(self._resolve_param(param))  # TypeError if unresolved variable!
```

**Why:** Unresolved variables are tuples: `('var', 'VAR_NAME')`

### 3. Timing Index Convention

Bars and beats are **1-indexed** in syntax, **0-indexed** in calculations:

```python
# ✅ CORRECT
absolute_ticks = (bar - 1) * beats_per_bar * ticks_per_beat

# ❌ WRONG - off by one bar/beat
absolute_ticks = bar * beats_per_bar * ticks_per_beat
```

**Why:** Musical notation: "bar 1, beat 1" vs MIDI ticks start at 0.

### 4. AST Immutability

Never modify AST nodes after parsing. Create new nodes instead:

```python
# ✅ CORRECT
new_event = MIDICommand(type=orig.type, timing=new_timing, ...)

# ❌ WRONG - breaks validation
event.timing = new_timing  # Mutation!
```

### 5. IR Layer Required

Always compile through IR layer. Never skip:

```python
# ✅ CORRECT
ir_program = compile_ast_to_ir(document, ppq=480)
midi_bytes = generate_midi_file(ir_program)

# ❌ WRONG - skips validation
midi_bytes = ast_to_midi_direct(document)  # Bypasses IR!
```

**For detailed explanations, see [@docs/dev-guides/anti-patterns.md](docs/dev-guides/anti-patterns.md)**

</critical_notes>

---

<architecture_quick_ref>

## Architecture Quick Reference

**Compilation Pipeline:**

```
Input (.mmd) → Parser → AST → Import Resolver → Alias Resolver
→ Command Expander → Validator → IR Compiler → Output (MIDI/CSV/JSON/Playback)
```

**Q: Where does X happen?**

| Operation | Location | Key Function |
|-----------|----------|--------------|
| Parsing text → AST | `parser/parser.py` | `MMLParser.parse_string()` |
| Loading device libraries | `alias/imports.py` | `resolve_imports()` |
| Expanding aliases | `alias/resolver.py` | `resolve_alias_call()` |
| Expanding variables/loops/sweeps | `expansion/expander.py` | `CommandExpander.process_ast()` |
| Timing calculations | `expansion/expander.py` | `_compute_absolute_time()` |
| Validation | `utils/validation/` | `validate_document()` |
| Converting to IR | `core/compiler.py` | `compile_ast_to_ir()` |
| Generating MIDI files | `codegen/midi_file.py` | `generate_midi_file()` |
| Real-time playback | `runtime/player.py` | `RealtimePlayer.play()` |

**For detailed architecture, see [@docs/developer-guide/architecture.md](docs/developer-guide/architecture.md)**

</architecture_quick_ref>

---

<development_guides>

## Developer Guides

**Complete implementation guides** (extracted for token efficiency):

- **[parser-patterns.md](docs/dev-guides/parser-patterns.md)** - How to add new MIDI commands, transformer patterns, grammar rules
- **[timing-system.md](docs/dev-guides/timing-system.md)** - Timing calculation formulas, all 4 timing paradigms, edge cases
- **[anti-patterns.md](docs/dev-guides/anti-patterns.md)** - Real bugs from our codebase, what went wrong, how to fix
- **[common-tasks.md](docs/dev-guides/common-tasks.md)** - Step-by-step workflows for frequent tasks

**When to read which guide:**

| Task | Read This Guide |
|------|----------------|
| Adding MIDI command | [parser-patterns.md](docs/dev-guides/parser-patterns.md) |
| Debugging timing | [timing-system.md](docs/dev-guides/timing-system.md) |
| Avoiding known bugs | [anti-patterns.md](docs/dev-guides/anti-patterns.md) |
| Creating device library | [common-tasks.md](docs/dev-guides/common-tasks.md) |

</development_guides>

---

<testing>

## Testing

### Test Markers

```python
@pytest.mark.unit           # 598 tests - Fast, isolated
@pytest.mark.integration    # 188 tests - Multi-component
@pytest.mark.e2e           # End-to-end workflows
@pytest.mark.cli           # CLI command tests
@pytest.mark.slow          # Long-running tests (>1 second)
```

### Running Tests

```bash
just test              # All tests with coverage
just test-unit         # Fast tests only
just test-integration  # Integration tests
pytest -m unit         # By marker
pytest -m "not slow"   # Skip slow tests
```

### Test Pattern

```python
class TestFeature:
    """Test feature description."""

    @pytest.mark.unit
    def test_basic_case(self, parser):
        """Test with inline MMD."""
        mml = """
[00:00.000]
- pc 1.0
"""
        doc = parser.parse_string(mml)
        assert len(doc.events) == 1
        assert doc.events[0]["type"] == "pc"
```

### Coverage

- **Current:** 72.53% overall
- **Target:** 80%+
- **Reports:** `just test-cov` generates HTML in `htmlcov/`

</testing>

---

<tool_permissions>

## Tool Permissions for Claude Code

### Safe for Autonomous Use

**Read/View:**

- All project files (`src/`, `tests/`, `examples/`, `devices/`, `docs/`)
- Configuration files (`pyproject.toml`, `justfile`, `CLAUDE.md`, `spec.md`)

**Write/Edit:**

- `src/` - Source code
- `tests/` - Test files
- `examples/` - Example MMD files
- `devices/` - Device library files
- `docs/` - Documentation
- `docs/dev-guides/` - Developer guides

**Bash Commands:**

- `just test*` - All test commands
- `just fmt`, `just lint`, `just check` - Code quality
- `pytest` - Run tests
- `ruff` - Format/lint
- `just run *` - CLI commands (compile, validate, play, inspect)

**Create:**

- Test files in `tests/`
- Example files in `examples/`
- Device libraries in `devices/`
- Documentation in `docs/`
- Developer guides in `docs/dev-guides/`

### Require Confirmation

**Write:**

- `pyproject.toml` - Dependency changes
- `justfile` - Build/test commands
- `CLAUDE.md` - This file
- `spec.md` - Language specification
- `.github/workflows/` - CI/CD configs

**Delete:**

- Any existing files (require explicit permission)

**Bash:**

- `uv add/remove` - Dependency changes
- Create new top-level directories

### Never Without Explicit Permission

**Dangerous Operations:**

- `rm -rf` - Recursive delete
- `git push` - Push to remote
- `git push --force` - Force push
- Delete `tests/` directory
- Delete core source files
- Modify GitHub Actions workflows
- System commands (sudo, etc.)

</tool_permissions>

---

<decision_protocol>

## Decision Protocol

<autonomous_actions>

**Claude should proceed WITHOUT asking when:**

- Bug has clear repro test case
- Fix is documented in [anti-patterns.md](docs/dev-guides/anti-patterns.md)
- Change is <50 lines in single module
- All tests pass after change
- Adding tests for existing features
- Improving documentation
- Code formatting/style fixes
- Error message improvements

</autonomous_actions>

<require_confirmation>

**Claude MUST ask before:**

- Grammar changes affecting .mmd file parsing (breaking change)
- Dependency additions (`uv add/remove`)
- Changes to `pyproject.toml`, `justfile`, `CLAUDE.md`, `spec.md`
- Breaking changes to public API
- Performance trade-offs (accuracy vs speed)
- Deleting existing files or directories
- Major refactoring affecting multiple modules

</require_confirmation>

</decision_protocol>

---

<language_specification>

## Language Specification

For complete MMD syntax and semantics, see **[@spec.md](spec.md)**

**Key implementation details Claude needs:**

### Command Types

- Abbreviated forms: `"pc"`, `"cc"`, `"note_on"`, `"pitch_bend"`, `"channel_pressure"`
- Full names in grammar: `program_change | pc`, `control_change | cc`

### Timing Resolution

All timing converters in `expansion/expander.py:_compute_absolute_time()`:

- Absolute: `[mm:ss.milliseconds]` → seconds * (ppq * tempo / 60)
- Musical: `[bars.beats.ticks]` → (bar-1) * beats_per_bar * ppq + (beat-1) * ppq + ticks
- Relative: `[+value unit]` → current_time + delta
- Simultaneous: `[@]` → current_time

### Validation Entry Points

- Document structure: `utils/validation/document_validator.py:validate_document()`
- Values: `utils/validation/value_validator.py:validate_*()` functions
- Timing: `expansion/expander.py:validate_timing_monotonic()`

**DO NOT duplicate syntax rules from spec.md** - reference it instead.

</language_specification>

---

<maintenance>

## CLAUDE.md Maintenance

**Update this file when:**

- New anti-pattern discovered → Add to [anti-patterns.md](docs/dev-guides/anti-patterns.md)
- New parser pattern emerges → Update [parser-patterns.md](docs/dev-guides/parser-patterns.md)
- Timing calculation changes → Update [timing-system.md](docs/dev-guides/timing-system.md)
- Common task identified → Add to [common-tasks.md](docs/dev-guides/common-tasks.md)
- Critical implementation rule added → Update `<critical_notes>` section above

**Use `#` command during session to add organically:**

Press `#` when Claude should remember something for future sessions.

</maintenance>

---

<examples_and_devices>

## Examples and Device Libraries

**Before implementing features, ALWAYS check existing examples:**

### Examples Directory

35 working MMD files in `examples/`:

- `00_basics/` - Start here (hello world, minimal MIDI)
- `01_timing/` - Timing paradigms (absolute, musical, relative)
- `02_midi_features/` - MIDI commands (CC, PC, pitch bend, etc.)
- `03_advanced/` - Loops, sweeps, aliases, computed values
- `04_device_libraries/` - Device library usage
- `05_generative/` - Random values, modulation (curves, waves, envelopes)
- `06_tutorials/` - Progressive learning path

### Device Libraries

6 device libraries in `devices/`:

- `quad_cortex.mmd` - Neural DSP Quad Cortex (86 aliases)
- `eventide_h90.mmd` - Eventide H90 (61 aliases)
- `helix.mmd` - Line 6 Helix (49 aliases)
- `hx_stomp.mmd`, `hx_effects.mmd`, `hx_stomp_xl.mmd` - HX family

**Use Read tool to examine these files for pattern guidance.**

</examples_and_devices>

---

<code_quality>

## Code Quality Standards

**Required for all new code:**

- ✅ **Type hints:** All code must have Python 3.12+ type annotations
- ✅ **Tests:** Required for all new features (unit + integration)
- ✅ **Formatting:** Run `just fmt` before commits (Ruff)
- ✅ **Linting:** No Ruff errors (`just lint`)
- ✅ **Type checking:** No mypy errors (`just typecheck`)
- ✅ **Coverage:** Maintain or improve 72.53% coverage
- ✅ **Documentation:** Update user guides if syntax changes
- ✅ **Examples:** Add examples for new features

**Pre-commit checklist:**

```bash
just check         # Format + lint + typecheck
just test          # All tests pass
just test-cov      # Coverage maintained/improved
```

</code_quality>

---

<claude_hooks>

## Claude Code Hooks

**Automated quality gates ensure all GitHub Actions CI checks pass.**

### Active Hooks

**Auto-format after edits** (`PostToolUse` → Edit/Write):
- Automatically runs `ruff format` on Python files
- Ensures consistent code style immediately

**Pre-commit checks** (`PreToolUse` → git commit):
- Runs `.claude/hooks/pre-commit.sh` before commits
- ✅ Step 1: Format check (`ruff format --check`)
- ✅ Step 2: Linting (`ruff check src tests`)
- ✅ Step 3: Type checking (`mypy src`)
- ✅ Step 4: Smoke tests (78 core tests in ~7s)

**Commits only proceed if all checks pass** - preventing CI failures.

### Testing Hooks

```bash
# Test pre-commit hook manually
./.claude/hooks/pre-commit.sh

# Expected: All 4 steps pass in ~18 seconds
```

### Documentation

- **[.claude/SUMMARY.md](.claude/SUMMARY.md)** - Implementation summary & test results
- **[.claude/HOOKS_SETUP.md](.claude/HOOKS_SETUP.md)** - Complete setup guide
- **[.claude/hooks/README.md](.claude/hooks/README.md)** - Hook documentation

**Hooks mirror GitHub Actions** - Same checks locally (18s) as in CI (3-5min).

</claude_hooks>

---

<reference>

## Reference Documentation

For detailed specifications and documentation:

- **[@spec.md](spec.md)** - Complete MMD language specification (1,650 lines)
- **[@docs/dev-guides/](docs/dev-guides/)** - Developer implementation guides
- **[@examples/README.md](examples/README.md)** - Example library with learning paths
- **[@docs/](docs/)** - User guides, tutorials, API references
- **[@devices/](devices/)** - Device library specifications
- **[@tests/](tests/)** - Test suite (1264 tests)

**Don't duplicate content from these files.** Link to them instead.

</reference>

---

**End of CLAUDE.md**

For questions or issues: [GitHub Issues](https://github.com/cjgdev/midi-markdown/issues)
