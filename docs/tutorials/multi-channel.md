# Tutorial: Multi-Channel Song Arrangement

**Level**: Intermediate
**Estimated Time**: 2-3 hours
**Prerequisites**: Completed [Basic Melody Tutorial](basic-melody.md), understanding of MIDI channels

## Goal

In this tutorial, you will learn how to:
- Create multi-channel MIDI arrangements
- Layer multiple instruments (melody, bass, drums)
- Use MIDI channel 10 for drums
- Coordinate timing across multiple parts
- Balance levels and pan positions
- Structure a complete song arrangement

By the end, you'll have a working 4-channel song with melody, bass, chords, and drums.

## Prerequisites

Before starting this tutorial, you should:
- Have completed the [Basic Melody Tutorial](basic-melody.md)
- Understand MIDI channels (1-16)
- Know that channel 10 is reserved for drums in General MIDI
- Understand basic music theory (melody, bass, harmony)
- Have a General MIDI compatible player or DAW

## What You'll Build

You'll create a 16-bar song with:
- **Channel 1**: Lead melody (synth)
- **Channel 2**: Bass line (bass)
- **Channel 3**: Chord pads (strings)
- **Channel 10**: Drum pattern (General MIDI drums)

## Step 1: Create the Basic Structure

Let's start with the document structure and tempo setup.

Create a file named `my_song.mmd`:

```markdown
---
title: "Multi-Channel Song"
author: "Your Name"
tempo: 120
time_signature: [4, 4]
midi_format: 1
ppq: 480
---

# Multi-Channel Song Arrangement
# 4 channels: Lead (Ch1), Bass (Ch2), Chords (Ch3), Drums (Ch10)

[00:00.000]
- tempo 120
- time_signature 4/4
- key_signature Cmaj
- marker "Intro"
```

**What this does:**
- **`midi_format: 1`**: Format 1 MIDI file (multi-track, recommended for multiple channels)
- **`key_signature Cmaj`**: C major key (no sharps or flats)
- **`marker "Intro"`**: Adds a text marker for DAW navigation

**MIDI format comparison:**
- **Format 0**: Single track (all channels mixed together)
- **Format 1**: Multi-track (each channel can have separate track)
- **Format 2**: Multiple independent sequences (rarely used)

**Test basic structure:**
```bash
mmdc validate my_song.mmd
```

Should output: "✓ Validation passed"

## Step 2: Add Channel 1 - Lead Melody

Let's add a simple lead melody on channel 1.

```markdown
---
title: "Multi-Channel Song"
author: "Your Name"
tempo: 120
time_signature: [4, 4]
midi_format: 1
ppq: 480
---

# Multi-Channel Song Arrangement

[00:00.000]
- tempo 120
- time_signature 4/4
- key_signature Cmaj
- marker "Intro"

# ============================================
# CHANNEL 1 - LEAD MELODY
# ============================================

# Setup: Medium volume, slight right pan
[00:00.000]
- cc 1.7.90
- cc 1.10.72

# Bar 1-4: Opening melody
[00:00.000]
- note_on 1.E4 100 500ms

[00:00.500]
- note_on 1.G4 100 500ms

[00:01.000]
- note_on 1.C5 100 1000ms

[00:02.000]
- note_on 1.G4 100 500ms

[00:02.500]
- note_on 1.E4 100 1500ms

[00:04.000]
- note_on 1.D4 95 500ms

[00:04.500]
- note_on 1.F4 95 500ms

[00:05.000]
- note_on 1.A4 95 1000ms

[00:06.000]
- note_on 1.F4 95 500ms

[00:06.500]
- note_on 1.D4 95 1500ms
```

**What this does:**
- **Channel 1**: Typically used for lead/melody in General MIDI
- **`cc 1.7.90`**: Set channel 1 volume to 90 (fairly loud for lead)
- **`cc 1.10.72`**: Pan slightly right (creates stereo space)
- **Notes**: 8-bar phrase with C major (E-G-C) and D minor (D-F-A) patterns

**Test with lead only:**
```bash
mmdc compile my_song.mmd -o my_song.mid
```

You should hear just the lead melody.

## Step 3: Add Channel 2 - Bass Line

Now add a bass line on channel 2 to provide foundation.

Add this section after the lead melody:

```markdown
# ============================================
# CHANNEL 2 - BASS LINE
# ============================================

# Setup: High volume, center pan
[00:00.000]
- cc 2.7.100
- cc 2.10.64

# Bar 1-4: Root notes following chord progression
[00:00.000]
- note_on 2.C2 100 2000ms

[00:02.000]
- note_on 2.C2 90 2000ms

[00:04.000]
- note_on 2.D2 100 2000ms

[00:06.000]
- note_on 2.D2 90 2000ms

# Bar 5-8: Same progression, add walking pattern
[00:08.000]
- note_on 2.C2 100 1000ms

[00:09.000]
- note_on 2.E2 90 1000ms

[00:10.000]
- note_on 2.C2 90 1000ms

[00:11.000]
- note_on 2.G2 85 1000ms

[00:12.000]
- note_on 2.D2 100 1000ms

[00:13.000]
- note_on 2.F2 90 1000ms

[00:14.000]
- note_on 2.D2 90 1000ms

[00:15.000]
- note_on 2.A2 85 1000ms
```

**What this does:**
- **Channel 2**: Typically bass in General MIDI
- **`cc 2.7.100`**: Louder than lead (bass needs presence)
- **`cc 2.10.64`**: Center pan (bass usually centered for power)
- **C2, D2**: Low notes (2 octaves below middle C)
- **Bars 1-4**: Whole notes on root (C, D)
- **Bars 5-8**: Walking bass pattern (root, third, root, fifth)

**Bass note explanation:**
- **C2**: Root of C major chord (bar 1-2, 9-10)
- **D2**: Root of D minor chord (bar 3-4, 13-14)
- **E2, G2**: Walking notes (third and fifth of C major)
- **F2, A2**: Walking notes (third and fifth of D minor)

**Test lead + bass:**
```bash
mmdc compile my_song.mmd -o my_song.mid
```

You should hear melody with bass foundation.

## Step 4: Add Channel 3 - Chord Pads

Add sustained chord pads on channel 3 for harmonic fullness.

```markdown
# ============================================
# CHANNEL 3 - CHORD PADS (STRINGS)
# ============================================

# Setup: Medium-low volume, slight left pan
[00:00.000]
- cc 3.7.75
- cc 3.10.56

# Bar 1-4: C major chord (C-E-G)
[00:00.000]
- note_on 3.C3 70 4000ms
[@]
- note_on 3.E3 70 4000ms
[@]
- note_on 3.G3 70 4000ms

# Bar 5-8: D minor chord (D-F-A)
[00:04.000]
- note_on 3.D3 70 4000ms
[@]
- note_on 3.F3 70 4000ms
[@]
- note_on 3.A3 70 4000ms

# Bar 9-12: C major chord again
[00:08.000]
- note_on 3.C3 75 4000ms
[@]
- note_on 3.E3 75 4000ms
[@]
- note_on 3.G3 75 4000ms

# Bar 13-16: G major chord (G-B-D)
[00:12.000]
- note_on 3.G3 75 4000ms
[@]
- note_on 3.B3 75 4000ms
[@]
- note_on 3.D4 75 4000ms
```

**What this does:**
- **Channel 3**: Typically used for strings/pads in General MIDI
- **`[@]`**: Simultaneous timing marker (plays at same time as previous event)
- **Three-note chords**: Play all notes simultaneously
- **Lower velocity (70-75)**: Pads sit in background
- **Long duration (4000ms)**: Sustained whole notes
- **Slight left pan (56)**: Balances lead's right pan (72)

**Chord voicings:**
- **C major**: C3-E3-G3 (root position)
- **D minor**: D3-F3-A3 (root position)
- **G major**: G3-B3-D4 (root position, creates resolution)

**Test with all harmonic instruments:**
```bash
mmdc compile my_song.mmd -o my_song.mid
```

You should hear melody, bass, and chord pads working together.

## Step 5: Add Channel 10 - Drum Pattern

Add drums on channel 10 (General MIDI drum channel).

```markdown
# ============================================
# CHANNEL 10 - DRUMS (GENERAL MIDI)
# ============================================

# Setup: High volume for drums
[00:00.000]
- cc 10.7.110

# Bar 1-2: Basic kick and snare pattern
# Kick on beats 1 and 3
[00:00.000]
- note_on 10.C1 120 100ms    # Kick (note 36 = C1)

[00:01.000]
- note_on 10.C1 120 100ms    # Kick

# Snare on beats 2 and 4
[00:00.500]
- note_on 10.D1 110 100ms    # Snare (note 38 = D1)

[00:01.500]
- note_on 10.D1 110 100ms    # Snare

[00:02.000]
- note_on 10.C1 120 100ms    # Kick

[00:02.500]
- note_on 10.D1 110 100ms    # Snare

[00:03.000]
- note_on 10.C1 120 100ms    # Kick

[00:03.500]
- note_on 10.D1 110 100ms    # Snare

# Bar 3-4: Add hi-hat on eighth notes
[00:04.000]
- note_on 10.C1 120 100ms    # Kick
[@]
- note_on 10.F#1 90 100ms    # Closed hi-hat (note 42 = F#1)

[00:04.500]
- note_on 10.D1 110 100ms    # Snare
[@]
- note_on 10.F#1 85 100ms    # Hi-hat

[00:05.000]
- note_on 10.C1 120 100ms    # Kick
[@]
- note_on 10.F#1 90 100ms    # Hi-hat

[00:05.500]
- note_on 10.F#1 85 100ms    # Hi-hat only

[00:06.000]
- note_on 10.C1 120 100ms    # Kick
[@]
- note_on 10.F#1 90 100ms    # Hi-hat

[00:06.500]
- note_on 10.D1 110 100ms    # Snare
[@]
- note_on 10.F#1 85 100ms    # Hi-hat

[00:07.000]
- note_on 10.C1 120 100ms    # Kick
[@]
- note_on 10.F#1 90 100ms    # Hi-hat

[00:07.500]
- note_on 10.D1 110 100ms    # Snare
[@]
- note_on 10.F#1 85 100ms    # Hi-hat
```

**What this does:**
- **Channel 10**: Reserved for drums in General MIDI specification
- **Note numbers = drum sounds** (not pitches):
  - C1 (36): Bass Drum / Kick
  - D1 (38): Snare Drum
  - F#1 (42): Closed Hi-Hat
- **Short duration (100ms)**: Drums are percussive
- **High velocity (110-120)**: Drums need to punch through
- **`[@]` for simultaneous**: Hi-hat plays with kick/snare

**General MIDI drum map (channel 10):**
- C1 (36): Bass Drum 1
- C#1 (37): Side Stick
- D1 (38): Snare Drum 1
- D#1 (39): Hand Clap
- E1 (40): Snare Drum 2
- F1 (41): Low Tom
- F#1 (42): Closed Hi-Hat
- G1 (43): Low-Mid Tom
- G#1 (44): Pedal Hi-Hat
- A1 (45): Mid Tom
- A#1 (46): Open Hi-Hat
- B1 (47): Low-Mid Tom
- C2 (48): High-Mid Tom
- C#2 (49): Crash Cymbal 1
- D2 (50): High Tom
- D#2 (51): Ride Cymbal 1

**Test complete arrangement:**
```bash
mmdc compile my_song.mmd -o my_song.mid
```

You should hear a complete band: melody, bass, chords, and drums!

## Step 6: Add Structure and Markers

Let's expand to a complete 16-bar song with sections.

Update your file with complete structure:

```markdown
---
title: "Multi-Channel Song"
author: "Your Name"
tempo: 120
time_signature: [4, 4]
midi_format: 1
ppq: 480
---

# Multi-Channel Song - Complete Arrangement
# Channel 1: Lead Melody (Synth)
# Channel 2: Bass Line
# Channel 3: Chord Pads (Strings)
# Channel 10: Drums

# ============================================
# INTRO - Bars 1-4
# ============================================

[00:00.000]
- tempo 120
- time_signature 4/4
- key_signature Cmaj
- marker "Intro"

# Channel setup
[00:00.000]
- cc 1.7.90      # Lead volume
- cc 1.10.72     # Lead pan (slight right)
- cc 2.7.100     # Bass volume
- cc 2.10.64     # Bass pan (center)
- cc 3.7.75      # Pads volume
- cc 3.10.56     # Pads pan (slight left)
- cc 10.7.110    # Drums volume

# Lead melody - Intro
[00:00.000]
- note_on 1.E4 100 500ms
[00:00.500]
- note_on 1.G4 100 500ms
[00:01.000]
- note_on 1.C5 100 1000ms
[00:02.000]
- note_on 1.G4 100 500ms
[00:02.500]
- note_on 1.E4 100 1500ms

# Bass - Intro (root notes)
[00:00.000]
- note_on 2.C2 100 2000ms
[00:02.000]
- note_on 2.C2 90 2000ms

# Pads - Intro (C major chord)
[00:00.000]
- note_on 3.C3 70 4000ms
[@]
- note_on 3.E3 70 4000ms
[@]
- note_on 3.G3 70 4000ms

# Drums - Intro (simple kick/snare)
[00:00.000]
- note_on 10.C1 120 100ms
[00:00.500]
- note_on 10.D1 110 100ms
[00:01.000]
- note_on 10.C1 120 100ms
[00:01.500]
- note_on 10.D1 110 100ms
[00:02.000]
- note_on 10.C1 120 100ms
[00:02.500]
- note_on 10.D1 110 100ms
[00:03.000]
- note_on 10.C1 120 100ms
[00:03.500]
- note_on 10.D1 110 100ms

# ============================================
# VERSE - Bars 5-8
# ============================================

[00:04.000]
- marker "Verse"

# Lead - Verse melody
[00:04.000]
- note_on 1.D4 95 500ms
[00:04.500]
- note_on 1.F4 95 500ms
[00:05.000]
- note_on 1.A4 95 1000ms
[00:06.000]
- note_on 1.F4 95 500ms
[00:06.500]
- note_on 1.D4 95 1500ms

# Bass - Verse (walking pattern)
[00:04.000]
- note_on 2.D2 100 1000ms
[00:05.000]
- note_on 2.F2 90 1000ms
[00:06.000]
- note_on 2.D2 90 1000ms
[00:07.000]
- note_on 2.A2 85 1000ms

# Pads - Verse (D minor chord)
[00:04.000]
- note_on 3.D3 70 4000ms
[@]
- note_on 3.F3 70 4000ms
[@]
- note_on 3.A3 70 4000ms

# Drums - Verse (add hi-hat)
[00:04.000]
- note_on 10.C1 120 100ms
[@]
- note_on 10.F#1 90 100ms
[00:04.500]
- note_on 10.D1 110 100ms
[@]
- note_on 10.F#1 85 100ms
[00:05.000]
- note_on 10.C1 120 100ms
[@]
- note_on 10.F#1 90 100ms
[00:05.500]
- note_on 10.F#1 85 100ms
[00:06.000]
- note_on 10.C1 120 100ms
[@]
- note_on 10.F#1 90 100ms
[00:06.500]
- note_on 10.D1 110 100ms
[@]
- note_on 10.F#1 85 100ms
[00:07.000]
- note_on 10.C1 120 100ms
[@]
- note_on 10.F#1 90 100ms
[00:07.500]
- note_on 10.D1 110 100ms
[@]
- note_on 10.F#1 85 100ms

# ============================================
# CHORUS - Bars 9-12
# ============================================

[00:08.000]
- marker "Chorus"

# Increase lead volume for chorus
[00:08.000]
- cc 1.7.105

# Lead - Chorus (higher notes)
[00:08.000]
- note_on 1.G4 110 500ms
[00:08.500]
- note_on 1.C5 110 500ms
[00:09.000]
- note_on 1.E5 110 1000ms
[00:10.000]
- note_on 1.C5 110 500ms
[00:10.500]
- note_on 1.G4 110 1500ms

# Bass - Chorus
[00:08.000]
- note_on 2.C2 100 1000ms
[00:09.000]
- note_on 2.E2 90 1000ms
[00:10.000]
- note_on 2.C2 90 1000ms
[00:11.000]
- note_on 2.G2 85 1000ms

# Pads - Chorus (C major, higher velocity)
[00:08.000]
- note_on 3.C3 75 4000ms
[@]
- note_on 3.E3 75 4000ms
[@]
- note_on 3.G3 75 4000ms

# Drums - Chorus (full pattern)
[00:08.000]
- note_on 10.C1 127 100ms
[@]
- note_on 10.F#1 95 100ms
[00:08.500]
- note_on 10.D1 115 100ms
[@]
- note_on 10.F#1 90 100ms
[00:09.000]
- note_on 10.C1 127 100ms
[@]
- note_on 10.F#1 95 100ms
[00:09.500]
- note_on 10.F#1 90 100ms
[00:10.000]
- note_on 10.C1 127 100ms
[@]
- note_on 10.F#1 95 100ms
[00:10.500]
- note_on 10.D1 115 100ms
[@]
- note_on 10.F#1 90 100ms
[00:11.000]
- note_on 10.C1 127 100ms
[@]
- note_on 10.F#1 95 100ms
[00:11.500]
- note_on 10.D1 115 100ms
[@]
- note_on 10.F#1 90 100ms

# ============================================
# OUTRO - Bars 13-16
# ============================================

[00:12.000]
- marker "Outro"

# Reduce lead volume
[00:12.000]
- cc 1.7.85

# Lead - Outro (resolution)
[00:12.000]
- note_on 1.D4 100 500ms
[00:12.500]
- note_on 1.G4 100 500ms
[00:13.000]
- note_on 1.B4 100 1000ms
[00:14.000]
- note_on 1.C5 90 2000ms

# Bass - Outro (resolve to C)
[00:12.000]
- note_on 2.G2 100 2000ms
[00:14.000]
- note_on 2.C2 95 2000ms

# Pads - Outro (G major then C major)
[00:12.000]
- note_on 3.G3 75 2000ms
[@]
- note_on 3.B3 75 2000ms
[@]
- note_on 3.D4 75 2000ms

[00:14.000]
- note_on 3.C3 70 2000ms
[@]
- note_on 3.E3 70 2000ms
[@]
- note_on 3.G3 70 2000ms

# Drums - Outro (simplified, fade out)
[00:12.000]
- note_on 10.C1 120 100ms
[@]
- note_on 10.F#1 90 100ms
[00:12.500]
- note_on 10.D1 110 100ms
[00:13.000]
- note_on 10.C1 120 100ms
[00:13.500]
- note_on 10.D1 110 100ms
[00:14.000]
- note_on 10.C1 120 100ms
[00:15.000]
- note_on 10.C1 100 100ms

[00:16.000]
- text "End of song"
- end_of_track
```

**What this does:**
- **16-bar structure**: Intro (4) → Verse (4) → Chorus (4) → Outro (4)
- **Markers**: Help navigate in DAW
- **Dynamic changes**: Volume increases for chorus, decreases for outro
- **Chord progression**: C → D minor → C → G → C (common pop progression)
- **Drum variation**: Builds from simple to full pattern

**Compile final version:**
```bash
mmdc compile my_song.mmd -o my_song.mid
mmdc compile my_song.mmd --format table  # View event timeline
```

## Complete Code

The complete 16-bar song is shown in Step 6 above. Key features:

- **4 distinct channels** with different roles
- **Clear song structure** with markers
- **Dynamic arrangement** (quiet intro → loud chorus → quiet outro)
- **Proper GM drum mapping** on channel 10
- **Balanced mix** (volume and pan settings)
- **Chord progression** that resolves properly

## Troubleshooting

### Problem: Drums sound like piano notes

**Solution**: Ensure you're using channel 10:
```markdown
- note_on 10.C1 120 100ms  # Correct (channel 10)
- note_on 1.C1 120 100ms   # Wrong (channel 1 = melody)
```

### Problem: Can't hear all instruments

**Possible causes:**
1. **Volume imbalance** - Check CC#7 values:
   ```markdown
   - cc 1.7.90    # Lead
   - cc 2.7.100   # Bass (louder)
   - cc 3.7.75    # Pads (softer)
   - cc 10.7.110  # Drums (loudest)
   ```

2. **GM bank not loaded** - Ensure your MIDI player uses General MIDI soundbank

3. **Channel limit** - Some players only support 8 simultaneous channels

### Problem: Timing feels off between channels

**Solution**: All channels must use same timing markers:
```markdown
# Correct - bass and drums at same time
[00:00.000]
- note_on 2.C2 100 1000ms    # Bass
[@]
- note_on 10.C1 120 100ms     # Drum (simultaneous)

# Wrong - different times
[00:00.000]
- note_on 2.C2 100 1000ms    # Bass
[00:00.001]
- note_on 10.C1 120 100ms     # Drum (1ms late!)
```

### Problem: Chords sound muddy

**Solutions:**
1. **Voice chords higher**: Use C3-E3-G3 instead of C2-E2-G2
2. **Reduce pad volume**: Try `cc 3.7.60` instead of 75
3. **Use wider voicings**: C3-G3-E4 (root, fifth, third)
4. **Pan pads away from bass**: Pads left (40), bass center (64)

### Problem: MIDI format 0 vs 1 confusion

**Explanation:**
- **Format 0**: All channels in one track (simpler, less DAW support)
- **Format 1**: Each channel can be separate track (better for editing)

Use `midi_format: 1` in frontmatter for multi-channel songs.

## Next Steps

Now that you understand multi-channel arrangement, try:

1. **Add more instruments**: Try channels 4-9 for guitar, organ, etc.
2. **Use program change (PC)**: Switch instruments mid-song
3. **Add expression**: Use CC#11 for dynamic swells
4. **Create drum fills**: Add crash cymbals (C#2) and toms (F1-D2)
5. **Learn device control**: See [Device Control Tutorial](device-control.md)
6. **Use variables**: Define chord voicings with `@define`
7. **Add loops**: Repeat patterns with `@loop`

## Advanced Techniques

### Technique 1: Layered Lead Sound

Stack two channels for thicker lead:

```markdown
# Channel 1: Bright synth
[00:00.000]
- cc 1.7.85
- cc 1.10.72
- note_on 1.C4 100 1000ms

# Channel 4: Detuned synth (simultaneous)
[@]
- cc 4.7.70
- cc 4.10.56
- note_on 4.C4 95 1000ms
```

### Technique 2: Call and Response

Alternate between channels for musical conversation:

```markdown
# Channel 1 asks
[00:00.000]
- note_on 1.C4 100 500ms
[00:00.500]
- note_on 1.E4 100 500ms

# Channel 5 answers
[00:01.000]
- note_on 5.G4 100 500ms
[00:01.500]
- note_on 5.C5 100 500ms
```

### Technique 3: Counter-melody

Add independent melody on another channel:

```markdown
# Main melody (channel 1) - ascending
[00:00.000]
- note_on 1.C4 100 1000ms
[00:01.000]
- note_on 1.E4 100 1000ms

# Counter-melody (channel 5) - descending
[00:00.000]
- note_on 5.C5 80 1000ms
[00:01.000]
- note_on 5.A4 80 1000ms
```

## Additional Resources

- [General MIDI Instrument List](https://www.midi.org/specifications-old/item/gm-level-1-sound-set)
- [General MIDI Drum Map](https://www.midi.org/specifications-old/item/general-midi-2)
- [MML Specification](https://github.com/cjgdev/midi-markdown/blob/main/spec.md) - Complete language reference
- [Example: 01_multi_channel_basic.mmd](https://github.com/cjgdev/midi-markdown/blob/main/examples/02_midi_features/01_multi_channel_basic.mmd)
- [Device Control Tutorial](device-control.md) - Control hardware devices
- [Basic Melody Tutorial](basic-melody.md) - Single-channel foundations

## Summary

In this tutorial, you learned:

- How to structure multi-channel MIDI arrangements
- Using channel 1 for lead melody
- Using channel 2 for bass line
- Using channel 3 for chord pads
- Using channel 10 for General MIDI drums
- Balancing levels with CC#7 (volume)
- Creating stereo space with CC#10 (pan)
- Building song structure with markers
- Coordinating timing across multiple channels
- General MIDI drum note mapping

You now have the skills to create complete multi-instrument arrangements with MML. Experiment with different instrument combinations and song structures!
