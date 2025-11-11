# MkDocs Documentation Setup

This document describes the MkDocs documentation system setup for MIDI Markdown.

## Overview

MkDocs has been configured with the Material theme and mkdocstrings plugin to provide:

- Beautiful, responsive documentation site
- Auto-generated API documentation from Python docstrings
- Search functionality
- Code syntax highlighting
- Dark/light theme toggle
- Navigation with tabs and sections

## Installation

### Required Dependencies

Add the following to your development environment:

```bash
# Install MkDocs with Material theme and Python documentation plugin
uv add --group dev mkdocs mkdocs-material "mkdocstrings[python]"
```

**Package Details**:
- `mkdocs` - Static site generator for documentation
- `mkdocs-material` - Material Design theme for MkDocs
- `mkdocstrings[python]` - Auto-generate API docs from Python docstrings

### Justfile Commands

The following commands have been added to the `justfile`:

```bash
just docs-serve     # Serve documentation locally at http://127.0.0.1:8000
just docs-build     # Build static site to site/ directory
just docs-deploy    # Deploy to GitHub Pages
just docs-clean     # Remove site/ build artifacts
```

## Configuration

### Main Configuration: mkdocs.yml

The main configuration file defines:

- **Site metadata**: Name, description, repository links
- **Theme**: Material theme with indigo/cyan colors, dark mode support
- **Plugins**: Search and mkdocstrings for API documentation
- **Navigation**: Structured menu matching docs/ folder organization
- **Markdown extensions**: Code highlighting, admonitions, tables, etc.

### Navigation Structure

```
Home
├── Getting Started
│   ├── Installation
│   ├── Quickstart
│   └── First Song
├── User Guide
│   ├── MMD Syntax
│   ├── Timing System
│   ├── MIDI Commands
│   ├── Alias System
│   ├── Alias API
│   ├── Device Libraries
│   └── Realtime Playback
├── CLI Reference
│   ├── Overview
│   ├── compile
│   ├── validate
│   ├── check
│   ├── inspect
│   ├── play
│   └── repl
├── Tutorials
│   ├── Basic Melody
│   ├── Multi-Channel
│   └── Device Control
├── Developer Guide
│   ├── Parser Architecture
│   ├── Lexer Architecture
│   ├── Quick References
│   └── API Reference ⭐
└── Reference
    ├── FAQ
    └── Troubleshooting
```

### API Reference Page

The new **API Reference** page (`docs/developer-guide/api-reference.md`) uses mkdocstrings to auto-generate documentation for:

**Parser Layer**:
- `MMLParser` class
- AST node dataclasses

**Core/IR Layer**:
- `MIDIEvent`, `IRProgram` classes
- `compile_ast_to_ir()` function

**Codegen Layer**:
- `generate_midi_file()` - MIDI file generation
- `export_to_csv()` - CSV export
- `export_to_json()` - JSON export

**Runtime Layer**:
- `MIDIPortManager` - MIDI I/O
- `EventScheduler` - Event scheduling
- `TempoTracker` - Tempo tracking
- `RealtimePlayer` - Playback API
- TUI components (state, display, components)

**Validation Layer**:
- Document validator
- Timing validator
- Value validator

**Alias System**:
- `AliasResolver` - Alias expansion
- Import resolver
- Conditionals and computation

**Expansion Layer**:
- `CommandExpander` - Orchestrator
- Variables, loops, sweeps

**Utilities**:
- Parameter type parsing
- MIDI constants

### Custom Styling

Custom CSS in `docs/stylesheets/extra.css` provides:

- Enhanced syntax highlighting for `.mmd` code blocks
- Improved table styling
- Custom admonitions
- API documentation formatting
- Status badges (Complete/Coming Soon)
- Command-line output styling
- Dark mode support

## File Structure

```
midi-markdown/
├── mkdocs.yml                              # Main MkDocs configuration
├── docs/
│   ├── index.md                            # Homepage (already exists)
│   ├── stylesheets/
│   │   └── extra.css                       # Custom CSS styling
│   ├── getting-started/
│   │   ├── installation.md
│   │   ├── quickstart.md
│   │   └── first-song.md
│   ├── user-guide/
│   │   ├── mml-syntax.md
│   │   ├── timing-system.md
│   │   ├── midi-commands.md
│   │   ├── alias-system.md
│   │   ├── alias-api.md
│   │   ├── device-libraries.md
│   │   └── realtime-playback.md
│   ├── cli-reference/
│   │   ├── overview.md
│   │   ├── compile.md
│   │   ├── validate.md
│   │   ├── check.md
│   │   ├── inspect.md
│   │   ├── play.md
│   │   └── repl.md
│   ├── tutorials/
│   │   ├── basic-melody.md
│   │   ├── multi-channel.md
│   │   └── device-control.md
│   ├── developer-guide/
│   │   ├── api-reference.md                # ⭐ NEW - Auto-generated API docs
│   │   └── architecture/
│   │       ├── parser.md
│   │       ├── lexer.md
│   │       └── quick-reference/
│   │           ├── parser-quick-ref.md
│   │           └── lexer-quick-ref.md
│   └── reference/
│       ├── faq.md
│       └── troubleshooting.md
└── site/                                    # Generated site (after build)
```

## Usage

### Local Development

Start the development server with live reload:

```bash
just docs-serve
```

Then open http://127.0.0.1:8000 in your browser. Changes to markdown files will automatically reload.

### Building the Site

Build the static site to the `site/` directory:

```bash
just docs-build
```

The generated site can be served by any static web server.

### Deploying to GitHub Pages

Deploy the documentation to GitHub Pages:

```bash
just docs-deploy
```

This will:
1. Build the documentation
2. Push to the `gh-pages` branch
3. Enable GitHub Pages at `https://yourusername.github.io/midi-markdown/`

## Writing Documentation

### Adding New Pages

1. Create a markdown file in the appropriate `docs/` subdirectory
2. Add the file to the `nav:` section in `mkdocs.yml`
3. Use standard Markdown syntax with Material extensions

### Using mkdocstrings for API Docs

To document a Python module/class/function:

```markdown
## Module Name

::: package.module.ClassName
    options:
      show_source: true
      heading_level: 3
      members:
        - method1
        - method2
```

**Options**:
- `show_source: true` - Include source code
- `heading_level: 3` - Set heading level for generated docs
- `members: [...]` - Only document specific members
- `filters: ["!^_"]` - Exclude private members (default)

### Code Blocks

Use fenced code blocks with language hints:

````markdown
```python
def hello():
    print("Hello, MML!")
```

```mml
# MMD example
@import "devices/quad_cortex.mmd"

[00:00.000]
- cortex_load 1.0.0.1
```
````

### Admonitions

Use admonitions for notes, warnings, tips:

```markdown
!!! note "Title"
    Content here

!!! warning
    Important warning

!!! tip "Pro Tip"
    Helpful advice

!!! example
    Example code or usage
```

## Features

### Material Theme Features

- **Dark mode toggle** - Automatic preference detection
- **Navigation tabs** - Top-level sections as tabs
- **Search** - Full-text search with highlighting
- **Code copy button** - One-click code copying
- **Table of contents** - Auto-generated ToC sidebar
- **Instant loading** - Single-page app with AJAX navigation

### Markdown Extensions

- **Syntax highlighting** - Pygments-based code highlighting
- **Tables** - GitHub-flavored markdown tables
- **Admonitions** - Note, warning, tip boxes
- **Footnotes** - Reference-style footnotes
- **Task lists** - `- [ ]` checkbox lists
- **Emoji** - `:emoji_name:` support
- **Math** - LaTeX math rendering (if needed)
- **Mermaid diagrams** - Flow charts, sequence diagrams

## Customization

### Theme Colors

Edit `mkdocs.yml` to change colors:

```yaml
theme:
  palette:
    - scheme: default
      primary: indigo    # Change to: blue, green, purple, etc.
      accent: cyan       # Change to: pink, orange, yellow, etc.
```

### Navigation Structure

Edit `nav:` in `mkdocs.yml`:

```yaml
nav:
  - Home: index.md
  - Section Name:
    - subsection/page1.md
    - subsection/page2.md
```

### Adding Custom CSS

Add styles to `docs/stylesheets/extra.css` and they'll be automatically loaded.

### Adding Custom JavaScript

Create `docs/javascripts/extra.js` and reference it:

```yaml
extra_javascript:
  - javascripts/extra.js
```

## Maintenance

### Updating Dependencies

```bash
uv lock --upgrade
uv sync
```

### Cleaning Build Artifacts

```bash
just docs-clean
```

### Updating API Documentation

The API reference auto-generates from docstrings. To update:

1. Update docstrings in source code following Google style
2. Rebuild documentation: `just docs-build`
3. Preview changes: `just docs-serve`

### Example Google-Style Docstring

```python
def compile_ast_to_ir(doc: MMLDocument, ppq: int = 480) -> IRProgram:
    """Compile MMD AST to Intermediate Representation.

    This function orchestrates the compilation pipeline from parsed AST
    to the queryable IR format used by codegen and runtime.

    Args:
        doc: Parsed MMD document AST
        ppq: Pulses per quarter note (MIDI resolution)

    Returns:
        IRProgram containing compiled MIDI events with metadata

    Raises:
        ValidationError: If document validation fails
        ValueError: If PPQ is invalid (<= 0)

    Example:
        ```python
        parser = MMLParser()
        doc = parser.parse_file("song.mmd")
        ir = compile_ast_to_ir(doc, ppq=960)
        print(f"Compiled {len(ir.events)} events")
        ```
    """
    # Implementation...
```

## Resources

- **MkDocs Documentation**: https://www.mkdocs.org/
- **Material Theme**: https://squidfunk.github.io/mkdocs-material/
- **mkdocstrings**: https://mkdocstrings.github.io/
- **Markdown Guide**: https://www.markdownguide.org/

## Next Steps

1. **Install dependencies**:
   ```bash
   uv add --group dev mkdocs mkdocs-material "mkdocstrings[python]"
   ```

2. **Start local server**:
   ```bash
   just docs-serve
   ```

3. **Review generated API docs** at http://127.0.0.1:8000/developer-guide/api-reference/

4. **Improve docstrings** in source code to enhance API documentation

5. **Consider adding**:
   - Architecture diagrams (using Mermaid)
   - More code examples in API docs
   - Contribution guidelines
   - Changelog/release notes

## Troubleshooting

### Import Errors During Build

If mkdocstrings can't import modules:

1. Ensure `uv sync` has been run
2. Check that source code has no syntax errors
3. Verify module paths in API reference are correct

### Broken Links

MkDocs will warn about broken links during build. Fix by:

1. Checking file paths in navigation
2. Ensuring markdown link targets exist
3. Using relative paths for internal links

### Missing Dependencies

If you see import errors for mido, rtmidi, etc.:

```bash
uv sync  # Install all project dependencies
```

---

**Status**: MkDocs setup complete. Ready to run `uv add` and serve documentation.
**Created**: 2024-11-08
**Version**: 0.1.0
