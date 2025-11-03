"""
Command expansion phase: variables, loops, sweeps.

This package handles Phase 4 of the compilation pipeline:
- Variable definitions (@define) and symbol table management
- Loop expansion (@loop) with iteration variables
- Sweep/ramp expansion (@sweep) with interpolation curves
- Command substitution and event generation

Pipeline position: FOURTH (after alias resolution, before validation)
Input: AST events (possibly with aliases already expanded)
Output: Expanded event list with all variables/loops/sweeps resolved
"""

from .errors import (
    ExpansionError,
    InvalidLoopConfigError,
    InvalidSweepConfigError,
    UndefinedVariableError,
    ValueRangeError,
)
from .expander import CommandExpander, ExpansionStats
from .loops import LoopCommand, LoopExpander
from .sweeps import RampType, SweepExpander
from .variables import SymbolTable, Variable

__all__ = [
    "CommandExpander",
    "ExpansionError",
    "ExpansionStats",
    "InvalidLoopConfigError",
    "InvalidSweepConfigError",
    "LoopCommand",
    "LoopExpander",
    "RampType",
    "SweepExpander",
    "SymbolTable",
    "UndefinedVariableError",
    "ValueRangeError",
    "Variable",
]
