# Agent Skills for MIDI Markdown

This directory contains Claude Code Agent Skills for working with MIDI Markdown (MMD). Skills are modular capabilities that extend Claude's functionality with domain-specific expertise.

## Available Skills

### 1. mmd-writing

**Purpose**: Write MIDI Markdown (MMD) files with correct syntax, timing paradigms, MIDI commands, and advanced features.

**Use when**:
- Creating or editing `.mmd` files
- Need help with MMD syntax
- Implementing MIDI automation sequences
- Troubleshooting MMD validation errors

**Files**:
- `SKILL.md` (359 lines) - Main instructions and quick reference
- `REFERENCE.md` - Complete syntax reference
- `EXAMPLES.md` - Pattern library with working examples
- `TROUBLESHOOTING.md` - Error diagnosis and solutions
- `scripts/validate_syntax.py` - Quick syntax validation script
- `scripts/generate_template.py` - MMD template generator

### 2. mmdc-cli-usage

**Purpose**: Use the MIDI Markdown Compiler (mmdc) CLI for compiling, validating, playing, and inspecting MMD files.

**Use when**:
- Compiling MMD to MIDI
- Validating or checking MMD syntax
- Real-time MIDI playback with TUI
- Exporting to JSON/CSV/table formats
- Troubleshooting compilation errors

**Files**:
- `SKILL.md` (460 lines) - Complete CLI reference and workflows

### 3. mmd-debugging

**Purpose**: Troubleshoot and debug MIDI Markdown files including validation errors, timing issues, and compilation failures.

**Use when**:
- Encountering MMD errors or validation failures
- Timing or value range issues
- Unexpected behavior in MMD files
- Need systematic debugging approach
- Creating minimal reproductions

**Files**:
- `SKILL.md` (425 lines) - Comprehensive debugging guide

### 4. device-library-creation

**Purpose**: Create custom MIDI device libraries with aliases, parameters, and documentation for hardware.

**Use when**:
- Creating device-specific aliases
- Documenting MIDI implementations
- Building reusable command libraries
- Supporting new hardware devices
- Organizing complex MIDI workflows

**Files**:
- `SKILL.md` (475 lines) - Complete library creation guide

## Skill Structure

Skills follow Anthropic's Agent Skills specification:

```
skill-name/
├── SKILL.md (required)          # Main instructions with YAML frontmatter
├── REFERENCE.md (optional)      # Detailed reference material
├── EXAMPLES.md (optional)       # Code examples and patterns
└── resources/ (optional)        # Additional resources
```

### YAML Frontmatter

Every `SKILL.md` file must start with YAML frontmatter:

```yaml
---
name: skill-name
description: Brief description of what this Skill does and when to use it
---
```

**Requirements**:
- `name`: Max 64 chars, lowercase letters/numbers/hyphens only
- `description`: Max 1024 chars, must include both what it does AND when to use it

### Progressive Disclosure

Skills use progressive disclosure - Claude loads content in stages:

1. **Level 1 (Metadata)**: YAML frontmatter (always loaded at startup)
2. **Level 2 (Instructions)**: SKILL.md body (loaded when skill is triggered)
3. **Level 3+ (Resources)**: Additional files (loaded as needed via bash)

This architecture ensures only relevant content occupies the context window, enabling:
- Fast skill invocation
- Better token efficiency
- Effectively unlimited bundled resources

## How Skills Work

1. **Discovery**: Claude pre-loads skill metadata (name + description) at startup
2. **Triggering**: When user request matches a skill's description, Claude loads SKILL.md
3. **Resource Access**: Claude reads additional files (REFERENCE.md, EXAMPLES.md) as needed
4. **Execution**: Claude uses instructions to help with the task

## Best Practices

### For Skill Authors

1. **Keep SKILL.md under 500 lines** - Split detailed content into separate files
2. **Write clear descriptions** - Include both "what" and "when to use"
3. **Use progressive disclosure** - Put common instructions in SKILL.md, details in REFERENCE.md
4. **Add examples** - Working code examples help Claude understand patterns
5. **Cross-reference** - Link to related skills and project documentation

### For Skill Users

1. **Skills load automatically** - No need to manually invoke them
2. **Skills are context-aware** - Claude uses them when your request matches
3. **Check skill status** - Use Claude Code skills panel to see available skills
4. **Update skills** - Pull latest changes from repository for improvements

## Compliance

These skills comply with Anthropic's Agent Skills specification:

- ✅ Required YAML frontmatter with `name` and `description`
- ✅ Field validation (length limits, character restrictions)
- ✅ Progressive disclosure architecture
- ✅ SKILL.md under 500 lines (mmd-writing split into 3 files)
- ✅ Clear, actionable descriptions
- ✅ No XML tags in metadata
- ✅ No reserved words ("anthropic", "claude")

For specification details, see `SKILLS_REVIEW.md` in this directory.

## Security

All skills in this directory are:
- ✅ Authored locally (project maintainer)
- ✅ Transparent and auditable (text files in version control)
- ✅ No external network dependencies
- ✅ No untrusted code execution

**Security Note**: Only use skills from trusted sources. These project skills are safe for use.

## Related Documentation

- [Anthropic Agent Skills Overview](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)
- [Skill Authoring Best Practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)
- [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills)
- [Skills Cookbook](https://github.com/anthropics/claude-cookbooks/tree/main/skills)
- [Anthropic Skills Repository](https://github.com/anthropics/skills)

## Contributing

To improve existing skills or add new ones:

1. Follow Anthropic's Agent Skills specification
2. Keep SKILL.md concise (<500 lines)
3. Add proper YAML frontmatter
4. Include examples and reference material
5. Test skills in Claude Code environment
6. Update this README with new skills

See `SKILLS_REVIEW.md` for detailed improvement recommendations.

## Support

For issues with skills:
1. Check `SKILLS_REVIEW.md` for known issues
2. Verify skills are properly formatted
3. Test skills in Claude Code
4. Report issues in project GitHub repository

---

**Last Updated**: 2025-11-12
**Skills Version**: 1.1.0 (4 skills with utilities and troubleshooting)
**Status**: Production-ready

## Skill Summary

| Skill | Lines | Purpose |
|-------|-------|---------|
| mmd-writing | 359 | Write MMD files with correct syntax |
| mmdc-cli-usage | 460 | Use mmdc CLI tools |
| mmd-debugging | 425 | Troubleshoot and debug MMD |
| device-library-creation | 475 | Create custom device libraries |

**Total**: 4 skills, 1,719 lines of core instructions
**Additional**: 2 utility scripts, 1 troubleshooting guide, 3 reference documents
