# ADR-061: Redis Caching Strategy

**Status:** Accepted
**Date:** 2026-01-08
**Author:** Antigravity

## 1. Context (The "Why")
The Market Intelligence dashboard requires multiple aggregations from Supabase and subsequent AI analysis. These operations are:
1. **Expensive:** LLM calls take time and cost credits.
2. **Slow:** Database aggregation + LLM generation can take 2-5 seconds.
Since market data for a city/zone doesn't change every minute, real-time fetching is inefficient.

## 2. Decision
Implemented a `CachePort` interface and a `RedisAdapter` (with `InMemoryCacheAdapter` as a fallback).
We now cache `market_analysis` results for 24 hours, keyed by city/zone.

## 3. Rationale (The "Proof")
* **Latency:** Cache hits return in <100ms.
* **Resilience:** If Redis is down, the system transparently falls back to in-memory caching or raw generation.
* **Standardization:** Uses the Port/Adapter pattern to allow switching providers (e.g., Memcached) if needed.

## 4. Consequences
* **Positive:** Significantly faster dashboard loading. Lower API costs.
* **Negative/Trade-offs:** Market data might be stale for up to 24 hours. Users need to wait for the first-ever request to populate the cache.

## 5. Wiring Check (No Dead Code)
- [x] Port defined in `domain/ports.py`
- [x] Adapter implemented in `infrastructure/adapters/cache_adapter.py`
- [x] Registered in `config/container.py`
- [x] Integrated in `application/services/market_intelligence.py`
