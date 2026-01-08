# Production Monitoring & Observability

**Last Updated:** 2026-01-08  
**Status:** Configured & Ready

---

## Health Check Endpoints

### `/health` - Basic Liveness
**Purpose:** Uptime monitoring, load balancer health checks  
**Returns:** 200 if service is running

```json
{
  "status": "healthy",
  "timestamp": "2026-01-08T12:20:00Z",
  "service": "agenzia-ai-api",
  "version": "1.0.0"
}
```

**Monitoring Setup:**
- UptimeRobot: Check every 5 minutes
- Alert if down for >2 consecutive checks

---

### `/ready` - Readiness Check
**Purpose:** Deployment readiness, dependency verification  
**Returns:** 200 if all dependencies ready, 503 if any down

```json
{
  "status": "ready",
  "timestamp": "2026-01-08T12:20:00Z",
  "checks": {
    "database": {
      "status": "up",
      "count": 150
    },
    "cache": {
      "status": "up"
    }
  }
}
```

**Use in CI/CD:**
```bash
# Wait for readiness before switching traffic
until $(curl --output /dev/null --silent --head --fail http://api/ready); do
    printf '.'
    sleep 5
done
```

---

## Sentry Error Tracking

### Configuration
- **DSN:** Configured via `SENTRY_DSN` env var
- **Environment:** `production` | `staging` | `development`
- **Sample Rate:** 10% in production, 100% in dev

### Enabled Features
- ✅ Error tracking with stack traces
- ✅ Performance monitoring (traces_sample_rate)
- ✅ Release tracking (set via deployment)
- ✅ User context (lead phone numbers - hashed)

### Key Metrics to Monitor in Sentry
- Error rate (target: <0.1% of requests)
- P95 response time (target: <200ms)
- Database query duration
- External API failures (Twilio, Mistral)

**Dashboard:** https://sentry.io/organizations/[org]/projects/agenzia-ai/

---

## Prometheus Metrics

### `/metrics` Endpoint
Exposes Prometheus-compatible metrics for scraping.

**Key Metrics:**

```prometheus
# Cache performance
cache_hit_rate{service="market-intelligence"} 0.92

# API activity
perplexity_api_calls_total 142
appraisal_requests_total 28

# Lead processing
messages_sent_total{channel="whatsapp"} 1250
messages_failed_total{channel="whatsapp"} 3
```

### Grafana Dashboards
Create dashboards for:
1. **API Health** - Request rate, error rate, latency
2. **Lead Flow** - Leads created, messages sent, conversions
3. **Cache Performance** - Hit rate, evictions
4. **External Dependencies** - Supabase query times, Redis latency

---

## Logging Strategy

### Structured Logging
All logs use structured format with context:

```python
logger.info("LEAD_QUALIFIED", context={
    "phone": "+39...",
    "score": 85,
    "journey_state": "HOT"
})
```

### Log Levels
- `ERROR`: Failures requiring investigation
- `WARNING`: Degraded state, retries
- `INFO`: Important business events
- `DEBUG`: Detailed trace (disabled in production)

### Log Aggregation
**Recommended:** Export to centralized logging service
- Options: Logtail, Papertrail, CloudWatch Logs
- Retention: 30 days
- Searchable by: phone, lead_id, error_type

---

## Alerts & SLAs

### Critical Alerts (PagerDuty/Email)
- `/health` endpoint down for >5 minutes
- Error rate >1% of requests
- Database connection failures
- Redis completely unavailable

### Warning Alerts (Slack)
- API p95 latency >500ms
- Cache hit rate <80%
- Twilio message failures >5% 

### SLA Targets
| Metric | Target | Current |
|--------|--------|---------|
| Uptime | 99.9% | TBD |
| API p50 latency | <100ms | TBD |
| API p95 latency | <200ms | TBD |
| Error rate | <0.1% | TBD |

---

## Monitoring Checklist

### Pre-Launch
- [ ] Set up UptimeRobot for `/health` monitoring
- [ ] Configure Sentry DSN in production env
- [ ] Export Prometheus metrics to Grafana Cloud
- [ ] Set up alert rules in Prometheus/Alertmanager
- [ ] Create Slack/email notification channels

### Post-Launch (Week 1)
- [ ] Validate alerts are firing correctly (test)
- [ ] Review Sentry error patterns
- [ ] Tune alert thresholds based on real traffic
- [ ] Create runbook for common incidents

---

## Incident Response

### On-Call Rotation
- Primary: [Founder/Tech Lead]
- Escalation: [External DevOps consultant]

### Runbook Links
- [Database connection issues](file:///Users/lycanbeats/Desktop/agenzia-ai/docs/runbook/database-troubleshooting.md)
- [Redis failures](file:///Users/lycanbeats/Desktop/agenzia-ai/docs/runbook/redis-troubleshooting.md)
- [WhatsApp message failures](file:///Users/lycanbeats/Desktop/agenzia-ai/docs/runbook/whatsapp-troubleshooting.md)

### Incident Process
1. Acknowledge alert
2. Check `/ready` endpoint for dependency status
3. Review recent deployments
4. Check Sentry for error spike
5. Escalate if not resolved in 30 minutes

---

## Cost Monitoring

### Cloud Services Budget (Monthly)
- Supabase Pro: €25
- Redis (Upstash): €10
- Sentry: €0 (free tier for now)
- Hosting (Railway/Render): €20

**Total Est:** €55/month for infrastructure

### Alert Thresholds
- Sentry quota: Alert at 80% of free tier events
- Supabase storage: Alert at 90% of plan limit
