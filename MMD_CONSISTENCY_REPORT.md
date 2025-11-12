# MMD/MML Consistency Report

## Executive Summary

Found **15 user-facing documentation files** using the incorrect abbreviation "MML" instead of "MMD". The project is officially named "**MIDI Markdown (MMD)**" as stated in CLAUDE.md (project context).

**Files with inconsistencies**: 15
**Severity**: High (impacts user documentation and brand consistency)
**Quick fixes needed**: 15 files, primarily in first-paragraph introductions

---

## Critical Finding: Inconsistent Naming

The project uses **MMD** as the official abbreviation (confirmed in CLAUDE.md), but most user-facing documentation uses **MML** instead. This creates confusion for users and inconsistent branding.

### Current State:
- ✅ **Correct (MMD)**: 1 file (frontmatter.md)
- ❌ **Incorrect (MML)**: 15 files
- ⚠️ **Mixed**: 2 files (both MML and MMD in same file)

---

## Files Requiring Changes

### Category 1: User-Facing Documentation (Change MML → MMD)

#### 1. **docs/index.md** (Line 3)
**Current:**
```markdown
Welcome to the MIDI Markdown (MML) documentation. MMD is a human-readable...
```
**Issue:** Uses "MML" in first sentence, then switches to "MMD" later - MIXED
**Type:** User-facing (documentation homepage)
**Recommendation:** Change to "MIDI Markdown (MMD)" consistently

---

#### 2. **docs/user-guide/mml-syntax.md** (Line 6)
**Current:**
```markdown
Complete reference for MIDI Markdown (MML) syntax.
```
**Issue:** Uses incorrect abbreviation
**Type:** User-facing (core syntax guide)
**Recommendation:** Change to "MIDI Markdown (MMD) syntax"

---

#### 3. **docs/reference/specification.md** (Lines 1, 22)
**Current:**
```markdown
# MIDI Markdown (MML) Specification
...
MIDI Markdown (MML) is a human-readable, text-based format...
```
**Issue:** Primary specification document uses MML
**Type:** User-facing (core reference)
**Recommendation:** Change all instances to "MIDI Markdown (MMD)"

---

#### 4. **docs/user-guide/alias-system.md** (Line 16)
**Current:**
```markdown
The MIDI Markdown (MML) alias system allows you to create reusable...
```
**Issue:** Uses MML in core feature documentation
**Type:** User-facing (feature guide)
**Recommendation:** Change to "MIDI Markdown (MMD) alias system"

---

#### 5. **docs/reference/faq.md** (Line 12)
**Current:**
```markdown
### What is MIDI Markdown (MML)?
```
**Issue:** FAQ uses incorrect abbreviation
**Type:** User-facing (support documentation)
**Recommendation:** Change to "What is MIDI Markdown (MMD)?"

---

#### 6. **docs/getting-started/quickstart.md** (Line 5)
**Current:**
```markdown
## What is MML?
...
MIDI Markdown (MML) is a human-readable, text-based format...
```
**Issue:** Quickstart uses MML twice
**Type:** User-facing (onboarding/first steps)
**Recommendation:** Change to "What is MMD?" and "MIDI Markdown (MMD)"

---

#### 7. **docs/getting-started/installation.md** (Line 49)
**Current:**
```markdown
# Output: MIDI Markdown (MML) Compiler
```
**Issue:** Installation guide uses MML
**Type:** User-facing (setup guide)
**Recommendation:** Change to "MIDI Markdown (MMD) Compiler"

---

#### 8. **docs/reference/random-expressions.md** (Line 3)
**Current:**
```markdown
Complete API reference for `random()` expressions in MIDI Markdown (MML).
```
**Issue:** Feature API reference uses MML
**Type:** User-facing (feature API reference)
**Recommendation:** Change to "MIDI Markdown (MMD)"

---

#### 9. **docs/developer-guide/contributing.md** (Line 6)
**Current:**
```markdown
Thank you for your interest in contributing to MIDI Markdown (MML)!
```
**Issue:** Contributing guide uses MML
**Type:** User-facing (community contribution guide)
**Recommendation:** Change to "MIDI Markdown (MMD)"

---

#### 10. **docs/cli-reference/overview.md** (Line 180)
**Current:**
```markdown
MIDI Markdown (MML) Compiler
```
**Issue:** CLI reference uses MML
**Type:** User-facing (command reference)
**Recommendation:** Change to "MIDI Markdown (MMD) Compiler"

---

#### 11. **docs/developer-guide/architecture-overview.md** (Line 3)
**Current:**
```markdown
This document describes the complete architecture of the MIDI Markdown (MML) compiler...
```
**Issue:** Architecture overview uses MML
**Type:** Developer documentation (but still user-visible)
**Recommendation:** Change to "MIDI Markdown (MMD)"

---

#### 12. **docs/developer-guide/cli-design.md** (Line 3)
**Current:**
```markdown
**MIDI Markdown (MML) Command-Line Interface Design Standards**
```
**Issue:** CLI design document uses MML
**Type:** Developer documentation
**Recommendation:** Change to "MIDI Markdown (MMD)"

---

#### 13. **docs/developer-guide/architecture/lexer.md** (Line 5)
**Current:**
```markdown
This document defines the complete design and implementation strategy for the MIDI Markdown (MML) lexer...
```
**Issue:** Technical architecture uses MML
**Type:** Developer documentation
**Recommendation:** Change to "MIDI Markdown (MMD)"

---

#### 14. **docs/architecture.md** (Line 3)
**Current:**
```markdown
This document describes the complete architecture of the MIDI Markdown (MML) compiler...
```
**Issue:** Duplicate architecture doc uses MML
**Type:** Developer documentation
**Recommendation:** Change to "MIDI Markdown (MMD)"

---

#### 15. **README.md** (Lines 25, 42, 44, 56, 65)
**Current:**
```markdown
- [Why MML?](#why-mml)
...
**The Solution**: MIDI Markdown (MML) provides human-readable...
**Why Choose MML?**
...
# Without MML: cryptic raw MIDI
# With MML: semantic, obvious
...
## Why MML?
...
**Why musicians choose MML:**
```
**Issue:** Project README uses MML extensively (7+ occurrences)
**Type:** User-facing (primary project documentation)
**Recommendation:** Change all instances to "MMD"
**Details:**
  - Line 25: "Why MML?" section header → "Why MMD?"
  - Line 42: "MIDI Markdown (MML)" → "MIDI Markdown (MMD)"
  - Line 44: "Why Choose MML?" → "Why Choose MMD?"
  - Line 56: "Without MML" → "Without MMD" 
  - Line 56: "With MML" → "With MMD"
  - Line 65: "## Why MML?" → "## Why MMD?"
  - Line 78: "Why musicians choose MML" → "Why musicians choose MMD"

---

### Category 2: Reference Files (Archive/Non-Critical)

#### 16. **devices/README_HELIX_FAMILY.md** (Line 3)
**Current:**
```markdown
This directory contains comprehensive MIDI Markdown (MML) device profiles...
```
**Issue:** Device documentation uses MML
**Type:** Device library documentation
**Recommendation:** Change to "MIDI Markdown (MMD)"

---

#### 17. **spec.md** (Lines 1, 22)
**Current:**
```markdown
# MIDI Markdown (MML) Specification
...
MIDI Markdown (MML) is a human-readable, text-based format...
```
**Issue:** Main specification file uses MML
**Type:** Reference specification (used by both users and developers)
**Recommendation:** Change to "MIDI Markdown (MMD)"

---

## Technical References (DO NOT CHANGE)

These should remain unchanged - they are class/code references:
- `MMLParser` (Python class name) - ✅ Keep as-is
- `MMLTransformer` (Python class name) - ✅ Keep as-is
- `mml.lark` (grammar file) - ✅ Keep as-is (filename convention)
- `mml-syntax.md` (documentation file) - ⚠️ **Consider renaming** to `mmnd-syntax.md` for consistency

---

## File Naming Inconsistency

**File: `docs/user-guide/mml-syntax.md`**
- **Current:** `mml-syntax.md`
- **Recommendation:** Consider renaming to `mmd-syntax.md` for consistency
- **Impact:** Would require updates to any links pointing to this file
- **Priority:** Medium (aesthetic consistency)

---

## Summary Table

| File | Line(s) | Type | Current | Should Be | Priority |
|------|---------|------|---------|-----------|----------|
| docs/index.md | 3 | User | MIDI Markdown (MML) | MIDI Markdown (MMD) | High |
| docs/user-guide/mml-syntax.md | 6 | User | MIDI Markdown (MML) | MIDI Markdown (MMD) | High |
| docs/reference/specification.md | 1, 22 | User | MIDI Markdown (MML) | MIDI Markdown (MMD) | High |
| docs/user-guide/alias-system.md | 16 | User | MIDI Markdown (MML) | MIDI Markdown (MMD) | High |
| docs/reference/faq.md | 12 | User | What is MIDI Markdown (MML)? | What is MIDI Markdown (MMD)? | High |
| docs/getting-started/quickstart.md | 5, 7 | User | What is MML? / MIDI Markdown (MML) | What is MMD? / MIDI Markdown (MMD) | High |
| docs/getting-started/installation.md | 49 | User | MIDI Markdown (MML) Compiler | MIDI Markdown (MMD) Compiler | High |
| docs/reference/random-expressions.md | 3 | User | MIDI Markdown (MML) | MIDI Markdown (MMD) | High |
| docs/developer-guide/contributing.md | 6 | User | MIDI Markdown (MML) | MIDI Markdown (MMD) | High |
| docs/cli-reference/overview.md | 180 | User | MIDI Markdown (MML) | MIDI Markdown (MMD) | High |
| docs/developer-guide/architecture-overview.md | 3 | Dev | MIDI Markdown (MML) | MIDI Markdown (MMD) | Medium |
| docs/developer-guide/cli-design.md | 3 | Dev | MIDI Markdown (MML) | MIDI Markdown (MMD) | Medium |
| docs/developer-guide/architecture/lexer.md | 5 | Dev | MIDI Markdown (MML) | MIDI Markdown (MMD) | Medium |
| docs/architecture.md | 3 | Dev | MIDI Markdown (MML) | MIDI Markdown (MMD) | Medium |
| README.md | 25, 42, 44, 56, 65, 78 | User | MML (7 instances) | MMD | High |
| devices/README_HELIX_FAMILY.md | 3 | Device | MIDI Markdown (MML) | MIDI Markdown (MMD) | Medium |
| spec.md | 1, 22 | Reference | MIDI Markdown (MML) | MIDI Markdown (MMD) | High |

---

## Recommended Action Plan

### Phase 1: Critical User-Facing (High Priority)
Fix these files first - they directly impact users:
1. **README.md** - Fix 7 instances
2. **docs/index.md** - Fix introduction
3. **docs/getting-started/quickstart.md** - Fix first-time user experience
4. **spec.md** - Fix specification document
5. **docs/reference/specification.md** - Fix comprehensive reference

### Phase 2: Supporting Documentation (High Priority)
6. **docs/user-guide/mml-syntax.md** - Core syntax guide
7. **docs/user-guide/alias-system.md** - Feature documentation
8. **docs/reference/faq.md** - Support documentation
9. **docs/getting-started/installation.md** - Setup documentation
10. **docs/reference/random-expressions.md** - Feature API reference

### Phase 3: Developer Documentation (Medium Priority)
11. **docs/developer-guide/contributing.md** - Community docs
12. **docs/cli-reference/overview.md** - CLI reference
13. **docs/developer-guide/architecture.md** - Architecture documentation
14. **docs/developer-guide/architecture-overview.md** - Overview
15. **docs/developer-guide/cli-design.md** - Design standards
16. **docs/developer-guide/architecture/lexer.md** - Technical documentation

### Phase 4: Optional File Renames (Low Priority)
- Consider renaming `docs/user-guide/mml-syntax.md` → `docs/user-guide/mmd-syntax.md`

---

## Notes

1. **Class Names Preserved**: `MMLParser`, `MMLTransformer`, and other Python classes should retain their names - these are technical implementation details.

2. **Grammar File Preserved**: `parser/mml.lark` should retain its name following Lark conventions.

3. **CLAUDE.md Authority**: The project context (CLAUDE.md) explicitly uses "MIDI Markdown (MMD)" - this is the source of truth for the correct abbreviation.

4. **Batch Fix Possible**: All instances can be fixed using find/replace operations since they follow consistent patterns:
   - Search: `MIDI Markdown \(MML\)`
   - Replace: `MIDI Markdown (MMD)`
   - Search: `What is MML\?`
   - Replace: `What is MMD?`
   - Search: `\bMML\b` (word boundary, context-dependent)

---

## Implementation Notes for Developers

When fixing these files:
1. Use case-sensitive find/replace to preserve class names
2. Check for context - some uses of "MML" might be abbreviations in section headers
3. Update table of contents and link anchors if section names change
4. Run documentation build to verify no broken links
5. Consider adding a style guide note to CLAUDE.md about MMD vs MML naming conventions

