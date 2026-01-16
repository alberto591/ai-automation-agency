# ADR-011: CI Cost Optimization Strategy

- **Status**: Accepted
- **Date**: 2026-01-16
- **Decision Makers**: Engineering Team

## Context

On January 16, 2026, we discovered that GitHub Actions had consumed **1,336 minutes ($8.02)** in a single day due to:

1. **32 commits in 24 hours** - Each triggered a full CI run
2. **Heavy dependencies installed on every run** (~8-10 min each):
   - `xgboost` (compiles C++, ~500MB)
   - `scikit-learn` (compiles C++)
   - `langchain`, `langchain-mistralai`, `langgraph`
   - `numpy`, `pandas`, `openai`, `tiktoken`
3. **No path filtering** - CI ran even for docs/frontend changes
4. **No concurrency control** - Duplicate runs weren't cancelled

### Cost Breakdown

| Metric | Before | After (Expected) |
|--------|--------|------------------|
| Avg run time | ~40 min | ~2 min |
| Monthly runs | ~200 | ~200 |
| Monthly cost | **$48+** | **~$2.40** |

## Decision

Implement a **multi-layered CI optimization strategy**:

### 1. Path-Based Filtering

Only run CI when backend Python code changes:

```yaml
paths:
  - '**.py'
  - 'requirements*.txt'
  - 'pyproject.toml'
  - '.github/workflows/ci.yml'
```

**Skipped for:** Docs, frontend (apps/), static files, markdown

### 2. Lightweight CI Dependencies (`requirements-ci.txt`)

Created a minimal dependency file excluding heavy ML libraries:

```
# Included (fast to install)
fastapi, pydantic, supabase, httpx, pytest, etc.

# Excluded (heavy, mocked in tests)
xgboost, scikit-learn, numpy, pandas, langchain*, openai, tiktoken
```

### 3. Dependency Mocking in `tests/conftest.py`

Auto-mock heavy dependencies if not installed:

```python
heavy_modules = ["xgboost", "sklearn", "langchain", "numpy", "pandas", ...]

for mod in heavy_modules:
    try:
        __import__(mod)
    except ImportError:
        sys.modules[mod] = MagicMock()
```

### 4. Test Markers (`@pytest.mark.ml_required`)

Tests requiring real ML libraries are marked to skip in CI:

```python
@pytest.mark.ml_required
def test_xgboost_adapter_prediction():
    ...  # Skipped in CI, runs locally
```

Registered in `pyproject.toml`:
```toml
markers = ["ml_required: marks tests that require heavy ML libraries"]
```

### 5. Concurrency Control

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true  # Cancel stale runs
```

### 6. Split Jobs (Lint vs Test)

| Job | Trigger | Duration |
|-----|---------|----------|
| `lint` | Every push | ~1 min |
| `test` | PRs only | ~5 min |

## Consequences

### Positive

- **95% cost reduction** ($48/month → ~$2.40/month)
- **Faster feedback** (2 min vs 40 min)
- **Still validates** core API, auth, database logic
- **ML tests still run** locally with full dependencies

### Negative

- ML tests don't run in CI (acceptable trade-off)
- Must remember to run `pytest` locally before merging ML changes

### Risks

- If ML code breaks, we won't catch it in CI
- Mitigation: Run full tests locally, or add a scheduled nightly full-test job

## Files Changed

| File | Purpose |
|------|---------|
| `requirements-ci.txt` | Lightweight deps for CI |
| `tests/conftest.py` | Mock heavy deps if missing |
| `.github/workflows/ci.yml` | Path filters, split jobs, concurrency |
| `pyproject.toml` | Register `ml_required` marker |
| `tests/unit/test_fifi_ml.py` | Add `@pytest.mark.ml_required` |
| `tests/unit/test_model_registry.py` | Add `@pytest.mark.ml_required` |
| `tests/unit/test_synthetic_data_and_training.py` | Add `@pytest.mark.ml_required` |

## Verification

After deployment, monitor:
1. GitHub Actions billing page
2. Average CI run time
3. Test skip count in CI logs

## References

- Commit: `79c562a` - ci: optimize test speed by mocking heavy ML deps
- Commit: `2ca3858` - ci: dramatically reduce GitHub Actions costs
- GitHub Billing: https://github.com/settings/billing
