"""Performance benchmarks for MIDI Markdown Language.

This package contains performance benchmarks to establish baselines
and prevent regressions.

Benchmark Categories:
- Parser: Parsing speed for various file sizes
- Compiler: IR compilation and MIDI generation speed
- Scheduler: Timing accuracy and latency
- CLI: Startup time and command execution speed

Run benchmarks with:
    uv run pytest benchmarks/ -v

Run specific benchmark:
    uv run pytest benchmarks/benchmark_parser.py -v

Skip benchmarks in regular tests:
    uv run pytest -m "not benchmark"
"""
