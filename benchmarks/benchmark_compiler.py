"""Benchmark IR compiler and code generation performance.

Tests compilation speed (AST → IR → MIDI) for various file sizes.

Performance Targets:
- AST → IR compilation: <100ms for medium files
- IR → MIDI generation: <100ms for medium files
- Full pipeline: <500ms for medium files

Run with:
    uv run pytest benchmarks/benchmark_compiler.py -v
"""

from __future__ import annotations

import pytest

from midi_markdown.codegen.csv_export import export_to_csv
from midi_markdown.codegen.json_export import export_to_json
from midi_markdown.codegen.midi_file import generate_midi_file
from midi_markdown.core.compiler import compile_ast_to_ir


@pytest.mark.benchmark
class TestCompilerPerformance:
    """IR compiler performance benchmarks."""

    def test_compile_small_to_ir(self, benchmark, parsed_small_document):
        """Benchmark AST → IR compilation for small file.

        Target: <50ms
        """
        result = benchmark(compile_ast_to_ir, parsed_small_document, ppq=480)

        assert result is not None
        assert len(result.events) > 0

    def test_compile_medium_to_ir(self, benchmark, parsed_medium_document):
        """Benchmark AST → IR compilation for medium file.

        Target: <100ms
        """
        result = benchmark(compile_ast_to_ir, parsed_medium_document, ppq=480)

        assert result is not None
        assert len(result.events) > 0

    def test_compile_large_to_ir(self, benchmark, parsed_large_document):
        """Benchmark AST → IR compilation for large file.

        Target: <500ms
        """
        result = benchmark(compile_ast_to_ir, parsed_large_document, ppq=480)

        assert result is not None
        assert len(result.events) > 0


@pytest.mark.benchmark
class TestCodegenPerformance:
    """Code generation performance benchmarks."""

    def test_generate_midi_file_small(self, benchmark, small_ir_program):
        """Benchmark IR → MIDI file generation for small program.

        Target: <50ms
        """
        result = benchmark(generate_midi_file, small_ir_program)

        assert result is not None
        assert len(result) > 0  # Should have MIDI bytes

    def test_generate_midi_file_medium(self, benchmark, medium_ir_program):
        """Benchmark IR → MIDI file generation for medium program.

        Target: <100ms
        """
        result = benchmark(generate_midi_file, medium_ir_program)

        assert result is not None
        assert len(result) > 0

    def test_generate_midi_file_large(self, benchmark, large_ir_program):
        """Benchmark IR → MIDI file generation for large program.

        Target: <500ms
        """
        result = benchmark(generate_midi_file, large_ir_program)

        assert result is not None
        assert len(result) > 0

    def test_generate_csv_export(self, benchmark, medium_ir_program):
        """Benchmark CSV export generation.

        Target: <100ms
        """
        result = benchmark(export_to_csv, medium_ir_program, include_header=True)

        assert result is not None
        assert len(result) > 0

    def test_generate_json_export(self, benchmark, medium_ir_program):
        """Benchmark JSON export generation.

        Target: <100ms
        """
        result = benchmark(export_to_json, medium_ir_program, simplified=False)

        assert result is not None
        assert len(result) > 0

    def test_generate_json_simplified_export(self, benchmark, medium_ir_program):
        """Benchmark simplified JSON export generation.

        Target: <100ms
        """
        result = benchmark(export_to_json, medium_ir_program, simplified=True)

        assert result is not None
        assert len(result) > 0


@pytest.mark.benchmark
class TestFullPipeline:
    """End-to-end pipeline performance benchmarks."""

    def test_full_pipeline_small(self, benchmark, small_mmd_file):
        """Benchmark full pipeline: Parse → Compile → Generate MIDI.

        Target: <200ms for small files
        """
        from midi_markdown.parser.parser import MMDParser

        def full_pipeline():
            parser = MMDParser()
            ast = parser.parse_file(str(small_mmd_file))
            ir = compile_ast_to_ir(ast, ppq=480)
            return generate_midi_file(ir)

        result = benchmark(full_pipeline)

        assert result is not None
        assert len(result) > 0

    def test_full_pipeline_medium(self, benchmark, medium_mmd_file):
        """Benchmark full pipeline for medium file.

        Target: <500ms
        """
        from midi_markdown.parser.parser import MMDParser

        def full_pipeline():
            parser = MMDParser()
            ast = parser.parse_file(str(medium_mmd_file))
            ir = compile_ast_to_ir(ast, ppq=480)
            return generate_midi_file(ir)

        result = benchmark(full_pipeline)

        assert result is not None
        assert len(result) > 0

    def test_full_pipeline_large(self, benchmark, large_mmd_file):
        """Benchmark full pipeline for large file.

        Target: <2000ms (2 seconds)
        """
        from midi_markdown.parser.parser import MMDParser

        def full_pipeline():
            parser = MMDParser()
            ast = parser.parse_file(str(large_mmd_file))
            ir = compile_ast_to_ir(ast, ppq=480)
            return generate_midi_file(ir)

        result = benchmark(full_pipeline)

        assert result is not None
        assert len(result) > 0


@pytest.mark.benchmark
class TestCompilerScalability:
    """Test compiler scalability with complex features."""

    def test_compile_with_many_tracks(self, benchmark):
        """Benchmark compilation with multiple tracks."""
        from midi_markdown.parser.parser import MMDParser

        mml_content = """---
title: "Multi-Track"
tempo: 120
ppq: 480
---

"""
        # Add 10 tracks
        for track_num in range(1, 11):
            mml_content += f"""
@track Track{track_num} channel={track_num}
  [00:00.000]
  @loop 10 times
    - note_on {track_num}.60.80 1b
  @end
@end
"""

        parser = MMDParser()
        ast = parser.parse_string(mml_content)

        result = benchmark(compile_ast_to_ir, ast, ppq=480)

        assert result is not None

    def test_compile_with_many_aliases(self, benchmark):
        """Benchmark compilation with heavy alias usage."""
        from midi_markdown.parser.parser import MMDParser

        mml_content = """---
title: "Alias Heavy"
tempo: 120
ppq: 480
---

@alias simple_note {ch}.{note}
  - note_on {ch}.{note}.80 1b
@end

[00:00.000]
@loop 100 times
  - simple_note 1.60
@end
"""

        parser = MMDParser()
        ast = parser.parse_string(mml_content)

        result = benchmark(compile_ast_to_ir, ast, ppq=480)

        assert result is not None

    def test_compile_with_sweeps(self, benchmark):
        """Benchmark compilation with sweep automation."""
        from midi_markdown.parser.parser import MMDParser

        mml_content = """---
title: "Sweep Test"
tempo: 120
ppq: 480
---

[00:00.000]
@sweep 200 from 0 to 127 over 20b
  - cc 1.7.{value}
@end
"""

        parser = MMDParser()
        ast = parser.parse_string(mml_content)

        result = benchmark(compile_ast_to_ir, ast, ppq=480)

        assert result is not None
        assert len(result.events) >= 200  # Should have generated sweep events
