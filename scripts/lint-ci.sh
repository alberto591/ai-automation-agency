#!/bin/bash
# Run the same linting checks as GitHub Actions CI

set -e

echo "🔍 Running Ruff linting (same as GitHub Actions)..."
echo ""

# Add pipx bin to PATH if needed
export PATH="$HOME/.local/bin:$PATH"

# Run ruff check on Python files
ruff check . --output-format=github

echo ""
echo "✅ Linting passed! Your code is ready for CI."
