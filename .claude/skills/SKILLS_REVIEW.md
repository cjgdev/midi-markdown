# Agent Skills Review and Improvement Plan

**Date**: 2025-11-12
**Status**: Needs Immediate Attention

## Executive Summary

Current skills in `.claude/skills/` do not comply with Anthropic's Agent Skills specification. Critical issues include missing required YAML frontmatter, exceeding recommended file size limits, and not following progressive disclosure patterns.

## Critical Issues Found

### 1. ❌ Missing Required YAML Frontmatter

**Current State**: Both skills start with markdown headings instead of YAML frontmatter.

**Requirement**: All skills MUST have YAML frontmatter with required fields:
```yaml
---
name: skill-name
description: Brief description of what this Skill does and when to use it
---
```

**Field Requirements**:
- `name`: Max 64 chars, lowercase letters/numbers/hyphens only, no XML tags, no "anthropic"/"claude"
- `description`: Max 1024 chars, non-empty, no XML tags, must include BOTH what it does AND when to use it

**Impact**: Skills may not be properly discovered or invoked by Claude

### 2. ❌ File Size Exceeds Recommendations

**Current State**:
- `mmd-writing.md`: 601 lines (exceeds 500 line recommendation)
- `mmdc-cli-usage.md`: 262 lines (within limit)

**Requirement**: Keep SKILL.md under 500 lines for optimal performance

**Recommendation**: Split `mmd-writing.md` into:
- Main SKILL.md (core instructions)
- REFERENCE.md (detailed syntax reference)
- EXAMPLES.md (pattern library)

### 3. ❌ Progressive Disclosure Not Implemented

**Current State**: All content is in single files without resource organization

**Best Practice**: Organize into progressive disclosure structure:
```
skill-name/
├── SKILL.md (main instructions, <500 lines)
├── REFERENCE.md (detailed reference)
├── EXAMPLES.md (code examples)
└── resources/
    └── additional-guides.md
```

**Benefits**:
- Only load necessary content into context
- Faster skill invocation
- Better token efficiency
- Unlimited bundled resources (loaded as needed)

### 4. ⚠️ Description Placement

**Current Issue**: "When to Use This Skill" is in markdown body, not YAML description

**Best Practice**: Include usage triggers in YAML `description` field for discovery

## Recommended Improvements

### Immediate Actions (Required)

1. **Add YAML Frontmatter** to both skills with proper `name` and `description`
2. **Split mmd-writing.md** into multiple files to stay under 500 lines
3. **Move to directory structure** for each skill

### Suggested Enhancements

1. **Add Resource Files**:
   - `COMMON_PATTERNS.md` - Frequently used MMD patterns
   - `TROUBLESHOOTING.md` - Common errors and fixes
   - `QUICK_REFERENCE.md` - Compact syntax cheat sheet

2. **Create Additional Skills**:
   - `mmd-debugging` - Specialized skill for troubleshooting MMD issues
   - `device-library-creation` - Guide for creating device libraries
   - `mmd-performance-optimization` - Skill for optimizing large MMD files

3. **Add Scripts** (optional):
   - `validate_syntax.py` - Quick syntax validation helper
   - `generate_template.py` - MMD template generator

## Comparison with Anthropic's Pre-built Skills

Anthropic's pre-built skills (PowerPoint, Excel, Word, PDF) demonstrate:
- Concise, focused SKILL.md with clear instructions
- Additional reference files for detailed documentation
- Scripts for deterministic operations
- Clear description with usage triggers

## Implementation Plan

### Phase 1: Compliance (Immediate)
- [ ] Add YAML frontmatter to existing skills
- [ ] Rename files to SKILL.md format
- [ ] Create skill directories
- [ ] Split mmd-writing into multiple files

### Phase 2: Enhancement (Short-term)
- [ ] Add REFERENCE.md to both skills
- [ ] Add EXAMPLES.md with common patterns
- [ ] Create TROUBLESHOOTING.md
- [ ] Add cross-references between skills

### Phase 3: Expansion (Future)
- [ ] Create additional specialized skills
- [ ] Add utility scripts
- [ ] Create comprehensive test suite
- [ ] Document skill authoring process

## Updated Skill Descriptions

### mmd-writing

**Proposed name**: `mmd-writing`
**Proposed description**: "Write MIDI Markdown (MMD) files with correct syntax, timing paradigms, MIDI commands, and advanced features like loops, sweeps, and modulation. Use when the user wants to create or edit .mmd files, needs help with MMD syntax, is implementing MIDI automation sequences, or is troubleshooting MMD validation errors."

### mmdc-cli-usage

**Proposed name**: `mmdc-cli-usage`
**Proposed description**: "Use the MIDI Markdown Compiler (mmdc) CLI for compiling MMD to MIDI, validating syntax, real-time playback with TUI, and exporting to different formats. Use when the user wants to compile, validate, play, or inspect MMD files, or is troubleshooting compilation errors."

## Security Considerations

Current skills are project-based and authored locally, which aligns with security best practices:
- ✅ Skills are from trusted source (project maintainer)
- ✅ No external network dependencies
- ✅ No untrusted code execution
- ✅ All instructions are transparent and auditable

## Next Steps

1. Update skills to comply with Anthropic specification
2. Test skills in Claude Code environment
3. Document skill usage in project README
4. Create skill authoring guide for contributors
5. Consider publishing skills to community repository

## References

- [Agent Skills Overview](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)
- [Skill Authoring Best Practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)
- [Agent Skills Engineering Blog](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [Anthropic Skills Repository](https://github.com/anthropics/skills)
- [Skills Cookbook](https://github.com/anthropics/claude-cookbooks/tree/main/skills)
