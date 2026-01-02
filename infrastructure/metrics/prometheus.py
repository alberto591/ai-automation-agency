"""Prometheus metrics for monitoring application performance."""
from prometheus_client import Counter, Gauge, Histogram

# Cache metrics
cache_hits_total = Counter("cache_hits_total", "Total number of cache hits", ["cache_type"])

cache_misses_total = Counter("cache_misses_total", "Total number of cache misses", ["cache_type"])

cache_hit_rate = Gauge("cache_hit_rate", "Cache hit rate percentage", ["cache_type"])

# Perplexity API metrics
perplexity_api_calls_total = Counter("perplexity_api_calls_total", "Total Perplexity API calls")

perplexity_api_duration_seconds = Histogram(
    "perplexity_api_duration_seconds",
    "Perplexity API call duration in seconds",
    buckets=[0.5, 1.0, 2.0, 3.0, 5.0, 10.0, 30.0],
)

# Appraisal metrics
appraisal_requests_total = Counter(
    "appraisal_requests_total", "Total appraisal requests", ["status"]
)

appraisal_duration_seconds = Histogram(
    "appraisal_duration_seconds",
    "Appraisal processing duration in seconds",
    buckets=[1.0, 2.0, 5.0, 10.0, 20.0, 30.0, 60.0],
)

# Lead creation metrics
lead_creation_total = Counter("lead_creation_total", "Total leads created", ["source"])
