"""
MIDI Markup Language Constants

Defines all magic numbers and constants used throughout the MML implementation.
"""

# MIDI Value Ranges
MIDI_MIN = 0
MIDI_MAX = 127

# MIDI Channels
MIDI_CHANNEL_MIN = 1
MIDI_CHANNEL_MAX = 16

# Note Numbers
MIDI_NOTE_MIN = 0  # C-1
MIDI_NOTE_MAX = 127  # G9
MIDI_MIDDLE_C = 60  # C4

# Pitch Bend Range
# Supports both signed (-8192 to +8191, center=0) and unsigned (0 to 16383, center=8192) notation
PITCH_BEND_MIN = -8192
PITCH_BEND_MAX = (
    16383  # Was 8191, but MIDI spec allows 0-16383 (unsigned) or -8192 to +8191 (signed)
)
PITCH_BEND_CENTER = 0

# Tempo Range (BPM)
TEMPO_MIN = 1
TEMPO_MAX = 300

# Default Values
DEFAULT_PPQ = 480  # Pulses per quarter note (ticks per beat)
DEFAULT_TEMPO = 120  # BPM
DEFAULT_TIME_SIGNATURE = (4, 4)  # 4/4 time
DEFAULT_VELOCITY = 64  # Default note_off velocity

# Note Calculation
SEMITONES_PER_OCTAVE = 12

# MIDI File Formats
MIDI_FORMAT_SINGLE_TRACK = 0
MIDI_FORMAT_MULTI_TRACK = 1
MIDI_FORMAT_MULTI_SONG = 2
