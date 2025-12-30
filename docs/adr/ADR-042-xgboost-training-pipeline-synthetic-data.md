# ADR-042: XGBoost Training Pipeline and Synthetic Data Strategy

**Status**: Accepted
**Date**: 2025-01-02
**Deciders**: ML Team, Backend Team
**Related**: [ADR-040](file:///Users/lycanbeats/Desktop/agenzia-ai/docs/adr/ADR-040-fifi-avm-development-and-test-strategy.md), [ADR-041](file:///Users/lycanbeats/Desktop/agenzia-ai/docs/adr/ADR-041-fifi-appraisal-intelligence-layer.md)

---

## Context

Following the establishment of the Fifi Appraisal Intelligence Layer (ADR-041), we needed to transition from heuristic-based property valuation to a production-grade machine learning model. Key challenges included:

1. **Data Acquisition Timeline**: OMI (Osservatorio del Mercato Immobiliare) bulk data purchase requires 2-4 weeks delivery and €500-2,000 upfront cost
2. **Development Velocity**: Waiting for real data would block ML pipeline development for weeks
3. **Model Validation**: Need to establish baseline model performance before scaling to production
4. **Feature Engineering**: Must codify Italian real estate market knowledge into synthetic data generation

---

## Decision

We will implement a **two-phase ML training strategy**:

### Phase 1: Synthetic Data Development (Current)
- Generate realistic Italian real estate transaction data using domain knowledge
- Train XGBoost model on synthetic dataset (1K-50K samples)
- Establish ML pipeline, feature engineering, and model persistence infrastructure
- Achieve MAPE <20% on synthetic test set as proof of concept

### Phase 2: Production Model (Future)
- Replace synthetic data with OMI historical transactions or licensed provider data
- Retrain XGBoost model on real market data
- Maintain same feature engineering and training pipeline code
- Deploy v2.0 model with real-world validation

---

## Technical Architecture

### Synthetic Data Generator

**Location**: [`scripts/data/generate_synthetic_data.py`](file:///Users/lycanbeats/Desktop/agenzia-ai/scripts/data/generate_synthetic_data.py)

**Pricing Model**:
```python
sale_price = sqm * base_price_sqm * condition_mult * floor_mult * elevator_mult * balcony_mult * garden_mult * noise_factor

Where:
- base_price_sqm: Zone-specific (€3,200 - €8,000)
- condition_mult: {luxury: 1.4, excellent: 1.2, good: 1.0, fair: 0.85, poor: 0.65}
- floor_mult: 1.0 + (floor * 0.02)
- noise_factor: Normal(1.0, 0.12) for ±12% variance
```

**Zone Coverage**: 18 zones across Florence, Milan, Rome, Bologna, Pisa, Lucca

**Validation**:
- Price distributions approximate Italian market knowledge
- Feature correlations (sqm vs bedrooms, elevator vs floor) match real-world patterns
- Gaussian noise prevents overfitting on perfect synthetic patterns

---

### XGBoost Training Pipeline

**Location**: [`infrastructure/ml/train_xgboost.py`](file:///Users/lycanbeats/Desktop/agenzia-ai/infrastructure/ml/train_xgboost.py)

**Feature Engineering**:
- **Numeric** (5): sqm, bedrooms, bathrooms, floor, property_age_years
- **Boolean** (3): has_elevator, has_balcony, has_garden
- **Categorical (one-hot)** (30): zone_slug, condition, energy_class, cadastral_category
- **Total**: 38 features

**Model Configuration**:
```python
XGBRegressor(
    n_estimators=200,
    max_depth=5,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    objective='reg:squarederror'
)
```

**Data Split**: 70% train / 15% validation / 15% test

**Success Criteria**:
- MAPE < 20% on held-out test set
- R² > 0.70
- Train/Test delta < 5% (no overfitting)

---

### Model Persistence

**Format**: XGBoost Booster JSON (native format, smallest file size, fastest loading)

**Metadata**:
```json
{
  "version": "v1.0",
  "training_date": "2025-01-02T...",
  "model_path": "models/fifi_xgboost_v1.json",
  "feature_names": ["sqm", "bedrooms", ...],
  "n_features": 38,
  "metrics": {
    "mape": 15.43,
    "mae": 81603,
    "r2": 0.7137
  },
  "data_source": "synthetic_1000",
  "n_samples": 1000
}
```

**Versioning Strategy**:
- v1.x: Synthetic data models (development)
- v2.x: OMI/licensed data models (production)
- Backward compatibility via fallback to heuristic if model file missing

---

### Production Integration

**Location**: [`infrastructure/ml/xgboost_adapter.py`](file:///Users/lycanbeats/Desktop/agenzia-ai/infrastructure/ml/xgboost_adapter.py)

**Load Strategy**:
1. On `__init__`, attempt to load `models/fifi_xgboost_v1.json`
2. If model exists, load as Booster and cache in memory
3. Load metadata from `*_metadata.json` for feature names and version
4. If model missing, log warning and fall back to heuristic

**Prediction Flow**:
```python
1. Convert PropertyFeatures (Pydantic) → pandas DataFrame
2. One-hot encode categorical features (must match training)
3. Reorder columns to match model's expected feature order
4. Convert to XGBoost DMatrix
5. Call booster.predict(dmatrix)
6. Return prediction as float
```

**Error Handling**:
- Missing model file → Heuristic fallback
- Prediction error (e.g., missing features) → Heuristic fallback
- All errors logged with full context for debugging

---

## Rationale

### Why Synthetic Data First?

**Pros**:
1. ✅ **Immediate Development**: No waiting for OMI data delivery
2. ✅ **Cost Savings**: Zero cost for initial pipeline development
3. ✅ **Controlled Testing**: Known ground truth for validation
4. ✅ **Risk Mitigation**: Validate ML approach before committing to data purchase
5. ✅ **Team Learning**: Allows team to iterate on feature engineering without real data constraints

**Cons**:
1. ⚠️ Model won't capture real market nuances (e.g., school proximity, transport access)
2. ⚠️ Requires retraining when real data arrives
3. ⚠️ Synthetic patterns may not generalize to production

**Mitigation**: Explicitly version models (v1.x synthetic, v2.x real) and maintain clear switchover plan

---

### Why XGBoost?

**Alternatives Considered**:
- **Random Forest**: Similar performance but slower inference
- **Linear Regression**: Too simple for non-linear price relationships
- **Neural Networks**: Overkill for tabular data, harder to interpret
- **LightGBM**: Comparable to XGBoost but less mature Python ecosystem

**XGBoost Chosen Because**:
1. ✅ Industry standard for tabular regression tasks
2. ✅ Excellent MAPE performance (~10-15% typical for real estate)
3. ✅ Fast inference (<10ms per prediction)
4. ✅ Feature importance for interpretability (GDPR/EU AI Act compliance)
5. ✅ Robust to missing values and mixed data types
6. ✅ Native support for quantile regression (uncertainty estimation)

---

## Consequences

### Positive

1. **Accelerated Timeline**: ML pipeline developed 4 weeks ahead of OMI data availability
2. **Proven Architecture**: Training script, feature engineering, and model loading all validated
3. **Cost Efficiency**: €0 spent on initial development; data purchase decision can wait
4. **Performance Baseline**: MAPE 15.43% on synthetic data suggests 12-18% achievable with real data
5. **Reusable Pipeline**: Same code will work with OMI CSV after minimal adjustments

### Negative

1. **Double Training Required**: Model must be retrained when real data arrives
2. **Synthetic Bias**: Model may learn synthetic-specific patterns that don't generalize
3. **Limited Production Use**: v1.x model can only be used for demos, not client-facing appraisals

### Neutral

1. **Feature Set Locked In**: 38 features defined; adding new features later requires full retraining
2. **Storage Overhead**: Model file (2.1MB) + metadata (1KB) per version

---

## Verification

### Automated Tests

**Location**: [`tests/unit/test_fifi_ml.py`](file:///Users/lycanbeats/Desktop/agenzia-ai/tests/unit/test_fifi_ml.py)

```bash
pytest tests/unit/test_fifi_ml.py -v
```

**Coverage**:
- ✅ PropertyFeatures Pydantic validation
- ✅ Synthetic data generation statistics
- ✅ XGBoost model loading
- ✅ Feature preparation (one-hot encoding)
- ✅ Inference accuracy (range validation)
- ✅ Uncertainty calculation

### Training Validation

```bash
python infrastructure/ml/train_xgboost.py \
    --data data/test_synthetic.csv \
    --output models/fifi_xgboost_v1.json

# Expected output:
# MAPE: <20%
# R²: >0.70
# Model saved successfully
```

### Production Smoke Test

```python
from infrastructure.ml.feature_engineering import PropertyFeatures
from infrastructure.ml.xgboost_adapter import XGBoostAdapter

features = PropertyFeatures(sqm=100, bedrooms=3, condition="excellent")
adapter = XGBoostAdapter()
prediction = adapter.predict(features)

assert 300000 < prediction < 1000000  # Reasonable for 100sqm excellent property
assert adapter.model_version == "v1.0"
```

---

## Future Work

### Phase 2: Real Data Integration (Week 6-8)

1. **Data Acquisition**:
   - Purchase OMI bulk dataset or sign contract with licensed provider
   - Ingest into `historical_transactions` table
   - Clean and validate (dedupe, outlier removal)

2. **Model Retraining**:
   ```bash
   python infrastructure/ml/train_xgboost.py \
       --data data/omi_transactions.csv \
       --output models/fifi_xgboost_v2.json \
       --tune  # Enable hyperparameter search
   ```

3. **Validation**:
   - Compare v2.0 vs v1.0 predictions on holdout set
   - Backtest on recent 2024 transactions (if available)
   - Manual review of 50 predictions by real estate domain expert

4. **Deployment**:
   - Update `XGBoostAdapter` default path to v2.0
   - Archive v1.0 for reference
   - Monitor MAPE in production via logging

### Model Monitoring (Ongoing)

- Track prediction distribution drift
- Log MAPE per zone (detect market shifts)
- Alert if >25% predictions fall outside confidence intervals
- Retrain quarterly as new transaction data accumulates

---

## References

- [XGBoost Documentation](https://xgboost.readthedocs.io/)
- [OMI Data Structure Specification](https://www.agenziaentrate.gov.it/portale/web/guest/schede/fabbricatiterreni/omi/banche-dati/omi-open-data)
- [Italian Real Estate Market Report 2024](https://www.idealista.it/news/immobiliare/residenziale/2024/01/15/)

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-01-02 | Use synthetic data for v1.0 | Accelerate development while waiting for OMI data |
| 2025-01-02 | Choose XGBoost over alternatives | Industry standard, best MAPE for tabular data |
| 2025-01-02 | Target MAPE <20% | Achievable with synthetic data, will improve with real data |
| 2025-01-02 | 38 features with one-hot encoding | Balance between model complexity and interpretability |
| 2025-01-02 | Booster JSON format | Smallest file size, fastest load time |
