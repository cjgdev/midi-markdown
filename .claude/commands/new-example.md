---
description: Create a new MMD example file with proper template and frontmatter
---

Create a new MMD example file with proper structure. Ask the user:

1. **Example name** (e.g., "06_filter_automation")
2. **Category** (00_basics, 01_timing, 02_midi_features, 03_advanced, 04_device_libraries, 05_generative, 06_tutorials)
3. **Brief description** of what this example demonstrates
4. **Difficulty level** (beginner, intermediate, advanced)

Then create a properly structured MMD file in `examples/{category}/{name}.mmd` with:

- Complete frontmatter (title, author, midi_format, ppq, devices if needed)
- Header comment explaining what the example demonstrates
- Well-commented MMD code showing the feature
- Follow the style and structure of existing examples in that category
- Include inline comments explaining key concepts

After creating the file:
1. Validate it with `mmdc validate`
2. Compile it to verify correctness
3. Update `examples/README.md` to include the new example in the appropriate section

Reference existing examples in the target category for style consistency.
