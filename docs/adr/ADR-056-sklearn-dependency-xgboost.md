# ADR-056: Scikit-learn Dependency for XGBoost Integration

**Status**: Accepted
**Date**: 2026-01-05
**Decision Makers**: Development Team

## Context

The CI pipeline was failing with `ImportError: sklearn needs to be installed in order to use this module` when running tests that use XGBoost's sklearn-compatible interface (`XGBRegressor`). The tests in `test_model_registry.py` and `test_synthetic_data_and_training.py` were affected.

## Decision

Add `scikit-learn>=1.4.0` as a dependency in `requirements.txt` to support:
1. XGBoost's sklearn-compatible estimator interface
2. ML training pipeline metrics (`mean_absolute_error`, `mean_absolute_percentage_error`, `r2_score`)
3. Model validation and cross-validation utilities

## Consequences

### Positive
- CI tests now pass for all XGBoost-related functionality
- Enables full use of XGBoost's sklearn API for model training
- Provides access to sklearn's comprehensive metrics library

### Negative
- Adds ~50MB to the dependency footprint
- Potential version conflicts with other ML libraries (mitigated by version pinning)

## Implementation

```diff
# requirements.txt
+ scikit-learn>=1.4.0
```

Commit: `db9951d`
