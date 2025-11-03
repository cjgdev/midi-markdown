"""Alias system for MIDI Markdown.

Handles device-specific command aliases and macro expansion.
"""

from .computation import ComputationError, SafeComputationEngine
from .conditionals import ConditionalEvaluator
from .errors import AliasError, AliasMaxDepthError, AliasRecursionError
from .imports import CircularImportError, ImportError, ImportManager
from .models import ExpansionContext, ExpansionNode
from .resolver import AliasResolver

__all__ = [
    "AliasError",
    "AliasMaxDepthError",
    "AliasRecursionError",
    "AliasResolver",
    "CircularImportError",
    "ComputationError",
    "ConditionalEvaluator",
    "ExpansionContext",
    "ExpansionNode",
    "ImportError",
    "ImportManager",
    "SafeComputationEngine",
]
