# Phase 6: Advanced Features & Generative Capabilities

**Status**: PLANNED
**Estimated Duration**: 6-8 weeks
**Target**: Complete generative music features, MIDI Learn workflow tool, and advanced automation capabilities

---

## Executive Summary

Phase 6 focuses on **generative music features** and **workflow automation** to maximize user value for live performance and composition. Based on comprehensive analysis of the current implementation (78.06% test coverage, 1,230 passing tests), this phase addresses the highest-priority gaps identified in spec.md while maintaining the project's "device-agnostic core" philosophy.

**Key Priorities**:
1. **Random value generation** - Generative music, humanization, variation
2. **Music theory scales** - Harmonic-aware algorithmic composition
3. **MIDI Learn mode** - Device library creation workflow tool
4. **Computed values in aliases** - Advanced device library capabilities
5. **Enhanced CLI options** - Improved user experience

---

## Current State Analysis

### ✅ Fully Implemented (85-90% spec compliance)
- Complete MIDI command coverage (all 7 message types)
- 4 timing paradigms (absolute, musical, relative, simultaneous)
- Robust alias system with conditionals, imports, nested expansion
- Variables, loops, and sweeps for automation
- Real-time MIDI playback with TUI (Phase 3)
- REPL interactive mode (Phase 2)
- Comprehensive diagnostic output (Phase 1, CSV/JSON/table)
- 6 device libraries (300+ combined aliases)

### 🔄 Partially Implemented
- Computed values in aliases (engine exists, wiring needed)
- Multi-line SysEx (grammar supports, needs testing)
- REPL test coverage (functionality works, pexpect tests flaky)
- TUI test coverage (30.61% display, 12.94% input - threading complexity)

### ❌ Not Implemented (High-Priority Gaps)
- **Random value generation** - Spec lines 508-513, 1257-1262
- **Music theory scales** - Spec lines 1257-1262
- **MIDI Learn mode** - Spec lines 1140-1142, 1240-1245
- **Enhanced modulation** (curves, waves, envelopes) - Spec lines 1246-1255
- **Document-level conditionals** - Spec lines 469-488
- **Advanced CLI options** (--split-tracks, --dry-run, etc.) - Spec lines 1061-1080

---

## Phase 6 Goals

### Primary Goals (Must-Have for v1.0)
1. ✅ Random value generation for generative music
2. ✅ Music theory scales for harmonic composition
3. ✅ MIDI Learn mode for device library creation
4. ✅ Computed values fully integrated into alias system
5. ✅ Enhanced CLI options for better UX

### Secondary Goals (Nice-to-Have)
6. ⚪ Document-level conditionals (@if/@elif/@else outside aliases)
7. ⚪ Enhanced modulation (curves, waves, envelopes)
8. ⚪ Fix REPL test flakiness (7 skipped tests)
9. ⚪ Improve TUI test coverage (currently 12-30%)
10. ⚪ Multi-line SysEx support (grammar exists, needs wiring)

### Stretch Goals (Future Phases)
- OSC integration (spec lines 1263-1268)
- MIDI file import (reverse engineering, spec lines 1121-1132)
- Advanced generative patterns (@random_pattern directive)
- Python/Lua scripting (spec lines 1269-1277)
- MIDI 2.0 support (spec lines 1293-1297)

---

## Implementation Stages

### Stage 1: Random Value Generation (Week 1)
**Priority**: HIGH | **Complexity**: LOW | **Effort**: 2-3 days

#### Objective
Implement `random(min, max)` expressions for generative music, humanization, and variation.

#### Scope
- Support random integer values for MIDI CC, velocity, note numbers
- Support random note names within octave ranges
- Integrate with existing expression evaluator (alias/computation.py)
- Seed control for reproducible randomness (optional)

#### Implementation Tasks
1. **Parser Enhancement** (2 hours)
   - Verify `random_expr` grammar rule (already exists in mml.lark line 309)
   - Add transformer method for `random_expr` → AST node
   - Create RandomExpression AST node in parser/ast_nodes.py

2. **Random Value Generator** (4 hours)
   - Create `expansion/random.py` module
   - Implement `RandomValueExpander` class
   - Support `random(min, max)` for integers
   - Support `random(note_min, note_max)` for note names
   - Optional: `random(min, max, seed=42)` for reproducibility

3. **Integration** (3 hours)
   - Add RandomValueExpander to expansion/expander.py pipeline
   - Wire into CommandExpander after variable substitution
   - Expand random() calls to concrete values before MIDI generation

4. **Testing** (5 hours)
   - 20+ unit tests in tests/unit/test_random.py
   - Random integer generation (CC values, velocities)
   - Random note generation (note names, MIDI numbers)
   - Range validation (min <= max)
   - Seed reproducibility tests
   - Integration tests with loops and sweeps

5. **Documentation** (2 hours)
   - Update docs/user-guide/mml-syntax.md
   - Add examples to examples/03_advanced/
   - Document use cases: humanization, generative patterns

#### Success Criteria
- [x] `random(0, 127)` generates valid MIDI values
- [x] `random(C3, C5)` generates notes within octave range
- [x] Random values vary across loop iterations
- [x] 20+ tests passing
- [x] Documentation with 3+ examples

#### Files Modified/Created
- NEW: `src/midi_markdown/expansion/random.py` (~80 lines)
- UPDATE: `src/midi_markdown/expansion/expander.py` (+15 lines)
- UPDATE: `src/midi_markdown/parser/transformer.py` (+20 lines)
- UPDATE: `src/midi_markdown/parser/ast_nodes.py` (+10 lines)
- NEW: `tests/unit/test_random.py` (~300 lines)
- NEW: `examples/03_advanced/random_humanization.mmd` (~100 lines)
- UPDATE: `docs/user-guide/mml-syntax.md` (+150 lines)

---

### Stage 2: Music Theory Scales (Week 1-2)
**Priority**: HIGH | **Complexity**: MEDIUM | **Effort**: 4-5 days

#### Objective
Add music theory scales for harmonic-aware generative composition.

#### Scope
- Major, minor, harmonic minor, melodic minor scales
- All 7 modes (Ionian, Dorian, Phrygian, Lydian, Mixolydian, Aeolian, Locrian)
- Pentatonic scales (major, minor)
- Blues scales
- Chromatic scale
- Support for `random(note_min, note_max, scale=C_major)`

#### Implementation Tasks
1. **Scale Database** (6 hours)
   - Create `utils/scales.py` module
   - Define ScaleDefinition dataclass (root, intervals)
   - Implement 20+ common scales:
     - Major, natural minor, harmonic minor, melodic minor
     - All 7 modes
     - Major pentatonic, minor pentatonic
     - Blues scale, whole tone, diminished
   - Note name parser (C#, Db, enharmonic equivalents)
   - Scale degree calculation (intervals from root)

2. **Scale-Aware Random** (4 hours)
   - Extend expansion/random.py with scale filtering
   - `random(C3, C5, scale=C_major)` → only major scale notes
   - `random(60, 84, scale=A_minor)` → MIDI numbers in A minor
   - Support custom scales: `scale=[0,2,4,5,7,9,11]` (semitone intervals)

3. **Chord Generation** (6 hours)
   - `chord(C4, major)` → [C4, E4, G4] (root, 3rd, 5th)
   - `chord(A3, minor7)` → [A3, C4, E4, G4]
   - Support inversions: `chord(C4, major, inversion=1)`
   - Common chord types: major, minor, dim, aug, maj7, min7, dom7, sus2, sus4

4. **Testing** (8 hours)
   - 30+ unit tests in tests/unit/test_scales.py
   - All scales generate correct intervals
   - Scale-aware random stays in scale
   - Chord generation (all common types)
   - Enharmonic equivalents (C# == Db)
   - Edge cases (scale boundaries, invalid roots)
   - Integration tests with random() and loops

5. **Documentation** (3 hours)
   - Create docs/user-guide/music-theory.md
   - Document all supported scales
   - Chord reference table
   - Generative composition examples

#### Success Criteria
- [x] 20+ scales defined with correct intervals
- [x] `random(C3, C5, scale=C_major)` generates only C major notes
- [x] `chord(C4, major)` generates [C4, E4, G4]
- [x] 30+ tests passing
- [x] Comprehensive music theory documentation

#### Files Modified/Created
- NEW: `src/midi_markdown/utils/scales.py` (~250 lines)
- UPDATE: `src/midi_markdown/expansion/random.py` (+100 lines)
- NEW: `tests/unit/test_scales.py` (~500 lines)
- NEW: `docs/user-guide/music-theory.md` (~800 lines)
- NEW: `examples/03_advanced/scale_exploration.mmd` (~200 lines)
- NEW: `examples/03_advanced/chord_progressions_auto.mmd` (~150 lines)

---

### Stage 3: MIDI Learn Mode (Week 2-3)
**Priority**: HIGH | **Complexity**: MEDIUM | **Effort**: 1.5-2 weeks

#### Objective
Create workflow tool for capturing MIDI messages from hardware and generating device library aliases.

#### Scope
- Monitor MIDI input port for messages
- Capture CC, PC, SysEx, note messages over time
- Detect patterns and repeated sequences
- Generate @alias definitions automatically
- Interactive mode: prompt user for alias names/descriptions
- Save to .mmd device library file

#### Implementation Tasks
1. **MIDI Input Monitoring** (8 hours)
   - Extend runtime/midi_io.py with input port support
   - Create MIDIInputMonitor class
   - Message capture with timestamps
   - Filter by message type (CC, PC, SysEx, notes)
   - Duration-based capture (30s, 1min, until stopped)

2. **Pattern Detection** (12 hours)
   - Create cli/learn/pattern_detector.py
   - Detect repeated CC/PC sequences (e.g., Bank MSB → Bank LSB → PC)
   - Group related messages (preset changes, snapshot loads)
   - Identify parameter ranges (CC min/max values)
   - SysEx pattern analysis (manufacturer ID, device ID, data patterns)

3. **Alias Generation** (10 hours)
   - Create cli/learn/alias_generator.py
   - Generate @alias templates from captured patterns
   - Infer parameter types (int ranges, enums for named values)
   - Add timing between messages (Bank/PC delay requirements)
   - Suggest parameter names based on CC numbers (CC 7 → {volume})

4. **Interactive CLI Command** (12 hours)
   - Create cli/commands/learn.py
   - `mmdc learn --device "My Device" --channel 1 --output device.mmd`
   - Interactive prompts:
     - "Press button/turn knob on device..."
     - "Enter alias name: preset_load"
     - "Enter parameter names (comma-separated): setlist,preset"
   - Real-time message display (Rich table)
   - Undo/redo message capture
   - Save to device library file

5. **Testing** (10 hours)
   - Mock MIDI input for unit tests
   - Pattern detection tests (Bank+PC sequences)
   - Alias generation tests (verify output quality)
   - CLI integration tests (full learn workflow)
   - 40+ tests total

6. **Documentation** (6 hours)
   - Create docs/user-guide/midi-learn.md
   - Step-by-step tutorial (learn Quad Cortex preset change)
   - Best practices (naming conventions, parameter organization)
   - Troubleshooting guide

#### Success Criteria
- [x] Capture MIDI messages from hardware device
- [x] Detect Bank+PC preset change patterns
- [x] Generate @alias with correct timing delays
- [x] Interactive prompts guide user through process
- [x] Save valid device library .mmd file
- [x] 40+ tests passing
- [x] Complete user tutorial

#### Files Modified/Created
- UPDATE: `src/midi_markdown/runtime/midi_io.py` (+150 lines, input support)
- NEW: `src/midi_markdown/cli/learn/` package
  - `pattern_detector.py` (~300 lines)
  - `alias_generator.py` (~250 lines)
- NEW: `src/midi_markdown/cli/commands/learn.py` (~400 lines)
- NEW: `tests/unit/test_pattern_detector.py` (~350 lines)
- NEW: `tests/unit/test_alias_generator.py` (~300 lines)
- NEW: `tests/integration/test_learn_command.py` (~200 lines)
- NEW: `docs/user-guide/midi-learn.md` (~600 lines)
- NEW: `examples/workflow/learn_device.md` (~300 lines, tutorial)

---

### Stage 4: Computed Values in Aliases (Week 3-4)
**Priority**: MEDIUM-HIGH | **Complexity**: MEDIUM | **Effort**: 3-5 days

#### Objective
Fully integrate computed value blocks into alias parameter expansion.

#### Scope
- Wire `computed_value` AST nodes from alias definitions into resolver
- Enable expression evaluation during parameter substitution
- Support complex transformations (BPM → CC value, time conversions)
- Critical for device libraries (Quad Cortex tempo mapping)

#### Implementation Tasks
1. **AST to Resolver Bridge** (6 hours)
   - Extend alias/resolver.py to handle ComputedValue AST nodes
   - Extract computed_value blocks from AliasDefinition
   - Pass to alias/computation.py evaluator
   - Store results in parameter context

2. **Expression Context** (4 hours)
   - Create ExpressionContext with available parameters
   - Support referencing other parameters: `{msb = int(preset / 128)}`
   - Symbol table for computed values
   - Dependency resolution (compute msb before using it)

3. **Advanced Transformations** (6 hours)
   - BPM/tempo conversions: `{cc_value = int((bpm - 40) * 127 / 260)}`
   - Time unit conversions: `{ticks = bars * ppq * 4}`
   - Range mapping: `{percent_to_midi = int(percent * 127 / 100)}`
   - Clamping: `{safe_value = max(0, min(127, raw_value))}`

4. **Testing** (8 hours)
   - 25+ integration tests in tests/integration/test_computed_aliases.py
   - BPM conversion example (Quad Cortex tempo CC)
   - Multi-parameter dependencies
   - Error handling (undefined variables, division by zero)
   - Real-world device library use cases

5. **Documentation** (3 hours)
   - Update docs/user-guide/alias-system.md
   - Computed value examples
   - Common transformation patterns
   - Device library best practices

#### Success Criteria
- [x] Computed value blocks execute during alias expansion
- [x] BPM → CC conversion works (spec.md line 605-608 example)
- [x] Multi-parameter dependencies resolve correctly
- [x] 25+ tests passing
- [x] Documentation with 5+ transformation examples

#### Files Modified/Created
- UPDATE: `src/midi_markdown/alias/resolver.py` (+120 lines)
- UPDATE: `src/midi_markdown/alias/models.py` (+30 lines, computed value tracking)
- NEW: `tests/integration/test_computed_aliases.py` (~400 lines)
- UPDATE: `docs/user-guide/alias-system.md` (+200 lines)
- UPDATE: `devices/quad_cortex.mmd` (+50 lines, tempo alias with computed value)

---

### Stage 5: Enhanced CLI Options (Week 4)
**Priority**: MEDIUM | **Complexity**: LOW-MEDIUM | **Effort**: 4-6 days

#### Objective
Implement advanced CLI options for improved user experience and workflow integration.

#### Scope
- `--split-tracks`: Output separate MIDI files per track
- `--dry-run`: Show what would be generated without writing files
- `--from/--to`: Compile time range (useful for large compositions)
- `-D VARIABLE=value`: Override @define values from command line

#### Implementation Tasks
1. **Track Splitting** (6 hours)
   - Add `--split-tracks` flag to compile command
   - Iterate IRProgram tracks in core/compiler.py
   - Generate separate MIDI files: `output_track1.mid`, `output_track2.mid`
   - Handle Format 0 (error: single track only)
   - Format 1/2: Split per track
   - Update file naming convention

2. **Dry Run Mode** (4 hours)
   - Add `--dry-run` flag to compile command
   - Run full compilation pipeline without file writes
   - Show Rich table with compilation stats:
     - Event count, track count, duration
     - MIDI file size estimate
     - Validation results
   - Display first 10 events as preview

3. **Time Range Filtering** (8 hours)
   - Add `--from/--to` options (musical time or absolute time)
   - Parse time formats: `--from 1.1.0` (bar 1), `--from 00:30.000` (30 seconds)
   - Filter events in core/compiler.py before MIDI generation
   - Adjust timing offsets (start from 0)
   - Use case: Extract chorus section, compile intro only

4. **Command-Line Defines** (6 hours)
   - Add `-D NAME=value` option
   - Parse before document processing
   - Inject into symbol table with highest precedence
   - Override document @define statements
   - Support: `-D TEMPO=140 -D CHANNEL=5`
   - Use case: Render same MMD with different parameters

5. **Testing** (10 hours)
   - Track splitting tests (multi-track Format 1/2)
   - Dry run validation (no files written)
   - Time range filtering (correct event selection)
   - Command-line defines (precedence, override)
   - 30+ CLI integration tests

6. **Documentation** (4 hours)
   - Update docs/cli-reference/compile.md
   - Add examples for each new option
   - Workflow scenarios (extracting sections, batch rendering)

#### Success Criteria
- [x] `--split-tracks` generates N files for N tracks
- [x] `--dry-run` shows stats without writing files
- [x] `--from 2.1.0 --to 4.1.0` extracts bars 2-4
- [x] `-D TEMPO=140` overrides document defines
- [x] 30+ tests passing
- [x] Documentation with workflow examples

#### Files Modified/Created
- UPDATE: `src/midi_markdown/cli/commands/compile.py` (+200 lines)
- UPDATE: `src/midi_markdown/core/compiler.py` (+80 lines, time filtering)
- UPDATE: `src/midi_markdown/expansion/variables.py` (+30 lines, CLI defines)
- NEW: `tests/integration/test_cli_advanced_options.py` (~450 lines)
- UPDATE: `docs/cli-reference/compile.md` (+250 lines)
- NEW: `docs/tutorials/workflow-advanced-cli.md` (~400 lines)

---

### Stage 6: Document-Level Conditionals (Week 5, Optional)
**Priority**: MEDIUM | **Complexity**: MEDIUM | **Effort**: 3-4 days

#### Objective
Implement @if/@elif/@else conditionals at document level (currently only work in aliases).

#### Scope
- Support conditionals outside @alias blocks
- Enable environment-specific MMD files (LIVE_MODE vs STUDIO_MODE)
- Conditional section inclusion based on @define variables

#### Implementation Tasks
1. **Transformer Enhancement** (6 hours)
   - Add transformer methods for if_clause, elif_clause, else_clause
   - Create ConditionalBlock AST node
   - Parse condition expressions
   - Handle nested conditionals

2. **Conditional Expander** (8 hours)
   - Create expansion/conditionals.py (separate from alias/conditionals.py)
   - Evaluate condition expressions using computation.py
   - Include/exclude events based on boolean result
   - Support: `@if ${LIVE_MODE} == 1`, `@if defined(QUAD_CORTEX)`

3. **Testing** (6 hours)
   - 20+ tests in tests/unit/test_document_conditionals.py
   - Simple conditionals (@if @else)
   - Nested conditionals
   - Variable evaluation
   - Integration with command-line defines (-D LIVE_MODE=1)

4. **Documentation** (3 hours)
   - Update docs/user-guide/mml-syntax.md
   - Conditional compilation examples
   - Live vs studio workflow

#### Success Criteria
- [x] @if/@elif/@else work at document level
- [x] Conditionals evaluate @define variables
- [x] Combine with -D CLI defines for flexible workflows
- [x] 20+ tests passing
- [x] Documentation with use cases

#### Files Modified/Created
- UPDATE: `src/midi_markdown/parser/transformer.py` (+60 lines)
- UPDATE: `src/midi_markdown/parser/ast_nodes.py` (+20 lines)
- NEW: `src/midi_markdown/expansion/conditionals.py` (~120 lines)
- UPDATE: `src/midi_markdown/expansion/expander.py` (+30 lines)
- NEW: `tests/unit/test_document_conditionals.py` (~350 lines)
- UPDATE: `docs/user-guide/mml-syntax.md` (+180 lines)

---

### Stage 7: Enhanced Modulation (Week 5-6, Optional)
**Priority**: MEDIUM-LOW | **Complexity**: HIGH | **Effort**: 1.5-2 weeks

#### Objective
Implement advanced modulation patterns: Bezier curves, waveforms, envelopes.

#### Scope
- Bezier curves for smooth parameter transitions
- Waveform generators (sine, triangle, square, sawtooth)
- ADSR envelopes for natural parameter automation
- Integration with sweep system

#### Implementation Tasks
1. **Curve Library** (10 hours)
   - Create utils/curves.py
   - Bezier curve interpolation (cubic, quadratic)
   - Easing functions (ease-in, ease-out, ease-in-out)
   - Control point specification

2. **Waveform Generator** (8 hours)
   - Create utils/waveforms.py
   - Sine, triangle, square, sawtooth waves
   - Frequency, amplitude, phase parameters
   - LFO (Low-Frequency Oscillator) for modulation

3. **Envelope Generator** (10 hours)
   - Create utils/envelopes.py
   - ADSR envelope (Attack, Decay, Sustain, Release)
   - Time-based stages
   - Output MIDI CC automation

4. **Syntax Integration** (12 hours)
   - Add curve(), wave(), envelope() expressions to grammar
   - Wire into sweep expansion
   - Example: `- cc 1.7 curve(bezier, 0, 100, 127, 30) from [00:00.000] to [00:04.000]`
   - Example: `- cc 1.1 wave(sine, 2Hz, 32, 96) for 8b`

5. **Testing** (12 hours)
   - Bezier curve interpolation tests
   - Waveform generation tests (verify periods, amplitudes)
   - ADSR envelope shape tests
   - Integration with sweep system
   - 40+ tests total

6. **Documentation** (6 hours)
   - Create docs/user-guide/advanced-modulation.md
   - Curve/wave/envelope reference
   - Musical examples (vibrato, tremolo, filter sweeps)

#### Success Criteria
- [x] Bezier curves generate smooth CC transitions
- [x] Sine wave LFO generates correct periods
- [x] ADSR envelope creates natural parameter automation
- [x] 40+ tests passing
- [x] Comprehensive modulation documentation

#### Files Modified/Created
- NEW: `src/midi_markdown/utils/curves.py` (~200 lines)
- NEW: `src/midi_markdown/utils/waveforms.py` (~180 lines)
- NEW: `src/midi_markdown/utils/envelopes.py` (~220 lines)
- UPDATE: `src/midi_markdown/expansion/sweeps.py` (+150 lines)
- UPDATE: `src/midi_markdown/parser/transformer.py` (+80 lines)
- NEW: `tests/unit/test_curves.py` (~300 lines)
- NEW: `tests/unit/test_waveforms.py` (~280 lines)
- NEW: `tests/unit/test_envelopes.py` (~320 lines)
- NEW: `docs/user-guide/advanced-modulation.md` (~900 lines)
- NEW: `examples/03_advanced/modulation_showcase.mmd` (~350 lines)

---

### Stage 8: Testing & Polish (Week 6-7)
**Priority**: HIGH | **Complexity**: MEDIUM | **Effort**: 1-1.5 weeks

#### Objective
Achieve 85%+ test coverage, fix flaky tests, improve test reliability.

#### Scope
- Fix 7 flaky REPL pexpect tests
- Improve TUI test coverage (currently 12-30%)
- Add edge case tests for new features
- Performance regression tests
- Integration test suite expansion

#### Implementation Tasks
1. **REPL Test Fixes** (8 hours)
   - Replace pexpect with mock-based unit tests
   - Or add pytest-timeout and retry logic
   - Focus on REPL component testing vs E2E
   - Target: All 7 skipped tests passing or properly mocked

2. **TUI Test Coverage** (10 hours)
   - Mock threading for display manager tests
   - Mock keyboard input for input handler tests
   - State management tests (already 100% coverage)
   - Target: 70%+ coverage for display.py and input.py

3. **Edge Case Testing** (12 hours)
   - Random value boundary tests
   - Scale edge cases (chromatic, custom intervals)
   - MIDI Learn pattern detection edge cases
   - Computed value error handling
   - CLI option combinations

4. **Performance Benchmarks** (8 hours)
   - Benchmark random value generation (should be <1ms)
   - Benchmark scale calculations
   - Benchmark large file compilation with new features
   - Regression tests vs Phase 5 baseline

5. **Integration Tests** (10 hours)
   - Full workflow tests (MML → compile → play → learn)
   - Cross-feature tests (random + scales + loops)
   - Real device library usage tests
   - CLI command chaining

#### Success Criteria
- [x] Test coverage 85%+ (up from 78.06%)
- [x] 0 flaky tests (all skipped tests resolved)
- [x] TUI coverage 70%+ (up from 12-30%)
- [x] Performance benchmarks established
- [x] 100+ new tests added

#### Files Modified/Created
- UPDATE: `tests/integration/test_repl_end_to_end.py` (fix 7 skipped tests)
- NEW: `tests/unit/test_tui_display_mocked.py` (~200 lines)
- NEW: `tests/unit/test_tui_input_mocked.py` (~180 lines)
- NEW: `tests/integration/test_phase6_workflows.py` (~400 lines)
- NEW: `benchmarks/benchmark_phase6.py` (~250 lines)
- UPDATE: Multiple test files with edge case coverage

---

### Stage 9: Documentation & Examples (Week 7-8)
**Priority**: HIGH | **Complexity**: LOW | **Effort**: 1 week

#### Objective
Create comprehensive documentation for all Phase 6 features with real-world examples.

#### Scope
- User guides for new features
- Updated CLI reference
- Example library expansion
- Tutorial content
- Video walkthroughs (optional)

#### Implementation Tasks
1. **User Guide Updates** (12 hours)
   - Update docs/user-guide/mml-syntax.md (random, scales, chords)
   - Create docs/user-guide/generative-music.md (composition techniques)
   - Create docs/user-guide/midi-learn.md (device library workflow)
   - Update docs/user-guide/alias-system.md (computed values)

2. **CLI Reference Updates** (6 hours)
   - Update docs/cli-reference/compile.md (new options)
   - Create docs/cli-reference/learn.md (MIDI Learn command)
   - Update docs/cli-reference/overview.md (Phase 6 feature summary)

3. **Example Library** (10 hours)
   - Create examples/04_generative/
     - random_melody.mmd (humanized melodies)
     - scale_walk.mmd (walking bass in scale)
     - algorithmic_drums.mmd (random velocities, swing)
     - generative_ambient.mmd (random + scales + long notes)
   - Create examples/05_workflow/
     - learn_device_tutorial.md (step-by-step MIDI Learn)
     - multi_render_workflow.mmd (using -D defines)

4. **Tutorial Content** (10 hours)
   - Create docs/tutorials/generative-composition.md
   - Create docs/tutorials/device-library-creation.md
   - Create docs/tutorials/advanced-cli-workflows.md
   - Update docs/tutorials/device-control.md (use computed values)

5. **Reference Documentation** (6 hours)
   - Create docs/reference/scale-reference.md (all scales + intervals)
   - Create docs/reference/chord-reference.md (all chord types)
   - Update docs/reference/faq.md (Phase 6 questions)

6. **Visual Documentation** (8 hours, optional)
   - Screenshots of MIDI Learn interactive prompts
   - Terminal recordings (asciinema) of workflows
   - Diagrams of pattern detection logic
   - Video walkthrough (10-15 minutes)

#### Success Criteria
- [x] All new features documented
- [x] 10+ new example files
- [x] 3+ new tutorials
- [x] Updated FAQ with Phase 6 content
- [x] Professional-quality documentation

#### Files Modified/Created
- UPDATE: `docs/user-guide/mml-syntax.md` (+300 lines)
- NEW: `docs/user-guide/generative-music.md` (~1,200 lines)
- NEW: `docs/user-guide/midi-learn.md` (~800 lines)
- UPDATE: `docs/user-guide/alias-system.md` (+250 lines)
- UPDATE: `docs/cli-reference/compile.md` (+200 lines)
- NEW: `docs/cli-reference/learn.md` (~600 lines)
- NEW: `docs/tutorials/generative-composition.md` (~1,000 lines)
- NEW: `docs/tutorials/device-library-creation.md` (~900 lines)
- NEW: `docs/tutorials/advanced-cli-workflows.md` (~700 lines)
- NEW: `docs/reference/scale-reference.md` (~500 lines)
- NEW: `docs/reference/chord-reference.md` (~400 lines)
- UPDATE: `docs/reference/faq.md` (+300 lines)
- NEW: 10+ example files in examples/04_generative/ and examples/05_workflow/

---

## Success Metrics

### Phase 6 Completion Criteria

#### Must-Have (v1.0 Blockers)
- [x] Random value generation implemented and tested (20+ tests)
- [x] Music theory scales implemented (20+ scales, 30+ tests)
- [x] MIDI Learn command functional (40+ tests)
- [x] Computed values fully integrated (25+ tests)
- [x] Enhanced CLI options working (30+ tests)
- [x] Test coverage ≥ 85% (up from 78.06%)
- [x] Documentation complete for all features
- [x] 10+ new examples demonstrating features

#### Nice-to-Have (Can Defer to v1.1)
- [ ] Document-level conditionals (20+ tests)
- [ ] Enhanced modulation (40+ tests)
- [ ] REPL test flakiness resolved (0 skipped tests)
- [ ] TUI test coverage ≥ 70%
- [ ] Video tutorial content

#### Quality Gates
- **Test Count**: 1,500+ total tests (up from 1,230)
- **Test Coverage**: 85%+ (up from 78.06%)
- **Performance**: No regressions vs Phase 5 baseline
- **Documentation**: 100% feature coverage
- **Examples**: 40+ total examples (up from 31)
- **Device Libraries**: 6+ (no change, but using computed values)

---

## Risk Assessment

### High Risk
1. **MIDI Learn Complexity** - Pattern detection may be harder than estimated
   - **Mitigation**: Start with simple patterns (Bank+PC), iterate to complex
   - **Contingency**: Ship with basic pattern detection, enhance in v1.1

2. **Scale Integration** - Random + scales may have edge cases
   - **Mitigation**: Comprehensive testing with all scale types
   - **Contingency**: Start with common scales (major, minor), add exotic later

### Medium Risk
1. **Computed Values Wiring** - Alias resolver changes are delicate
   - **Mitigation**: Incremental implementation with test-driven approach
   - **Contingency**: Document limitations if full implementation blocked

2. **TUI Test Coverage** - Threading makes testing difficult
   - **Mitigation**: Mock threading primitives
   - **Contingency**: Accept lower TUI coverage (50%+) if 70% infeasible

### Low Risk
1. **Random Value Generation** - Straightforward feature
2. **CLI Options** - Mostly plumbing work
3. **Documentation** - Time-consuming but low technical risk

---

## Timeline & Milestones

### Week 1: Foundation (Random + Scales)
- **Days 1-3**: Random value generation (Stage 1)
- **Days 4-7**: Music theory scales (Stage 2)
- **Milestone**: Generative music capabilities functional

### Week 2-3: MIDI Learn (Critical Feature)
- **Days 8-14**: MIDI input monitoring + pattern detection
- **Days 15-21**: Alias generation + interactive CLI
- **Milestone**: Device library creation workflow complete

### Week 3-4: Computed Values + CLI
- **Days 22-26**: Computed values in aliases (Stage 4)
- **Days 27-31**: Enhanced CLI options (Stage 5)
- **Milestone**: Advanced alias capabilities + UX improvements

### Week 5: Optional Features
- **Days 32-35**: Document-level conditionals (Stage 6, optional)
- **Days 36-38**: Start enhanced modulation (Stage 7, optional)
- **Milestone**: Optional features in progress

### Week 6-7: Testing & Documentation
- **Days 39-45**: Testing & polish (Stage 8)
- **Days 46-52**: Documentation & examples (Stage 9)
- **Milestone**: Phase 6 complete, ready for v1.0

### Week 8: Buffer & Release Prep
- **Days 53-56**: Bug fixes, final polish
- **Milestone**: v1.0 release candidate

---

## Dependencies & Prerequisites

### External Dependencies
- No new external libraries required for core features
- Optional: matplotlib for waveform visualization in docs
- Optional: asciinema for terminal recordings

### Internal Dependencies
- Phase 3 (Real-time MIDI) must be complete ✅
- Phase 2 (REPL) must be complete ✅ (with flaky tests acceptable)
- Test infrastructure from Phase 5 ✅
- Device libraries from Phase 5 ✅

### Team Resources
- 1 developer full-time for 6-8 weeks
- Or 2 developers part-time (20 hrs/week each)

---

## Post-Phase 6 Roadmap

### v1.0 Release (After Phase 6)
- All Phase 6 features complete
- 85%+ test coverage
- Comprehensive documentation
- Production-ready for public release

### v1.1 Features (3-6 months)
- Enhanced modulation (curves, waves, envelopes) if not in v1.0
- OSC integration (DAW control)
- Advanced generative patterns (@random_pattern directive)
- Community device library submissions

### v2.0 Features (6-12 months)
- MIDI file import (reverse engineering)
- Visual editor (GUI)
- Python/Lua scripting for advanced users
- MIDI 2.0 support
- Mobile companion app (preset management)

---

## Appendix

### Code Statistics Projections

**Current** (Post-Phase 5):
- Source code: ~15,000 lines
- Test code: ~10,700 lines
- Documentation: ~20,000 lines
- Examples: ~39,000 lines

**Projected** (Post-Phase 6):
- Source code: ~18,500 lines (+3,500, +23%)
- Test code: ~15,000 lines (+4,300, +40%)
- Documentation: ~27,000 lines (+7,000, +35%)
- Examples: ~45,000 lines (+6,000, +15%)

**Total**: ~105,500 lines of content (up from ~84,700, +25%)

### Key Stakeholders

- **Musicians/Composers**: Random, scales, chords for composition
- **Live Performers**: MIDI Learn for device library creation
- **Power Users**: Computed values, advanced CLI options
- **Device Library Authors**: MIDI Learn + computed values workflow
- **Developers**: Clean codebase, high test coverage

---

**Phase 6 Plan Created**: November 9, 2025
**Estimated Completion**: January 2026 (v1.0 release)
**Plan Author**: Claude (Sonnet 4.5) + User Collaboration
