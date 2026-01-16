# Agenzia AI - System Context for LLMs

> **Purpose**: This document provides a comprehensive overview of the Agenzia AI platform, designed to enable language models to quickly understand the project's scope, architecture, and capabilities.

---

## 1. Product Overview

**Agenzia AI** is an AI-powered automation platform for Italian real estate agencies. It automates lead qualification, property matching, and client communication via WhatsApp.

### Core Value Proposition

- **Automated Lead Qualification**: AI agents qualify incoming leads via natural conversation on WhatsApp 24/7.
- **Property Matching**: RAG-based search retrieves relevant listings from agency inventory.
- **AI Appraisal Tool (Fifi)**: A free, public-facing property valuation tool that serves as a lead magnet.
- **Multi-Tenant SaaS**: Each agency has its own isolated data (leads, properties, messages) via Row-Level Security (RLS).

### Target Users

- Real estate agencies in Italy (primary market).
- Expansion planned to Spain, Germany, France, UK, and USA.

---

## 2. Technology Stack

| Layer | Technology |
|-------|------------|
| **Backend API** | Python 3.11+, FastAPI |
| **Database** | Supabase (PostgreSQL + pgvector for embeddings) |
| **AI/LLM** | Mistral AI (chat, reasoning, embeddings) |
| **Research** | Perplexity AI (real-time web search for legal/market data) |
| **Messaging** | Meta WhatsApp Cloud API (primary), Twilio (fallback) |
| **Frontend - Dashboard** | React 19, Vite, TanStack Query, Tailwind CSS |
| **Frontend - Landing** | Static HTML/CSS/JS (Vercel) |
| **Hosting** | Vercel (frontend), Render (backend API) |
| **Authentication** | Supabase Auth (JWT) |

---

## 3. Architecture

The project follows **Hexagonal Architecture** (Ports & Adapters) with strict layering:

```
┌─────────────────────────────────────────────────────────────────┐
│                      PRESENTATION LAYER                         │
│   (FastAPI endpoints, WebSocket handlers, Webhooks)             │
└───────────────────────────────┬─────────────────────────────────┘
                                │ depends on
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                          │
│   (Use Cases: Lead Processing, Appraisal, Journey Management)   │
└───────────────────────────────┬─────────────────────────────────┘
                                │ depends on
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                         DOMAIN LAYER                            │
│   (Entities: Lead, Message, Property | Ports: LLMPort, DBPort)  │
└───────────────────────────────┬─────────────────────────────────┘
                                │ implemented by
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     INFRASTRUCTURE LAYER                        │
│   (Adapters: MistralAdapter, SupabaseAdapter, TwilioAdapter)    │
└─────────────────────────────────────────────────────────────────┘
```

### Key Directories

| Directory | Description |
|-----------|-------------|
| `domain/` | Pure business logic, entities, ports (interfaces). No I/O. |
| `application/` | Use cases and orchestration services. |
| `infrastructure/` | Adapters for external services (Supabase, Mistral, Twilio). |
| `presentation/` | FastAPI routes, middleware, WebSocket handlers. |
| `config/` | Dependency Injection container (`container.py`), settings. |
| `apps/` | Frontend monorepo (dashboard, landing-page, fifi). |
| `scripts/` | Operational and migration scripts. |
| `tests/` | Unit and integration tests (`pytest`). |

---

## 4. Core Features

### 4.1 Lead Qualification (WhatsApp AI Agent)

- **Trigger**: Incoming WhatsApp message or form submission.
- **Flow**:
  1. `LeadProcessor` receives message.
  2. AI generates context-aware response using Mistral.
  3. Lead is scored (HOT/WARM/COLD) based on intent.
  4. Follow-up actions (e.g., schedule viewing, send property links).
- **Key Files**:
  - `application/services/lead_processor.py`
  - `infrastructure/adapters/mistral_adapter.py`
  - `presentation/api/api.py` (WebSocket and webhook endpoints)

### 4.2 Property Appraisal (Fifi)

- **Trigger**: User submits property details on the public landing page.
- **Flow**:
  1. API receives appraisal request.
  2. `AppraisalService` gathers market data (Perplexity for live search).
  3. AI generates valuation estimate with comparables.
  4. Result shown to user with a CTA to contact the agency.
- **Key Files**:
  - `application/services/appraisal_service.py`
  - `apps/landing-page/appraisal/index.html`

### 4.3 Dashboard (Real-Time Conversation Management)

- **Purpose**: Agency staff monitor and take over conversations.
- **Features**:
  - Real-time updates via WebSocket.
  - Lead status cards (name, score, last message).
  - Manual message sending (AI mutes, human takes over).
- **Key Files**:
  - `apps/dashboard/src/` (React application)
  - `presentation/api/api.py` (WebSocket endpoint `/ws/conversations`)

---

## 5. Data Model (Simplified)

### Leads Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `tenant_id` | UUID | Multi-tenancy isolation |
| `customer_phone` | TEXT | WhatsApp number |
| `customer_name` | TEXT | Client name |
| `status` | ENUM | new, active, qualified, scheduled, closed |
| `score` | ENUM | HOT, WARM, COLD |
| `journey_state` | TEXT | Current step in the customer journey |

### Messages Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `lead_id` | UUID | Foreign key to leads |
| `role` | TEXT | user, assistant, system |
| `content` | TEXT | Message text |
| `timestamp` | TIMESTAMP | When sent |

---

## 6. Environment Variables (Key)

| Variable | Purpose |
|----------|---------|
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_KEY` | Supabase anon key (client-side) |
| `SUPABASE_JWT_SECRET` | JWT verification for backend auth |
| `MISTRAL_API_KEY` | Mistral AI API key |
| `TWILIO_*` or `META_*` | Messaging provider credentials |
| `CALCOM_API_KEY` | Calendar/booking integration |

---

## 7. Common Patterns

### Dependency Injection

All services are wired in `config/container.py`. No global singletons outside this file.

```python
# config/container.py
container = Container()
container.db = SupabaseAdapter(settings.SUPABASE_URL, settings.SUPABASE_KEY)
container.llm = MistralAdapter(settings.MISTRAL_API_KEY)
container.lead_processor = LeadProcessor(db=container.db, llm=container.llm)
```

### Structured Logging

All logs use a structured format with context fields.

```python
logger.info("LEAD_QUALIFIED", context={"phone": "+39...", "score": "HOT"})
```

### Multi-Tenancy

Row-Level Security (RLS) policies on Supabase ensure each agency sees only its own data.

---

## 8. Deployment

| Component | Platform | URL |
|-----------|----------|-----|
| Frontend (Landing) | Vercel | `agenzia-ai.vercel.app` |
| Frontend (Dashboard) | Vercel | `agenzia-ai.vercel.app/dashboard/` |
| Backend API | Render | `agenzia-api.onrender.com` |
| Database | Supabase | `zozgvcdnkwtyioyazgmx.supabase.co` |

---

## 9. How to Contribute (for LLMs)

When working on this codebase, follow these principles:

1. **SOLID**: Single responsibility, open-closed, dependency inversion.
2. **Fail Fast**: Never hide errors with mock data.
3. **Structured Logs**: Use `logger.info(EVENT_NAME, context={...})`.
4. **Research First**: For new features, consult official docs before implementing.
5. **Hexagonal Layers**: Keep domain pure (no I/O); I/O in infrastructure only.
6. **Tests**: Place tests in `tests/unit/` or `tests/integration/`, not in root.

For detailed coding standards, refer to `Claude.md` in the project root.

---

## 10. Quick Reference

| Task | Command |
|------|---------|
| Run backend | `uvicorn presentation.api.api:app --reload --port 8000` |
| Run dashboard | `cd apps/dashboard && npm run dev` |
| Run tests | `make test` or `pytest tests/` |
| Lint/Format | `ruff check . && ruff format .` |
| Generate config.js | `SUPABASE_URL=... SUPABASE_ANON_KEY=... node scripts/generate-config.js` |

---

*This document is designed to be consumed by AI coding assistants to quickly onboard onto the Agenzia AI project.*
