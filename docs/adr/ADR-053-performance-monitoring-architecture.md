# ADR-053: Automatic Performance Monitoring Architecture

**Date**: 2026-01-03  
**Status**: Accepted  
**Decision Makers**: Development Team  

---

## Context

After implementing Phases 1-3 optimizations, we achieved significant performance improvements (91% faster). However, we had no systematic way to:
- Track performance over time
- Identify regressions early
- Understand real-world usage patterns
- Collect user feedback on quality

**Requirements**:
- Non-blocking: Logging must not slow down requests
- Comprehensive: Capture all relevant metrics
- Privacy-conscious: Respect user data
- Actionable: Enable data-driven decisions

---

## Decision

**We will implement automatic performance monitoring** with three components:

1. **Automatic Metric Logging** (`PerformanceMetricLogger`)
2. **User Feedback Collection** (5-star ratings + comments)
3. **Monitoring Dashboard** (Metabase/Grafana integration)

**Architecture**:
```
AppraisalService
  ├─> estimate_value()
  │    ├─> [Performance tracking starts]
  │    ├─> Local search / Perplexity
  │    ├─> Calculate metrics
  │    └─> [Log to Supabase] (non-blocking)
  │
  └─> Performance data flows to:
       ├─> appraisal_performance_metrics (automatic)
       ├─> appraisal_feedback (user-initiated)
       └─> mv_daily_performance_summary (aggregated)
```

---

## Rationale

**Why Automatic Logging**:
- ✅ **Zero manual effort**: Developers don't need to remember to log
- ✅ **Consistent data**: Every request is tracked
- ✅ **Historical analysis**: Enables trend detection
- ✅ **A/B testing ready**: Can compare before/after changes

**Why Non-Blocking**:
- ✅ **No performance impact**: Logging happens after response
- ✅ **Graceful degradation**: Failed logging doesn't fail requests
- ✅ **User experience priority**: Never slow down for metrics

**Alternatives Considered**:

1. **Manual Logging** (developers log key events)
   - ❌ Easy to forget
   - ❌ Inconsistent coverage
   - ✅ More control

2. **Third-Party APM** (New Relic, DataDog)
   - ✅ Professional dashboards
   - ❌ Monthly cost ($50-200+)
   - ❌ Data leaves our infrastructure

3. **Logs-Only** (parse application logs)
   - ✅ No extra code
   - ❌ Difficult to query
   - ❌ Not structured

4. **Client-Side Only** (track in browser)
   - ❌ Misses backend performance
   - ❌ Privacy concerns
   - ✅ Network timing included

---

## Implementation Details

### 1. Performance Metric Logger

**Captured Metrics**:
```python
{
    "city": str,              # Geographic area
    "zone": str,              # Neighborhood
    "response_time_ms": int,  # Total response time
    "used_local_search": bool, # Local vs external
    "used_perplexity": bool,  # Fallback indicator
    "comparables_found": int, # Data quality
    "confidence_level": int,  # Result confidence (0-100)
    "reliability_stars": int, # User-facing quality (1-5)
    "estimated_value": float, # Result value
    "user_phone": str,        # Link to user (optional)
    "user_email": str         # Link to user (optional)
}
```

**Integration**:
- Injected via dependency injection
- Called at end of `estimate_value()`
- Try/except wrapper (never fails requests)

### 2. User Feedback Form

**Design Principles**:
- **Simple**: 3 ratings + 1 optional text field
- **Beautiful**: Modern UI with animations
- **Fast**: <5 seconds to complete
- **Optional**: Never required

**Ratings**:
1. Overall satisfaction (1-5⭐)
2. Speed rating (1-5⭐)
3. Accuracy rating (1-5⭐)
4. Comments (optional, max 1000 chars)

### 3. Dashboard Integration

**Metrics Available**:
- p50, p90, p99 response times
- Local hit rate over time
- Confidence distribution
- Geographic performance breakdown
- User satisfaction trends

**Query Examples**:
```sql
-- Last 24 hours summary
SELECT * FROM get_performance_stats(24);

-- Daily aggregates
SELECT * FROM mv_daily_performance_summary
ORDER BY date DESC LIMIT 7;
```

---

## Consequences

**Positive**:
- ✅ **Data-driven optimization**: Know what to optimize next
- ✅ **Regression detection**: Catch performance drops immediately
- ✅ **User insights**: Understand satisfaction drivers
- ✅ **Geographic analysis**: Identify underperforming areas
- ✅ **ROI tracking**: Measure optimization impact

**Negative**:
- ⚠️ **Storage growth**: ~100KB/day at 100 requests/day
- ⚠️ **Privacy considerations**: Store user identifiers
- ⚠️ **Dashboard maintenance**: Requires periodic review

**Neutral**:
- 📊 **Requires discipline**: Dashboard must be checked regularly
- 📊 **Action required**: Metrics are useless without action

---

## Monitoring Strategy

**Key Metrics**:
1. **Response Time** (p50, p90, p99)
   - Target p50: <500ms
   - Alert if: p90 >2s

2. **Local Hit Rate**
   - Target: >80%
   - Alert if: <70%

3. **Confidence Level**
   - Target avg: >70%
   - Alert if: <60%

4. **User Satisfaction**
   - Target avg: >4.0/5
   - Alert if: <3.5/5

**Review Cadence**:
- **Real-time**: During deployments
- **Daily**: Morning performance review
- **Weekly**: Trend analysis
- **Monthly**: Strategic planning

---

## Privacy & Compliance

**Data Collected**:
- ✅ Performance metrics (necessary for service)
- ✅ User contact (optional, for linking)
- ⚠️ Property values (anonymized when possible)

**Retention**:
- Performance metrics: 1 year
- User feedback: Indefinite
- User identifiers: 90 days (or on request)

**Access Control**:
- RLS enabled on all tables
- Service role for writes
- Dashboard users: read-only via RPC

---

## Success Criteria

**Achieved**:
- [x] Automatic logging working: **Verified in Supabase**
- [x] Non-blocking operation: **No performance impact**
- [x] Feedback form deployed: **Live at /feedback.html**
- [x] Dashboard guide created: **MONITORING_DASHBOARD.md**

**Metrics After 24h** (to verify):
- [ ] >50 performance entries logged
- [ ] p50 response time <500ms maintained
- [ ] Local hit rate >80%
- [ ] >5 user feedback submissions

---

## Future Enhancements

1. **Anomaly Detection**: Automatically flag unusual patterns
2. **A/B Testing Framework**: Compare optimization strategies
3. **Cost Tracking**: Link to API costs (Perplexity, Mistral)
4. **Prediction**: Forecast performance under load
5. **User Segmentation**: Analyze by user type, geography

---

## References

- Implementation: `infrastructure/monitoring/performance_logger.py`
- Feedback API: `presentation/api/feedback.py`
- Feedback UI: `apps/landing-page/public/feedback.html`
- Dashboard guide: `docs/MONITORING_DASHBOARD.md`
- SQL schema: `docs/sql/20260103_phase3_optimization_indexes.sql`
- Related ADRs: ADR-051 (Local-First), ADR-052 (Database Indexing)
