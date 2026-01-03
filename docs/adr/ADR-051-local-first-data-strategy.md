# ADR-051: Local-First Data Strategy for Property Appraisals

**Date**: 2026-01-03  
**Status**: Accepted  
**Decision Makers**: Development Team  

---

## Context

The property appraisal system was experiencing slow response times (5-8 seconds) due to reliance on external APIs (Perplexity) for finding comparable properties. Each appraisal required:
- External API call to Perplexity search (~3.5-4.2s)
- LLM parsing with Mistral (~1.5-2.5s)
- Investment calculations (~0.5s)

With 243 properties collected in our Supabase database covering Milano, Firenze, and Chianti, we needed to decide whether to continue relying solely on external APIs or leverage our local data.

**Constraints**:
- Target response time: <1 second for Milano queries
- Cost optimization required (reduce API expenses)
- Must maintain or improve confidence levels
- Geographic coverage limited to collected areas

---

## Decision

**We will implement a local-first data strategy** where the appraisal service prioritizes searching the local Supabase database before falling back to external APIs.

**Implementation**:
1. Create `LocalPropertySearchService` to query local database
2. Modify `AppraisalService` to try local search first
3. Fall back to Perplexity only if <3 local comparables found
4. Use dependency injection to make this behavior configurable

---

## Rationale

**Pros**:
- **85% faster** for Milano queries (0.9s vs 5-8s)
- **100% cost reduction** when local data is sufficient
- **Better comparables**: Real scraped data vs AI-summarized research
- **Offline capability**: System works even if external APIs are down
- **Scalable**: Performance improves as we collect more data

**Cons**:
- Only works for geographic areas with collected data (Milano, Firenze, Chianti)
- Requires active data collection process
- Database query overhead (though minimal with proper indexing)

**Alternatives Considered**:

1. **Continue External-Only**
   - ❌ Slow (5-8s)
   - ❌ Expensive ($0.007/request)
   - ✅ Works for any location

2. **Cache Perplexity Results**
   - ✅ Faster on cache hits
   - ❌ Cache misses still slow
   - ❌ Stale data concerns
   - ❌ Still costs money on misses

3. **Hybrid with 50/50 Split**
   - ❌ Unpredictable performance
   - ❌ Complex logic
   - ❌ Doesn't maximize local data value

---

## Implementation Details

**Search Criteria**:
- City/zone matching (via description ILIKE)
- Size range: ±30% of target property
- Price sanity check: €500-€15,000/sqm
- Minimum 3 comparables required

**Fallback Logic**:
```python
if local_comparables and len(local_comparables) >= 3:
    return local_comparables
else:
    # Fall back to Perplexity
    return perplexity_search()
```

---

## Consequences

**Positive**:
- ✅ **Dramatic performance improvement**: 85% faster (5-8s → 0.9s)
- ✅ **Cost savings**: 100% for Milano queries
- ✅ **Improved confidence**: 75% (4⭐) vs 50% (2⭐)
- ✅ **More comparables**: 3 vs 1-2
- ✅ **Foundation for further optimization**: Enables semantic search, ML models

**Negative**:
- ⚠️ **Geographic limitation**: Only works where we have data
- ⚠️ **Data freshness**: Requires ongoing collection
- ⚠️ **Maintenance burden**: Dataset needs curation

**Neutral**:
- 📊 **Monitoring required**: Track local hit rate
- 📊 **Data collection required**: Expand to Rome, Venice, Naples

---

## Metrics & Validation

**Success Criteria** (all achieved):
- [x] Response time <1s for Milano: **Achieved 0.9s**
- [x] Confidence >70%: **Achieved 75%**
- [x] Cost reduction >80%: **Achieved 100%**
- [x] Local hit rate >80%: **Achieved 100%** for Milano

**Actual Results**:
- Response time: **0.9s** (85% improvement)
- Confidence: **75%** (4⭐, +50%)
- Cost: **$0** (100% savings)
- Comparables: **3** (consistent quality)

---

## Future Considerations

1. **Expand Data Collection**: Target 500+ properties with Rome, Venice, Naples
2. **Semantic Search**: Vector embeddings for better matching (ADR-050 integration)
3. **ML Valuation**: Use collected data to train valuation model
4. **Real-time Updates**: Scrape new listings daily
5. **Quality Signals**: Track which comparables produce accurate valuations

---

## References

- Performance test results: `final_phase3_test_results.md`
- Implementation: `application/services/local_property_search.py`
- Container integration: `config/container.py`
- Related ADRs: ADR-050 (Semantic Search), ADR-052 (Database Indexing)
