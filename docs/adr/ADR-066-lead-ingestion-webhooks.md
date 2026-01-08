# ADR-066: Lead Ingestion Webhooks & Security

**Status:** Accepted
**Date:** 2026-01-08
**Author:** Antigravity

## 1. Context (The "Why")

Marketing teams use Facebook Lead Ads, Google Forms, and Zapier to capture leads. Manually entering these into FiFi AI is inefficient. We need an automated ingestion pipeline that is secure and easy to integrate with.

## 2. Decision

We implemented two primary webhook endpoints and a normalization service.

### 2.1 Technical Channels
- **Facebook Webhook**: Implements Meta's challenge/response handshake and `X-Hub-Signature-256` HMAC verification for payload integrity.
- **Generic Webhook**: A universal JSON-inbound endpoint protected by `X-Webhook-Key` header, ideal for Zapier/Make.

### 2.2 Normalized Model
The `LeadIngestionService` converts heterogeneous payloads into our standard `Lead` model, ensuring the AI qualification flow starts automatically.

## 3. Rationale (The "Proof")

*   **Security First**: Signature verification prevents malicious spoofing of lead data.
*   **Zero Loss**: Any valid JSON payload can be mapped, ensuring flexibility for future marketing tools.
*   **Instant Qualification**: Leads ingested via webhooks are immediately processed by the AI for scoring.

## 4. Consequences

*   **Positive**: "Set-and-forget" marketing automation.
*   **Trade-off**: Requires users to configure a shared secret/API key in their marketing tools.

## 5. Wiring Check (No Dead Code)
- [x] Router in `presentation/api/webhooks/lead_sources.py`
- [x] Ingestion Service in `application/services/lead_ingestion_service.py`
- [x] Facebook settings added to `config/settings.py`
