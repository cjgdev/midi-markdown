"""Benchmark parser performance.

Tests parsing speed for various file sizes to establish baselines
and prevent regressions.

Performance Targets:
- Small files (<100 events): <50ms
- Medium files (100-500 events): <200ms
- Large files (>1000 events): <1000ms

Run with:
    uv run pytest benchmarks/benchmark_parser.py -v
"""

from __future__ import annotations

import pytest

from midi_markdown.parser.parser import MMDParser


@pytest.mark.benchmark
class TestParserPerformance:
    """Parser performance benchmarks."""

    def test_parse_small_file_speed(self, benchmark, small_mmd_file):
        """Benchmark parsing small file (<100 events).

        Target: <50ms average parse time
        """
        parser = MMDParser()

        result = benchmark(parser.parse_file, str(small_mmd_file))

        # Verify parse succeeded
        assert result is not None
        assert len(result.events) > 0

        # Check performance (note: benchmark.stats available after run)
        # Small files should parse quickly

    def test_parse_medium_file_speed(self, benchmark, medium_mmd_file):
        """Benchmark parsing medium file (100-500 events).

        Target: <200ms average parse time
        """
        parser = MMDParser()

        result = benchmark(parser.parse_file, str(medium_mmd_file))

        # Verify parse succeeded
        assert result is not None
        assert len(result.events) > 0

    def test_parse_large_file_speed(self, benchmark, large_mmd_file):
        """Benchmark parsing large file (>1000 events).

        Target: <1000ms average parse time
        """
        parser = MMDParser()

        result = benchmark(parser.parse_file, str(large_mmd_file))

        # Verify parse succeeded
        assert result is not None
        assert len(result.events) > 0

    def test_parse_string_performance(self, benchmark):
        """Benchmark parsing from string (in-memory).

        This tests pure parser speed without file I/O overhead.
        """
        parser = MMDParser()

        # Create a moderately complex string inline
        mmd_content = """---
title: "Benchmark Test"
tempo: 120
ppq: 480
---

[00:00.000]
- tempo 120

@loop 50 times
  [+0.1s]
  - note_on 1.60.80 0.5s
  - cc 1.7.{i * 2}
@end
"""

        result = benchmark(parser.parse_string, mmd_content)

        assert result is not None
        assert len(result.events) > 0

    def test_parser_with_loops(self, benchmark):
        """Benchmark parser performance with loop constructs.

        Tests parser overhead for loop syntax.
        """
        parser = MMDParser()
        mml_content = """---
title: "Loop Benchmark"
tempo: 120
ppq: 480
---

[00:00.000]
@loop 100 times
  - note_on 1.60.80 0.1s
@end
"""

        result = benchmark(parser.parse_string, mml_content)

        assert result is not None
        # Should have 1 loop construct (not expanded yet)

    def test_parser_with_aliases(self, benchmark):
        """Benchmark parser performance with alias definitions.

        Tests parser overhead for alias syntax.
        """
        parser = MMDParser()
        mml_content = """---
title: "Alias Benchmark"
tempo: 120
ppq: 480
---

@alias test_alias {ch}.{note}.{vel}
  - note_on {ch}.{note}.{vel} 1b
@end

[00:00.000]
@loop 50 times
  - test_alias 1.60.80
@end
"""

        result = benchmark(parser.parse_string, mml_content)

        assert result is not None
        assert len(result.aliases) > 0


@pytest.mark.benchmark
class TestParserScalability:
    """Test parser scalability with increasing complexity."""

    def test_parse_many_channels(self, benchmark):
        """Benchmark parser with multi-channel content."""
        parser = MMDParser()

        # Generate content with all 16 MIDI channels
        lines = ["---", "title: Multi-Channel", "tempo: 120", "ppq: 480", "---", "", "[00:00.000]"]
        for ch in range(1, 17):
            lines.append(f"- note_on {ch}.60.80 1b")

        mml_content = "\n".join(lines)

        result = benchmark(parser.parse_string, mml_content)

        assert result is not None

    def test_parse_complex_timing(self, benchmark):
        """Benchmark parser with various timing formats."""
        parser = MMDParser()

        mml_content = """---
title: "Complex Timing"
tempo: 120
time_signature: "4/4"
ppq: 480
---

[00:00.000]
- note_on 1.60.80 1b

[00:01.500]
- cc 1.7.100

[+500ms]
- pc 1.5

[1.1.0]
- note_on 1.64.80 2b

[@]
- cc 1.10.50
"""

        result = benchmark(parser.parse_string, mml_content)

        assert result is not None

    def test_parse_with_comments(self, benchmark):
        """Benchmark parser with heavy comment usage."""
        parser = MMDParser()

        lines = ["---", "title: Comments", "tempo: 120", "ppq: 480", "---", ""]
        lines.append("# This is a comment")
        lines.append("/* Multi-line")
        lines.append("   comment block */")
        lines.append("[00:00.000]")

        for i in range(50):
            lines.append(f"# Comment line {i}")
            lines.append("- note_on 1.60.80 0.1s  # inline comment")

        mml_content = "\n".join(lines)

        result = benchmark(parser.parse_string, mml_content)

        assert result is not None
