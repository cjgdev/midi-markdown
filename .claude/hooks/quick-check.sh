#!/bin/bash
# Quick check hook: Fast validation after file changes
# Runs format + lint on changed files only

set -e

FILE="$1"

if [[ "$FILE" == *.py ]]; then
    echo "🔍 Quick check: $FILE"

    # Format the file
    uv run ruff format "$FILE"

    # Lint the file
    if ! uv run ruff check "$FILE"; then
        echo "⚠️  Linting issues in $FILE - attempting auto-fix..."
        uv run ruff check --fix "$FILE"
    fi

    echo "✅ Quick check passed"
fi
