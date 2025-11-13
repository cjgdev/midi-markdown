"""Console encoding utilities for cross-platform emoji and Unicode support.

This module provides utilities to detect console encoding capabilities and
determine whether emojis and Unicode characters can be safely displayed.

Particularly important for Windows consoles which may use limited encodings
like cp1252 or charmap that don't support Unicode emojis.
"""

from __future__ import annotations

import sys


def supports_unicode_emojis() -> bool:
    """Check if the current stdout encoding supports Unicode emojis.

    Returns:
        True if emojis can be safely displayed, False otherwise.
    """
    try:
        # Get stdout encoding (default to utf-8 if unknown)
        encoding = getattr(sys.stdout, "encoding", "utf-8") or "utf-8"

        # Known limited encodings that don't support emojis
        limited_encodings = {
            "cp1252",  # Windows Western European
            "windows-1252",  # Windows Western European (alt name)
            "charmap",  # Windows default (legacy)
            "mbcs",  # Windows Multi-Byte Character Set
            "ascii",  # 7-bit ASCII
            "latin-1",  # ISO-8859-1
            "iso-8859-1",  # ISO-8859-1 (alt name)
        }

        # Check if current encoding is limited
        if encoding.lower() in limited_encodings:
            return False

        # Try to encode a test emoji
        try:
            "✅".encode(encoding)
            return True
        except (UnicodeEncodeError, UnicodeDecodeError):
            return False

    except Exception:
        # If we can't determine encoding, assume no emoji support
        return False


def should_disable_emoji(no_emoji_flag: bool = False) -> bool:
    """Determine if emoji should be disabled based on environment.

    Args:
        no_emoji_flag: Explicit --no-emoji flag from user

    Returns:
        True if emoji should be disabled, False otherwise.
    """
    # Respect explicit flag
    if no_emoji_flag:
        return True

    # Auto-detect based on encoding
    return not supports_unicode_emojis()


def safe_emoji(emoji: str, fallback: str = "") -> str:
    """Return emoji if supported, otherwise return fallback.

    Args:
        emoji: Unicode emoji character(s)
        fallback: ASCII fallback string (default: empty string)

    Returns:
        emoji if supported, fallback otherwise.
    """
    if supports_unicode_emojis():
        return emoji
    return fallback


# Common emoji mappings with ASCII fallbacks
EMOJIS = {
    "check": ("✅", "[OK]"),
    "checkmark": ("✓", "[OK]"),
    "cross": ("✗", "[X]"),
    "error": ("❌", "[ERROR]"),
    "warning": ("⚠️", "[!]"),
    "info": ("ℹ️", "[i]"),
    "lightbulb": ("💡", "[i]"),
    "rocket": ("🚀", ">>"),
    "musical_note": ("🎵", "♪"),
    "gear": ("⚙️", "[*]"),
    "bullet": ("•", "-"),
    "arrow_right": ("→", "->"),
    "arrow_left": ("←", "<-"),
}


def get_emoji(name: str, use_fallback: bool | None = None) -> str:
    """Get emoji by name with automatic fallback.

    Args:
        name: Emoji name from EMOJIS dict
        use_fallback: Force fallback (None = auto-detect)

    Returns:
        Emoji or ASCII fallback based on encoding support.
    """
    if name not in EMOJIS:
        return ""

    emoji, fallback = EMOJIS[name]

    if use_fallback is None:
        use_fallback = not supports_unicode_emojis()

    return fallback if use_fallback else emoji
