# Pending Tasks & Future Development Roadmap

**Date:** 2026-01-09
**Status:** Implementation Paused - Phase 1 & 2 Complete

---

> [!IMPORTANT]
> ## 🛑 Development Freeze Until January 16, 2026
> No new feature development until **January 16, 2026**.
> Resume date: **Week of January 16-17, 2026**

---

## Summary

| Phase | Status | Pending Items |
|-------|--------|---------------|
| Phase 1 | ✅ Complete | 1 endpoint to build |
| Phase 2 | ✅ Code Complete | Deployment pending |
| Phase 3 | ❌ Not Started | E-invoicing + Agent onboarding |
| Phase 4 | ❌ Not Started | Edge function migration |

---

## Phase 1: WhatsApp Templates & Stripe Connect

### ✅ Completed
- WhatsApp templates JSON (`docs/whatsapp/templates.json`)
- StripeConnectAdapter (`infrastructure/adapters/stripe_connect_adapter.py`)
- PaymentPort interface in `domain/ports.py`
- Container registration

### ⏳ Pending
| Task | Priority | Effort | Notes |
|------|----------|--------|-------|
| Submit WhatsApp templates to Meta | P0 | 30 min | Manual step in Meta Business Manager |
| Register Stripe Connect platform | P0 | 1 hour | [Stripe Dashboard](https://dashboard.stripe.com/connect/accounts/overview) |
| Create agent onboarding endpoint | P1 | 2 hours | `POST /api/agents/onboard` |

---

## Phase 2: Voice Integration & GDPR Compliance

### ✅ Completed
- DeepgramAdapter (`infrastructure/adapters/deepgram_adapter.py`)
- VoiceAdapter with IVR consent (`infrastructure/adapters/voice_adapter.py`)
- CallConsent model in `domain/models.py`
- SQL migration (`docs/sql/20260112_call_consent.sql`)
- Voice webhook endpoints (3 new routes)
- Deepgram API key configured in Vercel

### ⏳ Pending
| Task | Priority | Effort | Notes |
|------|----------|--------|-------|
| Deploy FastAPI to separate platform | P1 | 2 hours | Railway.app or Render.com recommended |
| Configure Vercel Python runtime | P2 | 1 hour | Alternative to separate deployment |
| Test voice call flow end-to-end | P1 | 30 min | Requires Italian phone number |
| Integrate Deepgram with recording callback | P2 | 1 hour | Auto-transcribe recordings |

---

## Phase 3: E-Invoicing & Agent Onboarding (Not Started)

### Planned Tasks
| Task | Priority | Effort | Notes |
|------|----------|--------|-------|
| Research Italian e-invoicing providers | P1 | 2 hours | Fattura24, Aruba, InvoiceNinja |
| Create EInvoiceAdapter | P1 | 4 hours | SDI/FatturaPA integration |
| Invoice data model | P1 | 1 hour | Partita IVA, Codice Destinatario |
| SQL migration for invoices | P1 | 30 min | `invoices` table |
| Agent onboarding UI | P2 | 3 hours | Stripe Connect Express flow |
| Collect Partita IVA during onboarding | P2 | 1 hour | Form validation |

---

## Phase 4: Architecture Optimization (Not Started)

### Planned Tasks
| Task | Priority | Effort | Notes |
|------|----------|--------|-------|
| Create Edge function for webhook validation | P3 | 2 hours | `supabase/functions/webhook-validator` |
| Migrate rate limiting to Edge | P3 | 1 hour | Reduce FastAPI load |
| Benchmark Edge vs FastAPI | P3 | 2 hours | Latency comparison |

---

## Infrastructure & DevOps Pending

| Task | Priority | Effort | Notes |
|------|----------|--------|-------|
| Set up Railway/Render for FastAPI | P1 | 2 hours | Alternative to Vercel Python |
| Configure production environment variables | P1 | 30 min | All services |
| Set up monitoring dashboard | P2 | 2 hours | Prometheus + Grafana |
| Implement CI/CD for backend | P2 | 1 hour | GitHub Actions |

---

## Configuration Pending

### Environment Variables to Add
```env
# Stripe Connect (Phase 1)
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_CONNECT_CLIENT_ID=ca_xxx

# Deepgram (Phase 2) - DONE ✅
DEEPGRAM_API_KEY=xxx

# E-Invoicing (Phase 3)
EINVOICE_API_KEY=xxx
EINVOICE_CODICE_FISCALE=xxx
```

---

## Manual Steps Required

1. **Meta Business Manager:** Submit WhatsApp templates for approval
2. **Stripe Dashboard:** Register as Connect platform
3. **Twilio Console:** Webhook URL already configured ✅
4. **E-Invoice Provider:** Sign up and get API credentials (Phase 3)

---

## Files Created During This Sprint

| File | Purpose |
|------|---------|
| `docs/whatsapp/templates.json` | WhatsApp message templates |
| `infrastructure/adapters/stripe_connect_adapter.py` | Stripe Connect payments |
| `infrastructure/adapters/deepgram_adapter.py` | Italian STT |
| `infrastructure/adapters/voice_adapter.py` | GDPR voice consent |
| `docs/sql/20260112_call_consent.sql` | Consent tracking table |
| `api/index.py` | Vercel serverless entry point |

---

## Research Documents Available

- [Deep Research Report](file:///Users/lycanbeats/Desktop/agenzia-ai/docs/reference/architecture/2026-01-08_deep-research-report.md)
- [Integration Plan](file:///Users/lycanbeats/Desktop/agenzia-ai/docs/reference/architecture/2026-01-08_integration-plan.md)

---

## Resume Development When Ready

To resume, pick from these priorities:

1. **Quick Wins (< 1 hour):** Submit WhatsApp templates, register Stripe Connect
2. **Backend Deployment (2 hours):** Set up Railway.app for FastAPI
3. **Phase 3 Start:** E-invoicing research and integration
