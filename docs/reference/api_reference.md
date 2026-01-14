# Agenzia AI - API Reference

> **Version**: 1.0.0
> **Base URL**: `https://api.agenzia.ai` (Production) | `http://localhost:8000` (Development)
> **Authentication**: Bearer JWT Token (Supabase Auth)

---

## Overview

The Agenzia AI API provides programmatic access to our AI-powered real estate automation platform. Endpoints are organized by tier availability:

| Tier | Description | Access |
|------|-------------|--------|
| 🟢 **Free** | Public endpoints, webhooks, health checks | No auth required |
| 🔵 **Pro** | Dashboard actions, lead management, analytics | JWT Required |
| 🟣 **Enterprise** | Market intelligence, outreach automation, reporting | JWT + Org Admin |

---

## Authentication

All protected endpoints require a valid JWT token in the `Authorization` header:

```http
Authorization: Bearer <your-jwt-token>
```

Tokens are issued by Supabase Auth and include the user's `active_org_id` for multi-tenant isolation.

---

## 🟢 Free Tier Endpoints

### Health & Status

#### `GET /health`
Basic health check for uptime monitoring.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-14T17:00:00Z",
  "service": "agenzia-ai-api",
  "version": "1.0.0"
}
```

#### `GET /ready`
Readiness check verifying all dependencies (DB, Cache, LLM).

**Response (200 OK):**
```json
{
  "status": "ready",
  "checks": {
    "database": true,
    "cache": true,
    "llm": true,
    "whatsapp": true
  }
}
```

#### `GET /metrics`
Prometheus-format metrics for observability dashboards.

---

### Lead Ingestion

#### `POST /api/leads`
Create a new lead from external sources (landing pages, forms).

**Request:**
```json
{
  "name": "Marco Rossi",
  "agency": "Anzevino Realty",
  "phone": "+393331234567",
  "postcode": "20121",
  "properties": "3-room apartment in Centro",
  "language": "it"
}
```

**Response:**
```json
{
  "success": true,
  "lead_id": "uuid-...",
  "message": "Lead created and AI conversation initiated"
}
```

---

### Webhooks

#### `POST /api/twilio/webhook`
Receives incoming WhatsApp messages from Twilio.

#### `POST /api/twilio/status`
Receives delivery/read receipts from Twilio.

#### `POST /api/calcom/webhook`
Receives booking notifications from Cal.com.

#### `POST /api/voice/inbound`
Handles inbound voice call events.

#### `POST /api/portal/webhook`
Receives property listing updates from external portals.

#### `POST /api/leads/immobiliare`
Ingests leads from Immobiliare.it integration.

---

### Public Tools

#### `POST /api/appraisal`
Generates an AI-driven property valuation (Fifi Tool).

**Request:**
```json
{
  "address": "Via Monte Napoleone 8, Milano",
  "property_type": "apartment",
  "sqm": 120,
  "rooms": 4,
  "floor": 3,
  "condition": "ristrutturato"
}
```

**Response:**
```json
{
  "estimated_value": 850000,
  "range_min": 780000,
  "range_max": 920000,
  "price_per_sqm": 7083,
  "confidence": 0.85,
  "comparables": [...]
}
```

#### `POST /api/appraisal/pdf`
Generates a PDF appraisal report.

---

## 🔵 Pro Tier Endpoints

> **Authentication Required**: All Pro endpoints require a valid JWT.

### Lead Management

#### `POST /api/leads/takeover`
Pause AI automation and transfer lead to human agent.

**Request:**
```json
{ "phone": "+393331234567" }
```

#### `POST /api/leads/resume`
Resume AI automation for a paused lead.

#### `POST /api/leads/message`
Send a manual message to a lead.

**Request:**
```json
{
  "phone": "+393331234567",
  "message": "Buongiorno! Ho un immobile perfetto per lei."
}
```

#### `PUT /api/leads/update`
Update lead details (name, budget, zones, status).

**Request:**
```json
{
  "phone": "+393331234567",
  "name": "Marco Rossi Updated",
  "budget": 500000,
  "zones": ["Centro", "Navigli"],
  "status": "qualified"
}
```

#### `POST /api/leads/schedule`
Schedule a property viewing.

#### `POST /api/leads/contract`
Generate a preliminary contract.

---

### Analytics

#### `GET /api/analytics/qualification`
Get lead qualification funnel metrics.

**Query Parameters:**
- `days` (int, default: 7): Analysis period (1-90)

**Response:**
```json
{
  "total_started": 150,
  "total_completed": 42,
  "completion_rate": 28.0,
  "avg_completion_time_minutes": 4.5
}
```

#### `GET /api/analytics/scores`
Get lead score distribution (HOT/WARM/COLD).

---

### Intelligence

#### `GET /api/leads/{phone}/summary`
AI-generated conversation summary with sentiment analysis.

**Response:**
```json
{
  "summary": "Il cliente cerca un trilocale in zona Centro...",
  "sentiment": "positive",
  "key_interests": ["Centro", "ristrutturato", "terrazzo"],
  "next_action": "schedule_viewing"
}
```

---

### WebSocket

#### `WS /ws/conversations`
Real-time updates for dashboard conversations.

**Query Parameters:**
- `token` (string): JWT for authentication
- `client_id` (string, optional): Client identifier

**Messages Received:**
```json
{ "type": "connected", "connection_id": "uuid-..." }
{ "type": "conversations", "data": [...] }
{ "type": "new_message", "lead_id": "...", "message": {...} }
```

---

## 🟣 Enterprise Tier Endpoints

> **Authentication Required**: JWT with organization admin role.

### Market Intelligence

#### `GET /api/market/data`
Retrieve market transaction data.

**Query Parameters:**
- `city` (string): City filter
- `zone` (string): Zone filter
- `limit` (int, default: 100): Max results

#### `GET /api/market/analysis`
AI-generated market analysis with statistics.

#### `GET /api/market/trends`
Predictive price trends for a zone.

#### `GET /api/market/valuation`
Real-time zone valuation data.

---

### Outreach Automation

#### `GET /api/outreach/targets`
List agency outreach targets.

#### `POST /api/outreach/generate`
Discover new agency targets in a city.

**Request:**
```json
{ "city": "Milano" }
```

#### `POST /api/outreach/send`
Send personalized outreach message to target.

---

### Reporting

#### `POST /api/reports/sales`
Generate a comprehensive PDF sales report.

**Request:**
```json
{
  "property_id": "uuid-...",
  "owner_phone": "+393331234567"
}
```

---

### Lead Routing

#### `POST /api/leads/route`
Manually route or auto-assign lead to agent.

**Request:**
```json
{
  "lead_id": "uuid-...",
  "agent_id": "uuid-..." // Optional, auto-routes if null
}
```

---

### Feedback Collection

#### `POST /api/feedback/submit`
Submit user feedback on appraisals.

**Request:**
```json
{
  "appraisal_id": "uuid-...",
  "overall_rating": 5,
  "speed_rating": 4,
  "accuracy_rating": 5,
  "feedback_text": "Ottimo servizio, molto preciso!"
}
```

---

### Performance Monitoring

#### `GET /api/monitoring/performance`
Aggregated performance statistics for internal dashboards.

**Query Parameters:**
- `hours` (int, default: 24): Analysis window (1-168)

---

## Error Handling

All endpoints return consistent error responses:

```json
{
  "detail": "Error message describing the issue",
  "code": "ERROR_CODE",
  "status_code": 400
}
```

**Common Status Codes:**
- `400` - Bad Request (validation error)
- `401` - Unauthorized (missing/invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `500` - Internal Server Error

---

## Rate Limits

| Tier | Requests/min | WebSocket Connections |
|------|-------------|----------------------|
| Free | 60 | 0 |
| Pro | 300 | 5 |
| Enterprise | 1000 | Unlimited |

---

## SDK & Integration

### cURL Example
```bash
curl -X GET "https://api.agenzia.ai/api/analytics/qualification?days=7" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

### Python Example
```python
import requests

headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    "https://api.agenzia.ai/api/market/analysis",
    params={"city": "Milano"},
    headers=headers
)
print(response.json())
```

---

## Support

- **API Status**: [status.agenzia.ai](https://status.agenzia.ai)
- **Technical Support**: api-support@agenzia.ai
- **Documentation**: [docs.agenzia.ai](https://docs.agenzia.ai)
