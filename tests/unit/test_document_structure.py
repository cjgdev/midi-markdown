"""
Test Suite: Document Structure

Tests for MML document-level features including frontmatter, imports, and defines.
"""


class TestDocumentStructure:
    """Test document-level features"""

    # ========================================================================
    # Basic Document Structure
    # ========================================================================

    def test_empty_document(self, parser):
        """Test parsing an empty document"""
        mml = ""
        doc = parser.parse_string(mml)
        assert doc is not None
        assert len(doc.events) == 0

    # ========================================================================
    # Frontmatter Tests
    # ========================================================================

    def test_frontmatter(self, parser):
        """Test parsing YAML frontmatter"""
        mml = """---
title: "Test Song"
author: "Test Author"
ppq: 480
---
"""
        doc = parser.parse_string(mml)
        assert doc.frontmatter["title"] == "Test Song"
        assert doc.frontmatter["author"] == "Test Author"
        assert doc.frontmatter["ppq"] == 480

    def test_frontmatter_with_nested_data(self, parser):
        """Test frontmatter with nested structures"""
        mml = """---
title: "Complex Song"
metadata:
  genre: "Electronic"
  bpm: 140
tags:
  - ambient
  - experimental
---
"""
        doc = parser.parse_string(mml)
        assert doc.frontmatter["title"] == "Complex Song"
        assert doc.frontmatter["metadata"]["genre"] == "Electronic"
        assert doc.frontmatter["metadata"]["bpm"] == 140
        assert "ambient" in doc.frontmatter["tags"]

    # ========================================================================
    # Import Tests
    # ========================================================================

    def test_imports(self, parser):
        """Test import statements"""
        mml = """
@import "devices/quad_cortex.mmd"
@import "devices/eventide_h90.mmd"
"""
        doc = parser.parse_string(mml)
        assert "devices/quad_cortex.mmd" in doc.imports
        assert "devices/eventide_h90.mmd" in doc.imports

    def test_single_import(self, parser):
        """Test single import statement"""
        mml = '@import "my_library.mmd"'
        doc = parser.parse_string(mml)
        assert len(doc.imports) == 1
        assert "my_library.mmd" in doc.imports

    # ========================================================================
    # Define Tests
    # ========================================================================

    def test_defines(self, parser):
        """Test define statements"""
        mml = """
@define MAIN_CHANNEL 1
@define VERSE_PRESET 5
"""
        doc = parser.parse_string(mml)
        assert "MAIN_CHANNEL" in doc.defines
        assert doc.defines["MAIN_CHANNEL"] == 1
        assert "VERSE_PRESET" in doc.defines
        assert doc.defines["VERSE_PRESET"] == 5

    def test_define_with_string_value(self, parser):
        """Test define with string value"""
        mml = '@define SONG_NAME "My Epic Track"'
        doc = parser.parse_string(mml)
        assert len(doc.defines) >= 1

    # ========================================================================
    # Combined Document Features
    # ========================================================================

    def test_complete_document_header(self, parser):
        """Test document with frontmatter, imports, and defines"""
        mml = """---
title: "Full Document"
ppq: 960
---
@import "devices/common.mmd"
@define TEMPO 140
@define CHANNEL 1

[00:00.000]
- tempo 140
"""
        doc = parser.parse_string(mml)
        assert doc.frontmatter["title"] == "Full Document"
        assert doc.frontmatter["ppq"] == 960
        assert "devices/common.mmd" in doc.imports
        assert len(doc.defines) >= 1
        assert len(doc.events) == 1
