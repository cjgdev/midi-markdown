# Lexer Quick Reference Card

Quick lookup for implementing the MMD lexer. See [lexer_design.md](./lexer_design.md) for full details.

## Token Types (26 total)

### Structural (11)
```
DASH        -       Command prefix
AT          @       Directive prefix / simultaneous marker
HASH        #       Comment start
LBRACKET    [       Timing/array start
RBRACKET    ]       Timing/array end
LBRACE      {       Parameter placeholder start
RBRACE      }       Parameter placeholder end
DOT         .       Separator in dotted notation
COLON       :       Time separator
EQUALS      =       Assignment operator
COMMA       ,       Parameter separator
```

### Values (4)
```
IDENTIFIER          Command/variable/note names (pc, TEMPO, C4, etc.)
NUMBER              Integers and floats (127, 120.5, -8192)
STRING              Quoted strings ("text")
TIMECODE            Timing values (00:00.000, 1.1.000, +1b, +250ms)
```

### Keywords (9)
```
IMPORT      @import
DEFINE      @define
ALIAS       @alias
END         @end
IF          @if
ELIF        @elif
ELSE        @else
LOOP        @loop
TRACK       @track
```

### Special (2)
```
COMMENT     # or // or /* */
EOF         End of file marker
```

## Timing Notation Patterns

```python
ABSOLUTE_TIME   = r'\d{2}:\d{2}\.\d{3}'          # 00:00.000
MUSICAL_TIME    = r'\d+\.\d+\.\d{3}'             # 1.1.000
RELATIVE_UNIT   = r'\+\d+\.?\d*[smbt]'           # +1b, +0.5s, +250ms
RELATIVE_MUSIC  = r'\+\d+\.\d+\.\d+'             # +2.1.0
SIMULTANEOUS    = r'@'                            # [@]
```

## Scanner Dispatch Logic

```python
def _scan_token(self) -> Token | None:
    char = self._peek()

    # Order matters!
    if char == '#':                                    return self._scan_comment()
    if char == '/' and self._peek_next() == '/':      return self._scan_comment()
    if char == '/' and self._peek_next() == '*':      return self._scan_multiline_comment()
    if char == '[':                                    return self._scan_timing_or_bracket()
    if char == '@':                                    return self._scan_directive()
    if char == '"':                                    return self._scan_string()
    if char.isdigit() or (char == '-' and next_digit): return self._scan_number()
    if char.isalpha() or char in '_$':                return self._scan_identifier()

    return self._scan_single_char()  # -, @, [, ], {, }, ., :, =, ,
```

## Essential Helpers

```python
def _advance(self) -> str:
    """Consume and return char, update line/column."""
    char = self.source[self.position]
    self.position += 1
    if char == '\n':
        self.line += 1
        self.column = 1
    else:
        self.column += 1
    return char

def _peek(self) -> str:
    """Current char without consuming."""
    return self.source[self.position] if not self._is_at_end() else '\0'

def _peek_next(self) -> str:
    """Next char without consuming."""
    return self.source[self.position + 1] if self.position + 1 < len(self.source) else '\0'

def _skip_whitespace(self) -> None:
    """Skip spaces, tabs, newlines."""
    while not self._is_at_end() and self._peek() in ' \t\r\n':
        self._advance()
```

## Common Patterns

### Scanner Template
```python
def _scan_xxx(self) -> Token:
    start_line = self.line
    start_col = self.column

    # Consume starting character(s)
    self._advance()

    # Accumulate content
    content = ""
    while not self._is_at_end() and <condition>:
        content += self._advance()

    return Token(TokenType.XXX, content, start_line, start_col)
```

### Read Until Pattern
```python
# Read until delimiter
while not self._is_at_end() and self._peek() != delimiter:
    content += self._advance()

# Read while condition
while not self._is_at_end() and char.isalnum():
    content += self._advance()
```

### Escape Sequence Handling
```python
if self._peek() == '\\':
    self._advance()  # consume backslash
    escape_char = self._advance()
    content += {'n': '\n', 't': '\t', '"': '"', '\\': '\\'}[escape_char]
```

## Directive Mapping

```python
DIRECTIVE_MAP = {
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
```

## Error Handling

```python
class LexerError(Exception):
    def __init__(self, message: str, line: int, column: int):
        super().__init__(f"Lexer error at {line}:{column}: {message}")

# Usage
if self._is_at_end():
    raise LexerError("Unclosed string", start_line, start_col)
```

## Test Commands

```bash
# Run all lexer tests
pytest tests/unit/test_lexer.py -v

# Run specific test class
pytest tests/unit/test_lexer.py::TestTimingTokens -v

# Run single test
pytest tests/unit/test_lexer.py::TestLexerBasics::test_empty_source -v

# Run with coverage
pytest tests/unit/test_lexer.py --cov=src/midi_markdown/parser/lexer --cov-report=term-missing

# Lint and format
ruff check src/midi_markdown/parser/lexer.py
ruff format src/midi_markdown/parser/lexer.py
mypy src/midi_markdown/parser/lexer.py
```

## Implementation Order

1. ✅ Helper methods: `_advance`, `_peek`, `_peek_next`, `_skip_whitespace`
2. ✅ `_scan_single_char()` - Structural tokens
3. ✅ `_scan_number()` - Numbers (int/float/negative)
4. ✅ `_scan_identifier()` - Names and keywords
5. ✅ `_scan_string()` - Quoted strings with escapes
6. ✅ `_scan_comment()` - Single-line comments
7. ✅ `_scan_multiline_comment()` - Block comments
8. ✅ `_scan_directive()` - @ keywords
9. ✅ `_scan_timing_or_bracket()` - Timing notation
10. ✅ `tokenize()` - Main loop
11. ✅ `next_token()` - Incremental parsing
12. ✅ `peek_token()` - Lookahead

## Common Pitfalls

❌ **Don't**: Check for `[` as single char before checking timing
✅ **Do**: Handle timing notation first, then fall back to single bracket

❌ **Don't**: Forget to update line/column in `_advance()`
✅ **Do**: Always track position for error reporting

❌ **Don't**: Consume characters without checking `_is_at_end()`
✅ **Do**: Guard all character access with end-of-file checks

❌ **Don't**: Skip whitespace inside strings or comments
✅ **Do**: Only skip whitespace between tokens

❌ **Don't**: Return `None` from scanners
✅ **Do**: Always return a Token, raise LexerError for invalid syntax

## Edge Cases to Handle

- Empty files → Single EOF token
- Whitespace-only → Single EOF token
- Unclosed strings → LexerError
- Unclosed comments → LexerError
- Invalid timing format → LexerError
- Negative numbers vs. dash → Check if followed by digit
- `[@]` vs. `[` `@` → Special handling for simultaneous execution
- Variable refs `${VAR}` → Parse as single IDENTIFIER token
- Note names `C4`, `D#5` → Parse as IDENTIFIER (validation in parser)
- Unicode in strings/comments → Allow and preserve
- Multiple dots `1..5` → NUMBER DOT DOT NUMBER
- EOF mid-token → Raise appropriate error

## Example Tokenization

**Input:**
```
[00:00.000]
- pc 1.5
```

**Output:**
```
Token(LBRACKET, '[', 1, 1)
Token(TIMECODE, '00:00.000', 1, 2)
Token(RBRACKET, ']', 1, 11)
Token(DASH, '-', 2, 1)
Token(IDENTIFIER, 'pc', 2, 3)
Token(NUMBER, '1', 2, 6)
Token(DOT, '.', 2, 7)
Token(NUMBER, '5', 2, 8)
Token(EOF, '', 2, 9)
```

## Performance Tips

- Use `str.isdigit()`, `str.isalpha()` - They're fast
- Concatenate strings directly for short content
- Compile regex patterns once (module level)
- Skip whitespace efficiently (tight loop)
- Avoid unnecessary string copying

## Resources

- **Full Design**: [lexer_design.md](./lexer_design.md)
- **Summary**: [lexer_summary.md](../lexer-summary.md)
- **Tests**: [../tests/unit/test_lexer.py](../tests/unit/test_lexer.py)
- **Spec**: [specification.md](../../../reference/specification.md) lines 84-531
- **Implementation**: [../src/midi_markdown/parser/lexer.py](../src/midi_markdown/parser/lexer.py)
