# Project Standards & Enforcement

This document outlines all standards and enforcement mechanisms for the Agenzia AI project.

## 🎯 Core Principles

### 1. Architecture
- **Hexagonal Architecture**: Strict separation of concerns
- **Ports & Adapters**: All external dependencies abstracted
- **Dependency Injection**: Composition root in `config/container.py`
- **SOLID Principles**: Every module follows SRP, OCP, LSP, ISP, DIP

### 2. Documentation
- **ADR Policy**: Every feature requires an Architectural Decision Record
- **Inline Documentation**: All public APIs documented with docstrings
- **Markdown Standards**: All docs in `docs/` with manifest tracking

### 3. Code Quality
- **Linting**: Enforced via `ruff` (configured in `pyproject.toml`)
- **Type Safety**: `mypy` in strict mode for all application code
- **Testing**: Unit tests required for domain logic; integration tests for adapters
- **Formatting**: Automatic with `ruff format`

## 🛠️ Enforcement Mechanisms

### Pre-Commit Hooks
Installed via `.pre-commit-config.yaml`:
- Trailing whitespace removal
- YAML/JSON/TOML validation
- Private key detection
- Ruff linting and formatting
- MyPy type checking

**Setup**: `pip install pre-commit && pre-commit install`

### Continuous Integration
GitHub Actions (`.github/workflows/ci.yml`):
- Runs on every push and PR
- Executes linting, type checking, and tests
- Caches dependencies for faster builds

### Dependency Management
Dependabot (`.github/dependabot.yml`):
- Weekly updates for Python and npm packages
- Monthly updates for GitHub Actions
- Automatic security patches

### Makefile Commands
Quick access to common tasks:
```bash
make install     # Full setup
make check-all   # Run all quality checks
make lint        # Lint only
make test        # Test only
```

## 📋 Contribution Workflow

1. **Planning**: Write ADR in `docs/adr/`
2. **Implementation**: Follow architectural patterns
3. **Quality**: Run `make check-all`
4. **Documentation**: Update relevant docs
5. **Testing**: Write and run tests
6. **PR**: Submit with ADR reference

## 🚨 Non-Negotiables

- ❌ No code without an ADR
- ❌ No commits that fail pre-commit hooks
- ❌ No tests in root or backend root directories
- ❌ No hardcoded secrets (use `.env`)
- ❌ No blocking sync calls in async paths
- ❌ No mock/fallback data to hide errors
- ❌ No duplicate models/classes

## 📊 Quality Metrics

We maintain:
- **Type Coverage**: >80% with mypy
- **Test Coverage**: >70% for critical paths
- **Lint Compliance**: 100% (enforced pre-commit)
- **ADR Coverage**: 100% for features

## 🔄 Review Process

All PRs require:
1. ADR approval (if applicable)
2. CI passing (green checks)
3. Code review from maintainer
4. No merge conflicts
5. Updated documentation

See `CONTRIBUTING.md` for detailed contribution guidelines.
