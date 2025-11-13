"""CLI commands for MIDI Markup Language.

This package contains individual command implementations for the MML CLI.
"""

from __future__ import annotations

from .cheatsheet import cheatsheet
from .check import check
from .compile import compile
from .examples import examples
from .inspect import inspect
from .library import (
    library_create,
    library_info,
    library_install,
    library_list,
    library_search,
    library_validate,
)
from .play import play
from .ports import ports
from .repl import create_repl_command
from .validate import validate
from .version import version

__all__ = [
    "cheatsheet",
    "check",
    "compile",
    "create_repl_command",
    "examples",
    "inspect",
    "library_create",
    "library_info",
    "library_install",
    "library_list",
    "library_search",
    "library_validate",
    "play",
    "ports",
    "validate",
    "version",
]
