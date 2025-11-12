# Lexer Design Document

## Overview

This document defines the complete design and implementation strategy for the MIDI Markdown (MMD) lexer. The lexer is the first component in the compilation pipeline, responsible for breaking source code into tokens.

## Goals

1. **Tokenize MMD source code** into a stream of typed tokens
2. **Track position information** (line/column) for error reporting
3. **Handle all MMD syntax elements** per [specification.md](../../reference/specification.md)
4. **Provide clear error messages** for invalid syntax
5. **Support incremental parsing** via `next_token()` and `peek_token()`

## Token Types

Based on [specification.md](../../reference/specification.md), the lexer must recognize these token types:

### Structural Tokens
- `DASH` (`-`) - Command prefix
- `AT` (`@`) - Directive prefix
- `HASH` (`#`) - Comment start
- `LBRACKET` (`[`) - Timing/array start
- `RBRACKET` (`]`) - Timing/array end
- `LBRACE` (`{`) - Parameter placeholder start
- `RBRACE` (`}`) - Parameter placeholder end
- `DOT` (`.`) - Separator in dotted notation
- `COLON` (`:`) - Time separator
- `EQUALS` (`=`) - Assignment
- `COMMA` (`,`) - Parameter separator

### Value Tokens
- `IDENTIFIER` - Command names, variable names, note names
- `NUMBER` - Integers and floats (including negative)
- `STRING` - Quoted strings with escape sequences
- `TIMECODE` - Complete timing values (parsed as single token)

### Keyword Tokens (Directives)
- `IMPORT` (`@import`)
- `DEFINE` (`@define`)
- `ALIAS` (`@alias`)
- `END` (`@end`)
- `IF` (`@if`)
- `ELIF` (`@elif`)
- `ELSE` (`@else`)
- `LOOP` (`@loop`)
- `TRACK` (`@track`)

### Special Tokens
- `NEWLINE` - Line ending (optional, for tracking)
- `EOF` - End of file
- `COMMENT` - Comment content

## Timing Notation Tokenization

Timing is a critical part of MML. The lexer must recognize and parse timing notation inside brackets as a single `TIMECODE` token:

### Absolute Timecode
- Format: `[mm:ss.milliseconds]`
- Examples: `[00:00.000]`, `[01:23.250]`
- Regex: `\d{2}:\d{2}\.\d{3}`

### Musical Time
- Format: `[bars.beats.ticks]`
- Examples: `[1.1.000]`, `[8.4.120]`
- Regex: `\d+\.\d+\.\d{3}`

### Relative Delta
- Format: `[+value unit]` or `[+musical.time]`
- Examples: `[+0.500s]`, `[+1b]`, `[+250ms]`, `[+2.1.0]`
- Regex: `\+\d+\.?\d*[smbt]?` or `\+\d+\.\d+\.\d+`

### Simultaneous Execution
- Format: `[@]`
- Special marker for same-time execution

## Lexer Implementation Strategy

### Core Data Structure

```python
class Lexer:
    def __init__(self, source: str) -> None:
        self.source = source          # Original source code
        self.position = 0             # Current position in source
        self.line = 1                 # Current line number (1-indexed)
        self.column = 1               # Current column number (1-indexed)
        self.tokens: list[Token] = [] # Accumulated tokens (for tokenize())
```

### Main Entry Points

1. **`tokenize() -> list[Token]`**
   - Tokenize entire source into list of tokens
   - Used by parser to get all tokens at once
   - Simpler for most use cases

2. **`next_token() -> Token`**
   - Get next token and advance position
   - Used for incremental parsing
   - Returns EOF token when exhausted

3. **`peek_token() -> Token`**
   - Look at next token without consuming
   - Used for lookahead in parser
   - Does not advance position

### Tokenization Algorithm

```python
def tokenize(self) -> list[Token]:
    """Main tokenization loop."""
    while not self._is_at_end():
        self._skip_whitespace()
        if self._is_at_end():
            break

        token = self._scan_token()
        if token:
            self.tokens.append(token)

    self.tokens.append(self._make_token(TokenType.EOF, ""))
    return self.tokens

def _scan_token(self) -> Token | None:
    """Dispatch to specific token scanners based on next character."""
    char = self._peek()

    # Comments (highest priority to handle # before timing)
    if char == '#':
        return self._scan_comment()
    if char == '/' and self._peek_next() == '/':
        return self._scan_comment()
    if char == '/' and self._peek_next() == '*':
        return self._scan_multiline_comment()

    # Timing notation (must check before @ for [@])
    if char == '[':
        return self._scan_timing_or_bracket()

    # Directives (@import, @define, etc.)
    if char == '@':
        return self._scan_directive()

    # Strings
    if char == '"':
        return self._scan_string()

    # Numbers (including negative numbers)
    if char.isdigit() or (char == '-' and self._peek_next().isdigit()):
        return self._scan_number()

    # Identifiers, keywords, note names
    if char.isalpha() or char == '_' or char == '$':
        return self._scan_identifier()

    # Single character tokens
    return self._scan_single_char()
```

### Token Scanner Methods

#### 1. Timing Scanner

```python
def _scan_timing_or_bracket(self) -> Token:
    """Scan timing notation or just a bracket."""
    start_line = self.line
    start_col = self.column

    self._advance()  # consume '['

    # Check for simultaneous execution [@]
    if self._peek() == '@' and self._peek_next() == ']':
        # This is [@], return LBRACKET and let normal scanning handle @ and ]
        return self._make_token(TokenType.LBRACKET, '[')

    # Try to parse timing content
    timing_content = ""
    while not self._is_at_end() and self._peek() != ']':
        timing_content += self._advance()

    if self._is_at_end():
        raise LexerError("Unclosed bracket", start_line, start_col)

    self._advance()  # consume ']'

    # Validate timing format and create TIMECODE token
    if self._is_valid_timecode(timing_content):
        # Return compound token: LBRACKET + TIMECODE + RBRACKET
        # OR return just TIMECODE with brackets included
        # Decision: Return 3 separate tokens for parser flexibility
        self.tokens.append(Token(TokenType.LBRACKET, '[', start_line, start_col))
        self.tokens.append(Token(TokenType.TIMECODE, timing_content, start_line, start_col + 1))
        return Token(TokenType.RBRACKET, ']', self.line, self.column - 1)
    else:
        # Not a timing, just return LBRACKET and rewind
        # Actually, we already consumed content - this is error case
        raise LexerError(f"Invalid timing format: {timing_content}", start_line, start_col)

def _is_valid_timecode(self, content: str) -> bool:
    """Check if string is valid timing notation."""
    import re

    # Absolute: 00:00.000
    if re.match(r'^\d{2}:\d{2}\.\d{3}$', content):
        return True

    # Musical: 1.1.000
    if re.match(r'^\d+\.\d+\.\d{3}$', content):
        return True

    # Relative with units: +0.500s, +1b, +250ms
    if re.match(r'^\+\d+\.?\d*[smbt]$', content):
        return True

    # Relative musical: +2.1.0
    if re.match(r'^\+\d+\.\d+\.\d+$', content):
        return True

    return False
```

#### 2. Directive Scanner

```python
def _scan_directive(self) -> Token:
    """Scan @ directives like @import, @define, etc."""
    start_col = self.column
    self._advance()  # consume '@'

    # Get directive name
    directive_name = ""
    while not self._is_at_end() and (self._peek().isalnum() or self._peek() == '_'):
        directive_name += self._advance()

    # Map to keyword token type
    directive_map = {
        'import': TokenType.IMPORT,
        'define': TokenType.DEFINE,
        'alias': TokenType.ALIAS,
        'end': TokenType.END,
        'if': TokenType.IF,
        'elif': TokenType.ELIF,
        'else': TokenType.ELSE,
        'loop': TokenType.LOOP,
        'track': TokenType.TRACK,
    }

    token_type = directive_map.get(directive_name, TokenType.AT)

    if token_type == TokenType.AT:
        # Unknown directive, just return @ and let identifier be scanned next
        return self._make_token(TokenType.AT, '@')

    return Token(token_type, f'@{directive_name}', self.line, start_col)
```

#### 3. Comment Scanner

```python
def _scan_comment(self) -> Token:
    """Scan single-line comment (# or //)."""
    start_col = self.column

    # Consume comment start
    if self._peek() == '#':
        self._advance()
    elif self._peek() == '/' and self._peek_next() == '/':
        self._advance()
        self._advance()

    # Read until end of line
    comment_text = ""
    while not self._is_at_end() and self._peek() != '\n':
        comment_text += self._advance()

    return Token(TokenType.COMMENT, comment_text.strip(), self.line, start_col)

def _scan_multiline_comment(self) -> Token:
    """Scan multi-line comment /* ... */."""
    start_line = self.line
    start_col = self.column

    self._advance()  # consume '/'
    self._advance()  # consume '*'

    comment_text = ""
    while not self._is_at_end():
        if self._peek() == '*' and self._peek_next() == '/':
            self._advance()  # consume '*'
            self._advance()  # consume '/'
            break
        comment_text += self._advance()

    return Token(TokenType.COMMENT, comment_text.strip(), start_line, start_col)
```

#### 4. String Scanner

```python
def _scan_string(self) -> Token:
    """Scan quoted string with escape sequences."""
    start_line = self.line
    start_col = self.column

    self._advance()  # consume opening quote

    string_value = ""
    while not self._is_at_end() and self._peek() != '"':
        if self._peek() == '\\':
            # Handle escape sequences
            self._advance()
            if not self._is_at_end():
                escape_char = self._advance()
                # Handle common escapes
                escape_map = {
                    'n': '\n',
                    't': '\t',
                    'r': '\r',
                    '"': '"',
                    '\\': '\\'
                }
                string_value += escape_map.get(escape_char, escape_char)
        else:
            string_value += self._advance()

    if self._is_at_end():
        raise LexerError("Unclosed string", start_line, start_col)

    self._advance()  # consume closing quote

    return Token(TokenType.STRING, string_value, start_line, start_col)
```

#### 5. Number Scanner

```python
def _scan_number(self) -> Token:
    """Scan integer or floating point number."""
    start_col = self.column
    number_str = ""

    # Handle negative sign
    if self._peek() == '-':
        number_str += self._advance()

    # Read digits
    while not self._is_at_end() and self._peek().isdigit():
        number_str += self._advance()

    # Check for decimal point
    if not self._is_at_end() and self._peek() == '.' and self._peek_next().isdigit():
        number_str += self._advance()  # consume '.'
        while not self._is_at_end() and self._peek().isdigit():
            number_str += self._advance()

    return Token(TokenType.NUMBER, number_str, self.line, start_col)
```

#### 6. Identifier Scanner

```python
def _scan_identifier(self) -> Token:
    """Scan identifier, keyword, note name, or variable reference."""
    start_col = self.column
    identifier = ""

    # Handle variable references ${VAR}
    if self._peek() == '$' and self._peek_next() == '{':
        self._advance()  # $
        self._advance()  # {
        while not self._is_at_end() and self._peek() != '}':
            identifier += self._advance()
        if not self._is_at_end():
            self._advance()  # }
        # Return as identifier with original ${} syntax
        return Token(TokenType.IDENTIFIER, f'${{{identifier}}}', self.line, start_col)

    # Regular identifier
    while not self._is_at_end() and (self._peek().isalnum() or self._peek() in '_#'):
        identifier += self._advance()

    return Token(TokenType.IDENTIFIER, identifier, self.line, start_col)
```

#### 7. Single Character Scanner

```python
def _scan_single_char(self) -> Token:
    """Scan single character structural tokens."""
    char = self._advance()

    char_map = {
        '-': TokenType.DASH,
        '@': TokenType.AT,
        '#': TokenType.HASH,
        '[': TokenType.LBRACKET,
        ']': TokenType.RBRACKET,
        '{': TokenType.LBRACE,
        '}': TokenType.RBRACE,
        '.': TokenType.DOT,
        ':': TokenType.COLON,
        '=': TokenType.EQUALS,
        ',': TokenType.COMMA,
    }

    token_type = char_map.get(char)
    if token_type:
        return Token(token_type, char, self.line, self.column - 1)

    # Unknown character - could raise error or skip
    raise LexerError(f"Unexpected character: {char}", self.line, self.column - 1)
```

### Helper Methods

```python
def _advance(self) -> str:
    """Consume and return current character, updating position."""
    if self._is_at_end():
        return '\0'

    char = self.source[self.position]
    self.position += 1

    if char == '\n':
        self.line += 1
        self.column = 1
    else:
        self.column += 1

    return char

def _peek(self) -> str:
    """Return current character without consuming."""
    if self._is_at_end():
        return '\0'
    return self.source[self.position]

def _peek_next(self) -> str:
    """Return next character without consuming."""
    if self.position + 1 >= len(self.source):
        return '\0'
    return self.source[self.position + 1]

def _is_at_end(self) -> bool:
    """Check if at end of source."""
    return self.position >= len(self.source)

def _skip_whitespace(self) -> None:
    """Skip whitespace characters (except newlines if tracking them)."""
    while not self._is_at_end():
        char = self._peek()
        if char in ' \t\r\n':
            self._advance()
        else:
            break

def _make_token(self, type: TokenType, value: str) -> Token:
    """Create token at current position."""
    return Token(type, value, self.line, self.column)
```

## Error Handling

The lexer should raise `LexerError` exceptions for:
- Unclosed strings
- Unclosed brackets
- Invalid timing formats
- Unexpected characters

```python
class LexerError(Exception):
    """Lexer error with position information."""

    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Lexer error at {line}:{column}: {message}")
```

## Test Coverage

The test suite in [tests/unit/test_lexer.py](../tests/unit/test_lexer.py) provides comprehensive coverage:

### Test Categories

1. **Basic Functionality** (3 tests)
   - Initialization
   - Empty source
   - Whitespace only

2. **Timing Tokens** (10 tests)
   - Absolute timecode (multiple formats)
   - Musical time
   - Relative deltas (seconds, beats, musical, milliseconds)
   - Simultaneous execution

3. **Command Tokens** (5 tests)
   - Basic commands
   - Control change
   - Note commands with different accidentals

4. **Directives** (10 tests)
   - All directive types (@import, @define, @alias, @end, @if, @elif, @else, @loop, @track)

5. **Comments** (4 tests)
   - Hash comments
   - Double slash comments
   - Inline comments
   - Multi-line comments

6. **Strings and Values** (6 tests)
   - Quoted strings
   - Escaped quotes
   - Integer/float/negative numbers
   - Variable references

7. **Structural Tokens** (2 tests)
   - All single-char tokens
   - Newline handling

8. **Position Tracking** (3 tests)
   - Line tracking
   - Column tracking
   - Multi-line tracking

9. **Complex Scenarios** (4 tests)
   - Full commands with timing
   - Multiple commands
   - Alias definitions
   - Mixed content

10. **Edge Cases** (5 tests)
    - Unclosed strings
    - Invalid timing
    - Very long numbers
    - Consecutive dots
    - Unicode in comments

11. **Helper Methods** (3 tests)
    - peek_token
    - next_token
    - next_token until EOF

**Total: 55 test cases**

## Implementation Checklist

- [ ] Implement `_advance()`, `_peek()`, `_peek_next()` helpers
- [ ] Implement `_is_at_end()`, `_skip_whitespace()`, `_make_token()`
- [ ] Implement `_scan_single_char()` for structural tokens
- [ ] Implement `_scan_number()` for integers and floats
- [ ] Implement `_scan_identifier()` for names and keywords
- [ ] Implement `_scan_string()` with escape sequences
- [ ] Implement `_scan_comment()` for single-line comments
- [ ] Implement `_scan_multiline_comment()` for /* */ comments
- [ ] Implement `_scan_directive()` for @ keywords
- [ ] Implement `_scan_timing_or_bracket()` for timing notation
- [ ] Implement `_is_valid_timecode()` validation
- [ ] Implement `tokenize()` main loop
- [ ] Implement `next_token()` for incremental parsing
- [ ] Implement `peek_token()` for lookahead
- [ ] Add `LexerError` exception class
- [ ] Run all 55 tests and fix failures
- [ ] Add type hints and docstrings
- [ ] Run ruff and mypy for code quality
- [ ] Test with real MMD examples from [examples/](https://github.com/cjgdev/midi-markdown/tree/main/examples)

## Performance Considerations

1. **Single Pass**: Tokenize in one pass through source
2. **Minimal Backtracking**: Only peek ahead, rarely rewind
3. **Efficient String Building**: Use string concatenation for short strings
4. **Regex for Validation**: Use compiled regex patterns for timing validation

## Future Enhancements

1. **Token Location Ranges**: Track start and end positions for better error messages
2. **Token Metadata**: Add source file name to tokens
3. **Streaming Tokenization**: Support tokenizing from file streams for large files
4. **Better Error Recovery**: Continue tokenizing after errors to report multiple issues
5. **Preprocessor**: Handle frontmatter stripping before tokenization

## References

- **Specification**: [specification.md](../../reference/specification.md) lines 84-531
- **Test Suite**: [tests/unit/test_lexer.py](../tests/unit/test_lexer.py)
- **Implementation**: [src/midi_markdown/parser/lexer.py](../src/midi_markdown/parser/lexer.py)
- **Examples**: [examples/00_basics/01_hello_world.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/00_basics/01_hello_world.mmd)
