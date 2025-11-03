"""CLI commands for MIDI Markup Language.

This package contains individual command implementations for the MML CLI.
"""

from __future__ import annotations

from .check import check
from .compile import compile
from .inspect import inspect
from .library import library_info, library_list, library_validate
from .validate import validate
from .version import version

__all__ = [
    "check",
    "compile",
    "inspect",
    "library_info",
    "library_list",
    "library_validate",
    "validate",
    "version",
]
