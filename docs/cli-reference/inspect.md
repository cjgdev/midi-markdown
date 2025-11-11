# Command: inspect

> **Audience**: Users
> **Level**: Intermediate to Advanced

Analyze compiled MMD events without creating output files - perfect for debugging and verification.

---

## Synopsis

```bash
mmdc inspect [OPTIONS] INPUT_FILE
mml inspect [OPTIONS] INPUT_FILE       # Shorter alias
```

---

## Description

The `inspect` command compiles MMD files and displays the resulting MIDI events in various formats **without writing any output files**. It's the ideal tool for:

- Debugging timing issues
- Verifying event expansion (loops, sweeps, aliases)
- Analyzing import results
- Understanding compilation output
- Quick event inspection during development

**What inspect does**:
1. Parse MMD file to AST
2. Resolve imports and aliases
3. Expand loops, sweeps, variables
4. Compile to IR (Intermediate Representation)
5. Display events in chosen format (no file output)

**Difference from `compile`**:
- `inspect` - Displays events, **never writes files**
- `compile` - Generates output files (MIDI, CSV, JSON)

**Available formats**:
- `table` - Rich-formatted terminal table (default)
- `csv` - CSV format to stdout
- `json` - Complete JSON to stdout
- `json-simple` - Simplified JSON to stdout

---

## Options

### Input

#### `INPUT_FILE` (required)
Path to `.mmd` file to analyze.

```bash
mmdc inspect song.mmd
mmdc inspect path/to/performance.mmd
```

---

### Output Format

#### `--format, -f FORMAT`
Output format selection. Default: `table`

**Available formats**:
- `table` - Formatted table with colors (default)
- `csv` - CSV format for spreadsheet/database
- `json` - Complete MIDI event data with metadata
- `json-simple` - Simplified JSON for analysis

```bash
# Rich table (default)
mmdc inspect song.mmd

# CSV to stdout
mmdc inspect song.mmd --format csv

# JSON (complete)
mmdc inspect song.mmd --format json

# JSON (simplified)
mmdc inspect song.mmd -f json-simple
```

---

### Display Control (Table Format)

#### `--limit, -n COUNT`
Maximum number of events to display (table format only).

```bash
# Show first 50 events
mmdc inspect song.mmd --limit 50

# Show first 10 events
mmdc inspect song.mmd -n 10
```

**Default**: 100 events (table format only)

**Note**: CSV and JSON formats always show all events.

---

#### `--no-stats`
Hide statistics summary (table format only).

```bash
# Table without statistics
mmdc inspect song.mmd --no-stats
```

**Statistics include**:
- Total event count
- Duration (seconds)
- Tempo (BPM)
- PPQ (resolution)
- Event type breakdown

---

### Output Control

#### `-v, --verbose`
Show compilation steps.

```bash
mmdc inspect song.mmd --verbose
```

**Verbose output**:
```
Analyzing: song.mmd
Format: table
  Parsing MMD file...
  Parsed: 38 events, 0 tracks
  Compiling to IR...
  Compiled: 104 MIDI events

[Events table displayed]
```

---

#### `--no-color`
Disable colored output.

```bash
mmdc inspect song.mmd --no-color
```

**Use when**:
- Piping to files
- Terminal doesn't support colors
- Accessibility requirements

---

### Debugging

#### `--debug`
Show full error tracebacks.

```bash
mmdc inspect broken.mmd --debug
```

---

## Output Formats

### Table Format (Default)

**Features**:
- Color-coded event types
- Formatted timing (mm:ss.ms)
- Note names alongside numbers (C4, D#5)
- Compact display
- Statistics summary

**Example output**:
```
┌──────────┬──────────────┬─────────┬──────────────┬─────────┐
│ Time     │ Event        │ Channel │ Data         │ Note    │
├──────────┼──────────────┼─────────┼──────────────┼─────────┤
│ 0:00.000 │ Tempo        │ -       │ 120 BPM      │         │
│ 0:00.000 │ Note On      │ 1       │ 60 / 80      │ C4      │
│ 0:00.500 │ CC           │ 1       │ 7 / 100      │ Volume  │
│ 0:01.000 │ Note Off     │ 1       │ 60           │ C4      │
│ 0:01.000 │ PC           │ 1       │ 5            │ Preset  │
└──────────┴──────────────┴─────────┴──────────────┴─────────┘

Statistics:
  Events: 104
  Duration: 50.00s
  Tempo: 120 BPM
  PPQ: 480
```

**Best for**: Quick visual inspection, debugging, presentations.

---

### CSV Format

**Features**:
- midicsv-compatible format
- Spreadsheet/database import ready
- All events included (no limit)
- Header row included

**Example output**:
```csv
Track,Time,Type,Channel,Data1,Data2,Text
0,0,Tempo,,,120,
0,0,Note_on,1,60,80,
0,240,CC,1,7,100,
0,480,Note_off,1,60,0,
0,480,Program_change,1,5,,
```

**Best for**: Spreadsheet analysis, Python pandas, database import.

**Usage**:
```bash
# Pipe to file
mmdc inspect song.mmd --format csv > events.csv

# Open in Excel/Google Sheets
open events.csv

# Analyze with pandas
mmdc inspect song.mmd -f csv | python3 << EOF
import pandas as pd
import sys
df = pd.read_csv(sys.stdin)
print(df.groupby('Type').size())
EOF
```

---

### JSON Format (Complete)

**Features**:
- Complete MIDI event data
- All metadata included
- PPQ, format, track information
- Programmatic processing ready

**Example output**:
```json
{
  "ppq": 480,
  "format": 1,
  "initial_tempo": 120,
  "tracks": [
    {
      "name": "Master",
      "events": [
        {
          "time": 0,
          "type": "tempo",
          "tempo_bpm": 120,
          "microseconds_per_quarter": 500000
        },
        {
          "time": 0,
          "type": "note_on",
          "channel": 1,
          "note": 60,
          "velocity": 80
        }
      ]
    }
  ]
}
```

**Best for**: Programmatic processing, web applications, API integration.

---

### JSON Format (Simplified)

**Features**:
- Simplified structure
- Easier parsing for music analysis
- Human-readable format
- Less metadata overhead

**Example output**:
```json
{
  "events": [
    {
      "time": 0,
      "type": "tempo",
      "data": { "bpm": 120 }
    },
    {
      "time": 0,
      "type": "note_on",
      "channel": 1,
      "note": 60,
      "velocity": 80
    }
  ]
}
```

**Best for**: Music analysis tools, data visualization, learning.

---

## Examples

### Basic Inspection

```bash
# Default: table format with first 100 events
mmdc inspect song.mmd
```

---

### Show Specific Event Count

```bash
# Show first 20 events only
mmdc inspect song.mmd --limit 20

# Show first 5 events (quick peek)
mmdc inspect song.mmd -n 5
```

---

### Export to CSV

```bash
# View in terminal
mmdc inspect song.mmd --format csv

# Save to file
mmdc inspect song.mmd --format csv > events.csv

# Pipe to column formatter
mmdc inspect song.mmd -f csv | column -t -s,
```

---

### Export to JSON

```bash
# Complete JSON
mmdc inspect song.mmd --format json > data.json

# Simplified JSON
mmdc inspect song.mmd --format json-simple > simple.json

# Pretty-print with jq
mmdc inspect song.mmd -f json | jq '.'

# Query with jq
mmdc inspect song.mmd -f json | jq '.tracks[0].events[] | select(.type == "note_on")'
```

---

### Debugging Timing

```bash
# Inspect timing of first 50 events
mmdc inspect song.mmd --limit 50

# Look for timing gaps or issues in table
```

**Example debugging session**:
```
Time      Event        Channel  Data
0:00.000  Note On      1        60 / 80
0:01.000  Note Off     1        60
0:05.000  Note On      1        62 / 80  # Big gap! Check source
0:05.500  Note Off     1        62
```

---

### Verifying Loop Expansion

```bash
# Before expansion: 1 @loop statement
# After expansion: N events

mmdc inspect loop_test.mmd --limit 20
```

**Example**:
```yaml
# Source MML:
@loop 4
  [+0.250s]
  - note_on 1.60 80 100ms
@end

# Inspect shows 4 expanded note events:
# 0:00.000  Note On   1  60 / 80
# 0:00.100  Note Off  1  60
# 0:00.250  Note On   1  60 / 80
# 0:00.350  Note Off  1  60
# ... (4 total)
```

---

### Checking Import Results

```bash
# Inspect file with imports
mmdc inspect device_test.mmd --verbose
```

**Verbose output shows**:
```
Analyzing: device_test.mmd
  Parsing MMD file...
  Parsed: 5 events, 0 tracks
  Loading 1 import(s)...
  Loaded 86 alias(es) from imports
  Compiling to IR...
  Compiled: 15 MIDI events

# Table shows expanded aliases
```

---

### Analyzing Alias Expansion

```bash
# Compare pre/post expansion
mmdc inspect alias_test.mmd
```

**Example**:
```yaml
# Source: 1 alias call
- cortex_load 1.2.3.5

# Inspect shows 3 expanded CC commands:
# 0:00.000  CC  1  32 / 2   # Setlist
# 0:00.050  CC  1   0 / 3   # Group
# 0:00.100  PC  1   5       # Preset
```

---

### Comparing Formats

```bash
# Table for visual
mmdc inspect song.mmd --format table

# CSV for analysis
mmdc inspect song.mmd --format csv > analysis.csv

# JSON for scripting
mmdc inspect song.mmd --format json | jq '.tracks[0].events | length'
```

---

### No Statistics Display

```bash
# Table without stats footer
mmdc inspect song.mmd --no-stats
```

**Use when**: Only interested in events, not summary.

---

### Verbose Analysis

```bash
# See all compilation steps
mmdc inspect song.mmd --verbose
```

**Output includes**:
- Parse step
- Event count after parsing
- Import loading (if any)
- Alias resolution
- Compilation to IR
- Final event count

---

### Pipe to Analysis Tools

```bash
# Count event types with awk
mmdc inspect song.mmd -f csv | awk -F, 'NR>1 {count[$3]++} END {for(type in count) print type, count[type]}'

# Find all CC events
mmdc inspect song.mmd -f csv | grep "^0,[0-9]*,CC"

# Extract note events only
mmdc inspect song.mmd -f json | jq '.tracks[0].events[] | select(.type | startswith("note"))'
```

---

## Use Cases

### Debugging Timing Issues

**Problem**: Events not at expected times.

**Solution**:
```bash
# Inspect with table format
mmdc inspect song.mmd --limit 50

# Look for:
# - Timing gaps
# - Events out of order
# - Wrong delta calculations
```

---

### Verifying Event Expansion

**Problem**: Not sure if loops/sweeps expanded correctly.

**Solution**:
```bash
# Inspect before/after event count
mmdc inspect loop_test.mmd

# Check statistics for event count
# Verify expanded events in table
```

---

### Analyzing Import Effects

**Problem**: Want to see what aliases imported.

**Solution**:
```bash
# Verbose inspect shows import details
mmdc inspect device_test.mmd --verbose

# See alias expansion in event table
```

---

### Checking MIDI Values

**Problem**: Need to verify CC values, note numbers, velocities.

**Solution**:
```bash
# Table shows all values clearly
mmdc inspect song.mmd

# Or export to CSV for filtering
mmdc inspect song.mmd -f csv | grep "CC"
```

---

### Performance Analysis

**Problem**: Song too long/short, need duration.

**Solution**:
```bash
# Statistics show duration
mmdc inspect song.mmd

# Output includes:
# Duration: 50.00s
# Events: 104
# Tempo: 120 BPM
```

---

### Learning MMD Compilation

**Problem**: Want to understand how MMD compiles to MIDI.

**Solution**:
```bash
# Start with simple file
echo '[00:00.000]
- note_on 1.60 80 1b' | mmdc inspect -

# Inspect shows exact MIDI events:
# 0:00.000  Tempo     -    120 BPM
# 0:00.000  Note On   1    60 / 80
# 0:01.000  Note Off  1    60
```

---

## Common Issues

### "Too many events to display"

**Problem**: File has >100 events, table truncated.

**Solution**:
```bash
# Increase limit
mmdc inspect song.mmd --limit 500

# Or export to CSV for full view
mmdc inspect song.mmd --format csv > all_events.csv
```

---

### CSV/JSON shows no color

**Problem**: Expected colored output but CSV/JSON is plain.

**Explanation**: CSV and JSON are meant for piping/processing, not terminal display.

**Solution**: Use `table` format for colored output:
```bash
mmdc inspect song.mmd --format table
```

---

### Statistics not showing

**Problem**: Used `--no-stats` and now stats are hidden.

**Solution**: Remove flag:
```bash
mmdc inspect song.mmd  # Stats shown by default
```

---

### Large file inspection slow

**Problem**: Inspecting 10,000+ event file takes time.

**Solution**:
```bash
# Limit display to first N events
mmdc inspect large.mmd --limit 100

# Or use validate (faster, no display)
mmdc validate large.mmd
```

---

### Can't pipe CSV to file

**Problem**: CSV output includes ANSI codes.

**Solution**: Use `--no-color`:
```bash
mmdc inspect song.mmd --format csv --no-color > events.csv
```

---

## Tips & Tricks

### Quick Event Count

```bash
# Get total event count
mmdc inspect song.mmd --format json | jq '.tracks[0].events | length'

# Or from statistics
mmdc inspect song.mmd | grep "Events:"
```

---

### Filter Specific Event Types

```bash
# CSV: Show only CC events
mmdc inspect song.mmd -f csv | grep "^0,[0-9]*,CC"

# JSON: Extract note events
mmdc inspect song.mmd -f json | jq '.tracks[0].events[] | select(.type | startswith("note"))'
```

---

### Timing Analysis

```bash
# CSV: Extract timing column
mmdc inspect song.mmd -f csv | awk -F, 'NR>1 {print $2}' | head -20

# Find timing gaps >1 second
mmdc inspect song.mmd -f csv | awk -F, 'NR>1 {if ($2 - prev > 480) print "Gap at tick", $2; prev=$2}'
```

---

### Compare Before/After Edits

```bash
# Before edit
mmdc inspect song.mmd > before.txt

# Edit file...

# After edit
mmdc inspect song.mmd > after.txt

# Compare
diff before.txt after.txt
```

---

### Event Type Distribution

```bash
# Count event types with awk
mmdc inspect song.mmd -f csv | awk -F, 'NR>1 {count[$3]++} END {for (t in count) print t, count[t]}'

# Example output:
# Note_on 24
# Note_off 24
# CC 10
# PC 2
# Tempo 1
```

---

### Extract Metadata

```bash
# Get PPQ
mmdc inspect song.mmd -f json | jq '.ppq'

# Get initial tempo
mmdc inspect song.mmd -f json | jq '.initial_tempo'

# Get all tempos
mmdc inspect song.mmd -f json | jq '.tracks[0].events[] | select(.type == "tempo") | .tempo_bpm'
```

---

### Verify Channel Usage

```bash
# List unique channels
mmdc inspect song.mmd -f csv | awk -F, 'NR>1 && $4 != "" {channels[$4]=1} END {for (c in channels) print "Channel", c}'

# Count events per channel
mmdc inspect song.mmd -f csv | awk -F, 'NR>1 && $4 != "" {count[$4]++} END {for (c in count) print "Channel", c, ":", count[c], "events"}'
```

---

### Quick Debugging Script

```bash
#!/bin/bash
# inspect_debug.sh - Quick event analysis

FILE=$1

echo "=== Event Summary ==="
mmdc inspect "$FILE" --no-stats | head -20

echo ""
echo "=== Statistics ==="
mmdc inspect "$FILE" | grep -A 5 "Statistics:"

echo ""
echo "=== Event Type Count ==="
mmdc inspect "$FILE" -f csv | awk -F, 'NR>1 {count[$3]++} END {for (t in count) print t ":", count[t]}'
```

**Usage**:
```bash
chmod +x inspect_debug.sh
./inspect_debug.sh song.mmd
```

---

### Integration with jq

```bash
# Find all note events in range
mmdc inspect song.mmd -f json | \
  jq '.tracks[0].events[] | select(.type == "note_on" and .note >= 60 and .note <= 72)'

# Calculate total duration
mmdc inspect song.mmd -f json | \
  jq '.tracks[0].events[-1].time / .ppq / .initial_tempo * 60'

# Extract CC automation
mmdc inspect song.mmd -f json | \
  jq '.tracks[0].events[] | select(.type == "cc" and .cc_number == 7)'
```

---

## Advanced Usage

### Multi-file Comparison

```bash
# Compare event counts across files
for file in *.mmd; do
  count=$(mmdc inspect "$file" -f json | jq '.tracks[0].events | length')
  echo "$file: $count events"
done
```

---

### Event Timeline Visualization

```bash
# Generate timeline CSV
mmdc inspect song.mmd -f csv | \
  awk -F, 'NR>1 {printf "%s,%s,%s\n", $2/480, $3, $4}' > timeline.csv

# Import to plotting tool (Python, R, etc.)
```

---

### Automated Testing

```bash
# Test that compilation doesn't change event count
expected=104
actual=$(mmdc inspect song.mmd -f json | jq '.tracks[0].events | length')

if [ "$actual" -eq "$expected" ]; then
  echo "✓ Event count correct ($actual)"
else
  echo "✗ Event count mismatch: expected $expected, got $actual"
  exit 1
fi
```

---

## See Also

- [compile command](compile.md) - Generate output files (MIDI, CSV, JSON)
- [validate command](validate.md) - Validation without compilation
- [play command](play.md) - Real-time playback
- [Troubleshooting Guide](../reference/troubleshooting.md) - Common issues
- [MML Syntax Reference](../user-guide/mmd-syntax.md) - Complete syntax guide

---

**Next Steps**: Learn about [real-time playback](play.md) or [compilation](compile.md).
