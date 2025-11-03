"""
Test Suite: Tracks

Tests for MML multi-track features including track definitions and multi-track automation.
"""


class TestTracks:
    """Test multi-track features"""

    def test_track_definition(self, parser):
        """Test track definition"""
        mml = """
## Track 1: Drums
@track drums channel=10
[00:00.000]
- note_on 10.36 100

## Track 2: Bass
@track bass channel=2
[00:00.000]
- note_on 2.40 100
"""
        doc = parser.parse_string(mml)
        assert len(doc.tracks) >= 2

    def test_empty_tracks(self, parser):
        """Test empty track definitions"""
        mml = """
## Track 1: Empty
@track empty
"""
        doc = parser.parse_string(mml)
        assert len(doc.tracks) >= 1

    def test_track_with_default_channel(self, parser):
        """Test track with default channel assignment"""
        mml = """
## Track 1: Melody
@track melody channel=1
[00:00.000]
- pc 1.10
- note_on 1.60 100
"""
        doc = parser.parse_string(mml)
        assert len(doc.tracks) >= 1
        track = doc.tracks[0]
        assert track.channel == 1
