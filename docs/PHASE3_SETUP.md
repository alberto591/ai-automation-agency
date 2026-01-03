# Phase 3 Optimization & Monitoring Setup Guide

**Date**: 2026-01-03  
**Purpose**: Database indexes and performance monitoring setup

---

## Quick Start

### 1. Apply Database Indexes

**Via Supabase Dashboard**:
1. Go to: https://supabase.com/dashboard → SQL Editor
2. Copy contents of `docs/sql/20260103_phase3_optimization_indexes.sql`
3. Execute the SQL script
4. Verify indexes created:
   ```sql
   SELECT tablename, indexname 
   FROM pg_indexes 
   WHERE tablename = 'properties'
   ORDER BY indexname;
   ```

**Expected Impact**:
- Query time: 0.7s → **0.2-0.3s** (60% faster)
- Total appraisal time: 0.90s → **0.5-0.6s** 

---

## Phase 3 Components

### A. Database Indexes

**Created Indexes**:
1. `idx_properties_description_fts` - Full-text search (Italian)
2. `idx_properties_price` - Price range queries
3. `idx_properties_sqm` - Size range queries
4. `idx_properties_price_sqm` - Composite index
5. `idx_properties_image_url` - Deduplication (unique)

**Performance Tables**:
- `appraisal_performance_metrics` - Real-time performance tracking
- `appraisal_feedback` - User feedback collection
- `mv_daily_performance_summary` - Aggregated daily stats

### B. Performance Monitoring

**Automatic Logging**:
- Response times (p50, p90, p99)
- Local search hit rate
- Perplexity fallback rate
- Confidence levels
- Comparables found

**Dashboard Queries**:
```sql
-- Last 24 hours performance
SELECT * FROM get_performance_stats(24);

-- Daily summary
SELECT * FROM mv_daily_performance_summary 
ORDER BY date DESC 
LIMIT 7;
```

### C. User Feedback Collection

**Feedback Form** (to be added to UI):
- Overall rating (1-5 stars)
- Speed rating (1-5)
- Accuracy rating (1-5)
- Optional text feedback

**Integration**: Add to appraisal result page

---

## Implementation Checklist

### Database Setup ✅
- [ ] Execute SQL migration script
- [ ] Verify indexes created
- [ ] Test index performance
- [ ] Grant RLS permissions

### Code Integration ⏭️
- [ ] Import `PerformanceMetricLogger` in appraisal service
- [ ] Add performance tracking to estimate_value
- [ ] Test metric logging
- [ ] Verify data appears in Supabase

### Monitoring Dashboard ⏭️
- [ ] Create Grafana/Metabase dashboard
- [ ] Configure alerting thresholds
- [ ] Set up daily refresh of materialized views
- [ ] Share dashboard with team

### User Feedback ⏭️
- [ ] Add feedback form to appraisal UI
- [ ] Link feedback to appraisal requests
- [ ] Create admin view for feedback review
- [ ] Set up weekly feedback reports

---

## Monitoring Metrics

### Key Performance Indicators

**Response Time**:
- Target p50: <600ms (with indexes)
- Target p90: <1.5s
- Target p99: <3s

**Local Hit Rate**:
- Target: >80%
- Alert if: <70%

**Confidence**:
- Target avg: >70%
- Alert if: <60%

**User Satisfaction**:
- Target rating: >4.0/5
- Target speed rating: >4.2/5

---

## Testing the Optimization

### Before vs After Comparison

**Test Query**:
```python
# Run this test before and after applying indexes
import time
from config.container import container

start = time.time()
result = container.local_property_search.search_local_comparables(
    city="Milano",
    zone="Centro",
    property_type="apartment",
    surface_sqm=95,
    min_comparables=3
)
elapsed = (time.time() - start) * 1000
print(f"Query time: {elapsed:.0f}ms")
print(f"Results: {len(result)}")
```

**Expected Results**:
- Before: 700-900ms
- After: 200-350ms
- Improvement: ~60%

---

## Rollback Plan

If indexes cause issues:

```sql
-- Drop indexes
DROP INDEX IF EXISTS idx_properties_description_fts;
DROP INDEX IF EXISTS idx_properties_price;
DROP INDEX IF EXISTS idx_properties_sqm;
DROP INDEX IF EXISTS idx_properties_price_sqm;

-- Keep unique constraint
-- DROP INDEX idx_properties_image_url;  -- Don't drop this
```

---

## Next Steps

1. **Apply indexes** via Supabase Dashboard
2. **Test performance** improvement
3. **Integrate performance logger** in code
4. **Set up monitoring dashboard**
5. **Add feedback form** to UI
6. **Monitor for 48 hours** and adjust

---

*Setup time: ~30 minutes*  
*Expected impact: 60% faster queries, comprehensive monitoring*
