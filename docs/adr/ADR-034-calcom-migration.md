# ADR-034: Cal.com Migration for Appointment Scheduling

**Status**: Accepted
**Date**: 2025-12-29
**Supersedes**: ADR-033 (Setmore Appointment Scheduling)

## Context

The initial appointment scheduling implementation used Setmore, which required a Pro account subscription to access API features. This created a barrier to deployment and testing.

## Decision

We have migrated from **Setmore** to **Cal.com** for appointment scheduling.

### Rationale

1. **Cost**: Cal.com is open-source with free API access
2. **API Quality**: Cal.com provides a modern REST API (v2) with better documentation
3. **Control**: Self-hostable option available if needed
4. **Features**: Supports webhooks, OAuth2, and programmatic booking creation
5. **Community**: Active open-source community and regular updates

## Implementation

### Cal.com Adapter

Created `infrastructure/adapters/calcom_adapter.py` implementing `CalendarPort`:

```python
class CalComAdapter(CalendarPort):
    def get_availability(self, staff_id: str, date: str) -> list[str]:
        # GET /v2/slots with eventTypeId

    def create_event(...) -> str:
        # POST /v2/bookings
```

### Webhook Handler

Created `presentation/api/webhooks/calcom_webhook.py`:
- Handles `BOOKING_CREATED`, `BOOKING_CANCELLED`, `BOOKING_RESCHEDULED` events
- HMAC-SHA256 signature verification
- Updates lead status in database

### Configuration

**Environment Variables**:
- `CALCOM_API_KEY`: API authentication key
- `CALCOM_EVENT_TYPE_ID`: Event type for property viewings
- `CALCOM_WEBHOOK_SECRET`: Webhook signature secret
- `CALCOM_BOOKING_LINK`: Public booking page URL

## Consequences

### Positive

- ✅ No subscription cost
- ✅ Immediate API access for development
- ✅ Better API documentation and developer experience
- ✅ Open-source transparency
- ✅ Self-hosting option for future scaling

### Negative

- ⚠️ Requires manual setup of Cal.com account
- ⚠️ Event type configuration needed in Cal.com dashboard
- ⚠️ Less mature than enterprise solutions (but sufficient for MVP)

### Neutral

- Migration required updating:
  - Adapter implementation
  - Webhook handler
  - Configuration files
  - Test fixtures
  - Documentation

## Migration Checklist

- [x] Create `CalComAdapter`
- [x] Create `calcom_webhook.py`
- [x] Update `settings.py` with Cal.com env vars
- [x] Update `container.py` dependency injection
- [x] Update `api.py` webhook routes
- [x] Update `agents.py` booking link
- [x] Update test fixtures
- [x] Delete Setmore files
- [x] Update `.env.example`
- [ ] Configure Cal.com account (event type, webhook URL)
- [ ] Test end-to-end booking flow

## References

- [Cal.com API Documentation](https://cal.com/docs/api-reference)
- [Cal.com GitHub](https://github.com/calcom/cal.com)
