# MML Alias System: Implementation Plan
**Version 1.0**

## Executive Summary

This document outlines the phased implementation plan for the MIDI Markup Language (MML) alias system. The alias system enables users to create reusable, parameterized command shortcuts for MIDI devices, with support for:

- **Simple aliases**: Direct parameter substitution
- **Parameter types**: Notes, percentages, enums, ranges with validation
- **Multi-command macros**: Sequences of commands executed together
- **Computed values**: Safe expression evaluation for transformations
- **Conditional logic**: Dynamic command selection based on parameters
- **Nested aliases**: Aliases calling other aliases with cycle detection
- **Device libraries**: Importable collections of device-specific aliases

---

## Architecture Overview

### Component Structure

```
┌─────────────────────────────────────────────────────────┐
│                    MML Parser (Lark)                    │
│  Handles: Document structure, timing, MIDI commands    │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│                  Alias System Core                       │
├─────────────────────────────────────────────────────────┤
│  • AliasRegistry          - Storage & lookup            │
│  • AliasParser            - Parse @alias definitions    │
│  • ParameterResolver      - Type conversion/validation  │
│  • AliasExpansionEngine   - Expand aliases to MIDI      │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│              Advanced Features (Optional)                │
├─────────────────────────────────────────────────────────┤
│  • SafeComputationEngine  - Evaluate expressions        │
│  • ConditionalEvaluator   - Process @if/@elif/@else     │
│  • DependencyAnalyzer     - Detect cycles               │
│  • ExpansionTracer        - Debug expansion             │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

```
Input MML File
    ↓
Lark Parser → AST
    ↓
Extract @alias definitions → AliasRegistry
    ↓
Extract @import statements → Load device libraries
    ↓
Parse command sequences → Identify alias invocations
    ↓
AliasExpansionEngine → Expand aliases recursively
    ↓
Parameter resolution → Type conversion & validation
    ↓
Computation evaluation (if present) → Computed values
    ↓
Generate MIDI commands → MIDI events
    ↓
Output MIDI file
```

---

## Implementation Stages

Each stage builds on the previous one and delivers a functionally complete, tested feature set.

---

## Stage 1: Foundation & Simple Aliases
**Duration: 1-2 weeks**

### Goals
- Establish core data structures
- Implement basic alias definition and expansion
- Support simple parameter substitution
- No computation, no conditionals, no nesting yet

### Deliverables

#### 1.1 Core Data Structures

**File: `mml/alias/models.py`**

Implement:
```python
@dataclass
class ParameterDefinition:
    """Defines a parameter in an alias"""
    name: str
    param_type: ParameterType = ParameterType.GENERIC
    min_value: int = 0
    max_value: int = 127
    default_value: Optional[int] = None

@dataclass
class AliasCommand:
    """A single command within an alias"""
    command_type: str
    parameters: List[str]  # Can contain {param} placeholders
    line_number: int

@dataclass
class AliasDefinition:
    """Complete alias definition"""
    name: str
    parameters: List[ParameterDefinition]
    commands: List[AliasCommand]
    description: str = ""
    source_file: str = ""
    source_line: int = 0
```

#### 1.2 Alias Registry

**File: `mml/alias/registry.py`**

Implement:
```python
class AliasRegistry:
    """Central storage for alias definitions"""
    
    def register_alias(self, alias: AliasDefinition) -> None
    def get_alias(self, name: str) -> Optional[AliasDefinition]
    def has_alias(self, name: str) -> bool
    def list_aliases(self) -> List[str]
```

#### 1.3 Basic Parameter Resolver

**File: `mml/alias/parameters.py`**

Implement:
```python
class ParameterResolver:
    """Handles basic parameter validation and conversion"""
    
    def validate_range(self, value: int, min_val: int, max_val: int) -> int
    def apply_default(self, param_def: ParameterDefinition, 
                     provided_value: Optional[str]) -> int
```

#### 1.4 Simple Alias Parser

**File: `mml/alias/parser.py`**

Implement:
```python
class AliasParser:
    """Parse alias definitions from MML"""
    
    def parse_alias_definition(self, alias_node: LarkTree) -> AliasDefinition
    def extract_parameters(self, param_string: str) -> List[ParameterDefinition]
    def parse_command_template(self, cmd_string: str) -> AliasCommand
```

**Lark Grammar Extension:**
```
// Delegate to Claude AI coder to add:
// - @alias directive parsing
// - Parameter specification: {name}, {name:min-max}, {name=default}
// - Command template parsing with {param} placeholders
```

#### 1.5 Basic Expansion Engine

**File: `mml/alias/expander.py`**

Implement:
```python
class AliasExpansionEngine:
    """Expand simple aliases (no nesting, no computation)"""
    
    def expand(self, alias_name: str, 
               arguments: List[str]) -> List[MIDICommand]
    
    def _bind_parameters(self, alias_def: AliasDefinition,
                        arguments: List[str]) -> Dict[str, int]
    
    def _substitute_parameters(self, template: str,
                               param_values: Dict[str, int]) -> str
```

### Test Cases (Stage 1)

**File: `tests/alias/test_stage1_simple.py`**

```python
def test_simple_alias_registration()
def test_simple_alias_expansion()
def test_parameter_validation()
def test_default_parameter_values()
def test_parameter_range_enforcement()
def test_undefined_alias_error()
def test_parameter_count_mismatch()
def test_missing_required_parameter()
```

### Success Criteria

✅ Can parse and register simple alias definitions  
✅ Can expand aliases with basic parameter substitution  
✅ Parameter validation works (ranges, defaults)  
✅ Clear error messages for common mistakes  
✅ All Stage 1 tests pass  

### Example Working Code (Stage 1)

```markdown
# Define simple aliases
@alias cortex_preset pc.{channel}.{preset} "Load preset"
@alias h90_mix cc.{channel}.84.{value:0-127} "Set A/B mix"
@alias volume_max cc.{channel}.7.{level=127} "Set volume"

# Use them
[00:00.000]
- cortex_preset 1 5        # Expands to: pc 1.5
- h90_mix 2 64             # Expands to: cc 2.84.64
- volume_max 1             # Expands to: cc 1.7.127 (uses default)
```

---

## Stage 2: Enhanced Parameter Types
**Duration: 1 week**

### Goals
- Add support for special parameter types
- Implement note name resolution
- Add percentage scaling
- Support enum/named parameters

### Deliverables

#### 2.1 Enhanced Parameter Types

**File: `mml/alias/parameters.py` (extend)**

Add to ParameterResolver:
```python
def resolve_note_parameter(self, value: Union[str, int]) -> int
    # "C4" -> 60, "D#5" -> 75, etc.

def resolve_percent_parameter(self, value: int) -> int
    # 0-100 -> 0-127 scaling

def resolve_enum_parameter(self, value: str, 
                          enum_map: Dict[str, int]) -> int
    # Named values: "series" -> 0, "parallel" -> 1

def resolve_bool_parameter(self, value: Union[str, bool, int]) -> int
    # true/false/1/0 -> 0 or 127
```

#### 2.2 Enhanced Parameter Definition

Extend `ParameterDefinition` to support:
```python
@dataclass
class ParameterDefinition:
    # ... existing fields ...
    enum_values: Optional[Dict[str, int]] = None  # For named params
```

#### 2.3 Parser Updates

**File: `mml/alias/parser.py` (extend)**

Update `extract_parameters()` to parse:
- `{note}` - Note parameter
- `{percent:0-100}` - Percentage parameter  
- `{mode=series:0,parallel:1,a_only:2}` - Enum parameter
- `{enabled:0-1}` or `{bool}` - Boolean parameter

**Lark Grammar Extension:**
```
// Delegate to Claude AI coder to add:
// - Enum syntax: {name=opt1:val1,opt2:val2}
// - Type hints: {note}, {percent}, {bool}
```

### Test Cases (Stage 2)

**File: `tests/alias/test_stage2_types.py`**

```python
def test_note_name_resolution()
def test_note_with_sharps_flats()
def test_note_octave_ranges()
def test_percent_to_midi_scaling()
def test_enum_parameter_resolution()
def test_invalid_enum_value_error()
def test_bool_parameter_variations()
```

### Success Criteria

✅ Note names resolve correctly (C4=60, C#5=73, etc.)  
✅ Percentages scale to 0-127 properly  
✅ Enum parameters work with named values  
✅ Boolean parameters accept multiple formats  
✅ All Stage 2 tests pass  

### Example Working Code (Stage 2)

```markdown
@alias play_note note_on.{channel}.{note}.{velocity:0-127} "Play a note"
@alias h90_routing cc.{ch}.85.{mode=series:0,parallel:1,a_only:2,b_only:3}
@alias reverb_mix cc.{ch}.91.{percent:0-100} "Reverb mix percentage"
@alias stomp_toggle cc.{ch}.81.{enabled:0-1} "Toggle stomp"

# Usage
- play_note 1 C4 100           # Note name
- h90_routing 2 parallel       # Named enum
- reverb_mix 1 75%             # Percentage (delegated to parser)
- stomp_toggle 1 true          # Boolean
```

---

## Stage 3: Multi-Command Macros
**Duration: 1 week**

### Goals
- Support aliases that expand to multiple MIDI commands
- Implement @end block syntax
- Enable complex initialization sequences

### Deliverables

#### 3.1 Multi-Command Support

**File: `mml/alias/models.py` (extend)**

Update `AliasDefinition`:
```python
@dataclass
class AliasDefinition:
    # ... existing fields ...
    is_macro: bool = False  # True if multi-command
```

#### 3.2 Parser Updates

**File: `mml/alias/parser.py` (extend)**

Add:
```python
def parse_macro_body(self, body_nodes: List[LarkTree]) -> List[AliasCommand]
    # Parse command list between @alias and @end
```

**Lark Grammar Extension:**
```
// Delegate to Claude AI coder to add:
// - Multi-line alias syntax with @end terminator
// - Command list parsing within alias body
```

#### 3.3 Expander Updates

**File: `mml/alias/expander.py` (extend)**

Update expansion logic to handle multiple commands per alias.

### Test Cases (Stage 3)

**File: `tests/alias/test_stage3_macros.py`**

```python
def test_multi_command_expansion()
def test_parameter_substitution_in_macro()
def test_macro_generates_correct_count()
def test_macro_preserves_order()
```

### Success Criteria

✅ Multi-command aliases parse correctly  
✅ All commands in macro expand with correct parameters  
✅ Command order preserved  
✅ All Stage 3 tests pass  

### Example Working Code (Stage 3)

```markdown
@alias cortex_load {ch}.{setlist}.{group}.{preset} "Complete preset load"
  - cc {ch}.32.{setlist}
  - cc {ch}.0.{group}
  - pc {ch}.{preset}
@end

# Usage - expands to 3 MIDI commands
- cortex_load 1 2 0 5
```

---

## Stage 4: Import System & Device Libraries
**Duration: 1 week**

### Goals
- Implement @import directive
- Support device library files
- Handle relative paths
- Detect circular imports

### Deliverables

#### 4.1 Import Manager

**File: `mml/alias/imports.py`**

```python
class ImportManager:
    """Manages alias imports and device libraries"""
    
    def import_library(self, filepath: str, 
                      current_file: str) -> List[AliasDefinition]
    def resolve_path(self, import_path: str, 
                    relative_to: str) -> str
    def check_circular_import(self, filepath: str, 
                             import_chain: List[str]) -> None
```

#### 4.2 Registry Updates

**File: `mml/alias/registry.py` (extend)**

Add:
```python
def import_library(self, filepath: str) -> None
def get_import_chain(self) -> List[str]
```

#### 4.3 Parser Updates

**Lark Grammar Extension:**
```
// Delegate to Claude AI coder to add:
// - @import directive parsing
// - String literal for filepath
```

### Test Cases (Stage 4)

**File: `tests/alias/test_stage4_imports.py`**

```python
def test_import_device_library()
def test_import_relative_path()
def test_import_absolute_path()
def test_circular_import_detection()
def test_import_nonexistent_file()
def test_multiple_imports()
```

### Success Criteria

✅ Can import device library files  
✅ Relative paths resolve correctly  
✅ Circular imports detected and prevented  
✅ Imported aliases available in main file  
✅ All Stage 4 tests pass  

### Example Working Code (Stage 4)

```markdown
# main.mml
@import "devices/quad_cortex.mml"
@import "devices/eventide_h90.mml"

# Now can use aliases from imported libraries
- cortex_preset 1 5
- h90_routing 2 parallel
```

---

## Stage 5: Nested Alias Expansion
**Duration: 2 weeks**

### Goals
- Support aliases calling other aliases
- Implement cycle detection
- Add depth limiting
- Create dependency analyzer

### Deliverables

#### 5.1 Expansion with Nesting

**File: `mml/alias/expander.py` (major refactor)**

```python
class AliasExpansionEngine:
    """Expand aliases with full nesting support"""
    
    def __init__(self, registry, max_depth: int = 10)
    
    def expand(self, alias_name: str, 
               arguments: List[str],
               context: Dict[str, Any] = None) -> List[MIDICommand]
    
    def _expand_node(self, node: ExpansionNode,
                    context: Dict[str, Any],
                    expansion_stack: Set[str]) -> List[MIDICommand]
    
    def _expand_command(self, cmd: AliasCommand,
                       param_context: Dict[str, Any],
                       current_depth: int,
                       parent_node: ExpansionNode,
                       expansion_stack: Set[str]) -> List[MIDICommand]
```

#### 5.2 Expansion Tracking

**File: `mml/alias/models.py` (extend)**

```python
@dataclass
class ExpansionNode:
    """Node in expansion graph"""
    alias_name: str
    arguments: List[str]
    depth: int
    status: ExpansionStatus
    parent: Optional['ExpansionNode'] = None
    
    def get_call_chain(self) -> List[str]
```

#### 5.3 Dependency Analyzer

**File: `mml/alias/analysis.py`**

```python
class AliasDependencyAnalyzer:
    """Analyze alias dependencies"""
    
    def __init__(self, registry: AliasRegistry)
    def find_cycles(self) -> List[List[str]]
    def calculate_max_depth(self, alias_name: str) -> int
    def has_cycle(self, alias_name: str) -> bool
    def get_dependency_order(self) -> List[str]
```

#### 5.4 Error Classes

**File: `mml/alias/errors.py`**

```python
class RecursionError(Exception):
    def __init__(self, call_chain: List[str])

class MaxDepthExceededError(Exception):
    def __init__(self, depth: int, max_depth: int, call_chain: List[str])
```

### Test Cases (Stage 5)

**File: `tests/alias/test_stage5_nesting.py`**

```python
def test_simple_nested_alias()
def test_deep_nesting_within_limit()
def test_direct_recursion_detected()
def test_indirect_recursion_detected()
def test_max_depth_exceeded()
def test_dependency_analysis()
def test_cycle_detection()
def test_legitimate_repeated_use()
```

### Success Criteria

✅ Aliases can call other aliases  
✅ Cycles detected immediately (before expansion)  
✅ Depth limit prevents runaway expansion  
✅ Clear error messages with call chain  
✅ Dependency analysis works correctly  
✅ All Stage 5 tests pass  

### Example Working Code (Stage 5)

```markdown
# Base aliases
@alias h90_routing cc.{ch}.85.{mode=series:0,parallel:1}

# Calls another alias
@alias h90_dual_reverb {ch}.{preset}
  - pc {ch}.{preset}
  - h90_routing {ch} parallel  # Nested alias call
  - cc {ch}.84.64
@end

# Usage - expands recursively
- h90_dual_reverb 2 25
```

---

## Stage 6: Computation Engine
**Duration: 2 weeks**

### Goals
- Implement safe computation evaluation
- Support mathematical expressions
- Add MIDI-specific functions
- Ensure security (no arbitrary code execution)

### Deliverables

#### 6.1 Safe Computation Engine

**File: `mml/alias/computation.py`**

```python
class SafeComputationEngine:
    """Safely evaluate computation blocks"""
    
    MAX_OPERATIONS = 10000
    MAX_EXECUTION_TIME = 1.0
    
    def evaluate(self, code: str, 
                input_params: Dict[str, Any]) -> ComputationResult
    
    def _validate_ast(self, tree: ast.AST) -> None
    def _instrument_ast(self, tree: ast.AST, 
                       protected_params: set) -> ast.AST
    
    # Custom MIDI functions
    def _note_to_midi(self, note_name: str) -> int
    def _scale_range(self, value: float, in_min: float, in_max: float,
                    out_min: float, out_max: float) -> float
    def _bpm_to_ms(self, bpm: float, note_value: str) -> float
    def _msb(self, value: int) -> int
    def _lsb(self, value: int) -> int
    def _to_14bit(self, value: int) -> tuple
    # ... more MIDI functions
```

#### 6.2 Computation Result

**File: `mml/alias/models.py` (extend)**

```python
@dataclass
class ComputationResult:
    """Result of computation evaluation"""
    variables: Dict[str, Any]
    execution_time_ms: float
    operations_count: int
    warnings: List[str]
```

#### 6.3 Alias Definition Updates

**File: `mml/alias/models.py` (extend)**

```python
@dataclass
class AliasDefinition:
    # ... existing fields ...
    has_computation: bool = False
    computation_code: Optional[str] = None
```

#### 6.4 Parser Updates

**Lark Grammar Extension:**
```
// Delegate to Claude AI coder to add:
// - Computation block syntax: @alias name {...}
// - Python-like expression parsing within braces
```

#### 6.5 Integration with Expander

**File: `mml/alias/expander.py` (extend)**

Update `_expand_node` to evaluate computations:
```python
if alias_def.has_computation:
    comp_result = self.computation_engine.evaluate(
        alias_def.computation_code,
        param_context
    )
    param_context.update(comp_result.variables)
```

### Test Cases (Stage 6)

**File: `tests/alias/test_stage6_computation.py`**

```python
def test_basic_arithmetic()
def test_parameter_access()
def test_parameter_mutation_blocked()
def test_custom_midi_functions()
def test_note_to_midi_conversion()
def test_tempo_sync_calculation()
def test_security_import_blocked()
def test_security_attribute_blocked()
def test_operation_limit()
def test_execution_timeout()
def test_conditional_in_computation()
def test_list_comprehension()
```

### Success Criteria

✅ Computations evaluate safely (no code injection)  
✅ MIDI functions work correctly  
✅ Input parameters read-only  
✅ Operation/time limits enforced  
✅ Clear error messages for computation errors  
✅ All Stage 6 tests pass  

### Example Working Code (Stage 6)

```markdown
@alias cortex_tempo cc.{channel}.14.{bpm:40-300} "Set tempo" {
  value = int((bpm - 40) * 127 / 260)
}
  - cc {channel}.14.{value}
@end

@alias delay_sync {ch}.{bpm:40-300}.{note_val} "Tempo-synced delay" {
  delay_ms = bpm_to_ms(bpm, note_val)
  delay_cc = int(clamp(scale_range(delay_ms, 0, 2000, 0, 127), 0, 127))
}
  - cc {ch}.12.{delay_cc}
@end

# Usage
- cortex_tempo 1 120
- delay_sync 2 128 quarter
```

---

## Stage 7: Conditional Logic
**Duration: 1 week**

### Goals
- Implement @if/@elif/@else in aliases
- Support condition evaluation
- Integrate with computation engine

### Deliverables

#### 7.1 Conditional Structures

**File: `mml/alias/models.py` (extend)**

```python
@dataclass
class Condition:
    """Represents a condition"""
    left: str
    operator: str  # ==, !=, <, >, <=, >=
    right: Union[str, int]
    
    def evaluate(self, context: Dict[str, Any]) -> bool

@dataclass
class ConditionalBranch:
    """Branch in conditional"""
    condition: Optional[Condition]  # None for @else
    commands: List[AliasCommand]

@dataclass
class AliasDefinition:
    # ... existing fields ...
    has_conditionals: bool = False
    conditional_tree: Optional[List[ConditionalBranch]] = None
```

#### 7.2 Conditional Evaluator

**File: `mml/alias/conditionals.py`**

```python
class ConditionalEvaluator:
    """Evaluate conditional branches"""
    
    def evaluate_branches(self, branches: List[ConditionalBranch],
                         context: Dict[str, Any]) -> List[AliasCommand]
    
    def parse_condition(self, condition_str: str) -> Condition
```

#### 7.3 Parser Updates

**Lark Grammar Extension:**
```
// Delegate to Claude AI coder to add:
// - @if/@elif/@else/@end syntax
// - Condition parsing: {var} operator value
```

### Test Cases (Stage 7)

**File: `tests/alias/test_stage7_conditionals.py`**

```python
def test_simple_if_condition()
def test_if_elif_else()
def test_condition_with_enum_param()
def test_condition_with_computed_value()
def test_nested_conditionals()
def test_all_branches_skipped()
```

### Success Criteria

✅ Conditional syntax parses correctly  
✅ Branches evaluate properly  
✅ Works with enum parameters  
✅ Integrates with computation values  
✅ All Stage 7 tests pass  

### Example Working Code (Stage 7)

```markdown
@alias smart_load {ch}.{preset}.{device_type} "Device-aware load"
  @if {device_type} == "cortex"
    - pc {ch}.{preset}
  @elif {device_type} == "h90"
    - cc {ch}.71.{preset}
  @else
    - pc {ch}.{preset}
  @end
@end

# Usage
- smart_load 1 5 cortex    # Uses pc
- smart_load 2 10 h90      # Uses cc
```

---

## Stage 8: Performance & Polish
**Duration: 1 week**

### Goals
- Add memoization/caching
- Implement expansion tracing
- Create debugging tools
- Optimize hot paths

### Deliverables

#### 8.1 Memoized Expansion

**File: `mml/alias/expander.py` (extend)**

```python
class MemoizedExpansionEngine(AliasExpansionEngine):
    """Expansion with result caching"""
    
    def __init__(self, registry, max_depth=10)
    def expand(self, alias_name, arguments, context=None)
    def clear_cache(self)
    def get_cache_stats(self) -> Dict[str, int]
```

#### 8.2 Expansion Tracer

**File: `mml/alias/debug.py`**

```python
class ExpansionTracer:
    """Debug tracing for expansions"""
    
    def enable(self)
    def disable(self)
    def record_expansion(self, alias_name, arguments, depth, result)
    def print_trace(self, output_stream=None)
    def export_graphviz(self) -> str
```

#### 8.3 Error Formatter

**File: `mml/alias/errors.py` (extend)**

```python
class ErrorFormatter:
    """Format errors with context"""
    
    @staticmethod
    def format_alias_error(error, alias_name, source_code, line_num) -> str
    
    @staticmethod
    def format_computation_error(error, code, context) -> str
```

### Test Cases (Stage 8)

**File: `tests/alias/test_stage8_performance.py`**

```python
def test_memoization_caching()
def test_cache_invalidation()
def test_cache_hit_rate()
def test_expansion_tracing()
def test_trace_export()
def test_error_formatting()
```

### Success Criteria

✅ Caching improves repeated expansion performance  
✅ Tracing provides useful debug information  
✅ Error messages are clear and helpful  
✅ Cache stats available for monitoring  
✅ All Stage 8 tests pass  

---

## Stage 9: Integration & Documentation
**Duration: 1 week**

### Goals
- Integrate alias system with main MML parser
- Write comprehensive documentation
- Create example device libraries
- Performance benchmarking

### Deliverables

#### 9.1 Main Parser Integration

**File: `mml/parser.py` (extend)**

- Hook alias parsing into main document parsing
- Expand aliases before MIDI generation
- Handle timing preservation during expansion

#### 9.2 Device Libraries

**Files: `devices/*.mml`**

Create example libraries:
- `quad_cortex.mml` - Neural DSP Quad Cortex
- `eventide_h90.mml` - Eventide H90
- `kemper.mml` - Kemper Profiler
- `helix.mml` - Line 6 Helix

#### 9.3 Documentation

**Files:**
- `docs/alias_system_guide.md` - User guide
- `docs/device_library_creation.md` - Library author guide
- `docs/api_reference.md` - API documentation
- `examples/alias_examples.mml` - Practical examples

#### 9.4 Performance Benchmarks

**File: `benchmarks/alias_performance.py`**

Measure:
- Simple alias expansion time
- Nested alias expansion time
- Computation evaluation time
- Cache effectiveness
- Memory usage

### Test Cases (Stage 9)

**File: `tests/integration/test_stage9_integration.py`**

```python
def test_end_to_end_mml_with_aliases()
def test_device_library_usage()
def test_complex_real_world_scenario()
def test_performance_benchmarks()
def test_documentation_examples()
```

### Success Criteria

✅ Aliases work seamlessly in MML documents  
✅ Device libraries parse and function correctly  
✅ Documentation is complete and accurate  
✅ Performance meets targets (<10ms for typical expansion)  
✅ All integration tests pass  

---

## Testing Strategy

### Test Organization

```
tests/
├── alias/
│   ├── test_stage1_simple.py
│   ├── test_stage2_types.py
│   ├── test_stage3_macros.py
│   ├── test_stage4_imports.py
│   ├── test_stage5_nesting.py
│   ├── test_stage6_computation.py
│   ├── test_stage7_conditionals.py
│   └── test_stage8_performance.py
├── integration/
│   └── test_stage9_integration.py
└── fixtures/
    ├── simple_aliases.mml
    ├── device_library.mml
    └── complex_expansion.mml
```

### Test Coverage Requirements

- **Minimum Coverage**: 85% for all modules
- **Critical Path Coverage**: 95% for expander and computation engine
- **Security Tests**: 100% coverage for AST validation

### Continuous Testing

Each stage must:
1. Pass all previous stage tests (no regression)
2. Pass all new stage-specific tests
3. Maintain or improve code coverage
4. Pass performance benchmarks (if applicable)

---

## Parser Integration Notes (for Claude AI Coder)

### Lark Grammar Extensions Required

Each stage will require specific Lark grammar additions. The Claude AI coder should:

1. **Extend the existing MML grammar** incrementally
2. **Preserve existing grammar rules** (no breaking changes)
3. **Use consistent naming conventions** for new rules
4. **Add comprehensive comments** to grammar rules
5. **Test each grammar change** independently

### Key Grammar Areas to Extend

#### Stage 1: Basic Alias Syntax
```lark
// Add to grammar:
alias_definition: "@alias" NAME parameter_list command_pattern description?
parameter_list: PARAMETER+
command_pattern: COMMAND_TYPE "." parameter_references
```

#### Stage 2: Enhanced Parameters
```lark
// Add parameter type hints
parameter: "{" NAME type_hint? range_spec? default_value? enum_spec? "}"
type_hint: ":" ("note" | "percent" | "bool" | "channel")
```

#### Stage 3: Multi-Command Macros
```lark
// Add block syntax
macro_definition: "@alias" NAME parameter_list description? command_block "@end"
command_block: command_line+
```

#### Stage 4: Import Directive
```lark
// Add import statement
import_statement: "@import" STRING
```

#### Stage 6: Computation Blocks
```lark
// Add computation syntax
alias_with_computation: "@alias" NAME parameter_list description? computation_block command_block "@end"
computation_block: "{" python_like_code "}"
```

#### Stage 7: Conditionals
```lark
// Add conditional syntax
conditional_block: "@if" condition command_list elif_blocks? else_block? "@end"
elif_blocks: ("@elif" condition command_list)+
else_block: "@else" command_list
```

### AST Node Expectations

The Claude AI coder should ensure that parsed AST nodes contain:
- **Line numbers** for error reporting
- **Source file information** for debugging
- **Proper structure** matching the data models defined in each stage

---

## Success Metrics

### Functionality Metrics

- ✅ 100% of specification features implemented
- ✅ All test cases passing
- ✅ No known critical bugs

### Performance Metrics

- ⚡ Simple alias expansion: <1ms
- ⚡ Nested alias expansion (depth 5): <5ms
- ⚡ Computation evaluation: <10ms
- ⚡ Cache hit rate: >80% for repeated expansions
- ⚡ Memory usage: <100MB for 1000 aliases

### Quality Metrics

- 📊 Code coverage: >85%
- 📊 Critical path coverage: >95%
- 📝 Documentation completeness: 100%
- 🐛 Known bugs: 0 critical, <5 minor
- ✨ Code passes linting/formatting checks

### User Experience Metrics

- 📖 Error messages are clear and actionable
- 🔍 Documentation has working examples
- 🚀 Common tasks are simple and intuitive
- 🛡️ Security issues prevented, not just detected

---

## Risk Mitigation

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Infinite recursion in expansion | Medium | High | Depth limits, cycle detection in Stage 5 |
| Computation security vulnerabilities | Low | Critical | AST validation, whitelist approach in Stage 6 |
| Performance degradation | Medium | Medium | Caching, benchmarking in Stage 8 |
| Grammar conflicts | Medium | Medium | Incremental changes, extensive testing |

### Schedule Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Computation engine complexity | Medium | Medium | Allocate 2 weeks for Stage 6 |
| Parser integration issues | Low | High | Test integration early in Stage 9 |
| Test coverage gaps | Low | Medium | Continuous coverage monitoring |

---

## Handoff to Implementation

### For Claude AI Coder

When implementing each stage:

1. **Review the stage goals and deliverables** carefully
2. **Implement data structures first**, then logic
3. **Write tests before/alongside code** (TDD approach)
4. **Update Lark grammar incrementally** - test after each change
5. **Run all previous stage tests** to ensure no regression
6. **Document any deviations** from the plan with rationale
7. **Request clarification** if specifications are ambiguous

### Key Files to Create/Modify

New files to create:
- `mml/alias/models.py`
- `mml/alias/registry.py`
- `mml/alias/parser.py`
- `mml/alias/expander.py`
- `mml/alias/parameters.py`
- `mml/alias/computation.py`
- `mml/alias/conditionals.py`
- `mml/alias/imports.py`
- `mml/alias/analysis.py`
- `mml/alias/errors.py`
- `mml/alias/debug.py`

Existing files to modify:
- `mml/parser.py` (main parser integration)
- `mml/grammar.lark` (grammar extensions)

### Development Workflow

```
For each stage:
  1. Read stage specification
  2. Create/update data structures
  3. Implement core logic
  4. Extend Lark grammar
  5. Write tests
  6. Run all tests (current + previous stages)
  7. Document any API changes
  8. Commit with descriptive message
  9. Move to next stage
```
