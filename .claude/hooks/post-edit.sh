#!/bin/bash
# Post-edit hook: Auto-format Python files
# This runs after Claude edits a file

set -e

FILE="$1"

# Only format Python files
if [[ "$FILE" == *.py ]]; then
    echo "🔧 Auto-formatting $FILE..."
    uv run ruff format "$FILE"
    echo "✅ Formatted $FILE"
fi
