"""
Test Suite: Comments

Tests for MML comment syntax including single-line and multi-line comments.
"""


class TestComments:
    """Test comment handling"""

    def test_single_line_comments(self, parser):
        """Test single-line comments with #"""
        mml = """
# This is a comment
[00:00.000]
- pc 1.0  # Inline comment
# Another comment
- cc 1.7.100
"""
        doc = parser.parse_string(mml)
        # Comments should be ignored, only commands should remain
        commands = doc.events[0]["commands"]
        assert len(commands) == 2

    def test_multi_line_comments(self, parser):
        """Test multi-line comments with /* */"""
        mml = """
/*
This is a multi-line comment
It can span multiple lines
*/
[00:00.000]
- pc 1.0
/* Inline multi-line */ - cc 1.7.100
"""
        doc = parser.parse_string(mml)
        commands = doc.events[0]["commands"]
        assert len(commands) == 2

    def test_comment_with_special_chars(self, parser):
        """Test comments containing special characters"""
        mml = """
# Comment with special chars: @#$%^&*()
[00:00.000]
- pc 1.0
/* Comment with symbols: {}[]<>?/ */
- cc 1.7.100
"""
        doc = parser.parse_string(mml)
        commands = doc.events[0]["commands"]
        assert len(commands) == 2

    def test_empty_document_with_comments(self, parser):
        """Test document with only comments"""
        mml = """
# Just a comment
/* And another one */
"""
        doc = parser.parse_string(mml)
        assert len(doc.events) == 0
