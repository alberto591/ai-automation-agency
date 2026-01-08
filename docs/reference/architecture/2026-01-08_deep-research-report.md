# Deep Research Report - Agenzia AI Platform

**Date:** 2026-01-08
**Version:** 1.0

---

## Executive Summary

This report provides in-depth research findings for 5 critical areas of the Agenzia AI platform. Each section includes technical findings, recommendations, and actionable implementation guidance.

| Area | Priority | Status | Recommendation |
|------|----------|--------|----------------|
| Voice Integration | High | Research Complete | Implement Deepgram Nova-3 |
| Embedding Models | Medium | Research Complete | Keep OpenAI, monitor costs |
| Stripe Payments | High | Research Complete | Implement with e-invoicing |
| WhatsApp API | High | Research Complete | Apply for tier upgrade |
| Supabase Edge | Low | Research Complete | Keep FastAPI backend |

---

## 1. Voice Integration (Twilio + Deepgram)

### 1.1 Latency Optimization

**Target:** Sub-300ms end-to-end for voice AI interactions.

| Component | Best Practice | Latency Impact |
|-----------|---------------|----------------|
| STT Streaming | Use Deepgram Nova-3 or Flux | Sub-300ms |
| Audio Chunks | 200-250ms chunks via WebSocket | Faster feedback |
| Codec | Opus (optimized for real-time) | -50ms |
| Region | Deploy in EU (Frankfurt) | -100ms RTT |

**Twilio Media Streams:** Sends 20ms audio chunks via WebSocket. Forward directly to Deepgram for real-time transcription.

### 1.2 Italian Language Accuracy

| Provider | Model | Italian WER | Real-time |
|----------|-------|-------------|-----------|
| Deepgram | Nova-3 | ~10% (90% accuracy) | ✅ Yes |
| OpenAI | Whisper Large | ~8% | ❌ 30s chunks |
| Fine-tuned Whisper | Italian | ~6% | ❌ Self-hosted |

**Recommendation:** Use **Deepgram Nova-3** for real-time Italian transcription.

### 1.3 GDPR Call Recording Compliance (Italy)

> [!CAUTION]
> Recording calls without proper consent can result in **€250 - €8,000 fines**.

**Mandatory Requirements:**
1. Prior notification before recording
2. Legal basis (consent preferred)
3. 10-year max retention policy
4. Data subject rights within 30 days
5. Encrypt recordings at rest/transit

---

## 2. Embedding Model Optimization

### 2.1 Model Comparison for Italian

| Model | Dimensions | Italian Performance | Cost/1M tokens |
|-------|------------|---------------------|----------------|
| OpenAI text-embedding-3-small | 1536 | 44% MIRACL | $0.02 |
| Cohere Embed Multilingual v3 | 1024 | 46% nDCG@10 | ~$0.10 |
| BGE-M3 (Open Source) | 1024 | State-of-art | Free |

### 2.2 Cost Analysis

At 10K leads/month (~5M tokens): **$0.10/month**
At 100K leads/month: **$1.00/month**

**Verdict:** Keep OpenAI `text-embedding-3-small`. Extremely cost-effective.

---

## 3. Stripe Payment Integration (Italy)

### 3.1 E-Invoicing Mandate (2024)

> [!IMPORTANT]
> All VAT-registered businesses in Italy must issue electronic invoices via SDI using FatturaPA XML format.

**Requirements:**
- FatturaPA XML format via SDI
- 10-year archiving
- Cross-border SDI reporting

### 3.2 Stripe Connect for Multi-Agent Commissions

```
[Client] → Payment → [Platform] → Split (application_fee) → [Agent]
```

**E-Invoicing Responsibilities:**

| Transaction | Issuer | Via SDI |
|-------------|--------|---------|
| Client → Platform | Platform | ✅ |
| Platform → Agent | Platform | ✅ |
| Agent → Client | Agent | ✅ |

---

## 4. WhatsApp Business API

### 4.1 Rate Limits (2024)

| Tier | Daily Users | Requirement |
|------|-------------|-------------|
| Limited | 50 | Before verification |
| Tier 1 | 1,000 | After verification |
| Tier 2 | 10,000 | High quality + volume |
| Tier 3 | 100,000 | Sustained engagement |
| Tier 4 | Unlimited | Enterprise |

### 4.2 Template Approval

- Review: Seconds to 24 hours
- Categories: Marketing, Utility, Authentication, Service
- Key: Avoid vague content, follow policy

### 4.3 Pricing (2024-2025)

- **Nov 2024:** User-initiated = FREE
- **Jul 2025:** Per-template pricing

---

## 5. Supabase Edge vs. Python Backend

### 5.1 Comparison

| Metric | Supabase Edge | FastAPI |
|--------|---------------|---------|
| Cold Start | 400-1200ms | 500-2000ms |
| Hot Latency | 125-200ms | 50-100ms |
| Max Memory | 256MB | Unlimited |
| AI Support | Limited | Full ecosystem |

### 5.2 Recommendation

> [!TIP]
> **Keep FastAPI as primary backend.** Edge Functions only for lightweight webhook preprocessing.

**Hybrid Use Cases:**
- Edge: Webhook validation, rate limiting
- FastAPI: AI processing, LangGraph, business logic

---

## Implementation Priority

| Task | Effort | Impact | Priority |
|------|--------|--------|----------|
| Stripe e-invoicing | High | Critical | P0 |
| WhatsApp templates | Low | High | P0 |
| Deepgram Italian STT | Medium | High | P1 |
| GDPR consent flow | Medium | Critical | P1 |
| Embedding monitoring | Low | Medium | P2 |
| Edge migration | High | Low | P3 |

---

## Next Steps

1. **Today:** Submit WhatsApp templates, start Stripe Connect registration
2. **This Week:** Integrate Deepgram Nova-3, implement IVR consent
3. **This Month:** Partner with e-invoicing provider, complete agent onboarding
