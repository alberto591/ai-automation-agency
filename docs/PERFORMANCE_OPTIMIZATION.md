# Performance Optimization Analysis

**Date**: 2026-01-03
**Current Performance**: 5-8s API response time
**Target**: <3s for optimal UX

---

## Executive Summary

The appraisal API currently takes 5-8 seconds to respond, primarily due to:
1. **Perplexity AI Search**: 3.5-4.2s (external API call)
2. **Mistral LLM Parsing**: 1.5-2.5s (JSON extraction from text)
3. **Investment Calculations**: <0.5s (negligible)

**Quick Win Opportunities**: Caching, parallel processing, and query optimization can reduce response time to 2-3s.

---

## Current Performance Baseline

### Appraisal API Breakdown

**Test Scenario**: Milano Centro, 95 sqm apartment

| Step | Operation | Time | % of Total |
|------|-----------|------|------------|
| 1 | Request validation | <0.1s | 1% |
| 2 | **Perplexity search** | **3.5-4.2s** | **60-70%** |
| 3 | **Mistral LLM parsing** | **1.5-2.5s** | **25-35%** |
| 4 | Investment calculations | 0.1s | 2% |
| 5 | Result assembly | <0.1s | 1% |
| **Total** | **5.23-8.12s** | **100%** |

### Specific Measurements

**Test 1** (without cache):
- Total: 8.12s
- Perplexity: 4.21s (52%)
- LLM parsing: ~2.5s (31%)
- Comparables found: 2

**Test 2** (with cache):
- Total: 5.23s
- Perplexity: 3.54s (68%)
- LLM parsing: ~1.5s (29%)
- Comparables found: 1

---

## Performance Bottlenecks

### 1. Perplexity AI Search (60-70% of time) 🔴

**Current Implementation**:
```python
# application/services/appraisal.py:30-35
research_text = self.research.find_market_comparables(
    city=request.city,
    zone=request.zone,
    property_type=request.property_type,
    surface_sqm=request.surface_sqm,
)
```

**Issue**: Synchronous external API call, unoptimized query

**Impact**: 3.5-4.2 seconds per request

**Optimization Opportunities**:

#### A. Cache Strategy (IMPLEMENTED ✅)
```python
# infrastructure/adapters/perplexity_adapter.py
# Already has caching with 24h TTL
```
**Pros**:
- ✅ 35% faster on cache hits (8.12s → 5.23s)
- ✅ Already implemented
- ✅ No code changes needed

**Cons**:
- Only helps repeated queries
- Initial requests still slow

**Status**: ✅ Already active

#### B. Query Optimization 🟡
**Current query**:
```
"Cerca 3 annunci immobiliari IN VENDITA (non affitto) per apartment a Milano, CAP Centro, circa 95 mq"
```

**Optimized query**:
```
"Milano Centro apartment 90-100mq €/mq vendita"  # Shorter, more focused
```

**Expected Impact**: 15-20% faster Perplexity response
**Effort**: Low (1 line change)
**Risk**: Low (fallback to current query if no results)

#### C. Parallel Property Database Search 🟢
**Strategy**: Check local Supabase database FIRST, use Perplexity ONLY if insufficient local data

```python
# Pseudocode
local_comps = await db.search_properties(city, zone, sqm_range)
if len(local_comps) >= 3:
    return local_comps  # <0.5s response!
else:
    # Fall back to Perplexity for fresh data
    perplexity_comps = await research.find_market_comparables(...)
```

**Expected Impact**: 80-90% faster when local data available
**Effort**: Medium (new query function)
**Risk**: Low (Perplexity fallback ensures quality)

---

### 2. Mistral LLM Parsing (25-35% of time) 🟡

**Current Implementation**:
```python
# application/services/appraisal.py:104-178
def _parse_comparables(self, text: str) -> list[Comparable]:
    client = Mistral(api_key=settings.MISTRAL_API_KEY)
    response = client.chat.complete(
        model=settings.MISTRAL_MODEL,
        messages=[{"role": "user", "content": extraction_prompt}],
    )
    # ... JSON parsing ...
```

**Issue**: Additional AI call for data extraction

**Impact**: 1.5-2.5 seconds per request

**Optimization Opportunities**:

#### A. Structured Output Mode 🟢
**Strategy**: Use Mistral's JSON mode to skip parsing step

```python
response = client.chat.complete(
    model=settings.MISTRAL_MODEL,
    messages=[{"role": "user", "content": extraction_prompt}],
    response_format={"type": "json_object"},  # ← Add this
)
```

**Expected Impact**: 20-30% faster parsing
**Effort**: Low (parameter change)
**Risk**: Low (fallback regex still available)

#### B. Lighter Model 🟡
**Current**: `mistral-large-latest` (most capable, slowest)
**Alternative**: `mistral-small-latest` (faster, still good for extraction)

**Expected Impact**: 40-50% faster parsing
**Effort**: Low (config change)
**Risk**: Medium (may reduce extraction accuracy)

#### C. Skip LLM for Simple Cases 🟢
**Strategy**: If Perplexity returns well-formatted data, skip LLM entirely

```python
if self._is_structured_response(research_text):
    return self._parse_comparables_regex(research_text)  # Fast path
else:
    return self._parse_comparables_llm(research_text)  # Robust path
```

**Expected Impact**: 1.5-2.5s saved when structure is clear
**Effort**: Medium (detection logic)
**Risk**: Low (LLM fallback for complex cases)

---

### 3. Database Optimization (Future) 🔵

**Current**: 243 properties, no semantic search

**Opportunities**:

#### A. Add Indexes
```sql
CREATE INDEX idx_properties_zone_sqm ON properties(zone, sqm);
CREATE INDEX idx_properties_price_sqm ON properties(price, sqm);
```

**Impact**: <100ms query time
**Effort**: Low (SQL command)

#### B. Semantic Search (Future 2026)
Per ADR-050, implement:
- Vector embeddings for property descriptions
- Semantic matching for better comparables

**Impact**: Better quality, similar speed
**Effort**: High (requires RAG implementation)

---

## Recommended Optimization Plan

### Phase 1: Quick Wins (1-2 days) 🎯

**Priority 1**:
1. ✅ **Cache** - Already implemented
2. 🟢 **Local DB First** - Check Supabase before Perplexity
3. 🟢 **Structured JSON output** - Enable Mistral JSON mode

**Expected Results**: 5-8s → **2-3s** (60% improvement)

### Phase 2: Advanced Optimizations (1 week)

1. 🟡 **Query optimization** - Shorter, more focused Perplexity queries
2. 🟡 **Async processing** - Make AI calls non-blocking
3. 🟢 **Database indexes** - Speed up local queries

**Expected Results**: 2-3s → **1-2s** (additional 50% improvement)

### Phase 3: Architecture Improvements (1+ month)

1. 🔵 **Semantic search** - Vector-based matching (ADR-050)
2. 🔵 **Background refresh** - Pre-cache popular zones
3. 🔵 **CDN caching** - Edge caching for common queries

**Expected Results**: 1-2s → **<1s** (sub-second response)

---

## Implementation Priorities

### Immediate (This Week)

```python
# 1. Add local database search
async def get_local_comparables(city, zone, sqm_range):
    # Query Supabase properties table
    # Return if >=3 recent matches found
    pass

# 2. Enable Mistral JSON mode
response = client.chat.complete(
    model=settings.MISTRAL_MODEL,
    messages=messages,
    response_format={"type": "json_object"},  # ← Add
)
```

**Estimated effort**: 4-6 hours
**Expected impact**: 50-60% faster

### Next Sprint

```python
# 3. Optimize Perplexity query
query = f"{city} {zone} {property_type} {sqm_range}mq €/mq vendita"  # Shorter

# 4. Add database indexes
CREATE INDEX idx_properties_location ON properties(city, zone);
CREATE INDEX idx_properties_sqm_price ON properties(sqm, price);
```

**Estimated effort**: 2-3 hours
**Expected impact**: Additional 15-20% faster

---

## Monitoring & Metrics

### Performance Tracking

**Add logging for each step**:
```python
import time

start = time.time()
research_text = self.research.find_market_comparables(...)
logger.info("PERF_SEARCH", duration=time.time() - start)

start = time.time()
comparables = self._parse_comparables(research_text)
logger.info("PERF_PARSE", duration=time.time() - start)
```

**Target SLAs**:
| Percentile | Current | Target (Phase 1) | Target (Phase 3) |
|---|---|---|---|
| p50 | 6s | 2.5s | <1s |
| p90 | 8s | 3.5s | <1.5s |
| p99 | 10s+ | 5s | <2s |

---

## Cost Considerations

### API Costs

**Current** (per appraisal):
- Perplexity: $0.005
- Mistral parsing: $0.002
- **Total**: ~$0.007/request

**With optimizations**:
- Local DB (80% of requests): $0
- Perplexity (20% cache miss): $0.005
- Mistral (with JSON mode): $0.001
- **Total**: ~$0.0012/request average

**Savings**: 80% reduction in API costs

---

## Next Steps

1. [ ] Implement local database search function
2. [ ] Enable Mistral JSON response mode
3. [ ] Add database indexes for properties table
4. [ ] Test performance with optimizations
5. [ ] Monitor and iterate based on real user data

---

## Performance Test Script

```bash
# Before optimization
python scripts/live_demo.py  # Select option 4
# Record baseline: ~5-8s

# After Phase 1 optimizations
python scripts/live_demo.py  # Select option 4
# Target: ~2-3s

# Measure improvement
echo "Improvement: X% faster"
```

---

## Conclusion

> [!IMPORTANT]
> **Primary bottleneck**: External AI API calls (Perplexity + Mistral) consume 85-90% of response time.

**Recommended approach**:
1. **Short term**: Local database first, cached Perplexity fallback
2. **Medium term**: Optimized queries, async processing
3. **Long term**: Semantic search, edge caching

**Expected Results**: Current 5-8s → Target 2-3s (Phase 1) → Ultimate <1s (Phase 3)

---

*Last Updated: 2026-01-03*
