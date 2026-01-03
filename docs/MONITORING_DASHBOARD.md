# Monitoring Dashboard Setup Guide

**Date**: 2026-01-03  
**Purpose**: Set up real-time performance monitoring dashboard

---

## Quick Start

Choose your preferred dashboard tool:
- **Option A**: Metabase (recommended - free, easy setup)
- **Option B**: Grafana (powerful, requires more setup)
- **Option C**: Supabase Dashboard (basic queries)

---

## Option A: Metabase Dashboard (Recommended)

### 1. Installation

**Using Docker**:
```bash
docker run -d -p 3000:3000 \
  -e "MB_DB_TYPE=postgres" \
  -e "MB_DB_DBNAME=metabase" \
  -e "MB_DB_PORT=5432" \
  -e "MB_DB_USER=metabase" \
  -e "MB_DB_PASS=metabase" \
  -e "MB_DB_HOST=localhost" \
  --name metabase \
  metabase/metabase
```

**Or Cloud** (free tier):
- Visit https://www.metabase.com/start/oss/
- Create free account
- Skip local installation

### 2. Connect to Supabase

1. Open Metabase: http://localhost:3000
2. Add Database:
   - **Type**: PostgreSQL
   - **Host**: [Your Supabase host from settings]
   - **Port**: 5432
   - **Database**: postgres
   - **Username**: postgres
   - **Password**: [Your Supabase password]

Get connection details from Supabase Dashboard → Settings → Database

### 3. Create Dashboard

**Dashboard Layout**:
```
┌─────────────────────────────────────────────────┐
│  APPRAISAL PERFORMANCE - LAST 24 HOURS          │
├──────────────┬──────────────┬───────────────────┤
│  Avg Response│  Local Hit   │  Avg Confidence   │
│    650ms     │    85%       │      73%          │
├──────────────┴──────────────┴───────────────────┤
│  Response Time Distribution (p50, p90, p99)     │
│  [Line Chart]                                   │
├─────────────────────────────────────────────────┤
│  Queries by City/Zone [Bar Chart]               │
├──────────────────────┬───────────────────────────┤
│  Local vs Perplexity │  Confidence Over Time    │
│  [Pie Chart]         │  [Line Chart]            │
└──────────────────────┴───────────────────────────┘
```

### 4. Dashboard Queries

**Query 1: Performance Overview** (Numbers)
```sql
SELECT 
  COUNT(*) as total_appraisals,
  ROUND(AVG(response_time_ms)) as avg_response_ms,
  ROUND(AVG(confidence_level)) as avg_confidence,
  ROUND(SUM(CASE WHEN used_local_search THEN 1 ELSE 0 END)::NUMERIC / COUNT(*) * 100, 1) as local_hit_rate
FROM appraisal_performance_metrics
WHERE created_at >= NOW() - INTERVAL '24 hours';
```

**Query 2: Response Time Trends** (Line Chart)
```sql
SELECT 
  DATE_TRUNC('hour', created_at) as hour,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY response_time_ms) as p50,
  PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY response_time_ms) as p90,
  PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY response_time_ms) as p99
FROM appraisal_performance_metrics
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY DATE_TRUNC('hour', created_at)
ORDER BY hour;
```

**Query 3: Geographic Distribution** (Bar Chart)
```sql
SELECT 
  city,
  zone,
  COUNT(*) as requests,
  ROUND(AVG(response_time_ms)) as avg_ms,
  ROUND(AVG(confidence_level)) as avg_confidence
FROM appraisal_performance_metrics
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY city, zone
ORDER BY requests DESC
LIMIT 10;
```

**Query 4: Local vs Perplexity** (Pie Chart)
```sql
SELECT 
  CASE 
    WHEN used_local_search THEN 'Local Database'
    ELSE 'Perplexity API'
  END as source,
  COUNT(*) as count
FROM appraisal_performance_metrics
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY used_local_search;
```

**Query 5: User Feedback** (Table)
```sql
SELECT 
  created_at,
  rating,
  speed_rating,
  accuracy_rating,
  feedback_text
FROM appraisal_feedback
ORDER BY created_at DESC
LIMIT 20;
```

---

## Option B: Grafana Dashboard

### 1. Installation

**Using Docker**:
```bash
docker run -d -p 3001:3000 \
  --name=grafana \
  grafana/grafana
```

Default login: admin/admin

### 2. Add PostgreSQL Data Source

1. Configuration → Data Sources → Add PostgreSQL
2. Enter Supabase connection details
3. Test connection

### 3. Import Dashboard JSON

Create dashboard with panels for each metric above, or use Grafana's query builder.

**Sample Panel JSON**:
```json
{
  "targets": [
    {
      "rawSql": "SELECT created_at, response_time_ms FROM appraisal_performance_metrics WHERE $__timeFilter(created_at)",
      "format": "time_series"
    }
  ],
  "title": "Response Time"
}
```

---

## Option C: Supabase Dashboard Queries

**Run directly in Supabase SQL Editor**:

### Performance Last 24h
```sql
SELECT * FROM get_performance_stats(24);
```

### Daily Summary
```sql
SELECT 
  date,
  city,
  total_appraisals,
  ROUND(avg_response_ms) as avg_ms,
  ROUND(local_hit_rate * 100, 1) as local_hit_pct,
  ROUND(avg_confidence) as avg_conf
FROM mv_daily_performance_summary
ORDER BY date DESC, total_appraisals DESC
LIMIT 30;
```

### Real-time Stream
```sql
SELECT 
  created_at,
  city,
  zone,
  response_time_ms,
  confidence_level,
  used_local_search
FROM appraisal_performance_metrics
ORDER BY created_at DESC
LIMIT 50;
```

---

## Alerting Setup

### Metabase Alerts

1. Create question for each metric
2. Set up pulse/subscription
3. Email on threshold breach

**Example Alerts**:
- Alert if p90 response > 2000ms
- Alert if local hit rate < 70%
- Alert if avg confidence < 60%

### Alert Query Examples

**Slow Performance Alert**:
```sql
SELECT 
  COUNT(*) as slow_requests
FROM appraisal_performance_metrics
WHERE created_at >= NOW() - INTERVAL '1 hour'
  AND response_time_ms > 2000;
-- Alert if slow_requests > 10
```

**Low Confidence Alert**:
```sql
SELECT 
  AVG(confidence_level) as avg_confidence
FROM appraisal_performance_metrics
WHERE created_at >= NOW() - INTERVAL '1 hour';
-- Alert if avg_confidence < 60
```

---

## Automated Refresh

### Daily Stats Refresh

**Create cron job or Supabase Edge Function**:

```sql
-- Run daily at 2 AM
SELECT cron.schedule(
  'refresh-performance-views',
  '0 2 * * *',
  $$SELECT refresh_performance_views()$$
);
```

Or manually:
```sql
SELECT refresh_performance_views();
```

---

## Mobile Dashboard (Bonus)

**Metabase Mobile App**:
- iOS: https://apps.apple.com/app/metabase/id1117554942
- Android: https://play.google.com/store/apps/details?id=com.metabase

View dashboards on mobile for quick checks!

---

## Dashboard Sharing

**Public Dashboard** (Metabase):
1. Click "Share" on dashboard
2. Enable public link
3. Share with team

**Embed in Admin Panel**:
```html
<iframe
  src="https://metabase.yourdomain.com/public/dashboard/..."
  frameborder="0"
  width="100%"
  height="800"
  allowtransparency
></iframe>
```

---

## Monitoring Best Practices

### Check Frequency
- **Real-time**: During deployments
- **Daily**: Morning performance review
- **Weekly**: Trend analysis
- **Monthly**: Optimization planning

### Key Metrics to Watch
1. **p90 Response Time** - Should be <1.5s
2. **Local Hit Rate** - Should be >80%
3. **Confidence Level** - Should be >70%
4. **Error Rate** - Should be <1%

### Action Thresholds

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| p90 Response | >1.5s | >3s | Investigate slow queries |
| Local Hit Rate | <75% | <60% | Expand data collection |
| Avg Confidence | <65% | <55% | Review comp quality |
| Error Rate | >2% | >5% | Check API health |

---

## Next Steps

1. ✅ Choose dashboard tool (Metabase recommended)
2. ✅ Set up connection to Supabase
3. ✅ Create dashboard using queries above
4. ✅ Configure alerts
5. ✅ Share with team
6. ✅ Monitor for 24-48 hours

---

*Setup time: 30-60 minutes*  
*Difficulty: Easy-Medium*  
*Value: High - Real-time visibility into system performance*
