---
description: Debug timing issues in MMD files by analyzing timing calculations
---

Help debug timing problems in MMD files. Ask the user for:

1. **File path** to the MMD file with timing issues
2. **Expected timing** vs **actual timing** (if known)
3. **Specific event** or line number that's problematic

Then perform the following analysis:

## Analysis Steps:

### 1. Parse and Read the File
- Parse the MMD file using `MMLParser`
- Extract frontmatter (tempo, time_signature, ppq)
- Show the timing markers and events in question

### 2. Identify Timing Mode
Determine which timing paradigm is used:
- **Absolute**: `[mm:ss.milliseconds]` - Converted via tempo
- **Musical**: `[bars.beats.ticks]` - Requires time signature
- **Relative**: `[+duration unit]` - Depends on previous event
- **Simultaneous**: `[@]` - Uses previous event time

### 3. Show Calculations

For **Absolute timing**:
```python
seconds = mm * 60 + ss + (ms / 1000)
ticks_per_second = (ppq * tempo) / 60.0
absolute_ticks = int(seconds * ticks_per_second)
```

For **Musical timing**:
```python
# Remember: bars and beats are 1-indexed!
beats_per_bar = time_signature[0]
absolute_ticks = (
    (bar - 1) * beats_per_bar * ppq
    + (beat - 1) * ppq
    + tick
)
```

For **Relative timing**:
```python
# Add delta to previous event's time
absolute_ticks = previous_time + delta_ticks
```

### 4. Check Common Issues

✅ **Musical timing without time signature** - Causes calculation errors
✅ **Bars/beats off by one** - Remember bars and beats are 1-indexed
✅ **Tempo changes** - Absolute timing depends on current tempo
✅ **Non-monotonic timing** - Events must be in chronological order
✅ **Relative timing without previous event** - Needs a timing marker first
✅ **PPQ mismatch** - Different PPQ values affect tick calculations

### 5. Compile and Inspect

Run the file through the full pipeline:
```bash
just run inspect {file_path}
```

Show the generated event timeline with absolute times in seconds and ticks.

### 6. Provide Recommendations

Based on the analysis, suggest:
- Correct timing markers
- Whether to use musical vs absolute timing
- How to fix off-by-one errors
- Whether tempo changes are affecting calculations

Reference:
- `docs/dev-guides/timing-system.md` - Complete timing documentation
- `docs/dev-guides/anti-patterns.md` - Timing anti-patterns
- `expansion/expander.py` - Timing calculation implementation
