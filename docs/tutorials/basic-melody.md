# Tutorial: Creating a Basic Melody with CC Automation

**Level**: Beginner
**Estimated Time**: 2-3 hours
**Prerequisites**: Basic understanding of MIDI concepts (notes, channels, control changes)

## Goal

In this tutorial, you will learn how to:
- Create a simple 8-bar melody using MIDI notes
- Use absolute timing to place notes precisely
- Add CC automation for volume and panning
- Control note duration
- Structure a complete musical phrase

By the end, you'll have a working MML file that plays a complete melody with dynamic expression.

## Prerequisites

Before starting this tutorial, you should:
- Have MIDI Markup Language installed (`midimarkup --version`)
- Know basic MIDI concepts (what notes, channels, and CC messages are)
- Have a MIDI player or DAW to test your output files
- Understand musical timing (seconds, bars, beats)

## What You'll Build

You'll create a simple 8-bar melody with:
- 16 notes spanning 2 octaves
- Volume automation for dynamic expression
- Pan automation for stereo movement
- Proper note durations and spacing

## Step 1: Create Your First File

Let's start with the absolute minimum - a file that plays one note.

Create a file named `my_melody.mml`:

```markdown
---
title: "My First Melody"
author: "Your Name"
tempo: 120
time_signature: [4, 4]
ppq: 480
---

# My First Melody

[00:00.000]
- tempo 120
- note_on 1.C4 100 1000ms
```

**What this does:**
- **Frontmatter** (`---` section): Document metadata
  - `title`: Name of your composition
  - `tempo`: Default tempo in BPM (beats per minute)
  - `time_signature`: [4, 4] = 4/4 time signature
  - `ppq`: Pulses per quarter note (480 is standard, higher = more precision)
- **`[00:00.000]`**: Absolute timing marker (minutes:seconds.milliseconds)
- **`tempo 120`**: Set tempo to 120 BPM at this timestamp
- **`note_on 1.C4 100 1000ms`**: Play note on channel 1
  - `1` = MIDI channel 1
  - `C4` = Middle C (note name)
  - `100` = Velocity (how hard the note is struck, 0-127)
  - `1000ms` = Duration (note plays for 1 second)

**Test it:**
```bash
midimarkup compile my_melody.mml -o output.mid
```

Play `output.mid` in your MIDI player. You should hear a single middle C note lasting one second.

## Step 2: Add Multiple Notes

Now let's create a simple 4-note phrase.

Update your file:

```markdown
---
title: "My First Melody"
author: "Your Name"
tempo: 120
time_signature: [4, 4]
ppq: 480
---

# My First Melody - Four Note Phrase

[00:00.000]
- tempo 120

# First phrase (4 notes)
[00:00.000]
- note_on 1.C4 100 500ms

[00:00.500]
- note_on 1.E4 100 500ms

[00:01.000]
- note_on 1.G4 100 500ms

[00:01.500]
- note_on 1.C5 100 1000ms
```

**What this does:**
- Four notes spaced 500ms apart
- Creates an ascending C major arpeggio (C-E-G-C)
- Last note is longer (1000ms) to create a phrase ending
- Each note starts exactly when specified by the timing marker

**Musical explanation:**
- **C4**: Middle C (root note)
- **E4**: Major third (4 semitones up)
- **G4**: Perfect fifth (7 semitones up)
- **C5**: Octave (12 semitones up)

**Test it:**
```bash
midimarkup compile my_melody.mml -o output.mid
```

You should now hear a 4-note ascending phrase.

## Step 3: Create a Complete 8-Bar Melody

Let's expand to a full 8-bar melody with more interesting rhythm.

Update your file:

```markdown
---
title: "My First Melody"
author: "Your Name"
tempo: 120
time_signature: [4, 4]
ppq: 480
---

# 8-Bar Melody

[00:00.000]
- tempo 120
- time_signature 4/4

# Bar 1-2: Opening phrase
[00:00.000]
- note_on 1.C4 100 500ms

[00:00.500]
- note_on 1.E4 100 500ms

[00:01.000]
- note_on 1.G4 100 1000ms

[00:02.000]
- note_on 1.E4 100 500ms

[00:02.500]
- note_on 1.C4 100 1500ms

# Bar 3-4: Rising sequence
[00:04.000]
- note_on 1.D4 90 500ms

[00:04.500]
- note_on 1.F4 90 500ms

[00:05.000]
- note_on 1.A4 90 1000ms

[00:06.000]
- note_on 1.F4 90 500ms

[00:06.500]
- note_on 1.D4 90 1500ms

# Bar 5-6: Peak of phrase
[00:08.000]
- note_on 1.G4 110 500ms

[00:08.500]
- note_on 1.B4 110 500ms

[00:09.000]
- note_on 1.D5 110 1000ms

[00:10.000]
- note_on 1.B4 110 500ms

[00:10.500]
- note_on 1.G4 110 1500ms

# Bar 7-8: Resolution back to root
[00:12.000]
- note_on 1.E4 100 500ms

[00:12.500]
- note_on 1.C4 100 500ms

[00:13.000]
- note_on 1.A3 100 1000ms

[00:14.000]
- note_on 1.C4 100 2000ms
```

**What this does:**
- Creates 4 musical phrases (2 bars each)
- Uses varying velocities (90, 100, 110) for dynamic expression
- Longer notes at phrase endings create natural breathing points
- Peak phrase (bars 5-6) uses higher notes and louder velocity

**Musical structure:**
- **Bars 1-2**: Introduction on C chord (C-E-G)
- **Bars 3-4**: Transition to D minor (D-F-A)
- **Bars 5-6**: Climax on G chord (G-B-D) - highest and loudest
- **Bars 7-8**: Resolution back to C chord - final note is longest

**Timing math at 120 BPM:**
- 120 BPM = 2 beats per second
- 1 bar of 4/4 = 4 beats = 2 seconds
- Bar 1 starts at 0:00.000
- Bar 3 starts at 0:04.000 (2 bars × 2 seconds)
- Bar 5 starts at 0:08.000 (4 bars × 2 seconds)
- Bar 7 starts at 0:12.000 (6 bars × 2 seconds)

**Test it:**
```bash
midimarkup compile my_melody.mml -o output.mid
```

You should now hear a complete 16-second melody with a clear beginning, middle, and end.

## Step 4: Add Volume Automation

Now let's make the melody more expressive by adding volume automation using CC#7 (Channel Volume).

Update your file to add volume changes:

```markdown
---
title: "My First Melody"
author: "Your Name"
tempo: 120
time_signature: [4, 4]
ppq: 480
---

# 8-Bar Melody with Volume Automation

[00:00.000]
- tempo 120
- time_signature 4/4

# Start with medium volume
[00:00.000]
- cc 1.7.80

# Bar 1-2: Opening phrase
[00:00.000]
- note_on 1.C4 100 500ms

[00:00.500]
- note_on 1.E4 100 500ms

[00:01.000]
- note_on 1.G4 100 1000ms

[00:02.000]
- note_on 1.E4 100 500ms

[00:02.500]
- note_on 1.C4 100 1500ms

# Increase volume for rising section
[00:04.000]
- cc 1.7.90

# Bar 3-4: Rising sequence
[00:04.000]
- note_on 1.D4 90 500ms

[00:04.500]
- note_on 1.F4 90 500ms

[00:05.000]
- note_on 1.A4 90 1000ms

[00:06.000]
- note_on 1.F4 90 500ms

[00:06.500]
- note_on 1.D4 90 1500ms

# Maximum volume for climax
[00:08.000]
- cc 1.7.110

# Bar 5-6: Peak of phrase
[00:08.000]
- note_on 1.G4 110 500ms

[00:08.500]
- note_on 1.B4 110 500ms

[00:09.000]
- note_on 1.D5 110 1000ms

[00:10.000]
- note_on 1.B4 110 500ms

[00:10.500]
- note_on 1.G4 110 1500ms

# Reduce volume for resolution
[00:12.000]
- cc 1.7.85

# Bar 7-8: Resolution back to root
[00:12.000]
- note_on 1.E4 100 500ms

[00:12.500]
- note_on 1.C4 100 500ms

[00:13.000]
- note_on 1.A3 100 1000ms

# Final note with gentle fade
[00:14.000]
- cc 1.7.70

[00:14.000]
- note_on 1.C4 100 2000ms
```

**What this does:**
- **`cc 1.7.80`**: Control Change on channel 1, CC#7 (volume), value 80
  - CC#7 is the standard MIDI channel volume control
  - Values range from 0 (silent) to 127 (maximum)
  - 80 ≈ 63% volume (medium)
- Volume increases from 80 → 90 → 110 as melody builds
- Volume decreases to 85 then 70 for the ending
- Creates a natural dynamic arc: soft → loud → soft

**CC#7 value guide:**
- 0-31: Very quiet (pp-p)
- 32-63: Quiet (mp)
- 64-95: Medium (mf)
- 96-110: Loud (f)
- 111-127: Very loud (ff)

**Test it:**
```bash
midimarkup compile my_melody.mml -o output.mid
```

The melody should now feel more expressive with volume changes matching the musical phrases.

## Step 5: Add Panning Automation

Let's add stereo movement using CC#10 (Pan) to make the melody more interesting.

Complete file with panning:

```markdown
---
title: "My First Melody"
author: "Your Name"
tempo: 120
time_signature: [4, 4]
ppq: 480
---

# 8-Bar Melody with Volume and Pan Automation

[00:00.000]
- tempo 120
- time_signature 4/4

# Start center, medium volume
[00:00.000]
- cc 1.7.80
- cc 1.10.64

# Bar 1-2: Opening phrase (center)
[00:00.000]
- note_on 1.C4 100 500ms

[00:00.500]
- note_on 1.E4 100 500ms

[00:01.000]
- note_on 1.G4 100 1000ms

[00:02.000]
- note_on 1.E4 100 500ms

[00:02.500]
- note_on 1.C4 100 1500ms

# Pan left, increase volume
[00:04.000]
- cc 1.7.90
- cc 1.10.32

# Bar 3-4: Rising sequence (left)
[00:04.000]
- note_on 1.D4 90 500ms

[00:04.500]
- note_on 1.F4 90 500ms

[00:05.000]
- note_on 1.A4 90 1000ms

[00:06.000]
- note_on 1.F4 90 500ms

[00:06.500]
- note_on 1.D4 90 1500ms

# Pan right, maximum volume
[00:08.000]
- cc 1.7.110
- cc 1.10.96

# Bar 5-6: Peak of phrase (right)
[00:08.000]
- note_on 1.G4 110 500ms

[00:08.500]
- note_on 1.B4 110 500ms

[00:09.000]
- note_on 1.D5 110 1000ms

[00:10.000]
- note_on 1.B4 110 500ms

[00:10.500]
- note_on 1.G4 110 1500ms

# Pan back to center, reduce volume
[00:12.000]
- cc 1.7.85
- cc 1.10.64

# Bar 7-8: Resolution back to root (center)
[00:12.000]
- note_on 1.E4 100 500ms

[00:12.500]
- note_on 1.C4 100 500ms

[00:13.000]
- note_on 1.A3 100 1000ms

# Final note: center, gentle fade
[00:14.000]
- cc 1.7.70

[00:14.000]
- note_on 1.C4 100 2000ms

[00:16.000]
- text "End of melody"
```

**What this does:**
- **`cc 1.10.64`**: Control Change on channel 1, CC#10 (pan), value 64
  - CC#10 is the standard MIDI pan control
  - Values: 0 = hard left, 64 = center, 127 = hard right
- **Panning movement:**
  - Bars 1-2: Center (64) - introduction
  - Bars 3-4: Left (32) - creates space
  - Bars 5-6: Right (96) - climax with movement
  - Bars 7-8: Center (64) - stable resolution
- Creates a sense of stereo width and movement

**CC#10 pan values:**
- 0: Hard left (100% left)
- 32: Left (75% left, 25% right)
- 64: Center (50% left, 50% right)
- 96: Right (25% left, 75% right)
- 127: Hard right (100% right)

**Test it:**
```bash
midimarkup compile my_melody.mml -o output.mid
```

Listen with headphones or stereo speakers. You should hear the melody move from center → left → right → center.

## Complete Code

Here's the final complete melody with all automation:

```markdown
---
title: "My First Melody"
author: "Your Name"
tempo: 120
time_signature: [4, 4]
ppq: 480
---

# 8-Bar Melody with Volume and Pan Automation
# This example demonstrates:
# - Basic note_on commands with duration
# - Absolute timing markers
# - CC#7 (volume) automation
# - CC#10 (pan) automation
# - Musical phrase structure

[00:00.000]
- tempo 120
- time_signature 4/4
- marker "Introduction"

# Initial setup: center pan, medium volume
[00:00.000]
- cc 1.7.80
- cc 1.10.64

# Bar 1-2: Opening phrase (center)
[00:00.000]
- note_on 1.C4 100 500ms

[00:00.500]
- note_on 1.E4 100 500ms

[00:01.000]
- note_on 1.G4 100 1000ms

[00:02.000]
- note_on 1.E4 100 500ms

[00:02.500]
- note_on 1.C4 100 1500ms

[00:04.000]
- marker "Rising section"

# Pan left, increase volume
[00:04.000]
- cc 1.7.90
- cc 1.10.32

# Bar 3-4: Rising sequence (left)
[00:04.000]
- note_on 1.D4 90 500ms

[00:04.500]
- note_on 1.F4 90 500ms

[00:05.000]
- note_on 1.A4 90 1000ms

[00:06.000]
- note_on 1.F4 90 500ms

[00:06.500]
- note_on 1.D4 90 1500ms

[00:08.000]
- marker "Climax"

# Pan right, maximum volume
[00:08.000]
- cc 1.7.110
- cc 1.10.96

# Bar 5-6: Peak of phrase (right)
[00:08.000]
- note_on 1.G4 110 500ms

[00:08.500]
- note_on 1.B4 110 500ms

[00:09.000]
- note_on 1.D5 110 1000ms

[00:10.000]
- note_on 1.B4 110 500ms

[00:10.500]
- note_on 1.G4 110 1500ms

[00:12.000]
- marker "Resolution"

# Pan back to center, reduce volume
[00:12.000]
- cc 1.7.85
- cc 1.10.64

# Bar 7-8: Resolution back to root (center)
[00:12.000]
- note_on 1.E4 100 500ms

[00:12.500]
- note_on 1.C4 100 500ms

[00:13.000]
- note_on 1.A3 100 1000ms

# Final note: gentle volume reduction
[00:14.000]
- cc 1.7.70

[00:14.000]
- note_on 1.C4 100 2000ms

[00:16.000]
- text "End of melody"
- end_of_track
```

**Compile and test:**
```bash
# Compile to MIDI file
midimarkup compile my_melody.mml -o my_melody.mid

# View event timeline (optional)
midimarkup compile my_melody.mml --format table

# Validate syntax
midimarkup validate my_melody.mml
```

## Troubleshooting

### Problem: Notes sound at wrong times

**Solution**: Check your timing markers are monotonically increasing:
```markdown
[00:00.000]  # OK
[00:00.500]  # OK - increases
[00:00.300]  # ERROR - goes backwards!
```

### Problem: No sound when playing MIDI file

**Possible causes:**
1. MIDI channel mismatch - ensure your MIDI player is listening to channel 1
2. Volume too low - try `cc 1.7.127` for maximum volume
3. Note velocity too low - try `note_on 1.C4 127 1000ms` for maximum velocity

### Problem: Pan doesn't work

**Solution**: Some software synths ignore pan. Try:
- Using a different MIDI player/DAW
- Routing to a sampler that respects pan
- Testing with multiple instruments

### Problem: Timing feels wrong

**Solution**: Verify your tempo calculation:
- 120 BPM = 2 beats per second
- 1 bar of 4/4 = 2 seconds
- Use `midimarkup compile --format table` to see exact timing

## Next Steps

Now that you understand basic melody creation, try:

1. **Experiment with rhythms**: Try different note durations (250ms, 750ms, 1500ms)
2. **Add more CC automation**: Try CC#1 (modulation), CC#11 (expression), CC#74 (filter cutoff)
3. **Use different scales**: Try minor melodies (C-Eb-G), pentatonic (C-D-E-G-A)
4. **Add articulation**: Use shorter durations (100ms) for staccato notes
5. **Learn multi-channel composition**: See [Multi-Channel Tutorial](multi-channel.md)
6. **Add variables and loops**: Learn advanced features in the [spec.md](../../spec.md)

## Additional Resources

- [MIDI Note Numbers Reference](https://www.inspiredacoustics.com/en/MIDI_note_numbers_and_center_frequencies)
- [MIDI CC List](https://www.midi.org/specifications-old/item/table-3-control-change-messages-data-bytes-2)
- [MML Specification](../../spec.md) - Complete language reference
- [Example Files](../../examples/) - More working examples
- [Multi-Channel Tutorial](multi-channel.md) - Build multi-instrument songs

## Summary

In this tutorial, you learned:

- How to structure an MML file with frontmatter
- Using absolute timing markers (`[mm:ss.milliseconds]`)
- Creating notes with `note_on channel.note velocity duration`
- Using CC#7 for volume automation
- Using CC#10 for pan automation
- Building musical phrases with dynamic expression
- Creating a complete 8-bar composition

You now have the foundation to create expressive MIDI melodies with MML. Practice by creating your own melodies and experimenting with different CC controllers!
