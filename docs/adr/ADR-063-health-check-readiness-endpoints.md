# ADR-063: Health Check and Readiness Endpoints

**Status:** Accepted
**Date:** 2026-01-08
**Author:** System Architecture Team

## 1. Context (The "Why")

As we approach production deployment, we need reliable mechanisms to:
- Monitor API uptime and availability (for external monitoring services like UptimeRobot)
- Validate deployment readiness before routing traffic to new instances
- Provide visibility into critical dependency health (database, cache, external APIs)
- Enable automated health checks in CI/CD pipelines and load balancers

**Problem:** Without standardized health endpoints, we have:
- No way to programmatically verify the API is running
- No visibility into whether critical dependencies (Supabase, Redis) are accessible
- Manual deployment validation that is error-prone
- Inability to set up automated monitoring and alerting

## 2. Decision

We are implementing **two distinct health check endpoints** following Kubernetes health check patterns:

### `/health` - Liveness Probe
- **Purpose:** Simple binary check - "Is the API process running?"
- **Response:** 200 OK with minimal metadata (timestamp, service name, version)
- **Dependencies Checked:** None (lightweight by design)
- **Use Case:** Uptime monitoring, load balancer health checks

### `/ready` - Readiness Probe
- **Purpose:** Comprehensive check - "Is the API ready to serve traffic?"
- **Response:** 200 OK if all dependencies available, 503 Service Unavailable otherwise
- **Dependencies Checked:**
  - Supabase database connectivity (query test)
  - Redis/cache layer availability
  - (Future: External API reachability if critical)
- **Use Case:** Deployment validation, traffic routing decisions

## 3. Rationale (The "Proof")

### Why Two Endpoints?

**Separate Concerns:**
- `/health` for "is it alive?" (fast, always responds)
- `/ready` for "should it receive traffic?" (slower, dependency-aware)

**Industry Standard:**
- Kubernetes uses liveness + readiness probes
- AWS ELB health checks follow similar patterns
- Google Cloud Load Balancer supports both patterns

### Why This Approach Over Alternatives?

**Alternative 1: Single `/health` Endpoint with Dependency Checks**
- ❌ **Rejected:** Slow health checks cause false positives in uptime monitoring
- ❌ **Problem:** Temporary Redis outage would mark entire service as "down" even though it could serve cached requests

**Alternative 2: No Health Endpoints, Monitor via Logs**
- ❌ **Rejected:** Requires complex log parsing and delayed detection
- ❌ **Problem:** Can't be used by load balancers or deployment automation

**Alternative 3: Third-Party Health Check Service (e.g., Healthchecks.io)**
- ❌ **Rejected:** Adds external dependency for critical infrastructure
- ✅ **Compromise:** Use third-party for alerting, but expose native endpoints for internal checks

### Research References

- [Kubernetes Liveness/Readiness Probes Best Practices](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
- [Google SRE Book - Health Checks](https://sre.google/sre-book/service-level-objectives/)
- FastAPI Health Check Patterns (community consensus)

## 4. Consequences

### Positive
- ✅ **Automated Monitoring:** Can set up UptimeRobot to ping `/health` every 5 minutes
- ✅ **Deployment Safety:** `/ready` prevents traffic routing to instances with broken dependencies
- ✅ **Debugging Aid:** `/ready` response shows which specific dependency is failing
- ✅ **Load Balancer Integration:** Health checks work out-of-the-box with AWS ALB, GCP LB, etc.
- ✅ **Zero-Downtime Deploys:** New instances only receive traffic after `/ready` returns 200

### Negative/Trade-offs
- ⚠️ **Additional Maintenance:** Need to keep dependency checks updated as system evolves
- ⚠️ **False Negatives:** Overly strict `/ready` checks could prevent valid instances from serving traffic
- ⚠️ **Performance Overhead:** `/ready` makes real DB queries (mitigated: simple COUNT query, <50ms)
- ⚠️ **Dependency on Redis:** If Redis is down, `/ready` fails even though core functionality might work (acceptable trade-off)

### Acceptable Trade-offs
- `/ready` endpoint is **slightly slower** (~50-100ms) due to dependency checks
  - **Mitigation:** Only called during deployment/routing decisions, not per-request
- Potential for **false positives** if temporary network blip during check
  - **Mitigation:** Load balancers typically require 2-3 consecutive failures before marking unhealthy

## 5. Wiring Check (No Dead Code)

### Implementation Status
- [x] `/health` endpoint implemented in `presentation/api/api.py:270-281`
- [x] `/ready` endpoint implemented in `presentation/api/api.py:284-322`
- [x] Database health check using `container.db.client.table("leads").select("count")`
- [x] Cache health check using `container.cache.get("_health_check")`
- [x] Response models include timestamp, status, checks breakdown
- [x] HTTP status codes: 200 (healthy), 503 (not ready)
- [x] Monitoring guide created: `docs/MONITORING.md`

### Environment Variables
- No new environment variables required (uses existing DB/Redis config)

### Testing
- [x] Manual testing verified (both endpoints return 200 in dev)
- [ ] Integration test for `/ready` with mocked DB failure (TODO: Week 2)
- [x] Documented in `STATUS.md` under "Recent Completions"

### Integration Points
- **UptimeRobot:** Configure to monitor `/health` endpoint (5-min interval)
- **Vercel/Heroku:** Use `/ready` for deployment health checks
- **Prometheus:** `/metrics` endpoint separate (already exists)
- **Sentry:** Error monitoring separate (already configured)

### Code Example

```python
# /health - Lightweight liveness check
@app.get("/health")
def health_check() -> dict[str, Any]:
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "agenzia-ai-api",
        "version": "1.0.0",
    }

# /ready - Comprehensive readiness check
@app.get("/ready")
def readiness_check() -> dict[str, Any]:
    checks = {}
    all_ready = True

    # Database check
    try:
        result = container.db.client.table("leads").select("count", count="exact").limit(1).execute()
        checks["database"] = {"status": "up", "count": result.count if result else 0}
    except Exception as e:
        checks["database"] = {"status": "down", "error": str(e)}
        all_ready = False

    # Cache check
    try:
        container.cache.get("_health_check")
        checks["cache"] = {"status": "up"}
    except Exception as e:
        checks["cache"] = {"status": "down", "error": str(e)}
        all_ready = False

    status_code = 200 if all_ready else 503
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if all_ready else "not ready",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": checks,
        },
    )
```

## 6. Future Considerations

### Potential Enhancements
1. **Startup Probe:** Separate endpoint for initial bootstrap checks (heavy operations)
2. **Dependency Weighting:** Mark some dependencies as "optional" (e.g., cache vs database)
3. **Graceful Degradation:** `/ready` returns 200 with warnings if non-critical deps are down
4. **Health History:** Track last N health check results for trend analysis
5. **Custom Checks:** Plugin system to register custom health checks per feature

### When to Add New Checks to `/ready`
- **DO Add:** New critical external API (e.g., Twilio, if it becomes hard requirement)
- **DO Add:** New required database table (if schema migration needed)
- **DON'T Add:** Nice-to-have features that don't block core functionality
- **DON'T Add:** Checks that take >200ms (keep `/ready` fast)

### Migration Path
If we need to change health check strategy:
1. Add new endpoint (e.g., `/healthz/v2`) alongside existing
2. Migrate monitoring tools to new endpoint
3. Deprecate old endpoints after 2-week grace period
4. Document change in ADR-XXX

## 7. References

- **Implementation Commit:** `212f50c feat: Production monitoring setup`
- **Documentation:** `docs/MONITORING.md`
- **Status Update:** `STATUS.md` (lines 55-56)
- **Related ADRs:**
  - ADR-053: Performance Monitoring Architecture
  - ADR-061: Redis Caching Strategy

## 8. Review & Approval

- **Date Proposed:** 2026-01-08
- **Date Accepted:** 2026-01-08
- **Reviewers:** System Architecture Team
- **Next Review:** After first production deployment (Week 2)

---

**Decision Status:** ✅ Implemented and Deployed
**Last Updated:** 2026-01-08
