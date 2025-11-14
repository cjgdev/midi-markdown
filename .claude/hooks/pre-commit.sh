#!/bin/bash
# Pre-commit hook: Run quality checks before git commit
# Ensures GitHub Actions will pass

set -e

echo "🔍 Running pre-commit quality checks..."
echo ""

echo "📝 Step 1/4: Checking code formatting..."
if ! uv run ruff format --check .; then
    echo "❌ Code formatting check failed!"
    echo "   Run: just fmt"
    exit 1
fi
echo "✅ Formatting OK"
echo ""

echo "🔎 Step 2/4: Running linter..."
if ! uv run ruff check src tests; then
    echo "❌ Linting failed!"
    echo "   Run: just lint-fix"
    exit 1
fi
echo "✅ Linting OK"
echo ""

echo "🔬 Step 3/4: Running type checker..."
if ! uv run mypy src; then
    echo "❌ Type checking failed!"
    echo "   Fix type errors before committing"
    exit 1
fi
echo "✅ Type checking OK"
echo ""

echo "🧪 Step 4/4: Running smoke tests (core functionality)..."
if ! uv run pytest tests/unit/test_document_structure.py tests/unit/test_timing.py tests/unit/test_midi_commands.py -v --tb=short -x; then
    echo "❌ Tests failed!"
    echo "   Run: just test-unit for full details"
    exit 1
fi
echo "✅ Tests OK"
echo ""

echo "✅ All pre-commit checks passed! Ready to commit."
