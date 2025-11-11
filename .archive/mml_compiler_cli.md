# Building a Modern MML Compiler CLI: Comprehensive Design Reference

The best command-line compilers today don't just compile code—they guide developers through errors with clarity, provide rich feedback during compilation, and create delightful user experiences. This comprehensive guide distills best practices from mature compilers, modern CLI tools, and battle-tested Python libraries to help you build an exceptional MML (MIDI Markup Language) compiler.

## The modern compiler paradigm: Teaching through errors

**Rust, Elm, and TypeScript compilers demonstrate that error messages are educational tools, not punishment.** The Rust compiler's RFC 1644 established the foundation: errors should show *what* went wrong (primary labels), explain *why* it happened (secondary labels), and provide actionable suggestions—all with clear visual hierarchy and source code context. Elm takes this further with conversational tone ("I see an error..."), plain English explanations, and links to documentation. TypeScript optimizes for IDE integration with structured error formats that editors can parse and display inline.

The throughline across all excellent compilers: they respect users' time by making errors immediately understandable and actionable. Your MML compiler should adopt this philosophy—every error is an opportunity to teach MIDI concepts and guide users toward correct syntax.

## Color schemes and visual hierarchy that actually work

Modern CLIs use color deliberately, not decoratively. Research across hundreds of tools reveals a universal semantic color scheme: **red for errors (ANSI 31/91), yellow for warnings (ANSI 33/93), green for success (ANSI 32/92), and blue/cyan for informational text (ANSI 34/36)**. But color is never the sole information carrier—tools like ripgrep and fd combine color with symbols (✓, ✗, ⚠) to ensure accessibility for colorblind users and screen readers.

The critical accessibility rule: always provide `--no-color` flag support and automatically disable colors when output isn't a TTY (piped to file) or when `NO_COLOR` environment variable is set. The Rich library handles this automatically, making it ideal for Python CLI development. For maximum impact, use bold styling for the most critical information—Rust compiler bolds error codes, Elm bolds section headers, and modern tools bold key facts to enable rapid scanning.

Visual hierarchy extends beyond color. The best compilers create clear information layers: error headers (severity + code + message), location references (file:line:column in clickable format), code context windows with line numbers, inline annotations with carets (^ or ~) pointing to problems, explanations, and finally suggestions. Rust's "wall" separator (|) between line numbers and code creates clean visual structure that users can scan instantly.

## Strategic emoji usage without accessibility pitfalls

Emojis in CLI output remain controversial, with good reason. When GitHub's yubikey-agent launched with liberal emoji use (🔐 🚀 ✅), accessibility advocates immediately flagged screen reader issues—NVDA and JAWS announce every emoji's alt text ("lock key party popper check mark box with check"), creating frustrating experiences for blind users. The Content Design London accessibility team's research confirms: **emoji should enhance, never replace, textual information**.

The safe pattern: position emoji at line ends, never interrupt text flow, limit to 1-3 per message, and always provide flag to disable them. For MML compiler, consider: ✅ for successful compilation, ❌ for fatal errors, ⚠️ for warnings, 🎵 for MIDI-specific info, and 🎹 for playback actions. But make each emoji optional and redundant with text. The Rich library's Console class can conditionally render emoji based on terminal capabilities, automatically handling compatibility.

## Progress indication patterns for multi-phase compilation

Evil Martians' research on CLI progress patterns identifies three core types, each serving different needs. **Spinners (⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏) work for indeterminate tasks** like lexical analysis where duration is unpredictable. **"X of Y" counters work for sequential processing** like parsing multiple files (Processing track 3/12). **Progress bars excel for parallel operations** like MIDI generation across multiple channels, showing percentage completion with ETAs.

For your MML compiler, the ideal pattern combines these approaches across compilation phases:

**Lexical Analysis Phase**: Single spinner with updating message showing current file
```
⠋ Lexing input... (main.mml)
```

**Parsing Phase**: Counter format if processing multiple tracks
```
Parsing tracks (3/5)...
✓ Track 1 (Piano)
✓ Track 2 (Drums)  
⠋ Track 3 (Bass)
```

**Validation Phase**: Progress bar if checking many measures
```
Validating timing [████████░░░░] 65% ETA 2s
```

**MIDI Generation**: Spinner with summary, since it's usually quick
```
⠋ Generating MIDI output...
```

**Completion**: Static summary with emoji and statistics
```
✓ Compiled successfully in 1.4s
  5 tracks, 320 measures, 2.1KB output
```

Critical: all dynamic progress updates must detect TTY status. When output is piped or running in CI/CD, switch to simple line-based output without cursor control codes. Rich library's Progress class handles this automatically and provides templates for common patterns.

## Error message anatomy for compiler excellence

The structure of an excellent compiler error message follows a proven pattern, refined over decades. Start with a **header section** containing severity level (error/warning), optional error code (E001 style, searchable in documentation), concise problem description, and precise location in `filename:line:column` format. TypeScript and Rust both use this format because modern editors parse it for click-to-navigate functionality.

Follow with a **context window** showing relevant source code. Display 2-3 lines before and after the error location, with line numbers right-aligned and separated by a visual "wall" (| character). Use carets (^) or tildes (~) to underline the problematic code segment, with inline labels explaining what's wrong. Rust's innovation was two-layer labeling: primary labels (red/yellow underlines) show *what* is wrong, secondary labels (blue underlines) show *why* it occurred, creating visual flow that guides understanding.

Next comes **explanation and context**—why did the error occur? What did the compiler expect versus what it found? Elm excels here with plain English explanations that avoid jargon: "I see a type mismatch" rather than "ILLTYPE: incompatible assignment target." For MML compiler, translate technical parsing errors into musical domain language: "Expected a note duration (w, h, q, e, s) but found 'x'" rather than "Unexpected token 'x' at parser state 42."

Finally, provide **actionable suggestions**. Rust classifies suggestions by confidence level: MachineApplicable (can auto-fix), HasPlaceholders (user must fill in details), MaybeIncorrect (multiple valid approaches), and Unspecified (low confidence). Your MML compiler should offer specific fixes when possible: "Did you mean 'C4' instead of 'C5'?" or "Hint: Add a tempo marking like 't120' at the start of your file."

## File references that editors can parse

Every modern code editor—VS Code, Vim, Emacs, IntelliJ—automatically parses `filename:line:column` format for click-to-navigate functionality. Use this exact format consistently: `src/main.mml:42:15` not `main.mml(42)` or `main.mml line 42`. Line and column numbers should be 1-indexed (humans count from 1, not 0), and column should point to the first character of the problematic token.

For multi-file MML projects, always use relative paths from project root, not absolute filesystem paths. This makes error messages portable across machines and integrates better with version control. If the compiler encounters errors in imported/included files, show the full import chain to help users understand context:

```
error: Undefined instrument 'harpsichord'
  → lib/baroque.mml:23:12
  → imported by: src/main.mml:5:1
```

Clang's innovation of showing macro expansion chains applies similarly to MML's potential macro/template system—show the full expansion path so users can trace where problems originate.

## Multi-line error messages with code snippets

Source code context transforms cryptic error messages into educational moments. The proven format uses line numbers in a right-aligned column, separated from code by a vertical bar (|), with blank line number columns showing continuation. Show minimal necessary context—typically the error line plus 2 lines above and below. Use ellipsis (...) to indicate elided distant lines.

For MML compiler parsing errors, show the musical context:

```
error[E003]: Invalid note duration
  → melody.mml:15:8

   13 | C4 q D4 q E4 q F4 q
   14 | G4 q A4 q B4 q C5 q
   15 | D5 x E5 q F5 q G5 q
      |    ^ Expected duration (w, h, q, e, s, t) but found 'x'
   16 | A5 q B5 q C6 w
```

For semantic validation errors (wrong note range, tempo out of bounds, duration arithmetic errors), show the full musical phrase so users understand context:

```
warning[W012]: Note may be out of typical range
  → bass.mml:45:3

   43 | # Bass line  
   44 | @instrument bass
   45 | C1 w
      | ^^ Bass typically plays C2-C4; C1 is very low (32.7 Hz)
   46 | 
   
   💡 Hint: Did you mean C2? Or use @octave 2 then C?
```

The inline label appears directly on the source line, creating visual connection between problem and explanation. Use color (when available) to highlight the error span—red for errors, yellow for warnings.

## Making errors scannable with bold critical facts

Users scan error messages looking for key information: what broke, where, and how to fix it. Use bold styling for the most critical elements—error codes, file locations, problematic identifiers, and key suggestions. Rust compiler bolds error codes (`error[E0499]`), TypeScript bolds type names, Elm bolds section headers.

For MML compiler, bold the essential musical elements:

```
error: Tempo marking **t380** exceeds typical range
  → song.mml:1:2
  
  Most MIDI sequencers support tempos **t20** to **t300**
  
  💡 Did you mean **t180** (half of 380)?
```

But avoid over-bolding—if everything is bold, nothing stands out. Limit to 3-5 bolded elements per error. Use color and bold together strategically: red + bold for error severity, yellow + bold for warnings, green + bold for success messages.

Rich library's markup syntax makes this trivial: `console.print("[bold red]error[/bold red]: Invalid note")`. The markup is readable in source code and renders beautifully in terminals that support it, while gracefully degrading in limited environments.

## "Did you mean?" suggestions using Levenshtein distance

Typo-tolerant error messages dramatically improve user experience. When MML compiler encounters an unknown identifier, compute edit distance to valid options and suggest close matches. The proven approach: calculate Damerau-Levenshtein distance (allowing transpositions) to all valid identifiers, suggest any within distance ≤2, order by similarity.

For note names, instrument names, and keywords:

```
error: Unknown instrument 'violin'
  → orchestra.mml:12:13

   12 | @instrument violin
      |             ^^^^^^ No instrument named 'violin'
   
   💡 Did you mean one of these?
      • **violine** (in standard library)
      • **violin1** (defined at line 5)
      • **cello** (similar instrument family)
```

For MML syntax errors, suggest common corrections:

```
error: Unexpected token after note
  → melody.mml:8:6

    8 | C4 quarter D4 quarter
      |    ^^^^^^^ Expected duration symbol (q, w, h, e, s)
   
   💡 Did you mean **q** (quarter note)? 
      MML uses short codes: w=whole h=half q=quarter e=eighth s=sixteenth
```

Python's difflib library provides `get_close_matches()` for simple cases, but for production quality, implement proper edit distance with reasonable thresholds. The Lark parser's UnexpectedToken exception provides `expected` set—these are the valid tokens, perfect for fuzzy matching.

## Handling cascading errors without overwhelming users

A single syntax error often triggers dozens of follow-on errors as the parser loses synchronization. Mature compilers like Rust and TypeScript limit initial output to ~10 errors, then suggest fixes before showing more. The summary format:

```
error: aborting due to 3 previous errors; 5 warnings emitted

For more information about this error, try:
  mmlc --explain E003
  
Some errors have detailed explanations: E003, E012, E045
Use `mmlc --explain E003` to see detailed help
```

For MML compiler, detect related errors—if measure timing doesn't add up, it cascades into every subsequent measure. Stop after the first timing error and explain:

```
error: Measure duration mismatch in measure 8
  → song.mml:42:1
  
  Measure 8 contains **5 quarter notes** but time signature 4/4 expects **4**
  
  This error may cause additional errors in following measures.
  Fix this first, then recompile to see if other errors remain.
```

Lark parser's `on_error` callback enables limited error recovery—you can try to resynchronize at measure boundaries or track separators. But be conservative: false recovery creates confusing cascading errors. It's better to stop at first unrecoverable error and provide a clear explanation.

## Warning levels and severity hierarchy

Not all problems are equal. The standard three-tier system: **errors** (prevent compilation, exit code 1), **warnings** (potential issues but compilation continues, exit code 0), and **notes** (informational context for errors). Add a fourth tier for MML: **suggestions** (style recommendations, not problems).

**Errors**: Syntax errors, undefined references, type mismatches, file I/O failures
**Warnings**: Deprecated syntax, notes out of typical range, unusual tempo markings, missing recommended metadata
**Notes**: Additional context for errors, "also defined here" for duplicate definitions  
**Suggestions**: Style improvements, inefficient patterns, better alternatives

Use color coding consistently: red for errors, yellow for warnings, blue for notes, cyan for suggestions. Prefix each with level:

```
error[E045]: Undefined instrument reference
warning[W023]: Note velocity 127 may cause clipping
note: instrument 'piano' imported from stdlib.mml
suggestion: Consider using @velocity 100 for more realistic dynamics
```

Provide flags to control verbosity: `--quiet` (errors only), default (errors + warnings), `--verbose` (errors + warnings + notes), `--all` (everything including suggestions). Rich library's log levels integrate perfectly with Python's logging module for consistent filtering.

## Summary statistics for successful compilation

Users want to know what their compilation achieved. After successful MIDI generation, show meaningful statistics in a scannable format:

```
✅ Compilation successful (1.4s)

   Input:  main.mml (245 lines)
   Output: main.mid (18.2 KB)
   
   📊 Composition Details:
      5 tracks (Piano, Bass, Drums, Strings, Flute)
      32 measures at 120 BPM
      Duration: 1:04 (64 seconds)
      Notes: 1,247 events
   
   🎵 MIDI Format 1 (multi-track)
      Resolution: 480 PPQ
      Channels: 1, 2, 3, 4, 5
```

Include actionable next steps:

```
   ▶ Play:    mmlc play main.mid
   📝 Inspect: mmlc info main.mid  
   🔧 Edit:    vim main.mml
```

Rich library's Panel and Table classes create beautiful, professional output for statistics. Use emoji sparingly (only for top-level categories), bold key numbers, and dim/gray for less critical details.

## Lark parser integration for excellent position tracking

Lark parsing library excels at position tracking when configured correctly. Enable position propagation at parser creation:

```python
from lark import Lark

parser = Lark(
    grammar,
    parser='lalr',           # Fast, supports error recovery
    propagate_positions=True, # Essential for error reporting
    maybe_placeholders=False  # Cleaner parse trees
)
```

This gives every token and tree node `line`, `column`, `end_line`, and `end_column` attributes (1-indexed). For MML compiler error messages:

```python
from lark import UnexpectedToken, UnexpectedCharacters

try:
    tree = parser.parse(source_text)
except UnexpectedToken as e:
    # e.token has position info
    # e.expected contains valid token types
    show_parse_error(
        source_text,
        line=e.line,
        column=e.column,
        token=e.token.value,
        expected=format_expected(e.expected)
    )
except UnexpectedCharacters as e:
    # e.char is the unexpected character
    # e.allowed contains valid characters
    show_lexer_error(
        source_text,
        line=e.line,
        column=e.column,
        char=e.char,
        allowed=e.allowed
    )
```

For semantic errors detected during tree transformation, use `v_args(meta=True)` decorator to access position metadata:

```python
from lark import Transformer, v_args

class MMLValidator(Transformer):
    @v_args(meta=True)
    def note(self, meta, name, octave, duration):
        if octave < 0 or octave > 10:
            raise ValidationError(
                f"Octave {octave} out of range (0-10)",
                line=meta.line,
                column=meta.column
            )
        return Note(name, octave, duration)
```

The `meta` parameter contains `line`, `column`, `end_line`, `end_column` for the entire tree node span. Store this in your AST nodes for precise error reporting throughout compilation phases.

## Python library stack for professional CLI

After evaluating all major Python CLI libraries, the optimal stack for MML compiler combines three tools: **Typer for command-line argument parsing, Rich for output formatting (included with Typer), and optionally Questionary for interactive prompts**.

**Typer** is the modern choice over Click—it uses Python type hints for argument declaration, reducing boilerplate by ~40%. Where Click requires decorators for every parameter, Typer infers from function signature:

```python
import typer
from pathlib import Path
from rich.console import Console

app = typer.Typer()
console = Console()

@app.command()
def compile(
    input_file: Path = typer.Argument(..., help="MML source file"),
    output: Path = typer.Option(None, "-o", "--output", help="Output MIDI file"),
    verbose: bool = typer.Option(False, "-v", "--verbose"),
    no_color: bool = typer.Option(False, "--no-color")
):
    """Compile MML source to MIDI file."""
    
    if no_color:
        console = Console(no_color=True)
    
    console.print(f"[blue]Compiling[/blue] {input_file}...")
    
    try:
        # Your compilation logic
        midi_data = compile_mml(input_file)
        
        output_path = output or input_file.with_suffix('.mid')
        output_path.write_bytes(midi_data)
        
        console.print(f"[green]✓[/green] Success: {output_path}")
        
    except CompilationError as e:
        show_error(console, e)
        raise typer.Exit(1)

if __name__ == "__main__":
    app()
```

**Rich** provides everything for beautiful output: colored text with BBCode-like markup (`[red]text[/red]`), tables with Unicode borders, progress bars with customizable columns, syntax highlighting for code snippets (perfect for showing MML source in errors), and panels for grouped content. The automatic TTY detection and NO_COLOR support handles accessibility without extra code.

For sophisticated progress tracking during multi-file compilation:

```python
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    BarColumn(),
    TaskProgressColumn(),
    console=console
) as progress:
    
    task = progress.add_task("Compiling tracks...", total=len(tracks))
    
    for track in tracks:
        progress.update(task, description=f"Processing {track.name}")
        process_track(track)
        progress.advance(task)
```

**Questionary** adds professional interactive prompts when needed (configuration wizards, missing file paths):

```python
import questionary

if not input_file:
    input_file = questionary.path(
        "Select MML file:",
        only_files=True,
        validate=lambda p: p.endswith('.mml')
    ).ask()
```

Installation is simple: `pip install typer[all] questionary` gives you everything. The `[all]` extra includes Rich and shell completion support. Total dependency tree is reasonable (~10 packages), all actively maintained through 2024-2025.

## Message format templates for MML compiler

**Parse Error Template**:
```
error[E{code}]: {brief_description}
  → {filename}:{line}:{column}
  
   {line_num-1} | {context_line_before}
   {line_num}   | {source_line}
                | {pointer} {inline_explanation}
   {line_num+1} | {context_line_after}
  
   {detailed_explanation}
   
   💡 {suggestion_if_available}
```

**Validation Error Template**:
```
{severity}[{code}]: {what_is_wrong}
  → {filename}:{line}:{column}
  
   {source_context_with_pointer}
  
   {explanation_in_musical_terms}
   {impact_explanation}
   
   💡 Suggestion: {how_to_fix}
   📖 Learn more: {doc_link}
```

**Warning Template**:
```
warning[W{code}]: {potential_issue}
  → {filename}:{line}:{column}
  
   {minimal_context}
      {pointer} {why_this_might_be_problem}
  
   💡 Consider: {alternative_approach}
```

**Success Summary Template**:
```
✅ Compilation successful ({time_elapsed})

   Input:  {source_file} ({line_count} lines)
   Output: {midi_file} ({file_size})
   
   📊 Composition:
      {track_count} tracks ({track_names})
      {measure_count} measures at {tempo} BPM  
      Duration: {mm:ss} ({seconds} seconds)
      Events: {note_count} notes
   
   🎵 MIDI Format {format_type}
      Resolution: {ppq} PPQ
      Channels: {channels}
```

**Progress Indication Templates**:
```
# Indeterminate (lexing, quick operations)
⠋ {phase_name}... ({current_item})

# Determinate (multiple files/tracks)
{phase_name} ({current}/{total})...
✓ {completed_item}
✓ {completed_item}
⠋ {current_item}

# Long operations with ETA
{phase_name} [████████░░░░] {percent}% ETA {seconds}s
```

## When to use color, emoji, and rich formatting

**Color usage rules**: Use color for all terminal output when TTY is detected and NO_COLOR is unset. Red for errors, yellow for warnings, green for success, blue/cyan for informational. Never use color as sole information carrier—always combine with text or symbols. Disable automatically when piping to file or when running in CI environments (detect via `CI` environment variable).

**Emoji guidelines**: Use sparingly (max 3 per message), only for high-level status indicators (✓ success, ✗ error, ⚠ warning, ⠋ working). Place at line starts or ends, never mid-sentence. Provide `--no-emoji` flag. For MML compiler, consider music-specific emoji (🎵, 🎹, 🎸) for thematic consistency, but test with screen readers first. When in doubt, omit emoji—the text should always be complete without them.

**Bold and emphasis**: Bold error codes, file locations, problematic identifiers, key numbers in statistics, and primary suggestions. Use dim/gray for de-emphasized content like line numbers, less important context, and timestamp details. Rich library markup: `[bold red]` for emphasis, `[dim]` for de-emphasis.

**Tables and panels**: Use Rich's Table class for structured data (compilation statistics, multiple file results, instrument definitions). Use Panel for grouping related information (help sections, detailed explanations, suggestions). Both render as plain text when colors are disabled, maintaining readability.

**Syntax highlighting**: For showing MML source code in error messages, use Rich's Syntax class with custom MML lexer (define using Pygments). This adds dramatic readability to multi-line error context. Falls back gracefully to plain text without highlighting in limited terminals.

## Presenting validation errors vs parse errors

**Parse errors** occur during syntax analysis—unexpected tokens, missing delimiters, malformed structures. These should show the exact location where parsing failed and what tokens were expected:

```
error[E101]: Unexpected token
  → melody.mml:15:8
  
   15 | C4 q D4 q E4 ] F4 q
      |              ^ Expected note, rest, or end of track
      |                Found ']' (closing bracket)
   
   💡 Note: Brackets [] are for grouping or chords
      Did you mean to start a chord? [C4 E4 G4]
```

**Validation errors** occur after successful parsing—semantic issues like undefined references, type mismatches, constraint violations. These should explain the problem in domain terms (musical concepts) and show broader context:

```
error[E203]: Time signature violation
  → song.mml:45:1
  
   Measure 12 contains 5 quarter notes but 4/4 time signature expects 4.
   
   Measure content:
   45 | C4 q D4 q E4 q F4 q G4 q
      | ^^^^^^^^^^^^^^^^^^^^^^^^^ Total duration: 5 quarters
   
   In 4/4 time, each measure must contain exactly 4 quarter notes
   (or equivalent: 2 half notes, 1 whole note, 8 eighth notes, etc.)
   
   💡 Solutions:
      • Remove one note: C4 q D4 q E4 q F4 q
      • Change to 5/4 time: @time 5/4
      • Split across measures: C4 q D4 q E4 q F4 q | G4 q
```

The key difference: parse errors are localized syntax problems with mechanical fixes, validation errors are semantic issues requiring musical understanding. Reflect this in error messages—parse errors can be terse and technical, validation errors should be educational and contextual.

## Progress indication during compilation phases

Structure MML compilation as distinct phases with appropriate progress indicators for each:

**Phase 1: Lexical Analysis** (usually fast, \<100ms)
- Simple spinner: `⠋ Lexing source files...`
- Update message when processing multiple files
- No percentage—duration unpredictable

**Phase 2: Parsing** (fast for typical files)
- For single file: Spinner `⠋ Parsing MML syntax...`
- For multiple files: Counter format with track names
```
Parsing tracks (3/5)...
✓ Piano (main.mml:1-45)
✓ Bass (main.mml:46-89)
⠋ Drums (drums.mml:1-32)
```

**Phase 3: Semantic Validation** (can be slow for large compositions)
- Progress bar if validating many measures: `Validating [████░░] 65%`
- Or counter: `Validating measures (42/64)...`
- Show what's being checked: `Checking timing... Checking pitch ranges... Checking instruments...`

**Phase 4: MIDI Generation** (usually fast)
- Simple spinner: `⠋ Generating MIDI events...`
- Or if generating multiple tracks in parallel: `Generating track 3/5 (Strings)...`

**Phase 5: File I/O** (instant for typical sizes)
- Single line: `Writing output to main.mid...`
- Or include in success message

**Non-TTY fallback**: In CI/CD or when piped, output phase names without animation:
```
[1/5] Lexing source files...
[2/5] Parsing MML syntax...
[3/5] Validating composition...
[4/5] Generating MIDI events...
[5/5] Writing output...
Done.
```

Rich's Progress class handles TTY detection automatically. Define tasks with weights matching phase durations for accurate overall progress bar.

## Accessibility and terminal compatibility considerations

**Screen reader compatibility**: Avoid ASCII art for critical information (use for decoration only). Provide `--no-color` and `--no-emoji` flags. Structure output hierarchically with clear headings. Rich library respects `NO_COLOR` environment variable automatically. Test with NVDA (Windows) or Orca (Linux) screen readers to verify error messages are comprehensible when read aloud.

**Color blindness support** (affects ~8% of men): Never use color alone to distinguish error severity—always combine with symbols (✗, ⚠, ℹ) and text labels (error, warning, note). Avoid red/green as only distinction. The red-yellow-blue color scheme works well because it separates colors by both hue and brightness. Test with colorblind simulation tools (Coblis, Colorblindly browser extensions).

**Terminal compatibility**: Rich library detects terminal capabilities automatically and degrades gracefully—true color in modern terminals, 256 colors in xterm-256color, 16 colors in basic terminals, plain text when colors unsupported. Windows compatibility is excellent with Rich (works in cmd.exe, PowerShell, and modern Windows Terminal). For maximum compatibility, avoid Unicode box-drawing characters in critical output—Rich falls back to ASCII automatically.

**CI/CD environments**: Detect when running in continuous integration (check `CI` env var) and automatically switch to simple line-based output without progress bars or spinners. GitHub Actions, GitLab CI, Jenkins all set this variable. Rich handles this via TTY detection, but add explicit check for `CI` env var:

```python
from rich.console import Console
import os

console = Console(
    force_terminal=False if os.getenv('CI') else None,
    no_color=os.getenv('NO_COLOR') is not None
)
```

## Example implementation: Complete error handler

Here's a production-ready error handling system integrating Lark, Rich, and the patterns discussed:

```python
from dataclasses import dataclass
from pathlib import Path
from lark import Lark, UnexpectedToken, UnexpectedCharacters, UnexpectedInput
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
import sys

@dataclass
class CompilerError:
    """Structured error information"""
    code: str
    severity: str  # 'error', 'warning', 'note'
    message: str
    filename: str
    line: int
    column: int
    source_line: str
    suggestion: str = None
    
console = Console()

def show_error(error: CompilerError, source_text: str):
    """Display error with Rich formatting and code context"""
    
    # Severity color and emoji
    if error.severity == 'error':
        color, emoji = 'red', '✗'
    elif error.severity == 'warning':
        color, emoji = 'yellow', '⚠'
    else:
        color, emoji = 'blue', 'ℹ'
    
    # Header
    console.print(
        f"[{color}]{emoji} {error.severity}[{error.code}][/{color}]: "
        f"{error.message}"
    )
    console.print(f"  [cyan]→[/cyan] {error.filename}:{error.line}:{error.column}\n")
    
    # Code context with syntax highlighting
    lines = source_text.split('\n')
    start_line = max(0, error.line - 3)
    end_line = min(len(lines), error.line + 2)
    
    # Build context with line numbers
    for i in range(start_line, end_line):
        line_num = i + 1
        line_content = lines[i] if i < len(lines) else ""
        
        # Highlight error line
        if line_num == error.line:
            console.print(f"   {line_num:4} | {line_content}")
            # Pointer line
            pointer_padding = ' ' * (error.column - 1)
            console.print(
                f"        | {pointer_padding}[{color}]^[/{color}] "
                f"[{color}]{error.message}[/{color}]"
            )
        else:
            console.print(f"   [dim]{line_num:4}[/dim] | [dim]{line_content}[/dim]")
    
    # Suggestion if available
    if error.suggestion:
        console.print(f"\n   [yellow]💡 {error.suggestion}[/yellow]")
    
    console.print()  # Blank line after error

def parse_mml(source_file: Path) -> CompilerError:
    """Parse MML file and return tree or error"""
    
    source_text = source_file.read_text()
    
    try:
        tree = parser.parse(source_text)
        return tree
        
    except UnexpectedToken as e:
        # Format expected tokens in friendly way
        expected = format_expected_tokens(e.expected)
        
        error = CompilerError(
            code='E101',
            severity='error',
            message=f"Expected {expected}, found '{e.token.value}'",
            filename=str(source_file),
            line=e.line,
            column=e.column,
            source_line=source_text.split('\n')[e.line-1],
            suggestion=suggest_fix(e)
        )
        
        show_error(error, source_text)
        return None
        
    except UnexpectedCharacters as e:
        error = CompilerError(
            code='E102',
            severity='error',
            message=f"Unexpected character '{e.char}'",
            filename=str(source_file),
            line=e.line,
            column=e.column,
            source_line=source_text.split('\n')[e.line-1],
            suggestion=f"Valid characters here: {format_allowed(e.allowed)}"
        )
        
        show_error(error, source_text)
        return None

def format_expected_tokens(expected_set):
    """Convert token names to friendly descriptions"""
    friendly = {
        'NOTE': 'a note (C, D, E, F, G, A, B)',
        'DURATION': 'a duration (w, h, q, e, s)',
        'NUMBER': 'a number',
        'INSTRUMENT': 'an instrument name',
    }
    
    tokens = [friendly.get(t, t) for t in expected_set if not t.startswith('_')]
    
    if len(tokens) == 1:
        return tokens[0]
    elif len(tokens) == 2:
        return f"{tokens[0]} or {tokens[1]}"
    else:
        return ', '.join(tokens[:-1]) + f', or {tokens[-1]}'

def suggest_fix(error: UnexpectedInput) -> str:
    """Generate suggestion based on error context"""
    # Use Levenshtein distance to find similar valid tokens
    if hasattr(error, 'token'):
        typed = error.token.value.lower()
        valid_options = get_valid_identifiers()
        
        close_matches = [
            opt for opt in valid_options 
            if levenshtein_distance(typed, opt.lower()) <= 2
        ]
        
        if close_matches:
            if len(close_matches) == 1:
                return f"Did you mean '{close_matches[0]}'?"
            else:
                matches = ', '.join(f"'{m}'" for m in close_matches[:3])
                return f"Did you mean one of: {matches}?"
    
    return None

# Usage in compiler
def compile_mml(input_file: Path, output_file: Path):
    """Main compilation function"""
    
    console.print(f"[blue]Compiling[/blue] {input_file}...")
    
    # Parse
    tree = parse_mml(input_file)
    if tree is None:
        sys.exit(1)
    
    # Validate
    errors = validate_composition(tree, input_file)
    if errors:
        for error in errors:
            show_error(error, input_file.read_text())
        console.print(f"[red]Compilation failed with {len(errors)} errors[/red]")
        sys.exit(1)
    
    # Generate MIDI
    with console.status("[blue]Generating MIDI...[/blue]"):
        midi_data = generate_midi(tree)
    
    # Write output
    output_file.write_bytes(midi_data)
    
    # Success message
    console.print(f"[green]✓ Success:[/green] {output_file} ({len(midi_data)} bytes)")
```

This implementation demonstrates all best practices: structured error objects, Rich formatting with automatic terminal detection, friendly token name translation, "did you mean" suggestions, code context with line numbers, and clear severity indicators.

## Recommended error code taxonomy for MML

Organize error codes by category for easy reference and documentation:

**E1xx: Lexical/Parsing Errors**
- E101: Unexpected token
- E102: Unexpected character  
- E103: Unterminated string/comment
- E104: Invalid number format
- E105: Missing closing delimiter

**E2xx: Semantic/Validation Errors**
- E201: Undefined reference (instrument, macro, etc.)
- E202: Duplicate definition
- E203: Time signature violation
- E204: Invalid note range
- E205: Invalid tempo value
- E206: Invalid duration value

**E3xx: Type/Constraint Errors**
- E301: Type mismatch
- E302: Invalid operation
- E303: Constraint violation
- E304: Invalid parameter value

**E4xx: File/Import Errors**
- E401: File not found
- E402: Import cycle detected
- E403: Permission denied
- E404: Invalid file format

**W1xx-W4xx: Warnings** (parallel to errors)
- W201: Unused definition
- W202: Deprecated syntax
- W203: Note out of typical range
- W204: Unusual tempo marking

Each code should have detailed explanation accessible via `mmlc --explain E203` showing common causes, examples, and solutions.

## Creating documentation that matches your CLI

Modern CLIs provide multi-level help: inline `--help`, detailed `--explain` for error codes, man pages, and web documentation. For MML compiler:

**Level 1: Brief inline help** (`mmlc --help`)
```
MML Compiler - Convert MIDI Markup Language to MIDI files

USAGE:
    mmlc [OPTIONS] <INPUT>

ARGUMENTS:
    <INPUT>    MML source file to compile

OPTIONS:
    -o, --output <FILE>    Output MIDI file path [default: same as input]
    -v, --verbose          Show detailed compilation progress
    --no-color             Disable colored output
    --explain <CODE>       Show detailed explanation for error code
    -h, --help            Show this help message

EXAMPLES:
    mmlc song.mml                  # Compile to song.mid
    mmlc song.mml -o music.mid     # Specify output file
    mmlc --explain E203            # Explain error E203
```

**Level 2: Error code explanations** (`mmlc --explain E203`)
```
Error E203: Time signature violation

DESCRIPTION:
    A measure contains more or fewer notes than the time signature allows.
    In 4/4 time, each measure must total exactly 4 quarter notes (or equivalent).

COMMON CAUSES:
    • Forgot to add measure separator (|)
    • Miscounted note durations
    • Changed time signature mid-piece

EXAMPLES:
    Incorrect:
        @time 4/4
        C4 q D4 q E4 q F4 q G4 q  ← 5 quarters, should be 4
    
    Correct:
        @time 4/4
        C4 q D4 q E4 q F4 q |     ← Exactly 4 quarters
        G4 q A4 q B4 q C5 q       ← Next measure

SEE ALSO:
    • Time signatures: https://docs.mmlc.org/time-signatures
    • Measure syntax: https://docs.mmlc.org/measures
    • Duration values: https://docs.mmlc.org/durations
```

**Level 3: Web documentation** with comprehensive guides, tutorials, reference sections, and searchable error index.

## Final recommendations summary

Your MML compiler should embody these principles:

**1. Error messages are teaching moments** - Explain problems in musical domain language, not technical parser jargon. Every error should help users understand both what went wrong and why it matters for their composition.

**2. Visual hierarchy guides understanding** - Use color (red/yellow/green), bold for critical elements, proper spacing and indentation, code context with line numbers, and inline labels that create flow from problem to explanation.

**3. Position information is sacred** - Always show exact file:line:column references in clickable format. Display source code context with carets pointing to problems. Store position metadata through all compilation phases for precise error reporting.

**4. Accessibility is non-negotiable** - Provide `--no-color` and `--no-emoji` flags. Never use color alone to convey severity. Test with screen readers. Respect NO_COLOR environment variable. Detect TTY for automatic graceful degradation.

**5. Progress feedback prevents anxiety** - Show spinners for indeterminate tasks, counters for sequential processing, progress bars for long operations. Provide clear phase transitions. In CI environments, use simple line-based output without animation.

**6. Stack Typer + Rich for Python CLI** - Typer provides modern type-hint-based argument parsing with minimal boilerplate. Rich (included) provides beautiful formatting, progress bars, syntax highlighting, and automatic terminal compatibility. Together they eliminate 80% of CLI implementation tedium.

**7. Integrate Lark with position tracking** - Enable `propagate_positions=True` for automatic line/column tracking. Use `v_args(meta=True)` to access position in transformers. Store metadata in AST nodes for semantic validation errors. Customize UnexpectedToken/UnexpectedCharacters exceptions for friendly parse errors.

**8. Structure matters more than decoration** - A well-structured plain text error message with clear sections, proper spacing, and logical flow is infinitely more valuable than a colorful mess. Use Rich's formatting to enhance structure, not replace it.

Build your MML compiler with these patterns and it will stand alongside Rust, Elm, and TypeScript as an exemplar of compiler user experience—making music composition in text delightful and errors into learning opportunities.