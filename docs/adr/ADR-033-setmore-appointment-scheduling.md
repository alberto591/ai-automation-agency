# ADR-033: Setmore Appointment Scheduling

## Status
Accepted

## Context
The Sales Journey (Phase 4) requires the AI to steer qualified leads to a booking. Initially, Calendly was proposed.

## Decision
We selected **Setmore** as the appointment scheduling provider.

### Rationale
- **Free Tier**: More generous features on the free tier compared to Calendly.
- **API Availability**: robust API for future deep integration.
- **User Preference**: Explicit request from the project owner/user.

### Consequences
- **Link Injection**: The AI MUST inject the Setmore link (`https://anzevinoai.setmore.com`) when `intent=VISIT`.
- **State Transition**: Leads are moved to `APPOINTMENT_REQUESTED` upon link injection.

## Alternatives Considered
- **Calendly**: Good but restrictive free tier.
- **Google Calendar Direct**: Too complex to build a full UI for slot picking from scratch (Wheel reinvention).
