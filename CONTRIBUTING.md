# Contributing to Agenzia AI

## Development Standards

### 1. Code Quality Standards
- **Linting**: All code must pass `ruff check .`
- **Formatting**: Use `ruff format .` before committing
- **Type Checking**: Run `mypy` on your changes (configured in `pyproject.toml`)
- **Line Length**: Maximum 100 characters (enforced by ruff)

### 2. Architectural Decision Records (ADRs)
> [!IMPORTANT]
> Every new feature or architectural change **MUST** have a corresponding ADR.

See `docs/adr/template.md` for the format. Your PR will be rejected without an ADR.

### 3. Pre-Commit Hooks
Install pre-commit hooks to catch issues before committing:
```bash
pip install pre-commit
pre-commit install
```

### 4. Testing Requirements
- Unit tests for all business logic in `domain/` and `application/`
- Integration tests for adapters in `infrastructure/`
- All tests must be in `tests/` or `test_scripts/` (NOT in root or `backend/`)

### 5. Documentation Requirements
- Update `docs/README.md` if adding new features
- Document all environment variables in `.env.example`
- Add inline docstrings for public functions and classes

### 6. Commit Message Format
Follow Conventional Commits:
```
feat: Add real-time market data integration
fix: Resolve race condition in lead processor
docs: Update ADR for appraisal tool
refactor: Extract market adapter logic
```

### 7. Pull Request Process
1. Create a feature branch: `git checkout -b feat/your-feature`
2. Write your ADR in `docs/adr/`
3. Implement your feature following SOLID principles
4. Run tests: `pytest tests/`
5. Run linters: `ruff check . && mypy .`
6. Commit with conventional commits
7. Open PR with ADR link in description

### 8. File Organization
- **No tests in root**: Use `tests/` or `test_scripts/`
- **No docs in root**: Use `docs/` with manifest
- **Scripts naming**: `{action}_{target}_{qualifier}.py`
- **Markdown naming**: `{YYYY-MM-DD}_{slug}.md`

### 9. Deployment Verification
After pushing to `master`, you must verify the deployment status:
```bash
make check-deploy
```
This script checks:
- GitHub Actions (Lint, Test)
- Vercel Deployment Status (via links)

**Note:** You need `GITHUB_TOKEN` set in your environment for this command to work.

## Architecture Principles
- **Hexagonal Architecture**: Domain must not import from infrastructure
- **Dependency Injection**: Use `config/container.py` as composition root
- **Ports and Adapters**: All external integrations via ports
- **SOLID Principles**: Single responsibility, Open/Closed, LSP, ISP, DIP

## Questions?
See `docs/README.md` or the user rules in the codebase.
