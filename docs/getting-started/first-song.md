# Tutorial: Your First Song

> **Audience**: Beginners
> **Level**: Beginner
> **Time**: 30-45 minutes
> **Prerequisites**: [Quickstart Guide](quickstart.md), [Installation](installation.md)

Learn to create a complete multi-channel song with melody, bass, and atmospheric pads, including CC automation and tempo changes.

---

## What You'll Build

By the end of this tutorial, you'll have created a complete 1-minute 48-second song featuring:

- **Melody track** (Lead Synth on Channel 1) with pitch bend expression
- **Bass track** (Channel 2) with driving rhythms
- **Pad track** (Channel 3) with sustained chords
- **Song structure** with markers (Intro, Verse, Chorus, Bridge, Outro)
- **CC automation** for volume and modulation
- **Tempo changes** for dynamic energy shifts
- **Professional fade-out** ending

**Final result**: A complete MIDI file ready to load into your DAW or send to hardware synths.

---

## Step 1: Create Your Project File

Create a new file called `my_first_song.mmd`:

```bash
touch my_first_song.mmd
```

Open it in your favorite text editor. We'll build the song incrementally.

---

## Step 2: Add Frontmatter

Every MMD file starts with YAML frontmatter containing document properties:

```yaml
---
title: "My First Song"
author: "Your Name"
midi_format: 1
ppq: 480
description: "A complete song demonstrating MMD features"
---
```

**What this does**:
- `title` - Song name (stored in MIDI file)
- `author` - Your name (stored in MIDI metadata)
- `midi_format: 1` - Multi-track MIDI file (Format 1)
- `ppq: 480` - Pulses per quarter note (timing resolution)
- `description` - Optional project notes

---

## Step 3: Define Variables

Add convenience variables for channel numbers:

```yaml
@define LEAD_CHANNEL 1
@define BASS_CHANNEL 2
@define PAD_CHANNEL 3
```

**Why use variables?**
- Easy to change channel assignments later
- Makes code more readable
- Follows DRY (Don't Repeat Yourself) principle

Note: For this tutorial, we'll use the literal channel numbers (1, 2, 3) in commands for clarity. In production code, you'd use `${LEAD_CHANNEL}` syntax.

---

## Step 4: Set Up Song Structure

Add timing markers to define your song's sections:

```yaml
# ============================================
# Song Structure
# ============================================

[00:00.000]
- tempo 128
- time_signature 4/4
- key_signature Dm
- marker "Intro"
- track_name "Master"

[00:08.000]
- marker "Verse 1"

[00:24.000]
- marker "Pre-Chorus"

[00:32.000]
- marker "Chorus"

[00:48.000]
- marker "Verse 2"

[01:04.000]
- marker "Bridge"
- tempo 100

[01:20.000]
- marker "Final Chorus"
- tempo 132

[01:36.000]
- marker "Outro"
```

**Timing format**: `[mm:ss.milliseconds]` is **absolute timecode**

**What this does**:
- Sets tempo to 128 BPM at start
- Defines time signature (4/4 time)
- Sets key signature (D minor)
- Creates markers visible in your DAW
- Changes tempo at Bridge (slowdown) and Final Chorus (speed up)

---

## Step 5: Create the Lead Melody

Now let's add the lead synth melody. We'll start with an atmospheric intro:

```yaml
# ============================================
# Lead Synth (Channel 1) - Melody
# ============================================

# Intro - atmospheric entrance
[00:00.000]
- cc 1.7.40
- cc 1.10.64
[@]
- note_on 1.D4 60 2000ms

[00:02.000]
- note_on 1.F4 65 2000ms

[00:04.000]
- note_on 1.A4 70 4000ms
```

**Breaking it down**:

1. `cc 1.7.40` - Set volume (CC 7) to 40 on Channel 1
2. `cc 1.10.64` - Set pan (CC 10) to center (64)
3. `[@]` - **Simultaneous marker** - execute at same time as previous event
4. `note_on 1.D4 60 2000ms` - Play D4 (note name!), velocity 60, duration 2 seconds

**Note syntax**: `note_on <channel>.<note>.<velocity> <duration>`
- Channel: 1-16
- Note: MIDI number (60) OR note name (C4, D#5, Gb3)
- Velocity: 0-127 (loudness)
- Duration: milliseconds (ms) or seconds (s)

---

### Add Verse Melody

Continue with the verse melodic line:

```yaml
# Verse 1 - melodic line
[00:08.000]
- cc 1.7.70
[@]
- note_on 1.D5 80 500ms

[00:08.500]
- note_on 1.C5 80 500ms

[00:09.000]
- note_on 1.A4 85 1000ms

[00:10.000]
- note_on 1.F4 80 500ms

[00:10.500]
- note_on 1.D4 80 500ms

[00:11.000]
- note_on 1.C4 85 2000ms
```

**Notice**:
- Volume increased to 70 for the verse (`cc 1.7.70`)
- Timing precision to 500ms (half-second) for faster melody
- Mix of quarter notes (1000ms) and eighth notes (500ms)

---

### Add Expression with Pitch Bend

Make the melody more expressive with vibrato:

```yaml
# Add vibrato with pitch bend
[00:11.250]
- pb 1.200

[00:11.500]
- pb 1.-200

[00:11.750]
- pb 1.200

[00:12.000]
- pb 1.0
```

**Pitch bend syntax**: `pb <channel>.<amount>`
- Amount: -8192 to +8191 (0 = no bend)
- Creates vibrato by oscillating pitch up and down

---

### Add Pre-Chorus Build-Up

Build intensity with modulation (CC 1):

```yaml
# Pre-Chorus - building intensity
[00:24.000]
- cc 1.7.90
- cc 1.1.20
[@]
- note_on 1.A4 95 1000ms
[@]
- note_on 1.D5 95 1000ms

[00:25.000]
- cc 1.1.40

[00:26.000]
- cc 1.1.60
[@]
- note_on 1.F5 100 2000ms
[@]
- note_on 1.A5 100 2000ms

[00:28.000]
- cc 1.1.80
```

**Technique**: Gradual modulation increase (20 → 40 → 60 → 80) creates build-up tension.

---

### Add Full Energy Chorus

Peak energy with highest velocity and pitch bend expression:

```yaml
# Chorus - full energy
[00:32.000]
- cc 1.7.110
- cc 1.1.100
[@]
- note_on 1.D5 110 1000ms

[00:33.000]
- note_on 1.E5 110 1000ms

[00:34.000]
- note_on 1.F5 115 2000ms

[00:36.000]
- note_on 1.A5 120 4000ms

# Pitch bend expression
[00:37.000]
- pb 1.1000

[00:38.000]
- pb 1.2000

[00:39.000]
- pb 1.0
```

**Dynamics**:
- Volume maxed at 110 (`cc 1.7.110`)
- Velocities 110-120 (fortissimo)
- Dramatic pitch bends on sustained A5 note

---

## Step 6: Add the Bass Track

A solid bass foundation drives the rhythm:

```yaml
# ============================================
# Bass (Channel 2) - Foundation
# ============================================

# Verse 1 - simple bass line
[00:08.000]
- cc 2.7.90
[@]
- note_on 2.D2 100 900ms

[00:09.000]
- note_on 2.D2 95 900ms

[00:10.000]
- note_on 2.F2 100 900ms

[00:11.000]
- note_on 2.A2 100 900ms

[00:12.000]
- note_on 2.D2 100 900ms

[00:13.000]
- note_on 2.D2 95 900ms

[00:14.000]
- note_on 2.C2 100 900ms

[00:15.000]
- note_on 2.A1 100 900ms
```

**Bass pattern**: Steady quarter notes (900ms) outlining the chord progression.

---

### Add Driving Chorus Bass

Increase energy with eighth notes:

```yaml
# Chorus - driving eighth notes
[00:32.000]
- cc 2.7.110
[@]
- note_on 2.D2 110 450ms

[00:32.500]
- note_on 2.D2 100 450ms

[00:33.000]
- note_on 2.D2 110 450ms

[00:33.500]
- note_on 2.D2 100 450ms

[00:34.000]
- note_on 2.F2 110 450ms

[00:34.500]
- note_on 2.F2 100 450ms

[00:35.000]
- note_on 2.A2 110 450ms

[00:35.500]
- note_on 2.A2 100 450ms
```

**Technique**:
- Faster notes (450ms = eighth notes at 128 BPM)
- Velocity variation (110/100) creates pumping groove

---

## Step 7: Add Atmospheric Pads

Sustained chords create space and atmosphere:

```yaml
# ============================================
# Pad (Channel 3) - Atmosphere
# ============================================

# Intro - sustained chords
[00:00.000]
- cc 3.7.50
- cc 3.10.64
[@]
- note_on 3.D3 50 8000ms
[@]
- note_on 3.F3 50 8000ms
[@]
- note_on 3.A3 50 8000ms

# Gradual volume swell
[00:02.000]
- cc 3.7.60

[00:04.000]
- cc 3.7.70

[00:06.000]
- cc 3.7.80
```

**Pad technique**:
- Play multiple notes simultaneously with `[@]`
- Very long durations (8000ms = 8 seconds)
- Gradual volume swell (50 → 60 → 70 → 80)

---

### Add Verse and Chorus Pads

Continue with chord changes:

```yaml
# Verse - lighter pad
[00:08.000]
- cc 3.7.60
[@]
- note_on 3.D3 55 8000ms
[@]
- note_on 3.F3 55 8000ms
[@]
- note_on 3.A3 55 8000ms

[00:16.000]
- note_on 3.C3 55 8000ms
[@]
- note_on 3.E3 55 8000ms
[@]
- note_on 3.G3 55 8000ms

# Chorus - full pad
[00:32.000]
- cc 3.7.90
[@]
- note_on 3.D3 70 16000ms
[@]
- note_on 3.F3 70 16000ms
[@]
- note_on 3.A3 70 16000ms
[@]
- note_on 3.D4 70 16000ms
```

**Chord progression**:
- D minor (D-F-A) → C major (C-E-G)
- Chorus adds octave doubling (D4) for richness

---

## Step 8: Add Bridge (Tempo Change)

Create dynamic contrast with a tempo change and sparse notes:

```yaml
# ============================================
# Bridge - Tempo Change and Dynamic Shift
# ============================================

[01:04.000]
- cc 1.7.60
- cc 2.7.70
- cc 3.7.80

# Sparse, atmospheric notes
[@]
- note_on 1.D5 65 4000ms

[01:08.000]
- note_on 1.A4 65 4000ms

[01:12.000]
- note_on 1.F4 65 8000ms
```

**Remember**: We set `tempo 100` at `[01:04.000]` in the song structure (Step 4).

**Effect**: Sudden slowdown creates emotional impact and contrast.

---

## Step 9: Add Final Chorus (Explosive Return)

Return to full energy with tempo increase:

```yaml
# ============================================
# Final Chorus - Explosive Return
# ============================================

[01:20.000]
- cc 1.7.120
- cc 2.7.115
- cc 3.7.100

[@]
- note_on 1.D5 120 2000ms
[@]
- note_on 2.D2 120 1900ms
[@]
- note_on 3.D3 80 8000ms
[@]
- note_on 3.F3 80 8000ms
[@]
- note_on 3.A3 80 8000ms
```

**Remember**: We set `tempo 132` at `[01:20.000]` (slightly faster than original 128 BPM).

**Effect**: All three channels hit simultaneously with maximum energy.

---

## Step 10: Add Professional Fade-Out

End the song with a gradual fade:

```yaml
# ============================================
# Outro - Fade to Silence
# ============================================

[01:36.000]
- cc 1.7.100

[01:38.000]
- cc 1.7.80
- cc 2.7.70
- cc 3.7.60

[01:40.000]
- cc 1.7.60
- cc 2.7.50
- cc 3.7.40

[01:42.000]
- cc 1.7.40
- cc 2.7.30
- cc 3.7.20

[01:44.000]
- cc 1.7.20
- cc 2.7.10
- cc 3.7.10

[01:46.000]
- cc 1.7.0
- cc 2.7.0
- cc 3.7.0

[@]
- all_notes_off 1
[@]
- all_notes_off 2
[@]
- all_notes_off 3

[01:48.000]
- text "End of song"
- end_of_track
```

**Fade technique**:
- Gradual volume reduction every 2 seconds
- `all_notes_off` - Stops any lingering notes
- `end_of_track` - Signals MIDI file end

---

## Step 11: Compile Your Song

Save your file and compile it:

```bash
mmdc compile my_first_song.mmd -o output/my_first_song.mid
```

Expected output:
```
✅ Compilation successful (0.18s)
   Events: 142
   Tracks: 1 (Master)
   Duration: 1:48 (108s)
   Input: 4.2 KB → Output: 2.1 KB

   output/my_first_song.mid
```

---

## Step 12: Test Your Song

### Option 1: Load into DAW

Import `output/my_first_song.mid` into your DAW (Ableton Live, FL Studio, Logic Pro, etc.):

1. Create three MIDI tracks
2. Assign instruments:
   - Channel 1: Lead synth (bright, cutting sound)
   - Channel 2: Bass synth (deep, sub-heavy sound)
   - Channel 3: Pad synth (lush, atmospheric sound)
3. Press play!

### Option 2: Play in Real-Time

Play directly to hardware MIDI devices:

```bash
# List available MIDI ports
mmdc play --list-ports

# Play to specific port
mmdc play my_first_song.mmd --port "IAC Driver Bus 1"
```

---

## Complete File

Here's the complete `my_first_song.mmd` (simplified version):

<details>
<summary>Click to expand full code (140 lines)</summary>

```yaml
---
title: "My First Song"
author: "Your Name"
midi_format: 1
ppq: 480
description: "A complete song demonstrating MMD features"
---

@define LEAD_CHANNEL 1
@define BASS_CHANNEL 2
@define PAD_CHANNEL 3

# Song Structure
[00:00.000]
- tempo 128
- time_signature 4/4
- key_signature Dm
- marker "Intro"

[00:08.000]
- marker "Verse 1"

[00:32.000]
- marker "Chorus"

[01:04.000]
- marker "Bridge"
- tempo 100

[01:20.000]
- marker "Final Chorus"
- tempo 132

[01:36.000]
- marker "Outro"

# Lead Synth (Channel 1)
[00:00.000]
- cc 1.7.40
- cc 1.10.64
[@]
- note_on 1.D4 60 2000ms

[00:02.000]
- note_on 1.F4 65 2000ms

[00:04.000]
- note_on 1.A4 70 4000ms

[00:08.000]
- cc 1.7.70
[@]
- note_on 1.D5 80 500ms

[00:08.500]
- note_on 1.C5 80 500ms

[00:09.000]
- note_on 1.A4 85 1000ms

# Bass (Channel 2)
[00:08.000]
- cc 2.7.90
[@]
- note_on 2.D2 100 900ms

[00:09.000]
- note_on 2.D2 95 900ms

[00:10.000]
- note_on 2.F2 100 900ms

# Pad (Channel 3)
[00:00.000]
- cc 3.7.50
[@]
- note_on 3.D3 50 8000ms
[@]
- note_on 3.F3 50 8000ms
[@]
- note_on 3.A3 50 8000ms

# Outro - Fade
[01:36.000]
- cc 1.7.100

[01:38.000]
- cc 1.7.80
- cc 2.7.70
- cc 3.7.60

[01:46.000]
- cc 1.7.0
- cc 2.7.0
- cc 3.7.0
[@]
- all_notes_off 1
[@]
- all_notes_off 2
[@]
- all_notes_off 3

[01:48.000]
- end_of_track
```

</details>

---

## Key Concepts Learned

### 1. Timing
- **Absolute timecode**: `[mm:ss.milliseconds]` for precise timing
- **Simultaneous events**: `[@]` marker for layering
- **Tempo changes**: `tempo <bpm>` command

### 2. MIDI Commands
- **Note on**: `note_on <ch>.<note>.<vel> <duration>`
- **Control change**: `cc <ch>.<controller>.<value>`
- **Pitch bend**: `pb <ch>.<amount>`
- **All notes off**: `all_notes_off <ch>`

### 3. Note Names
- Use MIDI numbers (60) OR note names (C4, D#5, Gb3)
- Sharp (#) and flat (b) supported
- Octave range: C-1 to G9

### 4. Control Changes (CC)
- CC 7: Volume (0-127)
- CC 10: Pan (0=left, 64=center, 127=right)
- CC 1: Modulation wheel (0-127)

### 5. Song Structure
- Use `marker` for section labels
- Use `track_name` for track identification
- Use `key_signature` and `time_signature` for DAW integration

---

## Next Steps

### Enhance Your Song

Try these improvements:

1. **Add drums** - Use Channel 10 with MIDI drum notes:
   ```yaml
   [00:08.000]
   - note_on 10.36 100 100ms  # Kick drum (C2)
   - note_on 10.38 80 100ms   # Snare (D2)
   - note_on 10.42 60 100ms   # Hi-hat (F#2)
   ```

2. **Use aliases** for repeated patterns (see [Alias System Guide](../user-guide/alias-system.md))

3. **Add automation sweeps** for filter cutoff, reverb, delay:
   ```yaml
   [00:32.000]
   @sweep 1.74 0 127 4000ms linear  # Filter sweep
   ```

4. **Use musical timing** for better rhythm:
   ```yaml
   [1.1.0]  # Bar 1, Beat 1, Tick 0
   - note_on 1.C4 80 1b  # Duration in beats
   ```

### Continue Learning

- **[MML Syntax Reference](../user-guide/mmd-syntax.md)** - Complete command reference
- **[Timing System Guide](../user-guide/timing-system.md)** - All timing paradigms explained
- **[Alias System](../user-guide/alias-system.md)** - Create reusable command blocks
- **[Device Libraries](../user-guide/device-libraries.md)** - Control hardware devices
- **[Tutorials](../tutorials/)** - More step-by-step guides

### Explore Examples

Check out the `examples/` directory for more inspiration:
- `examples/03_advanced/10_comprehensive_song.mmd` - Full version of this tutorial
- `examples/03_advanced/01_loops_and_patterns.mmd` - Using `@loop` for repetition
- `examples/03_advanced/02_sweep_automation.mmd` - Advanced CC automation
- `examples/01_timing/02_musical_timing.mmd` - Musical time (bars.beats.ticks)

---

## Troubleshooting

### "Parse error: Unexpected token"

**Problem**: Syntax error in your MMD file.

**Solution**: Check that all commands are spelled correctly and values are in valid ranges. See [Troubleshooting Guide](../reference/troubleshooting.md).

### "Timing must be monotonically increasing"

**Problem**: Events are out of chronological order.

**Solution**: Ensure all timing markers increase in value:
```yaml
# ❌ WRONG
[00:03.000]
[00:02.000]  # Goes backwards!

# ✅ CORRECT
[00:02.000]
[00:03.000]
```

### "MIDI value out of range"

**Problem**: Used value outside 0-127.

**Solution**: MIDI values (notes, velocities, CC) must be 0-127:
```yaml
# ❌ WRONG
- note_on 1.60.128 1000ms  # Velocity > 127

# ✅ CORRECT
- note_on 1.60.127 1000ms  # Max velocity
```

### No sound when playing

**Problem**: MIDI port not configured or no instruments loaded.

**Solution**:
1. List available ports: `mmdc play --list-ports`
2. Select correct port: `mmdc play song.mmd --port "Your Port"`
3. In DAW, assign instruments to MIDI channels 1, 2, 3

---

## See Also

- [Quickstart Guide](quickstart.md) - 5-minute introduction
- [Installation](installation.md) - Setup instructions
- [CLI Reference](../cli-reference/compile.md) - `compile` command options
- [Troubleshooting Guide](../reference/troubleshooting.md) - Common issues and solutions
- [FAQ](../reference/faq.md) - Frequently asked questions

---

**Congratulations!** You've created your first complete MIDI song with MIDI Markdown. 🎉

Keep experimenting and share your creations!
