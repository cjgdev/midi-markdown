# Claude Code Skills for MIDI Markdown

MIDI Markdown provides official Claude Code skills to enhance your MMD development experience. These skills help Claude understand MMD syntax, CLI usage, and best practices when working with your MIDI automation files.

## What are Claude Code Skills?

Claude Code skills are specialized knowledge modules that help Claude assist you more effectively with specific tasks. When installed, these skills are automatically activated when you work with relevant files or request help with specific topics.

## Available Skills

### mmd-writing

**Purpose**: Helps write MIDI Markdown files with correct syntax, timing, MIDI commands, and advanced features.

**Activated when:**
- Creating or editing `.mmd` files
- Asking about MMD syntax
- Implementing MIDI automation or sequences
- Troubleshooting MMD syntax or validation errors

**Features:**
- Complete MMD syntax reference
- All timing paradigms (absolute, musical, relative, simultaneous)
- MIDI command examples (notes, CC, PC, pitch bend, etc.)
- Advanced features (loops, sweeps, variables, modulation)
- Random expressions and generative techniques
- Common patterns and best practices
- Troubleshooting and error avoidance

### mmdc-cli-usage

**Purpose**: Helps use the MIDI Markdown Compiler CLI effectively for compiling, validating, playing, and inspecting MMD files.

**Activated when:**
- Working with `mmdc` commands
- Compiling MMD to MIDI
- Validating or checking MMD files
- Playing MMD with real-time output
- Inspecting or exporting MMD in different formats
- Troubleshooting compilation or playback errors

**Features:**
- Complete `mmdc` CLI reference
- Compilation workflows and best practices
- Validation and debugging techniques
- Real-time playback with TUI
- Output format options (MIDI, JSON, CSV, table)
- Integration with other tools (UV, Just)
- Common workflows and error handling

### mmd-debugging

**Purpose**: Troubleshoot and debug MIDI Markdown files including validation errors, timing issues, value ranges, and syntax problems.

**Activated when:**
- Encountering MMD errors or validation failures
- Debugging unexpected behavior in MMD files
- Diagnosing timing, value range, or syntax issues

**Features:**
- Systematic debugging workflow
- Error category identification (parse, validation, expansion, compilation)
- Common error patterns and fixes
- Quick fixes for typical mistakes
- Diagnostic tool guidance

### device-library-creation

**Purpose**: Create custom MIDI device libraries for hardware with aliases, parameters, and documentation.

**Activated when:**
- Creating device-specific aliases for guitar processors, synthesizers, effects units
- Documenting MIDI implementations
- Building reusable command libraries

**Features:**
- Step-by-step device library creation guide
- Alias pattern best practices
- Parameter type documentation (numeric, note, percent, enum)
- Testing and validation workflows
- Common device patterns and examples

## Device-Specific Skills

The following skills provide specialized guidance for popular MIDI hardware:

### quad-cortex-usage

**Purpose**: Guide for using the Neural DSP Quad Cortex device library in MMD files.

**Activated when:**
- Working with Quad Cortex presets, scenes, or expression control
- Implementing Quad Cortex MIDI automation
- Troubleshooting Quad Cortex MIDI timing or control issues

**Key Topics:**
- Preset loading sequences (setlist + preset group + program change)
- Scene switching (8 scenes: A-H)
- Expression pedal control (4 expression inputs)
- Stomp switch automation (8 footswitches)
- Timing considerations (100-130ms latency for complex presets)

### h90-usage

**Purpose**: Guide for using the Eventide H90 Harmonizer device library in MMD files.

**Activated when:**
- Working with H90 program changes, HotSwitches, or effects routing
- Implementing H90 expression or parameter automation
- Troubleshooting H90 MIDI control issues

**Key Topics:**
- Program change and algorithm selection
- HotSwitch and bypass control
- Routing modes (series, parallel, A-only, B-only)
- Expression and rotary knob control
- Firmware-specific workarounds (1.9.4+ PC+CC bug)

### helix-usage

**Purpose**: Guide for using the Line 6 Helix Floor/LT/Rack device library in MMD files.

**Activated when:**
- Working with Helix presets, snapshots, or expression control
- Implementing full Helix automation (11 footswitches, 8 snapshots)
- Troubleshooting Helix MIDI timing or Command Center setup

**Key Topics:**
- Setlist and preset management
- Snapshot control (8 snapshots: 1-8)
- Expression pedal automation (2 expression inputs)
- Footswitch control (11 FS assignments)
- Looper and transport control

### hx-stomp-usage

**Purpose**: Guide for using the Line 6 HX Stomp device library in MMD files.

**Activated when:**
- Working with HX Stomp's 3-snapshot limitation
- Implementing compact HX Stomp automation
- USB MIDI setup and Mode switching

**Key Topics:**
- 3-snapshot workarounds (most limited snapshot count)
- USB-only MIDI connectivity
- All Bypass and Mode switching
- Direct PC addressing (no bank system)
- Compact form factor considerations

### hx-effects-usage

**Purpose**: Guide for using the Line 6 HX Effects device library in MMD files.

**Activated when:**
- Working with HX Effects processor (effects-only, no amp/cab modeling)
- Implementing 4-snapshot control
- 5-pin DIN MIDI and amp integration workflows

**Key Topics:**
- Sequential preset addressing (32 banks × 4 presets = 128 total)
- 4-snapshot control
- 5-pin DIN MIDI advantages
- Effects-only design for external amp integration
- Bank + preset navigation

### hx-stomp-xl-usage

**Purpose**: Guide for using the Line 6 HX Stomp XL device library in MMD files.

**Activated when:**
- Working with HX Stomp XL (middle ground between HX Stomp and full Helix)
- Implementing 4-snapshot and 8-footswitch control
- Comparing Stomp XL capabilities with other HX/Helix models

**Key Topics:**
- 4-snapshot control (more than HX Stomp, less than full Helix)
- 8 footswitch assignments
- USB MIDI and All Bypass control
- Best balance of features vs size
- Comparison with HX Stomp and full Helix

## Installation

### Prerequisites

- **Claude Code** installed on your system
- MIDI Markdown compiler (optional but recommended for testing)

### Option 1: Automatic Installation (Recommended)

1. **Download the skills package** from the latest [GitHub release](https://github.com/cjgdev/midi-markdown/releases):
   - `claude-skills-mmd-{version}.tar.gz` (Linux/macOS)
   - `claude-skills-mmd-{version}.zip` (Windows)

2. **Extract the archive**:

   ```bash
   # Linux/macOS
   tar -xzf claude-skills-mmd-{version}.tar.gz
   cd claude-skills-mmd-{version}

   # Windows (PowerShell)
   Expand-Archive claude-skills-mmd-{version}.zip
   cd claude-skills-mmd-{version}
   ```

3. **Run the installation script**:

   ```bash
   # Linux/macOS
   ./install.sh

   # Windows
   install.bat
   ```

The script will automatically install the skills to your Claude Code skills directory.

### Option 2: Manual Installation

1. **Download and extract** the skills package (see Option 1, steps 1-2)

2. **Copy skill files** to your Claude Code skills directory:

   **Linux/macOS**:
   ```bash
   mkdir -p ~/.config/claude/skills
   cp *.md ~/.config/claude/skills/
   ```

   **Windows (PowerShell)**:
   ```powershell
   New-Item -ItemType Directory -Force -Path "$env:APPDATA\Claude\skills"
   Copy-Item *.md "$env:APPDATA\Claude\skills\"
   ```

3. **Verify installation**:

   **Linux/macOS**:
   ```bash
   ls ~/.config/claude/skills/
   ```

   **Windows (PowerShell)**:
   ```powershell
   Get-ChildItem "$env:APPDATA\Claude\skills\"
   ```

   You should see:
   - `mmd-writing.md`
   - `mmdc-cli-usage.md`

### Option 3: Project-Local Installation

For project-specific skills, copy them to your MMD project's `.claude/skills/` directory:

```bash
# From your MMD project directory
mkdir -p .claude/skills

# Copy from extracted skills package
cp /path/to/extracted/skills/*.md .claude/skills/

# Or copy from an existing installation
cp ~/.config/claude/skills/mmd-*.md .claude/skills/  # Linux/macOS
```

Project-local skills override global skills and are useful for:
- Custom workflows specific to your project
- Sharing skills with team members via version control
- Testing modified skills before global installation

## Verification

To verify the skills are installed correctly:

1. **Check the skills directory** (see verification commands above)

2. **Test in Claude Code**:
   - Open a `.mmd` file or create a new one
   - Ask Claude: "Help me write an MMD file with a simple melody"
   - Claude should use the `mmd-writing` skill to provide detailed MMD syntax help

3. **Try CLI help**:
   - Ask Claude: "How do I compile an MMD file to MIDI?"
   - Claude should use the `mmdc-cli-usage` skill to provide specific `mmdc` commands

## Usage

### Automatic Activation

Claude Code automatically activates relevant skills based on:
- **File type**: Opening or editing `.mmd` files activates `mmd-writing`
- **Context**: Discussing `mmdc` commands activates `mmdc-cli-usage`
- **Keywords**: Mentioning "MMD syntax", "MIDI Markdown", etc.

### Explicit Invocation

You can explicitly request a specific skill:

```
"Use the mmd-writing skill to help me create a drum pattern"
"Use the mmdc-cli-usage skill to show me validation commands"
```

### Example Workflows

#### Creating a New MMD File

1. **Ask for help**:
   ```
   "Help me create an MMD file for a live guitar performance with preset changes"
   ```

2. **Claude uses `mmd-writing` skill** to provide:
   - Frontmatter template
   - Device library import suggestions
   - Timing and command examples
   - Best practices

#### Compiling and Testing

1. **Ask about compilation**:
   ```
   "How do I compile my MMD file and test it?"
   ```

2. **Claude uses `mmdc-cli-usage` skill** to provide:
   - Validation commands
   - Compilation options
   - Playback testing workflow
   - Troubleshooting tips

#### Debugging Issues

1. **Share your error**:
   ```
   "I'm getting a timing error when I compile. Here's my MMD file: ..."
   ```

2. **Claude uses both skills** to:
   - Identify syntax issues (`mmd-writing`)
   - Suggest validation commands (`mmdc-cli-usage`)
   - Provide corrected syntax
   - Recommend testing workflow

## Skill Contents

### mmd-writing Skill Includes

- **File structure**: Frontmatter, imports, definitions
- **Timing systems**: All four timing paradigms with examples
- **MIDI commands**: Notes, CC, PC, pitch bend, pressure, meta events
- **Advanced features**:
  - Variables and expressions
  - Loops and patterns
  - Sweeps and automation
  - Random expressions
  - Modulation (curves, waves, envelopes)
  - Imports and aliases
- **Common patterns**: Drums, chords, automation, humanization
- **Best practices**: Validation, timing, comments, reusability
- **Common mistakes**: What to avoid and how to fix
- **Quick reference**: Syntax table and examples

### mmdc-cli-usage Skill Includes

- **Core commands**:
  - `mmdc compile` - Compilation with all options
  - `mmdc validate` - Validation workflows
  - `mmdc check` - Syntax checking
  - `mmdc play` - Real-time playback
  - `mmdc inspect` - Event inspection
- **Output formats**: MIDI, JSON, CSV, table display
- **Workflow examples**: Development, testing, batch processing
- **Troubleshooting**: Validation errors, playback issues, compilation failures
- **Best practices**: Always validate, use inspect, test with playback
- **Integration**: UV, Just, piping, scripting
- **Quick reference**: Command table

## Updating Skills

When a new version of MIDI Markdown is released:

1. **Download the new skills package** from the [latest release](https://github.com/cjgdev/midi-markdown/releases)

2. **Re-run the installation** (the installer will overwrite old versions):
   ```bash
   ./install.sh  # Linux/macOS
   install.bat   # Windows
   ```

Skills are versioned with MIDI Markdown releases, so updating ensures you have the latest syntax and features.

## Customization

You can customize the skills for your workflow:

1. **Copy the skill file** you want to customize:
   ```bash
   cp ~/.config/claude/skills/mmd-writing.md ~/.config/claude/skills/mmd-writing-custom.md
   ```

2. **Edit the custom skill** to add:
   - Your own examples
   - Project-specific patterns
   - Team conventions
   - Additional device libraries

3. **Use the custom skill**:
   ```
   "Use the mmd-writing-custom skill to help me with our project conventions"
   ```

## Troubleshooting

### Skills Not Activating

**Problem**: Claude doesn't seem to use the skills

**Solutions**:
1. **Verify installation**:
   ```bash
   ls ~/.config/claude/skills/  # Linux/macOS
   ```

2. **Check file names**: Skills must end in `.md`

3. **Restart Claude Code** after installation

4. **Explicitly request the skill**:
   ```
   "Use the mmd-writing skill to help me"
   ```

### Skills Directory Not Found

**Problem**: Installation script can't find the skills directory

**Solutions**:
1. **Set the environment variable**:
   ```bash
   export CLAUDE_SKILLS_DIR=/path/to/your/skills/directory
   ./install.sh
   ```

2. **Create the directory manually**:
   ```bash
   mkdir -p ~/.config/claude/skills
   ```

3. **Use manual installation** (Option 2 above)

### Permission Errors

**Problem**: Can't write to skills directory

**Solutions**:
1. **Check directory permissions**:
   ```bash
   ls -ld ~/.config/claude/skills
   ```

2. **Fix permissions**:
   ```bash
   chmod 755 ~/.config/claude/skills
   ```

3. **Use project-local installation** (Option 3 above)

## Uninstalling

To remove the skills:

**Linux/macOS**:
```bash
rm ~/.config/claude/skills/mmd-writing.md
rm ~/.config/claude/skills/mmdc-cli-usage.md
```

**Windows (PowerShell)**:
```powershell
Remove-Item "$env:APPDATA\Claude\skills\mmd-writing.md"
Remove-Item "$env:APPDATA\Claude\skills\mmdc-cli-usage.md"
```

## FAQ

### Do I need Claude Code to use MIDI Markdown?

No! MIDI Markdown works standalone. Claude Code skills are an optional enhancement that makes development easier if you use Claude Code as your AI assistant.

### Can I use these skills with other AI tools?

The skills are formatted as Markdown documentation, so you could share them with other AI assistants, but they're optimized for Claude Code's skill system.

### Are the skills included in the mmdc installation?

No, skills are distributed separately. This allows you to:
- Skip skills if you don't use Claude Code
- Update skills independently
- Install skills only where needed

### Can I create my own MMD skills?

Yes! Use the included skills as templates. Skills are just Markdown files with structured information. See [Claude Code Skills documentation](https://docs.anthropic.com/claude/docs/claude-code-skills) for the skill format.

### Do skills work offline?

Skills are local files on your system and work offline. However, Claude Code itself requires an internet connection to communicate with Claude.

### How big are the skills files?

Very small:
- `mmd-writing.md`: ~25 KB
- `mmdc-cli-usage.md`: ~11 KB
- Total skills package: <100 KB

## See Also

- **[Quickstart Guide](quickstart.md)** - Get started with MIDI Markdown
- **[Installation](installation.md)** - Install the MIDI Markdown compiler
- **[First Song Tutorial](first-song.md)** - Write your first MMD file
- **[Examples Guide](examples-guide.md)** - Learn from example files
- **[MMD Syntax Reference](../user-guide/mmd-syntax.md)** - Complete syntax documentation
- **[CLI Reference](../cli-reference/overview.md)** - Full mmdc command documentation

## Support

- **GitHub Issues**: [Report problems](https://github.com/cjgdev/midi-markdown/issues)
- **Discussions**: [Ask questions](https://github.com/cjgdev/midi-markdown/discussions)
- **Documentation**: [Read the docs](https://cjgdev.github.io/midi-markdown/)

---

**Last Updated**: 2025-11-12
**Version**: 0.1.0
