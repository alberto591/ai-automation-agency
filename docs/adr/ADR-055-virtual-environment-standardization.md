# ADR-055: Virtual Environment Standardization

## Status
Accepted

## Date
2026-01-05

## Context
We encountered a critical failure in the API server where the process was hanging and utilizing high CPU. Upon investigation, we discovered that the server was running from a virtual environment located in a hidden, non-standard path (`.git/hide_from_vercel/bypass_upload/venv/`). This caused confusion, pathing errors, and made debugging difficult. To ensure the reliability of our Python environment and simplify developer workflows, we need a standardized approach to virtual environments.

## Decision
We enforce the use of a **standard, root-level `venv/` directory** for all local development and production Python environments.

**Requirements**:
1.  The virtual environment MUST be created as a directory named `venv` in the project root.
2.  This directory MUST be included in `.gitignore` to prevent committing dependencies or local binaries.
3.  All scripts and documentation shall assume the existence of `./venv/bin/python` or `./venv/bin/activate`.

## Consequences

**Positive**:
- **Predictability**: Developers and scripts always know where to find the python executable.
- **Cleanliness**: Prevents "venv-in-git" anti-patterns where OS-specific binaries are committed to the repo, breaking cross-platform compatibility.
- **Tooling Support**: IDEs (VS Code, PyCharm) automatically detect `venv` in the root.

**Negative**:
- **Setup Required**: A fresh checkout requires running `python -m venv venv` and `pip install -r requirements.txt`. (This is standard Python practice, so impact is minimal).

## Implementation
- Added `venv/` to `.gitignore`.
- Created fresh `venv` and re-installed dependencies.
