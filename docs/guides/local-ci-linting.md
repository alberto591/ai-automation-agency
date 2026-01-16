# Local CI Linting Guide

## Quick Start

Run the same linting checks as GitHub Actions locally:

```bash
./scripts/lint-ci.sh
```

## What It Does

This script runs **Ruff** linting on all Python files, exactly as GitHub Actions CI does.

## Requirements

- **Ruff** must be installed (already done via `pipx install ruff`)
- Add to PATH: `export PATH="$HOME/.local/bin:$PATH"` (or run `pipx ensurepath`)

## Manual Commands

If you prefer to run ruff directly:

```bash
# Check all Python files
ruff check .

# Auto-fix issues
ruff check . --fix

# Format code
ruff format .
```

## CI Workflow Alignment

This matches the **lint** job in [`.github/workflows/ci.yml`](file:///Users/lycanbeats/Desktop/agenzia-ai/.github/workflows/ci.yml):

```yaml
- name: Lint with Ruff
  run: ruff check . --output-format=github
```

## Common Issues

**Import order errors (I001):**
- Standard library imports first
- Third-party imports second
- Local imports last

**Module import not at top (E402):**
- Move imports to the top of the file
- Exception: imports after conditional mocking logic

## Pre-Commit Hook (Optional)

Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
./scripts/lint-ci.sh
```

Then: `chmod +x .git/hooks/pre-commit`
