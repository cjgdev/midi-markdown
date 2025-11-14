# Line 6 Helix Family - MMD Device Profiles

This directory contains comprehensive MIDI Markdown (MMD) device profiles for the complete Line 6 Helix family of guitar processors. Each profile provides extensive MIDI control capabilities with detailed documentation and usage examples.

## Quick Selection Guide

Choose the correct profile for your device:

| **Device** | **Profile File** | **Snapshots** | **Footswitches** | **MIDI** | **Best For** |
|------------|------------------|---------------|------------------|----------|--------------|
| **Helix Floor** | `helix.mmd` | 8 | 11 | 5-pin DIN + USB | Professional touring, complex arrangements |
| **Helix LT** | `helix.mmd` | 8 | 11 | 5-pin DIN + USB | Professional use, same as Floor |
| **Helix Rack** | `helix.mmd` | 8 | 0* | 5-pin DIN + USB | Studio/rack setups (*requires Helix Control) |
| **HX Stomp** | `hx_stomp.mmd` | 3 | 5 | USB only | Compact rigs, simple songs |
| **HX Stomp XL** | `hx_stomp_xl.mmd` | 4 | 8 | USB only | Balance of size and capability |
| **HX Effects** | `hx_effects.mmd` | 4 | 6 | 5-pin DIN + USB | Traditional amp rigs, effects only |

## Detailed Device Comparison

### Feature Matrix

| Feature | Floor/LT/Rack | HX Stomp | HX Stomp XL | HX Effects |
|---------|---------------|----------|-------------|------------|
| **Snapshots** | 8 | 3 | 4 | 4 |
| **Total Presets** | 1024 (8 setlists × 128) | 128 | 128 | 128 (32 banks × 4) |
| **Footswitches (MIDI)** | 11 | 5 | 8 | 6 |
| **Expression Pedals** | 3 | 2 | 2 | 2 |
| **5-pin DIN MIDI** | ✅ Yes | ❌ No | ❌ No | ✅ Yes |
| **USB MIDI** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **MIDI Thru** | ✅ Yes | ❌ No | ❌ No | ✅ Yes |
| **Command Center** | ✅ Full | ⚠️ Limited | ⚠️ Enhanced | ✅ Full* |
| **All Bypass (CC70)** | ❌ No | ✅ Yes | ✅ Yes | ❌ No |
| **Mode Switch (CC71)** | ❌ No | ✅ Yes | ✅ Yes | ❌ No |
| **Amp Modeling** | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No |
| **Dual DSP Path** | ✅ Yes | ❌ No | ❌ No | ⚠️ Effects |
| **CV Output** | ✅ Floor/Rack | ❌ No | ❌ No | ❌ No |
| **Ext Amp Switch** | ✅ Floor/LT | ❌ No | ❌ No | ❌ No |

*HX Effects Command Center lacks CV Out and Ext Amp (effects-only design)

### When to Choose Each Model

#### Helix Floor / LT / Rack
**Choose if you need:**
- 8 snapshots for complex song arrangements
- Maximum MIDI control (11 footswitches)
- 5-pin DIN MIDI for hardware integration
- Full Command Center with CV Out (Floor/Rack)
- Professional touring/studio capability

**MML Advantages:**
- Complete preset addressing (8 setlists × 128 presets)
- Maximum snapshot variations per song
- Full footswitch control (CC49-58)
- 3 expression pedals (CC1-3)

#### HX Stomp
**Choose if you need:**
- Compact size (smallest footprint)
- Budget-friendly option
- Simple songs (3 snapshots adequate)
- USB-only MIDI acceptable

**MML Limitations:**
- Only 3 snapshots (major constraint for complex songs)
- Only 5 footswitches (limited live control)
- No 5-pin DIN (cannot daisy-chain hardware)
- Limited Command Center (firmware 3.00+)

**Workarounds in MML:**
- Use preset changes for song sections
- Leverage Mode switching (CC71)
- Use All Bypass (CC70) for muting
- Organize presets strategically

#### HX Stomp XL
**Choose if you need:**
- Better than HX Stomp, smaller than full Helix
- 4 snapshots (verse/chorus/bridge/solo)
- 8 footswitches (adequate live control)
- Good size-to-capability ratio

**MML Advantages:**
- 4 snapshots covers most song structures
- Double the footswitches vs HX Stomp
- All Bypass and Mode Switch (CC70-71)
- Enhanced Command Center

**MML Note:**
- Still USB-only MIDI (no 5-pin DIN)
- Cannot daisy-chain MIDI hardware

#### HX Effects
**Choose if you need:**
- Effects processing only (use your own amp)
- Traditional amp rig integration
- 5-pin DIN MIDI (hardware chaining)
- 4 snapshots adequate

**MML Advantages:**
- Full Command Center for amp control
- 5-pin DIN MIDI (Thru capability)
- Unique preset addressing (32 banks × 4)
- Lower CPU load (no amp modeling)

**MML Note:**
- No amp/cab modeling
- Different preset addressing scheme
- No CV Out or Ext Amp switching

## Critical MIDI Implementation Notes

### Timing Requirements (ALL MODELS)

**Firmware 3.5x:**
- **350ms delay required** after Program Change messages
- Add 100ms between rapid CC messages
- Known issue: "dead time" where MIDI ignored

**Firmware 3.10+ (RECOMMENDED):**
- CC69 (snapshot) automatically buffered during preset load
- Can reduce delays to 50ms in most cases
- Still recommend 350ms for safety with complex presets

**Firmware 3.80 (CURRENT):**
- Most stable version (November 2024)
- Known issue: MIDI Clock Rx fails on preset changes
- Use Tap Tempo (CC64) after preset changes if tempo-critical

### Reserved CC Numbers (ALL MODELS)

**Never use these CCs for custom parameter control:**
- **CC1-3**: Expression Pedals 1-3
- **CC49-58**: Footswitches (varies by model)
- **CC59**: Expression Toe Switch
- **CC60-67**: Looper controls
- **CC64**: Tap Tempo (values 0-63 ignored, 64-127 = tap)
- **CC68**: Tuner on/off
- **CC69**: Snapshot select
- **CC70**: All Bypass (HX Stomp/XL only)
- **CC71**: Mode Switch (HX Stomp/XL only)
- **CC72**: Preset navigation

All other CCs (4-31, 33-48, 77-127) available for:
- Block bypass control (via MIDI Learn)
- Parameter control (via MIDI Learn)
- Custom assignments per preset

### Preset Addressing Schemes

**Helix Floor/LT/Rack:**
```
CC32 (value 0-7) = Select Setlist 1-8
PC (0-127) = Select Preset 1-128 within setlist

Example: Setlist 3, Preset 10
- cc 1.32.2     // Setlist 3 (0-indexed)
- pc 1.9        // Preset 10 (0-indexed)
```

**HX Stomp / HX Stomp XL:**
```
PC (0-127) = Direct preset addressing
No Bank Select needed

Example: Preset 42
- pc 1.41       // Preset 42 (0-indexed)
```

**HX Effects:**
```
PC (0-127) = Sequential bank addressing
32 Banks × 4 Presets (A-D)

PC 0-3   = Bank 1 (A,B,C,D)
PC 4-7   = Bank 2 (A,B,C,D)
...
PC 124-127 = Bank 32 (A,B,C,D)

Formula: PC = ((Bank - 1) × 4) + Preset_Offset
Where: A=0, B=1, C=2, D=3

Example: Bank 5, Preset C
- pc 1.18       // ((5-1)×4)+2 = 18
```

## Usage Examples

### Example 1: Simple Song Automation (Full Helix)

```mml
---
title: "Song with 8-Snapshot Arrangement"
devices:
  - helix: channel 1
---

@import "helix.mmd"

# INTRO
[00:00.000]
- helix_load 1 0 5              // Setlist 1, Preset 6
- helix_snap_1 1                // Clean intro

# VERSE
[00:16.000]
- helix_snap_2 1                // Verse tone

# PRE-CHORUS
[00:28.000]
- helix_snap_3 1                // Build-up

# CHORUS
[00:32.000]
- helix_snap_4 1                // High gain chorus

# BRIDGE
[01:04.000]
- helix_snap_5 1                // Ambient bridge

# SOLO
[01:20.000]
- helix_snap_6 1                // Lead tone

# FINAL CHORUS
[01:36.000]
- helix_snap_4 1                // Back to chorus

# OUTRO
[02:00.000]
- helix_snap_1 1                // Return to clean
```

### Example 2: HX Stomp with 3-Snapshot Limitation

```mml
---
title: "Song with Preset Changes (HX Stomp)"
devices:
  - stomp: channel 1
---

@import "hx_stomp.mmd"

# Use preset changes for major sections
# Use 3 snapshots for variations within sections

# VERSE PRESET
[00:00.000]
- hxstomp_preset 1 5
- hxstomp_snap_1 1              // Verse clean

[00:08.000]
- hxstomp_snap_2 1              // Verse with delay

# CHORUS PRESET (requires preset change)
[00:16.000]
- hxstomp_preset 1 6            // New preset
[+350ms]                         // Wait for load
- hxstomp_snap_1 1              // Chorus rhythm

[00:24.000]
- hxstomp_snap_2 1              // Chorus lead

# BRIDGE PRESET
[00:32.000]
- hxstomp_preset 1 7
[+350ms]
- hxstomp_snap_1 1              // Bridge ambient
```

### Example 3: Expression Pedal Automation

```mml
# Volume swell (works on all models)
@sweep from [00:00.000] to [00:04.000] every 16t
  - helix_exp1 1 ramp(0, 127)
@end

# Filter sweep
@sweep from [00:08.000] to [00:12.000] every 32t
  - helix_exp2 1 ramp(127, 0, exponential)
@end
```

### Example 4: HX Effects with Amp Control

```mml
---
title: "HX Effects + MIDI Amp Integration"
devices:
  - hxfx: channel 1
  - amp: channel 2
---

@import "hx_effects.mmd"

# Load HX Effects preset and switch amp channel
[00:00.000]
- hxfx_preset 1 8               // Bank 3 Preset A
[+350ms]
- pc 2.0                        // Amp clean channel

# Snapshot change with amp channel
[00:16.000]
- hxfx_snap_2 1                 // HX Effects chorus
[@]
- pc 2.1                        // Amp drive channel

# Solo section
[00:32.000]
- hxfx_snap_4 1                 // HX Effects lead
[@]
- pc 2.2                        // Amp lead channel
```

### Example 5: Looper Control (All Models)

```mml
# Enter looper mode and record
[02:00.000]
- helix_looper_on 1
[02:00.100]
- helix_looper_record_rec 1     // Start recording

# Switch to overdub after 8 seconds
[02:08.000]
- helix_looper_record_overdub 1

# Play loop
[02:16.000]
- helix_looper_play 1

# Half speed effect
[02:24.000]
- helix_looper_half_speed 1

# Reverse
[02:32.000]
- helix_looper_reverse 1

# Stop and exit
[02:40.000]
- helix_looper_stop 1
- helix_looper_off 1
```

## Troubleshooting Common Issues

### "Helix ignores my MIDI messages"
**Cause:** 350ms dead time after preset changes (firmware 3.5x)
**Solution:**
- Add 350ms delay after ALL Program Change messages
- Use firmware 3.10+ for CC69 buffering
- Organize songs with snapshots to avoid preset changes

### "Snapshots don't switch reliably"
**Cause:** Missing delays or old firmware
**Solution:**
- Update to firmware 3.10+ for automatic CC69 buffering
- Add 50ms delay after PC if using older firmware
- Check MIDI Base Channel matches in Global Settings

### "Footswitch toggles unpredictable"
**Cause:** Footswitches always TOGGLE (Helix limitation)
**Solution:**
- Don't expect absolute on/off control
- Send toggle commands, not state commands
- Program external controller accordingly

### "Expression pedal jerky/glitchy"
**Cause:** MIDI controller sending stepped values
**Solution:**
- Ensure external controller sends smooth CC curves
- Update to modern firmware (3.x)
- Test with MIDI monitor to verify CC stream

### "HX Stomp has no 5-pin MIDI"
**Cause:** Design limitation (USB-only)
**Solution:**
- Use MIDI Solutions USB MIDI Host adapter
- Use controller with USB-C capability
- Consider HX Effects if 5-pin DIN required

### "Can't connect MIDI hardware to HX Stomp/XL"
**Cause:** No MIDI Thru, USB-only
**Solution:**
- Use external MIDI interface/hub
- Use USB MIDI Host adapter for 5-pin conversion
- Consider full Helix or HX Effects for hardware chaining

## Firmware Recommendations

**RECOMMENDED: Firmware 3.80** (November 2024)
- Most stable current version
- All features mature
- Known issue: MIDI Clock Rx on preset change

**Alternative Stable Versions:**
- **3.71** (January 2024): Very stable, fixed HX One MIDI Thru bug
- **3.15** (February 2022): Last pre-Cab-Engine overhaul, lower dead time
- **3.00** (November 2020): Mandatory for HX Stomp Command Center

**Critical Updates:**
- HX Stomp: **3.00 mandatory** for Command Center
- HX One: **3.71 mandatory** for proper MIDI Thru

**After Every Firmware Update:**
1. Backup via HX Edit first
2. Update HX Edit software before firmware
3. Perform factory reset after update
4. Restore backup
5. Test all presets before live use

## Additional Resources

### Official Documentation
- Line 6 Helix Manual: https://line6.com/support/manuals/helix
- HX Stomp Manual: https://line6.com/support/manuals/hxstomp
- HX Effects Manual: https://line6.com/support/manuals/hxeffects
- MIDI PC Calculator: https://support.neuraldsp.com/help/quad-cortex-midi-pc-calculator

### Community Resources
- The Gear Page Helix Forum: https://www.thegearpage.net/board/
- Line 6 Forums: https://line6.com/support/forum/
- Helix Facebook Groups: Search "Line 6 Helix"

### Compatible MIDI Controllers
- **Morningstar MC6/MC8**: Most popular, excellent integration
- **Disaster Area Designs**: DMC.Micro, MIDI Baby
- **RJM Music**: Mastermind series (advanced)
- **Voes Controllers**: Good value
- **Paint Audio**: MIDI Captain series

### MMD Compiler Resources
- MMD Specification: See project documentation
- Device Profile Guidelines: See project documentation
- Example Projects: See examples directory

## Profile Maintenance

**Current Version:** 1.0.0
**Last Updated:** December 2024
**Tested Firmware:** 3.80
**MML Specification:** 1.0.0

**Change Log:**
- v1.0.0 (Dec 2024): Initial comprehensive release
  - Full Helix Floor/LT/Rack profile
  - HX Stomp profile with 3-snapshot workarounds
  - HX Stomp XL profile with 4-snapshot strategies
  - HX Effects profile with unique addressing
  - Complete documentation and examples

## Contributing

Found an issue or have improvements? Please submit:
- Bug reports for incorrect MIDI implementation
- Feature requests for additional macros
- Documentation improvements
- Usage examples for specific scenarios

## License

These device profiles are provided as part of the MMD project.
See main project LICENSE for details.

---

**Quick Start:** Import the appropriate device profile for your model and start programming! All profiles include extensive inline documentation, usage examples, and best practices for effective MIDI control.
