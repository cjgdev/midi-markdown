"""CLI commands for MIDI Markup Language.

This package contains individual command implementations for the MML CLI.
"""

from __future__ import annotations

from .check import check
from .cheatsheet import cheatsheet
from .compile import compile
from .examples import examples
from .inspect import inspect
from .library import library_info, library_list, library_validate
from .play import play
from .ports import ports
from .repl import create_repl_command
from .validate import validate
from .version import version

__all__ = [
    "check",
    "cheatsheet",
    "compile",
    "create_repl_command",
    "examples",
    "inspect",
    "library_info",
    "library_list",
    "library_validate",
    "play",
    "ports",
    "validate",
    "version",
]
