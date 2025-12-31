# Anzevino AI Real Estate Agent

## Project Overview

An AI-powered assistant for Italian real estate agencies. Automates lead qualification via WhatsApp, provides AI property appraisals, and streamlines the sales journey from first contact to closing.

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | FastAPI (Python 3.11+) |
| **Database** | Supabase (PostgreSQL + Vector) |
| **AI/LLM** | Mistral AI (embeddings + generation) |
| **Messaging** | Twilio WhatsApp API |
| **Frontend** | Vite + Vanilla JS / React |
| **Deployment** | Vercel |

## Architecture

```
Hexagonal Architecture (Ports & Adapters)
├── domain/          # Business entities, value objects
├── application/     # Use cases, workflows (LangGraph)
├── infrastructure/  # External adapters (Mistral, Twilio, Supabase)
└── presentation/    # REST API (FastAPI)
```

## Frontend Applications

| App | Route | Purpose |
|-----|-------|---------|
| Landing Page | `/` | Marketing, lead acquisition |
| Dashboard | `/dashboard` | Agent admin interface |
| Fifi | `/appraisal` | AI property appraisal tool |

All apps located in `apps/` directory with independent builds.

## Key Features

- **WhatsApp Lead Qualification**: 24/7 automated response in 15 seconds
- **AI Property Appraisal (Fifi)**: Market-based valuation with PDF reports
- **LangGraph Workflows**: Multi-step conversation orchestration
- **RAG-Based Matching**: Semantic property search (1024D Mistral embeddings)
- **GDPR Compliant**: Italian data protection standards

## Quick Start

```bash
# Backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Configure API keys
uvicorn presentation.api.api:app --reload --port 8000

# Frontend (any app)
cd apps/dashboard
npm install && npm run dev
```

## Testing

```bash
# Run all tests
./venv/bin/pytest tests/ -v

# API tests only
./venv/bin/pytest tests/unit/test_api.py -v
```

## Documentation

- [README.md](README.md) - Getting started
- [Claude.md](Claude.md) - AI coding standards
- [docs/adr/](docs/adr/) - Architectural Decision Records
- [GITHUB_PUSH_GUIDE.md](GITHUB_PUSH_GUIDE.md) - Git workflow

## Environment Variables

Required in `.env`:
```
SUPABASE_URL=
SUPABASE_KEY=
MISTRAL_API_KEY=
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=
```

---

*Last updated: 2025-12-31*
