---
description: Guide for adding a new MIDI command type to the MMD language
---

Guide the developer through adding a new MIDI command type. This is a multi-step process that touches several parts of the codebase.

Ask the user:
1. **Command name** (e.g., "note_pressure", "song_select")
2. **MIDI message type** (channel voice, system common, system realtime, meta)
3. **Parameters** needed (channel, data1, data2, etc.)
4. **Value ranges** for each parameter

Then implement the following steps:

## Step 1: Update Grammar (parser/mml.lark)

Add the command to the grammar rules:
- Update `command_name` rule with new command name
- Add alias if needed (e.g., `note_on | "non"`)

## Step 2: Update Transformer (parser/transformer.py)

Add transformation logic in `MMLTransformer`:
- Handle the new command in `midi_command()` method
- Extract parameters correctly
- Check for forward references using `isinstance(value, tuple)`
- Return proper command dictionary with type, channel, data

## Step 3: Update Validation (utils/validation/)

Add validation for the new command:
- Update `value_validator.py` to check parameter ranges
- Add specific validation function if needed
- Update `document_validator.py` to call new validator

## Step 4: Update IR Compiler (core/compiler.py)

Add IR event type if needed:
- Update `EventType` enum if new event type required
- Handle conversion from AST to IR in `compile_ast_to_ir()`

## Step 5: Update Codegen (codegen/midi_file.py)

Add MIDI file generation:
- Handle new event type in `generate_midi_file()`
- Use appropriate `mido.Message()` type
- Map parameters correctly to MIDI bytes

## Step 6: Write Tests

Create comprehensive tests:
- Unit test in `tests/unit/test_parser.py` for parsing
- Unit test in `tests/unit/test_transformer.py` for transformation
- Integration test in `tests/integration/` for end-to-end
- Test validation edge cases (min/max values)

## Step 7: Update Documentation

Document the new command:
- Add to `spec.md` under appropriate section
- Add example to `examples/02_midi_features/`
- Update any relevant user guides

## Critical Rules to Follow:

✅ **Use abbreviated command types** in code (e.g., "cc" not "control_change")
✅ **Check `isinstance(value, tuple)` before `int()` conversion** for forward references
✅ **Add descriptive error messages** with proper source location tracking
✅ **Follow existing patterns** - reference similar commands (e.g., for CC, look at existing CC implementation)

Reference files:
- `docs/dev-guides/parser-patterns.md` - Parser implementation patterns
- `docs/dev-guides/anti-patterns.md` - Common mistakes to avoid
- `docs/dev-guides/common-tasks.md` - Step-by-step workflows

After implementation:
1. Run `just test` to verify all tests pass
2. Run `just check` for linting and type checking
3. Create an example demonstrating the new command
4. Test the example end-to-end compilation
