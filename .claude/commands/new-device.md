---
description: Create a new device library file with proper template and aliases
---

Create a new device library file. Ask the user:

1. **Device name** (e.g., "Boss GT-1000")
2. **Manufacturer** name
3. **Default MIDI channel** (1-16)
4. **Documentation URL** (optional)
5. **List of key commands** they want to implement (presets, CC mappings, etc.)

Then create a device library file in `devices/{device_slug}.mmd` with:

- Complete frontmatter with device metadata
- Section comments organizing aliases by category
- Properly formatted @alias definitions with:
  - Clear parameter names and ranges
  - Descriptive documentation strings
  - Parameter types (int, note, percent, enum, etc.)
  - Default values where appropriate
  - Enum options for named parameters

**Alias naming convention:**
- Use device prefix: `{device}_command_name`
- Example: `cortex_preset`, `h90_mix`, `helix_snapshot`

**Common alias categories to include:**
- Preset/Program loading
- Scene/Snapshot switching
- Expression pedals
- Stomp switches
- Tempo control
- Effect parameters
- Routing/Mix controls

After creating the file:
1. Validate with `mmdc validate devices/{device_slug}.mmd`
2. Create a simple test example in `examples/04_device_libraries/` demonstrating the library
3. Update `docs/user-guide/device-libraries.md` to document the new device

Reference `devices/quad_cortex.mmd` and `devices/eventide_h90.mmd` for structure and style.
