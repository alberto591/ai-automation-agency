# Fifi Database Migration Guide

**Date**: 2026-01-01
**Purpose**: Set up database schema for Fifi AI Appraisal ML training

---

## Step 1: Apply Foundation Migration

### Via Supabase Dashboard (Recommended)

1. **Open Supabase Dashboard**
   - Go to: https://app.supabase.com/project/YOUR_PROJECT_ID/sql
   - Or navigate to: Project → SQL Editor

2. **Run Foundation Migration**
   - Copy contents of: `scripts/migrations/20251230_fifi_avm_foundation.sql`
   - Paste into SQL Editor
   - Click "Run" or press `Cmd+Enter`

3. **Verify Tables Created**
   ```sql
   SELECT table_name
   FROM information_schema.tables
   WHERE table_schema = 'public'
   AND table_name LIKE '%transaction%' OR table_name LIKE '%appraisal%';
   ```

   Expected tables:
   - ✅ `historical_transactions`
   - ✅ `property_features_stats`
   - ✅ `appraisal_validations`

---

## Step 2: Load Mock Transaction Data

### Upload Mock Data (500 transactions)

1. **Copy Mock Data SQL**
   - File: `scripts/migrations/mock_data_insert.sql`
   - Size: ~500 INSERT statements

2. **Execute in Supabase**
   - Paste into SQL Editor
   - Run the INSERT statements
   - Wait for completion (~5-10 seconds)

3. **Verify Data Loaded**
   ```sql
   SELECT COUNT(*) as total_transactions FROM historical_transactions;
   -- Expected: 500

   SELECT
       zone,
       COUNT(*) as count,
       AVG(sale_price_eur) as avg_price,
       AVG(price_per_sqm_eur) as avg_sqm_price
   FROM historical_transactions
   GROUP BY zone
   ORDER BY count DESC;
   ```

---

## Step 3: Validate Data Quality

### Check Data Distribution

```sql
-- Price distribution by zone
SELECT
    zone,
    MIN(sale_price_eur) as min_price,
    AVG(sale_price_eur) as avg_price,
    MAX(sale_price_eur) as max_price,
    COUNT(*) as properties
FROM historical_transactions
GROUP BY zone;

-- Condition distribution
SELECT
    condition,
    COUNT(*) as count,
    AVG(price_per_sqm_eur) as avg_sqm_price
FROM historical_transactions
GROUP BY condition
ORDER BY count DESC;

-- Recent transactions (last 30 days)
SELECT COUNT(*) as recent_count
FROM historical_transactions
WHERE sale_date >= CURRENT_DATE - INTERVAL '30 days';
```

---

## Step 4: Test ML Pipeline (Optional)

### Feature Engineering Test

```python
# Test if feature engineering works with new data
from infrastructure.ml.feature_engineering import prepare_features

# This will query historical_transactions
features = prepare_features(zone="Florence-Centro", limit=50)
print(f"Features prepared: {len(features)} rows")
```

### Model Training Test

```python
# Quick training test
from infrastructure.ml.train_xgboost import train_model

# Train on mock data
model = train_model(
    min_samples=100,  # We have 500
    test_size=0.2
)
print(f"Model trained with MAPE: {model.metrics['mape']}")
```

---

## Troubleshooting

### Migration Fails
- **Error**: "relation already exists"
  - **Solution**: Tables already created, skip foundation migration

- **Error**: "permission denied"
  - **Solution**: Ensure you're using project owner/admin account

### Data Upload Issues
- **Error**: "duplicate key value"
  - **Solution**: Data already uploaded, clear table first:
    ```sql
    TRUNCATE TABLE historical_transactions CASCADE;
    ```

- **Slow execution**
  - **Solution**: Upload in batches of 100 rows at a time

---

## Next Steps After Migration

1. ✅ **Verify** all 500 transactions loaded
2. 📊 **Analyze** data distribution and quality
3. 🤖 **Train** initial XGBoost model
4. 📈 **Test** appraisal predictions
5. 🎯 **Monitor** MAPE and accuracy metrics

---

## Quick Reference

**Migration Files**:
- Foundation: `scripts/migrations/20251230_fifi_avm_foundation.sql`
- Mock Data: `scripts/migrations/mock_data_insert.sql`

**Verification Queries**:
```sql
-- Row count
SELECT COUNT(*) FROM historical_transactions;

-- Sample data
SELECT * FROM historical_transactions LIMIT 5;

-- Stats by zone
SELECT zone, COUNT(*), AVG(sale_price_eur)
FROM historical_transactions
GROUP BY zone;
```
