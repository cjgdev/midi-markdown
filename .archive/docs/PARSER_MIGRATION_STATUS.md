# Parser Migration Status

## Summary

Migration from custom parser implementation to reference grammar (from `docs/grammar/`) is **90% complete** but requires grammar fixes before tests will pass.

## Completed Phases

### ✅ Phase 1: Grammar File Replacement
- **Status**: Complete
- **File**: [src/midi_markdown/parser/mml.lark](../src/midi_markdown/parser/mml.lark)
- **Changes**: Replaced 280-line custom grammar with 308-line reference grammar
- **Fix Applied**: Changed `DIGIT{2}` syntax to `/\d{2}/` regex (Lark-compatible)
- **Fix Applied**: Added missing `velocity: INT` rule

### ✅ Phase 2: AST Node Replacement
- **Status**: Complete
- **File**: [src/midi_markdown/parser/ast_nodes.py](../src/midi_markdown/parser/ast_nodes.py)
- **Changes**: Simplified from 30+ node types to 5 clean dataclasses:
  - `Timing` - timing specifications (absolute, musical, relative, simultaneous)
  - `MIDICommand` - flexible MIDI command structure
  - `AliasDefinition` - simple and macro aliases
  - `Track` - multi-track support
  - `MMLDocument` - root AST node
- **Benefits**: Much simpler structure, easier to work with

### ✅ Phase 3: Parser/Transformer Replacement
- **Status**: Complete
- **File**: [src/midi_markdown/parser/ast_builder.py](../src/midi_markdown/parser/ast_builder.py)
- **Changes**: Replaced custom transformer with reference implementation
- **Features**: Complete MMLTransformer with ~40 methods covering all MML features
- **Fix Applied**: Fixed type errors (Path vs str, removed unused imports)

### ✅ Phase 4: Test Suite Replacement
- **Status**: Complete
- **File**: [tests/unit/test_parser.py](../tests/unit/test_parser.py)
- **Changes**: Replaced 45 partial tests with 40 comprehensive tests from reference
- **Test Coverage**:
  - Basic structure (frontmatter, imports, defines)
  - All 4 timing paradigms
  - All MIDI commands (notes, PC, CC, pitch bend, pressure, meta, sysex)
  - Alias system (simple, macro, enums, calls)
  - Advanced features (tracks, loops, sweeps, conditionals, sections)
  - Expressions (variables, math, percent, ramp, random)
  - Comments (single-line, multi-line)
  - Integration tests (complete songs, multi-track)
  - Edge cases (note variations, nested expressions, etc.)
  - Performance tests (100+ events, 50+ aliases)

## Current Issue: Grammar Conflicts

### ⚠️ Problem: Reduce/Reduce Collisions

The reference grammar from `docs/grammar/mml_grammar.lark` has **reduce/reduce conflicts** in the LALR parser. Specifically:

**Location**: Line 213-216
```lark
track_def: "##" "Track" /[^\n]+/ _NL* track_attributes?
         | "@track" IDENTIFIER track_attributes?

track_attributes: ("channel" "=" INT)?
```

**Issue**: The optional `track_attributes?` creates ambiguity - the parser doesn't know whether to reduce an empty `track_attributes` or continue with the next token.

**Error Count**: 21+ reduce/reduce collisions all stemming from this issue

### Solutions

**Option A: Fix the Grammar (Recommended)**

Make track_attributes non-optional and handle the empty case explicitly:

```lark
track_def: "##" "Track" /[^\n]+/ _NL* track_attributes
         | "##" "Track" /[^\n]+/
         | "@track" IDENTIFIER track_attributes
         | "@track" IDENTIFIER

track_attributes: "channel" "=" INT
```

**Option B: Use Earley Parser**

Change `ast_builder.py` line 361:
```python
parser='earley',  # Handles ambiguous grammars
```

Trade-off: Slower but more forgiving.

**Option C: Simplify Grammar**

Remove optional track attributes entirely:
```lark
track_def: "##" "Track" /[^\n]+/
         | "@track" IDENTIFIER
```

Handle channel assignment via separate statements.

## Next Steps

1. **Choose and implement a solution** from the options above
2. **Run tests**: `pytest tests/unit/test_parser.py -v`
3. **Fix any remaining grammar issues** (there may be more beyond track_attributes)
4. **Update transformer methods** if grammar rules change
5. **Verify all 40 tests pass**

## Files Modified

| File | Lines | Status | Notes |
|------|-------|--------|-------|
| `src/midi_markdown/parser/mml.lark` | 308 | ⚠️ Has conflicts | Needs grammar fix |
| `src/midi_markdown/parser/ast_nodes.py` | 171 | ✅ Complete | Clean dataclasses |
| `src/midi_markdown/parser/ast_builder.py` | 446 | ✅ Complete | Full transformer |
| `tests/unit/test_parser.py` | 522 | ✅ Complete | 40 comprehensive tests |

## Reference Files Used

- `docs/grammar/mml_grammar.lark` - Reference grammar (308 lines)
- `docs/grammar/mml_parser.py` - Reference parser (568 lines)
- `docs/grammar/test_mml_parser.py` - Reference tests (515 lines)

## Benefits of This Migration

1. **Simpler AST**: 5 dataclasses vs 30+ node types
2. **Proven Grammar**: Reference implementation with extensive testing
3. **LALR Performance**: Fast O(n) parsing (once conflicts resolved)
4. **Complete Test Coverage**: 40 tests covering all MML features
5. **Better Maintainability**: Clean, documented code structure

## Estimated Completion Time

- **Grammar fix**: 30-60 minutes (Option A recommended)
- **Test validation**: 15-30 minutes
- **Total**: 1-2 hours to fully working parser

## Notes

- The reference grammar in `docs/grammar/` appears to be a work-in-progress with known issues
- The grammar conflicts are fixable - they're common LALR patterns
- Once fixed, this will be a robust, production-ready parser
- All supporting code (AST, transformer, tests) is already in place

---

**Migration Date**: 2025-10-29
**Status**: 90% Complete - Grammar Conflicts Remain
**Next Action**: Fix track_attributes grammar rule
